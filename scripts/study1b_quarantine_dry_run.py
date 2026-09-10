"""Dry-run the proposed Study 1B identity quarantine without activating it.

This script is strictly non-outcome. It removes the four pseudonymous identities named in the
DRAFT data-boundary amendment from an in-memory copy of the LFW Study 1B boundary, rebuilds
pair graphs at the preregistered pair counts, repeats the duplicate/near-duplicate audit, and
writes a small human-review contact sheet for the two disputed cross-role pairs.

It does NOT modify the active protocol, the official preflight graphs, or any biometric score.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageDraw

from siamese_compression_lab.study1b_preflight import (
    PAIR_COUNTS,
    _cross_role_duplicate_audit,
    _find_images_root,
    _parse_people_file,
    assign_roles,
    make_pair_graph,
    materialize_captures,
    sha256_file,
    write_pair_graph,
)

QUARANTINE = {
    "subject_1070cf723eb7b93398de": {
        "role": "SCREEN",
        "reason": "BLOCK_DUPLICATE_LIKE with TRAIN; 3/3 frozen image-similarity checks passed",
        "pair": "blocking",
    },
    "subject_97df35f042b9b8c49b8e": {
        "role": "TRAIN",
        "reason": "BLOCK_DUPLICATE_LIKE with SCREEN; 3/3 frozen image-similarity checks passed",
        "pair": "blocking",
    },
    "subject_fb92b5fb0163ff4b3751": {
        "role": "TEST",
        "reason": "AMBIGUOUS_REVIEW with TRAIN; 2/3 frozen image-similarity checks passed",
        "pair": "ambiguous",
    },
    "subject_815e0549ed1f8d0514b4": {
        "role": "TRAIN",
        "reason": "AMBIGUOUS_REVIEW with TEST; 2/3 frozen image-similarity checks passed",
        "pair": "ambiguous",
    },
}

PAIR_ORDER = [
    ("subject_1070cf723eb7b93398de", "subject_97df35f042b9b8c49b8e", "BLOCKING 3/3"),
    ("subject_fb92b5fb0163ff4b3751", "subject_815e0549ed1f8d0514b4", "AMBIGUOUS 2/3"),
]


def _capture_table(captures):
    by_subject = defaultdict(list)
    for capture in captures:
        by_subject[capture.subject_id].append(capture)
    return by_subject


def _capacity(captures, role: str) -> dict[str, int]:
    by_subject = defaultdict(list)
    for capture in captures:
        if capture.role == role:
            by_subject[capture.subject_id].append(capture)
    genuine = sum(len(items) * (len(items) - 1) // 2 for items in by_subject.values())
    total = sum(len(items) for items in by_subject.values())
    same_ordered = sum(len(items) ** 2 for items in by_subject.values())
    impostor = (total**2 - same_ordered) // 2
    return {"genuine": genuine, "impostor": impostor}


def _write_manifest(path: Path, captures) -> str:
    rows = [
        {
            "subject_id": c.subject_id,
            "capture_id": c.capture_id,
            "role": c.role,
            "source_sha256": c.sha256,
            "dhash64_hex": f"{c.dhash64:016x}",
        }
        for c in captures
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return sha256_file(path)


def _contact_sheet(images_root: Path, by_subject, output: Path) -> None:
    tile = 260
    text_h = 74
    canvas = Image.new("RGB", (tile * 2, (tile + text_h) * 2), "white")
    draw = ImageDraw.Draw(canvas)
    for row, (left_subject, right_subject, label) in enumerate(PAIR_ORDER):
        for col, subject in enumerate((left_subject, right_subject)):
            captures = by_subject[subject]
            if len(captures) != 1:
                raise RuntimeError(f"expected one capture for quarantined identity {subject}")
            capture = captures[0]
            with Image.open(images_root / capture.relative_path) as source:
                image = source.convert("RGB")
                image.thumbnail((tile, tile))
                x = col * tile + (tile - image.width) // 2
                y = row * (tile + text_h) + (tile - image.height) // 2
                canvas.paste(image, (x, y))
            text_y = row * (tile + text_h) + tile + 4
            draw.text((col * tile + 4, text_y), label, fill="black")
            draw.text((col * tile + 4, text_y + 18), QUARANTINE[subject]["role"], fill="black")
            draw.text((col * tile + 4, text_y + 36), subject, fill="black")
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


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
    captures = materialize_captures(root, roles, {**dev_train, **dev_test})
    by_subject = _capture_table(captures)

    excluded = []
    for subject, metadata in QUARANTINE.items():
        items = by_subject.get(subject, [])
        if not items:
            raise RuntimeError(f"quarantine subject not found: {subject}")
        observed_roles = sorted({item.role for item in items})
        if observed_roles != [metadata["role"]]:
            raise RuntimeError(f"role mismatch for {subject}: {observed_roles}")
        excluded.append(
            {
                "subject_id": subject,
                "role": metadata["role"],
                "reason": metadata["reason"],
                "pair": metadata["pair"],
                "capture_count": len(items),
                "capture_ids": [item.capture_id for item in items],
                "source_sha256": [item.sha256 for item in items],
            }
        )

    _contact_sheet(_find_images_root(root), by_subject, output_dir / "human_review_contact_sheet.png")

    retained = [c for c in captures if c.subject_id not in QUARANTINE]
    audit = _cross_role_duplicate_audit(retained)
    (output_dir / "post_quarantine_overlap_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest_hash = _write_manifest(output_dir / "capture_manifest_quarantine_dry_run.csv", retained)

    counts = defaultdict(Counter)
    for capture in retained:
        counts[capture.role][capture.subject_id] += 1

    graphs = {}
    capacities = {}
    for role in ("TRAIN", "VALIDATION", "SCREEN", "TEST"):
        genuine_count, impostor_count = PAIR_COUNTS[role]
        cap = _capacity(retained, role)
        capacities[role] = {
            **cap,
            "required_genuine": genuine_count,
            "required_impostor": impostor_count,
            "sufficient": cap["genuine"] >= genuine_count and cap["impostor"] >= impostor_count,
        }
        graph = make_pair_graph(role, retained, genuine_count, impostor_count)
        graph_path = output_dir / "graphs" / f"{role.lower()}_pairs.csv"
        graphs[role] = write_pair_graph(graph_path, graph)

    result = {
        "schema_version": 1,
        "kind": "study1b_quarantine_dry_run",
        "status": "DRAFT_NON_ACTIVE",
        "scientific_outcomes_opened": False,
        "active_boundary_modified": False,
        "excluded_identities": excluded,
        "identity_counts_after": {role: len(counts[role]) for role in counts},
        "capacity": capacities,
        "capture_manifest_sha256": manifest_hash,
        "graph_sha256": graphs,
        "post_quarantine_audit": {
            "exact_cross_role_duplicates": len(audit["exact_cross_role_duplicates"]),
            "near_cross_role_candidates": len(audit["near_cross_role_candidates"]),
            "near_duplicate_review_required": audit["near_duplicate_review_required"],
        },
        "human_review_contact_sheet": "human_review_contact_sheet.png",
        "human_review_scope": (
            "A human may judge whether each pair appears to be the same underlying photograph/crop "
            "or a clear false-positive similarity. Human review must not identify the people and does "
            "not alter frozen thresholds retroactively."
        ),
    }
    (output_dir / "quarantine_dry_run_report.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
