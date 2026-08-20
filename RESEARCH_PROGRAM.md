# Research programme v0.2.3

## Purpose

This repository studies a bounded engineering-scientific question:

> Can a learned projection reduce biometric embedding cost while preserving decision-relevant verification or identification performance relative to the uncompressed representation and matched compression controls?

The programme is falsifiable by design. It separates:

1. **mechanism validity** — does supervision actually update the projection?
2. **representation value** — does a compressed representation preserve the relevant operating point?
3. **supervision value** — does learned pair supervision outperform ordinary compression controls?
4. **threshold-transfer validity** — do thresholds selected away from TEST transfer credibly?
5. **engineering value** — do storage, memory, latency or throughput improve under measured workloads?
6. **claim admissibility** — is the evidence strong enough for the exact statement being proposed?

A failed gate is a valid result. It reduces the permitted claim level and may stop or redirect later work.

## Current state

The initial experiment, called **Study 0** inside this repository, is closed after a corrected subject-level uncertainty reanalysis.

Study 0 used frozen ImageNet ResNet-18 embeddings on LFW and compared raw 512D, random 128D, PCA 128D and Siamese 128D routes. The corrected analysis found that none of the 128D routes demonstrated non-inferiority to raw 512D under the frozen all-seeds rule at empirical `FMR = 0.01` with `delta_FNMR = 0.03`.

The historical pair-level bootstrap was found to understate uncertainty because the declared identity-aware sampling unit had not been implemented. The correction used a preregistered weighted subject-slot bootstrap, passed a known-truth coverage study, was replayed on the immutable historical scores, and was independently checked at materialization and interpretation stages.

Final bounded status:

| Object | State |
| --- | --- |
| Study 0 corrected reanalysis | closed |
| E-STAT-001 | `REANALYZED` |
| G2 estimator/statistical validity | `PASS` for corrected Study 0 reanalysis |
| C-NI-001 | `NOT_DEMONSTRATED` |
| C-SUP-001 | `NOT_DEMONSTRATED` |
| Study 1 | draft design, not executed |
| Geometry exploration | outside current scope |

The reader-oriented closure is `STUDY0_FINAL_REPORT.md`; the self-contained English paper is `paper/main.tex` version 0.2.3.

## Evidence escalation model

Study 0 exposed two distinct needs:

- when a methodological defect affects evidence already used as a foundation, repair the full chain and replay it rigorously;
- before a new direction has earned that cost, use explicitly exploratory evidence to decide whether full qualification is worth doing.

Future work therefore uses **progressive evidence escalation**.

### Stage A — exploratory screening

Screening answers only whether a direction deserves further investment. It may use a dedicated SCREEN set, fewer predeclared screening seeds and a bounded compute budget. It must keep qualification TEST closed and must be marked non-claim-bearing.

Allowed decisions are `CONTINUE`, `STOP` or `REDIRECT`.

### Stage B — qualification

Only a promoted direction enters claim-bearing qualification. Qualification freezes the complete estimand, margin, multiplicity policy, qualification seeds, data roles, uncertainty method, provenance, replay and independent review burden.

Screening results can never be silently relabelled as qualification evidence.

## Study sequence

| Study | Current status | Purpose | Maximum present conclusion |
| --- | --- | --- | --- |
| Study 0 | completed and corrected | Audit 512→128 compression in the original ImageNet ResNet-18/LFW setting | Limited LFW result |
| Study 1 | draft preregistration | Face-specific backbone, screening then 1:1 qualification | None until executed |
| Study 2 | planned | Dimensions, projection families, supervision value and quantization | Compression ablation |
| Study 3 | planned | External datasets and predeclared operational shifts | Bounded robustness |
| Study 4 | planned | 1:N retrieval, indexing and engineering cost | Bounded engineering value |
| Study 5 | planned | Independent replay and reproduction | Reproduction claim |

Later studies never overwrite earlier evidence.

## Study 1 — current design direction

Study 1 will replace the unsuitable ImageNet source extractor with a face-specific embedding. It is not yet authorized for execution.

