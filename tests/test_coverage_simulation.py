from __future__ import annotations

import unittest

from siamese_compression_lab.coverage_simulation import (
    CoverageScenario,
    coverage_gate_passes,
    make_sparse_graph,
    run_coverage_scenario,
    scenario_truth,
)


class CoverageSimulationTests(unittest.TestCase):
    def test_truth_matches_requested_delta(self) -> None:
        scenario = CoverageScenario(
            name="fixture",
            target_delta_fnmr=0.03,
            n_subjects=30,
            n_genuine=20,
            n_impostor=20,
            target_fmr=0.10,
            subject_effect_sd_genuine=0.04,
            subject_effect_sd_impostor=0.03,
        )
        truth = scenario_truth(scenario)
        self.assertAlmostEqual(truth.delta_fnmr, 0.03, places=10)
        self.assertAlmostEqual(truth.operational_candidate_fmr, 0.10)

    def test_sparse_graph_preserves_edge_budget_and_subject_universe(self) -> None:
        scenario = CoverageScenario(
            name="graph_fixture",
            target_delta_fnmr=0.0,
            n_subjects=30,
            n_genuine=20,
            n_impostor=20,
            target_fmr=0.10,
        )
        rows = make_sparse_graph(scenario, seed=7)
        self.assertEqual(len(rows), 40)
        subjects = {
            subject
            for row in rows
            for subject in (row.subject_slot_id_1, row.subject_slot_id_2)
        }
        self.assertEqual(len(subjects), 30)
        self.assertTrue(all(row.subject_slot_id_1 != row.subject_slot_id_2 for row in rows if row.same == 0))

    def test_smoke_run_reports_three_separate_metrics(self) -> None:
        scenario = CoverageScenario(
            name="smoke",
            target_delta_fnmr=0.0,
            n_subjects=30,
            n_genuine=20,
            n_impostor=20,
            target_fmr=0.10,
            subject_effect_sd_genuine=0.02,
            subject_effect_sd_impostor=0.02,
        )
        results = run_coverage_scenario(
            scenario,
            simulated_datasets=2,
            bootstrap_replicates=10,
            root_seed=91,
        )
        self.assertEqual(
            {result.metric for result in results},
            {"representation_delta_fnmr", "operational_fnmr", "operational_fmr"},
        )
        self.assertTrue(all(result.simulated_datasets == 2 for result in results))
        self.assertFalse(coverage_gate_passes(results))


if __name__ == "__main__":
    unittest.main()
