"""Aggregate prospective S4N2 synthetic non-outcome calibration shards."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from siamese_compression_lab.study1b_s4n1_selection import SELECTION_RULES
from siamese_compression_lab.study1b_s4n2_dagjk import aggregate_s4n2_candidate


def _read_rows(root: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(root.rglob("*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--gate", choices=("coverage", "power"), required=True)
    parser.add_argument("--expected", type=int, required=True)
    parser.add_argument("--truth-delta", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = _read_rows(args.input_root)
    if len(rows) != args.expected:
        raise SystemExit(f"expected {args.expected} rows, found {len(rows)}")
    indices = sorted(int(row["dataset_index"]) for row in rows)
    if indices != list(range(args.expected)):
        raise SystemExit("S4N2 aggregate requires exact dataset indices 0..expected-1")
    if any(row.get("mode") != "s4n2_core" for row in rows):
        raise SystemExit("non-S4N2-core row found")
    if any(abs(float(row["test_truth_delta"]) - args.truth_delta) > 1e-12 for row in rows):
        raise SystemExit("mixed truth-delta provenance in S4N2 aggregate")
    forbidden = (
        "scientific_outcomes_opened",
        "screen_opened",
        "test_opened",
        "representation_geometry_opened",
        "amendment_activated",
    )
    if any(any(bool(row.get(key)) for key in forbidden) for row in rows):
        raise SystemExit("S4N2 aggregate refuses outcome-bearing or activated rows")
    candidates = {
        candidate: aggregate_s4n2_candidate(rows, candidate=candidate)
        for candidate in SELECTION_RULES
    }
    summary = {
        "schema_version": 1,
        "kind": f"study1b_s4n2_core_{args.gate}_summary",
        "gate": args.gate,
        "scientific_outcomes_opened": False,
        "screen_opened": False,
        "test_opened": False,
        "representation_geometry_opened": False,
        "amendment_activated": False,
        "inference_candidate": "S4N2_DAGJK20_T975",
        "test_truth_delta": args.truth_delta,
        "simulated_datasets": len(rows),
        "candidates": candidates,
        "all_coverage_pass": all(value["coverage_pass"] for value in candidates.values()),
        "all_power_pass": all(value["power_pass"] for value in candidates.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
