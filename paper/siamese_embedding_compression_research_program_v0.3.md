# Siamese Embedding Compression Research Program
## Study 1B scientific closure, engineering-value qualification, and pre-execution governance

**Version:** 0.3  
**Date:** 2026-09-15  
**Status:** pre-execution research monograph; no protected Study 1B outcome included  
**Repository programme:** `siamese-embedding-compression-lab`

---

## Executive summary

The research programme began with a deceptively simple proposition: reduce a 512-dimensional biometric embedding to 128 dimensions and determine whether the smaller representation preserves decision-relevant performance while delivering a useful engineering benefit.

That proposition has now separated into two different questions that require two different evidence systems.

The **scientific question** asks whether random128, PCA128 or Siamese128 can be shown non-inferior to raw512 under a frozen biometric verification protocol. Study 1B preregistered the comparison at FMR 0.01 with an absolute FNMR non-inferiority margin of 0.03, dependence-aware uncertainty and a five-seed method-level rule. Before protected qualification outcomes could be opened, the uncertainty procedure itself was subjected to synthetic known-truth power calibration. Two prospectively frozen procedures, S4N1 and S4N2, both failed the preregistered 90% power target near the acceptable boundary `Delta_FNMR=0.01`. They remain closed negative. No S4N3 has been launched, and Study 1B SCREEN and qualification TEST remain sealed.

The **engineering question** asks what a structural reduction from 512 to 128 coordinates actually buys in a distributed edge 1:N system: RAM feasibility, throughput, latency, queueing, energy, battery implications and possibly a lower hardware tier. Some consequences are exact without measurement: at equal datatype and encoding, vector payload falls by 75%, as does the number of coordinate contributions in a direct dense dot-product numerator. Those facts do not imply 4× end-to-end speed or 75% lower power. Such claims require a prospectively frozen target-workload benchmark.

That engineering benchmark has itself become an experiment in evidence governance. A benchmark can bias its own result if hardware, BLAS/backend, thread count, affinity, power mode or measurement method are selected after seeing preview measurements of the same target workload. D1, D2 and D3 were therefore introduced to record provenance, bound genuinely pre-existing external evidence in time, and classify prior evidence by informational relevance rather than by labels such as "smoke test" or "pilot". Those conditions were accepted under v0.5, while canonical execution and construct validity remained explicitly unapproved.

The current v0.6 cycle hardens three residual semantic issues before any real execution lock is frozen: possession versus influence over evidence creation (N4), the narrow objective scope of public temporal ordering (N5), and choice-specific transfer of prior evidence across hardware classes (R1/N2). It also adopts a self-contained review-package rule (N6). These changes are prospective and still require independent review.

The programme is therefore **not waiting to run a benchmark**. It is making sure that when the benchmark is finally run, the result can be interpreted without hidden tuning, circular evidence or retrospective thresholding.

---

## 1. Research question and programme evolution

### 1.1 Core question

The bounded programme question is:

> Can a learned projection reduce biometric embedding cost while preserving decision-relevant verification or identification performance relative to the uncompressed representation and matched compression controls?

This question has multiple layers. A complete positive answer would require more than a good loss curve or a smaller vector:

- the training mechanism must really update the projection;
- the compressed representation must preserve the chosen operating point;
- supervision must be compared against ordinary compression controls;
- threshold selection must transfer credibly;
- engineering cost must improve under measured workloads;
- the evidence must support the exact claim being made.

A failed gate is a useful result because it narrows what can honestly be claimed.

### 1.2 Study 0

Study 0 used a frozen ImageNet ResNet-18 source representation on LFW. It compared:

- raw512;
- random128;
- PCA128;
- a supervised linear Siamese128 projection.

A methodological audit found that the original pair-level bootstrap did not respect repeated identities. The corrected subject-level reanalysis retained the negative conclusion: none of the 128D routes demonstrated non-inferiority to raw512 under the frozen all-seeds rule at empirical FMR 0.01 with `Delta_FNMR` margin 0.03.

Two lessons mattered:

1. uncertainty must reflect the dependence structure actually induced by repeated identities/templates;
2. a negative result on an unsuitable source representation should not be over-generalized into a claim about compression or metric learning as a whole.

### 1.3 Study 1A and Study 1B

Study 1 changes the representation substrate to a face-specific model.

Study 1B consumes an exact frozen AdaFace R100/IR101 512D representation:

