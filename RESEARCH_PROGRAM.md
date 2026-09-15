# Research programme v0.3

## Purpose

This repository studies a bounded engineering-scientific question:

> Can a learned projection reduce biometric embedding cost while preserving decision-relevant verification or identification performance relative to the uncompressed representation and matched compression controls?

The programme is falsifiable by design and separates:

1. mechanism validity;
2. representation value;
3. supervision value;
4. threshold-transfer validity;
5. uncertainty and decision-procedure validity;
6. engineering value;
7. claim admissibility.

A failed gate is a valid result. Later studies never overwrite earlier evidence.

## Current state — 2026-09-15

Study 0 is closed after corrected identity-aware uncertainty reanalysis. None of the tested 128D routes demonstrated non-inferiority to raw512 under the frozen Study 0 rule.

Study 1B is now the active design programme. It consumes the frozen face-specific AdaFace 512D substrate and preregisters matched `raw512`, `random128`, `pca128` and `siamese128` routes.

Protected Study 1B outcomes remain sealed.

The Stage B uncertainty/power preflight has been calibrated prospectively using synthetic known-truth worlds. Both frozen calibration procedures, S4N1 and S4N2, remain `CLOSED_NEGATIVE`: at true `Delta_FNMR=0.01`, all declared selector power estimates remain below the frozen 0.90 target, and their exact 95% Monte-Carlo uncertainty upper endpoints remain below 0.90. S4N3 has not been launched.

The programme therefore separates the unresolved biometric claim from a distinct non-outcome engineering-value question: what does the exact 512→128 structural reduction buy in RAM, dense-search compute, latency, throughput, queueing, energy and hardware-tier feasibility?

A Jungle Championship Phase A benchmark contract exists for synthetic exact-dense FP32 CPU top-1 search. Canonical execution remains blocked. The real edge hardware, load generator, external power meter, configuration-choice provenance and execution-specific environment lock are not yet materialized.

The v0.5 independent review accepted D1/D2/D3 provenance and information-firewall design while explicitly leaving execution inadmissible and construct validity unreviewed. The current v0.6 cycle prospectively hardens N4 (possession vs creation influence), N5 (scope of mechanically checkable temporal ordering), R1/N2 (choice-specific informational overlap across hardware classes) and N6 (self-contained review transport). v0.6 awaits independent re-review.

| Object | Current state |
| --- | --- |
| Study 0 corrected reanalysis | CLOSED |
| Study 1B SCREEN | SEALED |
| Study 1B qualification TEST | SEALED |
| S4N1 | CLOSED_NEGATIVE |
| S4N2 | CLOSED_NEGATIVE |
| S4N3 | NOT_LAUNCHED |
| D1/D2/D3 v0.5 history | ACCEPTED |
| v0.6 N4/N5/R1-N2 | CORRECTED_PROSPECTIVELY_AWAITING_REVIEW |
| Construct validity of Phase A | NOT_REVIEWED |
| Phase A target platform/measurement setup | NOT_BOUND |
| Canonical Phase A execution | BLOCKED |
| Representation geometry | OUTSIDE_CURRENT_OPEN_SCOPE |

## Frozen Study 1B scientific core

Primary estimand:

`Delta_FNMR(m, alpha) = FNMR_m(alpha) - FNMR_raw512(alpha)`.

Frozen values:

- `alpha = 0.01`;
- `delta_FNMR = 0.03`;
- one-sided UCB = 0.975;
- Stage B route seeds `[11,29,47,71,101]`;
- 10,000 identity-aware bootstrap replicates;
- all-seeds method-level non-inferiority rule.

`NOT_DEMONSTRATED` is distinct from inferiority.

## Evidence escalation and boundaries

### Protected scientific outcomes

SCREEN and qualification TEST route outcomes are outcome-bearing. They remain unopened.

### Synthetic calibration evidence

S4 known-truth simulations evaluate procedure behavior, not real biometric performance.

