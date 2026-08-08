from __future__ import annotations

import unittest

from siamese_compression_lab.coverage_execution import (
    run_coverage_scenario_datasets,
    spawn_scenario_seed_sequences,
)
from siamese_compression_lab.coverage_simulation import CoverageScenario


class VectorizedCoverageExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = CoverageScenario(
            name="vectorized_execution_fixture",
            target_delta_fnmr=0.015,
            n_subjects=30,
            n_genuine=20,
            n_impostor=20,
            target_fmr=0.10,
            subject_effect_sd_genuine=0.04,
            subject_effect_sd_impostor=0.03,
        )
        self.scenario_seed = spawn_scenario_seed_sequences(20260807, 1)[0]

    def test_vectorized_dataset_outcomes_match_legacy_exactly(self) -> None:
        legacy = run_coverage_scenario_datasets(
            self.scenario,
            simulated_datasets=3,
            bootstrap_replicates=50,
            scenario_seed=self.scenario_seed,
            workers=1,
            engine="legacy",
        )
        vectorized = run_coverage_scenario_datasets(
            self.scenario,
            simulated_datasets=3,
            bootstrap_replicates=50,
            scenario_seed=self.scenario_seed,
            workers=1,
            engine="vectorized",
        )
        self.assertEqual(vectorized, legacy)

    def test_vectorized_worker_count_preserves_exact_dataset_outcomes(self) -> None:
        serial = run_coverage_scenario_datasets(
            self.scenario,
            simulated_datasets=4,
            bootstrap_replicates=40,
            scenario_seed=self.scenario_seed,
            workers=1,
            engine="vectorized",
        )
        parallel = run_coverage_scenario_datasets(
            self.scenario,
            simulated_datasets=4,
            bootstrap_replicates=40,
            scenario_seed=self.scenario_seed,
            workers=2,
            engine="vectorized",
        )
        self.assertEqual(parallel, serial)

    def test_legacy_remains_default_engine(self) -> None:
        implicit = run_coverage_scenario_datasets(
            self.scenario,
            simulated_datasets=2,
            bootstrap_replicates=30,
            scenario_seed=self.scenario_seed,
            workers=1,
        )
        explicit = run_coverage_scenario_datasets(
            self.scenario,
            simulated_datasets=2,
            bootstrap_replicates=30,
            scenario_seed=self.scenario_seed,
            workers=1,
            engine="legacy",
        )
        self.assertEqual(implicit, explicit)

    def test_unknown_engine_is_rejected_before_execution(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown coverage engine"):
            run_coverage_scenario_datasets(
                self.scenario,
                simulated_datasets=1,
                bootstrap_replicates=10,
                scenario_seed=self.scenario_seed,
                workers=1,
                engine="unknown",  # type: ignore[arg-type]
            )


if __name__ == "__main__":
    unittest.main()
