from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def load_benchmark_module(path: Path):
    spec = importlib.util.spec_from_file_location("study1a_a1a2_benchmark", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import benchmark module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark-script", required=True)
    parser.add_argument("--source-label", required=True)
    parser.add_argument("--dataset-file", required=True)
    parser.add_argument("--dataset-locator", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--checkpoint-locator", required=True)
    parser.add_argument("--adaface-src", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--torch-threads", type=int, default=4)
    args = parser.parse_args()

    mod = load_benchmark_module(Path(args.benchmark_script).resolve())

    import numpy as np
    import torch

    dataset = Path(args.dataset_file).resolve()
    checkpoint = Path(args.checkpoint).resolve()
    adaface_src = Path(args.adaface_src).resolve()

    torch.set_num_threads(max(1, args.torch_threads))
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    device = torch.device("cpu")

    blobs, labels, dataset_info = mod.inspect_validation_container(dataset)
    dataset_sha = mod.sha256_file(dataset)
    model, checkpoint_sha = mod.load_model(checkpoint, adaface_src, device)
    embeddings, diagnostics = mod.infer_all(
        model,
        blobs,
        device=device,
        batch_size=args.batch_size,
        progress_every=512,
    )
    metrics = mod.evaluate_adaface_protocol(embeddings, labels)
    observed = float(metrics["accuracy_mean"])

    output = {
        "schema_version": "1.0",
        "kind": "study1a_cfp_fp_source_diagnostic",
        "diagnostic_only": True,
        "gate_authority": False,
        "canonical_gate_result_changed": False,
        "source_label": args.source_label,
        "dataset": {
            "locator": args.dataset_locator,
            "sha256": dataset_sha,
            "size_bytes": dataset.stat().st_size,
            **dataset_info,
        },
        "checkpoint": {
            "locator": args.checkpoint_locator,
            "sha256": checkpoint_sha,
            "architecture": "AdaFace IR101/R100",
        },
        "frozen_protocol": {
            "benchmark": "cfp_fp",
            "published_reference": 0.9926,
            "frozen_minimum": 0.9896,
            "distance": "squared_l2_on_l2_normalized_512d_embeddings",
            "folds": 10,
            "shuffle": False,
            "threshold_grid": "np.arange(0,4,0.01)",
            "horizontal_flip_tta": True,
            "feature_fusion": "AdaFace norm-aware original+flip fusion",
            "bgr_normalization": "(pixel/255 - 0.5)/0.5",
        },
        "observed_accuracy": observed,
        "delta_to_published_reference": observed - 0.9926,
        "delta_to_frozen_minimum": observed - 0.9896,
        "would_meet_frozen_minimum_if_this_were_the_preregistered_source": observed >= 0.9896,
        "metrics": metrics,
        "diagnostics": diagnostics,
        "embedding_digest": mod.sha256_bytes(
            np.ascontiguousarray(embeddings.astype(np.float32)).tobytes(order="C")
        ),
        "interpretation_boundary": (
            "Post-outcome source diagnostic only. This result cannot alter the canonical CFP-FP "
            "FAIL or authorize Study 1B without a separately reviewed correction/replay decision."
        ),
    }

    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
