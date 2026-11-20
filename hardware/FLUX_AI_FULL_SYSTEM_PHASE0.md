# FLUX.AI — Full-system correction to the Phase 0 scope (v0.2, 2026-11-20)

**This document overrides the narrowly scoped PCB-first framing in the initial Flux.ai brief. The earlier brief remains useful as a future subsystem prompt, not as the whole project.**

## Exact message to paste into the existing Flux.ai project

> **Correction: restore the full project scope before doing any PCB work.** I need you to design the **entire autonomous, mobile Siamese Embedded EO/NIR Vision + 1:N Research Device**, not just a measurement/supervisor PCB. Its internal MCU and probes are components of the field device. A **separate external PC and calibrated measurement bench** gather and analyze data during laboratory/field trials and never operate the device during its normal mission. Distinguish the three system boundaries: (1) complete mobile product, (2) external experiment/metrology/analysis bench, (3) engineering/fabrication toolchain.
>
> Read this mandatory full specification first: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/design/edge-device-metrology-20261120/hardware/FULL_FIELD_DEVICE_SYSTEM_REQUIREMENTS.md . Read the previously supplied `EDGE_SYSTEM_ARCHITECTURE_V0.md`, `PROBE_INTERFACE_AND_TELEMETRY_SPEC.md`, `DEVICE_CONTRACT_V0.yaml` and `BOM_PROVISIONAL.csv`. If links are inaccessible, ask for an upload and list exactly which files you could not read; do not pretend you saw them.
>
> **Field mission:** walking with or carrying the device, or installing it temporarily, while it autonomously detects passage/motion; captures synchronized RGB-visible + NIR scenes day and night; runs a locally stored model and 1:N matcher against encrypted galleries with independent authorization/watchlist policies; wakes/sleeps based on presence; survives realistic rain, cold, heat, sun, glare, changing light, humidity/condensation, shake and vibration. Network optional, fully offline local matching mandatory. Dual approved swappable protected batteries with validated no-interruption power path are a requirement to design/verify, not a proven circuit. Never claim weatherproofing, liveness/PAD or biometric accuracy without testing.
>
> **The external PC** runs the experiment supervisor: deterministic trial schedules, synchronizes external power/thermal/environment instruments, collects device trace/span and probe data, analyses datasets and uncertainties, and renders dashboards; the device remains autonomous when PC is unplugged. Create **two distinct BOMs: PRODUCT and TEST BENCH**. Define their physical interfaces, what is logged locally vs externally, and how no data is lost on unplug or network outage.
>
> In **Phase 0 now** produce deliverables: A) complete product system block diagram; B) mobile usage/optical/environment conditions test matrix including bright sun/backlight, low-light/NIR night, rain/drops/fog, cold/battery, heat/solar load, motion, vibrations, condensation, lightning changes and failure modes; C) validated vs provisional vs ungrounded requirement matrix; D) proposed computing/AI modules with real datasheets and measured-run compatibility test plans; E) camera configuration and optical/protection options; F) power, thermal, enclosure, hot-swap, ingress and mechanical assembly concept; G) PRODUCT and BENCH BOMs separately with supplier evidence and costs labeled quoted/unknown; H) on-device vs bench software and data/telemetry architecture; I) 3D concept and mechanical interface constraints using real component outlines only; J) an incremental manufacturing and test strategy, STOP/PIVOT/PERSEVERE gates and first risks.
>
> **Only AFTER whole-system design review** choose the initial small supervisor PCB (likely low-voltage MCU + sensor acquisition) as an implementation increment. Never reduce the entire product to this PCB. Create persistent actual Flux project artifacts rather than only replying in prose. You must not fabricate or order a PCB, assert safety/certifications, or start unreviewed lithium power-path design.
>
> On real subjects, restrict prototyping to informed-consent studies and approved use; begin with synthetic/replay engineering data. Never claim a watchlist match is confirmed identity; unknown != denylisted. Never upload personal face templates or actual watchlists to Flux.ai.

## Direct project document

https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/design/edge-device-metrology-20261120/hardware/FULL_FIELD_DEVICE_SYSTEM_REQUIREMENTS.md

### Expected response from Flux

Not a prompt to choose 'prepare phase 0 or review blockers'. Produce actual project artifacts first and a list of independent review decisions afterwards. Flag limitations of Flux.ai for optomechanical and environmental simulation rather than inventing detailed results. Prefer real board outlines, and export native editable CAD/ECAD where possible.
