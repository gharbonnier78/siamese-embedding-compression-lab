# Study 0 final report

## What “Study 0” means

In this repository, **Study 0** is simply the name of the first controlled experiment in the Siamese Embedding Compression research programme. It is not an external benchmark category. The experiment takes a frozen 512-dimensional ImageNet ResNet-18 representation of LFW face images and asks whether post-extractor compression to 128 dimensions can preserve verification performance.

The experiment is intentionally exploratory. ImageNet ResNet-18 is not a face-recognition backbone, and LFW DevTest has only 500 impostor pairs, so it cannot establish industrial very-low-FMR claims.

## Why dimensionality reduction is not one single technique

“Feature reduction” can mean several different things. The Study 0 comparison focuses on **feature extraction**: creating a new lower-dimensional representation from the existing 512D embedding. This differs from feature selection, which would simply retain a subset of the original coordinates.

The wider landscape includes:

- **random projection**: a data-independent linear projection; useful as a dimension-only control and motivated by approximate distance-preservation results such as Johnson–Lindenstrauss;
- **PCA**: an unsupervised data-adaptive linear projection that keeps directions of highest variance and minimizes linear reconstruction error for a fixed rank;
- **LDA**: a supervised class-label method that searches for between-class separation relative to within-class variation;
- **autoencoders**: nonlinear encoder/decoder models that learn a bottleneck, usually through reconstruction loss;
- **metric-learning projections**: supervised transformations that optimize a task-relevant geometry from pairs, triplets or related constraints;
- **hashing / binary embeddings**: representations designed for compact codes and Hamming-like comparisons;
- **quantization**: fewer bits per coordinate, which is complementary to dimensionality reduction rather than the same operation;
- **compact or distilled backbones**: change the extractor itself rather than adding a post-extractor projection.

Study 0 deliberately keeps the comparison simpler and more controlled: every compressed route produces a 128D linear representation from the same frozen 512D source embedding.

## The four matched routes

The same source embeddings and the same pair splits are used for all routes:

- **raw 512D**: no dimensionality reduction;
- **random 128D**: a seeded Gaussian matrix with entries distributed as `N(0, 1/128)`, followed by L2 normalization;
- **PCA 128D**: unsupervised PCA fitted on TRAIN endpoints only, using the 128 leading principal directions, followed by L2 normalization;
- **Siamese 128D**: a learned shared affine projection `512→128`, followed by L2 normalization, trained on genuine/impostor pairs with contrastive loss.

These controls answer different questions. Raw asks whether compression is acceptable at all. Random asks whether lowering dimension alone already preserves enough geometry. PCA asks whether ordinary unsupervised, data-adaptive compression is sufficient. Siamese asks whether **pair supervision adds value beyond those baselines**.

## What PCA does here

Let the TRAIN embeddings be centered around mean `mu`. PCA estimates the covariance structure of those TRAIN endpoints and finds orthogonal directions ordered by decreasing variance. The 128D representation keeps the first 128 principal directions.

PCA is a strong control because it adapts to the observed feature distribution without using genuine/impostor labels. But its objective is not biometric verification: preserving variance does not guarantee preserving the extreme impostor tail or the low-FMR operating region.

That distinction is central to the experiment. If Siamese supervision is useful, it should provide something beyond what PCA already achieves at the same output dimension.

## What “Siamese” means in this experiment

A Siamese architecture does **not** mean two different models. It means two training branches that use the **same weights**.

For each training pair, the two 512D source embeddings `z_i` and `z_j` are independently passed through the same trainable projection:

`u = L2_normalize(z W + b)`

with `W` of size `512×128` and `b` of size `128`. The two branches share exactly the same `W` and `b`, giving `65,664` trainable parameters.

The distance is Euclidean distance between the L2-normalized outputs. For unit vectors this is monotonic with cosine similarity because:

`||u_i-u_j||² = 2 - 2 cos(u_i,u_j)`.

The contrastive loss uses the pair label:

- for a **genuine pair**, squared distance is penalized, pulling the pair together;
- for an **impostor pair**, only distances inside margin `m=1` are penalized, pushing close impostors apart.

The important point is that pair labels modify the geometry of a single shared projection. They are not merely used to select a threshold.

The two-branch construction is also mainly a **training mechanism**. After training, a single image or source embedding passes through one branch and yields a 128D template. Verification later compares two such templates; pair labels are not needed at inference. The route is therefore not a closed-set softmax classifier and does not require the deployed system to run two neural branches as a special runtime architecture.

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

- arXiv-style paper source: `paper/study0_v0.2.3.tex` (`paper/main.tex` is the build entrypoint)
- original historical result: `RESULTS_LFW_V0.1.md`
- append-only statistical erratum: `ERRATA_STUDY_0.md`
- frozen correction: `protocol/studies/study_0_subject_bootstrap_v0.2.2.yaml`
- final corrected interpretation and reviews: `evidence/study_0_subject_bootstrap_v0.2.2/`
- current claim wording: `claims/registry.yaml`
- process lesson and next-study design: `docs/LESSONS_LEARNED_STUDY0_PROGRESSIVE_EVIDENCE.md` and `protocol/studies/study_1_face_backbone.yaml`
