# B1/B2/B3 — originating-reviewer closure check

**This is not the second independent review.** It does not set `B1_B2_B3_FOCUSED_CONFIRMATION_OBTAINED` and does not make platform materialization admissible. It is the author of B1/B2/B3 checking the corrections against the acceptance criteria he froze **before** seeing them, so the independent reviewer has a scored barème rather than a prose verdict to reconstruct.

File it under its own field, e.g. `B1_B2_B3_ORIGINATING_REVIEWER_CLOSURE_CHECK`.

- **Head:** `cb43fdb1543700ae1429a0ed93ea99eed9065899`
- **Package SHA-256:** `5d4d769e669f5a4efb9246325d5def6ddee299dc7464e5e5e4caf9add2e729e2` — matches announced
- **Criteria document:** `PR50_B1_B2_B3_ORIGINATING_REVIEWER_ACCEPTANCE_CRITERIA_2026-09-17.md`, authored 2026-09-17 with no access to the correction object
- **Date:** 2026-09-17

```
ORIGINATING_REVIEWER_CLOSURE_CHECK: PARTIAL

B1_MET: no    (B1c fails; B1b partial; B1a/d/e/f/g met)
B2_MET: no    (B2b fails; B2a/c met)
B3_MET: yes   (all four criteria met)
L1_MET: yes
L3_MET: no    (L3b not addressed; reporting class, low severity)
L2_MET: yes
A1_MET: yes   (verified by byte-identity, not by assertion)
A2_MET: no    (not addressed)
```

The blind barème earned its keep: of the three divergences I predicted, **two materialized (B1c, B2b) and one did not (B3b)**. B3 is closed cleanly and my predicted gap there was wrong. I record that as plainly as the failures.

---

## Transport

Run, though under the repository-primary model these are no longer this review's chain of evidence: ZIP SHA-256 matches; bundled verifier PASS; **13/13** blob identities recomputed with my own code and **13/13** provenance-bound to `cb43fdb1…`; **22/22** content hashes; HARNESS blob and SHA-256 both match; binding `5720470976` binds the exact head and carries `B1_B2_B3_FOCUSED_CONFIRMATION_OBTAINED = no`; **5/5** workflows success on the exact head; **20/20** tests pass.

---

## B1 — cache and bandwidth observability: **not met**

| Criterion | Result |
| --- | --- |
| B1a cache capacities recorded | **met** |
| B1b effective LLC derivable | **partial** |
| B1c derived bandwidth ratio always reported | **not met** |
| B1d characterization method named | **met, exceeds** |
| B1e working set vs LLC reported | met, inherits B1b |
| B1f ordering frozen before characterization | **met, exceeds** |
| B1g explicit D3 statement | **met** |

**B1c is the substantive failure.** `required_reporting` carries `achieved_memory_throughput_GB_per_s_when_observable` and `achieved_to_measured_bandwidth_fraction_when_observable`. Both are conditional on observability, which in practice means uncore or IMC counters — restricted or absent on most edge platforms, which are exactly the platforms in scope.

This creates a closed loop that defeats the finding. `interpretation_rule` states the report MUST NOT claim cache or bandwidth dominance without these recorded environment facts. So on a platform without counters, both fields go empty and the contract then forbids the very attribution B1 was raised to enable. B1 exists because `phase_a_scope.objective` asserts which of arithmetic, cache and bandwidth dominates; the correction makes that assertion unfalsifiable on the likely hardware.

The escape is that the quantity does not need to be observed. Phase A is fixed-work exact dense scan, so bytes streamed per query is `gallery_payload_bytes` exactly and completed QPS is retained:

```
derived_stream_rate_GB_s = gallery_payload_bytes × completed_QPS / 1e9
bandwidth_utilization    = derived_stream_rate_GB_s / measured_achievable_bandwidth_GB_per_s
```

always computable, both arms, every load point, no counters.

*Minimum correction:* add `derived_stream_rate_GB_per_s` and `derived_bandwidth_utilization_fraction` to `required_reporting` as **unconditional**, and confine `_when_observable` to the counter-based refinement. Amend `interpretation_rule` so bandwidth-proximity statements rest on the derived figure, with counters as corroboration.

