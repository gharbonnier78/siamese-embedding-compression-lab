# Embedded Software and Metrology

## Product: offline by design

Fixed mission on a calibrated support. Attach site profile, calibration version and flow direction to traces. Verify local operation without network access independently of PoE availability. Log data loss, power loss, switchover, backup duration and recovery as distinct events. Gallery metadata and signed policy are separate; no candidate triggers action without human review.

- **MCU:** State machine, watchdog, RTC, nonvolatile circular log, wake, rail control and NIR inhibit. Linux cannot bypass hardware protections. Synchronize clocks on wake; retain sequence counter and session ID across resets as applicable.
- **Linux:** Capture and hardware timestamp → quality check → detection/alignment → fixed model and preprocessing → embeddings → exact reference search or approximate index tested on identical queries → separate local policy engine. Distinguish candidate, unknown and no decision; unknown does not trigger a list rule. No LLM on the critical path. No PAD capability assumed validated.
- **Data:** Encrypted storage; hardware-protected keys where supported; least privilege; signed and versioned models, indexes and policies; minimized logs with no images by default. Local or authorized network update, signatures, A/B partitions or equivalent, rollback to known version after interruption and offline freshness policy. Verify secure boot, update and rollback on the target SKU. No real lists or identifiable data in Flux.
- **Bench:** Deterministic scenarios and synthetic galleries, instrument capture, uncertainty and distribution analysis, dashboard and decision log. PC absence does not interrupt product operation.

## Compute feasibility

Evaluation candidate: [Radxa ROCK 5B](https://docs.radxa.com/en/rock5/rock5b), RK3588 family; exact revision/SKU/RAM unselected. Comparator: Linux CPU without NPU on identical workloads. Freeze OS, model, precision and drivers for qualification; identify unsupported operations and CPU fallback. Measure end-to-end latency, peak RAM, storage throughput, J/query and temperature with both cameras and concurrent processing. Dual synchronized capture and module compatibility are unproven. Verify secure boot, eMMC/NVMe endurance and A/B storage. Power unmeasured; do not infer performance from TOPS.

| Gallery | 512D float32 | 128D float32 |
|---|---:|---:|
| 100k | 204.8 MB | 51.2 MB |
| 500k | 1,024 MB | 256 MB |
| 1M | 2,048 MB | 512 MB |

Decimal vector-only size: N × D × 4 bytes. Measure RAM copies, page cache, index, metadata, extraction and dual disk versions separately. Compare approximate recall against exact search, index size/rebuild time and burst p50/p95/p99. These figures are not hardware measurements.

## Telemetry contract — provisional sampling

| Probe | Reader and interface | Sampling and retention |
|---|---|---|
| PIR, tamper, reset, Power Good | Always-on MCU GPIO IRQ | Each edge; RTC + monotonic clock, durable log |
| DC/PoE input, rails and protected reserve | MCU I²C/ADC monitor and vendor BMS | Initially 1 Hz active, 0.1 Hz standby plus fault edges; independent fast analyzer for dips |
| Heatsink/shell/ambient/emitter temperature and humidity | MCU I²C/ADC; separate NIR protection | Initially 1 Hz active, 0.1 Hz standby; positions matched to external logger |
| SoC/throttling, free space and communications | Linux drivers, MCU for status signal | 1 Hz during tests and on events; local while offline |
| Cameras, NIR pulses, IMU | Trigger counter, sensor metadata, SPI/I²C IMU | Per frame/pulse; IMU initially 100 Hz, tune to vibration |
| DC, thermal, illumination and rain references | Bench | Set by shortest event and uncertainty; shared marker and independent calibration |

Event schema: trace/span ID, timestamps and estimated MCU–Linux–bench offsets, conditions, exposure/gain, sensor/calibration/firmware/model/gallery versions, loss count and no-decision cause. Bound retention, authenticate exports and signal saturation; size buffer and define retention from mission. Calibrate current, voltage and temperature against references; report offset, drift and uncertainty. Logging rates are not protection response rates.
