# Numerical cross-check after independent review — v0.2.3

This note addresses the two items the independent reviewer explicitly marked as not previously recalculated: the historical descriptive Table 6 values and the TEST-optimized ~70% diagnostic accuracies.

## Source archive identity

The immutable replay archive used for this supplementary cross-check is:

`lfw-resnet18-siamese-projection-v0.1-mmals-replay.zip`

SHA-256:

`7429c75a7da827281ca172d7a4184c65fcc27dbfa845eb9ffd27e04d81331897`

Size:

`4,158,610 bytes`

This matches the archive identity cited in the manuscript.

## Historical descriptive metrics — Table 6

Directly reading `method_summary.csv` from that immutable replay archive gives the following `test_equal_fmr_benchmark` means at target FMR 0.01:

| Route | FNMR mean | ROC AUC mean | EER mean |
|---|---:|---:|---:|
| Raw 512D | 0.8060 | 0.7930640 | 0.2890 |
| PCA 128D | 0.8216 | 0.8057856 | 0.2704 |
| Random 128D | 0.8416 | 0.7726480 | 0.3104 |
| Siamese 128D | 0.8288 | 0.8167208 | 0.2662 |

These round exactly to the values printed in the manuscript.

## TEST-optimized diagnostic accuracy

Using the immutable `test_pair_scores.csv`, for each route/seed the observed TEST distance thresholds were searched under the rule `match iff distance <= threshold`, selecting the threshold maximizing TEST pair-classification accuracy.

This is intentionally **TEST-tuned and non-deployable**; it is only the diagnostic context described in the paper.

| Route / seed | Maximum TEST accuracy |
|---|---:|
| Raw seed 11 | 0.715 |
| PCA seed 11 | 0.741 |
| PCA seed 29 | 0.742 |
| PCA seed 47 | 0.743 |
| PCA seed 71 | 0.743 |
| PCA seed 101 | 0.742 |
| Siamese seed 11 | 0.739 |
| Siamese seed 29 | 0.742 |
| Siamese seed 47 | 0.735 |
| Siamese seed 71 | 0.747 |
| Siamese seed 101 | 0.730 |
| Random seed 11 | 0.692 |
| Random seed 29 | 0.709 |
| Random seed 47 | 0.693 |
| Random seed 71 | 0.714 |
| Random seed 101 | 0.693 |

Therefore the manuscript shorthand is confirmed:

- raw: **71.5%**
- PCA: **74.1–74.3%**
- Siamese: **73.0–74.7%**
- random: **69.2–71.4%**

These values are not the primary endpoint and must not replace the frozen low-FMR non-inferiority analysis.

## Evidence status

This note is a supplementary numerical consistency check. It does not reopen Study 0, change any scientific gate, or add a new claim. The final independent paper-review verdict is archived separately in `paper/REVIEW_v0.2.3_2026-08-20.md`.
