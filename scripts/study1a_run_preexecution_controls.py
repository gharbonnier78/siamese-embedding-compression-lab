from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import multiprocessing as mp
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch

from siamese_compression_lab.study1_execution import (
    Provenance,
    ShardManifest,
    atomic_write_json,
    normalize_adaface_bgr_uint8,
    sha256_file,
    stable_shard_id,
    validate_shard_for_resume,
    write_completed_shard_manifest,
)

EXPECTED_CHECKPOINT_SHA256 = "0e7a3238d2a50f3fe3860782534928ac7cb2598977cf897f6869fd5ac2493fd0"
EXPECTED_FIRST_CONV_SHA256 = "02d7ce728ea1e7debc5d669a4df81a2874f0e711e8f378993e68cfdd727611ee"
PROTOCOL_ID = "study1a-compression-focused-sanity-v1"
PREPROCESSING_ID = "adaface-r100-bgr-112-five-point-v1"

_MODEL = None


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tensor_digest(tensor: torch.Tensor) -> str:
    arr = tensor.detach().cpu().contiguous().to(torch.float32).numpy()
    return _sha_bytes(arr.tobytes(order="C"))


def _load_upstream_net(adaface_src: Path):
    net_path = adaface_src / "net.py"
    if not net_path.is_file():
        raise FileNotFoundError(f"missing upstream net.py: {net_path}")
    spec = importlib.util.spec_from_file_location("study1a_upstream_adaface_net", net_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import pinned AdaFace net.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tensor_state_from_checkpoint(checkpoint_path: Path) -> dict[str, torch.Tensor]:
    obj = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    if not isinstance(obj, dict):
        raise RuntimeError("historical checkpoint is not a mapping")
    state = obj.get("state_dict", obj)
    if not isinstance(state, dict) or not state:
        raise RuntimeError("historical checkpoint has no tensor state_dict")
    if not all(torch.is_tensor(v) for v in state.values()):
        raise RuntimeError("historical state_dict contains non-tensor values")
    return state


def _backbone_state(state: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    mapped = {}
    for key, value in state.items():
        if key.startswith("model."):
            mapped[key[len("model.") :]] = value
    if not mapped:
        raise RuntimeError("no model.* backbone tensors found")
    return mapped


def _synthetic_bgr_fixtures() -> list[np.ndarray]:
    h, w = 112, 112
    yy, xx = np.mgrid[0:h, 0:w]
    fixtures = []
    channel_sets = [
        ((xx * 3 + yy) % 256, (yy * 5 + 17) % 256, (xx * 7 + 31) % 256),
        ((xx + 13) % 256, (xx + yy * 2) % 256, (yy * 9 + 3) % 256),
        (((xx ^ yy) * 5) % 256, (xx * 11 + 19) % 256, (yy * 13 + 23) % 256),
        ((xx * 17 + yy * 3) % 256, (yy * 7 + 29) % 256, ((xx + yy) * 5) % 256),
    ]
    for channels in channel_sets:
        fixtures.append(np.stack(channels, axis=-1).astype(np.uint8))
    return fixtures


def _preprocess(image_bgr: np.ndarray) -> torch.Tensor:
    normalized = normalize_adaface_bgr_uint8(image_bgr)
    chw = np.transpose(normalized, (2, 0, 1)).copy()
    return torch.from_numpy(chw).unsqueeze(0)


def _infer_tensor(model, image_bgr: np.ndarray) -> torch.Tensor:
    with torch.inference_mode():
        embedding, _norm = model(_preprocess(image_bgr))
    if tuple(embedding.shape) != (1, 512):
        raise RuntimeError(f"expected 1x512 embedding, got {tuple(embedding.shape)}")
    return embedding.detach().cpu().contiguous().to(torch.float32)


def _infer_worker(image: np.ndarray) -> bytes:
    global _MODEL
    if _MODEL is None:
        raise RuntimeError("worker model is not initialized")
    return _infer_tensor(_MODEL, image).numpy().tobytes(order="C")


def _load_model(checkpoint_path: Path, adaface_src: Path):
    net = _load_upstream_net(adaface_src)
    state = _tensor_state_from_checkpoint(checkpoint_path)
    backbone = _backbone_state(state)
    model = net.build_model("ir_101")
    expected_keys = set(model.state_dict().keys())
    actual_keys = set(backbone.keys())
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing or extra:
        raise RuntimeError(
            f"backbone key mismatch: missing={missing[:8]} extra={extra[:8]} "
            f"(missing_count={len(missing)} extra_count={len(extra)})"
        )
    model.load_state_dict(backbone, strict=True)
    model.eval()
    return model, state


def _write_payload_and_manifest(root: Path, index: int, payload: bytes, provenance: Provenance) -> None:
    payload_path = root / f"fixture-{index:02d}.bin"
    manifest_path = root / f"fixture-{index:02d}.manifest.json"
    payload_path.write_bytes(payload)
    manifest = ShardManifest(
        shard_id=stable_shard_id(provenance.dataset_manifest_sha256, index, index + 1),
        provenance=provenance,
        row_count=1,
        payload_sha256=sha256_file(payload_path),
    )
    write_completed_shard_manifest(manifest_path, manifest)


def run(args: argparse.Namespace) -> dict:
    checkpoint = Path(args.checkpoint).resolve()
    adaface_src = Path(args.adaface_src).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)

    observed_checkpoint_sha = sha256_file(checkpoint)
    if observed_checkpoint_sha != EXPECTED_CHECKPOINT_SHA256:
        raise RuntimeError(
            f"checkpoint SHA mismatch: {observed_checkpoint_sha} != {EXPECTED_CHECKPOINT_SHA256}"
        )

    model, raw_state = _load_model(checkpoint, adaface_src)
    global _MODEL
    _MODEL = model

    first_conv = raw_state["model.input_layer.0.weight"].detach().cpu().contiguous()
    first_conv_sha = _sha_bytes(first_conv.numpy().tobytes(order="C"))
    if first_conv_sha != EXPECTED_FIRST_CONV_SHA256:
        raise RuntimeError("first-convolution sentinel SHA mismatch")

    fixtures = _synthetic_bgr_fixtures()
    fixture_records = []
    preprocessed_bytes = bytearray()
    for idx, image in enumerate(fixtures):
        raw_sha = _sha_bytes(image.tobytes(order="C"))
        prep = _preprocess(image)
        prep_bytes = prep.numpy().tobytes(order="C")
        preprocessed_bytes.extend(prep_bytes)
        fixture_records.append({
            "record_id": f"synthetic-{idx:02d}",
            "subject_id": f"synthetic-subject-{idx:02d}",
            "role": "non_scientific_preexecution_fixture",
            "raw_sha256": raw_sha,
            "shape": list(image.shape),
            "dtype": str(image.dtype),
        })

    preprocessing_fingerprint = _sha_bytes(bytes(preprocessed_bytes))

    # RGB/BGR representation sentinel: the synthetic image is deliberately asymmetric in R/B.
    bgr = fixtures[0]
    rgb_reversal = bgr[:, :, [2, 1, 0]].copy()
    bgr_digest = _sha_bytes(_preprocess(bgr).numpy().tobytes(order="C"))
    rgb_as_bgr_digest = _sha_bytes(_preprocess(rgb_reversal).numpy().tobytes(order="C"))
    if bgr_digest == rgb_as_bgr_digest:
        raise RuntimeError("RGB/BGR sentinel is non-discriminating")

    # Deterministic replay on the exact frozen model and non-scientific fixture.
    replay_a = _infer_tensor(model, fixtures[0])
    replay_b = _infer_tensor(model, fixtures[0])
    replay_exact = bool(torch.equal(replay_a, replay_b))
    replay_digest_a = _tensor_digest(replay_a)
    replay_digest_b = _tensor_digest(replay_b)
    if not replay_exact or replay_digest_a != replay_digest_b:
        raise RuntimeError("deterministic embedding replay failed")

    # Reference uninterrupted execution over all fixtures.
    reference_payloads = [_infer_worker(image) for image in fixtures]
    reference_digest = _sha_bytes(b"".join(reference_payloads))

    # Single-worker vs two-worker execution equivalence. Linux GitHub runner uses fork here,
    # preserving the already-frozen model without reloading benchmark data or opening outcomes.
    ctx = mp.get_context("fork")
    with ctx.Pool(processes=2) as pool:
        worker_payloads = pool.map(_infer_worker, fixtures)
    worker_digest = _sha_bytes(b"".join(worker_payloads))
    worker_equal = worker_payloads == reference_payloads
    if not worker_equal or worker_digest != reference_digest:
        raise RuntimeError("single-worker / multi-worker equivalence failed")

    dataset_manifest = {
        "schema_version": "1.0",
        "kind": "synthetic_non_scientific_preexecution_fixture_manifest",
        "protocol_id": PROTOCOL_ID,
        "preprocessing_id": PREPROCESSING_ID,
        "scientific_outcomes_opened": False,
        "records": fixture_records,
    }
    manifest_path = output_dir / "synthetic_dataset_manifest.json"
    atomic_write_json(manifest_path, dataset_manifest)
    dataset_manifest_sha = sha256_file(manifest_path)

    provenance = Provenance(
        model_sha256=observed_checkpoint_sha,
        preprocessing_id=PREPROCESSING_ID + ":" + preprocessing_fingerprint,
        dataset_manifest_sha256=dataset_manifest_sha,
        protocol_id=PROTOCOL_ID,
    )

    # Restart/resume equivalence: create a deliberately partial two-shard state, then resume.
    with tempfile.TemporaryDirectory() as td:
        resume_root = Path(td)
        for idx in range(2):
            _write_payload_and_manifest(resume_root, idx, reference_payloads[idx], provenance)

        resumed_payloads = []
        for idx in range(len(fixtures)):
            payload_path = resume_root / f"fixture-{idx:02d}.bin"
            manifest_file = resume_root / f"fixture-{idx:02d}.manifest.json"
            if validate_shard_for_resume(manifest_file, payload_path, provenance):
                payload = payload_path.read_bytes()
            else:
                payload = _infer_worker(fixtures[idx])
                _write_payload_and_manifest(resume_root, idx, payload, provenance)
            resumed_payloads.append(payload)

        resume_digest = _sha_bytes(b"".join(resumed_payloads))
        resume_equal = resumed_payloads == reference_payloads
        if not resume_equal or resume_digest != reference_digest:
            raise RuntimeError("interruption/restart equivalence failed")

    overlap_design = {
        "schema_version": "1.0",
        "status": "FROZEN_PREOUTCOME_DESIGN",
        "scientific_outcomes_opened": False,
        "exact_duplicate_key": "raw_sha256",
        "near_duplicate_rule": "freeze deterministic image-space method/version/threshold before real outcomes; diagnostic unless official protocol or preregistered rule requires exclusion",
        "identity_overlap_rule": "report by stable identity/template identifiers where available; preserve official benchmark folds",
        "cross_role_rule": "no outcome-conditioned movement or removal of records",
        "failure_rule": "retain decode/detection/alignment/multi-face/corrupt failures with stable ids and reasons",
        "authoritative_design": "protocol/studies/STUDY1A_OVERLAP_AUDIT_DESIGN.md",
    }
    atomic_write_json(output_dir / "overlap_audit_design.json", overlap_design)

    report = {
        "schema_version": "1.0",
        "kind": "study1a_non_outcome_preexecution_control_report",
        "scientific_outcomes_opened": False,
        "checkpoint_sha256": observed_checkpoint_sha,
        "first_conv_sha256": first_conv_sha,
        "architecture": "AdaFace IR101/R100",
        "embedding_dimension": 512,
        "preprocessing_fingerprint_sha256": preprocessing_fingerprint,
        "rgb_bgr_sentinel": {
            "status": "PASS",
            "bgr_preprocessed_sha256": bgr_digest,
            "reversed_channels_preprocessed_sha256": rgb_as_bgr_digest,
            "digests_differ": True,
        },
        "deterministic_embedding_replay": {
            "status": "PASS",
            "exact_tensor_equal": replay_exact,
            "embedding_sha256": replay_digest_a,
        },
        "worker_count_equivalence": {
            "status": "PASS",
            "reference_workers": 1,
            "candidate_workers": 2,
            "combined_embedding_payload_sha256": reference_digest,
        },
        "restart_resume_equivalence": {
            "status": "PASS",
            "combined_embedding_payload_sha256": reference_digest,
        },
        "manifest_provenance": {
            "status": "PASS",
            "dataset_manifest_sha256": dataset_manifest_sha,
            "preprocessing_id": provenance.preprocessing_id,
            "protocol_id": provenance.protocol_id,
        },
        "overlap_audit_design": {
            "status": "PASS_DESIGN_FROZEN",
            "authoritative_design": "protocol/studies/STUDY1A_OVERLAP_AUDIT_DESIGN.md",
        },
        "overall_status": "PASS",
    }
    atomic_write_json(output_dir / "preexecution_control_report.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--adaface-src", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
