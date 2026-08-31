"""Post-failure, non-outcome Study 1B power design diagnostic.

Consumes canonical synthetic power JSONL rows and reports alternative k-of-five
rates and seed-level diagnostics. It never changes or replaces the preregistered
power gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def _load_rows(root: Path, effect: float) -> list[dict]:
    rows: dict[int, dict] = {}
    for path in sorted(root.rglob("*.jsonl")):
        if path.name.endswith(".progress.jsonl"):
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("mode") != "power":
                continue
            if abs(float(row.get("effect_scenario")) - effect) > 1e-12:
                continue
            idx = int(row["dataset_index"])
            if idx in rows and rows[idx] != row:
                raise ValueError(f"conflicting duplicate dataset_index={idx}")
            rows[idx] = row
    return [rows[idx] for idx in sorted(rows)]


def _quantiles(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    return {
        "q025": float(np.quantile(arr, 0.025)),
        "q25": float(np.quantile(arr, 0.25)),
        "median": float(np.quantile(arr, 0.5)),
        "q75": float(np.quantile(arr, 0.75)),
        "q975": float(np.quantile(arr, 0.975)),
    }


def summarize(rows: list[dict], effect: float) -> dict:
    if not rows:
        raise ValueError("no power rows found")
    seed_labels = [int(item["seed_label"]) for item in rows[0]["seeds"]]
    per_seed = {seed: [] for seed in seed_labels}
    seed_effects = {seed: [] for seed in seed_labels}
    pass_matrix = []
    max_ucb = []
    max_seed_effect = []

    for row in rows:
        seeds = row["seeds"]
        labels = [int(item["seed_label"]) for item in seeds]
        if labels != seed_labels:
            raise ValueError("inconsistent seed labels/order")
        flags = [bool(item["passes"]) for item in seeds]
        pass_matrix.append(flags)
        for item in seeds:
            seed = int(item["seed_label"])
            per_seed[seed].append(bool(item["passes"]))
            seed_effects[seed].append(float(item["seed_effect"]))
        max_ucb.append(max(float(item["ucb_97_5"]) for item in seeds))
        max_seed_effect.append(max(float(item["seed_effect"]) for item in seeds))

    matrix = np.asarray(pass_matrix, dtype=bool)
    counts = matrix.sum(axis=1)
    corr = np.corrcoef(matrix.astype(float), rowvar=False)

    return {
        "kind": "study1b_post_failure_power_design_diagnostic",
        "effect_scenario": effect,
        "datasets": len(rows),
        "scientific_outcomes_opened": False,
        "canonical_gate_replaced": False,
        "per_seed_pass_probability": {
            str(seed): float(np.mean(per_seed[seed])) for seed in seed_labels
        },
        "decision_rate": {
            "all_5_of_5": float(np.mean(counts >= 5)),
            "at_least_4_of_5": float(np.mean(counts >= 4)),
            "at_least_3_of_5": float(np.mean(counts >= 3)),
        },
        "max_ucb_97_5_quantiles": _quantiles(max_ucb),
        "max_positive_seed_effect_quantiles": _quantiles(max_seed_effect),
        "seed_effect_quantiles": {
            str(seed): _quantiles(seed_effects[seed]) for seed in seed_labels
        },
        "pairwise_seed_pass_indicator_correlation": {
            str(seed_labels[i]): {
                str(seed_labels[j]): float(corr[i, j])
                for j in range(len(seed_labels))
            }
            for i in range(len(seed_labels))
        },
        "interpretation": (
            "Post-failure design diagnostic only. Alternative k-of-five rates were not "
            "preregistered and must not be presented as Study 1B scientific outcomes."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--effect", type=float, required=True, choices=[0.0, 0.01])
    parser.add_argument("--expected", type=int, default=4000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = _load_rows(args.input_root, args.effect)
    if len(rows) != args.expected:
        raise ValueError(f"expected {args.expected} rows, found {len(rows)}")
    summary = summarize(rows, args.effect)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
