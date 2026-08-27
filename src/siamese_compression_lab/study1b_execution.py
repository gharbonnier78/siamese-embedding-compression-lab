"""Fail-closed Study 1B execution core.

Importing or testing this module does not open SCREEN/TEST outcomes. Outcome-bearing callers
must present a separate human authorization artifact bound to the exact Study 1B protocol.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml
from sklearn.decomposition import PCA

from .data import PairSplit, l2_normalize
from .models import RawProjection, SiameseLinearProjection
from .study1b_preflight import task_seed_sequence

STUDY_ID = "study_1b_matched_compression"
PROTOCOL_PATH = Path("protocol/studies/study_1b_matched_compression.yaml")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def seed_token(task: str) -> int:
    state = task_seed_sequence(task).generate_state(4, dtype=np.uint32)
    value = 0
    for offset, word in enumerate(state):
        value |= int(word) << (32 * offset)
    return value


def assert_outcome_authorized(authorization_path: Path, protocol_path: Path = PROTOCOL_PATH) -> dict:
    """Require explicit human GO bound to the exact protocol bytes.

    The repository intentionally contains no passing Study 1B authorization yet. Therefore a
    premature workflow_dispatch fails here before loading SCREEN/TEST embeddings or scores.
    """
    if not authorization_path.is_file():
        raise PermissionError("Study 1B outcome execution requires a separate authorization artifact")
    value = yaml.safe_load(authorization_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PermissionError("invalid Study 1B authorization mapping")
    expected = sha256_file(protocol_path)
    if value.get("study_id") != STUDY_ID:
        raise PermissionError("authorization is not for Study 1B")
    if value.get("status") != "AUTHORIZED":
        raise PermissionError("Study 1B authorization status is not AUTHORIZED")
    if value.get("human_go", {}).get("explicit") is not True:
        raise PermissionError("Study 1B explicit human GO is absent")
    if value.get("protocol_sha256") != expected:
        raise PermissionError("authorization is not bound to the current Study 1B protocol")
    return value


@dataclass(frozen=True)
class EmbeddingTable:
    capture_id: np.ndarray
    subject_id: np.ndarray
    role: np.ndarray
    embedding: np.ndarray
    source_sha256: str

    @classmethod
    def load(cls, path: Path) -> "EmbeddingTable":
        payload = np.load(path, allow_pickle=False)
        capture_id = payload["capture_id"].astype(str)
        subject_id = payload["subject_id"].astype(str)
        role = payload["role"].astype(str)
        embedding = payload["embedding"].astype(np.float32)
        n = len(capture_id)
        if embedding.shape != (n, 512):
            raise ValueError(f"raw512 table must have shape (N,512), got {embedding.shape}")
        if len(subject_id) != n or len(role) != n or len(set(capture_id)) != n:
            raise ValueError("embedding table ids/roles do not form a unique aligned table")
        norms = np.linalg.norm(embedding, axis=1)
        if not np.allclose(norms, 1.0, atol=2e-4, rtol=0.0):
            raise ValueError("raw512 embeddings must already satisfy the frozen L2 contract")
        return cls(capture_id, subject_id, role, embedding, sha256_file(path))

    def indices(self) -> dict[str, int]:
        return {capture_id: index for index, capture_id in enumerate(self.capture_id)}

    def unique_role_captures(self, role: str) -> np.ndarray:
        mask = self.role == role
        return self.embedding[mask]


def load_pair_graph(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"empty pair graph: {path}")
    pair_ids = [row["pair_id"] for row in rows]
    if len(pair_ids) != len(set(pair_ids)):
        raise ValueError(f"duplicate pair ids in {path}")
    return rows


def graph_to_split(name: str, graph: list[dict[str, str]], table: EmbeddingTable) -> PairSplit:
    index = table.indices()
    try:
        left = np.asarray([index[row["capture_id_1"]] for row in graph])
        right = np.asarray([index[row["capture_id_2"]] for row in graph])
    except KeyError as exc:
        raise ValueError(f"pair graph references capture missing from raw512 table: {exc}") from exc
    roles = {str(table.role[item]) for item in np.concatenate([left, right])}
    if roles != {name.upper()}:
        raise ValueError(f"{name}: graph/table role mismatch: {sorted(roles)}")
    return PairSplit(
        name=name.lower(),
        x1=table.embedding[left],
        x2=table.embedding[right],
        same=np.asarray([int(row["same"]) for row in graph], dtype=np.int8),
        identity1=np.asarray([row["subject_slot_id_1"] for row in graph]),
        identity2=np.asarray([row["subject_slot_id_2"] for row in graph]),
        pair_id=np.asarray([row["pair_id"] for row in graph]),
        source=f"study1b-frozen-{name.lower()}-pair-graph",
    )


@dataclass
class Random128:
    matrix: np.ndarray
    seed_label: int
    seed_token_value: int

    @classmethod
    def fit(cls, seed_label: int) -> "Random128":
        token = seed_token(f"random128|seed={seed_label}")
        rng = np.random.default_rng(token)
        matrix = rng.normal(0.0, 1.0 / np.sqrt(128), size=(512, 128)).astype(np.float32)
        return cls(matrix, seed_label, token)

    def transform(self, x: np.ndarray) -> np.ndarray:
        return l2_normalize(x @ self.matrix)


@dataclass
class PCA128:
    pca: PCA
    seed_label: int
    seed_token_value: int

    @classmethod
    def fit(cls, unique_train_captures: np.ndarray, seed_label: int) -> "PCA128":
        if unique_train_captures.ndim != 2 or unique_train_captures.shape[1] != 512:
            raise ValueError("PCA TRAIN capture matrix must be Nx512")
        token = seed_token(f"pca128|seed={seed_label}")
        # sklearn requires a conventional 32-bit random_state token.
        random_state = int(token % (2**32 - 1))
        pca = PCA(n_components=128, svd_solver="randomized", whiten=False, random_state=random_state)
        pca.fit(unique_train_captures)
        return cls(pca, seed_label, token)

    def transform(self, x: np.ndarray) -> np.ndarray:
        return l2_normalize(self.pca.transform(x).astype(np.float32))


def fit_siamese128(train: PairSplit, validation: PairSplit, seed_label: int) -> SiameseLinearProjection:
    token = seed_token(f"siamese128|seed={seed_label}")
    # Existing reviewed NumPy implementation is preserved; only its RNG token is derived
    # through the Study 1B task-bound lineage.
    model = SiameseLinearProjection(
        input_dim=512,
        output_dim=128,
        seed=token,
        margin=1.0,
        learning_rate=0.002,
        weight_decay=0.0001,
        epochs=35,
        batch_size=128,
        patience=6,
        minimum_improvement=0.0001,
    )
    return model.fit(train, validation)


def serialize_transform(path: Path, method: str, model, seed_label: int | None) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if method == "raw512" and isinstance(model, RawProjection):
        np.savez(path, method=method, input_dim=512)
    elif method == "random128" and isinstance(model, Random128):
        np.savez(path, method=method, matrix=model.matrix, seed_label=seed_label, seed_token=model.seed_token_value)
    elif method == "pca128" and isinstance(model, PCA128):
        np.savez(
            path,
            method=method,
            mean=model.pca.mean_,
            components=model.pca.components_,
            explained_variance=model.pca.explained_variance_,
            seed_label=seed_label,
            seed_token=model.seed_token_value,
        )
    elif method == "siamese128" and isinstance(model, SiameseLinearProjection):
        np.savez(
            path,
            method=method,
            weights=model.weights,
            bias=model.bias,
            seed_label=seed_label,
            best_epoch=model.best_epoch,
        )
    else:
        raise TypeError(f"unsupported transform serialization: {method} / {type(model).__name__}")
    return sha256_file(path)


def append_progress(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
