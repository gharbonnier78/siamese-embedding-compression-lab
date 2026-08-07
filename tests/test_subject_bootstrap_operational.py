from __future__ import annotations

import unittest

import numpy as np

from siamese_compression_lab.subject_bootstrap import SubjectPairRow
from siamese_compression_lab.subject_bootstrap_operational import (
    operational_percentile_summary,
    subject_bootstrap_fixed_threshold,
)


class OperationalSubjectBootstrapTests(unittest.TestCase):
    def test_validation_threshold_remains_frozen(self) -> None:
        rows = [
            SubjectPairRow("g_a", 1, "A", "A", "matched", 0),
            SubjectPairRow("g_b", 1, "B", "B", "matched", 1),
            SubjectPairRow("i_ab", 0, "A", "B", "mismatched", 0),
            SubjectPairRow("i_ac", 0, "A", "C", "mismatched", 1),
        ]
        replicates = subject_bootstrap_fixed_threshold(
            rows=rows,
            distances=np.asarray([0.7, 0.5, 0.2, 0.9]),
            validation_threshold=0.42,
            replicates=1,
            seed=123,
        )
        self.assertEqual(replicates[0].threshold, 0.42)
        summary = operational_percentile_summary(replicates)
        self.assertEqual(summary["validation_threshold"], 0.42)

    def test_nonfinite_validation_threshold_is_rejected(self) -> None:
        rows = [
            SubjectPairRow("g_a", 1, "A", "A", "matched", 0),
            SubjectPairRow("i_ab", 0, "A", "B", "mismatched", 0),
        ]
        with self.assertRaisesRegex(ValueError, "finite"):
            subject_bootstrap_fixed_threshold(
                rows=rows,
                distances=np.asarray([0.5, 0.7]),
                validation_threshold=float("nan"),
                replicates=1,
                seed=7,
            )


if __name__ == "__main__":
    unittest.main()
