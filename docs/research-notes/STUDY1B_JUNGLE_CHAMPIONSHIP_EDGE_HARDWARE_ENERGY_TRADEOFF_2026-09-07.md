# Study 1B — Jungle Championship edge hardware, RAM and energy trade-off

**Date:** 2026-09-07  
**Status:** non-outcome engineering decision analysis  
**Boundary:** no protected Study 1B SCREEN, qualification TEST result, real-route performance, representation geometry or amendment is opened.

## 1. New hard engineering constraint

For the Jungle Championship edge use case, the local biometric galleries must fit in RAM.

This changes the engineering question from a generic storage comparison into a feasibility/cost problem:

> Which combination of embedding representation, datatype, compute architecture and RAM can keep the required galleries resident in memory while still satisfying peak-flow response and battery/power constraints?

The representation reference remains **raw512 / 512D**. The compressed candidate remains **128D**. CPU, GPU/NPU and associated memory are implementation alternatives, not scientific replacements for the reference claim.

## 2. Comparison hierarchy

The decision should be made in layers.

1. **Biometric representation:** 512D reference versus 128D candidate.
2. **Encoding:** FP32 / FP16 / INT8 as separate engineering axes; quantization is not silently conflated with dimensional compression.
3. **Memory feasibility:** gallery plus index plus application/OS safety headroom must fit in system RAM or accelerator-accessible RAM.
4. **Compute platform:** CPU is preferred economically when it satisfies response requirements at peak flow; GPU/NPU remains an option when CPU cannot meet the service envelope or when accelerator efficiency is superior.
5. **Response under bursts:** mean latency is insufficient; measure throughput, p95/p99 latency, queue growth and recovery under representative ingress peaks.
6. **Electrical/thermal/battery:** compare average power, peak power, energy per identification/burst, autonomy and any change in battery/power-system sizing.
7. **Fleet economics:** only after per-device feasibility is established should device count multiply BOM, memory, synchronization or battery-value differences.

## 3. RAM first, not raw storage price

For the central scenario already archived (`500k whitelist + 10k blacklist + 3 templates + FP32`), full replication requires about 3.13 GB of vector payload per device in 512D and 0.78 GB in 128D, before index/database overhead and application headroom.

The relevant question is therefore not simply the price of 2.35 GB of memory. It is whether the full working set crosses a practical tier such as 4 GB, 8 GB, 16 GB or an accelerator-memory boundary after all non-gallery needs are included.

If 512D requires a larger hardware tier and 128D does not, the economic effect is discontinuous and can dominate the raw €/GB calculation.

## 4. CPU versus GPU/NPU

CPU remains a valid and potentially preferred architecture when:

- the gallery fits in RAM with safe headroom;
- exact or qualified indexed search meets peak throughput;
- response-time percentiles remain compatible with the operational requirement during bursts;
- queueing remains bounded;
- power and thermal behavior are acceptable.

GPU/NPU can be justified when one of these conditions fails or when it produces a better total cost/energy envelope. A faster accelerator is not automatically cheaper or lower-energy: idle power, memory subsystem, batch requirements and duty cycle matter.

The correct benchmark is therefore a matrix, not a single speed test:

`{512D,128D} × {FP32,FP16,INT8} × {CPU,GPU/NPU} × {gallery size} × {peak-flow profile}`.

Any ANN/index approximation that can change returned identities must be treated as a separate qualified method, not a pure implementation optimization.

## 5. Electrical consumption and battery autonomy

Embedding compression can plausibly reduce arithmetic and memory traffic, but the exact 75% coordinate reduction from 512D to 128D does **not** imply 75% lower device energy.

The device power budget contains several components:

- compute idle and active power;
- RAM idle/active power and memory bandwidth activity;
- camera/sensor baseline;
- NIR/illumination duty cycle;
- network communication;
- local storage and control electronics.

For a first-order workload model:

```text
P_avg = fixed/sensor/network baseline
      + compute duty-cycle contribution
      + RAM contribution
```

and battery autonomy is determined from usable battery energy divided by measured/estimated average power.

The most useful measurements will be:

- joules per identification at representative gallery sizes;
- joules and p95/p99 latency during a peak burst;
- Wh per match/day under a realistic traffic trace;
- idle/standby power between bursts;
- battery Wh needed to meet the required autonomous interval with reserve.

A CPU can therefore win even if each identification is slower, provided it still meets the burst SLA and reduces BOM/power enough. Conversely, a GPU/NPU can win on energy if it completes bursts quickly enough to return to a low-power state, despite higher instantaneous power.

## 6. Energy value in `C_miss`

The engineering value of an acceptable 128D route can now include:

```text
V_128D = V_RAM_tier
       + V_compute_platform
       + V_energy_or_battery
       + V_sync
       + V_offline_autonomy
       + other measured capacity/enabling value
```

`V_energy_or_battery` may represent:

- smaller battery required for the same autonomy;
- longer autonomy with the same battery;
- fewer battery swaps/recharges;
- smaller PSU/solar/power-distribution requirement;
- lower thermal-management need;
- lower energy cost over the fleet.

These terms remain zero/unknown until measured or explicitly estimated with provenance.

## 7. Recommended first benchmark envelope

Before assigning monetary value, benchmark feasibility with the following structure:

| Axis | Values / status |
|---|---|
| Representation | 512D reference, 128D candidate |
| Datatype | FP32 baseline; FP16/INT8 as separate candidates |
| Gallery population | 250k / 500k / 750k / 1M whitelist + blacklist scenarios |
| Templates/person | 1 / 3 / 5 |
| Gallery residency | RAM mandatory |
| Compute | CPU and GPU/NPU alternatives |
| Flow | low/central/peak burst profile |
| Response | throughput + p95/p99 + queue recovery |
| Energy | idle W, active W, J/query, Wh/burst, Wh/day |
| Battery | usable Wh, reserve, autonomy hours |
| Fleet `D` | 25 / 50 / 100 only after per-device results |

This keeps 512D as the stable representation reference while allowing the engineering design space to vary independently.

## 8. Current conclusion

The key question is no longer merely whether 128D saves bytes. It is whether 128D changes one or more **engineering feasibility thresholds**:

- gallery fits in a lower RAM tier;
- CPU becomes sufficient where 512D would need an accelerator;
- accelerator memory tier can be reduced;
- peak-flow response remains acceptable with cheaper/lower-power compute;
- battery autonomy or power-system size materially improves;
- broader offline replication becomes feasible.

Those threshold crossings are the most plausible high-value contributors to `C_miss` and therefore to the value of acquiring additional independent biometric evidence.
