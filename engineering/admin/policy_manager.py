"""Simulated policy provisioning with Ed25519 signatures; synthetic IDs ONLY.

No real user/deny/watch lists or person identities should ever be stored in this
source tree. This does not provide production authorization, encryption at rest,
legal basis, tamper-resistant storage or multi-tenant RBAC.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

def compact(data) -> bytes:
    return json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()

def validate(policy: dict) -> None:
    required=("policy_id","purpose_id","active_model_id","gallery_revision",
              "allowlist","watchlist","review_only")
    if not isinstance(policy,dict) or any(k not in policy for k in required):
        raise ValueError("incomplete versioned policy")
    if policy["review_only"] is not True:
        raise ValueError("synthetic watchlist alerts require human review")
    for key in ("allowlist","watchlist"):
        if not isinstance(policy[key],list) or not all(
                isinstance(i,str) and i.startswith("lab-") for i in policy[key]):
            raise ValueError("this demonstration accepts only lab-* pseudonyms")
    if set(policy["allowlist"]) & set(policy["watchlist"]):
        raise ValueError("overlapping allow/watch groups must be resolved")
    if len(set(policy["allowlist"])) != len(policy["allowlist"]):
        raise ValueError("duplicate allowed entry")
    if len(set(policy["watchlist"])) != len(policy["watchlist"]):
        raise ValueError("duplicate watch entry")

def sign(policy: dict, key: Ed25519PrivateKey) -> dict:
    validate(policy)
    digest=hashlib.sha256(compact(policy)).hexdigest()
    claims={"policy_hash":digest,"revision":policy["policy_id"],
            "model_id":policy["active_model_id"],
            "gallery_revision":policy["gallery_revision"]}
    sig=key.sign(compact(claims))
    return {"claims":claims,"signature_b64":base64.b64encode(sig).decode()}

def verify(policy: dict, envelope: dict, key: Ed25519PublicKey) -> None:
    validate(policy)
    claims=envelope["claims"]
    key.verify(base64.b64decode(envelope["signature_b64"],validate=True),compact(claims))
    if claims["policy_hash"]!=hashlib.sha256(compact(policy)).hexdigest():
        raise ValueError("policy was modified")
    if claims["revision"]!=policy["policy_id"] or \
        claims["model_id"]!=policy["active_model_id"] or \
        claims["gallery_revision"]!=policy["gallery_revision"]:
        raise ValueError("metadata mismatch")

def activate(root: Path, policy: dict, envelope: dict, key: Ed25519PublicKey) -> Path:
    verify(policy,envelope,key)
    root.mkdir(parents=True,exist_ok=True)
    manifest={"policy":policy,"signed":envelope}
    with tempfile.NamedTemporaryFile(mode="wb",dir=root,prefix=".policy-",delete=False) as h:
        h.write(compact(manifest))
        h.flush()
        os.fsync(h.fileno())
        tmp=Path(h.name)
    target=root/"active-synthetic-policy.json"
    os.replace(tmp,target)
    return target
