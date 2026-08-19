from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from siamese_compression_lab.scientific_harness import assert_execution_unblocked

ROOT = Path(__file__).resolve().parents[1]
AUTHORIZATION = ROOT / "protocol/authorizations/study_0_historical_reanalysis_v0.2.2.yaml"
COVERAGE_GATE = (
    ROOT
    / "evidence/study_0_subject_bootstrap_v0.2.2/coverage_validation_run_32157868533/coverage_gate.json"
)
COVERAGE_CONTRACT = ROOT / "protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml"
STUDY0 = ROOT / "protocol/studies/study_0_subject_bootstrap_v0.2.2.yaml"
STUDY1 = ROOT / "protocol/studies/study_1_face_backbone.yaml"
CHRONICLE = ROOT / "protocol/scientific_chronicle.yaml"
HARNESS_GATE = ROOT / "gates/scientific_harness.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def validate_historical_reanalysis_authorization(
    authorization_path: Path = AUTHORIZATION,
) -> dict[str, Any]:
    """Validate access governance without opening historical Study 0 score payloads."""
    authorization = _load_yaml(authorization_path)

    if authorization.get("status") != "AUTHORIZED":
        raise ValueError("historical reanalysis authorization is not AUTHORIZED")
    if authorization.get("activation") != "merge_to_main_after_review":
        raise ValueError("authorization activation must remain merge_to_main_after_review")
    if authorization.get("historical_study_0_scores_permitted") is not True:
        raise ValueError("historical Study 0 score access is not explicitly permitted")

    scope = authorization.get("scope") or {}
    if scope.get("execution_step") != "corrected_study_0_reanalysis":
        raise ValueError("authorization scope must be corrected_study_0_reanalysis only")
    if scope.get("study_id") != "study_0_subject_bootstrap_v0_2_2":
        raise ValueError("authorization scope must be Study 0 v0.2.2 only")

    researcher_go = authorization.get("researcher_go") or {}
    if researcher_go.get("explicit") is not True:
        raise ValueError("explicit researcher GO is required")
    if researcher_go.get("scope_change_requires_new_go") is not True:
        raise ValueError("material authorization scope changes must require a new GO")

    restrictions = authorization.get("restrictions") or {}
    required_true = (
        "original_scores_mutation_forbidden",
        "original_outputs_mutation_forbidden",
    )
    for key in required_true:
        if restrictions.get(key) is not True:
            raise ValueError(f"authorization must preserve restriction {key}")
    required_false = (
        "retraining_permitted",
        "score_recomputation_permitted",
        "all_pairs_generation_permitted",
        "study_1_execution_permitted",
        "geometry_exploration_permitted",
        "post_access_method_change_permitted",
        "scientific_gate_autopromotion_permitted",
        "result_interpretation_before_complete_materialization_permitted",
    )
    for key in required_false:
        if restrictions.get(key) is not False:
            raise ValueError(f"authorization must keep {key}=false")

    assert_execution_unblocked(CHRONICLE, HARNESS_GATE, "corrected_study_0_reanalysis")

    coverage_gate = _load_json(COVERAGE_GATE)
    prerequisite_gate = (authorization.get("prerequisites") or {}).get("coverage_gate") or {}
    if coverage_gate.get("status") != prerequisite_gate.get("required_status"):
        raise ValueError("known-truth coverage gate prerequisite is not satisfied")
    if coverage_gate.get("selected_dataset_checkpoint") != prerequisite_gate.get(
        "selected_dataset_checkpoint"
    ):
        raise ValueError("known-truth coverage checkpoint does not match authorization")
    if coverage_gate.get("historical_study_0_scores_read") is not False:
        raise ValueError("coverage evidence indicates historical scores were already read")

    frozen_coverage_contract = _load_yaml(COVERAGE_CONTRACT)
    if frozen_coverage_contract.get("historical_study_0_scores_permitted") is not False:
        raise ValueError("frozen coverage contract must remain byte-semantically historical-read false")

    study0 = _load_yaml(STUDY0)
    if study0.get("results") is not None:
        raise ValueError("preflight expects Study 0 corrected results to be unmaterialized")
    if study0.get("decision", {}).get("state") != "INDETERMINATE":
        raise ValueError("preflight must not inherit a pre-existing corrected Study 0 decision")

    study1 = _load_yaml(STUDY1)
    if study1.get("status") != "DRAFT_PREREGISTRATION":
        raise ValueError("Study 1 must remain unstarted and draft-preregistered")

    execution = authorization.get("execution_contract") or {}
    frozen_seeds = study0.get("noninferiority", {}).get("seeds")
    if execution.get("seeds") != frozen_seeds:
        raise ValueError("authorization seeds differ from frozen Study 0 protocol")
    if execution.get("bootstrap_replicates") != study0.get("bootstrap", {}).get("replicates"):
        raise ValueError("authorization bootstrap count differs from frozen Study 0 protocol")
    if execution.get("sampling_unit") != study0.get("bootstrap", {}).get("sampling_unit"):
        raise ValueError("authorization sampling unit differs from frozen Study 0 protocol")
    if execution.get("paired_routes_same_draw") != study0.get("bootstrap", {}).get(
        "paired_routes_same_draw"
    ):
        raise ValueError("authorization paired-draw rule differs from frozen Study 0 protocol")

    return authorization


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate governance prerequisites before historical Study 0 score access."
    )
    parser.add_argument("--authorization", type=Path, default=AUTHORIZATION)
    args = parser.parse_args()
    validate_historical_reanalysis_authorization(args.authorization)
    print(
        "PASS: historical Study 0 access is scoped to corrected_study_0_reanalysis; "
        "this preflight did not open historical score payloads."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
