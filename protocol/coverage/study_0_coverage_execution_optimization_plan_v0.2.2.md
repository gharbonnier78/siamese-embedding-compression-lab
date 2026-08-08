# Study 0 v0.2.2 Coverage Execution Optimization Plan

Status: **PRE-OUTCOME ENGINEERING PLAN — NO COVERAGE OUTCOME OBSERVED**

This document records the execution-design decisions required after the non-outcome cost benchmark identified the frozen coverage gate as computationally expensive at production scale. It does not alter the estimands, coverage criterion, scenarios, bootstrap count, stopping rule, or historical Study 0 evidence.

## 1. Trigger

The non-outcome benchmark of the reviewed implementation measured approximately 11–12 s per simulated dataset at 10,000 bootstrap replicates on a GitHub-hosted runner, implying roughly 6.5 h single-worker per 2,000-dataset scenario and roughly 33 h single-worker for the five-scenario first checkpoint.

The benchmark also changed the initial optimization hypothesis:

- code inspection suggested `weighted_threshold_at_fmr` as the likely dominant hotspot because its worst-case structure repeatedly scans weighted impostor distances;
- measurement at the frozen `target_fmr = 0.01` showed that the early break usually makes threshold selection inexpensive relative to subject-weight generation;
- `edge_weights` and subject-multiplicity generation are materially more expensive in the measured execution path;
- therefore optimization priority is based on measurement, not worst-case inspection alone.

No coverage outcome was computed and no historical Study 0 score artifact was read while making this decision.

## 2. Optimization order

The next engineering experiments are ordered as follows.

1. Deterministic dataset-level parallelism with explicitly independent RNG substreams.
2. Vectorized subject-edge weight construction using precomputed subject indices.
3. Possible reuse of identical subject draws/edge weights between representation and operational estimands, only if exact RNG and result semantics are proven equivalent to the reviewed reference behavior.
4. Threshold implementation optimization only if profiling after the previous steps shows it remains material.

No experiment in this list may silently change the frozen statistical contract.

## 3. Experiment 1 — deterministic parallel datasets

### 3.1 Why this comes first

Simulated datasets are conceptually independent outer Monte Carlo units. Parallelizing those units can reduce wall-clock time without changing the inner subject-bootstrap estimator, provided that random-number streams, dataset identity, output ordering, and failure semantics are independent of worker count and scheduling order.

### 3.2 RNG requirement

The current implementation derives per-dataset seeds arithmetically from `root_seed`. The frozen coverage contract specifies the root seed and PCG64 generator family but does not freeze the substream-derivation algorithm.

Before parallel execution is accepted, the implementation shall replace implicit arithmetic seed derivation with an explicit hierarchical NumPy `SeedSequence` contract.

Minimum required hierarchy:

```text
root SeedSequence(root_seed)
  -> scenario child stream
       -> dataset child stream
            -> distance-generation child stream
            -> bootstrap child stream
```

Equivalent hierarchy encodings are acceptable only if they preserve the same properties and are versioned explicitly.

The purpose is not merely deterministic seed mapping. It is to use a generator-supported substream construction designed for statistically independent child streams rather than relying on assumptions about nearby integer seeds.

### 3.3 Required provenance

Each simulated dataset must be reconstructable from recorded provenance including at least:

- root seed;
- scenario identifier/index;
- dataset index;
- SeedSequence spawn key or equivalent child-stream lineage;
- bit-generator family (`PCG64`);
- bootstrap replicate count;
- software commit/configuration identifier.

### 3.4 Acceptance tests

Parallelization is acceptable only if all of the following pass before production coverage execution:

1. **Serial/parallel identity test** — the same frozen root seed and configuration produce identical dataset-level outputs when executed with 1 worker and N workers.
2. **Scheduling-order invariance** — deliberately permuting task completion order does not change dataset identity, seeds, metrics, degeneracy status, or final ordered artifact rows.
3. **Worker-count invariance** — results are independent of the number of workers.
4. **Replay test** — any individual dataset can be regenerated from its recorded seed lineage without executing earlier datasets.
5. **No shared mutable RNG state** — workers never share one advancing `Generator` instance.
6. **No outcome-based retries** — failed or degenerate datasets are not silently regenerated with new child streams.
7. **Stable aggregation** — coverage counts and artifacts are assembled by deterministic dataset index, not completion order.

A statistical claim of mathematical independence is not inferred from empirical correlation tests. The contract relies on explicit `SeedSequence` child-stream construction plus deterministic replay and isolation tests.

### 3.5 Versioning boundary

Because the current contract freezes `root_seed` and `PCG64` but not the child-stream derivation, this SeedSequence hierarchy is treated as a pre-outcome reproducibility clarification. It must be versioned and reviewed before the first production coverage outcome is observed.

If any coverage outcome is observed before this clarification is accepted, changing RNG stream derivation afterward requires an explicit methodological amendment and cannot be represented as preregistered behavior.

## 4. Experiment 2 — vectorized `edge_weights`

The reference implementation performs Python-level endpoint lookup for every observed pair on every bootstrap replicate. The optimization may precompute integer subject indices for each pair and use NumPy indexing to construct weights.

Acceptance requires numerical identity to the reference implementation across:

- fixed fixtures;
- randomized multiplicity vectors;
- zero multiplicities;
- repeated subjects;
- genuine self-edges (`m_i`);
- impostor edges (`m_i * m_j`);
- large multiplicities within expected integer bounds.

The optimized path must not alter subject sampling, sparse graph structure, or pair ordering.

## 5. Experiment 3 — reuse of subject draws and weights

Representation and operational paths currently instantiate their own bootstrap execution while using aligned seeds. Reusing one subject draw/weight vector could remove duplicated work, but this is more semantically sensitive than dataset-level parallelism or local vectorization.

It is acceptable only if the reviewed specification requires the two estimands to operate on the same bootstrap draw and if equivalence tests prove that the refactor preserves the exact replicate sequence, thresholds, rates, audit behavior, and degeneracy semantics.

No reuse is allowed merely because it is faster.

## 6. Experiment 4 — threshold optimization

`weighted_threshold_at_fmr` remains a worst-case optimization candidate, but the measured `target_fmr = 0.01` execution path currently exits early and is not the dominant measured cost.

It should therefore be optimized only after re-profiling the previous changes. If optimized, whole-tie-block semantics, sentinel behavior, dtype handling, positive-weight filtering, and exact threshold choice must remain equivalent to the reviewed reference algorithm.

## 7. Runtime environment

The first checkpoint remains too expensive for a single long GitHub-hosted job even after modest local optimization. Production execution should therefore use either:

- bounded parallel jobs/shards with deterministic artifact aggregation; or
- a controlled self-hosted/off-CI execution environment with immutable environment/configuration capture and later artifact verification.

CI remains the place to validate the implementation and replay contract; it need not be the place where the entire production-scale Monte Carlo workload executes.

## 8. Decision gate

`CHRON-20260808-001` remains OPEN until the reviewed execution strategy demonstrates acceptable feasibility at the frozen scale without changing the statistical contract.

The benchmark alone does not permit production coverage execution. The optimization/parallelization path must be reviewed, its equivalence and RNG-isolation tests must pass, and its execution provenance must be versioned before the blocker can be resolved.
