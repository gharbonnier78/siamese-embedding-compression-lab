from __future__ import annotations

import unittest

from siamese_compression_lab.coverage_simulation import (
    CoverageScenario,
    make_sparse_graph,
    scenario_truth,
    simulate_distances,
)
from siamese_compression_lab.subject_bootstrap import subject_bootstrap_delta_fnmr
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


if __name__ == "__main__":
    unittest.main()
