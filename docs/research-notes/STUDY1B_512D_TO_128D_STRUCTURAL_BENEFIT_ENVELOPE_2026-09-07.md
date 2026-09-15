# Study 1B — 512D -> 128D structural benefit envelope

**Date:** 2026-09-07  
**Status:** non-outcome engineering decision analysis  
**Boundary:** no Study 1B SCREEN, qualification TEST result, real route performance, representation geometry, or amendment is opened by this note.

## 1. Why this note exists

The S4 value-of-information analysis needs a defensible meaning for `C_miss`: the engineering cost of failing to adopt, or delaying, an actually acceptable 128D representation.

Before using any product-specific measurements, there is one benefit that can be calculated exactly from the representation dimensions alone:

```text
512 -> 128 dimensions = 4:1 dimensional compression
```

If datatype, encoding and per-vector metadata are unchanged, the payload occupied by the vector itself becomes exactly one quarter of the 512D payload:

```text
128 / 512 = 0.25
```

so the vector payload reduction is exactly:

```text
1 - 0.25 = 0.75 = 75%
```

This is a structural arithmetic fact. It is **not** a claim of 75% end-to-end storage, latency, compute, energy or cost reduction.

## 2. Exact vector-payload arithmetic

Let:

- `N` = number of stored embeddings;
- `b` = bytes per component;
- `d_raw = 512`;
- `d_comp = 128`.

Then:

```text
Raw vector bytes        = N * 512 * b
Compressed vector bytes = N * 128 * b
Bytes avoided           = N * 384 * b
```

For identical datatype and no representation-dependent metadata, the avoided payload is 75% of the raw vector payload.

### Illustrative scales — float32 (`b = 4` bytes)

| Number of embeddings `N` | raw512 payload | 128D payload | payload avoided |
|---:|---:|---:|---:|
| 1 million | 2.048 GB | 0.512 GB | 1.536 GB |
| 10 million | 20.48 GB | 5.12 GB | 15.36 GB |
| 100 million | 204.8 GB | 51.2 GB | 153.6 GB |

These are decimal GB and include only the vector payload. Database/index overhead, identity metadata, replication, checksums, encryption framing, page/index structure and backups are excluded.

### Illustrative scales — float16 (`b = 2` bytes)

| Number of embeddings `N` | raw512 payload | 128D payload | payload avoided |
|---:|---:|---:|---:|
| 1 million | 1.024 GB | 0.256 GB | 0.768 GB |
| 10 million | 10.24 GB | 2.56 GB | 7.68 GB |
| 100 million | 102.4 GB | 25.6 GB | 76.8 GB |

Again, the 75% payload fraction is exact only when datatype and representation encoding are held fixed.

## 3. Transfer and replication

If an embedding is transmitted or replicated without additional representation-dependent overhead, bytes transferred scale with dimension in the same way.

For `Q` vector transfers over the decision horizon:

```text
Transfer bytes avoided = Q * 384 * b
```

If the platform stores `r` physical copies or replicas of each vector, the vector-payload storage difference becomes:

```text
Replicated bytes avoided = N * 384 * b * r
```

The formula is exact for the vector payload; the economic value still requires the actual storage/transfer rate and lifecycle horizon.

## 4. Similarity-comparison arithmetic

For a direct dot product or cosine numerator between two dense vectors, coordinate-wise arithmetic is linear in dimension.

Holding implementation constant:

```text
coordinate work at 128D / coordinate work at 512D = 128 / 512 = 0.25
```

So the dimensional part of a brute-force dense comparison performs 75% fewer coordinate contributions and has a theoretical 4:1 reduction in that specific arithmetic component.

This must **not** be translated automatically into 4x application throughput or 75% lower latency. End-to-end behavior can be dominated by:

- memory movement and cache behavior;
- vectorization/SIMD and kernel implementation;
- indexing or approximate-nearest-neighbor structures;
- batching;
- thresholding and post-processing;
- database/network overhead;
- concurrency and synchronization;
- accelerator occupancy;
- fixed per-request costs.

