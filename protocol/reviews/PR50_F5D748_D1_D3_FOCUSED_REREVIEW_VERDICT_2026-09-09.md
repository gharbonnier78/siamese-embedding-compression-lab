# Focused D1–D3 re-review — PR #50, head `f5d74800`

| Field | Value |
| --- | --- |
| Head under review | `f5d748006bdde7ab6e71fa4396d5e1a5e09d6aaa` |
| Previous reviewed head | `12827b23295608f7fdb1b986cd8f6414a818fd67` |
| Base | `5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7` |
| Pinned harness | `3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98` |
| Package | `PR50_F5D748_D1_D3_FOCUSED_REREVIEW_PACKAGE_2026-09-09.zip` |
| SHA-256 as received | `5d1949c82dfc38a808d0bfac4af07f03e5b9fe191104dab70a6ca8fbc0bd10a1` |
| Review date | 2026-09-09 |

```
VERDICT: ACCEPT_WITH_CHANGES

D1_CLOSED:                              yes
D2_CLOSED:                              no
D3_CLOSED:                              yes
PRIOR_DESIGN_CONDITIONS_SATISFIED:      no
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
CONSTRUCT_VALIDITY_REVIEWED:            no

BLOCKER: D2 — the structural-impossibility temporal anchor is the wrong one
         and is strictly more permissive than the D3 classifier requires.
```

One text change closes it. Nothing else in D1–D3 is open.

---

## 1. Verification performed

**Package integrity.** 19 files, 18/18 covered by `07_PACKAGE_SHA256.json`, 0 mismatches. The only uncovered file is the manifest itself, which is correct. No announced SHA-256 was supplied to me for the ZIP; the value above is what I computed on receipt and is recorded for binding, not as a match.

**Assurance test executed independently.** `python3 tests/test_study1b_engineering_benchmark_contract.py` from the package root: **14 tests, 14 pass, exit 0**. D5 is closed — the package now resolves all its inputs, including the S4 clarification, without reconstruction. The startup traceback in `05_LOCAL_TEST_EXECUTION.txt` is an artifact of the author's sandbox and not of the test; keeping it unedited in the log was the right call.

**Numerical claims recomputed from scratch.** All six Clopper-Pearson intervals in the S4 clarification reproduce to 10 decimal places from the recorded pass counts (3462/3476/3478 and 3388/3396/3414 out of 4000), all six binomial MCSE values match, and `t(0.975, df=19) = 2.0930240544083087` against `z = 1.959963984540054`, ratio `1.0678890382261181`, all exact. Every upper interval endpoint is below 0.90; the highest is 0.8798. The gate-robustness statement holds.

**Not verified.** Git blob SHA-1 correspondence at `f5d74800`, the compare in `04`, and the CI conclusions in `03` remain author/connector-supplied. The package marks them as such in every instance, which is the correct handling and matches what the prior cycle asked for.

---

## 2. D1 — attributable provenance: **closed**

`required_fields_per_choice` now carries `provenance_attested_by`, `attester_role`, `attestation_timestamp` and `attestation_statement`, and `attestation_requirements` adds `provenance_attested_by_must_identify_human_or_accountable_role: true` with `system_only_attester_permitted: false`. The canonical attestation statement is supplied verbatim rather than left to the attester to phrase.

This exceeds the two fields the prior cycle asked for. The `system_only_attester_permitted: false` clause in particular closes the obvious evasion, where a pipeline or agent identity is named as attester and no person answers for the record. The declaration is now imputable, which is the whole content of the requirement. Closed.

## 3. D2 — checkable temporal provenance: **not closed**

Two of the three components landed.

`evidence_timestamp` is now in `required_fields_per_choice`, and `measurement_source_requirements.evidence_timestamp_required: true` binds it for `source_type: preexisting_measurement`. The optional `evidence_date_if_known` that destroyed the property is gone. Correct.

The generator-code identity is `null`, `structural_impossibility_claim_available_now: false`, and the note states the specification timestamp is not substituted for the missing generator timestamp. Refusing to fabricate an unavailable anchor is the right call and I want it on the record as such.

