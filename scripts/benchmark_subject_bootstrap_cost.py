"""Benchmark Study 0 v0.2.2 bootstrap execution cost without computing coverage outcomes.

This script is feasibility evidence only. It generates one synthetic sparse graph and
synthetic distances, exercises the reviewed subject-bootstrap implementation, and
extrapolates wall-clock cost to the frozen first external checkpoint. It never reads
historical Study 0 scores and never evaluates the coverage gate.
"""

from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import numpy as np

from siamese_compression_lab.coverage_simulation import CoverageScenario, make_sparse_graph, simulate_distances
from siamese_compression_lab.subject_bootstrap import (
    draw_subject_multiplicities,
    edge_weights,
    subject_bootstrap_delta_fnmr,
    subject_universe,
    weighted_rates_at_threshold,
    weighted_threshold_at_fmr,
)
from siamese_compression_lab.subject_bootstrap_operational import subject_bootstrap_fixed_threshold


def _seconds(callable_) -> float:
    start = time.perf_counter()
    callable_()
    return time.perf_counter() - start


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=1000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.replicates <= 0 or args.repeats <= 0:
        raise ValueError("replicates and repeats must be positive")

    scenario = CoverageScenario(name="cost_benchmark", target_delta_fnmr=0.0)
    graph_seed = 20260808
    distance_seed = 20260809
    bootstrap_seed = 20260810
    rows = make_sparse_graph(scenario, seed=graph_seed)
    candidate, reference = simulate_distances(scenario, rows, seed=distance_seed)
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    subjects = subject_universe(rows)
    rng = np.random.Generator(np.random.PCG64(bootstrap_seed))
    multiplicities = draw_subject_multiplicities(subjects, rng)
    weights = edge_weights(rows, multiplicities)

    # Component timings use the same 1000/500/500 synthetic geometry as the frozen contract.
    component_repetitions = max(1000, args.replicates)
    component: dict[str, float] = {}

    local_rng = np.random.Generator(np.random.PCG64(bootstrap_seed + 1))
    component["draw_subject_multiplicities_seconds_per_call"] = _seconds(
        lambda: [draw_subject_multiplicities(subjects, local_rng) for _ in range(component_repetitions)]
    ) / component_repetitions
    component["edge_weights_seconds_per_call"] = _seconds(
        lambda: [edge_weights(rows, multiplicities) for _ in range(component_repetitions)]
    ) / component_repetitions
    component["weighted_threshold_seconds_per_call"] = _seconds(
        lambda: [
            weighted_threshold_at_fmr(same, candidate, weights, scenario.target_fmr)
            for _ in range(component_repetitions)
        ]
    ) / component_repetitions
    threshold = weighted_threshold_at_fmr(same, candidate, weights, scenario.target_fmr)
    component["weighted_rates_seconds_per_call"] = _seconds(
        lambda: [
            weighted_rates_at_threshold(same, candidate, weights, threshold)
            for _ in range(component_repetitions)
        ]
    ) / component_repetitions

    representation_runs: list[float] = []
    operational_runs: list[float] = []
    for repeat in range(args.repeats):
        seed = bootstrap_seed + repeat
        representation_runs.append(
            _seconds(
                lambda seed=seed: subject_bootstrap_delta_fnmr(
                    rows=rows,
                    candidate_distances=candidate,
                    reference_distances=reference,
                    target_fmr=scenario.target_fmr,
                    replicates=args.replicates,
                    seed=seed,
                )
            )
        )
        operational_runs.append(
            _seconds(
                lambda seed=seed: subject_bootstrap_fixed_threshold(
                    rows=rows,
                    distances=candidate,
                    validation_threshold=float(threshold),
                    replicates=args.replicates,
                    seed=seed,
                )
            )
        )

    representation_seconds_per_replicate = float(np.median(representation_runs) / args.replicates)
    operational_seconds_per_replicate = float(np.median(operational_runs) / args.replicates)
    combined_seconds_per_replicate = representation_seconds_per_replicate + operational_seconds_per_replicate

    frozen_bootstrap_replicates = 10_000
    first_checkpoint_datasets_per_scenario = 2_000
    scenario_count = 5
    first_checkpoint_datasets_total = first_checkpoint_datasets_per_scenario * scenario_count
    estimated_seconds_per_dataset = combined_seconds_per_replicate * frozen_bootstrap_replicates
    estimated_first_checkpoint_seconds_single_worker = estimated_seconds_per_dataset * first_checkpoint_datasets_total

    result = {
        "benchmark_kind": "non_outcome_computational_feasibility",
        "historical_study_0_scores_read": False,
        "coverage_outcomes_computed": False,
        "graph": {
            "pairs": len(rows),
            "genuine": int(np.sum(same == 1)),
            "impostor": int(np.sum(same == 0)),
            "subjects": len(subjects),
        },
        "benchmark": {
            "replicates_per_timed_run": args.replicates,
            "repeats": args.repeats,
            "representation_run_seconds": representation_runs,
            "operational_run_seconds": operational_runs,
            "representation_seconds_per_replicate_median": representation_seconds_per_replicate,
            "operational_seconds_per_replicate_median": operational_seconds_per_replicate,
            "combined_seconds_per_replicate_median": combined_seconds_per_replicate,
            "components": component,
        },
        "frozen_scale_extrapolation": {
            "bootstrap_replicates_per_dataset": frozen_bootstrap_replicates,
            "first_checkpoint_datasets_per_scenario": first_checkpoint_datasets_per_scenario,
            "scenario_count": scenario_count,
            "first_checkpoint_datasets_total": first_checkpoint_datasets_total,
            "estimated_seconds_per_dataset": estimated_seconds_per_dataset,
            "estimated_first_checkpoint_seconds_single_worker": estimated_first_checkpoint_seconds_single_worker,
            "estimated_first_checkpoint_hours_single_worker": estimated_first_checkpoint_seconds_single_worker / 3600.0,
            "note": "Linear extrapolation from a non-outcome synthetic timing benchmark; not a production runtime guarantee.",
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "decision_boundary": {
            "production_coverage_gate_executed": False,
            "historical_reanalysis_permitted_by_this_benchmark": False,
            "next_decision": "Use measured dominant costs to decide whether semantics-preserving optimization is required before resolving CHRON-20260808-001.",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