- released training corpus: WebFace12M;
- AdaFace code commit: `c60eaa786a42c03444f3df7096dbaf9d57ae010d`;
- checkpoint SHA-256: `0e7a3238d2a50f3fe3860782534928ac7cb2598977cf897f6869fd5ac2493fd0`;
- final output: L2-normalized 512D embedding;
- changed extraction semantics inside Study 1B are prohibited.

The comparison remains matched: raw512, random128, PCA128 and Siamese128.

---

## 2. Scientific objective, engineering objective, and evidence firewall

### 2.1 Scientific objective

For candidate route `m` and target FMR `alpha`:

`Delta_FNMR(m, alpha) = FNMR_m(alpha) - FNMR_raw512(alpha)`.

The primary Study 1B question is whether the candidate degradation remains below a preregistered margin under a frozen one-sided uncertainty procedure.

Frozen core values:

| Parameter | Frozen value |
| --- | --- |
| Target FMR | 0.01 |
| NI margin `Delta_FNMR` | 0.03 |
| One-sided UCB | 97.5% |
| Stage B route seeds | 11, 29, 47, 71, 101 |
| Bootstrap replicates | 10,000 |
| Method rule | every preregistered seed must pass |

The allowed wording is bounded: "non-inferiority demonstrated on this frozen Study 1B protocol". Failure is `NOT_DEMONSTRATED`, not universal inferiority.

### 2.2 Engineering objective

The engineering question is different:

> Given a fixed search problem, what RAM, compute, latency, throughput, queueing, energy and hardware-tier consequences follow from using 128D rather than 512D?

The engineering benchmark uses synthetic vectors and fixed-work exact dense top-1 search so the workload does not depend on biometric threshold behavior.

### 2.3 Firewall

Engineering evidence cannot establish biometric acceptability.

Biometric evidence cannot be opened to select or tune the engineering configuration.

This separation prevents a convenient engineering result from becoming a surrogate biometric claim, and prevents protected scientific outcomes from leaking into benchmark design.

---

## 3. Data sources and roles

### 3.1 LFW View 1 as the bounded Study 1B substrate

Study 1B uses the LFW View 1 development/test identity boundary. The choice is intentionally modest: public, identity-disjoint and reproducible, but not industrial biometric qualification.

The deterministic development-side role split is:

| Role | Identities | Purpose |
| --- | ---: | --- |
| TRAIN | 2,827 | fit learned/unsupervised transforms |
| VALIDATION | 606 | checkpoint/selection development |
| SCREEN | 605 | bounded non-claim-bearing Stage A |
| TEST | 1,711 | untouched qualification population |

All captures of an identity stay in one role. Cross-role duplicate/near-duplicate evidence is audited before outcomes.

### 3.2 Frozen pair-graph targets

| Role | Genuine pairs | Impostor pairs |
| --- | ---: | ---: |
| TRAIN | 20,000 | 20,000 |
| VALIDATION | 5,000 | 20,000 |
| SCREEN | 5,000 | 50,000 |
| TEST | 10,000 | 100,000 |

Pair graphs are generated from identity/capture metadata before route outcomes, canonicalized, de-duplicated and shared across routes.

### 3.3 Evidence classes

| Evidence class | Examples | Can affect biometric claim? | Current state |
| --- | --- | --- | --- |
| Protected scientific outcomes | SCREEN/TEST route scores, FNMR/FMR | Yes | sealed |
| Synthetic calibration | S4 known-truth simulations | Only procedure validity/power | closed negative on power |
| Engineering target workload | latency, throughput, joules/id | No | not yet executed |
| Structural analytic | byte counts, dimensions | No | established |
| Extrapolated system/fleet | fleet RAM/energy/cost | No, and only after measured base | not yet admissible |

---

## 4. Models and algorithms

### 4.1 raw512

The reference is the frozen 512D AdaFace embedding. It has no projection seed. Its serialized embedding manifest/hash is the source reference.

### 4.2 random128

For each seed:

- matrix shape 512×128;
- entries independently `N(0,1/128)`;
- no orthonormalization;
- transform `xR`;
- L2-normalize;
- serialize matrix, seed and hash.

This controls dimensional reduction without data-driven learning.

### 4.3 PCA128

For each seed:

- fit on unique TRAIN captures only;
- center on TRAIN mean;
- `n_components=128`;
- randomized SVD;
- no whitening;
- random state = route seed;
- L2-normalize transformed output.

The randomized-SVD seed is intentionally part of the method-level rule.

### 4.4 Siamese128

Shared affine projection:

`z = L2_normalize(xW + b)`.

