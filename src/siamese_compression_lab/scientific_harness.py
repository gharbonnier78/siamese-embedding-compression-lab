"""Scientific chronicle validation and execution preflight guards."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ScientificChronicleError(RuntimeError):
    """Raised when chronicle policy or execution preflight is violated."""


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ScientificChronicleError(f"{path}: expected YAML mapping")
    return value


def _superseded_ids(entries: list[dict[str, Any]]) -> set[str]:
    """Return earlier entry IDs explicitly superseded by later terminal entries."""
    terminal_statuses = {"RESOLVED", "SUPERSEDED", "ACCEPTED_RISK"}
    superseded: set[str] = set()
    for entry in entries:
        if entry.get("status") not in terminal_statuses:
            continue
        targets = entry.get("supersedes") or []
        if isinstance(targets, str):
            targets = [targets]
        superseded.update(str(target) for target in targets)
    return superseded


def validate_scientific_chronicle(
    chronicle_path: str | Path,
    gate_path: str | Path,
) -> list[str]:
    """Return validation errors for the machine-readable scientific chronicle."""
    chronicle = _load_yaml(Path(chronicle_path))
    gate = _load_yaml(Path(gate_path))
    errors: list[str] = []

    if chronicle.get("append_only") is not True:
        errors.append("scientific chronicle must declare append_only: true")
    if gate.get("append_only_required") is not True:
        errors.append("scientific harness gate must require append-only chronology")

    required_fields = list(gate.get("required_entry_fields", []))
    allowed_statuses = set(gate.get("allowed_statuses", []))
    declared_steps = set(gate.get("execution_steps", {}))
    raw_entries = chronicle.get("entries", [])
    if not isinstance(raw_entries, list):
        return errors + ["scientific chronicle entries must be a list"]

    entries: list[dict[str, Any]] = []
    ids: list[str] = []
    id_positions: dict[str, int] = {}
    for index, entry in enumerate(raw_entries):
        if not isinstance(entry, dict):
            errors.append(f"chronicle entry {index} must be a mapping")
            continue
        entries.append(entry)
        entry_id = str(entry.get("id", ""))
        ids.append(entry_id)
        if entry_id and entry_id not in id_positions:
            id_positions[entry_id] = index
        for field_name in required_fields:
            if field_name not in entry:
                errors.append(f"{entry_id or index}: missing chronicle field {field_name}")
        status = entry.get("status")
        if status not in allowed_statuses:
            errors.append(f"{entry_id or index}: invalid chronicle status {status}")
        if status == "OPEN" and not entry.get("next_action"):
            errors.append(f"{entry_id or index}: OPEN chronicle entry requires next_action")
        blocks = entry.get("blocks") or []
        if not isinstance(blocks, list):
            errors.append(f"{entry_id or index}: blocks must be a list")
            blocks = []
        for blocked_step in blocks:
            if blocked_step not in declared_steps:
                errors.append(
                    f"{entry_id or index}: blocks undeclared execution step {blocked_step}"
                )
        if status == "INFORMATIONAL" and blocks:
            errors.append(f"{entry_id or index}: INFORMATIONAL entry cannot block execution")
        if entry.get("outcome_evidence_seen") is not True and entry.get(
            "outcome_evidence_seen"
        ) is not False:
            errors.append(f"{entry_id or index}: outcome_evidence_seen must be boolean")
        if (
            entry.get("outcome_evidence_seen") is True
            and entry.get("kind") == "methodological_change"
            and entry.get("represented_as_preregistered") is True
        ):
            errors.append(
                f"{entry_id or index}: post-outcome methodological change cannot be preregistered"
            )

    if len(ids) != len(set(ids)):
        errors.append("duplicate scientific chronicle id")
    if any(not entry_id for entry_id in ids):
        errors.append("scientific chronicle entry id cannot be empty")

    terminal_statuses = {"RESOLVED", "SUPERSEDED", "ACCEPTED_RISK"}
    for index, entry in enumerate(raw_entries):
        if not isinstance(entry, dict) or "supersedes" not in entry:
            continue
        entry_id = str(entry.get("id", index))
        targets = entry.get("supersedes")
        if isinstance(targets, str):
            targets = [targets]
        if not isinstance(targets, list) or not targets:
            errors.append(f"{entry_id}: supersedes must name at least one earlier entry")
            continue
        if entry.get("status") not in terminal_statuses:
            errors.append(
                f"{entry_id}: only terminal chronicle entries may supersede earlier entries"
            )
        for target in targets:
            target_id = str(target)
            target_position = id_positions.get(target_id)
            if target_position is None:
                errors.append(f"{entry_id}: supersedes unknown chronicle entry {target_id}")
            elif target_position >= index:
                errors.append(
                    f"{entry_id}: supersedes must reference an earlier chronicle entry"
                )

    return errors


def open_blockers_for_step(
    chronicle_path: str | Path,
    step: str,
) -> list[dict[str, Any]]:
    """Return effective OPEN blockers after valid append-only supersession."""
    chronicle = _load_yaml(Path(chronicle_path))
    entries = [
        entry for entry in chronicle.get("entries", []) if isinstance(entry, dict)
    ]
    superseded = _superseded_ids(entries)
    blockers: list[dict[str, Any]] = []
    for entry in entries:
        if (
            entry.get("status") == "OPEN"
            and str(entry.get("id")) not in superseded
            and step in (entry.get("blocks") or [])
        ):
            blockers.append(entry)
    return blockers


def assert_execution_unblocked(
    chronicle_path: str | Path,
    gate_path: str | Path,
    step: str,
) -> None:
    """Fail before production execution when chronicle policy or blockers are unresolved."""
    gate = _load_yaml(Path(gate_path))
    declared_steps = gate.get("execution_steps", {})
    if step not in declared_steps:
        raise ScientificChronicleError(f"unknown execution step {step!r}")
    errors = validate_scientific_chronicle(chronicle_path, gate_path)
    if errors:
        raise ScientificChronicleError("scientific chronicle invalid: " + "; ".join(errors))
    blockers = open_blockers_for_step(chronicle_path, step)
    if blockers:
        ids = ", ".join(str(entry["id"]) for entry in blockers)
        raise ScientificChronicleError(
            f"execution step {step!r} blocked by OPEN scientific chronicle entries: {ids}"
        )
