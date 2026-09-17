# Study 1B — Preflight and execution architecture

Status: `NONOUTCOME_IMPLEMENTATION_IN_PROGRESS`

This document describes the executable structure needed to make the frozen Study 1B protocol reviewable and replayable. It does not authorize SCREEN or qualification outcomes.

## What `preflight` means here

`Preflight` is the engineering/scientific equivalent of a **pre-flight check before take-off**. It verifies that the experiment is capable of taking off under the frozen contract **before looking at the scientific result**.

For Study 1B, a preflight may inspect:

- source identity and hashes;
- identity/capture counts;
- TRAIN / VALIDATION / SCREEN / TEST isolation;
- pair-graph feasibility and hashes;
- exact/near-duplicate leakage risk;
- seed lineage and deterministic replay;
- estimator known-truth coverage on synthetic data;
- planning power on synthetic data;
- runtime, memory, sharding and restart cost;
- dependency/SBOM/security/static checks.

It must **not** inspect AdaFace compression SCREEN/TEST performance, select a winning route, move identities after seeing scores, tune hyperparameters from protected outcomes, or release a scientific claim.

Therefore:

`preflight PASS != compression works`.

It means only:

`the measuring instrument + data boundary + execution machinery are sufficiently prepared for the next authorized scientific action`.

A preflight failure is usually an engineering/protocol blocker, not a negative biometric result.

## Pipeline decomposition

```text
LFW public source
   |
   +--> peopleDevTrain / peopleDevTest hashes
   +--> image-byte hashes + pseudonymous capture manifest
   |
   v
NON-OUTCOME PREFLIGHT
   |
   +--> deterministic identity roles
   +--> cross-role duplicate / near-duplicate audit
   +--> frozen TRAIN / VALIDATION / SCREEN / TEST pair graphs
   +--> graph hashes + seed lineage
   +--> known-truth coverage simulation
   +--> a-priori power simulation
   +--> runtime/cost pilot and shard sizing
   +--> CI / static / dependency / SBOM assurance
   |
   v
DOUBLE INDEPENDENT REVIEW
   |
   v
EXPLICIT HUMAN GO
   |
   +----------------------------+
   |                            |
   v                            v
Stage A SCREEN             Stage B QUALIFICATION
(non-claim-bearing)        (claim-bearing)
   |                            |
raw/random/PCA/Siamese     raw/random/PCA/Siamese
seeds 11,29                seeds 11,29,47,71,101
   |                            |
identity bootstrap              identity bootstrap
   |                            |
CONTINUE/STOP/REDIRECT          frozen NI decision
```

Stage B must not be reached by merely changing a workflow input. The authorization artifact declares the allowed stage and is bound to the exact protocol SHA-256.

## Code boundaries

- `study1b_preflight.py`: source/role/capture/graph and leakage checks only; no model scores.
- `study1b_statistics.py`: frozen subject-slot resampling plus explicit degeneracy accounting.
- `study1b_simulation.py`: synthetic known-truth coverage and power.
- `study1b_execution.py`: raw512 table contract, route fitting/serialization, authorization guard.
- `study1b_preflight_lfw.py`: public LFW non-outcome materialization entry point.
- `study1b_run_simulation_shard.py`: resumable decomposed synthetic simulation with append-only progress.
- `study1b_execute.py`: outcome runner; inaccessible without an exact human authorization artifact.

## Separation of randomness

All scientific randomness is task-bound to root entropy `20260827`. Task labels are hashed into independent `numpy.random.SeedSequence` inputs. Worker number, scheduling order, shard id and restart position are never scientific seeds.

The following domains remain distinct:

- pair-graph generation;
- random128 transforms;
- PCA randomized SVD;
- Siamese initialization/training order;
- bootstrap draws;
- synthetic coverage datasets;
- synthetic power datasets.

## Simulation decomposition and the six-hour constraint

The previous Study 0 coverage work demonstrated that a nominal GitHub workflow timeout above six hours does not extend the GitHub-hosted job hard limit. Study 1B therefore treats **less than four hours per required shard** as the planning envelope.

The full coverage/power contract is intentionally not weakened to fit this envelope. A cheap non-gating cost pilot uses only 2 synthetic datasets x 100 bootstrap replicates to estimate runtime/memory. Its values have **zero gate authority**. They may only determine shard size and worker layout.

If the full frozen 10,000-replicate / 4,000-dataset design cannot fit the available compute architecture, the correct outcome is a preflight blocker and a reviewed protocol/execution amendment — not a silent reduction of replicates, checkpoints, graph size or seed count.

## Failure semantics

| Failure | Classification | Scientific meaning |
|---|---|---|
| wrong LFW counts/hash | provenance/infrastructure | none; fail closed |
| cross-role leakage | protocol blocker | none until resolved |
| requested pair graph impossible | design blocker | none; amend before outcomes |
| synthetic coverage gate fails | estimator-validity blocker | do not open protected outcomes |
| power < 0.90 | design/power blocker | do not open TEST |
| timeout/OOM | infrastructure/cost blocker | not a negative compression result |
| missing authorization | governance blocker | execution prohibited |
| SCREEN fails promotion | non-claim-bearing scientific screen | STOP/REDIRECT only |
| Stage B NI fails | claim-bearing scientific result | `NOT_DEMONSTRATED`, not universal inferiority |

## Current boundary

The user authorization of 2026-08-27 covers **non-outcome LFW preflight, synthetic coverage/power work and implementation of the Study 1B executor**. It does not authorize SCREEN, qualification TEST, representation geometry or production/biometric-certification claims.
