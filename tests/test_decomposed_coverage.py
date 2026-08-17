from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import yaml

from siamese_compression_lab.coverage_execution import (
    DatasetCoverageOutcome,
    aggregate_dataset_outcomes,
    build_scenario_execution_plan,
    run_coverage_scenario_datasets,
    spawn_scenario_seed_sequences,
)
from siamese_compression_lab.decomposed_coverage import (
    aggregate_checkpoint_artifacts,
    contract_sha256,
    load_scenario_chunk_artifact,
    merge_scenario_chunks,
    run_coverage_scenario_range,
    scenarios_from_contract,
    sha256_file,
    validate_cancelled_runtime_manifest,
    write_scenario_chunk_artifact,
)


class DecomposedCoverageTests(unittest.TestCase):
    def _contract(self) -> dict:
        return {
            "schema_version": "1.0.1",
            "contract_id": "decomposed_test_contract",
            "status": "IMPLEMENTATION_REVIEW_REQUIRED",
            "historical_study_0_scores_permitted": False,
            "root_seed": 20260807,
            "rng_hierarchy": {
                "derivation": "numpy_seedsequence_spawn",
                "arithmetic_seed_offsets_forbidden": True,
                "worker_count_must_not_change_outputs": True,
            },
            "execution": {
                "engine": "vectorized",
                "reference_oracle_engine": "legacy",
                "exact_dataset_outcome_equivalence_required": True,
                "implementation_only": True,
            },
            "bootstrap": {"replicates_per_simulated_dataset": 20},
            "simulation_precision": {
                "dataset_checkpoints": [4, 8],
                "stop_rule": "first_checkpoint_where_all_metric_mcse_lte_0_005",
                "maximum_monte_carlo_standard_error": 0.005,
            },
            "coverage_gate": {
                "binomial_interval": "clopper_pearson_exact_two_sided_95",
                "lower_bound_minimum": 0.93,
            },
            "graph": {
                "subjects": 30,
                "genuine_edges": 20,
                "impostor_edges": 20,
                "sparse_degree_exponent": 1.1,
            },
            "scenarios": [
                {
                    "name": "fixture_a",
                    "target_delta_fnmr": 0.0,
                    "subject_effect_sd_genuine": 0.04,
                    "subject_effect_sd_impostor": 0.03,
                    "candidate_reference_noise_correlation": 0.7,
                },
                {
                    "name": "fixture_b",
                    "target_delta_fnmr": 0.015,
                    "subject_effect_sd_genuine": 0.04,
                    "subject_effect_sd_impostor": 0.03,
                    "candidate_reference_noise_correlation": 0.7,
                },
            ],
        }

    def _write_contract(self, directory: Path) -> tuple[Path, dict]:
        contract = self._contract()
        path = directory / "coverage.yaml"
        path.write_text(yaml.safe_dump(contract, sort_keys=False), encoding="utf-8")
        return path, contract

    def _write_chunk(
        self,
        base: Path,
        *,
        contract_path: Path,
        contract: dict,
        scenario_index_zero: int,
        checkpoint: int,
        start: int,
        stop: int,
        workers: int = 1,
        git_commit: str = "fixture-commit",
    ) -> tuple[Path, list[DatasetCoverageOutcome]]:
        scenarios = scenarios_from_contract(contract)
        scenario = scenarios[scenario_index_zero]
        scenario_seeds = spawn_scenario_seed_sequences(
            int(contract["root_seed"]), len(scenarios)
        )
        scenario_seed = scenario_seeds[scenario_index_zero]
        outcomes = run_coverage_scenario_range(
            scenario,
            checkpoint=checkpoint,
            bootstrap_replicates=20,
            scenario_seed=scenario_seed,
            dataset_start=start,
            dataset_stop=stop,
            workers=workers,
            engine="vectorized",
        )
        output = base / f"{scenario.name}-{start}-{stop}"
        output.mkdir(parents=True, exist_ok=True)
        progress = output / "progress.jsonl"
        progress.write_text(
            json.dumps({"runtime_observability_only": True}) + "\n",
            encoding="utf-8",
        )
        write_scenario_chunk_artifact(
            output,
            outcomes=outcomes,
            progress_path=progress,
            execution_metadata={
                "complete": True,
                "historical_study_0_scores_read": False,
                "workers": workers,
            },
            repository="gharbonnier78/siamese-embedding-compression-lab",
            git_commit=git_commit,
            contract_path=contract_path,
            contract=contract,
            scenario_name=scenario.name,
            scenario_index=scenario_index_zero + 1,
            scenario_count=len(scenarios),
            checkpoint=checkpoint,
            dataset_start=start,
            dataset_stop=stop,
            bootstrap_replicates=20,
            root_seed=int(contract["root_seed"]),
            scenario_seed=scenario_seed,
            workers=workers,
            synthetic_nonproduction_fixture=True,
        )
        return output, outcomes

    def test_range_worker_count_and_chunking_preserve_monolithic_outputs(self) -> None:
        contract = self._contract()
        scenario = scenarios_from_contract(contract)[0]
        scenario_seed = spawn_scenario_seed_sequences(int(contract["root_seed"]), 2)[0]
        monolithic = run_coverage_scenario_datasets(
            scenario,
            simulated_datasets=4,
            bootstrap_replicates=20,
            scenario_seed=scenario_seed,
            workers=1,
            engine="vectorized",
        )
        progress_events: list[tuple[int, int]] = []
        full_parallel = run_coverage_scenario_range(
            scenario,
            checkpoint=4,
            bootstrap_replicates=20,
            scenario_seed=scenario_seed,
            workers=2,
            engine="vectorized",
            progress_callback=lambda completed, total: progress_events.append((completed, total)),
        )
        first = run_coverage_scenario_range(
            scenario,
            checkpoint=4,
            bootstrap_replicates=20,
            scenario_seed=scenario_seed,
            dataset_start=0,
            dataset_stop=2,
            workers=2,
            engine="vectorized",
        )
        second = run_coverage_scenario_range(
            scenario,
            checkpoint=4,
            bootstrap_replicates=20,
            scenario_seed=scenario_seed,
            dataset_start=2,
            dataset_stop=4,
            workers=1,
            engine="vectorized",
        )
        self.assertEqual(full_parallel, monolithic)
        self.assertEqual(first + second, monolithic)
        self.assertEqual(progress_events, [(1, 4), (2, 4), (3, 4), (4, 4)])

    def test_artifact_round_trip_and_aggregation_match_monolithic(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            contract_path, contract = self._write_contract(directory)
            artifact_dirs: list[Path] = []
            monolithic_results = []
            scenarios = scenarios_from_contract(contract)
            scenario_seeds = spawn_scenario_seed_sequences(int(contract["root_seed"]), 2)
            for scenario_index_zero, scenario in enumerate(scenarios):
                first_dir, _ = self._write_chunk(
                    directory,
                    contract_path=contract_path,
                    contract=contract,
                    scenario_index_zero=scenario_index_zero,
                    checkpoint=4,
                    start=0,
                    stop=2,
                    workers=2,
                )
                second_dir, _ = self._write_chunk(
                    directory,
                    contract_path=contract_path,
                    contract=contract,
                    scenario_index_zero=scenario_index_zero,
                    checkpoint=4,
                    start=2,
                    stop=4,
                    workers=1,
                )
                artifact_dirs.extend([first_dir, second_dir])
                monolithic = run_coverage_scenario_datasets(
                    scenario,
                    simulated_datasets=4,
                    bootstrap_replicates=20,
                    scenario_seed=scenario_seeds[scenario_index_zero],
                    workers=1,
                    engine="vectorized",
                )
                monolithic_results.extend(
                    aggregate_dataset_outcomes(
                        scenario,
                        monolithic,
                        bootstrap_replicates=20,
                    )
                )

            aggregated, decision = aggregate_checkpoint_artifacts(
                contract_path,
                artifact_dirs,
                expected_commit="fixture-commit",
                checkpoint=4,
                require_execution_authorized=False,
            )
            self.assertEqual(aggregated, monolithic_results)
            self.assertFalse(decision["historical_study_0_scores_read"])
            self.assertFalse(decision["production_coverage_gate_claimed"])

            manifest, outcomes = load_scenario_chunk_artifact(
                artifact_dirs[0],
                expected_commit="fixture-commit",
                expected_contract_sha256=contract_sha256(contract_path),
                expected_scenario="fixture_a",
                expected_checkpoint=4,
            )
            self.assertEqual(manifest["dataset_start"], 0)
            self.assertEqual([item.dataset_index for item in outcomes], [0, 1])

    def test_missing_duplicate_and_mixed_chunks_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            contract_path, contract = self._write_contract(directory)
            first_dir, _ = self._write_chunk(
                directory,
                contract_path=contract_path,
                contract=contract,
                scenario_index_zero=0,
                checkpoint=4,
                start=0,
                stop=2,
            )
            second_dir, _ = self._write_chunk(
                directory,
                contract_path=contract_path,
                contract=contract,
                scenario_index_zero=0,
                checkpoint=4,
                start=2,
                stop=4,
            )
            first = load_scenario_chunk_artifact(first_dir)
            second = load_scenario_chunk_artifact(second_dir)

            with self.assertRaisesRegex(ValueError, "complete checkpoint"):
                merge_scenario_chunks([first], checkpoint=4)
            with self.assertRaisesRegex(ValueError, "overlap|duplicated"):
                merge_scenario_chunks([first, first, second], checkpoint=4)

            wrong_commit_dir, _ = self._write_chunk(
                directory,
                contract_path=contract_path,
                contract=contract,
                scenario_index_zero=0,
                checkpoint=4,
                start=0,
                stop=2,
                git_commit="wrong-commit",
            )
            with self.assertRaisesRegex(ValueError, "commit"):
                load_scenario_chunk_artifact(
                    wrong_commit_dir,
                    expected_commit="fixture-commit",
                )
            with self.assertRaisesRegex(ValueError, "checkpoint"):
                load_scenario_chunk_artifact(first_dir, expected_checkpoint=8)
            with self.assertRaisesRegex(ValueError, "scenario"):
                load_scenario_chunk_artifact(first_dir, expected_scenario="fixture_b")
            with self.assertRaisesRegex(ValueError, "contract digest"):
                load_scenario_chunk_artifact(
                    first_dir,
                    expected_contract_sha256="0" * 64,
                )

    def test_digest_order_incomplete_and_degenerate_guards(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            directory = Path(directory_name)
            contract_path, contract = self._write_contract(directory)
            artifact_dir, _ = self._write_chunk(
                directory,
                contract_path=contract_path,
                contract=contract,
                scenario_index_zero=0,
                checkpoint=4,
                start=0,
                stop=2,
            )
            outcomes_path = artifact_dir / "dataset_outcomes.jsonl"
            original = outcomes_path.read_text(encoding="utf-8")
            outcomes_path.write_text(original + " ", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                load_scenario_chunk_artifact(artifact_dir)

            artifact_dir, _ = self._write_chunk(
                directory / "order",
                contract_path=contract_path,
                contract=contract,
                scenario_index_zero=0,
                checkpoint=4,
                start=0,
                stop=2,
            )
            outcomes_path = artifact_dir / "dataset_outcomes.jsonl"
            lines = outcomes_path.read_text(encoding="utf-8").splitlines()
            outcomes_path.write_text("\n".join(reversed(lines)) + "\n", encoding="utf-8")
            manifest_path = artifact_dir / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["dataset_outcomes_sha256"] = sha256_file(outcomes_path)
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            with self.assertRaisesRegex(ValueError, "order/range"):
                load_scenario_chunk_artifact(artifact_dir)

            artifact_dir, _ = self._write_chunk(
                directory / "incomplete",
                contract_path=contract_path,
                contract=contract,
                scenario_index_zero=0,
                checkpoint=4,
                start=0,
                stop=2,
            )
            manifest_path = artifact_dir / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["complete"] = False
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            with self.assertRaisesRegex(ValueError, "incomplete"):
                load_scenario_chunk_artifact(artifact_dir)

            scenarios = scenarios_from_contract(contract)
            scenario_seed = spawn_scenario_seed_sequences(int(contract["root_seed"]), 2)[0]
            plan = build_scenario_execution_plan(scenario_seed, 4)
            lineage = plan.datasets[0]
            degenerate = DatasetCoverageOutcome(
                dataset_index=0,
                representation_covered=False,
                operational_fnmr_covered=False,
                operational_fmr_covered=False,
                degenerate=True,
                representation_delta_sha256=None,
                operational_fnmr_sha256=None,
                operational_fmr_sha256=None,
                dataset_spawn_key=lineage.dataset.spawn_key,
                distances_spawn_key=lineage.distances.spawn_key,
                bootstrap_spawn_key=lineage.bootstrap.spawn_key,
            )
            normal_dir, normal_outcomes = self._write_chunk(
                directory / "degenerate",
                contract_path=contract_path,
                contract=contract,
                scenario_index_zero=0,
                checkpoint=4,
                start=0,
                stop=1,
            )
            self.assertEqual(normal_outcomes[0].dataset_index, 0)
            progress = normal_dir / "progress.jsonl"
            write_scenario_chunk_artifact(
                normal_dir,
                outcomes=[degenerate],
                progress_path=progress,
                execution_metadata={"complete": True, "historical_study_0_scores_read": False},
                repository="gharbonnier78/siamese-embedding-compression-lab",
                git_commit="fixture-commit",
                contract_path=contract_path,
                contract=contract,
                scenario_name=scenarios[0].name,
                scenario_index=1,
                scenario_count=2,
                checkpoint=4,
                dataset_start=0,
                dataset_stop=1,
                bootstrap_replicates=20,
                root_seed=int(contract["root_seed"]),
                scenario_seed=scenario_seed,
                workers=1,
                synthetic_nonproduction_fixture=True,
            )
            _, round_trip = load_scenario_chunk_artifact(normal_dir)
            self.assertEqual(round_trip, [degenerate])

    def test_cancelled_runtime_manifest_cannot_be_outcome_evidence(self) -> None:
        valid = {
            "conclusion": "cancelled",
            "runtime_observability_only": True,
            "outcome_evidence_seen": False,
            "historical_study_0_scores_read": False,
            "coverage_gate_result_admissible": False,
        }
        validate_cancelled_runtime_manifest(valid)
        for field, bad_value in (
            ("runtime_observability_only", False),
            ("outcome_evidence_seen", True),
            ("historical_study_0_scores_read", True),
            ("coverage_gate_result_admissible", True),
        ):
            with self.subTest(field=field):
                broken = dict(valid)
                broken[field] = bad_value
                with self.assertRaises(ValueError):
                    validate_cancelled_runtime_manifest(broken)


if __name__ == "__main__":
    unittest.main()
