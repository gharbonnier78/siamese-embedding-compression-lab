# Independent Design Re-Review — PR #50, head `12827b23`

| Field | Value |
| --- | --- |
| Head under review | `12827b23295608f7fdb1b986cd8f6414a818fd67` |
| Package | `PR50_12827B23_FINAL_DESIGN_REREVIEW_PACKAGE_2026-09-08.zip` |
| Announced SHA-256 | `27942c4135a3a07cd512f552da13abc29fa21a06c92056270988acb08e3175b7` |
| SHA-256 as received | **matches exactly** |
| Review date | 2026-09-08 |
| **Verdict** | **`ACCEPT_WITH_CHANGES`** |
| **Design accepted?** | **Yes**, conditional on D1–D3 below |
| **Execution admissible?** | **NO** |
| **Negative-provenance mechanism sufficient?** | **NOT YET SUFFICIENT** — v0.2 encodes neither of the two evidence forms |

---

## 1. Verification performed

Package SHA-256 matches. 13 files, 12/12 covered by the internal manifest, 0 checksum mismatches.

**Not verified:** the claim that the seven repository artifacts match their Git blob SHA-1 at `12827b23`. I have no repository access; that check rests on the author's connector query, not on mine. The same applies to the compare data in `09` and the CI conclusions in `10`.

**Assurance test executed.** `07_FOCUSED_ASSURANCE_TEST.py` resolves three inputs against a repository root. One of them — `protocol/decisions/STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml` — **is not in this package**; I supplied it from the earlier PR#50 transport package and reconstructed the expected layout. With all three inputs present: **11 tests, 11 pass**.

**What the tests are.** They assert that named keys exist in the YAML with specific boolean or literal values. They are contract-text drift detectors: they would catch a silent removal or weakening of the firewall clauses, and that is genuinely worth having. They verify no behaviour. The "assurance evidence, not scientific acceptance" framing in `10` is accurate and should be kept in exactly those words.

## 2. Benchmark v0.3 — accepted

The design is sound and several guards are better than what was asked for:

- Thresholds are null with `threshold_mode_if_null: CHARACTERIZATION_ONLY_NO_PASS_FAIL`, plus an explicit prohibition on choosing a threshold after inspecting results and applying it retroactively to that same execution. Post-result thresholds can govern only a newly identified execution.
- `phase_e_indexed_or_ann` is excluded from Phase A with the correct reason stated: an index or approximate search capable of changing returned identities is not a pure engineering optimization.
- Quantization is flagged as a separate intervention whose speed/energy gains do not establish biometric interchangeability.
- Autonomy figures must name their duty-cycle profile, and compute-only incremental energy may not be used for battery autonomy.
- `prelock_selection_guard` mirrors the lock's firewall faithfully, including the disclosure path when prior target-workload information exists.

## 3. Environment lock v0.2 — accepted with three required changes

Substantial improvement over v0.1. `configuration_choice_provenance` and `prelock_information_firewall` are the right two mechanisms, the firewall is genuinely label-independent, `allowed_source_types` is a closed list with `prohibited_undeclared_source_type`, and the disclosure path in `if_prior_target_workload_information_already_informed_a_choice` is good design — it gives an honest actor a way to comply rather than an incentive to conceal.

### D1 — the provenance record has no owner *(required)*

`required_fields_per_choice` captures `decision_authority_or_source`, but nothing binds a **person** to the declaration: no attester identity, no attestation date, no statement of responsibility. `target_benchmark_workload_used_to_inform_choice` is therefore a self-reported boolean that nobody answers for.

Note `08` asks whether v0.2 should encode one of the two evidence forms. It currently encodes **neither**. Two fields close most of the gap:

```yaml
required_fields_per_choice:
  - provenance_attested_by        # named human or role, not a system
  - attestation_timestamp
```

This does not prove the negative — nothing can. It makes the claim **imputable**, which is the entire content of form (1).

### D2 — form (2) is available in this lock and one field choice blocks it *(required)*

The lock already carries `synthetic_root_seed: 20260908` and `synthetic_generator_code_sha256`. If the generator code and seed are committed at a known time, then any target-workload measurement necessarily postdates that commit. A lock-defining choice whose evidence date precedes the generator commit **cannot** have been informed by target-workload measurement. That is a checkable ordering claim, not an unfalsifiable negative — exactly the structural-impossibility argument form (2) calls for, and it covers a real subset of the choices for free.

`evidence_date_if_known` is optional, which destroys precisely that property.

**Required:** make the evidence date mandatory whenever `source_type` is a measurement, and record the generator-commit timestamp in the lock so the ordering is checkable without repository access.

### D3 — the firewall's criterion is intent, not information *(required)*

Both artifacts scope the prohibition to a workload *intended to answer the same comparison question*. Intent is unauditable and is asserted by the party being constrained. The same weakness runs through two entries of `allowed_source_types`: `independent_non_target_workload_benchmark` and `prior_operational_measurement_unrelated_to_this_target_workload` both turn on a self-judgement of relatedness.

An exact-search latency benchmark at 512D on candidate hardware is materially informative about the 512D-versus-128D question regardless of what it was intended for.

**Required:** replace the intentional criterion with an informational one — any measurement whose workload shares the vector dimensionality, search/index type and hardware class under evaluation. That is checkable from a workload description; intent is not.

### D4 — schema-versioning defect propagates into the new artifacts *(recommended)*

Lock v0.2, benchmark v0.3 and Chronicle 041 all declare `schema_version: "1.0"` as a **string**, while the S4 result artifacts declare `1` as an **integer** and `harness-adoption.yaml` declares `"0.1"`. The prospective correction agreed in the previous cycle had its first opportunity here and was not applied. Distinct schema identifiers, or at minimum a consistent type, before more artifact families accumulate.

### D5 — the shipped assurance test is not executable from the package *(package only, not design)*

Include `03_S4_SHARED_POPULATION_T19_CLARIFICATION.yaml` (or the repository path it resolves to). As shipped, an external reviewer running `07` gets a `FileNotFoundError` before any test executes, and may conclude the assurance evidence is broken when it is merely incomplete in transport.

## 4. Execution admissibility — NO

Correct, and for two independent reasons rather than one. Beyond the unmaterialized hardware, wattmeter and load generator, `current_execution_gates` carries `configuration_choice_provenance: REQUIRED_NOT_YET_OBTAINED`. Even if the platform appeared tomorrow, the provenance gate blocks independently. That redundancy is good design and should be preserved when the lock is materialized.

## 5. Scope of this verdict

This review covers the **design** of benchmark v0.3 and lock v0.2, and the **sufficiency of the mechanism** proposed for substantiating the negative provenance fact.

It does **not** cover construct validity: whether the Phase A measurement design answers the 512D-versus-128D question it is posed to answer. No review in this series has covered that, and the accumulated confirmations must not be read as approaching it. Note `08` states this correctly and should stay in the record.

## 6. Reviewer disclosure

AI-assisted, single session. Package checksum-verified, assurance test executed after supplying one missing input, both contract artifacts read in full. Repository-side claims (blob SHA-1 correspondence, compare, CI conclusions) were not independently verified and are recorded as author-supplied.
