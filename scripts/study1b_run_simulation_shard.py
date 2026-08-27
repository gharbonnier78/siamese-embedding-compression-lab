"""Run one resumable non-outcome Study 1B coverage/power simulation shard."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import yaml

from siamese_compression_lab.study1b_simulation import (
    load_subject_graph,
    run_coverage_dataset,
    run_power_dataset,
    scenario_for_graph,
)


def _atomic_jsonl_append(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _completed_indices(path: Path) -> set[int]:
    if not path.is_file():
        return set()
    output = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            output.add(int(json.loads(line)["dataset_index"]))
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--test-graph", type=Path, required=True)
    parser.add_argument("--mode", choices=["coverage", "power", "cost-pilot"], required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract = yaml.safe_load(args.contract.read_text(encoding="utf-8"))
    if contract.get("status") != "NONOUTCOME_EXECUTION_AUTHORIZED":
        raise PermissionError("simulation preflight contract is not authorized")
    if contract.get("scientific_outcomes_permitted") is not False:
        raise PermissionError("preflight contract must prohibit Study 1B outcomes")
    if args.start < 0 or args.stop <= args.start:
        raise ValueError("invalid dataset shard range")

    rows = load_subject_graph(args.test_graph)
    if args.mode == "coverage":
        item = next(
            value for value in contract["coverage"]["scenarios"] if value["name"] == args.scenario
        )
        bootstrap_replicates = int(contract["estimator"]["bootstrap_replicates"])
        scenario = scenario_for_graph(
            item["name"],
            float(item["target_delta_fnmr"]),
            rows,
            subject_effect_sd_genuine=float(item["subject_effect_sd_genuine"]),
            subject_effect_sd_impostor=float(item["subject_effect_sd_impostor"]),
            candidate_reference_noise_correlation=float(item["candidate_reference_noise_correlation"]),
        )
    elif args.mode == "power":
        delta = float(args.scenario)
        if delta not in [float(value) for value in contract["power"]["effect_scenarios"]]:
            raise ValueError("power scenario is not frozen in the contract")
        bootstrap_replicates = int(contract["estimator"]["bootstrap_replicates"])
        scenario = scenario_for_graph(
            f"power_delta_{delta:g}",
            delta,
            rows,
            subject_effect_sd_genuine=0.08,
            subject_effect_sd_impostor=0.05,
            candidate_reference_noise_correlation=0.7,
        )
    else:
        pilot = contract["execution"]["cost_pilot"]
        bootstrap_replicates = int(pilot["bootstrap_replicates"])
        item = contract["coverage"]["scenarios"][1]
        scenario = scenario_for_graph(
            "cost_pilot_subject_dependence_null",
            float(item["target_delta_fnmr"]),
            rows,
            subject_effect_sd_genuine=float(item["subject_effect_sd_genuine"]),
            subject_effect_sd_impostor=float(item["subject_effect_sd_impostor"]),
            candidate_reference_noise_correlation=float(item["candidate_reference_noise_correlation"]),
        )
        if args.stop - args.start > int(pilot["simulated_datasets"]):
            raise ValueError("cost pilot may not exceed its frozen non-gating dataset budget")

    completed = _completed_indices(args.output)
    progress = args.output.with_suffix(args.output.suffix + ".progress.jsonl")
    shard_started = time.perf_counter()
    for dataset_index in range(args.start, args.stop):
        if dataset_index in completed:
            _atomic_jsonl_append(
                progress,
                {"event": "resume_skip", "dataset_index": dataset_index, "mode": args.mode},
            )
            continue
        started = time.perf_counter()
        if args.mode == "power":
            result = run_power_dataset(
                scenario,
                rows,
                dataset_index=dataset_index,
                bootstrap_replicates=bootstrap_replicates,
                seed_effect_sd=float(contract["power"]["seed_effect_model"]["sd"]),
            )
        else:
            result = run_coverage_dataset(
                scenario,
                rows,
                dataset_index=dataset_index,
                bootstrap_replicates=bootstrap_replicates,
            )
        elapsed = time.perf_counter() - started
        result.update(
            {
                "mode": args.mode,
                "bootstrap_replicates": bootstrap_replicates,
                "wall_seconds": elapsed,
                "scientific_outcomes_opened": False,
            }
        )
        _atomic_jsonl_append(args.output, result)
        done = dataset_index - args.start + 1
        rate = done / max(time.perf_counter() - shard_started, 1e-9)
        _atomic_jsonl_append(
            progress,
            {
                "event": "dataset_completed",
                "dataset_index": dataset_index,
                "mode": args.mode,
                "wall_seconds": elapsed,
                "datasets_per_second": rate,
                "completed_in_shard": done,
                "total_in_shard": args.stop - args.start,
            },
        )
        print(
            f"[{args.mode}] {done}/{args.stop - args.start} dataset={dataset_index} "
            f"elapsed={elapsed:.2f}s rate={rate:.4f} datasets/s",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
