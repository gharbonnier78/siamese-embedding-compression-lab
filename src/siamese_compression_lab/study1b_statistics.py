"""Study 1B identity-aware uncertainty primitives.

The Study 0 estimator failed on the first degenerate replicate. Study 1B preregisters a
slightly different *audit* policy: execute every declared draw, count degenerates, never
redraw them silently, and declare the comparison INDETERMINATE when the frozen tolerance is
exceeded. The weighting/threshold/statistic semantics remain the reviewed subject-slot ones.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .subject_bootstrap import (
    SubjectPairRow,
    draw_subject_multiplicities,
    edge_weights,
    subject_universe,
    weighted_rates_at_threshold,
    weighted_threshold_at_fmr,
)


@dataclass(frozen=True)
class Study1BBootstrapSummary:
    requested_replicates: int
    valid_replicates: int
    degenerate_replicates: int
    degenerate_fraction: float
    delta_fnmr_mean: float
    delta_fnmr_ci_low: float
    delta_fnmr_ucb_95: float
    delta_fnmr_ucb_97_5: float
    status: str


def subject_bootstrap_summary(
    *,
    rows: Sequence[SubjectPairRow],
    candidate_distances: np.ndarray,
    reference_distances: np.ndarray,
    target_fmr: float,
    replicates: int,
    seed: int,
    degeneracy_limit_fraction: float = 0.001,
) -> Study1BBootstrapSummary:
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    if not 0.0 <= degeneracy_limit_fraction <= 1.0:
        raise ValueError("degeneracy_limit_fraction must be in [0, 1]")
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    candidate = np.asarray(candidate_distances, dtype=np.float64)
    reference = np.asarray(reference_distances, dtype=np.float64)
    if not (len(rows) == len(candidate) == len(reference)):
        raise ValueError("rows/candidate/reference must align one-to-one")

    subjects = subject_universe(rows)
    rng = np.random.Generator(np.random.PCG64(seed))
    deltas: list[float] = []
    degenerate = 0
    for _replicate in range(replicates):
        multiplicities = draw_subject_multiplicities(subjects, rng)
        weights = edge_weights(rows, multiplicities)
        try:
            candidate_threshold = weighted_threshold_at_fmr(
                same, candidate, weights, target_fmr
            )
            reference_threshold = weighted_threshold_at_fmr(
                same, reference, weights, target_fmr
            )
            candidate_rates = weighted_rates_at_threshold(
                same, candidate, weights, candidate_threshold
            )
            reference_rates = weighted_rates_at_threshold(
                same, reference, weights, reference_threshold
            )
        except ValueError as exc:
            if not str(exc).startswith("degenerate replicate:"):
                raise
            degenerate += 1
            continue
        deltas.append(candidate_rates.fnmr - reference_rates.fnmr)

    degenerate_fraction = degenerate / replicates
    if not deltas:
        return Study1BBootstrapSummary(
            requested_replicates=replicates,
            valid_replicates=0,
            degenerate_replicates=degenerate,
            degenerate_fraction=degenerate_fraction,
            delta_fnmr_mean=float("nan"),
            delta_fnmr_ci_low=float("nan"),
            delta_fnmr_ucb_95=float("nan"),
            delta_fnmr_ucb_97_5=float("nan"),
            status="INDETERMINATE_DEGENERATE",
        )
    values = np.asarray(deltas, dtype=np.float64)
    status = (
        "PASS_DEGENERACY_AUDIT"
        if degenerate_fraction <= degeneracy_limit_fraction
        else "INDETERMINATE_DEGENERATE"
    )
    return Study1BBootstrapSummary(
        requested_replicates=replicates,
        valid_replicates=len(values),
        degenerate_replicates=degenerate,
        degenerate_fraction=degenerate_fraction,
        delta_fnmr_mean=float(values.mean()),
        delta_fnmr_ci_low=float(np.quantile(values, 0.025)),
        delta_fnmr_ucb_95=float(np.quantile(values, 0.95)),
        delta_fnmr_ucb_97_5=float(np.quantile(values, 0.975)),
        status=status,
    )
