# Siamese Embedding Compression Lab — Study 1 protocol supplement v0.4-preexecution

**Status:** pre-execution scientific/engineering supplement; no protected Study 1B SCREEN or qualification TEST outcomes are included.

**Documentation basis:** the accepted D1-D3 history through environment-lock v0.5, the prospective v0.6 semantic hardening dated 2026-09-14, and the five green bounded-assurance workflows on the v0.6-bound head. This document is descriptive: it does not release a gate or authorize canonical Phase A execution.

## 1. Programme trajectory

The programme asks a deliberately narrow question before making any product claim:

> Can a 512-dimensional face representation be compressed to 128 dimensions while retaining decision-relevant biometric performance, and if so, is the engineering benefit large enough to justify the additional qualification burden?

The work is split into progressively stronger studies.

1. **Study 0** compared raw512, random128, PCA128 and a learned Siamese128 projection using a frozen ImageNet ResNet-18 feature source and LFW.
2. **Study 1A** changes the substrate first: it specifies reproduction/qualification of an exact face-specific AdaFace R100 512D backbone before compression claims are revisited.
3. **Study 1B** is the matched compression study on that qualified substrate. Its protected real outcomes remain sealed.
4. **Jungle Championship Phase A** is a separate non-outcome engineering benchmark intended to quantify the implementation value of 512D→128D under a frozen edge-computing environment. It cannot rescue or redefine a failed scientific gate.

The programme therefore separates two questions that are related but not interchangeable:

- **scientific preservation question:** does the 128D route remain sufficiently close to raw512 at the frozen biometric operating point?
- **engineering value question:** what memory, comparison-work, latency, throughput and energy consequences follow from the smaller representation on a real target platform?

## 2. Study 0 — closed initial experiment

Study 0 used a frozen ImageNet ResNet-18 512D representation on LFW and compared:

- **raw512** — no compression;
- **random128** — seeded random linear projection;
- **PCA128** — unsupervised 512→128 PCA;
- **Siamese128** — supervised linear 512→128 projection trained with contrastive loss.

The primary operating point was empirical FMR=0.01 with a frozen non-inferiority margin of Δ_FNMR=0.03. Five pseudo-random seeds were required for stochastic routes.

A later audit found that the original uncertainty analysis had resampled pair rows although identities recur across multiple comparisons. The historical scores were not replaced. They were re-analysed with a dependence-aware subject-level procedure. The corrected Study 0 closure remained negative: non-inferiority was not demonstrated for random128, PCA128 or Siamese128.

The Study 0 result is bounded. It does **not** establish that 128D compression is universally inferior, that PCA is unsuitable, or that metric learning is ineffective. It establishes that preservation was not demonstrated in that frozen experiment.

## 3. Study 1A — qualify the source representation before compression

Study 1A specifies the exact face-specific source representation:

- AdaFace;
- R100 / `ir_101`;
- 512-dimensional embedding;
- released WebFace12M-trained checkpoint;
- frozen inference;
- official benchmark protocols and preprocessing equivalence;
- no face-backbone retraining inside Study 1A.

The intended evaluation hierarchy distinguishes reproduction/sanity benchmarks from the preferred low-FMR primary qualification endpoint. LFW, CFP-FP, AgeDB-30, CALFW and CPLFW are not treated as numerically interchangeable with IJB-C.

Gate A is conjunctive: provenance/pipeline integrity plus frozen reproduction thresholds plus a low-FMR primary endpoint. If lawful, replayable IJB-C access is unavailable, the low-FMR gate remains indeterminate until a prospective amendment freezes a public/replayable replacement. NIST FRTE is external context, not a local substitute dataset.

No new Study 1A scientific result is introduced by this v0.4 supplement.

## 4. Study 1B — matched compression study

Study 1B compares the same four representation families on the face-specific substrate:

| Route | Role | Learning source |
|---|---|---|
| raw512 | reference | frozen face backbone |
| random128 | dimensionality-only control | seeded random matrix |
| PCA128 | unsupervised compression control | TRAIN only |
| Siamese128 | supervised metric-compression candidate | TRAIN pair supervision only |

The primary estimand remains the candidate-minus-reference increase in FNMR at a frozen false-match operating point:

`Delta_FNMR(m, alpha) = FNMR_m(alpha) - FNMR_raw512(alpha)`.

Real SCREEN, qualification TEST, real route performance and representation geometry remain unopened in the current pre-execution state.

## 5. Dependence-aware uncertainty and S4 calibration

Study 1B requires the uncertainty procedure to respect the identity/template dependence graph. A pair row is not automatically an independent unit of evidence when the same identity participates in multiple genuine or impostor comparisons.

Before protected real outcomes can be used, the programme calibrated the frozen decision procedure on synthetic known-truth worlds.

### S4N1

The first prospective procedure used the frozen identity-aware subject bootstrap. At true Δ_FNMR=0.01, the prospectively preferred selector achieved power 0.8690 against the frozen 0.90 gate. The maximum observed selector power was 0.8695.

### S4N2

A second prospective procedure, DAGJK20, divided TEST identities into 20 deterministic groups and used a delete-a-group jackknife with a one-sided Student-t multiplier `t_0.975,19 = 2.0930240544`.

