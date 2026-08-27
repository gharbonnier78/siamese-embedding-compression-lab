"""Study 1B non-outcome LFW preflight.

Inspect source metadata, capture bytes, role boundaries, duplicate/near-duplicate risk and
pair-graph feasibility without computing AdaFace embeddings or verification outcomes.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image

ROOT_ENTROPY = 20260827
ROLE_NAMESPACE = "study1b-role-v1"
PUBLIC_ID_NAMESPACE = "study1b-public-id-v1"
ROLE_COUNTS = {"TRAIN": 2827, "VALIDATION": 606, "SCREEN": 605, "TEST": 1711}
PAIR_COUNTS = {
    "TRAIN": (20_000, 20_000),
    "VALIDATION": (5_000, 20_000),
    "SCREEN": (5_000, 50_000),
    "TEST": (10_000, 100_000),
}


@dataclass(frozen=True)
class Capture:
    subject_id: str
    capture_id: str
    role: str
    relative_path: str
    sha256: str
    dhash64: int


@dataclass(frozen=True)
class PairEdge:
    pair_id: str
    same: int
    subject_slot_id_1: str
    subject_slot_id_2: str
    capture_id_1: str
    capture_id_2: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _public_subject(identity: str) -> str:
    digest = hashlib.sha256(f"{PUBLIC_ID_NAMESPACE}|{identity}".encode()).hexdigest()
    return f"subject_{digest[:20]}"


def _role_key(identity: str) -> str:
    return hashlib.sha256(f"{ROLE_NAMESPACE}|{identity}".encode()).hexdigest()


def _parse_people_file(path: Path) -> dict[str, int]:
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    if not lines:
        raise ValueError(f"empty LFW people file: {path}")
    declared_total = int(lines[0])
    rows: dict[str, int] = {}
    for line in lines[1:]:
        fields = line.replace("\t", " ").split()
        if len(fields) < 2:
            raise ValueError(f"invalid people row in {path.name}: {line!r}")
        identity, count = fields[0], int(fields[1])
        if identity in rows:
            raise ValueError(f"duplicate identity in {path.name}: {identity}")
        rows[identity] = count
    if len(rows) != declared_total:
        raise ValueError(
            f"{path.name}: declared {declared_total} identities but parsed {len(rows)}"
        )
    return rows


def assign_roles(dev_train: Iterable[str], dev_test: Iterable[str]) -> dict[str, str]:
    train_names = sorted(set(dev_train), key=lambda value: (_role_key(value), value))
    test_names = set(dev_test)
    if len(train_names) != 4038 or len(test_names) != 1711:
        raise ValueError(
            f"unexpected LFW identity counts: DevTrain={len(train_names)}, "
            f"DevTest={len(test_names)}"
        )
    overlap = set(train_names) & test_names
    if overlap:
        raise ValueError(f"LFW DevTrain/DevTest identity overlap: {len(overlap)}")
    roles: dict[str, str] = {}
    offset = 0
    for role, count in (("TRAIN", 2827), ("VALIDATION", 606), ("SCREEN", 605)):
        for identity in train_names[offset : offset + count]:
            roles[identity] = role
        offset += count
    for identity in test_names:
        roles[identity] = "TEST"
    return roles


def _find_images_root(root: Path) -> Path:
    candidates = [root] + [path for path in root.rglob("lfw-deepfunneled") if path.is_dir()]
    for candidate in sorted(candidates, key=lambda item: (-len(item.parts), str(item))):
        if next(candidate.glob("*/*.jpg"), None) is not None:
            return candidate
    raise FileNotFoundError("could not locate lfw-deepfunneled identity/image hierarchy")


def _find_named(root: Path, name: str) -> Path:
    matches = sorted(root.rglob(name), key=lambda item: (len(item.parts), str(item)))
    if not matches:
        raise FileNotFoundError(f"missing required LFW metadata file: {name}")
    return matches[0]


def _dhash64(path: Path) -> int:
    with Image.open(path) as image:
        gray = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        values = np.asarray(gray, dtype=np.int16)
    bits = values[:, 1:] > values[:, :-1]
    result = 0
    for bit in bits.ravel(order="C"):
        result = (result << 1) | int(bit)
    return result


def materialize_captures(
    root: Path,
    roles: dict[str, str],
    declared: dict[str, int],
) -> list[Capture]:
    images_root = _find_images_root(root)
    captures: list[Capture] = []
    for identity, role in sorted(roles.items(), key=lambda item: (item[1], item[0])):
        expected = declared[identity]
        paths = sorted((images_root / identity).glob(f"{identity}_*.jpg"))
        if len(paths) != expected:
            raise ValueError(
                f"capture count mismatch for {_public_subject(identity)}: "
                f"{len(paths)} != {expected}"
            )
        subject_id = _public_subject(identity)
        for index, path in enumerate(paths, 1):
            captures.append(
                Capture(
                    subject_id=subject_id,
                    capture_id=f"{subject_id}_capture_{index:04d}",
                    role=role,
                    relative_path=str(path.relative_to(images_root)),
                    sha256=sha256_file(path),
                    dhash64=_dhash64(path),
                )
            )
    return captures


def _cross_role_duplicate_audit(captures: list[Capture], max_hamming: int = 4) -> dict:
    exact_groups: dict[str, list[Capture]] = defaultdict(list)
    for capture in captures:
        exact_groups[capture.sha256].append(capture)
    exact = []
    for digest, group in exact_groups.items():
        roles = {item.role for item in group}
        if len(roles) > 1:
            exact.append(
                {
                    "sha256": digest,
                    "roles": sorted(roles),
                    "captures": [item.capture_id for item in group],
                }
            )

    # A Hamming<=4 pair over 64 bits must match at least one of five disjoint bands.
    bands = ((0, 13), (13, 26), (26, 39), (39, 52), (52, 64))
    buckets: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, capture in enumerate(captures):
        for band_index, (_start, stop) in enumerate(bands):
            start = bands[band_index][0]
            width, shift = stop - start, 64 - stop
            value = (capture.dhash64 >> shift) & ((1 << width) - 1)
            buckets[(band_index, value)].append(index)

    checked: set[tuple[int, int]] = set()
    near = []
    for bucket in buckets.values():
        for offset, left in enumerate(bucket):
            for right in bucket[offset + 1 :]:
                a, b = (left, right) if left < right else (right, left)
                if (a, b) in checked:
                    continue
                checked.add((a, b))
                first, second = captures[a], captures[b]
                if first.role == second.role or first.sha256 == second.sha256:
                    continue
                distance = (first.dhash64 ^ second.dhash64).bit_count()
                if distance <= max_hamming:
                    near.append(
                        {
                            "capture_id_1": first.capture_id,
                            "capture_id_2": second.capture_id,
                            "role_1": first.role,
                            "role_2": second.role,
                            "dhash_hamming": distance,
                        }
                    )
    near = sorted(near, key=lambda row: (row["dhash_hamming"], row["capture_id_1"]))
    return {
        "exact_cross_role_duplicates": exact,
        "near_duplicate_rule": {"algorithm": "dhash64", "max_hamming": max_hamming},
        "near_cross_role_candidates": near,
        "exact_duplicate_blocking": bool(exact),
        "near_duplicate_review_required": bool(near),
    }


def task_seed_sequence(label: str, root_entropy: int = ROOT_ENTROPY) -> np.random.SeedSequence:
    words = np.frombuffer(hashlib.sha256(label.encode()).digest()[:16], dtype=">u4").astype(
        np.uint32
    )
    return np.random.SeedSequence([int(root_entropy), *(int(word) for word in words)])


def _canonical_edge(a: Capture, b: Capture) -> tuple[Capture, Capture]:
    return (a, b) if a.capture_id < b.capture_id else (b, a)


def make_pair_graph(
    role: str,
    captures: list[Capture],
    genuine_count: int,
    impostor_count: int,
) -> list[PairEdge]:
    by_subject: dict[str, list[Capture]] = defaultdict(list)
    for capture in captures:
        if capture.role == role:
            by_subject[capture.subject_id].append(capture)
    eligible = np.asarray(
        sorted(subject for subject, items in by_subject.items() if len(items) >= 2),
        dtype=object,
    )
    subjects = np.asarray(sorted(by_subject), dtype=object)
    if len(eligible) == 0 or len(subjects) < 2:
        raise ValueError(f"{role}: insufficient subjects for requested graph")

    genuine_capacity = sum(len(items) * (len(items) - 1) // 2 for items in by_subject.values())
    total_captures = sum(len(items) for items in by_subject.values())
    same_subject_ordered = sum(len(items) ** 2 for items in by_subject.values())
    impostor_capacity = (total_captures**2 - same_subject_ordered) // 2
    if genuine_capacity < genuine_count or impostor_capacity < impostor_count:
        raise ValueError(
            f"{role}: pair capacity insufficient: genuine={genuine_capacity}/{genuine_count}, "
            f"impostor={impostor_capacity}/{impostor_count}"
        )

    rng = np.random.default_rng(task_seed_sequence(f"pair-graph|{role}"))
    edges: list[PairEdge] = []
    seen: set[tuple[str, str, int]] = set()
    counters = {1: 0, 0: 0}

    def add(first: Capture, second: Capture, same: int) -> bool:
        first, second = _canonical_edge(first, second)
        key = (first.capture_id, second.capture_id, same)
        if key in seen:
            return False
        seen.add(key)
        pair_index = counters[same]
        counters[same] += 1
        edges.append(
            PairEdge(
                pair_id=f"{role.lower()}_{'g' if same else 'i'}_{pair_index:06d}",
                same=same,
                subject_slot_id_1=first.subject_id,
                subject_slot_id_2=second.subject_id,
                capture_id_1=first.capture_id,
                capture_id_2=second.capture_id,
            )
        )
        return True

    max_attempts = 250 * max(genuine_count, impostor_count)
    attempts = 0
    while counters[1] < genuine_count and attempts < max_attempts:
        attempts += 1
        subject = str(rng.choice(eligible))
        first_index, second_index = rng.choice(len(by_subject[subject]), size=2, replace=False)
        add(by_subject[subject][int(first_index)], by_subject[subject][int(second_index)], 1)
    if counters[1] != genuine_count:
        raise ValueError(
            f"{role}: unique genuine graph sampling failed: {counters[1]}/{genuine_count}"
        )

    attempts = 0
    while counters[0] < impostor_count and attempts < max_attempts:
        attempts += 1
        first_subject, second_subject = rng.choice(subjects, size=2, replace=False)
        first_items = by_subject[str(first_subject)]
        second_items = by_subject[str(second_subject)]
        first = first_items[int(rng.integers(len(first_items)))]
        second = second_items[int(rng.integers(len(second_items)))]
        add(first, second, 0)
    if counters[0] != impostor_count:
        raise ValueError(
            f"{role}: unique impostor graph sampling failed: {counters[0]}/{impostor_count}"
        )
    return edges


def write_pair_graph(path: Path, edges: list[PairEdge]) -> str:
    if not edges:
        raise ValueError("pair graph cannot be empty")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(asdict(edges[0]))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(asdict(edge) for edge in edges)
    return sha256_file(path)


def run_lfw_preflight(root: Path, output_dir: Path) -> dict:
    root = root.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    train_file = _find_named(root, "peopleDevTrain.txt")
    test_file = _find_named(root, "peopleDevTest.txt")
    dev_train = _parse_people_file(train_file)
    dev_test = _parse_people_file(test_file)
    roles = assign_roles(dev_train, dev_test)
    captures = materialize_captures(root, roles, {**dev_train, **dev_test})

    audit = _cross_role_duplicate_audit(captures)
    (output_dir / "overlap_near_duplicate_audit.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if audit["exact_duplicate_blocking"]:
        raise RuntimeError("cross-role exact duplicate leakage detected; preflight fails closed")

    counts_by_role_subject: dict[str, Counter[str]] = defaultdict(Counter)
    for capture in captures:
        counts_by_role_subject[capture.role][capture.subject_id] += 1

    role_summary = {}
    graph_hashes = {}
    for role in ("TRAIN", "VALIDATION", "SCREEN", "TEST"):
        role_captures = [item for item in captures if item.role == role]
        subject_counts = counts_by_role_subject[role]
        genuine, impostor = PAIR_COUNTS[role]
        graph = make_pair_graph(role, captures, genuine, impostor)
        graph_path = output_dir / "graphs" / f"{role.lower()}_pairs.csv"
        graph_hashes[role] = write_pair_graph(graph_path, graph)
        role_summary[role] = {
            "identities": len(subject_counts),
            "captures": len(role_captures),
            "eligible_genuine_identities": sum(count >= 2 for count in subject_counts.values()),
            "genuine_pairs": genuine,
            "impostor_pairs": impostor,
        }
        if len(subject_counts) != ROLE_COUNTS[role]:
            raise RuntimeError(f"{role}: identity-count invariant failed")

    capture_rows = [
        {
            "subject_id": item.subject_id,
            "capture_id": item.capture_id,
            "role": item.role,
            "source_sha256": item.sha256,
            "dhash64_hex": f"{item.dhash64:016x}",
        }
        for item in captures
    ]
    capture_manifest = output_dir / "capture_manifest.csv"
    with capture_manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(capture_rows[0]))
        writer.writeheader()
        writer.writerows(capture_rows)

    near_review = bool(audit["near_duplicate_review_required"])
    report = {
        "schema_version": "1.0",
        "kind": "study1b_lfw_non_outcome_preflight",
        "scientific_outcomes_opened": False,
        "source": {
            "peopleDevTrain_sha256": sha256_file(train_file),
            "peopleDevTest_sha256": sha256_file(test_file),
            "capture_manifest_sha256": sha256_file(capture_manifest),
        },
        "roles": role_summary,
        "graph_sha256": graph_hashes,
        "exact_duplicate_audit": "PASS",
        "near_duplicate_review_required": near_review,
        "overall_status": "PASS_PENDING_NEAR_DUPLICATE_REVIEW" if near_review else "PASS",
    }
    (output_dir / "preflight_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report
