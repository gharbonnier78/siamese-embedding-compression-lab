# B1/B2/B3 — originating-reviewer acceptance criteria

**Status:** not a review, not a verdict, not a closure check.
**Authored by:** the reviewer who raised B1, B2, B3, L1, L2 and L3 in the construct-validity verdict on `b5720dd7e2031e0ac090ae4f5ea4c09fb0a05cc5`.
**Date:** 2026-09-17
**Intended head:** `cb43fdb1543700ae1429a0ed93ea99eed9065899`

## What this document is

A frozen, testable statement of what the originating reviewer meant by each limitation, written **before** seeing the correction object. It exists so that the independent second reviewer can check closure against a stated standard rather than reconstruct intent from a prose verdict, and so that the originating reviewer cannot later adjust the standard to fit whatever was built.

It confers nothing. It does not set `B1_B2_B3_FOCUSED_CONFIRMATION_OBTAINED`, does not close any item, and does not make platform materialization admissible. A second reviewer may disagree with any criterion here; these are the originating reviewer's intent, not a binding specification.

## Disclosure — the exact state of blindness

I have **not** seen `STUDY1B_PHASE_A_CONSTRUCT_VALIDITY_CORRECTIONS_V0_1_2026-09-16.yaml` or any file in the `cb43fdb1` package. That package was not transmitted to me.

I **have** read `INSTRUCTIONS_SECOND_REVIEWER_B1_B2_B3_CLOSURE_2026-09-17.md` in full (SHA-256 `80d228a303f32ad2388b0d425f15acc3cc5cedb78b388153cf780dabd6765ab8`). Its §6 describes the shape the corrections are expected to take. So I am blind to the correction object but **not** blind to the author's description of it.

That partial contamination is disclosed rather than glossed. I have compensated by deriving each criterion from the original rationale for the finding rather than from §6's checklist, and by stating explicitly, under each item, where §6's described shape would **not** satisfy the criterion. Those three places — B1c, B2b, B3b — are the ones worth a second reviewer's attention, because they are where my intent and the described correction may diverge.

---

## B1 — Cache hierarchy and achievable memory bandwidth

**Why it was raised.** `phase_a_scope.objective` asserts that G0 is where arithmetic and cache behaviour dominate and G2 is where RAM capacity and bandwidth may dominate. Neither cache capacity nor bandwidth is recorded anywhere in the environment lock, so that assertion is unfalsifiable and a surprising ratio cannot be attributed. The concrete case: at G0 the arms occupy 61.44 MB and 15.36 MB, so on an edge LLC in the single-digit to low-tens of MiB the 128D arm may be substantially resident and the 512D arm not, producing a ratio above 4× from a capacity crossing rather than from arithmetic.

**B1a — Cache capacities recorded.** L1d, L2 and L3/LLC capacities in bytes, with inclusivity and sharing topology.

**B1b — Effective, not merely total, LLC is derivable.** Sharing topology must be recorded in enough detail to derive the LLC capacity **available to the benchmark's thread set**, not only the package total. On a chiplet, cluster or heterogeneous-core part with the benchmark pinned to a subset of cores, total LLC is the wrong denominator for the residency question. Recording cores-per-LLC-slice and the affinity set together is sufficient; recording only a package figure is not.

**B1c — The bandwidth ratio must always be reported, not only "where observable."**
*This is where §6 and my intent may diverge.* §6 asks for achieved memory throughput relative to measured achievable bandwidth **where observable**. Counter-based throughput needs uncore or IMC counters, which are restricted or absent on most edge platforms — precisely the platforms this benchmark targets. If "where observable" governs the whole quantity, the most interpretively valuable number disappears on the likely hardware.

For this construct it does not need to be observed, because it is derived. Phase A is fixed-work exact dense scan: bytes streamed per query is `gallery_payload_bytes` exactly, and completed QPS is retained. So

```
derived_stream_rate_GB_s   = gallery_payload_bytes × completed_QPS / 1e9
bandwidth_utilization      = derived_stream_rate_GB_s / measured_achievable_bandwidth_GB_s
```

is always computable, for both arms, at every load point. Closure requires that this **derived** figure be a mandatory reported quantity. Counter-based measurement is an optional refinement and is the only part to which `where observable` may apply.

**B1d — Bandwidth characterization method named and its measured value recorded**, with the method identified specifically enough to be repeated (e.g. STREAM Triad, thread count used, array size relative to LLC).

