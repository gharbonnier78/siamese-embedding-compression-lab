# Focused D2 v0.5 re-review — PR #50, head `cb124244`

| Field | Value |
| --- | --- |
| Head under review | `cb124244ecdc285c1c711dd28cc1a074ff645ddc` |
| Base | `5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7` |
| Pinned harness | `3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98` |
| Binding comment | PR #50 comment `5618135826` |
| Package | `PR50_CB124244_D2_V05_FOCUSED_REREVIEW_PACKAGE_2026-09-10.zip` |
| Announced SHA-256 | `473700dcc88dfd70c94e73e2f0231ae9f645fd80ed49b54ae2aec76ad83e58de` |
| SHA-256 as received | **matches exactly** |
| Review date | 2026-09-10 |

```
VERDICT: ACCEPT

D2_CLOSED:                                yes
D1_D2_RESPONSIBILITY_SPLIT_ACCEPTED:      yes
ROOT_PUBLIC_INFORMATION_BOUND_ACCEPTED:   yes
PRIOR_DESIGN_CONDITIONS_SATISFIED:        yes
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
CONSTRUCT_VALIDITY_REVIEWED:              no
R1_N2_PORTABLE_CHOICE_OVERLAP_CLOSED:     no
```

Three items recorded open below. None is a condition of this verdict. One (N6) is a change in how packages are transported, not in the design.

---

## 1. The reopening

This belongs at the top rather than in a findings list.

My verdict on `022e8f` closed D2 and said so, while flagging in §4 that the closure rested on one fact I could not verify — that `878bfe2a` was the *earliest* commit publishing the classifier-relevant attributes — and that a single reviewer with repository access could retire the dependency.

The audit was run. It falsified the anchor. `PR50_022E8F_D2_ANCHOR_REPOSITORY_AUDIT_2026-09-10.md` is recorded in the manifest with the role `repository_audit_that_reopened_d2`, and the superseded verdict is preserved in the repository rather than removed.

An accepted closure was reopened by the party holding the acceptance, on evidence they went and found themselves, against their own interest in closing. That is the behaviour this entire apparatus exists to produce, and it is the single strongest signal in five cycles. It should be in the chronicle in those terms.

## 2. Root public-information bound — accepted

The bound moves from `878bfe2a` (2026-09-07) to repository inception `4b40e7254bff1b88a44d13fb55b366bc7d3fc263` at `2026-08-07T08:23:56Z`, `parents: []`.

What matters here is not that the bound got earlier. It is that the claim changed **class**. "Is this the earliest commit publishing attributes X, Y and Z?" requires auditing an entire history to establish a negative, and it is exactly the kind of claim that failed last cycle. "Is this the repository root?" is a single fact with a definitive answer, settled by an empty parent list. The new bound cannot fail the way the old one did, because there is no earlier commit to find.

The supporting evidence exceeds what the bound needs. The root README already carried the 512→128 research question, the four routes, the FP32 per-template byte counts (2,048 versus 512), and a roadmap item naming 1:N retrieval, gallery indexing and latency measurement. `04_ROOT_BOUND_EVIDENCE.md` then declines to overclaim, stating explicitly that this does not mean the later CPU/G0/G2/threading/power contract existed at inception. Correct on both sides.

**Residual, and it is handled rather than open:** repository inception bounds *repository-published* knowability. The research question in the root README was formulated by someone before it was committed. No commit timestamp can bound what the authoring party knew. That residual is precisely what the D1/D2 split now carries, which is why the two items must be read together and why accepting one without the other would be wrong.

## 3. D1/D2 responsibility split — accepted

At `022e8f` I asked for one clause dividing the two mechanisms. What landed is more than that:

- **D2** is role-labelled `TEMPORAL_STRUCTURAL_IMPOSSIBILITY_FOR_EXTERNAL_PREEXISTING_EVIDENCE` and scoped to genuinely third-party or pre-existing external evidence, with the ordering condition against the repository bound, an independence-of-source condition, and an explicit statement that D2 cannot substitute for D1.
- **D1** is role-labelled `ACCOUNTABLE_NEGATIVE_FACT_FOR_ATTESTER_KNOWLEDGE_AND_ACTIONS` and carries the sentence that does the real work: **D1 applies even if the evidence predates public commit time.** That is the exact failure mode I raised, named and closed.
- The **conflict rule** defaults ambiguity to D1, treats the evidence as potentially informative, and forbids using D2 ordering alone to certify an untouched prospective lock. The default falls to the safe side, which is the property that matters when the rule is applied under pressure.

Accepted.

## 4. Open items — recorded, not conditions

### N4 — the D2 disqualifier list conflates influence with possession, and as written leaves D2 with no operative scope

D2 requires that the evidence was "not produced, commissioned, requested, reviewed, received or otherwise known by the attesting party."

To cite a source for a lock-defining choice, the attester must have it: `configuration_choice_provenance` requires `source_reference_or_identifier` and `rationale` for every choice. Citation entails possession. So every source that actually informs a choice trips "received", and D2 never independently discharges anything. A 2025 vendor datasheet — the paradigm case D2 exists to handle — fails the list purely because someone read it.

