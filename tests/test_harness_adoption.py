from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "harness-adoption.yaml"
AGENT_INSTRUCTIONS = ROOT / "AGENTS.md"
CASE_STUDY = ROOT / "pedagogy/case-studies/concurrency-is-not-free.md"
CHRONICLE = ROOT / "protocol/scientific_chronicle.yaml"
PINNED_HARNESS_COMMIT = "422e08f3d6483ca11fa5a4767cffa99ce386bde5"
CASE_STUDY_SOURCE_HARNESS_COMMIT = "1cead5808c126fd38e7505c27502fb3e7671c69a"
PEDAGOGY_ENTRY_ID = "CHRON-20260809-004"
PEDAGOGY_PATH = "pedagogy/case-studies/concurrency-is-not-free.md"


class HarnessAdoptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))

    def test_harness_dependency_is_pinned_to_the_merged_immutable_commit(self) -> None:
        harness = self.manifest["harness"]
        self.assertEqual(
            harness["repository"],
            "gharbonnier78/scientific-research-harness",
        )
        self.assertEqual(harness["ref"], PINNED_HARNESS_COMMIT)
        self.assertRegex(harness["ref"], re.compile(r"\A[0-9a-f]{40}\Z"))
        self.assertEqual(harness["entrypoint"], "HARNESS.md")

    def test_engineering_care_profile_is_declared(self) -> None:
        engineering = self.manifest["execution"]["engineering_care"]
        self.assertEqual(engineering["profile"], "POC")
        self.assertTrue(engineering["rationale"])
        self.assertEqual(
            engineering["telemetry_evidence"],
            "not_applicable_unless_later_declared_by_contract",
        )

    def test_local_manifest_references_resolve(self) -> None:
        consumer = self.manifest["consumer"]
        for path in consumer["instruction_entrypoints"]:
            self.assertTrue((ROOT / path).is_file(), path)

        for source in self.manifest["authority"]["sources"]:
            self.assertTrue((ROOT / source["reference"]).exists(), source["reference"])

        artifacts = self.manifest["artifacts"]
        for key in ("claims", "scientific_gates", "pedagogy"):
            for path in artifacts[key]:
                self.assertTrue((ROOT / path).exists(), path)
        self.assertEqual(artifacts["evidence"], ["artifacts/", "tests/"])
        self.assertTrue((ROOT / "tests").is_dir())
        self.assertTrue((ROOT / artifacts["chronicle"]).is_file())

        for path in self.manifest["local_extensions"]:
            self.assertTrue((ROOT / path).exists(), path)

    def test_scientific_authority_remains_local(self) -> None:
        artifacts = self.manifest["artifacts"]
        self.assertEqual(
            artifacts["scientific_gates"],
            ["protocol/scientific_chronicle.yaml"],
        )
        self.assertEqual(artifacts["chronicle"], "protocol/scientific_chronicle.yaml")
        self.assertTrue(self.manifest["authority"]["prohibited_substitution"])
        self.assertEqual(self.manifest["deviations"], [])

    def test_instructions_and_pedagogy_preserve_the_authority_boundary(self) -> None:
        instructions = AGENT_INSTRUCTIONS.read_text(encoding="utf-8")
        case_study = CASE_STUDY.read_text(encoding="utf-8")
        self.assertIn("The harness constrains method", instructions)
        self.assertIn("not outcome evidence", case_study)
        self.assertIn(CASE_STUDY_SOURCE_HARNESS_COMMIT, case_study)
        self.assertIn("removing this file changes no runner behavior", case_study)

    def test_chronicle_and_pedagogy_are_cross_referenced_without_outcome_claim(self) -> None:
        chronicle = yaml.safe_load(CHRONICLE.read_text(encoding="utf-8"))
        entry = next(
            item for item in chronicle["entries"] if item["id"] == PEDAGOGY_ENTRY_ID
        )
        case_study = CASE_STUDY.read_text(encoding="utf-8")
        self.assertIn(PEDAGOGY_PATH, entry["evidence_refs"])
        self.assertFalse(entry["outcome_evidence_seen"])
        self.assertIn(PEDAGOGY_ENTRY_ID, case_study)


if __name__ == "__main__":
    unittest.main()
