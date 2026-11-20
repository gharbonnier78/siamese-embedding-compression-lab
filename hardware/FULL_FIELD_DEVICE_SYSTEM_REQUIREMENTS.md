# Siamese Embedded — complete mobile field-device system specification (v0.2)

Date: 2026-11-20. Status: **proposed requirements to validate**, not achieved specifications, electrical safety approval, biometric deployment permission, or environmental certification.

## Scope correction — authoritative boundary

The PRODUCT is a self-contained mobile (handheld, wearable, or tripod-mounted options to compare) **EO/RGB + NIR vision and local 1:N matching device**. It shall operate on-site without a companion PC, cloud, Ethernet, or cellular link. The always-on MCU, power-path, temperature/probe sensing and embedded telemetry are **subsystems inside the PRODUCT**, not the main deliverable.

A SECOND independent system, the **external experiment/qualification bench**, consists of a PC, calibrated power analyzer, thermocouple logger/environment sensors, optional chamber, load generator, trace ingestion, displays and audit/reporting. It is connected only for experimentation, service or post-hoc download; it MUST NOT be a runtime dependency for capture, wake, local inference, identification or power safety.

A THIRD system, the **design and manufacturing toolchain**, uses Flux.ai plus CAD, ECAD, SPICE, BOM, firmware and versioned review. A low-voltage probe carrier PCB is merely a first build increment; it is NOT the product.

### Source fidelity

Recovered August 20 concepts include: RGB wide-angle EO and NIR, hardware camera trigger, low-power passage sensor, embedded model and local 1:N gallery, allow/watchlist concept, optional Wi-Fi/5G and Ethernet/PoE, secured software update, hot-swappable batteries proposed, and energy/thermal/throughput metrology. The explicit mobile weather/lighting testing below is a **2026-11-20 user-requested extension**, not assumed to have been pre-qualified or specified in a historic drawing.

## System of systems (three independent blocks)

```text
         [ PRODUCT — MOBILE / AUTONOMOUS / ALL-WEATHER GOAL ]
 ┌─────────────────────────────────────────────────────────────────┐
 │ EO/RGB wide-angle + NIR camera + NIR emitter + HW sync          │
 │ PIR/mmWave passage/motion sensor + configurable wake/trigger     │
 │  → image quality/PAD* → face detection → alignment              │
 │  → pinned local model/NPU/CPU → embedding raw512 or 128D         │
 │  → exact/ANN 1:N gallery search → versioned list/policy rules    │
 │  → candidate / unknown / no-decision / authorized action        │
 │ Encrypted local gallery + indexes + event store + secure OTA    │
 │ Always-on MCU reads sensors, watches rails, controls wake/sleep  │
 │ Dual protected battery modules + validated hot-swap power path  │
 │ Housing/windows/seals/thermal interfaces; sunlight/rain/cold    │
 │ Optional Ethernet+PoE / Wi-Fi / cellular maintenance & sync     │
 └─────────────────────────────────────────────────────────────────┘
     standalone operation   │ OPTIONAL DIAGNOSTICS ONLY
                            ▼
 [ EXTERNAL BENCH — NEVER REQUIRED DURING NORMAL OPERATIONS ]
 ┌─────────────────────────────────────────────────────────────────┐
 │ PC/workstation, benchmark scripts, telemetry/time-series DB,   │
 │ OTA laboratory server, trace collector and visual dashboard    │
 │ Independent calibrated DC analyzer/shunts and thermal logger    │
 │ Weather/light/temperature exposure rigs and scenario replay     │
 │ Dataset/manifests/versions, statistical analysis, QA evidence   │
 └─────────────────────────────────────────────────────────────────┘

 [ ENGINEERING / FABRICATION TOOLCHAIN — NOT RUNNING ON THE DEVICE ]
 Flux.ai -> ECAD / SPICE -> PCB, BOM; CAD -> enclosure STEP/STL;
 engineering review -> prototype -> trial/measure/pivot/stop
```

*PAD is a separate validated capability and cannot be implied from using NIR.

