from __future__ import annotations

import unittest

from siamese_compression_lab.coverage_execution import (
    build_scenario_execution_plan,
    run_coverage_dataset,
    run_coverage_scenario_datasets,
    seed_descriptor_to_int,
    spawn_scenario_seed_sequences,
)
from siamese_compression_lab.coverage_simulation import CoverageScenario, make_sparse_graph


class CoverageExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = CoverageScenario(
            name="execution_fixture",
            target_delta_fnmr=0.015,
            n_subjects=30,
            n_genuine=20,
            n_impostor=20,
            target_fmr=0.10,
            subject_effect_sd_genuine=0.04,
            subject_effect_sd_impostor=0.03,
        )

    def test_seedsequence_spawn_hierarchy_is_explicit_and_distinct(self) -> None:
        scenario_seeds = spawn_scenario_seed_sequences(20260807, 3)
        self.assertEqual(
            [seed.spawn_key for seed in scenario_seeds],
            [(0,), (1,), (2,)],
        )
        plan = build_scenario_execution_plan(scenario_seeds[1], 3)
        self.assertEqual(plan.graph.spawn_key, (1, 0))
        self.assertEqual(
            [lineage.dataset.spawn_key for lineage in plan.datasets],
            [(1, 1), (1, 2), (1, 3)],
        )
        self.assertEqual(plan.datasets[1].distances.spawn_key, (1, 2, 0))
        self.assertEqual(plan.datasets[1].bootstrap.spawn_key, (1, 2, 1))
        self.assertNotEqual(
            seed_descriptor_to_int(plan.datasets[1].distances),
            seed_descriptor_to_int(plan.datasets[1].bootstrap),
        )

    def test_worker_count_does_not_change_dataset_outputs(self) -> None:
        scenario_seed = spawn_scenario_seed_sequences(91, 1)[0]
        serial = run_coverage_scenario_datasets(
            self.scenario,
            simulated_datasets=3,
            bootstrap_replicates=20,
            scenario_seed=scenario_seed,
            workers=1,
        )
        parallel = run_coverage_scenario_datasets(
            self.scenario,
            simulated_datasets=3,
            bootstrap_replicates=20,
            scenario_seed=scenario_seed,
            workers=2,
        )
        self.assertEqual(serial, parallel)

    def test_isolated_dataset_replay_matches_parallel_bitwise_digests(self) -> None:
        scenario_seed = spawn_scenario_seed_sequences(12345, 1)[0]
        plan = build_scenario_execution_plan(scenario_seed, 3)
        graph = make_sparse_graph(
            self.scenario,
            seed=seed_descriptor_to_int(plan.graph),
        )
        isolated = run_coverage_dataset(
            self.scenario,
            graph,
            plan.datasets[1],
            bootstrap_replicates=25,
        )
        parallel = run_coverage_scenario_datasets(
            self.scenario,
            simulated_datasets=3,
            bootstrap_replicates=25,
            scenario_seed=scenario_seed,
            workers=2,
        )
        self.assertEqual(isolated, parallel[1])
        self.assertIsNotNone(isolated.representation_delta_sha256)
        self.assertIsNotNone(isolated.operational_fnmr_sha256)
        self.assertIsNotNone(isolated.operational_fmr_sha256)


if __name__ == "__main__":
    unittest.main()
