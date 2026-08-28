"""Bootstrap Study 1B accéléré, avec sémantique statistique inchangée.

Le tirage des multiplicités de sujets reste exactement le bootstrap par emplacements de
sujets revu pour Study 0/1B. L'accélération vient de préparations sans effet scientifique :
les extrémités du graphe et les blocs d'égalité de distances sont indexés une seule fois, puis
les poids/seuils sont calculés par petits lots NumPy. Chaque appel ``rng.multinomial`` reste
individuel et dans le même ordre que la voie scalaire. Aucune arête synthétique n'est créée et
aucune réplication dégénérée n'est retirée ou redessinée.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from .edge_weights_vectorized import prepare_edge_index
from .study1b_statistics import Study1BBootstrapSummary
from .subject_bootstrap import SubjectPairRow

DEFAULT_BATCH_SIZE = 16


@dataclass(frozen=True)
class PreparedRoute:
    distances: np.ndarray
    genuine_indices: np.ndarray
    impostor_sorted_indices: np.ndarray
    impostor_group_ends: np.ndarray
    impostor_group_values: np.ndarray
    nonfinite_indices: np.ndarray


def prepare_route(rows: Sequence[SubjectPairRow], distances: np.ndarray) -> PreparedRoute:
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    values = np.asarray(distances, dtype=np.float64)
    if len(rows) != len(values):
        raise ValueError("rows/distances must align one-to-one")
    if np.any((same != 0) & (same != 1)):
        raise ValueError("subject-map same labels must be 0 or 1")

    genuine = np.flatnonzero(same == 1).astype(np.int64, copy=False)
    finite_impostor = np.flatnonzero((same == 0) & np.isfinite(values))
    order = finite_impostor[np.argsort(values[finite_impostor], kind="stable")]
    sorted_values = values[order]
    if len(sorted_values):
        group_ends = np.r_[np.flatnonzero(sorted_values[1:] != sorted_values[:-1]), len(order) - 1]
        group_values = sorted_values[group_ends]
    else:
        group_ends = np.empty(0, dtype=np.int64)
        group_values = np.empty(0, dtype=np.float64)
    nonfinite = np.flatnonzero(~np.isfinite(values)).astype(np.int64, copy=False)
    return PreparedRoute(
        distances=values,
        genuine_indices=genuine,
        impostor_sorted_indices=order.astype(np.int64, copy=False),
        impostor_group_ends=group_ends.astype(np.int64, copy=False),
        impostor_group_values=group_values,
        nonfinite_indices=nonfinite,
    )


def _edge_weight_batch(graph, multiplicities: np.ndarray) -> np.ndarray:
    m1 = multiplicities[:, graph.endpoint_1]
    m2 = multiplicities[:, graph.endpoint_2]
    return np.where(graph.same[None, :] == 1, m1, m1 * m2).astype(np.int64, copy=False)


def _route_fnmr_batch(
    prepared: PreparedRoute,
    weights: np.ndarray,
    target_fmr: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return per-row validity and FNMR using the frozen whole-tie-block threshold rule."""
    if weights.ndim != 2 or weights.shape[1] != len(prepared.distances):
        raise ValueError("weight matrix must be batch x edge and align with distances")
    if np.any(weights < 0):
        raise ValueError("edge weights must be non-negative")
    if not 0.0 <= target_fmr <= 1.0:
        raise ValueError("target_fmr must be in [0, 1]")

    batch = weights.shape[0]
    valid = np.ones(batch, dtype=bool)
    if len(prepared.nonfinite_indices):
        valid &= ~np.any(weights[:, prepared.nonfinite_indices] > 0, axis=1)

    genuine_weights = weights[:, prepared.genuine_indices]
    genuine_total = genuine_weights.sum(axis=1, dtype=np.int64)
    valid &= genuine_total > 0

    if not len(prepared.impostor_sorted_indices):
        return np.zeros(batch, dtype=bool), np.full(batch, np.nan)
    ordered_weights = weights[:, prepared.impostor_sorted_indices]
    impostor_total = ordered_weights.sum(axis=1, dtype=np.int64)
    valid &= impostor_total > 0

    cumulative = np.cumsum(ordered_weights, axis=1, dtype=np.int64)
    group_cumulative = cumulative[:, prepared.impostor_group_ends]
    group_weights = np.diff(
        np.concatenate(
            [np.zeros((batch, 1), dtype=np.int64), group_cumulative],
            axis=1,
        ),
        axis=1,
    )
    positive_groups = group_weights > 0
    valid &= np.any(positive_groups, axis=1)

    safe_total = np.where(impostor_total > 0, impostor_total, 1)
    ratios = group_cumulative / safe_total[:, None]
    admissible = positive_groups & (ratios <= target_fmr)
    group_numbers = np.arange(len(prepared.impostor_group_values), dtype=np.int64)
    last_admissible = np.where(admissible, group_numbers[None, :], -1).max(axis=1)
    first_positive = np.where(positive_groups, group_numbers[None, :], len(group_numbers)).min(axis=1)

    thresholds = np.empty(batch, dtype=np.float64)
    has_admissible = last_admissible >= 0
    if np.any(has_admissible):
        thresholds[has_admissible] = prepared.impostor_group_values[
            last_admissible[has_admissible]
        ]
    no_admissible = ~has_admissible
    if np.any(no_admissible):
        safe_first = np.minimum(first_positive[no_admissible], len(group_numbers) - 1)
        minima = prepared.impostor_group_values[safe_first]
        sentinels = np.nextafter(minima, -np.inf)
        thresholds[no_admissible] = sentinels
        valid[no_admissible] &= np.isfinite(sentinels)

    genuine_distances = prepared.distances[prepared.genuine_indices]
    rejected = genuine_distances[None, :] > thresholds[:, None]
    rejected_weight = np.where(rejected, genuine_weights, 0).sum(axis=1, dtype=np.int64)
    safe_genuine = np.where(genuine_total > 0, genuine_total, 1)
    fnmr = rejected_weight / safe_genuine
    valid &= np.isfinite(fnmr)
    fnmr = np.where(valid, fnmr, np.nan)
    return valid, fnmr