**B1b is partial.** `sharing_topology` and `inclusivity_policy` are present, which is what makes an effective figure derivable, but the recorded capacity is named `l3_or_llc_capacity_bytes_total` and `required_reporting` asks for `last_level_cache_capacity_bytes` and `arm_working_set_to_llc_ratio` without saying which denominator. On a chiplet, cluster or heterogeneous-core part with the benchmark pinned to a subset of cores, the package total is too large a denominator and the ratio errs toward looking more cache-resident than the arm is — the permissive direction. *Minimum correction:* add `llc_capacity_bytes_effective_for_benchmark_thread_set` and bind `arm_working_set_to_llc_ratio` to it.

**Exceeding the criteria:** B1d asks for a named method; the correction supplies method, tool and version, kernel definition, thread count, affinity, repetitions, timestamp and raw artifact reference. B1f asks for a freeze-ordering rule; the correction supplies one and adds the remedy path — if characterization motivates a change, open a new prospective identity and repeat the review sequence. B1g is stated directly in `firewall_note` and correctly conditioned on the ordering.

---

## B2 — saturation and censoring guard: **not met**

| Criterion | Result |
| --- | --- |
| B2a pairwise guard | **met, exceeds** |
| B2b regime-assignment rule frozen and computable | **not met** |
| B2c absolute burst frozen, arm-relative additive | **met** |

**B2a exceeds.** `required_pairwise_rule` covers latency, throughput, queue recovery **and energy**; `cross_regime_ratio_permitted: false`; `right_censored_ratio_permitted: false`; two status tokens defined for invalid pairs. The five labels include `INDETERMINATE` and the rule fails closed on it — my three-outcome and fail-closed requirements are both satisfied, with a richer taxonomy than I asked for.

**B2b is the failure, and it is the one that matters most in this document.** The correction freezes the *labels* and does not freeze the *classifier*. Nothing states what assigns a `(arm, gallery, offered_QPS)` cell to `UNSATURATED` rather than `SATURATION_TRANSITION` or `SATURATED` — no completed-to-offered tolerance, no queue-depth trend criterion, no latency-inflation criterion.

The consequence is that whether a paired ratio may be published at all is decided by an analyst looking at the data, after the run. This project has spent six review cycles removing exactly that freedom — from estimator selection in S4, from operational thresholds, from the D2 anchor, from the informational-overlap classifier. B2b is the one place it survives, and it sits on the switch that governs whether the headline comparison can be stated as a number.

*Minimum correction:* freeze a rule computable from already-retained quantities, three-valued with `INDETERMINATE` defaulting to not-same-regime. Any of these would do, and the choice is the author's:

- `completed_QPS / offered_QPS` above a frozen tolerance → `UNSATURATED`, below a second frozen tolerance → `SATURATED`, between → `SATURATION_TRANSITION`;
- a frozen queue-depth trend criterion over the steady window;
- a frozen latency-inflation criterion relative to the lowest-load point.

The specific numbers do not matter to this check. That they are frozen before the run does.

---

## B3 — backend dispatch observability: **met**

| Criterion | Result |
| --- | --- |
| B3a dispatch equality not required | **met** |
| B3b NOT_EXPOSED escape partitioned | **met — predicted gap did not materialize** |
| B3c honest absence, mechanism claims blocked | **met, exceeds** |
| B3d recorded per arm | **met** |

I predicted the `NOT_EXPOSED_BY_BACKEND` escape would swallow caller-determined fields. It does not. `unavailable_dispatch_rule` triggers only on "no kernel/core identifier or blocking detail", and it requires the exact call shape to be recorded anyway even in that case. The field structure agrees: `_if_available` sits only on `backend_reported_blocking_parameters`, while `exact_call_shape` is an unconditional structured block carrying operation, GEMV-or-batched-GEMM, batch size, matrix and vector shapes, memory order and leading dimension. The partition I asked for is present, implemented differently from how I would have written it and correctly.

