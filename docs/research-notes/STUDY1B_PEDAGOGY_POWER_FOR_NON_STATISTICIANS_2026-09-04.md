# Study 1B pedagogy — power, Type I and Type II errors for non-statisticians

**Date:** 2026-09-04  
**Status:** pedagogical draft; non-outcome; no scientific gate is changed by this note.  
**Context of appearance:** Study 1B power preflight, S2/S3 power-design analysis, then S4NEW reframing.  
**Scientific authority:** none. This note explains the Study 1B protocol and its statistical sources; it does not replace them.

## 1. Start from the engineering problem, not the statistical vocabulary

Think of the statistical procedure as a **qualification bench that must return a decision from imperfect measurements**.

There is a real state of the world — which the bench does not know exactly — and there is the decision produced from finite, noisy data.

Two mistakes are possible:

| Reality | Decision | Engineering interpretation |
|---|---|---|
| The candidate does **not** deserve qualification | PASS | **Type I error** — false qualification / false alarm in favor of the candidate |
| The candidate **does** deserve qualification | FAIL or NOT DEMONSTRATED | **Type II error** — a valid candidate is missed |
| The candidate does not deserve qualification | FAIL | correct decision |
| The candidate deserves qualification | PASS | correct decision |

The statistical names are less important than the engineering meaning: a qualification system can either **accept something it should reject**, or **reject something it should accept**.

## 2. What does “deserve qualification” mean in Study 1B?

Study 1B compares a compressed 128D route with the frozen raw512 reference through

\[
\Delta = FNMR_{128D} - FNMR_{raw512}
\]

at the frozen operating point

\[
FMR = 0.01.
\]

The non-inferiority margin is

\[
\delta_{NI}=0.03.
\]

So the engineering question is not “are the two systems numerically identical?” It is:

> Is the degradation, if any, small enough to remain inside the maximum loss that the protocol declared acceptable?

A true value such as

\[
\Delta = 0.01
\]

means that the compressed route is worse by one FNMR point, but still inside the allowed three-point margin.

## 3. Type I error — the dangerous false PASS

In a non-inferiority test, the null hypothesis is essentially the adverse situation:

> the candidate is inferior by at least the allowed margin.

A Type I error therefore means:

> We declare the compression non-inferior even though its true degradation is actually too large.

For qualification, this is the **false PASS** risk.

This is why the confidence level / one-sided upper confidence bound is controlled conservatively: the protocol must not make it too easy to grant non-inferiority.

## 4. Type II error — the missed acceptable candidate

A Type II error is the opposite failure:

> The compression is really inside the acceptable margin, but the experiment does not manage to demonstrate it.

This is not evidence that the candidate is bad. It means the decision procedure did not have enough discriminatory capability, information, or precision to prove the acceptable situation.

In engineering language:

> the product may be conforming, but the qualification bench is not powerful enough to establish that fact reliably.

This can happen because:

- there is not enough genuinely independent information;
- the observations are strongly dependent;
- the measurement variance is high;
- the true effect is small;
- the decision rule is very conservative;
- several uncertainty sources accumulate.

## 5. Statistical power

**Power** answers:

> If the situation we want to recognize is really true, how often would this experimental procedure succeed in recognizing it if we could repeat the whole experiment many times?

Formally,

\[
Power = 1-\beta,
\]

where \(\beta\) is the Type II error probability.

The key point is that power is **not**:

- matcher accuracy;
- probability that the hypothesis is true;
- probability that the measured FNMR is correct;
- confidence level;
- quality score of the ML model.

It is a property of the **experimental design + decision rule + amount and structure of information + assumed true effect**.

## 6. Read the S3 result in ordinary language

In S3, under the x2 information design and the frozen all-five-seed rule, the estimated power at true

\[
\Delta=0.01
\]

was

\[
0.6485.
\]

Read this as:

> Suppose the real degradation is indeed only +0.01 FNMR, therefore comfortably inside the allowed +0.03 margin. If we could repeatedly regenerate complete experiments under the frozen synthetic model, the current decision procedure would establish non-inferiority only about 65 times out of 100.

Equivalently, it would fail to demonstrate an actually acceptable situation about

\[
1-0.6485 = 0.3515
\]

or 35 times out of 100.

