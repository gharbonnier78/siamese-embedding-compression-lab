"""Controlled coverage simulation primitives for the v0.2.2 subject-bootstrap estimator.

The Study 0 scores are never read here. This module defines the synthetic data-generating
process and coverage summaries only. Execution, RNG hierarchy, and parallelism live in
``coverage_execution.py`` so there is a single reviewed execution path.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import binomtest, norm

from .subject_bootstrap import SubjectPairRow


@dataclass(frozen=True)
class CoverageScenario:
    name: str
    target_delta_fnmr: float
    n_subjects: int = 963
    n_genuine: int = 500
    n_impostor: int = 500
    target_fmr: float = 0.01
    reference_genuine_mean: float = 0.45
    impostor_mean: float = 0.85
    pair_noise_sd_genuine: float = 0.12
    pair_noise_sd_impostor: float = 0.10
    subject_effect_sd_genuine: float = 0.0
    subject_effect_sd_impostor: float = 0.0
    candidate_reference_noise_correlation: float = 0.7
    sparse_degree_exponent: float = 1.1


@dataclass(frozen=True)
class ScenarioTruth:
    reference_threshold: float
    candidate_threshold: float
    reference_fnmr: float
    candidate_fnmr: float
    delta_fnmr: float
    operational_reference_fmr: float
    operational_candidate_fmr: float


@dataclass(frozen=True)
class CoverageResult:
    scenario: str
    metric: str
    simulated_datasets: int
    covered: int
    empirical_coverage: float
    monte_carlo_standard_error: float
    lower_95_binomial_bound: float
    degenerate_datasets: int
    bootstrap_replicates: int
    binomial_interval_method: str = "clopper_pearson_exact_two_sided_95"


def scenario_truth(scenario: CoverageScenario) -> ScenarioTruth:
    if not -0.95 < scenario.candidate_reference_noise_correlation < 0.95:
        raise ValueError(
            "candidate/reference noise correlation must lie strictly inside (-0.95, 0.95)"
        )
    if scenario.n_subjects < 3:
        raise ValueError("coverage scenario requires at least three subjects")
    if scenario.n_genuine <= 0 or scenario.n_impostor <= 0:
        raise ValueError("coverage scenario requires positive genuine and impostor edge counts")

    genuine_sd = float(
        np.sqrt(
            scenario.pair_noise_sd_genuine**2
            + scenario.subject_effect_sd_genuine**2
        )
    )
    impostor_sd = float(
        np.sqrt(
            scenario.pair_noise_sd_impostor**2
            + 2.0 * scenario.subject_effect_sd_impostor**2
        )
    )
    threshold = float(
        scenario.impostor_mean + impostor_sd * norm.ppf(scenario.target_fmr)
    )
    reference_fnmr = float(
        1.0
        - norm.cdf(
            (threshold - scenario.reference_genuine_mean) / genuine_sd
        )
    )
    candidate_fnmr = reference_fnmr + scenario.target_delta_fnmr
    if not 0.0 < candidate_fnmr < 1.0:
        raise ValueError("target delta produces an invalid candidate FNMR")
    candidate_genuine_mean = float(
        threshold - genuine_sd * norm.ppf(1.0 - candidate_fnmr)
    )
    candidate_fnmr_check = float(
        1.0 - norm.cdf((threshold - candidate_genuine_mean) / genuine_sd)
    )
    return ScenarioTruth(
        reference_threshold=threshold,
        candidate_threshold=threshold,
        reference_fnmr=reference_fnmr,
        candidate_fnmr=candidate_fnmr_check,
        delta_fnmr=candidate_fnmr_check - reference_fnmr,
        operational_reference_fmr=scenario.target_fmr,
        operational_candidate_fmr=scenario.target_fmr,
    )


def _candidate_genuine_mean(scenario: CoverageScenario, truth: ScenarioTruth) -> float:
    genuine_sd = float(
        np.sqrt(
            scenario.pair_noise_sd_genuine**2
            + scenario.subject_effect_sd_genuine**2
        )
    )
    return float(
        truth.candidate_threshold
        - genuine_sd * norm.ppf(1.0 - truth.candidate_fnmr)
    )


def make_sparse_graph(scenario: CoverageScenario, *, seed: int) -> list[SubjectPairRow]:
    """Create a fixed sparse symmetric pair graph while ensuring all subjects are represented."""
    rng = np.random.Generator(np.random.PCG64(seed))
    subjects = [f"S{index:04d}" for index in range(scenario.n_subjects)]
    if scenario.n_genuine + 2 * scenario.n_impostor < scenario.n_subjects:
        raise ValueError("edge budget cannot expose every simulated subject")

    order = np.arange(scenario.n_subjects)
    rng.shuffle(order)
    ranks = np.arange(1, scenario.n_subjects + 1, dtype=np.float64)
    probabilities = 1.0 / np.power(ranks, scenario.sparse_degree_exponent)
    probabilities /= probabilities.sum()
    propensity = np.empty_like(probabilities)
    propensity[order] = probabilities

    rows: list[SubjectPairRow] = []
    guaranteed = list(rng.permutation(scenario.n_subjects))
    genuine_subjects: list[int] = guaranteed[: min(scenario.n_genuine, len(guaranteed))]
    while len(genuine_subjects) < scenario.n_genuine:
        genuine_subjects.append(int(rng.choice(scenario.n_subjects, p=propensity)))
    for index, subject_index in enumerate(genuine_subjects):
        subject = subjects[subject_index]
        rows.append(
            SubjectPairRow(
                f"sim_g_{index:05d}",
                1,
                subject,
                subject,
                "sim",
                index,
            )
        )

    uncovered = guaranteed[len(set(genuine_subjects)) :]
    forced_endpoints = list(uncovered)
    endpoint_capacity = 2 * scenario.n_impostor
    if len(forced_endpoints) > endpoint_capacity:
        raise ValueError("impostor edge budget cannot cover remaining subjects")
    while len(forced_endpoints) < endpoint_capacity:
        forced_endpoints.append(int(rng.choice(scenario.n_subjects, p=propensity)))
    rng.shuffle(forced_endpoints)

    for index in range(scenario.n_impostor):
        first = forced_endpoints[2 * index]
        second = forced_endpoints[2 * index + 1]
        if first == second:
            alternatives = np.flatnonzero(np.arange(scenario.n_subjects) != first)
            second = int(rng.choice(alternatives))
        rows.append(
            SubjectPairRow(
                f"sim_i_{index:05d}",
                0,
                subjects[first],
                subjects[second],
                "sim",
                index,
            )
        )
    return rows


def _joint_noise(
    rng: np.random.Generator,
    count: int,
    sd: float,
    correlation: float,
) -> tuple[np.ndarray, np.ndarray]:
    covariance = np.asarray(
        [[sd**2, correlation * sd**2], [correlation * sd**2, sd**2]],
        dtype=np.float64,
    )
    values = rng.multivariate_normal(np.zeros(2), covariance, size=count)
    return values[:, 0], values[:, 1]


def simulate_distances(
    scenario: CoverageScenario,
    rows: list[SubjectPairRow],
    *,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    truth = scenario_truth(scenario)
    rng = np.random.Generator(np.random.PCG64(seed))
    subjects = sorted(
        {
            subject
            for row in rows
            for subject in (row.subject_slot_id_1, row.subject_slot_id_2)
        }
    )
    index = {subject: position for position, subject in enumerate(subjects)}
    genuine_effect = rng.normal(
        0.0,
        scenario.subject_effect_sd_genuine,
        len(subjects),
    )
    impostor_effect = rng.normal(
        0.0,
        scenario.subject_effect_sd_impostor,
        len(subjects),
    )
    candidate_genuine_mean = _candidate_genuine_mean(scenario, truth)

    same = np.asarray([row.same for row in rows], dtype=np.int8)
    genuine_indices = np.flatnonzero(same == 1)
    impostor_indices = np.flatnonzero(same == 0)
    ref_g_noise, cand_g_noise = _joint_noise(
        rng,
        len(genuine_indices),
        scenario.pair_noise_sd_genuine,
        scenario.candidate_reference_noise_correlation,
    )
    ref_i_noise, cand_i_noise = _joint_noise(
        rng,
        len(impostor_indices),
        scenario.pair_noise_sd_impostor,
        scenario.candidate_reference_noise_correlation,
    )

    reference = np.empty(len(rows), dtype=np.float64)
    candidate = np.empty(len(rows), dtype=np.float64)
    for offset, row_index in enumerate(genuine_indices):
        row = rows[row_index]
        effect = genuine_effect[index[row.subject_slot_id_1]]
        reference[row_index] = (
            scenario.reference_genuine_mean + effect + ref_g_noise[offset]
        )
        candidate[row_index] = candidate_genuine_mean + effect + cand_g_noise[offset]
    for offset, row_index in enumerate(impostor_indices):
        row = rows[row_index]
        effect = (
            impostor_effect[index[row.subject_slot_id_1]]
            + impostor_effect[index[row.subject_slot_id_2]]
        )
        reference[row_index] = scenario.impostor_mean + effect + ref_i_noise[offset]
        candidate[row_index] = scenario.impostor_mean + effect + cand_i_noise[offset]
    return candidate, reference


def _covered(values: np.ndarray, truth: float) -> bool:
    low, high = np.quantile(values, [0.025, 0.975])
    return bool(low <= truth <= high)


def _coverage_result(
    scenario: str,
    metric: str,
    outcomes: list[bool],
    *,
    degenerate_datasets: int,
    bootstrap_replicates: int,
) -> CoverageResult:
    total = len(outcomes)
    if total == 0:
        raise ValueError("coverage result requires simulated datasets")
    successes = int(sum(outcomes))
    coverage = successes / total
    mcse = float(np.sqrt(coverage * (1.0 - coverage) / total))
    lower = float(
        binomtest(successes, total).proportion_ci(
            confidence_level=0.95,
            method="exact",
        ).low
    )
    return CoverageResult(
        scenario=scenario,
        metric=metric,
        simulated_datasets=total,
        covered=successes,
        empirical_coverage=coverage,
        monte_carlo_standard_error=mcse,
        lower_95_binomial_bound=lower,
        degenerate_datasets=degenerate_datasets,
        bootstrap_replicates=bootstrap_replicates,
    )


def coverage_gate_passes(results: list[CoverageResult]) -> bool:
    if not results:
        return False
    return all(
        result.monte_carlo_standard_error <= 0.005
        and result.lower_95_binomial_bound >= 0.93
        and result.degenerate_datasets == 0
        for result in results
    )
