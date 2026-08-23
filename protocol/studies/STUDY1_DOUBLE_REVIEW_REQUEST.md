# Study 1 — Double review request before execution

Status: `REVIEW_REQUEST`

This review concerns **design only**. No Study 1 outcome-bearing execution is authorized by this request.

## Review target

Authoritative draft artifacts:

- `protocol/studies/study_1_face_backbone.yaml`
- `protocol/studies/study_1_preregistration.md`
- `protocol/studies/STUDY1_BACKBONE_ACCEPTANCE_GATE.md`
- `protocol/studies/STUDY1_EXECUTION_ARCHITECTURE_AND_SBOM.md`
- `RESEARCH_PROGRAM.md` for programme context
- `harness-adoption.yaml`
- pinned `scientific-research-harness/HARNESS.md` at `422e08f3d6483ca11fa5a4767cffa99ce386bde5`

The selected engineering-care profile is **POC**. Code quality, dependency/supply-chain review, SBOM, secret/security checks, architecture documentation, replay and restart semantics are release obligations, not optional polish.

Study 0 remains closed with `C-NI-001 = NOT_DEMONSTRATED` and `C-SUP-001 = NOT_DEMONSTRATED`.

The proposed Study 1 sequence is:

`pretrained AdaFace R100/WebFace12M raw 512D qualification -> Gate A -> matched 512D/128D compression study`

The backbone is pretrained and frozen; training the face backbone from scratch is outside Study 1.

## Review A — scientific / harness

Return one of:

- `VERDICT_A: ACCEPT`
- `VERDICT_A: REQUEST_CHANGES`

and explicitly address:

1. Is qualifying a face-specific raw 512D substrate logically prior to compression?
2. Is the exact model choice sufficiently frozen before outcomes?
3. Are the published R100/WebFace12M references used only as bounded reproduction anchors, not as a universal SOTA claim?
4. Is Gate A correctly conjunctive and frozen before outcomes?
5. Are the fixed thresholds defensible: LFW >=99.62%; CFP-FP >=98.96%; CPLFW >=94.27%; CALFW >=95.82%; AgeDB-30 >=97.70%; IJB-C TAR>=97.16% / FNMR<=2.84% at FAR/FMR=1e-4?
6. Is IJB-C correctly treated as the primary low-FMR qualification endpoint, with `INDETERMINATE` if access is unavailable rather than post-hoc substitution?
7. Are official folds/protocols protected against result-driven redesign?
8. Is identity/template dependence handled at the appropriate statistical unit for uncertainty reporting?
9. Are Study 1A reproduction evidence and later Study 1B non-inferiority evidence kept distinct?
10. Are prohibited inferences explicit enough?
11. Does pedagogy explain rather than authorize scientific claims?
12. Does the harness upgrade preserve historical Study 0 provenance?

The reviewer must list every blocker before `VERDICT_A: ACCEPT`.

## Review B — technical / reproducibility / engineering assurance

This review must be independent of Review A in role and reasoning.

Return one of:

- `VERDICT_B: ACCEPT`
- `VERDICT_B: REQUEST_CHANGES`

and explicitly address:

1. Is the AdaFace R100/WebFace12M checkpoint source identity frozen and can its exact downloaded bytes be SHA-256 pinned before execution?
2. Are repository licence, checkpoint terms and WebFace12M-related usage constraints reviewed separately rather than conflated?
3. Is the 112x112 BGR, mean/std 0.5 preprocessing contract deterministic and replayable once the alignment implementation is pinned?
4. Are detection/alignment failures durable and never silently dropped?
5. Are dataset folds/templates/protocol semantics implementable without hidden tuning?
6. Can identity/image/near-duplicate overlap be audited and recorded?
7. Does the 4-vCPU/16-GB/14-GB GitHub-hosted architecture have an explicit smoke and resource-feasibility gate?
8. Is the work deterministically sharded so runner loss or timeout can resume without changing scientific identity or seeds?
9. Is 1-worker vs 4-worker output/digest equivalence required and testable?
10. Is interruption/resume equivalence required and testable?
11. Does aggregation reject mixed model hashes, preprocessing contracts, dataset manifests and protocol versions?
12. Is full face-backbone training absent from Study 1A, with pretrained inference only?
13. Are later PCA/Siamese fitting and bootstrap jobs separable and restartable?
14. Are direct/transitive dependencies pinned/locked before execution?
15. Is a machine-readable CycloneDX JSON SBOM generated from the actual frozen environment?
16. Does the SBOM/provenance record include direct Git commit pins and the model SHA-256?
17. Are `pip-audit` or equivalent dependency review, secret scanning and static security analysis defined where supported?
18. Is untrusted pickle-like model deserialization treated as a security boundary?
19. Are dataset credentials and biometric source data excluded from public logs/artifacts?
20. Are every quality/security finding and every missing check explicitly dispositioned rather than silently treated as passing?
21. Are environment capture, replay commands and residual risks sufficient for a competent human reviewer?

The reviewer must list every blocker before `VERDICT_B: ACCEPT`.

## Mandatory release condition

No Study 1 outcome-bearing test may start until all of the following are true:

1. Review A returns `ACCEPT`.
2. Review B returns `ACCEPT`.
3. Exact checkpoint SHA-256 and usage terms are frozen.
4. Exact alignment/detector implementation and version are frozen.
5. Lawful/reproducible benchmark access, especially IJB-C, is confirmed.
6. The 4-vCPU sharded/resumable smoke path, worker equivalence and restart equivalence are green.
7. Lock/frozen environment and CycloneDX SBOM exist.
8. Applicable POC code-quality/security checks are green or have explicit bounded dispositions.
9. CI and Research Assurance are green for the frozen protocol/implementation commit.
10. The Chronicle records the reviewed freeze and exact next admissible action.
11. A separate explicit human `GO` authorizes Study 1A execution.

A review acceptance is not itself execution authorization.
