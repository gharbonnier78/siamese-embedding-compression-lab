"""Validate the research programme's machine-readable assurance contracts."""

from __future__ import annotations

import hashlib
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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_research_program(root: str | Path) -> AssuranceReport:
    """Return a deterministic cross-contract validation report."""
    root = Path(root)
    errors: list[str] = []
    checks: list[str] = []

    required = [
        "CHANGELOG.md",
        "ERRATA_STUDY_0.md",
        "docs/EXPERIMENT_HISTORY_AND_ERRATA.md",
        "protocol/experiment_ledger.yaml",
        "protocol/research_program.yaml",
        "protocol/studies/study_0_lfw.yaml",
        "protocol/studies/study_0_subject_bootstrap_spec.md",
        "protocol/studies/study_0_subject_bootstrap_v0.2.2.yaml",
        "protocol/studies/study_1_face_backbone.yaml",
        "protocol/studies/study_1_preregistration.md",
        "protocol/studies/study_2_compression_ablation.yaml",
        "protocol/studies/study_3_external_shift.yaml",
        "protocol/studies/study_4_identification_engineering.yaml",
        "protocol/studies/study_5_independent_reproduction.yaml",
        "claims/registry.yaml",
        "beliefs/prior_posterior.yaml",
        "configs/lfw_resnet18.yaml",
        "datasets/lfw_datasheet.yaml",
        "datasets/qualification_requirements.yaml",
        "gates/gate_spec.yaml",
        "gates/cal_spec.yaml",
        "paper/main.tex",
        "paper/figures-generated/figures_manifest.json",
        "evidence/study_0_lfw/run_manifest.json",
        "evidence/study_0_lfw/method_summary.csv",
        "evidence/study_0_lfw/paired_noninferiority.csv",
        "evidence/study_0_lfw/storage_engineering.csv",
        "output/pdf/siamese_embedding_compression_research_program_v0.2.pdf",
    ]
    for relative in required:
        _require((root / relative).is_file(), f"missing required file: {relative}", errors)
    if errors:
        return AssuranceReport("FAIL", checks, errors)
    checks.append("required_files_present")

    programme = _load_yaml(root / "protocol/research_program.yaml")
    ledger = _load_yaml(root / "protocol/experiment_ledger.yaml")
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

    reanalysis = next(
        study
        for study in studies
        if study.get("study_id") == "study_0_subject_bootstrap_v0_2_2"
    )
    _require(
        reanalysis.get("execution_status") == "SPECIFIED_NOT_EXECUTED",
        "v0.2.2 reanalysis must remain specified and unexecuted on the spec branch",
        errors,
    )
    reanalysis_status = reanalysis.get("status")
    _require(
        reanalysis_status in {"DRAFT_PREREGISTRATION", "PREREGISTERED"},
        "v0.2.2 spec status must be DRAFT_PREREGISTRATION or PREREGISTERED",
        errors,
    )
    _require(
        reanalysis.get("results") in (None, {}),
        "unexecuted v0.2.2 reanalysis cannot contain results",
        errors,
    )
    _require(
        str(reanalysis.get("decision", {}).get("g2", "")).startswith("FAIL_"),
        "unexecuted v0.2.2 reanalysis cannot pass G2",
        errors,
    )
    _require(reanalysis.get("study_1_started") is False, "v0.2.2 cannot start Study 1", errors)
    subject_spec = (root / "protocol/studies/study_0_subject_bootstrap_spec.md").read_text(
        encoding="utf-8"
    )
    status_token = (
        "SPECIFICATION DRAFT"
        if reanalysis_status == "DRAFT_PREREGISTRATION"
        else "PREREGISTERED"
    )
    for token in [
        status_token,
        "NOT IMPLEMENTED",
        "NO REANALYSIS RESULTS",
        "w_e = m_i",
        "w_e = m_i * m_j",
        "never synthesized",
        "10,000",
        "Study 1",
    ]:
        _require(token in subject_spec, f"v0.2.2 specification missing token: {token}", errors)
    checks.append("v0_2_2_specification_is_non_executing")

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
    for field_name in [
        "train_pairs",
        "validation_pairs",
        "test_pairs",
        "test_genuine_pairs",
        "test_impostor_pairs",
    ]:
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

    ledger_study_zero = next(
        item for item in ledger.get("studies", []) if item.get("study_id") == "study_0_lfw"
    )
    ledger_reanalysis = next(
        item
        for item in ledger.get("studies", [])
        if item.get("study_id") == "study_0_subject_bootstrap_v0_2_2"
    )
    _require(ledger.get("append_only") is True, "experiment ledger must be append-only", errors)
    _require(
        ledger_study_zero.get("run_id") == study_zero["run"]["run_id"],
        "experiment ledger changed the Study 0 run ID",
        errors,
    )
    _require(
        ledger_reanalysis.get("execution_status") == "SPECIFIED_NOT_EXECUTED",
        "experiment ledger cannot report an executed v0.2.2 reanalysis",
        errors,
    )
    archived_pdf = root / ledger_study_zero["original_paper"]
    _require(
        archived_pdf.is_file()
        and _sha256(archived_pdf) == ledger_study_zero.get("original_paper_sha256"),
        "archived v0.2 paper is missing or changed",
        errors,
    )
    _require(
        study_zero.get("qualification", {}).get("g2") == "FAIL",
        "Study 0 G2 failure E-STAT-001 must remain explicit",
        errors,
    )
    erratum = (root / "ERRATA_STUDY_0.md").read_text(encoding="utf-8")
    for token in ["E-STAT-001", "pair-level", "identity-aware", "0.156"]:
        _require(token in erratum, f"Study 0 erratum missing required token: {token}", errors)
    checks.append("append_only_history_and_errata_preserved")

    figure_manifest = json.loads(
        (root / "paper/figures-generated/figures_manifest.json").read_text(encoding="utf-8")
    )
    _require(
        figure_manifest.get("run_id") == study_zero["run"]["run_id"],
        "figure manifest run ID diverges from Study 0",
        errors,
    )
    for relative, expected_digest in figure_manifest.get("source_files", {}).items():
        source_path = root / "evidence/study_0_lfw" / relative
        _require(source_path.is_file(), f"figure source missing: {relative}", errors)
        if source_path.is_file():
            _require(
                _sha256(source_path) == expected_digest,
                f"figure source digest mismatch: {relative}",
                errors,
            )
    for relative, expected_digest in figure_manifest.get("protocol_sources", {}).items():
        source_path = root / relative
        _require(source_path.is_file(), f"figure protocol source missing: {relative}", errors)
        if source_path.is_file():
            _require(
                _sha256(source_path) == expected_digest,
                f"figure protocol digest mismatch: {relative}",
                errors,
            )
    for filename, expected_digest in figure_manifest.get("outputs", {}).items():
        output_path = root / "paper/figures-generated" / filename
        _require(output_path.is_file(), f"generated figure missing: {filename}", errors)
        if output_path.is_file():
            _require(
                _sha256(output_path) == expected_digest,
                f"generated figure digest mismatch: {filename}",
                errors,
            )
    checks.append("generated_figures_bound_to_replay_evidence")

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
        "E-STAT-001",
        "pair-level",
    ]:
        _require(token in paper, f"paper missing required traceability token: {token}", errors)
    checks.append("paper_traceability_tokens_present")

    status = "PASS" if not errors else "FAIL"
    return AssuranceReport(status, checks, errors)


def write_report(report: AssuranceReport, path: str | Path) -> None:
    Path(path).write_text(json.dumps(report.as_dict(), indent=2) + "\n", encoding="utf-8")
