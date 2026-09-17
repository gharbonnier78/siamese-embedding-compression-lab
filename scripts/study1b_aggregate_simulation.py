"""Aggregate resumable Study 1B non-outcome coverage/power simulation shards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from siamese_compression_lab.study1b_simulation import coverage_gate, power_gate


def _load_rows(root: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(root.rglob("*.jsonl")):
        if path.name.endswith(".progress.jsonl"):
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if "dataset_index" in row and "mode" in row:
                    rows.append(row)
    if not rows:
        raise ValueError(f"no simulation rows found under {root}")
    return rows


def _unique_by_index(rows: list[dict]) -> list[dict]:
    by_index: dict[int, dict] = {}
    for row in rows:
        index = int(row["dataset_index"])
        if index in by_index and by_index[index] != row:
            raise ValueError(f"conflicting duplicate dataset_index {index}")
        by_index[index] = row
    return [by_index[index] for index in sorted(by_index)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--mode", choices=["coverage", "power"], required=True)
    parser.add_argument("--expected-per-scenario", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rows = _load_rows(args.input_root)
    summary: dict = {
        "schema_version": 1,
        "kind": f"study1b_{args.mode}_simulation_summary",
        "scientific_outcomes_opened": False,
        "mode": args.mode,
        "expected_per_scenario": args.expected_per_scenario,
        "scenarios": {},
    }

    if args.mode == "coverage":
        names = sorted({str(row["scenario"]) for row in rows if row.get("mode") == "coverage"})
        for name in names:
            selected = _unique_by_index(
                [row for row in rows if row.get("mode") == "coverage" and row["scenario"] == name]
            )
            if len(selected) != args.expected_per_scenario:
                raise ValueError(
                    f"{name}: expected {args.expected_per_scenario} datasets, got {len(selected)}"
                )
            summary["scenarios"][name] = coverage_gate(selected)
    else:
        effects = sorted(
            {float(row["effect_scenario"]) for row in rows if row.get("mode") == "power"}
        )
        for effect in effects:
            selected = _unique_by_index(
                [
                    row
                    for row in rows
                    if row.get("mode") == "power" and float(row["effect_scenario"]) == effect
                ]
            )
            if len(selected) != args.expected_per_scenario:
                raise ValueError(
                    f"delta={effect}: expected {args.expected_per_scenario} datasets, got {len(selected)}"
                )
            if not all(row.get("shared_reference") is True for row in selected):
                raise ValueError(f"delta={effect}: shared-reference invariant missing")
            summary["scenarios"][f"delta_{effect:g}"] = power_gate(selected)

    summary["pass"] = bool(summary["scenarios"]) and all(
        bool(value["pass"]) for value in summary["scenarios"].values()
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
