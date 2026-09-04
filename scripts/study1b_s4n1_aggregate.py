"""Aggregate S4N1 synthetic non-outcome calibration shards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from siamese_compression_lab.study1b_s4n1_selection import (
    SELECTION_RULES,
    aggregate_core_candidate,
)


def _read_rows(root: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(root.rglob("*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--mode", choices=("core",), required=True)
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--truth-delta", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = _read_rows(args.input_root)
    if len(rows) != args.expected:
        raise SystemExit(f"expected {args.expected} rows, found {len(rows)}")
    indices = [int(row["dataset_index"]) for row in rows]
    if len(indices) != len(set(indices)):
        raise SystemExit("duplicate dataset_index across S4N1 shards")
    if any(row.get("mode") != "core" for row in rows):
        raise SystemExit("non-core row found in core aggregate")
    if any(abs(float(row["test_truth_delta"]) - args.truth_delta) > 1e-12 for row in rows):
        raise SystemExit("mixed truth-delta provenance in S4N1 aggregate")
    if any(bool(row.get("scientific_outcomes_opened")) for row in rows):
        raise SystemExit("S4N1 aggregate refuses outcome-bearing rows")

    candidates = {
        candidate: aggregate_core_candidate(rows, candidate=candidate)
        for candidate in SELECTION_RULES
    }
    summary = {
        "schema_version": 1,
        "kind": "study1b_s4n1_core_calibration_summary",
        "scientific_outcomes_opened": False,
        "test_truth_delta": args.truth_delta,
        "simulated_datasets": len(rows),
        "candidates": candidates,
        "all_coverage_pass": all(value["coverage_pass"] for value in candidates.values()),
        "all_power_pass": all(value["power_pass"] for value in candidates.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
