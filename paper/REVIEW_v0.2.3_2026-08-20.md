# Independent review outcome — paper v0.2.3

Date: 2026-08-20

## Bound artifact identity

- Reviewed LaTeX SHA-256: `8b0da216abcfad012b49e4199fa7eac947e12ec65cba39d4ab8e1b168996e59d`
- Reviewed PDF SHA-256: `c79082023383742cb698e0e043cc8408e50aada754226ebd9b5f1c07dee8169a`
- Canonical source: `paper/study0_v0.2.3.tex`

The first review pass returned `VERDICT: REVISE` solely because the review prompt declared an incorrect PDF hash. The reviewer independently recalculated the PDF hash as `c79082023383742cb698e0e043cc8408e50aada754226ebd9b5f1c07dee8169a` while independently confirming that the LaTeX hash matched the declared `8b0da216abcfad012b49e4199fa7eac947e12ec65cba39d4ab8e1b168996e59d`.

An integrity-only amendment corrected the declared PDF hash. No manuscript content changed between the substantive review and the integrity recheck.

## Final reviewer verdict

`VERDICT: ACCEPT`

The reviewer explicitly confirmed that the former `REVISE` was caused only by the erroneous PDF hash in the original review prompt, not by a manuscript-content or PDF-content discrepancy.

## Substantive review findings

### Scientific

No substantive scientific issue was identified. The reviewer found the full chain coherent: bounded non-inferiority question, statistical defect, frozen correction, known-truth validation, corrected reanalysis, independent verification, and bounded interpretation.

### Numerical / statistical

The reviewer independently cross-checked the corrected primary result tables, interval-width comparison, validation-frozen threshold-transfer values, known-truth coverage value `0.937743`, and historical archive identities against its prior independent interpretation review. Those values matched.

The reviewer explicitly noted that Table 6 historical descriptive AUC/EER/FNMR values and the TEST-optimized ~70% diagnostic accuracies had not been independently recomputed in that review pass. A separate repository note records an additional cross-check of those descriptive values against the immutable replay archive; it is supplementary verification, not part of the independent reviewer verdict.

### Biometrics

The biometric primer was accepted: training/enrollment/inference/decision, 1:1 versus 1:N, FMR/FNMR/ROC/AUC/EER, threshold trade-off, and the distinction between matcher-level FMR and end-to-end transaction false acceptance were considered correctly bounded.

### PCA / reduction

The PCA equations and interpretation, feature-selection versus feature-extraction distinction, Johnson--Lindenstrauss limitation, and Andrew Ng pedagogical-reference boundary were accepted.

### Siamese

The reviewer checked the L2 normalization explanation, Euclidean/cosine identity on unit vectors, the numeric cosine `0.8` example, contrastive loss, training-versus-inference explanation, and absence of closed-set softmax conflation. No correction was requested.

### Engineering boundary

The reviewer recalculated the storage arithmetic and naive exhaustive-scan traffic example and found them correct. The AI-assisted CAD paragraph was considered clearly non-validated and sufficiently separated from Study 0 evidence.

### Backbone / dataset

The reviewer accepted the frozen ImageNet ResNet-18 provenance and the statement that only the 512-to-128 head learns from LFW. It also accepted the bounded Study 1 wording around a face-specific frozen backbone, VGGFace2 availability, IJB-C access, identity overlap, and external validity.

### English / readability

The manuscript was judged self-contained and proportionate for an arXiv-like technical report. The only stylistic suggestion was optional: replacing the fictional name `Maurice` with a generic statistician label. This was explicitly non-blocking.

### Cosmetic

No suspended TODO/FIXME marker or figure-caption inconsistency was identified.

## Explicit coverage statement

The reviewer explicitly stated that it reviewed the title, abstract, biometric primer, PCA section, Siamese section, ImageNet-backbone rationale, threshold/non-inferiority section, subject-bootstrap correction, result tables, engineering paragraph, Study 1 data/backbone section, all three figures and captions, and the conclusion.

## Claim boundary

This review accepts the manuscript content. It does not change the already-closed scientific status of Study 0, does not convert `C-NI-001` or `C-SUP-001` into demonstrated claims, and does not authorize Study 1 execution or representation-geometry work.
