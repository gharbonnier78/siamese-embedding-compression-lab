#!/usr/bin/env python3
"""
contract_coverage.py — which contract clauses are actually enforced?

Run from the repository root, on a checked-out SHA:

    python3 contract_coverage.py

Walks each normative YAML contract, collects every key path, and checks whether
the key name appears anywhere in the test corpus. A key no test mentions is
prose: it says what should happen and nothing verifies that it does.

This is a heuristic. A key name appearing in a test file does not prove the test
asserts anything useful about it, and a key can be enforced indirectly. Treat a
0% section as a strong signal and a high percentage as a weak one, then read the
tests for the sections you care about.
"""

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("pip install 'PyYAML>=6,<7'")

CONTRACTS = [
    "protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml",
    "protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_V0_2_2026-09-14.yaml",
    "protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml",
    "protocol/benchmarks/STUDY1B_PHASE_A_CONSTRUCT_VALIDITY_CORRECTIONS_V0_1_2026-09-16.yaml",
]

TEST_GLOB = "tests/test_*.py"

# Keys that are bookkeeping rather than substance; not counted.
BORING = {
    "schema_id", "schema_version", "artifact_version", "date", "kind",
    "study_id", "benchmark_id", "correction_id", "status", "next_action",
    "purpose", "rationale", "note", "role", "rule", "requirement",
}


def walk(node, prefix=""):
    """Yield (top_level_section, dotted_path, leaf_key) for every key."""
    if isinstance(node, dict):
        for k, v in node.items():
            path = f"{prefix}.{k}" if prefix else k
            yield path.split(".")[0], path, k
            yield from walk(v, path)
    elif isinstance(node, list):
        for item in node:
            yield from walk(item, prefix)


def main():
    tests = list(Path(".").glob(TEST_GLOB))
    if not tests:
        sys.exit(f"no test files matched {TEST_GLOB} — run from the repo root")
    corpus = "\n".join(p.read_text(errors="replace") for p in tests)
    print(f"test corpus: {len(tests)} files, {len(corpus.splitlines())} lines\n")

    # Which contract files does any test actually OPEN? A key name appearing in
    # the corpus proves nothing if no test ever reads the file that key lives in
    # -- section names collide across contracts and produce false positives.
    opened = {c for c in CONTRACTS if Path(c).name in corpus}
    print("contracts opened by at least one test:")
    for c in CONTRACTS:
        mark = "READ " if c in opened else "NEVER OPENED"
        print(f"  [{mark:>12}]  {Path(c).name}")
    print()

    grand_covered = grand_total = 0

    for contract in CONTRACTS:
        f = Path(contract)
        if not f.exists():
            print(f"!! missing: {contract}\n")
            continue
        doc = yaml.safe_load(f.read_text())
        is_open = contract in opened

        sections = {}
        for section, path, leaf in walk(doc):
            if leaf in BORING:
                continue
            hit = is_open and re.search(rf"\b{re.escape(leaf)}\b", corpus) is not None
            covered, total = sections.get(section, (0, 0))
            sections[section] = (covered + int(hit), total + 1)

        print("=" * 78)
        print(f.name + ("" if is_open else "   <<< NO TEST OPENS THIS FILE"))
        print("=" * 78)
        if not is_open:
            print("  every section below is 0% by construction: no test reads this file.\n")
        silent = []
        for section in sorted(sections, key=lambda s: (sections[s][0] / sections[s][1], s)):
            covered, total = sections[section]
            pct = 100 * covered / total
            bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
            flag = "  <-- NOT ENFORCED" if covered == 0 else ""
            print(f"  {bar} {pct:5.1f}%  {covered:>3}/{total:<3}  {section}{flag}")
            if covered == 0:
                silent.append(section)
            grand_covered += covered
            grand_total += total
        if silent:
            print(f"\n  sections no test mentions at all: {', '.join(silent)}")
        print()

    pct = 100 * grand_covered / grand_total if grand_total else 0
    print("=" * 78)
    print(f"overall: {grand_covered}/{grand_total} keys mentioned by some test ({pct:.1f}%)")
    print("=" * 78)
    print(
        "\nRead the tests for any section you rely on. A mention is not an assertion,\n"
        "and this script cannot tell the difference."
    )


if __name__ == "__main__":
    main()
