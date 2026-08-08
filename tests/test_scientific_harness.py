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

    def test_open_cost_risk_blocks_production_coverage(self) -> None:
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

    def test_informational_entry_cannot_block_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chronicle.yaml"
            doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
            doc["entries"][0]["status"] = "INFORMATIONAL"
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            errors = validate_scientific_chronicle(path, GATE)
            self.assertTrue(any("INFORMATIONAL entry cannot block" in error for error in errors))

    def test_append_only_resolution_releases_named_step(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chronicle.yaml"
            doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
            original = dict(doc["entries"][0])
            doc["entries"] = [
                original,
                {
                    "id": "CHRON-TEST-RESOLUTION",
                    "recorded_at_utc": "2026-08-08T14:31:00Z",
                    "scope": original["scope"],
                    "kind": "decision",
                    "status": "RESOLVED",
                    "outcome_evidence_seen": False,
                    "summary": "Synthetic resolution fixture",
                    "rationale": "Exercises append-only supersession semantics.",
                    "evidence_refs": ["tests/test_scientific_harness.py"],
                    "blocks": [],
                    "supersedes": original["id"],
                },
            ]
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            self.assertEqual(doc["entries"][0]["status"], "OPEN")
            assert_execution_unblocked(path, GATE, "production_coverage_gate")

    def test_supersedes_unknown_entry_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "chronicle.yaml"
            doc = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
            doc["entries"].append(
                {
                    "id": "CHRON-TEST-BAD-RESOLUTION",
                    "recorded_at_utc": "2026-08-08T14:31:00Z",
                    "scope": "fixture",
                    "kind": "decision",
                    "status": "RESOLVED",
                    "outcome_evidence_seen": False,
                    "summary": "Bad resolution fixture",
                    "rationale": "Must fail because the target does not exist.",
                    "evidence_refs": ["tests/test_scientific_harness.py"],
                    "blocks": [],
                    "supersedes": "CHRON-DOES-NOT-EXIST",
                }
            )
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
            errors = validate_scientific_chronicle(path, GATE)
            self.assertTrue(any("supersedes unknown chronicle id" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
