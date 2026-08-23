# Targeted independent review request — v0.2.4 seed semantics

## Scope

This is a narrow reproducibility/pedagogy review. Study 0 scientific results are already closed. The only intended manuscript change from v0.2.3 is clarification of what the five preregistered seeds mean for each route, especially PCA.

## Finding being addressed

A reader correctly identified that v0.2.3 could be read inconsistently:

- the PCA section said randomized SVD used "a fixed seed";
- the seed section referred to the "stochastic 128D routes";
- Tables 3/4 reported PCA across five seeds.

The implementation shows that PCA is refitted for each seed because `PCAProjection` passes its route seed to scikit-learn as `random_state` while using `svd_solver="randomized"`. The data split is separately frozen by `split_seed = 20260806`.

## Reviewer checks requested

Please verify only the following bounded points:

1. `src/siamese_compression_lab/models.py` indeed gives PCA a route seed through `random_state=seed` with randomized SVD.
2. `configs/lfw_resnet18.yaml` indeed separates `split_seed: 20260806` from `training.seeds: [11, 29, 47, 71, 101]`.
3. The proposed wording accurately states the route-specific role of the five candidate seeds:
   - random: Gaussian projection matrix;
   - PCA: randomized SVD;
   - Siamese: initialization/training order;
   - raw: no projection randomness / one representation.
4. The wording correctly distinguishes model/projection randomness from bootstrap Monte-Carlo randomness.
5. No score, threshold, interval, table, scientific claim or gate is changed by the clarification.

## Expected verdict

Please return one of:

- `VERDICT: ACCEPT`
- `VERDICT: REVISE`

If revising, identify the exact sentence that is inaccurate or still ambiguous.

## Scientific boundary

A review acceptance authorizes only publication of the seed-semantics clarification. It does not reopen Study 0, change `C-NI-001` or `C-SUP-001`, authorize Study 1 execution, or authorize representation-geometry work.