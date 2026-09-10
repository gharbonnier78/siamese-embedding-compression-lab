"""Run one prospective non-outcome Study 1B S2 seed-variability power shard."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import yaml

from siamese_compression_lab.study1b_simulation import (
    load_subject_graph,
    run_power_dataset,
    scenario_for_graph,
)


def _append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _completed(path: Path) -> set[int]:
    if not path.is_file():
        return set()
    return {
        int(json.loads(line)["dataset_index"])
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--test-graph", type=Path, required=True)
    parser.add_argument("--effect", type=float, required=True)
    parser.add_argument("--seed-effect-sd", type=float, required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--stop", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    contract = yaml.safe_load(args.contract.read_text(encoding="utf-8"))
    if contract.get("status") != "NONOUTCOME_DESIGN_ANALYSIS_AUTHORIZED":
        raise PermissionError("S2 sensitivity contract is not authorized")
    if contract.get("scientific_outcomes_permitted") is not False:
        raise PermissionError("S2 contract must prohibit scientific outcomes")
    if contract.get("replaces_canonical_power_gate") is not False:
        raise PermissionError("S2 may not replace the canonical power gate")

    s2 = contract["phase_S2_seed_variability_sweep"]
    allowed_effects = [float(v) for v in s2["true_delta_scenarios"]]
    allowed_sd = [float(v) for v in s2["seed_effect_sd_values"]]
    if args.effect not in allowed_effects:
        raise ValueError("effect is not predeclared in S2 contract")
    if args.seed_effect_sd not in allowed_sd:
        raise ValueError("seed-effect SD is not predeclared in S2 contract")
    if args.start < 0 or args.stop <= args.start:
        raise ValueError("invalid shard range")
    if args.stop > int(s2["pilot_datasets_per_cell"]):
        raise ValueError("S2 pilot shard exceeds predeclared pilot budget")

    rows = load_subject_graph(args.test_graph)
    scenario = scenario_for_graph(
        f"s2_power_delta_{args.effect:g}_sd_{args.seed_effect_sd:g}",
        args.effect,
        rows,
        subject_effect_sd_genuine=0.08,
        subject_effect_sd_impostor=0.05,
        candidate_reference_noise_correlation=0.7,
    )
    bootstrap_replicates = int(s2["bootstrap_replicates_per_dataset"])

    completed = _completed(args.output)
    progress = args.output.with_suffix(args.output.suffix + ".progress.jsonl")
    shard_started = time.perf_counter()
    for dataset_index in range(args.start, args.stop):
        if dataset_index in completed:
            _append_jsonl(progress, {"event": "resume_skip", "dataset_index": dataset_index})
            continue
        started = time.perf_counter()
        result = run_power_dataset(
            scenario,
            rows,
            dataset_index=dataset_index,
            bootstrap_replicates=bootstrap_replicates,
            seed_effect_sd=args.seed_effect_sd,
        )
        result.update(
            {
                "analysis_phase": "S2_PROSPECTIVE_SEED_VARIABILITY_SWEEP",
                "effect_scenario": args.effect,
                "sensitivity_seed_effect_sd": args.seed_effect_sd,
                "bootstrap_replicates": bootstrap_replicates,
                "scientific_outcomes_opened": False,
                "canonical_gate_replaced": False,
                "wall_seconds": time.perf_counter() - started,
            }
        )
        _append_jsonl(args.output, result)
        done = dataset_index - args.start + 1
        rate = done / max(time.perf_counter() - shard_started, 1e-9)
        _append_jsonl(
            progress,
            {
                "event": "dataset_completed",
                "dataset_index": dataset_index,
                "completed_in_shard": done,
                "total_in_shard": args.stop - args.start,
                "datasets_per_second": rate,
            },
        )
        print(
            f"[S2] sd={args.seed_effect_sd:g} delta={args.effect:g} "
            f"{done}/{args.stop - args.start} dataset={dataset_index} rate={rate:.4f}/s",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
