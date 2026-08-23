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
  `422e08f3d6483ca11fa5a4767cffa99ce386bde5`

The selected engineering-care profile for Study 1 is **POC**. Under the pinned harness this is
not a waiver for code quality or security: the implementation must remain understandable,
reviewable and reproducible, with focused tests, code/static checks, dependency/secret review,
relevant security assumptions and explicit residual risks before outcome-bearing execution.

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
12. Is the harness upgrade itself correctly bounded so that historical Study 0 evidence is not retrospectively reinterpreted?

The reviewer should list every blocking item that must be frozen before `VERDICT_A: ACCEPT`.

## Review B — technical / reproducibility / engineering assurance

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
11. Is the Study 1 system/decomposition and code structure documented sufficiently for a competent human reviewer?
12. Are critical pure-logic paths covered by focused automated tests?
13. Are syntax/type/lint or equivalent code checks defined and visible in CI?
14. Is secret scanning present, and are dataset credentials/tokens prohibited from the repository?
15. Is dependency/supply-chain review present for Python packages, model weights and downloaded artifacts?
16. Is static security analysis used where supported, with findings fixed, shown not applicable, or explicitly accepted with bounded rationale?
17. Are security assumptions and residual risks explicit rather than implied by the label `POC`?
18. If any runtime telemetry is used as engineering/test evidence, is there a predeclared expected-signal contract and pinned applicable OpenTelemetry specification/semantic-convention version?
19. Is any implementation or engineering-assurance detail underspecified enough to block execution?

The reviewer should list every blocking item that must be frozen before `VERDICT_B: ACCEPT`.

## Mandatory release condition

No Study 1 test may start until all of the following are true:

1. Review A returns `ACCEPT`.
2. Review B returns `ACCEPT`.
3. All blocking protocol placeholders are resolved and frozen.
4. The POC engineering-care obligations applicable to the implemented Study 1 pipeline are present and reviewable.
5. CI and Research Assurance are green for the frozen protocol/implementation commit.
6. Missing quality/security checks are not misreported as passing checks.
7. The Chronicle records the reviewed freeze and exact next admissible action.
8. A separate explicit human `GO` authorizes Study 1A execution.

A review acceptance is not itself execution authorization.

## Expected next action after this PR

If either review requests changes: amend the draft only; do not execute.

If both reviews accept: freeze/hash the complete preregistration, run the non-outcome-bearing
validation/CI/engineering-assurance checks, record the Chronicle entry, and request explicit
`GO` for Study 1A.
