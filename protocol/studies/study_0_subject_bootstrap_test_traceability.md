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
