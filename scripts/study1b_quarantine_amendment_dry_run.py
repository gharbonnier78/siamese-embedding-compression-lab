"""Simulation à blanc non active du projet de quarantaine Study 1B.

Ce script ne modifie pas la frontière officielle. Il vérifie seulement, à partir du manifeste
pseudonymisé du preflight, les effectifs, les capacités de paires, l'audit perceptuel restant
et les hashes de graphes qui résulteraient de l'amendement proposé.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from siamese_compression_lab.study1b_preflight import (
    PAIR_COUNTS,
    Capture,
    _cross_role_duplicate_audit,
    make_pair_graph,
    write_pair_graph,
)

QUARANTINED_SUBJECTS = {
    "subject_1070cf723eb7b93398de",
    "subject_97df35f042b9b8c49b8e",
    "subject_fb92b5fb0163ff4b3751",
    "subject_815e0549ed1f8d0514b4",
}


def _load_captures(path: Path) -> list[Capture]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    captures = []
    for row in rows:
        captures.append(
            Capture(
                subject_id=row["subject_id"],
                capture_id=row["capture_id"],
                role=row["role"],
                relative_path="not_persisted",
                sha256=row["source_sha256"],
                dhash64=int(row["dhash64_hex"], 16),
            )
        )
    return captures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    all_captures = _load_captures(args.capture_manifest)
    observed_subjects = {capture.subject_id for capture in all_captures}
    missing = sorted(QUARANTINED_SUBJECTS - observed_subjects)
    if missing:
        raise ValueError(f"quarantine subjects missing from manifest: {missing}")
    captures = [
        capture for capture in all_captures if capture.subject_id not in QUARANTINED_SUBJECTS
    ]

    audit = _cross_role_duplicate_audit(captures)
    role_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for capture in captures:
        role_counts[capture.role][capture.subject_id] += 1

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    graph_hashes = {}
    roles = {}
    for role in ("TRAIN", "VALIDATION", "SCREEN", "TEST"):
        subject_counts = role_counts[role]
        genuine_needed, impostor_needed = PAIR_COUNTS[role]
        total_captures = sum(subject_counts.values())
        genuine_capacity = sum(count * (count - 1) // 2 for count in subject_counts.values())
        same_subject_ordered = sum(count**2 for count in subject_counts.values())
        impostor_capacity = (total_captures**2 - same_subject_ordered) // 2
        graph = make_pair_graph(role, captures, genuine_needed, impostor_needed)
        graph_hashes[role] = write_pair_graph(
            output_dir / "graphs" / f"{role.lower()}_pairs.csv",
            graph,
        )
        roles[role] = {
            "identities": len(subject_counts),
            "captures": total_captures,
            "eligible_genuine_identities": sum(count >= 2 for count in subject_counts.values()),
            "genuine_capacity": genuine_capacity,
            "genuine_pairs_requested": genuine_needed,
            "impostor_capacity": impostor_capacity,
            "impostor_pairs_requested": impostor_needed,
        }

    result = {
        "schema_version": 1,
        "kind": "study1b_quarantine_amendment_dry_run",
        "amendment_active": False,
        "scientific_outcomes_opened": False,
        "quarantined_subjects": sorted(QUARANTINED_SUBJECTS),
        "quarantined_capture_count": len(all_captures) - len(captures),
        "roles": roles,
        "proposed_graph_sha256": graph_hashes,
        "remaining_duplicate_audit": audit,
        "note": (
            "Dry run only. Proposed hashes are not official Study 1B graph hashes until "
            "independent review and explicit human activation of the amendment."
        ),
    }
    (output_dir / "quarantine_dry_run.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
