# PR #50 — Independent Phase A Construct-Validity Review

## Review metadata

- **Exact head reviewed:** `b5720dd7e2031e0ac090ae4f5ea4c09fb0a05cc5`
- **Base:** `5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7`
- **Pinned harness:** `gharbonnier78/scientific-research-harness@3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`
- **Package filename:** `PR50_B5720DD7_PHASE_A_CONSTRUCT_VALIDITY_REVIEW_2026-09-16.zip`
- **Package SHA-256:** `fe4ff0af8bec437e17efb10c809d9113f8d2c162ab416c8dd93a2abe5c7566de` — matches expected
- **Reviewer:** AI-assisted independent reviewer (Claude), single session
- **Review date:** 2026-09-16

### Independence statement

I did **not** design the Phase A benchmark, prepare this review package, or author any of the reviewed protocol changes.

One independence qualification must be disclosed rather than glossed. I authored the prior independent reviews in this series on heads `ab7f3d0`, `f5d748`, `022e8f`, `cb124244` and `c7d03cda`. Several features of the design now under construct-validity review exist because of findings in those reviews: the G0 control, the `infeasible_arm_rule`, the off-device load generator, the external energy plane, the percentile support rules, the `ANALYTICALLY_DERIVED_NOT_MEASURED_FINDING` classification of payload bytes, the `SCENARIO_ONLY_NOT_EVENT_FACT` marker on G2, and the fixed-work top-1 semantics that neutralize score concentration.

That creates a specific confirmation risk: a reviewer checking a design against his own earlier recommendations will tend to find it adequate. I have handled it by evaluating the current construct on its merits and by requiring the review to produce **new** findings rather than a checklist of closed ones. The three blockers in this verdict are new and were not raised in any prior cycle. If the programme wants the construct-validity decision to be fully independent of my prior involvement, a second reviewer with no history in this series should confirm it; that is a reasonable precaution and I would not argue against it.

---

## Transport verification

All checks run before any semantic analysis. Independent recomputation used my own implementations, then cross-checked against the bundled verifier.

- **ZIP SHA-256:** `fe4ff0af8bec437e17efb10c809d9113f8d2c162ab416c8dd93a2abe5c7566de` — **matches**.
- **Bundled verifier:** `Construct-validity transport verification PASS: 13 repository sources, N7/N8 satisfied by package construction`, exit 0.
- **Independent 13/13 Git-blob recomputation:** **13/13 match** `git_blob_sha1_expected`, computed as `SHA1("blob " + byte_length + NUL + content)` with my own code.
- **Immutable-source provenance check:** **13/13 provenance-bound.** Every entry carries `git_blob_sha1_expected_source` with `kind: immutable_repository_object`, `head_sha` equal to the manifest head, matching `path`, a `git_object_expression` of the form `b5720dd7…:<path>`, and both an `immutable_blob_api_url` and an `immutable_contents_api_url` pinned by `?ref=b5720dd7…`. No `git_blob_sha1_recomputed` column is present in any entry. **This closes N7 from the `c7d03cda` cycle.** The expected identities are now addressed to the repository rather than asserted, and the `git_object_expression` and contents URL are addresses that resolve independently of whatever hash the author computed.
- **Package contents:** 22/22 `04_PACKAGE_CONTENTS_SHA256.json` entries match on both SHA-256 and byte length. Only the manifest itself and a Python bytecode cache directory are uncovered.
- **Pinned HARNESS verification:** `external_authority/HARNESS.md` now shipped. Git blob SHA-1 `b5354c9c02c91cfa1e6a0b734741cdf78e39ed1d` — **matches**. SHA-256 `a992b6e58fe925747b0e803dfb9012c206e5664c4bd476a6d4d097c2b2f02268` — **matches**. The miniature N7 gap I recorded at `c7d03cda`, where a hash was supplied without bytes, is closed.
- **Immutable binding verification:** `05_IMMUTABLE_BINDING_COMMENT.json` contains comment `5697365170`, `author_association: OWNER`, created `2026-09-16T12:24:21Z`, with the required block verbatim: `HEAD_SHA = b5720dd7e2031e0ac090ae4f5ea4c09fb0a05cc5`, `BASE_SHA = 5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7`, `CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE = no`, `CONSTRUCT_VALIDITY_REVIEWED = no`. It also states that SCREEN, TEST, protected real-route performance and representation geometry remain sealed, S4N3 is not launched, Phase A is not executed, and no hardware, meter, load generator or execution-specific lock is selected or frozen. **This closes N8.**
- **Five exact-head workflow checks:** `06_EXACT_HEAD_WORKFLOWS.json` reports all five as `completed` / `success` on `b5720dd7…`, with run IDs and numbers matching the instruction table exactly: CI `35095031767`/682, Research assurance `35095031561`/613, Engineering Assurance `35095031627`/248, Non-outcome Preflight `35095031564`/251, Power Design Diagnostic `35095031623`/173. Recorded as technical assurance only; not treated as construct-validity evidence anywhere in this verdict.
- **Focused contract tests:** `tests.test_study1b_engineering_benchmark_contract_v06` — **11/11 pass**.

