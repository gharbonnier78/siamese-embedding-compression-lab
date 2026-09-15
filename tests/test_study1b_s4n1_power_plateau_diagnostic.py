from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "study1b_s4n1_power_plateau_diagnostic.py"
SPEC = importlib.util.spec_from_file_location("study1b_s4n1_power_plateau_diagnostic", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load S4N1 power plateau diagnostic module")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Study1BS4N1PowerPlateauDiagnosticTest(unittest.TestCase):
    @staticmethod
    def _rows(expected: int = 4) -> list[dict]:
        rows = []
        errors = (-0.006, -0.002, 0.002, 0.006)
        for truth in MODULE.TRUTHS:
            for index in range(expected):
                error = errors[index % len(errors)]
                point = truth + error
                ucb975 = point + 0.014
                ucb95 = point + 0.012
                low = point - 0.014
                candidates = {}
                for candidate in MODULE.CANDIDATES:
                    candidates[candidate] = {
                        "test_point_delta": point,
                        "test_estimation_error": error,
                        "passes_noninferiority": ucb975 <= MODULE.MARGIN,
                        "covered": low <= truth <= ucb975,
                        "bootstrap": {
                            "delta_fnmr_mean": point,
                            "delta_fnmr_ci_low": low,
                            "delta_fnmr_ucb_95": ucb95,
                            "delta_fnmr_ucb_97_5": ucb975,
                        },
                    }
                rows.append(
                    {
                        "dataset_index": index,
                        "mode": "core",
                        "scientific_outcomes_opened": False,
                        "test_truth_delta": truth,
                        "candidates": candidates,
                    }
                )
        return rows

    def test_diagnose_preserves_frozen_population_and_boundaries(self) -> None:
        result = MODULE.diagnose(self._rows(), 4)
        self.assertFalse(result["scientific_outcomes_opened"])
        self.assertFalse(result["s4n1_negative_result_reopened"])
        self.assertTrue(result["frozen_interpretation_tests"]["point_bias_not_primary"])
        self.assertTrue(result["frozen_interpretation_tests"]["selector_not_primary"])
        cell = result["cells"]["delta_0_01"]["S4N_FIXED_SEED"]
        self.assertEqual(cell["n"], 4)
        self.assertAlmostEqual(cell["ucb97_5_minus_point"]["median"], 0.014)
        self.assertIn("crossfit_known_truth_oracle", cell)

    def test_missing_archived_dataset_fails_closed(self) -> None:
        rows = self._rows()
        rows.pop()
        with self.assertRaisesRegex(ValueError, "require exact dataset indices"):
            MODULE.validate_archived_population(rows, 4)


if __name__ == "__main__":
    unittest.main()
