from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from siamese_compression_lab.coverage_execution import (
    aggregate_dataset_outcomes,
    build_scenario_execution_plan,
    run_coverage_dataset,
    run_coverage_scenario_datasets,
    seed_descriptor_to_int,
    spawn_scenario_seed_sequences,
)
from siamese_compression_lab.coverage_simulation import make_sparse_graph
from siamese_compression_lab.decomposed_coverage import (
    run_coverage_scenario_range,
    scenarios_from_contract,
)

CONTRACT_PATH = Path("protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml")


class DecomposedCoverageIntegrationTests(unittest.TestCase):
    def _contract(self) -> dict:
        value = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.assertIsInstance(value, dict)
        return value

    def test_all_five_frozen_scenarios_match_monolithic_and_isolated_replay(self) -> None:
        contract = self._contract()
        scenarios = scenarios_from_contract(contract)
        self.assertEqual(
            [scenario.name for scenario in scenarios],
            [
                "independent_pair_null",
                "subject_dependence_null",
                "subject_dependence_noninferior",
                "subject_dependence_boundary",
                "subject_dependence_inferior",
            ],
        )
        seeds = spawn_scenario_seed_sequences(int(contract["root_seed"]), len(scenarios))

        for scenario, scenario_seed in zip(scenarios, seeds, strict=True):
            with self.subTest(scenario=scenario.name):
                monolithic = run_coverage_scenario_datasets(
                    scenario,
                    simulated_datasets=2,
                    bootstrap_replicates=10,
                    scenario_seed=scenario_seed,
                    workers=1,
                    engine="vectorized",
                )
                decomposed_parallel = run_coverage_scenario_range(
                    scenario,
                    checkpoint=2,
                    bootstrap_replicates=10,
                    scenario_seed=scenario_seed,
                    dataset_start=0,
                    dataset_stop=2,
                    workers=2,
                    engine="vectorized",
                )
                self.assertEqual(decomposed_parallel, monolithic)
                self.assertEqual(
                    aggregate_dataset_outcomes(
                        scenario,
                        decomposed_parallel,
                        bootstrap_replicates=10,
                    ),
                    aggregate_dataset_outcomes(
                        scenario,
                        monolithic,
                        bootstrap_replicates=10,
                    ),
                )

                plan = build_scenario_execution_plan(scenario_seed, 2)
                graph = make_sparse_graph(
                    scenario,
                    seed=seed_descriptor_to_int(plan.graph),
                )
                isolated = run_coverage_dataset(
                    scenario,
                    graph,
                    plan.datasets[1],
                    10,
                    engine="vectorized",
                )
                self.assertEqual(isolated, monolithic[1])

    def test_higher_checkpoint_seed_plan_has_exact_lower_checkpoint_prefix(self) -> None:
        contract = self._contract()
        scenario_count = len(contract["scenarios"])
        scenario_seed = spawn_scenario_seed_sequences(
            int(contract["root_seed"]), scenario_count
        )[0]
        lower = build_scenario_execution_plan(scenario_seed, 2)
        higher = build_scenario_execution_plan(scenario_seed, 4)
        self.assertEqual(lower.graph, higher.graph)
        self.assertEqual(lower.datasets, higher.datasets[:2])

    def test_multiprocess_scenario_runner_progress_is_runtime_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory_name:
            output_dir = Path(directory_name) / "scenario"
            env = dict(os.environ)
            env["PYTHONPATH"] = "src"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_subject_bootstrap_coverage_scenario.py",
                    "--scenario",
                    "independent_pair_null",
                    "--checkpoint",
                    "2",
                    "--workers",
                    "2",
                    "--git-commit",
                    "integration-fixture",
                    "--output-dir",
                    str(output_dir),
                    "--smoke",
                ],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(completed.returncode, 0, msg=completed.stderr)
            progress_path = output_dir / "progress.jsonl"
            manifest_path = output_dir / "manifest.json"
            self.assertTrue(progress_path.exists())
            self.assertTrue(manifest_path.exists())

            events = [
                json.loads(line)
                for line in progress_path.read_text(encoding="utf-8").splitlines()
                if line
            ]
            self.assertEqual(events[0]["event"], "scenario_chunk_started")
            self.assertEqual(events[-1]["event"], "scenario_chunk_complete")
            self.assertTrue(any(event["event"] == "dataset_progress" for event in events))
            forbidden_keys = {
                "covered",
                "coverage",
                "coverage_gate",
                "empirical_coverage",
                "lower_95_binomial_bound",
                "monte_carlo_standard_error",
                "gate_status",
            }
            for event in events:
                self.assertTrue(event["runtime_observability_only"])
                self.assertTrue(forbidden_keys.isdisjoint(event))

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertTrue(manifest["complete"])
            self.assertEqual(manifest["workers"], 2)
            self.assertFalse(manifest["historical_study_0_scores_read"])
            self.assertFalse(manifest["production_gate_claimed"])

    def test_current_governance_preflight_authorizes_without_executing_outcomes(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = "src"
        completed = subprocess.run(
            [sys.executable, "scripts/preflight_decomposed_coverage.py"],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "EXECUTION_PREFLIGHT_PASS")
        self.assertEqual(payload["checkpoints"], [2000, 4000, 10000])
        self.assertFalse(payload["historical_study_0_scores_read"])
        self.assertFalse(payload["outcome_evidence_seen"])
        self.assertFalse(payload["production_coverage_gate_executed"])


if __name__ == "__main__":
    unittest.main()
