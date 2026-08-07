# Study 0 reanalysis v0.2.2 — protocol-preserving weighted subject bootstrap

Status: **SPECIFICATION DRAFT — NOT IMPLEMENTED — NO REANALYSIS RESULTS**

This document is normative for the planned correction of `E-STAT-001`. It freezes the
estimand, resampling unit, multiplicity rules, validation tests, artifacts and decision gates
before implementation. It does not replace Study 0, alter its historical outputs, or start
Study 1.

## 1. Purpose

Study 0 compared four routes applied to the same frozen 512-dimensional ImageNet
ResNet-18 representation:

- uncompressed, L2-normalized `raw512`;
- seeded Gaussian `random128`;
- TRAIN-only `pca128`;
- contrastively trained linear `siamese128`.

The original analysis correctly paired candidate and reference routes but resampled
genuine and impostor **pair indices** independently. Because multiple trials may share an
identity, those trials are dependent. The pair-level bootstrap was therefore incorrectly
described as identity-aware. `E-STAT-001` records this defect and keeps G2 failed.

The correction shall estimate uncertainty by resampling subject slots and applying their
multiplicities to the **observed LFW DevTest pair graph**. It shall compare the corrected
analysis with the retained historical pair-level analysis without overwriting any original
artifact.

## 2. Scientific and engineering boundaries

### 2.1 In scope

1. Restore the two endpoint identities for every one of the 1,000 LFW DevTest pairs.
2. Verify source hashes, ordering, labels, counts and pair identifiers.
3. Implement the weighted subject-slot bootstrap specified below.
4. Recompute paired uncertainty for the frozen Study 0 distances.
5. Compare pair-level and subject-level sensitivity on the same scores.
6. Validate interval coverage on controlled simulations with subject dependence.
7. Publish a new immutable reanalysis bundle and an append-only erratum resolution record.

### 2.2 Explicitly out of scope

- retraining ResNet-18 or any 512-to-128 projection;
- changing seeds, distances, embeddings, routes or the Study 0 pair protocol;
- generating missing all-pairs comparisons between the 963 TEST identities;
- claiming performance for a face-specific or industrial biometric extractor;
- estimating low-FMR performance unsupported by 500 observed impostor pairs;
- executing Study 1 or calculating its final sample size;
- closing `E-STAT-001` solely because an interval became wider or narrower.

An optional complete all-pairs analysis would target a different score distribution and
shall require a separately preregistered study. It must not be presented as the correction
of Study 0.

## 3. Methodological foundation

The design is grounded in subject/subsets bootstrap methods for biometric performance
evaluation, especially:

1. R. M. Bolle, N. K. Ratha and S. Pankanti, “Error Analysis of Pattern Recognition
   Systems — The Subsets Bootstrap,” *Computer Vision and Image Understanding*, 93(1),
   1–33, 2004, DOI `10.1016/j.cviu.2003.08.002`.
2. N. Poh and S. Bengio, “Estimating the Confidence Interval of Expected Performance
   Curve in Biometric Authentication Using Joint Bootstrap,” *ICASSP*, II-137–II-140,
   2007, DOI `10.1109/ICASSP.2007.366191`.
3. ISO/IEC 19795-1:2021 for the general biometric performance-testing, reporting and
   uncertainty boundary. This protocol does not claim that ISO mandates the exact weighted
   construction below.

The method is named **protocol-preserving weighted subject-slot bootstrap adapted to the
sparse symmetric LFW pair graph**. It is grounded in published subject-resampling
principles but is not represented as a verbatim reproduction of either cited algorithm.

## 4. Frozen input evidence

The only admissible empirical inputs are the immutable Study 0 run and its original LFW
DevTest protocol:

- run ID:
  `lfw_resnet18_siamese_projection_v0_1-89179914-911192ee-64559cbd`;
- 1,000 TEST pairs: 500 genuine and 500 impostor;
- 963 distinct TEST identities;
- frozen per-pair distances for every reported route and seed;
- original configuration and source-file digests recorded in the run manifest.

The historical `test_pair_scores.csv` is read-only and lacks identity endpoint columns. A
new versioned mapping shall be reconstructed from the original LFW DevTest matched and
mismatched pair files.

### 4.1 Required identity-mapping artifact

The reanalysis shall create `test_pair_subject_map_v0.2.2.csv` with at least:

```text
pair_id,same,subject_slot_id_1,subject_slot_id_2,source_class,source_row
```

Identity labels shall be deterministically pseudonymized for the public replay. The mapping
algorithm, source digests and ordering rule shall be recorded. The following invariants are
blocking:

- exactly 1,000 unique `pair_id` values;
- exactly 500 `same=1` and 500 `same=0` rows;
- exactly 963 unique endpoint subjects;
- for every genuine row, both endpoint subjects are equal;
- for every impostor row, endpoint subjects are different;
- a one-to-one join with every `(method, seed, pair_id)` score row;
- no score, label, pair identifier or row order is changed in the historical file.

## 5. Frozen estimands

### 5.1 Primary representation estimand

For candidate route `c`, reference route `r=raw512` and target `alpha=0.01`:

```text
Delta_FNMR(c,r,alpha) = FNMR(c,alpha) - FNMR(r,alpha)
```

Each route receives its own threshold located at the same weighted TEST FMR inside each
bootstrap replicate. This is a representation/discrimination comparison only. These
thresholds are non-deployable.

The original exploratory non-inferiority margin remains `delta=0.03`. Changing it after
seeing the reanalysis is forbidden.

### 5.2 Operational sensitivity estimand

The validation-selected threshold for each route remains frozen. Subject bootstrap weights
are applied to TEST scores to estimate uncertainty for FNMR and FMR after threshold
transfer. No TEST label may recalibrate these operational thresholds.

The representation and operational estimands shall never be combined into one pass/fail
statement.

## 6. Subject-slot sampling and pair weights

Let `S={1,...,N}` be the set of TEST subjects, with `N=963`. For replicate `b`, draw `N`
subject slots independently and uniformly with replacement. Let `m_i^(b)` be the number of
times subject `i` occurs. Equivalently:

```text
(m_1,...,m_N) ~ Multinomial(N; 1/N,...,1/N)
```

For every **observed** pair edge `e`:

- genuine edge `(i,i)`: `w_e = m_i`;
- impostor edge `(i,j)`, `i != j`: `w_e = m_i * m_j`.

Consequences:

- a subject with multiplicity zero contributes no edge;
- a subject drawn `k` times contributes `k` copies of each observed genuine edge;
- an observed impostor edge between multiplicities `k` and `l` contributes `k*l` copies;
- repeated subject slots are never deduplicated;
- two slots of the same underlying subject never create an impostor edge;
- an edge absent from LFW DevTest is never synthesized.

The implementation may use integer weights instead of physically materializing duplicate
rows, but both representations must be numerically equivalent on hand-computable fixtures.

## 7. Weighted error rates and thresholds

For a replicate with positive total impostor weight `W_I`:

```text
FMR_b(t) = sum_I w_e * 1[d_e <= t] / W_I
```

For positive total genuine weight `W_G`:

```text
FNMR_b(t) = sum_G w_e * 1[d_e > t] / W_G
```

For the representation estimand, each route independently selects the largest deterministic
threshold satisfying `FMR_b(t) <= alpha`. Ties, midpoint selection and floating-point
ordering shall be specified in code and tested against a manually calculated fixture.

For the operational sensitivity estimand, the threshold is read from the immutable
VALIDATION evidence and is never reselected.

Candidate and reference metrics must use the same subject draw, edge weights and replicate
identifier. Any route-specific resampling is a blocking error.

## 8. Replicates, intervals and seed aggregation

- bootstrap RNG: NumPy `Generator` with PCG64 and a recorded root seed;
- minimum subject-bootstrap replicates: 10,000;
- convergence checkpoints: 2,000, 5,000 and 10,000 replicates;
- primary interval: percentile interval;
- non-inferiority UCB: 97.5th percentile of paired `Delta_FNMR` replicates;
- report both interval endpoints, the point estimate and Monte Carlo convergence deltas;
- retain all five predeclared projection seeds: 11, 29, 47, 71 and 101;
- no best-seed selection;
- original all-seeds decision rule remains unchanged.

The 97.5th percentile is the upper endpoint of a two-sided 95% percentile interval and
corresponds to the pre-existing conservative non-inferiority convention. It shall not be
mislabelled as the 95th percentile.

## 9. Degenerate replicate policy

