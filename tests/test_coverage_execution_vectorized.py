from __future__ import annotations

import unittest

from siamese_compression_lab.coverage_execution import (
    run_coverage_scenario_datasets,
    spawn_scenario_seed_sequences,
)
from siamese_compression_lab.coverage_execution_vectorized import (
    run_coverage_scenario_datasets_vectorized,
)
from siamese_compression_lab.coverage_simulation import CoverageScenario


class VectorizedParallelCoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = CoverageScenario(
            name="vectorized_parallel_fixture",
            target_delta_fnmr=0.015,
            n_subjects=30,
            n_genuine=20,
            n_impostor=20,
            target_fmr=0.10,
            subject_effect_sd_genuine=0.04,
            subject_effect_sd_impostor=0.03,
        )
        self.scenario_seed = spawn_scenario_seed_sequences(20260808, 1)[0]

    def test_vectorized_serial_matches_reviewed_legacy_exactly(self) -> None:
        legacy = run_coverage_scenario_datasets(
            self.scenario,
            simulated_datasets=3,
            bootstrap_replicates=25,
            scenario_seed=self.scenario_seed,
            workers=1,
        )
        vectorized = run_coverage_scenario_datasets_vectorized(
            self.scenario,
            simulated_datasets=3,
            bootstrap_replicates=25,
            scenario_seed=self.scenario_seed,
            workers=1,
        )
        self.assertEqual(vectorized, legacy)

    def test_vectorized_worker_count_preserves_exact_outputs(self) -> None:
        serial = run_coverage_scenario_datasets_vectorized(
            self.scenario,
            simulated_datasets=4,
            bootstrap_replicates=25,
            scenario_seed=self.scenario_seed,
            workers=1,
        )
        parallel = run_coverage_scenario_datasets_vectorized(
            self.scenario,
            simulated_datasets=4,
            bootstrap_replicates=25,
            scenario_seed=self.scenario_seed,
            workers=2,
        )
        self.assertEqual(parallel, serial)


if __name__ == "__main__":
    unittest.main()
