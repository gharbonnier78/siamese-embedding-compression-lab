"""Measure vectorized coverage execution directly at the frozen 10k inner bootstrap scale.

This non-outcome benchmark removes the 1k->10k runtime extrapolation used by the scaling
benchmark. It first proves exact legacy/vectorized equality for one full 10,000-replicate
dataset, then times only the already-reviewed vectorized path at workers 1, 2 and 4.
Historical Study 0 scores are never read and coverage outcomes are never aggregated.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import time
from pathlib import Path

import numpy as np

from siamese_compression_lab.coverage_execution import (
    run_coverage_scenario_datasets,
    spawn_scenario_seed_sequences,
)
from siamese_compression_lab.coverage_execution_vectorized import (
    run_coverage_scenario_datasets_vectorized,
)
from siamese_compression_lab.coverage_simulation import CoverageScenario

FROZEN_BOOTSTRAP_REPLICATES = 10_000
FIRST_CHECKPOINT_DATASETS_PER_SCENARIO = 2_000
SCENARIO_COUNT = 5


def _run_vectorized(scenario, *, datasets, workers, root_seed):
    scenario_seed = spawn_scenario_seed_sequences(root_seed, 1)[0]
    started = time.perf_counter()
    outcomes = run_coverage_scenario_datasets_vectorized(
        scenario,
        simulated_datasets=datasets,
        bootstrap_replicates=FROZEN_BOOTSTRAP_REPLICATES,
        scenario_seed=scenario_seed,
        workers=workers,
    )
    return time.perf_counter() - started, outcomes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", type=int, default=8)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--workers", type=int, nargs="+", default=[1, 2, 4])
    parser.add_argument("--root-seed", type=int, default=20260807)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.datasets <= 0 or args.repeats <= 0:
        raise ValueError("datasets and repeats must be positive")
    workers = list(dict.fromkeys(args.workers))
    if not workers or any(worker <= 0 for worker in workers) or 1 not in workers:
        raise ValueError("workers must be positive and include workers=1")

    scenario = CoverageScenario(
        name="vectorized_frozen_inner_benchmark",
        target_delta_fnmr=0.015,
        subject_effect_sd_genuine=0.08,
        subject_effect_sd_impostor=0.05,
    )

    # Full-inner-scale oracle check: one dataset, exact 10k replicate sequence.
    oracle_seed = spawn_scenario_seed_sequences(args.root_seed, 1)[0]
    legacy_one = run_coverage_scenario_datasets(
        scenario,
        simulated_datasets=1,
        bootstrap_replicates=FROZEN_BOOTSTRAP_REPLICATES,
        scenario_seed=oracle_seed,
        workers=1,
    )
    vectorized_one = run_coverage_scenario_datasets_vectorized(
        scenario,
        simulated_datasets=1,
        bootstrap_replicates=FROZEN_BOOTSTRAP_REPLICATES,
        scenario_seed=oracle_seed,
        workers=1,
    )
    exact_10k_legacy_equivalence = vectorized_one == legacy_one
    if not exact_10k_legacy_equivalence:
        raise AssertionError("vectorized 10k inner result differs from legacy oracle")

    timings: dict[int, list[float]] = {worker: [] for worker in workers}
    serial_reference = None
    worker_equivalence = True
    for _ in range(args.repeats):
        for worker in workers:
            elapsed, outcomes = _run_vectorized(
                scenario,
                datasets=args.datasets,
                workers=worker,
                root_seed=args.root_seed,
            )
            timings[worker].append(elapsed)
            if serial_reference is None and worker == 1:
                serial_reference = outcomes
            elif outcomes != serial_reference:
                worker_equivalence = False
                raise AssertionError(
                    f"workers={worker} changed frozen-inner DatasetCoverageOutcome values"
                )

    assert serial_reference is not None
    serial_median = statistics.median(timings[1])
    rows = []
    for worker in workers:
        median = statistics.median(timings[worker])
        seconds_per_dataset = median / args.datasets
        rows.append(
            {
                "workers": worker,
                "elapsed_seconds": timings[worker],
                "median_elapsed_seconds": median,
                "speedup_vs_workers_1": serial_median / median,
                "parallel_efficiency_vs_workers_1": (serial_median / median) / worker,
                "measured_seconds_per_dataset_at_10000_replicates": seconds_per_dataset,
                "estimated_hours_per_2000_dataset_scenario": (
                    seconds_per_dataset * FIRST_CHECKPOINT_DATASETS_PER_SCENARIO / 3600.0
                ),
                "estimated_hours_all_5_scenarios_sequential": (
                    seconds_per_dataset
                    * FIRST_CHECKPOINT_DATASETS_PER_SCENARIO
                    * SCENARIO_COUNT
                    / 3600.0
                ),
            }
        )

    result = {
        "benchmark_kind": "non_outcome_vectorized_frozen_inner_scale",
        "historical_study_0_scores_read": False,
        "coverage_outcomes_aggregated": False,
        "production_coverage_gate_executed": False,
        "exact_10000_replicate_legacy_equivalence_verified": (
            exact_10k_legacy_equivalence
        ),
        "worker_count_equivalence_verified": worker_equivalence,
        "configuration": {
            "datasets_per_timed_run": args.datasets,
            "bootstrap_replicates_per_dataset": FROZEN_BOOTSTRAP_REPLICATES,
            "first_checkpoint_datasets_per_scenario": (
                FIRST_CHECKPOINT_DATASETS_PER_SCENARIO
            ),
            "scenario_count": SCENARIO_COUNT,
            "repeats": args.repeats,
            "workers": workers,
            "root_seed": args.root_seed,
        },
        "results": rows,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "logical_cpu_count": os.cpu_count(),
        },
        "interpretation_boundary": {
            "inner_bootstrap_scale_is_measured_not_extrapolated": True,
            "outer_2000_dataset_runtime_is_still_linearly_extrapolated": True,
            "small_sample_timing_is_qualitative_not_high_precision": True,
            "chronicle_resolution_requires_review": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