Training uses contrastive loss:

- genuine: `0.5 d^2`;
- impostor: `0.5 max(0, 1-d)^2`.

Frozen training semantics include:

- Adam `beta1=0.9`, `beta2=0.999`, `epsilon=1e-8`;
- learning rate 0.002;
- weight decay 0.0001 on W;
- batch size 128;
- max epochs 35;
- early-stop patience 6;
- minimum validation-loss improvement 0.0001;
- margin 1.0;
- checkpoint chosen by lowest qualifying VALIDATION contrastive loss.

The model seed controls initialization and minibatch order, not pair-graph construction.

---

## 5. Metrics and decision semantics

The programme distinguishes operating-point and threshold-aggregated metrics.

- **FMR/FAR:** false matches among impostor attempts at a threshold.
- **FNMR/FRR:** false non-matches among genuine attempts.
- **TAR/TMR:** genuine acceptance; under matched semantics `FNMR = 1 - TAR`.
- **ROC/DET:** diagnostic trade-off curves.
- **EER:** descriptive equal-error point.
- **AUC:** descriptive ranking summary.

ROC/DET/EER/AUC cannot post hoc replace a failed frozen operating-point criterion.

For Study 1B, the primary representation endpoint is equal-FMR comparison at 0.01. Operational threshold transfer from VALIDATION to TEST is secondary and descriptive.

---

## 6. Dependence-aware uncertainty

Verification pairs are linked by repeated identities. Treating pair rows as i.i.d. can understate uncertainty.

The frozen identity-aware procedure:

1. resamples TEST identity slots with replacement;
2. gives genuine edge `(i,i)` multiplicity `m_i`;
3. gives impostor edge `(i,j)` multiplicity `m_i*m_j`;
4. never synthesizes an edge absent from the frozen graph;
5. uses the same identity draw for raw and candidate;
6. runs 10,000 Stage B replicates;
7. fails closed on excessive degeneracy.

Known-truth coverage simulation is required before TEST outcome release. Coverage and power are separate questions: a conservative interval can cover truth very well and still have insufficient power to demonstrate a practically acceptable effect.

---

## 7. S4 known-truth calibration

### 7.1 Purpose

S4 does not estimate real face-recognition performance. It asks:

> If the true candidate degradation were known in a controlled synthetic world, how often would the complete frozen decision procedure demonstrate non-inferiority?

The power target is 0.90 at declared acceptable truths, including `Delta_FNMR=0.01`.

### 7.2 S4N1

At `Delta=0.01`:

| Selector | Passes / 4000 | Power |
| --- | ---: | ---: |
| FIXED | 3462 | 0.8655 |
| VALIDATION_BEST (prospectively preferred) | 3476 | 0.8690 |
| MEDIAN | 3478 | 0.8695 |

### 7.3 S4N2 DAGJK20

S4N2 changed the uncertainty estimator to a deterministic 20-group delete-a-group jackknife. Its one-sided multiplier is Student-t `t(0.975,19)=2.0930240544`, about 6.79% larger than the normal 0.975 quantile.

At `Delta=0.01`:

| Selector | Passes / 4000 | Power |
| --- | ---: | ---: |
| FIXED | 3388 | 0.8470 |
| VALIDATION_BEST (prospectively preferred) | 3396 | 0.8490 |
| MEDIAN | 3414 | 0.8535 |

### 7.4 Interpretation

Both procedures were evaluated on the **same deterministic synthetic known-truth population**. The independent evidence-line count is therefore one; two procedures were compared.

The 95% exact Clopper-Pearson upper endpoint for every `Delta=.01` power cell remains below 0.90. Monte-Carlo uncertainty does not rescue the frozen power gate.

Correct conclusion:

> The frozen procedures do not attain the preregistered 90% probability of demonstrating non-inferiority near `Delta_FNMR=0.01` under the synthetic generator.

Incorrect conclusions include:

- "128D is inferior";
- "Siamese compression fails in general";
- "the synthetic generator is validated for reality";
- "there were two independent replications";
- "zero degeneracy means zero biometric errors".

### 7.5 Why stop at S4N2

A third estimator is not automatically informative. Repeatedly inventing new estimators after observing failures creates post-hoc method shopping. S4N3 therefore remains unlaunched unless independently motivated by a new prospective methodological question.

---

## 8. Decision risk and operational policy

At `Delta=.01`, synthetic non-demonstration probability is `1-power`. For the prospectively preferred selector it is about 13.1% in S4N1 and 15.1% in S4N2, compared with the 10% target implied by 90% power.

