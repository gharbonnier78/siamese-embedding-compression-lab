# Study 1 — Evaluation methods, data sources and algorithm catalog

Status: `PREEXECUTION_DOCUMENTATION`

This document is a human-readable companion to the machine-readable Study 1 protocol. It consolidates the evaluation protocol, the roles of the different data sources, the frozen model/preprocessing chain, the metrics, the decision gates, and the algorithms that may later be used in Study 1B. It is documentation only: it does not widen any scientific authorization, alter a gate, or open any benchmark outcome.

Authoritative local contracts remain:

- `protocol/studies/study_1_face_backbone.yaml`;
- `protocol/studies/STUDY1_BACKBONE_ACCEPTANCE_GATE.md`;
- `protocol/studies/STUDY1_EXECUTION_ARCHITECTURE_AND_SBOM.md`;
- `protocol/studies/STUDY1_DOUBLE_REVIEW_REQUEST.md`;
- `protocol/authorizations/study_1a_execution_go_2026-08-24.yaml`.

Pinned methodological dependency: `scientific-research-harness` commit `3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98` through `harness-adoption.yaml`.

## 1. Why Study 1 exists

Study 0 closed with a valid negative result under a frozen ImageNet ResNet-18 representation and corrected subject-level uncertainty: the tested 128D random, PCA and Siamese routes did not demonstrate the preregistered non-inferiority claim. The largest scientific limitation was that the source representation itself was not a modern face-specific embedding.

Study 1 therefore separates two questions that must not be conflated:

1. **Study 1A — backbone qualification:** can one exact frozen face-specific 512D representation reproduce credible verification performance closely enough to be used as a substrate?
2. **Study 1B — compression comparison:** only if Study 1A passes and a separate GO is issued, what is the decision-relevant degradation, if any, from compressing that qualified 512D representation to 128D under matched controls?

A failure in Study 1A is not evidence about 512D-to-128D compression. It means the measuring substrate or its replay has not been qualified.

## 2. End-to-end evaluation pipeline

The intended logical pipeline is:

```text
model provenance and exact checkpoint
        |
        v
face detection / five-point alignment
        |
        v
112x112 BGR normalized crop
        |
        v
frozen AdaFace R100 / ir_101 inference
        |
        v
L2-normalized 512D embedding
        |
        +-------------------- Study 1A --------------------+
        |                                                   |
        v                                                   v
benchmark protocol                                   verification scores
        |                                                   |
        +-----------------------> Gate A <------------------+
                                    |
                          PASS + separate Study 1B GO
                                    |
                                    v
                raw512 / random128 / PCA128 / Siamese128
                                    |
                                    v
                      matched verification comparison
                                    |
                                    v
                     dependence-aware uncertainty
```

The pipeline must remain replayable by content hashes and immutable protocol identifiers. Failures of detection/alignment, exclusions, shard errors and provenance mismatches are evidence and must not be silently dropped.

## 3. Frozen Study 1A model and preprocessing

### 3.1 Backbone

The Study 1A measuring substrate is frozen as:

| Element | Frozen choice |
| --- | --- |
| Method | AdaFace |
| Architecture | R100 / official `ir_101` implementation |
| Embedding dimension | 512 |
| Released training corpus | WebFace12M |
| Upstream repository | `mk-minchul/AdaFace` |
| Upstream code/protocol commit | `c60eaa786a42c03444f3df7096dbaf9d57ae010d` |
| Checkpoint identity | R100 / WebFace12M |
| Checkpoint locator | Google Drive file id `1dswnavflETcnAuplZj1IOKKP0eM8ITgT` |
| Exact bytes | must be SHA-256 materialized before scientific outcome access |
| Face-backbone training in Study 1A | prohibited; pretrained inference only |

The repository MIT licence applies to source code. Checkpoint/data usage rights are treated separately and remain a pre-execution blocker until a defensible disposition is recorded.

### 3.2 Preprocessing

The frozen preprocessing contract follows the same AdaFace commit:

- reference alignment entry point: `face_alignment/align.py`;
- bundled MTCNN alignment path under `face_alignment/mtcnn_pytorch/`;
- five-point landmark transform;
- crop shape: `112 x 112 x 3`;
- channel order: BGR;
- normalization: `(pixel / 255 - 0.5) / 0.5`;
- model loader: `net.build_model('ir_101')`;
- frozen weights in `eval()` / inference mode;
- downstream L2 normalization of the 512D embedding;
- comparison by cosine similarity or equivalent normalized-Euclidean ordering, as frozen by the protocol implementation.