Two different things sit in one enumeration:

- **influence over the evidence's creation or framing** — produced, commissioned, requested, specified. These correctly force D1.
- **mere possession** — received, reviewed, otherwise known. These are entailed by citation and cannot be disqualifiers without emptying the mechanism.

**This does not reopen D2.** The error runs conservative: everything falls through to D1 attestation and nothing becomes permissive. But it should be fixed before the execution-specific lock is frozen, because that is the first moment anyone will try to apply D2 and discover it has no scope. Scope the disqualifiers to influence over creation or framing, leave possession out, keep the conflict rule as it stands.

### N5 — "structural impossibility" is narrower than the term suggests

Of D2's three conditions, only the timestamp ordering is objectively checkable. Independence of source and not-known-by are themselves attested negatives, discharged by the same accountable party under D1. D2 therefore contributes one objective condition and two attested ones.

This is not a defect — it is the correct architecture, and the conflict rule already makes D1 the backstop. It is a labelling risk. Someone reading "structural impossibility" downstream may cite it as though the whole mechanism were objective. One sentence saying which condition is checkable and which are attested prevents that.

### N6 — reviewability regression against D5

The package deliberately ships no normative artifacts, on the stated rationale that it should not silently reproduce or modify them. That rationale is sound and comes directly from last cycle's bytewise divergence in the transported test. But the consequence is that at this head I could not read lock v0.5, could not run the assurance test or observe its pass count, and could not verify any of the nine Git blob SHA-1 values, because the blobs are not present. My acceptance in §3 rests on an author-written excerpt, and an excerpt cannot show what changed elsewhere in the artifact.

D5 was closed at `f5d748` on exactly this property, and it has regressed.

There is a form that gets both properties at once: **ship the artifacts and their Git blob SHA-1 values, and have the reviewer recompute** `SHA1("blob " + bytelength + "\0" + content)` **locally.** Divergence is then detected by the reviewer rather than avoided by omission, and the reviewer can still read what they are accepting. That would have caught last cycle's divergence at the reviewer rather than only at the author.

## 5. Verification performed

**Verified by me:**

- ZIP SHA-256 matches the announced value exactly. Second consecutive cycle where an announced value was supplied and checked.
- 7/7 files covered by `99_PACKAGE_SHA256.json`, 0 mismatches; the only uncovered file is the manifest itself.
- The nested GitHub Actions artifact `06_STUDY1B_POC_ASSURANCE_ARTIFACT.zip` hashes to `60b9bcfc…34466`, matching the `github_reported_digest` recorded in `02_ASSURANCE_STATUS.json` exactly, and the SBOM's own internal `.sha256` verifies against its content. This is the first end-to-end digest chain for a CI artifact in this series. The caveat is that the GitHub-reported digest is itself recorded by the author, so what this establishes is that the transported artifact is the one the author claims GitHub produced — which closes the transport-divergence class for this file, and nothing beyond it.

**Not verified:**

- Lock v0.5 content, beyond `05_D1_D2_REVIEW_EXCERPT.md`.
- The assurance test and its pass count at this head.
- All nine Git blob SHA-1 values in `01_SOURCE_MANIFEST.json`.
- Root commit metadata — `parents: []`, timestamp, message — and the root README content quoted in `04`.
- The five workflow conclusions. The author's own framing, that these are technical assurance and not a semantic verdict, is correct and needs no qualification from me.

I attempted a direct fetch of the immutable lock v0.5 URL. My tooling refused it. The limitation is mine, not the package's, but it bears on N6: the package's reference-only form assumes a reviewer who can reach the repository, and I cannot.

## 6. Scope

`CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no`. Both independent blockers — platform and measurement environment, configuration-choice provenance and attestation — remain unmaterialized. Closing the last design condition does not move this, and nothing in the package suggests otherwise.

`R1_N2_PORTABLE_CHOICE_OVERLAP_CLOSED: no`. The D3 conjunction still under-classifies measurements informative for portable backend/BLAS, threading/affinity and energy-measurement choices. The excerpt declares it open in those words, which is the correct handling. It should close before the execution-specific lock is frozen, since it governs exactly the choices a cross-hardware measurement could silently make.

`CONSTRUCT_VALIDITY_REVIEWED: no`. Whether Phase A measures what it is posed to measure remains unreviewed by anyone in this series. Six cycles of provenance and firewall closure do not approach it. This `ACCEPT` covers the D1–D3 provenance and temporal-firewall design and nothing else, and it must not be cited as covering more.

## 7. Reviewer disclosure

AI-assisted, single session. ZIP verified against the announced SHA-256, package manifest verified 7/7, nested CI artifact digest and SBOM checksum verified, all six review-oriented files read in full.

- I did not produce the review on `12827b23`. I reviewed `ab7f3d0`, `f5d748`, `022e8f` and this head.
- My `022e8f` verdict closed D2 on an anchor that the author's subsequent audit falsified. §1 records this. My acceptance here is of a different bound and a different mechanism.
- Repository-side claims are recorded as author-supplied throughout; §5 lists exactly which.
- No SCREEN, qualification TEST, real route performance, representation geometry, amendment or S4N3 was opened or required at any point in this review.