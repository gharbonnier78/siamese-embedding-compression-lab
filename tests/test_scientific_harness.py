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

    def test_append_only_resolution_releases_named_step(self) -> None:
        assert_execution_unblocked(CHRONICLE, GATE, "production_coverage_gate")

    def test_decomposed_production_waits_for_exact_equivalence_evidence(self) -> None:
        with self.assertRaisesRegex(
            ScientificChronicleError,
            "CHRON-20260809-004",
        ):
            assert_execution_unblocked(
                CHRONICLE,
                GATE,
                "decomposed_production_coverage_gate",
            )

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