### Transport limitations

- I have no network access to the repository or the GitHub API from this environment. The blob identities, binding comment and workflow conclusions are verified as internally consistent and as bound to immutable addresses, but I did not dereference those addresses. A reviewer with network or a local clone at `b5720dd7…` can now complete that step, which was not possible before N7 landed.
- No transport check failed. The semantic review proceeded.

---

## Executive assessment

The Phase A design validly instantiates the bounded engineering constructs it claims to measure. The intervention is isolated, the search construct is genuinely fixed-work, the synthetic payload is adequate for the resource characterization claimed and is fenced off from any biometric reading, the two gallery points are correctly framed as sensitivity scenarios, the endpoints match the claims, the measurement plane supports a device-level energy statement, and the firewalls against promotion into biometric or qualification evidence are explicit and redundant.

The design is also unusually honest about what it cannot do. The 4× payload reduction is classified as analytically derived rather than a finding; the 75% guard appears in two places; the RAM-infeasibility outcome is defined as a valid result rather than a failure to be engineered around; and `CHARACTERIZATION_ONLY_NO_PASS_FAIL` is coupled to a rule that forbids retrofitting thresholds onto the execution that produced the data.

Three gaps remain, and all three are of the same type: the protocol specifies measurements that will be **valid** but has not specified the recordings needed to make an unexpected result **interpretable**. In each case the missing item lives in an object that is frozen at platform materialization, so it must be added prospectively or it cannot be added at all without post-hoc reasoning.

1. Neither cache hierarchy nor measured memory bandwidth is recorded anywhere, although the contract's own stated objective for G0 versus G2 is a claim about which of arithmetic, cache and bandwidth dominates.
2. Nothing forbids reducing a paired 512D/128D delta to a single ratio when the two arms are in different saturation or censoring regimes at the same offered QPS.
3. The backend's dispatched compute kernel is not recorded per arm, although a dense kernel routinely selects different code paths at inner dimension 512 and 128.

None of these invalidates the construct. All three should be closed before the execution-specific lock is frozen.

---

## CV1 — Intervention isolation

**Evidence.** `reference_and_candidate.phase_a_pairing_rule` requires hardware, datatype, gallery cardinality, template count, search algorithm, query schedule, concurrency, thread/backend configuration, warm-up, measurement window and aggregation policy to be identical between arms on a given hardware tier. `synthetic_data_contract.paired_generation` generates deterministic 512-component pre-normalization rows; the 512D arm normalizes the full row, the 128D arm normalizes the first-128 prefix independently; arm-specific matrices are materialized separately and **the 512D base matrix must not remain resident during a 128D measurement**. `measurement_statistics.execution_order.arm_order: COUNTERBALANCED_ACROSS_RESTARTS` with exact order and timestamps retained.

**Assessment.** The pairing list is complete against the factors that plausibly move latency, throughput, RAM and energy. The residency clause is the one that matters most and it is present and unambiguous: without it, a 128D measurement taken after a 512D measurement in the same process could sit on a warmed page cache and an already-resident 3.13 GB base matrix, and the 128D arm would look better for a reason that has nothing to do with dimension. Prefix truncation with independent renormalization is sound for this purpose — both arms carry the correct marginal distribution for their dimension (a uniform point on S^511 and on S^127 respectively), and the shared base stream affects reproducibility rather than timing.