A replicate is degenerate if it has zero genuine or impostor total weight, cannot support a
deterministic threshold under the specified rule, or produces a non-finite statistic.

The implementation shall:

1. record the replicate and exact reason;
2. never silently discard and redraw it;
3. fail the reanalysis if any degenerate replicate occurs unless a pre-implementation
   amendment, justified without looking at route outcomes, defines an accepted treatment;
4. report weighted genuine/impostor totals and effective edge counts per replicate.

## 10. Coverage validation by simulation

An interval is not validated merely because it is wider than the historical pair-level
interval. Before G2 can pass, controlled simulation shall test empirical coverage under:

- independent-pair null control;
- subject-level random effects affecting genuine scores;
- two-subject effects affecting impostor scores;
- raw/candidate score correlation;
- LFW-like sparse degree distribution and 500/500 edge budget;
- several discrimination regimes around the observed Study 0 range;
- threshold uncertainty at `FMR=0.01`;
- null, non-inferior and boundary `Delta_FNMR` scenarios.

The nominal target is 95% coverage. Each primary scenario shall use enough simulated
datasets for Monte Carlo standard error no greater than `0.005`. The preregistered gate is:

```text
lower 95% binomial bound on empirical coverage >= 0.93
```

Failure of this gate keeps G2 failed and triggers a versioned methodological amendment. It
does not authorize trying alternative estimators until one produces favorable Study 0
results.

## 11. Normative tests

Implementation is forbidden to claim completion until CI includes tests that demonstrate:

1. exact subject multiplicities for a fixed RNG seed;
2. genuine weight `m_i`;
3. observed impostor weight `m_i*m_j`;
4. preservation of duplicated subject slots;
5. absence of synthesized unobserved edges;
6. no impostor edge between slots of the same subject;
7. weighted/materialized equivalence;
8. identical weights across all routes in a paired replicate;
9. deterministic threshold and tie handling;
10. operational thresholds remain validation-frozen;
11. deterministic replay from root seed and configuration;
12. pair-level historical files and archived PDFs remain bitwise unchanged;
13. identity-map counts, labels, join cardinality and source digests;
14. coverage-gate behavior on passing and failing simulations;
15. an unexecuted reanalysis cannot contain results or close `E-STAT-001`.

## 12. Required new replay artifacts

No file under the original Study 0 replay may be edited. The new run shall be written under
`evidence/study_0_subject_bootstrap_v0.2.2/` and contain at least:

```text
run_manifest.json
config.resolved.yaml
source_manifest.json
test_pair_subject_map_v0.2.2.csv
subject_bootstrap_replicates.csv
subject_bootstrap_seed_summary.csv
pair_vs_subject_sensitivity.csv
threshold_transfer_uncertainty.csv
coverage_simulation.csv
coverage_gate.json
audit_trace.jsonl
replay.compact.json
```

Generated figures shall be derived only from these versioned tables and bound to their
hashes in a manifest. The complete MMALS replay bundle, source commit and paper snapshot
shall be released together.

## 13. Decision and erratum closure

`E-STAT-001` may move from `SPECIFIED_PENDING_IMPLEMENTATION` to `REANALYZED` only if:

- the identity mapping passes every invariant;
- the implementation passes every normative test;
- simulation passes the coverage gate;
- the pair-level and subject-bootstrap results are both published;
- original Study 0 artifacts remain unchanged;
- all seeds and failures are reported;
- an independent reviewer accepts the implementation and interpretation.

Passing these conditions permits G2 reassessment for the bounded Study 0 reanalysis only.
It does not establish non-inferiority, superiority, industrial biometric validity or Study 1
readiness. The result may remain `NOT_DEMONSTRATED`, and that outcome is admissible.

## 14. Relationship to the 512-to-128 projection

The projection is not omitted. Study 0 already trained the shared linear map
`512 -> 128` with contrastive loss while keeping ResNet-18 frozen. The reanalysis uses the
same frozen 128D distances and asks whether uncertainty around their comparison with raw
512D was estimated correctly.

The later research programme separately asks whether 512-to-128 projection:

- preserves verification at specified operating points;
- adds value over PCA and random projection;
- reduces watchlist payload by four;
- changes 1:N memory bandwidth or latency in practice;
- remains useful with a face-specific backbone and external data.

No storage or latency benefit can compensate for failure of the preregistered biometric
accuracy gate.
