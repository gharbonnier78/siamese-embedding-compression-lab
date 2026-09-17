# Focused v0.6 semantic re-review — PR #50, head `c7d03cda`

This file archives the independent review result received on 2026-09-16. It is append-only review evidence. It does not rewrite the reviewed v0.6 normative artifacts, does not establish construct validity, and does not authorize Phase A.

| Field | Value |
| --- | --- |
| Repository | `gharbonnier78/siamese-embedding-compression-lab` |
| Pull request | `#50` |
| Head under review | `c7d03cdad3bdf460bc6261508f2dc416504c7e4b` |
| Base | `5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7` |
| Pinned harness | `gharbonnier78/scientific-research-harness@3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98` |
| Immutable preparation binding | PR #50 comment `5687327361` |
| Package | `PR50_C7D03CDA_V06_N6_FOCUSED_REREVIEW_2026-09-15.zip` |
| Package SHA-256 | `09302b89d9319aa5755672a7f7c6af2bb736f7863b47b64a54b9a380e36f51b5` |
| GitHub Actions artifact id | `10416176129` |
| GitHub Actions artifact digest | `sha256:b148623c9c90b26312e719dd4e09ec5c5ca690697d83eeba8dd09c1b8be13a0f` |
| Review date | 2026-09-16 |

## Reviewer verdict

```text
VERDICT: ACCEPT
N4_CLOSED: yes
N5_CLOSED: yes
R1_N2_PORTABLE_CHOICE_OVERLAP_CLOSED: yes
N6_PACKAGE_RULE_SATISFIED: yes
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
CONSTRUCT_VALIDITY_REVIEWED: no
```

## Transport verification reported by the reviewer

The reviewer reports that transport was checked with independently written code and then cross-checked with the package verifier:

- `20/20` package SHA-256 values and byte lengths verified;
- `16/16` Git blob SHA-1 identities independently recomputed from transported bytes;
- no manifest entry missing;
- bundled verifier: PASS;
- focused v0.6 contract test: `11/11`;
- lock/addendum agreement re-derived directly from the two YAML artifacts rather than accepted only through the bundled test;
- `paper/` and `handoffs/` scanned for scope leakage; no protected result opening reported;
- all reported scientific results remained bounded negative statements.

## N4 — accepted closed

The reviewer accepts that possession/receipt/review/citation are separated from influence over evidence creation or framing. A genuinely pre-existing external source such as a vendor datasheet does not lose D2 eligibility merely because the attester later receives, reviews or cites it. Evidence produced, commissioned, requested, specified, directed or materially framed by the attesting party remains D1 territory, with ambiguity failing closed.

The reviewer also calls out `completeness_backstop_applies_to_all_lock_defining_choices` as a useful additional protection: D2 does not remove the obligation to attest completeness of the evidence set for each lock-defining choice.

## N5 — accepted closed

The reviewer accepts the v0.6 wording because the misleading mechanism label was removed rather than merely annotated. Only temporal ordering is represented as mechanically checkable; external/pre-existing source classification, absence of attester influence and completeness remain provenance/attestation claims.

## R1/N2 — accepted closed

The reviewer accepts the choice-specific informational-overlap model. In particular, `measurement_method_portable` correctly does not require vector dimension or search family because measurement-plane design and wattmeter placement can transfer across compute/workload classes.

The reviewer also positively notes `consequence_if_informative_evidence_already_informed_choice`: when informative prior evidence has already shaped a choice, the remedy is disclosure, a new prospective design/execution identity, freeze and independent review rather than silent reinterpretation.

## N6 — accepted satisfied for this package

The reviewer accepts that the package transported exact normative bytes and enabled local Git-blob recomputation. N6 is therefore satisfied for the reviewed package.

## New transport-only findings — non-conditions of this ACCEPT

### N7 — expected Git blob SHA-1 provenance is not declared in the manifest

The reviewer independently recomputed the transported bytes and confirmed they match the values recorded as `git_blob_sha1_expected`, but notes that the manifest does not state where those expected values came from. If both the transported bytes and the expected values originated from the same drifted local copy, a reviewer could verify internal agreement without proving identity to the repository object at the reviewed head.

Requested hardening:

- declare a `git_blob_sha1_expected_source` tied to the repository object at the immutable reviewed head;
- preferably remove `git_blob_sha1_recomputed` from the authored manifest so the reviewer performs the recomputation rather than comparing two author-produced pre-agreed columns.

The current package builder actually obtains `git_blob_sha1_expected` with `git rev-parse <head>:<path>` and checks local bytes against that object before packaging; the review finding is that this provenance is not exposed in the package manifest itself.

### N8 — binding and bounded workflow evidence are requested by the prompt but absent from the package

The reviewer notes that the prompt requires verification of the immutable PR binding comment and the five bounded workflow successes, while neither object is transported in the package. The prior `cb124244` package transported both binding/workflow material and a CI artifact digest chain.

Requested hardening is additive: future delegated review packages should transport reviewer-verifiable binding evidence and exact-head bounded-workflow evidence rather than requiring repository reachability for those checks.

## Scope and consequences

This ACCEPT closes the focused v0.6 semantic hardening items N4, N5 and R1/N2 and accepts N6 for the reviewed package. It does **not** establish construct validity and it does **not** authorize canonical execution.

The following remain unchanged:

```text
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
CONSTRUCT_VALIDITY_REVIEWED: no
```

Protected Study 1B SCREEN, qualification TEST, real-route performance and representation geometry remain sealed. S4N3 remains unlaunched. Phase A remains unexecuted.

The reviewer explicitly notes that the protocol now sequences construct-validity review before physical materialization; that ordering is accepted as the correct next scientific-review boundary.
