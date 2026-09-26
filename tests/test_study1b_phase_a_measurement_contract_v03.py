from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = (
    ROOT
    / "protocol/benchmarks/"
    "STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml"
)


class Study1BPhaseAMeasurementContractV03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.b = yaml.safe_load(BENCHMARK.read_text(encoding="utf-8"))

    def test_protected_boundaries_remain_closed(self) -> None:
        boundary = self.b["scientific_boundary"]
        self.assertFalse(boundary["protected_biometric_inputs_required"])
        self.assertFalse(boundary["real_study_outcomes_opened"])
        self.assertFalse(boundary["screen_opened"])
        self.assertFalse(boundary["qualification_test_opened"])
        self.assertFalse(boundary["real_route_performance_opened"])
        self.assertFalse(boundary["representation_geometry_opened"])
        self.assertFalse(boundary["amendment_activated"])
        self.assertFalse(boundary["s4n3_launched"])

    def test_phase_a_is_exact_dense_fixed_work(self) -> None:
        search = self.b["phase_a_search_semantics"]
        self.assertEqual(search["algorithm"], "EXACT_DENSE_DOT_PRODUCT_TOP1")
        self.assertEqual(search["top_k"], 1)
        self.assertFalse(search["threshold_gating"])
        self.assertEqual(search["threshold_lookup"], "none")
        self.assertEqual(search["candidate_pruning"], "none")
        self.assertFalse(search["approximate_search"])
        self.assertEqual(search["index"], "none")

    def test_phase_a_pairing_changes_dimension_only(self) -> None:
        pairing = self.b["reference_and_candidate"]
        self.assertEqual(pairing["representation_reference"]["dimension"], 512)
        self.assertEqual(pairing["compression_candidate"]["dimension"], 128)
        rule = pairing["phase_a_pairing_rule"]
        self.assertIn("Change representation dimension only", rule)
        self.assertIn("MUST be identical", rule)

    def test_g0_and_g2_payloads_recompute_from_cardinality(self) -> None:
        galleries = self.b["scenario_galleries"]
        g0 = galleries["G0_blacklist_control"]
        g2 = galleries["G2_central_full"]

        g0_vectors = g0["blacklist_identities"] * g0["templates_per_identity"]
        g2_vectors = (
            (g2["whitelist_identities"] + g2["blacklist_identities"])
            * g2["templates_per_identity"]
        )

        self.assertEqual(g0_vectors * 512 * 4, 61_440_000)
        self.assertEqual(g0_vectors * 128 * 4, 15_360_000)
        self.assertEqual(g2_vectors * 512 * 4, 3_133_440_000)
        self.assertEqual(g2_vectors * 128 * 4, 783_360_000)

        ram = self.b["ram_residency_contract"]
        self.assertEqual(ram["g2_512d_fp32_payload_bytes"], 3_133_440_000)
        self.assertEqual(ram["g2_128d_fp32_payload_bytes"], 783_360_000)

    def test_ram_infeasibility_rule_fails_closed_without_substitution(self) -> None:
        ram = self.b["ram_residency_contract"]
        self.assertTrue(ram["gallery_must_be_ram_resident"])
        self.assertEqual(ram["swap_policy"], "DISABLED_OR_PROVEN_ZERO_ACTIVITY")
        rule = ram["infeasible_arm_rule"]
        self.assertIn("RAM_INFEASIBLE_ON_TIER", rule)
        self.assertIn("Do not substitute a smaller gallery", rule)
        self.assertIn("If a larger tier was prospectively declared", rule)
        self.assertIn("BOTH arms may be repeated there", rule)

    def test_load_generation_contract_is_open_loop_and_off_device(self) -> None:
        load = self.b["load_generation"]
        self.assertEqual(load["canonical_placement"], "OFF_DEVICE")
        self.assertEqual(load["arrival_process"], "DETERMINISTIC_OPEN_LOOP_FIXED_RATE")
        self.assertEqual(load["steady_qps_per_device"], [0.25, 0.5, 1.0, 2.0, 4.0, 8.0])
        self.assertEqual(load["burst"]["qps"], 16.0)
        self.assertEqual(load["burst"]["duration_seconds"], 30)
        self.assertEqual(load["burst"]["recovery_observation_seconds"], 600)

    def test_measurement_statistics_are_frozen(self) -> None:
        stats = self.b["measurement_statistics"]
        self.assertEqual(stats["independent_process_restarts_per_configuration"], 5)
        self.assertEqual(stats["warmup_seconds_per_restart"], 60)
        self.assertTrue(stats["warmup_samples_excluded"])
        self.assertEqual(stats["steady_measurement_seconds_per_restart"], 600)
        self.assertEqual(stats["execution_order"]["arm_order"], "COUNTERBALANCED_ACROSS_RESTARTS")
        support = stats["percentile_support_rules"]
        self.assertEqual(support["p95_min_completed_samples_per_restart"], 200)
        self.assertEqual(support["p99_min_completed_samples_per_restart"], 1000)
        self.assertEqual(support["insufficient_support_status"], "INSUFFICIENT_SAMPLES_NO_PERCENTILE_CLAIM")

    def test_energy_measurement_requires_external_plane(self) -> None:
        energy = self.b["energy_measurement"]
        self.assertEqual(energy["canonical_measurement_plane"], "EXTERNAL_DEVICE_INPUT_OR_WALL")
        self.assertTrue(energy["external_meter_required_for_strong_energy_claim"])
        self.assertEqual(energy["minimum_external_sampling_rate_hz"], 10)
        self.assertEqual(energy["on_chip_telemetry_role"], "SUPPORTING_DIAGNOSTIC_ONLY")
        self.assertEqual(energy["idle_baseline"]["duration_seconds"], 300)
        self.assertTrue(
            energy["idle_baseline"]["measured_immediately_before_or_after_each_configuration_block"]
        )
        self.assertIn("MUST NOT be reported", energy["guard"])

    def test_rule_nine_prevents_biometric_outcome_contamination(self) -> None:
        rules = self.b["interpretation_rules"]
        self.assertIn(
            "No protected Study 1B outcome may be opened to select or tune an engineering configuration.",
            rules,
        )
        self.assertIn(
            "No target-workload preview, whatever its label, may silently determine the canonical lock configuration.",
            rules,
        )


if __name__ == "__main__":
    unittest.main()
