"""Aggregate prospective non-outcome Study 1B S2 seed-variability sensitivity rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(root: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(root.rglob("*.jsonl")):
        if path.name.endswith(".progress.jsonl"):
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("analysis_phase") == "S2_PROSPECTIVE_SEED_VARIABILITY_SWEEP":
                    rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import yaml

    contract = yaml.safe_load(args.contract.read_text(encoding="utf-8"))
    s2 = contract["phase_S2_seed_variability_sweep"]
    expected = int(s2["pilot_datasets_per_cell"])
    screening_floor = 0.80
    selection_target = float(s2["power_target"])
    rules = {
        item["id"]: int(item["minimum_seed_passes"])
        for item in s2["decision_rules"]
    }

    grouped: dict[tuple[float, float], dict[int, dict]] = {}
    for row in _load(args.input_root):
        effect = float(row["effect_scenario"])
        sd = float(row["sensitivity_seed_effect_sd"])
        idx = int(row["dataset_index"])
        key = (effect, sd)
        bucket = grouped.setdefault(key, {})
        if idx in bucket and bucket[idx] != row:
            raise ValueError(f"conflicting duplicate for effect={effect} sd={sd} dataset={idx}")
        bucket[idx] = row

    cells = []
    overall_complete = True
    for sd in [float(v) for v in s2["seed_effect_sd_values"]]:
        for effect in [float(v) for v in s2["true_delta_scenarios"]]:
            rows_by_idx = grouped.get((effect, sd), {})
            if len(rows_by_idx) != expected:
                overall_complete = False
            counts = []
            for idx in sorted(rows_by_idx):
                seeds = rows_by_idx[idx]["seeds"]
                counts.append(sum(bool(item["passes"]) for item in seeds))
            decisions = {}
            for rule_id, minimum in rules.items():
                rate = sum(c >= minimum for c in counts) / len(counts) if counts else 0.0
                decisions[rule_id] = {
                    "estimated_power": rate,
                    "pilot_screening_survives": rate >= screening_floor,
                    "meets_final_selection_target_at_pilot_resolution": rate >= selection_target,
                }
            cells.append(
                {
                    "effect_scenario": effect,
                    "seed_effect_sd": sd,
                    "datasets": len(counts),
                    "expected_datasets": expected,
                    "complete": len(counts) == expected,
                    "decision_rules": decisions,
                }
            )

    summary = {
        "schema_version": 1,
        "kind": "study1b_power_design_s2_seed_variability_pilot",
        "analysis_phase": "S2_PROSPECTIVE_SEED_VARIABILITY_SWEEP",
        "scientific_outcomes_opened": False,
        "canonical_gate_replaced": False,
        "pilot_role": s2["pilot_role"],
        "pilot_screening_floor": screening_floor,
        "final_selection_power_target": selection_target,
        "complete": overall_complete,
        "cells": cells,
        "interpretation": (
            "Prospective synthetic design sensitivity only. Pilot rates screen candidate designs; "
            "they do not activate an amendment and do not replace the canonical failed power gate."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0 if overall_complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
