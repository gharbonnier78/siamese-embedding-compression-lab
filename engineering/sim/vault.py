"""Encrypted external research evidence vault (stand-alone demo, NOT an archive service).

Only lawfully acquired, purpose-limited research data may be archived. Supply a unique
256-bit AES key via a managed, out-of-repo secret; GitHub and radio links get no contents.
AES-256-GCM supports authenticated encryption but does NOT provide key custody, backup,
access governance, tamper-proof retention or guaranteed deletion on its own.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

AAD = b"siamese-research-evidence-vault-v1"


def key_from_base64(value: str) -> bytes:
    key = base64.b64decode(value, validate=True)
    if len(key) != 32:
        raise ValueError("AES-256 requires exactly 32 random key bytes")
    return key


def seal_bytes(plaintext: bytes, metadata: dict, key: bytes) -> bytes:
    if len(key) != 32:
        raise ValueError("invalid key length")
    if not isinstance(metadata, dict) or "purpose_id" not in metadata:
        raise ValueError("metadata must include a documented purpose_id")
    nonce = os.urandom(12)
    payload = json.dumps({
        "metadata": metadata,
        "data_b64": base64.b64encode(plaintext).decode(),
        "plaintext_sha256": hashlib.sha256(plaintext).hexdigest(),
    }, sort_keys=True).encode()
    ciphertext = AESGCM(key).encrypt(nonce, payload, AAD)
    return json.dumps({
        "format": "research-vault-v1",
        "nonce_b64": base64.b64encode(nonce).decode(),
        "ciphertext_b64": base64.b64encode(ciphertext).decode(),
    }, sort_keys=True).encode()


def open_bytes(blob: bytes, key: bytes) -> tuple[bytes, dict]:
    if len(key) != 32:
        raise ValueError("invalid key length")
    envelope = json.loads(blob)
    if envelope.get("format") != "research-vault-v1":
        raise ValueError("invalid vault format")
    nonce = base64.b64decode(envelope["nonce_b64"], validate=True)
    ciphertext = base64.b64decode(envelope["ciphertext_b64"], validate=True)
    payload = json.loads(AESGCM(key).decrypt(nonce, ciphertext, AAD))
    data = base64.b64decode(payload["data_b64"], validate=True)
    if hashlib.sha256(data).hexdigest() != payload["plaintext_sha256"]:
        raise ValueError("artifact digest mismatch")
    return data, payload["metadata"]


def store_artifact(root: Path, plaintext: bytes, metadata: dict, key: bytes) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    # Random opaque filenames prevent leaking a case/subject identity.
    path = root / (uuid4().hex + ".vault")
    blob = seal_bytes(plaintext, metadata, key)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(blob)
        f.flush()
        os.fsync(f.fileno())
    return path


def read_artifact(path: Path, key: bytes) -> tuple[bytes, dict]:
    return open_bytes(path.read_bytes(), key)


if __name__ == "__main__":
    # Demonstrates synthetic only and never prints the key or plaintext.
    key = os.urandom(32)
    root = Path("/tmp/siamese-vault-synthetic-demo")
    p = store_artifact(root, b"synthetic repeatable stimulus seed=7",
                       {"purpose_id": "test-only", "seed": 7, "retention": "demo"}, key)
    data, metadata = read_artifact(p, key)
    assert data == b"synthetic repeatable stimulus seed=7"
    print(f"Sealed synthetic artifact {p.name}; metadata kept inside ciphertext")
