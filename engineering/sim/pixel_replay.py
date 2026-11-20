"""Offline visible/NIR image-pair exact matching demonstration.

NO learned face recognizer, NO identity inference, NO cross-spectral validation.
The 512D feature is a deterministic DCT image descriptor (engineering baseline);
128D random orthogonal projection is a deterministic dimension-change baseline.
Real image pairs may only be processed from an independently approved, isolated
local dataset with a documented legal basis/rights; none are bundled into GitHub.
Synthetic generated fixtures are abstract non-human patterns, not facial images.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import html
import io
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from scipy.fft import dctn

EXTRACTOR = "DEMO_DCT512_NOT_FACE_AI_V1"
MODEL_ID = "SYNTHETIC_LAB_PATTERNS"
COORDS = sorted(((i, j) for i in range(64) for j in range(64)
                 if (i, j) != (0, 0)),
                key=lambda p: (p[0] + p[1], p[0]))[:512]


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def descriptor512(image: Image.Image) -> np.ndarray:
    """L2 normalized image descriptor; not an EO/NIR biometric embedding."""
    gray = np.asarray(image.convert("L").resize((64, 64)), dtype=np.float32)
    gray = (gray - np.mean(gray)) / max(float(np.std(gray)), 1.0)
    frequency = dctn(gray, type=2, norm="ortho")
    v = np.asarray([frequency[i, j] for i, j in COORDS], dtype=np.float32)
    return v / max(float(np.linalg.norm(v)), 1e-8)


def random_projection(seed: int = 23) -> np.ndarray:
    """Predeclared shared 512->128 transform; not a trained Siamese model."""
    rng = np.random.default_rng(seed)
    a = rng.standard_normal((512, 128)).astype(np.float64)
    q, _ = np.linalg.qr(a, mode="reduced")
    return q.astype(np.float32)


def normalize(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float32)
    return v / max(float(np.linalg.norm(v)), 1e-8)


def project(v: np.ndarray, method: str, matrix: np.ndarray | None = None) -> np.ndarray:
    if method == "dct512":
        if v.shape != (512,):
            raise ValueError("expected 512D")
        return normalize(v)
    if method not in {"random128", "pca128", "siamese128"}:
        raise ValueError("unrecognized projection")
    if matrix is None or matrix.shape != (512, 128):
        raise ValueError("128D projection requires frozen 512x128 matrix")
    return normalize(v @ matrix)


def load_external_projection(path: Path, expected: str) -> tuple[np.ndarray, str]:
    """Require explicitly frozen experiment metadata. Never download weights here."""
    if expected not in {"pca128", "siamese128"}:
        raise ValueError("external projection only for PCA / Siamese")
    with np.load(path, allow_pickle=False) as bundle:
        matrix = np.asarray(bundle["matrix"], dtype=np.float32)
        metadata = json.loads(str(bundle["metadata"].item()))
    if matrix.shape != (512, 128):
        raise ValueError("projection must be 512x128")
    if metadata.get("method") != expected or metadata.get("data_split") != "TRAIN_ONLY":
        raise ValueError("projection metadata does not meet frozen training contract")
    if not metadata.get("training_dataset_sha256") or not metadata.get("model_revision"):
        raise ValueError("missing provenance/compatible-model revision")
    return matrix, file_sha(path)


def simulate_abstract_image(identity: int, mode: str, variant: int,
                            size: int = 96) -> Image.Image:
    """Generate ONLY non-human geometric patterns; 'NIR-like' is NOT NIR."""
    if mode not in {"RGB", "NIR"}:
        raise ValueError("mode")
    y, x = np.mgrid[0:size, 0:size]
    rng = np.random.default_rng(10000 + identity * 17)
    field = np.zeros((size, size), dtype=np.float64)
    for _ in range(5):
        cx, cy = rng.uniform(12, 84, size=2)
        sx, sy = rng.uniform(5, 15, size=2)
        field += rng.uniform(.3, 1.0) * np.exp(
            -(((x - cx) / sx)**2 + ((y - cy) / sy)**2) / 2)
    shift = int(variant % 3) - 1
    field = np.roll(field, shift, axis=1)
    field /= max(float(np.max(field)), 1e-7)
    noise = np.random.default_rng(11 + identity*100 + variant)
    field += noise.normal(0, .009, size=(size, size))
    # The two generated modalities have the same abstract geometry but
    # different artificial contrast response (NOT true sensor physics).
    field = np.clip(field, 0, 1)
    if mode == "NIR":
        arr = np.uint8(255 * (0.08 + 0.87 * field**0.85))
        return Image.fromarray(arr, mode="L")
    r = np.uint8(255 * np.clip(0.12 + .85*field, 0, 1))
    g = np.uint8(255 * np.clip(0.10 + .70*field, 0, 1))
    b = np.uint8(255 * np.clip(0.20 + .55*field, 0, 1))
    return Image.fromarray(np.stack((r, g, b), axis=-1), mode="RGB")


def generate_fixtures(root: Path, subjects: int = 5) -> dict[str, Any]:
    """This generator is the ONLY source of image bytes for the public demo."""
    root.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    for idx in range(subjects + 1):
        subject = f"lab-{idx+1:03d}" if idx < subjects else "unknown-pattern"
        for mode in ("RGB", "NIR"):
            for role, variant in (("enroll", 0), ("query", 1)):
                if idx == subjects and role == "enroll":
                    continue
                name = f"{subject}-{mode.lower()}-{role}.png"
                path = root / name
                simulate_abstract_image(idx, mode, variant).save(path)
                entries.append({
                    "capture_id": name[:-4], "subject_ref": subject,
                    "role": role, "modality": mode, "relative_path": name,
                    "sha256": file_sha(path),
                    "pose_label": "illustrative-shift-only",
                    "record_type": "SYNTHETIC_NONHUMAN",
                })
    manifest = {
        "schema": "image-pair-lab-demo-v1",
        "purpose_id": "SYNTHETIC_INTEGRATION_TEST_ONLY",
        "dataset_class": "SYNTHETIC_NONHUMAN",
        "source": "procedural geometric patterns, no people",
        "captures": entries,
    }
    (root/"dataset_manifest.json").write_text(
        json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    return manifest


def safe_read(root: Path, item: dict[str, Any], purpose: str) -> Image.Image:
    """Avoid traversals and reject unapproved external image datasets by default."""
    if purpose != "SYNTHETIC_INTEGRATION_TEST_ONLY":
        raise PermissionError("real image dataset access requires separate approved adapter")
    path = (root / item["relative_path"]).resolve()
    if not path.is_relative_to(root.resolve()) or path.suffix.lower() != ".png":
        raise ValueError("invalid fixture path")
    if file_sha(path) != item["sha256"]:
        raise ValueError("image changed after manifest sealing")
    with Image.open(path) as im:
        im.load()
        return im.copy()


def run_comparison(root: Path, manifest: dict, methods: list[str],
                   projection_paths: dict[str, Path] | None = None) -> dict:
    if manifest.get("dataset_class") != "SYNTHETIC_NONHUMAN" or (
        manifest.get("purpose_id") != "SYNTHETIC_INTEGRATION_TEST_ONLY"
    ):
        raise PermissionError("this demonstrator only accepts non-human fixtures")
    projection_paths = projection_paths or {}
    projections: dict[str, tuple[np.ndarray | None, str]] = {}
    for m in methods:
        if m == "dct512":
            projections[m] = (None, "identity512")
        elif m == "random128":
            projections[m] = (random_projection(), "seed23-qr-128")
        else:
            matrix, digest = load_external_projection(projection_paths[m], m)
            projections[m] = (matrix, digest)
    rows = []
    data = [
        (item, descriptor512(safe_read(root, item, manifest["purpose_id"])))
        for item in manifest["captures"]
    ]
    # Enrollment is RGB-only. Compare both RGB and synthetic NIR-like queries.
    enrollment = [(row, vec) for row, vec in data
                  if row["role"] == "enroll" and row["modality"] == "RGB"]
    queries = [(row, vec) for row, vec in data if row["role"] == "query"]
    for method in methods:
        matrix, proj_id = projections[method]
        gallery = np.stack([project(v, method, matrix) for _, v in enrollment])
        ids = [row["subject_ref"] for row, _ in enrollment]
        for capture, base in queries:
            q = project(base, method, matrix)
            scores = gallery @ q
            k = int(np.argmax(scores))
            # No operational biometric threshold, no security action.
            rows.append({
                "capture_id":capture["capture_id"], "modality":capture["modality"],
                "expected_fixture":capture["subject_ref"],
                "model":method, "dimension":len(q),
                "candidate_lab_ref":ids[k], "cosine_proxy":round(float(scores[k]), 6),
                "top_candidate_equal_fixture": bool(ids[k] == capture["subject_ref"]),
                "decision_class":"LAB_SIMULATED_CANDIDATE_ONLY",
                "source":"ABSTRACT_SYNTHETIC_IMAGES_NOT_FACES",
            })
    return {
        "manifest":{
            "experiment":"fixed_capture_pixel_replay_demo",
            "extractor":EXTRACTOR,
            "methods":methods,
            "projection_revisions":{k:rev for k,(_,rev) in projections.items()},
            "dataset_class":"SYNTHETIC_NONHUMAN",
            "dataset_manifest_sha256":file_sha(root/"dataset_manifest.json"),
            "biometric_performance_claim":False,
            "physical_energy_claim":False,
            "device_real_time_claim":False,
            "sample_count":len(queries),
        },
        "comparisons":rows,
    }


def export_report(data: dict, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory/"image_comparison.json").write_text(
        json.dumps(data,indent=2,sort_keys=True)+"\n", encoding="utf-8")
    rows = data["comparisons"]
    with (directory/"image_comparison.csv").open("w",newline="",encoding="utf-8") as h:
        wr=csv.DictWriter(h, fieldnames=list(rows[0]))
        wr.writeheader();wr.writerows(rows)
    trs=[]
    for row in rows:
        trs.append("<tr>"+ "".join("<td>"+html.escape(str(v))+"</td>"
            for v in (row["capture_id"],row["modality"],row["model"],
                      row["dimension"],row["candidate_lab_ref"],row["cosine_proxy"],
                      row["top_candidate_equal_fixture"]))+"</tr>")
    report = """<!doctype html><html lang="en"><meta charset="utf-8">
