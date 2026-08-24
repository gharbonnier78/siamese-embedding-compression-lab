# Study 1A — Frozen overlap / duplicate audit design

Status: `FROZEN_PREOUTCOME_DESIGN`

Date: 2026-08-24

## Purpose

This is a proportional pre-outcome control for the compression-focused Study 1A. It does not certify the benchmark datasets and it does not inspect verification outcomes. Its purpose is to prevent obvious leakage, accidental duplication, or outcome-conditioned filtering from invalidating the substrate sanity qualification or the later matched compression comparison.

## Scope

The audit is applied to every locally materialized Study 1A benchmark role before its scientific metrics are interpreted. The same frozen dataset/protocol identities are then reused by all later compression routes.

The audit MUST NOT use similarity scores, verification errors, benchmark pass/fail results, or any other scientific outcome to decide which records to retain.

## Required manifest fields

For every materialized image/capture, retain where legally and practically available:

- dataset name and version/source revision;
- official protocol / fold identifier;
- stable local record id;
- source file or capture id;
- cryptographic content hash of the raw bytes;
- subject/identity id or a privacy-preserving stable surrogate when the official protocol exposes one;
- template id when the benchmark is template based;
- declared role (`sanity`, `difficult_reproduction`, later `train`, `validation`, `test`, etc.);
- decode/alignment status and any frozen exclusion reason.

The complete manifest is content-hashed before outcome-bearing execution.

## Exact duplicate check

Exact duplicate detection is based on the cryptographic hash of the raw image/capture bytes. Repeated content is reported with all dataset/protocol roles in which it appears.

A duplicate is not silently deleted. Its disposition follows the official benchmark protocol. Any deviation requires a pre-outcome protocol amendment.

## Near-duplicate check

Where raw images are available and the dataset terms permit local analysis, a deterministic near-duplicate method MUST be selected and versioned before benchmark outcomes are opened. The method may use a perceptual image hash or another image-space technique that does not depend on the candidate verification scores under study.

The method, implementation version, threshold and known limitations are frozen in the dataset evidence pack before outcomes. Near-duplicate flags are diagnostic unless the official protocol or a preregistered rule requires exclusion.

## Identity / template overlap

When stable identity or template labels are available, the audit reports identity/template overlap across declared data roles. In particular:

- training/fitting data for PCA or Siamese MUST NOT contain qualification/test identities when the declared split is identity-disjoint;
- no test identity may be moved to another role after looking at route performance;
- repeated identities within an official verification protocol are preserved and handled by identity/dependence-aware uncertainty rather than falsely treated as independent samples.

For Study 1A public reproduction benchmarks, official folds/protocols remain authoritative. The audit diagnoses overlap; it does not rewrite the benchmark.

## Cross-dataset overlap

Where legally and practically possible, exact raw-content hashes and stable identity surrogates are compared across locally used datasets. Known lineage (for example LFW-derived challenge sets) is documented rather than interpreted as automatically invalid.

A cross-dataset overlap finding is reported before interpreting the combined evidence. It does not authorize post-hoc removal.

## Failure and exclusion semantics

Decode, detection, alignment, multi-face, corrupt-file and other input failures are retained in the evidence pack with stable record ids and reasons. No failure class may be silently dropped because removing it improves a benchmark score.

## Required pre-outcome evidence

Before Study 1A benchmark interpretation, the execution pack must contain:

1. dataset/protocol manifest and SHA-256;
2. exact-duplicate report;
3. near-duplicate method/version/threshold or a justified `not_applicable` / `not_permitted` disposition;
4. identity/template overlap report where identifiers permit it;
5. frozen exclusion/failure semantics;
6. explicit statement that no scientific metric was consulted when constructing the reports.

## Boundary

This is a leakage-control design for a research POC. It is not a forensic dataset certification, demographic audit, biometric product certification, or proof that no historical training overlap exists in WebFace12M. Such questions may be studied separately if they become decision-relevant.
