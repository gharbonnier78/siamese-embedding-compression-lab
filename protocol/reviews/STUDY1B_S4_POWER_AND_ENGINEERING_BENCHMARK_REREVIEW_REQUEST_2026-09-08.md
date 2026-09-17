# Study 1B — independent re-review request after PR #50 corrections

**Date:** 2026-09-08  
**Purpose:** verify closure of the 2026-09-08 `ACCEPT_WITH_CHANGES` blockers before any canonical engineering benchmark execution.  
**Protected biometric SCREEN/TEST outcomes:** **DO NOT OPEN**.  
**Canonical Phase A execution:** **still blocked** until independent re-review acceptance **and** a materialized target-hardware environment lock.

## Immutable navigation

Repository:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab

Pull request:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/pull/50

Base commit: `5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7`  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/commit/5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7

Pinned harness commit: `3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`  
https://github.com/gharbonnier78/scientific-research-harness/blob/3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98/HARNESS.md

Original reviewed head: `ab7f3d099ba0bd26dd1158afa8f80e5b66bf801d`  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/commit/ab7f3d099ba0bd26dd1158afa8f80e5b66bf801d

Archived independent review (`ACCEPT_WITH_CHANGES`) as committed at `cb02051ef3bf4a51e3ddc35b8efc391048f21b0e`:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/cb02051ef3bf4a51e3ddc35b8efc391048f21b0e/protocol/reviews/PR50_INDEPENDENT_REVIEW_2026-09-08.md

Corrected benchmark v0.2 as committed at `43aac8b86fae63efcd90a84918f13bf1843f98c6`:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/43aac8b86fae63efcd90a84918f13bf1843f98c6/protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_2_2026-09-08.yaml

Environment-lock contract as committed at `8741e08c9f026a8537bffda65a39c49e4fbedf16`:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/8741e08c9f026a8537bffda65a39c49e4fbedf16/protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_1_2026-09-08.yaml

S4 shared-population / t19 clarification as committed at `f5b54737d8dd32ce071b7afbb467e2c5ec0eed59`:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/f5b54737d8dd32ce071b7afbb467e2c5ec0eed59/protocol/decisions/STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml

Focused contract tests as committed at `7cab959c005ad2d93f63859c63a481265bd73d45`:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/7cab959c005ad2d93f63859c63a481265bd73d45/tests/test_study1b_engineering_benchmark_contract.py

Updated local harness adoption manifest as committed at `ce03f8d004bc5c5ea6b44f5b81c9dbc342635db7`:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/ce03f8d004bc5c5ea6b44f5b81c9dbc342635db7/harness-adoption.yaml

Historical S4N1 negative result at the immutable original review head:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/ab7f3d099ba0bd26dd1158afa8f80e5b66bf801d/protocol/chronicle/STUDY1B_S4N1_CORE_POWER_CALIBRATION_RESULT_2026-09-06.yaml

Historical S4N2 negative result at the immutable original review head:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/ab7f3d099ba0bd26dd1158afa8f80e5b66bf801d/protocol/chronicle/STUDY1B_S4N2_DAGJK20_POWER_4000_RESULT_2026-09-06.yaml

Frozen S4N2 contract at the immutable original review head:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/ab7f3d099ba0bd26dd1158afa8f80e5b66bf801d/protocol/simulations/STUDY1B_S4N2_DAGJK20_CALIBRATION_V0_1_2026-09-06.yaml

S4N2 implementation showing the `t.ppf(0.975, df=19)` construction and S4N1-compatible known-truth generation, at the immutable original review head:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/ab7f3d099ba0bd26dd1158afa8f80e5b66bf801d/src/siamese_compression_lab/study1b_s4n2_dagjk.py

Residual decision-risk framework at immutable original review head:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/ab7f3d099ba0bd26dd1158afa8f80e5b66bf801d/protocol/decisions/STUDY1B_S4_RESIDUAL_DECISION_RISK_FRAMEWORK_2026-09-06.yaml

