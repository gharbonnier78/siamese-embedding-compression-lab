from __future__ import annotations

import unittest

import numpy as np

from siamese_compression_lab.coverage_simulation import (
    CoverageScenario,
    make_sparse_graph,
    scenario_truth,
    simulate_distances,
)
from siamese_compression_lab.subject_bootstrap import (
    DegenerateReplicateError,
    SubjectPairRow,
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


def _fixture_rows() -> list[SubjectPairRow]:
    return [
        SubjectPairRow("g_a", 1, "A", "A", "matched", 0),
        SubjectPairRow("g_b", 1, "B", "B", "matched", 1),
        SubjectPairRow("g_c", 1, "C", "C", "matched", 2),
        SubjectPairRow("i_ab", 0, "A", "B", "mismatched", 0),
        SubjectPairRow("i_ac", 0, "A", "C", "mismatched", 1),
        SubjectPairRow("i_bc", 0, "B", "C", "mismatched", 2),
    ]


class VectorizedEdgeWeightTests(unittest.TestCase):
    def test_vectorized_weights_match_reviewed_scalar_reference(self) -> None:
        rows = _fixture_rows()
        plan = compile_edge_weight_plan(rows)
        rng = np.random.Generator(np.random.PCG64(20260808))
        for _ in range(200):
            counts = rng.integers(0, 8, size=len(plan.subjects), dtype=np.int64)
            multiplicities = {
                subject: int(value)
                for subject, value in zip(plan.subjects, counts)
            }
            np.testing.assert_array_equal(
                edge_weights_vectorized(plan, counts),
                edge_weights(rows, multiplicities),
            )

    def test_vectorized_weights_preserve_sparse_row_order_and_rules(self) -> None:
        rows = _fixture_rows()
        plan = compile_edge_weight_plan(rows)
        counts = np.asarray([2, 1, 3], dtype=np.int64)
        weights = edge_weights_vectorized(plan, counts)
        np.testing.assert_array_equal(weights, np.asarray([2, 1, 3, 2, 6, 3]))

    def test_vector_draw_matches_scalar_draw_for_same_rng_state(self) -> None:
        plan = compile_edge_weight_plan(_fixture_rows())
        for seed in (1, 7, 29, 101, 20260807):
            scalar_rng = np.random.Generator(np.random.PCG64(seed))
            vector_rng = np.random.Generator(np.random.PCG64(seed))
            scalar = draw_subject_multiplicities(plan.subjects, scalar_rng)
            vector = draw_subject_multiplicity_vector(plan, vector_rng)
            expected = np.asarray(
                [scalar[subject] for subject in plan.subjects], dtype=np.int64
            )
            np.testing.assert_array_equal(vector, expected)

    def test_negative_multiplicity_remains_rejected(self) -> None:
        plan = compile_edge_weight_plan(_fixture_rows())
        counts = np.asarray([-1, 1, 1], dtype=np.int64)
        with self.assertRaisesRegex(ValueError, "non-negative"):
            edge_weights_vectorized(plan, counts)

    def test_representation_bootstrap_matches_scalar_path_exactly(self) -> None:
        scenario = CoverageScenario(
            name="vectorized_equivalence",
            target_delta_fnmr=0.015,
            n_subjects=30,
            n_genuine=20,
            n_impostor=20,
            target_fmr=0.10,
            subject_effect_sd_genuine=0.04,
            subject_effect_sd_impostor=0.03,
        )
        rows = make_sparse_graph(scenario, seed=11)
        candidate, reference = simulate_distances(scenario, rows, seed=29)
        kwargs = dict(
            rows=rows,
            candidate_distances=candidate,
            reference_distances=reference,
            target_fmr=scenario.target_fmr,
            replicates=50,
            seed=47,
        )
        try:
            scalar = subject_bootstrap_delta_fnmr(**kwargs)
        except DegenerateReplicateError as scalar_error:
            with self.assertRaises(DegenerateReplicateError) as vector_error:
                subject_bootstrap_delta_fnmr_vectorized(**kwargs)
            self.assertEqual(vector_error.exception.audit, scalar_error.audit)
            self.assertEqual(
                vector_error.exception.completed_replicates,
                scalar_error.completed_replicates,
            )
        else:
            vectorized = subject_bootstrap_delta_fnmr_vectorized(**kwargs)
            self.assertEqual(vectorized, scalar)

    def test_operational_bootstrap_matches_scalar_path_exactly(self) -> None:
        scenario = CoverageScenario(
            name="vectorized_operational_equivalence",
            target_delta_fnmr=0.015,
            n_subjects=30,
            n_genuine=20,
            n_impostor=20,
            target_fmr=0.10,
            subject_effect_sd_genuine=0.04,
            subject_effect_sd_impostor=0.03,
        )
        rows = make_sparse_graph(scenario, seed=71)
        candidate, _ = simulate_distances(scenario, rows, seed=101)
        kwargs = dict(
            rows=rows,
            distances=candidate,
            validation_threshold=scenario_truth(scenario).candidate_threshold,
            replicates=50,
            seed=47,
        )
        try:
            scalar = subject_bootstrap_fixed_threshold(**kwargs)
        except DegenerateReplicateError as scalar_error:
            with self.assertRaises(DegenerateReplicateError) as vector_error:
                subject_bootstrap_fixed_threshold_vectorized(**kwargs)
            self.assertEqual(vector_error.exception.audit, scalar_error.audit)
            self.assertEqual(
                vector_error.exception.completed_replicates,
                scalar_error.completed_replicates,
            )
        else:
            vectorized = subject_bootstrap_fixed_threshold_vectorized(**kwargs)
            self.assertEqual(vectorized, scalar)


if __name__ == "__main__":
    unittest.main()