One residual is not a defect in the control but a limit on attribution. The pairing rule fixes the backend *configuration*; it cannot fix the backend *code path*, and it should not try to. A dense GEMV/GEMM implementation commonly dispatches different microkernels, blocking factors or small-inner-dimension specializations at d=512 and d=128. That dispatch is a genuine consequence of dimension and belongs in the measured effect, but nothing in the lock records which path was taken, so a delta that departs from the bandwidth or arithmetic expectation cannot be diagnosed as dimensional rather than a dispatch artifact.

**Finding.** Intervention isolation is **valid**. Blocker **B3** below.

---

## CV2 — Fixed-work dense-search construct

**Evidence.** `phase_a_search_semantics`: `algorithm: EXACT_DENSE_DOT_PRODUCT_TOP1`, `top_k: 1`, `threshold_gating: false`, `threshold_lookup: none`, `candidate_pruning: none`, `approximate_search: false`, `index: none`, `returned_value: top1_index_and_score`. `fixed_work_reason` states that every query compares against every resident gallery vector and returns exactly one argmax, so no threshold-dependent downstream candidate list is produced and the dimension-dependent concentration of synthetic cosine scores cannot change the amount of work performed.

**Assessment.** This is the correct construct and the reasoning behind it is stated correctly. Cosine similarity between random unit vectors concentrates with spread of order 1/√d, so random 128D vectors produce roughly twice the spread of random 512D vectors. Under any threshold-gated or top-k>1 design, the 128D arm would generate systematically more above-threshold candidates and more downstream work purely as an artifact of dimension interacting with the generator — a dimension-correlated confounder sitting in the exact place the design claims to isolate dimension. Fixing `top_k=1` with no threshold and no pruning removes it by construction rather than by controlling for it. Work per query is then a deterministic function of gallery cardinality and dimension.

**Finding.** **Valid**, strictly bounded. This establishes nothing about indexed or ANN search, where the relationship between dimension and work is not fixed and where the concentration effect returns through candidate-list size, and nothing about a complete biometric pipeline, where thresholding, quality checks, fusion and re-ranking reintroduce data-dependent work.

---

## CV3 — Synthetic payload construct

**Evidence.** `synthetic_data_contract`: `root_seed: 20260908`, `generator_family: PCG64_NORMAL_FLOAT32`, `base_distribution: independent_standard_normal_before_row_normalization`, `finite_normal_range_required: true`. `nan_inf_subnormal_guard` requires generation to fail closed on NaN or Inf, permits hardware flushing of subnormals, and requires the generator to record the subnormal count before execution with reviewer-visible disposition of a materially nonzero count. `permitted_claims` and `prohibited_claims` are enumerated; `no_real_biometric_embeddings`, `no_protected_match_scores`, `no_real_identity_labels` all true.

**Assessment.** The separation the review request asks for holds.

*Driven by shape, not values, and therefore adequately modelled by the synthetic payload:* resident working-set size, memory traffic per query, dense FP32 arithmetic volume, cache and TLB behaviour, throughput, queueing and the device energy that follows from them. All are functions of gallery cardinality, dimension, dtype and access pattern.

*Potentially value-sensitive, and handled:* denormal-induced FPU slowdowns are the one mechanism by which values could materially bias a timing endpoint on some hardware. The contract addresses this the right way, and the quantitative margin is large. For an L2-normalized vector in R^d, component RMS is 1/√d: **0.0442 at 512D and 0.0884 at 128D**, roughly 36 orders of magnitude above the FP32 minimum normal (~1.18e-38). Pairwise products and their accumulations stay far from the subnormal range. The fail-closed NaN/Inf rule and the subnormal counting requirement are correct belt-and-braces rather than the load-bearing protection.

*Not modelled and correctly excluded:* real embedding structure — clustering, intrinsic dimensionality below the nominal, correlated coordinates. These would matter for accuracy and for any data-dependent search, and matter not at all for fixed-work dense arithmetic. The payload is fenced from biometric interpretation by `prohibited_claims` and by interpretation rule 8.

No additional non-protected sensitivity distribution is required for the bounded characterization claimed. I considered requiring a second distribution (e.g. clustered rather than isotropic) and concluded it would add nothing: under fixed-work top-1 the arithmetic is identical for any finite normal-range input, so a second distribution would test the generator rather than the construct.

**Finding.** **Valid** for the bounded fixed-work engineering characterization. Not a biometric-performance model, and the contract says so.

---

## CV4 — G0/G2 scenario validity

