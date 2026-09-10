# Study 1B — focused re-review request for D2 repository-root bound and D1/D2 responsibility split

Date: 2026-09-10  
Scope: non-outcome engineering provenance / temporal-firewall design only

## Required immutable navigation

- Repository: https://github.com/gharbonnier78/siamese-embedding-compression-lab
- Pull request: https://github.com/gharbonnier78/siamese-embedding-compression-lab/pull/50
- Base: https://github.com/gharbonnier78/siamese-embedding-compression-lab/commit/5730e6bfa07b51afbe7ad6a89ffb4a6bd0ba6eb7
- Material design head before this review-request-only commit: https://github.com/gharbonnier78/siamese-embedding-compression-lab/commit/7fb6dda245598306e7b4a80c12ba7ee9ec19f97d
- Pinned harness: https://github.com/gharbonnier78/scientific-research-harness/blob/3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98/HARNESS.md
- Root commit proposed as D2 public-information bound: https://github.com/gharbonnier78/siamese-embedding-compression-lab/commit/4b40e7254bff1b88a44d13fb55b366bc7d3fc263
- Root README: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/4b40e7254bff1b88a44d13fb55b366bc7d3fc263/README.md
- Bounded backward audit: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/f6f6ac47df5a73bbd417b028e823e91964f708fd/protocol/reviews/PR50_D2_BOUNDED_BACKWARD_HISTORY_AUDIT_2026-09-10.md
- Environment lock v0.5 creation commit: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/050ae1a62e181f429a4808a74670f00bd7ae59a7/protocol/benchmarks/STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_ENVIRONMENT_LOCK_V0_5_2026-09-10.yaml
- Focused tests commit: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/857303e44fe8d2b520d995fc6da6f0f84acdf0e3/tests/test_study1b_engineering_benchmark_contract.py
- Harness binding commit: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/8b9d843faf14f3c28e0703b346cd38d568725d8f/harness-adoption.yaml
- Chronicle 046: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/7fb6dda245598306e7b4a80c12ba7ee9ec19f97d/protocol/chronicle/STUDY1B_PR50_D2_ROOT_BOUND_V0_5_REREVIEW_OPEN_2026-09-10.yaml
- Prior exact reviewer verdict preserved as issued: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/734d7f4ac7c70dc1d1fe1d2a10c3bf1dec0fb0cb/protocol/reviews/PR50_022E8F_D2_CLOSURE_VERDICT_2026-09-10.md
- Repository-side audit that reopened D2: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/eeba457334c7290d8a6f7ba5cfbd222fcd77b078/protocol/reviews/PR50_022E8F_D2_ANCHOR_REPOSITORY_AUDIT_2026-09-10.md

A PR comment will bind the exact final review head after assurance. If the head moves after that binding, the review does not carry forward automatically.

## Why this re-review exists

The previous focused reviewer returned `ACCEPT` and `D2_CLOSED: yes` on head `022e8f...`, while explicitly stating that closure depended on an author-supplied repository fact they could not verify: that `878bfe2a...` was the earliest relevant workload publication. The reviewer also stated that if materially informative repository content existed earlier, D2 would reopen.

Repository inspection then found earlier relevant content and D2 was reopened append-only. No reviewer wording was rewritten.

The bounded backward audit now reaches the repository root commit `4b40e725...`, whose Git commit has no parents. Its README already publishes the 512D-versus-128D engineering intervention, float32 template-storage comparison, and a future engineering gate covering 1:N retrieval, gallery indexing and latency measurements.

The proposed v0.5 lock therefore uses repository inception as a deliberately conservative public-information bound rather than trying to identify the first later commit containing every final Phase A detail.

## Review question A — is the root a defensible conservative D2 public-information bound?

Please assess whether the following reasoning is sound for the limited provenance purpose:

1. the relevant D2 question is when repository-public information first became sufficient that a repository-informed prior measurement could plausibly become materially informative for later lock-defining choices;
2. every final Phase A field need not already have been frozen for a prior measurement to be informative;
3. the root README already publishes 512D vs 128D plus retrieval/storage/latency engineering intent;
4. because the root commit has zero parents, no earlier repository commit can exist;
5. requiring D2-qualifying external evidence to be strictly earlier than the root is conservative and mechanically terminal;
6. the cost of this conservatism is acceptable: it may reject genuinely uninformed later evidence, but it avoids a late public anchor that creates a permissive window.

This is **not** a claim that the exact later CPU/G0/G2/threading/power Phase A contract existed at repository inception. v0.5 explicitly records that it did not.

## Review question B — does the D1/D2 responsibility split close the public-vs-private knowability gap?

v0.5 now states explicitly:

- D2 ordering may discharge only genuinely third-party or pre-existing external evidence whose provenance strictly predates the repository public-information bound and is independent of production/commissioning by the attesting party;
- D1 accountable attestation carries evidence produced, commissioned, requested, reviewed, received or otherwise known by the attesting party, even if it predates public commit time;
- ambiguous evidence requires D1 and is treated as potentially informative;
- the public anchor never substitutes for D1 attestation.

Please assess whether this correctly implements the reviewer observation that public commit time bounds public knowability, not the author's private knowability.

## Explicitly out of scope

This request does **not** ask the reviewer to reopen or assess:

- Study 1B SCREEN or qualification TEST;
- real raw512/random128/PCA128/Siamese128 performance;
- representation geometry;
- S4N1/S4N2 scientific closure;
- S4N3;
- FMR target, NI margin, confidence level, selector order or original 5/5 rule;
- benchmark construct validity;
- actual target hardware, power meter or load generator;
- Phase A execution;
- the R1/N2 portable-choice overlap classifier hardening, which remains an explicit separate pre-execution item.

## Current gates

Before this re-review:

```text
D1_CLOSED: yes          # historical reviewed state preserved
D2_CLOSED: no           # corrected prospectively, awaiting this review
D3_CLOSED: yes          # historical reviewed state preserved
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
CONSTRUCT_VALIDITY_REVIEWED: no
R1_N2_PORTABLE_CHOICE_OVERLAP_CLOSED: no
```

Execution is independently blocked because target platform/measurement environment and configuration-choice provenance are not materialized. Closing D2 would not authorize Phase A.

## Requested response

Please return at least:

```text
VERDICT: ACCEPT | ACCEPT_WITH_CHANGES | REJECT_OR_REDESIGN
D2_CLOSED: yes | no
D1_D2_RESPONSIBILITY_SPLIT_ACCEPTED: yes | no
ROOT_PUBLIC_INFORMATION_BOUND_ACCEPTED: yes | no
PRIOR_DESIGN_CONDITIONS_SATISFIED: yes | no
CANONICAL_EXECUTION_CURRENTLY_ADMISSIBLE: no
CONSTRUCT_VALIDITY_REVIEWED: no
R1_N2_PORTABLE_CHOICE_OVERLAP_CLOSED: no
```

Please distinguish package/integrity/assurance verification from semantic acceptance, and list any repository-side assertion you could not independently verify.
