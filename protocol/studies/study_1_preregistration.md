# Study 1 — Preregistration and pre-execution review checklist

Status: `DRAFT_PREREGISTRATION_REVIEW_REQUIRED`

This document is design-only. It does not authorize access to qualification outcomes or any
outcome-bearing Study 1 run. Study 0 remains closed and is not overwritten by Study 1.

Pinned methodological dependency: `scientific-research-harness` commit
`1cead5808c126fd38e7505c27502fb3e7671c69a` through `harness-adoption.yaml`.

## Research sequence

Study 1 is deliberately split into two logical gates.

**Study 1A — qualify the raw face-specific 512D representation.**

The first scientific question is not whether compression works. It is whether the source
representation is a credible modern face-verification substrate. A weak or incorrectly
implemented backbone would confound any later compression result.

**Study 1B — compare 512D with matched 128D routes.**

Only after Study 1A passes may the programme compare raw 512D, Gaussian random projection
128D, PCA 128D and supervised Siamese/metric-learning 128D.

A Study 1A failure means `STOP` and diagnose the backbone/pipeline. It must not be rescued by
running compression anyway.

## 1. Backbone, weights and provenance

- [ ] Select one exact face-specific 512D backbone before outcome-bearing execution.
- [ ] Pin architecture, weights, source, checksum and licence.
- [ ] Record the face-recognition training objective and source training corpus where known.
- [ ] Audit known training/evaluation overlap and document what cannot be established.
- [ ] Freeze face detection, alignment, crop, colour order, normalization and embedding L2
      normalization.
- [ ] Freeze treatment of detection/alignment failures and exclusions.

Backbone selection is a protocol decision, not a result-dependent tuning loop. If several
candidate backbones are considered, the selection procedure and data allowed for that decision
must be frozen before any qualification outcome is inspected.

## 2. Dataset roles and benchmark hierarchy

The current proposed hierarchy is:

- **LFW** — sanity/reproduction benchmark, not sufficient by itself to release the backbone gate;
- **CFP-FP, AgeDB-30, CALFW, CPLFW** — harder screening/diagnostic benchmarks;
- **IJB-C** — preferred primary qualification benchmark, conditional on lawful access, licence
  compliance and reproducible use of its official protocol.

Before execution:

- [ ] Confirm exact datasets and lawful/reproducible access.
- [ ] If IJB-C cannot be used, freeze a replacement before any qualification outcomes are read.
- [ ] Use official folds/protocols where they exist; do not invent favourable cross-validation.
- [ ] Declare TRAIN / VALIDATION / SCREEN / untouched qualification TEST roles.
- [ ] Declare target population, capture regime and exclusions.
- [ ] Audit identity, image and near-duplicate overlap between all data roles where applicable.
- [ ] Record identities, captures, genuine trials and impostor trials.

## 3. Study 1A — raw 512D viability gate

The raw backbone must reproduce a credible reference performance before compression can be
studied.

- [ ] Freeze at least one decision-relevant low-FMR/FAR endpoint.
- [ ] Freeze the reference result(s) for the exact backbone and exact benchmark protocol.
- [ ] Freeze a numerical reproduction tolerance before any Study 1A outcome is inspected.
- [ ] Require at least one difficult benchmark in addition to LFW.
- [ ] Freeze whether pass is conjunctive across benchmarks or uses another explicit rule.

The gate must not be defined as "close to SOTA" after looking at results. It must be a numeric,
predeclared reproduction criterion tied to the exact model/protocol being reproduced.

**Gate A result semantics**

- `PASS` — raw 512D foundation is credible; Study 1B may be prepared, but still requires its
  own authorization.
- `FAIL` — stop and diagnose model/preprocessing/data/protocol mismatch.
- `INDETERMINATE` — evidence is insufficient; do not proceed to compression qualification.

## 4. Study 1B — matched compression comparison

The comparison remains:

- raw 512D;
- Gaussian random projection 128D;
- TRAIN-only PCA 128D;
- supervised Siamese/metric-learning projection 128D.

Controls must receive the same input embeddings and data roles.

- [ ] Random route uses the declared Gaussian projection and L2 normalization.
- [ ] PCA is fitted only on authorized training data.
- [ ] Siamese training uses only authorized supervision and frozen training rules.
- [ ] Raw route is represented once and is not given artificial seed variability.
- [ ] Model/projection randomness remains distinct from bootstrap Monte-Carlo randomness.

## 5. Estimand, operating point and claims

Primary representation estimand for candidate `m`, raw reference `b`, and target false-match
rate `alpha`:

`delta_fnmr(m, alpha) = FNMR_m(alpha) - FNMR_b(alpha)`

Before execution:

- [ ] Freeze target FMR `alpha`.
- [ ] Freeze and justify non-inferiority margin `delta`.
- [ ] Do not inherit Study 0 `alpha=0.01` and `delta=0.03` automatically; justify reuse or change.
- [ ] Freeze one-sided UCB level and interval construction.
- [ ] Freeze all-seeds or alternative method-level decision rule.
- [ ] Separate equal-FMR representation benchmarking from operational threshold-transfer claims.
- [ ] Mark AUC/EER/ROC/DET as descriptive unless explicitly promoted in the preregistration.

