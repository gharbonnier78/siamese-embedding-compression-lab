"""Synthetic known-truth coverage/power simulation on a frozen Study 1B pair graph."""

from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

from .coverage_simulation import CoverageScenario, scenario_truth, simulate_distances
from .study1b_execution import seed_token
from .study1b_statistics import subject_bootstrap_summary
from .subject_bootstrap import SubjectPairRow


def load_subject_graph(path: Path) -> list[SubjectPairRow]:
    with path.open(newline="", encoding="utf-8") as handle:
        values = list(csv.DictReader(handle))
    rows = [
        SubjectPairRow(
            pair_id=row["pair_id"],
            same=int(row["same"]),
            subject_slot_id_1=row["subject_slot_id_1"],
            subject_slot_id_2=row["subject_slot_id_2"],
            source_class="study1b_frozen_graph",
            source_row=index,
        )
        for index, row in enumerate(values)
    ]
    if not rows:
        raise ValueError("simulation requires a non-empty frozen pair graph")
    return rows


def scenario_for_graph(
    name: str,
    target_delta_fnmr: float,
    rows: list[SubjectPairRow],
    *,
    subject_effect_sd_genuine: float,
    subject_effect_sd_impostor: float,
    candidate_reference_noise_correlation: float,
) -> CoverageScenario:
    subjects = {
        subject
        for row in rows
        for subject in (row.subject_slot_id_1, row.subject_slot_id_2)
    }
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    return CoverageScenario(
        name=name,
        target_delta_fnmr=target_delta_fnmr,
        n_subjects=len(subjects),
        n_genuine=int(np.sum(same == 1)),
        n_impostor=int(np.sum(same == 0)),
        target_fmr=0.01,
        subject_effect_sd_genuine=subject_effect_sd_genuine,
        subject_effect_sd_impostor=subject_effect_sd_impostor,
        candidate_reference_noise_correlation=candidate_reference_noise_correlation,
    )


def run_coverage_dataset(
    scenario: CoverageScenario,
    rows: list[SubjectPairRow],
    *,
    dataset_index: int,
    bootstrap_replicates: int,
) -> dict:
    distance_seed = seed_token(f"coverage|{scenario.name}|dataset={dataset_index}|distances")
    bootstrap_seed = seed_token(f"coverage|{scenario.name}|dataset={dataset_index}|bootstrap")
    candidate, reference = simulate_distances(scenario, rows, seed=distance_seed)
    summary = subject_bootstrap_summary(
        rows=rows,
        candidate_distances=candidate,
        reference_distances=reference,
        target_fmr=scenario.target_fmr,
        replicates=bootstrap_replicates,
        seed=bootstrap_seed,
    )
    truth = scenario_truth(scenario).delta_fnmr
    covered = bool(
        summary.status == "PASS_DEGENERACY_AUDIT"
        and summary.delta_fnmr_ci_low <= truth <= summary.delta_fnmr_ucb_97_5
    )
    return {
        "dataset_index": dataset_index,
        "scenario": scenario.name,
        "truth_delta_fnmr": truth,
        "covered": covered,
        **asdict(summary),
    }


def coverage_gate(rows: list[dict], lower_bound_minimum: float = 0.93) -> dict:
    if not rows:
        raise ValueError("coverage gate requires dataset rows")
    covered = sum(bool(row["covered"]) for row in rows)
    total = len(rows)
    lower = float(
        binomtest(covered, total).proportion_ci(confidence_level=0.95, method="exact").low
    )
    degenerate_fraction = float(
        sum(int(row["degenerate_replicates"]) for row in rows)
        / sum(int(row["requested_replicates"]) for row in rows)
    )
    return {
        "simulated_datasets": total,
        "covered": covered,
        "empirical_coverage": covered / total,
        "lower_95_clopper_pearson": lower,
        "degenerate_fraction": degenerate_fraction,
        "pass": lower >= lower_bound_minimum and degenerate_fraction <= 0.001,
    }


def _truncated_seed_effects(dataset_index: int, sd: float, low: float, high: float) -> np.ndarray:
    rng = np.random.default_rng(seed_token(f"power|dataset={dataset_index}|seed-effects"))
    values = rng.normal(0.0, sd, 5)
    return np.clip(values, low, high)


def run_power_dataset(
    base_scenario: CoverageScenario,
    rows: list[SubjectPairRow],
    *,
    dataset_index: int,
    bootstrap_replicates: int,
    seed_labels: tuple[int, ...] = (11, 29, 47, 71, 101),
    seed_effect_sd: float = 0.005,
) -> dict:
    if len(seed_labels) != 5:
        raise ValueError("frozen Study 1B power rule requires five seed labels")
    effects = _truncated_seed_effects(dataset_index, seed_effect_sd, -0.02, 0.02)
    seed_rows = []
    all_pass = True
    # Each model seed is simulated with its own candidate/reference noise stream. The common
    # graph and common truth regime preserve the study-level sampling structure; additive seed
    # effects make the all-five intersection rule explicit rather than pretending seeds vanish.
    for seed_label, effect in zip(seed_labels, effects):
        delta = float(base_scenario.target_delta_fnmr + effect)
        scenario = CoverageScenario(
            **{
                **asdict(base_scenario),
                "name": f"{base_scenario.name}_seed_{seed_label}",
                "target_delta_fnmr": delta,
            }
        )
        distance_seed = seed_token(
            f"power|{base_scenario.name}|dataset={dataset_index}|seed={seed_label}|distances"
        )
        bootstrap_seed = seed_token(
            f"power|{base_scenario.name}|dataset={dataset_index}|seed={seed_label}|bootstrap"
        )
        candidate, reference = simulate_distances(scenario, rows, seed=distance_seed)
        summary = subject_bootstrap_summary(
            rows=rows,
            candidate_distances=candidate,
            reference_distances=reference,
            target_fmr=0.01,
            replicates=bootstrap_replicates,
            seed=bootstrap_seed,
        )
        passes = bool(
            summary.status == "PASS_DEGENERACY_AUDIT"
            and summary.delta_fnmr_ucb_97_5 < 0.03
        )
        all_pass = all_pass and passes
        seed_rows.append(
            {
                "seed_label": seed_label,
                "seed_effect": float(effect),
                "true_seed_delta_fnmr": delta,
                "ucb_97_5": summary.delta_fnmr_ucb_97_5,
                "passes": passes,
                "degenerate_fraction": summary.degenerate_fraction,
            }
        )
    return {
        "dataset_index": dataset_index,
        "effect_scenario": base_scenario.target_delta_fnmr,
        "all_five_seeds_pass": all_pass,
        "seeds": seed_rows,
    }


def power_gate(rows: list[dict], required_probability: float = 0.90) -> dict:
    if not rows:
        raise ValueError("power gate requires simulated datasets")
    passed = sum(bool(row["all_five_seeds_pass"]) for row in rows)
    probability = passed / len(rows)
    return {
        "simulated_datasets": len(rows),
        "all_five_seed_passes": passed,
        "estimated_power": probability,
        "required_power": required_probability,
        "pass": probability >= required_probability,
    }
