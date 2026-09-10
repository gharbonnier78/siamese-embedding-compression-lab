# PR #50 supplemental independent review — package v3 confirmation

Date: 2026-09-08

Status: supplemental review evidence; **no new final benchmark-design verdict issued**.

Reviewed transport package:
`PR50_A00DE7BF_TARGETED_REREVIEW_PACKAGE_V3_2026-09-08.zip`

Reviewer-confirmed package SHA-256:
`823709fb47decfb646bff23900f9348435b0df8e6540397fe1c0cc272182bffe`

## Confirmed transport integrity

The reviewer confirmed:

- SHA-256 matches the announced value;
- 19 files are present;
- 18/18 non-manifest files are covered by the internal checksum manifest;
- relative to v2, only `18_REVIEWER_NOTE_RESULT_SCHEMA_CROSSWALK.md`, `15_SOURCE_MANIFEST.json`, and `16_PACKAGE_SHA256.json` changed;
- the remaining sixteen files are byte-identical, including the raw S4 artifacts, extracted JSON, environment lock, Chronicle files, clarification, append-only evidence, note 17, and README;
- no scientific artifact changed in the transport revision.

## Confirmed reading-note corrections

The reviewer independently confirmed that the packaged raw JSON uses integer `schema_version: 1` in both S4N1 and S4N2, not string `"1.0"`.

The package-side discriminator is `kind`, with the following exact values:

| Level | S4N1 | S4N2 |
|---|---|---|
| Root | `study1b_s4n1_core_power_calibration_4000` | `study1b_s4n2_dagjk20_power_calibration_4000` |
| Truth-cell summary | `study1b_s4n1_core_power_summary` | `study1b_s4n2_core_power_summary` |

The reviewer also confirmed that `entry_type` is absent from the packaged JSON and is correctly described only as a repository Chronicle-YAML discriminator.

The field crosswalk was checked assertion-by-assertion against the packaged artifacts and found consistent, including negative assertions such as S4N2 lacking S4N1 `covered`, and S4N1 lacking S4N2 `point_error_sd` / `dagjk_se_*`.

## Previously established points retained

- append-only path history for the closed S4N1/S4N2 result paths is accepted as sufficient to exclude modify/revert;
- the S4 negative closures do not depend on resolving the causal explanation of the S4N1-to-S4N2 power difference;
- reviewer-side power confidence intervals are not to be misattributed to archived S4 result fields;
- any formal S4N1-versus-S4N2 pass-rate comparison would need paired per-dataset indicators because both procedures reuse the same synthetic population;
- schema collision is a prospective consumer/schema-governance correction, not a reason to rewrite closed artifacts.

## Remaining open blocker at the reviewed head a00de7bf

The reviewer confirmed that the remaining material gap is the provenance of **lock-defining configuration decisions**. The v0.1 environment lock captured result provenance and blocked runtime substitution/tuning, but did not explicitly require provenance for the choices that selected hardware, backend, threading, power mode, or energy-measurement setup, and did not make the guard label-independent across smoke tests, pilots, Phase 0, exploratory runs, or equivalent target-workload previews.

This supplemental review therefore does **not** upgrade the prior verdict to `ACCEPT_ENGINEERING_BENCHMARK` on head `a00de7bf`.

## Required next action

Address the pre-lock configuration-choice provenance gap prospectively in a new benchmark/environment-lock version, keep S4 closed artifacts untouched, run assurance on the new head, publish a new immutable review binding, and obtain a fresh independent verdict before canonical Phase A execution.