This is why S3 failed its 0.90 power requirement.

It does **not** mean:

> “There is only a 64.85% chance that compression works.”

It means:

> “The current qualification rule is not sufficiently capable of converting this small true difference into a reliable PASS decision.”

## 7. Why this mattered for the research progression

The Study 1B preflight first revealed that the original `5 seeds out of 5 must pass` rule had low power at true \(\Delta=0.01\).

S2 examined whether simpler changes in seed aggregation solved the problem.

S3 then asked a more conservative question: could we keep the strong 5/5 semantics and recover power merely by adding genuinely distinct biometric information?

The answer was no. Power improved, but remained below the frozen 0.90 requirement.

That result triggered an important scientific distinction:

1. **Artifact qualification:** how well does one final frozen delivered artifact perform against raw512?
2. **Training-procedure stability:** how variable is the method when retrained under different random seeds?

The original 5/5 rule mixed these two questions. S4NEW was opened to qualify the first object without pretending that this also proves the second.

## 8. Analogy with an industrial test bench

A product may satisfy the underlying engineering requirement, yet a poor qualification setup may still reject it frequently because:

- the measurement chain is too noisy;
- the sample is too small;
- the environment is insufficiently representative;
- the decision threshold is too conservative;
- the test does not observe the right independent information.

Improving the **power of the test** therefore does not mean weakening the product requirement. It means improving the ability of the evidence-generation process to distinguish a genuinely acceptable system from an unacceptable one.

This is exactly why Study 1B refuses the shortcut “change the 0.03 margin until the test passes.” The scientific problem is to improve or correctly define the decision procedure, not to move the target after seeing a failure.

## 9. Misconceptions to avoid

### “Type I always means false positive, Type II always means false negative.”

Useful mnemonic, but incomplete. The operational meaning depends on how the hypotheses are formulated. In non-inferiority, the null hypothesis represents the adverse / insufficient-performance situation, so a Type I error is specifically a **false qualification of non-inferiority**.

### “Low power means the measured performance is wrong.”

No. It means the experiment is not sufficiently capable of making the intended inferential decision reliably at the specified effect size.

### “More bootstrap replicates increase power like more independent subjects.”

No. More bootstrap draws improve numerical approximation of the uncertainty calculation; they do not create new independent biometric information.

### “S3 failing means raw512 is better than all compressed routes.”

No. S3 was synthetic design calibration. No real Study 1B route outcome was opened.

### “If a rule is conservative, it must be scientifically better.”

Not necessarily. A rule can control false qualification very strongly while becoming so insensitive that it misses many acceptable candidates. Scientific defensibility requires the rule to match the actual claim being made.

## 10. Understanding gate

Before treating this concept as understood, one should be able to explain without formulas:

1. the difference between a false qualification and a missed acceptable candidate;
2. why statistical power concerns the decision procedure rather than model accuracy;
3. why power depends on the true effect being considered;
4. why S3 power = 0.6485 at true \(\Delta=0.01\) does not mean “64.85% chance the compression is good”;
5. why adding bootstrap repetitions is not the same as adding independent information;
6. why changing the NI margin after seeing a power failure would answer a different question rather than repair the original experiment.

## 11. Provenance / related artifacts

Study 1B scientific evidence and decisions remain authoritative in the protocol/Chronicle, notably:

- `protocol/chronicle/STUDY1B_POWER_PREFLIGHT_4000_EVIDENCE_CLOSURE_2026-08-31.yaml`
- `protocol/simulations/STUDY1B_POWER_DESIGN_SENSITIVITY_V0_1_2026-08-31.yaml`
- `protocol/chronicle/STUDY1B_POWER_DESIGN_S3_POWER_CALIBRATION_RESULT_2026-09-04.yaml`
- `protocol/chronicle/STUDY1B_S4_METHOD_LEVEL_PERSPECTIVE_REFRAME_2026-09-04.yaml`
- `protocol/simulations/STUDY1B_S4NEW_ARTIFACT_LEVEL_QUALIFICATION_V0_1_2026-09-04.yaml`

The parallel Diderot ML pedagogical capitalization is maintained separately in `gharbonnier78/diderot-machine-learning-specialization`.

No SCREEN, TEST or representation-geometry outcome is authorized or opened by this pedagogical note.
