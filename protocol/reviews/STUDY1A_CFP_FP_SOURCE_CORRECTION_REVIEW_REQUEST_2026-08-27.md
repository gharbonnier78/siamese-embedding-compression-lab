# Study 1A CFP-FP source-correction replay — independent review request

Status: `REVIEW_REQUESTED`  
Scope: Study 1A substrate qualification only  
Study 1B authorization: **NO**

## Review question

Should the author-managed CVLFace CFP-FP correction replay from GitHub Actions run `33003912752` be accepted as the corrected canonical CFP-FP evidence for Study 1A, with the original Icar-based CFP-FP result retained as historical/superseded evidence?

If accepted, the bounded Study 1A decision becomes a **candidate PASS** because LFW, CPLFW, CALFW and AgeDB-30 already passed their frozen gates and the corrected CFP-FP result also passes its frozen gate. Acceptance does **not** authorize Study 1B, production use, biometric certification, fairness/PAD/1:N claims, or representation-geometry work.

## Why a correction replay was necessary

The original canonical Study 1A A1/A2 run `32773439197` was valid but failed CFP-FP only:

- LFW: 99.8167% — PASS
- CFP-FP from `Icar/val_sets`: 97.6571% — FAIL against frozen minimum 98.96%
- CPLFW: 94.60% — PASS
- CALFW: 96.1167% — PASS
- AgeDB-30: 98.00% — PASS

A bounded post-outcome diagnostic then showed two independent non-byte-identical CFP-FP artifacts reproducing the expected AdaFace performance under the same checkpoint and evaluator:

- `gaunernst/face-recognition-eval`: 99.242857%
- `namkuner/namkuner_face_dataset`: 99.342857%

This supported a source-artifact hypothesis but did not itself change the gate. The subsequent correction replay therefore used the author-managed CVLFace evaluation toolkit distributed by the AdaFace/CVLFace author.

## Source authority and provenance

Author-managed toolkit instruction:

- repository: `mk-minchul/CVLface`
- documentation: `cvlface/data_utils/recognition/eval_data/README_EVAL_TOOLKIT.md`
- Google Drive file id: `1oEvQdseNhcWdBh2X7l2bMK_BfBZX8JCZ`
- toolkit archive SHA-256 observed in run `33003912752`:
  `79df53a35b8fed4bca0130685fe145aec26610efadab3abe3af3da52c800f79f`
- archive size: `13,862,111,134` bytes
- password source: GitHub Actions secret; password value was not recorded
- encrypted members: 58
- CFP-FP member path: `facerec_val/cfp_fp`

The CVLFace documentation describes the toolkit as containing derivatives of validation datasets such as aligned images and labels and asks users not to redistribute the password or unzipped toolkit. The workflow uploads metadata/results only, not the dataset content.

## Author derivative conversion

The workflow extracted only `facerec_val/cfp_fp` and verified:

- rows/images: 14,000
- pairs: 7,000
- genuine pairs: 3,500
- impostor pairs: 3,500
- source columns: `image`, `index`, `is_same`
- ordering: sorted by author `index`
- image size: 112×112 RGB
- unique RGB pixel digests: 5,890
- no dataset content uploaded

Transport into the frozen evaluator was lossless at pixel level:

`author PIL RGB pixels -> lossless PNG -> frozen cv2 BGR decode`

Converted evaluator container:

- SHA-256: `8204a7eccfb0a6eb7ed9a4511a0136f5326758f713270f17016fee908c38e45a`
- size: `239,200,076` bytes

## Frozen model and evaluator

Checkpoint was unchanged from the preregistered Study 1A execution:

- model: AdaFace IR101/R100, WebFace12M
- embedding dimension: 512
- checkpoint SHA-256:
  `0e7a3238d2a50f3fe3860782534928ac7cb2598977cf897f6869fd5ac2493fd0`
- pinned AdaFace source commit:
  `c60eaa786a42c03444f3df7096dbaf9d57ae010d`

Evaluation semantics remained frozen:

- pre-aligned 112×112 crops; no realignment
- `(pixel/255 - 0.5)/0.5`
- original + horizontal flip
- AdaFace norm-aware feature fusion
- L2-normalized 512D embeddings
- squared L2 distance
- 10 folds, `shuffle=False`
- threshold grid `np.arange(0,4,0.01)`
- threshold selected on train folds, evaluated on held-out fold
- frozen CFP-FP minimum: `0.9896` (98.96%)

