# Study 0 evidence snapshot

This directory is a deliberately small, versioned projection of the immutable MMALS replay
bundle for run:

`lfw_resnet18_siamese_projection_v0_1-89179914-911192ee-64559cbd`

It contains the tabular evidence needed to regenerate the paper figures and check their
interpretation. It does **not** contain LFW images, cached face features, learned models or
the complete pair-score table. Consequently, this snapshot supports figure regeneration
and evidence review; it is not a substitute for the complete replay bundle when independently
re-executing the experiment.

The source files are copied without numerical rewriting from the v0.1 replay bundle. The
figure generator records their SHA-256 digests in
`paper/figures-generated/figures_manifest.json`. CI regenerates the figures and fails if a
committed paper snapshot has drifted from these sources.

Key files:

- `method_summary.csv`: descriptive FNMR, FMR, ROC AUC and EER summaries;
- `paired_noninferiority.csv`: seed-level paired FNMR differences and confidence intervals;
- `method_noninferiority_summary.csv`: method-level robustness decisions;
- `storage_engineering.csv`: template-payload arithmetic only;
- `split_summary.csv`: pair, identity and split-digest summary;
- `routes.csv`: route dimensions, parameters and execution status;
- `thresholds.csv`: validation-fitted operating thresholds;
- `training_history.csv`: observed Siamese projection optimisation history;
- `audit_trace.jsonl` and `run_manifest.json`: audit decisions and provenance.

The authoritative complete artifact is the release-level MMALS replay bundle. A tagged
release must publish that bundle, its digest, this paper PDF and the corresponding source
commit together.
