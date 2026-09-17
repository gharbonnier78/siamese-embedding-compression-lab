# Study 1B — Phase A construct-validity review request v0.1

**Date:** 2026-09-16  
**Scope:** non-outcome, pre-execution review only  
**Repository:** `gharbonnier78/siamese-embedding-compression-lab`  
**PR:** `#50`

## 1. Review purpose

The v0.6 semantic-hardening review accepted N4, N5, R1/N2 and the N6 package rule on exact head `c7d03cdad3bdf460bc6261508f2dc416504c7e4b`. That review explicitly kept `CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE=no` and `CONSTRUCT_VALIDITY_REVIEWED=no`.

This new review asks a different question:

> If Jungle Championship Phase A were executed exactly as specified, would its measurements validly support the bounded engineering claims the benchmark is designed to make?

The review is about the **construct being measured**, not transport/provenance semantics already accepted, not hardware selection, and not protected biometric performance.

## 2. Hard boundary

The reviewer MUST NOT require or open:

- Study 1B SCREEN;
- qualification TEST;
- protected real-route biometric performance;
- representation geometry;
- S4N3;
- canonical Phase A result-bearing execution.

No real platform, power meter, load generator or execution-specific lock is to be selected or frozen as part of this review.

## 3. Normative objects under construct-validity review

Primary objects:

- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_V0_2_2026-09-14.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml`

Review-history/context objects:

- `protocol/reviews/PR50_C7D03CDA_V06_N6_FOCUSED_REREVIEW_VERDICT_2026-09-16.md`
- `protocol/chronicle/STUDY1B_PR50_C7D03CDA_V06_ACCEPT_2026-09-16.yaml`
- `harness-adoption.yaml`

The D1-D3/N4-N6 acceptance is historical context. This review MUST NOT silently reopen it unless a construct-validity finding genuinely depends on a contradiction in those semantics.

## 4. Claim boundary to evaluate

Phase A is intended to support only bounded engineering statements on the eventually frozen target platform and workload, such as:

- memory/RAM feasibility and resident working-set consequences;
- exact dense-search latency and throughput;
- queue/saturation/recovery characterization;
- device-level power and energy under the declared measurement convention;
- structural versus measured consequences of 512D versus 128D under otherwise paired conditions.

Phase A is **not** intended to support:

- biometric accuracy, FMR/FNMR or non-inferiority;
- superiority of 128D as a biometric representation;
- production suitability beyond the frozen characterization envelope;
- validity of ANN/indexed search;
- universal claims across hardware classes or deployment workloads.

Operational thresholds are currently null; unless prospectively frozen before a future execution, Phase A remains characterization-only.

## 5. Construct-validity questions

### CV1 — intervention isolation

Does the Phase A pairing rule isolate the intended intervention — representation dimension 512D versus 128D — while holding hardware, datatype, gallery cardinality, template count, exact-search algorithm, query schedule, backend, thread/affinity configuration, warm-up, measurement window and aggregation policy fixed within a paired configuration?

Check especially that independent 128D materialization and removal of the 512D base matrix prevent hidden memory-residency contamination.

### CV2 — fixed-work search construct

Is `EXACT_DENSE_DOT_PRODUCT_TOP1` with no threshold gating, no candidate pruning, no index and `top_k=1` a valid construct for measuring the dimension-dependent resource consequences of a brute-force exact dense 1:N search?

If accepted, state the boundary explicitly: this does not establish behavior for indexed/ANN search or a complete biometric pipeline.

### CV3 — synthetic payload construct

The benchmark uses deterministic L2-normalized dense synthetic vectors generated from finite normal FP32 values. Is that payload sufficient for the **bounded fixed-work engineering characterization** being claimed?

The reviewer should distinguish:

- properties driven primarily by vector length, memory traffic, dense arithmetic and resident gallery size;
- properties that could materially depend on the numerical/data distribution, sparsity, denormals, cache layout or a real embedding distribution.

The synthetic payload MUST NOT be interpreted as a biometric-performance model. If additional non-protected sensitivity distributions are required before construct validity can be accepted, identify them prospectively rather than opening protected embeddings.

### CV4 — G0/G2 scenario validity

Are G0 and G2 acceptably framed as sensitivity points rather than observed event facts?

- G0: small-working-set control;
- G2: large-gallery memory/bandwidth sensitivity point.

Check whether the contract prevents an infeasible G2 arm from being silently resized, swapped, retyped or moved asymmetrically to different hardware.

### CV5 — endpoint-to-claim alignment

Do the retained endpoints correspond to the engineering constructs claimed?

Review at least:

- raw per-query latency;
- completed throughput;
- queue depth and recovery;
- RAM residency / swap behavior;
- external device-input or wall power;
- total joules per identification;
- diagnostic incremental energy;
- failure/exclusion records;
- temperature/throttling when observable.

Confirm that a 75% coordinate/payload reduction is not permitted to become a 75% latency or energy claim without measurement.

### CV6 — measurement-plane validity

Does the external power plane plus off-device deterministic load generation sufficiently separate device-under-test energy from load-generator cost for the stated device-level claim?

Review the minimum sampling rate, idle-baseline convention, synchronization requirement, total-energy convention and non-clamping of negative diagnostic incremental values.

### CV7 — causal/confounding controls

Are the paired-arm controls sufficient to support a bounded interpretation that observed differences are attributable primarily to representation dimension under the frozen configuration?

Review counterbalanced arm order, five independent process restarts, identical configuration semantics, retained raw samples, failure retention, warm-up exclusion and no runtime tuning/substitution.

### CV8 — generalization and external-validity boundary

Are the generalization limits explicit enough?

A Phase A result should be bound to the exact hardware/runtime/workload/measurement environment. Fleet projections may be extrapolations only after per-device effects are measured and assumptions are stated. No single edge tier or synthetic workload should be presented as universally representative.

### CV9 — characterization versus qualification

Because operational thresholds are currently null, does the contract correctly keep Phase A in `CHARACTERIZATION_ONLY_NO_PASS_FAIL` mode?

If a future pass/fail requirement is desired, confirm it must be prospectively supplied and frozen before the execution to which it applies.

### CV10 — interpretation firewall

Does the contract keep engineering evidence from being promoted into biometric non-inferiority/superiority evidence or into protected Study 1B qualification claims?

## 6. Reviewer is expected to challenge the design

This is not a confirmation exercise. A reviewer may require prospective changes if the proposed measurements do not validly instantiate the intended construct. In particular, the reviewer should explicitly look for:

- a proxy that measures something easier than the intended engineering question;
- hidden confounding between dimension and runtime configuration;
- synthetic-data properties that could materially bias the claimed endpoint;
- endpoints whose operational meaning is weaker than their label suggests;
- scenario assumptions presented too broadly;
- missing sensitivity analysis needed to bound external validity.

Any requested correction remains prospective. Do not execute a target workload to decide how the benchmark should be redesigned.

## 7. Required verdict fields

```text
VERDICT: ACCEPT | ACCEPT_WITH_LIMITATIONS | CHANGES_REQUIRED
CONSTRUCT_VALIDITY_ACCEPTED: yes | no
DIMENSION_ONLY_INTERVENTION_VALID: yes | no
FIXED_WORK_DENSE_SEARCH_CONSTRUCT_VALID: yes | no
SYNTHETIC_DENSE_PAYLOAD_VALID_FOR_BOUNDED_ENGINEERING_CHARACTERIZATION: yes | no
G0_G2_SCOPE_VALID_AS_SENSITIVITY_NOT_EVENT_FACT: yes | no
MEASUREMENT_ENDPOINTS_MATCH_ENGINEERING_CLAIM_SCOPE: yes | no
MEASUREMENT_PLANE_VALID_FOR_DEVICE_LEVEL_ENERGY_CLAIM: yes | no
CONFOUND_CONTROL_SUFFICIENT_FOR_PAIRED_PHASE_A: yes | no
GENERALIZATION_LIMITS_EXPLICIT_AND_ACCEPTABLE: yes | no
CHARACTERIZATION_VS_QUALIFICATION_BOUNDARY_ACCEPTABLE: yes | no
INTERPRETATION_FIREWALL_ACCEPTABLE: yes | no
REQUIRES_PROTOCOL_CHANGE_BEFORE_PLATFORM_MATERIALIZATION: yes | no
PROTECTED_BIOMETRIC_OUTCOMES_REQUIRED_FOR_REVIEW: no
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
```

For `ACCEPT_WITH_LIMITATIONS`, list each limitation and state whether it is a reporting limitation, a future sensitivity requirement, or a blocker before platform materialization.

## 8. Consequence of review

Only an accepted construct-validity review can permit the programme to proceed to **materialization and freezing of the real target hardware / external meter / off-device load generator / configuration provenance / generator identity / execution-specific environment lock**.

Even after construct-validity acceptance, canonical Phase A remains inadmissible until those physical/provenance requirements are actually materialized, frozen and re-assured on an exact execution head.