"""Run one Study 0 coverage scenario/chunk without reading historical Study 0 scores."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from collections.abc import Callable
from pathlib import Path

import numpy as np

from siamese_compression_lab.coverage_execution import spawn_scenario_seed_sequences
from siamese_compression_lab.decomposed_coverage import (
    DECOMPOSED_PRODUCTION_GATE,
    load_coverage_contract,
    run_coverage_scenario_range,
    scenarios_from_contract,
    write_scenario_chunk_artifact,
)
from siamese_compression_lab.scientific_harness import assert_execution_unblocked

PROGRESS_EVERY_DATASETS = 25
DEFAULT_CONTRACT = Path("protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml")
DEFAULT_CHRONICLE = Path("protocol/scientific_chronicle.yaml")
DEFAULT_SCIENTIFIC_HARNESS = Path("gates/scientific_harness.yaml")
REPOSITORY = "gharbonnier78/siamese-embedding-compression-lab"


def _append_progress(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(event, sort_keys=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(f"[coverage-progress] {line}", flush=True)


def _runtime_estimate(remaining: int, completed: int, elapsed_seconds: float) -> float | None:
    if completed <= 0 or elapsed_seconds <= 0:
        return None
    return remaining * elapsed_seconds / completed


def _make_progress_callback(
    *,
    progress_path: Path,
    scenario_name: str,
    checkpoint: int,
    dataset_start: int,
    dataset_stop: int,
    started: float,
) -> Callable[[int, int], None]:
    def report_progress(completed: int, total: int) -> None:
        if completed != total and completed % PROGRESS_EVERY_DATASETS != 0:
            return
        elapsed = time.monotonic() - started
        remaining = total - completed
        eta = _runtime_estimate(remaining, completed, elapsed)
        canonical_completed_through = dataset_start + completed
        event = {
            "event": "dataset_progress",
            "scenario": scenario_name,
            "checkpoint": checkpoint,
            "dataset_start": dataset_start,
            "dataset_stop": dataset_stop,
            "datasets_completed": completed,
            "datasets_total": total,
            "canonical_datasets_completed_through": canonical_completed_through,
            "progress_percent": round(100.0 * completed / total, 3),
            "elapsed_seconds": round(elapsed, 3),
            "throughput_datasets_per_minute": round(60.0 * completed / elapsed, 4)
            if elapsed > 0
            else None,
            "eta_seconds": round(eta, 3) if eta is not None else None,
            "eta_is_runtime_estimate": True,
            "runtime_observability_only": True,
        }
        _append_progress(progress_path, event)

    return report_progress


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--chronicle", type=Path, default=DEFAULT_CHRONICLE)
    parser.add_argument("--scientific-harness", type=Path, default=DEFAULT_SCIENTIFIC_HARNESS)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--checkpoint", required=True, type=int)
    parser.add_argument("--dataset-start", type=int, default=0)
    parser.add_argument("--dataset-stop", type=int)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--git-commit",
        default=os.environ.get("GITHUB_SHA", "local-non-git-fixture"),
        help="Commit identity bound into the chunk manifest.",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Non-production plumbing fixture. It cannot authorize or satisfy the coverage gate.",
    )
    args = parser.parse_args()

    if args.workers <= 0:
        raise ValueError("workers must be positive")
    contract = load_coverage_contract(
        args.contract,
        require_execution_authorized=not args.smoke,
    )
    if not args.smoke:
        assert_execution_unblocked(
            args.chronicle,
            args.scientific_harness,
            DECOMPOSED_PRODUCTION_GATE,
        )
        checkpoints = [int(value) for value in contract["simulation_precision"]["dataset_checkpoints"]]
        if args.checkpoint not in checkpoints:
            raise ValueError("checkpoint is not present in the frozen production contract")

    scenarios = scenarios_from_contract(contract)
    scenario_names = [scenario.name for scenario in scenarios]
    if args.scenario not in scenario_names:
        raise ValueError(f"unknown coverage scenario: {args.scenario}")
    scenario_index_zero = scenario_names.index(args.scenario)
    scenario_index = scenario_index_zero + 1
    scenario = scenarios[scenario_index_zero]

    root_seed = int(contract["root_seed"])
    scenario_seeds = spawn_scenario_seed_sequences(root_seed, len(scenarios))
    scenario_seed = scenario_seeds[scenario_index_zero]
    dataset_stop = args.checkpoint if args.dataset_stop is None else int(args.dataset_stop)
    bootstrap_replicates = (
        10 if args.smoke else int(contract["bootstrap"]["replicates_per_simulated_dataset"])
    )
    engine = str(contract["execution"]["engine"])

    args.output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = args.output_dir / "progress.jsonl"
    if progress_path.exists():
        progress_path.unlink()
    started = time.monotonic()
    _append_progress(
        progress_path,
        {
            "event": "scenario_chunk_started",
            "scenario": scenario.name,
            "checkpoint": args.checkpoint,
            "dataset_start": args.dataset_start,
            "dataset_stop": dataset_stop,
            "datasets_total": dataset_stop - args.dataset_start,
            "runtime_observability_only": True,
        },
    )
    progress_callback = _make_progress_callback(
        progress_path=progress_path,
        scenario_name=scenario.name,
        checkpoint=args.checkpoint,
        dataset_start=args.dataset_start,
        dataset_stop=dataset_stop,
        started=started,
    )
    outcomes = run_coverage_scenario_range(
        scenario,
        checkpoint=args.checkpoint,
        bootstrap_replicates=bootstrap_replicates,
        scenario_seed=scenario_seed,
        dataset_start=args.dataset_start,
        dataset_stop=dataset_stop,
        workers=args.workers,
        engine=engine,  # type: ignore[arg-type]
        progress_callback=progress_callback,
    )
    elapsed = time.monotonic() - started
    _append_progress(
        progress_path,
        {
            "event": "scenario_chunk_complete",
            "scenario": scenario.name,
            "checkpoint": args.checkpoint,
            "dataset_start": args.dataset_start,
            "dataset_stop": dataset_stop,
            "datasets_completed": len(outcomes),
            "elapsed_seconds": round(elapsed, 3),
            "runtime_observability_only": True,
        },
    )

    metadata = {
        "runner": "scripts/run_subject_bootstrap_coverage_scenario.py",
        "repository": REPOSITORY,
        "git_commit": args.git_commit,
        "scenario": scenario.name,
        "scenario_index": scenario_index,
        "scenario_count": len(scenarios),
        "checkpoint": args.checkpoint,
        "dataset_start": args.dataset_start,
        "dataset_stop": dataset_stop,
        "workers": args.workers,
        "execution_engine": engine,
        "reference_oracle_engine": contract["execution"]["reference_oracle_engine"],
        "bootstrap_replicates_per_dataset": bootstrap_replicates,
        "root_seed": root_seed,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "synthetic_nonproduction_fixture": args.smoke,
        "historical_study_0_scores_read": False,
        "historical_study_0_scores_permitted": False,
        "production_gate_claimed": False,
        "complete": True,
        "elapsed_seconds": round(elapsed, 3),
    }
    manifest_path = write_scenario_chunk_artifact(
        args.output_dir,
        outcomes=outcomes,
        progress_path=progress_path,
        execution_metadata=metadata,
        repository=REPOSITORY,
        git_commit=args.git_commit,
        contract_path=args.contract,
        contract=contract,
        scenario_name=scenario.name,
        scenario_index=scenario_index,
        scenario_count=len(scenarios),
        checkpoint=args.checkpoint,
        dataset_start=args.dataset_start,
        dataset_stop=dataset_stop,
        bootstrap_replicates=bootstrap_replicates,
        root_seed=root_seed,
        scenario_seed=scenario_seed,
        workers=args.workers,
        synthetic_nonproduction_fixture=args.smoke,
    )
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
