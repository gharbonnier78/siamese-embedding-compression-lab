# Flux.ai — CANONICAL START: FIXED EVENT INSTALLATION (2026-11-20)

**THIS VERSION SUPERSEDES THE MOBILE/HANDHELD/HARNESS ASSUMPTION FROM EARLIER PROMPTS.** The field unit is temporarily fixed to a wall, pole, truss or rigid event structure. A tripod is a temporary calibration/bench fixture, not the deployed mission. People move through the monitored zone; the camera does not move while operating.

## Paste into the EXISTING Flux.ai Agent project

> **Urgent Phase 0 scope correction: please update the project artifacts you already created.** The product is an **autonomous, fixed-mounted, temporary event-entrance EO/RGB + NIR 1:N edge vision system**, not a handheld, wearable or walking-mounted device. The camera is rigidly fixed during operation (wall plate, event structure, pole or equivalent). The scene geometry is assessed at installation: field of view, camera height/orientation, capture distances, visitor flow, sunlight/lighting, crowd density, optics, cable routing. **Only people are walking.** A tripod is permitted only for controlled tests and temporary optical calibration, not a core product variant.
>
> Initial event stress scenario: up to 1,000 persons/hour, 10 hours/day for five days; synthetic or consented trials, no deployment claims. Compare local galleries of 100k, 500k and 1M. RGB EO + synchronized NIR, PIR/mmWave passage detection, configurable low-power wake, local AI SoM with validated runtime, encrypted gallery/index, independent allowlist/watchlist/denylist policy, local 1:N and optional 1:1 matching, secure offline operation, signed model/firmware updates and protected telemetry. Unknown is not automatically a denylist match; live watchlist use requires separate legal and performance authorization.
>
> Prefer **PoE or regulated mains/DC during event operation**, with protected battery backup and planned failover/swap where justified and electrical safety reviewed. Do not assume battery alone powers the five-day mission or that a 20 Wh demonstration pack will suffice. A hot-swap without interruption is a candidate requirement to validate with a real power-path design, not an existing circuit. Record power input, battery SoC, power state, SoC/LED/case/ambient heat, humidity, tamper and optical conditions using an independent low-power supervisor MCU and probes.
>
> Define weather/optical operating regimes for indoor/outdoor events: bright sunlight/backlight, night/NIR, sudden light transitions, rain on the optical window, cold, high heat/solar load, humidity/condensation, and *moving pedestrians* (motion blur and overlapping targets), plus mechanical robustness of temporary fixed mounting. Do not optimize grip, walking stability, worn comfort, or harness movement.
>
> **Three distinct systems:** (1) the fully autonomous fixed device, which performs inference/matching without a connected PC, (2) an external measurement/analysis PC with calibrated power/thermal/light equipment used ONLY for experiments, and (3) Flux/KiCad/FreeCAD/SPICE design and fabrication tools. Keep PRODUCT BOM and EXTERNAL BENCH BOM separate.
>
> **Read new canonical GitHub file:** https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/design/edge-device-metrology-20261120/hardware/FIXED_EVENT_INSTALLATION_MISSION.md . Also read `EDGE_SYSTEM_ARCHITECTURE_V0.md`, `PROBE_INTERFACE_AND_TELEMETRY_SPEC.md`, `DEVICE_CONTRACT_V0.yaml`, `BOM_PRODUCT_FIELD_DEVICE_V0.csv` and `BOM_EXTERNAL_TEST_BENCH_V0.csv`. If unable to read any file, explicitly report it and ask for upload.
>
> **Produce corrected, persistent Phase 0 artifacts in Flux (not only a narrative):** system boundary and functional diagram; wall bracket/pole/truss mounting and optical field concept; indoor/outdoor installation and commissioning procedure; camera and SoM options with verified specifications and sources; power and battery backup strategy and budget; full sensor/telemetry readout architecture; two source-grounded BOMs; thermal/weather/security and biometric evidence/test matrix; design trade-offs; and stage-gated manufacturing plan. Rework the existing 'Concept physique' and any handheld/harness trade-off rather than selecting either. Keep unknown dimensions and ratings explicitly TBD.
>
> **Do not start PCB routing or order components.** The supervisor/meter PCB is one subassembly of the product and must only be designed after full-device architecture review. Use synthetic vectors and consented laboratory data; do not upload real watchlists, embeddings or personal images to Flux.

## NEW — low-power wireless alert to event security

**Add a separate, secure, low-energy short-alert radio channel from each fixed unit to the event organizer's authorized security receiver.** It must not depend on the external metrology PC or continuous high-power 5G. Evaluate private LoRaWAN with event-owned on-site gateway, secure P2P sub-GHz, and existing wired/Wi-Fi alternatives; choose only after RF field study and regulatory check. Define application event ID, type, timestamp, pseudonymous zone, network receipt ACK, operator acknowledgement, retries, queuing, false-alert mitigation and separate on-device vs dispatch BOMs. Never send images, face vectors, personal identities or real watchlists over this channel. Receiver/dispatcher is operational infrastructure, not the experimental PC. See [LOW_POWER_SECURITY_ALERT_RF_REQUIREMENTS.md](LOW_POWER_SECURITY_ALERT_RF_REQUIREMENTS.md) and [BOM_EVENT_SECURITY_ALERT_RECEIVER_V0.csv](BOM_EVENT_SECURITY_ALERT_RECEIVER_V0.csv).

## Outdoor upgrade without locking prototype fabrication

The concept art A/B has no demonstrated ingress or humidity performance. **Keep P0/P1 manufacturable** with COTS SoM, cameras, open-frame bench and printed fit mock. Design A-v2 with no through-vents into electronics, a gasket land, replaceable optical windows, a single properly routed service cable, conductive outer heat path, and an optional *separately wall-fixed* power backup dock. Defer conformal coating, final IP label, expensive molds and verified thermal/weather claims to P3/P4. Produce a staged P0–P4 mechanical, electrical, environmental and DFM plan and evidence gates before final PCB/casing release. Read [STAGED_ENVIRONMENTAL_PROTOTYPING_AND_DFM_V0.md](STAGED_ENVIRONMENTAL_PROTOTYPING_AND_DFM_V0.md).

## Source-of-truth hierarchy

1. **[FIXED_EVENT_INSTALLATION_MISSION.md](FIXED_EVENT_INSTALLATION_MISSION.md)** — latest authoritative mission and deployment.
2. [EDGE_SYSTEM_ARCHITECTURE_V0.md](EDGE_SYSTEM_ARCHITECTURE_V0.md) — local AI, cameras, gallery/matching and independent probe architecture.
3. [DEVICE_CONTRACT_V0.yaml](DEVICE_CONTRACT_V0.yaml) — machine-readable interface/mode constraints as corrected.
4. [BOM_PRODUCT_FIELD_DEVICE_V0.csv](BOM_PRODUCT_FIELD_DEVICE_V0.csv) — provisional field-unit BOM.
5. [BOM_EXTERNAL_TEST_BENCH_V0.csv](BOM_EXTERNAL_TEST_BENCH_V0.csv) — separate external measurement-PC BOM.

**Warning:** older "FULL_FIELD_DEVICE_SYSTEM_REQUIREMENTS.md" and "FLUX_AI_FULL_SYSTEM_PHASE0.md" described a carried device; this was an erroneous design interpretation. Do not use these historical portions as current requirements.

**Evidence gates:** A Phase 0 design does not validate weatherproofing, optical safety, battery protection, biometric accuracy or legal use. Record STOP/PIVOT/PERSEVERE decisions with qualified evidence and independent engineering review.
