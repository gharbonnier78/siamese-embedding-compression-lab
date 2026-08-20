# Independent review request — paper v0.2.3

## Review objective

Review the English, scientific reasoning, numerical transcription, implementation fidelity,
biometric pedagogy, and self-contained readability of the proposed v0.2.3 paper that closes
the repository's initial embedding-compression experiment.

This is a **paper review**, not a new experiment and not authorization to execute Study 1.
Review the exact current manuscript `paper/study0_v0.2.3.tex`; its content blob after the
pedagogical revision is `9698c9f48c0fd45537daaa0d6cf0c9f72928912f`.

## Required checks

1. **Self-contained biometric narrative**
   - A reader should understand the research object before repository-specific shorthand becomes important.
   - Check the new `Biometric matching in one page` section for technical accuracy and accessibility.
   - Verify the distinction among training, enrollment, inference, and decision.
   - Verify 1:1 verification/authentication versus 1:N identification/watchlist search.
   - Verify that Study 0 remains explicitly a 1:1 representation experiment; the 1:N edge/watchlist scenario is motivation only.
   - Check FMR, FNMR, ROC, ROC AUC and EER definitions and their relationship to the decision threshold.
   - In particular, verify that FMR is not silently conflated with a complete transaction-level false-acceptance probability.

2. **Operating point, non-inferiority, and frozen choices**
   - Verify the plain-language explanation of why biometric threshold choices trade false matches against false non-matches.
   - Verify that `alpha = 0.01` is introduced as notation for the Study 0 target FMR, not a significance level.
   - Verify that on 500 impostor DevTest pairs, FMR 0.01 is correctly described as a nominal five-false-match grid point, with the tie-block caveat.
   - Verify that FMR 0.01 is presented as an exploratory resolvable Study 0 operating point, not an industrial requirement.
   - Verify that `delta = 0.03` is correctly explained as three absolute FNMR percentage points and that the paper does **not** invent a product/regulatory justification for this margin.
   - Verify the non-inferiority concept and the interpretation of the 97.5% upper confidence bound.
   - Verify the explanation of a pseudo-random seed, `predeclared`, and the all-seeds anti-selection rule.

3. **Dimensionality reduction and PCA**
   - Verify the distinction between feature selection and feature extraction.
   - Verify the PCA explanation: centering/covariance, principal directions, variance/reconstruction objective, TRAIN-only fitting, and why variance retention does not imply low-FMR biometric preservation.
   - Verify that Andrew Ng's Machine Learning Specialization is cited only as a pedagogical companion, not as scientific authority for the experiment.
   - Verify the random-projection explanation and that Johnson–Lindenstrauss is geometric motivation, not a biometric guarantee.
   - Verify that LDA, autoencoders, metric learning, hashing/quantization and compact-backbone approaches are clearly marked as context rather than tested routes.

4. **Exact Siamese mechanism and pedagogy**
   - Verify against `src/siamese_compression_lab/models.py` and `configs/lfw_resnet18.yaml`: shared `W,b`, 512→128 affine projection, L2 normalization, Euclidean distance, contrastive loss, training/validation behavior and inference semantics.
   - Verify the genuine-pair versus impostor-pair explanation.
   - Verify that L2 normalization is correctly described as deterministic, parameter-free post-processing in this implementation, including the `(3,4) -> (0.6,0.8)` intuition.
   - Verify the Euclidean/cosine relation on unit vectors, including the example `cosine = 0.8 -> Euclidean distance ≈ 0.632`.
   - Confirm the paper is explicit that the implementation thresholds Euclidean distance; cosine is only monotonically equivalent after normalization.
   - Verify the explanation of what `contrastive` means and the historical references to Siamese/contrastive metric learning.
   - Verify that the training-versus-inference section is both technically correct and understandable to a reader who initially assumes the two-branch architecture must also exist at deployment.
   - Verify that the paper does not conflate Siamese metric learning with closed-set softmax identity classification.

5. **ImageNet ResNet-18 provenance and limitation**
   - Verify against the motivating public implementation and this repository that the starting ResNet-18 is ImageNet-pretrained and fully frozen; only the 512→128 embedding head learns from LFW pairs.
   - Verify that the text does **not** incorrectly say that a face-recognition ResNet was trained on LFW.
   - Verify the rationale for questioning the source representation: ImageNet object-category supervision is not a face-identity objective, and a linear head cannot recover identity information absent from the frozen representation.
   - Recalculate the descriptive TEST-optimized accuracy context from immutable Study 0 scores: raw 71.5%; Siamese 73.0–74.7%; PCA 74.1–74.3%.
   - Confirm these accuracy values are explicitly labelled TEST-tuned/non-deployable and do not replace the low-FMR non-inferiority endpoint.

