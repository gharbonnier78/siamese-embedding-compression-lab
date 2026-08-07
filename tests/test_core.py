from __future__ import annotations

import json
import tempfile
import unittest

import numpy as np

from siamese_compression_lab.config import (
    DataConfig,
    EvaluationConfig,
    ExperimentConfig,
    TrainingConfig,
)
from siamese_compression_lab.data import make_synthetic_bundle
from siamese_compression_lab.experiment import run_experiment
from siamese_compression_lab.metrics import (
    evaluate_at_threshold,
    evaluate_benchmark_at_fmr,
    threshold_at_fmr,
)
from siamese_compression_lab.models import SiameseLinearProjection


class DataContractTests(unittest.TestCase):
    def test_synthetic_splits_are_identity_disjoint(self) -> None:
        bundle = make_synthetic_bundle(DataConfig())
        bundle.validate_no_identity_leakage()
        self.assertFalse(bundle.train.identities & bundle.validation.identities)
        self.assertFalse(bundle.train.identities & bundle.test.identities)
        self.assertFalse(bundle.validation.identities & bundle.test.identities)


class MetricTests(unittest.TestCase):
    def test_validation_threshold_meets_empirical_fmr_budget(self) -> None:
        same = np.array([0] * 100 + [1] * 20)
        distances = np.concatenate([np.linspace(0.2, 1.2, 100), np.linspace(0.1, 0.8, 20)])
        threshold, evidence = threshold_at_fmr(same, distances, 0.01)
        self.assertLessEqual(evidence["validation_fmr"], 0.01)
        result = evaluate_at_threshold(
            same,
            distances,
            threshold=threshold,
            target_fmr=0.01,
            threshold_source="validation",
        )
        self.assertLessEqual(result.fmr, 0.01)

    def test_non_validation_threshold_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_at_threshold(
                np.array([0, 1]),
                np.array([1.0, 0.1]),
                threshold=0.5,
                target_fmr=0.01,
                threshold_source="test",
            )

    def test_equal_fmr_benchmark_is_marked_non_deployable(self) -> None:
        same = np.array([0] * 100 + [1] * 20)
        distances = np.concatenate([np.linspace(0.2, 1.2, 100), np.linspace(0.1, 0.8, 20)])
        result, _ = evaluate_benchmark_at_fmr(same, distances, target_fmr=0.01)
        self.assertEqual(result.threshold_source, "test_benchmark_only")
        self.assertLessEqual(result.fmr, 0.01)


class GradientTests(unittest.TestCase):
    def test_linear_siamese_gradient_matches_finite_difference(self) -> None:
        rng = np.random.default_rng(7)
        model = SiameseLinearProjection(5, 3, seed=11)
        x1 = rng.normal(size=(4, 5)).astype(np.float32)
        x2 = rng.normal(size=(4, 5)).astype(np.float32)
        same = np.array([1, 0, 1, 0], dtype=np.int8)
        _, gradient, _ = model._loss_and_gradients(x1, x2, same)
        row, col = 1, 2
        original = float(model.weights[row, col])
        epsilon = 1e-3
        model.weights[row, col] = original + epsilon
        plus, _, _ = model._loss_and_gradients(x1, x2, same)
        model.weights[row, col] = original - epsilon
        minus, _, _ = model._loss_and_gradients(x1, x2, same)
        model.weights[row, col] = original
        numerical = (plus - minus) / (2 * epsilon)
        self.assertAlmostEqual(float(gradient[row, col]), numerical, delta=2e-3)


class ReplayTests(unittest.TestCase):
    def test_smoke_run_emits_guarded_replay_bundle(self) -> None:
        config = ExperimentConfig(
            experiment_id="unit_smoke",
            data=DataConfig(
                mode="synthetic",
                synthetic_input_dim=80,
                synthetic_latent_dim=8,
                synthetic_train_identities=12,
                synthetic_val_identities=8,
                synthetic_test_identities=8,
                synthetic_images_per_identity=4,
                synthetic_pairs_per_split=40,
            ),
            training=TrainingConfig(
                output_dim=4,
                seeds=(3,),
                epochs=3,
                batch_size=16,
                patience=2,
            ),
            evaluation=EvaluationConfig(
                target_fmrs=(0.1,),
                bootstrap_replicates=20,
                gallery_sizes=(1000,),
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            run_dir = run_experiment(config, directory)
            required = {
                "run_manifest.json",
                "data/events.jsonl",
                "routes.csv",
                "metrics.csv",
                "audit_trace.jsonl",
                "replay.compact.json",
                "benchmark_thresholds_non_deployable.csv",
                "method_noninferiority_summary.csv",
            }
            present = {
                str(path.relative_to(run_dir)) for path in run_dir.rglob("*") if path.is_file()
            }
            self.assertTrue(required <= present)
            manifest = json.loads((run_dir / "run_manifest.json").read_text())
            self.assertEqual(manifest["run_status"], "SMOKE_VALIDATED")
            self.assertEqual(manifest["evidence_level"], "synthetic_smoke")
            self.assertFalse(manifest["scientific_claim_allowed"])
            self.assertIn("non-deployable", manifest["benchmark_metric_policy"])
            events = [json.loads(line) for line in (run_dir / "data/events.jsonl").read_text().splitlines()]
            opened = next(i for i, event in enumerate(events) if event["event_type"] == "test_opened_once")
            frozen = [i for i, event in enumerate(events) if event["event_type"] == "route_completed"]
            evaluated = [i for i, event in enumerate(events) if event["event_type"] == "route_test_evaluated"]
            self.assertLess(max(frozen), opened)
            self.assertLess(opened, min(evaluated))


if __name__ == "__main__":
    unittest.main()
