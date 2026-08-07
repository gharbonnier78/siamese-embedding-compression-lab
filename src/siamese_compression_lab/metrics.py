"""Verification metrics with validation-frozen operating thresholds."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


@dataclass(frozen=True)
class VerificationResult:
    threshold: float
    target_fmr: float
    fmr: float
    fnmr: float
    tmr: float
    accuracy: float
    balanced_accuracy: float
    auc: float
    eer: float
    n_genuine: int
    n_impostor: int
    threshold_source: str

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "threshold": self.threshold,
            "target_fmr": self.target_fmr,
            "fmr": self.fmr,
            "fnmr": self.fnmr,
            "tmr": self.tmr,
            "accuracy": self.accuracy,
            "balanced_accuracy": self.balanced_accuracy,
            "auc": self.auc,
            "eer": self.eer,
            "n_genuine": self.n_genuine,
            "n_impostor": self.n_impostor,
            "threshold_source": self.threshold_source,
        }


def threshold_at_fmr(
    same: np.ndarray, distances: np.ndarray, target_fmr: float
) -> tuple[float, dict[str, int | float]]:
    """Choose the largest validation threshold satisfying the empirical FMR target."""
    impostor = np.sort(np.asarray(distances)[np.asarray(same) == 0])
    if len(impostor) == 0:
        raise ValueError("threshold calibration needs impostor pairs")
    allowed_false_matches = int(np.floor(target_fmr * len(impostor)))
    if allowed_false_matches <= 0:
        threshold = float(np.nextafter(impostor[0], -np.inf))
    elif allowed_false_matches >= len(impostor):
        threshold = float(np.inf)
    else:
        lower = impostor[allowed_false_matches - 1]
        upper = impostor[allowed_false_matches]
        threshold = float(lower + (upper - lower) / 2.0)
    achieved = float(np.mean(impostor <= threshold))
    return threshold, {
        "n_validation_impostors": len(impostor),
        "allowed_false_matches": allowed_false_matches,
        "validation_fmr": achieved,
    }


def _eer(same: np.ndarray, distances: np.ndarray) -> float:
    fpr, tpr, _ = roc_curve(same, -distances, pos_label=1)
    fnr = 1.0 - tpr
    index = int(np.argmin(np.abs(fpr - fnr)))
    return float((fpr[index] + fnr[index]) / 2.0)


def evaluate_at_threshold(
    same: np.ndarray,
    distances: np.ndarray,
    *,
    threshold: float,
    target_fmr: float,
    threshold_source: str = "validation",
) -> VerificationResult:
    same = np.asarray(same, dtype=np.int8)
    distances = np.asarray(distances, dtype=np.float64)
    if threshold_source != "validation":
        raise ValueError("deployable operating thresholds must come from validation")
    return _evaluate(
        same,
        distances,
        threshold=threshold,
        target_fmr=target_fmr,
        threshold_source=threshold_source,
    )


def _evaluate(
    same: np.ndarray,
    distances: np.ndarray,
    *,
    threshold: float,
    target_fmr: float,
    threshold_source: str,
) -> VerificationResult:
    predicted_same = distances <= threshold
    genuine = same == 1
    impostor = ~genuine
    if not genuine.any() or not impostor.any():
        raise ValueError("evaluation requires both genuine and impostor pairs")
    fnmr = float(np.mean(~predicted_same[genuine]))
    fmr = float(np.mean(predicted_same[impostor]))
    tmr = 1.0 - fnmr
    accuracy = float(np.mean(predicted_same == genuine))
    tnr = 1.0 - fmr
    return VerificationResult(
        threshold=float(threshold),
        target_fmr=float(target_fmr),
        fmr=fmr,
        fnmr=fnmr,
        tmr=tmr,
        accuracy=accuracy,
        balanced_accuracy=float((tmr + tnr) / 2.0),
        auc=float(roc_auc_score(same, -distances)),
        eer=_eer(same, distances),
        n_genuine=int(genuine.sum()),
        n_impostor=int(impostor.sum()),
        threshold_source=threshold_source,
    )


def evaluate_benchmark_at_fmr(
    same: np.ndarray, distances: np.ndarray, *, target_fmr: float
) -> tuple[VerificationResult, dict[str, int | float]]:
    """Evaluate discrimination at equal TEST FMR; this threshold is not deployable."""
    threshold, evidence = threshold_at_fmr(same, distances, target_fmr)
    result = _evaluate(
        np.asarray(same, dtype=np.int8),
        np.asarray(distances, dtype=np.float64),
        threshold=threshold,
        target_fmr=target_fmr,
        threshold_source="test_benchmark_only",
    )
    return result, evidence


def bootstrap_paired_fnmr_at_fmr(
    *,
    same: np.ndarray,
    candidate_distances: np.ndarray,
    reference_distances: np.ndarray,
    target_fmr: float,
    replicates: int,
    seed: int,
) -> dict[str, float | int]:
    """Paired bootstrap of FNMR difference with FMR recalibrated in each replicate."""
    same = np.asarray(same, dtype=np.int8)
    candidate_distances = np.asarray(candidate_distances, dtype=np.float64)
    reference_distances = np.asarray(reference_distances, dtype=np.float64)
    genuine_idx = np.flatnonzero(same == 1)
    impostor_idx = np.flatnonzero(same == 0)
    if len(genuine_idx) == 0 or len(impostor_idx) == 0:
        raise ValueError("bootstrap requires genuine and impostor pairs")
    rng = np.random.default_rng(seed)
    delta = np.empty(replicates, dtype=np.float64)
    candidate_fnmr_values = np.empty(replicates, dtype=np.float64)
    reference_fnmr_values = np.empty(replicates, dtype=np.float64)

    for i in range(replicates):
        genuine_sample = rng.choice(genuine_idx, size=len(genuine_idx), replace=True)
        impostor_sample = rng.choice(impostor_idx, size=len(impostor_idx), replace=True)
        bootstrap_same = np.concatenate(
            [np.ones(len(genuine_sample), dtype=np.int8), np.zeros(len(impostor_sample), dtype=np.int8)]
        )
        candidate_sample = np.concatenate(
            [candidate_distances[genuine_sample], candidate_distances[impostor_sample]]
        )
        reference_sample = np.concatenate(
            [reference_distances[genuine_sample], reference_distances[impostor_sample]]
        )
        candidate_threshold, _ = threshold_at_fmr(
            bootstrap_same, candidate_sample, target_fmr
        )
        reference_threshold, _ = threshold_at_fmr(
            bootstrap_same, reference_sample, target_fmr
        )
        candidate_fnmr = float(
            np.mean(candidate_distances[genuine_sample] > candidate_threshold)
        )
        reference_fnmr = float(
            np.mean(reference_distances[genuine_sample] > reference_threshold)
        )
        candidate_fnmr_values[i] = candidate_fnmr
        reference_fnmr_values[i] = reference_fnmr
        delta[i] = candidate_fnmr - reference_fnmr

    return {
        "replicates": replicates,
        "target_fmr": target_fmr,
        "candidate_fnmr_mean": float(np.mean(candidate_fnmr_values)),
        "reference_fnmr_mean": float(np.mean(reference_fnmr_values)),
        "delta_fnmr_mean": float(np.mean(delta)),
        "delta_fnmr_ci_low": float(np.quantile(delta, 0.025)),
        "delta_fnmr_ci_high": float(np.quantile(delta, 0.975)),
        "benchmark_threshold_policy": "recalibrated_within_each_test_bootstrap",
    }


def fmr_resolution(n_impostors: int) -> float:
    """Smallest non-zero empirical FMR step supported by a split."""
    if n_impostors <= 0:
        raise ValueError("n_impostors must be positive")
    return 1.0 / n_impostors
