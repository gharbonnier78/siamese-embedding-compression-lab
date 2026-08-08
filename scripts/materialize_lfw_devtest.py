"""Materialize the exact historical LFW DevTest sources and build the v0.2.2 subject map.

This script intentionally reads no Study 0 score artifact. It downloads only the two DevTest
pair CSV files from the exact Kaggle dataset version recorded by Study 0, verifies their
immutable SHA-256 digests, reconstructs the subject map, and enforces the preregistered
1000 / 500 / 500 / 963 invariants.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import kagglehub

from siamese_compression_lab.subject_bootstrap import (
    reconstruct_lfw_devtest_subject_map,
    validate_subject_map,
    write_subject_map,
)

DATASET_HANDLE = "jessicali9530/lfw-dataset/versions/4"
MATCHED_FILE = "matchpairsDevTest.csv"
MISMATCHED_FILE = "mismatchpairsDevTest.csv"
EXPECTED_MATCHED_SHA256 = "9428d939063ff006b72bc79f50b7305e7da51b46b52bf2c25ca14b3a29479fb6"
EXPECTED_MISMATCHED_SHA256 = "cf1a1326577bf33abc98d1bbc938d3c2ec00304d1ace9b4392f5b38b19e182d0"


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _download_exact_file(name: str, destination: Path) -> Path:
    resolved = Path(
        kagglehub.dataset_download(
            DATASET_HANDLE,
            path=name,
            force_download=True,
        )
    ).resolve()
    if not resolved.is_file():
        candidate = resolved / name
        if candidate.is_file():
            resolved = candidate
        else:
            raise FileNotFoundError(f"KaggleHub did not materialize {name}: {resolved}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(resolved, destination)
    return destination


def _require_digest(path: Path, expected: str) -> str:
    actual = _sha256(path)
    if actual != expected:
        raise ValueError(f"immutable source digest mismatch for {path.name}: {actual} != {expected}")
    return actual


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    sources_dir = output_dir / "sources"

    with tempfile.TemporaryDirectory(prefix="lfw-devtest-v4-") as temp_dir:
        temp_root = Path(temp_dir)
        matched = _download_exact_file(MATCHED_FILE, temp_root / MATCHED_FILE)
        mismatched = _download_exact_file(MISMATCHED_FILE, temp_root / MISMATCHED_FILE)

        matched_sha256 = _require_digest(matched, EXPECTED_MATCHED_SHA256)
        mismatched_sha256 = _require_digest(mismatched, EXPECTED_MISMATCHED_SHA256)

        sources_dir.mkdir(parents=True, exist_ok=True)
        matched_evidence = sources_dir / MATCHED_FILE
        mismatched_evidence = sources_dir / MISMATCHED_FILE
        shutil.copyfile(matched, matched_evidence)
        shutil.copyfile(mismatched, mismatched_evidence)

        rows = reconstruct_lfw_devtest_subject_map(matched, mismatched)
        counts = validate_subject_map(
            rows,
            expected_pairs=1000,
            expected_genuine=500,
            expected_impostor=500,
            expected_subjects=963,
        )

    subject_map = output_dir / "test_pair_subject_map_v0.2.2.csv"
    write_subject_map(subject_map, rows)

    manifest = {
        "dataset_handle": DATASET_HANDLE,
        "historical_study_0_scores_read": False,
        "matched_source": str(matched_evidence.relative_to(output_dir)),
        "matched_source_sha256": matched_sha256,
        "matched_source_expected_sha256": EXPECTED_MATCHED_SHA256,
        "mismatched_source": str(mismatched_evidence.relative_to(output_dir)),
        "mismatched_source_sha256": mismatched_sha256,
        "mismatched_source_expected_sha256": EXPECTED_MISMATCHED_SHA256,
        "subject_map": subject_map.name,
        "subject_map_sha256": _sha256(subject_map),
        "counts": counts,
        "identity_policy": "sha256 namespace pseudonyms; source identities not published in subject map",
        "pair_order": "matched source order followed by mismatched source order",
        "historical_source_hashes_verified": True,
    }
    manifest_path = output_dir / "source_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
