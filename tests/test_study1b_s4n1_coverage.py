from __future__ import annotations

import pytest

from siamese_compression_lab.study1b_s4n1_coverage import (
    aggregate_core_coverage_candidate,
)
from siamese_compression_lab.study1b_s4n1_selection import RULE_BEST


def test_coverage_only_aggregate_does_not_emit_power_semantics() -> None:
    template = {
        "bootstrap": {"requested_replicates": 100, "degenerate_replicates": 0},
        "validation_optimism": -0.001,
        "test_estimation_error": 0.002,
    }
    rows = []
    for index in range(100):
        candidate_row = {
            **template,
            "covered": index < 99,
            "passes_noninferiority": False,
        }
        rows.append({"candidates": {RULE_BEST: candidate_row}})

    out = aggregate_core_coverage_candidate(rows, candidate=RULE_BEST)

    assert out["simulated_datasets"] == 100
    assert out["empirical_coverage"] == pytest.approx(0.99)
    assert out["degenerate_fraction"] == 0.0
    assert out["coverage_pass"] is True
    assert "estimated_power" not in out
    assert "power_pass" not in out
    assert "noninferiority_passes" not in out


def test_coverage_only_aggregate_enforces_degeneracy_gate() -> None:
    rows = [
        {
            "candidates": {
                RULE_BEST: {
                    "bootstrap": {
                        "requested_replicates": 1000,
                        "degenerate_replicates": 2,
                    },
                    "validation_optimism": 0.0,
                    "test_estimation_error": 0.0,
                    "covered": True,
                }
            }
        }
        for _ in range(100)
    ]

    out = aggregate_core_coverage_candidate(rows, candidate=RULE_BEST)

    assert out["degenerate_fraction"] == pytest.approx(0.002)
    assert out["coverage_pass"] is False
