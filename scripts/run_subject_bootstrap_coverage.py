"""Run coverage simulations without reading historical Study 0 scores."""

from __future__ import annotations

import argparse
import csv
import json
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

    for checkpoint in checkpoints:
        checkpoint_rows: list[dict] = []
        for scenario, scenario_seed in zip(scenarios, scenario_seeds):
            results = run_coverage_scenario_seedsequence(
                scenario,
                simulated_datasets=checkpoint,
                bootstrap_replicates=bootstrap_replicates,
                scenario_seed=scenario_seed,
                workers=args.workers,
                engine=engine,  # type: ignore[arg-type]
            )
            checkpoint_rows.extend(asdict(result) for result in results)
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

    args.output_dir.mkdir(parents=True, exist_ok=True)
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
