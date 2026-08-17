# Changelog

This changelog is append-only. Published studies, negative results and known defects are
never rewritten as if they had not occurred. Corrections add a new entry and point back to
the original run, artifact and claim state.

## [Unreleased] - 2026-08-17

### Documentation

- Added a complete pedagogical and methodological note connecting PCA, random projection,
  raw 512D embeddings and the supervised Siamese 512→128 projection.
- Preserved the originating questions and distinguished embedding compression from backbone
  model compression.
- Clarified that Study 0 still reports `G2 = FAIL` and `NOT_DEMONSTRATED`; this note adds no
  experimental result and does not rewrite historical evidence.

## [0.2.2-spec] - 2026-08-07

### Added

- A formal, implementation-independent specification for the Study 0 weighted
  subject-slot bootstrap reanalysis.
- Exact multiplicity rules for genuine and observed impostor edges on the sparse LFW
  DevTest pair graph.
- Frozen estimands, coverage-simulation gate, normative tests, replay outputs and erratum
  closure criteria.
- Machine-readable `PLANNED` placeholders for Studies 2, 3 and 5, closing gaps between
  the declared study sequence and the study registry without starting those studies.

### Status boundary

- No corrected bootstrap has been implemented.
- No Study 0 reanalysis result exists.
- `E-STAT-001` remains open and G2 remains failed.
- Study 1 remains blocked and unexecuted.

## [0.2.1] - 2026-08-07

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
