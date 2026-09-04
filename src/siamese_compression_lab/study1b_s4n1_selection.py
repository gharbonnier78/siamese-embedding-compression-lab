"""S4N1 non-outcome artifact-selection and known-truth calibration primitives.

This module never reads Study 1B biometric route outcomes. It operates only on frozen pair-graph
metadata plus synthetic distances generated from prospectively frozen known-truth parameters.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Mapping, Sequence

import numpy as np
from scipy.stats import binomtest

from .coverage_simulation import CoverageScenario, scenario_truth
from .study1b_bootstrap_vectorized import subject_bootstrap_summary_vectorized
from .study1b_execution import seed_token
from .study1b_simulation import (
    _power_candidate_from_shared_reference,
    _power_shared_reference_latent,
)
from .subject_bootstrap import (
    SubjectPairRow,
    weighted_rates_at_threshold,
    weighted_threshold_at_fmr,
)

SEED_LABELS: tuple[int, ...] = (11, 29, 47, 71, 101)
RULE_FIXED = "S4N_FIXED_SEED"
RULE_BEST = "S4N_VALIDATION_BEST"
RULE_MEDIAN = "S4N_VALIDATION_MEDIAN"
SELECTION_RULES: tuple[str, ...] = (RULE_FIXED, RULE_BEST, RULE_MEDIAN)


def equal_fmr_delta_point(
    rows: Sequence[SubjectPairRow],
    candidate_distances: np.ndarray,
    reference_distances: np.ndarray,
    *,
    target_fmr: float = 0.01,
) -> float:
    """Deterministic unbootstrapped paired equal-FMR Delta_FNMR point estimate."""
    if not rows:
        raise ValueError("selection metric requires a non-empty graph")
    candidate = np.asarray(candidate_distances, dtype=np.float64)
    reference = np.asarray(reference_distances, dtype=np.float64)
    if not (len(rows) == len(candidate) == len(reference)):
        raise ValueError("rows/candidate/reference must align one-to-one")
    if not (np.all(np.isfinite(candidate)) and np.all(np.isfinite(reference))):
        raise ValueError("selection metric requires finite distances")
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    weights = np.ones(len(rows), dtype=np.int64)
    candidate_threshold = weighted_threshold_at_fmr(same, candidate, weights, target_fmr)
    reference_threshold = weighted_threshold_at_fmr(same, reference, weights, target_fmr)
    candidate_rates = weighted_rates_at_threshold(
        same, candidate, weights, candidate_threshold
    )
    reference_rates = weighted_rates_at_threshold(
        same, reference, weights, reference_threshold
    )
    return float(candidate_rates.fnmr - reference_rates.fnmr)


def select_seed(
    rule: str,
    scores: Mapping[int, float],
    *,
    seed_labels: Sequence[int] = SEED_LABELS,
) -> int:
    """Apply one frozen S4N1 seed-selection rule with exact deterministic tie-breaking."""
    labels = tuple(int(seed) for seed in seed_labels)
    if labels != SEED_LABELS:
        raise ValueError("S4N1 requires the frozen five seed labels")
    if rule == RULE_FIXED:
        return 11
    if rule not in {RULE_BEST, RULE_MEDIAN}:
        raise ValueError(f"unknown S4N1 selection rule: {rule}")
    if set(scores) != set(labels):
        raise ValueError("validation selection requires exactly the five frozen seed scores")
    values = {seed: float(scores[seed]) for seed in labels}
    if not all(np.isfinite(value) for value in values.values()):
        raise ValueError("validation selection fails closed on a non-finite seed score")
    order = {seed: index for index, seed in enumerate(labels)}
    ranked = sorted(labels, key=lambda seed: (values[seed], order[seed]))
    return ranked[0] if rule == RULE_BEST else ranked[2]


def _scenario(
    *,
    name: str,
    target_delta: float,
    rows: Sequence[SubjectPairRow],
) -> CoverageScenario:
    subjects = {
        subject
        for row in rows
        for subject in (row.subject_slot_id_1, row.subject_slot_id_2)
    }
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    return CoverageScenario(
        name=name,
        target_delta_fnmr=float(target_delta),
        n_subjects=len(subjects),
        n_genuine=int(np.sum(same == 1)),
        n_impostor=int(np.sum(same == 0)),
        target_fmr=0.01,
        subject_effect_sd_genuine=0.08,
        subject_effect_sd_impostor=0.05,
        candidate_reference_noise_correlation=0.7,
    )


def _truncated_effects(
    *,
    label: str,
    dataset_index: int,
    sd: float,
    low: float = -0.02,
    high: float = 0.02,
) -> np.ndarray:
    rng = np.random.default_rng(seed_token(f"s4n1|{label}|dataset={dataset_index}|effects"))
    return np.clip(rng.normal(0.0, sd, len(SEED_LABELS)), low, high)


def _role_distances(
    rows: list[SubjectPairRow],
    *,
    role_label: str,
    dataset_index: int,
    deltas_by_seed: Mapping[int, float],
) -> tuple[np.ndarray, dict[int, np.ndarray], dict[int, float]]:
    """Generate one shared raw reference plus five synthetic candidate artifacts for one role."""
    first_delta = float(next(iter(deltas_by_seed.values())))
    base = _scenario(
        name=f"s4n1_{role_label}_dataset_{dataset_index}",
        target_delta=first_delta,
        rows=rows,
    )
    reference, latent = _power_shared_reference_latent(
        base, rows, dataset_index=dataset_index
    )
    candidates: dict[int, np.ndarray] = {}
    truths: dict[int, float] = {}
    for seed in SEED_LABELS:
        delta = float(deltas_by_seed[seed])
        scenario = CoverageScenario(
            **{
                **asdict(base),
                "name": f"s4n1_{role_label}_dataset_{dataset_index}_seed_{seed}",
                "target_delta_fnmr": delta,
            }
        )
        truths[seed] = float(scenario_truth(scenario).delta_fnmr)
        candidates[seed] = _power_candidate_from_shared_reference(
            scenario,
            rows,
            latent,
            dataset_index=dataset_index,
            seed_label=seed,
        )
    return reference, candidates, truths


def _point_scores(
    rows: list[SubjectPairRow],
    reference: np.ndarray,
    candidates: Mapping[int, np.ndarray],
) -> dict[int, float]:
    return {
        seed: equal_fmr_delta_point(rows, candidates[seed], reference, target_fmr=0.01)
        for seed in SEED_LABELS
    }


def run_core_dataset(
    validation_rows: list[SubjectPairRow],
    test_rows: list[SubjectPairRow],
    *,
    dataset_index: int,
    test_truth_delta: float,
    bootstrap_replicates: int,
    validation_seed_effect_sd: float = 0.005,
) -> dict:
    """One core S4N1 known-truth dataset.

    Every seed artifact has the same declared TEST truth. VALIDATION has frozen synthetic
    seed variation so best/median selection can overfit finite development evidence without
    changing the primary artifact-level TEST truth.
    """
    validation_effects = _truncated_effects(
        label=f"core|truth={test_truth_delta}|validation",
        dataset_index=dataset_index,
        sd=validation_seed_effect_sd,
    )
    validation_deltas = {
        seed: float(test_truth_delta + effect)
        for seed, effect in zip(SEED_LABELS, validation_effects)
    }
    test_deltas = {seed: float(test_truth_delta) for seed in SEED_LABELS}

    validation_reference, validation_candidates, validation_truths = _role_distances(
        validation_rows,
        role_label=f"validation_core_truth_{test_truth_delta}",
        dataset_index=dataset_index,
        deltas_by_seed=validation_deltas,
    )
    test_reference, test_candidates, test_truths = _role_distances(
        test_rows,
        role_label=f"test_core_truth_{test_truth_delta}",
        dataset_index=dataset_index,
        deltas_by_seed=test_deltas,
    )
    scores = _point_scores(validation_rows, validation_reference, validation_candidates)
    test_points = _point_scores(test_rows, test_reference, test_candidates)

    selected = {rule: select_seed(rule, scores) for rule in SELECTION_RULES}
    summaries = {}
    for seed in sorted(set(selected.values())):
        summaries[seed] = subject_bootstrap_summary_vectorized(
            rows=test_rows,
            candidate_distances=test_candidates[seed],
            reference_distances=test_reference,
            target_fmr=0.01,
            replicates=bootstrap_replicates,
            seed=seed_token(
                f"s4n1|core|truth={test_truth_delta}|dataset={dataset_index}|"
                f"test-bootstrap|seed={seed}"
            ),
        )

    candidates_out = {}
    for rule in SELECTION_RULES:
        seed = selected[rule]
        summary = summaries[seed]
        truth = float(test_truths[seed])
        covered = bool(
            summary.status == "PASS_DEGENERACY_AUDIT"
            and summary.delta_fnmr_ci_low <= truth <= summary.delta_fnmr_ucb_97_5
        )
        candidates_out[rule] = {
            "selected_seed": seed,
            "validation_observed_score": float(scores[seed]),
            "validation_true_delta": float(validation_truths[seed]),
            "validation_optimism": float(scores[seed] - validation_truths[seed]),
            "test_true_delta": truth,
            "test_point_delta": float(test_points[seed]),
            "test_estimation_error": float(test_points[seed] - truth),
            "covered": covered,
            "passes_noninferiority": bool(
                summary.status == "PASS_DEGENERACY_AUDIT"
                and summary.delta_fnmr_ucb_97_5 <= 0.03
            ),
            "bootstrap": asdict(summary),
        }

    return {
        "dataset_index": int(dataset_index),
        "mode": "core",
        "scientific_outcomes_opened": False,
        "test_truth_delta": float(test_truth_delta),
        "validation_seed_effect_sd": float(validation_seed_effect_sd),
        "validation_scores": {str(k): float(v) for k, v in scores.items()},
        "validation_truths": {str(k): float(v) for k, v in validation_truths.items()},
        "test_truths": {str(k): float(v) for k, v in test_truths.items()},
        "candidates": candidates_out,
    }


def draw_cross_role_seed_effects(
    *,
    dataset_index: int,
    base_delta: float,
    seed_effect_sd: float,
    validation_test_correlation: float,
) -> tuple[dict[int, float], dict[int, float]]:
    """Draw the prospective bivariate VALIDATION/TEST latent seed-effect sensitivity."""
    rho = float(validation_test_correlation)
    if not 0.0 <= rho <= 1.0:
        raise ValueError("S4N1 transport correlation must lie in [0, 1]")
    rng = np.random.default_rng(
        seed_token(
            f"s4n1|transport|base={base_delta}|sd={seed_effect_sd}|rho={rho}|"
            f"dataset={dataset_index}|effects"
        )
    )
    if rho == 1.0:
        z_validation = rng.normal(size=len(SEED_LABELS))
        z_test = z_validation.copy()
    else:
        covariance = np.asarray([[1.0, rho], [rho, 1.0]], dtype=np.float64)
        z = rng.multivariate_normal(np.zeros(2), covariance, size=len(SEED_LABELS))
        z_validation, z_test = z[:, 0], z[:, 1]
    validation_effects = np.clip(seed_effect_sd * z_validation, -0.02, 0.02)
    test_effects = np.clip(seed_effect_sd * z_test, -0.02, 0.02)
    validation = {
        seed: float(base_delta + effect)
        for seed, effect in zip(SEED_LABELS, validation_effects)
    }
    test = {
        seed: float(base_delta + effect)
        for seed, effect in zip(SEED_LABELS, test_effects)
    }
    return validation, test


def run_transport_dataset(
    validation_rows: list[SubjectPairRow],
    test_rows: list[SubjectPairRow],
    *,
    dataset_index: int,
    base_delta: float,
    seed_effect_sd: float,
    validation_test_correlation: float,
) -> dict:
    """Secondary S4N1 transport sensitivity without TEST bootstrap inference."""
    validation_deltas, test_deltas = draw_cross_role_seed_effects(
        dataset_index=dataset_index,
        base_delta=base_delta,
        seed_effect_sd=seed_effect_sd,
        validation_test_correlation=validation_test_correlation,
    )
    validation_reference, validation_candidates, validation_truths = _role_distances(
        validation_rows,
        role_label=(
            f"validation_transport_base_{base_delta}_sd_{seed_effect_sd}_rho_"
            f"{validation_test_correlation}"
        ),
        dataset_index=dataset_index,
        deltas_by_seed=validation_deltas,
    )
    test_reference, test_candidates, test_truths = _role_distances(
        test_rows,
        role_label=(
            f"test_transport_base_{base_delta}_sd_{seed_effect_sd}_rho_"
            f"{validation_test_correlation}"
        ),
        dataset_index=dataset_index,
        deltas_by_seed=test_deltas,
    )
    scores = _point_scores(validation_rows, validation_reference, validation_candidates)
    test_points = _point_scores(test_rows, test_reference, test_candidates)
    true_test_values = np.asarray([test_truths[seed] for seed in SEED_LABELS], dtype=np.float64)
    true_best_seed = min(
        SEED_LABELS,
        key=lambda seed: (test_truths[seed], SEED_LABELS.index(seed)),
    )
    mean_truth = float(np.mean(true_test_values))
    min_truth = float(np.min(true_test_values))
    candidates_out = {}
    for rule in SELECTION_RULES:
        seed = select_seed(rule, scores)
        truth = float(test_truths[seed])
        candidates_out[rule] = {
            "selected_seed": seed,
            "validation_observed_score": float(scores[seed]),
            "validation_true_delta": float(validation_truths[seed]),
            "validation_optimism": float(scores[seed] - validation_truths[seed]),
            "test_true_delta": truth,
            "test_point_delta": float(test_points[seed]),
            "selected_is_true_test_best": bool(seed == true_best_seed),
            "selected_truth_minus_mean_truth": float(truth - mean_truth),
            "test_regret_vs_true_best": float(truth - min_truth),
        }
    return {
        "dataset_index": int(dataset_index),
        "mode": "transport",
        "scientific_outcomes_opened": False,
        "base_delta": float(base_delta),
        "seed_effect_sd": float(seed_effect_sd),
        "validation_test_correlation": float(validation_test_correlation),
        "validation_truths": {str(k): float(v) for k, v in validation_truths.items()},
        "test_truths": {str(k): float(v) for k, v in test_truths.items()},
        "candidates": candidates_out,
        "stability": {
            "test_truth_sd": float(np.std(true_test_values, ddof=0)),
            "test_truth_range": float(np.ptp(true_test_values)),
            "worst_seed_test_truth": float(np.max(true_test_values)),
        },
    }


def aggregate_core_candidate(
    rows: Sequence[dict],
    *,
    candidate: str,
    lower_coverage_bound_minimum: float = 0.93,
    power_minimum: float = 0.90,
) -> dict:
    """Aggregate one candidate within one exact core TEST-truth scenario."""
    if not rows:
        raise ValueError("S4N1 aggregate requires dataset rows")
    candidate_rows = [row["candidates"][candidate] for row in rows]
    covered = sum(bool(row["covered"]) for row in candidate_rows)
    total = len(candidate_rows)
    lower = float(
        binomtest(covered, total)
        .proportion_ci(confidence_level=0.95, method="exact")
        .low
    )
    requested = sum(int(row["bootstrap"]["requested_replicates"]) for row in candidate_rows)
    degenerate = sum(int(row["bootstrap"]["degenerate_replicates"]) for row in candidate_rows)
    degenerate_fraction = float(degenerate / requested) if requested else float("nan")
    passed_ni = sum(bool(row["passes_noninferiority"]) for row in candidate_rows)
    power = passed_ni / total
    return {
        "candidate": candidate,
        "simulated_datasets": total,
        "covered": covered,
        "empirical_coverage": covered / total,
        "lower_95_clopper_pearson": lower,
        "degenerate_fraction": degenerate_fraction,
        "coverage_pass": bool(
            lower >= lower_coverage_bound_minimum and degenerate_fraction <= 0.001
        ),
        "noninferiority_passes": passed_ni,
        "estimated_power": power,
        "power_pass": bool(power >= power_minimum),
        "mean_validation_optimism": float(
            np.mean([row["validation_optimism"] for row in candidate_rows])
        ),
        "mean_test_estimation_error": float(
            np.mean([row["test_estimation_error"] for row in candidate_rows])
        ),
    }
