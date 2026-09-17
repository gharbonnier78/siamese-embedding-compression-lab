# Study 1B Phase A — focused construct-validity limitations closure review request v0.1

Date: 2026-09-16

## Review purpose

This is a **focused, non-outcome, pre-materialization review** of the prospective corrections raised by the independent Phase A construct-validity review on exact head `b5720dd7e2031e0ac090ae4f5ea4c09fb0a05cc5`.

That review returned `ACCEPT_WITH_LIMITATIONS` with all CV1-CV10 fields `yes`, while requiring protocol changes before platform materialization. The three blockers were B1 cache/bandwidth observability, B2 cross-regime/censoring pairwise interpretation, and B3 backend dispatch observability.

The purpose of this review is **not** to repeat CV1-CV10 from scratch and not to authorize Phase A execution. It is to determine whether the prospective correction artifact closes B1-B3 without weakening the accepted scientific boundary or the previously accepted D1-D3 / N4-N6 semantics.

## Independence preference

Prefer a reviewer who has **not participated in the prior Study 1B review series**. The construct-validity reviewer disclosed that they authored several prior reviews and recommended a second reviewer with no history in the series if the programme wants stronger independence from confirmation risk.

A reviewer who has prior involvement must disclose it before issuing a verdict.

## Immutable historical review basis

- Construct-validity reviewed head: `b5720dd7e2031e0ac090ae4f5ea4c09fb0a05cc5`
- Base: `5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7`
- Pinned harness: `gharbonnier78/scientific-research-harness@3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`
- Verdict: `protocol/reviews/PR50_B5720DD7_PHASE_A_CONSTRUCT_VALIDITY_REVIEW_VERDICT_2026-09-16.md`
- Chronicle: `protocol/chronicle/STUDY1B_PR50_B5720DD7_PHASE_A_CONSTRUCT_VALIDITY_ACCEPT_WITH_LIMITATIONS_2026-09-16.yaml`
- Verdict SHA-256: `c0e7afe7c2f9f7d8a42dae42b5cf4d49fa8155c61719b4ccc1ff882fafc63d5a`

The accepted construct-validity decision remains bound to `b5720dd7...`; later correction commits do not retroactively move that basis.

## Correction object to review

`protocol/benchmarks/STUDY1B_PHASE_A_CONSTRUCT_VALIDITY_CORRECTIONS_V0_1_2026-09-16.yaml`

This object is a prospective normative extension. It deliberately does not rewrite the historical benchmark v0.3 or environment lock v0.6 bytes reviewed at `b5720dd7...`.

## Required focused checks

### B1 — cache hierarchy and measured memory bandwidth

Verify that the correction requires:

- L1d, L2 and L3/LLC capacities plus inclusivity/sharing topology;
- a named achievable-memory-bandwidth characterization method and measured value;
- each arm's working set relative to LLC capacity;
- achieved memory throughput relative to measured achievable bandwidth where observable;
- the platform/lock-defining choices to be frozen **before** bandwidth characterization;
- no retuning or substitution of a frozen choice based on the bandwidth characterization under the same execution identity.

Confirm that the bandwidth characterization remains an environment-characterization record rather than a target-workload selection signal and therefore does not silently reopen accepted D3 semantics.

### B2 — cross-regime and censoring interpretation

Verify that:

- a quantitative paired 512D/128D ratio or delta is permitted only when both arms are in the same non-censored saturation regime;
- each arm's saturation point/interval is reported alongside paired deltas;
- cross-regime observations are retained but receive no combined performance ratio;
- right-censored vs finite burst/recovery values are retained but receive no finite combined ratio;
- the fixed absolute 16 QPS burst remains valid and any arm-relative burst is optional/future rather than silently replacing it.

### B3 — backend dispatch observability

Verify that the correction requires, per arm:

- backend-reported kernel/core identifier when exposed;
- observability method;
- exact GEMV/batched-GEMM call shape, batch size, shapes, memory order and leading dimension;
- blocking parameters when exposed;
- immutable/raw backend verbose or trace evidence where available.

Confirm that the correction **does not force dispatch equality** between 512D and 128D. Dispatch differences are a legitimate consequence of dimension. If a backend cannot expose dispatch internals, the correction must fail honestly to `NOT_EXPOSED_BY_BACKEND` and prevent microkernel-specific mechanism claims rather than inventing provenance.

### L1 / L3 reporting limitations

Confirm that:

- every joules-per-identification value names offered QPS and saturation regime;
- the report preamble explains designed p95/p99 gaps arising from the frozen support rules;
- support thresholds cannot be relaxed after results are seen.

### L2 future sensitivity

Confirm that G1/intermediate working-set sensitivity remains a **future sensitivity requirement, not a Phase A blocker**, and that Phase A is prohibited from interpolating between G0 and G2 as though intermediate behavior were measured.

## Scientific boundary

This focused review MUST NOT require or open:

- Study 1B SCREEN;
- qualification TEST;
- protected real-route biometric performance;
- protected representation geometry;
- S4N3;
- Phase A result-bearing execution.

No target hardware, power meter, load generator or execution-specific lock should be selected or frozen as part of this review.

## Required verdict fields

Return the following block exactly:

```text
VERDICT: ACCEPT | ACCEPT_WITH_CHANGES | REJECT_OR_REDESIGN
B1_CACHE_AND_BANDWIDTH_OBSERVABILITY_CLOSED: yes | no
B1_D3_FIREWALL_COMPATIBLE: yes | no
B2_CROSS_REGIME_AND_CENSORING_GUARD_CLOSED: yes | no
B3_BACKEND_DISPATCH_OBSERVABILITY_CLOSED: yes | no
L1_ENERGY_REPORTING_GUARD_ACCEPTABLE: yes | no
L3_PERCENTILE_SUPPORT_REPORTING_GUARD_ACCEPTABLE: yes | no
L2_FUTURE_SENSITIVITY_CLASSIFICATION_ACCEPTABLE: yes | no
PROTECTED_BIOMETRIC_OUTCOMES_REQUIRED_FOR_REVIEW: no
PLATFORM_MATERIALIZATION_CURRENTLY_ADMISSIBLE: yes | no
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
```

`PLATFORM_MATERIALIZATION_CURRENTLY_ADMISSIBLE: yes` is permitted only if B1-B3 are all closed and no new pre-materialization blocker is raised. It is **not** permission to execute Phase A.

## Consequence of ACCEPT

A focused ACCEPT closes only the three construct-validity blockers and permits the next prospective preparation stage: select/materialize the target platform, meter and off-device generator; materialize configuration-choice provenance and attestation; identify the exact synthetic generator; and freeze an execution-specific lock.

Canonical Phase A remains blocked until that materialized execution head is complete, exact-head assurances succeed, and any review required by the lock/provenance mechanism is completed.

Protected biometric outcomes remain sealed throughout.
