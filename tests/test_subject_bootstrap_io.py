from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from siamese_compression_lab.subject_bootstrap import SubjectPairRow
from siamese_compression_lab.subject_bootstrap_io import (
    load_and_validate_score_join,
    sha256_file,
    verify_historical_score_artifact,
)


class SubjectBootstrapIOTests(unittest.TestCase):
    def test_historical_score_artifact_must_match_bytes_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test_pair_scores.csv"
            path.write_text("immutable\n", encoding="utf-8")
            expected_hash = sha256_file(path)
            evidence = verify_historical_score_artifact(
                path,
                expected_bytes=path.stat().st_size,
                expected_sha256=expected_hash,
            )
            self.assertEqual(evidence["sha256"], expected_hash)
            path.write_text("changed\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_historical_score_artifact(
                    path,
                    expected_bytes=len("immutable\n"),
                    expected_sha256=expected_hash,
                )

    def test_every_route_must_join_one_to_one_with_subject_map(self) -> None:
        rows = [
            SubjectPairRow("g0", 1, "A", "A", "matched", 0),
            SubjectPairRow("i0", 0, "A", "B", "mismatched", 0),
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scores.csv"
            pd.DataFrame(
                [
                    {"run_id": "r", "method": "raw", "seed": 11, "pair_id": "g0", "same": 1, "distance": 0.2},
                    {"run_id": "r", "method": "raw", "seed": 11, "pair_id": "i0", "same": 0, "distance": 0.8},
                    {"run_id": "r", "method": "candidate", "seed": 11, "pair_id": "g0", "same": 1, "distance": 0.3},
                    {"run_id": "r", "method": "candidate", "seed": 11, "pair_id": "i0", "same": 0, "distance": 0.7},
                ]
            ).to_csv(path, index=False)
            frame = load_and_validate_score_join(path, rows)
            self.assertEqual(len(frame), 4)

            broken = pd.read_csv(path).iloc[:-1]
            broken.to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "pair_id universe|one score"):
                load_and_validate_score_join(path, rows)


if __name__ == "__main__":
    unittest.main()