These are local study-level decision-procedure probabilities under the generator. They are not expected harm probabilities and cannot be averaged over an acceptable state without a prospective distribution over effects.

Working policy:

- PASS: promote to a controlled next engineering/qualification stage;
- non-demonstration: retain raw512 by default;
- preserve rollback, raw512 compatibility and shadow/dual-run if feasible;
- do not reinterpret non-demonstration as candidate inferiority.

---

## 9. Engineering value: the structural envelope

### 9.1 Exact payload arithmetic

At constant datatype/encoding:

| Representation | FP32 | FP16 | INT8 |
| --- | ---: | ---: | ---: |
| 512D | 2,048 B | 1,024 B | 512 B |
| 128D | 512 B | 256 B | 128 B |
| Reduction | 75% | 75% | 75% |

For direct dense dot/cosine numerator computation, coordinate contributions also drop from 512 to 128, a 75% reduction.

### 9.2 What this does not prove

The structural ratio does not prove:

- 4× throughput;
- 75% lower latency;
- 75% lower energy;
- a 4× smaller whole process;
- a lower hardware tier;
- equivalent identification results under quantization/indexing.

Extractor cost is also unchanged by a post-extractor projection.

### 9.3 Why the hardware threshold matters

The highest engineering value may arise not from a proportional latency change but from a **regime change**: a 512D gallery might exceed RAM/cache/accelerator capacity while the 128D gallery fits. That can alter architecture, bill of materials, thermal envelope or replication strategy discontinuously.

This is a hypothesis for measurement, not a result.

---

## 10. Jungle Championship engineering scenario

The benchmark models distributed autonomous edge units at entrances and internal zones, with local 1:N matching, offline operation and bursty traffic. The benchmark deliberately avoids claiming that scenario cardinalities are observed event facts.

### 10.1 Phase A search semantics

- exact dense dot-product top-1;
- L2-normalized synthetic vectors;
- FP32;
- CPU;
- no threshold gating;
- no candidate pruning;
- no ANN/index;
- fixed work per query.

The 512D and 128D arms differ only in representation dimension on a given hardware tier.

### 10.2 Gallery scenarios

`G0` is a small working-set control:
- 10,000 blacklist identities;
- 3 templates/identity.

`G2` is the primary large-gallery sensitivity:
- 500,000 whitelist identities;
- 10,000 blacklist identities;
- 3 templates/identity;
- 1.53 million templates.

G2 vector payload:

- 512D FP32: 3,133,440,000 bytes;
- 128D FP32: 783,360,000 bytes.

### 10.3 Measurements

Prospectively specified outputs include:

- process RSS and RAM residency;
- throughput;
- per-query p50/p95/p99 latency where sample support allows;
- queue depth/recovery;
- throttling/temperature where observable;
- external device-level power;
- total joules per identification;
- burst energy;
- conditioned battery-autonomy calculations.

External power measurement is required for a strong energy claim. On-chip telemetry is supporting diagnostic evidence only.

---

## 11. Provenance problem: a benchmark can tune itself

Suppose an exploratory run shows that one BLAS backend makes 128D look particularly favorable. If that backend is then silently chosen for the "official" comparison, the official benchmark is no longer prospectively configured.

The same problem can arise with:

- device model;
- RAM tier;
- backend/BLAS;
- thread count/affinity;
- frequency/boost policy;
- load generator;
- wattmeter/measurement plane;
- battery assumptions.

The programme therefore treats configuration selection itself as an evidence-governed decision.

---

## 12. D1, D2 and D3

### 12.1 D1 — accountable provenance

Each lock-defining choice needs:

- selected value;
- decision authority/source;
- source reference;
- evidence timestamp;
- accountable attester;
- attestation statement;
- disclosure of materially informative prior evidence;
- rationale.

D1 is the completeness backstop and is mandatory when the attester influenced evidence creation or framing.

### 12.2 D2 — bounded public temporal ordering

D2 exists for genuinely pre-existing external evidence. The accepted v0.5 mechanism uses the immutable repository root as a conservative public-information bound.

The key logical distinction is:

- repository history can mechanically establish a timestamp ordering;
- it cannot mechanically establish the full mental/causal history of who knew what.

D2 therefore cannot replace D1.

### 12.3 D3 — information, not labels

Prior evidence is classified by whether its observable content could influence a lock-defining choice. Labels and declared intent are not classifier inputs.

