"""End-to-end experiment with leakage guards and MMALS-compatible replay output."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from .config import ExperimentConfig, config_dict, validate_config
from .data import DatasetBundle, make_synthetic_bundle, summarize_splits
from .metrics import (
    bootstrap_paired_fnmr_at_fmr,
    evaluate_at_threshold,
    evaluate_benchmark_at_fmr,
    fmr_resolution,
    threshold_at_fmr,
)
from .models import (
    PCAProjection,
    RandomProjection,
    RawProjection,
    SiameseLinearProjection,
    pair_distances,
)
from .plots import plot_fnmr, plot_roc_curves, plot_storage, plot_training_history
from .replay import ReplayRecorder, deterministic_run_id, write_csv


def load_dataset(config: ExperimentConfig) -> DatasetBundle:
    if config.data.mode == "synthetic":
        return make_synthetic_bundle(config.data)
    if config.data.mode == "lfw":
        from .lfw import make_lfw_bundle

        return make_lfw_bundle(config)
    raise ValueError(f"unsupported data mode: {config.data.mode}")


def _save_projection(model: Any, model_dir: Path, model_id: str) -> None:
    model_dir.mkdir(parents=True, exist_ok=True)
    path = model_dir / f"{model_id}.npz"
    if isinstance(model, RawProjection):
        np.savez(path, model_type="raw", input_dim=model.input_dim)
    elif isinstance(model, RandomProjection):
        np.savez(path, model_type="random", matrix=model.matrix, seed=model.seed)
    elif isinstance(model, PCAProjection):
        assert model.pca is not None
        np.savez(
            path,
            model_type="pca",
            components=model.pca.components_,
            mean=model.pca.mean_,
            explained_variance=model.pca.explained_variance_,
            seed=model.seed,
        )
    elif isinstance(model, SiameseLinearProjection):
        np.savez(
            path,
            model_type="siamese_linear",
            weights=model.weights,
            bias=model.bias,
            seed=model.seed,
            margin=model.margin,
            best_epoch=model.best_epoch,
        )
    else:
        raise TypeError(type(model))


def _routes(config: ExperimentConfig, input_dim: int) -> list[tuple[str, int, Any]]:
    first_seed = config.training.seeds[0]
    routes: list[tuple[str, int, Any]] = [("raw", first_seed, RawProjection(input_dim))]
    for seed in config.training.seeds:
        routes.extend(
            [
                (
                    "random",
                    seed,
                    RandomProjection(input_dim, config.training.output_dim, seed),
                ),
                ("pca", seed, PCAProjection(input_dim, config.training.output_dim, seed)),
                (
                    "siamese",
                    seed,
                    SiameseLinearProjection(
                        input_dim=input_dim,
                        output_dim=config.training.output_dim,
                        seed=seed,
                        margin=config.training.contrastive_margin,
                        learning_rate=config.training.learning_rate,
                        weight_decay=config.training.weight_decay,
                        epochs=config.training.epochs,
                        batch_size=config.training.batch_size,
                        patience=config.training.patience,
                        minimum_improvement=config.training.minimum_improvement,
                    ),
                ),
            ]
        )
    return routes


def run_experiment(
    config: ExperimentConfig,
    output_root: str | Path,
    *,
    dataset: DatasetBundle | None = None,
) -> Path:
    """Run once; an existing deterministic run directory is never silently overwritten."""
    validate_config(config)
    dataset = dataset or load_dataset(config)
    dataset.validate_no_identity_leakage()
    split_rows = summarize_splits(dataset)
    data_digest = "".join(row["sha256"] for row in split_rows)
    run_id = deterministic_run_id(config, data_digest)
    run_dir = Path(output_root) / run_id
    if run_dir.exists():
        raise FileExistsError(f"run already exists and will not be overwritten: {run_dir}")
    run_dir.mkdir(parents=True)
    (run_dir / "figures").mkdir()
    (run_dir / "models").mkdir()

    (run_dir / "config.resolved.yaml").write_text(
        yaml.safe_dump(config_dict(config), sort_keys=True), encoding="utf-8"
    )
    write_csv(run_dir / "split_summary.csv", split_rows)
    recorder = ReplayRecorder(config=config, run_dir=run_dir, run_id=run_id)
    recorder.event(
        "configuration_frozen",
        "setup",
        payload={"seeds": list(config.training.seeds), "target_fmrs": list(config.evaluation.target_fmrs)},
    )
    recorder.audit(
        "identity_disjointness_check",
        rationale="Prevent identity leakage across TRAIN, VALIDATION and TEST.",
        outputs={"status": "no_overlap", "split_digests": split_rows},
    )
    recorder.event(
        "dataset_validated",
        "setup",
        payload={"splits": split_rows, "metadata": dataset.metadata},
    )
    recorder.audit(
        "test_seal",
        rationale="TEST is excluded from fitting, early stopping and threshold selection.",
        outputs={"threshold_source": "validation", "test_use": "final_evaluation_only"},
    )

    route_rows: list[dict[str, Any]] = []
    result_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    threshold_rows: list[dict[str, Any]] = []
    benchmark_threshold_rows: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    training_history_rows: list[dict[str, Any]] = []
    distance_cache: dict[tuple[str, int], dict[str, Any]] = {}
    frozen_routes: list[tuple[str, int, Any, str]] = []

    for method, seed, model in _routes(config, dataset.train.input_dim):
        model_id = f"{method}_seed_{seed}"
        recorder.event(
            "route_started",
            "fit",
            payload={"route_id": model_id, "method": method, "seed": seed},
        )
        start = time.perf_counter()
        if isinstance(model, PCAProjection):
            model.fit(dataset.train)
        elif isinstance(model, SiameseLinearProjection):
            model.fit(dataset.train, dataset.validation)
            for history in model.history:
                training_history_rows.append(
                    {"method": method, "seed": seed, **history, "evidence_kind": "observed"}
                )
        fit_seconds = time.perf_counter() - start
        _save_projection(model, run_dir / "models", model_id)

        validation_distances = pair_distances(model, dataset.validation)
        distance_cache[(method, seed)] = {
            "validation": validation_distances,
        }
        route_rows.append(
            {
                "run_id": run_id,
                "objective_id": config.replay.objective_id,
                "route_id": model_id,
                "method": method,
                "seed": seed,
                "source_dim": dataset.train.input_dim,
                "target_dim": model.output_dim,
                "trainable_parameters": model.trainable_parameters,
                "template_bytes_float32": model.output_dim * config.evaluation.template_dtype_bytes,
                "fit_seconds": fit_seconds,
                "status": "completed",
                "evidence_kind": "observed",
            }
        )

        for target_fmr in config.evaluation.target_fmrs:
            threshold, threshold_evidence = threshold_at_fmr(
                dataset.validation.same, validation_distances, target_fmr
            )
            calibration_status = (
                "ADEQUATE_FOR_EXPLORATORY_THRESHOLD"
                if int(threshold_evidence["n_validation_impostors"])
                >= config.evaluation.minimum_validation_impostors
                else "UNDERPOWERED_VALIDATION_IMPOSTOR_COUNT"
            )
            threshold_rows.append(
                {
                    "run_id": run_id,
                    "method": method,
                    "seed": seed,
                    "target_fmr": target_fmr,
                    "threshold": threshold,
                    "threshold_source": "validation",
                    "calibration_status": calibration_status,
                    **threshold_evidence,
                }
            )
            recorder.audit(
                "threshold_frozen",
                rationale="Select the largest validation threshold meeting the pre-specified FMR target.",
                inputs={"route_id": model_id, "target_fmr": target_fmr},
                outputs={
                    "threshold": threshold,
                    "calibration_status": calibration_status,
                    **threshold_evidence,
                },
            )
        frozen_routes.append((method, seed, model, model_id))
        recorder.event(
            "route_completed",
            "fit",
            payload={
                "route_id": model_id,
                "fit_seconds": fit_seconds,
                "thresholds_frozen": True,
            },
        )

    recorder.event(
        "test_opened_once",
        "test",
        payload={
            "purpose": "frozen-model evaluation",
            "selection_prohibited": True,
            "n_pairs": dataset.test.n_pairs,
        },
    )
    recorder.audit(
        "test_label_usage",
        rationale=(
            "Test labels are excluded from training and deployable threshold calibration; "
            "they locate equal-FMR benchmark points and paired uncertainty only."
        ),
        outputs={
            "used_for_training": False,
            "used_for_deployable_threshold": False,
            "used_for_equal_fmr_benchmark": True,
            "used_for_reporting": True,
        },
    )

    for method, seed, model, model_id in frozen_routes:
        test_distances = pair_distances(model, dataset.test)
        distance_cache[(method, seed)]["test"] = test_distances
        for target_fmr in config.evaluation.target_fmrs:
            threshold_row = next(
                row
                for row in threshold_rows
                if row["method"] == method
                and int(row["seed"]) == seed
                and float(row["target_fmr"]) == target_fmr
            )
            operating_result = evaluate_at_threshold(
                dataset.test.same,
                test_distances,
                threshold=float(threshold_row["threshold"]),
                target_fmr=target_fmr,
                threshold_source="validation",
            )
            benchmark_result, benchmark_evidence = evaluate_benchmark_at_fmr(
                dataset.test.same, test_distances, target_fmr=target_fmr
            )
            benchmark_threshold_rows.append(
                {
                    "run_id": run_id,
                    "method": method,
                    "seed": seed,
                    "target_fmr": target_fmr,
                    "threshold": benchmark_result.threshold,
                    "threshold_source": "test_benchmark_only",
                    "deployable": False,
                    **benchmark_evidence,
                }
            )
            evaluations = (
                ("validation_frozen_operating_point", operating_result),
                ("test_equal_fmr_benchmark", benchmark_result),
            )
            for metric_protocol, result in evaluations:
                result_row = {
                    "run_id": run_id,
                    "method": method,
                    "seed": seed,
                    "model_id": model_id,
                    "metric_protocol": metric_protocol,
                    **result.as_dict(),
                    "test_fmr_resolution": fmr_resolution(result.n_impostor),
                    "evidence_level": dataset.metadata["evidence_level"],
                }
                result_rows.append(result_row)
                for metric_name in (
                    "fmr",
                    "fnmr",
                    "tmr",
                    "accuracy",
                    "balanced_accuracy",
                    "auc",
                    "eer",
                    "threshold",
                ):
                    metric_rows.append(
                        {
                            "run_id": run_id,
                            "objective_id": config.replay.objective_id,
                            "route_id": model_id,
                            "split": "test",
                            "metric_protocol": metric_protocol,
                            "metric": metric_name,
                            "value": result_row[metric_name],
                            "target_fmr": target_fmr,
                            "threshold_source": result.threshold_source,
                            "evidence_kind": "observed",
                        }
                    )
        prediction_frames.append(
            pd.DataFrame(
                {
                    "run_id": run_id,
                    "method": method,
                    "seed": seed,
                    "pair_id": dataset.test.pair_id,
                    "same": dataset.test.same,
                    "distance": test_distances,
                }
            )
        )
        recorder.event(
            "route_test_evaluated",
            "test",
            payload={
                "route_id": model_id,
                "operating_threshold_source": "validation",
                "benchmark_threshold_source": "test_benchmark_only",
            },
        )

    raw_seed = config.training.seeds[0]
    noninferiority_rows: list[dict[str, Any]] = []
    for row in result_rows:
        if row["method"] == "raw" or row["metric_protocol"] != "test_equal_fmr_benchmark":
            continue
        target_fmr = float(row["target_fmr"])
        candidate_key = (str(row["method"]), int(row["seed"]))
        delta = bootstrap_paired_fnmr_at_fmr(
            same=dataset.test.same,
            candidate_distances=distance_cache[candidate_key]["test"],
            reference_distances=distance_cache[("raw", raw_seed)]["test"],
            target_fmr=target_fmr,
            replicates=config.evaluation.bootstrap_replicates,
            seed=config.evaluation.bootstrap_seed + int(row["seed"]),
        )
        if dataset.metadata["evidence_level"] == "synthetic_smoke":
            decision = "SMOKE_ONLY_NOT_ASSESSED"
        else:
            decision = (
                "NONINFERIOR_EXPLORATORY"
                if delta["delta_fnmr_ci_high"] <= config.evaluation.noninferiority_delta_fnmr
                else "NONINFERIORITY_NOT_SHOWN"
            )
        noninferiority_rows.append(
            {
                "run_id": run_id,
                "candidate_method": row["method"],
                "candidate_seed": row["seed"],
                "reference_method": "raw",
                "target_fmr": target_fmr,
                "noninferiority_margin_fnmr": config.evaluation.noninferiority_delta_fnmr,
                "metric_protocol": "test_equal_fmr_benchmark",
                "deployable_threshold": False,
                **delta,
                "decision": decision,
                "evidence_level": dataset.metadata["evidence_level"],
            }
        )

    seed_decisions = pd.DataFrame(noninferiority_rows)
    method_noninferiority_rows: list[dict[str, Any]] = []
    for (method, target_fmr), frame in seed_decisions.groupby(
        ["candidate_method", "target_fmr"], sort=True
    ):
        if dataset.metadata["evidence_level"] == "synthetic_smoke":
            method_decision = "SMOKE_ONLY_NOT_ASSESSED"
        else:
            method_decision = (
                "ROBUST_NONINFERIORITY_SHOWN_ALL_SEEDS"
                if (frame.decision == "NONINFERIOR_EXPLORATORY").all()
                else "NONINFERIORITY_NOT_SHOWN_ACROSS_ALL_SEEDS"
            )
        method_noninferiority_rows.append(
            {
                "run_id": run_id,
                "candidate_method": method,
                "target_fmr": target_fmr,
                "predeclared_seeds": len(config.training.seeds),
                "seeds_evaluated": int(frame.candidate_seed.nunique()),
                "worst_delta_fnmr_ci_high": float(frame.delta_fnmr_ci_high.max()),
                "mean_delta_fnmr": float(frame.delta_fnmr_mean.mean()),
                "noninferiority_margin_fnmr": config.evaluation.noninferiority_delta_fnmr,
                "method_decision": method_decision,
                "metric_protocol": "test_equal_fmr_benchmark",
            }
        )

    storage_rows: list[dict[str, Any]] = []
    method_dimensions = {"raw": dataset.train.input_dim, "random": config.training.output_dim,
                         "pca": config.training.output_dim, "siamese": config.training.output_dim}
    for method, dimension in method_dimensions.items():
        for gallery_size in config.evaluation.gallery_sizes:
            total_bytes = gallery_size * dimension * config.evaluation.template_dtype_bytes
            storage_rows.append(
                {
                    "method": method,
                    "template_dim": dimension,
                    "gallery_size": gallery_size,
                    "template_bytes": dimension * config.evaluation.template_dtype_bytes,
                    "gallery_bytes": total_bytes,
                    "gallery_gib": total_bytes / (1024**3),
                    "evidence_kind": "derived",
                }
            )

    results_df = pd.DataFrame(result_rows)
    predictions_df = pd.concat(prediction_frames, ignore_index=True)
    history_df = pd.DataFrame(training_history_rows)
    storage_df = pd.DataFrame(storage_rows)
    results_df.to_csv(run_dir / "results_wide.csv", index=False)
    predictions_df.to_csv(run_dir / "test_pair_scores.csv", index=False)
    history_df.to_csv(run_dir / "training_history.csv", index=False)
    storage_df.to_csv(run_dir / "storage_engineering.csv", index=False)
    write_csv(run_dir / "routes.csv", route_rows)
    write_csv(run_dir / "metrics.csv", metric_rows)
    write_csv(run_dir / "thresholds.csv", threshold_rows)
    write_csv(run_dir / "benchmark_thresholds_non_deployable.csv", benchmark_threshold_rows)
    write_csv(run_dir / "paired_noninferiority.csv", noninferiority_rows)
    write_csv(run_dir / "method_noninferiority_summary.csv", method_noninferiority_rows)

    method_summary = (
        results_df.groupby(["method", "target_fmr", "metric_protocol"], as_index=False)
        .agg(
            seeds=("seed", "nunique"),
            fnmr_mean=("fnmr", "mean"),
            fnmr_std=("fnmr", "std"),
            fmr_mean=("fmr", "mean"),
            auc_mean=("auc", "mean"),
            eer_mean=("eer", "mean"),
        )
        .fillna(0.0)
    )
    method_summary.to_csv(run_dir / "method_summary.csv", index=False)
    plot_roc_curves(predictions_df, run_dir / "figures" / "roc_test.png")
    plot_fnmr(results_df, run_dir / "figures" / "fnmr_at_target_fmr.png")
    plot_training_history(history_df, run_dir / "figures" / "siamese_validation_loss.png")
    plot_storage(storage_df, run_dir / "figures" / "gallery_storage.png")

    recorder.event(
        "paired_analysis_completed",
        "analysis",
        evidence_kind="derived",
        payload={"bootstrap_replicates": config.evaluation.bootstrap_replicates},
    )
    recorder.audit(
        "scientific_status_assignment",
        rationale="Synthetic runs validate code paths only; LFW runs support limited benchmark claims only.",
        outputs={
            "evidence_level": dataset.metadata["evidence_level"],
            "scientific_claim_allowed": dataset.metadata["scientific_claim_allowed"],
        },
    )
    run_status = (
        "SMOKE_VALIDATED"
        if dataset.metadata["evidence_level"] == "synthetic_smoke"
        else "BENCHMARK_EXECUTED"
    )
    recorder.event("run_completed", "finalize", status=run_status)
    compact_summary = {
        "methods": method_summary.to_dict(orient="records"),
        "seed_level_noninferiority": noninferiority_rows,
        "method_level_noninferiority": method_noninferiority_rows,
        "limitations": [
            dataset.metadata.get("warning", "Benchmark scope is limited to its stated protocol."),
            "A test-set EER is descriptive and is not a deployable threshold.",
            "Equal-FMR test thresholds compare embeddings but are explicitly non-deployable.",
            "A 1% FMR operating point is coarse when the test set contains few impostor pairs.",
        ],
    }
    recorder.finalize(
        run_status=run_status,
        evidence_level=str(dataset.metadata["evidence_level"]),
        scientific_claim_allowed=bool(dataset.metadata["scientific_claim_allowed"]),
        dataset_metadata={**dataset.metadata, "splits": split_rows},
        compact_summary=compact_summary,
    )
    return run_dir
