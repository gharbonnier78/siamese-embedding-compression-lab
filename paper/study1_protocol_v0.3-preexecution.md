# Siamese Embedding Compression Lab — Study 1 protocol supplement v0.3-preexecution

**Status:** pre-execution methods supplement; no Study 1 scientific outcomes included.

## Abstract

Study 0 asked whether 512D face-verification representations could be compressed to 128D with random, PCA or Siamese projections while remaining non-inferior to the uncompressed representation. After correction from pair-level to identity-dependence-aware uncertainty, Study 0 closed with non-inferiority not demonstrated for any 128D route. Study 1 changes the experimental substrate before repeating the compression question: it first qualifies an exact frozen face-specific 512D backbone, AdaFace R100 trained on the released WebFace12M corpus, and only if that raw representation passes a preregistered reproduction gate may a separately authorized Study 1B compare raw512, random128, PCA128 and Siamese128. This supplement records the evaluation protocol, data hierarchy, models and algorithms, low-FMR decision semantics, uncertainty strategy, execution architecture and pre-execution blockers. It contains no new scientific result.

## 1. From Study 0 to Study 1

Study 0 used frozen ImageNet ResNet-18 512D representations on LFW and compared four matched routes: raw512, random128, PCA128 and a supervised Siamese linear 512→128 projection. The corrected study retained its negative conclusion while showing that pair-level bootstrap intervals had understated uncertainty because identities recur across observed verification pairs.

Study 1 addresses the most consequential limitation first: before asking whether compression preserves verification performance, the 512D source representation itself must be credible for face verification.

The sequence is therefore:

1. **Study 1A:** reproduce one exact face-specific 512D backbone under frozen benchmark protocols.
2. **Gate A:** require provenance integrity plus preregistered numerical reproduction criteria.
3. **Study 1B:** only after Gate A PASS and a separate GO, compare matched 512D/128D compression routes.

## 2. Frozen face-specific backbone

Study 1A uses the official AdaFace implementation and checkpoint:

- method: AdaFace;
- architecture: R100 / `ir_101`;
- embedding dimension: 512;
- released training corpus: WebFace12M;
- upstream repository: `mk-minchul/AdaFace`;
- upstream commit: `c60eaa786a42c03444f3df7096dbaf9d57ae010d`;
- official R100/WebFace12M checkpoint locator: Google Drive file id `1dswnavflETcnAuplZj1IOKKP0eM8ITgT`;
- exact checkpoint SHA-256: materialized in a dedicated non-outcome-bearing pre-execution step before any benchmark outcome;
- face-backbone training inside Study 1A: prohibited.

Code licence, checkpoint rights and training-data rights are recorded separately. The MIT licence of the source repository is not treated as proof that model bytes or training data inherit identical terms.

## 3. Frozen preprocessing

The reference path is pinned to the same AdaFace commit:

- MTCNN/five-point face alignment;
- 112×112×3 crop;
- BGR channel order;
- normalization `(pixel / 255 - 0.5) / 0.5`;
- `net.build_model('ir_101')`;
- frozen `eval()` inference;
- L2-normalized 512D output;
- cosine similarity or equivalent normalized-Euclidean ordering for verification scoring.

Alignment/detection failures and exclusions are retained in the evidence pack. A local preprocessing adapter must demonstrate bounded equivalence before qualification outcomes can be opened.

## 4. Evaluation data hierarchy

The datasets have different roles and are not numerically interchangeable.

| Dataset / source | Role | Intended evidence |
| --- | --- | --- |
| LFW | sanity / reproduction | basic replay of the frozen backbone |
| CFP-FP | difficult reproduction | frontal-profile variation |
| AgeDB-30 | difficult reproduction | age-gap variation |
| CALFW | difficult reproduction | cross-age challenge |
| CPLFW | difficult reproduction | cross-pose challenge |
| IJB-C | preferred low-FMR primary qualification | official template-based 1:1 verification, only if lawful/replayable access is demonstrated |
| NIST FRTE 1:1 | external-validity / methodological reference | current sequestered NIST evaluation context; not a local replacement dataset |

