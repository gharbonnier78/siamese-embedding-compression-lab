"""Offline 512D image descriptor and 128D projection tests. Non-human fixtures only."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from sim.pixel_replay import (
    descriptor512, simulate_abstract_image, generate_fixtures, safe_read,
    run_comparison, random_projection, project, export_report, load_external_projection
)
import numpy as np

class PixelReplayTests(unittest.TestCase):
    def test_feature_dimensions_and_finite_unit_norm(self):
        image=simulate_abstract_image(1,"RGB",0)
        vec=descriptor512(image)
        self.assertEqual(vec.shape,(512,))
        self.assertTrue(np.all(np.isfinite(vec)))
        self.assertAlmostEqual(float(np.linalg.norm(vec)),1.,places=5)
        p=random_projection(seed=23)
        self.assertEqual(p.shape,(512,128))
        self.assertEqual(project(vec,"random128",p).shape,(128,))

    def test_replay_same_images_and_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"samples"
            m=generate_fixtures(source,subjects=4)
            a=run_comparison(source,m,["dct512","random128"])
            b=run_comparison(source,m,["dct512","random128"])
            self.assertEqual(a,b)
            self.assertEqual(a["manifest"]["sample_count"],10)
            self.assertEqual(len(a["comparisons"]),20)
            self.assertEqual(set(r["dimension"] for r in a["comparisons"]),{128,512})
            self.assertTrue(all(r["source"]=="ABSTRACT_SYNTHETIC_IMAGES_NOT_FACES" for r in a["comparisons"]))
            folder=Path(tmp)/"output"
            export_report(a,folder)
            self.assertTrue((folder/"offline_replay_report.html").exists())
            self.assertTrue((folder/"image_comparison.csv").exists())
            self.assertNotIn("face identification validated", (folder/"offline_replay_report.html").read_text())

    def test_manifest_tamper_and_real_image_access_denied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            manifest=generate_fixtures(root,subjects=2)
            obj=manifest["captures"][0].copy()
            image=safe_read(root,obj,manifest["purpose_id"])
            self.assertEqual(descriptor512(image).shape,(512,))
            obj["sha256"]="0"*64
            with self.assertRaises(ValueError):
                safe_read(root,obj,manifest["purpose_id"])
            manifest["dataset_class"]="REAL_IDENTIFIABLE_FACES"
            with self.assertRaises(PermissionError):
                run_comparison(root,manifest,["dct512"])

    def test_siamesetraining_checkpoint_cannot_be_faked(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"fake.npz"
            np.savez_compressed(p,matrix=np.zeros((512,128),dtype=np.float32),
                                metadata=json.dumps({"method":"siamese128",
                                     "data_split":"TEST_ONLY",
                                     "training_dataset_sha256":"bad",
                                     "model_revision":"bad"}))
            with self.assertRaises(ValueError):
                load_external_projection(p,"siamese128")

if __name__=="__main__":unittest.main()
