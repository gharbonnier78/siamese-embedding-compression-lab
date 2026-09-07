# Study 1B — Jungle Championship edge scenario assumptions

**Date:** 2026-09-07  
**Status:** non-outcome engineering scenario capitalisation  
**Purpose:** provide a concrete deployment scenario for the Study 1B `512D -> 128D` engineering-value / `C_miss` analysis.  
**Boundary:** no Study 1B SCREEN, qualification TEST result, real route performance, representation geometry or amendment is opened by this note.

## 1. Provenance classes

This note deliberately separates three classes:

- **USER-PROVIDED** — facts/assumptions supplied explicitly in the project conversation;
- **DERIVED** — arithmetic or structural consequences of supplied values;
- **SCENARIO** — exploratory values proposed for sensitivity analysis and not asserted as event facts.

The scenario is an engineering thought model. It is not presented as an audited event specification.

## 2. Event and attendance envelope

| Element | Current value / assumption | Provenance |
|---|---:|---|
| Event duration | 5 days | USER-PROVIDED |
| Matches per day | 3 | USER-PROVIDED |
| Total matches | 15 | DERIVED |
| Stadium capacity | 50,000 people | USER-PROVIDED |
| Maximum spectator-passages if every match is full | 750,000 | DERIVED |
| Unique spectators | less than or equal to 750,000 because repeat attendance is expected | USER-PROVIDED + DERIVED |
| Same spectators across matches | some repetition is expected but rate is unknown | USER-PROVIDED |
| Technical/event staff | recurrent population across event days/matches | USER-PROVIDED |
| Contractors/subcontractors | numerous; potentially recurrent | USER-PROVIDED |

The 750,000 value is a **passage envelope**, not an estimate of unique identities.

## 3. Biometric populations and decision roles

| Population | Meaning in scenario | Primary treatment | Provenance |
|---|---|---|---|
| Whitelist | persons authorized for the event: spectators, technical staff, organizing staff, contractors/subcontractors and other authorized roles | local/edge `1:N` authorization/recognition logic | USER-PROVIDED |
| Blacklist | restricted list of stadium-banned persons, potentially extended with nationally/internationally wanted persons | local/edge `1:N` detection/alert logic | USER-PROVIDED |
| Neither whitelist nor blacklist | observed persons with no local-list match | retain portrait + location + time for later national offline `1:N` identification | USER-PROVIDED |
| National offline gallery | downstream national identification reference | deferred `1:N` investigation | USER-PROVIDED |

The blacklist is expected to be materially smaller than the whitelist, but no audited cardinality is currently supplied.

## 4. Distributed edge topology

The edge devices are distributed across many physical locations. A logical identity is **not unique to one device**, and a person does **not** pass in front of every camera/device.

This creates four separate quantities that must not be conflated:

1. **Unique event identities** — logical persons in the event-level population.
2. **Gallery copies loaded on devices** — physical replication/partitioning of identities/templates across edge devices.
3. **Local observations / passages** — how often persons are observed by each device.
4. **Total matching work** — function of local observations, local gallery size, templates and embedding dimension.

A naive `people x cameras` load model is therefore invalid for this scenario.

## 5. Variables for the engineering model

| Symbol | Meaning | Current state |
|---|---|---|
| `N` | unique identities in the relevant event-level gallery | unknown / scenario variable |
| `U` | unique people actually attending/appearing | unknown / scenario variable |
| `T` | templates per identity | scenario: 1 / 3 / 5 |
| `D` | number of edge devices | unknown |
| `g_i` | fraction of global gallery loaded on device `i` | unknown / architecture-dependent |
| `v_i` | observations/passages processed by device `i` | unknown / topology- and flow-dependent |
| `B` | blacklist size | unknown; sensitivity scenarios may be used |
| `b` | bytes per embedding component | datatype-dependent |
| `d` | embedding dimension | 512 or 128 |
| `O` | total biometric observations across all devices | unknown; generally greater than unique persons |

## 6. Structural formulas

