# Study 1A — CFP-FP bounded diagnostic plan

Date: 2026-08-25
Status: ACTIVE_DIAGNOSTIC_AFTER_VALID_A2_FAILURE

## Trigger

Canonical Study 1A run `32773439197` produced a valid A1/A2 outcome. LFW, CPLFW, CALFW and AgeDB-30 reproduced at or above their frozen minima, while CFP-FP observed accuracy was `0.9765714285714285` against the frozen minimum `0.9896` and published reference `0.9926`.

This analysis is authorized by the human instruction `Ok pour lancer analyse` after the valid outcome was observed.

## Boundary

This is a **diagnostic after a valid failure**, not a gate rewrite.

The following are frozen during the diagnostic:

- A1/A2 thresholds;
- AdaFace IR101/R100 architecture;
- checkpoint identity used by the canonical run;
- BGR input convention and `(pixel/255 - 0.5)/0.5` normalization;
- horizontal-flip norm-aware feature fusion;
- 10-fold non-shuffled verification protocol;
- squared L2 distance on L2-normalized 512D embeddings.

A diagnostic result MUST NOT retroactively turn canonical CFP-FP FAIL into PASS. If a reproducible source/protocol defect is demonstrated, the consequence is a separately reviewed correction/replay decision with the original evidence retained.

Study 1B remains unauthorized.

## Primary hypotheses, ordered by value of information

### H-DATA — validation artifact/source mismatch

The canonical CFP-FP artifact came from `Icar/val_sets/cfp_fp.bin`, SHA-256 `76306c783c2ef59c8569ebdcdd2f529f450bcc3fad57c94a5fc2b91df0f10370`, size `76,267,779` bytes. Public mirrors advertise materially different CFP-FP file sizes, so source identity is not established by the filename alone.

Diagnostic: obtain two independent public mirrors (`gaunernst/face-recognition-eval` and `namkuner/namkuner_face_dataset`), record SHA-256, size, pair counts, labels and exact image-byte digests, then evaluate only if the artifact differs from the canonical source.

### H-PROTOCOL — local evaluator differs from pinned AdaFace evaluator

Static comparison already shows the local evaluator intentionally mirrors pinned upstream `evaluate_utils.evaluate`: thresholds `np.arange(0,4,0.01)`, 10-fold `shuffle=False`, train-fold threshold selection, squared L2 distance. Pinned `train_val.py` also uses original+horizontal-flip norm-aware fusion.

Diagnostic: for each alternate source, use the same frozen local evaluator. A later bounded parity check may compare local fold metrics to upstream `evaluate_utils.py` on identical embeddings if H-DATA is not explanatory.

### H-DECODE — encoded-image transport/decoder differences

The public `.bin` mirrors use heterogeneous pickle representations (`bytes`, `ndarray uint8`, sometimes singleton-column vectors). Transport is normalized losslessly to encoded bytes before OpenCV decode. Decoder-backend parity remains secondary because four of five canonical benchmarks reproduce closely or exactly.

### H-CHECKPOINT — checkpoint-specific behavior

Lower priority because the exact same checkpoint reproduces the other four benchmarks and the inference-backbone equivalence work has independently resolved the RGB/BGR first-layer transform. This hypothesis is not discarded, only deferred behind higher-value source/protocol checks.

## Diagnostic outputs

For each independent CFP-FP source retain:

- source locator;
- file SHA-256 and size;
- pair/genuine/impostor counts;
- image-payload representation counts;
- image-byte digest summary;
- observed verification accuracy and fold metrics;
- explicit `diagnostic_only: true` and `gate_authority: false`.

The combined diagnostic bundle must be retained durably if it changes the scientific decision path, following the evidence-retention rule proposed upstream to the scientific harness.

## Decision logic

1. If alternate mirrors are byte-identical to the canonical artifact and reproduce the same score, H-DATA is weakened.
2. If an independent artifact differs and reproduces the published CFP-FP result while the canonical artifact does not, H-DATA is strongly supported; do not alter the gate automatically—request a reviewed source-correction replay.
3. If independent artifacts differ but all yield about the same low score, prioritize H-PROTOCOL/H-DECODE/checkpoint investigation.
4. If mirrors disagree materially among themselves, treat CFP-FP provenance as unresolved and do not cherry-pick the source whose score best matches the published reference.

No threshold relaxation or post-outcome source selection is permitted.