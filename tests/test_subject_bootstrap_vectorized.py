from __future__ import annotations

import unittest
from unittest.mock import patch

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
    subject_bootstrap_delta_fnmr,
)
from siamese_compression_lab.subject_bootstrap_operational import (
    subject_bootstrap_fixed_threshold,
)
from siamese_compression_lab.subject_bootstrap_vectorized import (
    subject_bootstrap_delta_fnmr_vectorized,
    subject_bootstrap_fixed_threshold_vectorized,
)


class VectorizedFullBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = CoverageScenario(
            name="vectorized_full_fixture",
            target_delta_fnmr=0.015,
            n_subjects=30,
            n_genuine=20,
            n_impostor=20,
            target_fmr=0.10,
            subject_effect_sd_genuine=0.04,
            subject_effect_sd_impostor=0.03,
        )
        self.rows = make_sparse_graph(self.scenario, seed=17)
        self.candidate, self.reference = simulate_distances(
            self.scenario, self.rows, seed=23
        )

    def test_representation_replicates_match_legacy_exactly(self) -> None:
        expected = subject_bootstrap_delta_fnmr(
            rows=self.rows,
            candidate_distances=self.candidate,
            reference_distances=self.reference,
            target_fmr=self.scenario.target_fmr,
            replicates=100,
            seed=29,
        )
        actual = subject_bootstrap_delta_fnmr_vectorized(
            rows=self.rows,
            candidate_distances=self.candidate,
            reference_distances=self.reference,
            target_fmr=self.scenario.target_fmr,
            replicates=100,
            seed=29,
        )
        self.assertEqual(actual, expected)

    def test_operational_replicates_match_legacy_exactly(self) -> None:
        threshold = scenario_truth(self.scenario).candidate_threshold
        expected = subject_bootstrap_fixed_threshold(
            rows=self.rows,
            distances=self.candidate,
            validation_threshold=threshold,
            replicates=100,
            seed=31,
        )
        actual = subject_bootstrap_fixed_threshold_vectorized(
            rows=self.rows,
            distances=self.candidate,
            validation_threshold=threshold,
            replicates=100,
            seed=31,
        )
        self.assertEqual(actual, expected)

    def test_vectorized_operational_threshold_remains_frozen(self) -> None:
        threshold = scenario_truth(self.scenario).candidate_threshold
        actual = subject_bootstrap_fixed_threshold_vectorized(
            rows=self.rows,
            distances=self.candidate,
            validation_threshold=threshold,
            replicates=100,
            seed=31,
        )
        self.assertTrue(actual)
        self.assertTrue(all(row.threshold == threshold for row in actual))

    def test_study0_like_geometry_matches_for_fixed_seed(self) -> None:
        scenario = CoverageScenario(
            name="study0_like_vectorized_fixture",
            target_delta_fnmr=0.015,
            subject_effect_sd_genuine=0.08,
            subject_effect_sd_impostor=0.05,
        )
        rows = make_sparse_graph(scenario, seed=20260808)
        candidate, reference = simulate_distances(scenario, rows, seed=20260809)
        expected = subject_bootstrap_delta_fnmr(
            rows=rows,
            candidate_distances=candidate,
            reference_distances=reference,
            target_fmr=scenario.target_fmr,
            replicates=25,
            seed=20260810,
        )
        actual = subject_bootstrap_delta_fnmr_vectorized(
            rows=rows,
            candidate_distances=candidate,
            reference_distances=reference,
            target_fmr=scenario.target_fmr,
            replicates=25,
            seed=20260810,
        )
        self.assertEqual(actual, expected)

    def test_study0_like_operational_matches_for_fixed_seed(self) -> None:
        scenario = CoverageScenario(
            name="study0_like_vectorized_operational_fixture",
            target_delta_fnmr=0.015,
            subject_effect_sd_genuine=0.08,
            subject_effect_sd_impostor=0.05,
        )
        rows = make_sparse_graph(scenario, seed=20260808)
        candidate, _reference = simulate_distances(scenario, rows, seed=20260809)
        threshold = scenario_truth(scenario).candidate_threshold
        expected = subject_bootstrap_fixed_threshold(
            rows=rows,
            distances=candidate,
            validation_threshold=threshold,
            replicates=25,
            seed=20260810,
        )
        actual = subject_bootstrap_fixed_threshold_vectorized(
            rows=rows,
            distances=candidate,
            validation_threshold=threshold,
            replicates=25,
            seed=20260810,
        )
        self.assertEqual(actual, expected)

    def test_representation_degenerate_replicate_preserves_audit_and_prior_results(
        self,
    ) -> None:
        rows = [
            SubjectPairRow("g_a", 1, "A", "A", "matched", 0),
            SubjectPairRow("g_b", 1, "B", "B", "matched", 1),
            SubjectPairRow("i_ab", 0, "A", "B", "mismatched", 0),
            SubjectPairRow("i_ac", 0, "A", "C", "mismatched", 1),
        ]
        candidate = np.asarray([0.7, 0.5, 0.2, 0.9])
        reference = np.asarray([0.6, 0.4, 0.3, 0.8])
        draws = [
            np.asarray([1, 1, 1], dtype=np.int64),
            np.asarray([0, 0, 3], dtype=np.int64),
        ]
        with patch(
            "siamese_compression_lab.subject_bootstrap_vectorized._draw_multiplicity_vector",
            side_effect=draws,
        ), self.assertRaises(DegenerateReplicateError) as caught:
            subject_bootstrap_delta_fnmr_vectorized(
                rows=rows,
                candidate_distances=candidate,
                reference_distances=reference,
                target_fmr=0.25,
                replicates=2,
                seed=123,
            )
        error = caught.exception
        self.assertEqual(error.audit.replicate, 1)
        self.assertEqual(error.audit.completed_replicates, 1)
        self.assertEqual(len(error.completed_replicates), 1)
        self.assertEqual(error.audit.genuine_weight, 0)
        self.assertEqual(error.audit.impostor_weight, 0)
        self.assertEqual(error.audit.effective_genuine_edges, 0)
        self.assertEqual(error.audit.effective_impostor_edges, 0)
        self.assertIn("positive-weight impostor", error.audit.reason)

    def test_operational_degenerate_replicate_preserves_audit_and_prior_results(
        self,
    ) -> None:
        rows = [
            SubjectPairRow("g_a", 1, "A", "A", "matched", 0),
            SubjectPairRow("g_b", 1, "B", "B", "matched", 1),
            SubjectPairRow("i_ab", 0, "A", "B", "mismatched", 0),
            SubjectPairRow("i_ac", 0, "A", "C", "mismatched", 1),
        ]
        distances = np.asarray([0.7, 0.5, 0.2, 0.9])
        draws = [
            np.asarray([1, 1, 1], dtype=np.int64),
            np.asarray([0, 0, 3], dtype=np.int64),
        ]
        with patch(
            "siamese_compression_lab.subject_bootstrap_vectorized._draw_multiplicity_vector",
            side_effect=draws,
        ), self.assertRaises(DegenerateReplicateError) as caught:
            subject_bootstrap_fixed_threshold_vectorized(
                rows=rows,
                distances=distances,
                validation_threshold=0.5,
                replicates=2,
                seed=123,
            )
        error = caught.exception
        self.assertEqual(error.audit.replicate, 1)
        self.assertEqual(error.audit.completed_replicates, 1)
        self.assertEqual(len(error.completed_replicates), 1)
        self.assertEqual(error.audit.genuine_weight, 0)
        self.assertEqual(error.audit.impostor_weight, 0)
        self.assertEqual(error.audit.effective_genuine_edges, 0)
        self.assertEqual(error.audit.effective_impostor_edges, 0)


if __name__ == "__main__":
    unittest.main()
