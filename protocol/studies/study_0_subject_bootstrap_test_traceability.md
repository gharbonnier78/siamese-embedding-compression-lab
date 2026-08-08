# Study 0 v0.2.2 — normative implementation-test traceability

Status: **IMPLEMENTATION IN PROGRESS — NO STUDY 0 REANALYSIS RESULT**

This matrix maps the 15 normative requirements in
`study_0_subject_bootstrap_spec.md` §11 to implementation evidence. Any row below
`IMPLEMENTED` remains a blocker for implementation completion. Passing these tests does not
close `E-STAT-001`; coverage validation, immutable-input verification, replay execution and
independent review remain required.

Current status: **14/15 normative implementation requirements fully implemented.** Requirement
#12 remains PARTIAL because the complete historical replay bundle has not yet been
rematerialized and verified bitwise.

| # | Normative requirement | Current automated evidence | Status |
|---:|---|---|---|
| 1 | Exact subject multiplicities for a fixed RNG seed | `test_fixed_rng_draw_is_deterministic` | IMPLEMENTED |
| 2 | Genuine weight `m_i` | `test_genuine_and_impostor_multiplicity_rules` | IMPLEMENTED |
| 3 | Observed impostor weight `m_i*m_j` | `test_genuine_and_impostor_multiplicity_rules` | IMPLEMENTED |
| 4 | Preserve duplicated subject slots | `test_repeated_subject_slots_are_not_deduplicated` | IMPLEMENTED |
| 5 | Never synthesize unobserved edges | `test_no_unobserved_edge_is_synthesized` | IMPLEMENTED |
| 6 | No impostor edge between slots of same subject | `test_same_subject_never_becomes_impostor` | IMPLEMENTED |
| 7 | Weighted/materialized numerical equivalence | `test_weighted_and_materialized_rates_are_equivalent` | IMPLEMENTED |
| 8 | Identical weights across paired routes | `test_candidate_and_reference_receive_identical_edge_weights` captures both threshold calls and compares their complete edge-weight vectors | IMPLEMENTED |
| 9 | Deterministic threshold/tie/sentinel handling | `test_whole_tie_block_is_never_split`, `test_no_admissible_observed_threshold_uses_sentinel` | IMPLEMENTED |
| 10 | Operational thresholds remain VALIDATION-frozen | `test_validation_threshold_remains_frozen` | IMPLEMENTED |
| 11 | Deterministic replay from root seed/configuration | `test_paired_routes_replay_identically_from_root_seed` | IMPLEMENTED |
| 12 | Historical pair-level files and archived PDFs bitwise unchanged | existing research-assurance PDF guards + score-artifact hash guard; complete historical replay bundle rematerialization/verification still pending | PARTIAL |
| 13 | Identity-map counts, labels, join cardinality and source digests | exact Kaggle v4 DevTest materialization workflow + immutable source-digest checks + production map build; versioned `source_manifest.json` records 1000/500/500/963 and map SHA-256 `112c0d06963170665cd73b220d33251aae34511a331261d143de4e6644f7feea`; score-map one-to-one join guard remains implemented for later reanalysis | IMPLEMENTED |
| 14 | Coverage-gate behavior on passing/failing simulations, separately by estimand/metric/regime | `test_coverage_gate_passes_only_when_every_stream_passes` exercises PASS, one local coverage failure, and degenerate failure; production gate-sized execution still required as validation evidence | IMPLEMENTED |
| 15 | Unexecuted reanalysis cannot contain results or close `E-STAT-001` | existing `test_subject_bootstrap_spec_cannot_claim_unexecuted_results` | IMPLEMENTED |

## Production DevTest source-map evidence

The historical DevTest source-materialization blocker for requirement #13 is now closed without
opening any historical Study 0 score artifact.

The `Materialize LFW DevTest evidence` workflow downloads only the two pair CSVs from the exact
Study 0 source version `jessicali9530/lfw-dataset/versions/4` and blocks unless their bytes
match the frozen run-manifest digests:

- matched SHA-256: `9428d939063ff006b72bc79f50b7305e7da51b46b52bf2c25ca14b3a29479fb6`;
- mismatched SHA-256: `cf1a1326577bf33abc98d1bbc938d3c2ec00304d1ace9b4392f5b38b19e182d0`.

The verified production build records exactly 1,000 observed pairs, 500 genuine pairs, 500
impostor pairs and 963 endpoint subjects. The pseudonymized map is versioned at
`evidence/study_0_subject_bootstrap_v0.2.2/test_pair_subject_map_v0.2.2.csv` with SHA-256
`112c0d06963170665cd73b220d33251aae34511a331261d143de4e6644f7feea`. Its provenance and
counts are recorded in the adjacent `source_manifest.json`. The original source CSVs, which
contain identity names, remain outside Git and are retained only in the temporary workflow
artifact. The manifest explicitly records `historical_study_0_scores_read: false`.

This closes source-map materialization only. It does not satisfy requirement #12, execute the
production coverage gate, open `test_pair_scores.csv`, produce a corrected Study 0 result,
or change `E-STAT-001`, G2 or the Study 1 block.

## Section 9 degenerate-replicate audit

Reviewer inspection identified a gap between the original fail-fast implementation and the
full §9 audit contract. That gap is now addressed before any historical Study 0 score is
opened.

A degenerate replicate remains a blocking failure and is never silently redrawn, but the
failure is now raised as a structured `DegenerateReplicateError`. Its attached audit record
contains:

- failed replicate index;
- exact reason;
- weighted genuine and impostor totals;
- effective positive-weight genuine and impostor edge counts;
- number of completed replicates before failure.

The exception also preserves the already completed replicate objects so that the future
execution runner can write the partial `subject_bootstrap_replicates.csv` and an
`audit_trace.jsonl` failure event before terminating. The same behavior is implemented for
the representation and VALIDATION-frozen operational paths.

Automated evidence:

- `test_degenerate_replicate_preserves_audit_and_prior_results`;
- `test_degenerate_operational_replicate_is_structured_and_blocking`.

The future execution runner still has to serialize this structured evidence; no historical
reanalysis has been run in this PR.

## Additional implementation decisions reviewed before gate execution

The preregistered phrase `lower 95% binomial bound` is operationalized as the lower endpoint
of the two-sided 95% **exact Clopper–Pearson** binomial confidence interval. This is fixed in
code before any coverage simulation output is inspected and is intentionally conservative.

The primary simulation regimes are:

1. independent-pair null control;
2. subject-dependent null;
3. subject-dependent non-inferior `Delta_FNMR = +0.015`;
4. subject-dependent boundary `Delta_FNMR = +0.03`;
5. subject-dependent inferior regime `Delta_FNMR = +0.05`, beyond the frozen NI margin.

The fifth regime tests whether interval coverage remains calibrated beyond the NI boundary;
it is not a separate inferiority-decision gate.

All use a sparse 500-genuine/500-impostor graph at production gate size, two-subject effects
on impostor distances, subject effects on genuine distances, correlated candidate/reference
noise, and threshold uncertainty through re-selection of the weighted TEST threshold inside
each representation bootstrap replicate.

Two independent checkpoint axes are intentionally used:

- **inner estimator axis (§8):** 10,000 subject-bootstrap replicates per dataset, with
  convergence checkpoints at 2,000 / 5,000 / 10,000 bootstrap replicates;
- **outer coverage-validation axis (§10):** 2,000 / 4,000 / 10,000 independently simulated
  datasets, stopping at the first checkpoint where every reported Monte Carlo standard error
  is at most `0.005`.

The similar numbers do not denote the same quantity. No Study 0 historical score may be
opened to guide changes to these choices.
