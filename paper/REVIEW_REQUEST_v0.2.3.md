# Independent review request — paper v0.2.3

## Review objective

Review the English, scientific reasoning, numerical transcription, and self-contained readability of the proposed v0.2.3 paper that closes the repository's initial embedding-compression experiment.

This is a **paper review**, not a new experiment and not authorization to execute the next study.

## Required checks

1. **Self-contained narrative**
   - A reader must understand the research object before the internal label “Study 0” is used as shorthand.
   - Internal process identifiers may be cited for traceability but must not be required to understand the paper.
   - The paper must explain the four routes, data, threshold distinction, estimand, non-inferiority margin, and all-seeds rule before presenting results.

2. **Scientific fidelity**
   - Verify all corrected numerical values against the already-reviewed materialized result tables.
   - Verify that `C-NI-001` and `C-SUP-001` remain not demonstrated.
   - Verify that the statistical correction is described as widening uncertainty, not as proving the original conclusion correct.
   - Verify that the operational threshold-transfer table is not presented as an equal-FMR ranking.
   - Verify that storage arithmetic is separated from unmeasured end-to-end latency or 1:N claims.

3. **Correction narrative**
   - Confirm that the pair-level bootstrap defect and the weighted subject-slot correction are explained accurately.
   - Confirm that known-truth coverage validation is described as validation of the interval procedure under the frozen synthetic regimes, not as evidence for the compression claim.
   - Confirm that provenance and independent recalculation are described in ordinary scientific prose rather than as a status badge.

4. **English and arXiv-style readability**
   - Review grammar, idiom, article usage, punctuation, technical vocabulary, and unnecessary French-influenced constructions.
   - Flag sentences that are correct but sound unnatural in research English.
   - Check abstract, introduction, section transitions, table captions, conclusion, and title for clarity and concision.
   - Prefer precise scientific prose over governance jargon.

5. **Claim boundaries**
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
- **ENGLISH** findings;
- **READABILITY / SELF-CONTAINMENT** findings;
- **COSMETIC** findings;
- an explicit statement that the PDF/LaTeX title, abstract, tables and conclusion were reviewed.

If proposing English edits, quote only the sentence to change and provide a replacement.
