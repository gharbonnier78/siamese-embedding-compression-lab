# Study 1A — CFP-FP source-correction replay

Date: 2026-08-25
Status: AUTHORIZED_SOURCE_CORRECTION_REPLAY
Harness: `gharbonnier78/scientific-research-harness@3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`
Human authority: explicit instruction on 2026-08-25 to trace CFP-FP to the primary source, run a new benchmark on that source, and revise the Study 1A FAIL only if the correction is demonstrated.

## Trigger

Canonical A1/A2 run `32773439197` was valid and yielded Study 1A FAIL solely because CFP-FP scored `0.9765714285714285` below the frozen minimum `0.9896`. A bounded post-outcome diagnostic then evaluated two independent CFP-FP artifacts with the same checkpoint and same evaluator:

- `gaunernst/face-recognition-eval/cfp_fp.bin`: `0.9924285714285717`;
- `namkuner/namkuner_face_dataset/cfp_fp.bin`: `0.9934285714285714`.

Both pass the unchanged threshold and are close to the AdaFace published reference `0.9926`, while neither is byte-identical to the Icar artifact. This strongly supports an input-artifact/provenance problem but does not by itself authorize cherry-picking a mirror.

## Primary-source chain

The scientific authority for the dataset definition is Sengupta et al., *Frontal to Profile Face Verification in the Wild*, WACV 2016, DOI `10.1109/WACV.2016.7477558`. The authors' historical first-party dataset site is `http://www.cfpw.io/`, with the direct archive historically documented as `http://www.cfpw.io/cfp-dataset.zip`.

The primary distribution defines CFP as 500 identities with 10 frontal and 4 profile images per identity, plus the CFP-FP protocol. The official AdaFace repository is the authority for the model/evaluation side and reports R100/WebFace12M CFP-FP accuracy `0.9926`.

Because the first-party site is no longer reliably reachable in 2026, a first step of this replay is a fail-closed availability/provenance preflight. A preservation mirror may be used only if it is explicitly identified as a preserved copy of the first-party distribution and the embedded official protocol structure is validated; such a mirror must never be relabeled `official`.

## Frozen scientific semantics

No threshold, checkpoint, metric or gate is changed:

- checkpoint: AdaFace IR101/R100 WebFace12M, SHA-256 `0e7a3238d2a50f3fe3860782534928ac7cb2598977cf897f6869fd5ac2493fd0`;
- AdaFace code commit: `c60eaa786a42c03444f3df7096dbaf9d57ae010d`;
- input: 112x112 BGR, `(pixel/255 - 0.5)/0.5`;
- original + horizontal-flip norm-aware fusion;
- L2-normalized 512D embeddings;
- squared L2 distance;
- 10 folds, no shuffle, threshold grid `np.arange(0,4,0.01)` selected on 9 folds and applied to the held-out fold;
- CFP-FP published reference: `0.9926`;
- CFP-FP frozen minimum: `0.9896`.

## Correction/replay decision rule

1. The original run `32773439197` and its CFP-FP FAIL remain immutable historical evidence.
2. The source-correction replay may supersede that CFP-FP gate result only if the benchmark input is tied to the first-party CFP distribution/protocol by recoverable provenance, the replay is technically valid, and the frozen evaluator/checkpoint semantics are unchanged.
3. If corrected CFP-FP accuracy is `>= 0.9896`, CFP-FP becomes `PASS_CORRECTED_SOURCE_REPLAY`; Study 1A may then be recomputed from the already-valid LFW/CPLFW/CALFW/AgeDB results. Since those four already pass, the bounded Study 1A decision becomes PASS only after the correction evidence is archived and reviewed as a source correction rather than threshold relaxation.
4. If corrected CFP-FP remains `< 0.9896`, Study 1A remains FAIL.
5. If primary-source/provenance or replay validity is incomplete, the correction is INDETERMINATE and the current FAIL is not silently rewritten.

## Inferential boundary

A corrected Study 1A PASS would authorize only acceptance of the frozen AdaFace 512D representation as the substrate for the planned compression comparison. It does not establish production biometric fitness, fairness, PAD/security, regulatory conformity, 1:N performance, low-FMR operational validity, or SOTA status.

Study 1B still requires its own explicit human GO after this correction is closed.