**The defect is in the rule that will govern once the generator commit exists.** `structural_impossibility_rule` requires the evidence timestamp to be *strictly earlier than the generator code commit timestamp*. That anchor is unsound, and the package proves it internally:

The D3 classifier decides material informational overlap from **vector dimensionality (128 or 512), search/index computational family, and hardware class**. None of those three attributes requires the generator code or the root seed. All of them are fixed by the benchmark specification. A prior measurement that satisfies the classifier can therefore be constructed by anyone holding the specification, with no access to the generator whatsoever.

The generator commit necessarily lands at or after the specification commit. Anchoring impossibility on the generator commit therefore opens a window `[specification_commit, generator_commit)` in which evidence passes the impossibility test while having been fully capable of being informed by a known target workload. The rule as written is strictly more permissive than the firewall it is meant to support.

The anchor should be the earliest commit at which the classifier-relevant workload attributes became fixed. Note this is *earlier* than the `2026-09-08T15:29:02Z` recorded here: benchmark v0.1 of 2026-09-07 already fixed G2 × FP32 × CPU × exact dense × {512D, 128D}, so dimensionality and search family have been public since that commit.

**Required change:**

```yaml
structural_impossibility_anchor:
  rule: >-
    The impossibility anchor is the EARLIEST commit timestamp at which the workload
    attributes used by the informational-overlap classifier (vector dimensionality,
    search/index family) were fixed — not the generator-code commit timestamp, which
    is necessarily later and therefore admits evidence that could have been informed
    by the already-published specification.
  earliest_workload_defining_commit_sha: <benchmark v0.1 commit>
  earliest_workload_defining_commit_timestamp_utc: <its timestamp>
```

Keep the generator-code identity requirement — it is still needed for replay and for `result_provenance_requirements` — but stop using it as the impossibility bound.

Two consequences worth recording. First, `structural_impossibility_claim_available_now: false` is *conservative* rather than wrong: with the correct anchor, impossibility is already derivable now for any evidence predating the v0.1 commit. Second, this is a correction to a requirement the prior cycle itself specified. The author implemented D2 faithfully as written; the anchor named in that requirement was the wrong one, and I am not carrying it forward.

Until this lands, D2 is open, and with it `PRIOR_DESIGN_CONDITIONS_SATISFIED: no`.

## 4. D3 — informational firewall: **closed**

The intentional criterion is gone from both artifacts. `informational_overlap_rule` classifies on observable workload attributes with `intended_purpose_is_a_classifier_input: false` and `label_is_a_classifier_input: false`. `prelock_information_firewall` carries `label_independent: true` and `intent_independent: true`. The addendum's `prelock_selection_guard_v2` declares `classification_basis: INFORMATIONAL_OVERLAP_NOT_INTENT` and enumerates eight labels — smoke test, pilot, phase 0, exploratory run, dry run, preview, capacity check, tuning pass — as carrying no exemption. Naming the evasions explicitly is better than a general clause.

The two `allowed_source_types` entries the prior cycle objected to, `independent_non_target_workload_benchmark` and `prior_operational_measurement_unrelated_to_this_target_workload`, are gone. They are replaced by a neutral `preexisting_measurement` that triggers the workload signature and overlap assessment rather than a self-judgement of relatedness. That is the correct structural fix, not a rewording. Closed.

Two residuals, neither blocking closure:

**R1 — the classifier is conjunctive and under-inclusive for hardware-portable choices.** Overlap requires dimensionality AND family AND hardware class. A 512D exact-dense measurement on a *different* hardware class is therefore classified non-informative, yet it is materially informative for the lock-defining choices that transfer across hardware classes: `search_backend_and_blas_runtime`, `benchmark_thread_count_and_affinity`, and the energy measurement methodology. Consider making hardware-class overlap required only for the hardware-bound choices, and dimensionality-plus-family sufficient for the portable ones.

**R2 — dangling reference.** `hardware_class_source` points at `required_environment.device_under_test.model_or_declared_hardware_class`. That field does not exist; `device_under_test` has `model` and `hardware_class` as separate keys. The classifier's key input currently references nothing resolvable.