**Evidence.** All four galleries carry `provenance: SCENARIO_ONLY_NOT_EVENT_FACT`, including `G2_central_full`, which additionally carries `role: PRIMARY_ENGINEERING_SENSITIVITY_POINT`; `G0_blacklist_control` carries `role: SMALL_WORKING_SET_CONTROL`. `phase_a_scope.objective` states that no event-frequency claim is attached to either scenario. Interpretation rule 7 repeats it. `ram_residency_contract.infeasible_arm_rule`: if a gallery cannot be allocated and kept RAM-resident on the bound tier, record `RAM_INFEASIBLE_ON_TIER` as a valid engineering result; do not substitute a smaller gallery, enable swap, change datatype, or move only one arm to a larger tier; paired G2 comparison on that tier stops; if a larger tier was prospectively declared, **both** arms may be repeated there under a new execution identity while retaining the original infeasibility result; G0 remains available as the same-tier paired control.

**Assessment.** The scenario framing is correct and now consistent across the primary and the stress point. The infeasibility rule closes every asymmetric escape I can construct: resizing, retyping, swap, and single-arm tier migration are each named and forbidden, the original negative result is retained rather than superseded, and the fallback preserves a same-tier paired comparison at G0 rather than abandoning pairing. Declaring infeasibility a valid result rather than a run failure is the right inversion — on a modest edge tier the 3.13 GB 512D arm not fitting *is* the finding the Jungle Championship scenario exists to surface.

I verified the payload arithmetic independently: 510,000 identities × 3 templates = 1,530,000 vectors; at FP32 that is **3,133,440,000 bytes at 512D and 783,360,000 bytes at 128D**, matching `g2_512d_fp32_payload_bytes` and `g2_128d_fp32_payload_bytes` exactly. G0 is 30,000 vectors: 61.44 MB and 15.36 MB.

The two-point design has one structural limit. G0 and G2 differ by a factor of 51 in working set, and a two-point comparison cannot distinguish a smooth trend from a threshold crossing between them. `G1_hybrid` exists in the contract and is excluded from Phase A scope. That is a defensible cost decision, not a validity defect, and it is recorded below as a future sensitivity requirement rather than a blocker.

**Finding.** **Valid as sensitivity points, not event facts.** Asymmetric handling is closed.

---

## CV5 — Endpoint-to-claim alignment

**Evidence.** Endpoints retained: raw per-query latency samples, completed throughput, queue depth time series and recovery time, RAM residency preflight (`process_RSS_before_gallery`, `process_RSS_after_gallery`, `peak_working_set`, available RAM before and after, swap activity), external device-input or wall power, `total_joules_per_identification`, `incremental_joules_per_identification_diagnostic`, `joules_per_burst`, raw power trace, failure and exclusion records, CPU frequency/throttling and temperature where observable. `vector_payload_bytes_classification: ANALYTICALLY_DERIVED_NOT_MEASURED_FINDING`. `energy_measurement.guard` and interpretation rule 3 both state that 75% fewer coordinates must not be reported as 75% lower power or energy. `percentile_support_rules`: p95 requires ≥200 completed samples per restart, p99 requires ≥1000, otherwise `INSUFFICIENT_SAMPLES_NO_PERCENTILE_CLAIM`.

**Assessment.** The endpoints match the claims and the structural-versus-measured boundary is enforced in three independent places, which is the right amount of redundancy for the single most likely misreading of this benchmark. Classifying payload bytes as derived rather than a finding prevents a tautology (512→128 is exactly 4× by construction) from being presented as a result.

The percentile support rules are correctly calibrated and produce a predictable pattern that the report should anticipate. With a 600 s steady window per restart, completed samples per restart at the declared QPS grid are 150, 300, 600, 1200, 2400 and 4800. So **p95 is unsupported at 0.25 QPS, and p99 is unsupported at 0.25, 0.5 and 1.0 QPS.** The rule handles this correctly by emitting `INSUFFICIENT_SAMPLES_NO_PERCENTILE_CLAIM`, but it means roughly half the latency table will be legitimately empty, and gaps of that size read as missing data unless stated up front.

The gap in this section is interpretive, not instrumental. Every quantity needed to detect it is retained — offered QPS, completed QPS, queue depth, censoring status — but nothing forbids reducing a paired delta to a ratio when the two arms are not in the same regime. See blocker **B2**.

