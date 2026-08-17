"""Deterministic decomposed execution and artifact validation for Study 0 coverage.

This module is execution infrastructure only. It does not change the frozen coverage
estimands, scenarios, thresholds, bootstrap rules, stopping rule, or gate criteria. It
provides a scenario/chunk execution surface that is exactly replayable from the existing
SeedSequence hierarchy and an artifact contract that refuses gaps, overlaps, mixed commits,
mixed contracts, reordered outcomes, incomplete chunks, or digest corruption.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Any

import yaml

from .coverage_execution import (
    CoverageEngine,
    DatasetCoverageOutcome,
    SeedSequenceDescriptor,
    aggregate_dataset_outcomes,
    build_scenario_execution_plan,
    run_coverage_dataset,
    seed_descriptor_to_int,
    spawn_scenario_seed_sequences,
)
from .coverage_simulation import CoverageResult, CoverageScenario, make_sparse_graph

EXECUTION_AUTHORIZED_CONTRACT_STATUS = "EXECUTION_AUTHORIZED"
SCENARIO_CHUNK_ARTIFACT_TYPE = "study0_coverage_scenario_chunk"
SCENARIO_CHUNK_SCHEMA_VERSION = "1.0.0"
DECOMPOSED_PRODUCTION_GATE = "decomposed_production_coverage_gate"

RangeProgressCallback = Callable[[int, int], None]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def contract_sha256(path: Path) -> str:
    return sha256_file(path)


def load_coverage_contract(
    path: Path,
    *,
    require_execution_authorized: bool = True,
) -> dict[str, Any]:
    """Load the frozen coverage contract without ever reading historical Study 0 scores."""
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("coverage contract must be a YAML mapping")
    if (
        require_execution_authorized
        and value.get("status") != EXECUTION_AUTHORIZED_CONTRACT_STATUS
    ):
        raise ValueError(
            "coverage contract status must be "
            f"{EXECUTION_AUTHORIZED_CONTRACT_STATUS!r} for production execution; "
            f"got {value.get('status')!r}"
        )
    if value.get("historical_study_0_scores_permitted") is not False:
        raise ValueError("coverage contract must prohibit historical Study 0 scores")

    hierarchy = value.get("rng_hierarchy", {})
    if hierarchy.get("derivation") != "numpy_seedsequence_spawn":
        raise ValueError("coverage contract must require numpy SeedSequence.spawn hierarchy")
    if hierarchy.get("arithmetic_seed_offsets_forbidden") is not True:
        raise ValueError("coverage contract must forbid arithmetic seed offsets")
    if hierarchy.get("worker_count_must_not_change_outputs") is not True:
        raise ValueError("coverage contract must require worker-count invariant outputs")

    execution = value.get("execution", {})
    if execution.get("engine") not in {"legacy", "vectorized"}:
        raise ValueError("coverage contract must select legacy or vectorized execution engine")
    if execution.get("reference_oracle_engine") != "legacy":
        raise ValueError("coverage contract must preserve legacy as the execution oracle")
    if execution.get("exact_dataset_outcome_equivalence_required") is not True:
        raise ValueError("coverage contract must require exact engine equivalence")
    if execution.get("implementation_only") is not True:
        raise ValueError("coverage engine selection must be implementation-only")

    simulation_precision = value.get("simulation_precision", {})
    checkpoints = simulation_precision.get("dataset_checkpoints")
    if not isinstance(checkpoints, list) or not checkpoints:
        raise ValueError("coverage contract must declare dataset checkpoints")
    if simulation_precision.get("stop_rule") != "first_checkpoint_where_all_metric_mcse_lte_0_005":
        raise ValueError("coverage contract must preserve the frozen first-passing MCSE stop rule")
    return value


def scenario_from_contract(contract: Mapping[str, Any], item: Mapping[str, Any]) -> CoverageScenario:
    graph = contract["graph"]
    return CoverageScenario(
        name=str(item["name"]),
        target_delta_fnmr=float(item["target_delta_fnmr"]),
        n_subjects=int(graph["subjects"]),
        n_genuine=int(graph["genuine_edges"]),
        n_impostor=int(graph["impostor_edges"]),
        subject_effect_sd_genuine=float(item["subject_effect_sd_genuine"]),
        subject_effect_sd_impostor=float(item["subject_effect_sd_impostor"]),
        candidate_reference_noise_correlation=float(
            item["candidate_reference_noise_correlation"]
        ),
        sparse_degree_exponent=float(graph["sparse_degree_exponent"]),
    )


def scenarios_from_contract(contract: Mapping[str, Any]) -> list[CoverageScenario]:
    return [scenario_from_contract(contract, item) for item in contract["scenarios"]]


def _range_worker(args: tuple[Any, ...]) -> DatasetCoverageOutcome:
    scenario, graph, lineage, bootstrap_replicates, engine = args
    return run_coverage_dataset(
        scenario,
        graph,
        lineage,
        bootstrap_replicates,
        engine=engine,
    )


def run_coverage_scenario_range(
    scenario: CoverageScenario,
    *,
    checkpoint: int,
    bootstrap_replicates: int,
    scenario_seed: SeedSequenceDescriptor,
    dataset_start: int = 0,
    dataset_stop: int | None = None,
    workers: int = 1,
    engine: CoverageEngine = "legacy",
    progress_callback: RangeProgressCallback | None = None,
) -> list[DatasetCoverageOutcome]:
    """Execute a canonical dataset-index range from the full checkpoint seed plan.

    The complete checkpoint plan is spawned first and the requested range is sliced only
    afterwards. Therefore a chunk does not renumber datasets and cannot make its random
    lineage depend on chunk boundaries, worker count, scheduling, or retries.
    """
    if checkpoint <= 0:
        raise ValueError("checkpoint must be positive")
    if bootstrap_replicates <= 0:
        raise ValueError("bootstrap_replicates must be positive")
    if workers <= 0:
        raise ValueError("workers must be positive")
    stop = checkpoint if dataset_stop is None else int(dataset_stop)
    start = int(dataset_start)
    if start < 0 or stop <= start or stop > checkpoint:
        raise ValueError("dataset range must satisfy 0 <= start < stop <= checkpoint")
    if engine not in {"legacy", "vectorized"}:
        raise ValueError(f"unknown coverage engine: {engine}")

    plan = build_scenario_execution_plan(scenario_seed, checkpoint)
    graph = make_sparse_graph(scenario, seed=seed_descriptor_to_int(plan.graph))
    selected = plan.datasets[start:stop]
    tasks = [
        (scenario, graph, lineage, bootstrap_replicates, engine)
        for lineage in selected
    ]
    total = len(tasks)
    outcomes: list[DatasetCoverageOutcome] = []

    if workers == 1:
        iterator = (_range_worker(task) for task in tasks)
        for completed, outcome in enumerate(iterator, start=1):
            outcomes.append(outcome)
            if progress_callback is not None:
                progress_callback(completed, total)
        return outcomes

    with ProcessPoolExecutor(max_workers=workers) as executor:
        # executor.map preserves task order; chunk boundaries never alter canonical indices.
        for completed, outcome in enumerate(executor.map(_range_worker, tasks), start=1):
            outcomes.append(outcome)
            if progress_callback is not None:
                progress_callback(completed, total)
    return outcomes


def _outcome_to_jsonable(outcome: DatasetCoverageOutcome) -> dict[str, Any]:
    return asdict(outcome)


def _outcome_from_mapping(value: Mapping[str, Any]) -> DatasetCoverageOutcome:
    return DatasetCoverageOutcome(
        dataset_index=int(value["dataset_index"]),
        representation_covered=bool(value["representation_covered"]),
        operational_fnmr_covered=bool(value["operational_fnmr_covered"]),
        operational_fmr_covered=bool(value["operational_fmr_covered"]),
        degenerate=bool(value["degenerate"]),
        representation_delta_sha256=value.get("representation_delta_sha256"),
        operational_fnmr_sha256=value.get("operational_fnmr_sha256"),
        operational_fmr_sha256=value.get("operational_fmr_sha256"),
        dataset_spawn_key=tuple(int(item) for item in value["dataset_spawn_key"]),
        distances_spawn_key=tuple(int(item) for item in value["distances_spawn_key"]),
        bootstrap_spawn_key=tuple(int(item) for item in value["bootstrap_spawn_key"]),
    )


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_outcomes(path: Path, outcomes: Iterable[DatasetCoverageOutcome]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for outcome in outcomes:
            handle.write(
                json.dumps(
                    _outcome_to_jsonable(outcome),
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            )


def write_scenario_chunk_artifact(
    output_dir: Path,
    *,
    outcomes: list[DatasetCoverageOutcome],
    progress_path: Path,
    execution_metadata: Mapping[str, Any],
    repository: str,
    git_commit: str,
    contract_path: Path,
    contract: Mapping[str, Any],
    scenario_name: str,
    scenario_index: int,
    scenario_count: int,
    checkpoint: int,
    dataset_start: int,
    dataset_stop: int,
    bootstrap_replicates: int,
    root_seed: int,
    scenario_seed: SeedSequenceDescriptor,
    workers: int,
    synthetic_nonproduction_fixture: bool,
) -> Path:
    """Persist one complete, hash-bound chunk; incomplete chunks have no valid manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    if progress_path.resolve() != (output_dir / "progress.jsonl").resolve():
        raise ValueError("progress_path must be output_dir/progress.jsonl")
    if not progress_path.exists():
        raise ValueError("progress log must exist before finalizing a complete chunk")
    expected_indices = list(range(dataset_start, dataset_stop))
    actual_indices = [outcome.dataset_index for outcome in outcomes]
    if actual_indices != expected_indices:
        raise ValueError("chunk outcomes must already be in exact canonical dataset order")

    outcomes_path = output_dir / "dataset_outcomes.jsonl"
    metadata_path = output_dir / "execution_metadata.json"
    _write_outcomes(outcomes_path, outcomes)
    _write_json(metadata_path, execution_metadata)

    execution = contract["execution"]
    manifest = {
        "schema_version": SCENARIO_CHUNK_SCHEMA_VERSION,
        "artifact_type": SCENARIO_CHUNK_ARTIFACT_TYPE,
        "repository": repository,
        "git_commit": git_commit,
        "contract_path": str(contract_path.as_posix()),
        "contract_sha256": contract_sha256(contract_path),
        "contract_id": str(contract["contract_id"]),
        "scenario": scenario_name,
        "scenario_index": scenario_index,
        "scenario_count": scenario_count,
        "checkpoint": checkpoint,
        "dataset_start": dataset_start,
        "dataset_stop": dataset_stop,
        "bootstrap_replicates": bootstrap_replicates,
        "root_seed": root_seed,
        "scenario_seed_entropy": scenario_seed.entropy,
        "scenario_spawn_key": list(scenario_seed.spawn_key),
        "engine": str(execution["engine"]),
        "reference_oracle_engine": str(execution["reference_oracle_engine"]),
        "workers": workers,
        "outcome_count": len(outcomes),
        "complete": True,
        "resume_eligible": True,
        "synthetic_nonproduction_fixture": synthetic_nonproduction_fixture,
        "historical_study_0_scores_read": False,
        "historical_study_0_scores_permitted": False,
        "production_gate_claimed": False,
        "scientific_outcomes_present": True,
        "progress_runtime_observability_only": True,
        "dataset_outcomes_sha256": sha256_file(outcomes_path),
        "progress_sha256": sha256_file(progress_path),
        "execution_metadata_sha256": sha256_file(metadata_path),
    }
    manifest_path = output_dir / "manifest.json"
    _write_json(manifest_path, manifest)
    return manifest_path


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def _validate_manifest_flags(manifest: Mapping[str, Any]) -> None:
    if manifest.get("artifact_type") != SCENARIO_CHUNK_ARTIFACT_TYPE:
        raise ValueError("unexpected coverage artifact type")
    if manifest.get("schema_version") != SCENARIO_CHUNK_SCHEMA_VERSION:
        raise ValueError("unexpected coverage artifact schema version")
    if manifest.get("complete") is not True:
        raise ValueError("incomplete coverage chunk cannot be aggregated")
    if manifest.get("resume_eligible") is not True:
        raise ValueError("coverage chunk is not marked resume eligible")
    if manifest.get("historical_study_0_scores_read") is not False:
        raise ValueError("coverage artifact indicates historical Study 0 score access")
    if manifest.get("historical_study_0_scores_permitted") is not False:
        raise ValueError("coverage artifact must prohibit historical Study 0 scores")
    if manifest.get("production_gate_claimed") is not False:
        raise ValueError("scenario chunk must not claim the production gate")
    if manifest.get("progress_runtime_observability_only") is not True:
        raise ValueError("scenario progress must remain runtime-observability-only")


