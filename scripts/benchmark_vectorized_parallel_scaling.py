"""Benchmark combined vectorized + dataset-parallel coverage execution.

This is a non-outcome engineering benchmark. It compares legacy and vectorized execution on
identical synthetic datasets and SeedSequence lineages, verifies exact DatasetCoverageOutcome
equality before accepting timings, and never aggregates coverage or reads historical Study 0
scores.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import time
from dataclasses import asdict
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


def _time_runner(runner, scenario, *, datasets, replicates, seed, workers):
    scenario_seed = spawn_scenario_seed_sequences(seed, 1)[0]
    started = time.perf_counter()
    outcomes = runner(
        scenario,
        simulated_datasets=datasets,
        bootstrap_replicates=replicates,
        scenario_seed=scenario_seed,
        workers=workers,
    )
    return time.perf_counter() - started, outcomes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", type=int, default=16)
    parser.add_argument("--bootstrap-replicates", type=int, default=1000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--workers", type=int, nargs="+", default=[1, 2, 4])
    parser.add_argument("--root-seed", type=int, default=20260807)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.datasets <= 0 or args.bootstrap_replicates <= 0 or args.repeats <= 0:
        raise ValueError("datasets, bootstrap replicates and repeats must be positive")
    if not args.workers or any(worker <= 0 for worker in args.workers):
        raise ValueError("worker counts must be positive")
    workers = list(dict.fromkeys(args.workers))
    if 1 not in workers:
        raise ValueError("worker list must include workers=1")

    scenario = CoverageScenario(
        name="vectorized_parallel_scaling_benchmark",
        target_delta_fnmr=0.015,
        subject_effect_sd_genuine=0.08,
        subject_effect_sd_impostor=0.05,
    )
    legacy_timings = {worker: [] for worker in workers}
    vectorized_timings = {worker: [] for worker in workers}
    equivalence_verified = True

    for _ in range(args.repeats):
        for worker in workers:
            legacy_elapsed, legacy_outcomes = _time_runner(
                run_coverage_scenario_datasets,
                scenario,
                datasets=args.datasets,
                replicates=args.bootstrap_replicates,
                seed=args.root_seed,
                workers=worker,
            )
            vectorized_elapsed, vectorized_outcomes = _time_runner(
                run_coverage_scenario_datasets_vectorized,
                scenario,
                datasets=args.datasets,
                replicates=args.bootstrap_replicates,
                seed=args.root_seed,
                workers=worker,
            )
            if vectorized_outcomes != legacy_outcomes:
                equivalence_verified = False
                raise AssertionError(
                    f"vectorized workers={worker} changed DatasetCoverageOutcome values"
                )
            legacy_timings[worker].append(legacy_elapsed)
            vectorized_timings[worker].append(vectorized_elapsed)

    serial_vectorized_median = statistics.median(vectorized_timings[1])
    production_scale_factor = FROZEN_BOOTSTRAP_REPLICATES / args.bootstrap_replicates
    rows = []
    for worker in workers:
        legacy_median = statistics.median(legacy_timings[worker])
        vectorized_median = statistics.median(vectorized_timings[worker])
        benchmark_seconds_per_dataset = vectorized_median / args.datasets
        estimated_production_seconds_per_dataset = (
            benchmark_seconds_per_dataset * production_scale_factor
        )
        rows.append(
            {
                "workers": worker,
                "legacy_elapsed_seconds": legacy_timings[worker],
                "vectorized_elapsed_seconds": vectorized_timings[worker],
                "legacy_median_seconds": legacy_median,
                "vectorized_median_seconds": vectorized_median,
                "vectorized_speedup_vs_legacy_same_workers": (
                    legacy_median / vectorized_median
                ),
                "vectorized_parallel_speedup_vs_vectorized_workers_1": (
                    serial_vectorized_median / vectorized_median
                ),
                "vectorized_parallel_efficiency_vs_workers_1": (
                    (serial_vectorized_median / vectorized_median) / worker
                ),
                "production_scale_factor": production_scale_factor,
                "estimated_production_seconds_per_dataset": (
                    estimated_production_seconds_per_dataset
                ),
                "estimated_hours_per_2000_dataset_scenario": (
                    estimated_production_seconds_per_dataset
                    * FIRST_CHECKPOINT_DATASETS_PER_SCENARIO
                    / 3600.0
                ),
                "estimated_hours_all_5_scenarios_sequential": (
                    estimated_production_seconds_per_dataset
                    * FIRST_CHECKPOINT_DATASETS_PER_SCENARIO
                    * SCENARIO_COUNT
                    / 3600.0
                ),
            }
        )

    result = {
        "benchmark_kind": "non_outcome_vectorized_parallel_scaling",
        "historical_study_0_scores_read": False,
        "coverage_outcomes_aggregated": False,
        "production_coverage_gate_executed": False,
        "exact_dataset_outcome_equivalence_verified": equivalence_verified,
        "configuration": {
            "datasets_per_timed_run": args.datasets,
            "bootstrap_replicates_per_dataset": args.bootstrap_replicates,
            "frozen_bootstrap_replicates_per_dataset": FROZEN_BOOTSTRAP_REPLICATES,
            "first_checkpoint_datasets_per_scenario": (
                FIRST_CHECKPOINT_DATASETS_PER_SCENARIO
            ),
            "scenario_count": SCENARIO_COUNT,
            "repeats": args.repeats,
            "workers": workers,
            "root_seed": args.root_seed,
            "scenario": asdict(scenario),
        },
        "results": rows,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "logical_cpu_count": os.cpu_count(),
        },
        "interpretation_boundary": {
            "speedups_are_measured_not_multiplied_from_prior_benchmarks": True,
            "small_sample_speedup_is_qualitative_not_high_precision": True,
            "extrapolation_is_not_a_runtime_guarantee": True,
            "chronicle_resolution_requires_review": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
