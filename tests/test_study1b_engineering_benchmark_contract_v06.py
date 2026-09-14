from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ADDENDUM = ROOT / "protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_V0_2_2026-09-14.yaml"
LOCK = ROOT / "protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml"


class Study1BPreexecutionSemanticHardeningV06Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.addendum = yaml.safe_load(ADDENDUM.read_text(encoding="utf-8"))
        cls.lock = yaml.safe_load(LOCK.read_text(encoding="utf-8"))

    def test_protected_boundaries_remain_closed(self) -> None:
        b = self.lock["scientific_boundary"]
        self.assertFalse(b["protected_biometric_inputs_required"])
        self.assertFalse(b["screen_opened"])
        self.assertFalse(b["qualification_test_opened"])
        self.assertFalse(b["real_route_performance_opened"])
        self.assertFalse(b["representation_geometry_opened"])
        self.assertFalse(b["amendment_activated"])
        self.assertFalse(b["s4n3_launched"])

    def test_n4_mere_possession_does_not_equal_creation_influence(self) -> None:
        split = self.lock["negative_fact_responsibility_split"]
        d2 = split["D2_public_ordering"]
        d1 = split["D1_accountable_attestation"]
        self.assertTrue(d2["mere_receipt_possession_citation_or_review_is_not_creation_influence"])
        self.assertTrue(d2["may_remain_applicable_after_attester_receives_or_reviews_preexisting_external_evidence"])
        self.assertTrue(d2["cannot_substitute_for_D1_attestation"])
        self.assertIn("produced_by_attesting_party", d1["required_for_evidence_that_was"])
        self.assertIn("commissioned_by_attesting_party", d1["required_for_evidence_that_was"])
        self.assertIn("materially_framed_by_attesting_party", d1["required_for_evidence_that_was"])
        self.assertTrue(d1["completeness_backstop_applies_to_all_lock_defining_choices"])
        self.assertIn("require D1", split["conflict_rule"])

    def test_n5_only_temporal_ordering_is_mechanically_checkable(self) -> None:
        d2 = self.lock["negative_fact_responsibility_split"]["D2_public_ordering"]
        self.assertIn("strictly earlier", d2["mechanically_checkable_component"])
        self.assertIn("source_is_genuinely_external_or_preexisting", d2["provenance_backed_conditions"])
        self.assertIn("attesting_party_did_not_influence_creation_or_framing", d2["provenance_backed_conditions"])
        anchor = self.lock["public_ordering_anchor"]
        self.assertEqual(anchor["repository_root_commit_sha"], "4b40e7254bff1b88a44d13fb55b366bc7d3fc263")
        self.assertEqual(anchor["repository_root_commit_timestamp_utc"], "2026-08-07T08:23:56Z")
        self.assertIn("Only the temporal ordering", anchor["label_scope_note"])
        self.assertIn("MUST NOT cite", anchor["label_scope_note"])

    def test_r1_n2_classifier_is_choice_specific(self) -> None:
        firewall = self.lock["measurement_source_requirements"]["choice_specific_information_firewall"]
        self.assertEqual(firewall["classification_basis"], "CHOICE_SPECIFIC_INFORMATIONAL_OVERLAP")
        self.assertFalse(firewall["intent_is_classifier_input"])
        self.assertFalse(firewall["label_is_classifier_input"])
        self.assertTrue(firewall["uncertainty_defaults_to_informative"])
        self.assertTrue(firewall["not_informative_requires_attributable_rationale"])

    def test_cross_hardware_backend_evidence_can_be_informative(self) -> None:
        fam = self.lock["measurement_source_requirements"]["choice_specific_information_firewall"]["search_runtime_portable"]
        self.assertIn("search_backend_and_blas_runtime", fam["choices"])
        self.assertFalse(fam["hardware_class_required"])
        self.assertIn("Hardware mismatch alone cannot discharge", fam["rule"])

    def test_cross_hardware_threading_evidence_can_be_informative(self) -> None:
        fam = self.lock["measurement_source_requirements"]["choice_specific_information_firewall"]["concurrency_portable"]
        self.assertIn("benchmark_thread_count_and_affinity", fam["choices"])
        self.assertFalse(fam["hardware_class_required"])
        self.assertIn("across hardware", fam["rule"])

    def test_measurement_method_can_transfer_across_compute_classes(self) -> None:
        fam = self.lock["measurement_source_requirements"]["choice_specific_information_firewall"]["measurement_method_portable"]
        self.assertFalse(fam["hardware_class_required"])
        self.assertFalse(fam["vector_dimension_required"])
        self.assertFalse(fam["search_family_required"])
        self.assertIn("external_power_meter_and_measurement_plane", fam["choices"])
        self.assertIn("load_generator_host_and_link", fam["choices"])

    def test_addendum_and_lock_agree_on_choice_specific_semantics(self) -> None:
        a = self.addendum["information_firewall_v3"]
        self.assertEqual(a["classification_basis"], "CHOICE_SPECIFIC_INFORMATIONAL_OVERLAP_NOT_GLOBAL_HARDWARE_CONJUNCTION")
        self.assertTrue(a["fail_closed_rule"].startswith("If applicability"))
        self.assertFalse(a["choice_families"]["search_runtime_portable"]["hardware_class_required"])
        self.assertFalse(a["choice_families"]["concurrency_portable"]["hardware_class_required"])
        self.assertFalse(a["choice_families"]["measurement_method_portable"]["hardware_class_required"])

    def test_n6_package_rule_is_recorded(self) -> None:
        state = self.lock["preexecution_review_state"]["n6_review_transport"]
        self.assertEqual(state["status"], "PROCESS_RULE_ADOPTED_FOR_NEXT_PACKAGE")
        self.assertIn("expected Git blob SHA-1", state["rule"])
        self.assertIn("SHA1('blob '", state["rule"])

    def test_execution_remains_blocked_and_construct_validity_unreviewed(self) -> None:
        review = self.lock["preexecution_review_state"]
        self.assertEqual(review["construct_validity"]["status"], "NOT_REVIEWED")
        adm = self.lock["execution_admissibility"]
        self.assertFalse(adm["preexecution_semantic_hardening_independent_review_accepted"])
        self.assertFalse(adm["canonical_phase_a_execution_permitted"])
        self.assertEqual(
            set(adm["independent_blockers"]),
            {
                "PLATFORM_AND_MEASUREMENT_ENVIRONMENT_NOT_MATERIALIZED",
                "CONFIGURATION_CHOICE_PROVENANCE_NOT_MATERIALIZED",
            },
        )

    def test_v06_self_references_are_current(self) -> None:
        code = self.lock["required_environment"]["code_identity"]
        self.assertTrue(code["benchmark_addendum_path"].endswith("ADDENDUM_V0_2_2026-09-14.yaml"))
        self.assertTrue(code["environment_lock_path"].endswith("ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml"))


if __name__ == "__main__":
    unittest.main()
