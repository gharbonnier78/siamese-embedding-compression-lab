"""Benchmark deterministic dataset-level coverage parallelism without computing coverage outcomes.

This script measures wall-clock throughput only. It uses the reviewed synthetic coverage path,
verifies exact dataset outputs against the serial reference, and never aggregates coverage,
reads historical Study 0 scores, or executes the production coverage gate.
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
from siamese_compression_lab.coverage_simulation import CoverageScenario


FROZEN_BOOTSTRAP_REPLICATES = 10_000
FIRST_CHECKPOINT_DATASETS_PER_SCENARIO = 2_000
SCENARIO_COUNT = 5


def _run_once(
    scenario: CoverageScenario,
    *,
    datasets: int,
    bootstrap_replicates: int,
    workers: int,
    root_seed: int,
):
    scenario_seed = spawn_scenario_seed_sequences(root_seed, 1)[0]
    started = time.perf_counter()
    outcomes = run_coverage_scenario_datasets(
        scenario,
        simulated_datasets=datasets,
        bootstrap_replicates=bootstrap_replicates,
        scenario_seed=scenario_seed,
        workers=workers,
    )
    elapsed = time.perf_counter() - started
    return elapsed, outcomes


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
        raise ValueError("worker list must include serial reference workers=1")

    scenario = CoverageScenario(
        name="parallel_scaling_benchmark",
        target_delta_fnmr=0.015,
        subject_effect_sd_genuine=0.08,
        subject_effect_sd_impostor=0.05,
    )

    timings: dict[int, list[float]] = {worker: [] for worker in workers}
    serial_reference = None
    equivalence_verified = True

    for _ in range(args.repeats):
        for worker in workers:
            elapsed, outcomes = _run_once(
                scenario,
                datasets=args.datasets,
                bootstrap_replicates=args.bootstrap_replicates,
                workers=worker,
                root_seed=args.root_seed,
            )
            timings[worker].append(elapsed)
            if worker == 1 and serial_reference is None:
                serial_reference = outcomes
            elif serial_reference != outcomes:
                equivalence_verified = False
                raise AssertionError(
                    f"workers={worker} changed deterministic dataset outcomes"
                )

    assert serial_reference is not None
    serial_median = statistics.median(timings[1])
    production_scale_factor = FROZEN_BOOTSTRAP_REPLICATES / args.bootstrap_replicates
    rows = []
    for worker in workers:
        median = statistics.median(timings[worker])
        benchmark_seconds_per_dataset = median / args.datasets
        estimated_production_seconds_per_dataset = (
            benchmark_seconds_per_dataset * production_scale_factor
        )
        rows.append(
            {
                "workers": worker,
                "elapsed_seconds": timings[worker],
                "median_elapsed_seconds": median,
                "speedup_vs_1_worker": serial_median / median,
                "parallel_efficiency_vs_1_worker": (serial_median / median) / worker,
                "benchmark_seconds_per_dataset": benchmark_seconds_per_dataset,
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
        "benchmark_kind": "non_outcome_parallel_scaling",
        "historical_study_0_scores_read": False,
        "coverage_outcomes_aggregated": False,
        "production_coverage_gate_executed": False,
        "equivalence_verified_against_workers_1": equivalence_verified,
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
            "speedup_is_measured_not_assumed": True,
            "extrapolation_is_not_a_runtime_guarantee": True,
            "production_extrapolation_scales_to_frozen_10000_bootstrap_replicates": True,
            "chronicle_resolution_requires_review": True,
            "edge_weights_optimization_not_skipped_by_definition": True,
            "small_sample_speedup_is_qualitative_not_high_precision": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
