# Focused D2-closure re-review — PR #50, head `022e8f50`

| Field | Value |
| --- | --- |
| Head under review | `022e8f50437dca4b2aa56a034a5fb63e7751301b` |
| Previous reviewed head | `f5d748006bdde7ab6e71fa4396d5e1a5e09d6aaa` |
| Binding comment | PR #50 comment `5613343327` |
| Package | `PR50_022E8F_D2_CLOSURE_PACKAGE_2026-09-10.zip` |
| Announced SHA-256 | `9516772c06ff975d62740078d81834ca2042e3363f9a45379694fcfd63cc498c` |
| SHA-256 as received | **matches exactly** |
| Review date | 2026-09-10 |

```
VERDICT: ACCEPT

D2_CLOSED:                                yes
PRIOR_DESIGN_CONDITIONS_SATISFIED:        yes   (D1, D2, D3 all closed)
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
CONSTRUCT_VALIDITY_REVIEWED:              no
```

No blocking change remains in the D1–D3 design track. Three items are recorded below as open, none of them a condition of this verdict.

---

## 1. Verification performed

- **ZIP SHA-256 matches the announced value exactly.** First time in this series that an announced value was supplied and could be checked; it checks.
- **15 files, 14/14 covered by `06_PACKAGE_SHA256.json`, 0 mismatches.** The only uncovered file is the manifest itself.
- **Assurance test executed independently from the package as shipped:** `python3 tests/test_study1b_engineering_benchmark_contract.py` → **15 tests, 15 pass, exit 0.** The startup traceback in `04_LOCAL_TEST_EXECUTION.txt` is sandbox noise, not test failure; leaving it unedited remains the right call.
- **Not verified:** the anchor commit `878bfe2a` and its timestamp, the two blob SHA-1 correspondences, and the CI conclusions. All author/connector-supplied. The package labels the anchor evidence `author_connector_supplied_navigation/path-history evidence`, which is the correct handling. See §4.

The self-caught bytewise difference in the transported test is worth recording as good practice. A transport artifact that silently diverges from its repository blob is exactly how a package stops testing what it claims to test.

## 2. D2 — closed

The defect identified at `f5d748` was that `structural_impossibility_rule` anchored on the generator-code commit, which necessarily postdates the specification commit and therefore opened a `[specification_commit, generator_commit)` window in which evidence passed the impossibility test while having been fully capable of being informed by an already-published workload definition.

Lock v0.4 closes it, and closes it in the right shape rather than by patching a value:

- `structural_impossibility_anchor.rule` binds impossibility to the **earliest immutable commit timestamp at which the classifier-relevant workload attributes were sufficiently published**, and states explicitly that the later generator-code commit timestamp MUST NOT be used as the bound.
- The anchor is materialized: `878bfe2a64b34cce474a627d04b30233e2356958`, `2026-09-07T06:33:05Z`, benchmark v0.1, with an immutable URL and the published attributes enumerated (512/128, FP32, CPU, exact dense, G2). Earlier than the `2026-09-08T15:29:02Z` specification commit that v0.3 recorded, as it should be.
- Generator identity is moved out of the anchor into `target_workload_replay_identity`, carrying `generator_identity_role: REPLAY_AND_RESULT_PROVENANCE_NOT_STRUCTURAL_IMPOSSIBILITY_BOUND`. It remains mandatory before execution, for the right reason. Separating the two roles is the correct fix; keeping the requirement while removing it from the bound is precisely what was asked.
- `structural_impossibility_claim_available_for_qualifying_pre_anchor_evidence: true`. The claim is now live for pre-anchor evidence, which was the point of D2 from the start.
- `conservative_interpretation` states plainly that the anchor may reject genuinely uninformed post-anchor evidence, and that conservative rejection is preferred to reopening the permissive window. That is the correct direction of error and the record says so rather than glossing it.

**R2 from the previous cycle is also fixed.** `hardware_class_source` now resolves to `required_environment.device_under_test.hardware_class`, a field that exists, and a test asserts the exact string.

**Housekeeping.** `required_environment.code_identity.environment_lock_path` self-reference corrected from v0.3 to v0.4, with a dedicated regression assertion. Chronicle 044 records it as `semantic_effect: NONE_HOUSEKEEPING_ONLY`, which is accurate. The audit that found it was the author's own.

D1 and D3 are unchanged at this head and remain closed as determined at `f5d748`.

## 3. Open items — recorded, not conditions

