"""All inputs synthetic. Unit tests are not instrument or physical qualification."""
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from sim.bench import simulate
from sim.vault import seal_bytes, open_bytes, store_artifact, read_artifact
from admin.package_manager import signed_manifest,verify_manifest,activate_local_model
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


class StackTests(unittest.TestCase):
    def test_bench_same_seed(self):
        self.assertEqual(simulate(12,12),simulate(12,12))
        self.assertNotEqual(simulate(12,12),simulate(13,12))

    def test_integral_positive(self):
        samples=simulate(1,6)
        self.assertGreater(samples[-1]["energy_wh_ASSUMED"],0)
        self.assertEqual(samples[-1]["source"],"SYNTHETIC")

    def test_vault_encrypt_decrypt_and_integrity(self):
        key=os.urandom(32)
        plain=b"synthetic experiment data"
        metadata={"purpose_id":"synthetic-unit-test","seed":7}
        a=seal_bytes(plain,metadata,key)
        b=seal_bytes(plain,metadata,key)
        self.assertNotEqual(a,b)
        self.assertEqual(open_bytes(a,key),(plain,metadata))
        with self.assertRaises(Exception):
            open_bytes(a,os.urandom(32))
        with tempfile.TemporaryDirectory() as d:
            path=store_artifact(Path(d),plain,metadata,key)
            self.assertEqual(read_artifact(path,key),(plain,metadata))
            with self.assertRaises(Exception):
                read_artifact(path,os.urandom(32))

    def test_model_signature_and_pointer(self):
        priv=Ed25519PrivateKey.generate()
        payload=b"synthetic-model"
        claims={"model_id":"test","projection_id":"p512","dimension":512,
                "index_version":"synthetic-index","firmware_compat":"test-fw"}
        signature=signed_manifest(payload,claims,priv)
        self.assertEqual(verify_manifest(payload,signature,priv.public_key())["dimension"],512)
        with self.assertRaises(ValueError):
            verify_manifest(payload+b"tampered",signature,priv.public_key())
        other=Ed25519PrivateKey.generate()
        with self.assertRaises(Exception):
            verify_manifest(payload,signature,other.public_key())
        with tempfile.TemporaryDirectory() as d:
            active=activate_local_model(Path(d),payload,signature,priv.public_key())
            self.assertTrue(active.exists())
            self.assertEqual(active.name,"active.json")

if __name__=="__main__":
    unittest.main()
