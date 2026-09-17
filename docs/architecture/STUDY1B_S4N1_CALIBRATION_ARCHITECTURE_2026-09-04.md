# Study 1B S4N1 calibration architecture

Date: 2026-09-04  
Status: POC non-outcome architecture; governed by the frozen S4N1 contract.

## 1. Scope

This path calibrates artifact-selection semantics without reading biometric route outcomes. Its only
inputs are the frozen Study 1B role/pair-graph metadata and synthetic known-truth parameters.

It is not an outcome workflow and cannot activate the Study 1B amendment.

## 2. Scientific data flow

```text
pinned LFW metadata + active data-boundary rule
              |
              v
materialize exact VALIDATION and TEST pair graphs
(hash-check both against the active protocol)
              |
              v
two-role known-truth generator
   |                         |
   | VALIDATION              | TEST
   | synthetic distances     | synthetic distances
   v                         v
equal-FMR Delta_FNMR         untouched selected-artifact
point score per seed         identity bootstrap
   |                         ^
   v                         |
frozen selector -------------+
(fixed / best / median)
```

No SCREEN graph, route transform, raw512 embedding, random128 result, PCA128 result, Siamese128
result, or representation-geometry object is an input to this path.

## 3. Selection boundary

Exactly five predeclared seed artifacts are represented: `11, 29, 47, 71, 101`.

For `VALIDATION_BEST` and `VALIDATION_MEDIAN`, the ranking statistic is the unbootstrapped paired
equal-FMR `Delta_FNMR` point estimate at FMR 0.01. Thresholding reuses the reviewed whole-tie-block
and sentinel semantics already present in `subject_bootstrap.py`.

Tie-breaking is exact and deterministic in the frozen seed order. Missing or non-finite validation
scores fail closed.

`FIXED_SEED` returns seed 11 without consuming a validation score.

## 4. Known-truth roles and dependence

VALIDATION and TEST use their distinct frozen graphs, preserving the active identity/capture
boundary. Within each role, the existing Study 1B synthetic generator is reused for:

- one shared raw/reference realization across all candidate seeds;
- subject-level genuine and impostor effects;
- correlated raw/candidate pair noise;
- equal-FMR threshold uncertainty.

The POC imports the already-reviewed shared-reference helpers from `study1b_simulation.py` rather
than reimplementing them. They are private Python helpers today; that is an implementation
coupling to review, not a scientific-semantic change.

Core calibration fixes the same TEST truth for every seed artifact and varies VALIDATION seed
effects prospectively. This isolates selection-on-development-data from the older method-level
population-of-retrainings question.

Transport sensitivity is separate. It draws bivariate latent seed effects for VALIDATION and TEST
at frozen correlations 0, 0.5 and 1.0, allowing artifact quality to transfer imperfectly between
roles without making that transport model the primary estimand.

## 5. Inference path

Only the seed selected from VALIDATION is passed to the TEST bootstrap for each candidate rule.
The TEST interval is evaluated against that selected artifact's known TEST truth.

The identity-aware bootstrap remains unchanged:

- identity-slot resampling;
- genuine edge weight `m_i`;
- impostor edge weight `m_i*m_j`;
- no synthesized graph edges;
- paired raw/candidate draws;
- 10,000 replicates in calibrated execution;
- 97.5% upper bound;
- degeneracy audit at 0.001.

## 6. Randomness and replay

Scientific randomness is keyed by semantic task labels plus `dataset_index` through the existing
Study 1B `seed_token` lineage. Shard number and worker count do not define scientific randomness.

Therefore `[start, stop)` ranges are execution partitioning only. Re-running the same
`dataset_index` with the same contract and graphs must reproduce the same synthetic dataset and
selection.

## 7. Calibration order

1. Unit/replay/static checks on the exact implementation head.
2. Core known-truth coverage checkpoint at 1,000 datasets per declared truth scenario.
3. Escalate to 2,000/4,000 only according to the frozen coverage stopping rule if required.
4. Only after core coverage is accepted, complete the 4,000-dataset power calibration for TEST
   truths 0.00 and 0.01.
5. Then run the secondary cross-role transport sensitivity.
6. Compare candidate semantics using the predeclared table; do not activate an amendment.

The preferred rule is prospectively `VALIDATION_BEST` if it satisfies all gates. Synthetic power
must not be used to opportunistically select a different rule.

## 8. Failure boundaries

The path fails closed for:

- active graph hash mismatch;
- mixed truth-scenario provenance;
- duplicate dataset indices across shards;
- non-finite selection scores;
- inability to return exactly one selected artifact;
- excessive bootstrap degeneracy;
- incomplete checkpoint shards.

Infrastructure failure is not a scientific negative. Scientific gate failure is archived
append-only and does not permit threshold relaxation.

## 9. Downstream unresolved item

The current Stage A SCREEN rule belongs to the original 5-seed/method-level design. If an S4N1
artifact selector later becomes an activated amendment, SCREEN must be prospectively reconciled
to artifact-level semantics before any real outcome is opened. This POC does not perform that
reconciliation and SCREEN remains sealed.