### N1 — the anchor bounds *public* knowability, not the attester's

This is new. I did not raise it at `f5d748` and I am not using it to hold D2 open; the change I asked for was made, in the shape I asked for. It should be in the record before the execution-specific lock is frozen.

A commit timestamp establishes when the workload became knowable **to someone reading the repository**. The party the firewall constrains is the party that wrote the specification, and they knew its content before committing it. Evidence dated shortly before `2026-09-07T06:33:05Z` could therefore have been informed by an in-preparation design while still passing the impossibility test.

The mechanism to fix this already exists in the lock: it is D1. The two should be explicitly divided, so that a reader cannot take ordering alone as sufficient for the case where the real risk sits:

- **Ordering (D2)** discharges the negative for third-party or pre-existing external evidence.
- **Attestation (D1)** is what carries the negative for evidence the attesting party produced or commissioned. The anchor does not substitute for it.

One clause. Suggested placement is alongside `conservative_interpretation`.

A related observation that bears on how much the anchor buys. Vector dimensionality 128/512 has been this study's subject since the preregistration, well before the anchor commit; only the search family arrived with benchmark v0.1. The anchor therefore rests on `EXACT_DENSE_DOT_PRODUCT_TOP1` being the last classifier attribute to become public, and exact dense top-1 is the obvious default baseline for embedding-search work. The anchor is sound as a bound; it is less protective in practice than its date suggests. That is another reason the D1/D2 division above matters.

### N2 — R1 remains open

The overlap classifier is still conjunctive: dimensionality AND search family AND hardware class. A 512D exact-dense measurement on a *different* hardware class is classified non-informative, yet it is materially informative for the lock-defining choices that transfer across hardware classes — `search_backend_and_blas_runtime`, `benchmark_thread_count_and_affinity`, and the energy measurement methodology. Non-blocking at `f5d748`, non-blocking here, still open. It should close before the execution-specific lock is frozen, because it governs exactly the choices a cross-hardware benchmark could silently make.

### N3 — schema boundary

`STUDY1B_S4N1_S4N2_SHARED_POPULATION_AND_T19_CLARIFICATION_2026-09-08.yaml` still carries `schema_version: "1.0"` as a string with no `schema_id`, is dated the same day as the D4 policy, and appears in neither the conforming examples nor the historical-compatibility list. Assign it a family or name it in the historical list. Non-blocking.

## 4. What this verdict rests on

Every other closure in this series has been checkable from the package itself. D2 is not. Its closure rests entirely on one fact I cannot verify: that `878bfe2a` at `2026-09-07T06:33:05Z` is real, and is the *earliest* commit publishing the classifier-relevant attributes.

If a materially informative measurement was described in the repository before that commit, the anchor is still too late and D2 reopens. The package is honest about this — it classifies the anchor as author/connector-supplied — but the dependency deserves to be named, because it is now the single load-bearing unverified claim in the D1–D3 track. One reviewer with repository access confirming the anchor is the earliest such commit would retire it permanently.

## 5. Execution and scope

`CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no`, correctly and for two independent reasons. `execution_admissibility` is unchanged from v0.3 and the blocker set is test-enforced as exactly `{PLATFORM_AND_MEASUREMENT_ENVIRONMENT_NOT_MATERIALIZED, CONFIGURATION_CHOICE_PROVENANCE_NOT_MATERIALIZED}`. Closing the last design condition does not move this, and neither the lock, the chronicle nor the README suggests otherwise.

`CONSTRUCT_VALIDITY_REVIEWED: no`. Whether Phase A measures what it is posed to measure remains unreviewed by anyone in this series. Five cycles of assurance closure do not approach it, and this `ACCEPT` must not be read as approaching it. It covers the D1–D3 provenance and firewall design, nothing else.

## 6. Reviewer disclosure

AI-assisted, single session. ZIP checksum verified against the announced value, package manifest verified 14/14, assurance test executed independently from the package as shipped, lock v0.4 read in full, D1 and D3 clauses re-checked at this head for drift.

- I did not produce the review on `12827b23`. I reviewed `ab7f3d0`, `f5d748` and this head.
- Repository-side claims — anchor commit and timestamp, blob SHA-1 correspondence, CI conclusions — not independently verified; recorded as author-supplied. §4 states what turns on this.
- Benchmark v0.3 was re-read only for the clauses D1–D3 touch.
- No SCREEN, qualification TEST, real route performance, representation geometry, amendment or S4N3 was opened or required at any point in this review.
