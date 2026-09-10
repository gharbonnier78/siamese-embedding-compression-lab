"""Run one prospective S4N2 synthetic non-outcome calibration shard."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from siamese_compression_lab.study1b_s4n2_dagjk import run_s4n2_core_dataset
from siamese_compression_lab.study1b_simulation import load_subject_graph


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validation-graph", type=Path, required=True)
    parser.add_argument("--test-graph", type=Path, required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--truth-delta", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.start < 0 or args.stop <= args.start:
        raise SystemExit("--start/--stop must define a non-empty non-negative interval")
    validation_rows = load_subject_graph(args.validation_graph)
    test_rows = load_subject_graph(args.test_graph)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for dataset_index in range(args.start, args.stop):
            result = run_s4n2_core_dataset(
                validation_rows,
                test_rows,
                dataset_index=dataset_index,
                test_truth_delta=args.truth_delta,
            )
            handle.write(json.dumps(result, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
