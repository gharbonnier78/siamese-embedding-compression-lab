# Siamese Embedding Compression Lab — Study 1 protocol supplement v0.3-study1a-active

**Status:** Study 1A active; A1/A2 outcome-bearing benchmarks opened on 2026-08-24. Study 1B remains unauthorized. This revision describes the active protocol and pre-execution evidence; benchmark outcomes are intentionally not inserted until the A1/A2 run completes and its evidence bundle is archived.

## Abstract

Study 0 asked whether a 512D face-verification representation could be compressed to 128D by random projection, PCA or a learned Siamese projection while remaining competitive with the uncompressed representation. After correction from pair-level to identity-dependence-aware uncertainty, Study 0 v0.2.4 closed with non-inferiority not demonstrated for any 128D route. Study 1 changes the experimental substrate before repeating the compression question: it uses a credible face-specific frozen 512D backbone, AdaFace R100 / IR101 trained on WebFace12M, verifies that the exact inference pipeline is reproduced correctly, and then asks whether the learned Siamese 512→128 route preserves verification performance better than simple 128D controls. The active Study 1A gate is deliberately proportional to that question: A1 is an LFW sanity/reproduction check; A2 is a four-benchmark difficult public verification reproduction check. IJB-C and NIST FRTE remain external-validity/extension references rather than mandatory blockers for the compression experiment. Pre-execution controls for checkpoint identity, preprocessing, RGB/BGR convention, deterministic replay, worker-count equivalence, restart/resume equivalence, manifests/provenance and overlap-audit design have all passed and their evidence ZIP has been durably archived before A1/A2 outcomes are opened.

## 1. Scientific question and sequence

The central question is narrower than biometric-product qualification:

> Starting from a credible face-specific frozen 512D embedding, does a learned Siamese 512D→128D projection preserve verification performance better than Gaussian random projection and PCA, and how do all compressed routes compare with the uncompressed raw512 reference?

The sequence is:

1. **Study 1A:** establish that the exact frozen AdaFace 512D pipeline is a credible substrate for the compression comparison.
2. **A1/A2 sanity gate:** reproduce standard public AdaFace face-verification benchmarks within already-frozen tolerances.
3. **Study 1B:** only after Study 1A PASS and a separate explicit GO, compare raw512, random128, PCA128 and Siamese128 under matched data/splits/trials.

Study 1A is therefore a **substrate sanity qualification**, not a production biometric certification programme.

## 2. Frozen face-specific backbone

Study 1A uses a pretrained face-recognition backbone; it is not retrained in this study.

- method: **AdaFace**;
- architecture: **R100 / IR101** (`ir_101` in the pinned implementation);
- embedding dimension: **512**;
- released training corpus: **WebFace12M**;
- upstream repository: `mk-minchul/AdaFace`;
- upstream code/protocol commit: `c60eaa786a42c03444f3df7096dbaf9d57ae010d`;
- historical checkpoint candidate used by the active runner: `VishalMishraTss/AdaFace/adaface_ir101_webface12m.ckpt`;
- checkpoint SHA-256: `0e7a3238d2a50f3fe3860782534928ac7cb2598977cf897f6869fd5ac2493fd0`;
- inference state is loaded with `torch.load(..., weights_only=True)` and strict `model.*` backbone keys only.

Independent pre-execution work established a 49-residual-block IR101/R100 architecture fingerprint and exact inference-backbone equivalence with the author-maintained Hugging Face safetensors artifact under the deterministic RGB↔BGR first-convolution channel transformation. This is stronger than label/name matching but does not claim byte identity with the unavailable original Google Drive bytes.

## 3. Frozen input and preprocessing contract

A frozen model is not by itself a frozen experiment. The material input path is part of the model as executed.

For ordinary raw images, the contract freezes orientation/decoding, face detection, five-point alignment, 112×112 crop, representation convention, normalization, frozen inference and deterministic postprocessing. No undeclared denoise, sharpen, restoration, super-resolution, quality filtering or outcome-driven exclusions are permitted.

For the standard A1/A2 InsightFace/AdaFace validation `.bin` artifacts, face alignment has already been materialized upstream as aligned 112×112 crops. Re-running MTCNN on those benchmark crops would change the benchmark. The active benchmark path is therefore:

`aligned validation-bin bytes → deterministic decode → BGR → normalize to [-1,1] → frozen IR101 → horizontal flip → AdaFace norm-aware fusion → L2-normalized 512D embedding → verification protocol`.

## 4. Pre-execution controls: demonstrated, not merely declared

Before protected benchmark outcomes were opened, the dedicated `Study 1A Preexecution Controls` workflow demonstrated:

