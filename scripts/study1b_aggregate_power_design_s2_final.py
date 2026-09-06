"""Aggregate the final non-outcome Study 1B S2 confirmation at the reference seed SD."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(root: Path, *, effect: float, sd: float) -> dict[int, dict]:
    rows: dict[int, dict] = {}
    for path in sorted(root.rglob("*.jsonl")):
        if path.name.endswith(".progress.jsonl"):
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("analysis_phase") != "S2_PROSPECTIVE_SEED_VARIABILITY_SWEEP":
                continue
            if float(row["effect_scenario"]) != effect:
                continue
            if float(row["sensitivity_seed_effect_sd"]) != sd:
                continue
            idx = int(row["dataset_index"])
            if idx in rows and rows[idx] != row:
                raise ValueError(f"conflicting duplicate for effect={effect} sd={sd} dataset={idx}")
            rows[idx] = row
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--expected", type=int, default=4000)
    parser.add_argument("--seed-effect-sd", type=float, default=0.005)
    parser.add_argument("--power-target", type=float, default=0.90)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cells = []
    complete = True
    candidate_pass = True
    for effect in (0.0, 0.01):
        rows = _load(args.input_root, effect=effect, sd=args.seed_effect_sd)
        if len(rows) != args.expected:
            complete = False
        counts = [sum(bool(seed["passes"]) for seed in rows[idx]["seeds"]) for idx in sorted(rows)]
        rates = {}
        for minimum, label in ((5, "all_5_of_5"), (4, "at_least_4_of_5"), (3, "at_least_3_of_5")):
            rate = sum(count >= minimum for count in counts) / len(counts) if counts else 0.0
            rates[label] = {
                "estimated_power": rate,
                "passes_0_90_target": rate >= args.power_target,
            }
        candidate_ok = rates["at_least_3_of_5"]["passes_0_90_target"]
        candidate_pass = candidate_pass and candidate_ok
        cells.append({
            "effect_scenario": effect,
            "seed_effect_sd": args.seed_effect_sd,
            "datasets": len(counts),
            "expected_datasets": args.expected,
            "complete": len(counts) == args.expected,
            "decision_rules": rates,
        })

    summary = {
        "schema_version": 1,
        "kind": "study1b_power_design_s2_final_reference_sd_confirmation",
        "analysis_phase": "S2_FINAL_REFERENCE_SD_CONFIRMATION",
        "scientific_outcomes_opened": False,
        "canonical_gate_replaced": False,
        "candidate_rule": "at_least_3_of_5",
        "seed_effect_sd": args.seed_effect_sd,
        "required_power_each_scenario": args.power_target,
        "complete": complete,
        "candidate_rule_passes_both_scenarios": complete and candidate_pass,
        "cells": cells,
        "interpretation": (
            "Final synthetic confirmation of the sole simple k-of-five rule surviving the S2 pilot "
            "at the original reference seed-effect SD. This result cannot activate the amendment, "
            "open real outcomes, or replace the canonical failed 5-of-5 gate."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
