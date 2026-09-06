# Study 1B — S4 value-of-information decision table

**Date:** 2026-09-06  
**Status:** non-outcome engineering decision analysis  
**Boundary:** no Study 1B SCREEN, qualification TEST outcome, real route performance, representation geometry, or amendment is opened by this note.  
**Authority:** frozen protocols, workflow artifacts and Scientific Chronicle remain authoritative for scientific results.

## 1. Question

S4N1 and S4N2 both failed the prospectively frozen `power >= 0.90` requirement at the known synthetic truth `Delta_FNMR = +0.01`.

The engineering question is no longer:

> Which uncertainty estimator can be tuned until it crosses 90%?

It is:

> Is it worth acquiring more genuinely independent evidence to reduce the probability of returning `NOT DEMONSTRATED` for an actually acceptable compression candidate?

This is a **value-of-information** question.

## 2. What the observed gap actually buys

Using the prospectively preferred `BEST` selector for comparison only:

| Design | Power at true Delta=+0.01 | Non-demonstration probability | Gap to 90% target |
|---|---:|---:|---:|
| S4N1 | 86.90% | 13.10% | +3.10 percentage points |
| S4N2 | 84.90% | 15.10% | +5.10 percentage points |
| Frozen target | 90.00% | 10.00% | — |

These percentages are **study-level** probabilities under the frozen synthetic truth. They are not person-level FMR/FNMR probabilities.

## 3. Conservative fallback: `NOT DEMONSTRATED -> keep raw512`

Let:

- `C_miss` = total cost of failing to adopt, or delaying, an actually acceptable 128D route;
- `C_extra` = incremental cost of acquiring the extra independent evidence required by a future design;
- `q` = prospective probability, before outcome opening, that the candidate is actually in the acceptable state relevant to the decision.

Conditional on the candidate truly being acceptable, improving power from S4N1 BEST to 90% can avoid at most:

```text
0.031 * C_miss
```

of expected missed-demonstration cost per qualification opportunity.

For S4N2 BEST to 90% the corresponding quantity is:

```text
0.051 * C_miss
```

Before knowing whether the candidate is acceptable, multiply by `q`:

```text
Value of raising S4N1 BEST from 86.9% to 90% = q * 0.031 * C_miss
Value of raising S4N2 BEST from 84.9% to 90% = q * 0.051 * C_miss
```

Therefore a future evidence-acquisition plan intended **only** to recover these last power points is not economically justified on the missed-demonstration side if:

```text
C_extra >= q * 0.031 * C_miss     [relative to S4N1 BEST]
```

or, if S4N2 were the starting point,

```text
C_extra >= q * 0.051 * C_miss.
```

This is a break-even relation, not a claim that extra evidence would in fact achieve 90%.

## 4. Sensitivity table — no operational values assumed

The table below gives the maximum break-even evidence cost as a fraction of `C_miss`, under different hypothetical values of `q`.

| Prospective `q` | S4N1: `q * 3.10% * C_miss` | S4N2: `q * 5.10% * C_miss` |
|---:|---:|---:|
| 0.25 | 0.775% of `C_miss` | 1.275% of `C_miss` |
| 0.50 | 1.550% of `C_miss` | 2.550% of `C_miss` |
| 0.75 | 2.325% of `C_miss` | 3.825% of `C_miss` |
| 1.00 | 3.100% of `C_miss` | 5.100% of `C_miss` |

These values are **sensitivity examples only**. Study 1B has not established a value for `q` or `C_miss`.

## 5. What belongs inside `C_miss`?

Under the conservative fallback, `C_miss` could include only benefits/costs that are genuinely caused by not adopting the acceptable compression, for example:

- memory or storage that would otherwise have been saved;
- transfer bandwidth that would otherwise have been reduced;
- compute or latency/throughput benefit that would otherwise have been obtained;
- hardware or infrastructure capacity that would otherwise have been avoided;
- release delay caused by a new qualification cycle;
- engineering and laboratory effort caused by repeated evidence collection;
- strategic cost of not being able to use the 128D representation in a constrained deployment.

No value for any of these is inferred from unopened Study 1B outcomes.

## 6. False qualification must remain a separate side of the decision

Power addresses the **missed acceptable candidate** side.

A complete decision analysis must also account for the opposite error:

> qualifying a candidate that is actually worse than the allowed non-inferiority margin.

Let:

- `alpha` = prospectively calibrated false-qualification probability under the adverse state;
- `C_false_pass` = consequence of such a false qualification.

A generic expected-decision-loss template is:

```text
L = q * (1 - power) * C_miss
    + (1 - q) * alpha * C_false_pass
    + C_evidence
```

This equation is intentionally symbolic. The current S4 work does not authorize substituting person-level biometric harm probabilities or unopened real candidate outcomes into it.

## 7. Decision table for the next engineering conversation

| Question | If answer is small / cheap / reversible | If answer is large / expensive / irreversible |
|---|---|---|
| Cost of keeping raw512 after `NOT DEMONSTRATED`? | Power gap may have low operational value | More evidence may be valuable |
| Cost of collecting new independent evidence? | A future higher-power design may be justified | Accepting conservative fallback may dominate |
| Severity of a false qualification? | Some trade space may exist prospectively | Preserve strong false-pass control; do not trade it casually for power |
| Deployment reversible? | Pilot / rollback can reduce decision consequence | Qualification evidence deserves more weight |
| Benefit of 128D? | Missing it is mostly harmless | Missed demonstration can have substantial opportunity cost |
| Is raw512 a valid safe fallback? | Power deficit is mainly opportunity/delay risk | Need a different release-risk analysis |

## 8. Current recommendation

1. Keep S4N1 and S4N2 **CLOSED_NEGATIVE** against their frozen 90% gate.
2. Do **not** launch S4N3 merely to search for a passing estimator.
3. Treat 90% as binding for the completed campaigns, but not as an established physical safety threshold.
4. Before designing a future higher-power experiment, quantify the fallback policy and the costs represented by `C_miss`, `C_extra`, and `C_false_pass`.
5. Only then decide whether additional independent information has positive expected value.

## 9. Minimum operational inputs needed

A practical next pass needs explicit human/engineering inputs for:

- what a PASS authorizes;
- what `NOT DEMONSTRATED` triggers;
- whether raw512 remains deployable and acceptable;
- estimated economic/engineering value of an acceptable 128D route over the intended horizon;
- estimated cost and delay of obtaining more independent evidence;
- severity/cost class of a false qualification;
- reversibility and rollback capability;
- intended deployment volume/horizon if the cost model is per transaction or per system.

Until those inputs exist, the correct result is a **decision framework with explicit unknowns**, not a fabricated numerical business case.
