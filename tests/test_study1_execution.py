from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from siamese_compression_lab.study1_execution import (
    Provenance,
    ShardManifest,
    assert_homogeneous_provenance,
    normalize_adaface_bgr_uint8,
    sha256_file,
    stable_shard_id,
    validate_shard_for_resume,
    write_completed_shard_manifest,
)


class Study1ExecutionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.prov = Provenance(
            model_sha256="a" * 64,
            preprocessing_id="adaface-r100-bgr-112-v1",
            dataset_manifest_sha256="b" * 64,
            protocol_id="study1a-gate-a-v1",
        )

    def test_shard_id_depends_on_scientific_bounds_not_worker(self) -> None:
        a = stable_shard_id(self.prov.dataset_manifest_sha256, 0, 100)
        b = stable_shard_id(self.prov.dataset_manifest_sha256, 0, 100)
        c = stable_shard_id(self.prov.dataset_manifest_sha256, 100, 200)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_resume_accepts_only_matching_payload_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            payload = root / "part.bin"
            payload.write_bytes(b"frozen embedding shard")
            manifest_path = root / "part.manifest.json"
            manifest = ShardManifest(
                shard_id="s0",
                provenance=self.prov,
                row_count=1,
                payload_sha256=sha256_file(payload),
            )
            write_completed_shard_manifest(manifest_path, manifest)
            self.assertTrue(validate_shard_for_resume(manifest_path, payload, self.prov))
            payload.write_bytes(b"corrupted")
            self.assertFalse(validate_shard_for_resume(manifest_path, payload, self.prov))

    def test_aggregator_rejects_mixed_provenance(self) -> None:
        good = ShardManifest("s0", self.prov, 1, "1" * 64)
        other = ShardManifest(
            "s1",
            Provenance("c" * 64, self.prov.preprocessing_id, "b" * 64, self.prov.protocol_id),
            1,
            "2" * 64,
        )
        with self.assertRaisesRegex(ValueError, "mixed provenance"):
            assert_homogeneous_provenance([good, other])

    def test_atomic_manifest_is_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "manifest.json"
            write_completed_shard_manifest(
                path, ShardManifest("s0", self.prov, 4, "d" * 64)
            )
            decoded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(decoded["row_count"], 4)
            self.assertEqual(decoded["provenance"]["model_sha256"], "a" * 64)

    def test_adaface_preprocessing_contract(self) -> None:
        zeros = np.zeros((112, 112, 3), dtype=np.uint8)
        full = np.full((112, 112, 3), 255, dtype=np.uint8)
        self.assertTrue(np.allclose(normalize_adaface_bgr_uint8(zeros), -1.0))
        self.assertTrue(np.allclose(normalize_adaface_bgr_uint8(full), 1.0))
        with self.assertRaises(ValueError):
            normalize_adaface_bgr_uint8(np.zeros((224, 224, 3), dtype=np.uint8))


if __name__ == "__main__":
    unittest.main()
