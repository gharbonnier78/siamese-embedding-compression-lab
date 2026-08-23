# Changelog

This changelog is append-only. Published studies, negative results and known defects are
never rewritten as if they had not occurred. Corrections add a new entry and point back to
the original run, artifact and claim state.

## [0.2.4-draft] - 2026-08-23

### Clarified

- Clarifies the route-specific meaning of the five preregistered seeds
  `{11, 29, 47, 71, 101}` used by the 128D candidate routes.
- PCA is not a single unseeded deterministic fit: it is refitted for each preregistered
  model/projection seed because scikit-learn PCA uses `svd_solver="randomized"` with
  `random_state=seed`.
- The TRAIN/VALIDATION split remains fixed independently by `split_seed = 20260806`; the
  five candidate seeds do not resample or redefine the data split.
- Random projection uses the candidate seed to generate its Gaussian matrix; PCA uses it
  for randomized SVD; Siamese uses it for initialization and training order. Raw 512D has
  no projection randomness and is represented once.
- Distinguishes model/projection seed semantics from the bootstrap Monte-Carlo random
  stream used to estimate uncertainty from already frozen historical scores.

### Scientific status

- No score, threshold, table, confidence interval, claim, gate, dataset split or scientific
  conclusion changes relative to the independently reviewed v0.2.3 manuscript.
- `C-NI-001 = NOT_DEMONSTRATED` and `C-SUP-001 = NOT_DEMONSTRATED` remain unchanged.
- This is a reproducibility/pedagogy clarification triggered by an independent reader
  finding; it does not reopen Study 0 or authorize Study 1 or representation-geometry work.

## [0.2.2-harness-draft] - 2026-08-08

### Added

- A project-level Scientific Chronicle & Reproducibility Harness complementing CAL and
  MMALS replay with append-only reasoning provenance: doubts, assumptions, reviewer
  findings, computational constraints, rejected alternatives, changes of belief and
  pedagogically important clarifications.
- Machine-readable `protocol/scientific_chronicle.yaml` and
  `gates/scientific_harness.yaml`, validated independently in Research Assurance.
- An execution preflight that blocks named production steps while a chronicle entry is
  explicitly OPEN and blocking; smoke/benchmark work remains possible to resolve the risk.
- A first pre-outcome chronicle entry recording the computational-feasibility concern for
  the nested Study 0 v0.2.2 coverage simulation before any production coverage result is
  observed.

### Current blocking rationale

- `production_coverage_gate` is blocked while `CHRON-20260808-001` is OPEN.
- Resolution requires either a feasibility benchmark of the reviewed implementation or a
  semantics-preserving optimization with equivalence tests for threshold/tie/sentinel
  behavior.
- Runtime convenience alone must not silently reduce the frozen bootstrap count, scenario
  set, stopping rule, or statistical semantics.

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
  `lfw-resnet18-siamese_projection_v0_1-89179914-911192ee-64559cbd`.
- Reported that the contrastive mechanism trained successfully while non-inferiority and
  added value over matched controls were not demonstrated.