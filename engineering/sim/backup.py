"""Signed-manifest backup for ALREADY encrypted .vault records, synthetic demo only.

Source .vault files are AES-GCM sealed by sim/vault.py with keys managed OUTSIDE
this code. This backup does not create an enterprise WORM vault, network backup,
RBAC, key escrow, retention policies or a fully secure disaster-recovery system.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def canonical(data: dict) -> bytes:
    return json.dumps(data,sort_keys=True,separators=(",",":")).encode()

def create_backup(source: Path, destination: Path, signing_key: Ed25519PrivateKey) -> Path:
    if source.resolve() == destination.resolve():
        raise ValueError("destination must not be source")
    destination.mkdir(parents=True,exist_ok=True)
    encrypted=sorted(source.glob("*.vault"))
    if not encrypted:
        raise ValueError("no encrypted vault entries")
    entries=[]
    for path in encrypted:
        if path.is_symlink() or not path.is_file():
            raise ValueError("refuse symbolic links")
        name=path.name
        content=path.read_bytes()
        if len(content) > 200_000_000:
            raise ValueError("single demo artifact too large")
        target=destination/name
        if target.exists():
            raise FileExistsError("destination already contains "+name)
        # Ciphertext only, never decrypted plaintext.
        with target.open("xb") as f:
            os.chmod(target,0o600)
            f.write(content)
            f.flush(); os.fsync(f.fileno())
        entries.append({"name":name,"bytes":len(content),
                        "ciphertext_sha256":hashlib.sha256(content).hexdigest()})
    manifest={"schema":"encrypted-backup-demo-v1","items":entries,
              "encryption_state":"PRE_ENCRYPTED_SOURCE_ONLY"}
    sig=signing_key.sign(canonical(manifest))
    record={"manifest":manifest,"ed25519_signature_b64":base64.b64encode(sig).decode()}
    output=destination/"signed-backup-manifest.json"
    if output.exists():
        raise FileExistsError("backup manifest already exists")
    output.write_text(json.dumps(record,sort_keys=True,indent=2),encoding="utf8")
    os.chmod(output,0o600)
    return output

def verify_backup(source: Path, verification_key: Ed25519PublicKey) -> list[Path]:
    record=json.loads((source/"signed-backup-manifest.json").read_text(encoding="utf8"))
    manifest=record["manifest"]
    sig=base64.b64decode(record["ed25519_signature_b64"],validate=True)
    verification_key.verify(sig,canonical(manifest))
    if manifest["schema"]!="encrypted-backup-demo-v1" or \
        manifest["encryption_state"]!="PRE_ENCRYPTED_SOURCE_ONLY":
        raise ValueError("unexpected backup manifest")
    files=[]
    for row in manifest["items"]:
        name=row["name"]
        if Path(name).name!=name or not name.endswith(".vault"):
            raise ValueError("invalid backup filename")
        path=source/name
        if path.is_symlink() or not path.is_file():
            raise ValueError("missing or linked entry")
        content=path.read_bytes()
        if hashlib.sha256(content).hexdigest()!=row["ciphertext_sha256"] or \
                len(content)!=row["bytes"]:
            raise ValueError("encrypted backup tampered or incomplete")
        files.append(path)
    if not files:
        raise ValueError("empty backup")
    return files

def restore_backup(source: Path, destination: Path, verification_key: Ed25519PublicKey) -> list[Path]:
    files=verify_backup(source,verification_key)
    destination.mkdir(parents=True,exist_ok=True)
    if any((destination/f.name).exists() for f in files):
        raise FileExistsError("restore refuses overwrite")
    output=[]
    for source_file in files:
        target=destination/source_file.name
        with source_file.open("rb") as inp, target.open("xb") as out:
            os.chmod(target,0o600)
            shutil.copyfileobj(inp,out)
            out.flush(); os.fsync(out.fileno())
        output.append(target)
    return output
