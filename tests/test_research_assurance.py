from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from siamese_compression_lab.research_assurance import validate_research_program

ROOT = Path(__file__).resolve().parents[1]


class ResearchAssuranceTests(unittest.TestCase):
    def test_repository_research_contract_passes(self) -> None:
        report = validate_research_program(ROOT)
        self.assertEqual(report.status, "PASS", report.errors)

    def test_unexecuted_study_cannot_contain_results(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory)
            for relative in [
                "protocol/research_program.yaml",
                "protocol/studies/study_0_lfw.yaml",
                "protocol/studies/study_1_face_backbone.yaml",
                "claims/registry.yaml",
                "beliefs/prior_posterior.yaml",
                "configs/lfw_resnet18.yaml",
                "datasets/lfw_datasheet.yaml",
                "datasets/qualification_requirements.yaml",
                "gates/gate_spec.yaml",
                "gates/cal_spec.yaml",
                "paper/main.tex",
            ]:
                target = clone / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            for evidence in ["tests/test_core.py", "RESULTS_LFW_V0.1.md"]:
                target = clone / evidence
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / evidence).read_bytes())

            path = clone / "protocol/studies/study_1_face_backbone.yaml"
            study = yaml.safe_load(path.read_text(encoding="utf-8"))
            study["results"] = {"invented": 1.0}
            path.write_text(yaml.safe_dump(study), encoding="utf-8")
            report = validate_research_program(clone)
            self.assertEqual(report.status, "FAIL")
            self.assertTrue(any("unexecuted study has results" in error for error in report.errors))

    def test_cal_default_cannot_be_admissible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory)
            required = [
                "protocol/research_program.yaml",
                "protocol/studies/study_0_lfw.yaml",
                "protocol/studies/study_1_face_backbone.yaml",
                "claims/registry.yaml",
                "beliefs/prior_posterior.yaml",
                "configs/lfw_resnet18.yaml",
                "datasets/lfw_datasheet.yaml",
                "datasets/qualification_requirements.yaml",
                "gates/gate_spec.yaml",
                "gates/cal_spec.yaml",
                "paper/main.tex",
                "tests/test_core.py",
                "RESULTS_LFW_V0.1.md",
            ]
            for relative in required:
                target = clone / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            path = clone / "gates/cal_spec.yaml"
            cal = yaml.safe_load(path.read_text(encoding="utf-8"))
            cal["default_outcome"] = "ADMISSIBLE"
            path.write_text(yaml.safe_dump(cal), encoding="utf-8")
            report = validate_research_program(clone)
            self.assertEqual(report.status, "FAIL")
            self.assertIn("CAL default must be INDETERMINATE", report.errors)


if __name__ == "__main__":
    unittest.main()
