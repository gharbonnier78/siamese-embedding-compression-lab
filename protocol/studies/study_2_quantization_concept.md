# Study 2 concept note — Quantization of biometric embeddings

> **Status:** `CONCEPT_NOTE_NOT_PREREGISTERED_NOT_EXECUTED`  
> **Parent study:** `study_2_compression_ablation`  
> **Claim level:** none  
> **Historical boundary:** this note does not modify Study 0, resolve `E-STAT-001`,
> reopen G2, or start Study 1 or Study 2.

## Decision this study should support

Determine whether reducing the numerical precision of stored biometric embeddings is a
useful intervention after representation validity has been established: which precision,
if any, reduces actual template and memory-traffic cost while keeping verification and
identification performance within a preregistered decision margin.

This is not the same intervention as dimensionality reduction:

| Intervention | Changes | Primary loss mechanism | Example |
|---|---|---|---|
| projection / PCA / Siamese head | number and geometry of coordinates | discarded directions or learned remapping | 512D → 128D |
| quantization | numerical alphabet used for each coordinate | rounding, clipping and saturation | FP32 → INT8 |

The interventions are orthogonal and may be combined. Their effects must therefore be
estimated separately before a combined route is credited with engineering value.

## Research questions

1. **Same-representation effect:** at a fixed extractor, projection, dimension and matcher,
   how much decision-relevant performance changes when FP32 templates are represented as
   FP16 or INT8.
2. **Equal-cost mechanism comparison:** under the same measured serialized-byte budget,
   is it preferable to retain more dimensions at lower precision or fewer dimensions at
   higher precision? The central comparison is nominally `raw512-INT8` versus
   `projected128-FP32`.
3. **Combined compression:** after a 512→128 projection has independently qualified, does
   `projected128-INT8` provide further acceptable compression relative to
   `projected128-FP32`?
4. **Threshold migration:** can the quantized route use a threshold calibrated on
   VALIDATION without an unacceptable TEST FMR/FNMR change, and what happens if an existing
   FP32 threshold is retained during migration?
5. **Engineering realization:** do lower-bit templates improve measured storage, memory
   traffic, latency, throughput or energy on a declared implementation and hardware?
   This question belongs to the Study 4 measurement contract; bit count alone cannot
   answer it.

## Intervention boundary

The first bounded study concerns **post-training template quantization**:

```text
image -> unchanged frozen extractor -> optional frozen projection -> L2 normalization
      -> template quantization -> store / transmit -> declared matcher
```

- Primary object: gallery and probe embedding representation.
- Secondary object, only if separately declared: the 512×128 projection-head weights.
- Excluded from the first study: extractor quantization, pruning, distillation,
  quantization-aware training, product/vector quantization and ANN-index changes.
- The common extractor remains unchanged. Any later extractor quantization is a new
  intervention with separate biometric and system claims.

FP16 is retained as a reduced-precision control; it is not treated as equivalent to
integer quantization. INT4 is an optional stress condition only after INT8 has passed its
predeclared numerical and biometric gates.

## Candidate comparison skeleton

The exact routes, bit widths and budgets must be frozen in a later preregistration. The
current candidate factorial design is:

| Geometry route | Precision route | Nominal bytes/template* | Scientific role |
|---|---:|---:|---|
| raw 512D | FP32 | 2,048 | uncompressed reference |
| raw 512D | FP16 | 1,024 | reduced-precision control |
| raw 512D | INT8 | 512 | equal-payload candidate against 128D FP32 |
| random/PCA/Siamese 128D | FP32 | 512 | dimensionality-reduction controls |
| random/PCA/Siamese 128D | FP16 | 256 | combined reduced precision |
| random/PCA/Siamese 128D | INT8 | 128 | combined integer quantization |
| qualified 128D route | INT4 | 64 | optional stress condition, not an initial claim route |

\* Nominal coordinate payload only. The decision table must use **actual serialized bytes**
including scales, zero-points, padding, alignment, index metadata, encryption and
replication. For example, a per-template FP32 scale makes nominal `512D INT8` 516 bytes,
not 512 bytes.

The equal-cost comparison is scientifically valuable because it separates two competing
ways of spending the same approximate storage budget:

```text
512 coordinates × 8 bits   versus   128 coordinates × 32 bits
more geometry, less precision       less geometry, more precision
```

## Quantizer contract to freeze before execution

For an initial symmetric uniform signed quantizer, a candidate definition is:

```text
q_i = clip(round(x_i / s), -Q, Q)
x_hat_i = s q_i
```

The preregistration must remove all remaining degrees of freedom:

- signed range and tie-rounding rule;
- global, per-dimension or per-template scale granularity;
- scale and clipping estimator, fitted on TRAIN only;
- handling of zero vectors, NaN, infinity, underflow, overflow and saturation;
- whether L2 normalization occurs before quantization, after dequantization, or both;
- whether cosine is computed after dequantization or by a validated integer kernel;
- metadata serialization and byte accounting;
- deterministic reference fixtures and implementation tolerance.

Per-template scaling is not free: it stores metadata and changes the comparison. Multiple
scaling schemes must not be tried on TEST and reduced to the best result. If more than one
is retained, each becomes a predeclared route with multiplicity control.

## Data and execution discipline

- Resolve `E-STAT-001` through implementation and coverage validation of the preregistered
  subject-slot bootstrap before making a biometric inference from this extension.
- Complete and review Study 1 before executing confirmatory Study 2, as required by the
  existing programme order.
