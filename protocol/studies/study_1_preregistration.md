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

- [ ] Architecture, weights, source, checksum and licence pinned.
- [ ] Training corpus documented and overlap with qualification data audited.
- [ ] Selection rule evaluated only on development/screening data.
- [ ] Raw performance checked at the target low-FMR operating point, not only by global AUC.

Study 0 showed why this matters: a representation can retain broad discrimination while
remaining weak at the primary operating point. Study 1 therefore screens backbone viability
before qualification.

## 2. Population and datasets

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