One related reporting point. `total_joules_per_identification` includes idle baseline consumption by declared convention, which is correct for a device-level claim, but it makes the figure a strong function of offered QPS: at 0.25 QPS the idle term dominates, at saturation it is a small fraction. The contract requires every *autonomy* figure to name its duty-cycle profile (`battery_model.rule`) but imposes no equivalent requirement on J/identification, which is the figure most likely to be quoted in isolation.

**Finding.** Endpoints **match claim scope**. Blocker **B2**; reporting limitations **L1** and **L3**.

---

## CV6 — Measurement-plane validity

**Evidence.** `canonical_measurement_plane: EXTERNAL_DEVICE_INPUT_OR_WALL`; `external_meter_required_for_strong_energy_claim: true`; `minimum_external_sampling_rate_hz: 10`; `on_chip_telemetry_role: SUPPORTING_DIAGNOSTIC_ONLY`. `idle_baseline`: 300 s, measured immediately before or after each configuration block. `canonical_joules_per_identification`: total device energy over the measurement window divided by completed identifications, idle included. `diagnostic_incremental_joules_per_identification`: integral of power minus matched idle baseline, diagnostic only, `negative_values_due_to_measurement_noise_must_not_be_clamped: true`. `load_generation.canonical_placement: OFF_DEVICE`, with both server-boundary device latency and client round-trip latency reported, generator CPU/RAM/power excluded from device energy, and an on-device generator rendering a run diagnostic only unless separately re-reviewed. The lock carries meter manufacturer, model, serial, measurement location, sampling rate, calibration reference and timestamp synchronization method as required fields.

**Assessment.** This is the correct architecture for a device-level energy claim. Making the external plane canonical matters specifically here: on-chip counters exclude DRAM on many parts and always exclude board and supply losses, and DRAM is exactly where a 2.92 GiB versus 0.73 GiB working-set difference manifests. Telemetry-only energy would bias the comparison toward the arm under evaluation.

Three details are handled better than is typical. Declaring **both** conventions and naming one canonical removes the most common source of incomparable energy numbers. Matching the idle baseline to each configuration block rather than measuring it once removes thermal and background drift from the incremental figure. And forbidding the clamping of negative incremental values is the correct scientific choice: when the incremental signal is near the noise floor, clamping at zero turns symmetric noise into a positive bias, and a negative value is honest information that the measurement cannot resolve the increment.

10 Hz is adequate for the 600 s steady windows and for 30 s bursts with 600 s recovery observation. It is marginal for resolving per-query energy structure at the higher QPS points, but no endpoint requires that.

**Finding.** **Valid for the bounded device-level energy claim** under the declared convention.

---

## CV7 — Causal and confounding controls

**Evidence.** `independent_process_restarts_per_configuration: 5`; `warmup_seconds_per_restart: 60` with `warmup_samples_excluded: true`; `steady_measurement_seconds_per_restart: 600`; `burst_repetitions: 5`; raw latency and raw power samples retained; per-restart and across-restart aggregation both specified, including standard deviation, IQR, min and max rather than a point estimate; `no_silent_failed_run_exclusion: true` with `failed_run_handling: retain_failure_record_and_reason`; `arm_order: COUNTERBALANCED_ACROSS_RESTARTS` explicitly so thermal drift and background-time effects are not systematically assigned to one arm; `prelock_selection_guard` plus the accepted v0.6 per-choice firewall forbidding runtime tuning or substitution.

**Assessment.** The controls are sufficient to attribute observed differences primarily to representation dimension under the frozen configuration. Counterbalancing plus independent restarts addresses the ordering and drift confounds; dispersion reporting across restarts prevents a single noisy run from carrying a claim; failure retention prevents the most common silent bias, which is dropping the runs that went badly.

What the controls do not provide is the ability to *explain* a delta. Two recordings are missing, and both concern mechanisms the contract itself invokes.

