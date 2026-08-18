"""Preflight the reviewed decomposed Study 0 coverage path without executing outcomes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from siamese_compression_lab.decomposed_coverage import (
    DECOMPOSED_PRODUCTION_GATE,
    load_coverage_contract,
)
from siamese_compression_lab.scientific_harness import assert_execution_unblocked

DEFAULT_CONTRACT = Path("protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml")
DEFAULT_CHRONICLE = Path("protocol/scientific_chronicle.yaml")
DEFAULT_SCIENTIFIC_HARNESS = Path("gates/scientific_harness.yaml")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--chronicle", type=Path, default=DEFAULT_CHRONICLE)
    parser.add_argument("--scientific-harness", type=Path, default=DEFAULT_SCIENTIFIC_HARNESS)
    args = parser.parse_args()

    contract = load_coverage_contract(args.contract, require_execution_authorized=True)
    assert_execution_unblocked(
        args.chronicle,
        args.scientific_harness,
        DECOMPOSED_PRODUCTION_GATE,
    )
    checkpoints = [int(value) for value in contract["simulation_precision"]["dataset_checkpoints"]]
    if checkpoints != [2000, 4000, 10000]:
        raise ValueError("decomposed production workflow requires the frozen 2000/4000/10000 checkpoints")
    print(
        json.dumps(
            {
                "status": "EXECUTION_PREFLIGHT_PASS",
                "contract_id": contract["contract_id"],
                "checkpoints": checkpoints,
                "historical_study_0_scores_read": False,
                "outcome_evidence_seen": False,
                "production_coverage_gate_executed": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
