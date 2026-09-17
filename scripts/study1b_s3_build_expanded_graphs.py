"""Build frozen S3 x1.5/x2.0 TEST information graphs without biometric outcomes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

BASE_TEST_GRAPH_SHA256 = "08c86ca9a641fc96b74014ae1974f713cd00e558dd98946ac32ff440c4666f85"
BASE_MANIFEST_SHA256 = "767f9fe8d1d8466a0e722f826b26875a0e852f525f7413a9658a307a9639366e"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return sha256_file(path)


def canonical(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a < b else (b, a)


def select_capture(subject: str, other_subject: str, by_subject: dict[str, list[str]]) -> str:
    candidates = by_subject[subject]
    return min(
        candidates,
        key=lambda cap: (digest(f"study1b-s3-capture-v1|{other_subject}|{cap}"), cap),
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--base-test-graph", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()

    manifest_hash = sha256_file(args.manifest)
    graph_hash = sha256_file(args.base_test_graph)
    if manifest_hash != BASE_MANIFEST_SHA256:
        raise RuntimeError(f"manifest hash mismatch: {manifest_hash} != {BASE_MANIFEST_SHA256}")
    if graph_hash != BASE_TEST_GRAPH_SHA256:
        raise RuntimeError(f"base TEST graph hash mismatch: {graph_hash} != {BASE_TEST_GRAPH_SHA256}")

    manifest = [r for r in read_csv(args.manifest) if r["role"] == "TEST"]
    base = read_csv(args.base_test_graph)
    fields = list(base[0])
    by_subject: dict[str, list[str]] = defaultdict(list)
    for row in manifest:
        by_subject[row["subject_id"]].append(row["capture_id"])
    for captures in by_subject.values():
        captures.sort()

    base_genuine = [r for r in base if int(r["same"]) == 1]
    base_impostor = [r for r in base if int(r["same"]) == 0]
    if len(base_genuine) != 10_000 or len(base_impostor) != 100_000:
        raise RuntimeError("unexpected frozen base TEST pair counts")

    used_genuine = {canonical(r["capture_id_1"], r["capture_id_2"]) for r in base_genuine}
    used_impostor_ids = {
        canonical(r["subject_slot_id_1"], r["subject_slot_id_2"]) for r in base_impostor
    }

    genuine_pool: list[tuple[str, str, str, str]] = []
    for subject in sorted(by_subject):
        captures = by_subject[subject]
        for i, a in enumerate(captures):
            for b in captures[i + 1 :]:
                pair = canonical(a, b)
                if pair in used_genuine:
                    continue
                key = digest(f"study1b-s3-genuine-v1|{subject}|{pair[0]}|{pair[1]}")
                genuine_pool.append((key, subject, pair[0], pair[1]))
    genuine_pool.sort()

    subjects = sorted(by_subject)
    impostor_pool: list[tuple[str, str, str]] = []
    for i, a in enumerate(subjects):
        for b in subjects[i + 1 :]:
            pair = (a, b)
            if pair in used_impostor_ids:
                continue
            key = digest(f"study1b-s3-impostor-v1|{a}|{b}")
            impostor_pool.append((key, a, b))
    impostor_pool.sort()

    if len(genuine_pool) < 10_000 or len(impostor_pool) < 100_000:
        raise RuntimeError("frozen S3 x2.0 construction is no longer feasible")

    def build(multiplier: str, add_g: int, add_i: int) -> tuple[list[dict[str, str]], dict]:
        new_g = []
        for idx, (_key, subject, a, b) in enumerate(genuine_pool[:add_g]):
            new_g.append({
                "pair_id": f"test_s3{multiplier}_g_{idx:06d}",
                "same": "1",
                "subject_slot_id_1": subject,
                "subject_slot_id_2": subject,
                "capture_id_1": a,
                "capture_id_2": b,
            })

        new_i = []
        for idx, (_key, s1, s2) in enumerate(impostor_pool[:add_i]):
            c1 = select_capture(s1, s2, by_subject)
            c2 = select_capture(s2, s1, by_subject)
            if c2 < c1:
                c1, c2 = c2, c1
                s1, s2 = s2, s1
            new_i.append({
                "pair_id": f"test_s3{multiplier}_i_{idx:06d}",
                "same": "0",
                "subject_slot_id_1": s1,
                "subject_slot_id_2": s2,
                "capture_id_1": c1,
                "capture_id_2": c2,
            })

        rows = base + new_g + new_i
        new_g_units = {canonical(r["capture_id_1"], r["capture_id_2"]) for r in new_g}
        new_i_units = {canonical(r["subject_slot_id_1"], r["subject_slot_id_2"]) for r in new_i}
        if len(new_g_units) != add_g or new_g_units & used_genuine:
            raise RuntimeError(f"{multiplier}: genuine distinctness audit failed")
        if len(new_i_units) != add_i or new_i_units & used_impostor_ids:
            raise RuntimeError(f"{multiplier}: impostor distinctness audit failed")
        return rows, {
            "new_genuine_units": new_g_units,
            "new_impostor_units": new_i_units,
            "new_genuine_rows": len(new_g),
            "new_impostor_rows": len(new_i),
        }

    rows15, a15 = build("x15", 5_000, 50_000)
    rows20, a20 = build("x20", 10_000, 100_000)
    if not a15["new_genuine_units"].issubset(a20["new_genuine_units"]):
        raise RuntimeError("x1.5 genuine additions are not nested in x2.0")
    if not a15["new_impostor_units"].issubset(a20["new_impostor_units"]):
        raise RuntimeError("x1.5 impostor additions are not nested in x2.0")

    out15 = args.output_dir / "test_pairs_s3_x1_5.csv"
    out20 = args.output_dir / "test_pairs_s3_x2_0.csv"
    hash15 = write_csv(out15, rows15, fields)
    hash20 = write_csv(out20, rows20, fields)

    report = {
        "schema_version": "1.0",
        "kind": "study1b_s3_expanded_graph_construction",
        "analysis_phase": "S3_INFORMATION_CONSTRUCTION_ONLY",
        "scientific_outcomes_opened": False,
        "canonical_gate_replaced": False,
        "amendment_activated": False,
        "source": {
            "capture_manifest_sha256": manifest_hash,
            "base_test_graph_sha256": graph_hash,
            "test_identities": len(by_subject),
            "test_captures": len(manifest),
        },
        "candidate_pool": {
            "unused_distinct_genuine_capture_pairs": len(genuine_pool),
            "unused_distinct_impostor_identity_pairs": len(impostor_pool),
        },
        "graphs": {
            "x1_5": {
                "genuine_pairs": 15_000,
                "impostor_pairs": 150_000,
                "additional_genuine_pairs": 5_000,
                "additional_impostor_identity_pairs": 50_000,
                "sha256": hash15,
            },
            "x2_0": {
                "genuine_pairs": 20_000,
                "impostor_pairs": 200_000,
                "additional_genuine_pairs": 10_000,
                "additional_impostor_identity_pairs": 100_000,
                "sha256": hash20,
            },
        },
        "audits": {
            "base_rows_preserved_verbatim": True,
            "new_genuine_disjoint_from_base": True,
            "new_impostor_identity_pairs_disjoint_from_base": True,
            "x1_5_nested_in_x2_0_genuine_information": True,
            "x1_5_nested_in_x2_0_impostor_information": True,
            "status": "PASS",
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "s3_expanded_graphs_manifest.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