Those are future engineering measurements, not values inferred here.

## 5. Converting structural savings into engineering value

Introduce explicit engineering rates rather than guessing monetary benefit.

### Storage component

Let `R_storage` be the cost per byte over the chosen horizon, including only costs the engineering owner considers causally attributable to embedding payload.

```text
V_storage = N * 384 * b * r * R_storage
```

### Transfer component

Let `R_transfer` be the cost per byte transferred over the horizon.

```text
V_transfer = Q * 384 * b * R_transfer
```

### Compute/capacity component

This should be measured rather than inferred from dimension alone. Let:

```text
V_compute = measured avoided compute/capacity cost over the horizon
```

### Other enabling value

A compressed representation may enable a memory-constrained device, reduce a hardware tier, increase in-memory residency, simplify replication, or unlock another deployment. Such value should be recorded separately with provenance rather than hidden inside a generic multiplier.

A practical benefit model is therefore:

```text
V_128D = V_storage + V_transfer + V_compute + V_capacity + V_enabling
```

with every non-structural term measured or explicitly supplied by an engineering authority.

## 6. Link to `C_miss`

Under the working policy:

```text
NOT_DEMONSTRATED -> retain raw512 by default
```

`C_miss` is not biometric harm. It is the cost of failing to realize, or delaying, the benefit of an actually acceptable 128D route.

A first decomposition is:

```text
C_miss = delayed_or_foregone(V_128D)
       + avoidable_requalification_cost
       + avoidable_schedule/opportunity cost
```

Care is required to avoid double-counting. For example, if schedule delay is already reflected in the fraction of `V_128D` lost over the horizon, it should not be counted a second time.

## 7. How much can the last power points be worth?

Using the already frozen S4 results and the BEST selector only as the previously declared comparison basis:

```text
S4N1 power = 0.869
Target      = 0.900
Gap         = 0.031
```

If a future design could raise power from 86.9% to exactly 90% **without changing other error properties**, the maximum avoided missed-demonstration loss is:

```text
conditional on acceptable candidate: 0.031 * C_miss
before knowing candidate state:       q * 0.031 * C_miss
```

where `q` is the prospective probability assigned before real outcome opening to the candidate being in the decision-relevant acceptable state.

This creates a concrete break-even question:

> Is the cost of acquiring genuinely new independent evidence lower than `q * 0.031 * C_miss`?

If not, recovering the final 3.1 power points is not justified on the missed-demonstration side alone.

The opposite false-qualification side must still be analysed separately.

## 8. What must be measured next — and what must not be guessed

The following can now be filled without opening biometric outcome performance:

| Input | Can be obtained from engineering systems? | Current state |
|---|---|---|
| embedding datatype / bytes per component | yes | unknown here |
| number of embeddings / retention horizon | yes | unknown here |
| replication / backup factor | yes | unknown here |
| transfer volume / refresh frequency | yes | unknown here |
| storage and transfer economic rates | yes | unknown here |
| raw comparison kernel latency / throughput by dimension | benchmark required | not inferred |
| end-to-end search throughput / latency | benchmark required | not inferred |
| hardware tier or capacity avoided | architecture/capacity study | not inferred |
| cost/delay of new independent subjects/captures/sessions | study operations estimate | unknown here |

None of these require opening the protected real Study 1B matcher-performance outcome unless the particular benchmark is itself part of that frozen outcome boundary. Any future benchmark must preserve that boundary explicitly.

## 9. Current decision

The structural result is already clear:

> 128D provides an exact 75% reduction in the vector payload relative to 512D when datatype and encoding are held constant, and a 75% reduction in the coordinate count of a direct dense similarity computation. The real system and economic benefit remains an engineering measurement problem.

Therefore the next useful input is not another S4 estimator. It is an engineering cost sheet containing `N`, datatype, replication, transfer/refresh volume, horizon, applicable rates, and the cost/delay of obtaining genuinely independent evidence.