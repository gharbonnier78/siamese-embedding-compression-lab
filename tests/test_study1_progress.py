from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from siamese_compression_lab.study1_progress import (
    ParentProgressReporter,
    ProgressConfig,
    read_progress_events,
    resume_count_for_block,
)


class FakeClock:
    def __init__(self) -> None:
        self.value = 100.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


class Study1ProgressTests(unittest.TestCase):
    def config(self) -> ProgressConfig:
        return ProgressConfig(
            stage="embedding_512d",
            unit="images",
            block_id="images-0002000-0004000",
            block_start=2000,
            block_stop=4000,
            report_every=250,
            workers=4,
            campaign_total=10000,
            campaign_completed_before_block=2000,
        )

    def test_parent_reports_periodic_percent_throughput_eta_and_campaign_progress(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "progress.jsonl"
            clock = FakeClock()
            reporter = ParentProgressReporter(path, self.config(), clock=clock)
            clock.advance(30)
            self.assertIsNone(reporter.update(100))
            clock.advance(30)
            event = reporter.update(250)
            self.assertIsNotNone(event)
            assert event is not None
            self.assertEqual(event["block_progress_percent"], 12.5)
            self.assertEqual(event["canonical_completed_through"], 2250)
            self.assertEqual(event["campaign_completed"], 2250)
            self.assertEqual(event["campaign_progress_percent"], 22.5)
            self.assertGreater(event["throughput_units_per_minute"], 0)
            self.assertGreater(event["eta_seconds_block"], 0)
            self.assertEqual(event["workers"], 4)
            self.assertTrue(event["runtime_observability_only"])

    def test_completion_is_emitted_even_when_not_on_interval(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "progress.jsonl"
            clock = FakeClock()
            reporter = ParentProgressReporter(path, self.config(), clock=clock)
            clock.advance(10)
            event = reporter.update(2000)
            self.assertEqual(event["status"], "RUNNING")
            complete = reporter.complete()
            self.assertEqual(complete["status"], "COMPLETE")
            self.assertEqual(complete["block_progress_percent"], 100.0)

    def test_resume_reads_existing_progress_and_keeps_monotonic_canonical_count(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "progress.jsonl"
            config = self.config()
            clock = FakeClock()
            first = ParentProgressReporter(path, config, clock=clock)
            clock.advance(60)
            first.update(500)
            self.assertEqual(resume_count_for_block(path, config), 500)

            clock2 = FakeClock()
            resumed = ParentProgressReporter(
                path,
                config,
                resumed_completed=resume_count_for_block(path, config),
                clock=clock2,
            )
            clock2.advance(60)
            event = resumed.update(750)
            self.assertEqual(event["resumed_completed"], 500)
            self.assertEqual(event["canonical_completed_through"], 2750)
            self.assertEqual(event["block_progress_percent"], 37.5)

    def test_progress_jsonl_is_append_only_json_objects(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "progress.jsonl"
            clock = FakeClock()
            reporter = ParentProgressReporter(path, self.config(), clock=clock)
            clock.advance(1)
            reporter.update(250)
            reporter.retry(250)
            events = read_progress_events(path)
            self.assertGreaterEqual(len(events), 3)
            for line in path.read_text(encoding="utf-8").splitlines():
                self.assertIsInstance(json.loads(line), dict)
            self.assertEqual(events[-1]["status"], "RETRY")


if __name__ == "__main__":
    unittest.main()
