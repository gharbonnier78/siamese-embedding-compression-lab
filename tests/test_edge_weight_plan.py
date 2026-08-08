from __future__ import annotations

import unittest

import numpy as np

from siamese_compression_lab.edge_weight_plan import (
    build_edge_weight_plan,
    edge_weights_from_plan,
)
from siamese_compression_lab.subject_bootstrap import (
    SubjectPairRow,
    edge_weights,
    subject_universe,
)


def _rows() -> list[SubjectPairRow]:
    return [
        SubjectPairRow("g_a", 1, "A", "A", "matched", 0),
        SubjectPairRow("g_b", 1, "B", "B", "matched", 1),
        SubjectPairRow("i_ab", 0, "A", "B", "mismatched", 0),
        SubjectPairRow("i_ac", 0, "A", "C", "mismatched", 1),
        SubjectPairRow("i_bc", 0, "B", "C", "mismatched", 2),
    ]


class EdgeWeightPlanTests(unittest.TestCase):
    def test_plan_matches_reference_weight_rule_exactly(self) -> None:
        rows = _rows()
        plan = build_edge_weight_plan(rows, subject_universe(rows))
        multiplicities = {"A": 2, "B": 1, "C": 3}
        expected = edge_weights(rows, multiplicities)
        actual = edge_weights_from_plan(plan, multiplicities)
        self.assertEqual(actual.dtype, np.dtype(np.int64))
        np.testing.assert_array_equal(actual, expected)

    def test_plan_matches_reference_over_deterministic_random_draws(self) -> None:
        rows = _rows()
        subjects = subject_universe(rows)
        plan = build_edge_weight_plan(rows, subjects)
        rng = np.random.Generator(np.random.PCG64(20260808))
        for _ in range(100):
            counts = rng.multinomial(
                len(subjects), np.full(len(subjects), 1.0 / len(subjects))
            )
            multiplicities = {
                subject: int(count) for subject, count in zip(subjects, counts)
            }
            np.testing.assert_array_equal(
                edge_weights_from_plan(plan, multiplicities),
                edge_weights(rows, multiplicities),
            )

    def test_missing_subject_multiplicity_is_zero_like_reference(self) -> None:
        rows = _rows()
        plan = build_edge_weight_plan(rows, subject_universe(rows))
        multiplicities = {"A": 2, "B": 1}
        np.testing.assert_array_equal(
            edge_weights_from_plan(plan, multiplicities),
            edge_weights(rows, multiplicities),
        )

    def test_negative_multiplicity_fails_like_reference(self) -> None:
        rows = _rows()
        plan = build_edge_weight_plan(rows, subject_universe(rows))
        multiplicities = {"A": -1, "B": 2, "C": 2}
        with self.assertRaisesRegex(ValueError, "must be non-negative"):
            edge_weights(rows, multiplicities)
        with self.assertRaisesRegex(ValueError, "must be non-negative"):
            edge_weights_from_plan(plan, multiplicities)

    def test_plan_contains_only_observed_edge_slots(self) -> None:
        rows = _rows()
        plan = build_edge_weight_plan(rows, subject_universe(rows))
        self.assertEqual(len(plan.left_indices), len(rows))
        self.assertEqual(len(plan.right_indices), len(rows))
        self.assertEqual(len(plan.genuine_mask), len(rows))


if __name__ == "__main__":
    unittest.main()
