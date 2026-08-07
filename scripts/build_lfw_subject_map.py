"""Build the preregistered LFW DevTest subject map without touching Study 0 scores."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from siamese_compression_lab.subject_bootstrap import (
    reconstruct_lfw_devtest_subject_map,
    validate_subject_map,
    write_subject_map,
)

EXPECTED_MATCHED_SHA256 = "9428d939063ff006b72bc79f50b7305e7da51b46b52bf2c25ca14b3a29479fb6"
EXPECTED_MISMATCHED_SHA256 = "cf1a1326577bf33abc98d1bbc938d3c2ec00304d1ace9b4392f5b38b19e182d0"


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _require_historical_source_hashes(matched: Path, mismatched: Path) -> tuple[str, str]:
    matched_sha256 = _sha256(matched)
    mismatched_sha256 = _sha256(mismatched)
    if matched_sha256 != EXPECTED_MATCHED_SHA256:
        raise ValueError(
            "matchpairsDevTest.csv does not match the immutable Study 0 source digest: "
            f"{matched_sha256} != {EXPECTED_MATCHED_SHA256}"
        )
    if mismatched_sha256 != EXPECTED_MISMATCHED_SHA256:
        raise ValueError(
            "mismatchpairsDevTest.csv does not match the immutable Study 0 source digest: "
            f"{mismatched_sha256} != {EXPECTED_MISMATCHED_SHA256}"
        )
    return matched_sha256, mismatched_sha256


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matched", required=True, type=Path)
    parser.add_argument("--mismatched", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-manifest", type=Path)
    args = parser.parse_args()

    matched_sha256, mismatched_sha256 = _require_historical_source_hashes(
        args.matched, args.mismatched
    )
    rows = reconstruct_lfw_devtest_subject_map(args.matched, args.mismatched)
    counts = validate_subject_map(
        rows,
        expected_pairs=1000,
        expected_genuine=500,
        expected_impostor=500,
        expected_subjects=963,
    )
    write_subject_map(args.output, rows)

    manifest = {
        "artifact": str(args.output),
        "artifact_sha256": _sha256(args.output),
        "matched_source": str(args.matched),
        "matched_source_sha256": matched_sha256,
        "matched_source_expected_sha256": EXPECTED_MATCHED_SHA256,
        "mismatched_source": str(args.mismatched),
        "mismatched_source_sha256": mismatched_sha256,
        "mismatched_source_expected_sha256": EXPECTED_MISMATCHED_SHA256,
        "counts": counts,
        "identity_policy": "sha256 namespace pseudonyms; source identities not published",
        "pair_order": "matched source order followed by mismatched source order",
        "historical_source_hashes_verified": True,
    }
    if args.source_manifest:
        args.source_manifest.parent.mkdir(parents=True, exist_ok=True)
        args.source_manifest.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