def load_scenario_chunk_artifact(
    artifact_dir: Path,
    *,
    expected_commit: str | None = None,
    expected_contract_sha256: str | None = None,
    expected_contract_id: str | None = None,
    expected_scenario: str | None = None,
    expected_checkpoint: int | None = None,
    verify_seed_lineage: bool = True,
) -> tuple[dict[str, Any], list[DatasetCoverageOutcome]]:
    """Load and strictly validate one complete scenario chunk."""
    manifest_path = artifact_dir / "manifest.json"
    outcomes_path = artifact_dir / "dataset_outcomes.jsonl"
    progress_path = artifact_dir / "progress.jsonl"
    metadata_path = artifact_dir / "execution_metadata.json"
    for path in (manifest_path, outcomes_path, progress_path, metadata_path):
        if not path.exists():
            raise ValueError(f"coverage artifact missing required file: {path.name}")

    manifest = _read_json(manifest_path)
    _validate_manifest_flags(manifest)

    if expected_commit is not None and manifest.get("git_commit") != expected_commit:
        raise ValueError("coverage chunk commit does not match expected commit")
    if (
        expected_contract_sha256 is not None
        and manifest.get("contract_sha256") != expected_contract_sha256
    ):
        raise ValueError("coverage chunk contract digest does not match expected contract")
    if expected_contract_id is not None and manifest.get("contract_id") != expected_contract_id:
        raise ValueError("coverage chunk contract id does not match expected contract")
    if expected_scenario is not None and manifest.get("scenario") != expected_scenario:
        raise ValueError("coverage chunk scenario does not match expected scenario")
    if expected_checkpoint is not None and int(manifest.get("checkpoint")) != expected_checkpoint:
        raise ValueError("coverage chunk checkpoint does not match expected checkpoint")

    digest_expectations = {
        outcomes_path: manifest.get("dataset_outcomes_sha256"),
        progress_path: manifest.get("progress_sha256"),
        metadata_path: manifest.get("execution_metadata_sha256"),
    }
    for path, expected_digest in digest_expectations.items():
        if not isinstance(expected_digest, str) or sha256_file(path) != expected_digest:
            raise ValueError(f"coverage artifact digest mismatch for {path.name}")

    lines = [line for line in outcomes_path.read_text(encoding="utf-8").splitlines() if line]
    outcomes = [_outcome_from_mapping(json.loads(line)) for line in lines]
    start = int(manifest["dataset_start"])
    stop = int(manifest["dataset_stop"])
    checkpoint = int(manifest["checkpoint"])
    if start < 0 or stop <= start or stop > checkpoint:
        raise ValueError("coverage artifact has invalid dataset range")
    expected_indices = list(range(start, stop))
    actual_indices = [outcome.dataset_index for outcome in outcomes]
    if actual_indices != expected_indices:
        raise ValueError("coverage artifact dataset order/range is not canonical")
    if int(manifest["outcome_count"]) != len(outcomes):
        raise ValueError("coverage artifact outcome count does not match payload")

    if verify_seed_lineage:
        scenario_count = int(manifest["scenario_count"])
        scenario_index = int(manifest["scenario_index"])
        if not 1 <= scenario_index <= scenario_count:
            raise ValueError("coverage artifact scenario index is invalid")
        scenario_seeds = spawn_scenario_seed_sequences(int(manifest["root_seed"]), scenario_count)
        scenario_seed = scenario_seeds[scenario_index - 1]
        if list(scenario_seed.spawn_key) != list(manifest["scenario_spawn_key"]):
            raise ValueError("coverage artifact scenario spawn key is inconsistent")
        plan = build_scenario_execution_plan(scenario_seed, checkpoint)
        for outcome in outcomes:
            lineage = plan.datasets[outcome.dataset_index]
            if outcome.dataset_spawn_key != lineage.dataset.spawn_key:
                raise ValueError("coverage artifact dataset spawn key is inconsistent")
            if outcome.distances_spawn_key != lineage.distances.spawn_key:
                raise ValueError("coverage artifact distance spawn key is inconsistent")
            if outcome.bootstrap_spawn_key != lineage.bootstrap.spawn_key:
                raise ValueError("coverage artifact bootstrap spawn key is inconsistent")

    return manifest, outcomes


