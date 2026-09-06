# Study 1B S4N1 — selection bias, validation selection and independent TEST evaluation

Date: 2026-09-04  
Status: source-grounded non-outcome design note. No Study 1B SCREEN or TEST result is opened or authorized by this note.

## Question

S4NEW separates two scientific objects: the performance of one frozen route artifact and the
stability of the stochastic training procedure across retrainings. S4N1 must therefore answer a
narrower design question: if one artifact is selected from five predeclared seed artifacts using
VALIDATION only, what must be calibrated before that selected artifact can later be evaluated on
untouched TEST?

## Statistical source

Cawley and Talbot, *On Over-fitting in Model Selection and Subsequent Selection Bias in
Performance Evaluation*, JMLR 11 (2010), 2079–2107:

- https://www.jmlr.org/papers/v11/cawley10a.html

The paper shows that optimizing a model-selection criterion estimated on finite data can itself
overfit that criterion. The important Study 1B consequence is not "never select the best
validation artifact." It is that the selection criterion and the final performance evaluation
must not be confused. A validation-best score is expected to be optimistic on the data used to
choose it. That optimism does not become a confirmatory performance claim.

S4N1 therefore makes the selection step explicit and requires the final confidence bound to be
computed only on untouched TEST after the artifact identity has been frozen.

## Biometric evaluation source

NIST Face Recognition Technology Evaluation (FRTE) 1:1:

- https://pages.nist.gov/frvt/html/frvt11.html

NIST evaluates submitted implementations through a published API and reports verification
accuracy including FNMR at specified FMR operating points. This supports the already-recorded
S4 reframe toward a frozen/submitted implementation as a primary technology-evaluation object.
It does **not** prescribe how an ML developer should choose one stochastic training realization,
and S4N1 does not claim NIST or ISO conformity.

## Selection is not the same as TEST bias

There are three quantities that must remain separate.

1. **Validation optimism.** If the minimum of five noisy validation scores is selected, its
   observed validation score will tend to look better than its latent validation truth. This is
   the winner's-curse/model-selection effect that S4N1 must measure in known-truth simulation.

2. **TEST inference for the selected artifact.** If VALIDATION and TEST identities/captures are
   disjoint and TEST is not used for selection, the TEST estimator targets the selected
   artifact's TEST truth. S4N1 must verify this by empirical known-truth coverage rather than
   assuming it.

3. **Seed-quality transport.** The same artifact can genuinely perform relatively well or poorly
   across both VALIDATION and TEST. This latent artifact-quality dependence is distinct from
   finite-sample observation noise. S4N1 therefore treats VALIDATION→TEST latent seed-effect
   correlation as a prospective sensitivity parameter instead of silently setting it to one.

## Why the selection metric is the primary estimand's point estimate

The S4N1 cross-seed ranking metric is prospectively fixed as the paired equal-FMR
`Delta_FNMR` point estimate on VALIDATION at FMR 0.01. It is route-neutral and directly aligned
with the later primary TEST estimand.

A validation UCB is deliberately not used as a second optimization target. Uncertainty is still
handled where it matters inferentially: the selected artifact receives the frozen identity-aware
97.5% TEST UCB. The validation score is a development-selection statistic only.

## Why three artifact semantics remain

- `S4N_FIXED_SEED` is the cleanest control: no cross-seed outcome selection, but the seed is
  arbitrary and the claim is only about seed 11.
- `S4N_VALIDATION_BEST` represents a realistic delivered-artifact process: select the lowest
  validation `Delta_FNMR` among the five predeclared seeds, freeze it, and evaluate it later on
  untouched TEST.
- `S4N_VALIDATION_MEDIAN` deliberately reduces optimization of validation noise, but "median of
  five observed validation ranks" must not be misreported as a population median of all possible
  retrainings.

Before synthetic results are seen, S4N1 records `VALIDATION_BEST` as the semantic preference
**if** it passes the same prospective coverage and power gates. This prevents switching to a
different rule merely because a later synthetic table looks more favorable.

## Dependence model to calibrate prospectively

The active Study 1B boundary gives disjoint VALIDATION and TEST identities and pair graphs.
S4N1 therefore assumes role-specific subject and pair noise are independent conditional on the
artifact's latent role-specific quality. It does not assume the latent quality itself is
independent across roles.

The transport sensitivity uses bivariate seed effects with predeclared VALIDATION–TEST
correlations 0, 0.5 and 1. Zero is the no-transfer stress case; one is perfect transport.
Negative transport is not introduced without an external mechanism because doing so would add a
new scientific assumption rather than test the current one.

## Calibration consequence

Coverage is judged against the **selected artifact's known TEST truth**, not against its
validation score and not against the mean of five seed truths. Core power is likewise evaluated
at exact selected-artifact TEST deltas 0.00 and 0.01, preserving the existing FMR 0.01,
NI margin 0.03 and one-sided UCB level 0.975.

A separate transport sensitivity reports selection optimism, selected-seed frequency, TEST
selection regret and seed-truth spread. These secondary quantities keep seed instability visible
without converting the primary artifact claim back into the old method-level 5/5 estimand.

## Boundary

This note supplies design rationale only. It does not replace the original 5/5 rule, activate an
amendment, authorize SCREEN or TEST, or support any claim about the real performance of raw512,
random128, PCA128 or Siamese128.
