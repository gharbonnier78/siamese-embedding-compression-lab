# Study 1B — ADEMP mapping of the S4 simulation studies

**Date:** 2026-09-06  
**Status:** pedagogical / methodological capitalization; non-outcome.  
**Scientific authority:** none. Frozen Study 1B protocol, simulation contracts, workflow artifacts and Chronicle remain authoritative.  
**Boundary:** this note opens no SCREEN, qualification TEST result, real route performance, representation geometry or amendment.

## 1. Why add ADEMP now?

Morris, White and Crowther (2019) describe simulation studies as computer experiments and propose a structured planning/reporting framework: **ADEMP** — Aims, Data-generating mechanisms, Estimands, Methods, Performance measures.

Reference:

> Morris TP, White IR, Crowther MJ. *Using simulation studies to evaluate statistical methods*. Statistics in Medicine. 2019;38(11):2074-2102. DOI: 10.1002/sim.8086. PMID: 30652356. PMCID: PMC6492164.

Primary public source: https://onlinelibrary.wiley.com/doi/10.1002/sim.8086

This mapping is intentionally retrospective: Study 1B S4 was not originally written under an explicit ADEMP heading. The value of the mapping is therefore not to rewrite history, but to show which elements were already present, where they were distributed across artifacts, and what should be made explicit prospectively in future simulation work.

## 2. A — Aims

The S4 simulation programme had a bounded methodological aim:

> Before opening real Study 1B outcomes, determine whether the frozen artifact-level non-inferiority decision procedure has acceptable operating characteristics under known-truth synthetic worlds.

The successive sub-aims were:

1. S4N1: evaluate the frozen subject-aware bootstrap uncertainty procedure.
2. Diagnose why power plateaued around 86.9% at true `Delta_FNMR = +0.01`.
3. S4N2: prospectively evaluate a separately frozen DAGJK20 uncertainty estimator without changing the scientific question or decision threshold.

The aim was **not** to estimate the real performance of raw512, random128, PCA128 or Siamese128.

## 3. D — Data-generating mechanisms

The known-truth generator preserved the main structural ingredients considered decision-relevant for the calibration exercise:

- subject dependence in genuine and impostor scores;
- candidate/reference correlation;
- frozen validation/test graph structure;
- finite genuine and impostor information;
- equal-FMR thresholding semantics;
- synthetic truth cells for `Delta_FNMR`, including the critical acceptable state `+0.01` and other coverage cells.

The key benefit of simulation is that the true state is known by construction. This makes it possible to ask whether an interval actually covers truth, and whether a decision procedure recognizes a genuinely acceptable state often enough.

### Limitation

Passing a synthetic calibration only establishes behavior under the declared generator family. It does not prove that the real biometric world follows that generator. Generator adequacy is therefore a separate scientific question.

## 4. E — Estimands and decision targets

The central estimand remained:

```text
Delta_FNMR = FNMR_candidate - FNMR_raw512
```

at the frozen operating point:

```text
FMR = 0.01
```

with frozen non-inferiority margin:

```text
Delta_NI = +0.03
```

S4 was evaluating the **operating characteristics of the inference/decision procedure for this estimand**, not changing the estimand.

A true `Delta_FNMR = +0.01` means the candidate is genuinely one FNMR percentage point worse than the reference in that synthetic world, but still inside the allowed +3-point non-inferiority margin.

## 5. M — Methods

### S4N1

- same frozen point estimate;
- subject-aware bootstrap uncertainty calculation;
- one-sided 97.5% upper confidence bound;
- frozen artifact selectors `BEST`, `MEDIAN`, `FIXED`;
- PASS when the upper bound stays at or below `+0.03`.

### S4N2

The point estimate, FMR target, NI margin, confidence level, selectors, truth cells and decision rule were kept unchanged.

Only the uncertainty estimator changed to prospectively frozen `DAGJK20`:

- TEST identities assigned deterministically to 20 groups;
- delete one group at a time;
- remove all edges touching deleted identities;
- recompute candidate/reference thresholds and `Delta_FNMR`;
- estimate jackknife variance across 20 delete-group replicates;
- use Student-t 97.5% upper bound with 19 degrees of freedom.

This isolates the methodological question: can a different defensible uncertainty estimator recover the desired decision power without moving the scientific target?

## 6. P — Performance measures

The simulation did not judge a method from a single number.

### Calibration / coverage

- empirical two-sided 95% coverage;
- empirical one-sided upper 97.5% coverage;
- exact Monte Carlo confidence lower bounds for the coverage gates;
- degeneracy fraction.

### Decision capability

- power at known true `Delta_FNMR = 0`;
- power at the critical acceptable state `Delta_FNMR = +0.01`;
- frozen required power `>= 0.90`.

### Diagnostics

- point-estimate error mean and SD;
- estimated standard error;
- ratio between estimated SE and repeated-study point-estimate SD;
- selector sensitivity;
- deliberately non-admissible diagnostic alternatives kept separate from the frozen method.

## 7. What ADEMP makes clearer about the result

The final S4 story can be summarized without ambiguity:

| ADEMP element | What Study 1B S4 learned |
|---|---|
| Aim | qualify the inference procedure before real outcomes |
| Data-generating mechanism | known-truth subject-dependent biometric-like worlds |
| Estimand | equal-FMR `Delta_FNMR`; unchanged throughout |
| Methods | S4N1 bootstrap vs prospectively frozen S4N2 DAGJK20 |
| Performance measures | coverage, degeneracy, power, estimator diagnostics |

S4N1 and S4N2 both had acceptable/non-undercovering coverage behavior under the frozen generator, but neither reached the prospectively required 90% power at true `Delta=+0.01`. S4N2 was slightly less powerful than S4N1 on that criterion.

That is a valid negative methodological result. It is not a real matcher-performance result.

## 8. Prospective lesson for future studies

For future simulation-based methodological qualification, an ADEMP block SHOULD be frozen before execution when simulation results may change a scientific or engineering decision.

At minimum:

```text
A — What exact question will this simulation answer?
D — What worlds are generated, why are they relevant, and which worlds are intentionally absent?
E — What quantity or decision target is being estimated/evaluated?
M — Which methods are compared, with what fixed semantics?
P — Which measures determine success, failure and uncertainty in the Monte Carlo experiment?
```

Additional harness controls remain necessary: provenance, authorization boundary, frozen gates, random-state/replay assurance, Monte Carlo uncertainty, append-only negative results, independent review where warranted, and explicit separation between synthetic calibration and real outcome evidence.

ADEMP structures the **simulation study**; it does not replace the wider scientific harness.

## 9. Understanding gate

A reader should be able to explain:

1. why known-truth simulation can evaluate a statistical method without revealing real Study 1B outcomes;
2. the difference between the data-generating mechanism and the estimand;
3. why changing only the uncertainty estimator can be a clean method comparison;
4. why coverage and power are different performance measures;
5. why a simulation method can pass coverage but fail power;
6. why synthetic validity is conditional on the generator rather than proof of real-world representativeness.
