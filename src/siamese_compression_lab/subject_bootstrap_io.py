"""I/O guards for the v0.2.2 Study 0 subject-bootstrap reanalysis."""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import pandas as pd

from .subject_bootstrap import SubjectPairRow

STUDY0_TEST_PAIR_SCORES_BYTES = 1_821_547
STUDY0_TEST_PAIR_SCORES_SHA256 = (
    "f52ea23987a9d22647e0f63275a3d8a215b5fb0c588bac41723298537b383439"
)


def sha256_file(path: str | Path) -> str:
    path = Path(path)
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_historical_score_artifact(
    path: str | Path,
    *,
    expected_bytes: int = STUDY0_TEST_PAIR_SCORES_BYTES,
    expected_sha256: str = STUDY0_TEST_PAIR_SCORES_SHA256,
) -> dict[str, int | str]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    actual_bytes = path.stat().st_size
    if actual_bytes != expected_bytes:
        raise ValueError(
            f"historical test_pair_scores.csv byte size {actual_bytes}, expected {expected_bytes}"
        )
    actual_sha256 = sha256_file(path)
    if actual_sha256 != expected_sha256:
        raise ValueError(
            "historical test_pair_scores.csv SHA-256 mismatch: "
            f"{actual_sha256} != {expected_sha256}"
        )
    return {"bytes": actual_bytes, "sha256": actual_sha256}


def load_and_validate_score_join(
    path: str | Path,
    rows: Sequence[SubjectPairRow],
) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"run_id", "method", "seed", "pair_id", "same", "distance"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"historical score artifact missing columns: {sorted(missing)}")
    if frame[list(required)].isnull().any().any():
        raise ValueError("historical score artifact contains null required values")
    key_columns = ["method", "seed", "pair_id"]
    if frame.duplicated(key_columns).any():
        raise ValueError("historical score artifact contains duplicate (method, seed, pair_id)")

    expected_labels = {row.pair_id: row.same for row in rows}
    expected_ids = set(expected_labels)
    actual_ids = set(frame["pair_id"].astype(str))
    if actual_ids != expected_ids:
        missing_ids = sorted(expected_ids - actual_ids)
        extra_ids = sorted(actual_ids - expected_ids)
        raise ValueError(
            "historical score pair_id universe differs from subject map: "
            f"missing={missing_ids[:5]}, extra={extra_ids[:5]}"
        )

    for (method, seed), group in frame.groupby(["method", "seed"], sort=True):
        group_ids = set(group["pair_id"].astype(str))
        if group_ids != expected_ids or len(group) != len(rows):
            raise ValueError(
                f"route ({method}, {seed}) does not have one score per subject-map pair"
            )
        labels = dict(zip(group["pair_id"].astype(str), group["same"].astype(int)))
        if labels != expected_labels:
            raise ValueError(f"route ({method}, {seed}) labels diverge from subject map")

    if not pd.api.types.is_numeric_dtype(frame["distance"]):
        raise ValueError("historical distance column must be numeric")
    if not np.isfinite(frame["distance"].to_numpy(dtype=np.float64)).all():
        raise ValueError("historical distance column contains non-finite values")
    return frame
