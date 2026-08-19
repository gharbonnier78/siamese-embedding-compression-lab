from __future__ import annotations

import json
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd

from siamese_compression_lab.historical_reanalysis import (
    ALL_METHODS,
    CANDIDATE_METHODS,
    EXPECTED_BOOTSTRAP_BASE_SEED,
    EXPECTED_MODEL_SEEDS,
    EXPECTED_RUN_ID,
    FrozenRunnerConfig,
    HistoricalInputError,
    HistoricalSourceIdentity,
    execute_historical_reanalysis,
    frozen_runner_config,
    load_validation_thresholds,
    validate_historical_sources,
    validate_score_routes,
)
from siamese_compression_lab.subject_bootstrap import (
    BootstrapReplicate,
    DegenerateReplicateAudit,
    DegenerateReplicateError,
    SubjectPairRow,
)
from siamese_compression_lab.subject_bootstrap_io import sha256_file
from siamese_compression_lab.subject_bootstrap_operational import OperationalReplicate

ROOT = Path(__file__).resolve().parents[1]
STUDY_PROTOCOL = ROOT / "protocol/studies/study_0_subject_bootstrap_v0.2.2.yaml"


def _historical_configuration() -> dict:
    return {
        "training": {"seeds": list(EXPECTED_MODEL_SEEDS)},
        "evaluation": {
            "target_fmrs": [0.01],
            "bootstrap_replicates": 2000,
            "bootstrap_seed": EXPECTED_BOOTSTRAP_BASE_SEED,
            "noninferiority_delta_fnmr": 0.03,
        },
    }


def _small_rows() -> list[SubjectPairRow]:
    return [
        SubjectPairRow("g_a", 1, "A", "A", "matched", 0),
        SubjectPairRow("g_b", 1, "B", "B", "matched", 1),
        SubjectPairRow("i_ab", 0, "A", "B", "mismatched", 0),
        SubjectPairRow("i_ac", 0, "A", "C", "mismatched", 1),
    ]


def _small_config() -> FrozenRunnerConfig:
    return FrozenRunnerConfig(
        run_id=EXPECTED_RUN_ID,
        model_seeds=EXPECTED_MODEL_SEEDS,
        bootstrap_base_seed=EXPECTED_BOOTSTRAP_BASE_SEED,
        bootstrap_replicates=2,
        convergence_checkpoints=(1, 2),
        target_fmr=0.01,
        noninferiority_margin_fnmr=0.03,
        sampling_unit="subject_slot",
        subject_draws_per_replicate=3,
        paired_routes_same_draw=True,
        degenerate_replicate_action="FAIL_REANALYSIS",
        methods=ALL_METHODS,
        reference_method="raw",
    )


def _score_rows() -> list[dict]:
    rows = _small_rows()
    output = []
    route_keys = [("raw", EXPECTED_MODEL_SEEDS[0])] + [
        (method, seed) for method in CANDIDATE_METHODS for seed in EXPECTED_MODEL_SEEDS
    ]
    for method_index, (method, seed) in enumerate(route_keys):
        for pair_index, row in enumerate(rows):
            output.append(
                {
                    "run_id": EXPECTED_RUN_ID,
                    "method": method,
                    "seed": seed,
                    "pair_id": row.pair_id,
                    "same": row.same,
                    "distance": 0.1 + 0.05 * pair_index + 0.001 * method_index,
                }
            )
    return output


def _threshold_rows() -> list[dict]:
    route_keys = [("raw", EXPECTED_MODEL_SEEDS[0])] + [
        (method, seed) for method in CANDIDATE_METHODS for seed in EXPECTED_MODEL_SEEDS
    ]
    return [
        {
            "run_id": EXPECTED_RUN_ID,
            "method": method,
            "seed": seed,
            "target_fmr": 0.01,
            "threshold": 0.25,
            "threshold_source": "validation",
        }
        for method, seed in route_keys
    ]


def _pair_level_rows() -> list[dict]:
    return [
        {
            "run_id": EXPECTED_RUN_ID,
            "candidate_method": method,
            "candidate_seed": seed,
            "reference_method": "raw",
            "target_fmr": 0.01,
            "delta_fnmr_mean": 0.01,
            "delta_fnmr_ci_low": -0.01,
            "delta_fnmr_ci_high": 0.02,
        }
        for method in CANDIDATE_METHODS
        for seed in EXPECTED_MODEL_SEEDS
    ]


