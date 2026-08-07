# Research programme v0.2.2-spec

Version 0.2.1 records the methodological erratum. Version 0.2.2-spec adds only the draft,
implementation-independent correction contract and does not start Study 1. Executed
studies, negative results and errors are append-only records governed by
`docs/EXPERIMENT_HISTORY_AND_ERRATA.md` and `protocol/experiment_ledger.yaml`. Study 0
remains reproducible from its frozen configuration while `E-STAT-001` records the G2
bootstrap-unit defect and blocks Study 1 execution.

## Purpose

This repository is a falsifiable research and engineering programme, not a demonstration
that Siamese metric learning is inherently useful. It asks whether a learned projection
can reduce biometric template cost while preserving decision-relevant performance, and
whether any measured gain survives stronger baselines, independent datasets, operating
points, system constraints and distribution shift.

The programme separates five objects that are often conflated:

1. **mechanism validity** - does pair supervision actually update a shared projection?
2. **representation value** - is the learned representation better than matched controls?
3. **decision validity** - do validation-calibrated thresholds transfer to untouched data?
4. **engineering value** - does compression improve storage, memory, latency or throughput?
5. **claim admissibility** - is the evidence sufficient for the exact statement proposed?

## Single source of truth

The paper, CI and replay bundles are clients of machine-readable specifications:

| Object | Source of truth |
|---|---|
| Programme scope | `protocol/research_program.yaml` |
| Study protocols and status | `protocol/studies/*.yaml` |
| Claims and permitted wording | `claims/registry.yaml` |
| Dataset evidence | `datasets/*.yaml` |
| Scientific qualification | `gates/gate_spec.yaml` |
| CAL decision gate | `gates/cal_spec.yaml` |
| Prior and belief revision | `beliefs/prior_posterior.yaml` |
| Run evidence | immutable MMALS replay bundle |
| Paper evidence views | `evidence/study_0_lfw/` + generated-figure manifest |

`scripts/validate_research_program.py` checks cross-file consistency. It does not establish
biometric validity; it establishes that the evidence contract is internally coherent.

## Study sequence

| Study | Status | Purpose | Maximum permitted conclusion |
|---|---|---|---|
| Study 0 | completed | Audit the educational ImageNet ResNet-18/LFW setting | Limited LFW result |
| Study 0 v0.2.2 reanalysis | draft preregistration | Correct uncertainty on the unchanged sparse LFW pair graph | None before implementation, coverage validation and review |
| Study 1 | draft preregistration | Face-specific backbone, 1:1 non-inferiority | Exploratory external result |
| Study 2 | planned | Dimensions, projection families and quantization | Compression ablation |
| Study 3 | planned | External datasets and operational shifts | Bounded robustness claim |
| Study 4 | planned | 1:N retrieval and edge/system cost | Bounded engineering claim |
| Study 5 | planned | Independent replay and qualification | Reproduction claim |

Study 4 is preregistered in `protocol/studies/study_4_identification_engineering.yaml`.
It separates the unchanged extractor, added projection, gallery storage and search stages;
the current Study 0 supplies arithmetic bounds but no measured latency or 1:N benefit.

No later study may overwrite Study 0. A failed gate lowers the permitted claim level; it
does not authorize changing the endpoint, selecting a seed on TEST or silently replacing
the hypothesis.

The normative draft for the bounded Study 0 correction is
`protocol/studies/study_0_subject_bootstrap_spec.md`. It resamples subject slots, preserves
their multiplicities on the 1,000 observed LFW DevTest edges, and never constructs missing
all-pairs comparisons. It contains no corrected result; `E-STAT-001` and G2 remain open.

## Primary estimand

For candidate route `m`, raw reference `b`, and target false match rate `alpha`:

```text
delta_fnmr(m, alpha) = fnmr_m(alpha) - fnmr_b(alpha)
```

The primary non-inferiority claim requires the upper confidence bound of this paired
difference to be at or below a predeclared margin. TEST equal-FMR thresholds are allowed
only for representation comparison and remain non-deployable. Operational thresholds are
selected on VALIDATION and frozen before TEST.

## Evidence discipline

- TRAIN fits parameters.
- VALIDATION selects hyperparameters, early stopping and deployable-style thresholds.
- TEST is opened once after freezing.
- Qualification data are not used for method development.
- Smoke data validate plumbing only.
- Every stochastic route reports every declared seed.
- Identity-level dependencies must be respected by the uncertainty estimator.
- Dataset suitability is specific to a target population, capture regime and operating
  point; public availability is not evidence of representativity.

## CAL boundary

MMALS-CAL is an internal calibration/action gate in the evidence chain. Its outcomes are
`ADMISSIBLE`, `INADMISSIBLE` and `INDETERMINATE`. `INDETERMINATE` means that evidence is
insufficient and can never be silently treated as permission. CAL metrics belong to the
`decision_side_intervention` plane and must not be relabelled as matcher FMR/FNMR.

CAL compliance in this repository means conformance with `gates/cal_spec.yaml`. It is not
a regulatory certification, a biometric product approval or a complete safety proof.

## Build and validate

```bash
python scripts/validate_research_program.py --root .
python -m pip install -r requirements-render.txt
python scripts/generate_research_figures.py
python -m unittest discover -s tests -v
latexmk -pdf -interaction=nonstopmode -halt-on-error -cd paper/main.tex
```

The figure step deterministically regenerates the paper's Study 0 protocol, benchmark,
non-inferiority, threshold-transfer and payload-scaling views. CI rejects a commit when
those views differ from the evidence-bound snapshots in `paper/figures-generated/`. Exact
renderer dependencies are locked in `requirements-render.txt`; an intentional renderer
upgrade is treated as a reviewed evidence-presentation migration.
