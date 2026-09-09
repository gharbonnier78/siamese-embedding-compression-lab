from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml"
ADDENDUM = ROOT / "protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_2026-09-08.yaml"
ENV_LOCK = ROOT / "protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_4_2026-09-09.yaml"
CLARIFICATION = ROOT / "protocol/decisions/STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml"


class Study1BEngineeringBenchmarkContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.benchmark = yaml.safe_load(BENCHMARK.read_text(encoding="utf-8"))
        cls.addendum = yaml.safe_load(ADDENDUM.read_text(encoding="utf-8"))
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

    def test_d1_provenance_has_accountable_attester(self) -> None:
        provenance = self.environment["configuration_choice_provenance"]
        required = set(provenance["required_fields_per_choice"])
        self.assertIn("provenance_attested_by", required)
        self.assertIn("attestation_timestamp", required)
        self.assertIn("attestation_statement", required)
        attestation = provenance["attestation_requirements"]
        self.assertTrue(attestation["provenance_attested_by_must_identify_human_or_accountable_role"])
        self.assertFalse(attestation["system_only_attester_permitted"])

    def test_d2_measurement_evidence_timestamp_and_earliest_workload_anchor(self) -> None:
        measurement = self.environment["measurement_source_requirements"]
        self.assertTrue(measurement["evidence_timestamp_required"])
        anchor = self.environment["structural_impossibility_anchor"]
        self.assertEqual(
            anchor["earliest_workload_defining_commit_sha"],
            "878bfe2a64b34cce474a627d04b30233e2356958",
        )
        self.assertEqual(
            anchor["earliest_workload_defining_commit_timestamp_utc"],
            "2026-09-07T06:33:05Z",
        )
        self.assertTrue(
            anchor["evidence_timestamp_must_be_strictly_earlier_than_anchor_for_structural_impossibility"]
        )
        self.assertTrue(anchor["structural_impossibility_claim_available_for_qualifying_pre_anchor_evidence"])
        replay = self.environment["target_workload_replay_identity"]
        self.assertEqual(replay["synthetic_root_seed"], 20260908)
        self.assertTrue(replay["generator_code_identity_required_before_execution"])
        self.assertEqual(
            replay["generator_identity_role"],
            "REPLAY_AND_RESULT_PROVENANCE_NOT_STRUCTURAL_IMPOSSIBILITY_BOUND",
        )
        self.assertIsNone(replay["synthetic_generator_code_commit_timestamp_utc"])

    def test_d3_firewall_is_information_based_not_intent_based(self) -> None:
        measurement = self.environment["measurement_source_requirements"]
        overlap = measurement["informational_overlap_rule"]
        self.assertEqual(overlap["target_vector_dimensions"], [128, 512])
        self.assertEqual(overlap["target_search_family"], "EXACT_DENSE_DOT_PRODUCT_TOP1")
        self.assertEqual(overlap["target_index_mode"], "none")
        self.assertFalse(overlap["intended_purpose_is_a_classifier_input"])
        self.assertFalse(overlap["label_is_a_classifier_input"])
        self.assertEqual(overlap["hardware_class_source"], "required_environment.device_under_test.hardware_class")
        firewall = self.environment["prelock_information_firewall"]
        self.assertTrue(firewall["label_independent"])
        self.assertTrue(firewall["intent_independent"])
        self.assertIn("vector dimensionality", firewall["rule"])
        self.assertIn("hardware class", firewall["rule"])

    def test_benchmark_addendum_supersedes_intent_based_prelock_semantics(self) -> None:
        self.assertEqual(
            self.addendum["prelock_selection_guard_v2"]["classification_basis"],
            "INFORMATIONAL_OVERLAP_NOT_INTENT",
        )
        guard = self.addendum["prelock_selection_guard_v2"]
        self.assertFalse(guard["intent_is_classifier_input"])
        self.assertFalse(guard["label_is_classifier_input"])
        self.assertIn("smoke_test", guard["labels_with_no_exemption"])
        self.assertIn("phase_0", guard["labels_with_no_exemption"])

    def test_execution_has_two_independent_blockers(self) -> None:
        admissibility = self.environment["execution_admissibility"]
        self.assertFalse(admissibility["canonical_phase_a_execution_permitted"])
        blockers = set(admissibility["independent_blockers"])
        self.assertEqual(
            blockers,
            {
                "PLATFORM_AND_MEASUREMENT_ENVIRONMENT_NOT_MATERIALIZED",
                "CONFIGURATION_CHOICE_PROVENANCE_NOT_MATERIALIZED",
            },
        )

    def test_new_local_artifact_schemas_use_family_id_and_integer_version(self) -> None:
        self.assertEqual(self.environment["schema_id"], "study1b.engineering.environment_lock")
        self.assertIsInstance(self.environment["schema_version"], int)
        self.assertEqual(self.addendum["schema_id"], "study1b.engineering.benchmark_addendum")
        self.assertIsInstance(self.addendum["schema_version"], int)

    def test_s4_clarification_records_shared_population_and_t19(self) -> None:
        shared = self.clarification["shared_synthetic_population"]
        self.assertEqual(shared["independent_lines_of_evidence_count"], 1)
        self.assertEqual(shared["uncertainty_procedures_compared"], 2)
        multiplier = self.clarification["s4n2_confidence_multiplier"]
        self.assertEqual(multiplier["degrees_of_freedom"], 19)
        self.assertAlmostEqual(multiplier["critical_value_t_0_975_df19"], 2.0930240544083087)


if __name__ == "__main__":
    unittest.main()
