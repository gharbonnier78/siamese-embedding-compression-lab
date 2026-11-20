"""Synthetic-only tests for control flow, no claims about biometric performance."""
import json
import sys
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(HERE))
from sim.digital_twin import load_scenario, run, simulate_capture, vector
from sim.console import check_sanitized

class EndToEndSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenes=load_scenario(HERE/"sim"/"synthetic_scenes.json")

    def test_reproducible_active_128_and_512_models(self):
        a=run(self.scenes,128,17)
        b=run(self.scenes,128,17)
        c=run(self.scenes,512,17)
        self.assertEqual(a,b)
        self.assertEqual(a["manifest"]["active_dimension"],128)
        self.assertEqual(c["manifest"]["active_dimension"],512)
        self.assertEqual(len(vector("lab-001",512)),512)
        self.assertEqual(len(vector("lab-001",128)),128)
        self.assertFalse(a["manifest"]["no_real_images"] is False)

    def test_allow_unknown_review_and_no_decision(self):
        report=run(self.scenes,128)
        decisions={c["capture_id"]:c["decision"] for c in report["captures"]}
        self.assertEqual(decisions["syn-day-front-001"],"ALLOWLIST_CANDIDATE")
        self.assertEqual(decisions["syn-night-nir-003"],"REVIEW_REQUIRED")
        self.assertEqual(decisions["syn-unknown-005"],"UNKNOWN")
        self.assertEqual(decisions["syn-side-no-decision-004"],"NO_DECISION")
        self.assertTrue(report["security_alerts"])
        self.assertEqual(report["security_alerts"][0]["operator_ack"],"PENDING")

    def test_radio_alert_payload_contains_no_identity_or_embedding(self):
        report=run(self.scenes,128)
        for alert in report["security_alerts"]:
            self.assertNotIn("candidate_ref",alert)
            self.assertNotIn("subject",json.dumps(alert))
            self.assertNotIn("score",alert)
            self.assertNotIn("image",alert)

    def test_offline_network_and_radio_only_affect_reporting(self):
        report=run(self.scenes,128,ethernet_up=False,alert_radio_up=False)
        self.assertTrue(all(x["status"]=="QUEUED_OFFLINE" for x in report["ethernet_telemetry"]))
        self.assertTrue(all(x["rf_receipt"]=="QUEUED" for x in report["security_alerts"]))
        self.assertEqual(len(report["captures"]),len(self.scenes))

    def test_console_rejects_biometric_payload(self):
        report=run(self.scenes,128)
        permitted={k:report[k] for k in ("manifest","probes","ethernet_telemetry","security_alerts")}
        check_sanitized(permitted)
        permitted["security_alerts"][0]["face_template"]="bad"
        with self.assertRaises(ValueError):
            check_sanitized(permitted)

if __name__=="__main__": unittest.main()
