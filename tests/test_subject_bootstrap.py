from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from siamese_compression_lab.subject_bootstrap import (
    SubjectPairRow,
    draw_subject_multiplicities,
    edge_weights,
    percentile_summary,
    reconstruct_lfw_devtest_subject_map,
    subject_bootstrap_delta_fnmr,
    validate_subject_map,
    weighted_rates_at_threshold,
    weighted_threshold_at_fmr,
)


def _fixture_rows() -> list[SubjectPairRow]:
    return [
        SubjectPairRow("g_a", 1, "A", "A", "matched", 0),
        SubjectPairRow("g_b", 1, "B", "B", "matched", 1),
        SubjectPairRow("i_ab", 0, "A", "B", "mismatched", 0),
        SubjectPairRow("i_ac", 0, "A", "C", "mismatched", 1),
    ]


class SubjectBootstrapTests(unittest.TestCase):
    def test_genuine_and_impostor_multiplicity_rules(self) -> None:
        rows = _fixture_rows()
        weights = edge_weights(rows, {"A": 2, "B": 1, "C": 0})
        np.testing.assert_array_equal(weights, np.asarray([2, 1, 2, 0]))

    def test_repeated_subject_slots_are_not_deduplicated(self) -> None:
        rows = _fixture_rows()
        once = edge_weights(rows, {"A": 1, "B": 1, "C": 0})
        twice = edge_weights(rows, {"A": 2, "B": 1, "C": 0})
        self.assertEqual(int(once[0]), 1)
        self.assertEqual(int(twice[0]), 2)
        self.assertEqual(int(once[2]), 1)
        self.assertEqual(int(twice[2]), 2)

    def test_no_unobserved_edge_is_synthesized(self) -> None:
        rows = _fixture_rows()
        weights = edge_weights(rows, {"A": 2, "B": 1, "C": 3})
        self.assertEqual(len(weights), len(rows))
        self.assertNotIn("i_bc", {row.pair_id for row in rows})

    def test_same_subject_never_becomes_impostor(self) -> None:
        with self.assertRaisesRegex(ValueError, "identical endpoint subjects"):
            validate_subject_map(
                [SubjectPairRow("bad", 0, "A", "A", "mismatched", 0)]
            )

    def test_weighted_and_materialized_rates_are_equivalent(self) -> None:
        rows = _fixture_rows()
        same = np.asarray([row.same for row in rows], dtype=np.int8)
        distances = np.asarray([0.8, 0.4, 0.1, 0.7])
        weights = edge_weights(rows, {"A": 2, "B": 1, "C": 0})
        weighted = weighted_rates_at_threshold(same, distances, weights, 0.5)

        materialized_same = np.repeat(same, weights)
        materialized_distances = np.repeat(distances, weights)
        expected_fnmr = float(np.mean(materialized_distances[materialized_same == 1] > 0.5))
        expected_fmr = float(np.mean(materialized_distances[materialized_same == 0] <= 0.5))
        self.assertAlmostEqual(weighted.fnmr, expected_fnmr)
        self.assertAlmostEqual(weighted.fmr, expected_fmr)

    def test_whole_tie_block_is_never_split(self) -> None:
        same = np.asarray([0, 0, 0, 1], dtype=np.int8)
        distances = np.asarray([0.10, 0.10, 0.20, 0.30], dtype=np.float64)
        weights = np.asarray([1, 1, 8, 1], dtype=np.int64)
        threshold = weighted_threshold_at_fmr(same, distances, weights, 0.25)
        self.assertEqual(threshold, 0.10)
        result = weighted_rates_at_threshold(same, distances, weights, threshold)
        self.assertAlmostEqual(result.fmr, 0.2)

    def test_no_admissible_observed_threshold_uses_sentinel(self) -> None:
        same = np.asarray([0, 0, 1], dtype=np.int8)
        distances = np.asarray([0.10, 0.20, 0.30], dtype=np.float64)
        weights = np.asarray([1, 9, 1], dtype=np.int64)
        threshold = weighted_threshold_at_fmr(same, distances, weights, 0.05)
        self.assertLess(threshold, 0.10)
        result = weighted_rates_at_threshold(same, distances, weights, threshold)
        self.assertEqual(result.fmr, 0.0)

    def test_fixed_rng_draw_is_deterministic(self) -> None:
        subjects = ["A", "B", "C"]
        first = draw_subject_multiplicities(subjects, np.random.Generator(np.random.PCG64(7)))
        second = draw_subject_multiplicities(subjects, np.random.Generator(np.random.PCG64(7)))
        self.assertEqual(first, second)
        self.assertEqual(sum(first.values()), 3)

    def test_paired_routes_replay_identically_from_root_seed(self) -> None:
        rows = _fixture_rows()
        candidate = np.asarray([0.7, 0.5, 0.2, 0.9])
        reference = np.asarray([0.6, 0.4, 0.3, 0.8])
        first = subject_bootstrap_delta_fnmr(
            rows=rows,
            candidate_distances=candidate,
            reference_distances=reference,
            target_fmr=0.25,
            replicates=1,
            seed=123,
        )
        second = subject_bootstrap_delta_fnmr(
            rows=rows,
            candidate_distances=candidate,
            reference_distances=reference,
            target_fmr=0.25,
            replicates=1,
            seed=123,
        )
        self.assertEqual(first, second)
        self.assertEqual(percentile_summary(first), percentile_summary(second))
        self.assertGreater(first[0].genuine_weight, 0)
        self.assertGreater(first[0].impostor_weight, 0)

    def test_mapping_reconstruction_preserves_source_edges(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            matched = root / "matchpairsDevTest.csv"
            mismatched = root / "mismatchpairsDevTest.csv"
            matched.write_text("name,imagenum1,imagenum2\nAlice,1,2\nBob,1,2\n", encoding="utf-8")
            mismatched.write_text(
                "name1,imagenum1,name2,imagenum2\nAlice,1,Carol,1\nBob,1,Carol,2\n",
                encoding="utf-8",
            )
            rows = reconstruct_lfw_devtest_subject_map(matched, mismatched)
            counts = validate_subject_map(
                rows,
                expected_pairs=4,
                expected_genuine=2,
                expected_impostor=2,
                expected_subjects=3,
            )
            self.assertEqual(counts["subjects"], 3)
            self.assertEqual(
                [row.pair_id for row in rows],
                [
                    "test_genuine_00000",
                    "test_genuine_00001",
                    "test_impostor_00000",
                    "test_impostor_00001",
                ],
            )
            self.assertNotEqual(rows[0].subject_slot_id_1, "Alice")


if __name__ == "__main__":
    unittest.main()
