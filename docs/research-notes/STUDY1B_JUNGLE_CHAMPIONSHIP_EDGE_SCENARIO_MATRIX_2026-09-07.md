# Study 1B — Jungle Championship edge scenario matrix

**Date:** 2026-09-07  
**Status:** non-outcome engineering scenario / sensitivity analysis  
**Boundary:** no Study 1B SCREEN, qualification TEST result, real route performance, representation geometry, or amendment is opened by this note.

## 1. Purpose

Turn the archived Jungle Championship assumptions into a quantitative edge-sizing matrix for the `512D -> 128D` value-of-information analysis.

This note deliberately separates:

1. **event-level logical identities**;
2. **physical copies of galleries on edge devices**;
3. **local observations / passages seen by each device**;
4. **matching-work proxies**;
5. **unknown end-to-end performance**, which must be measured rather than inferred from vector dimension alone.

Values explicitly supplied by the human authority remain facts/assumptions of the scenario. Values introduced below for sensitivity analysis are marked **SCENARIO**, not event facts.

## 2. Event envelope

| Quantity | Value | Provenance |
|---|---:|---|
| Event duration | 5 days | USER_PROVIDED |
| Matches per day | 3 | USER_PROVIDED |
| Total matches | 15 | DERIVED |
| Stadium capacity | 50,000 | USER_PROVIDED |
| Maximum spectator admissions if every match is full | 750,000 | DERIVED |
| Same spectator may attend multiple matches | yes | USER_PROVIDED |
| Every person appears in front of every edge device | no | USER_PROVIDED |
| One identity belongs to exactly one edge device | no | USER_PROVIDED |

`750,000` is therefore a **passage/admission envelope**, not an estimate of unique people.

### Illustrative uniqueness sensitivity

If all 750,000 spectator admissions were realized, a simple sensitivity calculation is:

| Average matches attended per spectator | Approx. unique spectators | Status |
|---:|---:|---|
| 1.2 | 625,000 | SCENARIO |
| 1.5 | 500,000 | SCENARIO |
| 2.0 | 375,000 | SCENARIO |
| 3.0 | 250,000 | SCENARIO |

This ignores staff/organizer/contractor populations and should not be treated as a forecast.

## 3. Biometric populations

| Population | Scenario semantics | Edge / downstream role |
|---|---|---|
| Whitelist | authorized spectators, technical staff, organizing staff, contractors/subcontractors, other authorized roles | local or edge `1:N` authorization / recognition |
| Blacklist | stadium-banned persons, potentially extended with nationally/internationally wanted persons | local or edge `1:N` detection / alert |
| Neither list | no local whitelist/blacklist match | retain portrait + location + timestamp for later national offline `1:N` identification |

The national offline identification branch is a separate workload. Portrait storage may dominate embedding storage there.

## 4. Structural constants for 512D vs 128D

For a dense embedding with `b` bytes per component:

```text
bytes_per_embedding = dimension * b
```

| Datatype | Bytes/component `b` | 512D bytes/vector | 128D bytes/vector | Reduction |
|---|---:|---:|---:|---:|
| FP32 | 4 | 2,048 B | 512 B | 75% |
| FP16 | 2 | 1,024 B | 256 B | 75% |
| INT8 | 1 | 512 B | 128 B | 75% |

The 75% reduction is exact for the vector payload when representation encoding and metadata are otherwise unchanged. It is not an end-to-end latency, energy or cost claim.

## 5. Whitelist gallery footprint — full local copy, FP32

The sensitivity grid already archived for whitelist size is `250k / 500k / 750k / 1M` identities, with `1 / 3 / 5` templates per identity.

### 512D vs 128D per device

