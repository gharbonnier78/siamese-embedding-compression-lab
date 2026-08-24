# Study 1 — Execution architecture, resilience and SBOM contract

Status: `DRAFT_PREREGISTRATION_REVIEW_REQUIRED`

This is a POC engineering-assurance artifact required by the pinned scientific harness. It describes how Study 1A/1B should execute without changing scientific meaning. It does not authorize outcome-bearing runs.

## 1. Execution decision

**Do not train the face backbone from scratch.** Study 1A uses the frozen pretrained AdaFace R100/WebFace12M checkpoint documented in `STUDY1_BACKBONE_ACCEPTANCE_GATE.md`.

The only learned/fitted components inside this programme are the later 512D→128D candidate projections (PCA, Siamese/metric projection, and random control generation where applicable). This keeps the experiment focused on compression rather than large-scale face-model training.

## 2. Target GitHub-hosted execution envelope

The repository is public. A standard Linux `ubuntu-latest` GitHub-hosted runner currently provides **4 vCPU, 16 GB RAM and 14 GB SSD**. Study 1 must therefore be able to run safely inside that envelope for CI, smoke checks and bounded screening. Large qualification work must be decomposable into restartable jobs rather than assuming one long monolithic process.

Important consequence: CPU-only R100 inference is acceptable as a throughput-limited batch job, but full face-backbone training is out of scope and operationally unsuitable for this runner class.

## 3. Pipeline decomposition

The pipeline is split into idempotent stages with immutable contracts between stages:

1. **Acquire / verify model artifact**
   - download only from frozen source locator;
   - calculate SHA-256;
   - verify licence/provenance record;
   - cache only by content hash.

2. **Dataset manifest / overlap audit**
   - materialize immutable image/template/identity manifest;
   - record dataset version/source and protocol role;
   - audit identity/image/near-duplicate overlap where possible;
   - do not copy restricted datasets into repository artifacts.

3. **Preprocess / align**
   - deterministic detector/alignment configuration;
   - output manifest contains source id, preprocessing version, success/failure and reason;
   - failures are durable evidence, never silently discarded.

4. **512D embedding extraction**
   - pretrained backbone in `eval` / inference mode only;
   - CPU batches sized to memory profile;
   - embeddings written by deterministic shard key;
   - each shard includes model SHA, preprocessing contract id, dataset-manifest hash and row-level ids;
   - completed shard is immutable and reusable.

5. **Verification scoring / Gate A**
   - official fold/template protocols only;
   - threshold and metric semantics frozen before opening outcomes;
   - metrics materialized separately from raw embeddings.

6. **Study 1B projection fitting** — only after separate authorization
   - random projection: deterministic seed lineage;
   - PCA: fit on authorized TRAIN only;
   - Siamese projection: train on authorized TRAIN only, with checkpoint/restart support;
   - raw 512D is immutable reference.

7. **Qualification scoring / uncertainty**
   - subject/template dependence-aware resampling;
   - decomposable bootstrap/checkpoint jobs;
   - aggregation is deterministic and replayable.

## 4. Multiprocessing and CPU policy

The scientific unit must never be bound to worker number. Worker count is execution topology, not experimental identity.

For CPU execution on a 4-vCPU runner:

- default process count: `min(4, available_cpu)`;
- avoid nested oversubscription: numerical libraries must be constrained so each worker does not spawn an uncontrolled full thread pool;
- embedding extraction may use a bounded producer/consumer or shard-level process model, but model instances are local to workers and no mutable RNG/model state is shared;
- score generation and bootstrap may use the already-established task-bound seed lineage pattern;
- worker-count invariance must be tested on a bounded fixture before qualification.

Parallel execution is accepted only if `workers=1` and the declared multi-worker configuration produce the same ordered scientific outputs/digests for the same frozen inputs, modulo explicitly non-semantic timing/log fields.

## 5. Restart / resume contract

Every expensive stage must be restartable after GitHub timeout, transient download failure or runner loss.

Required pattern:

- work is partitioned into deterministic shards using stable ids, never scheduler order;
- a shard is complete only when its output and manifest are atomically written and hashes recorded;
- rerun first verifies existing shard hash/contract and skips valid completed shards;
- incomplete/corrupt shards are recomputed from the same frozen inputs;
- retries must reuse the same scientific seed lineage and may not silently draw a new seed;
- final aggregation refuses mixed model hashes, preprocessing contracts, dataset manifests or protocol versions.

