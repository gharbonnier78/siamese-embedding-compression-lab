from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CORRECTIONS = ROOT / "protocol/benchmarks/STUDY1B_PHASE_A_CONSTRUCT_VALIDITY_CORRECTIONS_V0_1_2026-09-16.yaml"


class Study1BPhaseAConstructValidityCorrectionsV01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.c = yaml.safe_load(CORRECTIONS.read_text(encoding="utf-8"))

    def test_review_basis_and_boundary(self) -> None:
        self.assertEqual(
            self.c["review_basis"]["construct_validity_reviewed_head"],
            "b5720dd7e2031e0ac090ae4f5ea4c09fb0a05cc5",
        )
        self.assertEqual(self.c["review_basis"]["verdict"], "ACCEPT_WITH_LIMITATIONS")
        b = self.c["scientific_boundary"]
        self.assertFalse(b["screen_opened"])
        self.assertFalse(b["qualification_test_opened"])
        self.assertFalse(b["real_route_performance_opened"])
        self.assertFalse(b["representation_geometry_opened"])
        self.assertFalse(b["s4n3_launched"])
        self.assertFalse(b["phase_a_executed"])

    def test_b1_requires_cache_hierarchy_and_measured_bandwidth(self) -> None:
        b1 = self.c["B1_cache_and_bandwidth_observability"]
        cache = b1["required_environment_cpu_extension"]["cache_hierarchy"]
        self.assertIn("l1d_capacity_bytes_per_core_or_cluster", cache)
        self.assertIn("l2_capacity_bytes_per_core_or_cluster", cache)
        self.assertIn("l3_or_llc_capacity_bytes_total", cache)
        self.assertIn("sharing_topology", cache)
        bw = b1["required_environment_memory_extension"]["achievable_bandwidth_characterization"]
        self.assertIn("measurement_method", bw)
        self.assertIn("measured_achievable_bandwidth_GB_per_s", bw)
        self.assertEqual(bw["role"], "ENVIRONMENT_CHARACTERIZATION_NOT_LOCK_SELECTION_SIGNAL")
        report = set(b1["required_reporting"])
        self.assertIn("arm_working_set_to_llc_ratio", report)
        self.assertIn("achieved_to_measured_bandwidth_fraction_when_observable", report)

    def test_b1_bandwidth_characterization_cannot_retune_frozen_choices(self) -> None:
        rule = self.c["B1_cache_and_bandwidth_observability"]["required_environment_memory_extension"][
            "achievable_bandwidth_characterization"
        ]["rule"]
        self.assertIn("prospectively frozen before this characterization is run", rule)
        self.assertIn("MUST NOT be used to retune or substitute", rule)
        self.assertIn("new prospective design/execution identity", rule)

    def test_b2_forbids_cross_regime_or_censored_ratios(self) -> None:
        b2 = self.c["B2_saturation_and_censoring_pairwise_interpretation"]
        rule = b2["required_pairwise_rule"]
        self.assertIn("same non-censored saturation regime", rule)
        self.assertIn("do not compute or publish a combined performance ratio", rule)
        self.assertFalse(b2["saturation_point_reporting"]["cross_regime_ratio_permitted"])
        self.assertFalse(b2["saturation_point_reporting"]["right_censored_ratio_permitted"])
        self.assertIn("REGIME_CROSSING_NO_COMBINED_RATIO", b2["required_status_token_for_invalid_ratio"])
        self.assertIn("CENSORED_PAIR_NO_COMBINED_RATIO", b2["required_status_token_for_invalid_ratio"])

    def test_b3_requires_per_arm_dispatch_provenance(self) -> None:
        b3 = self.c["B3_backend_dispatch_observability"]
        record = b3["required_runtime_extension"]["per_arm_dispatch_record"]
        self.assertIn("backend_reported_kernel_or_core_identifier", record)
        self.assertIn("backend_dispatch_observability_method", record)
        shape = record["exact_call_shape"]
        for key in (
            "operation",
            "gemv_or_batched_gemm",
            "batch_size",
            "matrix_shape",
            "memory_order",
            "leading_dimension",
        ):
            self.assertIn(key, shape)
        provenance = set(b3["result_provenance_extensions"])
        self.assertIn("per_arm_backend_dispatch_record", provenance)
        self.assertIn("exact_search_call_shape_per_arm", provenance)

    def test_b3_does_not_fake_unobservable_dispatch(self) -> None:
        rule = self.c["B3_backend_dispatch_observability"]["unavailable_dispatch_rule"]
        self.assertIn("NOT_EXPOSED_BY_BACKEND", rule)
        self.assertIn("Do not silently infer", rule)
        self.assertIn("NOT_DEMONSTRATED", rule)

    def test_reporting_limitations_are_frozen_prospectively(self) -> None:
        l1 = self.c["L1_energy_reporting_conditioning"]
        self.assertIn("offered QPS", l1["rule"])
        self.assertIn("saturation regime", l1["rule"])
        l3 = self.c["L3_percentile_support_reporting"]
        self.assertIn("200", l3["rule"])
        self.assertIn("1000", l3["rule"])
        self.assertIn("MUST NOT be relaxed after seeing results", l3["rule"])

    def test_l2_remains_future_sensitivity_not_phase_a_blocker(self) -> None:
        l2 = self.c["L2_intermediate_working_set_sensitivity"]
        self.assertEqual(l2["status"], "NOT_PHASE_A_BLOCKER")
        self.assertIn("MUST NOT be interpolated", l2["rule"])

    def test_materialization_and_execution_remain_blocked(self) -> None:
        e = self.c["execution_admissibility"]
        self.assertTrue(e["construct_validity_accepted_with_limitations_on_b5720dd7"])
        self.assertFalse(e["B1_B2_B3_focused_independent_confirmation_obtained"])
        self.assertFalse(e["platform_materialization_permitted"])
        self.assertFalse(e["canonical_phase_a_execution_permitted"])


if __name__ == "__main__":
    unittest.main()
