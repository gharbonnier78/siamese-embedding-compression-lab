from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np

from siamese_compression_lab.subject_bootstrap import (
    DegenerateReplicateError,
    SubjectPairRow,
    edge_weights,
    subject_bootstrap_delta_fnmr,
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
        subjects = ["A", "B", "C"]
        for _ in range(200):
            values = rng.integers(0, 8, size=len(subjects))
            multiplicities = {
                subject: int(value) for subject, value in zip(subjects, values)
            }
            np.testing.assert_array_equal(
                edge_weights_vectorized(plan, multiplicities),
                edge_weights(rows, multiplicities),
            )

    def test_vectorized_weights_preserve_sparse_row_order_and_rules(self) -> None:
        rows = _fixture_rows()
        plan = compile_edge_weight_plan(rows)
        weights = edge_weights_vectorized(plan, {"A": 2, "B": 1, "C": 3})
        np.testing.assert_array_equal(weights, np.asarray([2, 1, 3, 2, 6, 3]))

    def test_negative_multiplicity_remains_rejected(self) -> None:
        plan = compile_edge_weight_plan(_fixture_rows())
        with self.assertRaisesRegex(ValueError, "non-negative"):
            edge_weights_vectorized(plan, {"A": -1, "B": 1, "C": 1})

    def test_representation_bootstrap_matches_scalar_path_exactly(self) -> None:
        rows = _fixture_rows()
        candidate = np.asarray([0.42, 0.47, 0.51, 0.72, 0.79, 0.83])
        reference = np.asarray([0.40, 0.45, 0.50, 0.70, 0.80, 0.84])
        scalar = subject_bootstrap_delta_fnmr(
            rows=rows,
            candidate_distances=candidate,
            reference_distances=reference,
            target_fmr=0.34,
            replicates=25,
            seed=12345,
        )
        vectorized = subject_bootstrap_delta_fnmr_vectorized(
            rows=rows,
            candidate_distances=candidate,
            reference_distances=reference,
            target_fmr=0.34,
            replicates=25,
            seed=12345,
        )
        self.assertEqual(vectorized, scalar)

    def test_operational_bootstrap_matches_scalar_path_exactly(self) -> None:
        rows = _fixture_rows()
        distances = np.asarray([0.42, 0.47, 0.51, 0.72, 0.79, 0.83])
        scalar = subject_bootstrap_fixed_threshold(
            rows=rows,
            distances=distances,
            validation_threshold=0.75,
            replicates=25,
            seed=9876,
        )
        vectorized = subject_bootstrap_fixed_threshold_vectorized(
            rows=rows,
            distances=distances,
            validation_threshold=0.75,
            replicates=25,
            seed=9876,
        )
        self.assertEqual(vectorized, scalar)

    def test_degenerate_audit_matches_scalar_path(self) -> None:
        rows = _fixture_rows()
        candidate = np.asarray([0.42, 0.47, 0.51, 0.72, 0.79, 0.83])
        reference = np.asarray([0.40, 0.45, 0.50, 0.70, 0.80, 0.84])
        draws = [
            {"A": 1, "B": 1, "C": 1},
            {"A": 3, "B": 0, "C": 0},
        ]
        with patch(
            "siamese_compression_lab.subject_bootstrap.draw_subject_multiplicities",
            side_effect=draws,
        ), self.assertRaises(DegenerateReplicateError) as scalar_error:
            subject_bootstrap_delta_fnmr(
                rows=rows,
                candidate_distances=candidate,
                reference_distances=reference,
                target_fmr=0.34,
                replicates=2,
                seed=1,
            )
        with patch(
            "siamese_compression_lab.subject_bootstrap_vectorized.draw_subject_multiplicities",
            side_effect=draws,
        ), self.assertRaises(DegenerateReplicateError) as vectorized_error:
            subject_bootstrap_delta_fnmr_vectorized(
                rows=rows,
                candidate_distances=candidate,
                reference_distances=reference,
                target_fmr=0.34,
                replicates=2,
                seed=1,
            )
        self.assertEqual(vectorized_error.exception.audit, scalar_error.exception.audit)
        self.assertEqual(
            vectorized_error.exception.completed_replicates,
            scalar_error.exception.completed_replicates,
        )


if __name__ == "__main__":
    unittest.main()