**B1e — Per-arm working set reported against effective LLC**, at both G0 and G2, as a ratio and not only as two absolute numbers.

**Would not close B1:** recording CPU model alone and expecting a reader to look up cache sizes; recording total LLC without sharing topology; making the bandwidth utilization ratio conditional on counter availability.

---

## B1 ↔ D3 compatibility

**B1f — Ordering frozen before characterization.** Platform, backend, thread count, affinity and frequency policy are frozen **before** bandwidth characterization runs, and the characterization result may not retune or substitute any frozen choice under the same execution identity. §6 describes exactly this and it is the right construction.

**B1g — The characterization is not a target-workload signal.** A STREAM-class measurement shares hardware class with the target but shares neither vector dimensionality nor search family. Under the per-choice classifier accepted at `c7d03cda` it does not inform any lock-defining choice provided B1f holds. Closure requires that the correction object say so explicitly rather than leaving a future reader to re-derive it — otherwise the next reviewer will reasonably ask whether B1 reopened the accepted firewall.

---

## B2 — Cross-regime and censoring guard

**Why it was raised.** The 512D arm streams four times the bytes per query, so the arms will not saturate at the same offered QPS. At a fixed grid point one arm may be saturated and the other not, in which case the paired delta compares queueing against service time rather than dimension against dimension. The same applies to the 16-QPS burst, where a right-censored recovery paired against a finite one cannot be reduced to a ratio.

**B2a — The guard itself.** A quantitative paired ratio or delta is permitted only where both arms are assigned the same non-censored regime at that offered load. Cross-regime and censored/finite pairs are retained and reported, never reduced to a combined ratio. Each arm's saturation point or interval is reported alongside every paired delta.

**B2b — The regime-assignment rule must itself be frozen and computable.**
*This is the second place where §6 may fall short of the intent.* §6 requires each arm to have "an independently reported saturation point or interval" but does not require a rule for assigning a given `(arm, gallery, offered_QPS)` cell to a regime. Saturation is a knee, not a switch. Without a frozen assignment rule, the guard is unenforceable, and worse, the assignment could be made after seeing the data — which would reintroduce exactly the post-hoc freedom this project has spent six review cycles eliminating everywhere else.

Closure requires a prospectively frozen rule that is computable from already-retained quantities. Any of these would do, and the choice is the author's:

- `completed_QPS / offered_QPS` below a frozen tolerance;
- a frozen queue-depth trend criterion over the steady window;
- a frozen latency-inflation criterion relative to the lowest-load point.

Whatever is chosen must have **three** outcomes, not two, with an explicit ambiguous category, and ambiguity must default to *not same-regime* — fail closed, consistent with `uncertainty_defaults_to_informative` and the rest of this project's conventions.

**B2c — The absolute 16-QPS burst remains frozen**, and an arm-relative burst, if ever added, is additive and prospective and does not replace it. §6 has this and it is correct: replacing the frozen burst would be a protocol change driven by anticipated results.

**Would not close B2:** a prose instruction to "report deltas only within comparable regimes" with no computable assignment rule; a two-valued rule with no ambiguous category; an assignment rule that can be chosen after the run.

---

## B3 — Backend dispatch observability

**Why it was raised.** The pairing rule fixes backend *configuration*; it cannot fix the backend *code path*. Dense kernels routinely dispatch different microkernels, blocking factors or small-inner-dimension specializations at d=512 versus d=128. That difference is a legitimate part of the measured effect, but without recording it a delta that departs from the bandwidth or arithmetic expectation cannot be diagnosed.

**B3a — Dispatch equality is NOT required**, and the correction must say so. A dimension-induced dispatch difference is part of the intervention, not a confound to be engineered away. §6 states this correctly.

**B3b — The `NOT_EXPOSED_BY_BACKEND` escape must be partitioned.**
*This is the third place where the described shape may over-reach.* §6 lists eight B3 fields and then permits `NOT_EXPOSED_BY_BACKEND` if internals are unavailable. But those eight fields are not of one kind:

- **Caller-determined, always knowable, never eligible for the escape:** exact search call shape; GEMV versus batched GEMM; batch size; matrix and vector shapes; memory order; leading dimension. These are in the benchmark's own code. The backend has no say in whether they can be recorded.
- **Backend-exposed, legitimately eligible:** backend-reported kernel or core identifier; blocking parameters; verbose or trace evidence.

