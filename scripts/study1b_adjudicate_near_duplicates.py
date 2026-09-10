"""Examen déterministe des quasi-doublons candidats Study 1B, sans résultat biométrique.

Le premier filtre dHash est volontairement sensible. Cette seconde étape n'utilise que les
pixels et une règle figée, sans embeddings AdaFace ni scores de vérification. Les chemins LFW
nominatifs ne sont pas écrits dans l'artefact : les images sont retrouvées par leur SHA-256.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image

from siamese_compression_lab.study1b_preflight import _find_images_root, sha256_file

CANONICAL_SIZE = 128
CENTRAL_FRACTION = 0.80
NRMSE_BLOCK_MAX = 0.08
CORR_BLOCK_MIN = 0.985
GRAD_CORR_BLOCK_MIN = 0.97


def _canonical_pixels(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        gray = image.convert("L")
        width, height = gray.size
        crop_w = max(1, round(width * CENTRAL_FRACTION))
        crop_h = max(1, round(height * CENTRAL_FRACTION))
        left = (width - crop_w) // 2
        top = (height - crop_h) // 2
        gray = gray.crop((left, top, left + crop_w, top + crop_h))
        gray = gray.resize((CANONICAL_SIZE, CANONICAL_SIZE), Image.Resampling.LANCZOS)
        return np.asarray(gray, dtype=np.float64) / 255.0


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    av = a.ravel() - float(a.mean())
    bv = b.ravel() - float(b.mean())
    denom = float(np.linalg.norm(av) * np.linalg.norm(bv))
    if denom == 0.0:
        return 1.0 if np.array_equal(a, b) else 0.0
    return float(np.dot(av, bv) / denom)


def _gradient_magnitude(image: np.ndarray) -> np.ndarray:
    gy, gx = np.gradient(image)
    return np.hypot(gx, gy)


def _metrics(left: Path, right: Path) -> dict[str, float]:
    a = _canonical_pixels(left)
    b = _canonical_pixels(right)
    return {
        "nrmse": float(np.sqrt(np.mean((a - b) ** 2))),
        "pixel_corr": _corr(a, b),
        "gradient_corr": _corr(_gradient_magnitude(a), _gradient_magnitude(b)),
    }


def _decision(metrics: dict[str, float]) -> tuple[str, int]:
    checks = (
        metrics["nrmse"] <= NRMSE_BLOCK_MAX,
        metrics["pixel_corr"] >= CORR_BLOCK_MIN,
        metrics["gradient_corr"] >= GRAD_CORR_BLOCK_MIN,
    )
    passed = sum(checks)
    if passed == 3:
        return "BLOCK_DUPLICATE_LIKE", passed
    if passed == 2:
        return "AMBIGUOUS_REVIEW", passed
    return "CLEAR_NOT_DUPLICATE_LIKE", passed


def _load_manifest(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {row["capture_id"]: row for row in rows}


def _locate_required_images(images_root: Path, required_hashes: set[str]) -> dict[str, Path]:
    located: dict[str, Path] = {}
    for path in sorted(images_root.rglob("*.jpg")):
        digest = sha256_file(path)
        if digest in required_hashes:
            located[digest] = path
            if len(located) == len(required_hashes):
                break
    missing = sorted(required_hashes - located.keys())
    if missing:
        raise FileNotFoundError(f"missing {len(missing)} candidate image hashes in LFW source")
    return located


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--near-duplicate-audit", type=Path, required=True)
    parser.add_argument("--capture-manifest", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    audit = json.loads(args.near_duplicate_audit.read_text(encoding="utf-8"))
    candidates = audit["near_cross_role_candidates"]
    manifest = _load_manifest(args.capture_manifest)
    images_root = _find_images_root(args.dataset_root)
    required_hashes = {
        manifest[capture_id]["source_sha256"]
        for candidate in candidates
        for capture_id in (candidate["capture_id_1"], candidate["capture_id_2"])
    }
    image_by_hash = _locate_required_images(images_root, required_hashes)

    adjudications = []
    for candidate in candidates:
        capture_1 = candidate["capture_id_1"]
        capture_2 = candidate["capture_id_2"]
        hash_1 = manifest[capture_1]["source_sha256"]
        hash_2 = manifest[capture_2]["source_sha256"]
        metrics = _metrics(image_by_hash[hash_1], image_by_hash[hash_2])
        decision, passed_checks = _decision(metrics)
        adjudications.append(
            {
                **candidate,
                "source_sha256_1": hash_1,
                "source_sha256_2": hash_2,
                **metrics,
                "threshold_checks_passed": passed_checks,
                "decision": decision,
            }
        )

    counts = {
        label: sum(row["decision"] == label for row in adjudications)
        for label in (
            "BLOCK_DUPLICATE_LIKE",
            "AMBIGUOUS_REVIEW",
            "CLEAR_NOT_DUPLICATE_LIKE",
        )
    }
    result = {
        "schema_version": 1,
        "scientific_outcomes_opened": False,
        "method": {
            "candidate_source": "dhash64_hamming_le_4",
            "canonical_size": CANONICAL_SIZE,
            "central_fraction": CENTRAL_FRACTION,
            "block_thresholds": {
                "nrmse_max": NRMSE_BLOCK_MAX,
                "pixel_corr_min": CORR_BLOCK_MIN,
                "gradient_corr_min": GRAD_CORR_BLOCK_MIN,
            },
            "decision_rule": (
                "3/3 => BLOCK_DUPLICATE_LIKE; 2/3 => AMBIGUOUS_REVIEW; "
                "0-1/3 => CLEAR_NOT_DUPLICATE_LIKE"
            ),
            "image_locator": "capture source SHA-256; no nominal LFW path persisted",
        },
        "candidate_count": len(adjudications),
        "counts": counts,
        "overall_status": (
            "BLOCKED"
            if counts["BLOCK_DUPLICATE_LIKE"]
            else "REVIEW_REQUIRED"
            if counts["AMBIGUOUS_REVIEW"]
            else "PASS"
        ),
        "adjudications": adjudications,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
