# Experiment history, replay and errata policy

## Non-negotiable rule

An executed study is an immutable historical object. A later study, better implementation,
corrected estimator or revised belief may supersede a conclusion, but must never delete,
rewrite or silently summarize away the earlier experiment or its errors.

## Required preservation unit

Every executed study must retain or reference, under a permanent study identifier:

1. frozen preregistration and resolved configuration;
2. source commit and implementation digest;
3. dataset version, acquisition method, allowed redistribution and file hashes;
4. split construction, pair/identity counts and split hashes;
5. model/projection artifacts required for replay;
6. per-trial or minimally sufficient scores required to recompute estimators;
7. thresholds, metrics, uncertainty outputs and all declared seeds;
8. event stream, audit trace and artifact manifest;
9. original report and PDF exactly as published;
10. every later erratum, reanalysis and changed claim state as a linked new record.

Private or licence-restricted material may live in a controlled release bundle rather than
Git, but its content digest, retrieval instructions and availability status must remain in
the public ledger. An aggregate evidence snapshot is not called a complete replay bundle.

## Append-only correction model

Corrections use a stable erratum ID and record:

- discovery date and affected run/claim/gate;
- exact declared behaviour and exact implemented behaviour;
- affected artifacts and numbers;
- what remains valid and what becomes inadmissible or indeterminate;
- correction plan and status;
- links to both the original and corrected analyses.

The original CSV, PDF and decision remain addressable. Corrected values are written to new
files with a new analysis identifier; they do not replace historical rows.

## Reproduction across study generations

Study `k+1` may reuse code from Study `k`, but may not make Study `k` depend on later mutable
defaults. Each study must remain runnable from its frozen configuration and source revision.
CI validates the ledger and smoke contract on the active branch. Tagged releases bind the
source commit, paper, replay bundle and their hashes. Independent reproduction uses the
study-specific tag or commit, never the current defaults of a later study.

## Status vocabulary

- `ORIGINAL_EXECUTION`: the exact historical computation.
- `KNOWN_DEFECT`: a discovered mismatch preserved in an erratum.
- `REANALYSIS_PLANNED`: correction specified but not executed.
- `REANALYSIS_EXECUTED`: new immutable analysis linked to the original.
- `SUPERSEDED_FOR_CLAIM`: original evidence retained but no longer admissible for a claim.

An error is scientific evidence about the process. It is neither hidden nor promoted into a
result it cannot support.
