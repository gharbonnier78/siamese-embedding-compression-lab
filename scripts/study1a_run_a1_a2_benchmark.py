from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import pickle
import time
from pathlib import Path
from typing import ClassVar

import cv2
import numpy as np
import torch

EXPECTED_CHECKPOINT_SHA256 = "0e7a3238d2a50f3fe3860782534928ac7cb2598977cf897f6869fd5ac2493fd0"
ADAFACE_COMMIT = "c60eaa786a42c03444f3df7096dbaf9d57ae010d"
THRESHOLDS = np.arange(0, 4, 0.01)

BENCHMARKS = {
    "lfw": {"gate": "A1", "published_reference": 0.9982, "minimum": 0.9962, "description": "LFW basic reproduction sanity"},
    "cfp_fp": {"gate": "A2", "published_reference": 0.9926, "minimum": 0.9896, "description": "CFP-FP frontal/profile variation"},
    "cplfw": {"gate": "A2", "published_reference": 0.9457, "minimum": 0.9427, "description": "CPLFW cross-pose variation"},
    "calfw": {"gate": "A2", "published_reference": 0.9612, "minimum": 0.9582, "description": "CALFW cross-age variation"},
    "agedb_30": {"gate": "A2", "published_reference": 0.9800, "minimum": 0.9770, "description": "AgeDB-30 large age-gap variation"},
}


class RestrictedValidationUnpickler(pickle.Unpickler):
    """Restricted loader for standard InsightFace verification .bin containers."""

    _ALLOWED_BUILTINS: ClassVar[dict[str, object]] = {
        "bytearray": bytearray,
        "bytes": bytes,
        "frozenset": frozenset,
        "set": set,
        "slice": slice,
    }

    def find_class(self, module: str, name: str):
        if module == "builtins" and name in self._ALLOWED_BUILTINS:
            return self._ALLOWED_BUILTINS[name]
        if module in {"numpy.core.multiarray", "numpy._core.multiarray"} and name == "_reconstruct":
            return np.core.multiarray._reconstruct
        if module == "numpy" and name == "ndarray":
            return np.ndarray
        if module == "numpy" and name == "dtype":
            return np.dtype
        raise pickle.UnpicklingError(f"forbidden global in validation bin: {module}.{name}")


