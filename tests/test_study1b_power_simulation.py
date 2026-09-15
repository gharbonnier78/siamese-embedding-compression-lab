from __future__ import annotations

import unittest

from siamese_compression_lab.study1b_simulation import run_power_dataset, scenario_for_graph
from siamese_compression_lab.subject_bootstrap import SubjectPairRow


class Study1BPowerSimulationTests(unittest.TestCase):
    @staticmethod
    def _rows() -> list[SubjectPairRow]:
        rows = []
        for index, subject in enumerate("ABCDEFGH"):
            rows.append(SubjectPairRow(f"g_{subject}", 1, subject, subject, "fixture", index))
        offset = len(rows)
        for index, (left, right) in enumerate(
            [("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("B", "D"),
             ("C", "D"), ("E", "F"), ("E", "G"), ("F", "H"), ("G", "H")]
        ):
            rows.append(
                SubjectPairRow(
                    f"i_{left}{right}", 0, left, right, "fixture", offset + index
                )
            )
        return rows

    def test_power_dataset_uses_one_reference_for_all_five_model_seeds(self) -> None:
        rows = self._rows()
        scenario = scenario_for_graph(
            "power_fixture",
            0.01,
            rows,
            subject_effect_sd_genuine=0.02,
            subject_effect_sd_impostor=0.01,
            candidate_reference_noise_correlation=0.7,
        )
        first = run_power_dataset(
            scenario,
            rows,
            dataset_index=3,
            bootstrap_replicates=25,
        )
        second = run_power_dataset(
            scenario,
            rows,
            dataset_index=3,
            bootstrap_replicates=25,
        )
        self.assertTrue(first["shared_reference"])
        self.assertEqual(first["reference_sha256"], second["reference_sha256"])
        self.assertEqual(
            {row["reference_sha256"] for row in first["seeds"]},
            {first["reference_sha256"]},
        )
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
