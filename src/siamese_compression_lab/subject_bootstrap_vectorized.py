"""Vectorized execution of the frozen v0.2.2 subject bootstrap.

This module is an execution optimization only. It preserves the subject-slot estimands,
observed sparse graph, multiplicity rules, threshold semantics, degenerate behavior and RNG
sequence. The reviewed scalar implementation remains available as a reference path.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from .subject_bootstrap import (
    BootstrapReplicate,
    DegenerateReplicateError,
    SubjectPairRow,
    _degenerate_audit,
    draw_subject_multiplicities,
    subject_universe,
    weighted_rates_at_threshold,
    weighted_threshold_at_fmr,
)
from .subject_bootstrap_operational import OperationalReplicate


@dataclass(frozen=True)
class EdgeWeightPlan:
    """Pre-indexed immutable sparse-graph representation for bootstrap edge weights."""

    subjects: tuple[str, ...]
    endpoint_1: np.ndarray
    endpoint_2: np.ndarray
    same: np.ndarray


def compile_edge_weight_plan(rows: Sequence[SubjectPairRow]) -> EdgeWeightPlan:
    """Index subject endpoints once while preserving the exact observed row order."""
    subjects = tuple(subject_universe(rows))
    positions = {subject: index for index, subject in enumerate(subjects)}
    return EdgeWeightPlan(
        subjects=subjects,
        endpoint_1=np.asarray(
            [positions[row.subject_slot_id_1] for row in rows], dtype=np.int64
        ),
        endpoint_2=np.asarray(
            [positions[row.subject_slot_id_2] for row in rows], dtype=np.int64
        ),
        same=np.asarray([row.same for row in rows], dtype=np.int8),
    )


def edge_weights_vectorized(
    plan: EdgeWeightPlan,
    multiplicities: Mapping[str, int],
) -> np.ndarray:
    """Apply frozen m_i / m_i*m_j rules using pre-indexed NumPy gathers."""
    counts = np.fromiter(
        (int(multiplicities.get(subject, 0)) for subject in plan.subjects),
        dtype=np.int64,
        count=len(plan.subjects),
    )
    if np.any(counts < 0):
        raise ValueError("subject multiplicities must be non-negative")
    first = counts[plan.endpoint_1]
    weights = first.copy()
    impostor = plan.same != 1
    weights[impostor] = first[impostor] * counts[plan.endpoint_2[impostor]]
    return weights


def subject_bootstrap_delta_fnmr_vectorized(
    *,
    rows: Sequence[SubjectPairRow],
    candidate_distances: np.ndarray,
    reference_distances: np.ndarray,
    target_fmr: float,
    replicates: int,
    seed: int,
) -> list[BootstrapReplicate]:
    """Paired representation bootstrap with vectorized edge-weight construction."""
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    plan = compile_edge_weight_plan(rows)
    same = plan.same
    candidate_distances = np.asarray(candidate_distances)
    reference_distances = np.asarray(reference_distances)
    if not (len(rows) == len(candidate_distances) == len(reference_distances)):
        raise ValueError("subject map and route distance arrays must align one-to-one")
    rng = np.random.Generator(np.random.PCG64(seed))
    output: list[BootstrapReplicate] = []

    for replicate in range(replicates):
        multiplicities = draw_subject_multiplicities(plan.subjects, rng)
        weights = edge_weights_vectorized(plan, multiplicities)
        try:
            candidate_threshold = weighted_threshold_at_fmr(
                same, candidate_distances, weights, target_fmr
            )
            reference_threshold = weighted_threshold_at_fmr(
                same, reference_distances, weights, target_fmr
            )
            candidate = weighted_rates_at_threshold(
                same, candidate_distances, weights, candidate_threshold
            )
            reference = weighted_rates_at_threshold(
                same, reference_distances, weights, reference_threshold
            )
        except ValueError as exc:
            reason = str(exc)
            if not reason.startswith("degenerate replicate:"):
                raise
            raise DegenerateReplicateError(
                _degenerate_audit(
                    replicate=replicate,
                    reason=reason,
                    same=same,
                    weights=weights,
                    completed_replicates=len(output),
                ),
                output,
            ) from exc
        if (
            candidate.genuine_weight != reference.genuine_weight
            or candidate.impostor_weight != reference.impostor_weight
        ):
            raise AssertionError("paired routes received different bootstrap weights")
        output.append(
            BootstrapReplicate(
                replicate=replicate,
                candidate_fnmr=candidate.fnmr,
                reference_fnmr=reference.fnmr,
                delta_fnmr=candidate.fnmr - reference.fnmr,
                candidate_threshold=candidate_threshold,
                reference_threshold=reference_threshold,
                genuine_weight=candidate.genuine_weight,
                impostor_weight=candidate.impostor_weight,
            )
        )
    return output


def subject_bootstrap_fixed_threshold_vectorized(
    *,
    rows: Sequence[SubjectPairRow],
    distances: np.ndarray,
    validation_threshold: float,
    replicates: int,
    seed: int,
) -> list[OperationalReplicate]:
    """Operational TEST bootstrap with the frozen VALIDATION threshold unchanged."""
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    if not np.isfinite(validation_threshold):
        raise ValueError("validation threshold must be finite")
    distances = np.asarray(distances, dtype=np.float64)
    if len(rows) != len(distances):
        raise ValueError("subject map and route distances must align one-to-one")
    plan = compile_edge_weight_plan(rows)
    same = plan.same
    rng = np.random.Generator(np.random.PCG64(seed))
    output: list[OperationalReplicate] = []

    for replicate in range(replicates):
        multiplicities = draw_subject_multiplicities(plan.subjects, rng)
        weights = edge_weights_vectorized(plan, multiplicities)
        try:
            rates = weighted_rates_at_threshold(
                same,
                distances,
                weights,
                float(validation_threshold),
            )
        except ValueError as exc:
            reason = str(exc)
            if not reason.startswith("degenerate replicate:"):
                raise
            raise DegenerateReplicateError(
                _degenerate_audit(
                    replicate=replicate,
                    reason=reason,
                    same=same,
                    weights=weights,
                    completed_replicates=len(output),
                ),
                output,
            ) from exc
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
