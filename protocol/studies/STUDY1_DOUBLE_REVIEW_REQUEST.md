# Study 1 — Double review request before execution

Status: `REVIEW_A_ACCEPT_REVIEW_B_HUMAN_ACCEPT_PENDING_FINAL_HEAD_GREEN`

This review concerns **design and engineering readiness only**. No Study 1 outcome-bearing execution is authorized by this request or by either review acceptance.

## Review target

Authoritative draft artifacts:

- `protocol/studies/study_1_face_backbone.yaml`
- `protocol/studies/study_1_preregistration.md`
- `protocol/studies/STUDY1_BACKBONE_ACCEPTANCE_GATE.md`
- `protocol/studies/STUDY1_EXECUTION_ARCHITECTURE_AND_SBOM.md`
- `RESEARCH_PROGRAM.md` for programme context
- `harness-adoption.yaml`
- pinned `scientific-research-harness/HARNESS.md` at `3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`

The selected engineering-care profile is **POC**. Code quality, dependency/supply-chain review, SBOM, secret/security checks, architecture documentation, replay and restart semantics are release obligations, not optional polish.

Study 0 remains closed with `C-NI-001 = NOT_DEMONSTRATED` and `C-SUP-001 = NOT_DEMONSTRATED`.

The proposed Study 1 sequence is:

`pretrained AdaFace R100/WebFace12M raw 512D qualification -> Gate A -> matched 512D/128D compression study`

The backbone is pretrained and frozen; training the face backbone from scratch is outside Study 1.

## Recorded review state

### Review A — scientific / harness

`VERDICT_A: ACCEPT`

The independent PR review found no blocking scientific-design flaw. Gate A remains conjunctive and frozen, Study 1A/1B remain separated, and no outcome-bearing execution is authorized by this acceptance.

### Review B — technical / reproducibility / engineering assurance

`VERDICT_B: HUMAN_ACCEPT_RECORDED`

The accountable human reviewer explicitly approved the engineering/reproducibility remediation on 2026-08-24. This acceptance does **not** waive machine evidence. It becomes effective for merge/readiness only if the exact current head has green CI, Research Assurance, Study 1 Engineering Assurance and Study 1 Progress Observability. Any subsequent material implementation change requires the reviewer to determine whether Review B must be repeated.

Outstanding pre-execution blockers remain independent of Review B acceptance:

- exact checkpoint bytes and SHA-256;
- checkpoint/training-data usage terms;
- lawful/replayable low-FMR benchmark access or an independently reviewed replacement amendment;
- final environment lock/SBOM and resource/replay evidence required by the execution contract;
- separate explicit human GO for Study 1A.

## NIST / IJB-C / FRTE clarification

NIST states that distribution of IJB-A, IJB-B and IJB-C was discontinued on 2023-03-14. The current NIST robust-comparison path is Face Recognition Technology Evaluation (FRTE), including FRTE 1:1 Verification, which evaluates submitted algorithms on NIST-sequestered datasets and reports FNMR at fixed FMR operating points.

Accordingly:

- FRTE 1:1 is an external methodological/operational reference, not local Gate A evidence;
- FRTE datasets are not treated as a downloadable replacement for IJB-C;
- the frozen IJB-C A3 threshold is usable only if a lawful, replayable IJB-C copy is demonstrated;
- otherwise Gate A remains `INDETERMINATE` until a public/replayable low-FMR benchmark, its reference value and numeric gate are frozen by protocol amendment and independently reviewed before outcomes;
- no IJB-C threshold may be transplanted to another dataset merely because the FMR operating point has the same numeric value.

Authoritative NIST references:

- https://www.nist.gov/programs-projects/face-challenges
- https://pages.nist.gov/frvt/html/frvt11.html

## Review A — scientific / harness checklist

The reviewer must explicitly address:

1. Is qualifying a face-specific raw 512D substrate logically prior to compression?
2. Is the exact model choice sufficiently frozen before outcomes?
3. Are the published R100/WebFace12M references used only as bounded reproduction anchors, not as a universal SOTA claim?
4. Is Gate A correctly conjunctive and frozen before outcomes?
5. Are the fixed thresholds defensible: LFW >=99.62%; CFP-FP >=98.96%; CPLFW >=94.27%; CALFW >=95.82%; AgeDB-30 >=97.70%; IJB-C TAR>=97.16% / FNMR<=2.84% at FAR/FMR=1e-4 when IJB-C is lawfully replayable?
6. Is IJB-C correctly treated as conditional on lawful/replayable access, with `INDETERMINATE` rather than post-hoc substitution?
7. Is FRTE correctly kept as external context rather than silently substituted for local replay evidence?
8. Are official folds/protocols protected against result-driven redesign?
9. Is identity/template dependence handled at the appropriate statistical unit for uncertainty reporting?
10. Are Study 1A reproduction evidence and later Study 1B non-inferiority evidence kept distinct?
11. Are prohibited inferences explicit enough?
12. Does pedagogy explain rather than authorize scientific claims?
13. Does the harness upgrade preserve historical Study 0 provenance?

## Review B — technical / reproducibility / engineering assurance checklist

The reviewer must explicitly address:

1. Is the AdaFace R100/WebFace12M checkpoint source identity frozen and can its exact downloaded bytes be SHA-256 pinned before execution?
2. Are repository licence, checkpoint terms and WebFace12M-related usage constraints reviewed separately rather than conflated?
3. Is the 112x112 BGR, mean/std 0.5 preprocessing contract deterministic and replayable?
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
17. Are dependency review, secret scanning and static security analysis defined where supported?
18. Is untrusted pickle-like model deserialization treated as a security boundary?
19. Are dataset credentials and biometric source data excluded from public logs/artifacts?
20. Are every quality/security finding and every missing check explicitly dispositioned rather than silently treated as passing?
21. Are environment capture, replay commands, progress logs and residual risks sufficient for a competent human reviewer?

## Mandatory release condition

No Study 1 outcome-bearing test may start until all of the following are true:

1. Review A returns `ACCEPT`.
2. Review B is accepted by the accountable reviewer and remains applicable to the final reviewed head.
3. Exact checkpoint SHA-256 and usage terms are frozen.
4. Exact alignment/detector implementation and version are frozen.
5. Lawful/reproducible low-FMR benchmark access is confirmed, or a replacement amendment is independently reviewed and frozen before outcomes.
6. The 4-vCPU sharded/resumable smoke path, worker equivalence and restart equivalence are green.
7. Lock/frozen environment and CycloneDX SBOM exist.
8. Applicable POC code-quality/security checks are green or have explicit bounded dispositions.
9. CI, Research Assurance, Study 1 Engineering Assurance and Study 1 Progress Observability are green for the final reviewed commit.
10. The Chronicle records the reviewed freeze and exact next admissible action.
11. A separate explicit human `GO` authorizes Study 1A execution.

A review acceptance is not itself execution authorization.
