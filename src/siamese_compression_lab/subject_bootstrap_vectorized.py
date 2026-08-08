"""Full-bootstrap vectorized execution candidate for Study 0 v0.2.2.

This module is an engineering integration experiment. It preserves the reviewed estimator as
an oracle and replaces only repeated mapping-based edge-weight construction with the
pre-indexed NumPy candidate from ``edge_weights_vectorized``. It does not read historical
Study 0 scores or execute the production coverage gate.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .edge_weights_vectorized import (
    PreparedEdgeIndex,
    edge_weights_vectorized_from_array,
    prepare_edge_index,
)
from .subject_bootstrap import (
    BootstrapReplicate,
    DegenerateReplicateError,
    SubjectPairRow,
    _degenerate_audit,
    weighted_rates_at_threshold,
    weighted_threshold_at_fmr,
)
from .subject_bootstrap_operational import OperationalReplicate


def _draw_multiplicity_vector(
    prepared: PreparedEdgeIndex,
    rng: np.random.Generator,
) -> np.ndarray:
    """Draw the same multinomial subject-slot multiplicities as the reviewed mapping path."""
    count = len(prepared.subjects)
    if count <= 0:
        raise ValueError("subject bootstrap requires at least one subject")
    return rng.multinomial(count, np.full(count, 1.0 / count)).astype(
        np.int64, copy=False
    )


def subject_bootstrap_delta_fnmr_vectorized(
    *,
    rows: Sequence[SubjectPairRow],
    candidate_distances: np.ndarray,
    reference_distances: np.ndarray,
    target_fmr: float,
    replicates: int,
    seed: int,
) -> list[BootstrapReplicate]:
    """Representation bootstrap candidate with vectorized edge-weight construction only."""
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    candidate_distances = np.asarray(candidate_distances)
    reference_distances = np.asarray(reference_distances)
    if not (len(rows) == len(candidate_distances) == len(reference_distances)):
        raise ValueError("subject map and route distance arrays must align one-to-one")

    prepared = prepare_edge_index(rows)
    np.testing.assert_array_equal(prepared.same, same)
    rng = np.random.Generator(np.random.PCG64(seed))
    output: list[BootstrapReplicate] = []

    for replicate in range(replicates):
        multiplicities = _draw_multiplicity_vector(prepared, rng)
        weights = edge_weights_vectorized_from_array(prepared, multiplicities)
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
    """Operational bootstrap candidate with the VALIDATION threshold still frozen."""
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    if not np.isfinite(validation_threshold):
        raise ValueError("validation threshold must be finite")
    distances = np.asarray(distances, dtype=np.float64)
    if len(rows) != len(distances):
        raise ValueError("subject map and route distances must align one-to-one")

    same = np.asarray([row.same for row in rows], dtype=np.int8)
    prepared = prepare_edge_index(rows)
    np.testing.assert_array_equal(prepared.same, same)
    rng = np.random.Generator(np.random.PCG64(seed))
    output: list[OperationalReplicate] = []

    for replicate in range(replicates):
        multiplicities = _draw_multiplicity_vector(prepared, rng)
        weights = edge_weights_vectorized_from_array(prepared, multiplicities)
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
