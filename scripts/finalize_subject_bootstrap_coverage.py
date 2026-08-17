"""Finalize the selected decomposed Study 0 coverage checkpoint exactly once."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

from siamese_compression_lab.coverage_simulation import coverage_gate_passes
from siamese_compression_lab.decomposed_coverage import (
    aggregate_checkpoint_artifacts,
    load_coverage_contract,
)

DEFAULT_CONTRACT = Path("protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml")


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("final coverage gate requires metric rows")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--artifact-dir", type=Path, action="append", required=True)
    parser.add_argument("--checkpoint", type=int, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    contract = load_coverage_contract(args.contract, require_execution_authorized=True)
    results, precision_decision = aggregate_checkpoint_artifacts(
        args.contract,
        args.artifact_dir,
        expected_commit=args.git_commit,
        checkpoint=args.checkpoint,
        require_execution_authorized=True,
    )
    checkpoints = [int(value) for value in contract["simulation_precision"]["dataset_checkpoints"]]
    last_checkpoint = checkpoints[-1]
    if not precision_decision["all_metric_mcse_lte_threshold"] and args.checkpoint != last_checkpoint:
        raise ValueError(
            "a non-final checkpoint cannot be finalized before the frozen MCSE stopping rule is met"
        )

    gate_pass = coverage_gate_passes(results)
    rows = [asdict(result) for result in results]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(args.output_dir / "coverage_simulation.csv", rows)
    gate = {
        "status": "PASS" if gate_pass else "FAIL",
        "selected_dataset_checkpoint": args.checkpoint,
        "bootstrap_replicates_per_dataset": int(
            contract["bootstrap"]["replicates_per_simulated_dataset"]
        ),
        "root_seed": int(contract["root_seed"]),
        "rng_derivation": "numpy_seedsequence_spawn",
        "arithmetic_seed_offsets_used": False,
        "execution_engine": contract["execution"]["engine"],
        "reference_oracle_engine": contract["execution"]["reference_oracle_engine"],
        "binomial_interval": contract["coverage_gate"]["binomial_interval"],
        "lower_bound_minimum": float(contract["coverage_gate"]["lower_bound_minimum"]),
        "maximum_monte_carlo_standard_error": float(
            contract["simulation_precision"]["maximum_monte_carlo_standard_error"]
        ),
        "metric_gate_is_separate_by_scenario_and_metric": True,
        "pooled_coverage_gate_used": False,
        "degenerate_dataset_tolerance": int(
            contract["coverage_gate"]["degenerate_dataset_tolerance"]
        ),
        "historical_study_0_scores_read": False,
        "production_coverage_gate_executed": True,
    }
    (args.output_dir / "coverage_gate.json").write_text(
        json.dumps(gate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(gate, indent=2, sort_keys=True))
    return 0 if gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
