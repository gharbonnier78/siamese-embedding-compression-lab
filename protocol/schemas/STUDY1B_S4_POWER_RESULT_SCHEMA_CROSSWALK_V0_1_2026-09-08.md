# Study 1B S4 power-result schema crosswalk v0.1

Date: 2026-09-08

Status: prospective consumer guidance only. Historical S4N1/S4N2 result artifacts remain unchanged and append-only.

## Historical defect

The packaged raw JSON summaries for S4N1 and S4N2 both use `schema_version: 1` as an integer, but they are not the same machine-readable schema. A consumer must not select one shared parser solely from that field.

## Package-side discriminator

Use `kind`, which is present in the raw JSON:

| Level | S4N1 | S4N2 |
|---|---|---|
| Root | `study1b_s4n1_core_power_calibration_4000` | `study1b_s4n2_dagjk20_power_calibration_4000` |
| Truth-cell summary | `study1b_s4n1_core_power_summary` | `study1b_s4n2_core_power_summary` |

The Chronicle YAML records additionally expose distinct `entry_type` values, but `entry_type` is not present in the packaged raw JSON summaries and therefore is not a valid package-side discriminator.

## Field crosswalk

| Concept | S4N1 field | S4N2 field |
|---|---|---|
| Overall candidate pass map | `candidate_power_pass_both_truths` | `candidate_pass_both_truths` |
| Coverage numerator | `covered` | no same-named field |
| Empirical coverage | `empirical_coverage` | `two_sided_empirical_coverage` / `upper_empirical_coverage` |
| Coverage lower CP bound | `lower_95_clopper_pearson` | `two_sided_cp95_lower` / `upper_cp95_lower` |
| Validation optimism | `mean_validation_optimism` | no same result-field equivalent |
| Point-error SD | no same S4N1 result field | `point_error_sd` |
| DAGJK SE summaries | not applicable | `dagjk_se_mean`, `dagjk_se_median` |

## Important S4N1 reading note

`lower_95_clopper_pearson` in the archived S4N1 result is a lower Clopper-Pearson bound for empirical **coverage**, not for power. It must not be interpreted as a confidence bound on `estimated_power`.

The historical result is not renamed because it is closed append-only. Future result schemas should use names that encode the estimand directly.

## Forward schema policy

Future S4-like result artifacts must:

1. use a schema identifier that distinguishes the result family, not only a generic integer version;
2. preserve `kind` or an equivalent explicit family discriminator in raw machine-readable artifacts;
3. name confidence-interval fields with the quantity they bound, for example `power_cp95_*` versus `coverage_cp95_*`;
4. publish a migration/crosswalk whenever a field is renamed or split;
5. never rewrite the historical S4N1/S4N2 closed results to retrofit the new schema.
