"""Run coverage simulations without reading historical Study 0 scores."""

from __future__ import annotations

import argparse
import csv
import json
import time
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path

import yaml

from siamese_compression_lab.coverage_execution import (
    run_coverage_scenario_seedsequence,
    spawn_scenario_seed_sequences,
)
from siamese_compression_lab.coverage_simulation import (
    CoverageResult,
    CoverageScenario,
    coverage_gate_passes,
)
from siamese_compression_lab.scientific_harness import assert_execution_unblocked

PROGRESS_EVERY_DATASETS = 25


def _load_contract(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("coverage contract must be a YAML mapping")
    if value.get("historical_study_0_scores_permitted") is not False:
        raise ValueError("coverage simulation contract must prohibit historical Study 0 scores")
    hierarchy = value.get("rng_hierarchy", {})
    if hierarchy.get("derivation") != "numpy_seedsequence_spawn":
        raise ValueError("coverage contract must require numpy SeedSequence.spawn hierarchy")
    if hierarchy.get("arithmetic_seed_offsets_forbidden") is not True:
        raise ValueError("coverage contract must forbid arithmetic seed offsets")
    execution = value.get("execution", {})
    if execution.get("engine") not in {"legacy", "vectorized"}:
        raise ValueError("coverage contract must select legacy or vectorized execution engine")
    if execution.get("reference_oracle_engine") != "legacy":
        raise ValueError("coverage contract must preserve legacy as the execution oracle")
    if execution.get("exact_dataset_outcome_equivalence_required") is not True:
        raise ValueError("coverage contract must require exact engine equivalence")
    if execution.get("implementation_only") is not True:
        raise ValueError("coverage engine selection must be implementation-only")
    return value


def _scenario_from_contract(contract: dict, item: dict) -> CoverageScenario:
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


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


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
    checkpoint: int,
    checkpoint_index: int,
    checkpoint_total: int,
    checkpoint_started: float,
    scenario_name: str,
    scenario_index: int,
    scenario_count: int,
    scenario_started: float,
) -> Callable[[int, int], None]:
    def report_progress(completed: int, total: int) -> None:
        if completed != total and completed % PROGRESS_EVERY_DATASETS != 0:
            return
        now = time.monotonic()
        scenario_elapsed = now - scenario_started
        checkpoint_elapsed = now - checkpoint_started
        checkpoint_completed = (scenario_index - 1) * checkpoint + completed
        scenario_eta = _runtime_estimate(total - completed, completed, scenario_elapsed)
        checkpoint_eta = _runtime_estimate(
            checkpoint_total - checkpoint_completed,
            checkpoint_completed,
            checkpoint_elapsed,
        )
        event = {
            "event": "dataset_progress",
            "checkpoint": checkpoint,
            "checkpoint_index": checkpoint_index,
            "scenario": scenario_name,
            "scenario_index": scenario_index,
            "scenario_count": scenario_count,
            "datasets_completed": completed,
            "datasets_total": total,
            "scenario_progress_percent": round(100.0 * completed / total, 3),
            "checkpoint_datasets_completed": checkpoint_completed,
            "checkpoint_datasets_total": checkpoint_total,
            "checkpoint_progress_percent": round(
                100.0 * checkpoint_completed / checkpoint_total, 3
            ),
            "scenario_elapsed_seconds": round(scenario_elapsed, 3),
            "checkpoint_elapsed_seconds": round(checkpoint_elapsed, 3),
            "scenario_throughput_datasets_per_minute": round(
                60.0 * completed / scenario_elapsed, 4
            )
            if scenario_elapsed > 0
            else None,
            "scenario_eta_seconds": round(scenario_eta, 3)
            if scenario_eta is not None
            else None,
            "checkpoint_eta_seconds": round(checkpoint_eta, 3)
            if checkpoint_eta is not None
            else None,
            "eta_is_runtime_estimate": True,
            "runtime_observability_only": True,
        }
        _append_progress(progress_path, event)

    return report_progress


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml"),
    )
    parser.add_argument(
        "--chronicle",
        type=Path,
        default=Path("protocol/scientific_chronicle.yaml"),
    )
    parser.add_argument(
        "--scientific-harness",
        type=Path,
        default=Path("gates/scientific_harness.yaml"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Independent dataset worker processes. Worker count must not change outputs.",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Use tiny counts to validate plumbing only; cannot satisfy the coverage gate.",
    )
    args = parser.parse_args()
    if args.workers <= 0:
        raise ValueError("workers must be positive")

    contract = _load_contract(args.contract)
    engine = str(contract["execution"]["engine"])
    if not args.smoke:
        assert_execution_unblocked(
            args.chronicle,
            args.scientific_harness,
            "production_coverage_gate",
        )

    root_seed = int(contract["root_seed"])
    if args.smoke:
        checkpoints = [2]
        bootstrap_replicates = 10
    else:
        checkpoints = [
            int(value)
            for value in contract["simulation_precision"]["dataset_checkpoints"]
        ]
        bootstrap_replicates = int(
            contract["bootstrap"]["replicates_per_simulated_dataset"]
        )

    scenarios = [
        _scenario_from_contract(contract, item) for item in contract["scenarios"]
    ]
    scenario_seeds = spawn_scenario_seed_sequences(root_seed, len(scenarios))
    final_rows: list[dict] = []
    selected_checkpoint: int | None = None
    progress_path = args.output_dir / "progress.jsonl"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if progress_path.exists():
        progress_path.unlink()

    for checkpoint_index, checkpoint in enumerate(checkpoints, start=1):
        checkpoint_rows: list[dict] = []
        checkpoint_started = time.monotonic()
        checkpoint_total = len(scenarios) * checkpoint
        _append_progress(
            progress_path,
            {
                "event": "checkpoint_started",
                "checkpoint": checkpoint,
                "checkpoint_index": checkpoint_index,
                "checkpoint_count": len(checkpoints),
                "scenario_count": len(scenarios),
                "datasets_total": checkpoint_total,
                "runtime_observability_only": True,
            },
        )

        for scenario_index, (scenario, scenario_seed) in enumerate(
            zip(scenarios, scenario_seeds), start=1
        ):
            scenario_started = time.monotonic()
            progress_callback = _make_progress_callback(
                progress_path=progress_path,
                checkpoint=checkpoint,
                checkpoint_index=checkpoint_index,
                checkpoint_total=checkpoint_total,
                checkpoint_started=checkpoint_started,
                scenario_name=scenario.name,
                scenario_index=scenario_index,
                scenario_count=len(scenarios),
                scenario_started=scenario_started,
            )
            results = run_coverage_scenario_seedsequence(
                scenario,
                simulated_datasets=checkpoint,
                bootstrap_replicates=bootstrap_replicates,
                scenario_seed=scenario_seed,
                workers=args.workers,
                engine=engine,  # type: ignore[arg-type]
                progress_callback=progress_callback,
            )
            checkpoint_rows.extend(asdict(result) for result in results)
            _append_progress(
                progress_path,
                {
                    "event": "scenario_complete",
                    "checkpoint": checkpoint,
                    "scenario": scenario.name,
                    "scenario_index": scenario_index,
                    "scenario_count": len(scenarios),
                    "datasets_completed": checkpoint,
                    "elapsed_seconds": round(time.monotonic() - scenario_started, 3),
                    "runtime_observability_only": True,
                },
            )

        final_rows = checkpoint_rows
        if args.smoke:
            selected_checkpoint = checkpoint
            break
        maximum_mcse = float(
            contract["simulation_precision"]["maximum_monte_carlo_standard_error"]
        )
        if all(
            float(row["monte_carlo_standard_error"]) <= maximum_mcse
            for row in checkpoint_rows
        ):
            selected_checkpoint = checkpoint
            break

    if selected_checkpoint is None:
        selected_checkpoint = checkpoints[-1]

    _write_csv(args.output_dir / "coverage_simulation.csv", final_rows)
    gate_pass = (not args.smoke) and coverage_gate_passes(
        [CoverageResult(**row) for row in final_rows]
    )
    gate = {
        "status": "PASS" if gate_pass else ("SMOKE_ONLY" if args.smoke else "FAIL"),
        "selected_dataset_checkpoint": selected_checkpoint,
        "bootstrap_replicates_per_dataset": bootstrap_replicates,
        "root_seed": root_seed,
        "rng_derivation": "numpy_seedsequence_spawn",
        "arithmetic_seed_offsets_used": False,
        "workers": args.workers,
        "execution_engine": engine,
        "reference_oracle_engine": contract["execution"]["reference_oracle_engine"],
        "binomial_interval": contract["coverage_gate"]["binomial_interval"],
        "lower_bound_minimum": contract["coverage_gate"]["lower_bound_minimum"],
        "maximum_monte_carlo_standard_error": contract["simulation_precision"][
            "maximum_monte_carlo_standard_error"
        ],
        "historical_study_0_scores_read": False,
    }
    (args.output_dir / "coverage_gate.json").write_text(
        json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(gate, indent=2, sort_keys=True))
    return 0 if args.smoke or gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
