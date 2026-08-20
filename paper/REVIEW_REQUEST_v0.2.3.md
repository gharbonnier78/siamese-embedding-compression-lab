# Independent review request — paper v0.2.3

## Review objective

Review the English, scientific reasoning, numerical transcription, implementation fidelity,
and self-contained readability of the proposed v0.2.3 paper that closes the repository's
initial embedding-compression experiment.

This is a **paper review**, not a new experiment and not authorization to execute the next study.

## Required checks

1. **Self-contained narrative**
   - A reader must understand the research object before the internal label “Study 0” is used as shorthand.
   - Internal process identifiers may be cited for traceability but must not be required to understand the paper.
   - The paper must explain the four routes, data, threshold distinction, estimand, non-inferiority margin, and all-seeds rule before presenting results.

2. **Dimensionality reduction and Siamese mechanism**
   - Verify the distinction between feature selection and feature extraction.
   - Verify the PCA explanation: centering/covariance, principal directions, variance/reconstruction objective, TRAIN-only fitting, and why variance retention does not imply low-FMR biometric preservation.
   - Verify the random-projection explanation and that Johnson–Lindenstrauss is presented only as geometric motivation, not a biometric guarantee.
   - Verify that LDA, autoencoders, metric learning, hashing/quantization and compact-backbone approaches are clearly marked as context rather than tested routes.
   - Verify the exact implemented Siamese route against `src/siamese_compression_lab/models.py` and `configs/lfw_resnet18.yaml`: shared `W,b`, 512→128 affine projection, L2 normalization, Euclidean distance on the unit sphere, contrastive loss, training/validation behavior and inference semantics.
   - Verify that the paper does not conflate Siamese metric learning with closed-set softmax identity classification.

3. **ImageNet ResNet-18 provenance and limitation**
   - Verify against the motivating public implementation and this repository that the starting ResNet-18 is ImageNet-pretrained and fully frozen; only the 512→128 embedding head learns from LFW pairs.
   - Verify that the text does **not** incorrectly say that a face-recognition ResNet was trained on LFW.
   - Verify the scientific rationale for replacing it: ImageNet object-category supervision is not a face-identity objective, and a linear head cannot recover identity information absent from the frozen representation.
   - Recalculate the descriptive TEST-optimized accuracy context from the immutable Study 0 scores: raw 71.5%; Siamese 73.0–74.7%; PCA 74.1–74.3%.
   - Confirm these accuracy values are explicitly labelled TEST-tuned/non-deployable and do not replace the low-FMR non-inferiority endpoint.

4. **Scientific fidelity**
   - Verify all corrected numerical values against the already-reviewed materialized result tables.
   - Verify that `C-NI-001` and `C-SUP-001` remain not demonstrated.
   - Verify that the statistical correction is described as widening uncertainty, not as proving the original conclusion correct.
   - Verify that the operational threshold-transfer table is not presented as an equal-FMR ranking.
   - Verify that storage arithmetic is separated from unmeasured end-to-end latency or 1:N claims.

5. **Next-study backbone and dataset logic**
   - Verify that the preferred design is a pretrained, frozen face-specific extractor with pinned architecture, preprocessing, weights, training corpus, provenance and licence.
   - Verify that ArcFace-family / AdaFace wording is presented as candidate families, not as already frozen experimental choices.
   - Verify the separation of four data roles: backbone training provenance; projection TRAIN/VALIDATION; exploratory SCREEN; qualification TEST.
   - Verify the proposed screening suite (LFW, CFP-FP, AgeDB-30, CALFW, CPLFW) is non-claim-bearing.
   - Verify VGGFace2 is presented as scientifically attractive but not automatically available because the original Oxford download is no longer provided.
   - Verify IJB-C 1:1 template verification is presented as a preferred public qualification candidate only after lawful-access and identity-overlap checks.
   - Verify identity-overlap risk between common training corpora and LFW-family benchmarks is explicitly treated as a validity threat.
   - Verify public celebrity benchmarks are not presented as operationally representative of a specific production population/capture process.

6. **Correction narrative**
   - Confirm that the pair-level bootstrap defect and the weighted subject-slot correction are explained accurately.
   - Confirm that known-truth coverage validation is described as validation of the interval procedure under the frozen synthetic regimes, not as evidence for the compression claim.
   - Confirm that provenance and independent recalculation are described in ordinary scientific prose rather than as a status badge.

7. **English and arXiv-style readability**
   - Review grammar, idiom, article usage, punctuation, technical vocabulary, and unnecessary French-influenced constructions.
   - Flag sentences that are correct but sound unnatural in research English.
   - Check abstract, introduction, section transitions, table captions, conclusion, and title for clarity and concision.
   - Prefer precise scientific prose over governance jargon.

8. **Claim boundaries**
   - No industrial biometric validation claim.
   - No general claim that Siamese learning fails.
   - No claim that 128D is intrinsically inferior.
   - No claim of Siamese superiority over PCA/random.
   - No automatic authorization of the next study or representation-geometry exploration.

## Requested output

Return:

- `VERDICT: ACCEPT` or `VERDICT: REVISE`;
- **SCIENTIFIC** findings;
- **NUMERICAL** findings;
- **BACKBONE / DATASET** findings;
- **ENGLISH** findings;
- **READABILITY / SELF-CONTAINMENT** findings;
- **COSMETIC** findings;
- an explicit statement that the PDF/LaTeX title, abstract, PCA/reduction section, Siamese section, ImageNet-backbone rationale, dataset plan, tables and conclusion were reviewed.

If proposing English edits, quote only the sentence to change and provide a replacement.
