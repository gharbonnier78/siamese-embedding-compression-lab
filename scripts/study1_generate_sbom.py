from __future__ import annotations

import hashlib
import importlib.metadata as md
import json
import platform
import sys
from pathlib import Path


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> int:
    packages = sorted(
        ({"name": d.metadata.get("Name", d.name), "version": d.version} for d in md.distributions()),
        key=lambda x: (x["name"].lower(), x["version"]),
    )
    payload = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": "siamese-embedding-compression-lab-study1",
                "version": "preregistration",
            },
            "properties": [
                {"name": "python.version", "value": platform.python_version()},
                {"name": "python.implementation", "value": platform.python_implementation()},
                {"name": "platform", "value": platform.platform()},
            ],
        },
        "components": [
            {
                "type": "library",
                "name": p["name"],
                "version": p["version"],
                "bom-ref": f"pkg:pypi/{p['name'].lower()}@{p['version']}",
            }
            for p in packages
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, indent=2) + "\n"
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "artifacts/study1/sbom.cdx.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(encoded, encoding="utf-8")
    (out.with_suffix(out.suffix + ".sha256")).write_text(
        sha256_text(encoded) + "  " + out.name + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