The current draft introduces a dedicated non-claim-bearing screening stage before qualification:

- separate TRAIN / VALIDATION / SCREEN / untouched qualification TEST roles;
- raw/random/PCA/Siamese matched routes at 128D;
- screening seeds `[11,29]` fixed before outcomes;
- full qualification seeds `[11,29,47,71,101]` preserved regardless of screening outcomes;
- raw backbone viability checked at the decision-relevant low-FMR endpoint before compression qualification;
- numerical promotion and stop criteria frozen before SCREEN is opened;
- negative screening preserved and allowed to stop or redirect work;
- qualification TEST never used to rescue a failed screen.

Before screening can execute, the design still needs independently reviewed and frozen choices for the backbone/weights/licence, datasets and overlap audit, target population/capture regime, screening promotion rule, qualification FMR and margin, sample size, multiplicity policy and compute budget. A separate research authorization is required for Stage A execution.

## Primary representation estimand

For candidate route `m`, raw reference `b`, and target false-match rate `alpha`:

```text
delta_fnmr(m, alpha) = fnmr_m(alpha) - fnmr_b(alpha)
```

A non-inferiority claim requires the predeclared upper confidence bound for this paired difference to be at or below the predeclared margin. TEST equal-FMR thresholds are non-deployable representation benchmarks. Operational thresholds are selected on VALIDATION and frozen before TEST.

## Study 0 correction — frozen subject-level uncertainty

The corrected Study 0 analysis draws 963 subject slots with replacement on the observed LFW DevTest sparse graph:

- genuine edge weight `m_i`;
- impostor edge weight `m_i*m_j`;
- same draw for candidate and raw;
- no synthesized unobserved pairs;
- 10,000 bootstrap replicates per seed;
- PCG64 with frozen seed binding;
- fail on degeneracy rather than redraw;
- immutable historical score source.

Known-truth synthetic validation checked representation delta-FNMR, operational FNMR and operational FMR separately across five frozen dependence/effect regimes. The corrected historical result was then materialized and independently recalculated.

## Claim boundaries after Study 0

Study 0 establishes the training mechanism and exact payload arithmetic, but it does not establish:

- non-inferiority of any tested 128D route;
- added Siamese supervision value over PCA/random;
- industrial biometric validity;
- very-low-FMR performance;
- general failure of metric learning;
- 1:N preservation or end-to-end latency benefit;
- fairness, PAD, security or regulatory conformity.

## Engineering decomposition

The current post-extractor projection does not shrink or accelerate the frozen extractor. For workload `w`, future system studies should separate at least:

```text
C_total(w) = C_extract + C_project + C_store + C_index + C_search + C_postprocess + C_replicate
```

Study 0 establishes only route-specific template arithmetic. Study 4 is responsible for actual 1:N/index/latency measurements.

## Evidence and sources of truth

| Object | Source |
| --- | --- |
| Current reader-facing status | `README.md` |
| Study 0 closure narrative | `STUDY0_FINAL_REPORT.md` |
| Self-contained paper | `paper/main.tex` |
| Claims and permitted wording | `claims/registry.yaml` |
| Study protocols | `protocol/studies/*.yaml` |
| Append-only execution decisions | `protocol/scientific_chronicle.yaml` |
| Statistical erratum history | `ERRATA_STUDY_0.md` |
| Corrected Study 0 evidence | `evidence/study_0_subject_bootstrap_v0.2.2/` |
| Immutable historical replay | release-level MMALS replay bundle and recorded hashes |

Machine checks establish internal consistency and replayability; they do not substitute for scientific validity or domain expertise.

## Build and validation

```bash
python scripts/validate_research_program.py --root .
python scripts/validate_scientific_harness.py
python scripts/generate_research_figures.py
python -m unittest discover -s tests -v
latexmk -pdf -interaction=nonstopmode -halt-on-error -cd paper/main.tex
```

Historical PDFs and result artifacts remain versioned and are not overwritten by later papers or corrections.
