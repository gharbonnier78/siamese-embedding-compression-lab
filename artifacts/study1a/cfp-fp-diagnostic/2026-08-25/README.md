# Study 1A CFP-FP diagnostic evidence

Run: `32805230034`
Head SHA: `1e9d989b44248d1292074d689ef3509ab106f48e`
Artifact: `study1a-cfp-fp-diagnostic-bundle`
Artifact ID: `9549493950`
ZIP SHA-256: `3b3539d9fe9dd502c2e3079865708a1843606430491d8da3049748198bcba12f`

Purpose: preserve the completed post-outcome CFP-FP provenance diagnostic. This evidence is diagnostic only and has no authority to rewrite the canonical Study 1A gate without a separately reviewed correction/replay decision.

Observed diagnostic results under the same frozen checkpoint and evaluation protocol:

- `gaunernst/face-recognition-eval/cfp_fp.bin`
  - SHA-256: `a8754ddf9729a014438d00908a1dc2fe2dbdfb59db9d19a714251c2f814a94ad`
  - bytes: `76,454,058`
  - accuracy: `0.9924285714285717`
  - would meet frozen minimum `0.9896`: yes
  - byte-identical to canonical Icar artifact: no
- `namkuner/namkuner_face_dataset/cfp_fp.bin`
  - SHA-256: `d47cdcfe71efe12ff34438fa2254472f144eaa6f22f8ae7e210410c885fa2e43`
  - bytes: `79,602,255`
  - accuracy: `0.9934285714285714`
  - would meet frozen minimum `0.9896`: yes
  - byte-identical to canonical Icar artifact: no

Canonical comparison retained for traceability:

- `Icar/val_sets/cfp_fp.bin`
  - SHA-256: `76306c783c2ef59c8569ebdcdd2f529f450bcc3fad57c94a5fc2b91df0f10370`
  - bytes: `76,267,779`
  - canonical run `32773439197`
  - accuracy: `0.9765714285714285`
  - frozen minimum: `0.9896`
  - current canonical decision: `FAIL`

Interpretation: two independent transport artifacts, both non-byte-identical to the Icar artifact, reproduce AdaFace CFP-FP near the published reference (`0.9926`) under the same frozen evaluator. This is strong evidence that the anomalous canonical CFP-FP failure is source-artifact dependent. It does not by itself identify which transport artifact is the authoritative AdaFace validation artifact, nor does it change the gate. The next admissible scientific action is a separately reviewed provenance correction/replay decision based on first-party or otherwise defensible dataset identity evidence.
