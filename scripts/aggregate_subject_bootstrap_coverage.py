"""Aggregate complete decomposed Study 0 coverage chunks in canonical contract order."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path

from siamese_compression_lab.decomposed_coverage import aggregate_checkpoint_artifacts

DEFAULT_CONTRACT = Path("protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml")


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("coverage aggregation produced no rows")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--artifact-dir", type=Path, action="append", required=True)
    parser.add_argument("--checkpoint", type=int, required=True)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Aggregate a bounded non-production fixture; never claims a scientific gate.",
    )
    args = parser.parse_args()

    results, decision = aggregate_checkpoint_artifacts(
        args.contract,
        args.artifact_dir,
        expected_commit=args.git_commit,
        checkpoint=args.checkpoint,
        require_execution_authorized=not args.smoke,
    )
    rows = [asdict(result) for result in results]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(args.output_dir / "coverage_simulation.csv", rows)

    if args.smoke:
        decision = {
            **decision,
            "underlying_fixture_mcse_state": decision["status"],
            "status": "SMOKE_ONLY",
            "synthetic_nonproduction_fixture": True,
            "production_coverage_gate_claimed": False,
        }
    (args.output_dir / "checkpoint_decision.json").write_text(
        json.dumps(decision, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
