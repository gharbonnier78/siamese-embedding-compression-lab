"""Projection baselines and a NumPy implementation of a linear Siamese head."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np
from sklearn.decomposition import PCA

from .data import PairSplit, l2_normalize


class Projection(Protocol):
    name: str
    input_dim: int
    output_dim: int
    trainable_parameters: int

    def transform(self, x: np.ndarray) -> np.ndarray: ...


@dataclass
class RawProjection:
    input_dim: int
    name: str = "raw"

    @property
    def output_dim(self) -> int:
        return self.input_dim

    @property
    def trainable_parameters(self) -> int:
        return 0

    def transform(self, x: np.ndarray) -> np.ndarray:
        return l2_normalize(x)


@dataclass
class RandomProjection:
    input_dim: int
    output_dim: int
    seed: int
    name: str = "random"
    matrix: np.ndarray = field(init=False, repr=False)

    def __post_init__(self) -> None:
        rng = np.random.default_rng(self.seed)
        self.matrix = rng.normal(
            0.0, 1.0 / np.sqrt(self.output_dim), size=(self.input_dim, self.output_dim)
        ).astype(np.float32)

    @property
    def trainable_parameters(self) -> int:
        return 0

    def transform(self, x: np.ndarray) -> np.ndarray:
        return l2_normalize(x @ self.matrix)


@dataclass
class PCAProjection:
    input_dim: int
    output_dim: int
    seed: int
    name: str = "pca"
    pca: PCA | None = field(default=None, init=False, repr=False)

    @property
    def trainable_parameters(self) -> int:
        return 0

    def fit(self, train: PairSplit) -> PCAProjection:
        samples = train.endpoints()
        if self.output_dim > min(samples.shape):
            raise ValueError("PCA output dimension exceeds the available matrix rank")
        self.pca = PCA(
            n_components=self.output_dim,
            svd_solver="randomized",
            random_state=self.seed,
        )
        self.pca.fit(samples)
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.pca is None:
            raise RuntimeError("PCA projection must be fitted on training data")
        return l2_normalize(self.pca.transform(x).astype(np.float32))


@dataclass
class SiameseLinearProjection:
    input_dim: int
    output_dim: int
    seed: int
    margin: float = 1.0
    learning_rate: float = 0.002
    weight_decay: float = 0.0001
    epochs: int = 35
    batch_size: int = 128
    patience: int = 6
    minimum_improvement: float = 0.0001
    name: str = "siamese"
    weights: np.ndarray = field(init=False, repr=False)
    bias: np.ndarray = field(init=False, repr=False)
    history: list[dict[str, float]] = field(default_factory=list, init=False)
    best_epoch: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        rng = np.random.default_rng(self.seed)
        scale = np.sqrt(2.0 / (self.input_dim + self.output_dim))
        self.weights = rng.normal(
            0.0, scale, size=(self.input_dim, self.output_dim)
        ).astype(np.float32)
        self.bias = np.zeros(self.output_dim, dtype=np.float32)

    @property
    def trainable_parameters(self) -> int:
        return self.input_dim * self.output_dim + self.output_dim

    def transform(self, x: np.ndarray) -> np.ndarray:
        return l2_normalize(x @ self.weights + self.bias)

    def pair_distances(self, split: PairSplit) -> np.ndarray:
        z1 = self.transform(split.x1)
        z2 = self.transform(split.x2)
        return np.linalg.norm(z1 - z2, axis=1)

    def contrastive_loss(self, split: PairSplit) -> float:
        distance = self.pair_distances(split)
        same = split.same.astype(np.float32)
        genuine = same * 0.5 * np.square(distance)
        impostor = (1.0 - same) * 0.5 * np.square(np.maximum(0.0, self.margin - distance))
        return float(np.mean(genuine + impostor))

    def _loss_and_gradients(
        self, x1: np.ndarray, x2: np.ndarray, same: np.ndarray
    ) -> tuple[float, np.ndarray, np.ndarray]:
        raw1 = x1 @ self.weights + self.bias
        raw2 = x2 @ self.weights + self.bias
        norm1 = np.maximum(np.linalg.norm(raw1, axis=1, keepdims=True), 1e-12)
        norm2 = np.maximum(np.linalg.norm(raw2, axis=1, keepdims=True), 1e-12)
        z1, z2 = raw1 / norm1, raw2 / norm2
        delta = z1 - z2
        distance = np.maximum(np.linalg.norm(delta, axis=1), 1e-12)
        same_f = same.astype(np.float32)

        genuine_loss = same_f * 0.5 * np.square(distance)
        active_impostor = (1.0 - same_f) * (distance < self.margin)
        impostor_gap = np.maximum(0.0, self.margin - distance)
        impostor_loss = (1.0 - same_f) * 0.5 * np.square(impostor_gap)
        loss = float(np.mean(genuine_loss + impostor_loss))

        coefficient = same_f + active_impostor * (distance - self.margin) / distance
        grad_z1 = coefficient[:, None] * delta / len(same)
        grad_z2 = -grad_z1
        grad_raw1 = (
            grad_z1 - z1 * np.sum(grad_z1 * z1, axis=1, keepdims=True)
        ) / norm1
        grad_raw2 = (
            grad_z2 - z2 * np.sum(grad_z2 * z2, axis=1, keepdims=True)
        ) / norm2
        grad_w = x1.T @ grad_raw1 + x2.T @ grad_raw2
        grad_b = np.sum(grad_raw1 + grad_raw2, axis=0)
        return loss, grad_w.astype(np.float32), grad_b.astype(np.float32)

    def fit(self, train: PairSplit, validation: PairSplit) -> SiameseLinearProjection:
        rng = np.random.default_rng(self.seed)
        m_w = np.zeros_like(self.weights)
        v_w = np.zeros_like(self.weights)
        m_b = np.zeros_like(self.bias)
        v_b = np.zeros_like(self.bias)
        beta1, beta2, epsilon = 0.9, 0.999, 1e-8
        step = 0
        best_loss = np.inf
        best_weights, best_bias = self.weights.copy(), self.bias.copy()
        wait = 0

        for epoch in range(1, self.epochs + 1):
            order = rng.permutation(train.n_pairs)
            batch_losses: list[float] = []
            for start in range(0, train.n_pairs, self.batch_size):
                idx = order[start : start + self.batch_size]
                loss, grad_w, grad_b = self._loss_and_gradients(
                    train.x1[idx], train.x2[idx], train.same[idx]
                )
                batch_losses.append(loss)
                step += 1
                m_w = beta1 * m_w + (1 - beta1) * grad_w
                v_w = beta2 * v_w + (1 - beta2) * np.square(grad_w)
                m_b = beta1 * m_b + (1 - beta1) * grad_b
                v_b = beta2 * v_b + (1 - beta2) * np.square(grad_b)
                m_w_hat = m_w / (1 - beta1**step)
                v_w_hat = v_w / (1 - beta2**step)
                m_b_hat = m_b / (1 - beta1**step)
                v_b_hat = v_b / (1 - beta2**step)
                self.weights -= self.learning_rate * (
                    m_w_hat / (np.sqrt(v_w_hat) + epsilon)
                    + self.weight_decay * self.weights
                )
                self.bias -= self.learning_rate * m_b_hat / (np.sqrt(v_b_hat) + epsilon)

            train_loss = float(np.mean(batch_losses))
            validation_loss = self.contrastive_loss(validation)
            self.history.append(
                {"epoch": float(epoch), "train_loss": train_loss, "validation_loss": validation_loss}
            )
            if validation_loss < best_loss - self.minimum_improvement:
                best_loss = validation_loss
                best_weights, best_bias = self.weights.copy(), self.bias.copy()
                self.best_epoch = epoch
                wait = 0
            else:
                wait += 1
                if wait >= self.patience:
                    break

        self.weights, self.bias = best_weights, best_bias
        return self


def pair_distances(projection: Projection, split: PairSplit) -> np.ndarray:
    z1 = projection.transform(split.x1)
    z2 = projection.transform(split.x2)
    return np.linalg.norm(z1 - z2, axis=1).astype(np.float64)

