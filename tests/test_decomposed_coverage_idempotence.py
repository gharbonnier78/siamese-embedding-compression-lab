from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import yaml

from siamese_compression_lab.coverage_execution import spawn_scenario_seed_sequences
from siamese_compression_lab.decomposed_coverage import (
    load_scenario_chunk_artifact,
    run_coverage_scenario_range,
    scenarios_from_contract,
    write_scenario_chunk_artifact,
)


class DecomposedCoverageIdempotenceTests(unittest.TestCase):
    def test_complete_chunk_rewrite_requires_exact_outcomes_and_identity(self) -> None:
        contract = {
            "schema_version": "1.0.1",
            "contract_id": "idempotence_fixture",
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
            "bootstrap": {"replicates_per_simulated_dataset": 8},
            "simulation_precision": {
                "dataset_checkpoints": [2],
                "stop_rule": "first_checkpoint_where_all_metric_mcse_lte_0_005",
                "maximum_monte_carlo_standard_error": 0.005,
            },
            "coverage_gate": {
                "binomial_interval": "clopper_pearson_exact_two_sided_95",
                "lower_bound_minimum": 0.93,
            },
            "graph": {
                "subjects": 20,
                "genuine_edges": 12,
                "impostor_edges": 12,
                "sparse_degree_exponent": 1.1,
            },
            "scenarios": [
                {
                    "name": "fixture",
                    "target_delta_fnmr": 0.0,
                    "subject_effect_sd_genuine": 0.04,
                    "subject_effect_sd_impostor": 0.03,
                    "candidate_reference_noise_correlation": 0.7,
                }
            ],
        }

        with tempfile.TemporaryDirectory() as directory_name:
            output_dir = Path(directory_name)
            contract_path = output_dir / "coverage.yaml"
            contract_path.write_text(
                yaml.safe_dump(contract, sort_keys=False),
                encoding="utf-8",
            )
            scenario = scenarios_from_contract(contract)[0]
            scenario_seed = spawn_scenario_seed_sequences(int(contract["root_seed"]), 1)[0]
            outcomes = run_coverage_scenario_range(
                scenario,
                checkpoint=2,
                bootstrap_replicates=8,
                scenario_seed=scenario_seed,
                workers=1,
                engine="vectorized",
            )
            progress_path = output_dir / "progress.jsonl"
            progress_path.write_text(
                json.dumps({"runtime_observability_only": True}) + "\n",
                encoding="utf-8",
            )

            common = {
                "progress_path": progress_path,
                "repository": "gharbonnier78/siamese-embedding-compression-lab",
                "git_commit": "fixture-commit",
                "contract_path": contract_path,
                "contract": contract,
                "scenario_name": scenario.name,
                "scenario_index": 1,
                "scenario_count": 1,
                "checkpoint": 2,
                "dataset_start": 0,
                "dataset_stop": 2,
                "bootstrap_replicates": 8,
                "root_seed": int(contract["root_seed"]),
                "scenario_seed": scenario_seed,
                "synthetic_nonproduction_fixture": True,
            }

            write_scenario_chunk_artifact(
                output_dir,
                outcomes=outcomes,
                execution_metadata={"complete": True, "workers": 1},
                workers=1,
                **common,
            )
            outcomes_path = output_dir / "dataset_outcomes.jsonl"
            manifest_path = output_dir / "manifest.json"
            original_outcome_bytes = outcomes_path.read_bytes()

            # Worker count is deliberately not part of scientific chunk identity.
            write_scenario_chunk_artifact(
                output_dir,
                outcomes=outcomes,
                execution_metadata={"complete": True, "workers": 2},
                workers=2,
                **common,
            )
            self.assertEqual(outcomes_path.read_bytes(), original_outcome_bytes)
            manifest, round_trip = load_scenario_chunk_artifact(output_dir)
            self.assertEqual(round_trip, outcomes)
            self.assertEqual(manifest["workers"], 2)
            manifest_before_divergence = manifest_path.read_bytes()

            divergent = list(outcomes)
            divergent[0] = replace(
                divergent[0],
                representation_covered=not divergent[0].representation_covered,
            )
            with self.assertRaisesRegex(ValueError, "outcomes diverge"):
                write_scenario_chunk_artifact(
                    output_dir,
                    outcomes=divergent,
                    execution_metadata={"complete": True, "workers": 2},
                    workers=2,
                    **common,
                )
            self.assertEqual(outcomes_path.read_bytes(), original_outcome_bytes)
            self.assertEqual(manifest_path.read_bytes(), manifest_before_divergence)

            changed_identity = dict(common)
            changed_identity["git_commit"] = "different-commit"
            with self.assertRaisesRegex(ValueError, "identity differs for git_commit"):
                write_scenario_chunk_artifact(
                    output_dir,
                    outcomes=outcomes,
                    execution_metadata={"complete": True, "workers": 2},
                    workers=2,
                    **changed_identity,
                )


if __name__ == "__main__":
    unittest.main()
