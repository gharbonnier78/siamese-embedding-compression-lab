"""Generate deterministic paper figures from versioned Study 0 replay evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import __version__ as pillow_version

NAVY = "#183B56"
TEAL = "#147D92"
ORANGE = "#C87824"
RED = "#A23B3B"
GREY = "#687782"
LIGHT = "#EEF5F7"
METHODS = ["raw", "pca", "random", "siamese"]
METHOD_LABELS = {
    "raw": "Raw 512D",
    "pca": "PCA 128D",
    "random": "Random 128D",
    "siamese": "Siamese 128D",
}
COLORS = {"raw": NAVY, "pca": TEAL, "random": GREY, "siamese": ORANGE}

SOURCE_FILES = [
    "run_manifest.json",
    "method_summary.csv",
    "paired_noninferiority.csv",
    "method_noninferiority_summary.csv",
    "storage_engineering.csv",
    "split_summary.csv",
    "routes.csv",
    "training_history.csv",
    "thresholds.csv",
    "audit_trace.jsonl",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def configure_matplotlib() -> None:
    plt.switch_backend("Agg")
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "savefig.bbox": "tight",
            "svg.hashsalt": "siamese-compression-lab-v0.2",
        }
    )


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> list[Path]:
    paths: list[Path] = []
    pdf_path = output_dir / f"{stem}.pdf"
    png_path = output_dir / f"{stem}.png"
    pdf_staging = output_dir / f".{stem}.pdf.tmp"
    png_staging = output_dir / f".{stem}.png.tmp"
    fig.savefig(
        pdf_staging,
        format="pdf",
        metadata={"CreationDate": None, "ModDate": None, "Creator": "replay pipeline"},
    )
    fig.savefig(
        png_staging,
        format="png",
        dpi=180,
        metadata={"Software": "replay pipeline"},
    )
    plt.close(fig)
    pdf_staging.replace(pdf_path)
    png_staging.replace(png_path)
    paths.extend([pdf_path, png_path])
    return paths


def ordered(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.set_index("method").loc[METHODS].reset_index()
    return result


def benchmark_metrics(evidence: Path, output_dir: Path) -> list[Path]:
    data = pd.read_csv(evidence / "method_summary.csv")
    data = ordered(data[data.metric_protocol == "test_equal_fmr_benchmark"])
    metrics = [
        ("fnmr_mean", "FNMR at equal FMR=0.01", "Lower is better", (0.76, 0.87)),
        ("auc_mean", "ROC AUC", "Higher is better", (0.74, 0.84)),
        ("eer_mean", "EER", "Lower is better", (0.24, 0.33)),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.3))
    for ax, (column, title, direction, limits) in zip(axes, metrics, strict=True):
        values = data[column].to_numpy()
        bars = ax.bar(
            range(len(METHODS)), values, color=[COLORS[m] for m in METHODS], width=0.72
        )
        ax.set_title(title, fontweight="bold")
        ax.set_ylim(*limits)
        ax.set_xticks(range(len(METHODS)), [METHOD_LABELS[m] for m in METHODS], rotation=25)
        ax.grid(axis="y", alpha=0.22)
        ax.text(0.02, 0.98, direction, transform=ax.transAxes, va="top", color=GREY, fontsize=8)
        for bar, value in zip(bars, values, strict=True):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + (limits[1] - limits[0]) * 0.018,
                f"{value:.3f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    fig.suptitle(
        "Study 0 descriptive discrimination metrics — TEST labels used for benchmarking",
        color=NAVY,
        fontweight="bold",
    )
    fig.text(
        0.5,
        -0.03,
        "AUC and EER are descriptive; equal-FMR thresholds are non-deployable. "
        "Five seeds except deterministic raw.",
        ha="center",
        color=GREY,
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.91))
    return save_figure(fig, output_dir, "study0_benchmark_metrics")


def noninferiority(evidence: Path, output_dir: Path) -> list[Path]:
    data = pd.read_csv(evidence / "paired_noninferiority.csv")
    data = data.sort_values(["candidate_method", "candidate_seed"], kind="stable")
    methods = ["pca", "random", "siamese"]
    labels: list[str] = []
    rows: list[pd.Series] = []
    for method in methods:
        subset = data[data.candidate_method == method].sort_values("candidate_seed")
        for _, row in subset.iterrows():
            rows.append(row)
            labels.append(f"{METHOD_LABELS[method]} · seed {int(row.candidate_seed)}")
    y = np.arange(len(rows))[::-1]
    means = np.asarray([row.delta_fnmr_mean for row in rows])
    low = np.asarray([row.delta_fnmr_ci_low for row in rows])
    high = np.asarray([row.delta_fnmr_ci_high for row in rows])
    colors = [COLORS[row.candidate_method] for row in rows]
    margin = float(rows[0].noninferiority_margin_fnmr)

    fig, ax = plt.subplots(figsize=(8.6, 5.5))
    ax.axvspan(-0.13, margin, color="#E6F2E9", alpha=0.7, zorder=0)
    ax.axvline(0, color=NAVY, linewidth=1.0, linestyle="--", label="No FNMR difference")
    ax.axvline(margin, color=RED, linewidth=1.5, label=f"NI margin δ={margin:.2f}")
    for ypos, mean, lo, hi, color in zip(y, means, low, high, colors, strict=True):
        ax.errorbar(
            mean,
            ypos,
            xerr=np.array([[mean - lo], [hi - mean]]),
            fmt="o",
            color=color,
            ecolor=color,
            capsize=3,
            markersize=5,
        )
    ax.set_yticks(y, labels)
    ax.set_xlabel("Paired ΔFNMR = candidate − raw (95% bootstrap CI)")
    ax.set_title("Non-inferiority was not demonstrated for any compressed method", fontweight="bold")
    ax.grid(axis="x", alpha=0.22)
    ax.legend(loc="lower right", frameon=False)
    ax.text(
        0.01,
        -0.12,
        "Pass rule: every predeclared seed must have CI upper bound ≤ δ. "
        "All plotted decisions are NOT SHOWN.",
        transform=ax.transAxes,
        color=GREY,
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return save_figure(fig, output_dir, "study0_noninferiority")


def threshold_transfer(evidence: Path, output_dir: Path) -> list[Path]:
    data = pd.read_csv(evidence / "method_summary.csv")
    benchmark = ordered(data[data.metric_protocol == "test_equal_fmr_benchmark"])
    frozen = ordered(data[data.metric_protocol == "validation_frozen_operating_point"])
    x = np.arange(len(METHODS))
    width = 0.36

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 3.5))
    axes[0].bar(x - width / 2, benchmark.fnmr_mean, width, color=NAVY, label="Equal-FMR benchmark")
    axes[0].bar(x + width / 2, frozen.fnmr_mean, width, color=ORANGE, label="Validation-frozen")
    axes[0].set_ylim(0.76, 0.96)
    axes[0].set_ylabel("TEST FNMR")
    axes[0].set_title("Error after threshold transfer", fontweight="bold")
    axes[0].legend(frameon=False, fontsize=8)

    axes[1].bar(x - width / 2, benchmark.fmr_mean, width, color=NAVY)
    axes[1].bar(x + width / 2, frozen.fmr_mean, width, color=ORANGE)
    axes[1].axhline(0.01, color=RED, linestyle="--", linewidth=1.2, label="Target FMR=0.01")
    axes[1].set_ylim(0, 0.012)
    axes[1].set_ylabel("Achieved TEST FMR")
    axes[1].set_title("Achieved operating point", fontweight="bold")
    axes[1].legend(frameon=False, fontsize=8)

    for ax in axes:
        ax.set_xticks(x, [METHOD_LABELS[m] for m in METHODS], rotation=22)
        ax.grid(axis="y", alpha=0.22)
    fig.suptitle(
        "Equal-FMR discrimination and validation-frozen operation answer different questions",
        color=NAVY,
        fontweight="bold",
    )
    fig.text(
        0.5,
        -0.02,
        "The benchmark re-locates a threshold with TEST labels; only the orange threshold is frozen "
        "from VALIDATION.",
        ha="center",
        color=GREY,
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.91))
    return save_figure(fig, output_dir, "study0_threshold_transfer")


def storage(evidence: Path, output_dir: Path) -> list[Path]:
    data = pd.read_csv(evidence / "storage_engineering.csv")
    raw = data[data.method == "raw"].sort_values("gallery_size")
    compact = data[data.method == "siamese"].sort_values("gallery_size")
    if compact.empty:
        compact = data[data.template_dim == 128].drop_duplicates("gallery_size").sort_values(
            "gallery_size"
        )
    fig, ax = plt.subplots(figsize=(7.8, 4.1))
    ax.loglog(
        raw.gallery_size,
        raw.gallery_gib,
        marker="o",
        linewidth=2,
        color=NAVY,
        label="Raw 512D · 2,048 bytes/template",
    )
    ax.loglog(
        compact.gallery_size,
        compact.gallery_gib,
        marker="o",
        linewidth=2,
        color=ORANGE,
        label="Any 128D route · 512 bytes/template",
    )
    last_raw = raw.iloc[-1]
    last_compact = compact.iloc[-1]
    ax.annotate(
        f"{last_raw.gallery_gib:.1f} GiB",
        (last_raw.gallery_size, last_raw.gallery_gib),
        xytext=(-52, 8),
        textcoords="offset points",
        color=NAVY,
    )
    ax.annotate(
        f"{last_compact.gallery_gib:.1f} GiB",
        (last_compact.gallery_size, last_compact.gallery_gib),
        xytext=(-52, -15),
        textcoords="offset points",
        color=ORANGE,
    )
    ax.set_xlabel("Gallery templates")
    ax.set_ylabel("Float32 template payload (GiB)")
    ax.set_title("Fourfold payload reduction is arithmetic, not end-to-end system evidence", fontweight="bold")
    ax.grid(which="both", alpha=0.22)
    ax.legend(frameon=False)
    fig.text(
        0.5,
        -0.01,
        "Excludes extractor and projection weights, index, metadata, encryption, allocator overhead "
        "and replication.",
        ha="center",
        color=GREY,
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return save_figure(fig, output_dir, "study0_storage")


def engineering_bounds(evidence: Path, output_dir: Path) -> list[Path]:
    routes = pd.read_csv(evidence / "routes.csv")
    raw_row = routes[routes.method == "raw"].iloc[0]
    learned_row = routes[routes.method == "siamese"].iloc[0]
    raw_bytes = int(raw_row.template_bytes_float32)
    projected_bytes = int(learned_row.template_bytes_float32)
    projection_bytes = int(learned_row.trainable_parameters) * 4
    break_even = projection_bytes / (raw_bytes - projected_bytes)
    gallery = np.unique(np.geomspace(1, 150_000_000, 300).astype(int))

    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.15))
    ax = axes[0]
    ax.loglog(gallery, raw_bytes * gallery, color=NAVY, linewidth=2, label="Raw: 2,048N")
    ax.loglog(
        gallery,
        projected_bytes * gallery + projection_bytes,
        color=ORANGE,
        linewidth=2,
        label="Projected: 512N + 262,656",
    )
    ax.axvline(break_even, color=RED, linestyle="--", linewidth=1.3)
    ax.annotate(
        "equal at N=171",
        (break_even, raw_bytes * break_even),
        xytext=(14, 18),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": RED},
        color=RED,
    )
    ax.set_xlabel("Gallery templates (N)")
    ax.set_ylabel("Incremental route bytes")
    ax.set_title("Storage including projection head", fontweight="bold")
    ax.grid(which="both", alpha=0.22)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1]
    raw_work = int(raw_row.target_dim) * gallery
    projected_work = int(learned_row.target_dim) * gallery
    ax.loglog(gallery, raw_work, color=NAVY, linewidth=2, label="Raw: 512N")
    ax.loglog(gallery, projected_work, color=ORANGE, linewidth=2, label="Projected: 128N")
    ax.fill_between(gallery, projected_work, raw_work, color=TEAL, alpha=0.12)
    ax.text(0.54, 0.46, "4× fewer\ncomponents", transform=ax.transAxes, color=TEAL, ha="center")
    ax.set_xlabel("Gallery templates (N)")
    ax.set_ylabel("Components compared per probe")
    ax.set_title("Exact-search work proxy, not latency", fontweight="bold")
    ax.grid(which="both", alpha=0.22)
    ax.legend(frameon=False, fontsize=8)

    fig.suptitle("What 512D→128D can reduce—and what remains unmeasured", color=NAVY, fontweight="bold")
    fig.text(
        0.5,
        -0.01,
        "Common frozen extractor cancels. Excludes index, metadata, replicas and measured milliseconds; "
        "the projection adds work after extraction.",
        ha="center",
        color=GREY,
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    return save_figure(fig, output_dir, "study0_engineering_bounds")


def protocol_flow(root: Path, evidence: Path, output_dir: Path) -> list[Path]:
    study = yaml.safe_load((root / "protocol/studies/study_0_lfw.yaml").read_text())
    datasheet = yaml.safe_load((root / "datasets/lfw_datasheet.yaml").read_text())
    split = pd.read_csv(evidence / "split_summary.csv").set_index("split")
    design = study["design"]
    resolution = datasheet["protocol"]["empirical_fmr_step"]
    train_detail = (
        f"Fit projections only\n{int(split.loc['train', 'pairs'])} pairs · "
        f"{int(split.loc['train', 'identities'])} identities"
    )
    test_detail = (
        f"{int(split.loc['test', 'pairs'])} pairs · "
        f"{int(split.loc['test', 'impostor_pairs'])} impostors\n"
        f"empirical FMR step={resolution:.3f}"
    )

    stages = [
        (
            "1 · Freeze",
            f"Config + claims + seeds\n{len(design['seeds'])} seeds · target FMR={design['target_fmr']:.2f}",
            NAVY,
        ),
        (
            "2 · TRAIN",
            train_detail,
            TEAL,
        ),
        (
            "3 · VALIDATION",
            f"Select/early-stop/threshold\n{int(split.loc['validation', 'pairs'])} pairs · then freeze",
            TEAL,
        ),
        (
            "4 · TEST once",
            test_detail,
            ORANGE,
        ),
        (
            "5 · Gates + claim",
            "NI: NOT DEMONSTRATED\nAdded value: NOT DEMONSTRATED",
            RED,
        ),
    ]

    fig, ax = plt.subplots(figsize=(11.0, 2.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    xs = np.linspace(0.01, 0.81, len(stages))
    width = 0.18
    for index, (x, (title, detail, color)) in enumerate(zip(xs, stages, strict=True)):
        box = FancyBboxPatch(
            (x, 0.28),
            width,
            0.48,
            boxstyle="round,pad=0.012,rounding_size=0.025",
            linewidth=1.5,
            edgecolor=color,
            facecolor=LIGHT,
        )
        ax.add_patch(box)
        ax.text(x + width / 2, 0.64, title, ha="center", va="center", color=color, fontweight="bold")
        ax.text(x + width / 2, 0.44, detail, ha="center", va="center", fontsize=8)
        if index < len(stages) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (x + width + 0.005, 0.52),
                    (xs[index + 1] - 0.005, 0.52),
                    arrowstyle="-|>",
                    mutation_scale=12,
                    linewidth=1.4,
                    color=GREY,
                )
            )
    ax.text(
        0.5,
        0.10,
        "Identity-disjoint development splits · same frozen inputs for raw/random/PCA/Siamese · "
        "TEST cannot select a winner",
        ha="center",
        color=GREY,
        fontsize=8,
    )
    ax.set_title("Study 0 evidence flow generated from protocol YAML and replay tables", color=NAVY, fontweight="bold")
    fig.tight_layout()
    return save_figure(fig, output_dir, "study0_protocol")


def generate(root: Path, evidence: Path, output_dir: Path) -> dict[str, object]:
    configure_matplotlib()
    output_dir.mkdir(parents=True, exist_ok=True)
    missing = [name for name in SOURCE_FILES if not (evidence / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing evidence files: {', '.join(missing)}")

    manifest_data = json.loads((evidence / "run_manifest.json").read_text())
    outputs: list[Path] = []
    outputs.extend(benchmark_metrics(evidence, output_dir))
    outputs.extend(noninferiority(evidence, output_dir))
    outputs.extend(threshold_transfer(evidence, output_dir))
    outputs.extend(storage(evidence, output_dir))
    outputs.extend(engineering_bounds(evidence, output_dir))
    outputs.extend(protocol_flow(root, evidence, output_dir))

    manifest: dict[str, object] = {
        "schema_version": "1.0.0",
        "generator": "scripts/generate_research_figures.py",
        "run_id": manifest_data["run_id"],
        "render_environment": {
            "matplotlib": mpl.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "pillow": pillow_version,
            "python": platform.python_version(),
            "pyyaml": yaml.__version__,
        },
        "source_files": {name: sha256(evidence / name) for name in SOURCE_FILES},
        "protocol_sources": {
            str(path.relative_to(root)): sha256(path)
            for path in [
                root / "protocol/studies/study_0_lfw.yaml",
                root / "datasets/lfw_datasheet.yaml",
                root / "gates/gate_spec.yaml",
            ]
        },
        "outputs": {path.name: sha256(path) for path in sorted(outputs)},
        "interpretation_constraints": [
            "AUC and EER are descriptive in Study 0.",
            "Equal-FMR TEST thresholds are non-deployable.",
            "Storage values cover float32 template payload only.",
            "No industrial biometric-performance claim is permitted.",
        ],
    }
    manifest_path = output_dir / "figures_manifest.json"
    manifest_staging = output_dir / ".figures_manifest.json.tmp"
    manifest_staging.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    manifest_staging.replace(manifest_path)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    evidence = (args.evidence or root / "evidence/study_0_lfw").resolve()
    output = (args.output or root / "paper/figures-generated").resolve()
    manifest = generate(root, evidence, output)
    print(json.dumps({"run_id": manifest["run_id"], "output": str(output)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
