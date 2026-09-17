# Biometric technology-evaluation object: artifact performance vs training-procedure stability

Date: 2026-09-04  
Status: source-grounded research note; non-outcome; no Study 1B gate is released by this note.

## Question

After Study 1B S3 showed that the frozen `all five seeds must pass` rule remains underpowered at
true `Delta_FNMR = +0.01` even with x2 genuinely distinct pair information, what is the object
normally qualified in established biometric technology evaluations: a submitted/frozen
implementation, or the population distribution induced by repeatedly retraining the same
learning procedure?

## Official sources reviewed

### ISO/IEC 19795-1:2021

Current published International Standard (Edition 2, 2021; corrected English version 2024-09):

- https://www.iso.org/standard/73515.html

Its public abstract states that the standard establishes general principles for biometric
performance testing in terms of error and throughput rates, including measurement, comparison,
prediction and verification of conformance with specified performance requirements. It applies
to empirical testing of systems and algorithms through analysis of comparison scores and
output decisions. The public ISO page also records that a new edition is under development.

The 2026 draft is not treated here as normative authority:

- https://www.iso.org/standard/93355.html

### NIST FRTE 1:1 Verification

- https://pages.nist.gov/frvt/html/frvt11.html
- https://pages.nist.gov/frvt/api/FRVT_ongoing_11_api.pdf

NIST describes participation as submission of software wrapped behind its published C++ API,
validated to ensure consistent output between developer and NIST execution, and delivered as a
submission package. FRTE reports accuracy and other implementation characteristics, including
FNMR at controlled FMR operating points. The API exposes creation of templates and comparison
of two templates by the submitted implementation.

This is an evaluation of a submitted implementation. The reviewed FRTE material does not make
repeated retraining under several random seeds, nor an `all retrainings must pass` rule, the
primary technology-evaluation object.

### NIST PFT III

- https://www.nist.gov/programs-projects/proprietary-fingerprint-template-evaluations-pft-overview

NIST describes PFT III as a one-to-one evaluation of proprietary fingerprint template
generation and matching. It reports performance of the submitted technology on multiple
fingerprint datasets. NIST explicitly warns that high accuracy in the evaluation does not by
itself imply capability to field a full-scale AFIS, which is an important boundary between
algorithm/technology evidence and system/operational qualification.

### NIST MINEX III

- https://www.nist.gov/itl/iad/btg/minex-iii-compliance-guidelines
- https://pages.nist.gov/minex/results/tables/

MINEX III defines explicit compliance criteria on submitted template generators and matchers.
Examples include FNMR thresholds at specified FMR operating points, including native one-finger
matching with `FNMR <= 0.02` at `FMR <= 1e-4`. The compliance object is again a submitted
implementation and its behavior under the test protocol.

## Source-bounded conclusion

The reviewed ISO/NIST sources support a common primary evaluation pattern:

`fixed/submitted implementation -> controlled biometric comparisons -> error-rate metrics and/or compliance decision`.

They do **not** establish that stochastic training stability is irrelevant, nor do they provide
a universal rule for how a machine-learning developer should quantify retraining variability.
They also do not justify claiming that five training seeds are sufficient to characterize a
population of trained models. The narrower conclusion is that a `5/5 retraining realizations
must each pass` rule is not shown by these sources to be a standard primary biometric
technology-evaluation criterion.

## Consequence for Study 1B

Study 1B has been mixing two valid but distinct scientific objects:

1. **Artifact-level biometric performance**: after a route artifact is selected and frozen
   without TEST access, how does its 1:1 performance compare with frozen raw512 at the same FMR?
2. **Training-procedure stability**: if the stochastic route is retrained, what distribution of
   performance differences is induced by training randomness?

The original S4 method-level seed-distribution question remains scientifically meaningful for
object (2), but it should not automatically remain the primary blocking gate for object (1).
Any change to the frozen Study 1B primary rule still requires a prospective amendment,
calibration, independent review and explicit activation before outcomes are opened.

## Research implication

The next non-outcome step should define an artifact-level S4-new design that preserves the
existing matched FNMR-at-FMR estimand and identity-aware uncertainty while prospectively
specifying how a final stochastic route artifact is selected and frozen. Training-seed
stability should remain visible as a secondary/future method-level study rather than being
silently discarded.