## Correction replay result

GitHub Actions run: `33003912752`  
Benchmark step: **SUCCESS**  
Execution status: `VALID_OUTCOME`

Observed CFP-FP accuracy:

- mean: `0.9924285714285717` = **99.242857%**
- std: `0.002478478796128225`
- frozen minimum: `0.9896` = 98.96%
- published legacy reference used by the preregistration: `0.9926`
- scientific decision from benchmark result: **PASS**

Fold accuracies:

`[0.9928571, 0.9942857, 0.9928571, 0.9871429, 0.9928571, 0.9942857, 0.9957143, 0.9928571, 0.9885714, 0.9928571]`

Selected thresholds:

`[1.57, 1.63, 1.57, 1.57, 1.58, 1.57, 1.57, 1.57, 1.61, 1.57]`

Diagnostics:

- decode failures: 0
- exclusions: 0
- 14,000 image blobs
- 7,000 pairs

The observed value also matches the author-maintained CVLFace performance board for IR101/AdaFace/WebFace12M on CFP-FP to two decimals: 99.24%.

## Workflow-red condition and maintenance fix

The workflow run itself ended red **after the successful scientific benchmark** because the decision-record post-processing step read the wrong JSON field:

```python
observed = result.get('observed_accuracy')
```

The benchmark schema stores the value at:

```text
gate_evaluation.observed_accuracy
```

and equivalently at:

```text
metrics.accuracy_mean
```

This caused `None >= 0.9896` and a `TypeError`. It did not alter or invalidate the already-written benchmark result.

Maintenance fix commit:

`21a8f1715fa7f94c1edd7dd05fef2bfa1c11d0a3`

The fix:

1. reads `gate_evaluation.observed_accuracy`, with `metrics.accuracy_mean` as schema-compatible fallback;
2. fails explicitly if a `VALID_OUTCOME` contains neither field;
3. increments the decision-record schema to `1.1`;
4. changes the correction workflow to `workflow_dispatch` only so this maintenance commit cannot silently rerun the outcome-bearing benchmark.

No scientific result, threshold, checkpoint, dataset, fold, or preprocessing setting was changed by this maintenance fix.

## Evidence bundle

Run `33003912752` uploaded artifact:

- name: `study1a-cfp-fp-author-source-correction-replay`
- artifact id: `9622506401`
- artifact ZIP SHA-256:
  `068a6de98f9aedd0b9b15f7de4568b61845b33ecef37b8e37305673c306ff211`
- size: 2,917 bytes

Because the decision-record generation failed, the uploaded artifact contains the source preflight, conversion manifest, and CFP-FP benchmark JSON but not a valid generated `correction_decision.json`. Review should therefore treat the benchmark JSON as the scientific result and the decision-record failure as post-processing engineering debt fixed by commit `21a8f171...`, not as a scientific rerun requirement.

## Requested reviewer checks

Please verify independently that:

1. the author-managed CVLFace toolkit provenance is materially stronger than the original transport mirror for the purpose of source correction;
2. the toolkit archive and CFP-FP derivative were accessed without exposing or redistributing the protected content/password;
3. the conversion preserves author-provided aligned pixel content and pair ordering/labels without scientific transformation;
4. checkpoint identity and AdaFace code pin are unchanged;
5. evaluator semantics and frozen threshold are unchanged;
6. the observed result is `0.9924285714285717` and therefore passes `0.9896`;
7. the red workflow conclusion is explained solely by the post-processing field-path bug after successful outcome generation;
8. commit `21a8f171...` fixes only that bug and prevents silent reruns by making the workflow manual-only;
9. the old Icar-based result remains retained as historical evidence rather than deleted or rewritten;
10. accepting this correction revises only Study 1A substrate qualification and **does not authorize Study 1B**.

## Requested review verdict

Return one of:

- `ACCEPT_CORRECTION`: provenance, replay and maintenance fix are sufficient; CFP-FP corrected PASS may supersede the Icar-based CFP-FP result for the bounded Study 1A decision, while the old result remains historical evidence.
- `REQUEST_CHANGES`: list the exact blocking issues and whether they concern provenance, conversion, evaluator parity, evidence integrity, or governance.
- `REJECT_CORRECTION`: state why the author-managed replay is insufficient to supersede the historical result.

If `ACCEPT_CORRECTION`, explicitly confirm that this is **not** a Study 1B authorization.