Calling a run "pilot", "smoke", "capacity check" or "diagnostic" does not make its information disappear.

---

## 13. v0.5 acceptance and its boundary

The independent focused v0.5 re-review recorded:

- `VERDICT: ACCEPT`;
- `D2_CLOSED: yes`;
- `D1_D2_RESPONSIBILITY_SPLIT_ACCEPTED: yes`;
- `ROOT_PUBLIC_INFORMATION_BOUND_ACCEPTED: yes`;
- `PRIOR_DESIGN_CONDITIONS_SATISFIED: yes`;
- `CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no`;
- `CONSTRUCT_VALIDITY_REVIEWED: no`;
- `R1_N2_PORTABLE_CHOICE_OVERLAP_CLOSED: no`.

This is essential: acceptance of provenance/firewall design was **not** acceptance of Phase A construct validity or permission to execute.

The reviewer also recorded three nonblocking items to close before execution-specific lock freeze: N4, N5 and N6, while R1/N2 remained open.

---

## 14. v0.6 prospective hardening

### 14.1 N4 — possession versus influence

The prior language risked making D2 unusable because simply receiving or reviewing an external source could force D1.

v0.6 corrects this:

- mere receipt, possession, citation or review is not creation/framing influence;
- production, commissioning, requesting, specifying, directing or materially framing evidence requires D1;
- ambiguity defaults to D1;
- D1 completeness attestation remains mandatory.

### 14.2 N5 — what is mechanically checkable

The objective component is only:

> evidence timestamp is strictly earlier than the immutable repository-public bound.

The following remain provenance/attestation claims:

- source is genuinely external/pre-existing;
- attester did not influence its creation/framing;
- disclosure is complete.

"Structural impossibility" must therefore not be cited as though the whole independence mechanism were objective.

### 14.3 R1/N2 — choice-specific information transfer

A single global conjunction of same dimension + same search family + same hardware class under-classifies portable knowledge.

v0.6 classifies evidence per choice family:

| Choice family | Can cross hardware classes? | Example |
| --- | --- | --- |
| Platform-specific | sometimes, with rationale | device/RAM/power mode |
| Search runtime | yes | BLAS/backend/kernel evidence |
| Concurrency | yes | thread count, affinity, oversubscription |
| Measurement method | yes | wattmeter placement, sampling, synchronization, load generation |

If uncertain, evidence is treated as informative until an attributable rationale demonstrates otherwise.

### 14.4 N6 — self-contained review transport

Future focused review packages must contain the exact normative artifacts, not only author summaries, plus expected Git blob SHA-1 values. The reviewer recomputes Git blob identity locally using:

`SHA1("blob " + byte_length + NUL + content)`.

This simultaneously improves inspectability and catches transport divergence.

---

## 15. Evidence classification matrix

| Claim | Classification | Status on 2026-09-15 | Permitted wording |
| --- | --- | --- | --- |
| 512→128 coordinate reduction | structural | established | exactly 75% fewer coordinates |
| Vector byte reduction at fixed precision | structural | established | exactly 75% vector payload reduction |
| S4 power at Delta=.01 | synthetic measured | established under generator | below frozen 90% target |
| S4 real-world validity | unsupported | not established | no claim |
| 128D RAM feasibility on target edge device | engineering measured | not measured | no claim |
| 128D latency/throughput benefit | engineering measured | not measured | no claim |
| 128D energy/battery benefit | engineering measured | not measured | no claim |
| Fleet savings | extrapolated | blocked pending measured base | scenario only |
| Biometric NI vs raw512 | protected scientific outcome | TEST sealed | not demonstrated |
| Siamese superiority vs PCA/random | protected scientific outcome | TEST sealed | not demonstrated |
| Representation geometry | protected exploration | unopened | no claim |
| Production readiness | broader qualification | outside current evidence | no claim |

---

## 16. Current state and execution gate

This monograph was assembled from the repository state whose pre-documentation head was:

`beb2f193cfe1f5255b8f4fc1b5dd4c96aa386c2b`.

At that head all five bounded technical workflows were green:

- CI;
- Research Assurance;
- Study 1B Engineering Assurance;
- Study 1B Non-outcome Preflight;
- Study 1B Power Design Diagnostic.

Those checks are technical assurance, not a semantic/scientific verdict.

### 16.1 Scientific boundary

Still sealed:

- Stage A SCREEN outcomes;
- qualification TEST outcomes;
- real raw512/random128/PCA128/Siamese128 route performance;
- representation geometry;
- amendment activation.

Closed negative:

