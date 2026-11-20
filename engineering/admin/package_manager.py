"""Signed one-active-configuration demonstrator. NOT production OTA/secure boot.

A package signs the SHA-256 + normalized JSON metadata of a model artifact.
Do not put private signing keys, real face templates or galleries in source control.
Requires: cryptography>=42
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization


def canonical(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def signed_manifest(payload: bytes, metadata: dict, private_key: Ed25519PrivateKey) -> dict:
    if metadata.get("dimension") not in (128, 512):
        raise ValueError("prototype permits projection dimensions 128 or 512")
    required = ("model_id", "projection_id", "index_version", "firmware_compat")
    if not all(isinstance(metadata.get(k), str) and metadata[k] for k in required):
        raise ValueError("missing mandatory versioned identifiers")
    claims = dict(metadata)
    claims["artifact_sha256"] = hashlib.sha256(payload).hexdigest()
    signature = private_key.sign(canonical(claims))
    return {"claims": claims, "signature_b64": base64.b64encode(signature).decode()}


def verify_manifest(payload: bytes, signed: dict, key: Ed25519PublicKey) -> dict:
    claims = signed["claims"]
    signature = base64.b64decode(signed["signature_b64"], validate=True)
    key.verify(signature, canonical(claims))
    if hashlib.sha256(payload).hexdigest() != claims["artifact_sha256"]:
        raise ValueError("model artifact has changed")
    if claims.get("dimension") not in (128, 512):
        raise ValueError("invalid dimension")
    return claims


def activate_local_model(root: Path, payload: bytes, signed: dict, public_key: Ed25519PublicKey) -> Path:
    """Atomic pointer swap to a verified artifact in a *local simulation directory*.

    THIS DOES NOT IMPLEMENT secure rollback, hardware anti-rollback, MCU/OS updates,
    encrypted-at-rest model storage, actual gallery migration or live biometric policies.
    """
    claims = verify_manifest(payload, signed, public_key)
    root.mkdir(parents=True, exist_ok=True)
    digest = claims["artifact_sha256"]
    slot = root / f"{digest}.bin"
    with tempfile.NamedTemporaryFile(dir=root, prefix=".staging-", delete=False) as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
        tmp = Path(handle.name)
    os.replace(tmp, slot)
    pointer = root / "active.json"
    record = {"artifact": slot.name, "claims": claims}
    with tempfile.NamedTemporaryFile(mode="wb", dir=root, prefix=".active-", delete=False) as handle:
        handle.write(canonical(record))
        handle.flush()
        os.fsync(handle.fileno())
        temp_pointer = Path(handle.name)
    os.replace(temp_pointer, pointer)
    return pointer


def demo(out: Path) -> None:
    # This generated throwaway key is for demonstration ONLY. Never use to sign field firmware.
    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    payload = b"DETERMINISTIC-SYNTHETIC-MODEL-PACKAGE-NOT-A-REAL-MODEL"
    claims = {"model_id": "synthetic-v1", "projection_id": "raw512-v1",
              "dimension": 512, "index_version": "synthetic-index-1",
              "firmware_compat": "demo-api-v1"}
    m = signed_manifest(payload, claims, private)
    verify_manifest(payload, m, public)
    pointer = activate_local_model(out, payload, m, public)
    print(json.dumps({"active_pointer": str(pointer), "signed_model": m["claims"]}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("demo", help="no real biometric data")
    d.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.cmd == "demo":
        demo(args.out)


if __name__ == "__main__":
    main()