A failure to demonstrate non-inferiority means `NOT_DEMONSTRATED`, not general inferiority of
128D compression or of metric learning.

## 6. Identity dependence and uncertainty

Study 0 established that naive pair-row independence is not acceptable when trials share
identities.

- [ ] Preserve an identity-dependence-aware uncertainty estimator appropriate to the Study 1
      trial graph/protocol.
- [ ] Revalidate estimator behaviour if the new benchmark graph differs materially from Study 0.
- [ ] Same bootstrap/resampling draw must be used for paired raw-candidate differences.
- [ ] More bootstrap replicates must not be treated as a substitute for more independent subjects.
- [ ] Freeze degeneracy handling before outcomes.

## 7. Progressive evidence: Screen → Promote/Stop → Qualify

### Stage A — screening

Stage A is explicitly non-claim-bearing.

- [ ] Screening seeds frozen as `[11, 29]` unless changed before data opening.
- [ ] Screening dataset frozen.
- [ ] Promotion metric(s) frozen.
- [ ] Numeric promotion/stop thresholds frozen.
- [ ] Maximum compute/data budget frozen.
- [ ] Qualification TEST remains unopened.

Allowed decisions: `CONTINUE`, `STOP`, `REDIRECT`.

### Stage B — qualification

- [ ] Qualification seeds frozen as `[11, 29, 47, 71, 101]` unless changed before execution.
- [ ] Full subject-level uncertainty procedure frozen.
- [ ] Untouched TEST protocol frozen.
- [ ] Multiplicity policy frozen.
- [ ] Independent result review and replay requirements frozen.

Screening evidence must never be relabelled as qualification evidence.

## 8. A-priori sample size

Do not calculate power at the null boundary `Delta = delta`.

Use plausible alternatives such as `Delta_expected = 0` and `0.01`, then design for:

`P(UCB(Delta) < delta | Delta_true = Delta_expected) >= 0.90`.

- [ ] Simulation includes identity/capture clustering.
- [ ] Genuine/impostor construction is represented.
- [ ] Low-FMR threshold uncertainty is represented.
- [ ] Raw-candidate correlation is represented.
- [ ] Seed variation and final method-level rule are represented.
- [ ] Required identities/captures are primary; pair count is not treated as independent N.

## 9. Multiplicity, budget and environment

- [ ] Freeze dimensions, routes, seeds and claim-bearing comparisons.
- [ ] Freeze multiplicity treatment.
- [ ] Freeze compute platform, library versions, GPU/CPU assumptions and runtime budget.
- [ ] Freeze epochs, early stopping, learning rate, batch size and training budget where relevant.
- [ ] Capture environment and exact replay commands.

## 10. Required double review before any tests

Two independent reviews are mandatory.

### Review 1 — scientific / harness

Reviewer must explicitly accept or reject:

- falsifiability and bounded claims;
- data roles and leakage controls;
- official benchmark semantics;
- Study 1A viability gate and Study 1B promotion rules;
- estimand, sampling unit and uncertainty method;
- seed and multiplicity rules;
- prohibited inferences;
- distinction between evidence, Chronicle and pedagogy;
- human-understanding obligation.

### Review 2 — technical / reproducibility

Reviewer must explicitly accept or reject:

- exact model weights/checksum/licence;
- preprocessing/alignment/normalization;
- folds/splits/protocol implementation;
- overlap-audit implementation;
- threshold selection and freeze logic;
- randomness lineage;
- matched route semantics;
- environment capture and replay commands.

**Release condition:** both reviews return `ACCEPT`, CI/Research Assurance are green, and the
protocol is frozen. Only then may an explicit GO for Study 1A be requested.

## 11. Pedagogical / human-understanding gate

Before execution, at least one accountable human should be able to explain without relying on
a green CI badge:

1. why a face-specific 512D backbone is being qualified before compression;
2. why LFW alone is insufficient as the release gate;
3. why official benchmark folds/protocols are preserved;
4. the difference between FMR/FNMR and AUC/EER;
5. what the reproduction tolerance means;
6. why shared identities break naive pair independence;
7. why PCA and random projection remain necessary controls;
8. why Stage A screening is not final evidence;
9. what a non-inferiority margin means;
10. why `NOT_DEMONSTRATED` is not the same as "the method is worse".

This is an understanding gate only. It cannot release a scientific gate.

## 12. Explicitly prohibited next actions

Until the preregistration is frozen, double-reviewed and explicitly authorized, do not:

- run Study 1A or Study 1B outcome-bearing tests;
- inspect qualification outcomes to tune the model, tolerance, margin or promotion rule;
- substitute a different backbone after seeing qualification results;
- open qualification TEST to rescue a failed screen;
- start representation-geometry experiments;
- remove negative seeds or failed routes;
- claim industrial biometric validity from benchmark reproduction.
