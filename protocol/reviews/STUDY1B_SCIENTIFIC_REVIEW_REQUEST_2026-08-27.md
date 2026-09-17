# Study 1B independent review A — scientific / harness

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
- Study 1A amendment: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/main/protocol/studies/STUDY1A_COMPRESSION_FOCUSED_AMENDMENT_2026-08-24.md

The exact immutable PR head for final review must be supplied in a PR navigation comment after all review-basis files and non-outcome evidence are materialized. Do not review a later head under an earlier verdict.

## Required review

Independently ACCEPT or REJECT, with concrete findings, each of the following:

1. the falsifiable Study 1B question and bounded permitted claims;
2. preservation of Study 0 and Study 1A historical decisions;
3. use of the exact Study 1A-qualified AdaFace raw512 substrate;
4. LFW View 1 data-role design, identity disjointness and leakage boundary;
5. pair-graph construction and its sampling-unit implications;
6. primary estimand `FNMR_candidate(alpha)-FNMR_raw(alpha)`;
7. justification for `alpha=0.01` and NI margin `delta=0.03`;
8. one-sided 97.5% UCB and all-five-seeds intersection rule;
9. multiplicity treatment for the three method-specific candidate-vs-raw claims;
10. Holm-adjusted Siamese-vs-PCA/random confirmatory comparisons;
11. identity-aware subject-slot bootstrap, paired draws and degeneracy rule;
12. known-truth coverage revalidation criterion;
13. Stage A SCREEN `CONTINUE/STOP/REDIRECT` rule and TEST sealing;
14. a-priori power contract and primary sampling unit;
15. separation of equal-FMR representation benchmarking from validation-threshold transfer;
16. prohibited inferences, including production and geometry;
17. evidence / Chronicle / pedagogy separation under the pinned harness;
18. human-understanding obligations and exact next admissible action.

## Mandatory blocker check

Before returning `ACCEPT`, verify recoverable evidence exists on the exact head for:

- LFW source/capture/role/pair-graph manifests and hashes;
- overlap/near-duplicate audit;
- known-truth interval coverage simulation passing the frozen criterion;
- a-priori power simulation passing >=0.90 for both declared effect scenarios;
- the Study 1B implementation and POC assurance basis needed to make the scientific contract executable;
- CI and Research Assurance green.

## Verdict format

Return exactly one top-level verdict:

- `VERDICT_A: ACCEPT`
- `VERDICT_A: REJECT`
- `VERDICT_A: NOT_READY_FOR_REVIEW`

Then provide `BLOCKING`, `NON_BLOCKING` and `COSMETIC` findings. An understanding check or green CI must not substitute for scientific evidence.