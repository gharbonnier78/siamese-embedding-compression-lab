# Adopting the Scientific Chronicle & Reproducibility Harness

This guide is intended for future experimental repositories. It separates the scientific harness from any specific model, dataset, or Study 0 convention.

## 1. Minimum viable harness

A new project should start with these authoritative layers:

1. **Research programme** — bounded question, excluded claims, study order, evidence planes.
2. **Claims registry** — claim IDs, permitted/forbidden wording, required gates and evidence.
3. **Preregistration / protocol** — estimands, sampling unit, controls, stopping rules, uncertainty and failure criteria frozen before outcome inspection.
4. **Experiment ledger** — append-only study/run history, immutable references, linked errata.
5. **Scientific chronicle** — doubts, assumptions, reviewer findings, cost risks, rejected alternatives, belief changes and unresolved questions.
6. **Replay contract** — executable configuration, hashes, environment, seeds and result artifacts (MMALS-replay or an equivalent explicit contract).
7. **Claim-admissibility contract** — CAL or another bounded gate that keeps missing evidence from becoming permission.
8. **Research assurance** — CI checks that cross-reference these artifacts and fail on contradictions.

The harness must not make an experiment look rigorous merely because documentation exists. Every layer has a bounded role, and no later layer can repair missing empirical evidence in an earlier one.

## 2. Recommended repository skeleton

```text
claims/
  registry.yaml
beliefs/
  prior_posterior.yaml
protocol/
  research_program.yaml
  experiment_ledger.yaml
  scientific_chronicle.yaml
  studies/
  coverage/                  # when applicable
gates/
  gate_spec.yaml
  cal_spec.yaml              # when CAL is used
  scientific_harness.yaml
evidence/
  <immutable run snapshots>
docs/
  SCIENTIFIC_HARNESS.md
  SCIENTIFIC_HARNESS_ADOPTION.md
  EXPERIMENT_HISTORY_AND_ERRATA.md
paper/                      # optional publication layer
pedagogy/                   # optional progressive-exposition layer
```

## 3. Chronicle entry lifecycle

### Before outcome evidence
Record material doubts, assumptions, design alternatives, computational risks and expected failure modes. Set `outcome_evidence_seen: false`.

### During execution
Record unexpected degeneracies, environment/data failures, representativity concerns, runtime constraints and deviations. Do not silently redraw, rerun, respecify or replace inconvenient results.

### After outcome evidence
Any methodological change is post-outcome unless independently preregistered beforehand. Record it as such. A new version/study may be legitimate; pretending it was part of the original plan is not.

### Resolution
Resolve an OPEN entry only with explicit evidence or an explicit accepted-risk decision. Do not delete the original concern. Link the resolving entry, commit, test, benchmark, amendment or review.

## 4. Gate pattern

A useful harness gate should be narrow:

- validate structure and provenance;
- fail on missing mandatory fields or contradictory states;
- prevent named production steps when a material OPEN blocker explicitly lists them;
- allow smoke tests, exploratory benchmarks and plumbing work needed to resolve blockers;
- never infer scientific validity solely from process compliance.

This avoids both extremes: process theatre and uncontrolled experimentation.

## 5. Computational feasibility pattern

When a frozen method appears too expensive:

1. record the concern before seeing outcome-bearing results;
2. benchmark at a non-outcome scale;
3. identify the dominant operation;
4. optimize only implementation details when possible;
5. add equivalence tests against the reviewed reference algorithm;
6. preserve RNG, sampling, tie rules, estimands, intervals and stopping rules if they are frozen;
7. if those must change, create a versioned methodological amendment rather than calling it optimization.

Runtime, memory and storage constraints are part of the scientific record when they influence which experiment can actually be executed.

## 6. Hard scientific principles to preserve

- Falsifiable claims rather than success-oriented narratives.
- Negative results and failed gates remain visible.
- Sampling unit matches the inferential unit.
- Train/validation/test boundaries are explicit and immutable after execution begins.
- Data/source versions and hashes are recorded.
- Degenerate replicates or failed observations are not silently redrawn.
- Hyperparameter, seed or subgroup selection after seeing outcomes is disclosed.
- Multiple-comparison or model-selection effects are addressed when relevant.
- Confidence intervals and uncertainty procedures are defined before result inspection when used for decisions.
- External validity is not inferred from benchmark validity.
- Engineering feasibility and scientific evidence are separate evidence planes.
- Reviewer criticism is evidence about the process, not something to erase from the final narrative.
- Reproducibility includes both executable artifacts and decision context.

## 7. CAL + MMALS replay + chronicle

A useful division of responsibility is:

- **MMALS replay:** can the experiment and evidence chain be reconstructed?
- **CAL:** is a bounded claim admissible given the declared evidence and gates?
- **Scientific chronicle:** why did the study evolve this way, what was doubted, what changed, and what remains unresolved?

These layers should cross-link but not collapse into one score or one generic maturity label.

## 8. Pedagogy: Diderot / Fabric-inspired layer

Pedagogical artifacts may progressively expose the same research object at several depths:

- one-sentence claim and decision;
- intuitive mechanism;
- experiment diagram;
- mathematical estimand;
- uncertainty method;
- code/replay path;
- reviewer challenge;
- unresolved question.

A Fabric-like approach can make these explanations composable: claim card, method card, evidence card, failure card, reviewer card, replay card, decision card. A Diderot-like approach can expose them progressively to readers with different backgrounds.

The authoritative facts still live in protocols, evidence, hashes and chronicle entries. Pedagogy must reference them rather than fork them.

## 9. Stronger provenance options

Git history is useful provenance but does not by itself provide cryptographic non-repudiation of identity. Projects needing stronger guarantees may add:

- signed commits or signed release tags;
- immutable release bundles;
- timestamped external archives;
- transparency logs or append-only object stores;
- independent replication repositories.

The strength of provenance claimed in documentation must match the mechanism actually deployed.

## 10. Project bootstrap checklist

Before the first outcome-bearing run, verify:

- [ ] bounded research question and excluded claims exist;
- [ ] primary estimand and sampling unit are explicit;
- [ ] controls are frozen;
- [ ] data/split/version policy is frozen;
- [ ] uncertainty and stopping rules are frozen;
- [ ] claims and gates are machine-readable;
- [ ] replay/environment policy exists;
- [ ] chronicle is append-only and has a pre-outcome entry for material known risks;
- [ ] negative outcomes have an explicit publication/retention policy;
- [ ] execution preflight blocks unresolved named blockers;
- [ ] pedagogical artifacts, if any, link to authoritative sources;
- [ ] no process artifact is allowed to substitute for empirical evidence.

This checklist is a starting harness, not a certification standard. It should evolve through use, reviewer criticism and independent replication.
