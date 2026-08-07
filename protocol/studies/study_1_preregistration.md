# Study 1 - Preregistration checklist

Status: `DRAFT_PREREGISTRATION`. Freeze and hash this document before any qualification
TEST access. Study 0 remains independently reproducible and is not overwritten by Study 1.

## 1. Backbone and provenance

- [ ] Architecture, weights, source, checksum and licence pinned.
- [ ] Training corpus documented and overlap with qualification data audited.
- [ ] Selection rule evaluated only on a non-qualification screening set.
- [ ] Raw performance checked at the target low-FMR operating point, not only by global AUC.

Study 0 had raw AUC 0.7931 but raw FNMR 0.806 at FMR 0.01. Its representation therefore
contained global discrimination while remaining insufficient at the primary operating point.

## 2. Population and datasets

- [ ] Target population, capture process and exclusions declared.
- [ ] TRAIN, VALIDATION, screening and untouched TEST roles separated.
- [ ] Identity/image/near-duplicate overlap audit completed.
- [ ] Counts recorded for identities, captures per identity, genuine trials and impostor trials.

## 3. Estimands and claims

- [ ] Target FMR `alpha` and justified non-inferiority margin `delta` frozen.
- [ ] Representation benchmark claim separated from operational threshold-transfer claim.
- [ ] One-sided UCB level, bootstrap interval construction and method-level seed rule frozen.
- [ ] Raw, random, TRAIN-only PCA and Siamese routes use identical input embeddings.

The random control uses entries with variance `1/d` (standard deviation `1/sqrt(d)`) followed
by L2 normalization. For `d=128`, `R_ij ~ Normal(0, 1/128)` where the second parameter denotes
variance.

## 4. Blocking statistical correction

- [ ] `E-STAT-001` corrected and reviewed.
- [ ] Exact identity-dependence resampling algorithm specified for genuine and two-identity
  impostor trials.
- [ ] Pair-level versus identity-aware sensitivity published without overwriting Study 0.
- [ ] Coverage of the proposed interval evaluated by simulation.

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

- [ ] Seeds, dimensions, routes, comparisons and multiplicity policy frozen.
- [ ] Compute platform, versions, GPU-hours, epochs and early-stopping budget frozen.
- [ ] Supervision-versus-PCA/random claim designated confirmatory or explicitly exploratory.

## 7. CAL gate and exclusions

- [ ] Exact bounded claim and gates G1-G3 frozen.
- [ ] 1:N remains Study 4; external shift remains Study 3.
- [ ] Failed gates produce `INADMISSIBLE` or `INDETERMINATE`, never silent redesign.
