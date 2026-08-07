"""Operational threshold-transfer subject bootstrap for Study 0 v0.2.2."""

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
)


@dataclass(frozen=True)
class OperationalReplicate:
    replicate: int
    threshold: float
    fnmr: float
    fmr: float
    genuine_weight: int
    impostor_weight: int


def subject_bootstrap_fixed_threshold(
    *,
    rows: Sequence[SubjectPairRow],
    distances: np.ndarray,
    validation_threshold: float,
    replicates: int,
    seed: int,
) -> list[OperationalReplicate]:
    """Bootstrap TEST metrics while keeping the VALIDATION-selected threshold immutable."""
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    if not np.isfinite(validation_threshold):
        raise ValueError("validation threshold must be finite")
    distances = np.asarray(distances, dtype=np.float64)
    if len(rows) != len(distances):
        raise ValueError("subject map and route distances must align one-to-one")
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    subjects = subject_universe(rows)
    rng = np.random.Generator(np.random.PCG64(seed))
    output: list[OperationalReplicate] = []

    for replicate in range(replicates):
        multiplicities = draw_subject_multiplicities(subjects, rng)
        weights = edge_weights(rows, multiplicities)
        rates = weighted_rates_at_threshold(
            same,
            distances,
            weights,
            float(validation_threshold),
        )
        output.append(
            OperationalReplicate(
                replicate=replicate,
                threshold=float(validation_threshold),
                fnmr=rates.fnmr,
                fmr=rates.fmr,
                genuine_weight=rates.genuine_weight,
                impostor_weight=rates.impostor_weight,
            )
        )
    return output


def operational_percentile_summary(
    replicates: Sequence[OperationalReplicate],
) -> dict[str, float | int]:
    if not replicates:
        raise ValueError("cannot summarize an empty bootstrap")
    fnmr = np.asarray([row.fnmr for row in replicates], dtype=np.float64)
    fmr = np.asarray([row.fmr for row in replicates], dtype=np.float64)
    thresholds = {row.threshold for row in replicates}
    if len(thresholds) != 1:
        raise AssertionError("operational bootstrap changed the validation-frozen threshold")
    return {
        "replicates": len(replicates),
        "validation_threshold": float(next(iter(thresholds))),
        "fnmr_mean": float(fnmr.mean()),
        "fnmr_ci_low": float(np.quantile(fnmr, 0.025)),
        "fnmr_ci_high": float(np.quantile(fnmr, 0.975)),
        "fmr_mean": float(fmr.mean()),
        "fmr_ci_low": float(np.quantile(fmr, 0.025)),
        "fmr_ci_high": float(np.quantile(fmr, 0.975)),
    }
