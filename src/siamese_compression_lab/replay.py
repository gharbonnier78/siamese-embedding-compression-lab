"""MMALS activity-replay compatible evidence bundle writer."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any

from .config import ExperimentConfig, canonical_json, config_dict, config_digest


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def implementation_digest() -> str:
    """Hash the executable Python package independently of configuration and data."""
    package_root = Path(__file__).resolve().parent
    hasher = hashlib.sha256()
    for path in sorted(package_root.rglob("*.py")):
        hasher.update(str(path.relative_to(package_root)).encode("utf-8"))
        hasher.update(path.read_bytes())
    return hasher.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(canonical_json(row) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def dependency_versions(names: Iterable[str]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in names:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = "not-installed"
    return versions


@dataclass
class ReplayRecorder:
    config: ExperimentConfig
    run_dir: Path
    run_id: str
    events: list[dict[str, Any]] = field(default_factory=list)
    audits: list[dict[str, Any]] = field(default_factory=list)
    _logical_step: int = 0

    def event(
        self,
        event_type: str,
        phase: str,
        *,
        status: str = "completed",
        evidence_kind: str = "observed",
        payload: dict[str, Any] | None = None,
    ) -> None:
        self._logical_step += 1
        self.events.append(
            {
                "event_id": f"event-{self._logical_step:05d}",
                "logical_step": self._logical_step,
                "run_id": self.run_id,
                "objective_id": self.config.replay.objective_id,
                "phase": phase,
                "event_type": event_type,
                "status": status,
                "evidence_kind": evidence_kind,
                "payload": payload or {},
            }
        )

    def audit(
        self,
        action: str,
        *,
        rationale: str,
        status: str = "passed",
        evidence_kind: str = "observed",
        inputs: dict[str, Any] | None = None,
        outputs: dict[str, Any] | None = None,
    ) -> None:
        self.audits.append(
            {
                "audit_id": f"audit-{len(self.audits) + 1:05d}",
                "logical_step": self._logical_step,
                "run_id": self.run_id,
                "action": action,
                "status": status,
                "evidence_kind": evidence_kind,
                "rationale": rationale,
                "inputs": inputs or {},
                "outputs": outputs or {},
            }
        )

    def write_streams(self) -> None:
        write_jsonl(self.run_dir / "data" / "events.jsonl", self.events)
        write_jsonl(self.run_dir / "audit_trace.jsonl", self.audits)

    def finalize(
        self,
        *,
        run_status: str,
        evidence_level: str,
        scientific_claim_allowed: bool,
        dataset_metadata: dict[str, Any],
        compact_summary: dict[str, Any],
    ) -> Path:
        self.write_streams()
        compact = {
            "contract_version": self.config.replay.contract_version,
            "run_id": self.run_id,
            "run_status": run_status,
            "objective_id": self.config.replay.objective_id,
            "evidence_level": evidence_level,
            "scientific_claim_allowed": scientific_claim_allowed,
            "summary": compact_summary,
            "events": [
                {
                    "logical_step": event["logical_step"],
                    "phase": event["phase"],
                    "event_type": event["event_type"],
                    "status": event["status"],
                }
                for event in self.events
            ],
        }
        write_json(self.run_dir / "replay.compact.json", compact)

        artifact_rows = []
        for path in sorted(self.run_dir.rglob("*")):
            if path.is_file() and path.name != "run_manifest.json":
                artifact_rows.append(
                    {
                        "path": str(path.relative_to(self.run_dir)),
                        "bytes": path.stat().st_size,
                        "sha256": sha256_file(path),
                    }
                )
        manifest = {
            "contract_version": self.config.replay.contract_version,
            "schema_version": "1.0.0",
            "run_id": self.run_id,
            "experiment_id": self.config.experiment_id,
            "objective_id": self.config.replay.objective_id,
            "run_status": run_status,
            "evidence_level": evidence_level,
            "scientific_claim_allowed": scientific_claim_allowed,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "configuration": config_dict(self.config),
            "configuration_sha256": config_digest(self.config),
            "implementation_sha256": implementation_digest(),
            "dataset": dataset_metadata,
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "dependencies": dependency_versions(
                    [
                        "numpy",
                        "pandas",
                        "scipy",
                        "scikit-learn",
                        "matplotlib",
                        "PyYAML",
                        "torch",
                        "torchvision",
                        "kagglehub",
                    ]
                ),
            },
            "seeds": list(self.config.training.seeds),
            "threshold_policy": "calibrate_on_validation_then_freeze_before_test",
            "benchmark_metric_policy": (
                "test labels may locate equal-FMR comparison points; those thresholds are non-deployable"
            ),
            "test_selection_policy": (
                "no model, hyperparameter, seed, or deployable threshold selection on test labels"
            ),
            "artifacts": artifact_rows,
        }
        write_json(self.run_dir / "run_manifest.json", manifest)
        return self.run_dir / "run_manifest.json"


def deterministic_run_id(config: ExperimentConfig, data_digest: str) -> str:
    return (
        f"{config.experiment_id}-{config_digest(config)[:8]}-"
        f"{data_digest[:8]}-{implementation_digest()[:8]}"
    )
