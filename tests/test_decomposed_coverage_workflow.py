from __future__ import annotations

import unittest
from pathlib import Path


class DecomposedCoverageWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = Path(
            ".github/workflows/production-subject-bootstrap-coverage-decomposed-candidate.yml"
        ).read_text(encoding="utf-8")
        self.preflight = Path("scripts/preflight_decomposed_coverage.py").read_text(
            encoding="utf-8"
        )
        self.aggregator = Path("scripts/aggregate_subject_bootstrap_coverage.py").read_text(
            encoding="utf-8"
        )

    def test_candidate_is_manual_confirmed_and_currently_gate_blocked(self) -> None:
        self.assertIn("workflow_dispatch:", self.workflow)
        self.assertNotIn("pull_request:", self.workflow)
        self.assertNotIn("push:", self.workflow)
        self.assertIn("confirm_production_coverage", self.workflow)
        self.assertIn("scripts/preflight_decomposed_coverage.py", self.workflow)
        self.assertIn("DECOMPOSED_PRODUCTION_GATE", self.preflight)
        self.assertIn("require_execution_authorized=True", self.preflight)

    def test_checkpoints_are_staged_not_statically_parallel(self) -> None:
        self.assertIn("coverage_4000:", self.workflow)
        self.assertIn("needs: aggregate_2000", self.workflow)
        self.assertIn("if: needs.aggregate_2000.outputs.stop != 'true'", self.workflow)
        self.assertIn("coverage_10000:", self.workflow)
        self.assertIn("needs: aggregate_4000", self.workflow)
        self.assertIn("if: needs.aggregate_4000.outputs.stop != 'true'", self.workflow)
        self.assertEqual(self.workflow.count("--checkpoint 2000"), 3)
        self.assertEqual(self.workflow.count("--checkpoint 4000"), 3)
        self.assertEqual(self.workflow.count("--checkpoint 10000"), 3)

    def test_scenario_jobs_have_margin_below_six_hour_hosted_limit(self) -> None:
        self.assertEqual(self.workflow.count("timeout-minutes: 330"), 3)
        self.assertNotIn("timeout-minutes: 720", self.workflow)
        self.assertEqual(self.workflow.count("--workers 4"), 3)

    def test_all_five_frozen_scenarios_exist_in_every_checkpoint_matrix(self) -> None:
        for scenario in (
            "independent_pair_null",
            "subject_dependence_null",
            "subject_dependence_noninferior",
            "subject_dependence_boundary",
            "subject_dependence_inferior",
        ):
            self.assertEqual(self.workflow.count(f"- {scenario}"), 3)

    def test_intermediate_production_aggregation_is_precision_only(self) -> None:
        self.assertIn("Full coverage values are materialized only once", self.aggregator)
        self.assertIn("coverage_simulation.synthetic_smoke.csv", self.aggregator)
        self.assertNotIn('coverage_simulation.csv", rows', self.aggregator)
        self.assertIn("all_metric_mcse_lte_threshold", self.workflow)
        self.assertNotIn("lower_bound", self.workflow)

    def test_final_evidence_upload_precedes_failure_propagation(self) -> None:
        for checkpoint in (2000, 4000, 10000):
            finalize_index = self.workflow.index(f"finalize_{checkpoint}:")
            section_end = self.workflow.find("\n  coverage_", finalize_index + 1)
            if section_end == -1:
                section_end = len(self.workflow)
            section = self.workflow[finalize_index:section_end]
            upload_index = section.index("Upload final evidence before propagating the gate")
            propagate_index = section.index("Propagate scientific gate result")
            self.assertLess(upload_index, propagate_index)
            self.assertIn("if: always()", section)


if __name__ == "__main__":
    unittest.main()
