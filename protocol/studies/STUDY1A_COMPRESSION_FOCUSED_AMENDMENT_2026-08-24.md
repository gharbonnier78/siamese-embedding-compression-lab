# Study 1A — Compression-focused preregistration amendment

Status: `PROPOSED_PREOUTCOME_AMENDMENT_REVIEW_REQUIRED`

Date: 2026-08-24

## 1. Reason for the amendment

The purpose of Study 1 is not to qualify a face-recognition product against the strongest available operational benchmark. The scientific question is narrower:

> Starting from a credible face-specific frozen 512D embedding, does a learned Siamese 512D -> 128D projection preserve verification performance better than simple compression controls such as Gaussian random projection and PCA, and how does each compressed route compare with the uncompressed 512D reference?

Study 0 used an ImageNet ResNet representation that was not sufficiently face-specific for this comparison to be maximally informative. Study 1A therefore exists only to establish that the replacement AdaFace R100 / IR101 512D representation is a credible and correctly replayed substrate for the compression experiment.

The previous Gate A made lawful local low-FMR IJB-C replay a mandatory prerequisite. That requirement is scientifically valuable for a biometric qualification programme, but disproportionate to the bounded compression question because IJB-C distribution is discontinued and FRTE uses sequestered NIST data rather than a locally replayable benchmark.

No Study 1A scientific benchmark outcome has been opened when this amendment is proposed.

## 2. What remains frozen

This amendment does **not** change:

- the AdaFace R100 / IR101 / WebFace12M 512D backbone choice;
- exact artifact identity and hash/provenance recording;
- the frozen preprocessing/input contract;
- RGB/BGR equivalence evidence and representation-convention controls;
- official benchmark protocol use;
- durable failure/exclusion accounting;
- prohibition on outcome-driven preprocessing changes;
- the Study 1B comparison routes: raw512, random128, PCA128, Siamese128;
- matched source embeddings/splits/trials across routes;
- identity/dependence-aware uncertainty;
- the requirement for a separate Study 1B GO after Study 1A acceptance.

## 3. Revised bounded role of Study 1A

Study 1A becomes a **substrate sanity qualification**, not a production biometric qualification.

Its only decision is:

> Is this exact frozen AdaFace 512D pipeline reproduced credibly enough that differences observed later between raw512, random128, PCA128 and Siamese128 can reasonably be attributed to the compression routes rather than to an obviously broken or inappropriate face representation pipeline?

## 4. Mandatory pre-outcome controls

Before any qualification benchmark outcome is opened, the following engineering/provenance controls remain mandatory:

1. exact model artifact SHA-256, source and architecture fingerprint recorded;
2. preprocessing/input contract frozen, including orientation/decoding, five-point alignment, 112x112 shape, color convention, normalization and L2 normalization;
3. RGB/BGR sentinel/equivalence check tied to the exact model artifact;
4. **preprocessing fingerprint** on non-scientific fixtures;
5. **deterministic embedding replay** on non-scientific/synthetic fixtures: same input + same model + same pipeline => same serialized 512D embedding digest within the declared deterministic environment;
6. **single-worker versus multi-worker equivalence** for stable fixture outputs/digests when multiprocessing is used;
7. **interruption/restart equivalence** for resumable sharded execution when that path is used;
8. dataset manifest/version/protocol identity and explicit failure/exclusion semantics;
9. overlap/duplicate/near-duplicate audit design frozen before outcomes, with identity-aware handling where identifiers permit it;
10. environment, dependencies and SBOM/replay metadata captured according to the POC engineering-care profile.

These are pre-execution qualification controls. They are engineering/provenance evidence, not scientific benchmark outcomes and cannot by themselves release Study 1A.

## 5. Revised Study 1A scientific sanity gate

Subject to independent review of this amendment, the active numeric sanity gate becomes:

### A0 — pipeline integrity

Same intent as the existing Gate A A0, interpreted proportionately to the research POC. Exact artifact, frozen preprocessing, official protocol, failure accounting and no outcome-driven tuning remain mandatory.

### A1 — LFW reproduction sanity

Reference: 99.82% accuracy.

Frozen minimum: **99.62%**.

LFW alone cannot release Study 1A.

### A2 — difficult face-verification reproduction

All four already-frozen public benchmark checks are retained:

| Benchmark | Published reference | Frozen minimum |
| --- | ---: | ---: |
| CFP-FP | 99.26% | 98.96% |
| CPLFW | 94.57% | 94.27% |
| CALFW | 96.12% | 95.82% |
| AgeDB-30 | 98.00% | 97.70% |

These values are unchanged from the prior preregistration. The amendment removes no already-frozen accessible reproduction threshold.

### A3 — low-FMR context / extension, no longer mandatory for compression progression

IJB-C and FRTE remain scientifically useful external context for low-FMR operation, but they are **not mandatory release conditions** for the compression-focused Study 1A.

- IJB-C may be added later only if a lawful/replayable copy and official protocol metadata are available.
- FRTE remains a sequestered external-validity reference, not a local GitHub benchmark.
- WebFace260M or any other local low-FMR benchmark requires its own preregistered endpoint before its results can support a claim.
- No low-FMR result may be used post hoc to alter A1/A2 or rescue a failed sanity gate.

Low-FMR evidence may enrich external validity later; absence of such evidence does not block the bounded compression comparison.

## 6. Revised Study 1A decision semantics

If this amendment receives the required independent pre-outcome review:

- `PASS`: A0 + A1 + all A2 thresholds pass and mandatory pre-outcome controls are satisfied. The exact AdaFace raw512 representation is accepted **only as the substrate for the planned compression comparison**.
- `FAIL`: A0 is valid but one or more A1/A2 frozen thresholds fail. Stop and diagnose; do not run compression to rescue the substrate.
- `INDETERMINATE`: artifact/pipeline/protocol/replay evidence required by this bounded qualification is incomplete or invalid.

A PASS does not establish production readiness, fairness, PAD/security, regulatory conformity, 1:N quality, low-FMR operational fitness or SOTA performance.

## 7. Rights/provenance boundary

The study must record the exact model-card/repository licence metadata and upstream provenance used. The study does not redistribute model weights or training data and is scoped to research/POC evaluation.

Uncertainty about the upstream training dataset's broader commercial/redistribution terms remains a documented legal/provenance limitation and must not be silently generalized into a claim of unrestricted commercial rights. It does not by itself answer the scientific compression question. Any production/commercial reuse requires a separate rights review.

## 8. Activation rule

This amendment is proposed before Study 1A benchmark outcomes are opened. It becomes active only after independent review confirms that:

- the compression-focused question is represented faithfully;
- the reduced scope does not create outcome-driven threshold changes;
- A1/A2 thresholds remain exactly frozen;
- mandatory preprocessing/replay/overlap controls remain fail-closed;
- low-FMR evidence is correctly demoted to external-validity/extension status rather than silently discarded.

Until that review is recorded, the existing Gate A remains the formal active gate.