First, `phase_a_scope.objective` asserts that G0 is where "arithmetic/cache behavior dominates" and G2 is where "RAM capacity and memory bandwidth may dominate". Neither cache hierarchy nor memory bandwidth appears anywhere in the environment lock: `required_environment.cpu` records model, microcode, cores, threads, affinity, NUMA, governor and boost policy, but no L1/L2/L3 or LLC capacity; `required_environment.memory` records capacity, type, rated speed, channel configuration and ECC status, but no measured achievable bandwidth. The consequence is concrete. At G0 the arms occupy 61.44 MB and 15.36 MB. On an edge CPU with an LLC in the single-digit to low-tens of MiB, the 128D arm may be substantially LLC-resident while the 512D arm is not, and the observed ratio would exceed 4× because of a cache-capacity crossing rather than arithmetic. That crossing is a genuine consequence of dimension and belongs in the result — but with no recorded LLC size and no requirement to report each arm's working set against it, the report cannot say which mechanism produced the number, and the contract's own stated objective for G0 cannot be verified. The same applies at G2, where a measured bandwidth figure is what turns a latency into a statement about how close the arm runs to the memory bound.

Second, the kernel-dispatch point from CV1.

Both are recording gaps rather than control failures: the paired design remains sound, and the bounded attribution to dimension remains supportable. They determine whether an unexpected result is interpretable or merely observed.

**Finding.** Confound control **sufficient** for the bounded paired interpretation. Blockers **B1** and **B3**.

---

## CV8 — Generalization and external validity

**Evidence.** Interpretation rule 6: device count D scales fleet consequences only after per-device effects are measured, and D does not define local flow. Rule 7: G0/G2 are sensitivity scenarios, not observed event facts. Rule 4: CPU is admissible only against a prospectively declared operational envelope. Rule 5: GPU/NPU is not assumed superior without benchmark evidence. `battery_model.rule`: every autonomy figure must name the workload/duty-cycle profile it is conditioned on, and incremental compute-only energy must not be used for autonomy. `engineering_axes_later_phases` fences datatype (Phase C), compute platform (Phase B), energy/battery (Phase D) and indexed/ANN search (Phase E) as separate interventions. `reproducibility_and_environment` requires the environment to be materialized before canonical execution and binds result identity to it.

**Assessment.** The generalization limits are explicit and sit in the right places. The fleet rule in particular inverts the usual failure, where a per-device measurement is multiplied by device count and presented as an observation; here the multiplication is licensed only after per-device effects exist and is labelled an extrapolation. Prohibiting incremental compute-only energy from feeding autonomy is the correct guard against the most flattering possible battery number.

Results will be bound to one hardware tier, one runtime, one workload and one measurement environment. That is stated rather than implied. No single tier or synthetic workload is presented as universally representative.

**Finding.** Generalization limits **explicit and acceptable**. Future sensitivity requirement **L2**.

---

## CV9 — Characterization versus qualification

**Evidence.** All six operational thresholds are null. `threshold_mode_if_null: CHARACTERIZATION_ONLY_NO_PASS_FAIL`. `prospective_binding_rule`: a threshold may be supplied and frozen before a future execution, or the benchmark may remain characterization-only; a threshold must not be chosen after inspecting Phase A results and then applied retroactively to that same execution; any post-result threshold can govern only a new prospectively identified execution. `saturation_characterization.purpose: characterization_not_operational_pass_fail`, with `no_single_metric_saturation_claim: true`.

**Assessment.** `CHARACTERIZATION_ONLY_NO_PASS_FAIL` is the correct interpretation, and characterizing before setting thresholds is better practice than inventing thresholds to have something to pass. The guard is the part that matters and it is correctly constructed: it does not merely forbid post-hoc thresholds, it specifies what a post-result threshold *may* govern, which is a new prospectively identified execution. That is the same discipline the S4 power record applied to estimator selection, applied here to acceptance criteria, and the symmetry is deliberate.

**Finding.** Characterization-versus-qualification boundary **acceptable**. Any future pass/fail criterion must be prospectively frozen before the execution to which it applies.

---

## CV10 — Interpretation firewall

**Evidence.** `scientific_boundary.interpretation_firewall`: engineering measurements can support RAM/compute/energy/cost statements on the bound hardware and workload, and must not be promoted into evidence of biometric non-inferiority, superiority, SCREEN, qualification TEST, representation geometry or production suitability. Interpretation rule 8: no engineering result is evidence that 128D is biometrically acceptable. Rule 9: no protected Study 1B outcome may be opened to select or tune an engineering configuration. Rule 10: no target-workload preview, whatever its label, may silently determine the canonical lock configuration. `synthetic_data_contract.prohibited_claims` enumerates biometric accuracy, non-inferiority, superiority and operational FMR/FNMR. `scientific_boundary` records SCREEN, qualification TEST, real-route performance, representation geometry and amendment all false, S4N1 and S4N2 `CLOSED_NEGATIVE`, S4N3 not launched.

