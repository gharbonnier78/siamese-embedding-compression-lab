# Study 1A — Frozen image input and preprocessing contract

Status: `PREEXECUTION_ENGINEERING_AND_SCIENTIFIC_INPUT_CONTRACT`

## Purpose

A frozen CNN does not make the experiment frozen by itself. The complete input transformation from raw image bytes to the 512D embedding is part of the scientific object. A silent change in color order, orientation, alignment, normalization, image decoding, exclusion behavior, or test-time transformation can change embeddings and therefore verification outcomes.

This contract must be frozen before outcome-bearing Study 1A execution.

## Canonical pipeline

`raw image -> deterministic decode/orientation -> face detection -> 5-point alignment -> 112x112 crop -> color-space contract -> normalization -> frozen AdaFace IR101/R100 -> L2-normalized 512D embedding`

Every stage must be deterministic, versioned, replayable and represented in the run manifest.

## 1. Exact model/input pairing

The run manifest MUST record:

- exact checkpoint/model artifact SHA-256;
- source repository/revision or locator;
- architecture fingerprint proving IR101/R100 compatibility;
- expected input color-space convention for that exact artifact;
- preprocessing implementation revision;
- output embedding dimensionality and normalization rule.

The historical AdaFace checkpoint contract uses BGR input. The author-maintained CVLFace/Hugging Face safetensors artifact is RGB-oriented, with the RGB<->BGR conversion absorbed exactly by a permutation of the first convolution input channels. Therefore artifact and color-space contract MUST be treated as one inseparable pair.

## 2. Image decoding and orientation

- Decode images with a declared library/version and deterministic options.
- Apply EXIF orientation using a declared rule before face detection/alignment.
- Reject or log corrupt/unsupported images explicitly; never silently skip them.
- Require exactly three effective color channels after decode; alpha/grayscale handling must be declared and deterministic.
- Record dtype and integer/float range before normalization.

## 3. Detection and 5-point alignment

- Use the preregistered face detection/alignment path compatible with the frozen AdaFace reference pipeline.
- Record detector/landmarker implementation and revision.
- Freeze landmark order, similarity transform, interpolation method, crop geometry and target size.
- Target crop is 112x112.
- Multiple-face handling must be declared before outcomes; do not choose a face based on downstream score.
- Detection/alignment failures must remain visible in the dataset/run manifest.

## 4. Color-space contract

- Do not infer RGB/BGR from filename, library convention or model label.
- Bind color order to the exact model artifact.
- The selected implementation MUST have a unit/replay check proving the expected channel order.
- No adaptive or image-dependent channel transformation is permitted.

## 5. Normalization

Freeze the AdaFace input normalization used by the reference implementation:

`normalized = (pixel / 255.0 - 0.5) / 0.5`

Equivalent algebraic implementations are acceptable only when numerically demonstrated under the chosen dtype. Mean/std, scaling order and dtype conversion must not drift between datasets or workers.

## 6. No unregistered image enhancement

The qualification path MUST NOT introduce outcome-driven or convenience preprocessing such as:

- sharpening;
- denoising;
- super-resolution;
- face restoration;
- histogram/color correction;
- synthetic relighting;
- arbitrary crop repair;
- test-time augmentation.

Any such transformation would define a different scientific pipeline and requires a preregistered amendment before protected outcomes.

## 7. Dataset identity, overlap and leakage

For every evaluation dataset:

- maintain an immutable dataset manifest with stable sample IDs and file/content hashes where lawful;
- preserve subject/template identifiers required by the official protocol;
- audit exact duplicates and near-duplicates when feasible;
- audit known/possible overlap with backbone training data when evidence is available;
- keep TRAIN, VALIDATION, SCREEN, untouched TEST and external-validity roles distinct;
- never remove images after inspecting verification scores.

Exclusion criteria must be frozen before outcomes and applied mechanically.

## 8. Dependence-aware statistical identity

A verification pair is not automatically an independent statistical unit. Repeated identities/templates induce dependence. The dataset manifest must preserve subject/template relationships so later uncertainty procedures can resample at the preregistered identity/template level rather than treating pair rows as independent observations.

## 9. Failure accounting

At minimum record counts and stable IDs for:

- invalid/corrupt image;
- unsupported channel/layout;
- orientation failure;
- no face detected;
- multiple faces under a declared ambiguous-face rule;
- landmark/alignment failure;
- crop/shape mismatch;
- model inference failure;
- non-finite embedding;
- zero/invalid norm before L2 normalization.

A failure caused by acquisition/preprocessing must remain distinguishable from a scientific model-performance failure.

## 10. Provenance fields per run

The run evidence should bind at least:

- dataset manifest digest;
- dataset/protocol version;
- image decoder/library version;
- orientation rule;
- detector/alignment revision;
- crop size and interpolation;
- color-space convention;
- normalization formula and dtype;
- checkpoint/model SHA-256;
- preprocessing code commit;
- environment/SBOM identity;
- worker count and shard identity where applicable;
- output embedding manifest digest.

## 11. Additional pre-outcome controls

### 11.1 Preprocessing fingerprint

Before protected benchmark execution, run a bounded non-outcome-bearing fixture set using synthetic or non-evaluation images. Persist hashes for key intermediate representations, for example:

- decoded/oriented image bytes or array digest;
- aligned 112x112 crop digest;
- normalized tensor digest;
- final 512D embedding digest.

The purpose is to detect silent library, color, alignment or dtype drift.

### 11.2 Deterministic embedding replay

For the same fixed fixture image, exact model artifact and environment:

`same input contract -> same serialized 512D embedding digest`

Run this at least twice and across the intended execution paths. A mismatch blocks protected benchmark execution until explained.

### 11.3 Worker-count equivalence

For a bounded fixture shard, 1-worker and configured multi-worker execution must produce identical ordered sample identities and identical embedding digests. Scheduling may change runtime only, not scientific output.

### 11.4 Interruption/resume equivalence

Interrupt a bounded fixture extraction, resume from persisted shards, and verify that the reconstructed ordered embedding manifest and digest are identical to uninterrupted execution.

### 11.5 RGB/BGR sentinel

Keep a dedicated test that fails if the chosen artifact is paired with the wrong color convention. The test should be tied to the exact model SHA and preprocessing revision rather than to a generic model name.

## 12. Fail-closed rules

Protected Study 1A benchmark execution remains blocked if any of the following is unresolved:

- model artifact/input-color pairing is ambiguous;
- preprocessing fingerprint differs from the frozen reference unexpectedly;
- deterministic replay fails;
- worker-count or resume equivalence fails;
- dataset manifest/protocol identity is incomplete;
- exclusion/failure accounting cannot be reconstructed;
- a preprocessing rule is changed after protected outcomes are observed.

## Pedagogical lesson

**Frozen model != frozen experiment. Preprocessing is part of the model as executed.**

A face-recognition backbone consumes a very specific representation of the image. The effective scientific object is therefore not only the CNN weights but the composition:

`preprocessing + exact weights + postprocessing`

Freezing only the weights can leave enough degrees of freedom to change the resulting embeddings and invalidate comparison with reference metrics.

## Boundary

This document defines input/preprocessing and replay controls only. It does not open any benchmark outcome, change Gate A thresholds, authorize Study 1B, or authorize representation-geometry work.
