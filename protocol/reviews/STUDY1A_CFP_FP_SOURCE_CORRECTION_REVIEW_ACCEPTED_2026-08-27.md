# Study 1A CFP-FP source-correction replay — independent review accepted

Status: `ACCEPT_CORRECTION`  
Scope: Study 1A substrate qualification only  
Study 1B authorization: **NO**

Canonical PR under review:  
https://github.com/gharbonnier78/siamese-embedding-compression-lab/pull/46

Reviewed PR head: `fd3c607f592a07fc7fb0f2e33bc449533eb542c0`  
Maintenance-fix commit reviewed: `21a8f1715fa7f94c1edd7dd05fef2bfa1c11d0a3`  
Branch: `agent/study1a-go-preexecution-20260824`

## Independent verification summary

The independent reviewer confirmed:

1. PR #46 target and head identity, with the maintenance fix as an ancestor.
2. Author-managed CVLFace toolkit provenance is materially stronger than the diagnostic transport mirrors for the source-correction decision.
3. The protected toolkit is accessed through a GitHub Actions secret without recording or redistributing the password.
4. CFP-FP transport is a container conversion only: author PIL RGB pixels -> lossless PNG -> frozen cv2 BGR decode, with no scientific image transformation.
5. Checkpoint and AdaFace source pin are unchanged:
   - checkpoint SHA-256 `0e7a3238d2a50f3fe3860782534928ac7cb2598977cf897f6869fd5ac2493fd0`
   - AdaFace commit `c60eaa786a42c03444f3df7096dbaf9d57ae010d`
6. Frozen evaluator semantics and CFP-FP threshold remain unchanged.
7. Corrected CFP-FP result passes the frozen gate:
   - observed mean `0.9924285714285717` = 99.242857%
   - std `0.002478478796128225`
   - frozen minimum `0.9896` = 98.96%
8. The reviewer independently recomputed the mean and standard deviation from the 10 fold accuracies and obtained values consistent with the recorded result (rounding-only difference from shortened fold values).
9. The red conclusion of GitHub Actions run `33003912752` is attributable to the post-outcome JSON field-path bug in decision-record generation, after the scientific benchmark had completed successfully.
10. Commit `21a8f171...` corrects only that post-processing lookup and makes the correction workflow manual-only, preventing silent outcome-bearing reruns.
11. The original Icar-based CFP-FP result is retained as historical evidence rather than deleted or rewritten.
12. No Study 1B authorization is present. The reviewer explicitly confirmed that accepting this correction does not authorize Study 1B, production use, biometric certification, fairness/PAD/1:N claims, or representation-geometry work.

The reviewer also executed:

`PYTHONPATH=src python -m unittest tests.test_study1_execution`

Result: `8/8 OK`.

## Reviewer limitation and repository-side corroboration

The independent reviewer could not directly verify, from their unauthenticated environment, GitHub Actions run `33003912752` or artifact `9622506401` / ZIP digest `068a6de98f9aedd0b9b15f7de4568b61845b33ecef37b8e37305673c306ff211` because of GitHub API rate limits. This was explicitly reported as `NOT_VERIFIED`, not silently upgraded to confirmation.

Repository-side authenticated inspection separately established that:

- the scientific replay step completed successfully;
- the workflow failed only at decision-record generation with `TypeError: '>=' not supported between instances of 'NoneType' and 'float'` after reading the wrong JSON field;
- the compact evidence artifact was uploaded successfully as artifact `9622506401` with ZIP SHA-256 `068a6de98f9aedd0b9b15f7de4568b61845b33ecef37b8e37305673c306ff211`.

These repository-side facts are supporting evidence and are kept distinct from what the independent reviewer personally verified.

## Verdict

`ACCEPT_CORRECTION`

The author-managed CFP-FP replay is accepted as the corrected source for the bounded Study 1A substrate-qualification decision. The corrected CFP-FP result may supersede the Icar-based CFP-FP result for that decision, while the original result remains immutable historical evidence.

This acceptance revises only Study 1A substrate qualification. It does **not** authorize Study 1B. A separate explicit human GO remains required before any Study 1B outcome-bearing execution.

## Non-blocking item before merge

The PR description must reflect the full chronology now present on the branch — pre-execution controls -> authorized A1/A2 execution -> CFP-FP source diagnostic -> author-managed source correction -> independent acceptance — rather than describing the PR as pre-execution only.