A local adapter is permitted only if bounded equivalence to the pinned preprocessing is demonstrated before qualification outcomes are opened.

## 4. Data-source hierarchy and protocol roles

The datasets are not interchangeable. Each has a declared role and must keep its own official protocol semantics.

| Source | Study role | Primary use | Important boundary |
| --- | --- | --- | --- |
| **LFW** | sanity / reproduction | basic verification replay of the frozen backbone | cannot release Gate A alone |
| **CFP-FP** | difficult reproduction | frontal-profile variation | use official protocol; descriptive differences do not change frozen gate |
| **AgeDB-30** | difficult reproduction | age-gap verification | official protocol only |
| **CALFW** | difficult reproduction | cross-age LFW-derived challenge | kept distinct from LFW despite lineage |
| **CPLFW** | difficult reproduction | cross-pose LFW-derived challenge | kept distinct from LFW despite lineage |
| **IJB-C** | preferred low-FMR primary qualification | template-based 1:1 verification at low FAR/FMR | usable only if a lawful, reproducible copy and official protocol metadata are demonstrated |
| **NIST FRTE 1:1** | external-validity / methodological reference | contemporary operational reference for FNMR at fixed FMR | sequestered evaluation; not a downloadable local Gate-A substitute |

### 4.1 Why several datasets are needed

A single high LFW score does not establish that the implementation is credible under pose, age, template aggregation or low-FMR operating conditions. The hierarchy intentionally asks different datasets to stress different aspects while keeping their protocols separate.

### 4.2 Overlap and leakage control

Before outcome-bearing execution, the study must freeze an overlap/near-duplicate audit design across all local data roles. At minimum the evidence pack should make recoverable, where legally and practically possible:

- source and version identity;
- protocol role;
- identity identifiers or privacy-preserving stable ids;
- image/capture ids;
- template membership where relevant;
- genuine and impostor trial construction;
- known or suspected identity/image overlap;
- near-duplicate detection method and limitations;
- exclusions and their reasons.

The audit is not allowed to inspect scientific metrics to decide which records to retain.

## 5. Gate A: backbone reproduction decision

Gate A is conjunctive. It is intended to answer only whether the exact frozen 512D backbone replay is credible enough to become the Study 1B substrate.

### A0 — provenance and pipeline integrity

Required before numeric interpretation:

- exact checkpoint source and SHA-256;
- reviewed code/checkpoint/data usage terms;
- pinned or equivalence-proven preprocessing;
- official benchmark protocols;
- durable failure/exclusion accounting;
- no qualification outcome used for tuning.

A0 failure makes the result `INDETERMINATE`, not a scientific failure of AdaFace.

### A1 — LFW sanity criterion

- published reference: `99.82%` accuracy;
- frozen minimum: `99.62%`.

### A2 — difficult reproduction criteria

| Benchmark | Published reference | Frozen minimum |
| --- | ---: | ---: |
| CFP-FP | 99.26% | 98.96% |
| CPLFW | 94.57% | 94.27% |
| CALFW | 96.12% | 95.82% |
| AgeDB-30 | 98.00% | 97.70% |

### A3 — low-FMR qualification when lawfully replayable

Preferred source: IJB-C official 1:1 protocol.

- reference: `TAR = 97.66% @ FAR = 1e-4`;
- equivalent reference: `FNMR = 2.34% @ FMR = 1e-4`;
- frozen minimum TAR: `97.16%`;
- equivalent maximum FNMR: `2.84%`.

If lawful/reproducible IJB-C access cannot be demonstrated, A3 stays `INDETERMINATE`. A replacement requires a separate preregistration amendment, its own published/replayable reference, its own numeric criterion, and independent review before any replacement outcome is inspected. The IJB-C threshold must never be transplanted to another dataset simply because the numerical FMR is the same.

### Gate A semantics

- `PASS`: A0+A1+A2+A3 all pass; Study 1B may be prepared but remains separately authorized.
- `FAIL`: A0 is valid and one or more frozen numerical criteria fail; stop and diagnose.
- `INDETERMINATE`: provenance, rights, access, protocol or execution evidence is incomplete or invalid.

