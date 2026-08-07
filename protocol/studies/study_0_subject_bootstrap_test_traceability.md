# Study 0 v0.2.2 — normative implementation-test traceability

Status: **IMPLEMENTATION IN PROGRESS — NO STUDY 0 REANALYSIS RESULT**

This matrix maps the 15 normative requirements in
`study_0_subject_bootstrap_spec.md` §11 to implementation evidence. Any row below
`IMPLEMENTED` remains a blocker for implementation completion. Passing these tests does not
close `E-STAT-001`; coverage validation, immutable-input verification, replay execution and
independent review remain required.

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
| 12 | Historical pair-level files and archived PDFs bitwise unchanged | existing research-assurance PDF guards + new score-artifact hash guard; complete rematerialized bundle verification pending | PARTIAL |
| 13 | Identity-map counts, labels, join cardinality and source digests | mapping fixture + production CLI + score join guard; real 1000/500/500/963 execution pending source materialization | PARTIAL |
| 14 | Coverage-gate behavior on passing/failing simulations, separately by estimand/metric/regime | `test_coverage_gate_passes_only_when_every_stream_passes` exercises PASS, one local coverage failure, and degenerate failure; production gate-sized execution still required as validation evidence | IMPLEMENTED |
| 15 | Unexecuted reanalysis cannot contain results or close `E-STAT-001` | existing `test_subject_bootstrap_spec_cannot_claim_unexecuted_results` | IMPLEMENTED |

## Additional implementation decisions requiring review before gate execution

The preregistered phrase `lower 95% binomial bound` is operationalized as the lower endpoint
of the two-sided 95% **exact Clopper–Pearson** binomial confidence interval. This is fixed in
code before any coverage simulation output is inspected and is intentionally conservative.

The initial primary simulation regimes are:

1. independent-pair null control;
2. subject-dependent null;
3. subject-dependent non-inferior `Delta_FNMR = +0.015`;
4. subject-dependent boundary `Delta_FNMR = +0.03`.

All use a sparse 500-genuine/500-impostor graph at production gate size, two-subject effects
on impostor distances, subject effects on genuine distances, correlated candidate/reference
noise, and threshold uncertainty through re-selection of the weighted TEST threshold inside
each representation bootstrap replicate.

The production execution contract fixes 10,000 bootstrap replicates per simulated dataset
and simulation checkpoints at 2,000, 4,000 and 10,000 datasets, stopping at the first
checkpoint where every reported Monte Carlo standard error is at most `0.005`.

These implementation choices must be reviewed before the production coverage gate is run.
No Study 0 historical score may be opened to guide changes to them.
