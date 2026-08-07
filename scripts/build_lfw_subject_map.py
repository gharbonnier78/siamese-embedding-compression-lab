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


def _sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matched", required=True, type=Path)
    parser.add_argument("--mismatched", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-manifest", type=Path)
    args = parser.parse_args()

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
        "matched_source_sha256": _sha256(args.matched),
        "mismatched_source": str(args.mismatched),
        "mismatched_source_sha256": _sha256(args.mismatched),
        "counts": counts,
        "identity_policy": "sha256 namespace pseudonyms; source identities not published",
        "pair_order": "matched source order followed by mismatched source order",
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