Official folds/templates/protocols are preserved. The study must also freeze an identity/image/near-duplicate overlap audit design before evaluation data are opened.

## 5. Gate A — qualify the raw 512D substrate

Gate A is conjunctive.

### A0 — provenance and pipeline integrity

Required: exact checkpoint bytes and hash, reviewed usage terms, deterministic preprocessing, official protocols, durable failure accounting and no outcome-driven tuning.

### A1 — LFW sanity

- reference: 99.82% accuracy;
- minimum: 99.62%.

### A2 — difficult reproduction

| Benchmark | Reference | Minimum |
| --- | ---: | ---: |
| CFP-FP | 99.26% | 98.96% |
| CPLFW | 94.57% | 94.27% |
| CALFW | 96.12% | 95.82% |
| AgeDB-30 | 98.00% | 97.70% |

### A3 — low-FMR primary endpoint

If IJB-C is lawfully and reproducibly available under its official 1:1 protocol:

- reference: TAR 97.66% at FAR=1e-4;
- equivalent reference FNMR: 2.34% at FMR=1e-4;
- minimum TAR: 97.16%;
- equivalent maximum FNMR: 2.84%.

If IJB-C is unavailable, the gate remains **INDETERMINATE** until a separate pre-outcome protocol amendment freezes a public/replayable low-FMR replacement, its own reference value and its own numeric gate. NIST FRTE remains external context and is not substituted as local data.

Gate semantics:

- **PASS:** A0+A1+A2+A3 all pass;
- **FAIL:** A0 is valid but a frozen numeric criterion fails;
- **INDETERMINATE:** provenance, rights, access, protocol or execution evidence is incomplete.

## 6. Verification metrics

The study distinguishes operating-point metrics from threshold-aggregated diagnostics.

- **FMR/FAR:** false matches among impostor attempts at a threshold.
- **FNMR/FRR:** false non-matches among genuine attempts at a threshold.
- **TAR/TMR:** genuine acceptance rate; under matching semantics `FNMR = 1 - TAR`.
- **ROC/DET:** error trade-off across thresholds.
- **EER:** descriptive operating point where false-match and false-non-match rates coincide.
- **AUC:** descriptive threshold-aggregated ranking summary.

ROC/DET/EER/AUC may diagnose behaviour but cannot post hoc replace a failed frozen Gate A operating-point criterion.

## 7. Study 1B algorithm/control catalog

Study 1B remains blocked until Study 1A PASS and a separate explicit GO.

### Raw512

The L2-normalized AdaFace 512D embedding, with no learned projection and no artificial seed variation.

### Random128

A seeded Gaussian 512→128 projection with declared variance scaling followed by L2 normalization. It controls for dimensionality reduction without data-driven learning.

### PCA128

A linear PCA projection fit only on authorized TRAIN data, never on validation or qualification TEST. It is the principal unsupervised compression control.

### Siamese128

A shared supervised 512→128 metric projection trained on authorized TRAIN pair supervision only. The current programme descends from Study 0's linear contrastive-loss projection; any change to loss/training semantics must be frozen before Study 1B outcomes. Siamese is a candidate, not the method that must win.

## 8. Primary compression estimand

For candidate route `m`, raw reference `b` and target false-match rate `alpha`:

`Delta_FNMR(m, alpha) = FNMR_m(alpha) - FNMR_b(alpha)`.

The later non-inferiority question is whether the candidate degradation remains below a preregistered margin `delta` under a frozen one-sided uncertainty procedure and method-level seed rule. Study 0 used `alpha=0.01` and `delta=0.03`; Study 1 must justify reuse or change before outcome inspection.

`NOT_DEMONSTRATED` remains distinct from universal inferiority.

## 9. Dependence-aware uncertainty

