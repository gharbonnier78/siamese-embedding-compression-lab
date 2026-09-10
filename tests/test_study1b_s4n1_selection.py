from __future__ import annotations

import math

import numpy as np
import pytest

from siamese_compression_lab.coverage_simulation import CoverageScenario, make_sparse_graph
from siamese_compression_lab.study1b_s4n1_selection import (
    RULE_BEST,
    RULE_FIXED,
    RULE_MEDIAN,
    SEED_LABELS,
    aggregate_core_candidate,
    draw_cross_role_seed_effects,
    equal_fmr_delta_point,
    run_core_dataset,
    select_seed,
)
from siamese_compression_lab.subject_bootstrap import SubjectPairRow


def test_selection_rules_and_exact_tie_break() -> None:
    scores = {11: 0.02, 29: 0.01, 47: 0.01, 71: 0.03, 101: 0.04}
    assert select_seed(RULE_FIXED, {}) == 11
    assert select_seed(RULE_BEST, scores) == 29
    assert select_seed(RULE_MEDIAN, scores) == 11


def test_validation_selection_fails_closed_on_missing_or_nonfinite_score() -> None:
    missing = {11: 0.02, 29: 0.01, 47: 0.01, 71: 0.03}
    with pytest.raises(ValueError, match="exactly the five"):
        select_seed(RULE_BEST, missing)

    nonfinite = {seed: 0.01 for seed in SEED_LABELS}
    nonfinite[47] = math.nan
    with pytest.raises(ValueError, match="non-finite"):
        select_seed(RULE_MEDIAN, nonfinite)


def test_equal_fmr_delta_point_uses_frozen_threshold_semantics() -> None:
    rows = [
        SubjectPairRow("g1", 1, "A", "A", "sim", 0),
        SubjectPairRow("g2", 1, "B", "B", "sim", 1),
        SubjectPairRow("i1", 0, "A", "B", "sim", 2),
        SubjectPairRow("i2", 0, "A", "C", "sim", 3),
        SubjectPairRow("i3", 0, "B", "C", "sim", 4),
        SubjectPairRow("i4", 0, "B", "D", "sim", 5),
    ]
    # At target FMR=0.25, the largest admissible threshold is the minimum impostor distance.
    reference = np.asarray([0.10, 0.20, 0.50, 0.60, 0.70, 0.80])
    candidate = np.asarray([0.10, 0.55, 0.50, 0.60, 0.70, 0.80])
    delta = equal_fmr_delta_point(rows, candidate, reference, target_fmr=0.25)
    assert delta == pytest.approx(0.5)


def _small_graph(name: str, n_subjects: int) -> list[SubjectPairRow]:
    scenario = CoverageScenario(
        name=name,
        target_delta_fnmr=0.01,
        n_subjects=n_subjects,
        n_genuine=n_subjects + 8,
        n_impostor=4 * n_subjects,
    )
    return make_sparse_graph(scenario, seed=1234 + n_subjects)


def test_core_dataset_replays_and_targets_selected_artifact_test_truth() -> None:
    validation_rows = _small_graph("validation", 24)
    test_rows = _small_graph("test", 30)
    kwargs = {
        "validation_rows": validation_rows,
        "test_rows": test_rows,
        "dataset_index": 7,
        "test_truth_delta": 0.01,
        "bootstrap_replicates": 30,
    }
    first = run_core_dataset(**kwargs)
    second = run_core_dataset(**kwargs)
    assert first == second
    assert first["scientific_outcomes_opened"] is False
    assert set(first["candidates"]) == {RULE_FIXED, RULE_BEST, RULE_MEDIAN}
    assert all(value == pytest.approx(0.01) for value in first["test_truths"].values())
    assert all(
        item["selected_seed"] in SEED_LABELS
        and item["test_true_delta"] == pytest.approx(0.01)
        for item in first["candidates"].values()
    )


def test_transport_effects_replay_and_perfect_correlation() -> None:
    validation, test = draw_cross_role_seed_effects(
        dataset_index=4,
        base_delta=0.01,
        seed_effect_sd=0.005,
        validation_test_correlation=1.0,
    )
    validation_2, test_2 = draw_cross_role_seed_effects(
        dataset_index=4,
        base_delta=0.01,
        seed_effect_sd=0.005,
        validation_test_correlation=1.0,
    )
    assert validation == validation_2
    assert test == test_2
    assert validation == test


def test_core_aggregate_accounts_for_selected_artifact_only() -> None:
    template = {
        "bootstrap": {"requested_replicates": 100, "degenerate_replicates": 0},
        "validation_optimism": -0.001,
        "test_estimation_error": 0.002,
    }
    rows = []
    for index in range(100):
        candidate_row = {
            **template,
            "covered": index < 98,
            "passes_noninferiority": index < 95,
        }
        rows.append({"candidates": {RULE_BEST: candidate_row}})
    out = aggregate_core_candidate(rows, candidate=RULE_BEST)
    assert out["simulated_datasets"] == 100
    assert out["estimated_power"] == pytest.approx(0.95)
    assert out["degenerate_fraction"] == 0.0
    assert out["power_pass"] is True