- preprocessing fingerprint: **PASS**;
- deterministic 512D embedding replay: **PASS**;
- RGB/BGR representation sentinel: **PASS**;
- 1-worker vs 2-worker output/digest equivalence: **PASS**;
- interruption/restart equivalence: **PASS**;
- manifest/provenance integrity: **PASS**;
- overlap-audit design frozen: **PASS_DESIGN_FROZEN**;
- embedding dimension guard: **512D**;
- `scientific_outcomes_opened: false` during these controls.

The combined embedding payload digest was identical for reference, multi-worker and resumed execution:

`66c5de4c4a76d187ec915ad333c96e57f4641e7cd7231aa688624fdc8b3648c2`.

The compact evidence artifact from workflow run `32770622785` was promoted from temporary GitHub Actions storage into durable repository evidence. Archived ZIP SHA-256:

`a5915b11721c6b1f9defa3d53cefe7d0fae964d6f117779acdf28abc40f121fd`.

These checks are engineering/provenance evidence. They make the scientific run admissible; they are not themselves scientific benchmark results.

## 5. A1 — LFW sanity/reproduction

**A1 asks a simple question:** does the exact frozen AdaFace pipeline reproduce its basic published LFW performance closely enough that the pipeline is not obviously broken?

LFW (Labeled Faces in the Wild) is used here as the basic reproduction sanity benchmark under the standard 10-fold face-verification protocol.

- AdaFace R100/WebFace12M published reference: **99.82% accuracy**;
- preregistered minimum: **99.62% accuracy**;
- maximum tolerated reproduction deficit: **0.20 percentage point**;
- A1 alone cannot release Study 1A.

A failure of A1 with otherwise valid execution is a scientific **FAIL** for the substrate sanity gate, not an infrastructure error.

## 6. A2 — difficult public face-verification reproduction

**A2 asks whether the same frozen 512D substrate remains credible on more difficult, complementary variations rather than only on LFW.** All four checks must pass.

| Benchmark | Main variation stressed | Published reference | Frozen minimum |
| --- | --- | ---: | ---: |
| **CFP-FP** | frontal vs profile pose | 99.26% | **98.96%** |
| **CPLFW** | cross-pose | 94.57% | **94.27%** |
| **CALFW** | cross-age | 96.12% | **95.82%** |
| **AgeDB-30** | large age-gap | 98.00% | **97.70%** |

Each A2 threshold retains the preregistered maximum reproduction deficit of **0.30 percentage point**. These values were frozen before any Study 1A outcome was opened and were not relaxed by the compression-focused rescope.

A2 is conjunctive: `CFP-FP PASS ∧ CPLFW PASS ∧ CALFW PASS ∧ AgeDB-30 PASS`.

## 7. Active A1/A2 verification protocol

The benchmark runner follows the pinned AdaFace high-quality validation semantics:

1. preserve the standard validation-pair order;
2. decode the pre-aligned 112×112 image bytes;
3. use the historical AdaFace BGR convention and normalization `(pixel/255 - 0.5)/0.5`;
4. infer the original crop and its horizontal flip;
5. fuse original/flip features with AdaFace norm-aware fusion;
6. retain L2-normalized 512D embeddings;
7. pair consecutive embeddings from the standard verification container;
8. compute squared Euclidean distance;
9. use 10 non-shuffled folds;
10. within each fold, select the best threshold on the other nine folds from `np.arange(0,4,0.01)` and evaluate it on the held-out fold;
11. report the mean held-out accuracy, all fold accuracies and selected thresholds.

A valid numerical threshold failure is preserved as scientific evidence and does not make CI artificially red. An execution/provenance defect instead yields `INDETERMINATE`.

## 8. Validation data and provenance

The standard `.bin` transport artifacts for LFW, CFP-FP, CPLFW, CALFW and AgeDB-30 are acquired from the public Hugging Face mirror `Icar/val_sets`. The mirror is a **locator**, not the scientific identity of the benchmark.

Each downloaded file is hashed before interpretation. The outcome report records benchmark name, SHA-256, byte size, number of image blobs and pairs, genuine/impostor counts, exact image-byte duplicate diagnostics and any decode failure. The image/checkpoint bytes are not uploaded into the result artifact or committed into Git.

Because the serialized `.bin` transport does not provide stable subject identifiers for every pair, identity-level overlap cannot be reconstructed reliably from that artifact alone. This limitation is reported rather than guessed. No samples are removed based on observed performance.

## 9. A3 / low-FMR evidence — useful extension, not a release blocker

The earlier preregistration treated IJB-C low-FMR replay as mandatory. Independent pre-outcome review accepted a proportional amendment because the actual research question is compression on a credible face-specific embedding, not comprehensive biometric-product qualification.

Therefore:

