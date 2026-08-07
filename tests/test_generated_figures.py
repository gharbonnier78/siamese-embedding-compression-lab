"""Tests for replay-derived paper figures."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_STEMS = {
    "study0_benchmark_metrics",
    "study0_noninferiority",
    "study0_protocol",
    "study0_storage",
    "study0_threshold_transfer",
}
RUN_ID = "lfw_resnet18_siamese_projection_v0_1-89179914-911192ee-64559cbd"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GeneratedFigureTests(unittest.TestCase):
    def _generate(self, destination: Path) -> dict[str, object]:
        environment = os.environ.copy()
        environment["MPLCONFIGDIR"] = str(destination.parent / "mplconfig")
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/generate_research_figures.py"),
                "--root",
                str(ROOT),
                "--output",
                str(destination),
            ],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )
        return json.loads((destination / "figures_manifest.json").read_text())

    def test_outputs_are_complete_traceable_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first = base / "first"
            second = base / "second"
            manifest_first = self._generate(first)
            manifest_second = self._generate(second)

            self.assertEqual(manifest_first["run_id"], RUN_ID)
            self.assertEqual(manifest_first, manifest_second)
            self.assertEqual({path.stem for path in first.glob("*.pdf")}, EXPECTED_STEMS)
            self.assertEqual({path.stem for path in first.glob("*.png")}, EXPECTED_STEMS)
            for name, expected in manifest_first["outputs"].items():
                self.assertEqual(digest(first / name), expected)
                self.assertEqual(digest(second / name), expected)


if __name__ == "__main__":
    unittest.main()
