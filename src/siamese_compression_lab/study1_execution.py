from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Provenance:
    model_sha256: str
    preprocessing_id: str
    dataset_manifest_sha256: str
    protocol_id: str


@dataclass(frozen=True)
class ShardManifest:
    shard_id: str
    provenance: Provenance
    row_count: int
    payload_sha256: str


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(chunk_size), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_shard_id(dataset_manifest_sha256: str, start: int, stop: int) -> str:
    if start < 0 or stop <= start:
        raise ValueError("invalid shard bounds")
    material = f"{dataset_manifest_sha256}:{start}:{stop}".encode()
    return hashlib.sha256(material).hexdigest()[:24]


def atomic_write_json(path: str | Path, payload: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=target.name, dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, target)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def write_completed_shard_manifest(path: str | Path, manifest: ShardManifest) -> None:
    atomic_write_json(path, asdict(manifest))


def load_shard_manifest(path: str | Path) -> ShardManifest:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return ShardManifest(
        shard_id=data["shard_id"],
        provenance=Provenance(**data["provenance"]),
        row_count=int(data["row_count"]),
        payload_sha256=data["payload_sha256"],
    )


def validate_shard_for_resume(
    manifest_path: str | Path,
    payload_path: str | Path,
    expected_provenance: Provenance,
) -> bool:
    manifest_file = Path(manifest_path)
    payload_file = Path(payload_path)
    if not manifest_file.is_file() or not payload_file.is_file():
        return False
    try:
        manifest = load_shard_manifest(manifest_file)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return False
    if manifest.provenance != expected_provenance:
        return False
    return sha256_file(payload_file) == manifest.payload_sha256


def assert_homogeneous_provenance(manifests: Iterable[ShardManifest]) -> Provenance:
    iterator = iter(manifests)
    try:
        first = next(iterator)
    except StopIteration as exc:
        raise ValueError("at least one shard manifest is required") from exc
    for item in iterator:
        if item.provenance != first.provenance:
            raise ValueError("mixed provenance across shards")
    return first.provenance


def normalize_adaface_bgr_uint8(image):
    """Normalize an aligned BGR uint8 image to AdaFace's [-1, 1] convention.

    The function intentionally avoids importing torch so the preprocessing contract can be
    unit-tested in the lightweight CI path. It accepts NumPy-like arrays supporting
    astype/shape and arithmetic.
    """
    if getattr(image, "shape", None) != (112, 112, 3):
        raise ValueError("AdaFace input must be aligned 112x112x3 BGR")
    x = image.astype("float32") / 255.0
    return (x - 0.5) / 0.5


def canonical_array_sha256(array) -> str:
    """Return a stable digest for a C-contiguous numeric array.

    Shape and dtype are included in the digest material so an identical byte stream with a
    different interpretation cannot collide at the contract level. This helper is intended
    for non-outcome-bearing preprocessing and replay fixtures as well as frozen embedding
    artifacts.
    """
    contiguous = array.copy(order="C") if not getattr(array, "flags", {}).c_contiguous else array
    metadata = json.dumps(
        {"shape": list(contiguous.shape), "dtype": str(contiguous.dtype)},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256()
    digest.update(metadata)
    digest.update(b"\0")
    digest.update(contiguous.tobytes(order="C"))
    return digest.hexdigest()


def preprocessing_fingerprint(aligned_bgr_uint8) -> dict[str, str]:
    """Fingerprint the raw aligned fixture and its exact normalized model input.

    This is engineering/provenance evidence only. It does not inspect or summarize a
    scientific benchmark outcome.
    """
    normalized = normalize_adaface_bgr_uint8(aligned_bgr_uint8)
    return {
        "aligned_bgr_uint8_sha256": canonical_array_sha256(aligned_bgr_uint8),
        "normalized_float32_sha256": canonical_array_sha256(normalized),
    }


def embedding_replay_digest(embedding) -> str:
    """Digest one frozen 512D embedding for deterministic replay checks."""
    if getattr(embedding, "shape", None) != (512,):
        raise ValueError("Study 1A replay embedding must be exactly 512D")
    return canonical_array_sha256(embedding)


def bgr_rgb_roundtrip_exact(image) -> bool:
    """Check the explicit RGB<->BGR representation sentinel on a fixture."""
    if getattr(image, "shape", None) != (112, 112, 3):
        raise ValueError("representation sentinel expects 112x112x3 input")
    rgb = image[..., ::-1]
    restored_bgr = rgb[..., ::-1]
    return canonical_array_sha256(restored_bgr) == canonical_array_sha256(image)
