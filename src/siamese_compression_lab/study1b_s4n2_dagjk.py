"""Prospective non-outcome S4N2 identity delete-group jackknife calibration primitives."""
from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from scipy.stats import binomtest, t

from .study1b_s4n1_selection import (
    SEED_LABELS,
    SELECTION_RULES,
    _point_scores,
    _role_distances,
    select_seed,
)
from .subject_bootstrap import SubjectPairRow

GROUP_COUNT = 20
TARGET_FMR = 0.01
NI_MARGIN = 0.03
ONE_SIDED_LEVEL = 0.975
GROUP_NAMESPACE = "study1b-s4n2-dagjk20"


@dataclass(frozen=True)
class DagjkSummary:
    status: str
    point_delta: float
    jackknife_mean: float
    jackknife_variance: float
    standard_error: float
    critical_value: float
    ci_low: float
    ucb_97_5: float
    group_count: int
    group_size_min: int
    group_size_max: int
    min_remaining_genuine: int
    min_remaining_impostor: int


def identity_group_assignment(
    rows: Sequence[SubjectPairRow], *, group_count: int = GROUP_COUNT
) -> dict[str, int]:
    """Deterministically balance identities across score-blind delete groups."""
    if group_count < 2:
        raise ValueError("delete-group jackknife requires at least two groups")
    subjects = sorted(
        {
            subject
            for row in rows
            for subject in (row.subject_slot_id_1, row.subject_slot_id_2)
        }
    )
    if len(subjects) < group_count:
        raise ValueError("group count cannot exceed identity count")
    ranked = sorted(
        subjects,
        key=lambda subject: (
            hashlib.sha256(f"{GROUP_NAMESPACE}|{subject}".encode()).hexdigest(),
            subject,
        ),
    )
    return {subject: rank % group_count for rank, subject in enumerate(ranked)}


def _threshold_unweighted(
    same: np.ndarray,
    distances: np.ndarray,
    keep: np.ndarray,
    target_fmr: float,
) -> float:
    """Whole-tie-block threshold for one unweighted delete-group replicate."""
    impostor = np.asarray(distances, dtype=np.float64)[(same == 0) & keep]
    if len(impostor) == 0:
        raise ValueError("degenerate delete-group replicate: no impostor edges")
    if not np.all(np.isfinite(impostor)):
        raise ValueError("degenerate delete-group replicate: non-finite impostor distance")
    admissible_count = int(np.floor(target_fmr * len(impostor) + 1e-12))
    minimum = float(np.min(impostor))
    if admissible_count <= 0:
        sentinel = np.nextafter(minimum, -np.inf)
        if not np.isfinite(sentinel):
            raise ValueError("degenerate delete-group replicate: non-finite threshold sentinel")
        return float(sentinel)

    kth = float(np.partition(impostor, admissible_count - 1)[admissible_count - 1])
    if int(np.count_nonzero(impostor <= kth)) <= admissible_count:
        return kth
    lower = impostor[impostor < kth]
    if len(lower) == 0:
        sentinel = np.nextafter(minimum, -np.inf)
        if not np.isfinite(sentinel):
            raise ValueError("degenerate delete-group replicate: non-finite threshold sentinel")
        return float(sentinel)
    return float(np.max(lower))


def _delta_for_keep(
    rows: Sequence[SubjectPairRow],
    candidate: np.ndarray,
    reference: np.ndarray,
    keep: np.ndarray,
    *,
    target_fmr: float = TARGET_FMR,
) -> tuple[float, int, int]:
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    candidate = np.asarray(candidate, dtype=np.float64)
    reference = np.asarray(reference, dtype=np.float64)
    keep = np.asarray(keep, dtype=bool)
    if not (len(rows) == len(candidate) == len(reference) == len(keep)):
        raise ValueError("rows, distances and keep mask must align")
    if not (np.all(np.isfinite(candidate[keep])) and np.all(np.isfinite(reference[keep]))):
        raise ValueError("delete-group replicate requires finite retained distances")
    genuine = (same == 1) & keep
    impostor = (same == 0) & keep
    n_genuine = int(np.count_nonzero(genuine))
    n_impostor = int(np.count_nonzero(impostor))
    if n_genuine <= 0 or n_impostor <= 0:
        raise ValueError("degenerate delete-group replicate: missing genuine or impostor edges")
    candidate_threshold = _threshold_unweighted(same, candidate, keep, target_fmr)
    reference_threshold = _threshold_unweighted(same, reference, keep, target_fmr)
    candidate_fnmr = float(np.mean(candidate[genuine] > candidate_threshold))
    reference_fnmr = float(np.mean(reference[genuine] > reference_threshold))
    delta = candidate_fnmr - reference_fnmr
    if not np.isfinite(delta):
        raise ValueError("degenerate delete-group replicate: non-finite Delta_FNMR")
    return float(delta), n_genuine, n_impostor


