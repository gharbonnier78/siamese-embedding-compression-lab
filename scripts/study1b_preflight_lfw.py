"""Materialize the frozen Study 1B LFW metadata/graph preflight without model outcomes.

Image bytes come from the already recorded Kaggle LFW v4 package. View-1 identity metadata
comes from the original UMass LFW endpoint and is verified against checksums independently
published by torchvision. This avoids inferring missing identities from pair files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import urllib.request
from pathlib import Path

from siamese_compression_lab.study1b_preflight import run_lfw_preflight

DATASET_HANDLE = "jessicali9530/lfw-dataset/versions/4"
UMASS_LFW_PREFIX = "http://vis-www.cs.umass.edu/lfw/"
METADATA = {
    "peopleDevTrain.txt": "54eaac34beb6d042ed3a7d883e247a21",
    "peopleDevTest.txt": "e4bf5be0a43b5dcd9dc5ccfcb8fb19c5",
}
CHECKSUM_AUTHORITY = (
    "torchvision.datasets.lfw file checksums; source prefix points to the original UMass LFW site"
)


def _md5(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download_verified_metadata(name: str, expected_md5: str, destination: Path) -> dict:
    url = f"{UMASS_LFW_PREFIX}{name}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "siamese-embedding-compression-lab-study1b-preflight/1.0"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:  # noqa: S310 - frozen trusted host
        payload = response.read()
        final_url = response.geturl()
    destination.write_bytes(payload)
    actual_md5 = _md5(destination)
    if actual_md5 != expected_md5:
        destination.unlink(missing_ok=True)
        raise ValueError(
            f"official LFW metadata checksum mismatch for {name}: "
            f"{actual_md5} != {expected_md5}"
        )
    return {
        "name": name,
        "requested_url": url,
        "resolved_url": final_url,
        "md5": actual_md5,
        "expected_md5": expected_md5,
        "checksum_authority": CHECKSUM_AUTHORITY,
    }


def _resolve_dataset_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    import kagglehub

    return Path(kagglehub.dataset_download(DATASET_HANDLE)).resolve()


def _materialize_metadata_into_root(dataset_root: Path, output_dir: Path) -> list[dict]:
    sources_dir = output_dir / "sources" / "lfw-view1-metadata"
    records = []
    for name, expected_md5 in METADATA.items():
        retained = sources_dir / name
        record = _download_verified_metadata(name, expected_md5, retained)
        # Ephemeral copy only: run_lfw_preflight searches one root for both image hierarchy
        # and metadata. The retained provenance copy lives in the uploaded preflight artifact.
        shutil.copyfile(retained, dataset_root / name)
        records.append(record)
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    root = _resolve_dataset_root(args.dataset_root)
    metadata_records = _materialize_metadata_into_root(root, output_dir)
    report = run_lfw_preflight(root, output_dir)
    report["dataset_handle"] = DATASET_HANDLE
    report["metadata_provenance"] = metadata_records
    report["metadata_source_policy"] = (
        "official UMass LFW bytes + independent torchvision published checksum verification"
    )
    report["scientific_outcomes_opened"] = False
    (output_dir / "preflight_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
