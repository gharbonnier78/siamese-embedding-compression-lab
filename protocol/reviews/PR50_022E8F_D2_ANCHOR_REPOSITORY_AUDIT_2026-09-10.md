# PR #50 — repository-side audit of the D2 earliest-public-workload anchor

Date: 2026-09-10  
Scope: non-outcome provenance / review follow-up only  
Protected boundary: no Study 1B SCREEN, qualification TEST, real route performance, representation geometry, amendment, or S4N3 is opened.

## Trigger

The focused D2 reviewer returned `ACCEPT` on head `022e8f50437dca4b2aa56a034a5fb63e7751301b`, but made that closure explicitly conditional on one repository-side fact they could not verify: that commit `878bfe2a64b34cce474a627d04b30233e2356958` at `2026-09-07T06:33:05Z` was the **earliest** repository commit publishing the classifier-relevant workload attributes. The reviewer stated that if a materially informative description existed earlier, D2 would reopen.

Archived verdict:
`protocol/reviews/PR50_022E8F_D2_CLOSURE_VERDICT_2026-09-10.md`

## What repository access verifies

### A. The claimed anchor is real, but it is not the first relevant publication

Commit:
`878bfe2a64b34cce474a627d04b30233e2356958`

Timestamp:
`2026-09-07T06:33:05Z`

Message:
`benchmark: freeze Jungle Championship engineering benchmark proposal`

It adds:
`protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_1_2026-09-07.yaml`

That artifact explicitly freezes the later Phase-A-style workload envelope including 512D/128D, FP32, CPU and exact dense search.

However, its parent tree already contains earlier non-outcome engineering notes that disclose enough of the same dimensional / dense-comparison workload family to make a materially informative prior benchmark constructible.

### B. Earlier commit `eb4ac74...` already publishes dimensional + brute-force dense-comparison semantics

Commit:
`eb4ac74a9afd0516d727a7f0c714964b9b198e03`

Timestamp:
`2026-09-07T04:36:17Z`

Message:
`research: quantify nonoutcome 512D to 128D structural benefit envelope`

Added artifact:
`docs/research-notes/STUDY1B_512D_TO_128D_STRUCTURAL_BENEFIT_ENVELOPE_2026-09-07.md`

The note explicitly publishes:

- 512D reference versus 128D compressed representation;
- float32 illustrative payload arithmetic;
- direct dot product / cosine numerator between dense vectors;
- `brute-force dense comparison` as the dimensional compute component;
- a statement that raw comparison-kernel latency/throughput by dimension and end-to-end search throughput/latency require engineering benchmark measurement.

This is earlier than `878bfe2a` by 1 h 56 min 48 s. Under lock v0.4's own rule — earliest immutable commit at which workload attributes were sufficiently published to construct a materially informative prior measurement — this earlier publication is enough to invalidate `878bfe2a` as the claimed earliest bound. It is not necessary for the earlier artifact to be the final benchmark contract; the firewall is explicitly information-based rather than intent- or label-based.

Immutable URLs:

- commit: https://github.com/gharbonnier78/siamese-embedding-compression-lab/commit/eb4ac74a9afd0516d727a7f0c714964b9b198e03
- artifact: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/eb4ac74a9afd0516d727a7f0c714964b9b198e03/docs/research-notes/STUDY1B_512D_TO_128D_STRUCTURAL_BENEFIT_ENVELOPE_2026-09-07.md

### C. Further pre-anchor engineering material strengthens the finding

Commit `e8e82475c23968ec4a624460575a7948bf218bf4` at `2026-09-07T05:17:08Z` adds the edge engineering input sheet. It records 512D vs 128D, FP32/FP16/INT8, CPU/GPU/NPU, `exact_or_indexed_search`, and notes that 512D→128D gives 75% fewer coordinate contributions for fixed dense comparison while latency/energy require benchmark evidence.

Commit `034e465c355468a56cd13332b10d6c971ff19d71` at `2026-09-07T05:17:38Z` adds the Jungle Championship hardware/energy trade-off note. It records the same representation dimensions, FP32 baseline, CPU as an admissible/preferred architecture when sufficient, exact-or-qualified-indexed search as an explicit design choice, and a benchmark matrix across representation, datatype, compute, gallery size and peak-flow profile.

Both predate `878bfe2a` and independently show that the engineering workload design was already being made explicit before the claimed anchor.

## Conclusion

The reviewer verdict itself is preserved exactly as issued. The repository-side condition on which its D2 closure depended is **not satisfied** by the current anchor.

Therefore the project state is:

- reviewer verdict on `022e8f...`: `ACCEPT` — historical review fact;
- D1: closed;
- D3: closed;
- D2: **REOPENED_BY_REPOSITORY_ANCHOR_AUDIT**;
- `PRIOR_DESIGN_CONDITIONS_SATISFIED`: no, prospectively, until a corrected earliest-public-information bound is established and re-reviewed;
- canonical Phase A execution: no;
- construct validity reviewed: no.

This does not imply that `eb4ac74...` is already proven to be the globally earliest correct anchor. It proves only the narrower and sufficient fact that `878bfe2a...` is **not** earliest. A bounded backward repository-history audit must now determine the earliest admissible public-information bound before environment lock v0.5 is frozen.

## Reviewer observations retained for the next prospective lock

### N1 — D1 / D2 responsibility split

Before the execution-specific lock is frozen, state explicitly:

- D2 temporal ordering can discharge third-party or genuinely pre-existing external evidence against the public-information bound;
- D1 attributable attestation carries the negative for evidence produced, commissioned, or otherwise known by the attesting party before public commit time;
- the public commit anchor never substitutes for that attestation.

### N2 / R1 — portable-choice informational overlap

Still open and nonblocking for the historical D1–D3 verdict, but it must be addressed before execution-specific lock freeze. Hardware-class conjunction can under-classify evidence that remains informative for portable choices such as BLAS/backend selection, threading/affinity, or energy-measurement methodology. Any correction is prospective and requires review; do not silently rewrite D3.

### N3 — schema note

Repository inspection shows that the current schema policy already names `the append-only S4N1/S4N2 shared-population/t19 clarification` in its **Historical compatibility** section. Therefore the reviewer's N3 observation is already resolved on the current repository head; the historical S4 clarification itself remains untouched.

## Next admissible action

1. Complete a bounded backward repository-history audit for the earliest public workload information sufficient to construct a materially informative Phase A-style measurement.
2. Record that evidence immutably.
3. Create environment lock v0.5 prospectively with the corrected bound and the explicit D1/D2 responsibility split; do not rewrite v0.4.
4. Treat N2/R1 as a separate pre-execution lock-hardening item and review any semantic change prospectively.
5. Run bounded assurance on the new exact head and request a focused re-review.
6. Do not execute canonical Phase A while either execution blocker remains, and do not infer construct validity from this provenance track.
