# Study 1B / PR #50 — new-chat handoff

**Date:** 2026-09-15  
**Repository:** `gharbonnier78/siamese-embedding-compression-lab`  
**Pull request:** #50 — `Study 1B: close S4 power calibration and re-review corrected engineering benchmark`  
**Branch:** `agent/study1b-preregistration-20260827`  
**Base:** `main` @ `5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7`  
**Last substantive/documentation head before this handoff file:** `b306f64ec0287cf6c6704507b6fcda12b65e750a`  
**Pinned harness:** `gharbonnier78/scientific-research-harness@3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`

> **First action in a new chat:** fetch PR #50 and use its *current exact head*. This handoff file itself creates a later documentation-only commit, so do not assume `b306f64...` remains the branch head. Before any substantive work, read `AGENTS.md`, `harness-adoption.yaml`, and the pinned `HARNESS.md` at the immutable harness ref above.

---

## 1. What this project is trying to answer

The programme separates two related but non-interchangeable questions.

### Scientific preservation question

Can a face representation be compressed from 512D to 128D while preserving decision-relevant biometric performance under a frozen operating point, a frozen non-inferiority margin, and dependence-aware uncertainty?

### Engineering value question

If 128D is scientifically admissible, or even while scientific admissibility remains unresolved, what deterministic and measured engineering consequences follow from 512D→128D on a real edge 1:N platform: memory, dense-comparison work, latency, throughput, energy, hardware-tier fit, and operational headroom?

The engineering benchmark **must not** redefine, rescue or replace the scientific qualification question.

---

## 2. Non-negotiable scientific / authorization boundaries

Do **not** do any of the following unless a new explicit authorization and prospective protocol says otherwise:

- do **not** open Study 1B SCREEN;
- do **not** open qualification TEST;
- do **not** inspect real `raw512/random128/PCA128/Siamese128` performance;
- do **not** inspect representation geometry on protected real routes;
- do **not** activate an amendment;
- do **not** launch S4N3;
- do **not** silently change the original 5/5 seed rule;
- do **not** change FMR target, NI margin, confidence level, threshold semantics, selector order or frozen calibration gates because an estimator failed;
- do **not** use real outcomes to choose methods;
- do **not** claim ISO/NIST conformity;
- do **not** use a target-workload smoke/pilot/preview/capacity/tuning run to choose hardware, backend, threading or measurement settings before the execution-specific lock is frozen;
- do **not** run canonical Jungle Championship Phase A yet.

Negative results are append-only. Historical accepted reviews are preserved even when later evidence reopens a condition.

---

## 3. Harness obligations

The local project instructions require the following lifecycle:

`Bind → Frame → Execute → Verify → Explain → Chronicle / handoff`.

Always preserve the separation between:

- scientific evidence;
- runtime/engineering telemetry;
- Chronicle decisions;
- pedagogical explanation;
- understanding gates;
- execution authorization.

A green workflow is technical assurance only. It cannot release a scientific gate or establish construct validity.

The current `harness-adoption.yaml` pins the harness ref and binds execution metadata to the prospective v0.6 engineering environment lock.

Replay command declared in the manifest:

```bash
PYTHONPATH=src python -m unittest \
  tests.test_harness_adoption \
  tests.test_scientific_harness \
  tests.test_coverage_execution \
  tests.test_coverage_execution_vectorized \
  tests.test_study1b_engineering_benchmark_contract \
  tests.test_study1b_engineering_benchmark_contract_v06 -v
```

---

## 4. Study 0 — closed corrected negative

Study 0 used frozen ImageNet ResNet-18 512D representations on LFW and compared:

- `raw512`;
- `random128`;
- `PCA128`;
- a supervised linear `Siamese128` 512→128 projection trained with contrastive loss.

A later audit found that pair-row bootstrap uncertainty understated dependence because identities recur across comparison pairs. Historical scores were preserved and re-analysed with a dependence-aware subject-level procedure.

The corrected Study 0 conclusion remains bounded negative: non-inferiority was not demonstrated for any 128D route in that frozen experiment. It does not prove universal inferiority of 128D, PCA or metric learning.

The detailed historical manuscript remains in `paper/study0_v0.2.3.tex` and the older PDF series remains immutable.

---

## 5. Study 1A — face-specific source representation

Study 1A is intended to qualify the source representation before compression is reconsidered.

Frozen design context:

- method: AdaFace;
- architecture: R100 / `ir_101`;
- output dimension: 512;
- released WebFace12M-trained checkpoint;
- upstream AdaFace commit: `c60eaa786a42c03444f3df7096dbaf9d57ae010d`;
- no face-backbone retraining inside Study 1A;
- official protocols / deterministic preprocessing / provenance are part of Gate A.

