# Study 1 - Preregistration checklist

Status: `DRAFT_PREREGISTRATION`. Freeze and hash the qualification contract before any
qualification TEST access. Study 0 remains independently reproducible and is not overwritten
by Study 1.

## 0. Progressive evidence strategy — screen before qualification

Study 1 now has two explicit evidence modes.

### Stage A — exploratory screening

Purpose: decide whether the face-specific backbone and 128D compression routes are promising
enough at the decision-relevant low-FMR regime to justify a full qualification campaign.

- [ ] SCREEN dataset is distinct from untouched qualification TEST.
- [ ] Qualification TEST access remains forbidden during screening.
- [ ] Screening outputs are marked `EXPLORATORY_SCREENING_NOT_FOR_CLAIM`.
- [ ] Screening routes include raw, random, TRAIN-only PCA and Siamese on the same embeddings.
- [ ] Screening seeds are fixed in advance (`11`, `29`) and are not later used to remove
  unfavorable qualification seeds.
- [ ] Raw backbone viability at the relevant low-FMR endpoint is checked before spending
  qualification budget on compression.
- [ ] Numerical promotion and stop criteria are frozen before screening outcomes are read.
- [ ] If no credible signal survives matched controls, preserve the negative screening result,
  stop or redirect, and do not open qualification TEST.

Promotion from screening to qualification is a **research-investment decision**, not a
scientific claim.

### Stage B — qualification

Only a promoted design enters qualification. The full planned seed set remains
`[11, 29, 47, 71, 101]`, with the complete frozen uncertainty, provenance, multiplicity,
gate and independent-review burden. Screening evidence cannot be silently re-labelled as
qualification evidence.

## 1. Backbone and provenance

Study 0 intentionally reproduced a pedagogical architecture: a torchvision ResNet-18
pretrained for ImageNet object classification was **fully frozen**, and only the 512→128
linear embedding head learned from LFW pairs. That is useful for isolating the projection
mechanism, but it is not a strong face-recognition source representation. A linear head can
reorganize information already present in the 512D vector; it cannot reconstruct identity
information that the generic ImageNet representation did not encode reliably.

Study 1 therefore changes the source representation before it changes the compression claim.
The preferred primary design is a **pretrained, frozen face-specific extractor**, not a new
backbone trained as part of this compression experiment.

- [ ] Architecture, weights, source, checksum and licence pinned.
- [ ] Face-specific training objective documented (for example an ArcFace-family angular-margin model).
- [ ] Training corpus and training provenance documented well enough to audit evaluation overlap.
- [ ] Face detection/alignment/normalization pipeline pinned together with the embedding weights.
- [ ] Selection rule evaluated only on development/screening data.
- [ ] Raw performance checked at the target low-FMR operating point, not only by global AUC or accuracy.
- [ ] No alternate backbone may be substituted after SCREEN outcomes are read unless a new design is preregistered.

An ArcFace-family iResNet is the current **candidate class**, not yet a frozen implementation.
AdaFace is a plausible secondary candidate if a later, separately registered question asks
whether quality-aware source embeddings change the compression outcome. Study 1 should avoid
trying many backbones and keeping whichever looks best on screening data.

The remembered “~70% accuracy” from the first experiment is consistent with the immutable
replay only as a descriptive sanity check: a TEST-optimized threshold yields 71.5% for raw
512D and 73.0–74.7% across the Siamese seeds (PCA 74.1–74.3%). Those values are TEST-tuned,
non-deployable and not the claim-bearing endpoint. Their importance is that they make the
weakness of the source backbone visible before compression is blamed.

## 2. Population and datasets

The four data roles below must remain distinct: **backbone training**, **projection
TRAIN/VALIDATION**, **exploratory SCREEN**, and **qualification TEST**. Identity overlap
across roles can create optimistic evidence even when file-level splits are different.

### 2.1 Projection development — TRAIN / VALIDATION

Use a sufficiently large, authorized face-development corpus with many identities and
multiple captures per identity. Projection-development identities must be disjoint from the
qualification identities.

- **VGGFace2 is a scientifically attractive candidate** because it was designed with
  substantial pose and age variation and identity-separated train/test partitions.
- Its original Oxford download is no longer available, so it must not be treated as an
  automatically available dependency. Use it only if access is legitimate and its terms are
  compatible with this work.
- If VGGFace2 is unavailable, select another authorized development corpus that meets the
  same identity-count, capture-diversity, provenance and disjointness requirements.

### 2.2 Exploratory SCREEN

A standard public screening suite may include:

- **LFW** — continuity with Study 0 and basic sanity checking;
- **CFP-FP** — frontal/profile stress;
- **AgeDB-30** — age variation;
- **CALFW** — cross-age LFW-family stress;
- **CPLFW** — cross-pose LFW-family stress.

These datasets are **screening evidence only**. Common web-scale face-training corpora can
share identities with LFW-family benchmarks, so training/evaluation overlap must be audited
rather than assumed absent. A screening benchmark with unresolved overlap may still be useful
for engineering triage, but it cannot be silently promoted to independent qualification evidence.