- S4N1;
- S4N2.

Not launched:

- S4N3.

### 16.2 Engineering execution boundary

Not yet materialized:

- target edge hardware;
- external power meter;
- off-device load generator;
- configuration-choice provenance;
- provenance attestation;
- generator code identity;
- execution-specific environment lock.

Still pending:

- independent re-review of v0.6 semantic hardening;
- construct-validity review.

Therefore:

> **Canonical Phase A execution is blocked.**

---

## 17. What happens next

The admissible sequence is intentionally strict.

### Gate 1 — v0.6 independent re-review

Review only the prospective N4/N5/R1-N2 semantic hardening and N6 review transport. Do not reinterpret the accepted v0.5 history.

### Gate 2 — construct-validity review

Ask whether Phase A actually measures the intended engineering construct:

- Does synthetic exact-dense top-1 represent the decision we care about?
- Are G0/G2 the right sensitivity points?
- Are the selected latency, throughput, RAM and energy planes sufficient?
- Does fixed work remove unwanted biometric coupling without destroying engineering relevance?
- Which conclusions can and cannot transfer to indexed/ANN systems, quantization or real gallery distributions?

This is logically distinct from provenance correctness.

### Gate 3 — execution-specific platform selection

Only after Gates 1 and 2:

- select device/platform;
- select backend/BLAS;
- bind thread count/affinity;
- bind power mode;
- bind off-device load generator;
- bind external wattmeter and sampling/synchronization method;
- disclose all prior informative evidence per choice.

### Gate 4 — freeze the environment lock

The fully materialized lock must be committed before canonical execution. Any material change creates a new execution identity.

### Gate 5 — exact-head assurance

All bounded workflows must be green on the exact frozen head.

### Gate 6 — Phase A engineering measurement

Only then can target-workload engineering results be opened.

None of these gates opens protected Study 1B biometric outcomes.

---

## 18. Methodological lessons accumulated so far

### 18.1 Coverage and power are not substitutes

A procedure can have high coverage and still be too conservative to demonstrate a useful effect with sufficient probability.

### 18.2 Negative studies are assets when preserved

S4N1/S4N2 are not failed work to hide. They constrain the next legitimate step and reduce method-shopping freedom.

### 18.3 Prospective configuration is part of experimental validity

Hardware and software runtime choices are not neutral implementation details when they can change the measured contrast.

### 18.4 "I did not intend to tune" is not a firewall

The relevant question is whether prior information could inform the choice, not what the run was called.

### 18.5 Reproducibility is more than code

A replayable result requires data/generator identity, execution environment, choice provenance, measurement plane, raw samples, failure logs and the semantic contract governing interpretation.

### 18.6 Scientific and engineering claims can share a programme without sharing authority

The same 512→128 intervention may be studied scientifically and operationally, but the evidence routes must remain separated until a predeclared bridge is justified.

---

## 19. Source-of-truth map

The main normative sources for this version are:

1. `protocol/studies/STUDY1B_MATCHED_COMPRESSION_PREREGISTRATION_2026-08-27.md`
2. `protocol/decisions/STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml`
3. `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml`
4. `protocol/reviews/PR50_CB124244_D2_V05_FOCUSED_REREVIEW_VERDICT_2026-09-10.md`
5. `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_V0_2_2026-09-14.yaml`
6. `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml`
7. `protocol/chronicle/STUDY1B_PR50_PREEXECUTION_SEMANTIC_HARDENING_V0_6_OPEN_2026-09-14.yaml`
8. `harness-adoption.yaml`

This monograph is explanatory. Frozen normative artifacts and accepted independent reviews take precedence over its prose.

---

## 20. Compact current-state record

**Scientific:** Study 1B protected outcomes remain unopened. S4N1/S4N2 are closed negative on power near `Delta=.01`; S4N3 is not launched.

**Engineering:** structural 512→128 savings are established analytically; target-device latency/throughput/RAM/energy benefits are not yet measured.

**Governance:** D1/D2/D3 accepted under v0.5. v0.6 prospectively hardens N4/N5/R1-N2 and review transport N6; independent review remains pending.

**Execution:** Phase A remains blocked until construct validity is reviewed, the real platform and measurement setup are bound, provenance is materialized, the environment lock is frozen and exact-head assurance is green.

**Next scientific discipline:** do not open SCREEN/TEST to rescue engineering uncertainty, do not launch S4N3 without a new prospective rationale, and do not let target-workload previews silently tune the canonical benchmark.