## 6. Verification metrics and operating-point semantics

Study 1 distinguishes threshold-free summaries from decision-relevant operating points.

### 6.1 FMR / FAR

For impostor comparisons, FMR/FAR is the proportion of false accepts at a chosen threshold. A low-FMR operating point asks the algorithm to remain selective in a regime where false matches are rare.

### 6.2 FNMR / FRR and TAR / TMR

For genuine comparisons:

```text
FNMR = 1 - TAR
```

when the benchmark uses the corresponding verification semantics. Gate A3 therefore expresses the same reproduction tolerance as either a minimum TAR or a maximum FNMR.

### 6.3 ROC / DET / EER / AUC

These remain descriptive unless explicitly promoted by a preregistered claim:

- ROC: trade-off curve across thresholds;
- DET: error trade-off in a scale useful for verification comparison;
- EER: descriptive point where false-match and false-non-match rates are equal;
- AUC: threshold-aggregated ranking summary.

They may help diagnose a result but cannot post hoc replace a failed frozen operating-point criterion.

## 7. Study 1B algorithm catalog — blocked until Gate A PASS + separate GO

Study 1B compares the same qualified source embeddings under matched 512D/128D routes.

### 7.1 Raw 512D reference

- frozen L2-normalized AdaFace embedding;
- no projection;
- no artificial seed variability;
- serves as reference for candidate differences.

### 7.2 Gaussian random projection 512D -> 128D

Purpose: dimensionality-control baseline with no data-driven compression learning.

Frozen design intent:

- seeded Gaussian projection;
- variance scaled as declared in the machine-readable protocol (`1/d` convention);
- L2 normalization after projection;
- seed lineage separated from bootstrap randomness.

### 7.3 PCA 512D -> 128D

Purpose: strong unsupervised linear compression control.

Rules:

- fit only on authorized TRAIN data;
- never fit on validation/qualification TEST;
- transform the same source 512D embeddings as other routes;
- L2 normalize as declared by the route implementation.

### 7.4 Siamese / metric projection 512D -> 128D

Purpose: test whether pair supervision adds value beyond dimensionality reduction alone.

Current design intent:

- shared linear projection from 512D to 128D;
- pair-supervised metric learning on authorized TRAIN only;
- matched source embeddings and data roles;
- frozen training budget/seeds before claim-bearing execution;
- candidate status only: the protocol does not assume that Siamese must win.

Study 0 used contrastive loss for this route. Study 1 must preserve or amend that training rule before Study 1B outcomes; it may not choose a new loss because the qualification result looks inconvenient.

## 8. Study 1B primary estimand and non-inferiority logic

For candidate route `m`, raw reference `b`, and target false-match rate `alpha`:

```text
Delta_FNMR(m, alpha) = FNMR_m(alpha) - FNMR_b(alpha)
```

The scientific question is whether the candidate's degradation stays below a preregistered non-inferiority margin `delta` with the frozen one-sided uncertainty procedure and method-level seed rule.

Study 0 used `alpha = 0.01` and `delta = 0.03`; Study 1 must justify reuse or change rather than inheriting them automatically.

Failure to demonstrate non-inferiority means `NOT_DEMONSTRATED`. It does not automatically establish that compression is universally inferior.

## 9. Dependence-aware uncertainty

Verification trials are not necessarily independent rows. Multiple genuine or impostor trials can share one identity or template. Study 0 showed why naive pair-row bootstrap can understate uncertainty when repeated subjects are treated as independent sampling units.

Study 1 therefore requires an uncertainty method that follows the benchmark's identity/template dependence structure. The exact resampling implementation may differ across benchmark graph structures, but the following principles are preserved:

- primary independent units are identities/templates/captures as justified by the protocol, not raw pair count;
- raw and candidate routes use the same resampling draw for paired differences;
- bootstrap Monte-Carlo seeds are distinct from model/projection seeds;
- more bootstrap replicates improve numerical approximation but do not create more independent subjects;
- degeneracy and low-FMR threshold handling are frozen before outcomes;
- if the new trial graph differs materially from Study 0, estimator behaviour must be revalidated rather than assumed transferable.

## 10. Progressive evidence and data-access discipline