**Assessment.** The firewall runs in both directions and is stated at three levels: the boundary block, the claim enumeration attached to the data contract, and the interpretation rules. Bidirectionality is the property that matters — rule 9 prevents protected outcomes from leaking *into* engineering configuration selection, which is the direction most contracts forget. The production-suitability exclusion is the third leg and is the one most likely to be tested in practice, since a favourable Phase A result on a chosen tier is exactly the kind of evidence that gets quoted as readiness.

**Finding.** Interpretation firewall **acceptable**.

---

## Limitations / required prospective corrections

### B1 — Cache hierarchy and measured memory bandwidth are not recorded
**Class: blocker before platform materialization.**

*Causing objects:* `STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml` → `required_environment.cpu` and `required_environment.memory`; the claim they fail to support is `STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml` → `phase_a_scope.objective`.

*Minimum prospective correction:* add to `required_environment.cpu` a `cache_hierarchy` block (L1d, L2, L3 or LLC capacity in bytes; inclusive or exclusive; sharing topology), and to `required_environment.memory` a `measured_achievable_bandwidth_GB_per_s` field with the measurement method named. Add to the benchmark's reporting requirements that each arm's resident working set be reported against LLC capacity, and each arm's achieved memory throughput against measured bandwidth.

*Firewall note:* a STREAM-class bandwidth measurement is executed after the lock is frozen, as part of environment characterization, and shares neither vector dimensionality nor search family with the target workload. Under the per-choice classifier accepted at `c7d03cda` it does not inform any lock-defining choice and raises no D3 issue. I raise this explicitly so the correction is not mistaken for a reopening of the accepted firewall semantics.

### B2 — No rule governs paired deltas across differing saturation or censoring regimes
**Class: blocker before platform materialization.**

*Causing objects:* `..._BENCHMARK_V0_3_...yaml` → `load_generation.steady_qps_per_device`, `load_generation.burst`, `saturation_characterization`, `measurement_statistics.aggregation`.

*The problem:* the two arms will not saturate at the same offered QPS — the 512D arm streams four times the bytes per query. At a fixed grid point one arm can be saturated while the other is not, in which case the paired latency and energy delta compares queueing against service time rather than dimension against dimension. The same applies to the fixed 16 QPS burst: `nonrecovery_reporting: RIGHT_CENSORED_GREATER_THAN_600_SECONDS` correctly records a non-recovering arm, but a right-censored value paired against a finite one cannot be reduced to a ratio. `no_single_metric_saturation_claim` constrains saturation claims; it does not constrain paired deltas.

*Minimum prospective correction:* add an interpretation rule stating that a paired 512D/128D delta is quantitatively interpretable only where both arms are in the same saturation regime and neither is censored; that each arm's saturation point must be reported alongside every paired delta; and that cross-regime pairs must be reported as regime-crossing observations without a combined ratio. Optionally add an arm-relative burst point (a fixed multiple of each arm's measured saturation QPS) alongside the absolute 16 QPS point, so burst absorption is characterized within each arm's envelope as well as against a common absolute load.

*Note:* every quantity needed to apply this rule is already retained. This is a reporting rule, not new instrumentation — which is precisely why it must be frozen before the data exist.

### B3 — Backend compute-kernel dispatch is not recorded per arm
**Class: blocker before platform materialization.**

*Causing objects:* `..._ENVIRONMENT_LOCK_V0_6_...yaml` → `required_environment.runtime` and `result_provenance_requirements`.

*Minimum prospective correction:* require, per arm, the backend-reported kernel or core identifier (for example the OpenBLAS core name, or the MKL verbose dispatch line), the exact call shape used for the search (GEMV versus batched GEMM, batch size, memory order, leading dimension) and any backend-reported blocking parameters. Add these to `result_provenance_requirements`.

*Rationale:* dispatch differences at inner dimension 512 versus 128 are a real consequence of the intervention and belong in the measured effect. Recording them does not change the measurement; it makes an unexpected delta diagnosable rather than merely observed.

### L1 — Total joules per identification is strongly QPS-dependent and may be quoted unconditioned
**Class: reporting limitation.**

