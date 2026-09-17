# Study 1B — residual decision risk and operational-impact framing after S4N1/S4N2

**Date:** 2026-09-06  
**Status:** non-outcome decision-analysis note; no real Study 1B outcome is opened.  
**Purpose:** translate the synthetic power deficit into a decision-risk quantity before any human acceptability decision.  
**Authority:** the frozen protocols, workflow artifacts and Scientific Chronicle remain authoritative for scientific results.

## 1. Why this note exists

S4N1 and S4N2 both failed the prospectively frozen requirement of at least 0.90 power at true `Delta_FNMR = +0.01`.

That fact alone does not say whether the remaining deficit is operationally important.

The next question is therefore not:

> How can we tune the estimator until it passes?

It is:

> What decision risk does 85–87 % power create, what happens operationally when the study returns `NOT DEMONSTRATED`, and is that consequence acceptable for the intended use?

This is a decision-analysis question, not a new attempt to modify the S4N2 estimator.

## 2. Translate power into study-level non-demonstration risk

At a fixed true state of the synthetic world,

```text
non-demonstration probability = 1 - power
```

At true `Delta_FNMR = +0.01`, which is inside the frozen non-inferiority margin `+0.03`:

| Selector | S4N1 power | S4N1 non-demonstration | S4N2 power | S4N2 non-demonstration |
|---|---:|---:|---:|---:|
| FIXED | 86.55 % | 13.45 % | 84.70 % | 15.30 % |
| BEST | 86.90 % | 13.10 % | 84.90 % | 15.10 % |
| MEDIAN | 86.95 % | 13.05 % | 85.35 % | 14.65 % |
| frozen target | 90.00 % | 10.00 % | 90.00 % | 10.00 % |

So the residual gap relative to the frozen target is:

- S4N1: roughly **+3.05 to +3.45 percentage points** of study-level non-demonstration probability;
- S4N2: roughly **+4.65 to +5.30 percentage points**.

These are probabilities about the **decision produced by an entire repeated study under the synthetic truth**, not probabilities about individual biometric transactions.

## 3. What this number does NOT mean

A 15.1 % non-demonstration probability does **not** mean any of the following:

- 15.1 % of people will be falsely accepted;
- 15.1 % of people will be falsely rejected;
- the compressed matcher is wrong 15.1 % of the time;
- there is a 15.1 % probability that compression is bad;
- the real Study 1B candidate has `Delta_FNMR = +0.01`.

The value comes from a known-truth synthetic design used to qualify the **evidence-generation and decision procedure**.

## 4. The operational consequence depends on the policy after `NOT DEMONSTRATED`

Power matters operationally only through the action taken when the study cannot demonstrate non-inferiority.

Three illustrative policies show why.

### Policy A — conservative fallback

```text
NOT DEMONSTRATED -> keep raw512 / do not adopt compression
```

If the compressed route were actually acceptable, a missed demonstration would mainly create a **false rejection of the engineering change**.

Potential consequences could include:

- foregone memory reduction;
- foregone compute reduction;
- lower throughput than could have been achieved;
- higher storage / transfer cost;
- inability to exploit a 128D representation where it would otherwise be acceptable.

Under this policy, low power does not directly translate into unsafe biometric acceptance. The dominant risk is **opportunity cost / qualification conservatism**.

### Policy B — evidence fallback

```text
NOT DEMONSTRATED -> collect more independent evidence / rerun qualification / escalate review
```

The main consequence becomes:

- schedule delay;
- extra compute and laboratory cost;
- extra data-acquisition or qualification effort;
- delayed release decision.

Again, the statistical Type-II risk is converted mainly into cost and delay, provided the fallback itself is respected.

### Policy C — ignore the non-demonstration

```text
NOT DEMONSTRATED -> deploy anyway
```

This bypasses the intended evidential control. In that case the power analysis no longer provides the relevant safety argument because the decision policy is overriding the qualification result.

This note does not support such a policy.

## 5. Whitelist / blacklist or stadium-flow example

For an identity system used in a high-throughput flow, there are at least three distinct layers that must not be merged:

