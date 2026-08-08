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
    subject_universe,
)
from siamese_compression_lab.subject_bootstrap_operational import (
    subject_bootstrap_fixed_threshold,
)
from siamese_compression_lab.subject_bootstrap_vectorized import (
    compile_edge_weight_plan,
    edge_weights_vectorized,
    subject_bootstrap_delta_fnmr_vectorized,
    subject_bootstrap_fixed_threshold_vectorized,
)


def _timed(callable_):
    started = time.perf_counter()
    value = callable_()
    return time.perf_counter() - started, value


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
    subjects = subject_universe(graph)
    plan = compile_edge_weight_plan(graph)

    rng = np.random.Generator(np.random.PCG64(20260810))
    multiplicity_draws = [
        draw_subject_multiplicities(subjects, rng) for _ in range(args.component_draws)
    ]

    scalar_component_times = []
    vector_component_times = []
    for _ in range(args.repeats):
        elapsed, scalar_weights = _timed(
            lambda: [edge_weights(graph, draw) for draw in multiplicity_draws]
        )
        scalar_component_times.append(elapsed)
        elapsed, vector_weights = _timed(
            lambda: [edge_weights_vectorized(plan, draw) for draw in multiplicity_draws]
        )
        vector_component_times.append(elapsed)
        for scalar, vectorized in zip(scalar_weights, vector_weights):
            np.testing.assert_array_equal(vectorized, scalar)

    scalar_end_to_end_times = []
    vector_end_to_end_times = []
    for _ in range(args.repeats):
        elapsed, scalar_representation = _timed(
            lambda: subject_bootstrap_delta_fnmr(
                rows=graph,
                candidate_distances=candidate,
                reference_distances=reference,
                target_fmr=scenario.target_fmr,
                replicates=args.bootstrap_replicates,
                seed=20260811,
            )
        )
        scalar_end_to_end_times.append(elapsed)
        elapsed, vector_representation = _timed(
            lambda: subject_bootstrap_delta_fnmr_vectorized(
                rows=graph,
                candidate_distances=candidate,
                reference_distances=reference,
                target_fmr=scenario.target_fmr,
                replicates=args.bootstrap_replicates,
                seed=20260811,
            )
        )
        vector_end_to_end_times.append(elapsed)
        if vector_representation != scalar_representation:
            raise AssertionError("vectorized representation bootstrap changed outputs")

        elapsed, scalar_operational = _timed(
            lambda: subject_bootstrap_fixed_threshold(
                rows=graph,
                distances=candidate,
                validation_threshold=truth.candidate_threshold,
                replicates=args.bootstrap_replicates,
                seed=20260811,
            )
        )
        scalar_end_to_end_times[-1] += elapsed
        elapsed, vector_operational = _timed(
            lambda: subject_bootstrap_fixed_threshold_vectorized(
                rows=graph,
                distances=candidate,
                validation_threshold=truth.candidate_threshold,
                replicates=args.bootstrap_replicates,
                seed=20260811,
            )
        )
        vector_end_to_end_times[-1] += elapsed
        if vector_operational != scalar_operational:
            raise AssertionError("vectorized operational bootstrap changed outputs")

    scalar_component_median = statistics.median(scalar_component_times)
    vector_component_median = statistics.median(vector_component_times)
    scalar_end_to_end_median = statistics.median(scalar_end_to_end_times)
    vector_end_to_end_median = statistics.median(vector_end_to_end_times)

    result = {
        "benchmark_kind": "non_outcome_edge_weights_vectorization",
        "historical_study_0_scores_read": False,
        "production_coverage_gate_executed": False,
        "scalar_vectorized_outputs_identical": True,
        "configuration": {
            "component_draws": args.component_draws,
            "bootstrap_replicates": args.bootstrap_replicates,
            "repeats": args.repeats,
            "pairs": len(graph),
            "subjects": len(subjects),
        },
        "component": {
            "scalar_elapsed_seconds": scalar_component_times,
            "vectorized_elapsed_seconds": vector_component_times,
            "scalar_median_seconds": scalar_component_median,
            "vectorized_median_seconds": vector_component_median,
            "speedup": scalar_component_median / vector_component_median,
        },
        "end_to_end_representation_plus_operational": {
            "scalar_elapsed_seconds": scalar_end_to_end_times,
            "vectorized_elapsed_seconds": vector_end_to_end_times,
            "scalar_median_seconds": scalar_end_to_end_median,
            "vectorized_median_seconds": vector_end_to_end_median,
            "speedup": scalar_end_to_end_median / vector_end_to_end_median,
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
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