| Whitelist identities `N` | Templates `T` | 512D FP32 | 128D FP32 | Bytes avoided |
|---:|---:|---:|---:|---:|
| 250k | 1 | 0.512 GB | 0.128 GB | 0.384 GB |
| 250k | 3 | 1.536 GB | 0.384 GB | 1.152 GB |
| 250k | 5 | 2.560 GB | 0.640 GB | 1.920 GB |
| 500k | 1 | 1.024 GB | 0.256 GB | 0.768 GB |
| 500k | 3 | 3.072 GB | 0.768 GB | 2.304 GB |
| 500k | 5 | 5.120 GB | 1.280 GB | 3.840 GB |
| 750k | 1 | 1.536 GB | 0.384 GB | 1.152 GB |
| 750k | 3 | 4.608 GB | 1.152 GB | 3.456 GB |
| 750k | 5 | 7.680 GB | 1.920 GB | 5.760 GB |
| 1M | 1 | 2.048 GB | 0.512 GB | 1.536 GB |
| 1M | 3 | 6.144 GB | 1.536 GB | 4.608 GB |
| 1M | 5 | 10.240 GB | 2.560 GB | 7.680 GB |

Decimal GB are used. Database/index overhead, identity metadata, encryption framing, checksums, allocation overhead and backups are excluded.

## 6. Central whitelist case across datatypes

Use **500k identities × 3 templates** only as a sensitivity midpoint, not an event fact.

| Datatype | 512D local whitelist | 128D local whitelist | Avoided |
|---|---:|---:|---:|
| FP32 | 3.072 GB | 0.768 GB | 2.304 GB |
| FP16 | 1.536 GB | 0.384 GB | 1.152 GB |
| INT8 | 0.768 GB | 0.192 GB | 0.576 GB |

Dimension reduction and quantization are separate interventions. A future study must not attribute an INT8 gain to 128D or vice versa.

## 7. Blacklist footprint — full local replication, FP32

Blacklist cardinalities `1k / 10k / 100k` remain exploratory sensitivity values.

For **3 templates per identity**:

| Blacklist identities `B` | 512D FP32 | 128D FP32 | Avoided |
|---:|---:|---:|---:|
| 1k | 6.144 MB | 1.536 MB | 4.608 MB |
| 10k | 61.44 MB | 15.36 MB | 46.08 MB |
| 100k | 614.4 MB | 153.6 MB | 460.8 MB |

This illustrates why full blacklist replication may remain feasible even when full whitelist replication becomes material, but actual device limits are still unknown.

## 8. Three edge-distribution architectures

Let:

- `N` = whitelist identities;
- `B` = blacklist identities;
- `T` = templates per identity;
- `g_i` = fraction of whitelist loaded on device `i`;
- blacklist fraction is assumed `1.0` in the hybrid sensitivity example below;
- `d` = embedding dimension;
- `b` = bytes/component.

Per-device gallery payload:

```text
G_i = ((N * g_i) + B) * T * d * b
```

### Central sensitivity point

Use only for comparison:

```text
N = 500,000 whitelist identities      [SCENARIO]
B = 10,000 blacklist identities       [SCENARIO]
T = 3 templates                       [SCENARIO]
b = 4 bytes (FP32)                    [SCENARIO]
```

| Architecture sensitivity | Whitelist fraction `g_i` | 512D payload/device | 128D payload/device | Avoided/device |
|---|---:|---:|---:|---:|
| A — full replication | 1.00 | 3.13344 GB | 0.78336 GB | 2.35008 GB |
| C1 — hybrid, quarter whitelist | 0.25 | 0.82944 GB | 0.20736 GB | 0.62208 GB |
| C2 — hybrid, tenth whitelist | 0.10 | 0.36864 GB | 0.09216 GB | 0.27648 GB |

The hybrid cases keep the complete 10k blacklist in this sensitivity example while localizing the whitelist.

## 9. Physical replication across many devices

The device count `D` has not been supplied. The following is therefore only a **sensitivity table** showing how physical gallery copies scale.

Using the central values above:

### Full replication (`g=1.0`)

| Devices `D` | 512D total gallery payload | 128D total gallery payload | Avoided |
|---:|---:|---:|---:|
| 10 | 31.3344 GB | 7.8336 GB | 23.5008 GB |
| 50 | 156.672 GB | 39.168 GB | 117.504 GB |
| 100 | 313.344 GB | 78.336 GB | 235.008 GB |

### Hybrid quarter-whitelist (`g=0.25`)

| Devices `D` | 512D total gallery payload | 128D total gallery payload | Avoided |
|---:|---:|---:|---:|
| 10 | 8.2944 GB | 2.0736 GB | 6.2208 GB |
| 50 | 41.472 GB | 10.368 GB | 31.104 GB |
| 100 | 82.944 GB | 20.736 GB | 62.208 GB |

