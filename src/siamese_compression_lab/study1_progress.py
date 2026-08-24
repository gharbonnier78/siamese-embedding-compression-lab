from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

Clock = Callable[[], float]


@dataclass(frozen=True)
class ProgressConfig:
    stage: str
    unit: str
    block_id: str
    block_start: int
    block_stop: int
    report_every: int
    workers: int
    campaign_total: int | None = None
    campaign_completed_before_block: int = 0

    def __post_init__(self) -> None:
        if self.block_start < 0 or self.block_stop <= self.block_start:
            raise ValueError("invalid progress block bounds")
        if self.report_every <= 0:
            raise ValueError("report_every must be positive")
        if self.workers <= 0:
            raise ValueError("workers must be positive")
        if self.campaign_completed_before_block < 0:
            raise ValueError("campaign_completed_before_block must be non-negative")
        if self.campaign_total is not None and self.campaign_total <= 0:
            raise ValueError("campaign_total must be positive")


class ParentProgressReporter:
    """Study 1 runtime observability, adapted from the Study 0 parent callback pattern.

    Workers do not write the progress log. The parent/aggregator calls ``update`` as
    completed work is received, preserving one ordered GitHub-visible log stream and one
    append-only ``progress.jsonl`` artifact.
    """

    def __init__(
        self,
        progress_path: str | Path,
        config: ProgressConfig,
        *,
        resumed_completed: int = 0,
        clock: Clock = time.monotonic,
    ) -> None:
        self.path = Path(progress_path)
        self.config = config
        self.block_total = config.block_stop - config.block_start
        if resumed_completed < 0 or resumed_completed > self.block_total:
            raise ValueError("resumed_completed outside block")
        self.resumed_completed = resumed_completed
        self._last_emitted = resumed_completed
        self._clock = clock
        self._started = clock()
        self._append("block_started", resumed_completed)

    def _runtime_estimate(self, remaining: int, completed_this_run: int, elapsed: float) -> float | None:
        if completed_this_run <= 0 or elapsed <= 0:
            return None
        return remaining * elapsed / completed_this_run

    def _append(self, event_name: str, completed: int, *, status: str | None = None) -> dict:
        elapsed = max(0.0, self._clock() - self._started)
        completed_this_run = max(0, completed - self.resumed_completed)
        remaining = self.block_total - completed
        eta = self._runtime_estimate(remaining, completed_this_run, elapsed)
        campaign_completed = self.config.campaign_completed_before_block + completed
        campaign_total = self.config.campaign_total
        event = {
            "event": event_name,
            "stage": self.config.stage,
            "unit": self.config.unit,
            "block_id": self.config.block_id,
            "block_start": self.config.block_start,
            "block_stop": self.config.block_stop,
            "block_completed": completed,
            "block_total": self.block_total,
            "canonical_completed_through": self.config.block_start + completed,
            "block_progress_percent": round(100.0 * completed / self.block_total, 3),
            "workers": self.config.workers,
            "resumed_completed": self.resumed_completed,
            "elapsed_seconds_this_run": round(elapsed, 3),
            "throughput_units_per_minute": (
                round(60.0 * completed_this_run / elapsed, 4)
                if elapsed > 0 and completed_this_run > 0
                else None
            ),
            "eta_seconds_block": round(eta, 3) if eta is not None else None,
            "eta_is_runtime_estimate": True,
            "runtime_observability_only": True,
        }
        if campaign_total is not None:
            event["campaign_completed"] = campaign_completed
            event["campaign_total"] = campaign_total
            event["campaign_progress_percent"] = round(
                100.0 * campaign_completed / campaign_total, 3
            )
        if status is not None:
            event["status"] = status
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event, sort_keys=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
        print(f"[study1-progress] {line}", flush=True)
        self._last_emitted = completed
        return event

    def update(self, completed: int) -> dict | None:
        if completed < self.resumed_completed or completed > self.block_total:
            raise ValueError("completed outside valid resumed block range")
        if completed < self._last_emitted:
            raise ValueError("progress must be monotonic")
        if completed != self.block_total and completed - self._last_emitted < self.config.report_every:
            return None
        return self._append("block_progress", completed, status="RUNNING")

    def skipped_valid(self, completed: int) -> dict:
        return self._append("block_progress", completed, status="SKIPPED_VALID")

    def retry(self, completed: int) -> dict:
        return self._append("block_progress", completed, status="RETRY")

    def complete(self) -> dict:
        return self._append("block_complete", self.block_total, status="COMPLETE")


def read_progress_events(path: str | Path) -> list[dict]:
    progress_path = Path(path)
    if not progress_path.exists():
        return []
    events: list[dict] = []
    for line in progress_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise TypeError("progress line must be a JSON object")
            events.append(value)
    return events


def resume_count_for_block(path: str | Path, config: ProgressConfig) -> int:
    completed = 0
    for event in read_progress_events(path):
        if (
            event.get("stage") == config.stage
            and event.get("block_id") == config.block_id
            and event.get("block_start") == config.block_start
            and event.get("block_stop") == config.block_stop
        ):
            completed = max(completed, int(event.get("block_completed", 0)))
    return min(completed, config.block_stop - config.block_start)
