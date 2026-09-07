# Study 1B — independent review request: S4 power closure and Jungle Championship engineering benchmark

**Date:** 2026-09-07  
**Requested verdict:** `ACCEPT_ENGINEERING_BENCHMARK`, `ACCEPT_WITH_CHANGES`, or `REJECT_OR_REDESIGN`  
**Scope:** closed synthetic S4 power-calibration evidence + proposed non-outcome engineering benchmark  
**Protected biometric SCREEN/TEST outcomes:** **DO NOT OPEN**

## Canonical navigation

Repository: https://github.com/gharbonnier78/siamese-embedding-compression-lab

PR: https://github.com/gharbonnier78/siamese-embedding-compression-lab/pull/50

Pinned harness commit: https://github.com/gharbonnier78/scientific-research-harness/commit/3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98

Pinned HARNESS.md: https://github.com/gharbonnier78/scientific-research-harness/blob/3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98/HARNESS.md

Local adoption manifest: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/harness-adoption.yaml

Engineering benchmark contract: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_1_2026-09-07.yaml

S4N1 final power result: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/protocol/chronicle/STUDY1B_S4N1_CORE_POWER_CALIBRATION_RESULT_2026-09-06.yaml

S4N2 final power result: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/protocol/chronicle/STUDY1B_S4N2_DAGJK20_POWER_4000_RESULT_2026-09-06.yaml

S4N1 plateau diagnostic result: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/protocol/chronicle/STUDY1B_S4N1_POWER_PLATEAU_DIAGNOSTIC_RESULT_2026-09-06.yaml

Residual decision-risk framework: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/protocol/decisions/STUDY1B_S4_RESIDUAL_DECISION_RISK_FRAMEWORK_2026-09-06.yaml

Value-of-information Chronicle: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/protocol/chronicle/STUDY1B_S4_VALUE_OF_INFORMATION_ANALYSIS_2026-09-06.yaml

Jungle Championship scenario capitalisation: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/protocol/chronicle/STUDY1B_JUNGLE_CHAMPIONSHIP_EDGE_SCENARIO_CAPITALISATION_2026-09-07.yaml

Hardware/energy trade-off Chronicle: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/protocol/chronicle/STUDY1B_JUNGLE_CHAMPIONSHIP_HARDWARE_ENERGY_TRADEOFF_2026-09-07.yaml

## What the reviewer is asked to verify

### A. Closed S4 power-calibration record

Verify that the repository preserves the negative synthetic calibration evidence rather than tuning around it.

Expected facts to verify from canonical artifacts:

- S4N1 and S4N2 are both closed negative against the frozen `>= 0.90` power requirement at true `Delta_FNMR = 0.01`.
- S4N1 BEST power is `0.8690`; S4N2 BEST power is `0.8490`.
- S4N2 did not rescue the power deficit and was stopped rather than post-hoc tuned.
- Coverage/degeneracy behavior is kept distinct from power.
- No selector, margin, FMR target, confidence level or protected outcome was changed/opened to obtain a passing result.
- The repository now treats the power deficit as a study-level risk of `NOT DEMONSTRATED`, not as a person-level biometric-error probability.

Do **not** reinterpret negative S4 results as evidence that the real 128D model is inferior. They qualify the decision procedure under the frozen synthetic generator, not real matcher performance.

### B. Transition to non-outcome engineering value analysis

Verify that the transition is scientifically legitimate:

- no S4N3 estimator shopping is launched;
- the working policy is `PASS -> controlled next engineering/qualification stage`, not automatic production release;
- `NOT_DEMONSTRATED -> retain raw512 by default` remains a working engineering policy;
- `C_miss` is treated as foregone/delayed engineering value, not biometric harm;
- raw512 operational fallback validity and real economic values remain engineering inputs, not facts inferred from unopened outcomes.

### C. Jungle Championship benchmark design

Review the benchmark contract for fairness, reproducibility and useful decision value.

Check especially:

1. **Reference pairing:** 512D/raw512 remains the representation reference; Phase A changes dimension only while holding datatype, hardware, search semantics, gallery size and workload fixed.
2. **Protected-data boundary:** deterministic synthetic vectors are used for canonical engineering measurement; no real Study 1B embeddings, scores, SCREEN, TEST or geometry are opened.
3. **RAM feasibility:** local galleries must reside in RAM; measured working set must include process/runtime/index overhead rather than vector payload only.
4. **Peak-flow behavior:** benchmark measures p95/p99, sustained throughput, saturation, queue growth and recovery, not only single-query latency.
5. **CPU vs accelerator:** CPU remains admissible if it satisfies the operational envelope; GPU/NPU is not assumed superior.
6. **Energy:** measure device-level power/energy where possible; 75% fewer coordinates must not be converted into a 75% energy claim.
7. **Battery:** autonomy uses measured/estimated average power and usable battery energy with explicit assumptions.
8. **Quantization:** FP16/INT8 are separate interventions and are not conflated with dimensional compression.
9. **ANN/indexing:** approximate/indexed search that may change returned identities remains outside Phase A and cannot silently replace exact-search semantics.
10. **Fleet count:** device count scales fleet BOM/memory/synchronization/energy effects only after per-device effects are established; it is not conflated with local observation flow.
11. **Missing operational thresholds:** latency/QPS/battery/headroom thresholds remain unset rather than invented; initial execution characterizes the envelope unless thresholds are prospectively supplied.

## Reviewer challenge questions

Please actively try to falsify the design rather than merely confirm it.

- Is any protected biometric information accidentally needed by the proposed engineering benchmark?
- Does the synthetic-vector workload reproduce enough of the memory and compute behavior for the intended engineering claim?
- Are there hidden confounders that would make 512D-versus-128D attribution invalid?
- Is G2 (`500k whitelist + 10k blacklist`, 3 templates, FP32) a reasonable central sensitivity point while clearly remaining a scenario rather than an event fact?
- Should Phase A include G1 or G3 immediately, or is G2-first the smallest sufficient benchmark?
- Is an external wall-power measurement required for energy claims, with internal CPU/GPU telemetry used only as supporting diagnostics?
- Which result fields must be captured to make the benchmark replayable on another edge platform?
- Are any decision thresholds required before execution, or is characterization-first acceptable at this stage?

## Required reviewer output

Please return:

```text
VERDICT: ACCEPT_ENGINEERING_BENCHMARK | ACCEPT_WITH_CHANGES | REJECT_OR_REDESIGN

S4_POWER_RECORD:
- correct / incorrect / incomplete
- key findings

ENGINEERING_BENCHMARK:
- scientific-boundary assessment
- fairness/confounding assessment
- RAM/load/energy/battery assessment
- reproducibility assessment

BLOCKING_CHANGES:
- ...

NON_BLOCKING_RECOMMENDATIONS:
- ...

BOUNDARY_CONFIRMATION:
- SCREEN opened? yes/no
- qualification TEST opened? yes/no
- real route performance opened? yes/no
- representation geometry opened? yes/no
- S4N3 launched? yes/no
```

A reviewer limitation must be reported explicitly. Missing evidence must not be silently replaced by assumptions.

## Author-side intended next action

No canonical engineering benchmark execution before independent review acceptance (or explicit accepted changes). After review, execute the smallest Phase A benchmark first. Engineering results are allowed to be opened and archived because they are non-biometric engineering evidence, but they must never be promoted to evidence of biometric non-inferiority.