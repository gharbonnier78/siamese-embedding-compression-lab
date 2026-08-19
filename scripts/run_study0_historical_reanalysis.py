from __future__ import annotations

import argparse
from pathlib import Path

from preflight_study0_historical_reanalysis import preflight_historical_reanalysis
from siamese_compression_lab.historical_reanalysis import execute_historical_reanalysis

ROOT = Path(__file__).resolve().parents[1]
STUDY_PROTOCOL = ROOT / "protocol/studies/study_0_subject_bootstrap_v0.2.2.yaml"
COVERAGE_ROOT = (
    ROOT
    / "evidence/study_0_subject_bootstrap_v0.2.2"
    / "coverage_validation_run_32157868533"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize the frozen Study 0 v0.2.2 historical subject-bootstrap reanalysis. "
            "The governance preflight executes before any historical score artifact is opened."
        )
    )
    parser.add_argument("--historical-run-dir", type=Path, required=True)
    parser.add_argument("--matched-devtest", type=Path, required=True)
    parser.add_argument("--mismatched-devtest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--study-protocol", type=Path, default=STUDY_PROTOCOL)
    parser.add_argument(
        "--coverage-simulation",
        type=Path,
        default=COVERAGE_ROOT / "coverage_simulation.csv",
    )
    parser.add_argument(
        "--coverage-gate",
        type=Path,
        default=COVERAGE_ROOT / "coverage_gate.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Deliberate hard boundary: this is the first operation that may authorize historical
    # access.  Nothing under --historical-run-dir is inspected before this call returns.
    _, activated_via = preflight_historical_reanalysis()
    print(f"PRELIGHT PASS: historical access activated through {activated_via}", flush=True)

    manifest = execute_historical_reanalysis(
        repo_root=ROOT,
        historical_run_dir=args.historical_run_dir,
        matched_path=args.matched_devtest,
        mismatched_path=args.mismatched_devtest,
        output_dir=args.output_dir,
        study_protocol_path=args.study_protocol,
        coverage_simulation_path=args.coverage_simulation,
        coverage_gate_path=args.coverage_gate,
    )
    print(
        "MATERIALIZATION COMPLETE, NOT INTERPRETED: "
        f"{manifest}. No scientific claim or gate was promoted.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