def dagjk20_summary(
    rows: Sequence[SubjectPairRow],
    candidate_distances: np.ndarray,
    reference_distances: np.ndarray,
    *,
    point_delta: float,
    target_fmr: float = TARGET_FMR,
    group_count: int = GROUP_COUNT,
) -> DagjkSummary:
    """Recompute the full equal-FMR statistic after deleting each identity group."""
    if group_count != GROUP_COUNT:
        raise ValueError("S4N2 freezes the delete-group count at 20")
    candidate = np.asarray(candidate_distances, dtype=np.float64)
    reference = np.asarray(reference_distances, dtype=np.float64)
    if not (len(rows) == len(candidate) == len(reference)):
        raise ValueError("rows/candidate/reference must align")
    assignment = identity_group_assignment(rows, group_count=group_count)
    group_sizes = np.bincount(list(assignment.values()), minlength=group_count)
    if int(group_sizes.max() - group_sizes.min()) > 1:
        raise ValueError("S4N2 identity groups must be balanced within one identity")

    endpoint_1 = np.asarray([assignment[row.subject_slot_id_1] for row in rows], dtype=np.int16)
    endpoint_2 = np.asarray([assignment[row.subject_slot_id_2] for row in rows], dtype=np.int16)
    replicates: list[float] = []
    remaining_genuine: list[int] = []
    remaining_impostor: list[int] = []
    for group in range(group_count):
        keep = (endpoint_1 != group) & (endpoint_2 != group)
        delta, n_genuine, n_impostor = _delta_for_keep(
            rows,
            candidate,
            reference,
            keep,
            target_fmr=target_fmr,
        )
        replicates.append(delta)
        remaining_genuine.append(n_genuine)
        remaining_impostor.append(n_impostor)

    values = np.asarray(replicates, dtype=np.float64)
    replicate_mean = float(np.mean(values))
    variance = float((group_count - 1) / group_count * np.sum((values - replicate_mean) ** 2))
    if not np.isfinite(variance) or variance < 0.0:
        raise ValueError("S4N2 jackknife variance must be finite and non-negative")
    standard_error = float(np.sqrt(variance))
    critical = float(t.ppf(ONE_SIDED_LEVEL, df=group_count - 1))
    low = float(point_delta - critical * standard_error)
    upper = float(point_delta + critical * standard_error)
    if not all(np.isfinite(value) for value in (standard_error, critical, low, upper)):
        raise ValueError("S4N2 confidence calculation produced a non-finite value")
    return DagjkSummary(
        status="PASS_DEGENERACY_AUDIT",
        point_delta=float(point_delta),
        jackknife_mean=replicate_mean,
        jackknife_variance=variance,
        standard_error=standard_error,
        critical_value=critical,
        ci_low=low,
        ucb_97_5=upper,
        group_count=group_count,
        group_size_min=int(group_sizes.min()),
        group_size_max=int(group_sizes.max()),
        min_remaining_genuine=min(remaining_genuine),
        min_remaining_impostor=min(remaining_impostor),
    )


