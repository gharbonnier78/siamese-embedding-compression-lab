# Study 0 corrected historical reanalysis — interpretation draft

Status: **DRAFT_PENDING_INDEPENDENT_INTERPRETATION_REVIEW**

This document is the first scientific interpretation of the independently approved `MATERIALIZED_NOT_INTERPRETED` bundle. It proposes no final gate promotion until an independent reviewer accepts this interpretation.

## Frozen decision rule

Primary estimand: `Delta_FNMR = FNMR(candidate, FMR=0.01) - FNMR(raw, FMR=0.01)`.

The frozen non-inferiority margin is `delta = 0.03`. For a candidate route to satisfy Study 0 non-inferiority, the 97.5% upper percentile bound for `Delta_FNMR` must be `<= 0.03` for **every** predeclared seed.

## Primary corrected result

No 128D route satisfies the frozen non-inferiority rule.

| route | seeds passing | UCB 97.5% range | interpretation |
|---|---:|---:|---|
| random 128D | 0/5 | 0.112649 to 0.151768 | non-inferiority not demonstrated |
| PCA 128D | 0/5 | 0.125556 to 0.133606 | non-inferiority not demonstrated |
| Siamese 128D | 0/5 | 0.176584 to 0.189156 | non-inferiority not demonstrated |

For Siamese, observed equal-FMR point deltas across seeds are `+0.034, +0.064, -0.006, +0.050, +0.010`. The corrected subject-bootstrap means are `+0.0392, +0.0438, +0.0024, +0.0372, +0.0113`. Every corrected 95% interval crosses both favorable and unfavorable values, but every upper bound is far above the frozen `0.03` margin.

Therefore the admissible conclusion is **failure to demonstrate non-inferiority**. This is not evidence that Siamese compression is proven inferior.

## What E-STAT-001 changed

The original pair-level bootstrap understated uncertainty relative to the frozen subject-slot bootstrap on this sample.

Average 95% interval width:

| route | pair bootstrap | subject bootstrap | subject/pair |
|---|---:|---:|---:|
| random | 0.1304 | 0.2042 | ~1.57x |
| PCA | 0.1749 | 0.2664 | ~1.52x |
| Siamese | 0.1944 | 0.2991 | ~1.55x |

The corrected analysis therefore does **not** reverse the original Study 0 negative decision. It makes the uncertainty materially wider while preserving the same bounded scientific conclusion: preservation at the low-FMR endpoint was not demonstrated.

## Supervision-value claim C-SUP-001

`C-SUP-001` remains **NOT_DEMONSTRATED**.

Study 0 did not preregister a superiority margin or Pareto rule for Siamese versus PCA/random; that rule is explicitly deferred to Study 2. The corrected Study 0 outputs also do not show consistent descriptive dominance by Siamese across seeds.

No wording such as “Siamese is the best compression route” is admissible.

## Operational threshold-transfer analysis

At validation-frozen thresholds, the bootstrap means averaged across seeds are approximately:

| route | FNMR | FMR |
|---|---:|---:|
| raw 512D | 0.8939 | 0.00201 |
| PCA 128D | 0.8468 | 0.00201 |
| random 128D | 0.8940 | 0.00241 |
| Siamese 128D | 0.9311 | 0.00158 |

These are **not equal-FMR comparisons** and must not be interpreted as a direct ranking. For Siamese, the transferred validation thresholds describe a stricter operating trade-off: lower observed FMR with higher FNMR relative to raw. This does not rescue the primary non-inferiority claim.

## Proposed bounded scientific decisions

Pending independent interpretation review:

- `C-NI-001`: remain `NOT_DEMONSTRATED`.
- `C-SUP-001`: remain `NOT_DEMONSTRATED`.
- `E-STAT-001`: eligible to move from `SPECIFIED_PENDING_IMPLEMENTATION` to `REANALYZED` only after the independent interpretation review approves this document.
- `G2 estimator_and_statistical_validity`: the prior bootstrap-unit defect is technically corrected and the validated estimator is eligible for bounded reassessment; do **not** mark G2 PASS until independent review accepts the interpretation as required by the frozen correction specification.
- Study 1 remains blocked until that final interpretation review and the resulting append-only Chronicle/gate update.
- Geometry remains out of scope.

## Interpretation boundary

This result supports neither industrial biometric validity, very-low-FMR production claims, universal failure of metric learning, proof that 128D compression is intrinsically harmful, nor superiority of PCA or any other route.

The bounded result is narrower: for this frozen ImageNet ResNet-18 / LFW Study 0 experiment, after correction of the uncertainty unit and validated subject-bootstrap reanalysis, non-inferiority of the tested 128D routes to raw 512D at empirical FMR 0.01 is not demonstrated.
