# Study 1 / Study 1B — Current pre-execution narrative v0.4

**Date:** 2026-09-15  
**Status:** documentation snapshot; no protected Study 1B outcome opened.  
**Scientific authority:** the normative protocol, decision, review, benchmark, environment-lock and Chronicle artifacts named below. This document is explanatory and must not override them.

## 1. Why the programme changed after Study 0

The programme asks whether a learned 512D→128D projection can reduce the engineering cost of biometric embeddings while preserving decision-relevant performance relative to an uncompressed representation and matched compression controls.

Study 0 used frozen ImageNet ResNet-18 512D representations on LFW and compared raw512, random128, PCA128 and Siamese128. Its corrected subject-level reanalysis closed negatively for the frozen non-inferiority claim: none of the tested 128D routes demonstrated non-inferiority to raw512 under the frozen all-seeds rule. That negative result remains valid and is not overwritten by later work.

Study 1 changes the substrate before repeating the compression question. The source representation is a face-specific AdaFace R100/IR101 512D embedding, frozen with exact code/checkpoint/preprocessing provenance. Study 1B then defines a matched comparison among raw512, random128, PCA128 and Siamese128 under identity-disjoint TRAIN / VALIDATION / SCREEN / TEST roles and dependence-aware uncertainty.

## 2. The two questions are now explicitly separated

### 2.1 Scientific question

For candidate route `m` at target false-match rate `alpha`:

`Delta_FNMR(m, alpha) = FNMR_m(alpha) - FNMR_raw512(alpha)`.

The frozen Study 1B qualification contract uses:

- target FMR `alpha = 0.01`;
- non-inferiority margin `delta = 0.03` absolute FNMR;
- one-sided upper confidence level `97.5%`;
- Stage B route seeds `[11, 29, 47, 71, 101]`;
- 10,000 dependence-aware bootstrap replicates for the frozen Stage B procedure;
- all-seeds method rule: a candidate supports the bounded non-inferiority wording only if every preregistered seed passes.

`NOT_DEMONSTRATED` is not a statement of universal inferiority.

### 2.2 Engineering question

Independently of whether biometric non-inferiority can be demonstrated, reducing 512 coordinates to 128 has exact structural consequences for representation payload and dense arithmetic. The engineering question is whether those structural reductions translate, on a prospectively frozen edge platform and workload, into useful RAM, throughput, latency, queueing, energy or hardware-tier effects.

Engineering evidence is firewalled from biometric evidence. It cannot establish biometric non-inferiority, superiority, production suitability, fairness, PAD/security, regulatory conformity or representation geometry.

## 3. Data and evidence hierarchy

Study 1B uses the LFW View 1 identity boundary for a bounded public and reproducible compression experiment. It is not industrial biometric qualification.

The frozen development-side split is deterministic:

| Role | Identities | Main use |
| --- | ---: | --- |
| TRAIN | 2,827 | fit PCA and Siamese training only |
| VALIDATION | 606 | model/checkpoint selection and threshold-development roles |
| SCREEN | 605 | bounded non-claim-bearing Stage A, still sealed |
| TEST | 1,711 | untouched qualification population, still sealed |

The preregistered pair-graph targets are 20k/20k genuine/impostor for TRAIN, 5k/20k for VALIDATION, 5k/50k for SCREEN, and 10k/100k for TEST. Pair graphs are frozen from identity/capture metadata before route outcomes and are shared across routes.

The current programme distinguishes four evidence classes:

1. **Scientific outcome evidence** — SCREEN/TEST biometric route outcomes. Protected and still sealed.
2. **Synthetic calibration evidence** — known-truth simulations used to validate uncertainty/power procedures. S4N1/S4N2 are closed negative on power near the acceptable boundary.
3. **Engineering evidence** — future synthetic-vector Phase A RAM/compute/energy measurements. Not yet admissible because the execution environment and provenance are not materialized.
4. **Structural/analytic facts** — e.g. dimensional and byte-count arithmetic. These need no target-workload execution but do not prove end-to-end benefit.

