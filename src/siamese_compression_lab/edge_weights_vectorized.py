"""Isolated vectorized candidate for subject-bootstrap edge weights.

This module is an engineering experiment only. The reviewed Study 0 estimator continues to
use ``subject_bootstrap.edge_weights`` until equivalence and performance evidence justify an
integration change. No historical Study 0 scores are read here.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from .subject_bootstrap import SubjectPairRow, subject_universe


@dataclass(frozen=True)
class PreparedEdgeIndex:
    """Pre-indexed sparse observed-edge graph for repeated multiplicity evaluation."""

    subjects: tuple[str, ...]
    endpoint_1: np.ndarray
    endpoint_2: np.ndarray
    same: np.ndarray


def prepare_edge_index(rows: Sequence[SubjectPairRow]) -> PreparedEdgeIndex:
    """Map observed edge endpoints to stable indices without synthesizing any edge."""
    subjects = tuple(subject_universe(rows))
    subject_to_index = {subject: index for index, subject in enumerate(subjects)}
    endpoint_1 = np.asarray(
        [subject_to_index[row.subject_slot_id_1] for row in rows], dtype=np.int64
    )
    endpoint_2 = np.asarray(
        [subject_to_index[row.subject_slot_id_2] for row in rows], dtype=np.int64
    )
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    if np.any((same != 0) & (same != 1)):
        raise ValueError("subject-map same labels must be 0 or 1")
    return PreparedEdgeIndex(
        subjects=subjects,
        endpoint_1=endpoint_1,
        endpoint_2=endpoint_2,
        same=same,
    )


def multiplicity_vector(
    prepared: PreparedEdgeIndex,
    multiplicities: Mapping[str, int],
) -> np.ndarray:
    """Materialize multiplicities in the prepared subject order."""
    values = np.fromiter(
        (int(multiplicities.get(subject, 0)) for subject in prepared.subjects),
        dtype=np.int64,
        count=len(prepared.subjects),
    )
    if np.any(values < 0):
        raise ValueError("subject multiplicities must be non-negative")
    return values


def edge_weights_vectorized_from_array(
    prepared: PreparedEdgeIndex,
    multiplicities: np.ndarray,
) -> np.ndarray:
    """Compute preregistered m_i / m_i*m_j weights by NumPy indexing."""
    multiplicities = np.asarray(multiplicities, dtype=np.int64)
    if multiplicities.ndim != 1 or len(multiplicities) != len(prepared.subjects):
        raise ValueError("multiplicity vector must align with prepared subject universe")
    if np.any(multiplicities < 0):
        raise ValueError("subject multiplicities must be non-negative")
    m1 = multiplicities[prepared.endpoint_1]
    m2 = multiplicities[prepared.endpoint_2]
    weights = np.where(prepared.same == 1, m1, m1 * m2).astype(
        np.int64, copy=False
    )
    if weights.dtype != np.int64:
        raise AssertionError("vectorized edge weights must remain int64")
    return weights


def edge_weights_vectorized(
    prepared: PreparedEdgeIndex,
    multiplicities: Mapping[str, int],
) -> np.ndarray:
    """Mapping-compatible candidate used only for equivalence/performance experiments."""
    return edge_weights_vectorized_from_array(
        prepared,
        multiplicity_vector(prepared, multiplicities),
    )
