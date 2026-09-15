"""Study 1B outcome runner.

This file is executable scaffolding only. It cannot run SCREEN or qualification unless a
separate human authorization artifact exists and is bound to the exact protocol hash.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from siamese_compression_lab.metrics import evaluate_benchmark_at_fmr
from siamese_compression_lab.models import RawProjection, pair_distances
from siamese_compression_lab.study1b_execution import (
    PCA128,
    EmbeddingTable,
    Random128,
    append_progress,
    assert_outcome_authorized,
    fit_siamese128,
    graph_to_split,
    load_pair_graph,
    seed_token,
    serialize_transform,
)
from siamese_compression_lab.study1b_statistics import subject_bootstrap_summary
from siamese_compression_lab.subject_bootstrap import SubjectPairRow


def _subject_rows(graph: list[dict[str, str]]) -> list[SubjectPairRow]:
    return [
        SubjectPairRow(
            pair_id=row["pair_id"],
            same=int(row["same"]),
            subject_slot_id_1=row["subject_slot_id_1"],
            subject_slot_id_2=row["subject_slot_id_2"],
            source_class="study1b_frozen_graph",
            source_row=index,
        )
        for index, row in enumerate(graph)
    ]


def _distances(model, split) -> np.ndarray:
    return pair_distances(model, split)


def _candidate_models(seed_label: int, train, validation, unique_train: np.ndarray):
    yield "random128", Random128.fit(seed_label)
    yield "pca128", PCA128.fit(unique_train, seed_label)
    yield "siamese128", fit_siamese128(train, validation, seed_label)


def _stage_config(stage: str) -> tuple[str, tuple[int, ...], float, int]:
    if stage == "SCREEN":
        return "SCREEN", (11, 29), 0.95, 10_000
    if stage == "QUALIFICATION":
        return "TEST", (11, 29, 47, 71, 101), 0.975, 10_000
    raise ValueError(stage)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--embedding-table", type=Path, required=True)
    parser.add_argument("--graphs-dir", type=Path, required=True)
    parser.add_argument("--stage", choices=["SCREEN", "QUALIFICATION"], required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    authorization = assert_outcome_authorized(args.authorization, args.protocol)
    allowed = set(authorization.get("allowed_stages", []))
    if args.stage not in allowed:
        raise PermissionError(f"authorization does not include stage {args.stage}")

    role, seed_labels, ucb_level, bootstrap_replicates = _stage_config(args.stage)
    table = EmbeddingTable.load(args.embedding_table)
    graphs = {
        name: load_pair_graph(args.graphs_dir / f"{name.lower()}_pairs.csv")
        for name in ("TRAIN", "VALIDATION", role)
    }
    train = graph_to_split("TRAIN", graphs["TRAIN"], table)
    validation = graph_to_split("VALIDATION", graphs["VALIDATION"], table)
    target = graph_to_split(role, graphs[role], table)
    subject_rows = _subject_rows(graphs[role])
    unique_train = table.unique_role_captures("TRAIN")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    progress = args.output_dir / "progress.jsonl"
    transforms_dir = args.output_dir / "transforms"
    raw = RawProjection(512)
    raw_distances = _distances(raw, target)
    raw_result, _ = evaluate_benchmark_at_fmr(target.same, raw_distances, target_fmr=0.01)
    rows = []

    for seed_label in seed_labels:
        for method, model in _candidate_models(seed_label, train, validation, unique_train):
            append_progress(
                progress,
                {"event": "route_started", "stage": args.stage, "method": method, "seed": seed_label},
            )
            transform_path = transforms_dir / f"{method}_seed_{seed_label}.npz"
            transform_sha = serialize_transform(transform_path, method, model, seed_label)
            candidate_distances = _distances(model, target)
            candidate_result, _ = evaluate_benchmark_at_fmr(
                target.same, candidate_distances, target_fmr=0.01
            )
            bootstrap = subject_bootstrap_summary(
                rows=subject_rows,
                candidate_distances=candidate_distances,
                reference_distances=raw_distances,
                target_fmr=0.01,
                replicates=bootstrap_replicates,
                seed=seed_token(
                    f"bootstrap|stage={args.stage}|method={method}|seed={seed_label}"
                ),
            )
            point_delta = candidate_result.fnmr - raw_result.fnmr
            selected_ucb = (
                bootstrap.delta_fnmr_ucb_95
                if ucb_level == 0.95
                else bootstrap.delta_fnmr_ucb_97_5
            )
            row = {
                "stage": args.stage,
                "role": role,
                "method": method,
                "seed_label": seed_label,
                "target_fmr": 0.01,
                "point_delta_fnmr": point_delta,
                "ucb_level": ucb_level,
                "delta_fnmr_ucb": selected_ucb,
                "bootstrap_status": bootstrap.status,
                "degenerate_fraction": bootstrap.degenerate_fraction,
                "transform_sha256": transform_sha,
                "raw512_embedding_table_sha256": table.source_sha256,
                "scientific_outcome": True,
            }
            rows.append(row)
            append_progress(progress, {"event": "route_completed", **row})

    (args.output_dir / "results.json").write_text(
        json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"stage": args.stage, "rows": len(rows)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
