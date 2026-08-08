"""Benchmark Experiment #2 vectorized edge weights without outcome-bearing evidence.

This benchmark compares the reviewed scalar subject-bootstrap path with the candidate
pre-indexed NumPy path. It never reads historical Study 0 scores, aggregates coverage, or
executes the production coverage gate. Exact scalar/vectorized equality is required before
speedup is reported.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
from pathlib import Path

import numpy as np

from siamese_compression_lab.coverage_simulation import (
    CoverageScenario,
    make_sparse_graph,
    scenario_truth,
    simulate_distances,
)
from siamese_compression_lab.subject_bootstrap import (
    draw_subject_multiplicities,
    edge_weights,
    subject_bootstrap_delta_fnmr,
)
from siamese_compression_lab.subject_bootstrap_operational import (
    subject_bootstrap_fixed_threshold,
)
from siamese_compression_lab.subject_bootstrap_vectorized import (
    compile_edge_weight_plan,
    draw_subject_multiplicity_vector,
    edge_weights_vectorized,
    subject_bootstrap_delta_fnmr_vectorized,
    subject_bootstrap_fixed_threshold_vectorized,
)


def _seconds(callable_) -> tuple[float, object]:
    started = time.perf_counter()
    result = callable_()
    return time.perf_counter() - started, result


def _scalar_weight_loop(rows, subjects, replicates: int, seed: int):
    rng = np.random.Generator(np.random.PCG64(seed))
    last = None
    for _ in range(replicates):
        multiplicities = draw_subject_multiplicities(subjects, rng)
        last = edge_weights(rows, multiplicities)
    return last


def _vector_weight_loop(plan, replicates: int, seed: int):
    rng = np.random.Generator(np.random.PCG64(seed))
    last = None
    for _ in range(replicates):
        multiplicities = draw_subject_multiplicity_vector(plan, rng)
        last = edge_weights_vectorized(plan, multiplicities)
    return last


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=1000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.replicates <= 0 or args.repeats <= 0:
        raise ValueError("replicates and repeats must be positive")

    scenario = CoverageScenario(
        name="vectorized_edge_weights_benchmark",
        target_delta_fnmr=0.015,
        subject_effect_sd_genuine=0.08,
        subject_effect_sd_impostor=0.05,
    )
    rows = make_sparse_graph(scenario, seed=20260808)
    candidate, reference = simulate_distances(scenario, rows, seed=20260809)
    plan = compile_edge_weight_plan(rows)
    threshold = scenario_truth(scenario).candidate_threshold

    # Pre-timing semantic checks use identical RNG states and the frozen sparse graph.
    scalar_rng = np.random.Generator(np.random.PCG64(20260810))
    vector_rng = np.random.Generator(np.random.PCG64(20260810))
    for _ in range(200):
        scalar_map = draw_subject_multiplicities(plan.subjects, scalar_rng)
        vector_counts = draw_subject_multiplicity_vector(plan, vector_rng)
        expected_counts = np.asarray(
            [scalar_map[subject] for subject in plan.subjects], dtype=np.int64
        )
        np.testing.assert_array_equal(vector_counts, expected_counts)
        np.testing.assert_array_equal(
            edge_weights_vectorized(plan, vector_counts),
            edge_weights(rows, scalar_map),
        )

    reference_representation = subject_bootstrap_delta_fnmr(
        rows=rows,
        candidate_distances=candidate,
        reference_distances=reference,
        target_fmr=scenario.target_fmr,
        replicates=args.replicates,
        seed=20260811,
    )
    candidate_representation = subject_bootstrap_delta_fnmr_vectorized(
        rows=rows,
        candidate_distances=candidate,
        reference_distances=reference,
        target_fmr=scenario.target_fmr,
        replicates=args.replicates,
        seed=20260811,
    )
    if candidate_representation != reference_representation:
        raise AssertionError("vectorized representation bootstrap changed scalar outputs")

    reference_operational = subject_bootstrap_fixed_threshold(
        rows=rows,
        distances=candidate,
        validation_threshold=threshold,
        replicates=args.replicates,
        seed=20260811,
    )
    candidate_operational = subject_bootstrap_fixed_threshold_vectorized(
        rows=rows,
        distances=candidate,
        validation_threshold=threshold,
        replicates=args.replicates,
        seed=20260811,
    )
    if candidate_operational != reference_operational:
        raise AssertionError("vectorized operational bootstrap changed scalar outputs")

    timings = {
        "scalar_draw_plus_edge_weights": [],
        "vectorized_draw_plus_edge_weights": [],
        "scalar_representation": [],
        "vectorized_representation": [],
        "scalar_operational": [],
        "vectorized_operational": [],
    }

    for repeat in range(args.repeats):
        seed = 20260900 + repeat
        elapsed, scalar_last = _seconds(
            lambda seed=seed: _scalar_weight_loop(
                rows, plan.subjects, args.replicates, seed
            )
        )
        timings["scalar_draw_plus_edge_weights"].append(elapsed)
        elapsed, vector_last = _seconds(
            lambda seed=seed: _vector_weight_loop(plan, args.replicates, seed)
        )
        timings["vectorized_draw_plus_edge_weights"].append(elapsed)
        np.testing.assert_array_equal(vector_last, scalar_last)

        elapsed, scalar_rep = _seconds(
            lambda seed=seed: subject_bootstrap_delta_fnmr(
                rows=rows,
                candidate_distances=candidate,
                reference_distances=reference,
                target_fmr=scenario.target_fmr,
                replicates=args.replicates,
                seed=seed,
            )
        )
        timings["scalar_representation"].append(elapsed)
        elapsed, vector_rep = _seconds(
            lambda seed=seed: subject_bootstrap_delta_fnmr_vectorized(
                rows=rows,
                candidate_distances=candidate,
                reference_distances=reference,
                target_fmr=scenario.target_fmr,
                replicates=args.replicates,
                seed=seed,
            )
        )
        timings["vectorized_representation"].append(elapsed)
        if vector_rep != scalar_rep:
            raise AssertionError("timed representation outputs diverged")

        elapsed, scalar_op = _seconds(
            lambda seed=seed: subject_bootstrap_fixed_threshold(
                rows=rows,
                distances=candidate,
                validation_threshold=threshold,
                replicates=args.replicates,
                seed=seed,
            )
        )
        timings["scalar_operational"].append(elapsed)
        elapsed, vector_op = _seconds(
            lambda seed=seed: subject_bootstrap_fixed_threshold_vectorized(
                rows=rows,
                distances=candidate,
                validation_threshold=threshold,
                replicates=args.replicates,
                seed=seed,
            )
        )
        timings["vectorized_operational"].append(elapsed)
        if vector_op != scalar_op:
            raise AssertionError("timed operational outputs diverged")

    medians = {key: statistics.median(values) for key, values in timings.items()}
    scalar_total = medians["scalar_representation"] + medians["scalar_operational"]
    vector_total = medians["vectorized_representation"] + medians["vectorized_operational"]

    result = {
        "benchmark_kind": "non_outcome_vectorized_edge_weights",
        "historical_study_0_scores_read": False,
        "coverage_outcomes_aggregated": False,
        "production_coverage_gate_executed": False,
        "scalar_vectorized_equivalence_verified": True,
        "configuration": {
            "replicates_per_timed_run": args.replicates,
            "repeats": args.repeats,
            "subjects": len(plan.subjects),
            "pairs": len(rows),
            "genuine": int(np.sum(plan.same == 1)),
            "impostor": int(np.sum(plan.same == 0)),
            "target_fmr": scenario.target_fmr,
        },
        "timings_seconds": timings,
        "medians_seconds": medians,
        "speedups": {
            "draw_plus_edge_weights": (
                medians["scalar_draw_plus_edge_weights"]
                / medians["vectorized_draw_plus_edge_weights"]
            ),
            "representation": (
                medians["scalar_representation"]
                / medians["vectorized_representation"]
            ),
            "operational": (
                medians["scalar_operational"]
                / medians["vectorized_operational"]
            ),
            "combined_representation_plus_operational": scalar_total / vector_total,
        },
        "combined_seconds_per_replicate": {
            "scalar": scalar_total / args.replicates,
            "vectorized": vector_total / args.replicates,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "interpretation_boundary": {
            "component_speedup_is_not_end_to_end_speedup": True,
            "benchmark_is_not_production_runtime_guarantee": True,
            "chronicle_resolution_requires_review": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
