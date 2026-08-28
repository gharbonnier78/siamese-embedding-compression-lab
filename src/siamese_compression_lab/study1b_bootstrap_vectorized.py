"""Bootstrap Study 1B accéléré, avec sémantique statistique inchangée.

Le tirage des multiplicités de sujets reste exactement le bootstrap par emplacements de
sujets revu pour Study 0/1B. L'accélération vient de deux préparations sans effet scientifique :
(1) les extrémités du graphe sont indexées une seule fois et les poids m_i / m_i*m_j sont
calculés par NumPy ; (2) l'ordre des distances et les blocs d'égalité sont préparés une seule
fois, ce qui évite de rescanner toutes les distances pour chaque seuil et chaque réplication.
Aucune arête synthétique n'est créée et aucune réplication dégénérée n'est retirée/redessinée.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from .edge_weights_vectorized import edge_weights_vectorized_from_array, prepare_edge_index
from .subject_bootstrap import SubjectPairRow
from .study1b_statistics import Study1BBootstrapSummary


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


def _threshold_and_fnmr(
    prepared: PreparedRoute,
    weights: np.ndarray,
    target_fmr: float,
) -> tuple[float, float]:
    weights = np.asarray(weights, dtype=np.int64)
    if len(weights) != len(prepared.distances):
        raise ValueError("weights/distances must align one-to-one")
    if np.any(weights < 0):
        raise ValueError("edge weights must be non-negative")
    if not 0.0 <= target_fmr <= 1.0:
        raise ValueError("target_fmr must be in [0, 1]")
    if len(prepared.nonfinite_indices) and np.any(weights[prepared.nonfinite_indices] > 0):
        raise ValueError("degenerate replicate: non-finite positive-weight distance")

    genuine_weights = weights[prepared.genuine_indices]
    genuine_total = int(genuine_weights.sum())
    if genuine_total <= 0:
        raise ValueError("degenerate replicate: zero genuine or impostor total weight")

    ordered_weights = weights[prepared.impostor_sorted_indices]
    if not len(ordered_weights) or not np.any(ordered_weights > 0):
        raise ValueError("degenerate replicate: no positive-weight impostor edges")
    impostor_total = int(ordered_weights.sum())
    if impostor_total <= 0:
        raise ValueError("degenerate replicate: zero impostor weight")

    cumulative = np.cumsum(ordered_weights, dtype=np.int64)
    group_cumulative = cumulative[prepared.impostor_group_ends]
    group_starts = np.r_[0, prepared.impostor_group_ends[:-1] + 1]
    group_weights = np.add.reduceat(ordered_weights, group_starts)
    positive_groups = group_weights > 0
    ratios = group_cumulative.astype(np.float64) / float(impostor_total)
    admissible = positive_groups & (ratios <= target_fmr)
    if np.any(admissible):
        threshold = float(prepared.impostor_group_values[np.flatnonzero(admissible)[-1]])
    else:
        first_positive = int(np.flatnonzero(positive_groups)[0])
        minimum = prepared.impostor_group_values[first_positive]
        sentinel = np.nextafter(minimum, -np.inf, dtype=prepared.impostor_group_values.dtype)
        if not np.isfinite(sentinel):
            raise ValueError("degenerate replicate: threshold sentinel is non-finite")
        threshold = float(sentinel)

    rejected = prepared.distances[prepared.genuine_indices] > threshold
    fnmr = float(genuine_weights[rejected].sum() / genuine_total)
    if not np.isfinite(fnmr):
        raise ValueError("degenerate replicate: non-finite statistic")
    return threshold, fnmr


def subject_bootstrap_summary_vectorized(
    *,
    rows: Sequence[SubjectPairRow],
    candidate_distances: np.ndarray,
    reference_distances: np.ndarray,
    target_fmr: float,
    replicates: int,
    seed: int,
    degeneracy_limit_fraction: float = 0.001,
) -> Study1BBootstrapSummary:
    """Calcul accéléré du même résumé bootstrap Study 1B.

    Les appels ``rng.multinomial`` restent un par réplication, dans le même ordre que la voie
    scalaire, afin que la lignée aléatoire soit directement comparable lors des tests oracle.
    """
    if replicates <= 0:
        raise ValueError("replicates must be positive")
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
    for _replicate in range(replicates):
        multiplicities = rng.multinomial(subject_count, probabilities).astype(np.int64, copy=False)
        weights = edge_weights_vectorized_from_array(graph, multiplicities)
        try:
            _, candidate_fnmr = _threshold_and_fnmr(candidate, weights, target_fmr)
            _, reference_fnmr = _threshold_and_fnmr(reference, weights, target_fmr)
        except ValueError as exc:
            if not str(exc).startswith("degenerate replicate:"):
                raise
            degenerate += 1
            continue
        deltas.append(candidate_fnmr - reference_fnmr)

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
