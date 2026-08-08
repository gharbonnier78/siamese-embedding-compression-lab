"""Protocol-preserving weighted subject-slot bootstrap for Study 0 v0.2.2.

This module implements the preregistered estimator only. It does not execute the Study 0
reanalysis, change historical evidence, or close E-STAT-001.
"""

from __future__ import annotations

import csv
import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class SubjectPairRow:
    pair_id: str
    same: int
    subject_slot_id_1: str
    subject_slot_id_2: str
    source_class: str
    source_row: int


@dataclass(frozen=True)
class WeightedRates:
    threshold: float
    fmr: float
    fnmr: float
    genuine_weight: int
    impostor_weight: int


@dataclass(frozen=True)
class BootstrapReplicate:
    replicate: int
    candidate_fnmr: float
    reference_fnmr: float
    delta_fnmr: float
    candidate_threshold: float
    reference_threshold: float
    genuine_weight: int
    impostor_weight: int


@dataclass(frozen=True)
class DegenerateReplicateAudit:
    """Structured §9 evidence for a bootstrap replicate that cannot be evaluated."""

    replicate: int
    reason: str
    genuine_weight: int
    impostor_weight: int
    effective_genuine_edges: int
    effective_impostor_edges: int
    completed_replicates: int

    def as_dict(self) -> dict[str, int | str]:
        return {
            "replicate": self.replicate,
            "reason": self.reason,
            "genuine_weight": self.genuine_weight,
            "impostor_weight": self.impostor_weight,
            "effective_genuine_edges": self.effective_genuine_edges,
            "effective_impostor_edges": self.effective_impostor_edges,
            "completed_replicates": self.completed_replicates,
        }


class DegenerateReplicateError(RuntimeError):
    """Blocking failure that preserves the failed replicate audit and prior results."""

    def __init__(
        self,
        audit: DegenerateReplicateAudit,
        completed_replicates: Sequence[Any] = (),
    ) -> None:
        self.audit = audit
        self.completed_replicates = tuple(completed_replicates)
        super().__init__(
            f"degenerate bootstrap replicate {audit.replicate}: {audit.reason}"
        )


def _read_csv_rows(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = [row for row in csv.reader(handle) if row]
    if rows and rows[0][0].strip().lower() in {"name", "name1", "person"}:
        rows = rows[1:]
    return rows


def _pseudonym(identity: str, namespace: str) -> str:
    digest = hashlib.sha256(f"{namespace}|{identity}".encode()).hexdigest()
    return f"subject_{digest[:16]}"


def reconstruct_lfw_devtest_subject_map(
    matched_path: str | Path,
    mismatched_path: str | Path,
    *,
    namespace: str = "lfw-devtest-v0.2.2",
) -> list[SubjectPairRow]:
    """Reconstruct the Study 0 TEST endpoint identities without creating new pair edges."""
    matched_path = Path(matched_path)
    mismatched_path = Path(mismatched_path)
    rows: list[SubjectPairRow] = []

    for index, row in enumerate(_read_csv_rows(matched_path)):
        if len(row) < 3:
            raise ValueError(f"invalid matched LFW row {index}: {row}")
        subject = _pseudonym(row[0], namespace)
        rows.append(
            SubjectPairRow(
                pair_id=f"test_genuine_{index:05d}",
                same=1,
                subject_slot_id_1=subject,
                subject_slot_id_2=subject,
                source_class="matched",
                source_row=index,
            )
        )

    for index, row in enumerate(_read_csv_rows(mismatched_path)):
        if len(row) < 4:
            raise ValueError(f"invalid mismatched LFW row {index}: {row}")
        rows.append(
            SubjectPairRow(
                pair_id=f"test_impostor_{index:05d}",
                same=0,
                subject_slot_id_1=_pseudonym(row[0], namespace),
                subject_slot_id_2=_pseudonym(row[2], namespace),
                source_class="mismatched",
                source_row=index,
            )
        )
    return rows


def validate_subject_map(
    rows: Sequence[SubjectPairRow],
    *,
    expected_pairs: int | None = None,
    expected_genuine: int | None = None,
    expected_impostor: int | None = None,
    expected_subjects: int | None = None,
) -> dict[str, int]:
    pair_ids = [row.pair_id for row in rows]
    if len(pair_ids) != len(set(pair_ids)):
        raise ValueError("subject map contains duplicate pair_id values")
    genuine = [row for row in rows if row.same == 1]
    impostor = [row for row in rows if row.same == 0]
    if len(genuine) + len(impostor) != len(rows):
        raise ValueError("subject map same labels must be 0 or 1")
    if any(row.subject_slot_id_1 != row.subject_slot_id_2 for row in genuine):
        raise ValueError("genuine subject-map row has different endpoint subjects")
    if any(row.subject_slot_id_1 == row.subject_slot_id_2 for row in impostor):
        raise ValueError("impostor subject-map row has identical endpoint subjects")
    subjects = {
        subject
        for row in rows
        for subject in (row.subject_slot_id_1, row.subject_slot_id_2)
    }
    counts = {
        "pairs": len(rows),
        "genuine": len(genuine),
        "impostor": len(impostor),
        "subjects": len(subjects),
    }
    expected = {
        "pairs": expected_pairs,
        "genuine": expected_genuine,
        "impostor": expected_impostor,
        "subjects": expected_subjects,
    }
    for key, value in expected.items():
        if value is not None and counts[key] != value:
            raise ValueError(f"subject map {key}={counts[key]}, expected {value}")
    return counts


def write_subject_map(path: str | Path, rows: Sequence[SubjectPairRow]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "pair_id",
                "same",
                "subject_slot_id_1",
                "subject_slot_id_2",
                "source_class",
                "source_row",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.pair_id,
                    row.same,
                    row.subject_slot_id_1,
                    row.subject_slot_id_2,
                    row.source_class,
                    row.source_row,
                ]
            )


