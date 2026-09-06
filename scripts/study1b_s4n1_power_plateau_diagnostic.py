#!/usr/bin/env python3
"""Diagnose archived S4N1 synthetic power without rerunning scientific simulation."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

CANDIDATES = (
    "S4N_FIXED_SEED",
    "S4N_VALIDATION_BEST",
    "S4N_VALIDATION_MEDIAN",
)
TRUTHS = (0.0, 0.01)
Z_975 = 1.959963984540054
MARGIN = 0.03


def _quantile(values: np.ndarray, q: float) -> float:
    return float(np.quantile(values, q, method="linear"))


def load_rows(root: Path) -> list[dict[str, Any]]:
    files = sorted(root.rglob("*.jsonl"))
    if not files:
        raise ValueError(f"no JSONL shard files found below {root}")
    rows: list[dict[str, Any]] = []
    for path in files:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    if row.get("scientific_outcomes_opened") is not False:
                        raise ValueError(f"outcome-bearing row refused: {path}")
                    if row.get("mode") != "core":
                        raise ValueError(f"non-core row refused: {path}")
                    rows.append(row)
    return rows


def validate_archived_population(rows: list[dict[str, Any]], expected_per_truth: int) -> None:
    by_truth: dict[float, list[int]] = defaultdict(list)
    for row in rows:
        truth = float(row["test_truth_delta"])
        if truth not in TRUTHS:
            raise ValueError(f"unexpected truth cell {truth}")
        if tuple(sorted(row["candidates"])) != tuple(sorted(CANDIDATES)):
            raise ValueError("candidate rule set differs from frozen S4N1 rules")
        by_truth[truth].append(int(row["dataset_index"]))
    for truth in TRUTHS:
        indices = sorted(by_truth[truth])
        expected = list(range(expected_per_truth))
        if indices != expected:
            raise ValueError(
                f"truth={truth}: require exact dataset indices 0..{expected_per_truth - 1}; "
                f"got {len(indices)} rows"
            )


def _candidate_arrays(
    rows: list[dict[str, Any]], truth: float, candidate: str
) -> dict[str, np.ndarray]:
    chosen = sorted(
        (row for row in rows if float(row["test_truth_delta"]) == truth),
        key=lambda row: int(row["dataset_index"]),
    )
    arrays: dict[str, list[float]] = defaultdict(list)
    arrays_bool: dict[str, list[bool]] = defaultdict(list)
    indices: list[int] = []
    for row in chosen:
        data = row["candidates"][candidate]
        boot = data["bootstrap"]
        indices.append(int(row["dataset_index"]))
        arrays["point"].append(float(data["test_point_delta"]))
        arrays["point_error"].append(float(data["test_estimation_error"]))
        arrays["bootstrap_mean"].append(float(boot["delta_fnmr_mean"]))
        arrays["ci_low"].append(float(boot["delta_fnmr_ci_low"]))
        arrays["ucb95"].append(float(boot["delta_fnmr_ucb_95"]))
        arrays["ucb975"].append(float(boot["delta_fnmr_ucb_97_5"]))
        arrays_bool["passed"].append(bool(data["passes_noninferiority"]))
        arrays_bool["covered"].append(bool(data["covered"]))
    out = {key: np.asarray(value, dtype=np.float64) for key, value in arrays.items()}
    out.update({key: np.asarray(value, dtype=bool) for key, value in arrays_bool.items()})
    out["dataset_index"] = np.asarray(indices, dtype=np.int64)
    return out


def _crossfit_oracle(arrays: dict[str, np.ndarray], truth: float) -> dict[str, float]:
    idx = arrays["dataset_index"]
    point = arrays["point"]
    error = arrays["point_error"]
    even = idx % 2 == 0
    odd = ~even
    if not np.any(even) or not np.any(odd):
        raise ValueError("crossfit requires both even and odd dataset indices")
    q_even = _quantile(error[even], 0.975)
    q_odd = _quantile(error[odd], 0.975)
    heldout_ucb = np.empty_like(point)
    heldout_ucb[odd] = point[odd] + q_even
    heldout_ucb[even] = point[even] + q_odd
    return {
        "calibration_q97_5_even_applied_to_odd": q_even,
        "calibration_q97_5_odd_applied_to_even": q_odd,
        "heldout_upper_coverage": float(np.mean(heldout_ucb >= truth)),
        "heldout_noninferiority_pass_fraction": float(np.mean(heldout_ucb <= MARGIN)),
    }


def summarize_cell(arrays: dict[str, np.ndarray], truth: float) -> dict[str, Any]:
    point = arrays["point"]
    error = arrays["point_error"]
    bmean = arrays["bootstrap_mean"]
    u95 = arrays["ucb95"]
    u975 = arrays["ucb975"]
    current_headroom = u975 - point
    boot_headroom = u975 - bmean
    u95_headroom = u95 - point
    external_sd = float(np.std(error, ddof=1))
    empirical_q975 = _quantile(error, 0.975)
    approx_boot_se = boot_headroom / Z_975
    median_approx_boot_se = float(np.median(approx_boot_se))
    se_ratio = median_approx_boot_se / external_sd if external_sd > 0 else float("nan")
    headroom_ratio = (
        float(np.median(boot_headroom)) / empirical_q975
        if empirical_q975 > 0
        else float("nan")
    )

    allowable_scale = (MARGIN - point) / current_headroom
    finite = allowable_scale[np.isfinite(allowable_scale)]
    # For 90% pass, k must not exceed the 10th percentile of per-row allowable scale.
    k90 = _quantile(finite, 0.10)
    info_multiplier = 1.0 / (k90 * k90) if 0.0 < k90 < 1.0 else 1.0

    return {
        "n": int(len(point)),
        "current_noninferiority_pass_fraction": float(np.mean(arrays["passed"])),
        "existing_two_sided_interval_coverage": float(np.mean(arrays["covered"])),
        "one_sided_upper_coverage_truth_lte_ucb97_5": float(np.mean(u975 >= truth)),
        "point_estimation_error": {
            "mean": float(np.mean(error)),
            "sd": external_sd,
            "q02_5": _quantile(error, 0.025),
            "q05": _quantile(error, 0.05),
            "q50": _quantile(error, 0.50),
            "q95": _quantile(error, 0.95),
            "q97_5": empirical_q975,
        },
        "bootstrap_mean_minus_point": {
            "mean": float(np.mean(bmean - point)),
            "sd": float(np.std(bmean - point, ddof=1)),
        },
        "ucb97_5_minus_point": {
            "mean": float(np.mean(current_headroom)),
            "median": float(np.median(current_headroom)),
            "p10": _quantile(current_headroom, 0.10),
            "p90": _quantile(current_headroom, 0.90),
        },
        "ucb97_5_minus_bootstrap_mean": {
            "mean": float(np.mean(boot_headroom)),
            "median": float(np.median(boot_headroom)),
            "p10": _quantile(boot_headroom, 0.10),
            "p90": _quantile(boot_headroom, 0.90),
        },
        "ucb95_minus_point": {
            "mean": float(np.mean(u95_headroom)),
            "median": float(np.median(u95_headroom)),
        },
        "empirical_repeated_sampling_q97_5_point_error": empirical_q975,
        "median_approx_bootstrap_upper_se": median_approx_boot_se,
        "bootstrap_se_to_repeated_sampling_sd_ratio": se_ratio,
        "ucb97_5_headroom_to_empirical_q97_5_error_ratio": headroom_ratio,
        "diagnostic_only_power_if_existing_ucb95_were_used": float(np.mean(u95 <= MARGIN)),
        "headroom_scale_needed_for_90_percent_pass_rate": k90,
        "square_root_information_multiplier_heuristic": info_multiplier,
        "crossfit_known_truth_oracle": _crossfit_oracle(arrays, truth),
    }


def diagnose(rows: list[dict[str, Any]], expected_per_truth: int) -> dict[str, Any]:
    validate_archived_population(rows, expected_per_truth)
    cells: dict[str, Any] = {}
    selector_ranges: dict[str, float] = {}
    for truth in TRUTHS:
        key = f"delta_{truth:.2f}".replace(".", "_")
        cells[key] = {}
        powers = []
        for candidate in CANDIDATES:
            summary = summarize_cell(_candidate_arrays(rows, truth, candidate), truth)
            cells[key][candidate] = summary
            powers.append(summary["current_noninferiority_pass_fraction"])
        selector_ranges[key] = float(max(powers) - min(powers))

    d001 = cells["delta_0_01"]
    point_bias_not_primary = all(
        abs(d001[candidate]["point_estimation_error"]["mean"]) <= 0.001
        for candidate in CANDIDATES
    )
    selector_not_primary = selector_ranges["delta_0_01"] <= 0.01
    conservatism_signal = all(
        d001[candidate]["one_sided_upper_coverage_truth_lte_ucb97_5"] >= 0.985
        and d001[candidate]["bootstrap_se_to_repeated_sampling_sd_ratio"] >= 1.15
        for candidate in CANDIDATES
    )
    return {
        "schema_version": 1,
        "kind": "study1b_s4n1_archived_power_plateau_diagnostic",
        "scientific_outcomes_opened": False,
        "screen_opened": False,
        "test_opened": False,
        "representation_geometry_opened": False,
        "amendment_activated": False,
        "s4n1_negative_result_reopened": False,
        "source_run_id": 33950949898,
        "expected_datasets_per_truth": expected_per_truth,
        "margin_delta_fnmr": MARGIN,
        "cells": cells,
        "selector_power_range": selector_ranges,
        "frozen_interpretation_tests": {
            "point_bias_not_primary": point_bias_not_primary,
            "selector_not_primary": selector_not_primary,
            "potential_ucb_spread_conservatism_signal": conservatism_signal,
        },
        "interpretation_boundary": (
            "Diagnostic only. Cross-fit known-truth oracle and UCB95 counterfactual are not "
            "admissible real-data estimators and cannot rescue S4N1."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--expected-per-truth", type=int, default=4000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = load_rows(args.input_root)
    result = diagnose(rows, args.expected_per_truth)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["frozen_interpretation_tests"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
