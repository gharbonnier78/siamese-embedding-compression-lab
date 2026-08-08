"""Pre-indexed vectorized edge weights for the v0.2.2 sparse subject graph.

This module is an execution optimization only. It preserves the frozen weighting rule:
- genuine observed edge (i, i): m_i
- impostor observed edge (i, j): m_i * m_j

It never creates unobserved edges and does not alter RNG, thresholds, estimands, or
degenerate-replicate policy.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class EdgeWeightPlan:
    """Immutable indexing of observed sparse edges into the subject multiplicity vector."""

    subjects: tuple[str, ...]
    left_indices: np.ndarray
    right_indices: np.ndarray
    genuine_mask: np.ndarray


def build_edge_weight_plan(
    rows: Sequence[Any], subjects: Sequence[str]
) -> EdgeWeightPlan:
    """Index the fixed observed graph once so replicates need no per-edge dict lookups."""
    subject_tuple = tuple(subjects)
    subject_index = {subject: index for index, subject in enumerate(subject_tuple)}
    if len(subject_index) != len(subject_tuple):
        raise ValueError("edge-weight plan subjects must be unique")

    try:
        left = np.fromiter(
            (subject_index[row.subject_slot_id_1] for row in rows),
            dtype=np.intp,
            count=len(rows),
        )
        right = np.fromiter(
            (subject_index[row.subject_slot_id_2] for row in rows),
            dtype=np.intp,
            count=len(rows),
        )
    except KeyError as exc:
        raise ValueError(f"edge endpoint absent from subject universe: {exc.args[0]}") from exc

    genuine = np.fromiter(
        (row.same == 1 for row in rows), dtype=np.bool_, count=len(rows)
    )
    return EdgeWeightPlan(
        subjects=subject_tuple,
        left_indices=left,
        right_indices=right,
        genuine_mask=genuine,
    )


def edge_weights_from_plan(
    plan: EdgeWeightPlan, multiplicities: Mapping[str, int]
) -> np.ndarray:
    """Apply the frozen sparse-edge weighting rule with vectorized indexed arithmetic."""
    counts = np.fromiter(
        (int(multiplicities.get(subject, 0)) for subject in plan.subjects),
        dtype=np.int64,
        count=len(plan.subjects),
    )
    if np.any(counts < 0):
        raise ValueError("subject multiplicities must be non-negative")

    m1 = counts[plan.left_indices]
    m2 = counts[plan.right_indices]
    weights = np.where(plan.genuine_mask, m1, m1 * m2)
    return np.asarray(weights, dtype=np.int64)
