# Independent review — PR #50

**Reviewed head:** `ab7f3d099ba0bd26dd1158afa8f80e5b66bf801d`
**Base:** `5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7`
**Pinned harness:** `3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`
**Review date:** 2026-09-08
**Role:** independent reviewer. No authorship, no design optimisation on the author's behalf, no inference of intended conclusions from prior project conversation.

```
VERDICT: ACCEPT_WITH_CHANGES
```

---

## Objects actually loaded

Read at the immutable head `ab7f3d0`:

- PR #50 conversation and body
- `protocol/reviews/STUDY1B_S4_POWER_AND_ENGINEERING_BENCHMARK_REVIEW_REQUEST_2026-09-07.md`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_1_2026-09-07.yaml`
- `protocol/chronicle/STUDY1B_S4N1_CORE_POWER_CALIBRATION_RESULT_2026-09-06.yaml`
- `protocol/chronicle/STUDY1B_S4N2_DAGJK20_POWER_4000_RESULT_2026-09-06.yaml`
- `protocol/chronicle/STUDY1B_S4N1_POWER_PLATEAU_DIAGNOSTIC_RESULT_2026-09-06.yaml`
- `harness-adoption.yaml`

Read at the mutable branch `agent/study1b-preregistration-20260827` only, because no immutable link was available (see BLOCKING-1):

- `protocol/decisions/STUDY1B_S4_RESIDUAL_DECISION_RISK_FRAMEWORK_2026-09-06.yaml`

**Not loaded. Findings below do not rest on them:** pinned `HARNESS.md`; `STUDY1B_S4_VALUE_OF_INFORMATION_ANALYSIS_2026-09-06.yaml`; the frozen S4N1/S4N2 simulation contracts; the coverage-checkpoint chronicles; the Jungle Championship scenario-capitalisation and hardware/energy chronicles; the review-open chronicle `CHRON-20260907-035`; `src/`; `tests/`; CI run logs and raw artifacts.

---

## S4_POWER_RECORD

**Assessment: correct but incomplete.**

The recorded numbers are internally consistent and the closure decision is sound. Three gaps in the record are listed below; none of them overturns `CLOSED_NEGATIVE`.

### Verified

1. **Numbers reconcile across all four artifacts.** S4N1 at true `Delta_FNMR = 0.01`: FIXED_SEED 0.8655, VALIDATION_BEST 0.8690, VALIDATION_MEDIAN 0.8695. S4N2: 0.8470 / 0.8490 / 0.8535. The `comparison_to_s4n1` block in the S4N2 record reproduces the S4N1 values exactly. The residual-decision-risk framework's `beta = 1 - power` column is arithmetically correct in all six cells, and its 3.10 / 5.10 percentage-point target gaps follow from the values it cites.

2. **No post-hoc rescue is present in the record.** Margin (0.03), target FMR (0.01), one-sided level (0.975), selector set and gate (0.90 at both truth cells) are identical in the S4N1 record, the S4N2 record and the residual framework. `prohibited_rescue_actions` in S4N1 explicitly bars increasing dataset count to seek a pass, reordering selectors, and using transport sensitivity to override core failure. S4N2 bars group-count tuning and selector substitution. The least-failing selector was not promoted: `preferred_candidate: null` in both.

3. **Coverage is kept distinct from power, and the record says so in the right direction.** S4N2's `interpretation_guardrails` state that high coverage does not imply high power, and that zero degeneracy means zero invalid statistical calculations, not zero biometric errors. Coverage passes while power fails, which is exactly the pattern a conservative interval produces.

4. **Power is not reinterpreted as person-level harm.** The residual framework's `key_statement` conditions beta explicitly on the frozen synthetic truth and states it is not a probability of false match, false non-match or person-level harm. `biometric_safety_inference_from_power_gap: prohibited` is recorded under the conservative fallback. The S4N2 record adds that S4N2 being lower-powered than S4N1 does not mean the compressed model is worse. I attempted to find a place where a power number is carried into a biometric claim and did not find one.

5. **Monte Carlo noise does not rescue either campaign.** The records report Clopper-Pearson bounds on coverage but not on power, so I computed it. At n = 4000 the binomial standard error at p ≈ 0.87 is ≈ 0.0053. The most favourable single cell in the entire campaign is S4N1 VALIDATION_MEDIAN at 0.8695; the 0.90 gate is roughly 5.7 standard errors above it, and the 95 % upper bound is ≈ 0.880. For S4N2's most favourable cell (0.8535) the gate is ≈ 8.3 standard errors away. The negative closure is robust to simulation error by a wide margin.

### FINDING S4-A — "BEST" in the summaries means the candidate named `VALIDATION_BEST`, not the highest observed power

The PR body and the review request both state "S4N1 BEST: 0.8690" and "S4N2 DAGJK20 BEST: 0.8490". In both campaigns the highest observed power at `Delta_FNMR = 0.01` belongs to `S4N_VALIDATION_MEDIAN` (0.8695 and 0.8535), not to `S4N_VALIDATION_BEST`.

Reporting the prospectively preferred rule rather than the maximum is the correct scientific choice and I endorse it. The problem is only the label: a reader outside the repository will read "BEST: 0.8490" as "the best we achieved was 0.8490", which understates S4N2's maximum by 0.45 percentage points. Rename to `PROSPECTIVELY_PREFERRED` in all summary-facing text and state the maximum alongside it.

### FINDING S4-B — S4N1 and S4N2 share one simulated population; they are not two independent failures

The S4N2 record reports `point_error_mean` and `point_error_sd` values that are identical to S4N1's `mean_test_estimation_error` and to the plateau diagnostic's `point_error_sd`, to full floating-point precision, in all six selector-by-truth cells. Examples: `0.00011017500000000025` vs `0.000110175`; `-0.00008045000000000907` vs `-0.00008045`; `point_error_sd` `0.005158831529104863` in both S4N2 and the diagnostic.

The only way this occurs is that S4N2 re-evaluated the same synthetic datasets and the same point estimates as S4N1, changing only the uncertainty estimator (bootstrap to DAGJK20). That is a good design for isolating the estimator effect, and I am not criticising it. Two consequences are unrecorded:

- The record never states the reuse. A reader would reasonably assume S4N2 drew fresh data. `frozen_source_boundary` gives graph and manifest hashes but no statement that the synthetic dataset population is the S4N1 population. Add an explicit field.
- The residual framework's stop rationale reads: "Two prospectively frozen uncertainty procedures have now failed the same 0.90 power target." Accurate as to procedures, but the sentence invites the stronger reading that two independent lines of evidence failed. They did not. One generator, one dataset population, two interval estimators. Neither campaign probes generator misspecification at all. The stop decision remains defensible on post-hoc-optimisation grounds, but the rationale should be restated in terms of estimator search risk rather than accumulated independent evidence.

### FINDING S4-C — the plateau diagnostic predicts S4N2 should have gained power; it lost 2.0 points, and nothing reconciles this

This is the substantive gap. The diagnostic localises the plateau to conservative uncertainty spread: for `VALIDATION_BEST`, median UCB97.5 headroom ≈ 0.014015, bootstrap SE to repeated-sampling SD ratio ≈ 1.391, and it computes that scaling headroom to ≈ 94.6 % of its present value would have reached 0.90.

S4N2's DAGJK20 estimator is **less** conservative on the same data by that same measure: `median_se_to_point_error_sd_ratio` ≈ 1.267 versus 1.391, and `dagjk_se_median` ≈ 0.006528 versus the bootstrap's ≈ 0.007164. On the median-headroom mechanism the diagnostic proposes, a tighter interval on identical point estimates should raise power. Observed power fell from 0.8690 to 0.8490.

The record notes the drop and cautions against misreading it as model degradation, which is right, but it offers no mechanism. The likeliest explanation is dispersion rather than location: a 20-group delete-a-group jackknife produces a noisy SE, so the right tail of the SE distribution can destroy power at the decision boundary even when the median SE shrinks. A second candidate is the quantile multiplier: the candidate is named `S4N2_DAGJK20_T975`, implying a t quantile, and with 19 degrees of freedom that is 2.093 against the normal 1.960, a 6.8 % inflation. The record never states which multiplier was used.

Both are testable directly from the already-archived shards, with no new simulation and no boundary movement. Required before the S4 record can be called complete:

- state the quantile multiplier and degrees of freedom used by S4N2;
- report the dispersion of the SE across datasets for both estimators, not only its median and mean;
- report the joint behaviour of SE and point estimate near the decision boundary for both estimators.

Until that is recorded, the repository's causal account of the plateau is contradicted by its own next experiment. The closure is unaffected. The methodological conclusion drawn from the closure is not yet supported.

### FINDING S4-D — the value-of-power arithmetic implicitly fixes the acceptable state at exactly `Delta_FNMR = 0.01`

`incremental_value_of_power` computes `q * (0.90 - 0.8690) * C_miss`. That treats power at the single point `Delta = 0.01` as the power that matters. The acceptable region is `Delta_FNMR < 0.03`, and power over that region is nowhere near constant: the same records show power ≈ 0.999 at `Delta = 0`. If the true acceptable state is likelier near 0 than at 0.01, the expected missed-demonstration cost is much smaller than the formula implies, and the case for buying more power weakens accordingly.

The framework already lists "whether a decision-relevant effect other than Delta_FNMR=0.01 should be prospectively justified" as a required input, so the gap is acknowledged. It should also be marked as a stated limitation on the `0.0310` and `0.0510` figures themselves, since those two numbers are the ones that will travel into a decision brief.

---

## ENGINEERING_BENCHMARK

### Scientific-boundary assessment: passes

I tried to find a protected input the benchmark needs and could not. Working-set size, memory traffic, dense-search throughput, latency percentiles and device energy are functions of `(N, d, dtype, hardware, access pattern, concurrency)`. None of them requires real embeddings, real scores or real identity labels. `synthetic_data_contract` forbids all three. The engineering-versus-biometric firewall in `interpretation_rules` is stated in both directions: no engineering result may become evidence that 128D is biometrically acceptable, and no protected outcome may be opened to select an engineering configuration.

The opening policy (engineering outputs may be archived after execution because they are non-biometric) is consistent with that firewall and I have no objection to it.

One residual, addressed in BLOCKING-6: the contract forbids using protected outcomes to tune the configuration, but nothing in it forbids setting the currently-null operational thresholds *after* seeing Phase A results. That is the same post-hoc hazard the S4 record spent considerable effort avoiding, reappearing on the engineering side.

### Fairness and confounding assessment

**Correct as written:** the reference pairing (Phase A varies dimension only, holding datatype, hardware, search semantics, gallery cardinality and workload fixed); quantization held out as a separate intervention in Phase C; ANN and indexed search held out as a separate qualification in Phase E; the refusal to assume accelerator superiority; the refusal to convert 75 % fewer coordinates into a 75 % energy claim.

**The confounder the design does not address (BLOCKING-3):** cosine similarity between random unit vectors concentrates as dimension grows, with spread of order `1/sqrt(d)`. Random 128D vectors therefore produce a score distribution roughly twice as wide as random 512D vectors. If any part of the measured path is threshold-gated rather than fixed-work top-k, the 128D arm will produce systematically more above-threshold candidates and more downstream work, purely as an artifact of dimension interacting with the synthetic generator. That is a dimension-correlated confounder in the exact place the contract claims to isolate dimension. It is also invisible in a fixed-work top-k design, which is why the contract must say which one Phase A uses.

**A second asymmetry (BLOCKING-4):** at G2 the two arms are not in the same memory regime. 510,000 identities at 3 templates is 1,530,000 vectors, so the 512D FP32 gallery is 3.13 GB (2.92 GiB) and the 128D gallery is 783 MB (0.73 GiB). `gallery_residency: RAM_REQUIRED` is declared, but the contract has no rule for the case where the 512D arm does not fit in the RAM of the device under test. On a modest edge device that case is likely, and it is precisely the case the Jungle Championship scenario exists to explore. If it occurs, Phase A cannot produce a paired measurement and the contract gives no declared handling.

### RAM, load, energy and battery assessment

**RAM.** The requirement that the measured working set include process, runtime and index overhead rather than vector payload alone is correct and is the right instinct. One claim-hygiene point: `vector_payload_bytes` is exactly 4x by construction and is arithmetic, not measurement. Mark it as derived so that the report does not present a tautology as a finding. The informative quantities are the non-payload terms and the degree to which throughput and energy fail to scale by 4x.

**Load.** The steady grid tops out at 8 QPS with a 16 QPS burst. A rough sanity check suggests these points may straddle the two arms asymmetrically: a 2.92 GiB gallery streamed once per query at an optimistic 10 GB/s effective bandwidth implies roughly 0.3 s per query, so a per-device ceiling of order a few QPS for the 512D arm and roughly four times that for 128D. Treat those numbers as order-of-magnitude only, since no hardware is declared. If they are even approximately right, the 16 QPS burst sits far past saturation for 512D and inside the operating envelope for 128D, so `queue_recovery_time_after_burst` would be measurable for one arm and unbounded for the other. The `extension_rule` covers the case where saturation is not reached at the top point; it does not cover this asymmetry.

**Energy.** `joules_per_identification` is not well defined until two choices are declared. First, measurement plane: external wall or DC measurement should be canonical, with on-chip telemetry as diagnostic only. On many parts the on-chip counters exclude DRAM and always exclude board and supply losses, and DRAM is exactly where a 2.92 GiB versus 0.73 GiB difference shows up, so telemetry-only energy would bias the comparison in favour of the arm the benchmark is evaluating. Second, baseline: total energy versus idle-subtracted energy differ by a large factor at low QPS, and the contract measures `idle_power_W` without saying which convention `joules_per_identification` uses. Those two numbers drive the fleet economics downstream.

**Battery.** `estimated_autonomy_hours` from `usable_capacity_Wh` and average power is the right shape and the contract already requires explicit assumptions. Add duty cycle as a named input, since autonomy at 0.25 QPS and at saturation differ by more than any 512D-versus-128D effect, and add the load profile that each autonomy figure is conditioned on.

### Reproducibility assessment: currently insufficient

This is the weakest part of the contract. The benchmark's entire output is hardware-dependent measurement, and the contract declares no hardware. There is no device, core count, RAM size or speed, memory bandwidth, OS or kernel, BLAS or backend library, thread count, NUMA topology, frequency governor, thermal environment, or library and interpreter versions. `harness-adoption.yaml` compounds this with `execution.environment_lock: null`.

On a memory-bound similarity search, thread count and BLAS backend alone can move throughput by more than the effect under study. Without an environment lock, Phase A cannot support an attribution claim about dimension, and no other platform can replay it.

There is also no measurement statistics policy: no repetition count, no warm-up or discard rule, no run duration per load point, and no statement of how many samples back a p99. A 30-second burst at 16 QPS yields roughly 480 samples, which makes p99 approximately the fifth-worst observation and very noisy.

### Answers to the reviewer challenge questions

- **Protected information needed?** No. Verified above.
- **Are synthetic vectors sufficient?** For memory footprint, memory traffic and dense-search compute, yes, provided the generator guarantees finite normal-range values. Denormals and NaNs can change floating-point throughput substantially on some hardware, and "normalized" does not by itself exclude them. For anything threshold-gated, no, for the concentration reason in BLOCKING-3.
- **Hidden confounders?** Two, both above: score-distribution asymmetry and memory-regime asymmetry at G2.
- **Is G2 a reasonable central point?** Yes as a sensitivity point, and it is correctly framed as a scenario. But `G3_stress` carries `provenance: SCENARIO_ONLY_NOT_EVENT_FACT` while `G2_central_full`, the primary, carries no such marker. The unmarked primary is the one that will leak into a briefing as a fact.
- **Should Phase A include G1 or G3?** Not G3. But add **G0** to Phase A. It is 30,000 vectors, roughly 61 MB at 512D and 15 MB at 128D, so it costs almost nothing to run and gives a small-working-set control point. Without it the report cannot distinguish a bandwidth-driven 512D-versus-128D delta from a compute-driven one, which is the first question any reader will ask. G1 can wait for Phase B.
- **Is external wall-power measurement required?** Yes, for any claimed energy figure. Internal telemetry as supporting diagnostic only. Reasoning above.
- **Which fields make it replayable elsewhere?** The full environment lock (device, CPU model, cores and threads used, RAM size and speed, OS and kernel, BLAS/backend and version, thread count, governor, ambient temperature, library and interpreter versions), plus generator seed and vector-generation code hash, gallery construction parameters, search semantics including exact top-k value and whether any threshold is applied, load generator location and its own resource use, repetition count and warm-up policy, raw per-query latency samples or their full distribution rather than only summary percentiles, and the energy measurement plane and baseline convention.
- **Are thresholds required before execution?** No. Characterisation-first is the right call and is better than inventing thresholds. It requires the guard in BLOCKING-6.

---

## BLOCKING_CHANGES

1. **Re-pin the review request's own navigation to the immutable head.** `STUDY1B_S4_POWER_AND_ENGINEERING_BENCHMARK_REVIEW_REQUEST_2026-09-07.md` links eight artifacts by mutable branch `agent/study1b-preregistration-20260827`. The harness re-pin note in `harness-adoption.yaml` states that harness `3b109ad` was adopted precisely to require immutable artifact URLs, so the review request violates the contract it cites. This is not theoretical: it forced me to read the residual decision-risk framework at a mutable ref, which I have flagged in my review basis.

2. **Add a full environment lock to the benchmark contract**, and resolve `execution.environment_lock: null` in `harness-adoption.yaml` for benchmark execution. Fields listed under the reproducibility question above. No canonical Phase A execution should occur without it.

3. **Declare Phase A search semantics precisely, and eliminate the score-distribution confounder.** State whether Phase A is fixed-work top-k with no thresholding (recommended) or threshold-gated. If threshold-gated, declare the per-arm threshold and report above-threshold candidate counts per arm as a first-class result so the confounder is visible.

4. **Add a declared rule for the case where the 512D G2 gallery does not fit in the device's RAM** (3.13 GB payload before overhead). State whether the run is reported as a 512D infeasibility result, moved to a larger tier, or falls back to G0/G1 for the paired comparison. Do not leave this to run-time improvisation.

5. **Declare the energy measurement plane and baseline convention.** External wall or DC measurement canonical, on-chip telemetry diagnostic only; and state explicitly whether `joules_per_identification` is total or idle-subtracted.

6. **Add a post-hoc threshold guard to `current_missing_thresholds`.** Thresholds left null may be supplied prospectively before an execution, or characterised without conversion into PASS/FAIL, but may not be set after seeing Phase A results and then applied retroactively to that same execution. Mirror the language already used in `prohibited_rescue_actions` in the S4N1 record.

7. **Declare the measurement statistics policy:** repetitions per configuration, warm-up and discard rule, run duration per load point, sample count backing each percentile, and reporting of dispersion across repetitions rather than a single value.

8. **Declare load generator placement and accounting.** If it runs on the device under test, its CPU, memory and power contribution must be measured and reported separately. If off-device, state the link and its contribution to measured latency.

9. **Mark `G2_central_full` with `provenance: SCENARIO_ONLY_NOT_EVENT_FACT`,** matching G3. It is the primary configuration and the one most likely to be quoted.

10. **Record the S4N1/S4N2 shared-population fact and the S4N2 quantile multiplier**, and restate the estimator-stop rationale in terms of post-hoc optimisation risk rather than accumulated independent evidence. See FINDING S4-B and S4-C.

## NON_BLOCKING_RECOMMENDATIONS

- Rename summary-facing "BEST" to "PROSPECTIVELY_PREFERRED" and report the maximum alongside it (FINDING S4-A).
- Add Monte Carlo standard error and a Clopper-Pearson interval on power as first-class fields in power result files, as already done for coverage. At n = 4000 the MCSE is ≈ 0.005. The current records make the gate a bare point comparison.
- Add the SE-dispersion and boundary-behaviour analysis described in FINDING S4-C. It uses archived shards only and opens nothing.
- Add G0 to Phase A as a small-working-set control.
- Mark `vector_payload_bytes` as analytically derived rather than measured.
- Constrain the synthetic generator to finite normal-range values and state the distribution.
- Add duty cycle and the conditioning load profile as named inputs to every autonomy figure.
- In Phase C, require that any change in returned top-k versus FP32 be recorded as a diagnostic. "No identity change" is the property that would have to hold for quantization to be a pure engineering optimisation, so it should be measured rather than assumed.
- Attach a stated-limitation note to the `0.0310` and `0.0510` incremental-power figures (FINDING S4-D).

## BOUNDARY_CONFIRMATION

Based on the declarations in the artifacts I read, and consistent across all of them. I verified declared state in documents; I did not execute anything, read `src/`, or inspect raw run artifacts, so this confirms consistency of the record rather than the physical absence of the data.

```
SCREEN opened?                      no
qualification TEST opened?          no
real route performance opened?      no
representation geometry opened?     no
S4N3 launched?                      no
amendment activated?                no
S4N1 status                         CLOSED_NEGATIVE
S4N2 status                         CLOSED_NEGATIVE
```

## REVIEWER_LIMITATIONS

Reported explicitly, not silently replaced by assumptions.

1. **CI state not verified.** The PR states that Engineering Assurance and Power Design Diagnostic were green at review opening while CI, Research Assurance and Non-outcome Preflight were still running. I could not observe check status on the reviewed head. Any final acceptance should bind CI status at `ab7f3d0` separately.
2. **One artifact read at a mutable ref.** The residual decision-risk framework was read at branch `agent/study1b-preregistration-20260827`, not at `ab7f3d0`, for the reason in BLOCKING-1. If the branch has advanced, my reading of that file is not pinned to the reviewed head.
3. **Raw artifacts not independently recomputed.** The SHA-256 digests recorded for `power_4000.json` and the diagnostic bundle are reproduced in the chronicles as self-reported. I did not download the GitHub artifacts or recompute the digests, so artifact integrity is attested, not independently verified by me.
4. **Frozen contracts not read.** S4N1's and S4N2's frozen simulation contracts, and the coverage-checkpoint chronicles, were not loaded. My finding that no gate was moved rests on cross-comparison of the four result and decision artifacts, which agree, and not on inspection of the frozen contracts themselves.
5. **No independent re-simulation.** All power figures are taken from the archived records. My Monte Carlo error and memory-footprint calculations are analytic checks over those reported values.
6. **Value-of-information analysis not read.** `STUDY1B_S4_VALUE_OF_INFORMATION_ANALYSIS_2026-09-06.yaml` was not loaded. FINDING S4-D applies to the residual framework's formulas as written and may already be addressed there.

## VERDICT RATIONALE

`ACCEPT_WITH_CHANGES`, not `ACCEPT_ENGINEERING_BENCHMARK` and not `REJECT_OR_REDESIGN`.

The S4 closure is the strong part of this PR. Two prospectively frozen campaigns failed a prospectively frozen gate, the failures were preserved rather than tuned away, the least-failing selector was not promoted, and the transition to decision analysis keeps study-level non-demonstration separate from person-level biometric risk throughout. I looked for a post-hoc rescue and did not find one. The one real methodological gap, FINDING S4-C, weakens the repository's causal explanation of the plateau, not the closure itself.

The benchmark is directionally right. Its firewalls, its refusal to conflate quantization or ANN with dimensional compression, and its refusal to invent thresholds are all correct and unusually disciplined. It is not yet executable as a canonical benchmark: it declares no environment for a measurement whose every output is environment-dependent, it leaves the two arms in different memory regimes at G2 with no rule for the infeasible case, and it leaves a dimension-correlated score-distribution confounder unaddressed in exactly the phase that claims to isolate dimension. Those are specification gaps in a contract, fixable without redesign, which is why the verdict is `ACCEPT_WITH_CHANGES` rather than `REJECT_OR_REDESIGN`.

The changes in BLOCKING 1 through 9 should land before canonical Phase A execution. BLOCKING-10 is a record amendment and can land in parallel.