**Final corrected review head:** use the exact immutable PR head SHA stated in the PR body and the dedicated re-review binding comment created after this request. If the PR head changes after that binding, stop and require a new binding.

## Blocker-by-blocker verification requested

1. **Immutable navigation.** Verify that this re-review request uses immutable artifact URLs rather than mutable branch URLs for normative review objects.
2. **Environment lock.** Verify the complete hardware/software/load-generator/power-meter capture contract and that canonical execution remains blocked until all required values are materialized non-null in an immutable execution-specific lock. Do not require invented hardware values now.
3. **Exact Phase A semantics.** Verify `EXACT_DENSE_DOT_PRODUCT_TOP1`, `top_k=1`, no threshold gating, no ANN/index, and identical workload/configuration across dimensions.
4. **G2 RAM infeasibility.** Verify that 512D inability to fit in RAM is retained as `RAM_INFEASIBLE_ON_TIER`, with no swap, smaller-gallery substitution, datatype change or one-arm-only tier move.
5. **Energy plane and baseline.** Verify external device-input/wall measurement is canonical for strong energy claims, on-chip telemetry is diagnostic, and total versus idle-subtracted joules/identification are explicitly distinct.
6. **Post-hoc threshold guard.** Verify null operational thresholds imply characterization-only, and any later threshold applies only prospectively to a new execution.
7. **Measurement statistics.** Verify repetitions, warm-up, measurement duration, raw-sample retention, percentile support rules, dispersion reporting and failed-run retention are frozen.
8. **Load generator placement.** Verify canonical off-device placement and separate device-boundary versus client RTT reporting.
9. **Scenario provenance.** Verify G2 is explicitly `SCENARIO_ONLY_NOT_EVENT_FACT` and G0 is added only as a small-working-set engineering control.
10. **S4 clarification.** Verify S4N1/S4N2 share one deterministic synthetic population, represent two uncertainty procedures rather than two independent generator replications, use t19 critical value `2.0930240544083087` for S4N2, and stop S4N3 because of estimator-shopping risk rather than accumulated independent evidence.

Also check the non-blocking corrections already capitalized: summary-facing `PROSPECTIVELY_PREFERRED` terminology, exact Monte Carlo power intervals, local limitation of the `0.0310/0.0510` value-of-power terms, G0 control, derived-versus-measured payload labeling, finite synthetic values, duty-cycle conditioning, and quantization top1-change diagnostic.

## Important interpretation of the environment-lock status

The target edge hardware has not yet been supplied by engineering authority. Therefore the environment-lock artifact is intentionally a **complete lock contract whose execution-specific values are still unbound**. This is not permission to run. The reviewer should distinguish:

- **benchmark-design acceptance**, which can be granted if the lock mechanism is adequate; from
- **execution admissibility**, which remains blocked until the actual device/meter/load-generator environment is populated and frozen.

No canonical Phase A run may occur on an arbitrary CI runner or guessed edge platform.

## Required verdict

Return one of:

- `ACCEPT_ENGINEERING_BENCHMARK`
- `ACCEPT_WITH_CHANGES`
- `REJECT_OR_REDESIGN`

Then state separately:

- `BENCHMARK_DESIGN_ACCEPTED: yes/no`
- `CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: yes/no`
- `ENVIRONMENT_LOCK_MATERIALIZED: yes/no`

The expected current state, unless engineering hardware is supplied during review, is that benchmark design may be accepted while canonical execution remains **not admissible** because the environment lock is not yet materialized.

## Protected boundary

The reviewer MUST NOT open SCREEN, qualification TEST, real raw512/random128/PCA128/Siamese128 performance, real route outcomes, or representation geometry. The reviewer MUST NOT launch S4N3 or activate an amendment.

If any required immutable object is inaccessible, report it as missing evidence. Do not replace it with memory, branch state, prior conversation or author prose.