For long campaigns, GitHub Actions should use a matrix or explicit shard/checkpoint workflow, upload immutable artifacts per shard, and run a separate deterministic aggregation job. No scientific conclusion may depend on one runner surviving longer than the platform limit.

## 6. Resource-feasibility gates before outcome-bearing execution

Before Study 1A outcomes are opened, run non-outcome-bearing engineering checks on synthetic/public fixture data:

- memory high-water mark < **12 GB** on the 16-GB runner;
- free disk reserve >= **2 GB** throughout the smoke run;
- deterministic 1-worker vs 4-worker digest equivalence;
- forced-interruption/restart test reproduces the same final digest as uninterrupted execution;
- model load + one-batch inference succeeds on CPU;
- throughput benchmark records images/s and extrapolated wall time without claiming scientific performance;
- no single required shard is sized to require > **4 hours** under measured CPU throughput, leaving margin below the GitHub-hosted 6-hour job ceiling used by the existing programme experience;
- artifact sizes are checked before choosing GitHub Actions artifact retention as storage.

If the measured R100 CPU throughput makes a qualification dataset impractical, the scientific protocol does not change. The allowed responses are: reduce shard size, add more independent jobs, or use an explicitly documented larger/GPU runner. It is not allowed to switch backbone after seeing scientific outcomes.

## 7. Dependency and SBOM policy

Study 1 must produce a machine-readable SBOM for the **actual frozen execution environment**, not just a prose dependency list.

Preferred output formats:

- CycloneDX JSON for Python/environment dependencies;
- SHA-256 inventory for downloaded model artifacts and executable scripts/configs.

Minimum SBOM/provenance scope:

- Python interpreter version;
- `torch` / `torchvision` if the PyTorch AdaFace path is used;
- `numpy`;
- `scipy` where used;
- `scikit-learn` for PCA/metrics where used;
- image stack (`opencv-python-headless`, Pillow as applicable);
- face-alignment/detector dependency and exact version/commit;
- YAML/config parser dependencies;
- test/lint/static-analysis packages used by CI;
- any direct Git dependency pinned to immutable commit;
- AdaFace source commit;
- exact pretrained checkpoint SHA-256;
- dataset manifests by hash, without embedding restricted dataset contents in the SBOM.

The final list must be generated from the lock/frozen environment after implementation; this document intentionally does not invent package versions before the implementation path is reviewed.

## 8. Supply-chain and security checks

Before outcome-bearing execution:

- dependencies must be pinned/locked;
- direct Git dependencies require immutable commit SHAs;
- `pip-audit` or equivalent dependency vulnerability review runs in CI;
- secret scanning runs in CI/repository protection path;
- static code/security analysis runs where supported;
- model checkpoint source and SHA-256 are verified before load;
- deserialization of untrusted pickle-like checkpoints is treated as a security boundary; prefer safe loading/conversion path and do not execute arbitrary downloaded code;
- dataset credentials/tokens must be injected through GitHub secrets or local environment, never committed or persisted in artifacts/logs;
- logs must not publish biometric source images or restricted identifiers;
- every finding is fixed, marked not applicable, or explicitly accepted with rationale and scope.

## 9. Architecture acceptance for Study 1A

The technical/reproducibility reviewer may return `VERDICT_B: ACCEPT` only if:

1. the frozen pretrained backbone loads from a hashed artifact;
2. the exact preprocessing path is deterministic and tested;
3. the dependency environment is pinned and SBOM generation is reproducible;
4. CPU smoke inference passes on the target 4-vCPU class;
5. 1-worker/4-worker equivalence passes on the bounded fixture;
6. interruption/resume equivalence passes;
7. shard/aggregation contracts reject mixed provenance;
8. quality/security checks required by the POC harness profile are green or have explicit bounded dispositions;
9. measured throughput shows that the chosen sharding plan is operationally feasible on GitHub-hosted runners, or an alternative runner class is frozen before outcomes;
10. no backbone training is accidentally present in the Study 1A workflow.

## 10. Scientific boundary

Execution feasibility is engineering evidence only. A fast, resumable, secure pipeline does not prove Gate A and does not demonstrate compression non-inferiority. Conversely, an infrastructure failure must be reported as infrastructure failure rather than converted into a scientific negative result.
