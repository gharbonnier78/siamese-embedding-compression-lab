"""Benchmark end-to-end dataset-level vectorized coverage execution without outcomes.

The benchmark compares the reviewed legacy coverage engine with the vectorized candidate
using identical SeedSequence lineages, synthetic datasets, worker counts and bootstrap
replicate counts. It refuses to report speedup unless every DatasetCoverageOutcome is
exactly equal, including byte-level bootstrap digests.
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
import yaml

from siamese_compression_lab.coverage_execution import (
    run_coverage_scenario_datasets,
    spawn_scenario_seed_sequences,
)
from siamese_compression_lab.coverage_simulation import CoverageScenario

FROZEN_BOOTSTRAP_REPLICATES = 10_000
FIRST_CHECKPOINT_DATASETS_PER_SCENARIO = 2_000
SCENARIO_COUNT = 5
SPEEDUP_DEFINITION = (
    "legacy median elapsed time divided by vectorized median elapsed time "
    "at the same worker count"
)


def _run_once(
    scenario: CoverageScenario,
    *,
    datasets: int,
    bootstrap_replicates: int,
    workers: int,
    root_seed: int,
    engine: str,
):
    scenario_seed = spawn_scenario_seed_sequences(root_seed, 1)[0]
    started = time.perf_counter()
    outcomes = run_coverage_scenario_datasets(
        scenario,
        simulated_datasets=datasets,
        bootstrap_replicates=bootstrap_replicates,
        scenario_seed=scenario_seed,
        workers=workers,
        engine=engine,  # type: ignore[arg-type]
    )
    return time.perf_counter() - started, outcomes


def _load_execution_contract(path: Path) -> dict[str, object]:
    contract = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(contract, dict):
        raise TypeError("coverage contract must be a YAML mapping")
    execution = contract.get("execution")
    if not isinstance(execution, dict):
        raise TypeError("coverage contract must define execution")
    if execution.get("engine") != "vectorized":
        raise ValueError("benchmark expects contract execution.engine=vectorized")
    if execution.get("reference_oracle_engine") != "legacy":
        raise ValueError("benchmark expects legacy reference oracle")
    if execution.get("exact_dataset_outcome_equivalence_required") is not True:
        raise ValueError("contract must require exact dataset outcome equivalence")
    return execution


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", type=int, default=16)
    parser.add_argument("--bootstrap-replicates", type=int, default=1000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--workers", type=int, nargs="+", default=[1, 2, 4])
    parser.add_argument("--root-seed", type=int, default=20260807)
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.datasets <= 0 or args.bootstrap_replicates <= 0 or args.repeats <= 0:
        raise ValueError("datasets, bootstrap replicates and repeats must be positive")
    workers = list(dict.fromkeys(args.workers))
    if not workers or any(worker <= 0 for worker in workers):
        raise ValueError("worker counts must be positive")
    if 1 not in workers:
        raise ValueError("worker list must include workers=1")

    execution_contract = _load_execution_contract(args.contract)
    scenario = CoverageScenario(
        name="vectorized_end_to_end_benchmark",
        target_delta_fnmr=0.015,
        subject_effect_sd_genuine=0.08,
        subject_effect_sd_impostor=0.05,
    )
    timings = {worker: {"legacy": [], "vectorized": []} for worker in workers}
    equivalence_verified = True

    for _ in range(args.repeats):
        for worker in workers:
            legacy_elapsed, legacy = _run_once(
                scenario,
                datasets=args.datasets,
                bootstrap_replicates=args.bootstrap_replicates,
                workers=worker,
                root_seed=args.root_seed,
                engine="legacy",
            )
            vectorized_elapsed, vectorized = _run_once(
                scenario,
                datasets=args.datasets,
                bootstrap_replicates=args.bootstrap_replicates,
                workers=worker,
                root_seed=args.root_seed,
                engine="vectorized",
            )
            if vectorized != legacy:
                equivalence_verified = False
                raise AssertionError(
                    f"vectorized engine changed dataset outcomes for workers={worker}"
                )
            timings[worker]["legacy"].append(legacy_elapsed)
            timings[worker]["vectorized"].append(vectorized_elapsed)

    production_scale_factor = FROZEN_BOOTSTRAP_REPLICATES / args.bootstrap_replicates
    rows = []
    for worker in workers:
        legacy_median = statistics.median(timings[worker]["legacy"])
        vectorized_median = statistics.median(timings[worker]["vectorized"])
        vectorized_seconds_per_dataset = vectorized_median / args.datasets
        estimated_production_seconds_per_dataset = (
            vectorized_seconds_per_dataset * production_scale_factor
        )
        rows.append(
            {
                "workers": worker,
                "legacy_elapsed_seconds": timings[worker]["legacy"],
                "vectorized_elapsed_seconds": timings[worker]["vectorized"],
                "legacy_median_elapsed_seconds": legacy_median,
                "vectorized_median_elapsed_seconds": vectorized_median,
                "end_to_end_speedup_legacy_over_vectorized": (
                    legacy_median / vectorized_median
                ),
                "speedup_definition": SPEEDUP_DEFINITION,
                "vectorized_benchmark_seconds_per_dataset": vectorized_seconds_per_dataset,
                "production_scale_factor": production_scale_factor,
                "estimated_vectorized_production_seconds_per_dataset": (
                    estimated_production_seconds_per_dataset
                ),
                "estimated_vectorized_hours_per_2000_dataset_scenario": (
                    estimated_production_seconds_per_dataset
                    * FIRST_CHECKPOINT_DATASETS_PER_SCENARIO
                    / 3600.0
                ),
                "estimated_vectorized_hours_all_5_scenarios_sequential": (
                    estimated_production_seconds_per_dataset
                    * FIRST_CHECKPOINT_DATASETS_PER_SCENARIO
                    * SCENARIO_COUNT
                    / 3600.0
                ),
            }
        )

    result = {
        "benchmark_kind": "non_outcome_vectorized_coverage_execution",
        "historical_study_0_scores_read": False,
        "coverage_outcomes_aggregated": False,
        "production_coverage_gate_executed": False,
        "exact_dataset_outcome_equivalence_verified": equivalence_verified,
        "speedup_definition": SPEEDUP_DEFINITION,
        "execution_contract": {
            "selected_engine": execution_contract["engine"],
            "reference_oracle_engine": execution_contract["reference_oracle_engine"],
            "exact_dataset_outcome_equivalence_required": execution_contract[
                "exact_dataset_outcome_equivalence_required"
            ],
            "implementation_only": execution_contract.get("implementation_only"),
        },
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
            "speedup_compares_same_worker_count": True,
            "small_sample_speedup_is_qualitative_not_high_precision": True,
            "production_extrapolation_scales_to_frozen_10000_bootstrap_replicates": True,
            "extrapolation_is_not_a_runtime_guarantee": True,
            "chronicle_resolution_requires_review": True,
            "contract_selected_engine_is_vectorized": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