These totals count **physical copies**, not unique logical identities.

## 10. Matching-work proxy per observation

For brute-force dense matching only, a first-order proxy is:

```text
coordinate_contributions_per_observation
    = number_of_local_templates * dimension
```

At the central sensitivity point:

### Full replication

```text
local templates = (500,000 + 10,000) * 3 = 1,530,000
```

| Dimension | Coordinate contributions / observation |
|---|---:|
| 512D | 783.36 million |
| 128D | 195.84 million |

### Hybrid quarter-whitelist

```text
local templates = (500,000 * 0.25 + 10,000) * 3 = 405,000
```

| Dimension | Coordinate contributions / observation |
|---|---:|
| 512D | 207.36 million |
| 128D | 51.84 million |

This is again an exact 75% reduction in coordinate-level dense arithmetic. It is **not** a prediction of measured latency because indexing, ANN search, SIMD, batching, memory hierarchy, fixed overhead and accelerator behavior may dominate.

For device `i` with `v_i` observations over an interval:

```text
work_proxy_i = v_i * local_templates_i * d
```

The correct event-wide structural proxy is:

```text
sum_i work_proxy_i
```

not `people * cameras`.

## 11. Gallery synchronization / refresh envelope

A full gallery refresh transfers approximately the same vector payload as the local gallery size before transport framing and metadata.

At the central FP32 sensitivity point:

| Architecture | 512D full vector refresh/device | 128D full vector refresh/device |
|---|---:|---:|
| Full replication | 3.13344 GB | 0.78336 GB |
| Hybrid quarter-whitelist | 0.82944 GB | 0.20736 GB |
| Hybrid tenth-whitelist | 0.36864 GB | 0.09216 GB |

Actual synchronization traffic depends on update cadence, delta-update capability, compression, encryption/protocol overhead and whether whitelist partitions move between devices. Those remain open inputs.

## 12. What this tells us about `C_miss`

The 128D value in this edge scenario may come from more than storage price:

- fitting a larger local gallery into edge RAM/cache;
- allowing broader local replication of a security-relevant list while remaining offline-capable;
- reducing synchronization payload when galleries are refreshed;
- reducing dense coordinate work for each local observation;
- avoiding a higher hardware tier or increasing capacity headroom;
- allowing a simpler architecture with fewer remote dependencies.

Therefore:

```text
C_miss != storage_cost_only
```

A defensible Jungle Championship `C_miss` may include the value of **architectural freedom / offline autonomy** if an engineering owner can show that the 512D footprint actually constrains the target device or topology.

## 13. Parameters still required before economic calculation

The matrix is intentionally not yet a business case. The next values needed are:

| Input | Why it matters |
|---|---|
| Number and topology of edge devices | physical gallery replication |
| Per-zone whitelist fraction `g_i` | actual local gallery footprint |
| Observation flow `v_i`, including peaks | actual matching workload |
| Actual templates/person | gallery cardinality |
| Actual embedding datatype | bytes/vector |
| Actual blacklist size and update rate | globally replicated security workload |
| Whitelist registration/update cadence | synchronization traffic |
| Edge RAM/storage/compute constraints | determines whether 512D is actually limiting |
| Unmatched portrait format/retention | may dominate deferred-investigation storage |
| Permitted representative edge benchmark | converts structural proxy into measured performance |
| Cost/delay of new independent biometric evidence | value-of-information comparison |

## 14. Current admissible conclusion

The matrix shows that `512D -> 128D` creates an exact 75% reduction in embedding payload and dense coordinate-count at any fixed gallery/template configuration. In a distributed edge architecture, that saving is multiplied by physical gallery replication and may therefore have system-level architectural value.

It does **not** establish that Jungle Championship requires 128D, that the real 128D biometric candidate is acceptable, or that end-to-end latency/energy/cost improves by 75%.

The next scientifically admissible step is to populate real **engineering topology/resource values** that are outside the protected Study 1B biometric outcome boundary, then compute a bounded `C_miss` and value-of-information scenario.