## 4. Models and algorithms

### raw512

The reference route is the frozen L2-normalized AdaFace 512D embedding. Study 1B records the AdaFace code commit and checkpoint SHA-256 and prohibits changed extraction semantics inside the matched comparison.

### random128

A seeded Gaussian 512×128 random projection with entries distributed `N(0, 1/128)`, followed by L2 normalization. It is the dimensionality-reduction control without data-driven fitting.

### pca128

PCA with `n_components=128`, randomized SVD, no whitening, fitted only on unique TRAIN captures. VALIDATION, SCREEN and TEST cannot enter the fit. The randomized-SVD seed remains part of the method-level seed rule.

### siamese128

A shared affine 512→128 projection followed by L2 normalization, trained with contrastive loss on the frozen TRAIN pair graph. The frozen design uses Adam semantics, learning rate 0.002, weight decay 0.0001 on W, batch size 128, maximum 35 epochs, patience 6, and checkpoint selection by lowest VALIDATION contrastive loss satisfying the minimum-improvement rule. SCREEN/TEST tuning is prohibited.

## 5. Evaluation protocol and uncertainty

Verification pair rows are not independent when identities recur across pairs. Naive row bootstrap is therefore prohibited.

The frozen Study 1B design reuses the corrected subject-slot bootstrap principle:

- resample identity slots;
- genuine edge weight `m_i`;
- impostor edge weight `m_i*m_j`;
- never synthesize absent edges;
- use the same identity draw for raw and candidate in a paired comparison;
- fail closed on excessive degeneracy.

Before qualification TEST can be opened, the uncertainty procedure must also pass known-truth coverage and power calibration on the frozen graph family.

## 6. S4 power calibration — what was learned

S4 is **synthetic known-truth calibration**, not real biometric performance.

Two prospectively frozen uncertainty procedures were evaluated on the **same deterministic synthetic population**. They are two procedures on one evidence population, not two independent replications.

At true `Delta_FNMR = 0.01`, the frozen 90% power target was not reached:

| Procedure | Selector | Estimated power |
| --- | --- | ---: |
| S4N1 | FIXED | 0.8655 |
| S4N1 | prospectively preferred VALIDATION_BEST | 0.8690 |
| S4N1 | MEDIAN | 0.8695 |
| S4N2 DAGJK20 | FIXED | 0.8470 |
| S4N2 DAGJK20 | prospectively preferred VALIDATION_BEST | 0.8490 |
| S4N2 DAGJK20 | MEDIAN | 0.8535 |

The exact 95% Clopper-Pearson upper endpoints for Monte-Carlo power at `Delta=0.01` remain below 0.90 in every selector cell. S4N1 and S4N2 therefore remain `CLOSED_NEGATIVE`. S4N3 has not been launched.

This means: **the frozen qualification procedure does not achieve the preregistered 90% probability of demonstrating non-inferiority near the acceptable boundary `Delta=0.01` under the synthetic generator.** It does not mean that a 128D route is biometrically inferior, and it does not validate or invalidate the real-world generator.

Continuing to invent uncertainty estimators after seeing each failure would create estimator-shopping risk. A new S4N3 would require a new, independently motivated prospective methodological question.

## 7. Operational consequence of the negative S4 closure

The working policy remains conservative:

- a demonstrated qualification result could promote a route to a controlled next engineering/qualification stage;
- non-demonstration retains raw512 by default;
- non-demonstration is not evidence of candidate inferiority;
- preserve raw512 compatibility, rollback ownership and shadow/dual-run possibilities where feasible.

Decision-risk quantities derived from S4 are study-level probabilities. They must not be reframed as person-level biometric harm probabilities.

## 8. Jungle Championship — bounded engineering benchmark

The engineering benchmark uses synthetic vectors only and asks what 512D versus 128D changes for distributed edge 1:N search. Phase A is frozen conceptually as exact dense dot-product top-1 search, FP32, CPU, fixed work, no threshold gating, no ANN/index pruning.