def subject_universe(rows: Sequence[SubjectPairRow]) -> list[str]:
    return sorted(
        {
            subject
            for row in rows
            for subject in (row.subject_slot_id_1, row.subject_slot_id_2)
        }
    )


def draw_subject_multiplicities(
    subjects: Sequence[str], rng: np.random.Generator
) -> dict[str, int]:
    subjects = list(subjects)
    if not subjects:
        raise ValueError("subject bootstrap requires at least one subject")
    counts = rng.multinomial(len(subjects), np.full(len(subjects), 1.0 / len(subjects)))
    return {subject: int(count) for subject, count in zip(subjects, counts)}


def edge_weights(
    rows: Sequence[SubjectPairRow], multiplicities: Mapping[str, int]
) -> np.ndarray:
    weights = np.empty(len(rows), dtype=np.int64)
    for index, row in enumerate(rows):
        m1 = int(multiplicities.get(row.subject_slot_id_1, 0))
        m2 = int(multiplicities.get(row.subject_slot_id_2, 0))
        if m1 < 0 or m2 < 0:
            raise ValueError("subject multiplicities must be non-negative")
        weights[index] = m1 if row.same == 1 else m1 * m2
    return weights


def bootstrap_weight_diagnostics(
    same: np.ndarray,
    weights: np.ndarray,
) -> dict[str, int]:
    """Return the §9 totals/effective-edge counts even for a degenerate replicate."""
    same = np.asarray(same, dtype=np.int8)
    weights = np.asarray(weights, dtype=np.int64)
    if len(same) != len(weights):
        raise ValueError("same and weights must have equal length")
    genuine = same == 1
    impostor = same == 0
    return {
        "genuine_weight": int(weights[genuine].sum()),
        "impostor_weight": int(weights[impostor].sum()),
        "effective_genuine_edges": int(np.count_nonzero(weights[genuine] > 0)),
        "effective_impostor_edges": int(np.count_nonzero(weights[impostor] > 0)),
    }


def _degenerate_audit(
    *,
    replicate: int,
    reason: str,
    same: np.ndarray,
    weights: np.ndarray,
    completed_replicates: int,
) -> DegenerateReplicateAudit:
    diagnostics = bootstrap_weight_diagnostics(same, weights)
    return DegenerateReplicateAudit(
        replicate=replicate,
        reason=reason.removeprefix("degenerate replicate: "),
        completed_replicates=completed_replicates,
        **diagnostics,
    )


