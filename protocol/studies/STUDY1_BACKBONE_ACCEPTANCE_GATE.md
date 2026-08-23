# Study 1A — Frozen backbone and acceptance gate

Status: `DRAFT_PREREGISTRATION_REVIEW_REQUIRED`

This document freezes the proposed Study 1A backbone and its numeric acceptance gate before any Study 1A outcome is inspected. It does **not** authorize execution. Study 0 remains closed.

## 1. Frozen face-specific backbone

Study 1A will use a **pretrained** face-recognition backbone. We will **not train the face backbone from scratch** in this study.

Frozen model identity:

- method: **AdaFace**;
- architecture: **R100 / IR-101-family face-recognition residual backbone as implemented by the official AdaFace repository**;
- embedding dimension: **512**;
- training corpus of the selected released checkpoint: **WebFace12M**;
- upstream repository: `mk-minchul/AdaFace`;
- upstream source ref for code/protocol documentation: commit `c60eaa786a42c03444f3df7096dbaf9d57ae010d`;
- official released checkpoint identity: **R100 / WebFace12M** from the AdaFace README pretrained-model table;
- checkpoint source locator: Google Drive file id `1dswnavflETcnAuplZj1IOKKP0eM8ITgT`;
- checkpoint SHA-256: `TO_BE_MATERIALIZED_AND_FROZEN_BEFORE_EXECUTION`;
- repository code licence: MIT;
- checkpoint/training-data usage: **research-only POC until the checkpoint and WebFace12M terms are reviewed and recorded explicitly**. The repository licence must not be silently treated as a licence for third-party training data or all downstream uses.

The checkpoint SHA-256 is deliberately still a release blocker: the logical model choice is frozen now, but the exact downloaded bytes must be hashed and reviewed before any outcome-bearing run. If the downloaded artifact does not match the frozen source identity or if usage rights cannot be established for this research use, Gate A cannot execute and the protocol must be amended before outcomes.

## 2. Frozen preprocessing contract

The AdaFace reference implementation expects aligned faces with:

- five-point landmark alignment through the reference alignment path;
- `112 x 112 x 3` crop;
- **BGR** channel order;
- input normalization equivalent to `mean=0.5`, `std=0.5` per channel;
- 512D output embedding;
- L2-normalized embedding before cosine similarity / normalized-Euclidean equivalence is used downstream.

The exact detector/alignment implementation and version remain to be pinned before execution. Detection/alignment failures must be counted and preserved; they may not be silently dropped to improve benchmark performance.

## 3. Why pretrained weights are the correct choice here

The scientific question is whether a good face-specific 512D representation can be compressed to 128D without unacceptable verification loss. Training a modern R100 face backbone from scratch would add a second research programme: large-scale face-data curation, many-GPU optimization, loss/hyperparameter tuning and training reproducibility.

Therefore Study 1 treats the pretrained backbone as a **frozen measuring substrate**. Only the later 512D→128D projection routes are trained or fitted. This isolates the compression question and makes the experiment feasible on modest CI hardware.

## 4. Published reference values used to freeze Gate A

The official AdaFace repository reports the following results for **R100 / WebFace12M / AdaFace**:

| Benchmark | Published reference |
| --- | ---: |
| LFW accuracy | 99.82% |
| CFP-FP accuracy | 99.26% |
| CPLFW accuracy | 94.57% |
| CALFW accuracy | 96.12% |
| AgeDB-30 accuracy | 98.00% |
| IJB-C TAR @ FAR = 0.01% (`1e-4`) | 97.66% |

For the IJB-C verification endpoint, `TAR = 97.66%` is equivalent to `FNMR = 2.34%` at the same FAR/FMR operating point.

These values are references for reproducing the frozen public model under its declared benchmark protocols. They are not a claim that this model is universally SOTA in 2026.

## 5. Gate A — numeric acceptance criteria

Gate A is **conjunctive**. All mandatory conditions below must pass. The tolerances are fixed before Study 1A execution and may not be widened after observing outcomes.

### A0 — provenance and pipeline integrity

`PASS` only if all are true:

- the checkpoint source identity is the frozen R100/WebFace12M AdaFace release;
- SHA-256 of the exact checkpoint bytes is recorded;
- code and model/data usage terms are reviewed and recorded;
- preprocessing/alignment contract is frozen and replayable;
- official benchmark folds/protocols are used;
- failures/exclusions are reported;
- no qualification outcome was used to tune the pipeline.

Failure of A0 makes the result `INDETERMINATE`, not a scientific failure of the backbone.

### A1 — LFW sanity/reproduction

Published reference: `99.82%` accuracy.

Acceptance threshold: **accuracy >= 99.62%** (maximum allowed reproduction deficit: `0.20` percentage point).

LFW alone can never release Gate A.

### A2 — difficult high-quality verification benchmarks

All four difficult-benchmark thresholds must pass:

| Benchmark | Reference | Frozen minimum |
| --- | ---: | ---: |
| CFP-FP | 99.26% | **98.96%** |
| CPLFW | 94.57% | **94.27%** |
| CALFW | 96.12% | **95.82%** |
| AgeDB-30 | 98.00% | **97.70%** |

Each allows at most a `0.30` percentage-point reproduction deficit from the official R100/WebFace12M reference.

### A3 — primary low-FMR/FAR qualification endpoint

Preferred primary benchmark: **IJB-C**, using the official 1:1 verification protocol.

Published reference: `TAR = 97.66% @ FAR = 1e-4`, hence `FNMR = 2.34% @ FMR/FAR = 1e-4`.

Frozen acceptance criterion:

- **TAR >= 97.16% @ FAR = 1e-4**, equivalently
- **FNMR <= 2.84% @ FMR/FAR = 1e-4**.

This permits a maximum reproduction deficit of `0.50` percentage point in TAR, or equivalently a maximum FNMR increase of `0.50` percentage point relative to the published reference.

The subject/template-aware uncertainty interval must be reported, but Gate A is a **reference-reproduction gate** and therefore the primary pass/fail comparison is the preregistered point metric under the official protocol. The interval is diagnostic and must not be used post hoc to rescue a failed point criterion.

If lawful/reproducible IJB-C access is unavailable, Gate A cannot be declared `PASS`. It remains `INDETERMINATE` until a replacement low-FMR qualification dataset and numeric reference are amended, independently reviewed and frozen **before** replacement outcomes are inspected.

## 6. Gate A decision semantics

- `PASS`: A0, A1, A2 and A3 all pass. The raw 512D substrate is accepted as credible for Study 1B preparation. This does not itself authorize Study 1B execution.
- `FAIL`: provenance/pipeline are valid, but one or more frozen numerical reproduction thresholds fail. Stop and diagnose model/preprocessing/protocol mismatch. Do not run compression to rescue the result.
- `INDETERMINATE`: evidence is unavailable or invalid (for example unresolved licence, missing IJB-C access, checksum not frozen, protocol deviation, or incomplete benchmark execution). Do not proceed to compression qualification.

## 7. What Gate A does not establish

Passing Gate A does not prove production readiness, fairness, PAD/security, regulatory conformity, 1:N identification quality, operational latency, or universal superiority of AdaFace. It only establishes that the exact frozen 512D research backbone has been reproduced closely enough, under the declared verification benchmarks, to serve as the substrate for the later compression experiment.
