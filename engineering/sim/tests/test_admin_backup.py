import os
from pathlib import Path
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(HERE))
from admin.policy_manager import sign, verify, activate
from sim.vault import store_artifact, read_artifact
from sim.backup import create_backup, verify_backup, restore_backup
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


class AdminBackupTests(unittest.TestCase):
    def example_policy(self):
        return {"policy_id":"demo-p1","purpose_id":"synthetic-only",
                "active_model_id":"model-sim-128",
                "gallery_revision":"synthetic-gallery-v1",
                "allowlist":["lab-001"],"watchlist":["lab-003"],
                "review_only":True}

    def test_signed_policy_validates_and_rejects_modification(self):
        private=Ed25519PrivateKey.generate()
        policy=self.example_policy()
        env=sign(policy,private)
        verify(policy,env,private.public_key())
        with tempfile.TemporaryDirectory() as d:
            p=activate(Path(d),policy,env,private.public_key())
            self.assertTrue(p.exists())
        modified=dict(policy,watchlist=["lab-004"])
        with self.assertRaises(ValueError):
            verify(modified,env,private.public_key())
        conflict=dict(policy,watchlist=["lab-001"])
        with self.assertRaises(ValueError):
            sign(conflict,private)

    def test_sealed_backup_verified_restored_and_tamper_rejected(self):
        private=Ed25519PrivateKey.generate()
        vault_key=os.urandom(32)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)
            source=path/"vault"
            archive=path/"backup"
            restored=path/"restored"
            entry=store_artifact(source,b"simulated permitted acquisition, no face",
                                 {"purpose_id":"test-only","run_id":"synthetic-42"},vault_key)
            create_backup(source,archive,private)
            files=verify_backup(archive,private.public_key())
            self.assertEqual(len(files),1)
            out=restore_backup(archive,restored,private.public_key())
            self.assertEqual(len(out),1)
            self.assertEqual(read_artifact(out[0],vault_key),
                             (b"simulated permitted acquisition, no face",
                              {"purpose_id":"test-only","run_id":"synthetic-42"}))
            with self.assertRaises(FileExistsError):
                restore_backup(archive,restored,private.public_key())
            with files[0].open("ab") as h:
                h.write(b"corruption")
            with self.assertRaises(ValueError):
                verify_backup(archive,private.public_key())


if __name__=="__main__":
    unittest.main()
