"""Generate a standalone Colab/Jupyter notebook with the source package embedded."""

from __future__ import annotations

import base64
import hashlib
import io
import json
import textwrap
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "siamese_embedding_compression_colab.ipynb"


def source_payload() -> tuple[str, str]:
    selected = [
        ROOT / "pyproject.toml",
        ROOT / "README.md",
        ROOT / "RESULTS_LFW_V0.1.md",
        ROOT / "LICENSE",
        ROOT / "THIRD_PARTY_NOTICES.md",
    ]
    for directory in ("src", "configs", "schemas", "tests"):
        selected.extend(path for path in (ROOT / directory).rglob("*") if path.is_file())
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(selected):
            archive.write(path, path.relative_to(ROOT))
    payload = buffer.getvalue()
    return base64.b64encode(payload).decode("ascii"), hashlib.sha256(payload).hexdigest()


def markdown(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": textwrap.dedent(text).strip() + "\n"}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": textwrap.dedent(text).strip() + "\n",
    }


def main() -> None:
    payload, payload_sha = source_payload()
    wrapped_payload = "\n".join(textwrap.wrap(payload, 100))
    cells = [
        markdown(
            """
            # Siamese Embedding Compression Lab — Colab/Jupyter

            **Question.** Can a supervised 512→128 metric projection reduce template
            storage by four without an unacceptable verification loss versus raw 512D?

            This notebook implements four routes: **raw 512D**, **random 128D**,
            **PCA 128D**, and **Siamese linear 128D**. It is compatible with the MMALS
            activity-replay domain-pack contract.

            The default is a deterministic synthetic smoke replay. A smoke result validates
            the pipeline only; it is never biometric evidence.
            """
        ),
        markdown(
            """
            ## Frozen protocol

            1. Identity-disjoint TRAIN / VALIDATION / TEST.
            2. Fit projections on TRAIN only.
            3. Early stopping and operating thresholds on VALIDATION only.
            4. Freeze all routes and thresholds before TEST is opened.
            5. Paired equal-FMR bootstrap versus raw 512D on the same TEST pairs.
            6. Preserve observed, derived and declared evidence separately in replay files.

            **Important limitation:** the LFW ResNet-18 route reproduces Antonio's setting,
            but ImageNet ResNet-18 is not a biometric-grade face extractor and LFW is too
            small for industrial low-FMR claims.
            """
        ),
        code(
            f'''# Standalone bootstrap: use the checked-out project when present; otherwise
# reconstruct the exact embedded package in the notebook runtime.
import base64, hashlib, io, os, pathlib, sys, zipfile

EMBEDDED_ZIP_SHA256 = "{payload_sha}"
EMBEDDED_ZIP_B64 = """{wrapped_payload}""".replace("\\n", "")

cwd = pathlib.Path.cwd().resolve()
if (cwd / "src" / "siamese_compression_lab").exists():
    PROJECT_ROOT = cwd
else:
    PROJECT_ROOT = pathlib.Path("/content/siamese-embedding-compression-lab")
    if not pathlib.Path("/content").exists():
        PROJECT_ROOT = cwd / "_standalone_siamese_embedding_compression_lab"
    raw = base64.b64decode(EMBEDDED_ZIP_B64)
    assert hashlib.sha256(raw).hexdigest() == EMBEDDED_ZIP_SHA256
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        archive.extractall(PROJECT_ROOT)

sys.path.insert(0, str(PROJECT_ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))
print("Project root:", PROJECT_ROOT)
print("Embedded source SHA-256:", EMBEDDED_ZIP_SHA256)
'''
        ),
        code(
            '''# @title Choose the execution profile
RUN_MODE = "smoke"  # @param ["smoke", "lfw"]
DOWNLOAD_RUN = False  # @param {type:"boolean"}

assert RUN_MODE in {"smoke", "lfw"}
print("Selected profile:", RUN_MODE)
if RUN_MODE == "smoke":
    print("Status target: SMOKE_VALIDATED — no biometric claim permitted.")
else:
    print("Status target: BENCHMARK_EXECUTED — limited LFW claim only.")
'''
        ),
        code(
            '''# Install only missing dependencies. Colab normally already contains the
# numerical stack and PyTorch.
import importlib.util, subprocess

base_requirements = {
    "numpy": "numpy>=1.26,<3",
    "pandas": "pandas>=2.1,<3",
    "scipy": "scipy>=1.11,<2",
    "sklearn": "scikit-learn>=1.4,<2",
    "matplotlib": "matplotlib>=3.8,<4",
    "yaml": "PyYAML>=6,<7",
    "PIL": "Pillow>=10,<13",
}
if RUN_MODE == "lfw":
    base_requirements.update({
        "torch": "torch>=2.2",
        "torchvision": "torchvision>=0.17",
        "kagglehub": "kagglehub>=0.3",
    })
missing = [requirement for module, requirement in base_requirements.items()
           if importlib.util.find_spec(module) is None]
if missing:
    print("Installing:", missing)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *missing])
else:
    print("All required packages are already available.")
'''
        ),
        code(
            '''# Execute the frozen experiment. Existing immutable output is reused rather
# than silently overwritten when this cell is run twice.
from pathlib import Path
from siamese_compression_lab.config import load_config
from siamese_compression_lab.experiment import run_experiment

config_name = "smoke.yaml" if RUN_MODE == "smoke" else "lfw_resnet18.yaml"
config = load_config(PROJECT_ROOT / "configs" / config_name)
output_root = PROJECT_ROOT / "notebook_runs"
try:
    RUN_DIR = run_experiment(config, output_root)
    execution_action = "executed"
except FileExistsError:
    candidates = sorted(output_root.glob(f"{config.experiment_id}-*"))
    if not candidates:
        raise
    RUN_DIR = candidates[-1]
    execution_action = "reused immutable run"

print("Action:", execution_action)
print("Run directory:", RUN_DIR)
'''
        ),
        code(
            '''# Scientific guardrails and concise results.
import json
import pandas as pd

manifest = json.loads((RUN_DIR / "run_manifest.json").read_text())
summary = pd.read_csv(RUN_DIR / "method_summary.csv")
noninferiority = pd.read_csv(RUN_DIR / "paired_noninferiority.csv")
method_noninferiority = pd.read_csv(RUN_DIR / "method_noninferiority_summary.csv")

print("Run status:", manifest["run_status"])
print("Evidence level:", manifest["evidence_level"])
print("Scientific claim allowed:", manifest["scientific_claim_allowed"])
print("Threshold policy:", manifest["threshold_policy"])
print("Benchmark policy:", manifest["benchmark_metric_policy"])
print("\\nMethod summary")
print(summary.to_string(index=False))
print("\\nNon-inferiority decisions")
print(noninferiority[["candidate_method", "candidate_seed", "decision"]].to_string(index=False))
print("\\nMethod decisions across every pre-declared seed")
print(method_noninferiority[["candidate_method", "method_decision"]].to_string(index=False))

if RUN_MODE == "smoke":
    assert manifest["run_status"] == "SMOKE_VALIDATED"
    assert manifest["scientific_claim_allowed"] is False
    assert set(noninferiority.decision) == {"SMOKE_ONLY_NOT_ASSESSED"}
    assert set(method_noninferiority.method_decision) == {"SMOKE_ONLY_NOT_ASSESSED"}
'''
        ),
        code(
            '''# Replay contract checks.
required = {
    "run_manifest.json",
    "data/events.jsonl",
    "routes.csv",
    "metrics.csv",
    "audit_trace.jsonl",
    "replay.compact.json",
    "benchmark_thresholds_non_deployable.csv",
    "method_noninferiority_summary.csv",
}
present = {str(path.relative_to(RUN_DIR)) for path in RUN_DIR.rglob("*") if path.is_file()}
missing = required - present
assert not missing, missing

events = [json.loads(line) for line in (RUN_DIR / "data/events.jsonl").read_text().splitlines()]
opened = next(i for i, event in enumerate(events) if event["event_type"] == "test_opened_once")
last_freeze = max(i for i, event in enumerate(events) if event["event_type"] == "route_completed")
first_test = min(i for i, event in enumerate(events) if event["event_type"] == "route_test_evaluated")
assert last_freeze < opened < first_test
print("Replay contract: PASS")
print("All models/thresholds frozen before TEST: PASS")
print("Artifacts declared in manifest:", len(manifest["artifacts"]))
'''
        ),
        code(
            '''# Display evidence figures when IPython is available.
figure_paths = sorted((RUN_DIR / "figures").glob("*.png"))
print("Figures:")
for path in figure_paths:
    print(" -", path.name)
try:
    from IPython.display import Image as IPImage, display
    for path in figure_paths:
        display(IPImage(filename=str(path)))
except Exception as exc:
    print("Inline display unavailable:", exc)
'''
        ),
        code(
            '''# Export the complete immutable replay bundle.
import shutil

archive_base = PROJECT_ROOT / f"{RUN_DIR.name}-mmals-replay"
archive_path = Path(shutil.make_archive(str(archive_base), "zip", RUN_DIR))
print("Replay ZIP:", archive_path)
print("Bytes:", archive_path.stat().st_size)

if DOWNLOAD_RUN:
    try:
        from google.colab import files
        files.download(str(archive_path))
    except ImportError:
        print("DOWNLOAD_RUN is only automatic inside Google Colab.")
'''
        ),
        markdown(
            """
            ## Interpretation gate

            - `SMOKE_VALIDATED`: only the implementation and replay chain were exercised.
            - `BENCHMARK_EXECUTED`: LFW results may be discussed only within the frozen
              protocol and its limitations.
            - No result here establishes national-gallery performance, PAD resistance,
              demographic fairness, sensor robustness, or a production acceptance threshold.
            """
        ),
    ]
    notebook = {
        "cells": cells,
        "metadata": {
            "colab": {"name": OUTPUT.name, "provenance": []},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
