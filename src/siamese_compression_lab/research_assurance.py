"""Validate the research programme's machine-readable assurance contracts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AssuranceReport:
    status: str
    checks: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"status": self.status, "checks": self.checks, "errors": self.errors}


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: expected a YAML mapping")
    return value


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_research_program(root: str | Path) -> AssuranceReport:
    """Return a deterministic cross-contract validation report."""
    root = Path(root)
    errors: list[str] = []
    checks: list[str] = []

    required = [
        "protocol/research_program.yaml",
        "protocol/studies/study_0_lfw.yaml",
        "protocol/studies/study_1_face_backbone.yaml",
        "claims/registry.yaml",
        "beliefs/prior_posterior.yaml",
        "configs/lfw_resnet18.yaml",
        "datasets/lfw_datasheet.yaml",
        "datasets/qualification_requirements.yaml",
        "gates/gate_spec.yaml",
        "gates/cal_spec.yaml",
        "paper/main.tex",
    ]
    for relative in required:
        _require((root / relative).is_file(), f"missing required file: {relative}", errors)
    if errors:
        return AssuranceReport("FAIL", checks, errors)
    checks.append("required_files_present")

    programme = _load_yaml(root / "protocol/research_program.yaml")
    claim_doc = _load_yaml(root / "claims/registry.yaml")
    gate_doc = _load_yaml(root / "gates/gate_spec.yaml")
    cal_doc = _load_yaml(root / "gates/cal_spec.yaml")
    lfw_config = _load_yaml(root / "configs/lfw_resnet18.yaml")
    lfw_datasheet = _load_yaml(root / "datasets/lfw_datasheet.yaml")
    study_paths = sorted((root / "protocol/studies").glob("*.yaml"))
    studies = [_load_yaml(path) for path in study_paths]

    study_ids = [study.get("study_id") for study in studies]
    _require(len(study_ids) == len(set(study_ids)), "duplicate study_id", errors)
    for study_id in programme.get("study_order", []):
        if study_id in {"study_0_lfw", "study_1_face_backbone"}:
            _require(study_id in study_ids, f"declared study missing: {study_id}", errors)
    checks.append("study_registry_consistent")

    allowed_study_states = {
        "COMPLETED",
        "DRAFT_PREREGISTRATION",
        "PREREGISTERED",
        "RUNNING",
        "PLANNED",
        "FAILED",
    }
    for study in studies:
        state = study.get("status")
        _require(state in allowed_study_states, f"invalid study status: {state}", errors)
        if state == "COMPLETED":
            run = study.get("run") or {}
            _require(bool(run.get("run_id")), f"{study.get('study_id')}: completed without run_id", errors)
            _require(isinstance(study.get("results"), dict), f"{study.get('study_id')}: completed without results", errors)
        if state in {"PLANNED", "DRAFT_PREREGISTRATION", "PREREGISTERED"}:
            _require(study.get("results") in (None, {}), f"{study.get('study_id')}: unexecuted study has results", errors)
    checks.append("study_status_guards_passed")

    study_zero = next(study for study in studies if study.get("study_id") == "study_0_lfw")
    design = study_zero.get("design") or {}
    data_protocol = lfw_datasheet.get("protocol") or {}
    evaluation = lfw_config.get("evaluation") or {}
    _require(
        design.get("target_fmr") in evaluation.get("target_fmrs", []),
        "Study 0 target FMR diverges from frozen configuration",
        errors,
    )
    _require(
        design.get("noninferiority_delta_fnmr") == evaluation.get("noninferiority_delta_fnmr"),
        "Study 0 non-inferiority margin diverges from frozen configuration",
        errors,
    )
    for field_name in ["train_pairs", "validation_pairs", "test_pairs", "test_impostor_pairs"]:
        _require(
            design.get(field_name) == data_protocol.get(field_name),
            f"Study 0 and LFW datasheet disagree on {field_name}",
            errors,
        )
    result_report = (root / "RESULTS_LFW_V0.1.md").read_text(encoding="utf-8")
    _require(
        study_zero["run"]["run_id"] in result_report,
        "Study 0 run ID is absent from the result report",
        errors,
    )
    checks.append("study_zero_frozen_evidence_consistent")

    gate_ids = {gate.get("id") for gate in gate_doc.get("gates", [])}
    _require(gate_ids == {f"G{index}" for index in range(8)}, "expected gates G0 through G7", errors)
    claim_ids: list[str] = []
    for claim in claim_doc.get("claims", []):
        claim_id = claim.get("id")
        claim_ids.append(claim_id)
        _require(bool(claim.get("permitted_wording")), f"{claim_id}: missing permitted wording", errors)
        _require(bool(claim.get("forbidden_wording")), f"{claim_id}: missing forbidden wording", errors)
        unknown_gates = set(claim.get("required_gates", [])) - gate_ids
        _require(not unknown_gates, f"{claim_id}: unknown gates {sorted(unknown_gates)}", errors)
        for evidence in claim.get("evidence", []):
            _require((root / evidence).exists(), f"{claim_id}: missing evidence {evidence}", errors)
    _require(len(claim_ids) == len(set(claim_ids)), "duplicate claim id", errors)
    claims_by_id = {claim["id"]: claim for claim in claim_doc.get("claims", [])}
    _require(
        claims_by_id["C-NI-001"]["status"] == "NOT_DEMONSTRATED",
        "C-NI-001 must preserve the negative Study 0 decision",
        errors,
    )
    _require(
        study_zero["decision"]["noninferiority_demonstrated"] is False,
        "Study 0 decision cannot claim non-inferiority",
        errors,
    )
    checks.append("claim_registry_cross_references_passed")

    _require(
        cal_doc.get("allowed_outcomes") == ["ADMISSIBLE", "INADMISSIBLE", "INDETERMINATE"],
        "CAL outcomes must be ordered ADMISSIBLE, INADMISSIBLE, INDETERMINATE",
        errors,
    )
    _require(cal_doc.get("default_outcome") == "INDETERMINATE", "CAL default must be INDETERMINATE", errors)
    _require(
        cal_doc.get("metric_plane") == "decision_side_intervention",
        "CAL metric plane must remain decision_side_intervention",
        errors,
    )
    _require(cal_doc.get("not_regulatory_certification") is True, "CAL regulatory boundary missing", errors)
    checks.append("cal_boundary_guards_passed")

    paper = (root / "paper/main.tex").read_text(encoding="utf-8")
    for token in [
        "C-NI-001",
        "Study 0",
        "INDETERMINATE",
        "MMALS",
        "ISO/IEC 19795-1:2021",
        "0.8060",
        "0.8288",
        "0.156",
    ]:
        _require(token in paper, f"paper missing required traceability token: {token}", errors)
    checks.append("paper_traceability_tokens_present")

    status = "PASS" if not errors else "FAIL"
    return AssuranceReport(status, checks, errors)


def write_report(report: AssuranceReport, path: str | Path) -> None:
    Path(path).write_text(json.dumps(report.as_dict(), indent=2) + "\n", encoding="utf-8")
