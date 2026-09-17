# Study 1B — Engineering cost and value-of-information worksheet

**Date:** 2026-09-07  
**Status:** non-outcome engineering decision worksheet  
**Boundary:** no SCREEN, qualification TEST result, real matcher performance, representation geometry or amendment is opened by this worksheet.

## Purpose

Turn the Study 1B S4 power shortfall into an engineering decision with explicit inputs rather than guessed economics.

Working policy:

- `PASS -> promote to a controlled next engineering/qualification stage`;
- `NOT_DEMONSTRATED -> retain raw512 by default`;
- do not launch S4N3 merely to search for a passing estimator;
- acquire genuinely new independent evidence only if its value is justified.

## 1. Structural facts already known

For the vector payload itself, holding datatype and encoding fixed:

```text
512D -> 128D
128 / 512 = 0.25
payload reduction = 75%
```

For `N` embeddings and `b` bytes/component:

```text
raw bytes        = N * 512 * b
128D bytes       = N * 128 * b
bytes avoided    = N * 384 * b
```

With effective replication/backup factor `r`:

```text
replicated bytes avoided = N * 384 * b * r
```

These are dimensional arithmetic facts, not end-to-end performance claims.

## 2. Inputs to fill

| Input | Symbol | Value | Unit | Source / owner |
|---|---|---:|---|---|
| bytes per component | `b` | ? | bytes | ? |
| number of embeddings | `N` | ? | vectors | ? |
| retention horizon | — | ? | months/years | ? |
| effective replication + backup factor | `r` | ? | copies | ? |
| vector transfers over horizon | `Q` | ? | transfers | ? |
| storage rate | `R_storage` | ? | currency/byte/horizon | ? |
| transfer rate | `R_transfer` | ? | currency/byte | ? |
| measured compute/capacity value | `V_compute` | ? | currency or capacity unit | ? |
| enabling value | `V_enabling` | ? | currency or declared unit | ? |
| extra independent evidence cost | `C_extra` | ? | currency | ? |
| extra evidence delay | — | ? | days/weeks | ? |
| prospective acceptable-state probability | `q` | ? | 0..1 | rationale required |
| false-qualification consequence | `C_false_pass` | ? | cost/severity model | ? |
| raw512 valid fallback? | — | ? | yes/no/conditional | owner |
| rollback time | — | ? | hours/days | owner |

Unknown is an acceptable value. A fabricated number is not.

## 3. Engineering value of 128D

### Storage

```text
V_storage = N * 384 * b * r * R_storage
```

### Transfer

```text
V_transfer = Q * 384 * b * R_transfer
```

### Compute / capacity

Use measured engineering evidence rather than the dimensional ratio:

```text
V_compute = measured avoided compute/capacity cost
```

### Total value

```text
V_128D = V_storage + V_transfer + V_compute + V_capacity + V_enabling
```

Terms must be mutually exclusive enough to avoid double-counting.

## 4. Cost of a missed demonstration

Under the conservative fallback, `C_miss` is the cost of failing to realize or delaying an actually acceptable 128D route.

A practical decomposition is:

```text
C_miss = foregone_or_delayed(V_128D)
       + avoidable requalification cost
       + avoidable schedule/opportunity cost
```

Do not interpret `C_miss` as biometric harm.

## 5. Value of recovering the final S4N1 power gap

The frozen S4N1 BEST result is:

```text
power = 0.869
required target = 0.900
gap = 0.031
```

If a future design could raise power from 86.9% to exactly 90% without worsening other error properties:

```text
conditional value if the candidate is acceptable = 0.031 * C_miss
prospective value before knowing that state       = q * 0.031 * C_miss
```

Therefore the missed-demonstration-side break-even rule is:

```text
acquire more independent evidence only if
C_extra < q * 0.031 * C_miss
```

This is not sufficient by itself: a complete decision must also account for false qualification.

## 6. False-qualification side

A generic decision-loss model remains:

```text
L = q * (1 - power) * C_miss
  + (1 - q) * alpha * C_false_pass
  + C_evidence
```

`alpha` must come from a prospectively justified/calibrated adverse-state analysis. It must not be invented from the S4 power result.

## 7. Reversibility changes the consequence

The same statistical error can have very different operational consequences depending on the downstream architecture.

A controlled promotion with dual-run, preserved raw512 compatibility, explicit monitoring and rapid rollback can bound the impact of a false qualification. A one-way representation migration cannot.

This is why `PASS` is deliberately not defined as automatic production release.

## 8. Minimum information needed for the next calculation

A useful first pass does not require a perfect business case. It needs only:

1. datatype / bytes per component;
2. rough `N` and retention horizon;
3. effective replication/backup factor;
4. whether transfer volume is material;
5. a rough order of magnitude for the cost and delay of acquiring genuinely new independent evidence;
6. confirmation that raw512 is operationally retainable;
7. a consequence class for false qualification and a rollback/reversibility description.

With those values we can calculate a range for `C_miss`, a break-even `C_extra`, and run sensitivity on `q` rather than pretending to know it precisely.

## 9. What is intentionally not done here

- no real raw512/128D matcher outcome is opened;
- no latency/throughput gain is inferred from 512/128 alone;
- no monetary product value is guessed;
- no 90% gate is changed retrospectively;
- no S4N3 is launched;
- no synthetic result is promoted into a real-world biometric claim.

The next step is to populate the structured input sheet at `protocol/decisions/STUDY1B_ENGINEERING_COST_INPUT_SHEET_V0_1_2026-09-07.yaml` with explicit engineering values and provenance.
