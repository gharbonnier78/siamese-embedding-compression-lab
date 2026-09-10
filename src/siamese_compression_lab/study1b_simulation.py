"""Synthetic known-truth coverage/power simulation on a frozen Study 1B pair graph."""

from __future__ import annotations

import csv
import hashlib
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

from .coverage_simulation import CoverageScenario, scenario_truth, simulate_distances
from .study1b_bootstrap_vectorized import subject_bootstrap_summary_vectorized
from .study1b_execution import seed_token
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
    summary = subject_bootstrap_summary_vectorized(
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


def _array_sha256(values: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(values, dtype=np.float64).tobytes(order="C")).hexdigest()


def _power_shared_reference_latent(
    scenario: CoverageScenario,
    rows: list[SubjectPairRow],
    *,
    dataset_index: int,
) -> tuple[np.ndarray, dict]:
    """Generate one raw/reference realization shared by every candidate model seed.

    The reference subject effects and pair noise are drawn once per simulated dataset. Candidate
    seeds receive independent conditional residual pair noise while retaining the frozen marginal
    candidate/reference correlation. This matches the Study 1B all-five-seed question: five model
    seeds are compared against the same realized raw512 dataset, not five different raw worlds.
    """
    rho = float(scenario.candidate_reference_noise_correlation)
    if not -0.95 < rho < 0.95:
        raise ValueError("candidate/reference noise correlation must lie strictly inside (-0.95, 0.95)")
    rng = np.random.default_rng(
        seed_token(f"power|{scenario.name}|dataset={dataset_index}|shared-reference")
    )
    subjects = sorted(
        {
            subject
            for row in rows
            for subject in (row.subject_slot_id_1, row.subject_slot_id_2)
        }
    )
    subject_index = {subject: position for position, subject in enumerate(subjects)}
    genuine_effect = rng.normal(0.0, scenario.subject_effect_sd_genuine, len(subjects))
    impostor_effect = rng.normal(0.0, scenario.subject_effect_sd_impostor, len(subjects))
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    genuine_indices = np.flatnonzero(same == 1)
    impostor_indices = np.flatnonzero(same == 0)
    ref_g_noise = rng.normal(0.0, scenario.pair_noise_sd_genuine, len(genuine_indices))
    ref_i_noise = rng.normal(0.0, scenario.pair_noise_sd_impostor, len(impostor_indices))

    reference = np.empty(len(rows), dtype=np.float64)
    for offset, row_index in enumerate(genuine_indices):
        row = rows[row_index]
        effect = genuine_effect[subject_index[row.subject_slot_id_1]]
        reference[row_index] = scenario.reference_genuine_mean + effect + ref_g_noise[offset]
    for offset, row_index in enumerate(impostor_indices):
        row = rows[row_index]
        effect = (
            impostor_effect[subject_index[row.subject_slot_id_1]]
            + impostor_effect[subject_index[row.subject_slot_id_2]]
        )
        reference[row_index] = scenario.impostor_mean + effect + ref_i_noise[offset]

    latent = {
        "subjects": subjects,
        "subject_index": subject_index,
        "genuine_effect": genuine_effect,
        "impostor_effect": impostor_effect,
        "genuine_indices": genuine_indices,
        "impostor_indices": impostor_indices,
        "ref_g_noise": ref_g_noise,
        "ref_i_noise": ref_i_noise,
    }
    return reference, latent


def _power_candidate_from_shared_reference(
    scenario: CoverageScenario,
    rows: list[SubjectPairRow],
    latent: dict,
    *,
    dataset_index: int,
    seed_label: int,
) -> np.ndarray:
    truth = scenario_truth(scenario)
    genuine_sd = float(
        np.sqrt(scenario.pair_noise_sd_genuine**2 + scenario.subject_effect_sd_genuine**2)
    )
    from scipy.stats import norm

    candidate_genuine_mean = float(
        truth.candidate_threshold - genuine_sd * norm.ppf(1.0 - truth.candidate_fnmr)
    )
    rho = float(scenario.candidate_reference_noise_correlation)
    residual_scale = float(np.sqrt(1.0 - rho**2))
    rng = np.random.default_rng(
        seed_token(
            f"power|{scenario.name}|dataset={dataset_index}|seed={seed_label}|candidate-residual"
        )
    )
    cand_g_residual = rng.normal(
        0.0, scenario.pair_noise_sd_genuine, len(latent["genuine_indices"])
    )
    cand_i_residual = rng.normal(
        0.0, scenario.pair_noise_sd_impostor, len(latent["impostor_indices"])
    )
    cand_g_noise = rho * latent["ref_g_noise"] + residual_scale * cand_g_residual
    cand_i_noise = rho * latent["ref_i_noise"] + residual_scale * cand_i_residual

    candidate = np.empty(len(rows), dtype=np.float64)
    for offset, row_index in enumerate(latent["genuine_indices"]):
        row = rows[row_index]
        effect = latent["genuine_effect"][latent["subject_index"][row.subject_slot_id_1]]
        candidate[row_index] = candidate_genuine_mean + effect + cand_g_noise[offset]
    for offset, row_index in enumerate(latent["impostor_indices"]):
        row = rows[row_index]
        effect = (
            latent["impostor_effect"][latent["subject_index"][row.subject_slot_id_1]]
            + latent["impostor_effect"][latent["subject_index"][row.subject_slot_id_2]]
        )
        candidate[row_index] = scenario.impostor_mean + effect + cand_i_noise[offset]
    return candidate


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
    reference, latent = _power_shared_reference_latent(
        base_scenario, rows, dataset_index=dataset_index
    )
    reference_hash = _array_sha256(reference)
    seed_rows = []
    all_pass = True
    for seed_label, effect in zip(seed_labels, effects):
        delta = float(base_scenario.target_delta_fnmr + effect)
        scenario = CoverageScenario(
            **{
                **asdict(base_scenario),
                "name": f"{base_scenario.name}_seed_{seed_label}",
                "target_delta_fnmr": delta,
            }
        )
        bootstrap_seed = seed_token(
            f"power|{base_scenario.name}|dataset={dataset_index}|seed={seed_label}|bootstrap"
        )
        candidate = _power_candidate_from_shared_reference(
            scenario,
            rows,
            latent,
            dataset_index=dataset_index,
            seed_label=seed_label,
        )
        summary = subject_bootstrap_summary_vectorized(
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
                "reference_sha256": reference_hash,
                "candidate_sha256": _array_sha256(candidate),
            }
        )
    if {row["reference_sha256"] for row in seed_rows} != {reference_hash}:
        raise RuntimeError("power simulation violated shared-reference invariant")
    return {
        "dataset_index": dataset_index,
        "effect_scenario": base_scenario.target_delta_fnmr,
        "shared_reference": True,
        "reference_sha256": reference_hash,
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
