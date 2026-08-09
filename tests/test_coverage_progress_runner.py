from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CoverageProgressRunnerTests(unittest.TestCase):
    def test_smoke_runner_persists_runtime_only_progress(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "coverage"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_subject_bootstrap_coverage.py",
                    "--output-dir",
                    str(output_dir),
                    "--workers",
                    "2",
                    "--smoke",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("[coverage-progress]", completed.stdout)

            progress_path = output_dir / "progress.jsonl"
            self.assertTrue(progress_path.exists())
            events = [
                json.loads(line)
                for line in progress_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(events[0]["event"], "checkpoint_started")
            dataset_events = [event for event in events if event["event"] == "dataset_progress"]
            scenario_events = [event for event in events if event["event"] == "scenario_complete"]
            self.assertEqual(len(dataset_events), 5)
            self.assertEqual(len(scenario_events), 5)
            self.assertEqual(dataset_events[-1]["checkpoint_progress_percent"], 100.0)
            self.assertTrue(all(event["datasets_completed"] == 2 for event in dataset_events))
            self.assertTrue(all(event["datasets_total"] == 2 for event in dataset_events))
            self.assertTrue(all(event["runtime_observability_only"] is True for event in events))

            forbidden_keys = {
                "coverage",
                "coverage_lower_bound",
                "degenerate_datasets",
                "gate_status",
            }
            self.assertTrue(all(forbidden_keys.isdisjoint(event) for event in events))

            gate = json.loads((output_dir / "coverage_gate.json").read_text(encoding="utf-8"))
            self.assertEqual(gate["status"], "SMOKE_ONLY")
            self.assertEqual(gate["execution_engine"], "vectorized")
            self.assertEqual(gate["reference_oracle_engine"], "legacy")
            self.assertFalse(gate["historical_study_0_scores_read"])
            self.assertTrue((output_dir / "coverage_simulation.csv").exists())


if __name__ == "__main__":
    unittest.main()
