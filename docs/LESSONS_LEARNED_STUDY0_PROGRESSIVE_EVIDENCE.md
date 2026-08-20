# Lesson learned — progressive evidence before full qualification

Status: **PROCESS LESSON / STUDY 1 DESIGN INPUT**

## Observation

Study 0 required a long corrective chain because a methodological defect had been found in evidence that was already being used as a foundation for the next study. The full chain — frozen correction protocol, exact provenance recovery, coverage validation, immutable replay, reviewed materialization and independent interpretation boundary — was justified because the defect could in principle have changed the scientific decision.

At the same time, the episode exposed a cost-design lesson: the broad research direction could have been triaged much earlier with explicitly exploratory evidence before committing to publication-grade qualification.

The lesson is therefore **not** “use less rigor”. It is:

> Use the minimum sufficient rigor for the decision currently being made, and escalate the evidence burden explicitly when a result is promoted toward a claim.

A second lesson is specific to representation studies: **check the source representation before blaming the compression method**. Study 0 intentionally inherited a pedagogical setup in which an ImageNet-pretrained ResNet-18 was completely frozen and only a 512→128 linear head learned from face pairs. That isolates the projection mechanism, but it also means weak identity information in the generic source embedding cannot be recovered by the compression head. The next study must therefore establish raw face-backbone viability before paying for compression qualification.

## Two-stage operating model

### Stage A — exploratory screening

Purpose: answer `is there enough signal to justify qualification?`

Permitted characteristics:

- dedicated SCREEN data only;
- fewer predeclared screening seeds;
- reduced compute budget;
- fast matched controls and ablations;
- descriptive or lightweight uncertainty adequate for triage;
- no qualification TEST access;
- explicit `EXPLORATORY / NOT FOR CLAIM` status.

A screening result may support `CONTINUE`, `STOP`, or `REDIRECT`. It cannot support a confirmatory biometric claim.

### Stage B — qualification

Purpose: answer the frozen scientific question with claim-bearing evidence.

Qualification retains the full burden appropriate to the claim: frozen estimands and margins, full seed policy, qualification data, validated uncertainty, immutable provenance, replay, gates and independent review.

## Why this does not weaken the Study 0 correction

Once E-STAT-001 was discovered, the question was no longer merely whether the Siamese direction looked promising. The question was whether the wrong uncertainty unit could have changed a result already used as a scientific foundation. That required the full corrective chain.

A corrected conclusion that remains directionally unchanged does not imply that the original method was valid. A materially different uncertainty estimate is itself scientifically relevant.

## Study 1 consequence

Study 1 is amended in draft form to use progressive evidence escalation:

1. **Replace the generic ImageNet source with a pinned face-specific backbone** before re-testing compression.
2. **Keep backbone training provenance, projection-development data, SCREEN data and qualification TEST as separate data roles**, with explicit identity-overlap checks.
3. **Screen the face-specific backbone and compression routes first** on dedicated non-qualification data.
4. Verify that the raw face-specific embedding itself is credible at the decision-relevant low-FMR operating point before spending qualification budget on compression.
5. Use matched raw/random/PCA/Siamese controls during screening so that an apparent Siamese signal is not interpreted without compression baselines.
6. Freeze a screening promotion/stop rule before reading screening outcomes.
7. If screening shows no credible low-FMR or compression-retention signal, stop or redirect without opening qualification TEST.
8. Only a promoted candidate enters the full Study 1 qualification design with all predeclared qualification seeds and the complete uncertainty/review burden.
9. Screening seeds or outcomes must never be used to drop unfavorable qualification seeds after the fact.

The current public-data plan treats LFW/CFP-FP/AgeDB-30/CALFW/CPLFW as non-claim-bearing screening candidates and IJB-C 1:1 template verification as a preferred public qualification candidate, subject to lawful access, provenance and training/test identity-overlap checks. VGGFace2 is a scientifically attractive projection-development candidate if it is legitimately available, but its original Oxford download is no longer provided and must not be assumed accessible.

This amendment changes Study 1 planning only. It does not execute Study 1, does not reopen Study 0, and does not authorize geometry exploration.

## Broader research-program consequence

The more useful next question is not automatically “make Siamese better”. Before deeper geometry or representation stories, separate the possible causes of weak compression evidence:

- source backbone suitability at the target operating point;
- compression dimension;
- supervised objective;
- dataset/population regime;
- threshold-transfer behavior;
- matched compression controls.

Study 1 should therefore act as a **screen-then-qualify decision point**, not as an automatic expensive continuation of Study 0.

## Reusable rule

A negative screening result is a valid research outcome if it prevents an unjustified qualification campaign. A negative qualified result is a valid scientific outcome if it closes a claim under a defensible procedure. Both should be preserved.