def subject_bootstrap_summary_vectorized(
    *,
    rows: Sequence[SubjectPairRow],
    candidate_distances: np.ndarray,
    reference_distances: np.ndarray,
    target_fmr: float,
    replicates: int,
    seed: int,
    degeneracy_limit_fraction: float = 0.001,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> Study1BBootstrapSummary:
    """Calcul accéléré du même résumé bootstrap Study 1B, par petits lots bornés en mémoire."""
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if not 0.0 <= degeneracy_limit_fraction <= 1.0:
        raise ValueError("degeneracy_limit_fraction must be in [0, 1]")

    graph = prepare_edge_index(rows)
    candidate = prepare_route(rows, candidate_distances)
    reference = prepare_route(rows, reference_distances)
    subject_count = len(graph.subjects)
    if subject_count <= 0:
        raise ValueError("subject bootstrap requires at least one subject")

    rng = np.random.Generator(np.random.PCG64(seed))
    probabilities = np.full(subject_count, 1.0 / subject_count)
    deltas: list[float] = []
    degenerate = 0
    completed = 0
    while completed < replicates:
        current = min(batch_size, replicates - completed)
        # Conserver exactement un tirage multinomial par réplication et son ordre RNG.
        multiplicities = np.stack(
            [rng.multinomial(subject_count, probabilities) for _ in range(current)]
        ).astype(np.int64, copy=False)
        weights = _edge_weight_batch(graph, multiplicities)
        candidate_valid, candidate_fnmr = _route_fnmr_batch(candidate, weights, target_fmr)
        reference_valid, reference_fnmr = _route_fnmr_batch(reference, weights, target_fmr)
        valid = candidate_valid & reference_valid
        degenerate += int(np.count_nonzero(~valid))
        if np.any(valid):
            deltas.extend((candidate_fnmr[valid] - reference_fnmr[valid]).tolist())
        completed += current

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
