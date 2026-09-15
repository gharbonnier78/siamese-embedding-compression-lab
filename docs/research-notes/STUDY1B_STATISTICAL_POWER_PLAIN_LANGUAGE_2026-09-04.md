# Study 1B — statistical power in plain language

**Date:** 2026-09-04  
**Status:** pedagogical research note; non-outcome; does not release any scientific gate.  
**Context:** Study 1B matched embedding-compression comparison (`raw512` vs `random128` / `PCA128` / `Siamese128`), after the canonical power preflight and S2/S3 design analyses.  
**Scientific authority:** none. This note explains the Study 1B protocol and statistical concepts; it does not replace the frozen protocol, Chronicle, simulation evidence, or authoritative statistical sources.

## Why this note exists

The Study 1B power work can sound much more abstract than the engineering question it is actually answering. The purpose of this note is to translate the concepts of **Type I error**, **Type II error**, and **statistical power** into the language of a qualification bench.

The important point is that power is **not** a performance metric of the biometric matcher and is **not** the probability that a model is good. It is a property of the **experimental decision procedure**.

---

## 1. Think of the statistical test as a qualification bench

Imagine that we have built a bench whose job is to return a decision such as `PASS`, `FAIL`, or more rigorously `NON-INFERIORITY DEMONSTRATED` / `NOT DEMONSTRATED`.

There is a real physical/statistical state of the system that the bench cannot observe perfectly. It only sees a finite amount of noisy information and applies a decision rule.

That creates four possibilities:

| Reality | Decision of the bench | Interpretation |
|---|---|---|
| The candidate does not deserve the PASS | PASS | **Type I error** — unjustified acceptance |
| The candidate deserves the PASS | FAIL / not demonstrated | **Type II error** — missed acceptable candidate |
| The candidate does not deserve the PASS | FAIL | correct rejection |
| The candidate deserves the PASS | PASS | correct qualification |

This table is more useful than memorizing symbols first.

---

## 2. Study 1B question in ordinary language

For the primary non-inferiority comparison, Study 1B asks whether reducing an AdaFace representation from 512 dimensions to 128 dimensions degrades one-to-one biometric matching by more than an allowed margin.

The primary difference is

\[
\Delta = FNMR_{128D} - FNMR_{raw512}.
\]

The allowed non-inferiority margin is

\[
\delta_{NI}=0.03.
\]

So, very roughly:

- if the compressed route loses less than 3 FNMR points, it is inside the predefined acceptable margin;
- if it loses 3 points or more, it is outside that margin.

The actual Study 1B decision uses the full one-sided uncertainty calculation, not just the observed point estimate.

---

## 3. Type I error — a false PASS

The probability of a Type I error is traditionally written **\(\alpha\)**.

In this Study 1B non-inferiority setting, the dangerous mistake is:

> **The compression is actually too degraded, but the experiment declares it non-inferior anyway.**

In engineering language, this is similar to a qualification bench issuing an acceptance when the product does not actually satisfy the intended criterion.

That is why the confidence / decision threshold is deliberately controlled prospectively.

A useful caution: the shortcut “Type I = false positive” is only safe after checking how the hypotheses are defined. In a non-inferiority test, the null hypothesis is not simply “nothing happens”; it essentially represents the candidate being insufficiently good relative to the allowed margin.

---

## 4. Type II error — a false FAIL or missed qualification

The probability of a Type II error is traditionally written **\(\beta\)**.

For Study 1B, this corresponds to:

> **The compression is actually inside the acceptable margin, but the experiment does not manage to demonstrate it.**

In engineering language, the product may be acceptable but the qualification bench is not discriminating enough to prove it reliably.

This can happen when:

- there is too little genuinely independent information;
- observations are dependent;
- measurement uncertainty is large;
- the true difference is small;
- the decision rule is very conservative;
- several uncertainty sources accumulate.

This distinction matters because a `NOT DEMONSTRATED` result is not equivalent to evidence that the compression is truly inferior.

