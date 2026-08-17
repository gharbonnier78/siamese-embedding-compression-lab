# Future-study concept note — Explainable distribution shift with WaX

> **Status:** `CONCEPT_NOTE_NOT_PREREGISTERED_NOT_EXECUTED`  
> **Candidate role:** future representativity and robustness diagnostic; study placement TBD  
> **Claim level:** none  
> **Historical boundary:** this note does not modify Study 0, resolve `E-STAT-001`,
> reopen G2, read historical Study 0 scores, or start Study 1 or any later study.

## Decision this study should support

Determine whether a biometric representation is stable across declared populations,
datasets and acquisition regimes, and identify which samples, features or latent subspaces
drive any observed distribution difference.

The intended decision is not merely whether two distributions differ. It is whether the
observed difference is:

- larger than expected under a matched same-domain negative control;
- attributable to a stable and reproducible structure rather than sampling noise;
- associated with decision-relevant degradation in verification or identification;
- reduced, preserved or amplified by a compression route;
- sufficiently understood to justify data collection, model revision, threshold review or
  an explicit residual-risk statement.

WaX is therefore proposed as an **explanatory diagnostic layer**, not as a fifth Study 0
route, a replacement for the biometric endpoints, or evidence of causality.

## Source and scientific status

Primary source:

> Philip Naumann, Jacob Kauffmann and Grégoire Montavon, “Wasserstein Distances Made
> Explainable: Insights Into Dataset Shifts and Transport Phenomena,” *IEEE Transactions on
> Pattern Analysis and Machine Intelligence*, vol. 48, no. 6, pp. 6393–6406, June 2026.
> DOI: [10.1109/TPAMI.2026.3656947](https://doi.org/10.1109/TPAMI.2026.3656947).
> Open manuscript: [arXiv:2505.06123v2](https://arxiv.org/abs/2505.06123).

The paper introduces WaX, a post-hoc method that explains a precomputed Wasserstein
distance, and U-WaX, an extension that attributes the common Euclidean `W2` formulation to
orthogonal latent subspaces. It is a recent peer-reviewed research contribution, not an
established foundational method with the historical maturity of PCA.

## What WaX explains

For empirical source and target distributions, a Wasserstein distance represents the
minimum expected cost of coupling source samples `x_k` with target samples `y_l`. The
optimal coupling is denoted `gamma*`.

WaX:

1. solves or receives the optimal-transport problem and fixes `gamma*`;
2. rewrites the selected Wasserstein calculation as an equivalent short computational
   graph;
3. propagates the scalar distance backward using LRP-inspired rules;
4. returns relevance contributions for coupled instance pairs and input features.

Its central accounting property is conservation:

```text
sum_i R_i = sum_(k,l) R_kl = W_p
```

This makes the explanation a decomposition of the selected distance. It does **not** make
the explanation a decomposition of ground-truth causal change. Because `gamma*` is fixed
during attribution, WaX explains the chosen, already-fitted transport model.

The method supports several `p`-Wasserstein and Minkowski ground-cost specifications, as
well as Sinkhorn-regularized transport. These choices are part of the model and must be
frozen and sensitivity-tested; they are not interchangeable presentation settings.

## Relationship to PCA and the existing compression routes

| Method | Question answered | Object optimized | Role in this programme |
|---|---|---|---|
| PCA | Where does one dataset vary most? | covariance / retained variance | unsupervised 512→128 compression control |
| random projection | Is generic dimensionality reduction sufficient? | seeded geometry-preserving map | non-learned 512→128 control |
| Siamese projection | Which 128D map improves a pair-supervised objective? | contrastive training objective | learned compression candidate |
| WaX | What contributes to a declared distribution distance? | attribution of fixed transport cost | explanatory diagnostic |
| U-WaX | Which orthogonal directions carry distinct sub-shifts? | transport-relevant subspaces | shift-disentanglement diagnostic |

For the special `W2`, Euclidean, one-subspace, `r=2` case, U-WaX obtains a direction from
the eigensystem of a transport-displacement matrix of the form:

```text
M_transport = sum_(k,l) gamma*_kl (x_k - y_l)(x_k - y_l)^T
```

This resembles PCA computationally, but it answers a different question. PCA analyzes the
variance of samples around their own center. U-WaX analyzes directions of coupled movement
between source and target distributions. A direction with high variance in both domains
may dominate PCA and be irrelevant to U-WaX; a lower-variance direction with systematic
domain displacement may do the opposite.

No WaX-derived subspace is automatically a good compression space. Removing a
domain-specific direction may improve transfer, but it may also remove identity evidence.
Any feature pruning or new projection inspired by WaX is a separate intervention requiring
its own TRAIN-only fit, preregistration and biometric evaluation.

## Direct relevance to face embeddings

The source paper includes a qualitative comparison of 10,000 CelebA images and 10,000 LFW
images. It applies U-WaX to normalized CLIP representations and reports a dominant
demographic difference together with more localized sub-shifts involving eyewear,
multi-person images and visual context.

This use case makes the paper directly relevant to the present programme, but its evidence
cannot be transferred to this repository:

- CLIP is a multimodal semantic representation, not the frozen ResNet-18 representation
  or a biometric-grade face embedding;
- text alignment gives CLIP subspaces a naming mechanism that ordinary biometric
  coordinates do not have;
- CelebA-versus-LFW differences do not establish the failure mechanism of a verification
  system;
- qualitative inspection of highly relevant images is hypothesis generation, not a
  demographic, fairness or causal conclusion.

For biometric embeddings, subspaces should be interpreted through predeclared metadata,
controlled perturbations or validated concept probes, never named solely by visual
inspection of a few extreme samples.

## Candidate research questions

1. **Representation shift:** how large is the source-to-target shift within each frozen
   representation route: `raw512`, `random128`, `pca128` and `siamese128`?
2. **Compression effect:** relative to a matched same-domain null, does a compression route
   attenuate, preserve or amplify cross-domain shift?
3. **Shift anatomy:** which coupled samples, declared variables and stable latent subspaces
   contribute most to the shift?
4. **Nuisance versus identity:** do relevant subspaces correspond to pose, illumination,
   blur, occlusion, capture source, age interval or other authorized factors, and do they
   retain or damage identity discrimination?
5. **Decision linkage:** are the shift magnitude and its attributions associated with
   changes in FMR, FNMR, calibration, threshold transfer, rank or top-k performance?
6. **Actionability:** does the explanation lead to a falsifiable data, model or evaluation
   intervention that improves a preregistered endpoint on untouched data?

## Candidate comparison design

### Domain pairs

The exact pairs must be frozen later. Candidate regimes are:

- two identity-aware random halves of the same authorized population as a negative
  control;
- development versus external evaluation dataset;
- enrollment versus probe captures;
- declared sensor, site, illumination, pose, occlusion, quality or time regimes;
- authorized age and demographic strata when sample size, consent, governance and the
  intended decision make such analysis admissible;
- controlled synthetic perturbations with known direction and strength for method
  validation only.

Global LFW split comparisons require special caution. Identity-disjoint splits can make
identity composition itself dominate the transport. LFW also lacks the scale and capture
metadata needed for industrial low-FMR or broad representativity claims. A confirmatory
study therefore requires independently justified, authorized data.

### Representation spaces

Run the source-target analysis separately in each frozen space:

```text
raw512:     source_raw512     versus target_raw512
random128:  source_random128  versus target_random128
pca128:     source_pca128     versus target_pca128
siamese128: source_siamese128 versus target_siamese128
```

Standard Wasserstein distances in 512D and 128D do not live in the same ground space and
must not be directly ranked as if their values had identical meaning. A candidate
dimensionless comparison is a null-normalized shift index:

```text
rho_route = W(source, target) / median W(matched same-domain split A, split B)
```

The null-generation rule, number of repetitions and uncertainty interval must be
preregistered. This ratio is only a candidate estimand until its finite-sample behavior and
coverage are validated. Direct comparison across unregistered spaces would require a
separately justified method such as Gromov-Wasserstein; it is out of scope for the first
WaX study.

Score-distribution Wasserstein distances for genuine and impostor scores may be useful as
secondary decision diagnostics. They do not provide a rich feature attribution in one
dimension and cannot replace operating-point metrics.

### Transport specification

Freeze before TEST:

- data normalization and sample weighting;
- exact versus Sinkhorn-regularized transport;
- Wasserstein power `p` and ground norm `q`;
- Sinkhorn regularization and convergence tolerance when applicable;
- subsampling or mini-batch scheme;
- coupling and attribution implementation;
- WaX attribution parameters;
- U-WaX number and dimensionality of subspaces, `r`, optimizer, initialization, stopping
  rule and orthogonalization;
- all seeds, sensitivity analyses and failure handling.

The model choice defines what WaX will explain. Trying several settings on TEST and keeping
the most narratively appealing explanation is prohibited.

## Candidate hypotheses

- **H-WAX-NULL:** matched same-domain controls do not exhibit a reproducible dominant shift
  beyond the preregistered finite-sample envelope.
- **H-WAX-STABILITY:** a claimed feature or subspace is not interpretable unless its
  attribution is stable under identity-aware resampling, transport-solver tolerance and
  every declared initialization.
- **H-WAX-ROBUSTNESS:** no compression route is credited with domain robustness unless its
  null-normalized shift and biometric endpoints jointly satisfy preregistered constraints.
- **H-WAX-LINK:** an association between shift relevance and biometric degradation is
  reported only with an untouched evaluation split and a frozen analysis; it is not
  presumed.
- **H-WAX-CAUSAL-NULL:** WaX attribution alone supports no causal, demographic, fairness or
  operational acceptance claim.

No numerical margin is proposed in this concept note. Margins, operating points,
multiplicity handling and practical cost functions belong to the future preregistration
and require domain justification.

## Endpoints and evidence

### Distribution-shift endpoints

- selected Wasserstein distance with identity-aware uncertainty;
- matched-null distance distribution and candidate `rho_route`;
- paired route contrasts only where their scale and estimand are demonstrated comparable;
- sample-pair, variable and subspace relevance with conservation checks;
- residual relevance outside the retained U-WaX subspaces.

### Explanation-quality endpoints

- conservation error;
- relevance stability under identity-aware bootstrap;
- principal-angle or projection-matrix stability for learned subspaces;
- recovery of predeclared synthetic shifts;
- sensitivity to `p`, `q`, regularization, sample size and solver tolerance;
- relevance-removal/addition tests computed without selecting features on TEST.

### Biometric linkage endpoints

- FMR and FNMR at preregistered operating points;
- validation-frozen threshold transfer;
- EER and ROC AUC as descriptive metrics only;
- score-distribution drift by genuine/impostor class;
- rank and top-k effects only under an active identification protocol;
- subgroup results only when sample support and multiplicity control are adequate.

WaX explanations remain diagnostic evidence. A release or model decision must still be
grounded in biometric performance, uncertainty, representativity and operational context.

## Controls, falsification and stop conditions

1. **Known-shift control:** construct TRAIN/VALIDATION-only or synthetic examples where the
   changed variables and affected samples are known. WaX must recover them within frozen
   tolerances before real-data interpretation.
2. **Matched-null control:** repeat same-domain identity-aware splits. If apparent
   explanations are equally strong under the null, stop interpretive claims.
3. **Route controls:** retain random and TRAIN-only PCA routes. The learned projection is
   not compared only against raw embeddings.
4. **Solver/model sensitivity:** exact and regularized couplings may differ. Materially
   unstable explanations are reported as unresolved.
5. **Initialization stability:** U-WaX uses an optimization procedure for general
   subspaces. Seed-sensitive components are not assigned stable semantic names.
6. **No visual storytelling:** a few extreme images cannot establish a concept. Metadata,
   controlled perturbations or independently validated probes must support interpretation.
7. **No causal overreach:** an attributed feature may be a proxy, correlate or consequence.
   WaX does not identify an intervention or causal graph.
8. **No TEST-guided pruning:** using WaX on TEST to remove features and then reporting
   improved TEST performance is leakage. Any derived intervention returns to TRAIN and is
   evaluated on untouched data.
9. **No cross-dimensional scalar shortcut:** raw512 and projected128 Wasserstein values are
   not directly compared without a validated normalization or cross-space transport model.
10. **No industrial claim from LFW:** its pair count, metadata and FMR resolution remain
    inadequate for operational validation.

Negative, unstable and indeterminate results remain admissible and should be retained.

## Proposed gates

1. **GW0 — implementation fidelity:** deterministic fixtures, coupling replay, attribution
   conservation and reference calculations pass.
2. **GW1 — known-shift recovery:** the frozen method retrieves simulated or controlled
   shifts with adequate sensitivity and false-attribution control.
3. **GW2 — protocol integrity:** domains, routes, transport settings, seeds, interpretation
   rules and multiplicity policy are frozen before TEST.
4. **GW3 — stability and uncertainty:** identity-aware intervals and explanation-stability
   measures pass their validated requirements.
5. **GW4 — biometric linkage:** any robustness claim is supported jointly by distribution
   evidence and preregistered biometric endpoints on untouched data.
6. **GW5 — actionability:** a proposed intervention is independently trained and evaluated;
   explanation quality alone cannot close this gate.

Failure at an earlier gate stops stronger downstream claims.

## Expected future artifacts

If promoted through review, the study should produce:

- a human-readable preregistration and machine-readable contract;
- immutable source/target cohort manifests and authorization constraints;
- embedding-route and domain-pair manifests;
- transport configuration, coupling digest and solver diagnostics;
- instance, feature and subspace attribution tables;
- null, known-shift and sensitivity results;
- explanation-stability and biometric-linkage tables;
- no-leakage audit events and claim-admissibility decisions;
- an MMALS-compatible replay bundle with hashes and environment lock;
- append-only claims, chronicle, ledger, results and paper updates.

An official complete implementation repository was not identified during the initial
review. The paper includes a compact Python reference in its supplementary material. Any
implementation adopted here must therefore receive independent fixtures, review and replay
tests rather than being treated as authoritative because it follows the paper pseudocode.

## Immediate bounded next step

1. Keep this document as a concept note only.
2. Finish the currently frozen v0.2.2 estimator implementation and known-truth coverage
   validation without reading or altering historical Study 0 outcomes.
3. Resolve or retain `E-STAT-001` and G2 according to that evidence.
4. Complete and review the Study 1 face-backbone and representative-data design.
5. Only then decide whether WaX is a diagnostic inside that study or a separate follow-on
   preregistration.
6. Before any biometric TEST analysis, validate the implementation on known shifts and
   freeze the transport, explanation and interpretation contracts.

Until those steps are complete, the only admissible statement is:

> Explainable optimal transport is a promising future diagnostic for characterizing
> representation and dataset shift. Its stability, biometric relevance and operational
> value have not been demonstrated in this programme.