<title>Siamese Embedded - offline pixel replay</title>
<style>body{font:14px system-ui;background:#101c24;color:#e6eff4;margin:2rem auto;
max-width:1150px;padding:0 1rem}h1{color:#e7f9ff}p{line-height:1.6}
aside{padding:12px;background:#423329;color:#ffe6b4;border-radius:8px}
table{width:100%;border-collapse:collapse;background:#192b37;border-radius:9px}
th,td{text-align:left;padding:8px;border-bottom:1px solid #2e4c5c}
th{background:#233f4c}small{color:#adc6d2}</style>
<h1>Siamese Embedded / Fixed EO &amp; NIR Image Replay</h1>
<aside>DEMONSTRATION ONLY: synthetic NON-HUMAN patterns, not actual EO/NIR camera
captures; DCT512 is not a face model; scores cannot establish FPIR/FNIR.</aside>
<p>Same immutable synthetic acquisitions processed by 512D feature and 128D projection;
one active representation at a time on the future field node. No claims about
real identification, environmental resilience or energy.</p>
<table><thead><tr><th>Capture</th><th>Mode</th><th>Method</th><th>Dimension</th><th>Lab candidate</th>
<th>Cosine proxy</th><th>Fixture match</th></tr></thead><tbody>
""" + "\n".join(trs) + "</tbody></table><p><small>Manifest and raw CSV/JSON available in the run output; never upload real people data.</small></p></html>"
    (directory/"offline_replay_report.html").write_text(report,encoding="utf-8")


def main():
    parser=argparse.ArgumentParser(description="Offline abstract-image RGB/NIR matching lab")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--methods", nargs="+", default=["dct512","random128"],
                        choices=["dct512","random128","pca128","siamese128"])
    parser.add_argument("--pca-checkpoint",type=Path)
    parser.add_argument("--siamese-checkpoint",type=Path)
    args=parser.parse_args()
    dataset = args.out/"synthetic_fixture_images"
    manifest = generate_fixtures(dataset)
    projections={}
    if args.pca_checkpoint:
        projections["pca128"]=args.pca_checkpoint
    if args.siamese_checkpoint:
        projections["siamese128"]=args.siamese_checkpoint
    result=run_comparison(dataset,manifest,args.methods,projections)
    export_report(result,args.out)
    print(json.dumps(result["manifest"],sort_keys=True))


if __name__ == "__main__":
    main()
