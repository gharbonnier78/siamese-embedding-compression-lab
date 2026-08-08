from __future__ import annotations

import unittest

import numpy as np

from siamese_compression_lab.edge_weights_vectorized import (
    edge_weights_vectorized,
    edge_weights_vectorized_from_array,
    multiplicity_vector,
    prepare_edge_index,
)
from siamese_compression_lab.subject_bootstrap import SubjectPairRow, edge_weights


def _rows() -> list[SubjectPairRow]:
    return [
        SubjectPairRow("g_a", 1, "A", "A", "matched", 0),
        SubjectPairRow("g_b", 1, "B", "B", "matched", 1),
        SubjectPairRow("g_c", 1, "C", "C", "matched", 2),
        SubjectPairRow("i_ab", 0, "A", "B", "mismatched", 0),
        SubjectPairRow("i_ac", 0, "A", "C", "mismatched", 1),
        SubjectPairRow("i_bc", 0, "B", "C", "mismatched", 2),
    ]


class VectorizedEdgeWeightTests(unittest.TestCase):
    def test_known_fixture_matches_legacy_exactly(self) -> None:
        rows = _rows()
        prepared = prepare_edge_index(rows)
        multiplicities = {"A": 2, "B": 1, "C": 0}
        np.testing.assert_array_equal(
            edge_weights_vectorized(prepared, multiplicities),
            edge_weights(rows, multiplicities),
        )

    def test_many_random_multiplicity_vectors_match_legacy_exactly(self) -> None:
        rows = _rows()
        prepared = prepare_edge_index(rows)
        rng = np.random.Generator(np.random.PCG64(20260808))
        for _ in range(1000):
            values = rng.multinomial(3, np.full(3, 1.0 / 3.0))
            multiplicities = {
                subject: int(value)
                for subject, value in zip(prepared.subjects, values)
            }
            expected = edge_weights(rows, multiplicities)
            actual_mapping = edge_weights_vectorized(prepared, multiplicities)
            actual_array = edge_weights_vectorized_from_array(prepared, values)
            np.testing.assert_array_equal(actual_mapping, expected)
            np.testing.assert_array_equal(actual_array, expected)

    def test_large_expected_multiplicities_match_legacy_exactly(self) -> None:
        rows = _rows()
        prepared = prepare_edge_index(rows)
        multiplicities = {"A": 963, "B": 962, "C": 961}
        expected = edge_weights(rows, multiplicities)
        actual = edge_weights_vectorized(prepared, multiplicities)
        np.testing.assert_array_equal(actual, expected)
        self.assertEqual(int(actual[0]), 963)
        self.assertEqual(int(actual[3]), 963 * 962)
        self.assertEqual(actual.dtype, np.int64)

    def test_prepared_index_preserves_observed_edge_count_and_order(self) -> None:
        rows = _rows()
        prepared = prepare_edge_index(rows)
        self.assertEqual(len(prepared.endpoint_1), len(rows))
        self.assertEqual(len(prepared.endpoint_2), len(rows))
        self.assertEqual(len(prepared.same), len(rows))
        self.assertEqual(tuple(prepared.subjects), ("A", "B", "C"))
        np.testing.assert_array_equal(
            prepared.same,
            np.asarray([row.same for row in rows], dtype=np.int8),
        )

    def test_negative_multiplicity_is_rejected_like_legacy(self) -> None:
        rows = _rows()
        prepared = prepare_edge_index(rows)
        with self.assertRaisesRegex(ValueError, "non-negative"):
            edge_weights_vectorized(prepared, {"A": -1, "B": 2, "C": 2})
        with self.assertRaisesRegex(ValueError, "non-negative"):
            edge_weights_vectorized_from_array(
                prepared, np.asarray([-1, 2, 2], dtype=np.int64)
            )

    def test_mapping_and_array_paths_are_identical(self) -> None:
        prepared = prepare_edge_index(_rows())
        mapping = {"A": 1, "B": 0, "C": 2}
        vector = multiplicity_vector(prepared, mapping)
        np.testing.assert_array_equal(
            edge_weights_vectorized(prepared, mapping),
            edge_weights_vectorized_from_array(prepared, vector),
        )


if __name__ == "__main__":
    unittest.main()
