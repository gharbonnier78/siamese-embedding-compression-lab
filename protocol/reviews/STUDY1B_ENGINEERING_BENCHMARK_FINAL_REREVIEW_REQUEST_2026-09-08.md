# Study 1B — final independent re-review request for PR #50

Date: 2026-09-08

Purpose: obtain a fresh independent verdict on the provenance-aware non-outcome engineering benchmark after the supplemental review identified one remaining pre-lock configuration-choice provenance gap.

Protected biometric SCREEN/TEST outcomes: **DO NOT OPEN**.

Canonical Phase A execution: **BLOCKED** regardless of design verdict until the real platform and provenance-aware execution-specific environment lock are materialized and frozen before target-workload measurements can inform lock-defining choices.

## Immutable review basis

Repository:
https://github.com/gharbonnier78/siamese-embedding-compression-lab

Pull request:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/pull/50

Base commit:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/commit/5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7

Pinned harness:
https://github.com/gharbonnier78/scientific-research-harness/blob/3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98/HARNESS.md

Previous corrected review head `a00de7bf4e6a6c7d108ec8e36430581e0b559b0f`:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/commit/a00de7bf4e6a6c7d108ec8e36430581e0b559b0f

Original independent review (`ACCEPT_WITH_CHANGES`):
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/cb02051ef3bf4a51e3ddc35b8efc391048f21b0e/protocol/reviews/PR50_INDEPENDENT_REVIEW_2026-09-08.md

Supplemental package-v3 review confirmation, with no final verdict:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/e400a1a0057d2f7dbee722350b1c9eb880206217/protocol/reviews/PR50_SUPPLEMENTAL_REVIEW_V3_CONFIRMATION_2026-09-08.md

Provenance-aware environment lock v0.2:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/c86dad3071f94af69e01a31044e1489a1a7f4fc1/protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_2_2026-09-08.yaml

Benchmark v0.3:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/56eb46d085868c18bd74455aba941d0e706f8660/protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml

Prospective S4 result-schema crosswalk:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/5d71ed6fe3007ef87bf03de0100d468cfce04ed3/protocol/schemas/STUDY1B_S4_POWER_RESULT_SCHEMA_CROSSWALK_V0_1_2026-09-08.md

Updated harness adoption manifest:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/c834f79d66e5eadce3e515d6d88d4676b0917d4b/harness-adoption.yaml

Focused assurance test:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/ea9f816d4a9e94a4eea1a48346380f53e8913cc3/tests/test_study1b_engineering_benchmark_contract.py

Supplemental-review/provenance Chronicle:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/3d70b2a7915c093bd8c6bdf2e09069a1198f0d5f/protocol/chronicle/STUDY1B_PR50_SUPPLEMENTAL_REVIEW_AND_PROVENANCE_GUARD_2026-09-08.yaml

Historical S4N1 closed negative result at the prior reviewed head:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/a00de7bf4e6a6c7d108ec8e36430581e0b559b0f/protocol/chronicle/STUDY1B_S4N1_CORE_POWER_CALIBRATION_RESULT_2026-09-06.yaml

Historical S4N2 closed negative result at the prior reviewed head:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/a00de7bf4e6a6c7d108ec8e36430581e0b559b0f/protocol/chronicle/STUDY1B_S4N2_DAGJK20_POWER_4000_RESULT_2026-09-06.yaml

S4 shared-population/t19 clarification:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/f5b54737d8dd32ce071b7afbb467e2c5ec0eed59/protocol/decisions/STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml

The **final corrected review head** is the exact SHA published in the dedicated PR #50 binding comment created after this request and its review-open Chronicle are committed. If the branch head changes after that binding, stop and require a new binding.

## What changed after the supplemental review

The remaining gap at `a00de7bf` was not a runtime-tuning gap but a **pre-lock decision provenance** gap. v0.2/v0.3 now require provenance for each lock-defining choice and apply a label-independent firewall.

Please verify that:

1. hardware, backend, RAM tier, threading/affinity, power mode, load-generator setup, external energy meter/plane and battery policy each require a provenance record;
2. the provenance record captures source/authority, reference, rationale and whether target-workload evidence informed the choice;
3. target Phase A workload measurements, or materially equivalent measurements intended to answer the same comparison question, may not select/tune lock-defining settings before freeze;
4. the rule is explicitly independent of labels such as smoke test, pilot, Phase 0, exploratory run, preview, capacity check or tuning pass;
5. any already-used target-workload information must be declared and forces a newly identified prospective design/execution identity rather than being hidden;
6. a diagnostic run after a fully frozen lock cannot modify that lock; material change requires a new lock and execution identity;
7. canonical Phase A remains blocked until the real environment and configuration-choice provenance are materialized in an immutable execution-specific lock;
8. no CI runner or guessed hardware can substitute for the target platform.

## S4 and schema checks

Also verify that:

- S4N1 and S4N2 remain closed negative and untouched;
- the unresolved causal explanation for the S4N1-to-S4N2 power difference is not used to justify or reverse either negative closure;
- the schema crosswalk is prospective only and correctly states packaged JSON `schema_version: 1` as an integer;
- package-side raw-JSON discrimination uses `kind`, not `entry_type`;
- the S4N1 `lower_95_clopper_pearson` reading note identifies it as a coverage bound, not a power bound;
- no formal significance claim about the S4N1-to-S4N2 power difference is made without paired per-dataset indicators.

## Protected boundary

Do not open SCREEN, qualification TEST, real raw512/random128/PCA128/Siamese128 performance, real route outcomes, representation geometry, or any protected biometric result. Do not launch S4N3 and do not activate an amendment.

## Required verdict

Return one of:

- `ACCEPT_ENGINEERING_BENCHMARK`
- `ACCEPT_WITH_CHANGES`
- `REJECT_OR_REDESIGN`

Then state separately:

- `BENCHMARK_DESIGN_ACCEPTED: yes/no`
- `CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: yes/no`
- `ENVIRONMENT_LOCK_MATERIALIZED: yes/no`
- `CONFIGURATION_CHOICE_PROVENANCE_MATERIALIZED: yes/no`

An accepted design does **not** imply current execution admissibility. With hardware still unbound, the expected execution state is `no` until a real immutable execution-specific lock is supplied and separately checked.