class HistoricalRunnerContractTests(unittest.TestCase):
    def test_frozen_config_preserves_original_bootstrap_seed_binding(self) -> None:
        manifest = {"configuration": _historical_configuration()}
        config = frozen_runner_config(STUDY_PROTOCOL, manifest)
        self.assertEqual(config.bootstrap_base_seed, 20260806)
        self.assertEqual(config.model_seeds, (11, 29, 47, 71, 101))
        self.assertEqual(config.bootstrap_replicates, 10000)
        self.assertEqual(config.convergence_checkpoints, (2000, 5000, 10000))
        self.assertEqual(config.target_fmr, 0.01)
        self.assertEqual(config.noninferiority_margin_fnmr, 0.03)

    def test_score_route_set_must_be_exact(self) -> None:
        frame = pd.DataFrame(_score_rows())
        validate_score_routes(frame)
        broken = frame[~((frame.method == "siamese") & (frame.seed == 101))]
        with self.assertRaisesRegex(HistoricalInputError, "route/seed set"):
            validate_score_routes(broken)

    def test_operational_thresholds_cannot_be_test_recalibrated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "thresholds.csv"
            frame = pd.DataFrame(_threshold_rows())
            frame.to_csv(path, index=False)
            thresholds = load_validation_thresholds(path)
            self.assertEqual(len(thresholds), 16)
            frame.loc[0, "threshold_source"] = "test"
            frame.to_csv(path, index=False)
            with self.assertRaisesRegex(HistoricalInputError, "validation-frozen"):
                load_validation_thresholds(path)

    def test_source_validation_is_manifest_and_hash_bound_before_score_parse(self) -> None:
        rows = _small_rows()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir = root / "historical"
            run_dir.mkdir()
            matched = root / "matched.csv"
            mismatched = root / "mismatched.csv"
            matched.write_text("name,a,b\nA,1,2\n", encoding="utf-8")
            mismatched.write_text("name1,a,name2,b\nA,1,B,1\n", encoding="utf-8")
            pd.DataFrame(_score_rows()).to_csv(run_dir / "test_pair_scores.csv", index=False)
            pd.DataFrame(_threshold_rows()).to_csv(run_dir / "thresholds.csv", index=False)
            pd.DataFrame(_pair_level_rows()).to_csv(
                run_dir / "paired_noninferiority.csv", index=False
            )
            artifact_rows = []
            for name in ("test_pair_scores.csv", "thresholds.csv", "paired_noninferiority.csv"):
                path = run_dir / name
                artifact_rows.append(
                    {"path": name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
                )
            manifest = {
                "run_id": EXPECTED_RUN_ID,
                "configuration": _historical_configuration(),
                "dataset": {
                    "dev_test_files": {
                        "matched_pairs_sha256": sha256_file(matched),
                        "mismatched_pairs_sha256": sha256_file(mismatched),
                    }
                },
                "artifacts": artifact_rows,
            }
            (run_dir / "run_manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            score = run_dir / "test_pair_scores.csv"
            identity = HistoricalSourceIdentity(score.stat().st_size, sha256_file(score))
            with mock.patch(
                "siamese_compression_lab.historical_reanalysis.reconstruct_lfw_devtest_subject_map",
                return_value=rows,
            ), mock.patch(
                "siamese_compression_lab.historical_reanalysis.validate_subject_map",
                return_value={"pairs": 1000, "genuine": 500, "impostor": 500, "subjects": 963},
            ):
                _, config, returned_rows, source_manifest = validate_historical_sources(
                    historical_run_dir=run_dir,
                    matched_path=matched,
                    mismatched_path=mismatched,
                    study_protocol_path=STUDY_PROTOCOL,
                    score_identity=identity,
                )
            self.assertEqual(config.run_id, EXPECTED_RUN_ID)
            self.assertEqual(returned_rows, rows)
            self.assertEqual(
                source_manifest["historical_run"]["artifacts"][0]["sha256"],
                sha256_file(score),
            )
            score.write_text("mutated\n", encoding="utf-8")
            with self.assertRaises((HistoricalInputError, ValueError)):
                with mock.patch(
                    "siamese_compression_lab.historical_reanalysis.reconstruct_lfw_devtest_subject_map",
                    return_value=rows,
                ), mock.patch(
                    "siamese_compression_lab.historical_reanalysis.validate_subject_map",
                    return_value={"pairs": 1000, "genuine": 500, "impostor": 500, "subjects": 963},
                ):
                    validate_historical_sources(
                        historical_run_dir=run_dir,
                        matched_path=matched,
                        mismatched_path=mismatched,
                        study_protocol_path=STUDY_PROTOCOL,
                        score_identity=identity,
                    )


class HistoricalRunnerMaterializationTests(unittest.TestCase):
    def _prepare_fixture(self, root: Path) -> tuple[Path, Path, Path, Path, Path]:
        run_dir = root / "historical"
        run_dir.mkdir()
        pd.DataFrame(_score_rows()).to_csv(run_dir / "test_pair_scores.csv", index=False)
        pd.DataFrame(_threshold_rows()).to_csv(run_dir / "thresholds.csv", index=False)
        pd.DataFrame(_pair_level_rows()).to_csv(run_dir / "paired_noninferiority.csv", index=False)
        coverage_sim = root / "coverage_simulation.csv"
        coverage_gate = root / "coverage_gate.json"
        coverage_sim.write_text("scenario,coverage\nfixture,0.95\n", encoding="utf-8")
        coverage_gate.write_text('{"status":"PASS"}\n', encoding="utf-8")
        matched = root / "matched.csv"
        mismatched = root / "mismatched.csv"
        matched.write_text("fixture\n", encoding="utf-8")
        mismatched.write_text("fixture\n", encoding="utf-8")
        return run_dir, matched, mismatched, coverage_sim, coverage_gate

    @staticmethod
    def _representation_replicates(**kwargs):
        del kwargs
        return [
            BootstrapReplicate(0, 0.20, 0.19, 0.01, 0.2, 0.2, 3, 3),
            BootstrapReplicate(1, 0.21, 0.19, 0.02, 0.2, 0.2, 3, 3),
        ]

    @staticmethod
    def _operational_replicates(**kwargs):
        threshold = float(kwargs["validation_threshold"])
        return [
            OperationalReplicate(0, threshold, 0.20, 0.01, 3, 3),
            OperationalReplicate(1, threshold, 0.21, 0.02, 3, 3),
        ]

    def test_complete_bundle_is_materialized_before_interpretation(self) -> None:
        rows = _small_rows()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir, matched, mismatched, coverage_sim, coverage_gate = self._prepare_fixture(root)
            destination = root / "out"
            original_score_hash = sha256_file(run_dir / "test_pair_scores.csv")
            source_manifest = {"fixture": True}
            diagnostics = [
                {
                    "replicate": 0,
                    "genuine_weight": 3,
                    "impostor_weight": 3,
                    "effective_genuine_edges": 2,
                    "effective_impostor_edges": 2,
                },
                {
                    "replicate": 1,
                    "genuine_weight": 3,
                    "impostor_weight": 3,
                    "effective_genuine_edges": 2,
                    "effective_impostor_edges": 2,
                },
            ]
            with mock.patch(
                "siamese_compression_lab.historical_reanalysis.validate_historical_sources",
                return_value=({}, _small_config(), rows, source_manifest),
            ), mock.patch(
                "siamese_compression_lab.historical_reanalysis._bootstrap_diagnostics",
                return_value=diagnostics,
            ), mock.patch(
                "siamese_compression_lab.historical_reanalysis.subject_bootstrap_delta_fnmr",
                side_effect=self._representation_replicates,
            ), mock.patch(
                "siamese_compression_lab.historical_reanalysis.subject_bootstrap_fixed_threshold",
                side_effect=self._operational_replicates,
            ), mock.patch(
                "siamese_compression_lab.historical_reanalysis._git_head",
                return_value="fixture-head",
            ):
                manifest_path = execute_historical_reanalysis(
                    repo_root=ROOT,
                    historical_run_dir=run_dir,
                    matched_path=matched,
                    mismatched_path=mismatched,
                    output_dir=destination,
                    study_protocol_path=STUDY_PROTOCOL,
                    coverage_simulation_path=coverage_sim,
                    coverage_gate_path=coverage_gate,
                    score_identity=HistoricalSourceIdentity(
                        (run_dir / "test_pair_scores.csv").stat().st_size,
                        original_score_hash,
                    ),
                )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["run_status"], "MATERIALIZED_NOT_INTERPRETED")
            self.assertFalse(manifest["scientific_claim_allowed"])
            self.assertEqual(manifest["interpretation_status"], "PENDING")
            self.assertFalse(manifest["original_historical_artifacts_mutated"])
            self.assertEqual(sha256_file(run_dir / "test_pair_scores.csv"), original_score_hash)
            self.assertEqual(len(pd.read_csv(destination / "subject_bootstrap_seed_summary.csv")), 15)
            self.assertEqual(len(pd.read_csv(destination / "threshold_transfer_uncertainty.csv")), 16)
            self.assertTrue((destination / "pair_vs_subject_sensitivity.csv").is_file())
            self.assertTrue((destination / "subject_bootstrap_replicates.csv").is_file())
            self.assertTrue((destination / "run_manifest.json").is_file())
            with self.assertRaises(FileExistsError):
                execute_historical_reanalysis(
                    repo_root=ROOT,
                    historical_run_dir=run_dir,
                    matched_path=matched,
                    mismatched_path=mismatched,
                    output_dir=destination,
                    study_protocol_path=STUDY_PROTOCOL,
                    coverage_simulation_path=coverage_sim,
                    coverage_gate_path=coverage_gate,
                )

    def test_degeneracy_fails_without_complete_manifest(self) -> None:
        rows = _small_rows()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_dir, matched, mismatched, coverage_sim, coverage_gate = self._prepare_fixture(root)
            destination = root / "failed"
            audit = DegenerateReplicateAudit(
                replicate=1,
                reason="zero genuine or impostor total weight",
                genuine_weight=0,
                impostor_weight=0,
                effective_genuine_edges=0,
                effective_impostor_edges=0,
                completed_replicates=1,
            )
            with mock.patch(
                "siamese_compression_lab.historical_reanalysis.validate_historical_sources",
                return_value=({}, _small_config(), rows, {"fixture": True}),
            ), mock.patch(
                "siamese_compression_lab.historical_reanalysis._bootstrap_diagnostics",
                return_value=[
                    {
                        "replicate": 0,
                        "genuine_weight": 3,
                        "impostor_weight": 3,
                        "effective_genuine_edges": 2,
                        "effective_impostor_edges": 2,
                    },
                    {
                        "replicate": 1,
                        "genuine_weight": 0,
                        "impostor_weight": 0,
                        "effective_genuine_edges": 0,
                        "effective_impostor_edges": 0,
                    },
                ],
            ), mock.patch(
                "siamese_compression_lab.historical_reanalysis.subject_bootstrap_delta_fnmr",
                side_effect=DegenerateReplicateError(audit),
            ):
                with self.assertRaises(DegenerateReplicateError):
                    execute_historical_reanalysis(
                        repo_root=ROOT,
                        historical_run_dir=run_dir,
                        matched_path=matched,
                        mismatched_path=mismatched,
                        output_dir=destination,
                        study_protocol_path=STUDY_PROTOCOL,
                        coverage_simulation_path=coverage_sim,
                        coverage_gate_path=coverage_gate,
                    )
            self.assertFalse((destination / "run_manifest.json").exists())
            self.assertTrue((destination / "run_failure.json").is_file())
            failure = json.loads((destination / "run_failure.json").read_text(encoding="utf-8"))
            self.assertEqual(failure["status"], "FAILED_NOT_INTERPRETED")
            self.assertFalse(failure["scientific_claim_allowed"])


class HistoricalRunnerCliBoundaryTests(unittest.TestCase):
    def test_preflight_completes_before_executor_is_called(self) -> None:
        script_globals = runpy.run_path(str(ROOT / "scripts/run_study0_historical_reanalysis.py"))
        main = script_globals["main"]
        order: list[str] = []

        def preflight():
            order.append("preflight")
            return {}, "refs/remotes/origin/main"

        def executor(**kwargs):
            del kwargs
            self.assertEqual(order, ["preflight"])
            order.append("execute")
            return Path("fixture/run_manifest.json")

        argv = [
            "run_study0_historical_reanalysis.py",
            "--historical-run-dir",
            "historical",
            "--matched-devtest",
            "matched.csv",
            "--mismatched-devtest",
            "mismatched.csv",
            "--output-dir",
            "out",
        ]
        with mock.patch.object(sys, "argv", argv), mock.patch.dict(
            main.__globals__,
            {
                "preflight_historical_reanalysis": preflight,
                "execute_historical_reanalysis": executor,
            },
        ):
            self.assertEqual(main(), 0)
        self.assertEqual(order, ["preflight", "execute"])


if __name__ == "__main__":
    unittest.main()
