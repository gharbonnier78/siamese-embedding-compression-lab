"""Materialize the active Study 1B amended data boundary without biometric outcomes."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from siamese_compression_lab.study1b_preflight import (
    PAIR_COUNTS,
    _cross_role_duplicate_audit,
    _parse_people_file,
    assign_roles,
    make_pair_graph,
    materialize_captures,
    sha256_file,
    write_pair_graph,
)

QUARANTINE = {
    "subject_1070cf723eb7b93398de": "SCREEN",
    "subject_97df35f042b9b8c49b8e": "TRAIN",
    "subject_fb92b5fb0163ff4b3751": "TEST",
    "subject_815e0549ed1f8d0514b4": "TRAIN",
}

EXPECTED_IDENTITY_COUNTS = {"TRAIN": 2825, "VALIDATION": 606, "SCREEN": 604, "TEST": 1710}
EXPECTED_MANIFEST_SHA256 = "767f9fe8d1d8466a0e722f826b26875a0e852f525f7413a9658a307a9639366e"
EXPECTED_GRAPH_SHA256 = {
    "TRAIN": "a0951ead4109d615d6854b7e60cc16d62319ae828137d160d3e08f5e669d0706",
    "VALIDATION": "fb849558e0b09b0fa7ff301991af010815f0b4ee98ab62faa1c585477f9f8601",
    "SCREEN": "c0d36757121f54c4585d2298a1b02c401606ce939c7be2bedd070c03adf233f7",
    "TEST": "08c86ca9a641fc96b74014ae1974f713cd00e558dd98946ac32ff440c4666f85",
}


def _write_manifest(path: Path, captures) -> str:
    rows = [
        {
            "subject_id": item.subject_id,
            "capture_id": item.capture_id,
            "role": item.role,
            "source_sha256": item.sha256,
            "dhash64_hex": f"{item.dhash64:016x}",
        }
        for item in captures
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return sha256_file(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = args.dataset_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    dev_train = _parse_people_file(root / "peopleDevTrain.txt")
    dev_test = _parse_people_file(root / "peopleDevTest.txt")
    roles = assign_roles(dev_train, dev_test)
    all_captures = materialize_captures(root, roles, {**dev_train, **dev_test})

    observed = defaultdict(set)
    for capture in all_captures:
        observed[capture.subject_id].add(capture.role)
    for subject_id, expected_role in QUARANTINE.items():
        if observed.get(subject_id) != {expected_role}:
            raise RuntimeError(
                f"active amendment subject mismatch: {subject_id} -> {sorted(observed.get(subject_id, set()))}"
            )

    captures = [item for item in all_captures if item.subject_id not in QUARANTINE]
    audit = _cross_role_duplicate_audit(captures)
    (output_dir / "overlap_near_duplicate_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if audit["exact_duplicate_blocking"]:
        raise RuntimeError("active amended boundary still contains exact cross-role duplicates")

    manifest_hash = _write_manifest(output_dir / "capture_manifest.csv", captures)
    if manifest_hash != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError(
            f"active amended manifest hash mismatch: {manifest_hash} != {EXPECTED_MANIFEST_SHA256}"
        )

    counts_by_role_subject: dict[str, Counter[str]] = defaultdict(Counter)
    for capture in captures:
        counts_by_role_subject[capture.role][capture.subject_id] += 1

    role_summary = {}
    graph_hashes = {}
    for role in ("TRAIN", "VALIDATION", "SCREEN", "TEST"):
        genuine, impostor = PAIR_COUNTS[role]
        graph = make_pair_graph(role, captures, genuine, impostor)
        graph_hash = write_pair_graph(output_dir / "graphs" / f"{role.lower()}_pairs.csv", graph)
        graph_hashes[role] = graph_hash
        if graph_hash != EXPECTED_GRAPH_SHA256[role]:
            raise RuntimeError(
                f"{role}: active amended graph hash mismatch: {graph_hash} != {EXPECTED_GRAPH_SHA256[role]}"
            )
        subject_counts = counts_by_role_subject[role]
        if len(subject_counts) != EXPECTED_IDENTITY_COUNTS[role]:
            raise RuntimeError(
                f"{role}: active amended identity count mismatch: {len(subject_counts)} != {EXPECTED_IDENTITY_COUNTS[role]}"
            )
        role_captures = [item for item in captures if item.role == role]
        role_summary[role] = {
            "identities": len(subject_counts),
            "captures": len(role_captures),
            "eligible_genuine_identities": sum(value >= 2 for value in subject_counts.values()),
            "genuine_pairs": genuine,
            "impostor_pairs": impostor,
        }

    report = {
        "schema_version": "1.0",
        "kind": "study1b_lfw_active_amended_non_outcome_preflight",
        "boundary_amendment": "STUDY1B_DATA_BOUNDARY_AMENDMENT_2026-08-28",
        "boundary_status": "ACTIVE_PREOUTCOME_DATA_BOUNDARY",
        "scientific_outcomes_opened": False,
        "excluded_identity_count": len(QUARANTINE),
        "excluded_identities": sorted(QUARANTINE),
        "source": {"capture_manifest_sha256": manifest_hash},
        "roles": role_summary,
        "graph_sha256": graph_hashes,
        "exact_duplicate_audit": "PASS",
        "near_duplicate_review_required": bool(audit["near_duplicate_review_required"]),
        "overall_status": (
            "PASS_PENDING_NEAR_DUPLICATE_REVIEW"
            if audit["near_duplicate_review_required"]
            else "PASS"
        ),
    }
    (output_dir / "preflight_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
