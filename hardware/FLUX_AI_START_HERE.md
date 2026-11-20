# FLUX.AI — Siamese Embedded FULL MOBILE DEVICE, Phase 0 (v0.2)

**CANONICAL STARTING POINT — supersedes v0.1's premature sensor-PCB framing.**  
Status: conceptual engineering; no PCB fabrication, no battery safety approval, no environmental performance claims, no biometric deployment authorization.

## What we are actually designing

**A complete portable autonomous EO/RGB + NIR vision and local Siamese/other embedding 1:N experimental system**, with wake-on-passage/motion, embedded AI computer, encrypted local gallery, locally executable 1:N matcher and versioned allow/watch/deny policies, power-management/battery hot-swap design, environmental enclosure and onboard low-power measurement/supervision. The device operates **without an attached PC, cloud or network**.

The **external calibrated instrumentation and independent PC** are a separate experimental bench. The **PCB measuring/supervision board** is just a possible subassembly of the autonomous device, not the final product.

The complete system must be evaluated when carried or moving, in rain/cold/high heat, bright sun/backlight, changing illumination and at night, with vibration, fog/condensation and camera motion blur. All performances are TBD until measured.

## First: paste this into Flux.ai Agent

> **Correct the scope of our existing project: Phase 0 must design the WHOLE MOBILE SIAMESE EMBEDDED DEVICE, not just the supervisory/measurement PCB.** We have three distinct blocks: (1) the complete standalone field device that runs RGB/NIR sensing, wake-on-motion, local model inference, local 1:N search and encrypted allow/watchlist policies, weather-resistant mechanical housing, dual protected hot-swappable packs and on-device MCU/probes; (2) a separately instrumented external TEST BENCH with a PC, calibrated electrical/thermal/lighting measurement and dashboards, which is never needed for normal device operation; (3) engineering/fabrication tools Flux/KiCad/FreeCAD/SPICE/BOM, which are not parts of the device.
>
> Read the new canonical specification FIRST: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/design/edge-device-metrology-20261120/hardware/FULL_FIELD_DEVICE_SYSTEM_REQUIREMENTS.md . Also use `BOM_PRODUCT_FIELD_DEVICE_V0.csv`, `BOM_EXTERNAL_TEST_BENCH_V0.csv`, `EDGE_SYSTEM_ARCHITECTURE_V0.md` and `PROBE_INTERFACE_AND_TELEMETRY_SPEC.md` from the same folder. If you cannot read any link, identify the missing files and request their text/upload; never assume access.
>
> **Produce REAL Phase 0 engineering artifacts in Flux**: whole-device system architecture, EO/NIR camera/optics/wake options, computing and local matching/storage alternatives, environmental operating and qualification matrix (sun/night/rain/cold/heat/humidity/fast motion), power and hot-swap domains, sealed mechanical concept and thermal risks, distinct product vs bench BOMs, internal vs external probe/readout plan, software boundaries and component-level datasheet evidence, plus a sequenced manufacturing/test plan with uncertainties and STOP/PIVOT/PERSEVERE criteria. No unverified performance claims. Only after full-system review propose a small MCU/probe PCB as the first manufacturing increment.
>
> Do not draw a definitive battery/charging PCB or start PCB routing yet. No live watchlists, real biometric templates or sensitive images in Flux. Use synthetic data and consented controlled trials only.

## Mandatory canonical links

- [Complete mobile product scope and environmental scenarios](FULL_FIELD_DEVICE_SYSTEM_REQUIREMENTS.md)
- [Flux correction prompt in full](FLUX_AI_FULL_SYSTEM_PHASE0.md)
- [Product-only BOM](BOM_PRODUCT_FIELD_DEVICE_V0.csv)
- [External test bench BOM (PC, power, temperature and weather instruments)](BOM_EXTERNAL_TEST_BENCH_V0.csv)
- [Detailed AI/1:N device architecture](EDGE_SYSTEM_ARCHITECTURE_V0.md)
- [Probe and telemetry interface requirements](PROBE_INTERFACE_AND_TELEMETRY_SPEC.md)
- [Physical probe readout matrix](PROBE_INTERFACE_MATRIX.csv)
- [Research and STOP/PIVOT/PERSEVERE measurement protocol](METROLOGY_AND_DECISION_PROTOCOL.md)
- [Provisional early enclosure sketch, not yet printable](cad/edge_enclosure_concept_v0.scad)

## Design output and next decision

**Phase 0 asks for all ten product-level artifacts.** Expected first review checks how optical, environment, AI and physical power constraints shape the device. Then choose a qualified compute module and real cameras. The low-voltage supervision board is a possible later deliverable, not the first architecture question.

Preserve scientifically separate study gates: Study 0 has a bounded negative result and Study 1B protected outcomes remain sealed. Do not claim performance, certified ingress protection or production watchlist validity.