Two Phase A gallery sensitivities are central:

- `G0`: small blacklist control — 10,000 identities × 3 templates;
- `G2`: central full scenario — 500,000 whitelist + 10,000 blacklist identities × 3 templates.

These are **scenario values**, not observed event facts.

For `G2` FP32:

- 1.53 million templates;
- 512D vector payload = 3,133,440,000 bytes;
- 128D vector payload = 783,360,000 bytes.

If a gallery cannot remain RAM-resident on a prospectively bound hardware tier, `RAM_INFEASIBLE_ON_TIER` is a valid engineering result. The protocol forbids silently shrinking the gallery, enabling swap, changing datatype or moving only one arm to a larger tier.

## 9. Structural 512→128 benefit — and its limits

For identical datatype and encoding, 512→128 is exactly a factor of four in vector dimensionality:

| Encoding | 512D | 128D | Saving |
| --- | ---: | ---: | ---: |
| FP32 | 2,048 B | 512 B | 1,536 B (75%) |
| FP16 | 1,024 B | 256 B | 768 B (75%) |
| INT8 | 512 B | 128 B | 384 B (75%) |

For direct dense dot/cosine numerator computation, the number of coordinate contributions is also reduced by 75%.

These are structural facts. They do **not** establish:

- 4× end-to-end throughput;
- 75% lower latency;
- 75% lower power or energy;
- biometric interchangeability;
- that a CPU/GPU/NPU tier becomes sufficient;
- that an ANN/indexed search will return the same identities.

Whether the reduction crosses a RAM/cache/bandwidth/hardware-tier boundary is exactly what the future engineering benchmark is intended to measure.

## 10. Why D1, D2 and D3 exist

The benchmark must not tune its own execution environment from preview measurements of the same target question.

The accepted v0.5 review closed the three provenance/firewall design conditions while explicitly keeping canonical execution inadmissible and construct validity unreviewed.

### D1 — accountable provenance/attestation

For each lock-defining choice, the record must disclose material evidence used and who can attest to its provenance. D1 carries the negative-fact burden when the attesting party influenced evidence creation or framing and remains the completeness backstop.

### D2 — public temporal ordering for genuinely pre-existing external evidence

D2 contributes a bounded, mechanically checkable temporal fact: qualifying external/pre-existing evidence predates an immutable repository-public bound. It does **not** make the whole independence story objective and cannot replace D1.

### D3 — informational relevance, not labels or intent

Whether prior evidence can influence a configuration choice depends on what information it contains, not whether someone called the run a "smoke test", "pilot", "preview" or another label. Informative prior evidence must be disclosed; it cannot silently tune an allegedly untouched prospective lock.

## 11. v0.6 prospective semantic hardening

The v0.5 D1-D3 acceptance is preserved. v0.6 addresses reviewer findings prospectively before any execution-specific lock is frozen.

### N4 — possession is not creation influence

Reading, receiving, possessing or citing a genuinely pre-existing external source does not by itself mean the attester influenced its creation. Producing, commissioning, requesting, specifying, directing or materially framing the evidence does. Ambiguity defaults to D1.

### N5 — narrower use of "structural impossibility"

Only temporal ordering against the immutable repository-public bound is mechanically checkable from repository history. External-origin classification, absence of creation/framing influence and completeness remain provenance/attestation claims. Downstream text must not describe the entire mechanism as objectively established.

### R1/N2 — informational overlap is choice-specific

The earlier global conjunction was too coarse. v0.6 evaluates prior evidence against the **lock-defining choice it can inform**:

- hardware class matters primarily for platform-specific choices;
- backend/BLAS evidence can transfer across hardware classes;
- threading/affinity evidence can transfer across hardware classes;
- measurement-plane, power-meter, synchronization and load-generation evidence can transfer even when vector dimensions/search/hardware differ.

If relevance is uncertain, the rule fails closed to `INFORMATIVE` until an attributable rationale justifies `NOT_INFORMATIVE`.

### N6 — review transport