- IJB-C remains valuable if a lawful/replayable copy is available;
- NIST **FRTE 1:1** remains the modern sequestered external-validity/methodological reference;
- WebFace260M or another low-FMR local benchmark would require its own preregistered endpoint;
- no A3/low-FMR result may alter or rescue failed A1/A2 thresholds;
- absence of low-FMR evidence does **not** block the bounded compression comparison.

## 10. Active Study 1A decision semantics

Under the independently accepted compression-focused amendment:

- **A1 PASS:** LFW accuracy ≥ 99.62%.
- **A2 PASS:** all four A2 accuracies meet their frozen minima.
- **Study 1A PASS:** A0/pipeline integrity remains valid + A1 PASS + A2 PASS.
- **FAIL:** execution is valid but at least one frozen A1/A2 threshold fails.
- **INDETERMINATE:** artifact, dataset, protocol, preprocessing or execution evidence is invalid/incomplete.

A PASS means only:

> the exact AdaFace raw512 representation is accepted as a credible substrate for the planned compression comparison.

It does not establish production readiness, fairness, PAD/security, regulatory conformity, 1:N quality, low-FMR operational fitness or state-of-the-art superiority.

## 11. Study 1B routes — still blocked pending separate GO

The later matched comparison remains:

- **raw512:** frozen L2-normalized AdaFace 512D embedding;
- **random128:** seeded Gaussian 512→128 projection, then L2 normalization;
- **PCA128:** PCA fit only on authorized TRAIN embeddings, never qualification TEST;
- **Siamese128:** supervised shared 512→128 metric projection trained only on authorized TRAIN pair supervision.

Siamese is a candidate to test, not the method that must win. Study 1B remains outside the current human authorization even if Study 1A passes.

## 12. Compression estimand and uncertainty direction

For a candidate route `m`, raw reference `b` and target false-match operating point `alpha`:

`Delta_FNMR(m, alpha) = FNMR_m(alpha) - FNMR_b(alpha)`.

Study 1B must preserve dependence-aware uncertainty because verification rows can share identities/templates. Sampling units, paired raw/candidate resampling, projection/model seeds, bootstrap Monte-Carlo seeds and degeneracy handling must be explicit. Study 0's corrected identity-aware result remains the warning against treating verification pair rows as independent observations.

## 13. Evidence retention and reproducibility

Load-bearing evidence must outlive temporary CI retention when losing it would make a gate/review decision unreconstructable.

For Study 1A:

- pre-execution evidence ZIP has already been archived durably with SHA-256;
- each A1/A2 job uploads compact JSON evidence only;
- the final A1/A2 aggregation bundle must be downloaded, hashed and promoted to durable repository/controlled-store retention before its temporary Actions retention expires;
- restricted face images, checkpoint bytes and other large/licensed artifacts are referenced by content hash and controlled locator rather than copied into Git.

This is the practical evidence-retention rule now proposed upstream to the scientific research harness.

## 14. Current state at this revision

As of 2026-08-24:

- Study 0 v0.2.4: **closed negative result**;
- Study 1A human GO: **recorded**;
- compression-focused Study 1A amendment: **independently ACCEPTED and ACTIVE**;
- checkpoint/preprocessing/concurrency/resume pre-execution controls: **PASS**;
- pre-execution evidence ZIP: **durably archived**;
- A1/A2 scientific benchmarks: **OPENED / RUNNING**;
- A1/A2 scientific outcomes: **not yet inserted in this document**;
- IJB-C/FRTE low-FMR: **external-validity extension, not mandatory A1/A2 blocker**;
- Study 1B: **NOT AUTHORIZED**.

## References / authoritative project artifacts

- `protocol/studies/STUDY1A_COMPRESSION_FOCUSED_AMENDMENT_2026-08-24.md`
- `protocol/studies/STUDY1A_A1_A2_EXECUTION_PLAN_2026-08-24.md`
- `protocol/studies/STUDY1A_FROZEN_INPUT_IMAGE_CONTRACT.md`
- `protocol/studies/STUDY1A_OVERLAP_AUDIT_DESIGN.md`
- `protocol/studies/STUDY1_CHECKPOINT_SOURCE_AND_EQUIVALENCE.md`
- `protocol/reviews/STUDY1A_COMPRESSION_FOCUSED_AMENDMENT_REVIEW_ACCEPTED_2026-08-24.md`
- `protocol/authorizations/study_1a_execution_go_2026-08-24.yaml`
- `artifacts/study1a/preexecution/2026-08-24/`
- `harness-adoption.yaml`
- AdaFace upstream commit `c60eaa786a42c03444f3df7096dbaf9d57ae010d`
- NIST Face Challenges / FRTE 1:1 references recorded in the protocol
