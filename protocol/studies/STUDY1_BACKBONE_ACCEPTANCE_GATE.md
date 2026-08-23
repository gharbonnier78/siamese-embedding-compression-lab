# Study 1A — Frozen backbone and acceptance gate

Status: `DRAFT_PREREGISTRATION_REVIEW_REQUIRED`

This document freezes the proposed Study 1A backbone and its numeric acceptance gate before any Study 1A outcome is inspected. It does **not** authorize execution. Study 0 remains closed.

## 1. Frozen face-specific backbone

Study 1A uses a **pretrained** face-recognition backbone; the face backbone is not trained from scratch in this study.

Frozen model identity:

- method: **AdaFace**;
- architecture: **R100 / AdaFace `ir_101`**, as implemented by the official repository;
- embedding dimension: **512**;
- released training corpus: **WebFace12M**;
- upstream repository: `mk-minchul/AdaFace`;
- upstream code/protocol ref: commit `c60eaa786a42c03444f3df7096dbaf9d57ae010d`;
- official checkpoint: **R100 / WebFace12M**;
- checkpoint source: Google Drive file id `1dswnavflETcnAuplZj1IOKKP0eM8ITgT`;
- checkpoint SHA-256: `TO_BE_MATERIALIZED_AND_FROZEN_BEFORE_EXECUTION`;
- repository code licence: MIT;
- checkpoint/training-data usage: research POC only until checkpoint and dataset terms are explicitly reviewed.

The model choice is frozen. The exact checkpoint bytes remain a technical release blocker: the first authorized acquisition step must hash the downloaded artifact and record that SHA-256 before outcome-bearing execution. A different checkpoint requires a protocol amendment before any outcomes are inspected.

## 2. Frozen preprocessing contract

Preprocessing is pinned to the reference AdaFace implementation at the same upstream commit:

- face alignment entry point: `face_alignment/align.py` at `c60eaa786a42c03444f3df7096dbaf9d57ae010d`;
- detector/alignment implementation: the bundled AdaFace MTCNN path under `face_alignment/mtcnn_pytorch/` at the same immutable commit;
- crop size: `112 x 112 x 3`;
- five-point landmark alignment as implemented by that pinned code;
- reference landmark transform: `face_alignment/mtcnn_pytorch/src/align_trans.py` at the same commit;
- model input channel order: **BGR**;
- normalization: `(pixel / 255 - 0.5) / 0.5`, equivalent to mean `0.5`, std `0.5`;
- model architecture loader: AdaFace `net.build_model('ir_101')`;
- inference mode: frozen weights, `eval()` only;
- downstream comparison: L2-normalized 512D embeddings before cosine/normalized-Euclidean scoring.

Detection/alignment failures are part of the evidence pack and may not be silently discarded. Any local adapter must prove equivalence to the pinned preprocessing on a bounded fixture before qualification data are opened.

## 3. Why pretrained weights are the correct choice here

The scientific question is whether a credible face-specific 512D representation can be compressed to 128D without unacceptable verification loss. Training R100 from scratch would introduce a separate large-scale face-training programme, new hyperparameters, data curation and GPU-dependent training uncertainty. Study 1 therefore treats the pretrained 512D backbone as a frozen measuring substrate. Only later 512D→128D projection routes are fitted or trained.

## 4. Published reference values used to freeze Gate A

The official AdaFace repository reports for **R100 / WebFace12M / AdaFace**:

| Benchmark | Published reference |
| --- | ---: |
| LFW accuracy | 99.82% |
| CFP-FP accuracy | 99.26% |
| CPLFW accuracy | 94.57% |
| CALFW accuracy | 96.12% |
| AgeDB-30 accuracy | 98.00% |
| IJB-C TAR @ FAR = 0.01% (`1e-4`) | 97.66% |

At the IJB-C operating point, `TAR = 97.66%` corresponds to `FNMR = 2.34%`.

These are reproduction references for the frozen public model/protocol, not a universal 2026 SOTA claim.

## 5. Gate A — numeric acceptance criteria

Gate A is **conjunctive**. Thresholds are frozen before Study 1A execution and may not be widened after outcomes.

### A0 — provenance and pipeline integrity

`PASS` only if all are true:

- exact R100/WebFace12M checkpoint source identity is used;
- exact checkpoint SHA-256 is recorded before outcome access;
- code/model/data usage terms are reviewed and recorded;
- pinned AdaFace preprocessing is replayable or a local adapter has demonstrated bounded equivalence;
- official benchmark folds/protocols are used;
- failures/exclusions are counted and reported;
- no qualification outcome was used to tune the pipeline.

Failure of A0 makes Gate A `INDETERMINATE`, not a scientific failure of the backbone.

### A1 — LFW sanity/reproduction

Reference `99.82%`; frozen minimum **99.62%**.

LFW alone can never release Gate A.

### A2 — difficult high-quality verification benchmarks

| Benchmark | Reference | Frozen minimum |
| --- | ---: | ---: |
| CFP-FP | 99.26% | **98.96%** |
| CPLFW | 94.57% | **94.27%** |
| CALFW | 96.12% | **95.82%** |
| AgeDB-30 | 98.00% | **97.70%** |

Each permits at most a `0.30` percentage-point reproduction deficit.

### A3 — primary low-FMR/FAR qualification endpoint

Primary benchmark: **IJB-C**, official 1:1 verification protocol.

Reference: `TAR = 97.66% @ FAR = 1e-4`, equivalent to `FNMR = 2.34% @ FMR/FAR = 1e-4`.

Frozen criterion:

- **TAR >= 97.16% @ FAR = 1e-4**, equivalently
- **FNMR <= 2.84% @ FMR/FAR = 1e-4**.

The maximum accepted reproduction deficit is `0.50` percentage point TAR, equivalently `+0.50` point FNMR. Subject/template-aware uncertainty must be reported diagnostically and may not be used post hoc to rescue a failed point criterion.

If lawful/reproducible IJB-C access is unavailable, Gate A is `INDETERMINATE`. Any replacement must be amended, independently reviewed and frozen before replacement outcomes are inspected.

## 6. Gate A decision semantics

- `PASS`: A0+A1+A2+A3 all pass. Raw 512D is accepted only as a credible substrate for later compression preparation.
- `FAIL`: A0 is valid but one or more frozen numerical thresholds fail. Stop and diagnose; do not run compression to rescue the result.
- `INDETERMINATE`: provenance, rights, checksum, access, protocol or execution evidence is incomplete/invalid. Do not proceed.

## 7. What Gate A does not establish

Passing Gate A does not establish production readiness, fairness, PAD/security, regulatory conformity, 1:N identification quality, operational latency or universal superiority. It establishes only that the exact frozen 512D research backbone has been reproduced closely enough to serve as the Study 1B substrate.