def merge_scenario_chunks(
    chunks: list[tuple[Mapping[str, Any], list[DatasetCoverageOutcome]]],
    *,
    checkpoint: int,
) -> list[DatasetCoverageOutcome]:
    """Merge complete chunks only when their canonical ranges cover the checkpoint exactly."""
    if not chunks:
        raise ValueError("at least one complete chunk is required")
    first = chunks[0][0]
    identity_fields = (
        "git_commit",
        "contract_sha256",
        "contract_id",
        "scenario",
        "scenario_index",
        "scenario_count",
        "checkpoint",
        "bootstrap_replicates",
        "root_seed",
        "engine",
        "reference_oracle_engine",
    )
    ordered = sorted(chunks, key=lambda item: int(item[0]["dataset_start"]))
    cursor = 0
    merged: list[DatasetCoverageOutcome] = []
    for manifest, outcomes in ordered:
        for field in identity_fields:
            if manifest.get(field) != first.get(field):
                raise ValueError(f"cannot mix coverage chunks with different {field}")
        start = int(manifest["dataset_start"])
        stop = int(manifest["dataset_stop"])
        if start != cursor:
            if start < cursor:
                raise ValueError("coverage chunks overlap or are duplicated")
            raise ValueError("coverage chunks contain a gap")
        merged.extend(outcomes)
        cursor = stop
    if cursor != checkpoint:
        raise ValueError("coverage chunks do not cover the complete checkpoint")
    if [outcome.dataset_index for outcome in merged] != list(range(checkpoint)):
        raise ValueError("merged coverage outcomes are not in canonical order")
    return merged


