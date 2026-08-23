# Study 1 — Double review request before execution

Status: `REVIEW_REQUEST`

This review concerns **design only**. No Study 1 outcome-bearing execution is authorized by
this request.

## Review target

Authoritative draft artifacts:

- `protocol/studies/study_1_face_backbone.yaml`
- `protocol/studies/study_1_preregistration.md`
- `RESEARCH_PROGRAM.md` for programme context
- `harness-adoption.yaml`
- pinned `scientific-research-harness/HARNESS.md` at
  `1cead5808c126fd38e7505c27502fb3e7671c69a`

Study 0 remains closed with `C-NI-001 = NOT_DEMONSTRATED` and
`C-SUP-001 = NOT_DEMONSTRATED`. The proposed Study 1 sequence is:

`face-specific raw 512D qualification -> gate -> matched 512D/128D compression study`

The raw 512D foundation must pass before compression work may begin.

## Review A — scientific / harness

Please inspect the proposal as a scientific contract rather than as a coding task.

Return one of:

- `VERDICT_A: ACCEPT`
- `VERDICT_A: REQUEST_CHANGES`

and explicitly address:

1. Is the Study 1A question falsifiable and logically prior to compression?
2. Are the benchmark roles separated appropriately (sanity, screening, qualification)?
3. Are official folds/protocols protected against result-driven redesign?
4. Is the raw-512D viability gate required to be numeric and frozen before outcomes?
5. Is the Study 1B estimand `delta_fnmr` correctly bounded and interpretable?
6. Is identity dependence handled at the correct statistical unit?
7. Are screening and qualification evidence prevented from being conflated?
8. Are seed, multiplicity and non-inferiority decisions required before outcome access?
9. Are prohibited inferences sufficiently explicit?
10. Does the pedagogical layer explain rather than authorize scientific claims?
11. Is any scientific choice still underspecified enough to block execution?

The reviewer should list every blocking item that must be frozen before `VERDICT_A: ACCEPT`.

## Review B — technical / reproducibility

This review must be independent of Review A in role and reasoning, even if performed by
another LLM or reviewer using the same repository.

Return one of:

- `VERDICT_B: ACCEPT`
- `VERDICT_B: REQUEST_CHANGES`

and explicitly address:

1. Can the exact backbone architecture and weight artifact be pinned and checksummed?
2. Is licence/research-use provenance reviewable before download/use?
3. Can preprocessing, face detection/alignment, crop, colour order and normalization be
   made deterministic and replayable?
4. Are benchmark folds/splits/protocol semantics implementable without hidden tuning?
5. Can identity/image/near-duplicate overlap be audited and recorded?
6. Can threshold selection be kept strictly on authorized development data?
7. Are model/projection seeds separated from bootstrap Monte-Carlo seeds?
8. Are raw/random/PCA/Siamese input embeddings and data roles genuinely matched?
9. Can the exact environment and replay commands be captured?
10. Are failure modes such as unavailable IJB-C data, failed face detection, missing images
    and degenerate bootstrap draws specified before execution?
11. Is any implementation detail underspecified enough to block execution?

The reviewer should list every blocking item that must be frozen before `VERDICT_B: ACCEPT`.

## Mandatory release condition

No Study 1 test may start until all of the following are true:

1. Review A returns `ACCEPT`.
2. Review B returns `ACCEPT`.
3. All blocking protocol placeholders are resolved and frozen.
4. CI and Research Assurance are green for the frozen protocol commit.
5. The Chronicle records the reviewed freeze and exact next admissible action.
6. A separate explicit human `GO` authorizes Study 1A execution.

A review acceptance is not itself execution authorization.

## Expected next action after this PR

If either review requests changes: amend the draft only; do not execute.

If both reviews accept: freeze/hash the complete preregistration, run the non-outcome-bearing
validation/CI checks, record the Chronicle entry, and request explicit `GO` for Study 1A.
