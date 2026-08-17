"""Reprofile full Study-0-like bootstrap paths with the vectorized edge-weight candidate.

This is non-outcome engineering evidence only. It compares the reviewed legacy estimator and
an exact-output vectorized candidate on synthetic data. It never reads historical Study 0
scores, aggregates coverage, or executes the production coverage gate.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from siamese_compression_lab.coverage_simulation import (
    CoverageScenario,
    make_sparse_graph,
    scenario_truth,
    simulate_distances,
)
from siamese_compression_lab.subject_bootstrap import subject_bootstrap_delta_fnmr
from siamese_compression_lab.subject_bootstrap_operational import (
    subject_bootstrap_fixed_threshold,
)
from siamese_compression_lab.subject_bootstrap_vectorized import (
    subject_bootstrap_delta_fnmr_vectorized,
    subject_bootstrap_fixed_threshold_vectorized,
)


def _seconds(callable_) -> float:
    started = time.perf_counter()
    callable_()
    return time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=1000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260808)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.replicates <= 0 or args.repeats <= 0:
        raise ValueError("replicates and repeats must be positive")

    scenario = CoverageScenario(
        name="full_bootstrap_vectorized_benchmark",
        target_delta_fnmr=0.015,
        subject_effect_sd_genuine=0.08,
        subject_effect_sd_impostor=0.05,
    )
    rows = make_sparse_graph(scenario, seed=args.seed)
    candidate, reference = simulate_distances(scenario, rows, seed=args.seed + 1)
    threshold = scenario_truth(scenario).candidate_threshold
    bootstrap_seed = args.seed + 2

    legacy_representation = subject_bootstrap_delta_fnmr(
        rows=rows,
        candidate_distances=candidate,
        reference_distances=reference,
        target_fmr=scenario.target_fmr,
        replicates=args.replicates,
        seed=bootstrap_seed,
    )
    vectorized_representation = subject_bootstrap_delta_fnmr_vectorized(
        rows=rows,
        candidate_distances=candidate,
        reference_distances=reference,
        target_fmr=scenario.target_fmr,
        replicates=args.replicates,
        seed=bootstrap_seed,
    )
    if vectorized_representation != legacy_representation:
        raise AssertionError("vectorized representation bootstrap changed replicate outputs")

    legacy_operational = subject_bootstrap_fixed_threshold(
        rows=rows,
        distances=candidate,
        validation_threshold=threshold,
        replicates=args.replicates,
        seed=bootstrap_seed,
    )
    vectorized_operational = subject_bootstrap_fixed_threshold_vectorized(
        rows=rows,
        distances=candidate,
        validation_threshold=threshold,
        replicates=args.replicates,
        seed=bootstrap_seed,
    )
    if vectorized_operational != legacy_operational:
        raise AssertionError("vectorized operational bootstrap changed replicate outputs")

    legacy_representation_times: list[float] = []
    vectorized_representation_times: list[float] = []
    legacy_operational_times: list[float] = []
    vectorized_operational_times: list[float] = []

    for _ in range(args.repeats):
        legacy_representation_times.append(
            _seconds(
                lambda: subject_bootstrap_delta_fnmr(
                    rows=rows,
                    candidate_distances=candidate,
                    reference_distances=reference,
                    target_fmr=scenario.target_fmr,
                    replicates=args.replicates,
                    seed=bootstrap_seed,
                )
            )
        )
        vectorized_representation_times.append(
            _seconds(
                lambda: subject_bootstrap_delta_fnmr_vectorized(
                    rows=rows,
                    candidate_distances=candidate,
                    reference_distances=reference,
                    target_fmr=scenario.target_fmr,
                    replicates=args.replicates,
                    seed=bootstrap_seed,
                )
            )
        )
        legacy_operational_times.append(
            _seconds(
                lambda: subject_bootstrap_fixed_threshold(
                    rows=rows,
                    distances=candidate,
                    validation_threshold=threshold,
                    replicates=args.replicates,
                    seed=bootstrap_seed,
                )
            )
        )
        vectorized_operational_times.append(
            _seconds(
                lambda: subject_bootstrap_fixed_threshold_vectorized(
                    rows=rows,
                    distances=candidate,
                    validation_threshold=threshold,
                    replicates=args.replicates,
                    seed=bootstrap_seed,
                )
            )
        )

    legacy_representation_median = statistics.median(legacy_representation_times)
    vectorized_representation_median = statistics.median(vectorized_representation_times)
    legacy_operational_median = statistics.median(legacy_operational_times)
    vectorized_operational_median = statistics.median(vectorized_operational_times)
    legacy_combined = legacy_representation_median + legacy_operational_median
    vectorized_combined = vectorized_representation_median + vectorized_operational_median

    result = {
        "benchmark_kind": "non_outcome_full_bootstrap_vectorized_reprofile",
        "historical_study_0_scores_read": False,
        "coverage_outcomes_aggregated": False,
        "production_coverage_gate_executed": False,
        "exact_representation_replay_verified": True,
        "exact_operational_replay_verified": True,
        "configuration": {
            "subjects": scenario.n_subjects,
            "pairs": scenario.n_genuine + scenario.n_impostor,
            "bootstrap_replicates": args.replicates,
            "repeats": args.repeats,
            "seed": args.seed,
            "target_fmr": scenario.target_fmr,
        },
        "legacy_representation_elapsed_seconds": legacy_representation_times,
        "vectorized_representation_elapsed_seconds": vectorized_representation_times,
        "legacy_operational_elapsed_seconds": legacy_operational_times,
        "vectorized_operational_elapsed_seconds": vectorized_operational_times,
        "legacy_representation_median_seconds": legacy_representation_median,
        "vectorized_representation_median_seconds": vectorized_representation_median,
        "legacy_operational_median_seconds": legacy_operational_median,
        "vectorized_operational_median_seconds": vectorized_operational_median,
        "representation_speedup": (
            legacy_representation_median / vectorized_representation_median
        ),
        "operational_speedup": legacy_operational_median / vectorized_operational_median,
        "legacy_combined_median_seconds": legacy_combined,
        "vectorized_combined_median_seconds": vectorized_combined,
        "combined_speedup": legacy_combined / vectorized_combined,
        "interpretation_boundary": {
            "synthetic_timing_only": True,
            "exact_output_equivalence_required_before_timing": True,
            "production_runtime_not_claimed": True,
            "historical_reanalysis_not_permitted_by_this_benchmark": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
