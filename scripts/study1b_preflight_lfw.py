"""Materialize the frozen Study 1B LFW metadata/graph preflight without model outcomes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from siamese_compression_lab.study1b_preflight import run_lfw_preflight

DATASET_HANDLE = "jessicali9530/lfw-dataset/versions/4"


def _resolve_dataset_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    import kagglehub

    return Path(kagglehub.dataset_download(DATASET_HANDLE)).resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = _resolve_dataset_root(args.dataset_root)
    report = run_lfw_preflight(root, args.output_dir)
    report["dataset_handle"] = DATASET_HANDLE
    report["scientific_outcomes_opened"] = False
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
