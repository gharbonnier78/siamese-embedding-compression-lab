from __future__ import annotations

import argparse
import json
import subprocess
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
COVERAGE_REVIEW = (
    ROOT
    / "evidence/study_0_subject_bootstrap_v0.2.2/coverage_validation_run_32157868533/review_round2_approve.fr.md"
)
COVERAGE_CONTRACT = ROOT / "protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml"
STUDY0 = ROOT / "protocol/studies/study_0_subject_bootstrap_v0.2.2.yaml"
STUDY1 = ROOT / "protocol/studies/study_1_face_backbone.yaml"
CHRONICLE = ROOT / "protocol/scientific_chronicle.yaml"
HARNESS_GATE = ROOT / "gates/scientific_harness.yaml"
PR31_MERGE_SHA = "91b5b84f1d83c15bd2e3fbfa589f809461a77c8b"
COVERAGE_RESOLUTION_ID = "CHRON-20260819-008"
ACCESS_AUTHORIZATION_ID = "CHRON-20260819-009"
MAIN_REFS = ("refs/remotes/origin/main", "refs/heads/main")
NON_EXECUTING_STUDY1_STATUSES = {
    "DRAFT_PREREGISTRATION",
    "DRAFT_PREREGISTRATION_REVIEW_REQUIRED",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: expected YAML mapping")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: expected JSON object")
    return value


def _chronicle_entry(chronicle: dict[str, Any], entry_id: str) -> dict[str, Any]:
    entries = chronicle.get("entries") or []
    for entry in entries:
        if isinstance(entry, dict) and entry.get("id") == entry_id:
            return entry
    raise ValueError(f"required Chronicle entry {entry_id} is missing")


