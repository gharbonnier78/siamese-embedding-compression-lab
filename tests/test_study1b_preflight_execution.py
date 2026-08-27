from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from siamese_compression_lab.study1b_execution import (
    PCA128,
    Random128,
    assert_outcome_authorized,
    seed_token,
)
from siamese_compression_lab.study1b_preflight import Capture, assign_roles, make_pair_graph
from siamese_compression_lab.study1b_statistics import subject_bootstrap_summary
from siamese_compression_lab.subject_bootstrap import SubjectPairRow


class Study1BPreflightTests(unittest.TestCase):
    def test_role_assignment_is_deterministic_and_exact(self) -> None:
        dev_train = [f"train_{index:04d}" for index in range(4038)]
        dev_test = [f"test_{index:04d}" for index in range(1711)]
        first = assign_roles(dev_train, dev_test)
        second = assign_roles(reversed(dev_train), reversed(dev_test))
        self.assertEqual(first, second)
        self.assertEqual(sum(value == "TRAIN" for value in first.values()), 2827)
        self.assertEqual(sum(value == "VALIDATION" for value in first.values()), 606)
        self.assertEqual(sum(value == "SCREEN" for value in first.values()), 605)
        self.assertEqual(sum(value == "TEST" for value in first.values()), 1711)

    def test_pair_graph_is_replayable_and_unique(self) -> None:
        captures = []
        for subject in range(6):
            for capture in range(3):
                captures.append(
                    Capture(
                        subject_id=f"s{subject}",
                        capture_id=f"s{subject}_c{capture}",
                        role="TRAIN",
                        relative_path="fixture.jpg",
                        sha256=f"{subject:02x}{capture:02x}".ljust(64, "0"),
                        dhash64=subject * 17 + capture,
                    )
                )
        a = make_pair_graph("TRAIN", captures, 8, 20)
        b = make_pair_graph("TRAIN", captures, 8, 20)
        self.assertEqual(a, b)
        keys = {(row.capture_id_1, row.capture_id_2, row.same) for row in a}
        self.assertEqual(len(keys), 28)
        self.assertEqual(sum(row.same == 1 for row in a), 8)
        self.assertEqual(sum(row.same == 0 for row in a), 20)


class Study1BExecutionTests(unittest.TestCase):
    def test_outcome_execution_fails_closed_without_go(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(PermissionError):
                assert_outcome_authorized(Path(directory) / "missing.yaml")

    def test_task_seed_token_is_stable_and_task_bound(self) -> None:
        self.assertEqual(seed_token("random128|seed=11"), seed_token("random128|seed=11"))
        self.assertNotEqual(seed_token("random128|seed=11"), seed_token("pca128|seed=11"))
        self.assertNotEqual(seed_token("random128|seed=11"), seed_token("random128|seed=29"))

    def test_random_projection_is_deterministic(self) -> None:
        first = Random128.fit(11)
        second = Random128.fit(11)
        np.testing.assert_array_equal(first.matrix, second.matrix)
        self.assertAlmostEqual(float(np.var(first.matrix)), 1.0 / 128.0, delta=8e-4)

    def test_pca_fits_unique_capture_matrix_not_pair_endpoints(self) -> None:
        rng = np.random.default_rng(4)
        train = rng.normal(size=(180, 512)).astype(np.float32)
        first = PCA128.fit(train, 11)
        second = PCA128.fit(train, 11)
        np.testing.assert_allclose(first.pca.components_, second.pca.components_, atol=0, rtol=0)
        self.assertEqual(first.pca.n_components_, 128)
        self.assertFalse(first.pca.whiten)


class Study1BStatisticsTests(unittest.TestCase):
    def test_subject_bootstrap_uses_paired_identity_draws(self) -> None:
        rows = [
            SubjectPairRow("g_a", 1, "A", "A", "fixture", 0),
            SubjectPairRow("g_b", 1, "B", "B", "fixture", 1),
            SubjectPairRow("g_c", 1, "C", "C", "fixture", 2),
            SubjectPairRow("i_ab", 0, "A", "B", "fixture", 3),
            SubjectPairRow("i_ac", 0, "A", "C", "fixture", 4),
            SubjectPairRow("i_bc", 0, "B", "C", "fixture", 5),
        ]
        reference = np.asarray([0.4, 0.5, 0.6, 0.8, 0.9, 1.0])
        candidate = reference.copy()
        result = subject_bootstrap_summary(
            rows=rows,
            candidate_distances=candidate,
            reference_distances=reference,
            target_fmr=0.34,
            replicates=50,
            seed=91,
            degeneracy_limit_fraction=1.0,
        )
        self.assertEqual(result.valid_replicates + result.degenerate_replicates, 50)
        self.assertAlmostEqual(result.delta_fnmr_mean, 0.0)


if __name__ == "__main__":
    unittest.main()