## 5. D4 and D5

**D4 — adopted, and correctly scoped.** The schema policy requires `schema_id` + integer `schema_version` + human-facing `artifact_version` prospectively, forbids cross-family inference from `schema_version` alone, explicitly declines retrospective rewrites, and gives a reasoned exclusion for `harness-adoption.yaml` as belonging to the upstream harness family. Environment lock v0.3, the addendum and Chronicle 042 all conform, and a test enforces it. Better than what was recommended.

One inconsistency: `STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml` carries `schema_version: "1.0"` as a string with no `schema_id`. It is dated the same day as the policy and appears in neither the conforming examples nor the historical-compatibility list. Assign it a family or name it in the historical list, so the policy's own boundary is unambiguous.

**D5 — closed.** Repository paths preserved, S4 clarification included, test runs from the package unmodified.

## 6. S4 clarification — BLOCKING-10 correctly discharged

This lands as an **append-only** clarification with `status: CLARIFIED_NO_CHANGE_TO_NEGATIVE_CLOSURE`, not as an edit to the archived S4N1/S4N2 results. That was the right and the only acceptable form, and I flagged the alternative as a more serious problem than the finding itself. It was not taken.

On substance the clarification is accurate and does not overclaim:

- The shared population is stated plainly, with `independent_lines_of_evidence_count: 1` and `uncertainty_procedures_compared: 2`, and the implication that neither result tests generator misspecification.
- The estimator-stop rationale is restated as protection against estimator shopping rather than accumulated independent evidence, and names the misreading it is guarding against.
- The t19 multiplier is stated exactly, with the honest qualifier that 6.79 % does not by itself explain the power difference.
- The unresolved SE-dispersion question is recorded as open rather than closed with a plausible story, and its admissible diagnostics need no new simulation and no protected outcome.
- The `0.0310` / `0.0510` limitation is attached to the figures themselves.
- `PROSPECTIVELY_PREFERRED` replaces `BEST`, with the maxima recorded alongside.

Nothing here needs changing.

## 7. Execution admissibility — NO, correctly

`canonical_phase_a_execution_permitted: false`, with the two independent blockers preserved and test-enforced as an exact set. `execution_gate_redundancy` in the addendum states the property explicitly: materializing hardware does not satisfy provenance, and completing provenance does not substitute for a bound platform. The redundancy the prior cycle asked to preserve has been preserved and hardened.

The lock also picks up several items from the first cycle that were not part of D1–D5: off-device load generator as canonical with device-side latency measured at the server boundary, external wall or device-input power plane with on-chip telemetry as `SUPPORTING_DIAGNOSTIC_ONLY`, a 10 Hz minimum sampling rate, swap disabled or zero-swap evidence required for RAM-residency claims, and generator commit timestamp in `result_provenance_requirements`.

## 8. Scope

This verdict covers **D1–D3 closure against the prior cycle's stated conditions**, plus the D4/D5 items and the S4 clarification.

It does **not** cover construct validity: whether Phase A measures what it is posed to measure. `CONSTRUCT_VALIDITY_REVIEWED: no`. Four cycles of accumulating assurance confirmations do not approach it, and a D1–D3 closure must not be rewritten as one. The package states this in three places and each of them should stay.

## 9. Reviewer disclosure and limitations

AI-assisted, single session. Package checksum-verified, assurance test executed independently from the package as shipped, all statistical claims in the S4 clarification recomputed from the recorded counts, all four contract artifacts read in full.

- Repository-side claims — blob SHA-1 correspondence, compare, CI conclusions — not independently verified; recorded as author-supplied.
- I did not produce the review on `12827b23`. I reviewed `ab7f3d0`. I have read the `12827b23` verdict as an input defining D1–D5, and I do not otherwise inherit its conclusions. Section 3 departs from one of them.
- Benchmark v0.3 was read for the clauses D1–D3 touch. I did not re-review it in full at this head; the prior cycle accepted it and I record that as inherited context, not as my finding.
- No SCREEN, qualification TEST, real route performance, representation geometry, amendment or S4N3 was opened or required at any point in this review.
