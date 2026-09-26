#!/usr/bin/env python3
"""
workflow_inspect.py — what does each workflow actually run?

Run from the repository root, on a checked-out SHA:

    python3 workflow_inspect.py
    python3 workflow_inspect.py --grep study1b    # only workflows mentioning this

Prints, per workflow: its display name, triggers, jobs, and the actual shell
commands and actions each step executes. The point is to replace "Study 1B
Engineering Assurance is green" with "Study 1B Engineering Assurance runs these
seven commands, and none of them opens the benchmark contract."

A green check is evidence for exactly the commands listed below it, nothing more.
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pip install 'PyYAML>=6,<7'")

WF_DIR = Path(".github/workflows")
INTERESTING = ("unittest", "pytest", "python", "bandit", "pip-audit", "safety",
               "sbom", "cyclonedx", "ruff", "flake8", "mypy", "compileall")


def steps_of(job):
    s = job.get("steps")
    return s if isinstance(s, list) else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grep", help="only workflows whose text contains this (case-insensitive)")
    ap.add_argument("--full", action="store_true", help="print every step, not just executing ones")
    args = ap.parse_args()

    if not WF_DIR.is_dir():
        sys.exit(f"{WF_DIR} not found — run from the repository root")

    files = sorted(p for p in WF_DIR.iterdir() if p.suffix in (".yml", ".yaml"))
    if not files:
        sys.exit(f"no workflow files in {WF_DIR}")

    print(f"{len(files)} workflow file(s) in {WF_DIR}\n")

    for f in files:
        raw = f.read_text(errors="replace")
        if args.grep and args.grep.lower() not in raw.lower():
            continue
        try:
            wf = yaml.safe_load(raw) or {}
        except yaml.YAMLError as e:
            print(f"!! {f.name}: unparseable ({e})\n")
            continue

        # PyYAML turns the bare key `on:` into boolean True.
        triggers = wf.get("on", wf.get(True, "?"))
        if isinstance(triggers, dict):
            triggers = ", ".join(triggers)
        elif isinstance(triggers, list):
            triggers = ", ".join(map(str, triggers))

        print("=" * 78)
        print(f"{f.name}")
        print(f"  display name : {wf.get('name', '(none)')}")
        print(f"  triggers     : {triggers}")
        print("=" * 78)

        jobs = wf.get("jobs") or {}
        if not jobs:
            print("  (no jobs)\n")
            continue

        for job_id, job in jobs.items():
            runs_on = job.get("runs-on", "?")
            print(f"\n  job: {job_id}   [{runs_on}]")
            if job.get("if"):
                print(f"    condition: {job['if']}")
            executed = 0
            for i, st in enumerate(steps_of(job), 1):
                name = st.get("name") or st.get("id") or f"step {i}"
                if "uses" in st:
                    print(f"    - {name}\n        uses: {st['uses']}")
                    executed += 1
                elif "run" in st:
                    body = str(st["run"]).strip()
                    lines = [l.strip() for l in body.splitlines() if l.strip()
                             and not l.strip().startswith("#")]
                    hot = any(k in body.lower() for k in INTERESTING)
                    if not (hot or args.full):
                        print(f"    - {name}   ({len(lines)} shell line(s), no test/lint/audit keyword)")
                        continue
                    print(f"    - {name}")
                    for l in lines:
                        print(f"        $ {l}")
                    executed += 1
                elif args.full:
                    print(f"    - {name}   (no run/uses)")
            if executed == 0:
                print("    (no executing steps matched — rerun with --full)")
        print()

    print("=" * 78)
    print("For each workflow ask: which step verifies the property I am relying on?")
    print("If you cannot point at the step, the green check is not evidence for it.")
    print("=" * 78)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:      # piping into head/less
        pass
