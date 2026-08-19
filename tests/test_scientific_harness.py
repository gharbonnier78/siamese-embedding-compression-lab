from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from siamese_compression_lab.scientific_harness import (
    ScientificChronicleError,
    assert_execution_unblocked,
    validate_scientific_chronicle,
)

ROOT = Path(__file__).resolve().parents[1]
CHRONICLE = ROOT / "protocol/scientific_chronicle.yaml"
GATE = ROOT / "gates/scientific_harness.yaml"
COVERAGE_CONTRACT = ROOT / "protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml"


class ScientificHarnessTests(unittest.TestCase):
    def test_repository_chronicle_contract_is_valid(self) -> None:
        self.assertEqual(validate_scientific_chronicle(CHRONICLE, GATE), [])

    def test_open_cost_risk_blocks_without_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chronicle.yaml"
            doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
            doc["entries"] = [doc["entries"][0]]
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            with self.assertRaisesRegex(
                ScientificChronicleError,
                "CHRON-20260808-001",
            ):
                assert_execution_unblocked(path, GATE, "production_coverage_gate")

    def test_open_entry_requires_next_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chronicle.yaml"
            doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
            doc["entries"][0]["next_action"] = None
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            errors = validate_scientific_chronicle(path, GATE)
            self.assertTrue(any("requires next_action" in error for error in errors))

    def test_monolithic_production_remains_blocked_by_explicit_scope_guard(self) -> None:
        with self.assertRaisesRegex(
            ScientificChronicleError,
            "CHRON-20260818-006",
        ):
            assert_execution_unblocked(CHRONICLE, GATE, "production_coverage_gate")

    def test_decomposed_production_is_unblocked_after_reviewed_equivalence_resolution(self) -> None:
        assert_execution_unblocked(
            CHRONICLE,
            GATE,
            "decomposed_production_coverage_gate",
        )

    def test_decomposed_resolution_supersedes_the_open_architecture_blocker(self) -> None:
        doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
        resolution = next(
            entry
            for entry in doc["entries"]
            if entry["id"] == "CHRON-20260818-005"
        )
        self.assertEqual(resolution["status"], "RESOLVED")
        self.assertEqual(resolution["supersedes"], "CHRON-20260809-004")
        self.assertFalse(resolution["outcome_evidence_seen"])
        self.assertEqual(resolution["blocks"], [])

    def test_monolithic_scope_guard_is_open_and_only_blocks_legacy_gate(self) -> None:
        doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
        guard = next(
            entry
            for entry in doc["entries"]
            if entry["id"] == "CHRON-20260818-006"
        )
        self.assertEqual(guard["status"], "OPEN")
        self.assertFalse(guard["outcome_evidence_seen"])
        self.assertEqual(guard["blocks"], ["production_coverage_gate"])
        self.assertTrue(guard["next_action"])

    def test_reviewed_coverage_resolution_supersedes_pending_reanalysis_blocker(self) -> None:
        doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
        pending = next(
            entry
            for entry in doc["entries"]
            if entry["id"] == "CHRON-20260818-007"
        )
        resolution = next(
            entry
            for entry in doc["entries"]
            if entry["id"] == "CHRON-20260819-008"
        )
        self.assertEqual(pending["status"], "OPEN")
        self.assertEqual(pending["blocks"], ["corrected_study_0_reanalysis"])
        self.assertEqual(resolution["status"], "RESOLVED")
        self.assertEqual(resolution["supersedes"], "CHRON-20260818-007")
        self.assertTrue(resolution["outcome_evidence_seen"])
        self.assertEqual(resolution["blocks"], [])

    def test_corrected_reanalysis_is_unblocked_after_independent_coverage_approval(self) -> None:
        assert_execution_unblocked(
            CHRONICLE,
            GATE,
            "corrected_study_0_reanalysis",
        )

    def test_coverage_resolution_does_not_authorize_historical_score_access(self) -> None:
        contract = yaml.safe_load(COVERAGE_CONTRACT.read_text(encoding="utf-8"))
        self.assertFalse(contract["historical_study_0_scores_permitted"])

    def test_unknown_execution_step_cannot_bypass_the_gate_contract(self) -> None:
        with self.assertRaisesRegex(ScientificChronicleError, "unknown execution step"):
            assert_execution_unblocked(CHRONICLE, GATE, "misspelled_production_gate")

    def test_chronicle_cannot_block_an_undeclared_execution_step(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chronicle.yaml"
            doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
            doc["entries"][-1]["blocks"] = ["misspelled_production_gate"]
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            errors = validate_scientific_chronicle(path, GATE)
            self.assertTrue(any("blocks undeclared execution step" in error for error in errors))

    def test_nonterminal_supersession_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chronicle.yaml"
            doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
            resolution = next(
                entry
                for entry in doc["entries"]
                if entry["id"] == "CHRON-20260808-003"
            )
            resolution["status"] = "OPEN"
            resolution["next_action"] = "still investigating"
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            errors = validate_scientific_chronicle(path, GATE)
            self.assertTrue(
                any("only terminal chronicle entries may supersede" in error for error in errors)
            )

    def test_supersession_must_reference_earlier_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chronicle.yaml"
            doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
            resolution = next(
                entry
                for entry in doc["entries"]
                if entry["id"] == "CHRON-20260808-003"
            )
            resolution["supersedes"] = "CHRON-DOES-NOT-EXIST"
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            errors = validate_scientific_chronicle(path, GATE)
            self.assertTrue(any("supersedes unknown" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
