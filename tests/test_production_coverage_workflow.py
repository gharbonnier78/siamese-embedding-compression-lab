from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/production-subject-bootstrap-coverage.yml"


class ProductionCoverageWorkflowTests(unittest.TestCase):
    def test_production_workflow_is_manual_and_explicitly_confirmed(self) -> None:
        workflow = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        self.assertEqual(set(workflow["on"]), {"workflow_dispatch"})
        confirmation = workflow["on"]["workflow_dispatch"]["inputs"]["confirm_execution"]
        self.assertEqual(confirmation["required"], "true")
        self.assertEqual(confirmation["type"], "boolean")
        self.assertEqual(workflow["jobs"]["coverage"]["if"], "${{ inputs.confirm_execution }}")

    def test_evidence_is_uploaded_before_failure_is_propagated(self) -> None:
        workflow = yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        steps = workflow["jobs"]["coverage"]["steps"]
        names = [step.get("name") for step in steps]
        self.assertLess(
            names.index("Upload production coverage evidence"),
            names.index("Propagate scientific gate failure after evidence upload"),
        )


if __name__ == "__main__":
    unittest.main()
