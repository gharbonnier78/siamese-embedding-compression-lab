# Study 1B independent review B — technical / reproducibility / engineering assurance

Status: `PREPARED_NOT_YET_READY_FOR_FINAL_VERDICT`

Do not substitute repository search, prior chat context or author prose for the direct artifacts below. If a required object is inaccessible or a non-outcome blocker remains open, return `NOT_READY_FOR_REVIEW` rather than an ACCEPT verdict.

## Direct navigation

- Repository: https://github.com/gharbonnier78/siamese-embedding-compression-lab
- Pull request: https://github.com/gharbonnier78/siamese-embedding-compression-lab/pull/50
- Head branch: https://github.com/gharbonnier78/siamese-embedding-compression-lab/tree/agent/study1b-preregistration-20260827
- Base commit: https://github.com/gharbonnier78/siamese-embedding-compression-lab/commit/5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7
- Pinned harness: https://github.com/gharbonnier78/scientific-research-harness/blob/3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98/HARNESS.md
- Adoption manifest: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/harness-adoption.yaml
- Human-readable Study 1B contract: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/protocol/studies/STUDY1B_MATCHED_COMPRESSION_PREREGISTRATION_2026-08-27.md
- Machine-readable Study 1B contract: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1b-preregistration-20260827/protocol/studies/study_1b_matched_compression.yaml
- Study 1A final decision: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/main/protocol/decisions/STUDY1A_FINAL_DECISION_2026-08-27.yaml
- Current projection implementation: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/main/src/siamese_compression_lab/models.py

The exact immutable PR head for final review must be supplied in a PR navigation comment after all review-basis files and non-outcome evidence are materialized. Do not review a later head under an earlier verdict.

## Required review

Independently ACCEPT or REJECT, with concrete findings, each of the following:

1. exact AdaFace code/checkpoint/preprocessing/raw512 inheritance from Study 1A;
2. LFW source identity, source hashes and deterministic role assignment;
3. capture manifest and overlap/near-duplicate audit implementation;
4. pair-graph generation, canonicalization, duplicate rejection and stable graph hashes;
5. TEST seal and enforcement of TRAIN/VALIDATION/SCREEN/TEST boundaries;
6. random128 matrix distribution `N(0,1/128)`, no orthonormalization, L2 normalization and serialization;
7. PCA128 unique-TRAIN-capture fit, centering, randomized solver, no whitening, seed behavior, L2 normalization and serialization;
8. Siamese affine 512->128 + L2, Euclidean distance, contrastive loss, Adam semantics, LR/WD/batch/epochs/patience/checkpoint selection and no outcome-driven tuning;
9. task-bound `SeedSequence` lineage and separation of pair-graph, model/projection, bootstrap and simulation streams;
10. identity-aware bootstrap implementation, same-draw paired differences, threshold/tie behavior and degeneracy handling;
11. coverage simulation and power simulation implementation/replay;
12. validation-threshold freeze and one-time TEST transfer;
13. route/source/graph/config hashes carried in every shard/output;
14. transform serialization and deterministic replay;
15. worker-count equivalence and scientific identity independence from worker number;
16. interruption/restart equivalence where sharding/resume is used;
17. mixed-provenance aggregation refusal;
18. parent-owned progress and append-only `progress.jsonl`;
19. architecture/decomposition documentation and focused tests;
20. dependency/SBOM, secret scan, static checks/security review and residual-risk dispositions;
21. manual/fail-closed outcome workflow authorization;
22. CI and Research Assurance on the exact final head.

## Mandatory blocker check

Before returning `ACCEPT`, verify that the exact head contains recoverable non-outcome evidence for the frozen LFW manifests/graphs, coverage and power preflights, implementation tests, environment/SBOM and applicable POC assurance checks. A missing check is not a passing check.

## Verdict format

Return exactly one top-level verdict:

- `VERDICT_B: ACCEPT`
- `VERDICT_B: REJECT`
- `VERDICT_B: NOT_READY_FOR_REVIEW`

Then provide `BLOCKING`, `NON_BLOCKING` and `COSMETIC` findings. Green runtime telemetry is not scientific evidence.