# Siamese Embedding Compression Lab

[![CI](https://github.com/gharbonnier78/siamese-embedding-compression-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/gharbonnier78/siamese-embedding-compression-lab/actions/workflows/ci.yml)
[![Research assurance](https://github.com/gharbonnier78/siamese-embedding-compression-lab/actions/workflows/research-assurance.yml/badge.svg)](https://github.com/gharbonnier78/siamese-embedding-compression-lab/actions/workflows/research-assurance.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A replayable research programme asking whether a learned 512→128 embedding projection can reduce template cost while preserving decision-relevant face-verification performance relative to the uncompressed embedding and matched compression controls.

## Current status — August 2026

The first controlled experiment in this repository, called **Study 0**, is now closed after a corrected subject-level uncertainty reanalysis.

Study 0 used frozen ImageNet ResNet-18 embeddings on the LFW development protocol and compared four routes on the same source embeddings:

- raw 512D;
- Gaussian random projection to 128D;
- TRAIN-only PCA to 128D;
- a learned Siamese linear 512→128 projection trained with contrastive loss.

The primary question was whether each 128D route was non-inferior to raw 512D at empirical `FMR = 0.01`, with an absolute `FNMR` margin of `0.03` and an all-predeclared-seeds decision rule.

**Final bounded result:** non-inferiority is **not demonstrated** for random, PCA, or Siamese compression. Pair supervision also does **not** demonstrate added compression value over PCA/random controls in this experiment. The corrected subject-level bootstrap intervals are materially wider than the original pair-level intervals, so the original analysis understated uncertainty even though the qualitative negative decision remains unchanged.

This is not evidence that metric learning fails in general, that 128D compression is intrinsically inferior, or that the experiment establishes industrial biometric validity.

## Start here

1. **[Study 0 final report](STUDY0_FINAL_REPORT.md)** — 5–10 minute reader-oriented account of the question, correction, result, and next decision.
2. **[v0.2.3 paper source](paper/main.tex)** — self-contained arXiv-style English manuscript closing the initial experiment.
3. **[Original historical result](RESULTS_LFW_V0.1.md)** — retained v0.1 result before the uncertainty correction.
4. **[Study 0 erratum](ERRATA_STUDY_0.md)** — append-only record of E-STAT-001 and its resolution.
5. **[Research programme](RESEARCH_PROGRAM.md)** — current sequence of studies and claim boundaries.
6. **[Claims registry](claims/registry.yaml)** — current machine-readable claim status and permitted wording.
7. **[Scientific Chronicle](protocol/scientific_chronicle.yaml)** — append-only decisions that alter executable research behaviour.

Archived historical papers remain available at:

- [v0.2.1 PDF](output/pdf/siamese_embedding_compression_research_program_v0.2.1.pdf)
- [v0.2 PDF](output/pdf/siamese_embedding_compression_research_program_v0.2.pdf)

The v0.2.3 PDF is rebuilt from `paper/main.tex`; historical PDFs are never overwritten.

## What Study 0 established

The final corrected decisions are:

| Object | Current state | Meaning |
| --- | --- | --- |
| E-STAT-001 | `REANALYZED` | The pair-vs-subject bootstrap defect has been corrected and replayed. |
| G2 estimator/statistical validity | `PASS` for the corrected Study 0 reanalysis | The corrected estimator and interval procedure satisfy the bounded evidence contract. |
| C-NI-001 | `NOT_DEMONSTRATED` | The tested 128D routes do not demonstrate non-inferiority to raw 512D. |
| C-SUP-001 | `NOT_DEMONSTRATED` | Siamese supervision does not demonstrate added value over matched PCA/random controls. |

Corrected 97.5% upper-bound ranges for `Delta_FNMR = FNMR(candidate) - FNMR(raw)` are:

| Route | Seeds passing | UCB range |
| --- | ---: | ---: |
| Random 128D | 0/5 | 0.112649–0.151768 |
| PCA 128D | 0/5 | 0.125556–0.133606 |
| Siamese 128D | 0/5 | 0.176584–0.189156 |

The frozen non-inferiority margin is `0.03`.

## Why the statistical correction mattered

The historical execution resampled genuine and impostor **pairs**. The research contract had described identity-aware uncertainty, but multiple trials can share the same identity. The correction therefore uses a weighted subject-slot bootstrap on the exact observed LFW DevTest pair graph:

- 963 subject slots drawn with replacement;
- genuine-edge weight `m_i`;
- impostor-edge weight `m_i*m_j`;
- no synthetic unobserved all-pairs comparisons;
- paired candidate/raw draws;
- 10,000 replicates per seed;
- frozen threshold, tie, seed and degeneracy rules.

Known-truth simulation validated the interval procedure before the immutable historical score bundle was reanalysed. Independent review then verified the materialization/provenance and separately recalculated the final interpretation from the result tables.

Average corrected interval widths are about 1.5× the original pair-bootstrap widths. That is the main statistical lesson: the old qualitative decision survived, but the old uncertainty was too narrow.

## Engineering result — bounded to what was measured

Float32 template payload falls from:

- 512D: `2,048 bytes/template`;
- 128D: `512 bytes/template`.

The learned projection itself contains `65,664` float32 parameters (`262,656` bytes). Excluding the common extractor and system overhead:

```text
raw(N)       = 2048 N bytes
projected(N) =  512 N + 262656 bytes
```

The two are equal at `N = 171`; projected route-specific storage is smaller above that count under these assumptions.

Study 0 did **not** measure end-to-end latency, memory bandwidth, energy, index behaviour, or 1:N throughput. No fourfold speed-up is claimed.

## Lesson learned — screen before qualification

The Study 0 correction required publication-grade care because a defect was found in evidence already being used as a foundation for later work. That does not mean every early idea should immediately pay the same evidence cost.

The research programme now distinguishes:

- **exploratory screening**: dedicated SCREEN data, matched controls, bounded compute, no qualification TEST access, and no scientific claim;
- **qualification**: only after a direction earns further investment, freeze full estimands, all qualification seeds, untouched TEST, validated uncertainty, provenance, replay, gates and independent review.

See `docs/LESSONS_LEARNED_STUDY0_PROGRESSIVE_EVIDENCE.md`.

## Next study

Study 1 remains **draft and unexecuted**. It will replace ImageNet ResNet-18 with a face-specific backbone and use a `screening -> qualification` structure.

The screening design currently requires:

- a dedicated SCREEN set distinct from qualification TEST;
- raw/random/PCA/Siamese matched controls;
- predeclared screening seeds `[11,29]`;
- a frozen promotion/stop rule before screening outcomes are opened;
- preservation of the full qualification seed set `[11,29,47,71,101]`;
- no use of screening outcomes to drop unfavorable qualification seeds;
- a negative screen to be preserved and allowed to stop or redirect the programme.

Study 1 execution requires a separate research authorization after its design is independently reviewed and frozen. Representation-geometry exploration remains outside the current authorized scope.

## Reproducibility

The repository binds scientific claims to versioned protocols, replay artifacts, source hashes, tests and append-only decision records. Relevant commands include:

```bash
python scripts/validate_research_program.py --root .
python scripts/validate_scientific_harness.py
python -m unittest discover -s tests -v
latexmk -pdf -interaction=nonstopmode -halt-on-error -cd paper/main.tex
```

Research Assurance regenerates evidence-bound figures and rebuilds the paper twice to check bitwise PDF reproducibility in its pinned environment.

## Historical replay identity

Study 0 historical run:

`lfw_resnet18_siamese_projection_v0_1-89179914-911192ee-64559cbd`

Recovered complete replay archive:

- bytes: `4,158,610`;
- SHA-256: `7429c75a7da827281ca172d7a4184c65fcc27dbfa845eb9ffd27e04d81331897`.

Historical score table:

- `test_pair_scores.csv` bytes: `1,821,547`;
- SHA-256: `f52ea23987a9d22647e0f63275a3d8a215b5fb0c588bac41723298537b383439`.

## Scientific boundaries

This repository does not currently establish:

- industrial biometric validity;
- very-low-FMR production performance;
- fairness, PAD or adversarial robustness;
- general superiority or inferiority of Siamese metric learning;
- 1:N performance or system latency benefit;
- regulatory or product acceptance.

Negative results, failed gates and corrected errors are retained as scientific evidence rather than rewritten away.
