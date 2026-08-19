from __future__ import annotations

import runpy
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION = ROOT / "protocol/authorizations/study_0_historical_reanalysis_v0.2.2.yaml"
COVERAGE_CONTRACT = ROOT / "protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml"
STUDY1 = ROOT / "protocol/studies/study_1_face_backbone.yaml"
PREFLIGHT = runpy.run_path(str(ROOT / "scripts/preflight_study0_historical_reanalysis.py"))
VALIDATE = PREFLIGHT["validate_historical_reanalysis_authorization"]


class HistoricalReanalysisAuthorizationTests(unittest.TestCase):
    def test_repository_authorization_is_scoped_and_preflight_passes(self) -> None:
        authorization = VALIDATE(AUTHORIZATION)
        self.assertEqual(
            authorization["scope"]["execution_step"],
            "corrected_study_0_reanalysis",
        )
        self.assertTrue(authorization["historical_study_0_scores_permitted"])
        self.assertTrue(authorization["researcher_go"]["explicit"])
        self.assertTrue(authorization["researcher_go"]["scope_change_requires_new_go"])

    def test_frozen_coverage_contract_remains_historical_read_false(self) -> None:
        contract = yaml.safe_load(COVERAGE_CONTRACT.read_text(encoding="utf-8"))
        self.assertFalse(contract["historical_study_0_scores_permitted"])

    def test_authorization_does_not_start_study_1(self) -> None:
        study1 = yaml.safe_load(STUDY1.read_text(encoding="utf-8"))
        authorization = yaml.safe_load(AUTHORIZATION.read_text(encoding="utf-8"))
        self.assertEqual(study1["status"], "DRAFT_PREREGISTRATION")
        self.assertFalse(authorization["restrictions"]["study_1_execution_permitted"])
        self.assertFalse(authorization["restrictions"]["geometry_exploration_permitted"])

    def test_wrong_execution_scope_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authorization.yaml"
            authorization = yaml.safe_load(AUTHORIZATION.read_text(encoding="utf-8"))
            authorization["scope"]["execution_step"] = "study_1_execution"
            path.write_text(yaml.safe_dump(authorization, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "corrected_study_0_reanalysis only"):
                VALIDATE(path)

    def test_missing_researcher_go_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authorization.yaml"
            authorization = yaml.safe_load(AUTHORIZATION.read_text(encoding="utf-8"))
            authorization["researcher_go"]["explicit"] = False
            path.write_text(yaml.safe_dump(authorization, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "explicit researcher GO"):
                VALIDATE(path)

    def test_scope_change_without_new_go_rule_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authorization.yaml"
            authorization = yaml.safe_load(AUTHORIZATION.read_text(encoding="utf-8"))
            authorization["researcher_go"]["scope_change_requires_new_go"] = False
            path.write_text(yaml.safe_dump(authorization, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "scope changes must require a new GO"):
                VALIDATE(path)

    def test_method_broadening_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "authorization.yaml"
            authorization = yaml.safe_load(AUTHORIZATION.read_text(encoding="utf-8"))
            authorization["restrictions"]["retraining_permitted"] = True
            path.write_text(yaml.safe_dump(authorization, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "retraining_permitted=false"):
                VALIDATE(path)


if __name__ == "__main__":
    unittest.main()
