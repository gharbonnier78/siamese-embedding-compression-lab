# Independent review request — Study 1A compression-focused amendment

Status: `REVIEW_REQUEST`

## Review objective

Review the proposed pre-outcome amendment that narrows Study 1A from broad biometric qualification to a proportional sanity qualification of the AdaFace 512D substrate used for the later compression comparison.

The reviewer must judge the amendment **before any Study 1A benchmark outcome is opened**.

## Canonical navigation

- Repository: https://github.com/gharbonnier78/siamese-embedding-compression-lab
- Pull request: https://github.com/gharbonnier78/siamese-embedding-compression-lab/pull/46
- Amendment on branch: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1a-go-preexecution-20260824/protocol/studies/STUDY1A_COMPRESSION_FOCUSED_AMENDMENT_2026-08-24.md
- Existing active Gate A: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1a-go-preexecution-20260824/protocol/studies/STUDY1_BACKBONE_ACCEPTANCE_GATE.md
- Frozen input contract: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1a-go-preexecution-20260824/protocol/studies/STUDY1A_FROZEN_INPUT_IMAGE_CONTRACT.md
- Harness adoption: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/agent/study1a-go-preexecution-20260824/harness-adoption.yaml
- Pinned harness: https://github.com/gharbonnier78/scientific-research-harness/blob/3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98/HARNESS.md

Review basis branch head at request creation: `a7c7ce18e4b7b4af426b9a7ced7133360214e85f`.

## Required review questions

1. Does the revised Study 1A role faithfully match the scientific question: compare raw512/random128/PCA128/Siamese128 compression routes on a credible face-specific substrate rather than certify a biometric product?
2. Is demoting IJB-C/FRTE from mandatory Gate A release criteria to external-validity/extension evidence methodologically defensible for that bounded question?
3. Are A1/A2 thresholds unchanged and still sufficient as a pre-compression sanity check?
4. Are the mandatory pre-outcome controls adequate to catch a broken pipeline before scientific outcomes are interpreted: artifact identity, input/preprocessing contract, preprocessing fingerprint, deterministic embedding replay, RGB/BGR sentinel, concurrency equivalence, restart/resume equivalence, dataset/protocol manifest, failure accounting and overlap-audit design?
5. Does the rights/provenance treatment remain explicit without overclaiming unrestricted commercial rights?
6. Does the amendment avoid any post-outcome tuning or rescue path?

## Expected verdict

Return one of:

- `ACCEPT` — amendment may become active before Study 1A outcomes;
- `REQUEST_CHANGES` — list concrete changes required before activation;
- `REJECT` — explain why the original broader Gate A is scientifically necessary for the bounded compression question.

A green CI run is not a substitute for this scientific/methodological review.