### 2.3 Qualification TEST

**IJB-C 1:1 template verification is the preferred public qualification candidate** because
it contains substantially richer unconstrained still/video material and many more impostor
template comparisons than LFW, making lower false-accept regions measurable.

Before it can be called qualification evidence:

- [ ] lawful/authorized access is confirmed;
- [ ] identity overlap against the frozen backbone's training corpus is audited;
- [ ] identity overlap against projection TRAIN/VALIDATION is zero by construction;
- [ ] the chosen IJB-C protocol, template aggregation and preprocessing are frozen;
- [ ] the target FAR/FMR and sample-size/precision analysis are compatible with the protocol.

If training/test identity disjointness cannot be established, the IJB-C result is still a
useful external benchmark but must be labelled accordingly rather than used as a strong
independent qualification claim.

### 2.4 Operational / external validity

No public celebrity benchmark establishes representativity for a passport, border kiosk,
mobile-device enrollment, national gallery or any specific production population. A later
external-validity study must use authorized population- and capture-relevant data before such
claims are made. Demographic/capture stress testing remains a later study rather than being
silently folded into Study 1.

Common checklist:

- [ ] Target population, capture process and exclusions declared.
- [ ] TRAIN, VALIDATION, SCREEN and untouched qualification TEST roles separated.
- [ ] Identity/image/near-duplicate overlap audit completed.
- [ ] Counts recorded for identities, captures per identity, genuine trials and impostor trials.

## 3. Estimands and claims

- [ ] Target FMR `alpha` and justified non-inferiority margin `delta` frozen for qualification.
- [ ] Representation benchmark claim separated from operational threshold-transfer claim.
- [ ] One-sided UCB level, bootstrap interval construction and method-level seed rule frozen.
- [ ] Raw, random, TRAIN-only PCA and Siamese qualification routes use identical input embeddings.

The random control uses entries with variance `1/d` (standard deviation `1/sqrt(d)`) followed
by L2 normalization. For `d=128`, `R_ij ~ Normal(0, 1/128)` where the second parameter denotes
variance.

## 4. Study 0 statistical prerequisite — satisfied, not an execution authorization

- [x] Study 0 `E-STAT-001` final interpretation review accepted and append-only closure recorded.
- [x] `G2 estimator_and_statistical_validity = PASS` recorded for the bounded corrected Study 0 reanalysis.
- [x] Subject-slot bootstrap implementation and coverage evidence remain versioned and replayable.
- [x] Pair-level versus subject-level sensitivity remains preserved without overwriting Study 0.

Authoritative closure: `main@935b3dd02fd11d47b6b64a14d1cdef59eddecbb4` and
`evidence/study_0_subject_bootstrap_v0.2.2/STUDY0_CLOSURE_DECISION_2026-08-19.yaml`.

This prerequisite being satisfied does **not** authorize Study 1 screening or qualification.
The design amendment still requires independent review and merge, all remaining inputs below
must be frozen, and a separate researcher authorization is required before screening execution.

## 5. A-priori sample size

Do not calculate power at `Delta=delta`, the null boundary. Declare plausible
`Delta_expected < delta`, for example 0 and 0.01, then select the study design such that:

`P(UCB(Delta) < delta | Delta_true = Delta_expected) >= 0.90`.

- [ ] Simulation includes identity/capture clustering, genuine/impostor construction,
  threshold uncertainty, raw-candidate correlation, seed variation and the all-seeds rule.
- [ ] Required identities and captures are primary; pair counts alone are not treated as
  independent sample size.
- [ ] VALIDATION supports threshold estimation and TEST supports transfer assessment.
- [ ] FMR and FNMR resolution and confidence precision are compatible with `alpha` and
  `delta`.

## 6. Multiplicity and budget

- [ ] Screening and qualification compute budgets are recorded separately.
- [ ] Qualification seeds, dimensions, routes, comparisons and multiplicity policy frozen.
- [ ] Compute platform, versions, GPU-hours, epochs and early-stopping budget frozen.
- [ ] Supervision-versus-PCA/random claim designated confirmatory or explicitly exploratory.

## 7. CAL gate and exclusions

- [ ] Exact bounded qualification claim and gates G1-G3 frozen.
- [ ] 1:N remains Study 4; external shift remains Study 3.
- [ ] Failed gates produce `INADMISSIBLE` or `INDETERMINATE`, never silent redesign.
- [ ] Geometry remains outside Study 1 unless separately proposed and authorized after the
  compression evidence warrants it.

## 8. Escalation record

- [ ] If Stage A promotes to Stage B, record why the additional qualification cost is justified.
- [ ] If Stage A stops, retain the negative result and the reason for redirection.
- [ ] Never use qualification TEST to rescue a failed screening design.

See `docs/LESSONS_LEARNED_STUDY0_PROGRESSIVE_EVIDENCE.md` for the process lesson that motivated
this amendment.
