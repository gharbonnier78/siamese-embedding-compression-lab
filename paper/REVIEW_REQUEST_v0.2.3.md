# Independent review request — paper v0.2.3

## Review objective

Review the English, scientific reasoning, numerical transcription, and self-contained readability of the proposed v0.2.3 paper that closes the repository's initial embedding-compression experiment.

Primary manuscript: `paper/study0_v0.2.3.tex` (`paper/main.tex` is the build entrypoint).

This is a **paper review**, not a new experiment and not authorization to execute the next study.

## Required checks

1. **Self-contained narrative**
   - A reader must understand the research object before the internal label “Study 0” is used as shorthand.
   - Internal process identifiers may be cited for traceability but must not be required to understand the paper.
   - The paper must explain the data, threshold distinction, estimand, non-inferiority margin, and all-seeds rule before presenting results.

2. **Dimensionality-reduction background**
   - Confirm that feature selection and feature extraction are distinguished correctly.
   - Check the PCA explanation mathematically and conceptually: TRAIN-only fitting, centering/covariance/principal directions, variance/reconstruction objective, and the fact that PCA does not optimize low-FMR verification.
   - Check the random-projection explanation, including the implemented `N(0,1/d)` scaling and the bounded Johnson–Lindenstrauss intuition without turning it into a biometric guarantee.
   - Check the discussion of LDA, autoencoders, metric-learning projections, hashing/binary embeddings, quantization, and compact backbones. The paper should explain why these are relevant alternatives without implying that Study 0 tested them.
   - Confirm that dimensionality reduction and quantization are not conflated.

3. **Siamese explanation**
   - Verify against `src/siamese_compression_lab/models.py` and `configs/lfw_resnet18.yaml` that the manuscript accurately explains the implemented Siamese route.
   - The two training branches must be described as sharing the same affine projection `W,b`, not as two independently trained models.
   - Confirm the 512→128 shape and `65,664` trainable-parameter count.
   - Confirm L2 normalization and Euclidean distance on normalized outputs; check the stated monotonic equivalence with cosine similarity.
   - Confirm the exact contrastive-loss semantics: genuine pairs are pulled together; impostor pairs inside margin `m=1` are pushed apart.
   - Confirm the stated training configuration: up to 60 epochs, batch size 128, learning rate `1e-3`, weight decay `1e-4`, patience 8, minimum improvement `1e-4`.
   - Confirm the distinction between the two-branch training construction and one-branch-per-template inference.
   - Confirm that the route is not presented as closed-set softmax identity classification and that decreasing contrastive loss is not treated as sufficient evidence of useful compression.
   - Confirm that raw/random/PCA/Siamese form a meaningful baseline hierarchy for isolating compression and pair-supervision value.

4. **Scientific fidelity**
   - Verify all corrected numerical values against the already-reviewed materialized result tables.
   - Verify that `C-NI-001` and `C-SUP-001` remain not demonstrated.
   - Verify that the statistical correction is described as widening uncertainty, not as proving the original conclusion correct.
   - Verify that the operational threshold-transfer table is not presented as an equal-FMR ranking.
   - Verify that storage arithmetic is separated from unmeasured end-to-end latency or 1:N claims.

5. **Correction narrative**
   - Confirm that the pair-level bootstrap defect and the weighted subject-slot correction are explained accurately.
   - Confirm that known-truth coverage validation is described as validation of the interval procedure under the frozen synthetic regimes, not as evidence for the compression claim.
   - Confirm that provenance and independent recalculation are described in ordinary scientific prose rather than as a status badge.

6. **English and arXiv-style readability**
   - Review grammar, idiom, article usage, punctuation, technical vocabulary, and unnecessary French-influenced constructions.
   - Flag sentences that are correct but sound unnatural in research English.
   - Check title, abstract, introduction, the dimensionality-reduction section, the full Siamese section, section transitions, table/figure captions, results, and conclusion for clarity and concision.
   - Prefer precise scientific prose over governance jargon.

7. **Claim boundaries**
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
- **METHODS / PCA / REDUCTION** findings;
- **SIAMESE** findings;
- **ENGLISH** findings;
- **READABILITY / SELF-CONTAINMENT** findings;
- **COSMETIC** findings;
- an explicit statement that the PDF/LaTeX title, abstract, dimensionality-reduction section, Siamese section, tables, figure, results and conclusion were reviewed.

If proposing English edits, quote only the sentence to change and provide a replacement.