B3c exceeds the criterion by severing the two claims: a run with no dispatch record "may support the bounded paired dimension effect" while "mechanism-specific claims about microkernel dispatch MUST remain `NOT_DEMONSTRATED`". That preserves the primary result and blocks only the mechanism story, which is the right cut and better than what the original finding specified.

---

## L1 — energy conditioning: **met**

The rule conditions on offered QPS, saturation regime **and** steady-versus-burst, and applies to both `total_joules_per_identification` and the diagnostic incremental figure. The original finding named only QPS and only the total. "Every reported value MUST name…" satisfies L1b, since it binds each appearance rather than a methods section.

---

## L3 — percentile support reporting: **not met (L3b)**

L3a is met: preamble statement, designed-outcome framing, no post-hoc relaxation.

**L3b is not addressed.** The suppression rule keys on *completed* samples, so an empty cell carries two opposite meanings. From the frozen grid and the 600 s window the expected completed counts are 150, 300, 600, 1200, 2400 and 4800 — so suppression is *by design* at 0.25 QPS for p95 and at 0.25, 0.5 and 1.0 QPS for p99. An empty p99 cell at 4 or 8 QPS cannot be by design; it means the arm completed fewer than 1000 queries in ten minutes, which is a saturation finding, not a gap. Nothing requires the expected counts to be published alongside the actual ones, so the two are indistinguishable to a reader.

This is a reporting limitation and low severity in isolation. It is worth more than its class here because it is the cheapest independent cross-check on B2's regime assignment, and B2b is open.

*Minimum correction:* publish expected and actual completed counts per cell.

---

## L2 — intermediate working set: **met**

Classified `FUTURE_SENSITIVITY_REQUIREMENT` / `NOT_PHASE_A_BLOCKER`, with an explicit prohibition on interpolating G0 and G2 and a requirement that Phase A state no intermediate claim if G1 never arrives. Both criteria met.

---

## A1/A2/A3 — additive and non-perturbing

**A1 — met, and verified rather than accepted.** `composition_rule` states the artifact does not rewrite historical bytes. I checked rather than took it: the three accepted construct objects are **byte-identical between `b5720dd7` and `cb43fdb1`** —

```
BENCHMARK_V0_3            4b6a9952e203…  identical
ADDENDUM_V0_2             5b2750dee497…  identical
ENVIRONMENT_LOCK_V0_6     a43861120930…  identical
```

The corrections are a separate artifact that extends rather than edits. CV1–CV10 assessed exactly these bytes.

**A2 — not met.** Nothing in the correction addresses where the bandwidth characterization sits in the execution sequence. `must_record_B1_bandwidth_value_before_result_bearing_phase_a: true` establishes that it precedes the run, which is necessary and not sufficient: "before" admits "immediately before the first measured block". A STREAM-class run saturates memory and heats the part, and CV7's counterbalancing was accepted on the assumption that nothing else occupies the device between measured blocks. *Minimum correction:* freeze the characterization's position in the sequence, require it outside the measurement blocks, and require an idle or thermal-settling period before the first measured block.

**A3 — open recommendation.** The second-reviewer verdict block still has no field for this. Recommend `CORRECTIONS_ADDITIVE_AND_DO_NOT_PERTURB_ACCEPTED_CONSTRUCT: yes | no`, so `PLATFORM_MATERIALIZATION_CURRENTLY_ADMISSIBLE: yes` cannot be reached without someone having looked at A2.

---

## What the independent reviewer should do with this

Four items fail my criteria: **B1c**, **B1b (partial)**, **B2b**, **L3b**, plus **A2** outside the original set. Two are substantive — B1c and B2b — and both are single-clause additions to the correction artifact, not redesigns.

None of this is a finding by an independent reviewer and none of it obliges a branch change now. Changing the branch would stale the binding and the package, which costs more than carrying a known gap into a review that will read the corrections anyway.

The independent reviewer is free to disagree with any criterion here, and has more standing than I do at B1c and B2b specifically, since those are the places where I am marking my own intent. What they should not do is treat this document as evidence of closure. It is a barème and a score, and the score is partial.