Evaluation hierarchy includes LFW, CFP-FP, AgeDB-30, CALFW, CPLFW, and preferably IJB-C as the low-FMR primary endpoint if lawful/replayable access exists. NIST FRTE is external context, not a local replacement dataset.

No new Study 1A scientific outcome has been introduced by the September documentation refresh.

---

## 6. Study 1B frozen scientific constants

Key frozen constants remain:

- FMR target: `0.01`;
- non-inferiority margin: `Δ_FNMR = 0.03`;
- one-sided confidence/UCB level: `0.975`;
- bootstrap replicates: `10,000` where applicable;
- seeds: `[11, 29, 47, 71, 101]`;
- validation graph SHA-256: `fb849558e0b09b0fa7ff301991af010815f0b4ee98ab62faa1c585477f9f8601`;
- TEST graph SHA-256: `08c86ca9a641fc96b74014ae1974f713cd00e558dd98946ac32ff440c4666f85`;
- capture manifest SHA-256: `767f9fe8d1d8466a0e722f826b26875a0e852f525f7413a9658a307a9639366e`;
- synthetic subject effects: genuine SD `0.08`, impostor SD `0.05`;
- candidate/reference pair-noise correlation: `0.7`;
- Siamese checkpoint selection: validation contrastive loss;
- original 5/5 rule unchanged.

Primary estimand:

```text
Delta_FNMR(m, alpha) = FNMR_m(alpha) - FNMR_raw512(alpha)
```

Real Study 1B SCREEN/TEST outcomes remain sealed.

---

## 7. S4 calibration state

### S4N1

Frozen selector semantics:

- FIXED: seed 11;
- VALIDATION_BEST: argmin unbootstrapped paired equal-FMR validation `Δ_FNMR`;
- VALIDATION_MEDIAN: rank 3/5;
- ties: numeric then seed order;
- missing/non-finite: fail closed;
- preference order: BEST → MEDIAN → FIXED → STOP.

At true `Δ_FNMR=0.01`, synthetic power results on 4,000 datasets:

- FIXED: `0.8655`;
- prospectively preferred VALIDATION_BEST: `0.8690`;
- VALIDATION_MEDIAN: `0.8695`.

Frozen power target: `>= 0.90`.

Result: **S4N1 CLOSED_NEGATIVE**.

### S4N2

S4N2 used DAGJK20:

- 20 deterministic TEST-identity groups;
- delete all edges touching one group;
- recompute threshold and `Δ`;
- jackknife variance;
- one-sided Student-t critical value `t(0.975,19)=2.0930240544083087`.

At true `Δ_FNMR=0.01`:

- FIXED: `0.8470`;
- prospectively preferred VALIDATION_BEST: `0.8490`;
- VALIDATION_MEDIAN: `0.8535`.

Result: **S4N2 CLOSED_NEGATIVE**.

### Shared-population clarification

S4N1 and S4N2 intentionally use the **same deterministic synthetic known-truth population**. They are two uncertainty procedures, not two independent validations of the generator.

The highest 95% Clopper-Pearson upper endpoint among the `Δ=0.01` cells remains below `0.90`, so Monte-Carlo noise does not rescue the gate.

S4N3 remains **NOT LAUNCHED**. The stop rationale is protection against estimator shopping, not accumulation of independent evidence.

Canonical language:

> The frozen Study 1B decision procedures tested so far do not attain the preregistered 90% power objective at the acceptable synthetic truth `Δ_FNMR=0.01`.

---

## 8. Decision-risk / policy interpretation

At `Δ=0.01`, non-demonstration probability is `1 - power`.

For the prospectively preferred selector:

- S4N1 BEST: `13.10%` non-demonstration, `+3.10 pp` above the 10% target;
- S4N2 BEST: `15.10%` non-demonstration, `+5.10 pp` above target.

These are study-level synthetic probabilities, not person-level biometric harm probabilities.

If qualification is not demonstrated, current policy is conservative:

- retain `raw512` by default;
- preserve raw512 compatibility;
- dual/shadow operation if feasible;
- define rollback owner/trigger;
- avoid irreversible migration.

`NOT_DEMONSTRATED` is not equivalent to “candidate inferior”.

---

## 9. Jungle Championship engineering benchmark

The engineering scenario models distributed autonomous edge units around a large event site. It is an engineering stress model, not product qualification data.

Important modeling hygiene:

- identities ≠ templates ≠ passages ≠ observations ≠ camera count;
- do not multiply 50k stadium capacity by camera count to invent gallery size or event count.

One illustrative planning case:

- whitelist identities: 500k;
- blacklist identities: 10k;
- templates per identity: 3;
- full replication: 1.53M templates.

FP32 structural payload:

- 512D: `3.13344 GB/device`;
- 128D: `0.78336 GB/device`;
- saving: `2.35008 GB/device`.

Dense coordinate contributions per observation:

- 512D: `783.36M`;
- 128D: `195.84M`.

Across 50 fully replicated devices:

- 512D: `156.672 GB` aggregate gallery payload;
- 128D: `39.168 GB`;
- saving: `117.504 GB`.

Hybrid 25% local replication:

- 512D: `0.82944 GB/device`;
- 128D: `0.20736 GB/device`.

These are deterministic structural/workload calculations, **not** measured latency or power results.

For equal datatype/encoding, 512D→128D gives:

- dimension ratio `0.25`;
- 75% vector-payload reduction;
- 75% fewer coordinate contributions for direct dense dot/cosine numerator.

Never turn this into an automatic “4× faster”, “75% lower latency” or “75% lower power” claim.

---

## 10. Phase A benchmark semantics

Current Phase A contract is a non-outcome engineering benchmark of exact dense 1:N search.

Canonical design includes:

- exact dense `top_k=1`;
- no threshold gating;
- no ANN/index in Phase A;
- G0 small-working-set control;
- G2 central scenario/sensitivity;
- CPU phase for the current bounded contract;
- FP32 for the canonical initial comparison;
- five process restarts;
- 60 s warm-up;
- 600 s steady measurement windows;
- raw sample retention;
- percentile support rules;
- off-device load generator;
- device-boundary latency separated from client RTT;
- external device-input/wall energy measurement canonical for strong energy claims;
- on-chip telemetry diagnostic only;
- no retrospective operational thresholds.

If a 512D arm does not fit the frozen RAM tier, record `RAM_INFEASIBLE_ON_TIER`. Do not silently use swap, a smaller gallery, another datatype, or move only one arm to another tier.

Quantization and ANN/indexed search are separate later interventions and can change scientific/engineering semantics; they require separate qualification.

---

## 11. D1 / D2 / D3 accepted history

### D1 — accountable provenance / attestation

D1 covers the negative-fact burden for evidence whose creation or framing was influenced by the attesting party, and remains the completeness backstop for lock-defining choices.

### D2 — conservative public temporal bound

The accepted v0.5 design uses repository inception as the mechanically terminal public-information bound:

- root commit: `4b40e7254bff1b88a44d13fb55b366bc7d3fc263`;
- timestamp: `2026-08-07T08:23:56Z`;
- parent count: `0`;
- root artifact: `README.md`.

The root README already published the 512→128 question and future 1:N / gallery indexing / latency direction.

Only the temporal ordering is mechanically checkable. It does not prove what an author privately knew before publication; D1 handles that residual.

### D3 — information rather than declared intent

Prior evidence is classified by whether it can inform a lock-defining choice, not by whether someone calls it “smoke”, “pilot”, “preview”, “capacity” or “tuning”.

### Accepted v0.5 reviewer verdict

Archived artifact:

`protocol/reviews/PR50_CB124244_D2_V05_FOCUSED_REREVIEW_VERDICT_2026-09-10.md`

Accepted fields:

```text
VERDICT: ACCEPT
D2_CLOSED: yes
D1_D2_RESPONSIBILITY_SPLIT_ACCEPTED: yes
ROOT_PUBLIC_INFORMATION_BOUND_ACCEPTED: yes
PRIOR_DESIGN_CONDITIONS_SATISFIED: yes
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
CONSTRUCT_VALIDITY_REVIEWED: no
R1_N2_PORTABLE_CHOICE_OVERLAP_CLOSED: no
```

The reviewer explicitly praised the fact that an earlier accepted D2 closure was reopened when repository-side audit falsified its load-bearing anchor. Preserve that history; do not rewrite the old verdict.

---

## 12. v0.6 semantic hardening — current active design work

Current environment lock:

`protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml`

Current addendum:

`protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_V0_2_2026-09-14.yaml`

v0.6 addresses three pre-execution semantic findings and one review-process finding.

### N4 — possession vs influence

Corrected prospectively:

- mere receipt, possession, citation or review of genuinely pre-existing external evidence does not by itself mean the attester influenced its creation;
- production, commissioning, requesting, specifying, directing or materially framing evidence requires D1;
- ambiguity defaults to D1 / potentially informative.

