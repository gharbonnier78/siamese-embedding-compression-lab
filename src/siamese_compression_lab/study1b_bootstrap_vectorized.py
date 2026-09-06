"""Bootstrap Study 1B accéléré, avec sémantique statistique inchangée.

Le tirage des multiplicités de sujets reste exactement le bootstrap par emplacements de
sujets revu pour Study 0/1B. L'accélération ne change pas l'estimateur : les extrémités du
graphe sont indexées une seule fois, le poids imposteur total est calculé une seule fois par
réplication, et la recherche du seuil à faible FMR ne matérialise d'abord que le préfixe trié
nécessaire. Le préfixe est étendu déterministement si besoin, sans approximation. Aucune arête
synthétique n'est créée et aucune réplication dégénérée n'est retirée ou redessinée.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from .edge_weights_vectorized import PreparedEdgeIndex, prepare_edge_index
from .study1b_statistics import Study1BBootstrapSummary
from .subject_bootstrap import SubjectPairRow

INITIAL_PREFIX_EDGES = 4096


@dataclass(frozen=True)
class PreparedGraph:
    edges: PreparedEdgeIndex
    genuine_indices: np.ndarray
    impostor_indices: np.ndarray


@dataclass(frozen=True)
class PreparedRoute:
    distances: np.ndarray
    genuine_distances: np.ndarray
    impostor_sorted_positions: np.ndarray
    impostor_sorted_distances: np.ndarray
    impostor_group_ends: np.ndarray
    nonfinite_indices: np.ndarray


def prepare_graph(rows: Sequence[SubjectPairRow]) -> PreparedGraph:
    edges = prepare_edge_index(rows)
    return PreparedGraph(
        edges=edges,
        genuine_indices=np.flatnonzero(edges.same == 1).astype(np.int64, copy=False),
        impostor_indices=np.flatnonzero(edges.same == 0).astype(np.int64, copy=False),
    )


def prepare_route(
    rows: Sequence[SubjectPairRow],
    graph: PreparedGraph,
    distances: np.ndarray,
) -> PreparedRoute:
    values = np.asarray(distances, dtype=np.float64)
    if len(rows) != len(values):
        raise ValueError("rows/distances must align one-to-one")

    impostor_distances = values[graph.impostor_indices]
    finite_positions = np.flatnonzero(np.isfinite(impostor_distances))
    order_local = finite_positions[
        np.argsort(impostor_distances[finite_positions], kind="stable")
    ].astype(np.int64, copy=False)
    sorted_values = impostor_distances[order_local]
    if len(sorted_values):
        group_ends = np.r_[
            np.flatnonzero(sorted_values[1:] != sorted_values[:-1]),
            len(sorted_values) - 1,
        ].astype(np.int64, copy=False)
    else:
        group_ends = np.empty(0, dtype=np.int64)
    return PreparedRoute(
        distances=values,
        genuine_distances=values[graph.genuine_indices],
        impostor_sorted_positions=order_local,
        impostor_sorted_distances=sorted_values,
        impostor_group_ends=group_ends,
        nonfinite_indices=np.flatnonzero(~np.isfinite(values)).astype(np.int64, copy=False),
    )


def _positive_weight_on_indices(
    graph: PreparedGraph,
    multiplicities: np.ndarray,
    indices: np.ndarray,
) -> bool:
    if not len(indices):
        return False
    same = graph.edges.same[indices]
    m1 = multiplicities[graph.edges.endpoint_1[indices]]
    m2 = multiplicities[graph.edges.endpoint_2[indices]]
    weights = np.where(same == 1, m1, m1 * m2)
    return bool(np.any(weights > 0))


def _threshold_from_prefix(
    route: PreparedRoute,
    impostor_weights: np.ndarray,
    target_fmr: float,
    total_weight: int,
) -> float:
    count = len(route.impostor_sorted_positions)
    if count == 0:
        raise ValueError("degenerate replicate: no positive-weight impostor edges")

    prefix = min(INITIAL_PREFIX_EDGES, count)
    while True:
        # Ne jamais couper un bloc d'égalité de distances.
        group_end_index = int(np.searchsorted(route.impostor_group_ends, prefix - 1, side="left"))
        prefix_end = int(route.impostor_group_ends[group_end_index]) + 1
        positions = route.impostor_sorted_positions[:prefix_end]
        weights = impostor_weights[positions]
        cumulative = np.cumsum(weights, dtype=np.int64)
        group_ends = route.impostor_group_ends[: group_end_index + 1]
        group_cumulative = cumulative[group_ends]
        group_starts = np.r_[0, group_ends[:-1] + 1]
        group_weights = np.add.reduceat(weights, group_starts)
        positive = group_weights > 0
        ratios = group_cumulative.astype(np.float64) / float(total_weight)
        crossed = positive & (ratios > target_fmr)
        admissible = positive & (ratios <= target_fmr)

        if np.any(crossed):
            first_cross = int(np.flatnonzero(crossed)[0])
            earlier_admissible = np.flatnonzero(admissible[:first_cross])
            if len(earlier_admissible):
                return float(
                    route.impostor_sorted_distances[
                        int(group_ends[int(earlier_admissible[-1])])
                    ]
                )
            first_positive = int(np.flatnonzero(positive[: first_cross + 1])[0])
            minimum = route.impostor_sorted_distances[int(group_starts[first_positive])]
            sentinel = np.nextafter(minimum, -np.inf, dtype=route.impostor_sorted_distances.dtype)
            if not np.isfinite(sentinel):
                raise ValueError("degenerate replicate: threshold sentinel is non-finite")
            return float(sentinel)

        if prefix_end >= count:
            earlier_admissible = np.flatnonzero(admissible)
            if len(earlier_admissible):
                return float(
                    route.impostor_sorted_distances[
                        int(group_ends[int(earlier_admissible[-1])])
                    ]
                )
            raise ValueError("degenerate replicate: no positive-weight impostor edges")
        prefix = min(count, max(prefix_end + 1, prefix * 2))


def _route_fnmr(
    route: PreparedRoute,
    graph: PreparedGraph,
    multiplicities: np.ndarray,
    genuine_weights: np.ndarray,
    genuine_total: int,
    impostor_weights: np.ndarray,
    impostor_total: int,
    target_fmr: float,
) -> float:
    if len(route.nonfinite_indices) and _positive_weight_on_indices(
        graph, multiplicities, route.nonfinite_indices
    ):
        raise ValueError("degenerate replicate: non-finite positive-weight distance")
    threshold = _threshold_from_prefix(route, impostor_weights, target_fmr, impostor_total)
    rejected = route.genuine_distances > threshold
    fnmr = float(genuine_weights[rejected].sum() / genuine_total)
    if not np.isfinite(fnmr):
        raise ValueError("degenerate replicate: non-finite statistic")
    return fnmr


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
    """Calcul accéléré du même résumé bootstrap Study 1B."""
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    if not 0.0 <= degeneracy_limit_fraction <= 1.0:
        raise ValueError("degeneracy_limit_fraction must be in [0, 1]")
    if not 0.0 <= target_fmr <= 1.0:
        raise ValueError("target_fmr must be in [0, 1]")

    graph = prepare_graph(rows)
    candidate = prepare_route(rows, graph, candidate_distances)
    reference = prepare_route(rows, graph, reference_distances)
    subject_count = len(graph.edges.subjects)
    if subject_count <= 0:
        raise ValueError("subject bootstrap requires at least one subject")

    rng = np.random.Generator(np.random.PCG64(seed))
    probabilities = np.full(subject_count, 1.0 / subject_count)
    deltas: list[float] = []
    degenerate = 0
    for _replicate in range(replicates):
        multiplicities = rng.multinomial(subject_count, probabilities).astype(np.int64, copy=False)

        genuine_m = multiplicities[graph.edges.endpoint_1[graph.genuine_indices]]
        genuine_weights = genuine_m.astype(np.int64, copy=False)
        genuine_total = int(genuine_weights.sum())

        imp_m1 = multiplicities[graph.edges.endpoint_1[graph.impostor_indices]]
        imp_m2 = multiplicities[graph.edges.endpoint_2[graph.impostor_indices]]
        impostor_weights = (imp_m1 * imp_m2).astype(np.int64, copy=False)
        impostor_total = int(impostor_weights.sum())

        if genuine_total <= 0 or impostor_total <= 0:
            degenerate += 1
            continue
        try:
            candidate_fnmr = _route_fnmr(
                candidate,
                graph,
                multiplicities,
                genuine_weights,
                genuine_total,
                impostor_weights,
                impostor_total,
                target_fmr,
            )
            reference_fnmr = _route_fnmr(
                reference,
                graph,
                multiplicities,
                genuine_weights,
                genuine_total,
                impostor_weights,
                impostor_total,
                target_fmr,
            )
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