For device `i`, if the local gallery is a fraction `g_i` of a global gallery of `N` identities with `T` templates per identity, the embedding payload is:

```text
local_gallery_bytes_i = N * g_i * T * d * b
```

Total edge gallery payload is:

```text
sum_i N * g_i * T * d * b
```

For brute-force dense `1:N` comparison, a first-order matching-work proxy is:

```text
work_i proportional to v_i * (N * g_i * T) * d
```

This is a structural proxy only. It does not assert end-to-end latency or throughput because indexing, batching, SIMD/accelerator behavior, memory access and fixed system costs may dominate.

## 7. Population sensitivity scenarios

The following are **SCENARIO values**, not supplied event facts.

### Whitelist

| Scenario | Unique identities |
|---|---:|
| low | 250k |
| central | 500k |
| high | 750k |
| stress/extension | 1M |

These values are intended to span different repeat-attendance assumptions and possible inclusion of recurring staff/contractor populations.

### Blacklist

| Scenario | Identities |
|---|---:|
| small | 1k |
| medium | 10k |
| large/stress | 100k |

These values are exploratory only until an authoritative blacklist size is provided.

### Templates and representation

```text
T in {1, 3, 5}
Dimension in {512, 128}
Datatype in {FP32, FP16, INT8} where technically meaningful
```

The earlier Study 1B engineering envelope can therefore be exercised over `population x templates x dimension x datatype` without opening biometric outcomes.

## 8. Edge gallery architecture scenarios

Three architectures should be kept distinct.

| Architecture | Whitelist | Blacklist | Engineering consequence |
|---|---|---|---|
| A — Full replication | complete on every relevant device | complete | maximum offline autonomy; maximum gallery replication |
| B — Partitioned | partitioned by zone/role/access domain | complete or partitioned | lower local memory/work; more routing/configuration complexity |
| C — Hybrid | localized/partial whitelist | broadly replicated blacklist | compromise between offline security coverage and edge resource limits |

**C — Hybrid** is the current central **SCENARIO hypothesis**, not an established production architecture.

## 9. Unknown-person retention

For persons in neither whitelist nor blacklist, the scenario retains:

```text
portrait + location + timestamp
```

for deferred national offline identification.

This means the 512D-to-128D embedding reduction may be a secondary storage effect for this branch if portrait image bytes dominate. Portrait format, retention count, retention period and duplicate/event association rules remain unknown.

## 10. Why this matters to `C_miss`

In this scenario, the engineering value of an acceptable 128D representation may include more than raw storage reduction:

- smaller replicated/local galleries;
- more gallery content fitting in edge RAM/cache;
- reduced synchronization/transfer payload;
- lower coordinate-level comparison work;
- increased freedom to replicate security-relevant lists locally;
- increased offline autonomy;
- potentially simpler device sizing or greater capacity headroom.

These are **value categories**, not measured benefits. Monetary/system values must remain unknown until supplied or benchmarked.

A lost/delayed acceptable compression can therefore create `C_miss` through constrained edge architecture, not only through storage cost.

## 11. What must be measured or supplied next

Before a numerical Jungle Championship `C_miss` can be computed, obtain or scenario-bound:

- actual or intended device count `D` and topology by zone;
- gallery-routing rule / expected `g_i` distribution;
- local observation-flow distribution `v_i`, including peak ingress devices;
- templates per identity;
- embedding datatype;
- blacklist cardinality and update frequency;
- whitelist cardinality / registration process / repeat-attendance estimate;
- portrait format and retention policy for unmatched persons;
- network synchronization/update cadence;
- edge RAM/storage/compute constraints;
- measured 512D vs 128D benchmark on representative edge hardware if permitted;
- cost/delay of additional independent biometric evidence.

## 12. Scientific boundary reminder

This scenario is used only to evaluate the **engineering consequence of a missed acceptable compression** and the value of additional evidence. It must not be used to infer real Study 1B biometric accuracy, real FMR/FNMR, representation geometry, or a production release decision.