Closure requires this partition. Without it, a blanket `NOT_EXPOSED_BY_BACKEND` can swallow the fields that are always available, and B3 reduces to nothing on any backend that is quiet about its internals.

**B3c — Honest absence over invented provenance.** Where a backend-exposed field is genuinely unavailable, record `NOT_EXPOSED_BY_BACKEND` and forbid microkernel-specific mechanism claims. §6 has this and it is better than what the original finding specified; I did not cover the unavailable case and should have.

**B3d — Recorded per arm**, not once per configuration block.

---

## L1 — Energy reporting guard

**L1a** — Every joules-per-identification value is conditioned by offered QPS, saturation regime, and steady-state versus burst. §6 has all three; my original finding named only QPS.

**L1b — The conditioning travels with the number.** Closure requires the conditioning to appear wherever the figure appears — tables, abstract, summary, slide — not only in a methods section. A conditioning rule that lives in the methods and a bare number that lives in the abstract is the failure mode this guard exists to prevent.

---

## L3 — Percentile support reporting guard

**L3a** — The report preamble states the frozen support rules, that `INSUFFICIENT_SAMPLES_NO_PERCENTILE_CLAIM` is a designed result rather than missing data, and that the thresholds cannot be relaxed after seeing results.

**L3b — Designed suppression must be distinguishable from undelivered samples.** The support rule keys on *completed* samples. From the frozen grid and the 600 s window, the expected completed counts per restart are 150, 300, 600, 1200, 2400 and 4800, so p95 is designed-suppressed at 0.25 QPS and p99 at 0.25, 0.5 and 1.0 QPS. But a **saturated** arm at 4 QPS offered may complete far fewer than 2400, suppressing p99 for an entirely different reason.

An empty cell therefore has two opposite meanings: "by design, too little offered load" and "this arm could not keep up." Closure requires the report to publish the expected counts alongside the actual completed counts, so the two are never confused. This is where L3 and B2 meet, and it is the cheapest possible cross-check on the regime assignment.

---

## L2 — Intermediate working set

**L2a** — Classification as a future sensitivity requirement rather than a Phase A blocker is correct and I reaffirm it. G0 and G2 differ by a factor of 51 in resident working set; excluding G1 is a defensible cost decision.

**L2b** — Phase A must state that no intermediate behaviour between G0 and G2 is claimed. That single sentence is the whole of what L2 requires at this stage.

---

## Additive-correction criterion

Raised separately and not part of the original B1/B2/B3, but it bears on whether closure is safe.

**A1** — The correction object must be **additive** to the construct accepted at `b5720dd7`. It should add recordings, reporting rules and guards; it should not modify `phase_a_pairing_rule`, `phase_a_search_semantics`, `synthetic_data_contract`, `measurement_statistics` or `energy_measurement` in ways that would change what CV1–CV10 assessed.

**A2** — Specifically, the B1 bandwidth characterization introduces a new activity into the execution sequence. Its position must be frozen, it must sit outside the measurement blocks, and an idle or thermal-settling period must separate it from the first measured block. Running a bandwidth saturation test immediately before a measured arm perturbs thermal state and interacts with the CV7 counterbalancing that was accepted on the assumption that nothing else occupies the device.

**A3** — The verdict block in the second-reviewer instructions has no field for this. Recommend adding `CORRECTIONS_ADDITIVE_AND_DO_NOT_PERTURB_ACCEPTED_CONSTRUCT: yes | no`, so that `PLATFORM_MATERIALIZATION_CURRENTLY_ADMISSIBLE: yes` cannot be reached without someone having looked at the interaction.

---

## How to use this document

For the **second reviewer**: a reference for what the originating findings meant, not a specification you must adopt. Disagree where you think the criterion is wrong — particularly at B1c, B2b and B3b, which are the places where my intent and the correction's described shape may diverge, and where I have the least standing to insist.

For the **author**: if a criterion here is not met, that is information about what a second reviewer may raise. It is not a finding, and it does not require a branch change before the second review. Changing the branch now would stale the binding and the package, which costs more than carrying a known gap into the review.

For the **record**: this document should be archived as append-only review history under its own name and its own status field. It must not be cited as, or counted toward, `B1_B2_B3_FOCUSED_CONFIRMATION_OBTAINED`.
