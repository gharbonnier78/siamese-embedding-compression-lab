"""Benchmark Experiment #2: vectorized edge weights without reading Study 0 scores."""

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


def _timed(callable_):
    started = time.perf_counter()
    value = callable_()
    return time.perf_counter() - started, value


def _scalar_draw_and_weight(rows, subjects, draws: int, seed: int):
    rng = np.random.Generator(np.random.PCG64(seed))
    last = None
    for _ in range(draws):
        multiplicities = draw_subject_multiplicities(subjects, rng)
        last = edge_weights(rows, multiplicities)
    return last


def _vectorized_draw_and_weight(plan, draws: int, seed: int):
    rng = np.random.Generator(np.random.PCG64(seed))
    last = None
    for _ in range(draws):
        multiplicities = draw_subject_multiplicity_vector(plan, rng)
        last = edge_weights_vectorized(plan, multiplicities)
    return last


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--component-draws", type=int, default=5000)
    parser.add_argument("--bootstrap-replicates", type=int, default=1000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.component_draws <= 0 or args.bootstrap_replicates <= 0 or args.repeats <= 0:
        raise ValueError("benchmark counts must be positive")

    scenario = CoverageScenario(
        name="edge_weights_vectorization_benchmark",
        target_delta_fnmr=0.015,
        subject_effect_sd_genuine=0.08,
        subject_effect_sd_impostor=0.05,
    )
    graph = make_sparse_graph(scenario, seed=20260808)
    truth = scenario_truth(scenario)
    candidate, reference = simulate_distances(scenario, graph, seed=20260809)
    plan = compile_edge_weight_plan(graph)

    # Validate exact multinomial draws and resulting edge weights before timing.
    scalar_rng = np.random.Generator(np.random.PCG64(20260810))
    vectorized_rng = np.random.Generator(np.random.PCG64(20260810))
    for _ in range(200):
        scalar_map = draw_subject_multiplicities(plan.subjects, scalar_rng)
        vector_counts = draw_subject_multiplicity_vector(plan, vectorized_rng)
        expected_counts = np.asarray(
            [scalar_map[subject] for subject in plan.subjects], dtype=np.int64
        )
        np.testing.assert_array_equal(vector_counts, expected_counts)
        np.testing.assert_array_equal(
            edge_weights_vectorized(plan, vector_counts),
            edge_weights(graph, scalar_map),
        )

    scalar_component_times = []
    vector_component_times = []
    scalar_representation_times = []
    vector_representation_times = []
    scalar_operational_times = []
    vector_operational_times = []

    for repeat in range(args.repeats):
        seed = 20260900 + repeat
        elapsed, scalar_last = _timed(
            lambda seed=seed: _scalar_draw_and_weight(
                graph, plan.subjects, args.component_draws, seed
            )
        )
        scalar_component_times.append(elapsed)
        elapsed, vector_last = _timed(
            lambda seed=seed: _vectorized_draw_and_weight(plan, args.component_draws, seed)
        )
        vector_component_times.append(elapsed)
        np.testing.assert_array_equal(vector_last, scalar_last)

        elapsed, scalar_representation = _timed(
            lambda seed=seed: subject_bootstrap_delta_fnmr(
                rows=graph,
                candidate_distances=candidate,
                reference_distances=reference,
                target_fmr=scenario.target_fmr,
                replicates=args.bootstrap_replicates,
                seed=seed,
            )
        )
        scalar_representation_times.append(elapsed)
        elapsed, vector_representation = _timed(
            lambda seed=seed: subject_bootstrap_delta_fnmr_vectorized(
                rows=graph,
                candidate_distances=candidate,
                reference_distances=reference,
                target_fmr=scenario.target_fmr,
                replicates=args.bootstrap_replicates,
                seed=seed,
            )
        )
        vector_representation_times.append(elapsed)
        if vector_representation != scalar_representation:
            raise AssertionError("vectorized representation bootstrap changed outputs")

        elapsed, scalar_operational = _timed(
            lambda seed=seed: subject_bootstrap_fixed_threshold(
                rows=graph,
                distances=candidate,
                validation_threshold=truth.candidate_threshold,
                replicates=args.bootstrap_replicates,
                seed=seed,
            )
        )
        scalar_operational_times.append(elapsed)
        elapsed, vector_operational = _timed(
            lambda seed=seed: subject_bootstrap_fixed_threshold_vectorized(
                rows=graph,
                distances=candidate,
                validation_threshold=truth.candidate_threshold,
                replicates=args.bootstrap_replicates,
                seed=seed,
            )
        )
        vector_operational_times.append(elapsed)
        if vector_operational != scalar_operational:
            raise AssertionError("vectorized operational bootstrap changed outputs")

    scalar_component_median = statistics.median(scalar_component_times)
    vector_component_median = statistics.median(vector_component_times)
    scalar_representation_median = statistics.median(scalar_representation_times)
    vector_representation_median = statistics.median(vector_representation_times)
    scalar_operational_median = statistics.median(scalar_operational_times)
    vector_operational_median = statistics.median(vector_operational_times)
    scalar_end_to_end_median = scalar_representation_median + scalar_operational_median
    vector_end_to_end_median = vector_representation_median + vector_operational_median

    result = {
        "benchmark_kind": "non_outcome_edge_weights_vectorization",
        "historical_study_0_scores_read": False,
        "coverage_outcomes_aggregated": False,
        "production_coverage_gate_executed": False,
        "scalar_vectorized_outputs_identical": True,
        "configuration": {
            "component_draws": args.component_draws,
            "bootstrap_replicates": args.bootstrap_replicates,
            "repeats": args.repeats,
            "pairs": len(graph),
            "subjects": len(plan.subjects),
        },
        "component_draw_plus_edge_weights": {
            "scalar_elapsed_seconds": scalar_component_times,
            "vectorized_elapsed_seconds": vector_component_times,
            "scalar_median_seconds": scalar_component_median,
            "vectorized_median_seconds": vector_component_median,
            "speedup": scalar_component_median / vector_component_median,
        },
        "representation": {
            "scalar_elapsed_seconds": scalar_representation_times,
            "vectorized_elapsed_seconds": vector_representation_times,
            "scalar_median_seconds": scalar_representation_median,
            "vectorized_median_seconds": vector_representation_median,
            "speedup": scalar_representation_median / vector_representation_median,
        },
        "operational": {
            "scalar_elapsed_seconds": scalar_operational_times,
            "vectorized_elapsed_seconds": vector_operational_times,
            "scalar_median_seconds": scalar_operational_median,
            "vectorized_median_seconds": vector_operational_median,
            "speedup": scalar_operational_median / vector_operational_median,
        },
        "end_to_end_representation_plus_operational": {
            "scalar_median_seconds": scalar_end_to_end_median,
            "vectorized_median_seconds": vector_end_to_end_median,
            "speedup": scalar_end_to_end_median / vector_end_to_end_median,
            "scalar_seconds_per_replicate": (
                scalar_end_to_end_median / args.bootstrap_replicates
            ),
            "vectorized_seconds_per_replicate": (
                vector_end_to_end_median / args.bootstrap_replicates
            ),
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "interpretation_boundary": {
            "component_speedup_is_not_end_to_end_speedup": True,
            "small_benchmark_is_for_engineering_decision_not_precise_metrology": True,
            "historical_scores_remain_unread": True,
            "chronicle_resolution_requires_review": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
