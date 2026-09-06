"""Audit whether S3 can add genuinely distinct pair information without outcomes."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def _read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_graph(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--test-graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = [row for row in _read_manifest(args.manifest) if row["role"] == "TEST"]
    graph = _read_graph(args.test_graph)
    by_subject: dict[str, list[str]] = defaultdict(list)
    for row in manifest:
        by_subject[row["subject_id"]].append(row["capture_id"])

    genuine_capacity = sum(len(v) * (len(v) - 1) // 2 for v in by_subject.values())
    subjects = sorted(by_subject)
    identity_pair_capacity = len(subjects) * (len(subjects) - 1) // 2

    used_genuine_edges = {
        tuple(sorted((r["capture_id_1"], r["capture_id_2"])))
        for r in graph if int(r["same"]) == 1
    }
    used_impostor_identity_pairs = {
        tuple(sorted((r["subject_slot_id_1"], r["subject_slot_id_2"])))
        for r in graph if int(r["same"]) == 0
    }

    base_genuine = len(used_genuine_edges)
    base_impostor = sum(1 for r in graph if int(r["same"]) == 0)
    unused_genuine_edges = genuine_capacity - len(used_genuine_edges)
    unused_impostor_identity_pairs = identity_pair_capacity - len(used_impostor_identity_pairs)

    multipliers = [1.0, 1.5, 2.0]
    candidates = []
    for m in multipliers:
        target_g = round(base_genuine * m)
        target_i = round(base_impostor * m)
        add_g = max(0, target_g - base_genuine)
        add_i = max(0, target_i - base_impostor)
        genuine_feasible = add_g <= unused_genuine_edges
        # Contract is conservative: additional impostor information must correspond to
        # previously unused identity pairs, not merely more capture combinations.
        impostor_feasible = add_i <= unused_impostor_identity_pairs
        candidates.append({
            "multiplier": m,
            "target_genuine_pairs": target_g,
            "target_impostor_pairs": target_i,
            "additional_genuine_pairs_required": add_g,
            "additional_impostor_pairs_required": add_i,
            "unused_distinct_genuine_capture_pairs_available": unused_genuine_edges,
            "unused_distinct_impostor_identity_pairs_available": unused_impostor_identity_pairs,
            "genuine_distinct_information_feasible": genuine_feasible,
            "impostor_distinct_information_feasible": impostor_feasible,
            "s3_information_multiplier_feasible": genuine_feasible and impostor_feasible,
        })

    report = {
        "schema_version": "1.0",
        "kind": "study1b_s3_information_feasibility_audit",
        "analysis_phase": "S3_INFORMATION_FEASIBILITY_ONLY",
        "scientific_outcomes_opened": False,
        "canonical_gate_replaced": False,
        "amendment_activated": False,
        "test_role_identities": len(subjects),
        "test_role_captures": len(manifest),
        "existing_graph": {"genuine_pairs": base_genuine, "impostor_pairs": base_impostor},
        "source_capacity": {
            "unique_genuine_capture_pairs": genuine_capacity,
            "unique_impostor_identity_pairs": identity_pair_capacity,
            "unused_distinct_genuine_capture_pairs": unused_genuine_edges,
            "unused_distinct_impostor_identity_pairs": unused_impostor_identity_pairs,
        },
        "candidate_information_multipliers": candidates,
        "interpretation_rule": (
            "A multiplier is feasible only if required additional genuine rows can use previously unused "
            "capture pairs and required additional impostor rows can use previously unused identity pairs. "
            "This audit does not claim independence beyond those structural distinctions and opens no outcomes."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
