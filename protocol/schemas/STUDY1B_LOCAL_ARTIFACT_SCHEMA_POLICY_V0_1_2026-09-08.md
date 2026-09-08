# Study 1B local artifact schema policy v0.1

Date: 2026-09-08
Status: prospective local schema-governance rule; historical closed artifacts are not rewritten.

## Purpose

Prevent a generic `schema_version` field from being treated as a cross-family discriminator.
The prior S4 review showed that different artifact families can legitimately have different shapes while
sharing a version token, and that type inconsistency (`1` integer versus `"1.0"` string) creates avoidable
consumer ambiguity.

## Prospective rule

New local Study 1B machine-readable artifacts created after this policy MUST declare:

- `schema_id`: a stable family identifier;
- `schema_version`: an integer scoped to that `schema_id`;
- `artifact_version`: a human-facing version string when the artifact itself is versioned.

A consumer MUST select a parser from `schema_id` first and MUST NOT infer compatibility across distinct
families from `schema_version` alone.

## Current examples

- `study1b.engineering.environment_lock`, `schema_version: 2`
- `study1b.engineering.benchmark_addendum`, `schema_version: 1`
- `study1b.chronicle.review_result`, `schema_version: 1`

## Historical compatibility

Historical S4N1/S4N2 results, benchmark v0.3, environment lock v0.2, Chronicle 041, and other already-recorded
artifacts retain their original schema declarations. This policy does not authorize retrospective rewrites.

`harness-adoption.yaml` follows the pinned harness repository's manifest family and is not silently retyped by
this local policy. If the upstream harness changes that schema, the consumer should adopt it through an explicit
harness upgrade rather than a local incompatible edit.
