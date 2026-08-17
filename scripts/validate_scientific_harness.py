"""Validate the scientific chronicle and harness contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from siamese_compression_lab.scientific_harness import validate_scientific_chronicle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--chronicle",
        type=Path,
        default=Path("protocol/scientific_chronicle.yaml"),
    )
    parser.add_argument(
        "--gate",
        type=Path,
        default=Path("gates/scientific_harness.yaml"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    errors = validate_scientific_chronicle(args.chronicle, args.gate)
    report = {"status": "PASS" if not errors else "FAIL", "errors": errors}
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