The next review package must ship exact normative artifacts together with expected Git blob SHA-1 values and reviewer-side recomputation instructions. The goal is both self-contained reviewability and detection of transport divergence.

These v0.6 changes are currently **prospective and awaiting independent review**. They do not authorize execution.

## 12. Measured, structural, synthetic and extrapolated claims

| Statement | Evidence class | Current status |
| --- | --- | --- |
| 512→128 reduces vector coordinates by 75% | Structural arithmetic | Established |
| FP32 payload 2048 B→512 B/template | Structural arithmetic | Established |
| S4N1/S4N2 power near Delta=.01 is below 90% | Synthetic known-truth simulation | Established for frozen generator/procedures |
| 128D gives lower device latency | Target engineering measurement | Not measured |
| 128D gives lower device energy | Target engineering measurement | Not measured |
| 128D crosses a RAM/hardware-tier threshold | Target engineering measurement | Not measured |
| 128D is biometrically non-inferior to raw512 | Protected Study 1B outcome | Not demonstrated / TEST unopened |
| 128D representation geometry is better | Protected exploratory outcome | Not opened |
| Fleet-level savings | Extrapolation from per-device evidence | Not admissible until per-device measurements exist |

## 13. Current state as of 2026-09-15

The exact pre-documentation head used to assemble this snapshot is `beb2f193cfe1f5255b8f4fc1b5dd4c96aa386c2b`.

At that head the five bounded technical workflows were green: CI, Research Assurance, Study 1B Engineering Assurance, Study 1B Non-outcome Preflight and Study 1B Power Design Diagnostic. Workflow success is technical assurance, not semantic/scientific acceptance.

Current gate state:

| Gate | State |
| --- | --- |
| S4N1 | CLOSED_NEGATIVE |
| S4N2 | CLOSED_NEGATIVE |
| S4N3 | NOT_LAUNCHED |
| D1 | CLOSED / accepted history |
| D2 | CLOSED / accepted history |
| D3 | CLOSED / accepted history |
| v0.6 N4/N5/R1-N2 | corrected prospectively; independent review pending |
| v0.6 N6 package rule | adopted for next package |
| Construct-validity review | NOT_REVIEWED |
| Target edge hardware | NOT_BOUND |
| External power meter | NOT_BOUND |
| Off-device load generator | NOT_BOUND |
| Configuration-choice provenance | NOT_MATERIALIZED |
| Execution-specific environment lock | NOT_MATERIALIZED |
| Canonical Phase A execution | BLOCKED |
| Study 1B SCREEN | SEALED |
| Study 1B qualification TEST | SEALED |
| Real route performance | SEALED |
| Representation geometry | SEALED |

## 14. Next admissible gates

1. Independently re-review v0.6 N4, N5 and R1/N2 using the self-contained N6 package.
2. Perform a separate **construct-validity review** of Phase A: do the chosen synthetic workload, fixed-work search, gallery scenarios, metrics and measurement planes answer the intended engineering decision?
3. Only after those reviews, select and document the real target platform, backend, threading, load generator, external power meter and configuration-choice provenance.
4. Freeze a new execution-specific environment lock and execution identity.
5. Run exact-head assurance.
6. Only then may canonical Phase A engineering measurement become admissible.

No step above opens SCREEN, qualification TEST, real route performance or representation geometry.

## 15. Normative references

- `protocol/studies/STUDY1B_MATCHED_COMPRESSION_PREREGISTRATION_2026-08-27.md`
- `protocol/decisions/STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml`
- `protocol/reviews/PR50_CB124244_D2_V05_FOCUSED_REREVIEW_VERDICT_2026-09-10.md`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_V0_2_2026-09-14.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml`
- `protocol/chronicle/STUDY1B_PR50_PREEXECUTION_SEMANTIC_HARDENING_V0_6_OPEN_2026-09-14.yaml`
- `harness-adoption.yaml`

This narrative explains the current programme state. If it conflicts with a frozen normative artifact, the normative artifact wins.