Status: `CORRECTED_PROSPECTIVELY_AWAITING_INDEPENDENT_REVIEW`.

### N5 — scope of “structural impossibility”

Corrected prospectively:

- only temporal ordering against the immutable repository-root bound is mechanically checkable;
- source origin and absence of creation/framing influence are provenance/attestation claims;
- downstream readers must not cite “structural impossibility” as though the whole mechanism were objective.

Status: `CORRECTED_PROSPECTIVELY_AWAITING_INDEPENDENT_REVIEW`.

### R1/N2 — portable-choice informational overlap

Corrected prospectively by moving from one global conjunction to **choice-specific informational overlap**.

- platform-specific choices may require comparable hardware class;
- backend/BLAS evidence can remain informative across hardware classes;
- threading/affinity evidence can transfer across materially comparable execution models;
- measurement-method evidence can transfer across hardware, dimensions and search families;
- uncertainty defaults to informative;
- `NOT_INFORMATIVE` requires attributable rationale.

Status: `CORRECTED_PROSPECTIVELY_AWAITING_INDEPENDENT_REVIEW`.

### N6 — review package transport

Adopted process rule:

Future focused review packages must ship the **exact normative artifacts themselves** plus their expected Git blob SHA-1 values. The reviewer must be able to recompute:

```text
SHA1("blob " + byte_length + NUL + content)
```

locally. This preserves both inspectability and bytewise correspondence to repository objects.

Status: `PROCESS_RULE_ADOPTED_FOR_NEXT_PACKAGE`.

---

## 13. Current execution gate

Canonical Phase A is still **NOT ADMISSIBLE**.

Still not materialized:

- target edge hardware;
- external power meter;
- off-device load generator;
- complete configuration-choice provenance;
- provenance attestation;
- exact synthetic generator code identity;
- execution-specific materialized environment lock;
- accepted v0.6 semantic re-review;
- construct-validity review.

Independent execution blockers remain:

- `PLATFORM_AND_MEASUREMENT_ENVIRONMENT_NOT_MATERIALIZED`;
- `CONFIGURATION_CHOICE_PROVENANCE_NOT_MATERIALIZED`.

Do not substitute a GitHub-hosted runner for the target edge platform.

---

## 14. Human-readable documentation synchronized on 2026-09-15

The repository now contains:

- `paper/study1_protocol_v0.4-preexecution.md` — current narrative supplement;
- `paper/siamese_embedding_compression_research_program_v0.3.tex` — current monograph source;
- `paper/main.tex` — build entrypoint now points to the v0.3 monograph;
- `protocol/chronicle/STUDY1B_HUMAN_READABLE_DOCUMENTATION_SYNC_V0_3_2026-09-15.yaml` — `CHRON-20260915-049`.

The v0.3 PDF was rendered and visually/preflight checked outside the GitHub text connector:

- target file name: `siamese_embedding_compression_research_program_v0.3.pdf`;
- SHA-256: `152afa0ba16d8dd5eb66865142e4b82419046ebf1b25eabc1cedc83521059270`;
- source SHA-256: `c6a10007dda0c3f9442dcbbf3fdbc15708470c9beb56fdbd25a0a9ec9c3b4493`;
- narrative Markdown SHA-256: `36c1a5ab80f6f3b08f73a19fef6b56782eb4e3f5d24defe96d76706699f7e901`.

**Important:** the current GitHub connector can write UTF-8 text files but not arbitrary binary PDF bytes. Therefore the v0.3 PDF binary itself is not yet committed under `output/pdf/`; its source, target name, hash and publication status are archived here and in `CHRON-20260915-049`. Existing v0.2 / v0.2.1 PDFs remain historical and must not be overwritten.

---

## 15. Assurance state before this handoff commit

On exact head `b306f64ec0287cf6c6704507b6fcda12b65e750a`, all five bounded workflows completed successfully:

- CI — success;
- Research assurance — success;
- Study 1B Engineering Assurance — success;
- Study 1B Non-outcome Preflight — success;
- Study 1B Power Design Diagnostic — success.

This handoff file creates a later documentation-only head, so the workflows will rerun. In a new chat, verify the exact current head and its workflow state before publishing any immutable review binding.

---

## 16. Key Chronicle sequence for orientation

Relevant recent entries:

- `CHRON-20260910-045` — reviewer ACCEPT on old D2 closure archived, then D2 reopened by repository anchor audit;
- `CHRON-20260910-046` — root-bound v0.5 re-review cycle opened;
- `CHRON-20260914-047` — applicable v0.5 ACCEPT archived; D2 closed correctly on root bound + D1/D2 split;
- `CHRON-20260914-048` — prospective v0.6 pre-execution semantic hardening opened for N4/N5/R1-N2; N6 adopted;
- `CHRON-20260915-049` — human-readable documentation synchronized; no scientific or execution gate changed.

