# Scientific Chronicle & Reproducibility Harness

Status: **living project-level scientific governance artifact**

This document defines a secondary scientific harness for this research programme. It does not replace study protocols, code, result artifacts, preregistrations, CAL gates, or MMALS replay. Its role is to preserve the reasoning context that is otherwise easy to lose: doubts, assumptions, computational constraints, alternatives considered, rejected approaches, reviewer challenges, changes of belief, and the exact reason a methodological or engineering choice was made.

## 1. Why this exists

A reproducible experiment should preserve more than final code and numbers. Future reviewers must also be able to reconstruct:

- what was believed before an observation was seen;
- what was uncertain;
- which alternatives were considered and rejected;
- which decisions were methodological versus implementation-only;
- when computational, data, tooling, or operational constraints were discovered;
- whether a change was made before or after seeing outcome-bearing evidence;
- which negative or inconvenient findings were retained;
- how reviewer criticism changed the work;
- which questions remain open.

This chronicle is therefore part of the research evidence chain, but it is **not outcome evidence**. A chronicle entry cannot make a claim true, close a statistical gate, or substitute for an experiment.

## 2. Core principles

### 2.1 Non-repudiating chronology
Entries are append-only. Incorrect or superseded entries are not silently rewritten; they receive a linked correction or superseding entry. Git history is part of the provenance record.

### 2.2 Pre-outcome versus post-outcome separation
Every entry must state whether outcome-bearing evidence had already been inspected when the decision, doubt, or proposal was recorded. A methodological change after outcome inspection must be explicit and versioned; it must never be represented as preregistered.

### 2.3 Falsifiability over narrative convenience
Negative results, failed gates, degeneracies, infeasible computational plans, and reviewer objections are first-class records. The purpose is not to create a success story but to preserve an inspectable sequence of claims, tests, failures, revisions, and residual uncertainty.

### 2.4 CAL boundary
CAL governs admissibility of bounded claims and remains separate from this chronicle. Chronicle entries may explain why a CAL outcome changed, but cannot themselves yield ADMISSIBLE, INADMISSIBLE, or INDETERMINATE.

### 2.5 MMALS replay boundary
MMALS replay preserves executable and artifact-level reproducibility. The chronicle complements replay by preserving the decision context around the executable record. Where possible, chronicle entries link directly to replay artifacts, commits, manifests, issues, PRs, tests, and reviewer evidence.

### 2.6 Immutable evidence and linked errata
Original outputs are never overwritten to make later methodology look cleaner. Corrections create new records, linked errata, and explicit status transitions.

### 2.7 Computational proportionality is scientific information
Runtime, memory, storage, numerical stability, and scaling doubts must be recorded when they can affect feasibility, representativity, or methodological choices. Optimizations are acceptable only when they preserve the frozen estimand and algorithmic semantics, or when a methodological amendment is explicitly declared.

### 2.8 No silent optimization-driven methodology drift
Performance engineering may change implementation structure but must not silently change sampling unit, random-number semantics when frozen, threshold/tie rules, estimands, confidence-interval construction, stopping rules, scenario definitions, or gate thresholds. Equivalence tests are required when an implementation is optimized after a reference implementation has been reviewed.

### 2.9 Pedagogical traceability
Important conceptual transitions should be explainable at more than one level without changing the underlying claim. The project may maintain explanatory artifacts inspired by Diderot-style progressive exposition and Fabric-style composable learning/reasoning artifacts. These pedagogical layers must link back to the same authoritative protocol, evidence, and chronicle entries rather than invent parallel facts.

### 2.10 Bounded role of AI assistance
AI-generated suggestions, code, critiques, or summaries are treated as proposed work, not authority. Material methodological changes require explicit review, tests, and provenance. The chronicle should record consequential AI-assisted decisions in the same way as human suggestions when they materially alter the research path.

## 3. What must be chronicled

A new entry is required when any of the following materially affects a study or its interpretation:

1. a new scientific or engineering doubt;
2. an assumption is added, weakened, rejected, or discovered to be false;
3. a reviewer identifies a non-trivial gap;
4. a gate fails or its interpretation changes;
5. a computational feasibility issue may alter execution strategy;
6. an implementation optimization touches statistically sensitive logic;
7. a data source, hash, split, mapping, or representativity issue is discovered;
8. a methodological alternative is seriously considered and rejected;
9. a claim, prior, or expected result changes;
10. an unexpected negative result or degeneracy occurs;
11. a preregistered choice requires amendment;
12. evidence is unavailable, stale, incomplete, or impossible to reproduce;
13. a pedagogically important conceptual clarification materially changes how the study is understood.

Trivial lint fixes, formatting-only edits, and routine dependency bumps do not need chronicle entries unless they unexpectedly affect reproducibility.

## 4. Required fields

The machine-readable chronicle is `protocol/scientific_chronicle.yaml`. Each entry contains at least:

- `id` — immutable unique identifier;
- `recorded_at_utc` — timestamp;
- `scope` — programme or study identifier;
- `kind` — doubt, decision, reviewer_finding, cost_risk, amendment, negative_result, evidence_gap, pedagogical_note, or similar;
- `status` — OPEN, RESOLVED, SUPERSEDED, ACCEPTED_RISK, or INFORMATIONAL;
- `outcome_evidence_seen` — true/false;
- `summary` — concise statement;
- `rationale` — why it matters;
- `evidence_refs` — links/paths/commits/tests supporting the entry;
- `next_action` — required for OPEN entries;
- `blocks` — explicit study/gate/execution step blocked, if any;
- `supersedes` / `superseded_by` where relevant.

## 5. Gate policy

Research Assurance fails if:

- the chronicle file is missing or does not declare append-only policy;
- chronicle IDs are duplicated;
- a required field is absent;
- an OPEN entry has no `next_action`;
- an entry with non-empty `blocks` is marked INFORMATIONAL;
- a post-outcome methodological change is represented as preregistered;
- the programme does not declare this harness in its reproducibility section.

A production execution preflight must block a named step while an OPEN chronicle entry explicitly lists that step in `blocks`, unless a versioned resolution or accepted-risk entry supersedes it.

## 6. Relationship to study artifacts

The intended evidence stack is:

**claim / hypothesis → preregistration → implementation → tests → immutable run evidence → MMALS replay → CAL admissibility → scientific chronicle → pedagogical exposition**

Later layers cannot repair missing evidence in earlier layers. The chronicle and pedagogical artifacts explain and preserve context; they do not manufacture statistical support.

## 7. Current Study 0 v0.2.2 rule

The production coverage gate must not be executed while the recorded computational-feasibility risk around the nested subject-bootstrap simulation remains OPEN. Acceptable resolution is either:

- demonstrate that the reviewed implementation is feasible at the frozen production scale; or
- optimize the implementation with semantics-preserving equivalence tests against the reviewed reference algorithm.

Reducing the preregistered number of bootstrap replicates or scenarios merely for runtime convenience is not semantics-preserving and requires a versioned methodological amendment.