At true Δ_FNMR=0.01, the prospectively preferred selector achieved power 0.8490; the maximum observed selector power was 0.8535.

### Interpretation

S4N1 and S4N2 used the **same deterministic synthetic known-truth population**. They are two uncertainty procedures, not two independent validations of the generator. Both are archived `CLOSED_NEGATIVE`; S4N3 has not been launched.

Exact Monte-Carlo uncertainty does not rescue the gate. The largest 95% Clopper-Pearson upper endpoint among the Δ=0.01 cells is below 0.90.

The correct statement is therefore:

> The frozen Study 1B decision procedures tested so far do not attain the preregistered 90% power objective at the acceptable synthetic truth Δ_FNMR=0.01.

This does not open or inspect protected biometric outcomes.

## 6. Why continue with an engineering benchmark after a negative S4 closure?

S4 answers a question about the **ability of the qualification procedure to demonstrate non-inferiority**. It does not answer the implementation question: how much does reducing 512 dimensions to 128 dimensions change the resource envelope of an edge 1:N system?

That engineering information can be valuable even while the scientific compression claim remains unresolved, provided it is not used to redefine the frozen scientific question.

The programme therefore created a distinct non-outcome benchmark contract, illustrated by the Jungle Championship scenario.

## 7. Jungle Championship engineering scenario

The engineering scenario models distributed autonomous edge units deployed around a large event site. Units can perform local 1:N searches, include RGB/NIR acquisition and liveness/tamper functions, operate through intermittent connectivity, and buffer events locally.

The benchmark deliberately distinguishes:

- identities;
- enrolled templates;
- passages/transactions;
- observations;
- camera/device count.

It must not infer workload by naively multiplying stadium capacity by camera count.

The scenario is an engineering stress model, not a product deployment claim and not a biometric-performance dataset.

## 8. Structural consequences of 512D→128D

Some consequences are true by representation structure alone and do not require a timing benchmark.

For equal datatype/encoding:

- dimension ratio = 128 / 512 = 0.25;
- vector payload reduction = 75%;
- exact dense dot/cosine numerator uses 75% fewer coordinate-wise contributions.

Per-template payload:

| Representation | FP32 | FP16 | INT8 |
|---|---:|---:|---:|
| 512D | 2,048 B | 1,024 B | 512 B |
| 128D | 512 B | 256 B | 128 B |
| Saving | 1,536 B | 768 B | 384 B |

These facts do **not** justify claims of “4× faster end-to-end”, “75% lower latency” or “75% lower power”. Runtime effects depend on memory hierarchy, vectorization, backend, threading, indexing, batching, thermal behavior and the rest of the system.

## 9. Central memory/work estimates used for engineering planning

For one illustrative full-replication scenario with 500k whitelist identities, 10k blacklist identities and three templates per identity:

- total templates: 1.53 million;
- FP32 gallery payload at 512D: 3.13344 GB/device;
- FP32 gallery payload at 128D: 0.78336 GB/device;
- structural saving: 2.35008 GB/device;
- dense coordinate contributions per observation: 783.36 million at 512D versus 195.84 million at 128D.

For 50 devices, full replication gives 156.672 GB versus 39.168 GB of aggregate gallery payload.

A hybrid 25% local-replication scenario gives 0.82944 GB versus 0.20736 GB per device.

These are deterministic workload arithmetic under the stated assumptions. They are not measured latency or energy results.

## 10. Phase A engineering benchmark — what it is meant to measure

Phase A is intended to measure the cost of exact dense 1:N search on a frozen target edge platform, with at least:

- raw latency samples;
- throughput;
- RAM residency and swap behavior;
- external power samples;
- joules per identification or a prospectively defined energy metric;
- temperature/throttling where available;
- failure/exclusion logs;
- complete backend/threading/runtime provenance.

The canonical measurement plane for energy is external device-input or wall measurement. On-chip telemetry is supporting diagnostic evidence only.

The load generator is required to be off-device so load generation does not silently contaminate the device-under-test measurements.

No target-workload pilot, smoke test, preview, tuning pass or capacity check may be used to choose the lock-defining configuration before the execution-specific environment lock is frozen.

## 11. D1, D2 and D3 — preventing outcome-informed benchmark design

The engineering benchmark is deliberately protected against a subtler form of leakage: choosing the hardware, BLAS/backend, thread count, power mode or measurement method because earlier target-workload measurements already revealed which choice makes one representation look better.

### D1 — accountable provenance/attestation

D1 applies to evidence whose **creation or framing** was influenced by the attesting party: produced, commissioned, requested, specified, directed or materially framed. It also remains the completeness backstop for every lock-defining choice.

### D2 — public temporal ordering for genuinely pre-existing external evidence

D2 contributes a bounded, mechanically checkable fact: an external/pre-existing evidence timestamp can be shown to be strictly earlier than the immutable repository-root public-information bound.

The current conservative anchor is repository inception:

- commit `4b40e7254bff1b88a44d13fb55b366bc7d3fc263`;
- timestamp `2026-08-07T08:23:56Z`;
- root artifact `README.md`.