The Scientific Chronicle is append-only. Do not rewrite these entries to make the history look cleaner.

---

## 17. Exact next admissible action

The next chat should **not** start hardware benchmarking and should **not** open protected outcomes.

Proceed in this order:

1. Fetch PR #50 and identify the current exact head after this handoff commit.
2. Load `AGENTS.md`, `harness-adoption.yaml`, and the pinned harness `HARNESS.md` at `3b109adc...`.
3. Verify the five bounded workflows on that exact head.
4. If all are green, publish an immutable PR review binding for the exact current head.
5. Build a **self-contained N6-compliant focused v0.6 re-review package** that includes the exact normative repository artifacts, not summaries only.
6. For each shipped normative file, include expected Git blob SHA-1 and reviewer instructions to recompute Git object identity locally.
7. Include the focused v0.6 tests and enough material for the reviewer to execute them without repository access.
8. Include the relevant CI/assurance evidence, clearly labelled technical assurance rather than semantic/scientific acceptance.
9. Ask the reviewer specifically to decide whether N4, N5 and R1/N2 are closed. N6 is a package-process condition and should be demonstrably satisfied by the package itself.
10. Keep `CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE = no` and `CONSTRUCT_VALIDITY_REVIEWED = no` unless a separate review changes those fields.
11. If v0.6 is accepted, perform a **separate construct-validity review** of Phase A before choosing/finalizing the real hardware platform.
12. Only after construct-validity acceptance should the project materialize target hardware, external power meter, off-device load generator, configuration-choice provenance/attestation and exact synthetic generator identity.
13. Freeze a new execution-specific environment lock, run bounded assurance on that exact head, and obtain any required execution review.
14. Only then may canonical Phase A engineering execution become eligible.
15. None of these steps opens protected Study 1B SCREEN/TEST/geometry.

---

## 18. What the construct-validity review should challenge

Do not confuse provenance/firewall correctness with experimental usefulness.

The later construct-validity reviewer should ask at least:

- Does exact dense top-1 Phase A measure the engineering question we actually care about, or only a kernel microbenchmark?
- Are G0 and G2 sufficient to identify cache/memory-regime transitions?
- Are latency, throughput, RAM residency and external energy the right primary engineering outcomes?
- Is the off-device load generator design sufficient to isolate DUT work without creating unrealistic transport behavior?
- Does `joules/identification` need total and idle-subtracted forms?
- Are warm-up and 600 s windows sufficient to expose thermal/frequency-state behavior on the eventual edge device?
- Is the benchmark decision-relevant for choosing 128D when biometric non-inferiority is still not demonstrated?
- What claims may legitimately be extrapolated from one device tier to a fleet or battery policy?
- What additional intervention would ANN/indexed search introduce, and why must it remain outside Phase A?

This is the next major epistemic question after v0.6 semantics are independently accepted.

---

## 19. Files to read first in a new chat

Minimum navigation set:

1. `AGENTS.md`
2. `harness-adoption.yaml`
3. pinned `scientific-research-harness/HARNESS.md` at `3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`
4. `paper/study1_protocol_v0.4-preexecution.md`
5. `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml`
6. `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_V0_2_2026-09-14.yaml`
7. `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml`
8. `protocol/reviews/PR50_CB124244_D2_V05_FOCUSED_REREVIEW_VERDICT_2026-09-10.md`
9. `protocol/chronicle/STUDY1B_PR50_PREEXECUTION_SEMANTIC_HARDENING_V0_6_OPEN_2026-09-14.yaml`
10. `protocol/chronicle/STUDY1B_HUMAN_READABLE_DOCUMENTATION_SYNC_V0_3_2026-09-15.yaml`
11. `tests/test_study1b_engineering_benchmark_contract.py`
12. `tests/test_study1b_engineering_benchmark_contract_v06.py`
13. this handoff file.

For S4 details also read:

- `protocol/decisions/STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml`;
- archived S4N1 and S4N2 Chronicle result artifacts.

---

## 20. Current status in one line

**Study 0 closed negative; Study 1B protected outcomes sealed; S4N1/S4N2 closed negative; D1/D2/D3 accepted; v0.6 N4/N5/R1-N2 prospectively corrected and awaiting independent review; N6 packaging rule adopted; human-readable docs synchronized; Phase A still blocked; construct validity still unreviewed.**