def aggregate_checkpoint_artifacts(
    contract_path: Path,
    artifact_dirs: Iterable[Path],
    *,
    expected_commit: str,
    checkpoint: int,
    require_execution_authorized: bool,
) -> tuple[list[CoverageResult], dict[str, Any]]:
    """Validate all scenario chunks, aggregate in contract order, and evaluate MCSE stopping."""
    contract = load_coverage_contract(
        contract_path,
        require_execution_authorized=require_execution_authorized,
    )
    checkpoints = [int(item) for item in contract["simulation_precision"]["dataset_checkpoints"]]
    if checkpoint not in checkpoints and require_execution_authorized:
        raise ValueError("checkpoint is not present in the frozen production contract")

    scenarios = scenarios_from_contract(contract)
    expected_names = [scenario.name for scenario in scenarios]
    expected_digest = contract_sha256(contract_path)
    grouped: dict[str, list[tuple[Mapping[str, Any], list[DatasetCoverageOutcome]]]] = {
        name: [] for name in expected_names
    }

    for artifact_dir in artifact_dirs:
        manifest, outcomes = load_scenario_chunk_artifact(
            artifact_dir,
            expected_commit=expected_commit,
            expected_contract_sha256=expected_digest,
            expected_contract_id=str(contract["contract_id"]),
            expected_checkpoint=checkpoint,
        )
        scenario_name = str(manifest["scenario"])
        if scenario_name not in grouped:
            raise ValueError(f"unexpected coverage scenario artifact: {scenario_name}")
        grouped[scenario_name].append((manifest, outcomes))

    missing = [name for name, chunks in grouped.items() if not chunks]
    if missing:
        raise ValueError(f"missing scenario coverage artifacts: {', '.join(missing)}")

    bootstrap_replicates = int(contract["bootstrap"]["replicates_per_simulated_dataset"])
    if not require_execution_authorized:
        # Non-production fixtures may deliberately use a tiny bootstrap count. Every chunk
        # within a scenario must still agree, and the first scenario defines the fixture count.
        first_manifest = grouped[expected_names[0]][0][0]
        bootstrap_replicates = int(first_manifest["bootstrap_replicates"])

    results: list[CoverageResult] = []
    for scenario in scenarios:
        chunks = grouped[scenario.name]
        merged = merge_scenario_chunks(chunks, checkpoint=checkpoint)
        scenario_bootstrap_counts = {int(item[0]["bootstrap_replicates"]) for item in chunks}
        if len(scenario_bootstrap_counts) != 1:
            raise ValueError("scenario chunks disagree on bootstrap replicate count")
        scenario_bootstrap = next(iter(scenario_bootstrap_counts))
        if require_execution_authorized and scenario_bootstrap != bootstrap_replicates:
            raise ValueError("production chunk bootstrap count does not match frozen contract")
        if not require_execution_authorized and scenario_bootstrap != bootstrap_replicates:
            raise ValueError("non-production fixture chunks disagree on bootstrap count")
        results.extend(
            aggregate_dataset_outcomes(
                scenario,
                merged,
                bootstrap_replicates=scenario_bootstrap,
            )
        )

    maximum_mcse = float(
        contract["simulation_precision"]["maximum_monte_carlo_standard_error"]
    )
    mcse_pass = all(result.monte_carlo_standard_error <= maximum_mcse for result in results)
    checkpoint_position = checkpoints.index(checkpoint) if checkpoint in checkpoints else -1
    next_checkpoint = (
        checkpoints[checkpoint_position + 1]
        if checkpoint_position >= 0 and checkpoint_position + 1 < len(checkpoints)
        else None
    )
    decision = {
        "status": "STOP_MCSE_SATISFIED" if mcse_pass else "CONTINUE_MCSE_NOT_SATISFIED",
        "checkpoint": checkpoint,
        "maximum_monte_carlo_standard_error": maximum_mcse,
        "all_metric_mcse_lte_threshold": mcse_pass,
        "selected_checkpoint": checkpoint if mcse_pass else None,
        "next_checkpoint": None if mcse_pass else next_checkpoint,
        "scenario_count": len(scenarios),
        "metric_count": len(results),
        "historical_study_0_scores_read": False,
        "production_coverage_gate_claimed": False,
        "aggregation_only": True,
    }
    return results, decision


def validate_cancelled_runtime_manifest(manifest: Mapping[str, Any]) -> None:
    """Prevent cancelled runtime evidence from being cited as coverage outcome evidence."""
    if manifest.get("conclusion") != "cancelled":
        raise ValueError("cancelled runtime manifest must record conclusion=cancelled")
    if manifest.get("runtime_observability_only") is not True:
        raise ValueError("cancelled runtime evidence must be runtime-observability-only")
    if manifest.get("outcome_evidence_seen") is not False:
        raise ValueError("cancelled runtime evidence must not claim outcome evidence")
    if manifest.get("historical_study_0_scores_read") is not False:
        raise ValueError("cancelled runtime evidence must record historical scores unread")
    if manifest.get("coverage_gate_result_admissible") is not False:
        raise ValueError("cancelled runtime evidence cannot be admissible coverage evidence")
