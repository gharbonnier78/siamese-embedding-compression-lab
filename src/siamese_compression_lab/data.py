"""Pair data contracts and deterministic synthetic smoke data."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from .config import DataConfig


@dataclass(frozen=True)
class PairSplit:
    """A verification split; ``same=1`` means a genuine/mated pair."""

    name: str
    x1: np.ndarray
    x2: np.ndarray
    same: np.ndarray
    identity1: np.ndarray
    identity2: np.ndarray
    pair_id: np.ndarray
    source: str

    def __post_init__(self) -> None:
        n = len(self.same)
        if self.x1.shape != self.x2.shape or self.x1.ndim != 2:
            raise ValueError("x1 and x2 must be equally shaped two-dimensional arrays")
        if self.x1.shape[0] != n:
            raise ValueError("feature and label lengths differ")
        for array in (self.identity1, self.identity2, self.pair_id):
            if len(array) != n:
                raise ValueError("pair metadata length differs from labels")
        if not np.isin(self.same, [0, 1]).all():
            raise ValueError("same labels must be binary")

    @property
    def n_pairs(self) -> int:
        return len(self.same)

    @property
    def input_dim(self) -> int:
        return self.x1.shape[1]

    @property
    def identities(self) -> set[str]:
        return set(self.identity1.astype(str)) | set(self.identity2.astype(str))

    @property
    def n_genuine(self) -> int:
        return int(np.sum(self.same == 1))

    @property
    def n_impostor(self) -> int:
        return int(np.sum(self.same == 0))

    def endpoints(self) -> np.ndarray:
        return np.concatenate([self.x1, self.x2], axis=0)

    def digest(self) -> str:
        hasher = hashlib.sha256()
        for array in (self.x1, self.x2, self.same, self.identity1, self.identity2, self.pair_id):
            contiguous = np.ascontiguousarray(array)
            hasher.update(str(contiguous.dtype).encode("ascii"))
            hasher.update(str(contiguous.shape).encode("ascii"))
            if contiguous.dtype.kind in {"U", "O"}:
                hasher.update("\n".join(map(str, contiguous.tolist())).encode("utf-8"))
            else:
                hasher.update(contiguous.tobytes())
        return hasher.hexdigest()


@dataclass(frozen=True)
class DatasetBundle:
    train: PairSplit
    validation: PairSplit
    test: PairSplit
    metadata: dict[str, object]

    def validate_no_identity_leakage(self) -> None:
        splits = [self.train, self.validation, self.test]
        for i, left in enumerate(splits):
            for right in splits[i + 1 :]:
                overlap = left.identities & right.identities
                if overlap:
                    preview = sorted(overlap)[:5]
                    raise ValueError(
                        f"identity leakage between {left.name} and {right.name}: {preview}"
                    )


def l2_normalize(x: np.ndarray, epsilon: float = 1e-12) -> np.ndarray:
    norm = np.linalg.norm(x, axis=1, keepdims=True)
    return (x / np.maximum(norm, epsilon)).astype(np.float32, copy=False)


def _identity_images(
    *,
    prefix: str,
    count: int,
    images_per_identity: int,
    identity_basis: np.ndarray,
    nuisance_basis: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    input_dim, latent_dim = identity_basis.shape
    images: list[np.ndarray] = []
    labels: list[str] = []
    for identity_index in range(count):
        identity_code = rng.normal(0, 1.0, size=latent_dim)
        identity_signal = identity_basis @ identity_code
        for _ in range(images_per_identity):
            nuisance = nuisance_basis @ rng.normal(0, 0.55, size=nuisance_basis.shape[1])
            sensor_noise = rng.normal(0, 0.12, size=input_dim)
            images.append(identity_signal + nuisance + sensor_noise)
            labels.append(f"{prefix}_{identity_index:05d}")
    return l2_normalize(np.asarray(images, dtype=np.float32)), np.asarray(labels)


def _sample_pairs(
    name: str,
    embeddings: np.ndarray,
    identities: np.ndarray,
    n_pairs: int,
    rng: np.random.Generator,
) -> PairSplit:
    if n_pairs % 2:
        raise ValueError("synthetic_pairs_per_split must be even")
    groups = {
        identity: np.flatnonzero(identities == identity) for identity in np.unique(identities)
    }
    identity_names = np.asarray(sorted(groups))
    records: list[tuple[int, int, int]] = []

    for _ in range(n_pairs // 2):
        identity = str(rng.choice(identity_names))
        first, second = rng.choice(groups[identity], size=2, replace=False)
        records.append((int(first), int(second), 1))

    for _ in range(n_pairs // 2):
        identity_a, identity_b = rng.choice(identity_names, size=2, replace=False)
        first = int(rng.choice(groups[str(identity_a)]))
        second = int(rng.choice(groups[str(identity_b)]))
        records.append((first, second, 0))

    rng.shuffle(records)
    idx1 = np.asarray([r[0] for r in records])
    idx2 = np.asarray([r[1] for r in records])
    same = np.asarray([r[2] for r in records], dtype=np.int8)
    pair_id = np.asarray([f"{name}_{i:06d}" for i in range(n_pairs)])
    return PairSplit(
        name=name,
        x1=embeddings[idx1],
        x2=embeddings[idx2],
        same=same,
        identity1=identities[idx1],
        identity2=identities[idx2],
        pair_id=pair_id,
        source="synthetic_identity_embedding_generator_v1",
    )


def make_synthetic_bundle(config: DataConfig, seed: int = 20260806) -> DatasetBundle:
    """Create identity-disjoint embeddings for pipeline validation only."""
    rng = np.random.default_rng(seed)
    basis_width = config.synthetic_latent_dim + 60
    random_basis = rng.normal(size=(config.synthetic_input_dim, basis_width))
    orthonormal, _ = np.linalg.qr(random_basis)
    identity_basis = orthonormal[:, : config.synthetic_latent_dim]
    nuisance_basis = orthonormal[:, config.synthetic_latent_dim :]

    split_specs = (
        ("train", config.synthetic_train_identities),
        ("validation", config.synthetic_val_identities),
        ("test", config.synthetic_test_identities),
    )
    splits: dict[str, PairSplit] = {}
    for split_name, identity_count in split_specs:
        images, labels = _identity_images(
            prefix=split_name,
            count=identity_count,
            images_per_identity=config.synthetic_images_per_identity,
            identity_basis=identity_basis,
            nuisance_basis=nuisance_basis,
            rng=rng,
        )
        splits[split_name] = _sample_pairs(
            split_name,
            images,
            labels,
            config.synthetic_pairs_per_split,
            rng,
        )

    bundle = DatasetBundle(
        train=splits["train"],
        validation=splits["validation"],
        test=splits["test"],
        metadata={
            "dataset": "synthetic",
            "seed": seed,
            "evidence_level": "synthetic_smoke",
            "scientific_claim_allowed": False,
            "warning": "Pipeline validation only; no biometric performance conclusion.",
        },
    )
    bundle.validate_no_identity_leakage()
    return bundle


def summarize_splits(bundle: DatasetBundle) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for split in (bundle.train, bundle.validation, bundle.test):
        rows.append(
            {
                "split": split.name,
                "pairs": split.n_pairs,
                "genuine_pairs": split.n_genuine,
                "impostor_pairs": split.n_impostor,
                "identities": len(split.identities),
                "input_dim": split.input_dim,
                "sha256": split.digest(),
                "source": split.source,
            }
        )
    return rows


def identity_overlap(left: Iterable[str], right: Iterable[str]) -> set[str]:
    return set(map(str, left)) & set(map(str, right))

