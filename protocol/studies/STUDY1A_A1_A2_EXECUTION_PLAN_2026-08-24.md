# Study 1A — A1/A2 outcome-bearing execution plan

Status: **AUTHORIZED_FOR_EXECUTION**

Date: 2026-08-24

## Purpose

Open the outcome-bearing part of Study 1A that was explicitly authorized by the accountable
human researcher and activated by the independently reviewed compression-focused amendment.

The bounded question is not whether AdaFace is production-ready or state of the art. It is:

> Is the exact frozen AdaFace R100 / IR101 512D face representation reproduced credibly enough
> on standard public face-verification validation sets to serve as the substrate for the later
> raw512 / random128 / PCA128 / Siamese128 compression comparison?

Study 1B remains unauthorized by this execution.

## A1 — LFW reproduction sanity

A1 is a basic sanity/reproduction check on **LFW (Labeled Faces in the Wild)** using the
standard 10-fold verification protocol used by the pinned AdaFace evaluation code.

- published AdaFace R100/WebFace12M reference: **99.82% accuracy**;
- preregistered minimum: **99.62% accuracy**;
- decision role: detect an obviously broken checkpoint, preprocessing path, color convention or
  verification implementation before accepting the raw 512D substrate;
- A1 alone cannot release Study 1A.

## A2 — difficult public verification reproduction

A2 requires **all four** already-frozen checks below to pass. They deliberately stress different
forms of intra-person variation while remaining the same standard AdaFace/InsightFace style
verification protocol.

| Benchmark | What it stresses | Published reference | Frozen minimum |
| --- | --- | ---: | ---: |
| CFP-FP | frontal/profile pose variation | 99.26% | **98.96%** |
| CPLFW | cross-pose variation | 94.57% | **94.27%** |
| CALFW | cross-age variation | 96.12% | **95.82%** |
| AgeDB-30 | large age-gap variation | 98.00% | **97.70%** |

The thresholds are unchanged from the preregistration. They may not be widened after outcomes.
A low-FMR result, IJB-C or FRTE result may not rescue a failed A1/A2 criterion.

## Benchmark input form

The standard InsightFace/AdaFace validation `.bin` files contain **already aligned 112x112 face
crops and pair labels**. To reproduce the upstream high-quality validation path, this execution
MUST NOT re-run MTCNN or perform a second alignment on those benchmark crops.

For these benchmark artifacts the effective input path is therefore:

```text
standard aligned validation-bin image bytes
  -> deterministic image decode
  -> BGR representation convention expected by the historical AdaFace checkpoint
  -> normalization to [-1, 1] using mean=0.5, std=0.5
  -> frozen IR101/R100 inference
  -> horizontal-flip inference
  -> AdaFace norm-aware feature fusion
  -> L2-normalized 512D embedding
  -> squared L2 pair distance
  -> upstream-equivalent 10-fold threshold selection/evaluation
```

This is not a weakening of the frozen input contract: alignment has already been materialized in
the official-style validation artifact, so re-aligning would itself change the benchmark.

## Model identity

Execution uses the hash-pinned historical AdaFace R100/WebFace12M checkpoint candidate already
used by the successful preexecution controls:

- source locator: `VishalMishraTss/AdaFace/adaface_ir101_webface12m.ckpt`;
- SHA-256: `0e7a3238d2a50f3fe3860782534928ac7cb2598977cf897f6869fd5ac2493fd0`;
- upstream architecture code: `mk-minchul/AdaFace` commit
  `c60eaa786a42c03444f3df7096dbaf9d57ae010d`;
- architecture: IR101/R100, 512D;
- checkpoint is loaded with `torch.load(..., weights_only=True)` and only `model.*` backbone
  tensors are admitted.

The earlier exact RGB/BGR/channel-permutation evidence and independent review remain part of the
provenance record. The benchmark itself uses the BGR historical representation directly.

## Validation-set transport and provenance

The five standard `.bin` files are acquired from a public Hugging Face transport mirror
`Icar/val_sets`. The mirror is a locator, not scientific identity.

Before any score is interpreted, each downloaded `.bin` is SHA-256 hashed and its byte size,
locator and benchmark name are recorded in the outcome report. No outcome may be compared across
reruns unless the dataset artifact identity is recoverable.

The `.bin` files contain face images and are treated as research data. They are used transiently
inside the runner and are **not** uploaded as GitHub Actions artifacts or committed to Git.

## Verification protocol

The execution reproduces the pinned AdaFace high-quality validation semantics:

1. preserve benchmark pair ordering;
2. infer the original crop and its horizontal flip;
3. fuse the two embeddings using AdaFace norm-aware fusion;
4. pair consecutive embeddings (`0/1`, `2/3`, ...);
5. compute squared Euclidean distance on normalized embeddings;
6. use 10 non-shuffled folds;
7. on each fold, select the best threshold on the other nine folds from
   `np.arange(0, 4, 0.01)`;
8. apply that threshold to the held-out fold;
9. report mean held-out accuracy and per-fold accuracies/thresholds.

A scientific threshold failure is a valid Study 1A **FAIL**, not an infrastructure failure.
Infrastructure/provenance failure instead makes the affected execution **INDETERMINATE**.

## Data-integrity diagnostics

The execution records without filtering:

- number of pair labels and image blobs;
- exact dataset SHA-256 and size;
- exact duplicate image-byte counts;
- decode failures, if any;
- embedding dimension and non-finite values;
- per-fold accuracies and selected thresholds.

No sample is removed because of the observed score. Standard benchmark order and denominator are
preserved.

Identity-level overlap cannot in general be reconstructed from the serialized `.bin` transport
alone because stable subject identifiers are not part of this artifact. That limitation is
reported rather than silently invented. The previously frozen overlap-audit design remains the
rule for later data where identities/templates are available.

## Evidence retention

Each benchmark job uploads only compact reports/manifests, not face images or checkpoint bytes.
A final aggregation artifact contains the A1/A2 reports and the overall bounded Study 1A verdict.
Because these artifacts are load-bearing evidence, the resulting ZIP and its SHA-256 MUST be
promoted to durable repository or controlled-store retention before the temporary Actions
retention expires.

## Decision

- **A1 PASS** iff LFW accuracy >= 0.9962.
- **A2 PASS** iff CFP-FP >= 0.9896, CPLFW >= 0.9427, CALFW >= 0.9582 and AgeDB-30 >= 0.9770.
- **Study 1A PASS** under the active compression-focused amendment iff A0 remains valid and A1 +
  all A2 checks pass.
- A valid numerical failure stops compression progression; Study 1B may not be used to rescue it.

## Authority boundary

This execution is outcome-bearing and is authorized for **Study 1A A1/A2 only**. It does not
authorize Study 1B training/comparison, representation geometry, production claims, fairness/PAD
claims, 1:N claims, low-FMR operational claims or commercial deployment.