```text
Layer 1 — study-level inference
Can the experiment demonstrate non-inferiority of the compressed route?

Layer 2 — engineering release policy
What do we do if the answer is NOT DEMONSTRATED?

Layer 3 — person-level operation
What happens to one traveller / spectator / citizen at a gate or checkpoint?
```

The synthetic power deficit exists at **Layer 1**.

It affects Layer 3 only through the policy chosen at Layer 2.

For example, if Layer 2 says “keep the already-qualified raw512 route whenever compression is not demonstrated”, then a false non-demonstration is primarily a missed optimisation. It does **not** imply that 13–15 % of spectators are mishandled.

Conversely, person-level risks such as false matches, false non-matches, queueing, manual review, denial of access, or security misses require their own operational probabilities, costs and safeguards. They cannot be inferred from statistical power alone.

## 6. Why 90 % is not automatically sacred — but cannot be moved post hoc

The current experiment correctly keeps the frozen 0.90 requirement. Since the S4N results are already known, changing it now to 0.85 would be post-hoc redefinition of success.

However, for a **future study or governance decision**, it is legitimate to ask where a power requirement should come from.

A defensible future threshold would ideally be connected to quantities such as:

- cost of a false qualification;
- cost of a missed acceptable candidate;
- cost and feasibility of collecting more independent information;
- reversibility of deployment;
- fallback policy;
- operational criticality;
- effect size that is decision-relevant, not merely statistically convenient.

That future policy analysis must be explicit and prospective. It cannot rewrite S4N1 or S4N2 as PASS.

## 7. Current residual decision-risk statement

Given only the evidence opened so far, the strongest defensible statement is:

> Under the frozen synthetic generator at true `Delta_FNMR = +0.01`, the tested S4N1 and S4N2 inference procedures fail to meet the prospectively required 0.90 power. Their study-level probability of failing to demonstrate an actually non-inferior state is approximately 13.05–13.45 % for S4N1 and 14.65–15.30 % for S4N2, versus the target 10 %. The operational severity of this residual Type-II risk cannot be determined without an explicit fallback/release policy and cost model.

## 8. Decision questions before any next scientific opening

Before treating the 85–87 % versus 90 % gap as acceptable or unacceptable, human authority should answer:

1. What is the exact decision enabled by a Study 1B PASS?
2. What happens when the result is `NOT DEMONSTRATED`?
3. Is raw512 retained as a safe fallback, or is new evidence collected?
4. What engineering benefit is lost when an acceptable 128D route is not qualified?
5. What is the cost/delay of gathering more genuinely independent information?
6. Which error is more costly in the intended use: false qualification or missed acceptable compression?
7. Is the 90 % threshold itself linked to an operational-risk requirement, or was it a generic design convention?
8. Would a future prospective design with more independent information be economically justified?

These answers can support an acceptability decision. They do not alter the already-closed S4N1/S4N2 results.

## 9. Scientific boundary

This note uses only synthetic known-truth calibration results already authorized for S4N1/S4N2.

It does not open:

- Study 1B SCREEN;
- qualification TEST outcomes;
- real raw512 / random128 / PCA128 / Siamese128 performance;
- representation geometry;
- an amendment;
- real-study artifact selection.

It also does not assert what the actual production fallback policy is. The policies above are explicit **decision-analysis scenarios** that show what information is still required.

## 10. Provenance

Primary result records:

- `protocol/chronicle/STUDY1B_S4N1_CORE_POWER_CALIBRATION_RESULT_2026-09-06.yaml`;
- `protocol/chronicle/STUDY1B_S4N1_POWER_PLATEAU_DIAGNOSTIC_RESULT_2026-09-06.yaml`;
- `protocol/chronicle/STUDY1B_S4N2_DAGJK20_COVERAGE_1000_RESULT_2026-09-06.yaml`;
- `protocol/chronicle/STUDY1B_S4N2_DAGJK20_POWER_4000_RESULT_2026-09-06.yaml`.

Pedagogical companion:

- `pedagogy/case-studies/quand-une-methode-bien-calibree-manque-de-puissance-study1b-s4n1-s4n2.fr.md`.