`canonical_joules_per_identification` includes idle baseline by declared convention, correct for a device-level claim, but the resulting figure varies by a large factor across the 0.25–8 QPS grid. `battery_model.rule` requires every autonomy figure to name its duty-cycle profile; no equivalent requirement attaches to J/identification. Recommend extending the same conditioning rule: every joules-per-identification figure names the offered QPS and saturation regime it was measured at.

### L2 — Two working-set points cannot distinguish a trend from a threshold crossing
**Class: future sensitivity requirement.**

G0 and G2 differ by a factor of 51 in resident working set. `G1_hybrid` exists in the contract and is excluded from Phase A. Excluding it is a defensible cost decision and not a validity defect, but any interpolation between G0 and G2 remains an assumption. Recommend G1 in Phase B, or an explicit statement in the Phase A report that no intermediate behaviour is claimed.

### L3 — Roughly half the percentile table will be legitimately empty
**Class: reporting limitation.**

With a 600 s window, completed samples per restart are 150, 300, 600, 1200, 2400 and 4800 across the QPS grid. Under `percentile_support_rules`, p95 is unsupported at 0.25 QPS and p99 is unsupported at 0.25, 0.5 and 1.0 QPS. `INSUFFICIENT_SAMPLES_NO_PERCENTILE_CLAIM` handles this correctly, but the pattern should be stated in the report preamble so the gaps are read as designed rather than as missing data. If p99 at low QPS is wanted, the correct prospective lever is a longer steady window, not a relaxed support rule.

---

## Required verdict fields

```text
VERDICT: ACCEPT_WITH_LIMITATIONS
CONSTRUCT_VALIDITY_ACCEPTED: yes
DIMENSION_ONLY_INTERVENTION_VALID: yes
FIXED_WORK_DENSE_SEARCH_CONSTRUCT_VALID: yes
SYNTHETIC_DENSE_PAYLOAD_VALID_FOR_BOUNDED_ENGINEERING_CHARACTERIZATION: yes
G0_G2_SCOPE_VALID_AS_SENSITIVITY_NOT_EVENT_FACT: yes
MEASUREMENT_ENDPOINTS_MATCH_ENGINEERING_CLAIM_SCOPE: yes
MEASUREMENT_PLANE_VALID_FOR_DEVICE_LEVEL_ENERGY_CLAIM: yes
CONFOUND_CONTROL_SUFFICIENT_FOR_PAIRED_PHASE_A: yes
GENERALIZATION_LIMITS_EXPLICIT_AND_ACCEPTABLE: yes
CHARACTERIZATION_VS_QUALIFICATION_BOUNDARY_ACCEPTABLE: yes
INTERPRETATION_FIREWALL_ACCEPTABLE: yes
REQUIRES_PROTOCOL_CHANGE_BEFORE_PLATFORM_MATERIALIZATION: yes
PROTECTED_BIOMETRIC_OUTCOMES_REQUIRED_FOR_REVIEW: no
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
```

Blockers before platform materialization: **B1, B2, B3**. Reporting limitations: **L1, L3**. Future sensitivity requirement: **L2**.

Per §10 of the reviewer instructions, this acceptance permits only the next preparation stage, and only after B1–B3 are landed prospectively: materialization and freezing of the real target hardware, external meter, off-device load generator, configuration provenance, generator identity and execution-specific environment lock. It does not authorize canonical Phase A execution.

---

## Boundary confirmation

No protected biometric outcome, S4N3 result, Phase A result-bearing execution, or target-platform freeze was required or opened for this review.

```
SCREEN opened?                          no
qualification TEST opened?              no
protected real-route performance opened? no
representation geometry opened?         no
S4N3 launched?                          no
amendment activated?                    no
Phase A executed?                        no
target hardware / meter / load generator selected or frozen?  no
S4N1 status                             CLOSED_NEGATIVE
S4N2 status                             CLOSED_NEGATIVE
```

The construct-validity questions in scope were decidable entirely from the benchmark contract, the addendum, the environment lock and arithmetic over declared quantities. At no point did an answer require a protected outcome. `PROTECTED_BIOMETRIC_OUTCOMES_REQUIRED_FOR_REVIEW: no` is a finding, not a formality: it confirms that the engineering and biometric tracks were separable in practice and not only in principle.

I also record that this review did not reopen the D1–D3 or N4–N6 acceptances. B1's firewall note is the only place a construct-validity finding touches those semantics, and it is written to stay inside them.
