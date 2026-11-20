# Edge-device metrology, falsification, trial-and-adjust protocol

**Status:** prospective exploratory engineering only; not a retrospective biometric result. All performance claims must state workload, model/configuration hash, hardware ID, firmware/runtime versions, measured ambient conditions, and statistical uncertainty.

## Hypotheses

H-E1: Compression may reduce gallery/index memory footprint and search energy on-device; energy gain could be negligible for capture/extraction-dominated workloads.
H-E2: Sleep/PIR gating may improve autonomy much more than embedding compression.
H-E3: Increasing gallery size 100k to 1M may move search from cache-resident to bandwidth-bound and change 128D benefits.
H-E4: An active cooling path may improve sustained throughput but raise battery draw and maintenance.
H-E5: No value may survive real operating constraints (false alerts, operator handling, energy, privacy, costs, false nonmatches).

## Required instrumentation and trace provenance

External time-aligned DC power meter / power analyzer on device input (including the chosen regulated supply boundary); optional separate rails for accelerator, RGB/NIR, communication and battery. Measure voltage/current/power, active/inactive energy, startup peaks, battery coulomb balance, charger losses if relevant, and instrument overhead. Time-synchronized sensor telemetry for ambient, CPU/SoC, heatsink, enclosure surface and battery temperatures. Record clock throttling, governor, fan state, frequency, utilization, temperature and ambient airflow.

Recommended raw fields:
`timestamp_utc, run_id, unit_id, scenario_id, mode, power_boundary, voltage_V, current_A, power_W, energy_Wh_cumulative, ambient_C, soc_C, heatsink_C, enclosure_surface_C, battery_C, throttled, battery_soc_pct, gallery_size, embedding_dim, route_id, index_type, accuracy_protocol_id, software_sha256, model_sha256, dataset_sha256_or_synthetic_seed, board_revision, cad_revision, battery_pack_id, instrument_id, calibration_id, sample_rate_hz, trace_id, span_id`.

Energy = integral(P(t) dt). Report joules per *successful verified operation*, joules per detected event, joules per candidate list produced, joules per 1:N query, and standby watt-hours per day. Duty-cycle autonomy must be verified on actual approved battery and charger, not solely extrapolated from nominal Wh. Keep separate stand-alone runtime, mission duration, charging requirements, and thermal survival.

## Test matrix (prospectively frozen per campaign)

Modes: OFF, SLEEP, IDLE WATCH, DETECTION ONLY, VERIFICATION 1:1, IDENTIFICATION 1:N, BURST, TRANSMIT, THERMAL-SOAK, RECOVERY.
Gallery sizes: 100000, 500000, 1000000 (synthetic for preliminary load; genuine biometric test only with authorization).
Representations: raw512, random128, PCA128, Siamese128 where scientific gates and license allow; otherwise synthetic workload only.
Index paths: exhaustive baseline + selected ANN; report candidate recall, index build time, rebuild cost, storage, RAM/flash bandwidth, working-set vs last-level cache, backend and dispatch shape.
Conditions: start at a documented nominal ambient, then examine elevated conditions, weak radio, low battery, restart and repeated bursts. Freeze chosen temperatures and repetitions before running.
Thresholds: select on VALIDATION, never tune on independent TEST; separate verification FMR/FNMR and identification FPIR/FNIR + rank-k. Report confidence intervals clustered by identity/session and PAD failures separately. No unconsented face collection.

## Measured end-to-end breakdown

For each event associate monotonic clock intervals with OTEL trace/span IDs, where feasible: wake, exposure, capture, detection, quality/PAD, alignment, extractor, projection, gallery fetch, index, matcher, post-processing, user decision, notification and recovery. Annotate active power segments; the external meter is the energy source of truth. Fixed workloads are replayed in common matched order with randomized/blocked route scheduling to reduce thermal/order bias. Control for CPU governor, thermal state, clocks, OS services, acceleration backend and index recall. Distinguish low-level projection energy from end-to-end energy and peak/current sizing.

## Decision method: baseline, trade-off, adversarial alternatives

Compare with a simpler non-biometric presence sensor, camera plus cloud compute when lawful and feasible, local face verification with smaller identity roster, centralized 1:N, and uncompressed model on the same board. Use a cost model:
`TCO = equipment + assembly + energy + connectivity + maintenance + failures + handling_false_alerts + replacement + data-governance_costs`.
Do not price a security-critical accuracy loss with arbitrary weights: hard safety, privacy, legal and operational false-identification/false-rejection constraints act as feasibility gates. Among feasible options, show Pareto frontier (energy, battery life, p95 delay, memory, FPIR/FNIR, TCO, cost of manual intervention).

**Falsification:** Reject as useless if the use case has no compelling human need; if a simpler non-biometric alternative dominates; if privacy or operational error constraints fail; if expected savings collapse end-to-end; or if thermal/power/autonomy constraints cannot reasonably be met. **Pivot:** adjust power-gating, camera, board, quantization, gallery size, offload or mission design if a specific measured bottleneck justifies it. **Persevere:** only when repeatable, uncertainty-qualified experimental improvements and user value warrant further spend.

## Evidence gates

- P0: establish externally measured idle and load power, timestamps, calibration and replay on breadboard; reject unsupported energy claims.
- P1: controlled multi-mode engineering benchmark using synthetic galleries, with raw traces, manifest, no claims about biometric accuracy.
- P2: mechanical / thermal fit and battery sizing by actual duty-cycle, with electrical and enclosure safety review.
- P3: a separately approved biometric evidence campaign on permitted data, without violating Study 1B's sealed outcomes.
- P4: five-day scenario validation only if production-like integration and the privacy/consent operating context are justified.

All decisions append-only, with explicit `STOP`, `PIVOT`, `PERSEVERE` and owner/date/evidence. Preserve even negative results.