---

## 5. Statistical power — the ability of the bench to detect an acceptable situation

Statistical power is

\[
\mathrm{Power}=1-\beta.
\]

In plain language:

> **If the situation we want the test to recognize is really true, how often would this experimental procedure successfully recognize it if we could repeat the whole experiment many times?**

Power is therefore always tied to a specific assumed truth.

A test can have high power for a large difference and low power for a very small difference.

It is not meaningful to say only “the test has 80% power” without saying **for which true effect size and under which data-generating assumptions**.

---

## 6. Study 1B concrete example

Suppose the true compression degradation is

\[
\Delta_{true}=0.01.
\]

That means the candidate loses one FNMR point relative to raw512, while the allowed NI margin is three points.

So the true situation is compatible with the intended non-inferiority claim.

Under the frozen S3 x2 design and the old `all five seeds must pass` rule, the estimated synthetic power was

\[
0.6485.
\]

Operational reading:

> In the frozen synthetic model, if the true degradation really were +0.01 and we repeated the entire experiment many times, about 64.85% of experiments would demonstrate non-inferiority, while about 35.15% would fail to demonstrate it.

The latter corresponds to the Type II error rate under that scenario:

\[
\beta \approx 1-0.6485=0.3515.
\]

The predeclared Study 1B target was 0.90 power, so this was scientifically insufficient.

---

## 7. What the 0.6485 number does **not** mean

It does **not** mean:

- the candidate has 64.85% biometric accuracy;
- there is a 64.85% probability that compression is good;
- the observed measurements are only 64.85% trustworthy;
- PCA, random or Siamese compression is known to pass or fail;
- the real Study 1B outcome has been inspected.

The number describes only the **ability of one frozen experimental decision rule to detect a predeclared synthetic truth**.

---

## 8. Why a conservative test can have poor power

Suppose a qualification bench is designed to almost never accept a bad product.

One way to achieve that is to demand a very strong amount of evidence before giving PASS.

But if the criterion becomes too strict, the bench may also reject many acceptable products.

That is the engineering analogue of the balance between Type I and Type II errors.

Study 1B's original `all five seeds must individually pass` rule behaved like a **series system controlled by the least favorable training realization**:

\[
PASS = PASS_1 \land PASS_2 \land PASS_3 \land PASS_4 \land PASS_5.
\]

This gives a strong worst-seed interpretation, but it can make the joint decision much harder to pass than the performance of any one realization would suggest.

S2 and S3 were designed to determine whether this loss of power came from simple aggregation semantics, seed variability, or lack of independent biometric information.

---

## 9. Why more data did not solve everything

S3 increased the amount of genuinely distinct pair information while keeping the old 5/5 rule unchanged.

At true \(\Delta=0.01\):

- x1.5 information design: power = 0.565;
- x2 information design: power = 0.6485;
- required: at least 0.90.

So more independent information helped, but not enough.

That was a useful negative result: it showed that the problem was not simply “we need more pairs”.

It pushed the research toward examining whether the **scientific object of the decision rule** itself had been defined correctly.

---

## 10. The perspective change that followed

A key distinction emerged:

### Artifact-level question

> Once a particular compression artifact has been selected and frozen, how does that delivered artifact perform against raw512?

### Training-procedure question

> If the compression method is retrained many times, how variable is the distribution of resulting trained models?

Both are legitimate questions, but they are not the same estimand.

The original 5/5 rule mixed them by requiring five stochastic training realizations to all pass in order to qualify the artifact-level comparison.

The S4 perspective reframe retained the method-level question for a separate stability study and opened S4NEW/S4N1 to study the artifact-level qualification problem prospectively.

---

## 11. A compact memory model for engineers

Think:

```text
Reality
  ↓
finite / noisy observations
  ↓
statistical decision rule
  ↓
PASS / NOT DEMONSTRATED
```

Two main mistakes are possible:

```text
bad reality + PASS
    = Type I error
    = unjustified qualification

acceptable reality + NOT DEMONSTRATED
    = Type II error
    = missed qualification
```

And:

```text
Power
    = ability to avoid the second mistake
      for a precisely specified true situation
```

---

## 12. Misconceptions to avoid

### Misconception 1

> `Power = probability that the hypothesis is true.`

**Correction:** No. Power is computed under an assumed true scenario and describes repeated behavior of the decision procedure.

### Misconception 2

> `If power is poor, the measured FNMR values are invalid.`

**Correction:** Not necessarily. Poor power mainly limits how reliably the experiment can support a specific inferential decision.

### Misconception 3

> `NOT DEMONSTRATED = inferior.`

**Correction:** No. A Type II error is exactly the situation where an acceptable candidate fails to be demonstrated as acceptable.

### Misconception 4

> `More bootstrap replicates increase independent biometric information.`

**Correction:** No. Bootstrap replicates improve Monte Carlo approximation of the uncertainty procedure; they do not create new subjects, captures or independent biometric evidence.

### Misconception 5

> `Type I always means false positive and Type II always means false negative.`

**Correction:** These analogies are useful only after the null and alternative hypotheses have been interpreted in the current application.

---

## 13. Understanding gate

Before treating this concept as understood, the learner should be able to explain without formulas:

1. the difference between a Type I and a Type II error in the Study 1B non-inferiority context;
2. why a power of 0.6485 does not describe matcher accuracy;
3. why `NOT DEMONSTRATED` is not equivalent to `inferior`;
4. why increasing genuine independent information can increase power;
5. why more bootstrap repetitions do not create more independent biometric information;
6. why the old 5/5 rule can be scientifically valid yet badly matched to the artifact-level qualification question.

A stronger understanding gate is to reconstruct the following sentence correctly:

> If the true degradation is +0.01, a power of 0.6485 means that under the frozen synthetic model and experimental decision rule, repeated experiments would demonstrate non-inferiority about 64.85% of the time; it says nothing directly about the actual observed accuracy of the compression routes.

---

## 14. Research provenance / encounters

This concept was not introduced here as an isolated textbook definition. It became necessary through the actual Study 1B research progression:

1. canonical Study 1B power preflight — original 5/5 rule underpowered at true \(\Delta=0.01\);
2. S1 — reanalysis of existing synthetic rows;
3. S2 — seed-rule / seed-variability sensitivity;
4. S3 — additional independent-information sensitivity;
5. S3 negative result — x2 improves power but remains below 0.90;
6. S4 perspective reframe — separation of frozen-artifact performance from stochastic retraining stability;
7. S4NEW / S4N1 — prospective artifact-selection and qualification design.

This encounter chain should remain visible because it explains not only what statistical power means, but **why Study 1B needed to understand it**.

---

## 15. Related authoritative / normative objects

For scientific interpretation, consult the frozen Study 1B protocol and Chronicle entries rather than this note.

Relevant project artifacts include:

- `protocol/chronicle/STUDY1B_POWER_PREFLIGHT_4000_EVIDENCE_CLOSURE_2026-08-31.yaml`;
- `protocol/simulations/STUDY1B_POWER_DESIGN_SENSITIVITY_V0_1_2026-08-31.yaml`;
- `protocol/chronicle/STUDY1B_POWER_DESIGN_S3_POWER_CALIBRATION_RESULT_2026-09-04.yaml`;
- `protocol/chronicle/STUDY1B_S4_METHOD_LEVEL_PERSPECTIVE_REFRAME_2026-09-04.yaml`;
- `protocol/simulations/STUDY1B_S4NEW_ARTIFACT_LEVEL_QUALIFICATION_V0_1_2026-09-04.yaml`.

This note is pedagogical evidence only. It does not change the outcome boundary:

```yaml
real_study1b_outcomes_opened: false
screen_opened: false
test_opened: false
representation_geometry_opened: false
amendment_activated: false
```