## Primary field scenarios: optical + climatic + kinetic conditions

Each scenario should be exercised with authorized consenting subjects or controlled synthetic/phantom targets as appropriate. Set and justify actual extrema from the intended operating mission and chosen component ratings **before** performance testing; no arbitrary -20 °C or IP class is represented as passed.

| Scenario | Physical stress and conditions | Required evidence |
|---|---|---|
| Bright sun / midday | sun facing camera, backlit face, glare, fast lighting transitions, solar enclosure heating, NIR washout | per-sensor exposure/saturation, detection yield, quality, latency, false candidate and heat vs solar irradiance |
| Night / dim light | no visible ambient, NIR emitter duty cycle, moving subject, potential glare/reflectors | capture yield, NIR safety controls, operational energy, detection/recognition errors |
| Rain / water drops | rain, driven rain, water drops/film on window, condensation | functional continuity, lens occlusion rate, window cleaning need, ingress check and resulting no-decision rate |
| Cold / freezing risk | low ambient, wet-to-cold transition, battery discharge and safe charge restrictions, condensation on warming | measured startup/wake, BMS cutoffs, useful Wh, lens fog, low-temp recovery |
| Hot day / prolonged sun | high ambient plus solar load and model bursts, no easy forced-air inlet if sealed | internal/skin/pack temp, thermal time constants, throttling and safe shutdown |
| Humid / foggy | high relative humidity, cold-soak then warm, temporary clouding and seals | dew/condensation, quality decline, recovery and moisture damage |
| Moving device | walking, running, hand-held shake, vibration, horizon tilt, varying subject distances | blur, gyro/IMU sync, detection FN, false candidates, latency under movement |
| Moving subjects | 1,000 crossing/hour exploratory stress, multiple simultaneously visible, occlusion, head turn, scale | track/deduplication, dropped frames, track continuity, FTA/FTC, per-event energy and operator burden |
| Sun ↔ shade / indoor ↔ outdoor | fast optical and thermal transitions | adaptation time, stable trigger thresholds, image normalization |
| Loss of network | Wi-Fi/5G/Ethernet disconnected for whole mission | 100% local pipeline continuity, policy freshness warning, secure store-and-forward |
| Battery swap under load | hot-swap A/B while 1:N burst running | continuous power, zero resets, no corrupted indexed gallery, battery-safe temperatures |
| Security & maintenance | authenticated periodic sync, signed OTA, no network and interrupted update | rollback, offline behavior, update energy, tamper and audit trails |

## Environmental and optical engineering requirements — prospectively testable

- **Housing:** target ingress-protection class selected from mission (IEC 60529 such as IP65 as a *candidate*, never a claim); sealing all camera windows, power/battery doors and connectors; serviceability and drop/vibration/strap mounting. IP rating requires tested complete assembly; a material datasheet alone is insufficient.
- **Thermal:** choose heat spreader, conduction path, TIM, exposed surface temperature and passively sealed cooling strategy; evaluate solar heating + AI load and cold-start. Fanless is a preference subject to measured viability, not an unconditional constraint. Evaluate battery and optics separately.
- **Optics:** RGB & NIR field of view, wavelength, anti-reflection/transmission, weather window fogging, drops, cleaning, sun shading, illumination safety (IEC 62471 applicable evaluation and sensor-dependent controls), sensor time sync, rolling/global shutter comparison, motion blur and exposure.
- **Sensors:** PIR vs mmWave passage trigger may degrade with ambient heat, weather, clothing, motion; test detection ranges/false wakes in realistic contexts; IMU and ambient light/IR monitor are candidate readout probes.
- **Power:** actual autonomy per power state (not nominal 20Wh), battery pack temperature effects, commercially protected two-pack hot-swap and verified power rails/hold-up. Avoid DIY lithium design.
- **Secure stand-alone behavior:** identity/policy snapshot, encrypted local indexes, secure key storage, signed model+OTA updates and rollback, privacy-preserving local telemetry, deterministic model execution; the optional PC/cloud collects results only.
- **Biometric validity:** keep detection failure/FTA/FTC vs quality vs PAD vs 1:1 FMR/FNMR vs 1:N FPIR/FNIR separated by capture regime, and distinguish confidence intervals from single observations; unknown not automatically in denylist. Do not test real watchlists or unconstrained street identification without separate authorizations.
- **Observability:** log conditions (ambient temp, RH, illuminance, internal sensor temp, wind/rain as externally measured, IMU, battery), camera mode, exposure/gain, sun angle/scene label, power/Wh, thermal throttle, latency and no-decision. Associate timestamps to trace/span IDs and calibration/firmware/model/gallery versions.
- **Environmental tests:** use IEC 60068 series as a source of test methods and IEC 60529 for enclosure ingress; final relevant editions, severity/dwell times and official approvals to be chosen in documented design review, not automatically claimed.

