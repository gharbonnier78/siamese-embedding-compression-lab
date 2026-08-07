"""Validate research contracts without executing a biometric benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from siamese_compression_lab.research_assurance import validate_research_program, write_report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--output", help="Optional JSON report path")
    args = parser.parse_args()

    report = validate_research_program(Path(args.root))
    if args.output:
        write_report(report, args.output)
    print(json.dumps(report.as_dict(), indent=2))
    return 0 if report.status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