def restricted_pickle_load(path: Path):
    with path.open("rb") as stream:
        return RestrictedValidationUnpickler(stream, encoding="bytes").load()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load_upstream_net(adaface_src: Path):
    net_path = adaface_src / "net.py"
    if not net_path.is_file():
        raise FileNotFoundError(f"missing pinned AdaFace net.py: {net_path}")
    spec = importlib.util.spec_from_file_location("study1a_benchmark_adaface_net", net_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import pinned AdaFace net.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_model(checkpoint: Path, adaface_src: Path, device: torch.device):
    observed_sha = sha256_file(checkpoint)
    if observed_sha != EXPECTED_CHECKPOINT_SHA256:
        raise RuntimeError(f"checkpoint SHA mismatch: {observed_sha} != {EXPECTED_CHECKPOINT_SHA256}")

    obj = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if not isinstance(obj, dict):
        raise TypeError("checkpoint container is not a mapping")
    raw_state = obj.get("state_dict", obj)
    if not isinstance(raw_state, dict) or not raw_state:
        raise TypeError("checkpoint contains no state_dict mapping")
    if not all(torch.is_tensor(v) for v in raw_state.values()):
        raise TypeError("checkpoint state_dict contains non-tensor values")

    backbone = {key[len("model.") :]: value for key, value in raw_state.items() if key.startswith("model.")}
    net = load_upstream_net(adaface_src)
    model = net.build_model("ir_101")
    expected = set(model.state_dict())
    actual = set(backbone)
    if expected != actual:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise RuntimeError(
            f"IR101 backbone key mismatch: missing={missing[:8]} extra={extra[:8]} "
            f"missing_count={len(missing)} extra_count={len(extra)}"
        )
    model.load_state_dict(backbone, strict=True)
    model.eval().to(device)
    return model, observed_sha


def canonical_encoded_blob(item, index: int) -> tuple[bytes, str]:
    if isinstance(item, bytes):
        return item, "bytes"
    if isinstance(item, bytearray):
        return bytes(item), "bytearray"
    if isinstance(item, np.ndarray):
        is_encoded_vector = item.ndim == 1 or (item.ndim == 2 and 1 in item.shape)
        if item.dtype != np.uint8 or not is_encoded_vector:
            raise TypeError(
                f"image payload {index} is ndarray but not an encoded uint8 vector: "
                f"dtype={item.dtype} shape={item.shape}"
            )
        return item.reshape(-1).tobytes(order="C"), "ndarray_uint8_encoded_bytes"
    raise TypeError(f"unsupported validation image payload at {index}: {type(item).__name__}")


def decode_bgr_normalized(blob: bytes) -> np.ndarray:
    encoded = np.frombuffer(blob, dtype=np.uint8)
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("image decode failed")
    if image.shape != (112, 112, 3):
        raise ValueError(f"expected aligned 112x112x3 crop, got {image.shape}")
    image = image.astype(np.float32) / 255.0
    image = (image - 0.5) / 0.5
    return np.transpose(image, (2, 0, 1)).copy()


def fuse_original_and_flip(model, batch: torch.Tensor) -> torch.Tensor:
    with torch.inference_mode():
        emb, norm = model(batch)
        emb_flip, norm_flip = model(torch.flip(batch, dims=[3]))
        fused_pre_norm = emb * norm + emb_flip * norm_flip
        return torch.nn.functional.normalize(fused_pre_norm, p=2, dim=1)


def infer_all(model, blobs: list[bytes], *, device: torch.device, batch_size: int, progress_every: int) -> tuple[np.ndarray, dict]:
    embeddings = np.empty((len(blobs), 512), dtype=np.float32)
    decode_failures: list[dict] = []
    started = time.monotonic()
    for start in range(0, len(blobs), batch_size):
        stop = min(start + batch_size, len(blobs))
        tensors = []
        for index in range(start, stop):
            try:
                tensors.append(decode_bgr_normalized(blobs[index]))
            except Exception as exc:
                decode_failures.append({"image_index": index, "error": repr(exc)})
                raise RuntimeError(f"decode failed at image index {index}: {exc}") from exc
        batch = torch.from_numpy(np.stack(tensors, axis=0)).to(device)
        fused = fuse_original_and_flip(model, batch)
        if tuple(fused.shape) != (stop - start, 512):
            raise RuntimeError(f"unexpected embedding shape {tuple(fused.shape)}")
        if not torch.isfinite(fused).all():
            raise RuntimeError("non-finite embedding detected")
        embeddings[start:stop] = fused.detach().cpu().to(torch.float32).numpy()
        done = stop
        if done == len(blobs) or done % progress_every < batch_size:
            elapsed = max(time.monotonic() - started, 1e-9)
            rate = done / elapsed
            remain = (len(blobs) - done) / max(rate, 1e-9)
            print(f"progress {done}/{len(blobs)} ({100.0 * done / len(blobs):.1f}%) {rate:.2f} images/s ETA {remain / 60.0:.1f} min", flush=True)
    return embeddings, {"decode_failure_count": len(decode_failures), "decode_failures": decode_failures}


def calculate_accuracy(threshold: float, dist: np.ndarray, actual_issame: np.ndarray) -> float:
    predict_issame = np.less(dist, threshold)
    tp = np.sum(np.logical_and(predict_issame, actual_issame))
    tn = np.sum(np.logical_and(np.logical_not(predict_issame), np.logical_not(actual_issame)))
    return float(tp + tn) / float(dist.size)


def contiguous_kfold_indices(n: int, n_splits: int = 10):
    if n_splits <= 1 or n < n_splits:
        raise ValueError("invalid fold configuration")
    fold_sizes = np.full(n_splits, n // n_splits, dtype=int)
    fold_sizes[: n % n_splits] += 1
    current = 0
    all_indices = np.arange(n)
    for fold_size in fold_sizes:
        start, stop = current, current + fold_size
        test = all_indices[start:stop]
        train = np.concatenate((all_indices[:start], all_indices[stop:]))
        yield train, test
        current = stop


def evaluate_adaface_protocol(embeddings: np.ndarray, issame: np.ndarray) -> dict:
    if embeddings.ndim != 2 or embeddings.shape[1] != 512:
        raise ValueError("expected Nx512 embedding matrix")
    if embeddings.shape[0] % 2:
        raise ValueError("embedding count must be even")
    if embeddings.shape[0] // 2 != len(issame):
        raise ValueError("pair labels do not match embedding count")
    dist = np.sum(np.square(np.subtract(embeddings[0::2], embeddings[1::2])), axis=1)
    labels = np.asarray(issame, dtype=bool)
    fold_accuracies = []
    best_thresholds = []
    fold_sizes = []
    for fold_index, (train, test) in enumerate(contiguous_kfold_indices(len(labels), 10)):
        train_acc = np.array([calculate_accuracy(float(th), dist[train], labels[train]) for th in THRESHOLDS], dtype=np.float64)
        best_index = int(np.argmax(train_acc))
        threshold = float(THRESHOLDS[best_index])
        test_acc = calculate_accuracy(threshold, dist[test], labels[test])
        fold_accuracies.append(test_acc)
        best_thresholds.append(threshold)
        fold_sizes.append(len(test))
        print(f"fold {fold_index}: test_n={len(test)} threshold={threshold:.2f} accuracy={test_acc:.6f}", flush=True)
    values = np.asarray(fold_accuracies, dtype=np.float64)
    return {
        "fold_accuracies": [float(v) for v in values],
        "best_thresholds": best_thresholds,
        "fold_sizes": fold_sizes,
        "accuracy_mean": float(values.mean()),
        "accuracy_std": float(values.std()),
        "mean_selected_threshold": float(np.mean(best_thresholds)),
    }


def inspect_validation_container(path: Path) -> tuple[list[bytes], np.ndarray, dict]:
    loaded = restricted_pickle_load(path)
    if not isinstance(loaded, (tuple, list)) or len(loaded) != 2:
        raise TypeError("validation .bin must contain (image_payloads, issame_labels)")
    blobs_raw, labels_raw = loaded
    raw_items = list(blobs_raw)
    if not raw_items:
        raise ValueError("validation image payload is empty")
    blobs = []
    representations: dict[str, int] = {}
    for index, item in enumerate(raw_items):
        blob, representation = canonical_encoded_blob(item, index)
        blobs.append(blob)
        representations[representation] = representations.get(representation, 0) + 1
    labels = np.asarray(labels_raw, dtype=bool).reshape(-1)
    if len(blobs) != 2 * len(labels):
        raise RuntimeError(f"expected 2 images per pair: images={len(blobs)} labels={len(labels)}")
    image_hashes = [sha256_bytes(blob) for blob in blobs]
    unique_count = len(set(image_hashes))
    return blobs, labels, {
        "image_blob_count": len(blobs),
        "pair_count": len(labels),
        "genuine_pair_count": int(labels.sum()),
        "impostor_pair_count": int((~labels).sum()),
        "payload_representation_counts": representations,
        "unique_image_byte_digest_count": unique_count,
        "exact_duplicate_image_occurrence_count": len(image_hashes) - unique_count,
        "identity_overlap_status": "NOT_AVAILABLE_FROM_SERIALIZED_BIN_WITHOUT_STABLE_SUBJECT_IDS",
        "exclusion_count": 0,
    }


def run(args: argparse.Namespace) -> dict:
    benchmark = args.benchmark
    spec = BENCHMARKS[benchmark]
    checkpoint = Path(args.checkpoint).resolve()
    dataset_file = Path(args.dataset_file).resolve()
    adaface_src = Path(args.adaface_src).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(max(1, args.torch_threads))
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    device = torch.device(args.device)
    report_path = output_dir / f"{benchmark}_result.json"
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    base_report = {
        "schema_version": "1.1",
        "kind": "study1a_a1_a2_outcome",
        "benchmark": benchmark,
        "gate": spec["gate"],
        "description": spec["description"],
        "published_reference": spec["published_reference"],
        "frozen_minimum": spec["minimum"],
        "study1b_authorized": False,
        "outcome_bearing": True,
        "protocol_id": "study1a-compression-focused-sanity-v1",
        "adaface_upstream_commit": ADAFACE_COMMIT,
        "started_utc": started_utc,
        "execution_status": "RUNNING",
        "scientific_decision": "INDETERMINATE",
    }
    atomic_json(report_path, base_report)
    try:
        dataset_sha = sha256_file(dataset_file)
        dataset_size = dataset_file.stat().st_size
        blobs, labels, dataset_info = inspect_validation_container(dataset_file)
        print(f"dataset {benchmark}: sha256={dataset_sha} bytes={dataset_size} pairs={len(labels)} images={len(blobs)}", flush=True)
        model, checkpoint_sha = load_model(checkpoint, adaface_src, device)
        embeddings, execution_diagnostics = infer_all(model, blobs, device=device, batch_size=args.batch_size, progress_every=args.progress_every)
        metrics = evaluate_adaface_protocol(embeddings, labels)
        accuracy = float(metrics["accuracy_mean"])
        gate_pass = accuracy >= float(spec["minimum"])
        report = {
            **base_report,
            "execution_status": "VALID_OUTCOME",
            "scientific_decision": "PASS" if gate_pass else "FAIL",
            "checkpoint": {"source_locator": args.checkpoint_locator, "sha256": checkpoint_sha, "architecture": "AdaFace IR101/R100", "embedding_dimension": 512, "loader": "torch.load(weights_only=True); strict model.* backbone"},
            "dataset": {"source_locator": args.dataset_locator, "sha256": dataset_sha, "size_bytes": dataset_size, **dataset_info},
            "preprocessing": {"benchmark_input": "pre-aligned 112x112 standard InsightFace validation-bin crop", "decode": "cv2.imdecode(IMREAD_COLOR) -> BGR", "normalization": "(pixel/255 - 0.5)/0.5", "realignment_performed": False, "horizontal_flip_tta": True, "feature_fusion": "AdaFace norm-aware fusion of original and horizontal flip"},
            "verification_protocol": {"distance": "squared_l2_on_l2_normalized_512d_embeddings", "folds": 10, "shuffle": False, "threshold_grid": "np.arange(0,4,0.01)", "threshold_selection": "maximize train-fold accuracy; evaluate held-out fold"},
            "metrics": metrics,
            "gate_evaluation": {"observed_accuracy": accuracy, "frozen_minimum": spec["minimum"], "published_reference": spec["published_reference"], "pass": gate_pass},
            "diagnostics": execution_diagnostics,
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        atomic_json(report_path, report)
        print(json.dumps(report, indent=2, sort_keys=True), flush=True)
        return report
    except Exception as exc:
        failure = {**base_report, "execution_status": "INFRASTRUCTURE_OR_PROVENANCE_FAILURE", "scientific_decision": "INDETERMINATE", "error": repr(exc), "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        atomic_json(report_path, failure)
        print(json.dumps(failure, indent=2, sort_keys=True), flush=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", required=True, choices=sorted(BENCHMARKS))
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--checkpoint-locator", required=True)
    parser.add_argument("--dataset-file", required=True)
    parser.add_argument("--dataset-locator", required=True)
    parser.add_argument("--adaface-src", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--torch-threads", type=int, default=4)
    parser.add_argument("--progress-every", type=int, default=512)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
