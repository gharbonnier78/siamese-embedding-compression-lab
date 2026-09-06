from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np
from scipy.stats import t

from siamese_compression_lab.study1b_s4n2_dagjk import (
    GROUP_COUNT,
    ONE_SIDED_LEVEL,
    _delta_for_keep,
    _threshold_unweighted,
    dagjk20_summary,
    identity_group_assignment,
)
from siamese_compression_lab.subject_bootstrap import SubjectPairRow


def _toy_rows(n_subjects: int = 40) -> list[SubjectPairRow]:
    subjects = [f"s{index:03d}" for index in range(n_subjects)]
    rows: list[SubjectPairRow] = []
    for index, subject in enumerate(subjects):
        rows.append(SubjectPairRow(f"g{index}", 1, subject, subject, "toy", index))
    source = n_subjects
    for index, subject in enumerate(subjects):
        other = subjects[(index + 1) % n_subjects]
        rows.append(SubjectPairRow(f"i{index}", 0, subject, other, "toy", source + index))
    return rows


class Study1BS4N2DagjkTest(unittest.TestCase):
    def test_group_assignment_is_deterministic_balanced_and_complete(self) -> None:
        rows = _toy_rows(41)
        first = identity_group_assignment(rows)
        second = identity_group_assignment(list(reversed(rows)))
        self.assertEqual(first, second)
        self.assertEqual(len(first), 41)
        sizes = np.bincount(list(first.values()), minlength=GROUP_COUNT)
        self.assertLessEqual(int(sizes.max() - sizes.min()), 1)
        self.assertEqual(set(first.values()), set(range(GROUP_COUNT)))

    def test_whole_tie_block_threshold_falls_back_before_crossing_tie(self) -> None:
        same = np.asarray([0] * 100 + [1] * 10, dtype=np.int8)
        distances = np.concatenate(
            [np.asarray([0.1, 0.1] + [0.2 + index / 1000 for index in range(98)]), np.ones(10)]
        )
        keep = np.ones(len(same), dtype=bool)
        threshold = _threshold_unweighted(same, distances, keep, 0.01)
        self.assertLess(threshold, 0.1)

    def test_delete_mask_removes_edges_touching_either_endpoint(self) -> None:
        rows = [
            SubjectPairRow("g0", 1, "a", "a", "toy", 0),
            SubjectPairRow("g1", 1, "b", "b", "toy", 1),
            SubjectPairRow("i0", 0, "a", "b", "toy", 2),
            SubjectPairRow("i1", 0, "b", "c", "toy", 3),
            SubjectPairRow("i2", 0, "c", "d", "toy", 4),
        ]
        candidate = np.asarray([0.1, 0.2, 0.8, 0.9, 1.0])
        reference = np.asarray([0.1, 0.2, 0.7, 0.8, 0.9])
        keep = np.asarray([False, True, False, True, True])
        delta, n_genuine, n_impostor = _delta_for_keep(rows, candidate, reference, keep)
        self.assertTrue(np.isfinite(delta))
        self.assertEqual(n_genuine, 1)
        self.assertEqual(n_impostor, 2)

    def test_jackknife_variance_and_t19_bound_are_frozen(self) -> None:
        rows = _toy_rows(40)
        candidate = np.linspace(0.1, 1.0, len(rows))
        reference = candidate + 0.01
        replicate_values = np.linspace(-0.01, 0.01, GROUP_COUNT)
        side_effect = [(float(value), 30, 30) for value in replicate_values]
        point = 0.005
        with patch(
            "siamese_compression_lab.study1b_s4n2_dagjk._delta_for_keep",
            side_effect=side_effect,
        ):
            summary = dagjk20_summary(rows, candidate, reference, point_delta=point)
        expected_variance = (GROUP_COUNT - 1) / GROUP_COUNT * float(
            np.sum((replicate_values - np.mean(replicate_values)) ** 2)
        )
        self.assertAlmostEqual(summary.jackknife_variance, expected_variance)
        expected_critical = float(t.ppf(ONE_SIDED_LEVEL, df=19))
        self.assertAlmostEqual(summary.critical_value, expected_critical)
        self.assertAlmostEqual(
            summary.ucb_97_5,
            point + expected_critical * np.sqrt(expected_variance),
        )

    def test_degenerate_delete_group_fails_closed(self) -> None:
        rows = _toy_rows(40)
        candidate = np.linspace(0.1, 1.0, len(rows))
        reference = candidate + 0.01
        with patch(
            "siamese_compression_lab.study1b_s4n2_dagjk._delta_for_keep",
            side_effect=ValueError("degenerate delete-group replicate"),
        ):
            with self.assertRaisesRegex(ValueError, "degenerate delete-group replicate"):
                dagjk20_summary(rows, candidate, reference, point_delta=0.0)


if __name__ == "__main__":
    unittest.main()