6. **Subject bootstrap and correction narrative**
   - Verify the new non-statistician explanation of bootstrap and sampling unit.
   - Verify the pair-dependence toy figure: repeated identity involvement is an intuition for dependence, not a claim that every pair has the same dependence structure.
   - Verify that the historical pair-level estimator and the weighted subject-slot correction are described accurately.
   - Verify the `m_i` and `m_i m_j` weighting interpretation and that only historically observed pair edges are reweighted.
   - Verify the stated risk: in this one-sided non-inferiority setup, an overly narrow interval could produce false confidence near the margin; more generally a wrong dependence model can distort coverage.
   - Verify that the paper does not claim the original conclusion was proved correct merely because the corrected conclusion stayed negative.
   - Verify known-truth coverage validation is described as validation of the interval procedure under frozen synthetic regimes, not evidence for the compression claim.

7. **Scientific and numerical fidelity**
   - Verify all corrected numerical values against the already-reviewed materialized result tables.
   - Verify that `C-NI-001` and `C-SUP-001` remain not demonstrated.
   - Verify that the statistical correction is described as widening uncertainty, not as proving compression inferior.
   - Verify that the operational threshold-transfer table is not presented as an equal-FMR ranking.
   - Verify that the secondary AUC/EER table remains descriptive and cannot override the primary endpoint.

8. **Engineering vignette and claim boundary**
   - Recalculate the illustrative gallery payload arithmetic: 512D FP32 = 2048 bytes/template; 128D FP32 = 512 bytes/template; 1M identities × 5 templates = 10.24 GB versus 2.56 GB payload.
   - Recalculate the deliberately naive exhaustive-scan traffic example at 1,000 probes/hour: approximately 2.84 GB/s versus 0.71 GB/s before indexing/overhead.
   - Confirm these numbers are explicitly engineering calculations, not measured Study 0 results.
   - Confirm the hypothetical statistician/edge-engineer vignette improves motivation without turning the paper into a product design or 1:N qualification claim.
   - Confirm no statement implies fourfold template reduction guarantees fourfold end-to-end latency, energy, or throughput improvement.

9. **Next-study backbone and dataset logic**
   - Verify the preferred design is a pretrained, frozen face-specific extractor with pinned architecture, preprocessing, detector/alignment pipeline, weights, training corpus, provenance and licence.
   - Verify ArcFace-family / AdaFace wording is presented as candidate families, not already frozen experimental choices.
   - Verify the separation of four data roles: backbone-training provenance; projection TRAIN/VALIDATION; exploratory SCREEN; claim-bearing TEST.
   - Verify LFW/CFP-FP/AgeDB-30/CALFW/CPLFW remain non-claim-bearing screening candidates.
   - Verify VGGFace2 is described as scientifically attractive but not automatically obtainable because the official Oxford download is no longer available.
   - Verify IJB-C is described as an established benchmark conditional on lawful existing access, rather than a currently downloadable public dataset; NIST discontinued distribution in 2023.
   - Verify identity-overlap risk is explicitly treated and that an unavailable dataset does not justify weakening the qualification gate.
   - Verify public web/celebrity benchmarks are not presented as operationally representative of a specific deployment population/capture process.

10. **Figures, pedagogy, and length**
   - Review all vector/TikZ figures for correctness, legibility and actual pedagogical value.
   - Confirm the existing Siamese figure remains faithful to the implementation.
   - Confirm the biometric 1:1/1:N pipeline and pair-dependence figure clarify concepts rather than add decorative complexity.
   - Assess whether the expanded manuscript remains proportionate in length for an arXiv-like technical/pedagogical report; flag content that can be removed without losing scientific or pedagogical value.
   - The manuscript deliberately does **not** link to a Diderot/toy artifact yet because no such reviewed artifact is part of the evidence set.

11. **English and arXiv-style readability**
   - Review grammar, idiom, article usage, punctuation, technical vocabulary, and unnecessary French-influenced constructions.
   - Flag sentences that are correct but sound unnatural in research English.
   - Check title, abstract, introduction, primer, section transitions, figure/table captions, conclusion and references for clarity and concision.
   - Prefer precise scientific prose over repository/governance jargon.

12. **Claim boundaries**
   - No industrial biometric validation claim.
   - No general claim that Siamese learning fails.
   - No claim that 128D is intrinsically inferior.
   - No claim of Siamese superiority over PCA/random.
   - No claim that FMR 0.01 or delta 0.03 are universal deployment requirements.
   - No claim that the hypothetical edge device has been built or benchmarked.
   - No automatic authorization of Study 1 or representation-geometry exploration.
   - Future interactive teaching companions, if built, must remain explanatory and cannot replace replay/evidence or release scientific gates.

## Requested output

Return:

- `VERDICT: ACCEPT` or `VERDICT: REVISE`;
- **SCIENTIFIC** findings;
- **NUMERICAL / STATISTICAL** findings;
- **BIOMETRICS** findings;
- **PCA / REDUCTION** findings;
- **SIAMESE** findings;
- **BACKBONE / DATASET** findings;
- **ENGINEERING BOUNDARY** findings;
- **ENGLISH** findings;
- **READABILITY / SELF-CONTAINMENT** findings;
- **COSMETIC** findings;
- an explicit statement that the title, abstract, biometric primer, PCA/reduction section,
  Siamese section, ImageNet-backbone rationale, threshold/non-inferiority explanation,
  subject-bootstrap correction, result tables, next-study dataset plan, figures and conclusion
  were reviewed.

If proposing English edits, quote only the sentence to change and provide a replacement.
