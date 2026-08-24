# Independent review record — Study 1A compression-focused amendment

Status: `ACCEPTED`

Date: 2026-08-24

Review basis head: `2110c32b071fa9a836d5dc2d55716d448bc8a10f`

Repository: https://github.com/gharbonnier78/siamese-embedding-compression-lab

Pull request: https://github.com/gharbonnier78/siamese-embedding-compression-lab/pull/46

Pinned harness: https://github.com/gharbonnier78/scientific-research-harness/blob/3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98/HARNESS.md

Amendment: `protocol/studies/STUDY1A_COMPRESSION_FOCUSED_AMENDMENT_2026-08-24.md`

## Verdict

**VERDICT: ACCEPT**, subject only to the pre-execution controls already declared.

## Scientific / methodological assessment

- The amendment faithfully aligns Study 1A with the actual bounded scientific question: whether a learned Siamese 512D -> 128D projection preserves verification performance better than Gaussian random projection and PCA controls, relative to the raw 512D AdaFace reference.
- Reframing Study 1A as substrate sanity qualification rather than broad biometric certification is proportionate to that question.
- Demoting IJB-C / FRTE from mandatory release conditions to external-validity / extension evidence is methodologically acceptable for this bounded compression study.
- A1/A2 thresholds remain unchanged from the prior preregistration, so the amendment does not relax already-frozen accessible reproduction criteria.
- Gate PASS/FAIL/INDETERMINATE semantics remain valid, and low-FMR context may not be used post hoc to rescue a failed A1/A2 sanity gate.
- The amendment was reviewed pre-outcome; no Study 1A scientific benchmark outcome was used to motivate threshold changes.

## Checkpoint / preprocessing assessment

- Artifact identity is treated rigorously: model labels and URLs are not accepted as sufficient evidence of equivalence.
- The 49-block architecture fingerprint supports IR101/R100 and rules against the IR50 topology implicated by the upstream mislabel concern.
- The RGB/BGR permutation probe is specific and falsifiable: only channel permutation `[2,1,0]` produces exact equality for the differing first-convolution tensor with zero numerical error.
- The frozen preprocessing contract is scientifically appropriate and correctly treats preprocessing as part of the executed model.

## Engineering / reproducibility assessment

- CI and Study 1 Engineering Assurance were reported green at the review head `2110c32b071fa9a836d5dc2d55716d448bc8a10f`.
- Deterministic replay, concurrency equivalence and restart/resume are correctly wired as required pre-execution controls, but their scientific use remains conditional on actual evidence from the declared execution path.
- Provenance/manifests and checkpoint-equivalence evidence are structured appropriately.

## Rights / provenance assessment

- AdaFace code MIT status is explicit.
- Checkpoint / training-data-derived rights remain bounded and must not be generalized into unrestricted commercial or redistribution rights.
- The study is a research/POC evaluation; production/commercial use requires separate rights review.

## Blocking findings

No blocking finding prevents activation of the compression-focused Study 1A amendment itself.

The amendment may become active before Study 1A outcomes, subject only to the already-declared pre-execution qualification controls.

## Non-blocking recommendations

- Reconcile the author-maintained artifact against the original Google Drive artifact when lawful access and quota permit; this is not required to proceed with the bounded compression study if the accepted inference-backbone equivalence contract remains satisfied.
- Any future WebFace260M or other low-FMR extension should receive its own pre-outcome preregistration/review.
- Track GitHub Actions Node runtime deprecation warnings as engineering maintenance.

## Final authorization statement

> The compression-focused Study 1A amendment is acceptable for activation before Study 1A outcomes, subject only to the pre-execution controls already declared. This verdict does not authorize Study 1B.

This record captures the independent review supplied to the accountable researcher. It does not itself widen the existing human GO beyond Study 1A.
