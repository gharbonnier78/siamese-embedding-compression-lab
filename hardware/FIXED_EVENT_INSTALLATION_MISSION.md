# Siamese Embedded — Fixed event-installation mission baseline (2026-11-20)

**Authoritative user clarification: supersedes prior "mobile, handheld, walking with device, harness" variants.** This project is a **temporarily installed, wall- or fixed-support-mounted, self-contained EO/RGB + NIR edge identification research unit** for event entrance/passage zones. The device stays immobile during its mission; people move through a largely known viewing zone. A tripod is only an optional temporary installation, setup, calibration or controlled measurement fixture. A nearby PC is **only** for independent experimental supervision, metrology, analysis and reporting: it is not the runtime host for inference/matching.

## Frozen mission reference (NOT qualified performance)

- Expected scenario: approximately 1,000 pedestrian encounters/hour, 10 hours/day, 5 consecutive days; actual arrivals may be clustered, multiple persons per field of view and non-cooperative in pose. This is a load/test hypothesis, not achieved performance.
- Gallery scales to benchmark independently: 100k, 500k, 1M reference identities; local encrypted gallery and indices, separate versioned authorization/watchlist metadata, local 1:N (and optional 1:1), unknown/no-decision semantics.
- **Power preference for fixed deployment**: suitable PoE (if verified electrical budget) or regulated mains/DC for mission duty, plus buffered/replaceable protected backup power for interruptions. The backup may be hot-swappable only if the validated continuity and power/charging architecture makes sense. Do not size five days from a 20 Wh demonstrator battery or require battery-only field operation without need.
- **Installation**: authorized temporary wall plate/bracket, event truss/pole or equivalent secure fixed mount; consider quick-install/remove, repeatable calibration, cable retention, anti-tamper, safe public access, no unsafe fixings, ingress protection as dictated by indoor/outdoor use, discreet enclosure. Fit wall-to-optical axis, distance, FOV, height and crowd flow after site survey.
- **Device autonomy** means runtime independence from a PC or network: local model, CPU/NPU, embedded matching, allowed data and configuration, wake/PIR, camera trigger, local evidence retention and safe watchdog. It does NOT mean necessarily running from battery alone.
- **EO/IR**: visible RGB and NIR capture with safe NIR illumination and synchronized triggers; a thermal LWIR scene camera is an optional *different* sensor, not assumed.
- **Thermal/probe controller**: onboard always-on MCU reads supply, backup battery/BMS, camera/NIR LED, SoC/heatsink/window/enclosure, ambient temperature/humidity, opening/tamper, link and log integrity. External calibrated meter / PC is connected only for experiments.
- **Network and updates**: Ethernet+PoE for fixed deployments if supported by power budget, optional Wi-Fi/5G for fallback or event configurations; secure signed update with rollback, policy changes atomic, authenticated telemetry and service. Continuous network accessibility in sleep carries a measured energy cost.

## Known installation geometry, variable capture environment

Device orientation is fixed between installation and removal; characterize:
- local site geometry: mounting height, tilt/yaw, protective shroud, capture range/optical field, density, entrance/exit directions, occlusions and glare surfaces;
- **people are moving**, so capture delay, camera shutter/exposure, walking speed, motion blur and multi-person tracking still matter;
- light/day-night/strong sun and backlight, rapid indoor/outdoor contrast, NIR washout, reflections, optical windows/drops;
- if outside: rain, humidity, water intrusion, condensation, cold start, hot sun and solar heating, ice/frost risk; if inside: lighting changes, reflections and potentially HVAC gradients;
- temperature rise from SoC/NPU under sustained bursts, battery backup restrictions and failure modes, power cut, network cut, vandalism/tamper;
- repeatable site setup and calibration, post-event removal/redeployment and change-of-view regression tests.

Not a roaming/wearable vision device: **do not** optimize grip, user-body heat, harness ergonomics, walking-induced device shake, moving power cable, center-of-gravity while worn, or simultaneous hand navigation. Fixed mounting still requires vibration/structural disturbance tests appropriate to the installation.

## Architecture and experiment boundary

```text
EVENT WALKWAY/PASSAGE  -->  [ WALL- OR FIXED-SUPPORT-MOUNTED PRODUCT ]
                              RGB EO + NIR + PIR/wake + synchronized capture
                              local inference model + index + 1:N matching
                              local allow/watchlist policy + safe human-reviewed alert
                              local encrypted templates/storage + signed OTA
                              always-on MCU + power/thermal/environment probes
                              PoE/DC/main supply + protected backup/switchover
                              sealed enclosure/bracket/cables + tamper protection
                                   |
                                   +--- optional Ethernet / Wi-Fi / 5G link
                                   +--- optional controlled test port / instrument
                                               |
                                   [EXTERNAL BENCH, not required in service]
                                    calibrated power and thermal instruments
                                    PC, experimental supervisor, logs/dashboard
                                    repeatable lab + controlled field trials
```

The **design/fabrication toolchain** (Flux.ai, KiCad, FreeCAD, SPICE, BOM) is separate from both runtime and measurement bench.

## Phase 0 expected outputs for Flux

1. Correct title and product concept to **Fixed, Temporary Event-Entrance EO/NIR Edge Unit**; remove mobile/handheld/harness preference and physical portability as a runtime activity.
2. Produce installation diagrams (front/elevation/side/optic zone) showing illustrative wall/bracket/truss mount, field of view, height, walking flow, cable route, tamper and safe camera/illumination geometry. Label actual dimensions TBD pending site survey and camera selection.
3. Core AI and sensing block diagrams: RGB/NIR + PIR wake + CPU/NPU + encrypted 1:N galleries / allow-watchlist policy + local alert with no PC.
4. Separation of **Product BOM** and **External Bench BOM**; verify PoE/regulated DC normal operation versus backup battery sizing and hot-swap continuity proof.
5. Case analysis for indoor and outdoor temporary events, sun/backlight/day/night/rain/fog/cold/hot and pedestrians moving through a fixed camera view. Include captured person FTA/FTC and 1:N FPIR/FNIR, energy per event, sustained latency and false alarm/operator workload.
6. Installation and commissioning procedure (site survey, FOV and face pixel density, illumination/eye safety, test captures, alignment calibration, signed model/gallery policy check, clock/time sync, network-off health check, acceptance and re-validation after relocation).
7. Trade-off decision: compare PoE/DC with backup, mains-only + UPS, and battery-only if explicitly needed; justify rather than assume full two-pack hot-swap is always optimal.
8. Prototype sequencing: fixed-sensor bench kit + optomechanical wall-mount mockup, compute module integration, instrumentation board, enclosure + thermal tests, environmental qualification, limited consented pilot; no PCB routing before whole-device review.
9. Preserves STOP / PIVOT / PERSEVERE philosophy and separate biometric research gates. Synthetic data and consented subjects only, no public-space unconsented identification or real watchlist disclosure to cloud tools.

## Corrections to prior documents

Earlier references to **"mobile, walking with device, handheld, worn, harness, movement of device" are superseded** and should not be used by Flux as design goals. Controlled temporary tripod support is not a separate product variant. Environmental qualification remains necessary, but risk comes from changing conditions around a static mounted device and moving people, **not from someone carrying the device**.
