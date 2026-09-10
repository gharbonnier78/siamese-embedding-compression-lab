# Study 1B — Jungle Championship device-count and edge-cost sensitivity

**Date:** 2026-09-07  
**Status:** non-outcome engineering scenario analysis  
**Boundary:** no protected Study 1B biometric outcome, SCREEN, qualification TEST result, real-route performance, geometry or amendment is opened by this note.

## 1. Question

How much does the number of distributed edge devices matter for the 512D -> 128D value analysis?

The answer is: **device count matters mainly for replicated physical cost and total distributed capacity; it is not, by itself, a per-device biometric-performance parameter.**

A larger `D` multiplies any gallery payload that is physically replicated on every device. It also affects synchronization traffic, fleet BOM/capacity and aggregate energy/cost. But the per-device matching burden is primarily controlled by that device's local gallery and local observation flow.

## 2. Scenario estimate for Jungle Championship

No deployment design has supplied an actual device count. For the five-day, 50,000-capacity stadium scenario with entrances, circulation areas, staff/technical zones, parking/perimeter and distributed offline-capable biometric points, use the following **engineering sensitivity only**:

| Scenario | Edge devices `D` | Meaning |
|---|---:|---|
| Low | 25 | relatively sparse deployment / major access points only |
| Central | 50 | distributed stadium deployment with multiple public and controlled zones |
| High | 100 | dense deployment / broader perimeter and internal coverage |

`D = 50` is retained as the central **scenario estimate**, not as an event fact.

## 3. Why D does and does not matter

### D directly multiplies

- total physical copies of replicated whitelist/blacklist embeddings;
- aggregate gallery RAM/storage footprint across the fleet;
- total gallery synchronization/update payload when the same content is pushed to many devices;
- any per-device hardware-tier premium caused by larger memory/capacity requirements;
- fleet-wide capacity or energy differences if demonstrated by measurement.

### D does not directly determine

- the number of unique people at the event;
- how many devices a particular person passes;
- per-device local observation rate `v_i`;
- per-device latency unless device count changes flow allocation/topology;
- biometric accuracy or Study 1B non-inferiority.

More devices can even reduce per-device flow if a fixed ingress volume is distributed among more lanes/devices. Therefore `D` and `v_i` must not be collapsed into one parameter.

## 4. Central structural point reused from the archived matrix

Sensitivity point, not event fact:

- whitelist `N = 500,000`;
- blacklist `B = 10,000`;
- `T = 3` templates/person;
- FP32 (`b = 4` bytes/component).

### Full local replication

Per device:

- 512D gallery payload: 3.13344 GB;
- 128D gallery payload: 0.78336 GB;
- exact vector-payload saving: 2.35008 GB/device.

Fleet sensitivity:

| Devices | 512D payload | 128D payload | Avoided payload |
|---:|---:|---:|---:|
| 25 | 78.336 GB | 19.584 GB | 58.752 GB |
| 50 | 156.672 GB | 39.168 GB | 117.504 GB |
| 100 | 313.344 GB | 78.336 GB | 235.008 GB |

### Hybrid: 25% of whitelist local + full blacklist

Per device:

- 512D payload: 0.82944 GB;
- 128D payload: 0.20736 GB;
- avoided payload: 0.62208 GB/device.

Fleet sensitivity:

| Devices | 512D payload | 128D payload | Avoided payload |
|---:|---:|---:|---:|
| 25 | 20.736 GB | 5.184 GB | 15.552 GB |
| 50 | 41.472 GB | 10.368 GB | 31.104 GB |
| 100 | 82.944 GB | 20.736 GB | 62.208 GB |

These values are vector payload only. They exclude database/index overhead, portraits, metadata, operating system, application memory, replication protocol framing and storage redundancy inside each device.

## 5. Economic interpretation: the key non-linearity

For `C_miss`, the device count becomes economically important when the representation dimension changes the **hardware or architecture tier**.

Examples of the decision logic:

- if both 512D and 128D fit comfortably in the same device RAM/storage tier, the direct BOM saving from memory may be close to zero even though several GB are structurally avoided across the fleet;
- if 512D forces a higher RAM/storage SKU while 128D fits the lower tier, the benefit becomes approximately `D * hardware_tier_delta`, potentially much larger than the raw storage-price value;
- if 128D makes full or broader offline gallery replication feasible, the value is architectural/operational rather than merely €/GB;
- if gallery synchronization is costly or connectivity constrained, `D` multiplies the transfer benefit of smaller embeddings.

Thus the most important next hardware input is not simply the price of a GB. It is:

> **Does the 512D-vs-128D difference cross a device resource threshold or change the feasible edge architecture?**

## 6. Recommended treatment in the decision model

Keep device count as a sensitivity parameter:

```text
D in {25, 50, 100}, central = 50
```

and separate three value terms:

```text
V_edge_memory_payload = D * avoided_payload_per_device * attributable_storage_or_RAM_rate
V_device_tier = D * hardware_tier_delta, if a threshold is actually crossed
V_sync = D * update_frequency * avoided_gallery_transfer_bytes * transfer_or_operational_rate
```

Do not assign monetary values until device BOM, RAM/storage tiers, update cadence and architecture are supplied or measured.

## 7. Consequence for Study 1B value of information

The number of devices is therefore **secondary to the scientific power question**, but can be first-order for `C_miss` because it scales the engineering value of an acceptable 128D route across the fleet.

If the fleet effect is small and raw512 remains easy to deploy, the value of paying for new independent biometric evidence may be low. If the compression crosses a hardware/offline-autonomy threshold across dozens of devices, `C_miss` can become materially larger and additional evidence can become easier to justify.

## 8. Next required inputs

- approximate device RAM/storage tier(s) and available headroom;
- whether whitelist/blacklist vectors must reside in RAM, local SSD/eMMC, or both;
- actual or design-target device count/topology;
- gallery update cadence;
- approximate per-device BOM delta between relevant memory/storage tiers;
- whether 512D prevents a desired offline/full-or-partial replication architecture;
- local flow/peak load only for compute analysis, kept separate from `D`.
