"""Run one S4N1 synthetic non-outcome calibration shard."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from siamese_compression_lab.study1b_s4n1_selection import (
    run_core_dataset,
    run_transport_dataset,
)
from siamese_compression_lab.study1b_simulation import load_subject_graph


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validation-graph", type=Path, required=True)
    parser.add_argument("--test-graph", type=Path, required=True)
    parser.add_argument("--mode", choices=("core", "transport"), required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--truth-delta", type=float)
    parser.add_argument("--bootstrap-replicates", type=int, default=10000)
    parser.add_argument("--base-delta", type=float)
    parser.add_argument("--seed-effect-sd", type=float)
    parser.add_argument("--validation-test-correlation", type=float)
    args = parser.parse_args()

    if args.start < 0 or args.stop <= args.start:
        raise SystemExit("--start/--stop must define a non-empty non-negative interval")

    validation_rows = load_subject_graph(args.validation_graph)
    test_rows = load_subject_graph(args.test_graph)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as handle:
        for dataset_index in range(args.start, args.stop):
            if args.mode == "core":
                if args.truth_delta is None:
                    raise SystemExit("--truth-delta is required in core mode")
                result = run_core_dataset(
                    validation_rows,
                    test_rows,
                    dataset_index=dataset_index,
                    test_truth_delta=args.truth_delta,
                    bootstrap_replicates=args.bootstrap_replicates,
                )
            else:
                if (
                    args.base_delta is None
                    or args.seed_effect_sd is None
                    or args.validation_test_correlation is None
                ):
                    raise SystemExit(
                        "--base-delta, --seed-effect-sd and "
                        "--validation-test-correlation are required in transport mode"
                    )
                result = run_transport_dataset(
                    validation_rows,
                    test_rows,
                    dataset_index=dataset_index,
                    base_delta=args.base_delta,
                    seed_effect_sd=args.seed_effect_sd,
                    validation_test_correlation=args.validation_test_correlation,
                )
            handle.write(json.dumps(result, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