- Reuse the same frozen extractor, projection artifacts, identity-disjoint splits and
  declared seeds within a comparison.
- No retraining is required for the post-training quantization intervention.
- New distances must be computed from the quantized templates; historical Study 0 scores
  are never overwritten or relabelled as quantized scores.
- Quantizer parameters are fitted on TRAIN only. VALIDATION selects operational thresholds.
  TEST is opened once after every route and rule is frozen.
- A Study 0-derived run, if used, is plumbing-only and cannot repair G2, establish
  non-inferiority or support an industrial low-FMR claim.

## Estimands and endpoints

### Representation endpoint

For a quantized candidate `q` and its otherwise identical FP32 reference `f`, at target
FMR `alpha`:

```text
delta_FNMR_quant(alpha) = FNMR_q(alpha) - FNMR_f(alpha)
```

Candidate and reference may each be located at the same TEST FMR only for the
non-deployable representation comparison. The uncertainty estimator must respect identity
and capture dependence.

### Operational endpoint

Select the candidate threshold on VALIDATION, freeze it, then report TEST FMR and FNMR.
Also report a separately labelled threshold-migration stress result using the frozen FP32
threshold, if that deployment scenario is preregistered.

### Secondary diagnostic endpoints

- cosine/angle distortion and score drift relative to FP32;
- saturation and clipping rates, including distribution tails;
- EER and ROC AUC as descriptive metrics only;
- threshold displacement and calibration error;
- rank and top-k changes only when the Study 4 1:N protocol is active;
- actual payload, metadata and index bytes;
- latency, throughput, memory and energy only when measured under a pinned hardware and
  software profile.

Mean squared reconstruction error is diagnostic, not a biometric acceptance criterion. A
small average numerical error can still move the impostor or genuine tail across an
operational threshold.

## Hypotheses and gates to preregister

- **H-Q-NI:** the quantized template is not demonstrably non-inferior to the identical FP32
  route unless the paired upper confidence bound for `delta_FNMR_quant` is within a
  predeclared margin at every required operating point.
- **H-Q-EQUAL-COST:** at the actual equal-byte budget, neither `raw512-INT8` nor
  `projected128-FP32` is preferred until the preregistered biometric endpoint and cost
  function support the decision.
- **H-Q-THRESHOLD:** drop-in reuse of the FP32 threshold is unsafe until its TEST FMR/FNMR
  consequences are bounded.
- **H-Q-SPEED-NULL:** lower-bit storage does not imply faster inference; speed is claimed
  only from stage-isolated measurements on a supported kernel and declared hardware.

Proposed gates:

1. **GQ0 — numerical correctness:** deterministic quantize/dequantize fixtures, boundary
   values, saturation accounting and reference-kernel agreement pass.
2. **GQ1 — protocol integrity:** quantizer and thresholds use only their permitted splits;
   routes, bit widths and stop rules are frozen before TEST.
3. **GQ2 — inferential adequacy:** the dependence-aware interval method passes its coverage
   requirement for every primary endpoint and regime.
4. **GQ3 — biometric decision:** the preregistered non-inferiority and operational
   constraints pass without selecting a bit width, seed or scale on TEST.
5. **GQ4 — engineering value:** actual bytes or measured system endpoints improve under
   the declared cost function without a prohibited biometric regression.

The Study 0 exploratory `+0.03` FNMR margin must **not** be inherited automatically. Study 2
must justify and freeze its own operating points, margins, sample size, multiplicity policy
and practical cost function before execution.

## Falsification and stop conditions

- Any TEST-informed scale, clipping rule, bit-width selection or route removal invalidates
  the affected confirmatory comparison.
- If GQ0 fails, no biometric run starts.
- If the interval-coverage gate fails, the result remains descriptive and no
  non-inferiority conclusion is permitted.
- If INT8 fails the predeclared gate, INT4 does not become a rescue analysis.
- If actual serialized payloads are unequal, the comparison is not described as
  equal-cost.
- If the hardware or kernel does not realize lower-bit operations, no latency, throughput
  or energy improvement is inferred from storage arithmetic.
- LFW pair counts and FMR resolution continue to prohibit industrial low-FMR claims.
- Negative and indeterminate outcomes remain publishable evidence.

## Expected future artifacts

When the blockers are cleared, promote this concept through a separate review into:

- a human-readable preregistration and machine-readable Study 2 contract;
- frozen quantizer and cost-accounting configurations;
- numerical reference fixtures and unit tests;
- versioned quantized-template metadata and new score tables;
- validation thresholds and non-deployable equal-FMR benchmark thresholds;
- score-drift, saturation, payload and decision tables;
- a hardware/kernel manifest for any system-performance claim;
- an immutable MMALS replay bundle, audit trace and artifact hashes;
- append-only claims, ledger, results and paper updates.

## Immediate bounded next step

1. Keep this file as a concept note only.
2. Implement and coverage-validate the v0.2.2 subject-slot bootstrap; resolve or retain
   `E-STAT-001` according to the evidence.
3. Complete and review the Study 1 face-backbone preregistration and execution.
4. Convert this note into a reviewed Study 2 preregistration that freezes quantizer
   semantics, bit widths, payload accounting, operating points, margins, seeds, sample
   size, multiplicity and stop rules.
5. Run numerical fixtures and synthetic smoke before opening biometric TEST data.

Until those steps are complete, the only admissible statement is:

> Quantization is a planned, orthogonal compression intervention. No biometric
> preservation, speed-up or operational value has yet been demonstrated.