Study 1B, if later authorized, separates:

- **Stage A screening:** non-claim-bearing; declared SCREEN data, limited seeds `[11,29]`, bounded compute, no qualification TEST access, decisions limited to `CONTINUE`, `STOP`, `REDIRECT`;
- **Stage B qualification:** claim-bearing; full declared seeds `[11,29,47,71,101]`, untouched qualification TEST, dependence-aware uncertainty, multiplicity policy and independent result review.

Screening evidence may not be relabelled as qualification evidence.

## 11. Outcome-bearing vs non-outcome-bearing execution

This distinction is part of the scientific control surface.

Usually non-outcome-bearing:

- checkpoint download and SHA-256;
- licence/provenance review;
- synthetic smoke inference;
- SBOM, dependency and secret review;
- CPU throughput, memory and sharding measurements;
- worker-count equivalence;
- forced interruption/resume equivalence.

Outcome-bearing:

- benchmark accuracy, FNMR/FMR, TAR/FAR, ROC/DET/EER/AUC;
- scientific loss curves used for model selection;
- ablations or intermediate metrics that could redirect the scientific protocol;
- any protected benchmark result capable of changing a claim, gate, threshold, model or interpretation.

The human GO recorded on 2026-08-24 satisfies the Study 1A authority requirement, but activation remains fail-closed until the listed pre-execution blockers are closed with recoverable evidence.

## 12. Execution, resilience and provenance

The Study 1 engineering contract requires:

- deterministic shard keys and atomic manifests;
- checkpoint/model hash, preprocessing contract id and dataset-manifest hash on every scientific shard;
- parent-owned progress reporting with append-only `progress.jsonl`;
- no scientific identity derived from worker number;
- bounded `workers=1` versus multi-worker digest equivalence;
- forced interruption/restart equivalence;
- aggregation refusal on mixed provenance;
- machine-readable SBOM from the actual environment;
- public artifacts that exclude restricted biometric source data and secrets.

Infrastructure failure must remain infrastructure failure; it must never be converted into a scientific negative result.

## 13. Pedagogical capitalization map

The following concepts are sufficiently general and important to be capitalized in Diderot MMALS/ML rather than left only inside one study:

1. outcome-bearing vs non-outcome-bearing execution;
2. verification operating point: FMR/FNMR and TAR/FAR;
3. non-inferiority: reference, margin, estimand and one-sided decision;
4. dependency-aware resampling: why repeated identities invalidate naive pair independence;
5. backbone qualification before downstream compression/ablation;
6. dataset-role separation: TRAIN / VALIDATION / SCREEN / untouched TEST / external-validity reference;
7. scientific gate versus understanding gate;
8. checkpoint provenance: source locator, bytes hash, code licence and model/data rights are different objects.

Diderot explanations are pedagogical instances. They do not replace this protocol or authorize claims.

## 14. Publication/versioning plan

Study 0's reviewed paper remains frozen as `v0.2.3` on `main`; historical PDFs must never be overwritten.

The move from closed Study 0 to a new face-specific Study 1 is a substantial programme transition. The recommended reader-facing continuation is therefore a **v0.3 pre-execution protocol/methods supplement**, not a silent rewrite of the v0.2.x Study 0 paper. Its first edition should contain:

- Study 0 closure in one compact section;
- why Study 1 changes the substrate;
- the complete model/preprocessing provenance chain;
- the dataset hierarchy and protocol roles;
- Gate A and its decision semantics;
- the Study 1B algorithm/control catalog without claiming execution;
- uncertainty and low-FMR methodology;
- execution/replay architecture;
- explicit open blockers and authorization state;
- links to Diderot pedagogical concepts.

Once Study 1A produces reviewed evidence, the same v0.3 line can be extended with an append-only results section or a later versioned paper artifact. Protocol text and scientific outcomes must remain distinguishable.

## 15. Current state at creation of this catalog

This document intentionally contains no new Study 1 scientific result. At creation time:

- Study 0 remains closed;
- Study 1A human GO has been recorded;
- checkpoint identity materialization is a non-outcome-bearing pre-execution activity;
- checkpoint/data rights, low-FMR lawful replay or replacement, overlap-audit design, frozen execution environment, replay-equivalence evidence and final assurance remain release conditions;
- Study 1B and representation geometry remain unauthorized.
