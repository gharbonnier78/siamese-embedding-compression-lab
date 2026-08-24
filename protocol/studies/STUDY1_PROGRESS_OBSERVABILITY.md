# Study 1 — Progress observability contract

Status: `DRAFT_PREREGISTRATION_REVIEW_REQUIRED`

This contract adapts the proven Study 0 production-coverage observability pattern to Study 1. It is runtime observability only; it does not create or alter scientific evidence.

## 1. Study 0 pattern being reused

Study 0 used a parent-process callback around `ProcessPoolExecutor.map`, not unsynchronized worker logging. The parent emitted an append-only `progress.jsonl` line and a flushed GitHub log line every fixed number of completed datasets. Each event carried checkpoint/block identity, completed/total counts, canonical progress, percentage, elapsed time, throughput and ETA. Study 0 production work was itself split into explicit checkpoint blocks such as 2,000 and 4,000 datasets.

Study 1 preserves that separation:

- **worker/process topology is execution-only**;
- **the parent/aggregator owns progress accounting and output**;
- **progress is append-only and persisted in `progress.jsonl`**;
- **GitHub receives the same JSON event immediately through a flushed stdout line**;
- **resume continues from the last validated canonical count rather than restarting progress at zero**.

## 2. Adaptation to Study 1 units

Study 1 does not have one universal unit called `dataset`. Each long stage must declare its progress unit and block bounds before execution.

Recommended units:

| Stage | Unit | Typical block meaning |
| --- | --- | --- |
| detection/alignment | images | stable image-index range |
| AdaFace 512D extraction | images | stable image-index range |
| verification scoring | trials or templates | official protocol range |
| subject/template bootstrap | replicates | deterministic bootstrap-index range |
| Study 1B Siamese fitting | batches/epochs plus samples | frozen training checkpoint interval |

The scientific identity of a block is defined by stable input/protocol bounds, never by which worker happened to process it.

## 3. Mandatory visible event fields

Every long-running block must emit `block_started`, periodic `block_progress`, and `block_complete` events. Retry and already-valid resume paths should emit `RETRY` and `SKIPPED_VALID` where applicable.

Every periodic event must expose in GitHub logs and `progress.jsonl`:

- stage and unit;
- block id, start and stop;
- completed and total units in the block;
- canonical completed-through index;
- block progress percentage;
- worker count;
- resume offset;
- elapsed time for the current run;
- throughput in units/minute;
- estimated remaining seconds for the current block;
- campaign-level completed/total and percentage when a campaign total is known;
- `runtime_observability_only=true`.

## 4. Reporting cadence

The cadence is stage-specific and must be chosen so GitHub never appears silent for a long-running process while avoiding excessive log volume.

Initial defaults for review:

- image preprocessing / embedding extraction: every **250 images**;
- verification trial scoring: every **1,000 trials**;
- bootstrap: every **25 replicates** or an equivalent interval preserving regular feedback;
- training: at least once per epoch and additionally every bounded batch interval if epochs are long.

The final cadence may be changed before outcome-bearing execution based on the non-outcome throughput smoke, but the requirement for regular parent-owned progress cannot be removed.

## 5. Block structure analogous to Study 0 2,000 / 4,000 checkpoints

For Study 1, dataset size determines the exact ranges. Once a dataset manifest is frozen, preprocessing and embedding work is partitioned into deterministic contiguous or stable-hash ranges. For example, a 10,000-image campaign may be represented as blocks `0:2000`, `2000:4000`, `4000:6000`, etc. This is an execution example, not a scientifically privileged block size.

Each GitHub matrix job should carry one or more explicit block ids, and the logs must make both the current block percentage and campaign percentage visible. A completed block is hash-bound and reusable on restart.

## 6. Resume semantics

On restart:

1. validate existing shard payload and provenance first;
2. read the matching append-only progress log only as runtime state/diagnostic information;
3. derive the authoritative resume point from validated completed artifacts/manifests;
4. initialize progress with the validated completed count;
5. continue canonical counters and campaign percentage monotonically;
6. never draw a new scientific seed solely because a job restarted.

A progress line alone can never make a shard scientifically complete.

## 7. Multiprocess rule

Workers may optionally report completion messages to the parent through the executor/future collection path, but workers must not independently append to the shared progress file. The parent serializes progress events. This avoids interleaved/missing lines and makes `workers=1` versus `workers=4` observability comparable while scientific outputs remain identical.

## 8. Acceptance criteria for Review B

`VERDICT_B: ACCEPT` requires all of the following before outcome-bearing execution:

1. a bounded CI smoke visibly prints `[study1-progress]` events;
2. `progress.jsonl` is uploaded as an artifact;
3. periodic events include percent, throughput and ETA;
4. parent-owned accounting is used in the multiprocess execution path;
5. restart/resume continues canonical counts without resetting or double-counting;
6. completed artifact manifests, not logs alone, remain the authority for resume eligibility;
7. real 4-vCPU throughput measurement is used to finalize block sizing so no planned block approaches the GitHub-hosted job ceiling.

## 9. Scientific boundary

Progress, throughput and ETA are operational metadata. They must not be used as biometric performance evidence, as a substitute for Gate A, or to alter frozen scientific thresholds after outcomes are visible.