Only the temporal ordering is mechanically checkable. Source independence and absence of authoring influence remain provenance/attestation claims.

### D3 — information, not declared intent

Prior evidence is classified by whether it could inform a **lock-defining choice**, not by whether someone says they intended to use it.

The v0.6 hardening makes this classification choice-specific:

- platform-specific choices may depend on hardware class;
- backend/BLAS evidence can remain informative across hardware classes;
- threading/affinity evidence can transfer across materially comparable execution models;
- measurement-method evidence can transfer even when hardware, dimension or search family differ.

Uncertainty defaults to informative. `NOT_INFORMATIVE` requires attributable rationale.

## 12. v0.6 semantic hardening

The accepted v0.5 focused review closed D2 and accepted the D1/D2 responsibility split and repository-root bound, while keeping canonical execution inadmissible and construct validity unreviewed.

The same review recorded three non-blocking items that had to be handled before an execution-specific lock could be frozen:

- **N4:** distinguish influence over evidence creation/framing from mere receipt, possession, citation or review;
- **N5:** stop describing the entire D2 mechanism as mechanically objective when only timestamp ordering is;
- **R1/N2:** classify informational overlap per lock-defining choice so portable backend/threading/measurement evidence is not incorrectly dismissed by hardware mismatch.

Environment-lock v0.6 corrects these prospectively. It preserves the accepted D1-D3 history and does not rewrite historical review artifacts.

A fourth process item, **N6**, changes review-package transport: future packages ship exact normative artifacts plus expected Git blob SHA-1 values so the reviewer can recompute Git object identity locally.

At the current state, the v0.6 semantic hardening still awaits independent re-review.

## 13. Measured, structural and extrapolated claims

To prevent category errors, the programme uses three evidence classes.

### Structural

Derivable exactly from representation dimension and datatype, for example 512D→128D payload reduction.

### Measured

Observed on a frozen, reviewable execution environment with preserved raw evidence, for example latency samples or wall-power samples.

### Extrapolated

Derived from structural or measured quantities under declared workload assumptions, for example aggregate memory across 50 replicated devices or battery-life projections.

An extrapolation must never be restated as though it had been measured.

## 14. Current state — 2026-09-15

### Closed and preserved

- Study 0 corrected initial experiment: negative bounded closure.
- S4N1: `CLOSED_NEGATIVE`.
- S4N2: `CLOSED_NEGATIVE`.
- S4N3: not launched.
- D1: accepted in the v0.5 history.
- D2: accepted in the v0.5 history.
- D3: accepted in the v0.5 history.
- Repository-root temporal bound: accepted.
- Protected SCREEN/TEST/real-route/geometry outcomes: still unopened.

### Prospectively hardened, awaiting focused independent review

- N4 possession-vs-influence semantics;
- N5 objective-vs-attested scope wording;
- R1/N2 choice-specific portable-information classification;
- N6 self-contained review-package process.

### Still absent

- target edge hardware binding;
- external power meter binding;
- off-device load-generator binding;
- complete configuration-choice provenance;
- accountable provenance attestation;
- frozen synthetic generator code identity;
- execution-specific materialized environment lock;
- construct-validity review.

### Canonical Phase A

**NOT ADMISSIBLE.**

Five bounded assurance workflows are green on the v0.6-bound head. Those workflow results establish technical/repository assurance only. They do not constitute the independent semantic acceptance of v0.6, construct validity, platform binding, scientific evidence or execution authorization.

## 15. Exact next admissible sequence

1. Freeze an immutable review basis for the current v0.6 documentation/contract head only after documentation synchronization is complete.
2. Build the N6-compliant self-contained focused re-review package with exact normative artifacts and reviewer-verifiable Git blob SHA-1 values.
3. Obtain independent review of N4, N5 and R1/N2.
4. If accepted, conduct a **separate construct-validity review** of Phase A before selecting/freezing the real platform.
5. Only after construct validity is accepted may the project materialize hardware, power meter, load generator, provenance and the execution-specific environment lock.
6. Re-run bounded assurance on that exact materialized execution head.
7. Only then may canonical Phase A engineering execution become eligible.
8. None of these steps opens protected Study 1B biometric outcomes.

## 16. Authoritative project artifacts

Primary project authority remains the repository artifacts, not this explanatory supplement:

- `AGENTS.md`
- `harness-adoption.yaml`
- `protocol/decisions/STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_V0_2_2026-09-14.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml`
- `protocol/reviews/PR50_CB124244_D2_V05_FOCUSED_REREVIEW_VERDICT_2026-09-10.md`
- `protocol/chronicle/STUDY1B_PR50_PREEXECUTION_SEMANTIC_HARDENING_V0_6_OPEN_2026-09-14.yaml`
- `paper/study0_v0.2.3.tex`
- `paper/study1_protocol_v0.3-preexecution.md`

The project is pinned to scientific-research-harness commit `3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`.

---

**Interpretive rule:** this document may summarize, teach and navigate the programme. It does not supersede frozen protocol artifacts, independent review verdicts or append-only Chronicle entries.
