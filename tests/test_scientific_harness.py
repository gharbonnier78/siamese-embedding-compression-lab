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

    def test_resolved_cost_risk_releases_production_coverage(self) -> None:
        assert_execution_unblocked(CHRONICLE, GATE, "production_coverage_gate")

    def test_open_cost_risk_still_blocks_production_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chronicle.yaml"
            doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
            doc["entries"][0]["status"] = "OPEN"
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
            doc["entries"][0]["status"] = "OPEN"
            doc["entries"][0]["next_action"] = None
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            errors = validate_scientific_chronicle(path, GATE)
            self.assertTrue(any("requires next_action" in error for error in errors))

    def test_informational_entry_cannot_block_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chronicle.yaml"
            doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
            doc["entries"][0]["status"] = "INFORMATIONAL"
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            errors = validate_scientific_chronicle(path, GATE)
            self.assertTrue(any("INFORMATIONAL entry cannot block" in error for error in errors))

    def test_resolved_entry_releases_named_step(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chronicle.yaml"
            doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
            doc["entries"][0]["status"] = "RESOLVED"
            doc["entries"][0]["next_action"] = None
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            assert_execution_unblocked(path, GATE, "production_coverage_gate")


if __name__ == "__main__":
    unittest.main()
