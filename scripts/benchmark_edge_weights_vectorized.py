"""Benchmark the isolated vectorized edge-weight candidate against the reviewed legacy path."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import numpy as np

from siamese_compression_lab.coverage_simulation import CoverageScenario, make_sparse_graph
from siamese_compression_lab.edge_weights_vectorized import (
    edge_weights_vectorized_from_array,
    prepare_edge_index,
)
from siamese_compression_lab.subject_bootstrap import edge_weights


def _time_legacy(rows, subjects, draws) -> float:
    started = time.perf_counter()
    for values in draws:
        mapping = {subject: int(value) for subject, value in zip(subjects, values)}
        edge_weights(rows, mapping)
    return time.perf_counter() - started


def _time_vectorized(prepared, draws) -> float:
    started = time.perf_counter()
    for values in draws:
        edge_weights_vectorized_from_array(prepared, values)
    return time.perf_counter() - started


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--draws", type=int, default=5000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260808)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.draws <= 0 or args.repeats <= 0:
        raise ValueError("draws and repeats must be positive")

    scenario = CoverageScenario(name="edge_weights_benchmark", target_delta_fnmr=0.0)
    rows = make_sparse_graph(scenario, seed=args.seed)
    prepared = prepare_edge_index(rows)
    rng = np.random.Generator(np.random.PCG64(args.seed))
    draws = [
        rng.multinomial(
            len(prepared.subjects),
            np.full(len(prepared.subjects), 1.0 / len(prepared.subjects)),
        ).astype(np.int64, copy=False)
        for _ in range(args.draws)
    ]

    for values in draws[:100]:
        mapping = {
            subject: int(value)
            for subject, value in zip(prepared.subjects, values)
        }
        np.testing.assert_array_equal(
            edge_weights(rows, mapping),
            edge_weights_vectorized_from_array(prepared, values),
        )

    legacy = [_time_legacy(rows, prepared.subjects, draws) for _ in range(args.repeats)]
    vectorized = [_time_vectorized(prepared, draws) for _ in range(args.repeats)]
    legacy_median = statistics.median(legacy)
    vectorized_median = statistics.median(vectorized)

    result = {
        "benchmark_kind": "isolated_edge_weights_vectorization",
        "historical_study_0_scores_read": False,
        "production_coverage_gate_executed": False,
        "estimator_integration_changed": False,
        "equivalence_checked_before_timing": True,
        "configuration": {
            "subjects": len(prepared.subjects),
            "edges": len(rows),
            "genuine_edges": int(sum(row.same == 1 for row in rows)),
            "impostor_edges": int(sum(row.same == 0 for row in rows)),
            "draws_per_repeat": args.draws,
            "repeats": args.repeats,
            "seed": args.seed,
        },
        "legacy_elapsed_seconds": legacy,
        "vectorized_elapsed_seconds": vectorized,
        "legacy_median_seconds": legacy_median,
        "vectorized_median_seconds": vectorized_median,
        "speedup_legacy_over_vectorized": legacy_median / vectorized_median,
        "interpretation_boundary": {
            "microbenchmark_only": True,
            "full_bootstrap_speedup_not_inferred_without_reprofile": True,
            "integration_requires_exact_replay_evidence": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