def assert_authorization_merged_to_main(
    root: Path = ROOT,
    main_refs: tuple[str, ...] = MAIN_REFS,
) -> str:
    """Fail closed unless the current execution HEAD is reachable from a local main ref."""
    try:
        head_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            "cannot establish authorization activation: git HEAD is unavailable"
        ) from exc

    head_sha = head_result.stdout.strip()
    if not head_sha:
        raise RuntimeError("cannot establish authorization activation: git HEAD is empty")

    available_refs: list[str] = []
    for ref in main_refs:
        try:
            ref_result = subprocess.run(
                ["git", "show-ref", "--verify", "--quiet", ref],
                cwd=root,
                check=False,
            )
        except OSError as exc:
            raise RuntimeError(
                "cannot establish authorization activation: git executable is unavailable"
            ) from exc

        if ref_result.returncode != 0:
            continue
        available_refs.append(ref)

        ancestor_result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", head_sha, ref],
            cwd=root,
            check=False,
        )
        if ancestor_result.returncode == 0:
            return ref
        if ancestor_result.returncode != 1:
            raise RuntimeError(
                f"cannot establish authorization activation against {ref}: "
                f"git merge-base returned {ancestor_result.returncode}"
            )

    if not available_refs:
        raise RuntimeError(
            "authorization activation cannot be verified: no local origin/main or main ref; "
            "fetch main and retry"
        )

    raise RuntimeError(
        "historical Study 0 authorization is not active: current HEAD is not reachable "
        "from main; merge the independently reviewed authorization and run from main"
    )


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

    prerequisites = authorization.get("prerequisites") or {}
    if prerequisites.get("prerequisite_merge_sha") != PR31_MERGE_SHA:
        raise ValueError("authorization is not anchored to the reviewed PR #31 merge")
    if prerequisites.get("chronicle_resolution") != COVERAGE_RESOLUTION_ID:
        raise ValueError("authorization must depend on CHRON-20260819-008")

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

    chronicle = _load_yaml(CHRONICLE)
    coverage_resolution = _chronicle_entry(chronicle, COVERAGE_RESOLUTION_ID)
    if coverage_resolution.get("status") != "RESOLVED":
        raise ValueError("known-truth coverage review resolution is not RESOLVED")
    if coverage_resolution.get("supersedes") != "CHRON-20260818-007":
        raise ValueError("known-truth coverage review resolution has unexpected lineage")
    if coverage_resolution.get("blocks") not in ([], None):
        raise ValueError("known-truth coverage review resolution still declares blockers")

    access_resolution = _chronicle_entry(chronicle, ACCESS_AUTHORIZATION_ID)
    if access_resolution.get("status") != "RESOLVED":
        raise ValueError("historical score access authorization Chronicle entry is not RESOLVED")
    if access_resolution.get("blocks") not in ([], None):
        raise ValueError("historical score access authorization still declares blockers")

    coverage_gate = _load_json(COVERAGE_GATE)
    prerequisite_gate = prerequisites.get("coverage_gate") or {}
    if prerequisite_gate.get("path") != str(COVERAGE_GATE.relative_to(ROOT)):
        raise ValueError("authorization coverage gate path is not the reviewed gate")
    if coverage_gate.get("status") != prerequisite_gate.get("required_status"):
        raise ValueError("known-truth coverage gate prerequisite is not satisfied")
    if coverage_gate.get("selected_dataset_checkpoint") != prerequisite_gate.get(
        "selected_dataset_checkpoint"
    ):
        raise ValueError("known-truth coverage checkpoint does not match authorization")
    if coverage_gate.get("historical_study_0_scores_read") is not False:
        raise ValueError("coverage evidence indicates historical scores were already read")

    review_prerequisite = prerequisites.get("independent_coverage_review") or {}
    if review_prerequisite.get("path") != str(COVERAGE_REVIEW.relative_to(ROOT)):
        raise ValueError("authorization review path is not the archived independent review")
    review_text = COVERAGE_REVIEW.read_text(encoding="utf-8")
    required_verdict = review_prerequisite.get("required_verdict")
    if required_verdict != "APPROVE" or "VERDICT: APPROVE" not in review_text:
        raise ValueError("independent coverage review prerequisite is not APPROVE")

    frozen_coverage_contract = _load_yaml(COVERAGE_CONTRACT)
    if frozen_coverage_contract.get("historical_study_0_scores_permitted") is not False:
        raise ValueError(
            "frozen coverage contract must remain historical-study-score-access false"
        )

    study0 = _load_yaml(STUDY0)
    if study0.get("results") is not None:
        raise ValueError("preflight expects Study 0 corrected results to be unmaterialized")
    if study0.get("decision", {}).get("state") != "INDETERMINATE":
        raise ValueError("preflight must not inherit a pre-existing corrected Study 0 decision")
    if scope.get("normative_protocol") != str(STUDY0.relative_to(ROOT)):
        raise ValueError("authorization does not reference the frozen Study 0 protocol")
    if scope.get("normative_specification") != study0.get("normative_specification"):
        raise ValueError("authorization specification reference differs from Study 0")
    if scope.get("historical_run_id") != study0.get("historical_inputs", {}).get("run_id"):
        raise ValueError("authorization historical run differs from frozen Study 0")

    if study0.get("historical_inputs", {}).get("original_scores_mutable") is not False:
        raise ValueError("Study 0 no longer declares original scores immutable")
    if study0.get("historical_inputs", {}).get("original_outputs_mutable") is not False:
        raise ValueError("Study 0 no longer declares original outputs immutable")
    if study0.get("scope", {}).get("retraining") is not False:
        raise ValueError("Study 0 frozen scope unexpectedly permits retraining")
    if study0.get("scope", {}).get("score_recomputation") is not False:
        raise ValueError("Study 0 frozen scope unexpectedly permits score recomputation")
    if study0.get("scope", {}).get("all_pairs_generation") is not False:
        raise ValueError("Study 0 frozen scope unexpectedly permits all-pairs generation")
    if study0.get("outputs", {}).get("overwrite_original_study_zero") is not False:
        raise ValueError("Study 0 frozen scope unexpectedly permits original output overwrite")

    study1 = _load_yaml(STUDY1)
    if study1.get("status") not in NON_EXECUTING_STUDY1_STATUSES:
        raise ValueError("Study 1 must remain unstarted and draft-preregistered")

    execution = authorization.get("execution_contract") or {}
    if execution.get("frozen_method_reference") != str(STUDY0.relative_to(ROOT)):
        raise ValueError("authorization execution contract is not bound to frozen Study 0")
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
    if execution.get("degenerate_replicate_action") != study0.get(
        "degenerate_replicates", {}
    ).get("default_action"):
        raise ValueError("authorization degeneracy action differs from frozen Study 0 protocol")

    return authorization


def preflight_historical_reanalysis(
    authorization_path: Path = AUTHORIZATION,
) -> tuple[dict[str, Any], str]:
    """Validate the frozen authorization and enforce its real merge activation boundary."""
    authorization = validate_historical_reanalysis_authorization(authorization_path)
    activated_via = assert_authorization_merged_to_main()
    return authorization, activated_via


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate governance prerequisites before historical Study 0 score access."
    )
    parser.add_argument("--authorization", type=Path, default=AUTHORIZATION)
    args = parser.parse_args()
    _, activated_via = preflight_historical_reanalysis(args.authorization)
    print(
        "PASS: historical Study 0 access is scoped to corrected_study_0_reanalysis and "
        f"activated through {activated_via}; this preflight did not open historical score payloads."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
