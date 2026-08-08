"""Check 1k -> 10k bootstrap runtime scaling on the reviewed synthetic execution path.

This is a non-outcome feasibility benchmark. It does not aggregate coverage, execute a gate,
or read historical Study 0 scores.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from siamese_compression_lab.coverage_execution import (
    run_coverage_scenario_datasets,
    spawn_scenario_seed_sequences,
)
from siamese_compression_lab.coverage_simulation import CoverageScenario


def _timed_run(
    scenario: CoverageScenario,
    *,
    datasets: int,
    replicates: int,
    root_seed: int,
) -> tuple[float, list]:
    scenario_seed = spawn_scenario_seed_sequences(root_seed, 1)[0]
    started = time.perf_counter()
    outcomes = run_coverage_scenario_datasets(
        scenario,
        simulated_datasets=datasets,
        bootstrap_replicates=replicates,
        scenario_seed=scenario_seed,
        workers=1,
    )
    return time.perf_counter() - started, outcomes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", type=int, default=4)
    parser.add_argument("--small-replicates", type=int, default=1000)
    parser.add_argument("--frozen-replicates", type=int, default=10000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--root-seed", type=int, default=20260807)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if min(args.datasets, args.small_replicates, args.frozen_replicates, args.repeats) <= 0:
        raise ValueError("benchmark counts must be positive")

    scenario = CoverageScenario(
        name="bootstrap_scale_linearity_benchmark",
        target_delta_fnmr=0.015,
        subject_effect_sd_genuine=0.08,
        subject_effect_sd_impostor=0.05,
    )

    small_times: list[float] = []
    frozen_times: list[float] = []
    small_outcomes = None
    frozen_outcomes = None
    for _ in range(args.repeats):
        elapsed, outcomes = _timed_run(
            scenario,
            datasets=args.datasets,
            replicates=args.small_replicates,
            root_seed=args.root_seed,
        )
        small_times.append(elapsed)
        if small_outcomes is None:
            small_outcomes = outcomes
        elif outcomes != small_outcomes:
            raise AssertionError("1k benchmark replay changed deterministic outcomes")

        elapsed, outcomes = _timed_run(
            scenario,
            datasets=args.datasets,
            replicates=args.frozen_replicates,
            root_seed=args.root_seed,
        )
        frozen_times.append(elapsed)
        if frozen_outcomes is None:
            frozen_outcomes = outcomes
        elif outcomes != frozen_outcomes:
            raise AssertionError("10k benchmark replay changed deterministic outcomes")

    small_median = statistics.median(small_times)
    frozen_median = statistics.median(frozen_times)
    replicate_ratio = args.frozen_replicates / args.small_replicates
    observed_runtime_ratio = frozen_median / small_median
    linear_prediction_seconds = small_median * replicate_ratio
    relative_to_linear_prediction = frozen_median / linear_prediction_seconds

    result = {
        "benchmark_kind": "non_outcome_bootstrap_scale_linearity",
        "historical_study_0_scores_read": False,
        "coverage_outcomes_aggregated": False,
        "production_coverage_gate_executed": False,
        "deterministic_replay_verified_within_each_scale": True,
        "configuration": {
            "datasets": args.datasets,
            "small_replicates": args.small_replicates,
            "frozen_replicates": args.frozen_replicates,
            "repeats": args.repeats,
            "workers": 1,
            "root_seed": args.root_seed,
        },
        "timing": {
            "small_elapsed_seconds": small_times,
            "frozen_elapsed_seconds": frozen_times,
            "small_median_seconds": small_median,
            "frozen_median_seconds": frozen_median,
            "replicate_ratio": replicate_ratio,
            "observed_runtime_ratio": observed_runtime_ratio,
            "linear_prediction_seconds": linear_prediction_seconds,
            "relative_to_linear_prediction": relative_to_linear_prediction,
        },
        "interpretation_boundary": {
            "this_is_not_coverage": True,
            "this_is_not_a_runtime_guarantee_for_2000_datasets": True,
            "purpose_is_only_to_check_local_1k_to_10k_scaling": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
