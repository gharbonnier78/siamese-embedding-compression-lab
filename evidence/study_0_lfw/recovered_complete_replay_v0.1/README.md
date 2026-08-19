# Recovered complete Study 0 replay — archival record

On 2026-08-19 the complete historical Study 0 MMALS replay archive was recovered from a ChatGPT conversation attachment after earlier temporary sandbox paths were no longer accessible.

Recovered archive identity:

- historical run: `lfw_resnet18_siamese_projection_v0_1-89179914-911192ee-64559cbd`
- filename: `lfw-resnet18-siamese-projection-v0.1-mmals-replay.zip`
- bytes: `4,158,610`
- SHA-256: `7429c75a7da827281ca172d7a4184c65fcc27dbfa845eb9ffd27e04d81331897`
- members: 40
- `test_pair_scores.csv`: 1,821,547 bytes

The archive listing was checked for `run_manifest.json`, `test_pair_scores.csv`, `thresholds.csv` and `paired_noninferiority.csv`. The ZIP digest exactly matches the release checksum preserved from the original Study 0 delivery.

## Durable backup

A separate durable binary copy was created as a Gmail draft attachment on 2026-08-19 together with the recovery JSON manifest. The machine-readable recovery record in `recovery_manifest.json` stores the draft and message identifiers so the binary can be recovered without relying on a transient ChatGPT sandbox path.

The binary itself is deliberately not added to Git through this archival-record PR because the available repository connector accepts UTF-8 repository files rather than direct binary release assets. A future release-asset publication may copy the exact verified ZIP without recomputation.

## Scientific boundary

This archival recovery did **not** inspect or interpret historical score values. No scientific claim, gate, `E-STAT-001` status, G2 status, Study 1 status or geometry work is changed by this recovery record.

The recovered archive may only be exercised under the separately reviewed `corrected_study_0_reanalysis` authorization and merged runner, including the required preflight and complete-before-interpretation boundary.