Verification pair rows are not necessarily independent because the same identity or template may appear in several genuine or impostor trials. Study 0 demonstrated that naive pair-level resampling can understate uncertainty.

Study 1 therefore requires uncertainty to follow the benchmark's identity/template dependence structure:

- sampling units justified at identity/template/capture level;
- paired raw/candidate resampling draws;
- model/projection seeds separated from bootstrap Monte-Carlo seeds;
- no interpretation of bootstrap replicate count as independent sample size;
- frozen degeneracy and low-FMR threshold handling;
- revalidation if the Study 1 trial graph materially differs from Study 0.

## 10. Progressive evidence

If Study 1B is later authorized:

- **Stage A screening:** non-claim-bearing, SCREEN data, seeds [11,29], bounded compute, no qualification TEST, only CONTINUE/STOP/REDIRECT;
- **Stage B qualification:** claim-bearing, seeds [11,29,47,71,101], untouched TEST, dependence-aware uncertainty, multiplicity policy and independent review.

Screening evidence cannot be reused as if it had remained untouched qualification evidence.

## 11. Outcome-bearing execution boundary

A run is outcome-bearing when its output can influence a scientific claim, estimand, gate, belief, comparison or decision.

Examples normally **non-outcome-bearing** here: checkpoint hashing, licence review, SBOM, synthetic smoke inference, CPU throughput, memory/sharding measurement, worker-count equivalence and interruption/resume equivalence.

Examples **outcome-bearing**: benchmark accuracy, FNMR/FMR, TAR/FAR, ROC/DET/EER/AUC, scientific loss curves, ablations and intermediate metrics that could redirect the study.

The explicit human GO of 2026-08-24 satisfies Study 1A authority, but execution remains fail-closed until all mandatory pre-execution blockers are closed with recoverable evidence.

## 12. Execution and reproducibility

The implementation is designed for a standard GitHub-hosted 4-vCPU/16-GB class and decomposed into restartable deterministic shards. Required engineering evidence includes:

- exact checkpoint and dataset-manifest hashes;
- deterministic preprocessing and shard identity;
- parent-owned append-only progress logging;
- 1-worker versus multi-worker digest equivalence;
- forced interruption/restart equivalence;
- aggregation rejection of mixed provenance;
- generated CycloneDX SBOM from the actual execution environment;
- dependency, secret and static-security checks;
- no public persistence of restricted biometric data or credentials.

Engineering failure and scientific failure remain separate categories.

## 13. Pedagogical capitalization

The study explicitly exports reusable concepts to Diderot MMALS/ML: outcome-bearing execution; biometric verification operating points; non-inferiority; dependency-aware resampling; backbone qualification; dataset-role separation; scientific versus understanding gates; and checkpoint/model/data provenance.

This pedagogical layer explains the study. It is not scientific authority and cannot release a gate.

## 14. Current blockers

At this pre-execution version, the remaining release blockers include:

- materialized/frozen checkpoint SHA-256;
- checkpoint/training-data rights disposition;
- lawful/replayable IJB-C or a pre-reviewed low-FMR replacement;
- overlap/near-duplicate audit design;
- frozen compute environment and budget;
- worker-count and interruption/resume equivalence evidence;
- final green assurance on the execution head.

No Study 1A scientific result is reported in this document.

## References / authoritative project artifacts

- `protocol/studies/study_1_face_backbone.yaml`
- `protocol/studies/STUDY1_BACKBONE_ACCEPTANCE_GATE.md`
- `protocol/studies/STUDY1_EVALUATION_METHODS_AND_DATA_CATALOG.md`
- `protocol/studies/STUDY1_EXECUTION_ARCHITECTURE_AND_SBOM.md`
- `protocol/authorizations/study_1a_execution_go_2026-08-24.yaml`
- `harness-adoption.yaml`
- AdaFace upstream commit `c60eaa786a42c03444f3df7096dbaf9d57ae010d`
- NIST Face Challenges / FRTE 1:1 references recorded in the protocol
