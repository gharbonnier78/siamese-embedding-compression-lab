# Changelog

This changelog is append-only. Published studies, negative results and known defects are
never rewritten as if they had not occurred. Corrections add a new entry and point back to
the original run, artifact and claim state.

## [0.2.1-draft] - 2026-08-07

### Added

- An immutable experiment ledger and an explicit history/errata policy.
- Full erratum `E-STAT-001` for the Study 0 pair-level bootstrap that had been declared as
  identity-aware.
- A reviewer-informed Study 1 preregistration checklist with statistical and sample-size
  blockers.
- CI guards requiring the Study 0 run, negative decision, erratum and archived v0.2 PDF to
  remain present while later studies are added.

### Corrected without rewriting history

- Study 0 still reports the originally executed pair-level intervals and the original
  `NOT_DEMONSTRATED` decision. Those numbers are not silently replaced.
- G2 is now explicitly failed for the inferential claim until a separately versioned
  identity-dependence sensitivity analysis is implemented and published.
- The random control is documented as a Gaussian projection with variance `1/128`, followed
  by L2 normalization.

## [0.2.0-draft] - 2026-08-07

- Added the arXiv-like research programme, CAL claim registry, deterministic replay-derived
  figures, Study 0 report and planned Studies 1-5.
- Added bounded engineering analysis for projection overhead, watchlist storage and the
  still-unmeasured 1:N latency hypothesis.
- Preserved the Study 0 negative non-inferiority result.

## [0.1.0] - 2026-08-06

- Executed the frozen ImageNet ResNet-18/LFW mechanism audit.
- Stored immutable run ID
  `lfw_resnet18_siamese_projection_v0_1-89179914-911192ee-64559cbd`.
- Reported that the contrastive mechanism trained successfully while non-inferiority and
  added value over matched controls were not demonstrated.
