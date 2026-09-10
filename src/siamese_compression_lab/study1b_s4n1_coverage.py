"""Coverage-only aggregation for the prospective Study 1B S4N1 checkpoint.

This module intentionally does not compute or report S4N1 power.  The first S4N1 gate is
known-truth interval coverage; power is a separate later phase that is admissible only after
the frozen coverage gate passes.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.stats import binomtest


def aggregate_core_coverage_candidate(
    rows: Sequence[dict],
    *,
    candidate: str,
    lower_coverage_bound_minimum: float = 0.93,
    degeneracy_limit_fraction: float = 0.001,
) -> dict:
    """Aggregate selected-artifact coverage for one exact TEST-truth scenario."""
    if not rows:
        raise ValueError("S4N1 coverage aggregate requires dataset rows")
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
    return {
        "candidate": candidate,
        "simulated_datasets": total,
        "covered": covered,
        "empirical_coverage": covered / total,
        "lower_95_clopper_pearson": lower,
        "degenerate_fraction": degenerate_fraction,
        "coverage_pass": bool(
            lower >= lower_coverage_bound_minimum
            and degenerate_fraction <= degeneracy_limit_fraction
        ),
        "mean_validation_optimism": float(
            np.mean([row["validation_optimism"] for row in candidate_rows])
        ),
        "mean_test_estimation_error": float(
            np.mean([row["test_estimation_error"] for row in candidate_rows])
        ),
    }
