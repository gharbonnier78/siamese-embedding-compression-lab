# Study 0 final report

## What “Study 0” means

In this repository, **Study 0** is simply the name of the first controlled experiment in the Siamese Embedding Compression research programme. It is not an external benchmark category. The experiment takes a frozen 512-dimensional ImageNet ResNet-18 representation of LFW face images and asks whether post-extractor compression to 128 dimensions can preserve verification performance.

Four matched routes are compared on the same source embeddings and pair splits:

- **raw 512D**: no dimensionality reduction;
- **random 128D**: seeded Gaussian projection;
- **PCA 128D**: unsupervised PCA fitted on TRAIN endpoints only;
- **Siamese 128D**: a learned shared linear 512→128 projection trained on pairs with contrastive loss.

The experiment is intentionally exploratory. ImageNet ResNet-18 is not a face-recognition backbone, and LFW DevTest has only 500 impostor pairs, so it cannot establish industrial very-low-FMR claims.

## Scientific question

At an empirical TEST FMR of 0.01, define

`Delta_FNMR = FNMR(candidate) - FNMR(raw)`.

The frozen non-inferiority margin is `0.03` absolute FNMR. A 128D route is considered non-inferior only if its 97.5% upper confidence bound is at or below `0.03` for **every** predeclared seed `[11, 29, 47, 71, 101]`.

Equal-FMR TEST thresholds are used only to compare representation discrimination and are explicitly non-deployable. A separate operational analysis selects thresholds on VALIDATION, freezes them, and transfers them once to TEST.

## What happened in the original execution

The original historical execution produced a negative result: none of the 128D routes satisfied the all-seeds non-inferiority rule. Siamese had attractive secondary descriptive AUC/EER values, but those did not rescue the primary low-FMR endpoint.

A later audit found a real statistical defect, recorded as **E-STAT-001**. The research contract described identity-aware uncertainty, but the executed bootstrap resampled genuine and impostor **pairs** rather than identities. Candidate and raw routes were paired correctly, but repeated identities across trials were not represented in the uncertainty unit.

The historical outputs were not rewritten. The original score table, results, paper, and negative decision remain immutable.

## Corrective method

The correction was frozen before reopening the historical result values. It uses a weighted **subject-slot bootstrap** on the exact observed LFW DevTest pair graph:

- draw 963 subject slots with replacement;
- genuine edge weight: `m_i`;
- impostor edge weight: `m_i * m_j`;
- never synthesize an unobserved pair;
- use the same subject draw for candidate and raw;
- run 10,000 bootstrap replicates per seed;
- preserve the frozen threshold, tie, sentinel, seed and degeneracy rules;
- never retrain the models or recompute historical pair scores.

Before applying it to the historical bundle, the interval procedure was tested in known-truth synthetic simulations covering independent-pair and subject-dependent regimes. At the selected 4,000-dataset checkpoint, all 15 scenario×metric checks satisfied the frozen coverage criterion. The weakest exact lower 95% Clopper-Pearson bound was `0.937743`, above the required `0.93`.

## Provenance and replay

The exact historical replay archive was recovered and verified:

- archive bytes: `4,158,610`;
- archive SHA-256: `7429c75a7da827281ca172d7a4184c65fcc27dbfa845eb9ffd27e04d81331897`;
- `test_pair_scores.csv` bytes: `1,821,547`;
- `test_pair_scores.csv` SHA-256: `f52ea23987a9d22647e0f63275a3d8a215b5fb0c588bac41723298537b383439`;
- historical run ID: `lfw_resnet18_siamese_projection_v0_1-89179914-911192ee-64559cbd`.

The corrected reanalysis was materialized in a fresh output directory. All declared output hashes were checked. An independent reviewer then verified the materialization and provenance before any result interpretation. Only after that boundary was passed were result values opened. A second independent review recalculated the interpretation directly from the materialized tables and found no discrepancy requiring a scientific change.

## Corrected result

No 128D route satisfies the frozen non-inferiority rule:

| Route | Seeds passing | 97.5% UCB range for `Delta_FNMR` |
| --- | ---: | ---: |
| Random 128D | 0/5 | 0.112649–0.151768 |
| PCA 128D | 0/5 | 0.125556–0.133606 |
| Siamese 128D | 0/5 | 0.176584–0.189156 |

