# Study 1B v0.6 review-package requirements — N6

Date: 2026-09-14
Status: prospective review-process rule

## Purpose

Restore reviewer-side inspectability without reintroducing silent transport divergence.

Every v0.6 focused re-review package MUST include the exact normative artifacts that the reviewer is asked to accept,
not merely excerpts or immutable URLs. For every shipped repository-derived normative file, the package MUST record the
expected Git blob SHA-1 and instruct the reviewer to recompute it locally from the shipped bytes:

`SHA1("blob " + decimal_byte_length + "\0" + content_bytes)`

A mismatch is a package failure and MUST be reported rather than repaired silently.

## Minimum shipped normative artifacts

- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_V0_2_2026-09-14.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml`
- `protocol/reviews/PR50_CB124244_D2_V05_FOCUSED_REREVIEW_VERDICT_2026-09-10.md`
- `protocol/chronicle/STUDY1B_PR50_CB124244_D2_V05_ACCEPT_2026-09-14.yaml`
- `protocol/chronicle/STUDY1B_PR50_PREEXECUTION_SEMANTIC_HARDENING_V0_6_OPEN_2026-09-14.yaml`
- `protocol/reviews/STUDY1B_PREEXECUTION_SEMANTIC_HARDENING_V06_REREVIEW_REQUEST_2026-09-14.md`
- `tests/test_study1b_engineering_benchmark_contract_v06.py`
- `harness-adoption.yaml`
- `AGENTS.md`

If another test is requested, every file it resolves MUST also be shipped at its repository path.

## Reviewer-side verification

The package README SHOULD ask the reviewer to:

1. verify the outer ZIP SHA-256 announced by the author;
2. verify the package SHA-256 manifest for every non-manifest payload;
3. recompute each expected Git blob SHA-1 from the local shipped bytes;
4. run the focused test from the package root;
5. report any mismatch as missing/invalid transport evidence rather than substituting repository search, memory or author summary.

## Interpretation boundary

Passing package checks proves transport identity and focused contract consistency only. It does not prove construct validity,
scientific acceptance or execution admissibility.