At `Delta=.01`:

- S4N1 powers: FIXED 0.8655, prospectively preferred VALIDATION_BEST 0.8690, MEDIAN 0.8695;
- S4N2 powers: FIXED 0.8470, prospectively preferred VALIDATION_BEST 0.8490, MEDIAN 0.8535.

S4N1/S4N2 use the same deterministic synthetic population and compare two uncertainty procedures; they are not independent replications.

### Engineering evidence

Future Phase A engineering measurements use synthetic vectors and cannot establish biometric non-inferiority or superiority.

### Structural facts

At equal datatype/encoding, 512→128 reduces vector payload and direct dense coordinate contributions by exactly 75%. This does not imply 4× end-to-end speed or 75% lower power.

## Study sequence

| Study / workstream | Status | Purpose |
| --- | --- | --- |
| Study 0 | completed/corrected | original LFW/ImageNet compression audit |
| Study 1A | frozen face-specific substrate | qualify source representation |
| Study 1B scientific | preregistered, protected outcomes sealed | matched compression comparison |
| Study 1B S4 | closed negative | calibrate uncertainty/power before TEST |
| Study 1B engineering Phase A | design only, execution blocked | measure structural engineering consequences |
| Construct-validity review | pending | verify benchmark answers intended engineering question |
| Later dimension/index/quantization work | future | separate interventions requiring their own contracts |

## Current engineering benchmark contract

Phase A freezes:

- exact dense dot-product top-1;
- FP32 CPU;
- L2-normalized synthetic vectors;
- fixed work, no threshold gating;
- no candidate pruning or ANN;
- paired 512D/128D arms on the same bound tier;
- G0 small-control and G2 large-gallery sensitivity;
- external device-input/wall power for strong energy claims.

G2 is a scenario, not event fact:

- 500,000 whitelist + 10,000 blacklist identities;
- 3 templates/identity;
- 1.53M templates;
- FP32 payload 3,133,440,000 bytes at 512D versus 783,360,000 bytes at 128D.

## D1/D2/D3 and v0.6

D1 provides accountable provenance and attestation for lock-defining choices.

D2 provides bounded public temporal ordering for genuinely pre-existing external evidence and cannot replace D1.

D3 classifies prior evidence by informational relevance, not by intent or labels.

v0.6 prospectively clarifies:

- N4: possession/review does not itself equal influence over evidence creation;
- N5: only the temporal-ordering component is mechanically checkable;
- R1/N2: relevance must be evaluated per lock-defining choice, allowing portable backend/threading/measurement-method information to transfer across hardware classes;
- N6: future review packages ship exact normative artifacts and Git blob SHA-1 values for local recomputation.

Canonical Phase A remains blocked until v0.6 re-review, construct-validity review, platform/measurement materialization, provenance attestation, execution-specific lock freeze and exact-head assurance.

## Reader-facing documents

- Current detailed narrative: `paper/study1_protocol_v0.4-preexecution-v06.md`
- Current research monograph source: `paper/siamese_embedding_compression_research_program_v0.3.md`
- Historical Study 0 closure: `STUDY0_FINAL_REPORT.md`
- Historical PDFs remain versioned and are never overwritten.

## Main normative sources

- `protocol/studies/STUDY1B_MATCHED_COMPRESSION_PREREGISTRATION_2026-08-27.md`
- `protocol/decisions/STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml`
- `protocol/reviews/PR50_CB124244_D2_V05_FOCUSED_REREVIEW_VERDICT_2026-09-10.md`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_V0_2_2026-09-14.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml`
- `protocol/chronicle/STUDY1B_PR50_PREEXECUTION_SEMANTIC_HARDENING_V0_6_OPEN_2026-09-14.yaml`
- `harness-adoption.yaml`

Machine checks establish internal consistency and replayability. They do not substitute for scientific validity, construct validity or domain expertise.
