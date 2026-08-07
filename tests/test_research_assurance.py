from __future__ import annotations

import shutil
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
                "CHANGELOG.md",
                "ERRATA_STUDY_0.md",
                "docs/EXPERIMENT_HISTORY_AND_ERRATA.md",
                "protocol/experiment_ledger.yaml",
                "protocol/research_program.yaml",
                "protocol/studies/study_0_lfw.yaml",
                "protocol/studies/study_1_face_backbone.yaml",
                "protocol/studies/study_1_preregistration.md",
                "claims/registry.yaml",
                "beliefs/prior_posterior.yaml",
                "configs/lfw_resnet18.yaml",
                "datasets/lfw_datasheet.yaml",
                "datasets/qualification_requirements.yaml",
                "gates/gate_spec.yaml",
                "gates/cal_spec.yaml",
                "paper/main.tex",
                "output/pdf/siamese_embedding_compression_research_program_v0.2.pdf",
            ]:
                target = clone / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            for evidence in ["tests/test_core.py", "RESULTS_LFW_V0.1.md"]:
                target = clone / evidence
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / evidence).read_bytes())
            shutil.copytree(ROOT / "evidence", clone / "evidence")
            shutil.copytree(ROOT / "paper/figures-generated", clone / "paper/figures-generated")

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
                "CHANGELOG.md",
                "ERRATA_STUDY_0.md",
                "docs/EXPERIMENT_HISTORY_AND_ERRATA.md",
                "protocol/experiment_ledger.yaml",
                "protocol/research_program.yaml",
                "protocol/studies/study_0_lfw.yaml",
                "protocol/studies/study_1_face_backbone.yaml",
                "protocol/studies/study_1_preregistration.md",
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
                "output/pdf/siamese_embedding_compression_research_program_v0.2.pdf",
            ]
            for relative in required:
                target = clone / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            shutil.copytree(ROOT / "evidence", clone / "evidence")
            shutil.copytree(ROOT / "paper/figures-generated", clone / "paper/figures-generated")
            path = clone / "gates/cal_spec.yaml"
            cal = yaml.safe_load(path.read_text(encoding="utf-8"))
            cal["default_outcome"] = "ADMISSIBLE"
            path.write_text(yaml.safe_dump(cal), encoding="utf-8")
            report = validate_research_program(clone)
            self.assertEqual(report.status, "FAIL")
            self.assertIn("CAL default must be INDETERMINATE", report.errors)

    def test_archived_study_zero_paper_cannot_be_rewritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory)
            shutil.copytree(ROOT, clone, dirs_exist_ok=True)
            archived = clone / "output/pdf/siamese_embedding_compression_research_program_v0.2.pdf"
            archived.write_bytes(archived.read_bytes() + b"history rewrite")
            report = validate_research_program(clone)
            self.assertEqual(report.status, "FAIL")
            self.assertIn("archived v0.2 paper is missing or changed", report.errors)


if __name__ == "__main__":
    unittest.main()
