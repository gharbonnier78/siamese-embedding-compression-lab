# Study 0 errata and retained experimental defects

This file is append-only. It does not replace `RESULTS_LFW_V0.1.md`, the original replay
tables or the original v0.2 paper.

## E-STAT-001 - Bootstrap unit differs from the declared uncertainty contract

- Discovered: 2026-08-07
- Affected run: `lfw_resnet18_siamese_projection_v0_1-89179914-911192ee-64559cbd`
- Affected claims: `C-NI-001`, `C-SUP-001`
- Affected gate: `G2 estimator_and_statistical_validity`
- Status: `SPECIFIED_PENDING_IMPLEMENTATION`

### What was declared

The research programme and Study 1 draft used the term
`paired_identity_aware_bootstrap`. The paper required uncertainty to be resampled at an
identity or justified cluster level.

### What Study 0 actually executed

`bootstrap_paired_fnmr_at_fmr` samples genuine-pair indices and impostor-pair indices with
replacement. Candidate and raw distances use the same sampled pair indices, so the method
is paired across matchers and label-stratified. It does not use `identity1` or `identity2`
and therefore does not cluster trials sharing an identity.

The values in `paired_noninferiority.csv`, including the worst reported upper bound `0.156`,
are historical pair-level results. They remain reproducible and must not be relabelled as
identity-aware intervals.

### Consequence

The coverage guarantee claimed for an identity-aware interval is unsupported. Study 0 G2
is `FAIL` for inferential qualification. Non-inferiority remains `NOT_DEMONSTRATED`; the
defect does not permit a positive claim. The mechanism, deterministic execution, raw metrics,
storage arithmetic and existence of the negative pair-level analysis remain valid within
their separately bounded claims.

### Planned correction

1. Restore the LFW DevTest identity mapping and verify its recorded source hashes.
2. Join anonymized endpoint identities to the preserved `test_pair_scores.csv` replay table.
3. Specify and test a resampling method appropriate for genuine trials and two-identity
   impostor trials.
4. Recompute pair-level and identity-dependence-aware analyses from the same stored scores.
5. Publish new, versioned sensitivity tables and figures without overwriting original rows.
6. Treat interval-width differences as sample-specific sensitivity, not proof of true
   coverage; validate coverage through simulation before using the variance for Study 1.

Until those steps pass, Study 1 execution and its a-priori sample-size calculation are
blocked.

### Frozen correction specification

Version `0.2.2-spec` freezes the proposed protocol-preserving weighted subject-slot
bootstrap in
[`protocol/studies/study_0_subject_bootstrap_spec.md`](protocol/studies/study_0_subject_bootstrap_spec.md).
It resamples 963 subject slots with replacement, assigns weight `m_i` to each observed
genuine edge and `m_i*m_j` to each observed impostor edge, preserves repeated slots, and
never synthesizes a pair absent from LFW DevTest.

This specification is not an implementation or result. G2 remains `FAIL`, this erratum
remains open, and Study 1 remains blocked until the implementation, coverage validation,
versioned reanalysis and independent review all pass.

## Resolution record — 2026-08-19

Current resolution state: **`REANALYZED`**.

This record is append-only and does not alter the historical description above. The frozen
v0.2.2 weighted subject-slot estimator was implemented and tested, its interval procedure
passed the preregistered known-truth coverage gate, and the exact historical Study 0 score
bundle was reanalysed without retraining or score recomputation. The complete materialized
bundle received independent approval before interpretation. A second independent review
then recalculated the numerical interpretation from the materialized result tables and
returned `VERDICT: APPROVE` with no blocking, non-blocking or cosmetic findings.

The corrected subject-level intervals are materially wider than the original pair-level
intervals. The correction therefore confirms that the original analysis understated
uncertainty. It does **not** reverse the bounded scientific outcome: non-inferiority remains
`NOT_DEMONSTRATED`, and added value of Siamese over PCA/random controls remains
`NOT_DEMONSTRATED`.

The scientific closure decision is recorded in
`evidence/study_0_subject_bootstrap_v0.2.2/STUDY0_CLOSURE_DECISION_2026-08-19.yaml`:

- `E-STAT-001 = REANALYZED`;
- `G2 estimator_and_statistical_validity = PASS` for the corrected Study 0 reanalysis;
- `C-NI-001 = NOT_DEMONSTRATED`;
- `C-SUP-001 = NOT_DEMONSTRATED`.

Evidence:

- `evidence/study_0_subject_bootstrap_v0.2.2/INTERPRETATION_DRAFT_2026-08-19.md`;
- `evidence/study_0_subject_bootstrap_v0.2.2/INTERPRETATION_REVIEW_APPROVE_2026-08-19.fr.md`;
- `evidence/study_0_subject_bootstrap_v0.2.2/STUDY0_CLOSURE_DECISION_2026-08-19.yaml`;
- the independently approved known-truth coverage evidence and corrected materialization
  already archived under `evidence/study_0_subject_bootstrap_v0.2.2/`.

This resolution closes the statistical defect for Study 0 only. It does not establish
industrial biometric validity, does not prove Siamese inferior, does not establish Siamese
superiority, does not automatically authorize Study 1 execution, and does not authorize
geometry work.