def run_s4n2_core_dataset(
    validation_rows: list[SubjectPairRow],
    test_rows: list[SubjectPairRow],
    *,
    dataset_index: int,
    test_truth_delta: float,
    validation_seed_effect_sd: float = 0.005,
) -> dict:
    """Generate one S4N1-compatible known-truth world and apply only the S4N2 TEST estimator."""
    from .study1b_s4n1_selection import _truncated_effects

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
    validation_scores = _point_scores(validation_rows, validation_reference, validation_candidates)
    test_points = _point_scores(test_rows, test_reference, test_candidates)
    selected = {rule: select_seed(rule, validation_scores) for rule in SELECTION_RULES}

    summaries: dict[int, DagjkSummary] = {}
    for seed in sorted(set(selected.values())):
        summaries[seed] = dagjk20_summary(
            test_rows,
            test_candidates[seed],
            test_reference,
            point_delta=float(test_points[seed]),
            target_fmr=TARGET_FMR,
        )

    candidates_out = {}
    for rule in SELECTION_RULES:
        seed = selected[rule]
        summary = summaries[seed]
        truth = float(test_truths[seed])
        candidates_out[rule] = {
            "selected_seed": seed,
            "validation_observed_score": float(validation_scores[seed]),
            "validation_true_delta": float(validation_truths[seed]),
            "test_true_delta": truth,
            "test_point_delta": float(test_points[seed]),
            "test_estimation_error": float(test_points[seed] - truth),
            "two_sided_covered": bool(summary.ci_low <= truth <= summary.ucb_97_5),
            "upper_covered": bool(truth <= summary.ucb_97_5),
            "passes_noninferiority": bool(summary.ucb_97_5 <= NI_MARGIN),
            "dagjk": {
                "status": summary.status,
                "jackknife_mean": summary.jackknife_mean,
                "jackknife_variance": summary.jackknife_variance,
                "standard_error": summary.standard_error,
                "critical_value": summary.critical_value,
                "ci_low": summary.ci_low,
                "ucb_97_5": summary.ucb_97_5,
                "group_count": summary.group_count,
                "group_size_min": summary.group_size_min,
                "group_size_max": summary.group_size_max,
                "min_remaining_genuine": summary.min_remaining_genuine,
                "min_remaining_impostor": summary.min_remaining_impostor,
            },
        }
    return {
        "dataset_index": int(dataset_index),
        "mode": "s4n2_core",
        "scientific_outcomes_opened": False,
        "screen_opened": False,
        "test_opened": False,
        "representation_geometry_opened": False,
        "amendment_activated": False,
        "test_truth_delta": float(test_truth_delta),
        "validation_seed_effect_sd": float(validation_seed_effect_sd),
        "inference_candidate": "S4N2_DAGJK20_T975",
        "candidates": candidates_out,
    }


def _cp_lower(successes: int, total: int) -> float:
    return float(
        binomtest(successes, total).proportion_ci(confidence_level=0.95, method="exact").low
    )


def aggregate_s4n2_candidate(rows: list[dict], *, candidate: str) -> dict:
    if not rows:
        raise ValueError("S4N2 aggregate requires rows")
    values = [row["candidates"][candidate] for row in rows]
    n = len(values)
    two = sum(bool(value["two_sided_covered"]) for value in values)
    upper = sum(bool(value["upper_covered"]) for value in values)
    power = sum(bool(value["passes_noninferiority"]) for value in values)
    point_errors = np.asarray([float(value["test_estimation_error"]) for value in values])
    ses = np.asarray([float(value["dagjk"]["standard_error"]) for value in values])
    point_sd = float(np.std(point_errors, ddof=1))
    return {
        "simulated_datasets": n,
        "two_sided_covered": two,
        "two_sided_empirical_coverage": two / n,
        "two_sided_cp95_lower": _cp_lower(two, n),
        "upper_covered": upper,
        "upper_empirical_coverage": upper / n,
        "upper_cp95_lower": _cp_lower(upper, n),
        "noninferiority_passes": power,
        "estimated_power": power / n,
        "point_error_mean": float(np.mean(point_errors)),
        "point_error_sd": point_sd,
        "dagjk_se_mean": float(np.mean(ses)),
        "dagjk_se_median": float(np.median(ses)),
        "median_se_to_point_error_sd_ratio": float(np.median(ses) / point_sd),
        "degenerate_fraction": 0.0,
        "coverage_pass": bool(_cp_lower(two, n) >= 0.93 and _cp_lower(upper, n) >= 0.95),
        "power_pass": bool(power / n >= 0.90),
    }
