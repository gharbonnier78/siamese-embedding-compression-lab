"""Verify the preserved cancelled-run runtime evidence without reading Study 0 scores."""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path

from siamese_compression_lab.decomposed_coverage import validate_cancelled_runtime_manifest

DEFAULT_ROOT = Path("evidence/runtime/cancelled_coverage_run_31312018512")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def verify(root: Path) -> dict[str, object]:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    validate_cancelled_runtime_manifest(manifest)
    progress = manifest["files"]["progress.jsonl"]
    encoded = progress["repository_lossless_encoded_copy"]
    if encoded.get("encoding") != "deterministic-gzip-base64-split":
        raise ValueError("unexpected cancelled progress repository encoding")
    if encoded.get("reconstructable_exact_raw_bytes") is not True:
        raise ValueError("cancelled progress must be marked exactly reconstructable")

    encoded_parts: list[bytes] = []
    for part in encoded["parts"]:
        path = root / part["path"]
        payload = path.read_bytes()
        if len(payload) != int(part["bytes"]):
            raise ValueError(f"encoded progress part has wrong byte length: {path.name}")
        if _sha256(payload) != part["sha256"]:
            raise ValueError(f"encoded progress part digest mismatch: {path.name}")
        encoded_parts.append(payload)

    base64_payload = b"".join(encoded_parts)
    if len(base64_payload) != int(encoded["base64_bytes"]):
        raise ValueError("encoded progress base64 length mismatch")
    if _sha256(base64_payload) != encoded["base64_sha256"]:
        raise ValueError("encoded progress base64 digest mismatch")

    compressed = base64.b64decode(base64_payload, validate=True)
    if len(compressed) != int(encoded["gzip_bytes"]):
        raise ValueError("encoded progress gzip length mismatch")
    if _sha256(compressed) != encoded["gzip_sha256"]:
        raise ValueError("encoded progress gzip digest mismatch")

    raw = gzip.decompress(compressed)
    if len(raw) != int(progress["bytes"]):
        raise ValueError("reconstructed progress byte length mismatch")
    if _sha256(raw) != progress["sha256"]:
        raise ValueError("reconstructed progress digest mismatch")
    event_count = len(raw.splitlines())
    if event_count != int(progress["events"]):
        raise ValueError("reconstructed progress event count mismatch")

    execution_metadata = (root / "execution_metadata.json").read_bytes()
    metadata_manifest = manifest["files"]["execution_metadata.json"]
    if len(execution_metadata) != int(metadata_manifest["bytes"]):
        raise ValueError("execution metadata byte length mismatch")
    if _sha256(execution_metadata) != metadata_manifest["sha256"]:
        raise ValueError("execution metadata digest mismatch")

    return {
        "status": "PASS",
        "workflow_run_id": manifest["workflow_run_id"],
        "artifact_id": manifest["artifact_id"],
        "progress_sha256": progress["sha256"],
        "progress_bytes": len(raw),
        "progress_events": event_count,
        "historical_study_0_scores_read": False,
        "coverage_gate_result_admissible": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    print(json.dumps(verify(args.root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
