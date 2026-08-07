"""Small, deterministic plots for the replay evidence bundle."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve


def plot_roc_curves(predictions: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 6.0))
    selected = predictions.groupby("method", sort=True)["seed"].min().to_dict()
    for method, seed in selected.items():
        frame = predictions[(predictions.method == method) & (predictions.seed == seed)]
        fpr, tpr, _ = roc_curve(frame.same, -frame.distance, pos_label=1)
        ax.plot(fpr, tpr, label=f"{method} (seed {seed})")
    ax.plot([0, 1], [0, 1], "--", color="0.65", linewidth=1)
    ax.set_xscale("log")
    ax.set_xlim(1e-3, 1)
    ax.set_ylim(0, 1.01)
    ax.set_xlabel("False Match Rate")
    ax.set_ylabel("True Match Rate")
    ax.set_title("Test ROC — one pre-specified seed per route")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_fnmr(results: pd.DataFrame, path: Path) -> None:
    if "metric_protocol" in results.columns:
        results = results[results.metric_protocol == "test_equal_fmr_benchmark"]
    grouped = results.groupby(["method", "target_fmr"], as_index=False).agg(
        fnmr_mean=("fnmr", "mean"), fnmr_std=("fnmr", "std")
    )
    grouped["fnmr_std"] = grouped.fnmr_std.fillna(0.0)
    labels = [f"{m}\nFMR={f:g}" for m, f in zip(grouped.method, grouped.target_fmr)]
    x = np.arange(len(grouped))
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    ax.bar(x, grouped.fnmr_mean, yerr=grouped.fnmr_std, capsize=4, color="#4C78A8")
    ax.set_xticks(x, labels)
    ax.set_ylabel("FNMR on test at equal benchmark FMR")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_training_history(history: pd.DataFrame, path: Path) -> None:
    if history.empty:
        return
    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    for seed, frame in history.groupby("seed", sort=True):
        ax.plot(frame.epoch, frame.validation_loss, label=f"validation seed {seed}")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Contrastive loss")
    ax.set_title("Siamese linear projection — validation loss")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_storage(storage: pd.DataFrame, path: Path) -> None:
    gallery = int(storage.gallery_size.max())
    frame = storage[storage.gallery_size == gallery].sort_values("template_dim")
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.bar(frame.method, frame.gallery_gib, color="#59A14F")
    ax.set_ylabel("Derived gallery storage (GiB)")
    ax.set_title(f"Float32 template storage at {gallery:,} enrolled templates")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