def weighted_threshold_at_fmr(
    same: np.ndarray,
    distances: np.ndarray,
    weights: np.ndarray,
    target_fmr: float,
) -> float:
    """Apply the preregistered whole-tie-block weighted TEST threshold rule."""
    same = np.asarray(same, dtype=np.int8)
    distances = np.asarray(distances)
    weights = np.asarray(weights, dtype=np.int64)
    if not (len(same) == len(distances) == len(weights)):
        raise ValueError("same, distances and weights must have equal length")
    if not 0.0 <= target_fmr <= 1.0:
        raise ValueError("target_fmr must be in [0, 1]")
    mask = (same == 0) & (weights > 0)
    impostor_distances = distances[mask]
    impostor_weights = weights[mask]
    if len(impostor_distances) == 0:
        raise ValueError("degenerate replicate: no positive-weight impostor edges")
    if not np.all(np.isfinite(impostor_distances)):
        raise ValueError("degenerate replicate: non-finite impostor distance")
    total_weight = int(impostor_weights.sum())
    if total_weight <= 0:
        raise ValueError("degenerate replicate: zero impostor weight")

    unique = np.unique(impostor_distances)
    admissible: list[float] = []
    for value in unique:
        cumulative = int(impostor_weights[impostor_distances <= value].sum()) / total_weight
        if cumulative <= target_fmr:
            admissible.append(float(value))
        else:
            break
    if admissible:
        return admissible[-1]
    minimum = impostor_distances.min()
    sentinel = np.nextafter(minimum, -np.inf, dtype=impostor_distances.dtype)
    if not np.isfinite(sentinel):
        raise ValueError("degenerate replicate: threshold sentinel is non-finite")
    return float(sentinel)


def weighted_rates_at_threshold(
    same: np.ndarray,
    distances: np.ndarray,
    weights: np.ndarray,
    threshold: float,
) -> WeightedRates:
    same = np.asarray(same, dtype=np.int8)
    distances = np.asarray(distances, dtype=np.float64)
    weights = np.asarray(weights, dtype=np.int64)
    if not (len(same) == len(distances) == len(weights)):
        raise ValueError("same, distances and weights must have equal length")
    if np.any(weights < 0):
        raise ValueError("edge weights must be non-negative")
    positive = weights > 0
    if not np.all(np.isfinite(distances[positive])):
        raise ValueError("degenerate replicate: non-finite positive-weight distance")
    genuine = same == 1
    impostor = same == 0
    genuine_weight = int(weights[genuine].sum())
    impostor_weight = int(weights[impostor].sum())
    if genuine_weight <= 0 or impostor_weight <= 0:
        raise ValueError("degenerate replicate: zero genuine or impostor total weight")
    fnmr = float(weights[genuine & (distances > threshold)].sum() / genuine_weight)
    fmr = float(weights[impostor & (distances <= threshold)].sum() / impostor_weight)
    if not (np.isfinite(fnmr) and np.isfinite(fmr)):
        raise ValueError("degenerate replicate: non-finite statistic")
    return WeightedRates(
        threshold=float(threshold),
        fmr=fmr,
        fnmr=fnmr,
        genuine_weight=genuine_weight,
        impostor_weight=impostor_weight,
    )


def subject_bootstrap_delta_fnmr(
    *,
    rows: Sequence[SubjectPairRow],
    candidate_distances: np.ndarray,
    reference_distances: np.ndarray,
    target_fmr: float,
    replicates: int,
    seed: int,
) -> list[BootstrapReplicate]:
    """Paired subject-slot bootstrap for the representation estimand."""
    if replicates <= 0:
        raise ValueError("replicates must be positive")
    same = np.asarray([row.same for row in rows], dtype=np.int8)
    candidate_distances = np.asarray(candidate_distances)
    reference_distances = np.asarray(reference_distances)
    if not (len(rows) == len(candidate_distances) == len(reference_distances)):
        raise ValueError("subject map and route distance arrays must align one-to-one")
    subjects = subject_universe(rows)
    rng = np.random.Generator(np.random.PCG64(seed))
    output: list[BootstrapReplicate] = []

    for replicate in range(replicates):
        multiplicities = draw_subject_multiplicities(subjects, rng)
        weights = edge_weights(rows, multiplicities)
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


def percentile_summary(replicates: Sequence[BootstrapReplicate]) -> dict[str, float | int]:
    if not replicates:
        raise ValueError("cannot summarize an empty bootstrap")
    delta = np.asarray([row.delta_fnmr for row in replicates], dtype=np.float64)
    return {
        "replicates": len(replicates),
        "delta_fnmr_mean": float(delta.mean()),
        "delta_fnmr_ci_low": float(np.quantile(delta, 0.025)),
        "delta_fnmr_ci_high": float(np.quantile(delta, 0.975)),
        "delta_fnmr_ucb_97_5": float(np.quantile(delta, 0.975)),
    }
