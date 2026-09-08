from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_2_2026-09-08.yaml"
ENV_LOCK = ROOT / "protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_1_2026-09-08.yaml"
CLARIFICATION = ROOT / "protocol/decisions/STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml"


class Study1BEngineeringBenchmarkContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.benchmark = yaml.safe_load(BENCHMARK.read_text(encoding="utf-8"))
        cls.environment = yaml.safe_load(ENV_LOCK.read_text(encoding="utf-8"))
        cls.clarification = yaml.safe_load(CLARIFICATION.read_text(encoding="utf-8"))

    def test_protected_biometric_boundary_stays_closed(self) -> None:
        boundary = self.benchmark["scientific_boundary"]
        self.assertFalse(boundary["protected_biometric_inputs_required"])
        self.assertFalse(boundary["screen_opened"])
        self.assertFalse(boundary["qualification_test_opened"])
        self.assertFalse(boundary["real_route_performance_opened"])
        self.assertFalse(boundary["representation_geometry_opened"])
        self.assertFalse(boundary["amendment_activated"])
        self.assertFalse(boundary["s4n3_launched"])

    def test_phase_a_is_fixed_work_exact_top1_without_threshold(self) -> None:
        search = self.benchmark["phase_a_search_semantics"]
        self.assertEqual(search["algorithm"], "EXACT_DENSE_DOT_PRODUCT_TOP1")
        self.assertEqual(search["top_k"], 1)
        self.assertFalse(search["threshold_gating"])
        self.assertFalse(search["approximate_search"])
        self.assertEqual(search["index"], "none")

    def test_g0_and_g2_are_explicit_scenarios(self) -> None:
        galleries = self.benchmark["scenario_galleries"]
        for key in ("G0_blacklist_control", "G2_central_full"):
            self.assertEqual(galleries[key]["provenance"], "SCENARIO_ONLY_NOT_EVENT_FACT")
        self.assertEqual(
            self.benchmark["phase_a_scope"]["galleries"],
            ["G0_blacklist_control", "G2_central_full"],
        )

    def test_ram_infeasibility_is_a_result_not_runtime_tuning(self) -> None:
        ram = self.benchmark["ram_residency_contract"]
        self.assertTrue(ram["gallery_must_be_ram_resident"])
        rule = ram["infeasible_arm_rule"]
        self.assertIn("RAM_INFEASIBLE_ON_TIER", rule)
        self.assertIn("Do not substitute a smaller gallery", rule)
        self.assertIn("BOTH arms", rule)

    def test_energy_claim_uses_external_device_measurement(self) -> None:
        energy = self.benchmark["energy_measurement"]
        self.assertTrue(energy["external_meter_required_for_strong_energy_claim"])
        self.assertEqual(energy["on_chip_telemetry_role"], "SUPPORTING_DIAGNOSTIC_ONLY")
        self.assertTrue(energy["canonical_joules_per_identification"]["includes_idle_baseline_consumption"])

    def test_thresholds_cannot_be_set_retroactively(self) -> None:
        thresholds = self.benchmark["operational_thresholds"]
        self.assertEqual(thresholds["threshold_mode_if_null"], "CHARACTERIZATION_ONLY_NO_PASS_FAIL")
        self.assertIn("MUST NOT be chosen after inspecting Phase A results", thresholds["prospective_binding_rule"])

    def test_measurement_statistics_and_load_generator_are_frozen(self) -> None:
        stats = self.benchmark["measurement_statistics"]
        self.assertEqual(stats["independent_process_restarts_per_configuration"], 5)
        self.assertEqual(stats["warmup_seconds_per_restart"], 60)
        self.assertEqual(stats["steady_measurement_seconds_per_restart"], 600)
        self.assertEqual(stats["percentile_support_rules"]["p99_min_completed_samples_per_restart"], 1000)
        self.assertEqual(self.benchmark["load_generation"]["canonical_placement"], "OFF_DEVICE")

    def test_canonical_execution_remains_blocked_until_environment_is_bound(self) -> None:
        gates = self.benchmark["current_execution_gates"]
        self.assertEqual(gates["canonical_phase_a_execution"], "BLOCKED")
        self.assertTrue(
            self.benchmark["reproducibility_and_environment"]["environment_must_be_materialized_before_canonical_execution"]
        )
        self.assertEqual(self.environment["status"], "BLOCKED_PENDING_PLATFORM_BINDING")
        self.assertTrue(
            self.environment["binding_rule"]["canonical_execution_permitted_only_if_all_required_values_non_null"]
        )

    def test_s4_clarification_records_shared_population_and_t19(self) -> None:
        shared = self.clarification["shared_synthetic_population"]
        self.assertEqual(shared["independent_lines_of_evidence_count"], 1)
        self.assertEqual(shared["uncertainty_procedures_compared"], 2)
        multiplier = self.clarification["s4n2_confidence_multiplier"]
        self.assertEqual(multiplier["degrees_of_freedom"], 19)
        self.assertAlmostEqual(multiplier["critical_value_t_0_975_df19"], 2.0930240544083087)


if __name__ == "__main__":
    unittest.main()
