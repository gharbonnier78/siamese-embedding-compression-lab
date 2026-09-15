# Study 1B — focused pre-execution semantic-hardening re-review request

Date: 2026-09-14  
Scope: non-outcome engineering provenance/firewall design only  
Harness: `gharbonnier78/scientific-research-harness@3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`

## Review basis

The D1-D3 design track was accepted on reviewed head `cb124244ecdc285c1c711dd28cc1a074ff645ddc`.
This request does **not** reopen or rewrite that accepted history. It asks whether three explicitly non-blocking reviewer findings
have been closed prospectively before an execution-specific lock is frozen.

Primary prospective artifacts:

- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_D1_D3_ADDENDUM_V0_2_2026-09-14.yaml`
- `protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_6_2026-09-14.yaml`
- `protocol/chronicle/STUDY1B_PR50_PREEXECUTION_SEMANTIC_HARDENING_V0_6_OPEN_2026-09-14.yaml`
- `tests/test_study1b_engineering_benchmark_contract.py`

Accepted historical basis:

- `protocol/reviews/PR50_CB124244_D2_V05_FOCUSED_REREVIEW_VERDICT_2026-09-10.md`
- `protocol/chronicle/STUDY1B_PR50_CB124244_D2_V05_ACCEPT_2026-09-14.yaml`

## Questions for the reviewer

### N4 — possession versus creation/framing influence

Does v0.6 preserve D1 as the accountable completeness backstop while allowing D2 to retain an operative role for genuinely
pre-existing external evidence that the attester later receives, reviews or cites?

Required properties:

- mere receipt/possession/review is not itself treated as influence over creation;
- production, commissioning, requesting, specifying, directing or materially framing evidence requires D1 treatment;
- ambiguity defaults to D1 and potentially informative treatment;
- informative evidence still cannot silently tune an untouched prospective lock.

### N5 — scope of “structural impossibility”

Does v0.6 make clear that only temporal ordering against the immutable repository-root bound is mechanically checkable,
while source independence, absence of creation/framing influence and completeness of disclosure remain provenance/attestation claims?

The reviewer should reject any wording that could be read as making the whole D1/D2 mechanism objective.

### R1/N2 — portable-choice informational overlap

Does the choice-specific classifier close the previous under-inclusion created by the global conjunction
`dimension AND search-family AND hardware-class`?

The intended semantics are:

- hardware class may matter for platform-specific choices;
- hardware mismatch alone does **not** discharge relevance for backend/BLAS/runtime evidence;
- hardware mismatch alone does **not** discharge relevance for threading/affinity/parallelism evidence;
- measurement-method evidence may transfer across hardware, dimensions and search families;
- uncertainty defaults to `INFORMATIVE`;
- `NOT_INFORMATIVE` requires attributable rationale.

Please explicitly state whether this closes R1/N2 sufficiently for an execution-specific lock to be frozen later.

### N6 — package transport rule

This is process hardening, not a scientific/design gate. The next transport package must include the exact normative files and
expected Git blob SHA-1 values, so the reviewer can locally recompute:

`SHA1("blob " + byte_length + "\0" + content)`

The package must also be self-contained for any focused test the reviewer is asked to execute.

## Requested verdict

```text
VERDICT: ACCEPT | ACCEPT_WITH_CHANGES | REJECT_OR_REDESIGN
N4_CLOSED: yes | no
N5_CLOSED: yes | no
R1_N2_PORTABLE_CHOICE_OVERLAP_CLOSED: yes | no
N6_PACKAGE_RULE_ACCEPTED: yes | no
PREEXECUTION_SEMANTIC_HARDENING_SATISFIED: yes | no
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
CONSTRUCT_VALIDITY_REVIEWED: no
```

## Protected boundary

Do not open or use:

- Study 1B SCREEN;
- qualification TEST;
- real raw512/random128/PCA128/Siamese128 outcome performance;
- representation geometry;
- amendment;
- S4N3.

S4N1 and S4N2 remain `CLOSED_NEGATIVE`; S4N3 remains `NOT_LAUNCHED`.

## Execution status

Canonical Phase A remains **NO** regardless of this review result because real platform/measurement environment and configuration-choice
provenance/attestation are not yet materialized. Construct validity remains a separate review question and is not established here.

## Next step if accepted

If N4, N5 and R1/N2 are accepted, perform a separate construct-validity review **before** selecting and freezing the real execution platform.
Only after construct validity is accepted should engineering authority bind hardware, power meter, off-device load generator and attributable
choice provenance in a new immutable execution-specific lock.