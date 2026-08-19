# Revue indépendante PR #32 — round 1

- Repository: `gharbonnier78/siamese-embedding-compression-lab`
- PR: #32
- Reviewed head: `07a9c7087cade8ecf7f2e7d3824a034a8fae7880`
- Base: `91b5b84f1d83c15bd2e3fbfa589f809461a77c8b`
- Pinned harness: `gharbonnier78/scientific-research-harness@1cead5808c126fd38e7505c27502fb3e7671c69a`
- Historical Study 0 scores opened during review: **NO**
- Verdict: **REQUEST_CHANGES**

This artifact archives the reviewer report supplied after an evidence-based review of the exact PR head above. The review deliberately ignored similarly named branches and did not open historical Study 0 score payloads.

## Scope and evidence inspected

The reviewer inspected the full 5-file PR diff and the binding artifacts required by the pinned harness: `AGENTS.md`, `harness-adoption.yaml`, the exact pinned `HARNESS.md`, the authorization YAML, preflight script, authorization tests, `protocol/scientific_chronicle.yaml`, the frozen Study 0 protocol/specification, the coverage contract, scientific harness gate, Study 1 preregistration, and the archived known-truth coverage evidence/reviews.

The reviewer executed ancestry/scope checks, `assert_execution_unblocked`, the historical-reanalysis preflight directly on the unmerged PR branch, 14 manual authorization mutation checks, and the full test suite. The reported full suite result was **110/110 OK**. CI/Research Assurance were reported as **NOT_VERIFIED** from the reviewer environment because its unauthenticated GitHub API access was rate-limited; the reviewer explicitly did not turn that unknown state into PASS.

## Finding PR32-1 — BLOCKING

**Authorization preflight passes on the unmerged branch itself.**

The reviewer executed `scripts/preflight_study0_historical_reanalysis.py` on the exact unmerged PR head while `git merge-base --is-ancestor HEAD origin/main` returned non-zero, yet the preflight returned PASS. The script checked only that `activation` had the string value `merge_to_main_after_review`; it did not bind that label to actual Git reachability from `main`.

Why this matters: an agent or human could run the preflight before review/merge and receive a positive authorization message even though the authorization is not yet operational. This is authorization leakage and a fail-open temporal boundary.

Minimal remediation requested by the reviewer: add an explicit fail-closed Git-state check proving that the execution HEAD is reachable from a local `main`/`origin/main` reference (or an equivalently strong real merge-state check). If merge state cannot be established, the preflight must fail closed.

- Material authorization scope change: **NO**
- New researcher GO required: **NO**

## Finding PR32-2 — NON_BLOCKING

**Negative-path regression coverage is materially thinner than the preflight's own fail-closed branches.**

The repository tests covered only a small subset of the negative paths. The reviewer independently mutated wrong prerequisite SHA, historical run, study id, seeds, replicate count, sampling unit, degeneracy action, score recomputation, all-pairs generation, coverage gate path/status/checkpoint, review path and Chronicle resolution; all were correctly rejected by the implementation.

Minimal remediation requested: add these negative cases to the repository regression suite so future edits cannot silently weaken currently working guards.

- Material authorization scope change: **NO**
- New researcher GO required: **NO**

## Finding PR32-3 — COSMETIC

The new preflight does not itself re-verify threshold/tie/sentinel semantics or the prohibition on synthesizing unobserved impostor edges. The reviewer classified this as cosmetic for PR #32 because no `src/` estimator/engine code is changed by the PR and those semantics remain properties of the already frozen Study 0 implementation/protocol.

No remediation is required for PR #32. A future preflight hardening note may cover these invariants.

## Frozen method assessment

The reviewer traced the authorization values directly to the frozen Study 0 protocol and confirmed the following unchanged: seeds `[11, 29, 47, 71, 101]`, 10,000 bootstrap replicates, `subject_slot` sampling, 963 subject draws per replicate, paired route draws, `delta_fnmr: 0.03`, `FAIL_REANALYSIS` degeneracy handling, immutable original scores/outputs, no retraining, no score recomputation, no all-pairs generation, no overwrite of original Study 0 outputs, `decision.state: INDETERMINATE`, and the exact historical run id.

## Prerequisite and claim-boundary assessment

The reviewer confirmed that the known-truth coverage gate, archived review, Chronicle resolution and frozen protocol are loaded from real repository artifacts rather than duplicated only in the new authorization declaration. No accidental scientific promotion was found: `C-NI-001`/`C-SUP-001` remain not demonstrated, E-STAT-001 remains open to corrected reanalysis, G2 is not passed, Study 1 remains draft/unstarted, and geometry remains outside the authorized scope.

## Chronicle / temporal semantics

The reviewer confirmed append-only preservation of earlier entries but identified the same root temporal issue from the Chronicle side: `CHRON-20260819-009` is already `RESOLVED` with `blocks: []` on the unmerged PR branch, while its prose says review and merge must happen before operational access. The requested remediation is therefore to make the preflight's machine behavior enforce the merge activation boundary rather than trusting prose or a string label.

## Explicit GO assessment

The existing researcher GO recorded at `2026-08-19T10:57:00+02:00` remains valid for the requested remediation because PR32-1 is implementation hardening and PR32-2 is test hardening; neither changes the material authorization scope. A material scope change would require a new GO, but the reviewer did not request one.

## Reviewer-prescribed next admissible action

Remediate PR32-1 without opening historical Study 0 scores, optionally close PR32-2 in the same pass, produce a new exact head, rerun required checks including the unmerged-branch activation test, and request a fresh independent review. Do not merge or open historical scores before the new exact head receives that review.