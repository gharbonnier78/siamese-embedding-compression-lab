from __future__ import annotations

import json
import unittest
from pathlib import Path

from siamese_compression_lab.decomposed_coverage import (
    sha256_file,
    validate_cancelled_runtime_manifest,
)


class CancelledRuntimeEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path("evidence/runtime/cancelled_coverage_run_31312018512")

    def test_cancelled_run_is_bound_as_runtime_only_evidence(self) -> None:
        manifest = json.loads((self.root / "manifest.json").read_text(encoding="utf-8"))
        validate_cancelled_runtime_manifest(manifest)
        self.assertEqual(manifest["workflow_run_id"], 31312018512)
        self.assertEqual(manifest["workflow_job_id"], 93241146532)
        self.assertEqual(manifest["artifact_id"], 9041998610)
        self.assertEqual(
            manifest["artifact_archive_sha256"],
            "c08c4043c8aaba608e37bd56b7086c9055e898ab068f012f74239192b10eed58",
        )
        self.assertEqual(
            sha256_file(self.root / "execution_metadata.json"),
            manifest["files"]["execution_metadata.json"]["sha256"],
        )
        self.assertFalse(manifest["files"]["progress.jsonl"]["repository_copy"])
        self.assertEqual(
            manifest["files"]["progress.jsonl"]["sha256"],
            "8f04887118ce400463047c4ee78cddf38cd5c0369caf583f351a8719a84adec6",
        )

    def test_progress_summary_carries_no_admissible_scientific_result(self) -> None:
        summary = json.loads(
            (self.root / "progress_summary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(summary["event_count"], 654)
        self.assertEqual(summary["checkpoint_4000"]["datasets_completed_observed"], 6150)
        self.assertFalse(summary["scientific_outcome_reuse_permitted"])
        self.assertFalse(summary["historical_study_0_scores_read"])
        self.assertTrue(summary["last_event"]["runtime_observability_only"])


if __name__ == "__main__":
    unittest.main()