## TWO BOMs and two software scopes

**PRODUCT BOM** — on-device compute SoM + storage + two cameras + NIR light and safety + wake and environmental probes + IMU + power path and dual smart protected battery modules + MCU + PCB(s) + housing + optical windows/seals + mechanical mounting + ports/radios + service update/security. Device runs matching and sensor acquisition locally.

**EXPERIMENT BENCH BOM** — independent DC power analyzer, calibrated temperature data logger, ambient lighting measurement, rain/cold/heat/exposure test arrangements, lab PSU, bench PC, timing sync hardware, instrument cables and software. No PC or external meter needs to be installed inside the carried device.

**On-device software:** watchdog/sensor MCU firmware, GPIO wake, camera sync, detection and quality, pinned model/runtime, local 1:N matching, authorized gallery and list policies, secure OTA, local data retention; no LLM on critical path.

**Bench software:** reproducible deterministic workloads and synthetic gallery generation, trace/time-series ingestion, latency and biometric-error reporting on permitted data, thermography/energy joins, uncertainty computation, dashboard, automated replay and STOP/PIVOT/PERSEVERE ledger.

## Required system-first Phase 0 outputs for Flux.ai

1. Overall PRODUCT functional and physical architecture (not only MCU/PCB), ergonomic concept alternatives for mobile, fixed and carried operation; external PC clearly outside product.
2. Optical/environmental concept with RGB/NIR geometry, FOV, active illumination safety, sunlight vs nighttime modes, rain/condensation management and changing conditions.
3. Compute feasibility matrix: selected vendor+revision, model operator compatibility, 1:N 100k/500k/1M RAM/flash/index, cameras, predicted vs measured energy explicitly differentiated.
4. Power / thermal / mechanical subsystem concept including two commercial hot-swappable packs; stand-alone operation and accessible battery door while sealed; no unreviewed charger PCB.
5. Physical packaging and mass/volume/center-of-gravity/ergonomics options, materials, environmental/impact targets, 3D interface skeleton but no invented component dimensions.
6. **PRODUCT BOM** and separate **BENCH BOM**, both sources/MPN and TBD, uncertainty and per-subsystem power budget.
7. Instrumentation/telemetry interface control: probe readout and timestamp sampling; bench-to-device connection only diagnostic; no runtime dependence on PC.
8. Environmental and biometric field-validation matrix with safe/ethical data scope and independent evidence thresholds.
9. Decomposition into 3 possible first manufacturing increments: COTS SoM+camera mobile integration; independent low-voltage probes PCB; dedicated housing after measured components.
10. Issue/assumption/change register and falsifiable architecture trade-off alternatives. No PCB schematic until full-device boundary and user review.

## Standards references (test-method context, not certificates)

- IEC 60529: ingress protection of electrical equipment enclosures (https://webstore.iec.ch/en/publication/2452).
- IEC 60068 environmental test family (https://webstore.iec.ch/).
- ISO/IEC 30107-1:2023 PAD framework (https://www.iso.org/standard/83828.html).

**Scientific guardrail:** existing Study 0 remains negative; Study 1B protected qualification sets remain sealed. This file is a separate product-engineering specification, not an authorized biometric effectiveness result.