For Siamese, the equal-FMR point deltas are:

`+0.034, +0.064, -0.006, +0.050, +0.010`.

The corrected subject-bootstrap means are:

`+0.0392, +0.0438, +0.0024, +0.0372, +0.0113`.

The correct conclusion is **failure to demonstrate non-inferiority**. It is **not** proof that Siamese compression is inferior.

## What the statistical correction changed

The correction did not reverse the qualitative negative decision, but it materially widened uncertainty:

| Route | Pair-bootstrap interval width | Subject-bootstrap interval width | Ratio |
| --- | ---: | ---: | ---: |
| Random | 0.1304 | 0.2042 | ~1.57× |
| PCA | 0.1749 | 0.2664 | ~1.52× |
| Siamese | 0.1944 | 0.2991 | ~1.54× |

So the original analysis was directionally consistent with the corrected outcome but statistically too confident.

## Operational threshold transfer

At VALIDATION-frozen thresholds, the corrected bootstrap means are approximately:

| Route | FNMR | FMR |
| --- | ---: | ---: |
| Raw 512D | 0.8939 | 0.00201 |
| PCA 128D | 0.8468 | 0.00201 |
| Random 128D | 0.8940 | 0.00241 |
| Siamese 128D | 0.9311 | 0.00158 |

These rows are **not** an equal-FMR ranking. For Siamese, the transferred threshold describes a stricter trade-off: lower observed FMR together with higher FNMR.

## Final bounded decisions

- **E-STAT-001**: reanalysed and resolved for this corrected Study 0 inference.
- **G2 estimator and statistical validity**: passes for the corrected Study 0 reanalysis.
- **C-NI-001**: remains `NOT_DEMONSTRATED`.
- **C-SUP-001**: remains `NOT_DEMONSTRATED`.

These decisions do not establish industrial biometric validity, very-low-FMR performance, general inferiority of 128D compression, or superiority of PCA/random over Siamese.

## Engineering value actually established

A float32 512D template occupies 2,048 bytes; a 128D template occupies 512 bytes. Payload is therefore reduced fourfold.

The learned linear projection contains `65,664` float32 parameters, or `262,656` bytes. Excluding the common extractor and all system overhead:

- raw route storage: `2048 N` bytes;
- projected route storage: `512 N + 262656` bytes;
- break-even: `N = 171` templates.

No end-to-end latency, memory-bandwidth, energy, index behavior, or 1:N throughput gain was measured in Study 0.

## Main lesson learned

The corrective chain was intentionally rigorous because the defect affected evidence already being used as a foundation for future work. But the research programme does not need that maximum evidence burden for every early idea.

The next studies should use **progressive evidence escalation**:

1. **Exploratory screening** on dedicated SCREEN data, with matched controls, bounded compute and no claim-bearing TEST access, to decide `CONTINUE / STOP / REDIRECT`.
2. **Full qualification** only after a direction shows enough decision-relevant signal to justify the cost.

This is not a reduction in scientific standards. It aligns the evidence burden with the decision being made.

## Consequence for the next study

The next experiment will replace ImageNet ResNet-18 with a face-specific backbone. Its current design uses a non-claim-bearing screening stage before qualification:

- SCREEN is distinct from qualification TEST;
- raw/random/PCA/Siamese remain matched;
- screening seeds `[11,29]` are fixed in advance;
- the full qualification seed set `[11,29,47,71,101]` cannot be reduced after screening;
- promotion and stop criteria must be frozen before screening outcomes are opened;
- a negative screen is preserved and can stop the programme before expensive qualification;
- representation-geometry work remains outside this next step unless later evidence warrants it.

## Where to read next

- arXiv-style paper source: `paper/main.tex` (v0.2.3)
- original historical result: `RESULTS_LFW_V0.1.md`
- append-only statistical erratum: `ERRATA_STUDY_0.md`
- frozen correction: `protocol/studies/study_0_subject_bootstrap_v0.2.2.yaml`
- final corrected interpretation and reviews: `evidence/study_0_subject_bootstrap_v0.2.2/`
- current claim wording: `claims/registry.yaml`
- process lesson and next-study design: `docs/LESSONS_LEARNED_STUDY0_PROGRESSIVE_EVIDENCE.md` and `protocol/studies/study_1_face_backbone.yaml`
