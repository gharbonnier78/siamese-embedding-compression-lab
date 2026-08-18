from __future__ import annotations

import runpy
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml"
RUNNER = runpy.run_path(str(ROOT / "scripts/run_subject_bootstrap_coverage.py"))
LOAD_CONTRACT = RUNNER["_load_contract"]


class CoverageContractAuthorizationTests(unittest.TestCase):
    def test_repository_contract_is_execution_authorized(self) -> None:
        loaded = LOAD_CONTRACT(CONTRACT)
        self.assertEqual(loaded["status"], "EXECUTION_AUTHORIZED")
        self.assertFalse(loaded["historical_study_0_scores_permitted"])

    def test_review_pending_fixture_still_blocks_production_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contract.yaml"
            contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
            contract["status"] = "IMPLEMENTATION_REVIEW_REQUIRED"
            path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "IMPLEMENTATION_REVIEW_REQUIRED"):
                LOAD_CONTRACT(path)

    def test_explicit_execution_authorization_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "contract.yaml"
            contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
            contract["status"] = "EXECUTION_AUTHORIZED"
            path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
            loaded = LOAD_CONTRACT(path)
            self.assertEqual(loaded["status"], "EXECUTION_AUTHORIZED")

    def test_non_outcome_smoke_can_validate_authorized_contract(self) -> None:
        loaded = LOAD_CONTRACT(CONTRACT, require_execution_authorized=False)
        self.assertEqual(loaded["status"], "EXECUTION_AUTHORIZED")
        self.assertFalse(loaded["historical_study_0_scores_permitted"])


if __name__ == "__main__":
    unittest.main()
