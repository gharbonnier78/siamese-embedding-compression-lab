"""Frozen Study 0 v0.2.2 historical reanalysis orchestration.

This module binds the already-reviewed subject-bootstrap estimator to immutable Study 0
artifacts.  It deliberately does not decide scientific claims.  Production callers MUST run
the historical-access preflight before calling :func:`execute_historical_reanalysis`.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import yaml

from .subject_bootstrap import (
    DegenerateReplicateError,
    SubjectPairRow,
    bootstrap_weight_diagnostics,
    draw_subject_multiplicities,
    edge_weights,
    percentile_summary,
    reconstruct_lfw_devtest_subject_map,
    subject_bootstrap_delta_fnmr,
    subject_universe,
    validate_subject_map,
    weighted_rates_at_threshold,
    weighted_threshold_at_fmr,
    write_subject_map,
)
from .subject_bootstrap_io import (
    STUDY0_TEST_PAIR_SCORES_BYTES,
    STUDY0_TEST_PAIR_SCORES_SHA256,
    load_and_validate_score_join,
    sha256_file,
    verify_historical_score_artifact,
)
from .subject_bootstrap_operational import (
    operational_percentile_summary,
    subject_bootstrap_fixed_threshold,
)

EXPECTED_RUN_ID = "lfw_resnet18_siamese_projection_v0_1-89179914-911192ee-64559cbd"
EXPECTED_MODEL_SEEDS = (11, 29, 47, 71, 101)
EXPECTED_BOOTSTRAP_BASE_SEED = 20260806
EXPECTED_BOOTSTRAP_REPLICATES = 10_000
EXPECTED_CHECKPOINTS = (2_000, 5_000, 10_000)
EXPECTED_TARGET_FMR = 0.01
EXPECTED_NI_MARGIN = 0.03
EXPECTED_SUBJECTS = 963
EXPECTED_PAIRS = 1_000
EXPECTED_GENUINE = 500
EXPECTED_IMPOSTOR = 500
REFERENCE_METHOD = "raw"
CANDIDATE_METHODS = ("random", "pca", "siamese")
ALL_METHODS = (REFERENCE_METHOD, *CANDIDATE_METHODS)
REQUIRED_HISTORICAL_FILES = (
    "run_manifest.json",
    "test_pair_scores.csv",
    "thresholds.csv",
    "paired_noninferiority.csv",
)


@dataclass(frozen=True)
class HistoricalSourceIdentity:
    score_bytes: int = STUDY0_TEST_PAIR_SCORES_BYTES
    score_sha256: str = STUDY0_TEST_PAIR_SCORES_SHA256


@dataclass(frozen=True)
class FrozenRunnerConfig:
    run_id: str
    model_seeds: tuple[int, ...]
    bootstrap_base_seed: int
    bootstrap_replicates: int
    convergence_checkpoints: tuple[int, ...]
    target_fmr: float
    noninferiority_margin_fnmr: float
    sampling_unit: str
    subject_draws_per_replicate: int
    paired_routes_same_draw: bool
    degenerate_replicate_action: str
    methods: tuple[str, ...]
    reference_method: str

    def as_dict(self) -> dict[str, Any]:
        value = asdict(self)
        for key in ("model_seeds", "convergence_checkpoints", "methods"):
            value[key] = list(value[key])
        return value


class HistoricalInputError(RuntimeError):
    """Raised when immutable historical input provenance or schema is inconsistent."""


class ReanalysisMaterializationError(RuntimeError):
    """Raised when the complete frozen bundle cannot be materialized."""


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


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(_canonical_json(row) + "\n")


def _dependency_versions(names: Iterable[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in names:
        try:
            result[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            result[name] = "not-installed"
    return result


def _git_head(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReanalysisMaterializationError("cannot record runner git HEAD") from exc
    head = completed.stdout.strip()
    if not head:
        raise ReanalysisMaterializationError("runner git HEAD is empty")
    return head


def frozen_runner_config(
    study_protocol_path: str | Path,
    historical_manifest: dict[str, Any],
) -> FrozenRunnerConfig:
    """Bind orchestration to the frozen protocol and the immutable original run config."""
    study = _load_yaml(Path(study_protocol_path))
    historical = study.get("historical_inputs") or {}
    bootstrap = study.get("bootstrap") or {}
    noninferiority = study.get("noninferiority") or {}

    if historical.get("run_id") != EXPECTED_RUN_ID:
        raise HistoricalInputError("Study 0 protocol historical run id drifted")
    seeds = tuple(int(value) for value in noninferiority.get("seeds") or [])
    if seeds != EXPECTED_MODEL_SEEDS:
        raise HistoricalInputError("Study 0 projection seed set drifted")
    if int(bootstrap.get("replicates", -1)) != EXPECTED_BOOTSTRAP_REPLICATES:
        raise HistoricalInputError("Study 0 bootstrap replicate count drifted")
    checkpoints = tuple(int(value) for value in bootstrap.get("convergence_checkpoints") or [])
    if checkpoints != EXPECTED_CHECKPOINTS:
        raise HistoricalInputError("Study 0 convergence checkpoints drifted")
    if bootstrap.get("sampling_unit") != "subject_slot":
        raise HistoricalInputError("Study 0 sampling unit drifted")
    if int(bootstrap.get("subject_draws_per_replicate", -1)) != EXPECTED_SUBJECTS:
        raise HistoricalInputError("Study 0 subject draw count drifted")
    if bootstrap.get("paired_routes_same_draw") is not True:
        raise HistoricalInputError("Study 0 paired-route draw rule drifted")
    if float(noninferiority.get("delta_fnmr", np.nan)) != EXPECTED_NI_MARGIN:
        raise HistoricalInputError("Study 0 non-inferiority margin drifted")
    if (study.get("degenerate_replicates") or {}).get("default_action") != "FAIL_REANALYSIS":
        raise HistoricalInputError("Study 0 degeneracy action drifted")
    target = float((study.get("estimands") or {}).get("representation", {}).get("target_fmr", np.nan))
    if target != EXPECTED_TARGET_FMR:
        raise HistoricalInputError("Study 0 representation target FMR drifted")

    manifest_config = historical_manifest.get("configuration") or {}
    training = manifest_config.get("training") or {}
    evaluation = manifest_config.get("evaluation") or {}
    manifest_seeds = tuple(int(value) for value in training.get("seeds") or [])
    if manifest_seeds != EXPECTED_MODEL_SEEDS:
        raise HistoricalInputError("historical run model seeds differ from frozen Study 0")
    target_fmrs = [float(value) for value in evaluation.get("target_fmrs") or []]
    if target_fmrs != [EXPECTED_TARGET_FMR]:
        raise HistoricalInputError("historical run target FMR differs from frozen Study 0")
    if float(evaluation.get("noninferiority_delta_fnmr", np.nan)) != EXPECTED_NI_MARGIN:
        raise HistoricalInputError("historical run non-inferiority margin differs from frozen Study 0")
    bootstrap_base_seed = int(evaluation.get("bootstrap_seed", -1))
    if bootstrap_base_seed != EXPECTED_BOOTSTRAP_BASE_SEED:
        raise HistoricalInputError("historical run bootstrap base seed differs from frozen source config")

    # Preserve the original Study 0 seed binding: each route seed uses bootstrap_seed + route seed.
    # This is an orchestration binding, not a new statistical choice, and is reviewed before outcomes.
    return FrozenRunnerConfig(
        run_id=EXPECTED_RUN_ID,
        model_seeds=seeds,
        bootstrap_base_seed=bootstrap_base_seed,
        bootstrap_replicates=EXPECTED_BOOTSTRAP_REPLICATES,
        convergence_checkpoints=checkpoints,
        target_fmr=EXPECTED_TARGET_FMR,
        noninferiority_margin_fnmr=EXPECTED_NI_MARGIN,
        sampling_unit="subject_slot",
        subject_draws_per_replicate=EXPECTED_SUBJECTS,
        paired_routes_same_draw=True,
        degenerate_replicate_action="FAIL_REANALYSIS",
        methods=ALL_METHODS,
        reference_method=REFERENCE_METHOD,
    )


def _manifest_artifact_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    artifacts = manifest.get("artifacts") or []
    result: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        if isinstance(artifact, dict) and isinstance(artifact.get("path"), str):
            result[artifact["path"]] = artifact
    return result


def _verify_manifest_bound_file(
    run_dir: Path,
    artifact_map: dict[str, dict[str, Any]],
    relative_path: str,
) -> dict[str, int | str]:
    entry = artifact_map.get(relative_path)
    if entry is None:
        raise HistoricalInputError(f"historical run manifest lacks {relative_path}")
    path = run_dir / relative_path
    if not path.is_file():
        raise HistoricalInputError(f"historical run file missing: {relative_path}")
    actual_bytes = path.stat().st_size
    actual_sha = sha256_file(path)
    if int(entry.get("bytes", -1)) != actual_bytes:
        raise HistoricalInputError(f"historical manifest byte count mismatch for {relative_path}")
    if entry.get("sha256") != actual_sha:
        raise HistoricalInputError(f"historical manifest SHA-256 mismatch for {relative_path}")
    return {"path": relative_path, "bytes": actual_bytes, "sha256": actual_sha}


def _validate_devtest_source_hashes(
    manifest: dict[str, Any],
    matched_path: Path,
    mismatched_path: Path,
) -> list[dict[str, int | str]]:
    dev_test = ((manifest.get("dataset") or {}).get("dev_test_files") or {})
    expected = {
        "matched": dev_test.get("matched_pairs_sha256"),
        "mismatched": dev_test.get("mismatched_pairs_sha256"),
    }
    if not all(isinstance(value, str) and value for value in expected.values()):
        raise HistoricalInputError("historical run manifest lacks DevTest pair-source hashes")
    result = []
    for label, path in (("matched", matched_path), ("mismatched", mismatched_path)):
        actual = sha256_file(path)
        if actual != expected[label]:
            raise HistoricalInputError(f"DevTest {label} pair source SHA-256 mismatch")
        result.append({"source": label, "path": str(path), "bytes": path.stat().st_size, "sha256": actual})
    return result


def validate_historical_sources(
    *,
    historical_run_dir: str | Path,
    matched_path: str | Path,
    mismatched_path: str | Path,
    study_protocol_path: str | Path,
    score_identity: HistoricalSourceIdentity = HistoricalSourceIdentity(),
) -> tuple[dict[str, Any], FrozenRunnerConfig, list[SubjectPairRow], dict[str, Any]]:
    """Validate immutable provenance before parsing any score value."""
    run_dir = Path(historical_run_dir)
    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise HistoricalInputError("historical run_manifest.json is missing")
    manifest = _load_json(manifest_path)
    if manifest.get("run_id") != EXPECTED_RUN_ID:
        raise HistoricalInputError("historical run id does not match frozen Study 0")

    config = frozen_runner_config(study_protocol_path, manifest)
    artifact_map = _manifest_artifact_map(manifest)
    source_files = [
        _verify_manifest_bound_file(run_dir, artifact_map, name)
        for name in REQUIRED_HISTORICAL_FILES
        if name != "run_manifest.json"
    ]
    score_path = run_dir / "test_pair_scores.csv"
    verify_historical_score_artifact(
        score_path,
        expected_bytes=score_identity.score_bytes,
        expected_sha256=score_identity.score_sha256,
    )

    matched = Path(matched_path)
    mismatched = Path(mismatched_path)
    pair_sources = _validate_devtest_source_hashes(manifest, matched, mismatched)
    rows = reconstruct_lfw_devtest_subject_map(matched, mismatched)
    counts = validate_subject_map(
        rows,
        expected_pairs=EXPECTED_PAIRS,
        expected_genuine=EXPECTED_GENUINE,
        expected_impostor=EXPECTED_IMPOSTOR,
        expected_subjects=EXPECTED_SUBJECTS,
    )
    source_manifest = {
        "historical_run": {
            "run_id": EXPECTED_RUN_ID,
            "manifest_path": str(manifest_path),
            "manifest_bytes": manifest_path.stat().st_size,
            "manifest_sha256": sha256_file(manifest_path),
            "artifacts": source_files,
        },
        "lfw_devtest_pair_sources": pair_sources,
        "subject_map_invariants": counts,
    }
    return manifest, config, rows, source_manifest


def _expected_route_keys() -> set[tuple[str, int]]:
    return {(REFERENCE_METHOD, EXPECTED_MODEL_SEEDS[0])} | {
        (method, seed) for method in CANDIDATE_METHODS for seed in EXPECTED_MODEL_SEEDS
    }


def validate_score_routes(frame: pd.DataFrame) -> None:
    if set(frame["run_id"].astype(str)) != {EXPECTED_RUN_ID}:
        raise HistoricalInputError("historical score rows contain an unexpected run id")
    keys = {(str(method), int(seed)) for method, seed in frame[["method", "seed"]].drop_duplicates().itertuples(index=False, name=None)}
    if keys != _expected_route_keys():
        raise HistoricalInputError(f"historical score route/seed set differs from frozen Study 0: {sorted(keys)}")


def load_validation_thresholds(path: str | Path) -> dict[tuple[str, int], float]:
    frame = pd.read_csv(path)
    required = {"run_id", "method", "seed", "target_fmr", "threshold", "threshold_source"}
    missing = required - set(frame.columns)
    if missing:
        raise HistoricalInputError(f"thresholds.csv missing columns: {sorted(missing)}")
    frame = frame[np.isclose(frame["target_fmr"].astype(float), EXPECTED_TARGET_FMR)].copy()
    if frame.empty:
        raise HistoricalInputError("thresholds.csv lacks target FMR 0.01")
    if set(frame["run_id"].astype(str)) != {EXPECTED_RUN_ID}:
        raise HistoricalInputError("threshold rows contain an unexpected run id")
    if set(frame["threshold_source"].astype(str)) != {"validation"}:
        raise HistoricalInputError("operational thresholds must remain validation-frozen")
    if frame.duplicated(["method", "seed", "target_fmr"]).any():
        raise HistoricalInputError("duplicate validation threshold row")
    if not np.isfinite(frame["threshold"].to_numpy(dtype=np.float64)).all():
        raise HistoricalInputError("validation threshold contains non-finite value")
    thresholds = {
        (str(row.method), int(row.seed)): float(row.threshold)
        for row in frame.itertuples(index=False)
    }
    if set(thresholds) != _expected_route_keys():
        raise HistoricalInputError("validation threshold route/seed set differs from frozen Study 0")
    return thresholds


def load_historical_pair_level(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {
        "run_id",
        "candidate_method",
        "candidate_seed",
        "reference_method",
        "target_fmr",
        "delta_fnmr_mean",
        "delta_fnmr_ci_low",
        "delta_fnmr_ci_high",
    }
    missing = required - set(frame.columns)
    if missing:
        raise HistoricalInputError(f"paired_noninferiority.csv missing columns: {sorted(missing)}")
    selected = frame[np.isclose(frame["target_fmr"].astype(float), EXPECTED_TARGET_FMR)].copy()
    if set(selected["run_id"].astype(str)) != {EXPECTED_RUN_ID}:
        raise HistoricalInputError("pair-level rows contain an unexpected run id")
    if set(selected["reference_method"].astype(str)) != {REFERENCE_METHOD}:
        raise HistoricalInputError("pair-level reference route must remain raw")
    keys = {(str(method), int(seed)) for method, seed in selected[["candidate_method", "candidate_seed"]].itertuples(index=False, name=None)}
    expected = {(method, seed) for method in CANDIDATE_METHODS for seed in EXPECTED_MODEL_SEEDS}
    if keys != expected or len(selected) != len(expected):
        raise HistoricalInputError("pair-level route/seed set differs from frozen Study 0")
    for column in ("delta_fnmr_mean", "delta_fnmr_ci_low", "delta_fnmr_ci_high"):
        if not np.isfinite(selected[column].to_numpy(dtype=np.float64)).all():
            raise HistoricalInputError(f"pair-level {column} contains non-finite value")
    return selected


def _route_distances(
    frame: pd.DataFrame,
    rows: list[SubjectPairRow],
    method: str,
    seed: int,
) -> np.ndarray:
    group = frame[(frame["method"] == method) & (frame["seed"].astype(int) == seed)].copy()
    order = {row.pair_id: index for index, row in enumerate(rows)}
    group["_order"] = group["pair_id"].astype(str).map(order)
    if group["_order"].isnull().any() or len(group) != len(rows):
        raise HistoricalInputError(f"route ({method}, {seed}) cannot align to subject map")
    group = group.sort_values("_order")
    return group["distance"].to_numpy(dtype=np.float64)


def _bootstrap_diagnostics(rows: list[SubjectPairRow], replicates: int, seed: int) -> list[dict[str, int]]:
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    subjects = subject_universe(rows)
    rng = np.random.Generator(np.random.PCG64(seed))
    output: list[dict[str, int]] = []
    for replicate in range(replicates):
        multiplicities = draw_subject_multiplicities(subjects, rng)
        weights = edge_weights(rows, multiplicities)
        output.append({"replicate": replicate, **bootstrap_weight_diagnostics(same, weights)})
    return output


def _point_estimate(
    rows: list[SubjectPairRow],
    candidate: np.ndarray,
    reference: np.ndarray,
    target_fmr: float,
) -> dict[str, float]:
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    weights = np.ones(len(rows), dtype=np.int64)
    candidate_threshold = weighted_threshold_at_fmr(same, candidate, weights, target_fmr)
    reference_threshold = weighted_threshold_at_fmr(same, reference, weights, target_fmr)
    candidate_rates = weighted_rates_at_threshold(same, candidate, weights, candidate_threshold)
    reference_rates = weighted_rates_at_threshold(same, reference, weights, reference_threshold)
    return {
        "candidate_fnmr_point": candidate_rates.fnmr,
        "reference_fnmr_point": reference_rates.fnmr,
        "delta_fnmr_point": candidate_rates.fnmr - reference_rates.fnmr,
        "candidate_threshold_point": candidate_threshold,
        "reference_threshold_point": reference_threshold,
    }


def _convergence_summary(replicates: list[Any], checkpoints: tuple[int, ...]) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    previous: dict[str, float | int] | None = None
    for checkpoint in checkpoints:
        current = percentile_summary(replicates[:checkpoint])
        row: dict[str, Any] = {"checkpoint": checkpoint, **current}
        if previous is None:
            row["delta_ucb_from_previous"] = None
            row["delta_mean_from_previous"] = None
        else:
            row["delta_ucb_from_previous"] = float(current["delta_fnmr_ucb_97_5"]) - float(previous["delta_fnmr_ucb_97_5"])
            row["delta_mean_from_previous"] = float(current["delta_fnmr_mean"]) - float(previous["delta_fnmr_mean"])
        summaries.append(row)
        previous = current
    return {"checkpoints": summaries}


def _audit_event(events: list[dict[str, Any]], event_type: str, **payload: Any) -> None:
    events.append(
        {
            "event_id": f"event-{len(events) + 1:05d}",
            "event_type": event_type,
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
    )


def _artifact_manifest(output_dir: Path) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    for path in sorted(output_dir.rglob("*")):
        if path.is_file() and path.name != "run_manifest.json":
            rows.append(
                {
                    "path": str(path.relative_to(output_dir)),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return rows


def execute_historical_reanalysis(
    *,
    repo_root: str | Path,
    historical_run_dir: str | Path,
    matched_path: str | Path,
    mismatched_path: str | Path,
    output_dir: str | Path,
    study_protocol_path: str | Path,
    coverage_simulation_path: str | Path,
    coverage_gate_path: str | Path,
    score_identity: HistoricalSourceIdentity = HistoricalSourceIdentity(),
) -> Path:
    """Materialize the frozen corrected reanalysis without assigning scientific verdicts."""
    root = Path(repo_root)
    run_dir = Path(historical_run_dir)
    destination = Path(output_dir)
    if destination.exists():
        raise FileExistsError(f"reanalysis output already exists and will not be overwritten: {destination}")
    destination.mkdir(parents=True)
    events: list[dict[str, Any]] = []

    try:
        _audit_event(events, "materialization_started", historical_run_id=EXPECTED_RUN_ID)
        manifest, config, rows, source_manifest = validate_historical_sources(
            historical_run_dir=run_dir,
            matched_path=matched_path,
            mismatched_path=mismatched_path,
            study_protocol_path=study_protocol_path,
            score_identity=score_identity,
        )
        _audit_event(events, "historical_sources_validated", source_manifest=source_manifest)

        write_subject_map(destination / "test_pair_subject_map_v0.2.2.csv", rows)
        (destination / "config.resolved.yaml").write_text(
            yaml.safe_dump(config.as_dict(), sort_keys=True), encoding="utf-8"
        )
        _write_json(destination / "source_manifest.json", source_manifest)

        score_path = run_dir / "test_pair_scores.csv"
        scores = load_and_validate_score_join(score_path, rows)
        validate_score_routes(scores)
        thresholds = load_validation_thresholds(run_dir / "thresholds.csv")
        pair_level = load_historical_pair_level(run_dir / "paired_noninferiority.csv")
        _audit_event(events, "historical_tables_parsed_and_joined", score_rows=len(scores))

        raw_seed = EXPECTED_MODEL_SEEDS[0]
        raw_distances = _route_distances(scores, rows, REFERENCE_METHOD, raw_seed)
        diagnostics_by_seed: dict[int, list[dict[str, int]]] = {}
        for model_seed in EXPECTED_MODEL_SEEDS:
            bootstrap_seed = config.bootstrap_base_seed + model_seed
            diagnostics_by_seed[model_seed] = _bootstrap_diagnostics(
                rows, config.bootstrap_replicates, bootstrap_seed
            )

        replicate_rows: list[dict[str, Any]] = []
        seed_summary_rows: list[dict[str, Any]] = []
        convergence_rows: list[dict[str, Any]] = []
        for method in CANDIDATE_METHODS:
            for model_seed in EXPECTED_MODEL_SEEDS:
                bootstrap_seed = config.bootstrap_base_seed + model_seed
                candidate = _route_distances(scores, rows, method, model_seed)
                point = _point_estimate(rows, candidate, raw_distances, config.target_fmr)
                replicates = subject_bootstrap_delta_fnmr(
                    rows=rows,
                    candidate_distances=candidate,
                    reference_distances=raw_distances,
                    target_fmr=config.target_fmr,
                    replicates=config.bootstrap_replicates,
                    seed=bootstrap_seed,
                )
                if len(replicates) != config.bootstrap_replicates:
                    raise ReanalysisMaterializationError("representation bootstrap did not fully materialize")
                diagnostics = diagnostics_by_seed[model_seed]
                for replicate, diagnostic in zip(replicates, diagnostics):
                    if replicate.genuine_weight != diagnostic["genuine_weight"] or replicate.impostor_weight != diagnostic["impostor_weight"]:
                        raise AssertionError("bootstrap diagnostic replay diverged from representation estimator")
                    replicate_rows.append(
                        {
                            "candidate_method": method,
                            "candidate_seed": model_seed,
                            "reference_method": REFERENCE_METHOD,
                            "reference_seed": raw_seed,
                            "bootstrap_seed": bootstrap_seed,
                            **asdict(replicate),
                            "effective_genuine_edges": diagnostic["effective_genuine_edges"],
                            "effective_impostor_edges": diagnostic["effective_impostor_edges"],
                        }
                    )
                summary = percentile_summary(replicates)
                convergence = _convergence_summary(replicates, config.convergence_checkpoints)
                seed_summary_rows.append(
                    {
                        "candidate_method": method,
                        "candidate_seed": model_seed,
                        "reference_method": REFERENCE_METHOD,
                        "reference_seed": raw_seed,
                        "bootstrap_seed": bootstrap_seed,
                        "target_fmr": config.target_fmr,
                        "noninferiority_margin_fnmr": config.noninferiority_margin_fnmr,
                        **point,
                        **summary,
                        "interpretation_status": "NOT_INTERPRETED",
                    }
                )
                for checkpoint in convergence["checkpoints"]:
                    convergence_rows.append(
                        {
                            "candidate_method": method,
                            "candidate_seed": model_seed,
                            "bootstrap_seed": bootstrap_seed,
                            **checkpoint,
                        }
                    )
                _audit_event(events, "representation_seed_materialized", method=method, seed=model_seed)

        pd.DataFrame(replicate_rows).to_csv(
            destination / "subject_bootstrap_replicates.csv", index=False
        )
        pd.DataFrame(seed_summary_rows).to_csv(
            destination / "subject_bootstrap_seed_summary.csv", index=False
        )
        pd.DataFrame(convergence_rows).to_csv(
            destination / "subject_bootstrap_convergence.csv", index=False
        )

        subject_summary = pd.DataFrame(seed_summary_rows)
        sensitivity_rows: list[dict[str, Any]] = []
        for historical_row in pair_level.itertuples(index=False):
            current = subject_summary[
                (subject_summary["candidate_method"] == historical_row.candidate_method)
                & (subject_summary["candidate_seed"] == int(historical_row.candidate_seed))
            ].iloc[0]
            sensitivity_rows.append(
                {
                    "candidate_method": str(historical_row.candidate_method),
                    "candidate_seed": int(historical_row.candidate_seed),
                    "target_fmr": EXPECTED_TARGET_FMR,
                    "pair_bootstrap_delta_mean": float(historical_row.delta_fnmr_mean),
                    "pair_bootstrap_ci_low": float(historical_row.delta_fnmr_ci_low),
                    "pair_bootstrap_ci_high": float(historical_row.delta_fnmr_ci_high),
                    "subject_bootstrap_delta_point": float(current.delta_fnmr_point),
                    "subject_bootstrap_delta_mean": float(current.delta_fnmr_mean),
                    "subject_bootstrap_ci_low": float(current.delta_fnmr_ci_low),
                    "subject_bootstrap_ci_high": float(current.delta_fnmr_ci_high),
                    "pair_ci_width": float(historical_row.delta_fnmr_ci_high - historical_row.delta_fnmr_ci_low),
                    "subject_ci_width": float(current.delta_fnmr_ci_high - current.delta_fnmr_ci_low),
                    "interpretation_status": "DESCRIPTIVE_ONLY_NOT_INTERPRETED",
                }
            )
        pd.DataFrame(sensitivity_rows).to_csv(
            destination / "pair_vs_subject_sensitivity.csv", index=False
        )

        operational_rows: list[dict[str, Any]] = []
        operational_replicate_rows: list[dict[str, Any]] = []
        for method, model_seed in sorted(_expected_route_keys()):
            bootstrap_seed = config.bootstrap_base_seed + model_seed
            distances = _route_distances(scores, rows, method, model_seed)
            threshold = thresholds[(method, model_seed)]
            replicates = subject_bootstrap_fixed_threshold(
                rows=rows,
                distances=distances,
                validation_threshold=threshold,
                replicates=config.bootstrap_replicates,
                seed=bootstrap_seed,
            )
            if len(replicates) != config.bootstrap_replicates:
                raise ReanalysisMaterializationError("operational bootstrap did not fully materialize")
            diagnostics = diagnostics_by_seed[model_seed]
            for replicate, diagnostic in zip(replicates, diagnostics):
                if replicate.genuine_weight != diagnostic["genuine_weight"] or replicate.impostor_weight != diagnostic["impostor_weight"]:
                    raise AssertionError("bootstrap diagnostic replay diverged from operational estimator")
                operational_replicate_rows.append(
                    {
                        "method": method,
                        "seed": model_seed,
                        "bootstrap_seed": bootstrap_seed,
                        **asdict(replicate),
                        "effective_genuine_edges": diagnostic["effective_genuine_edges"],
                        "effective_impostor_edges": diagnostic["effective_impostor_edges"],
                    }
                )
            operational_rows.append(
                {
                    "method": method,
                    "seed": model_seed,
                    "bootstrap_seed": bootstrap_seed,
                    "target_fmr": config.target_fmr,
                    "threshold_source": "validation",
                    **operational_percentile_summary(replicates),
                    "interpretation_status": "NOT_INTERPRETED",
                }
            )
            _audit_event(events, "operational_seed_materialized", method=method, seed=model_seed)

        pd.DataFrame(operational_replicate_rows).to_csv(
            destination / "operational_bootstrap_replicates.csv", index=False
        )
        pd.DataFrame(operational_rows).to_csv(
            destination / "threshold_transfer_uncertainty.csv", index=False
        )

        coverage_simulation = Path(coverage_simulation_path)
        coverage_gate = Path(coverage_gate_path)
        if not coverage_simulation.is_file() or not coverage_gate.is_file():
            raise ReanalysisMaterializationError("reviewed coverage evidence is missing")
        (destination / "coverage_simulation.csv").write_bytes(coverage_simulation.read_bytes())
        (destination / "coverage_gate.json").write_bytes(coverage_gate.read_bytes())

        _write_jsonl(destination / "audit_trace.jsonl", events)
        replay_compact = {
            "schema_version": "1.0.0",
            "run_type": "study_0_subject_bootstrap_v0.2.2_historical_reanalysis",
            "historical_run_id": EXPECTED_RUN_ID,
            "materialization_status": "COMPLETE_NOT_INTERPRETED",
            "scientific_claim_allowed": False,
            "interpretation_status": "PENDING_INDEPENDENT_REVIEW_AND_GATE_REASSESSMENT",
            "methods": list(ALL_METHODS),
            "model_seeds": list(EXPECTED_MODEL_SEEDS),
            "bootstrap_replicates": EXPECTED_BOOTSTRAP_REPLICATES,
        }
        _write_json(destination / "replay.compact.json", replay_compact)
        _write_jsonl(destination / "audit_trace.jsonl", events)

        runner_head = _git_head(root)
        run_manifest = {
            "schema_version": "1.0.0",
            "run_type": "study_0_subject_bootstrap_v0.2.2_historical_reanalysis",
            "historical_run_id": EXPECTED_RUN_ID,
            "run_status": "MATERIALIZED_NOT_INTERPRETED",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "runner_git_head": runner_head,
            "configuration": config.as_dict(),
            "source_manifest_sha256": sha256_file(destination / "source_manifest.json"),
            "historical_score_source_sha256": score_identity.score_sha256,
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "dependencies": _dependency_versions(["numpy", "pandas", "PyYAML"]),
            },
            "scientific_claim_allowed": False,
            "interpretation_status": "PENDING",
            "original_historical_artifacts_mutated": False,
            "artifacts": _artifact_manifest(destination),
        }
        _write_json(destination / "run_manifest.json", run_manifest)
        return destination / "run_manifest.json"
    except Exception as exc:
        if isinstance(exc, DegenerateReplicateError):
            _audit_event(events, "degenerate_replicate_fail_reanalysis", **exc.audit.as_dict())
        else:
            _audit_event(events, "materialization_failed", error_type=type(exc).__name__, message=str(exc))
        _write_jsonl(destination / "audit_trace.jsonl", events)
        _write_json(
            destination / "run_failure.json",
            {
                "status": "FAILED_NOT_INTERPRETED",
                "error_type": type(exc).__name__,
                "message": str(exc),
                "scientific_claim_allowed": False,
            },
        )
        raise
