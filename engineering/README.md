# Siamese Embedded — reproducible engineering reference stack

**2026-11-20 · IMPLEMENTATION STARTER, NOT A RELEASED MANUFACTURING DESIGN**

Purpose: source-controlled engineering to progress from a **fixed wall-mounted** EO/RGB+NIR event node through electronic and 3D prototypes, deterministic PC bench simulation, independent evidence, and gated manufacturing. This is NOT a wearable device and the external analysis PC is NEVER a runtime dependency.

## Flux.ai this weekend — correction: NOT FPGA

The intended tool is **Flux.ai electronic/PCB design, not FPGA hardware**. Use [P1 minimal purchase guide](bom/P1_MINIMAL_PURCHASE_GUIDE.md), [SKU-level candidate list](bom/P1_PROCUREMENT_CANDIDATES_2026-11-20.csv), [Flux.ai low-voltage carrier design brief](electronics/FLUX_AI_P1_BOARD_BRIEF.md) and [laboratory materials/environment questions](docs/LAB_MATERIALS_AND_PROTOTYPE_QUESTIONS.md). Build P1 from COTS and measure before designing a custom PCB. No qualified PCB schematic or manufacturing release exists.

## NEW executable 512D/128D image-pixel demonstrator

`engineering/sim/pixel_replay.py` now generates abstract synthetic visible-like and NIR-like image files and performs genuine deterministic image-pixel DCT512 feature extraction, cosine exact search and matched random128 comparison, with a local HTML/CSV/JSON report. **This is not a face AI algorithm nor real NIR sensor acquisition.** Existing `digital_twin.py` independently demonstrates fake watchlist/allowlist decision states, telemetry and PC operator console. The complete integration, ONNX/RKNN true model, licensed RGB/NIR acquisition, independent metrology and actual PCB fabrication are *not* complete.

```bash
python -m pip install -r engineering/requirements.txt
python engineering/sim/pixel_replay.py --out /tmp/siamese-pixel-demo
python -m unittest discover -s engineering/sim/tests -v
```

See [pixel replay](sim/PIXEL_REPLAY_AND_MODEL_ADAPTERS.md), [full image-pair plan](sim/IMAGE_PAIR_REPLAY_PLAN.md) and the technical dossier in `docs/`.

## Complete integrated dossier and verification plan

**[INTEGRATED DEMONSTRATOR & FABRICATION DOSSIER V1](docs/INTEGRATED_DEMONSTRATOR_AND_FABRICATION_DOSSIER_V1.md)** consolidates the four-system architecture, three mechanical variants, P1 COTS BOM, PCB/MCU specifications, 512D/128D pixel demo, true EO/NIR model adapter gates, PC supervisor, security/research evidence, staged manufacturing and lab questions. **[26 requirements / tests / proposed success thresholds](docs/SYSTEM_REQUIREMENTS_TEST_EVIDENCE_V1.csv)** distinguish existing synthetic code from missing physical evidence.

`engineering/mechanical/concept_variants.scad` provides **Hull / Book / Cassette** P0 rounded design variants; the physical/optical build remains unverified. No face image data or real model checkpoints are included.

**Flux.ai trial is over; the tooling baseline is OpenSCAD/FreeCAD/Build123d (MCAD), KiCad/ngspice (ECAD), C/Python and GitHub Actions.** The old Flux briefs are retained as historical architecture records, *not active paid-tool dependencies*.

## Work packages / source layout

| Folder | Deliverable | Current maturity |
| --- | --- | --- |
| mechanical/ | Parametric enclosure and wall bracket; STEP/STL exporters, preliminary materials | P0 concept, unverified component fit |
| electronics/kicad/ | Native KiCad project / board-outline starter for low-voltage probe carrier | Schematic/connector/PCB design INCOMPLETE; **HOLD FAB** |
| firmware/ | Portable C MCU state machine + host test harness | Testable behavior simulation; hardware drivers unimplemented |
| device/ | Non-biometric synthetic exact search benchmark and pipeline boundaries | Research engineering; NO real biometric model or live list |
| sim/ | Deterministic PC experiment controller: power state, thermal and RF link | Simulated only; not measured, not model validation |
| telemetry/ | Versioned event and reading schema / policy | Initial engineering contract |
| bom/ | Part register and validation for product, security receiver and external bench | MPNs TBD, NOT approved to purchase |
| docs/ | Build instructions, architecture, test-to-requirement trace and sign-off | Draft |
| .github/workflows/edge-appliance.yml | Scoped automated checks and OpenSCAD artifact export | Source-level tests only; NOT a manufacturing release |

## Priority gates — fail closed

- **G0 Need and lawful scope**: entrepreneurship O0–O6, no deployment of generalized public-space facial blacklists; client/venue/privacy permissions before participant studies.
- **G1 Product design**: selected actual SoM, camera/optical stack, RF module, PoE/DC and backup electrical architecture, interface voltage levels, manufacturing dimensional input; review true end-to-end cost of power and 1:N memory.
- **G2 Functional COTS rig**: RGB/NIR, wake and telemetry, local model runtime only after compatibility confirmed; independent meter for W/Wh/J, target 100k/500k/1m synthetic retrieval.
- **G3 Approved electronics and mechanics**: KiCad ERC/DRC + electrical peer review, reviewed battery power path and RF/NIR safety, enclosure clearance and thermal simulations/measurements.
- **G4 Controlled field environmental trial**: rain/cold/heat/sun/condensation and safe fixation; no IP rating without assembly test; no live biometrics without independent legal gate.
- **G5 Manufacturing release**: qualified BOM with MPNs/suppliers, full schematics and routed PCB, DFM/DFA/DFT, assembly & calibration instructions, EMC/RED/optical/electrical and ingress evidence, versioned sign-offs.

**Never interpret a generated STL, STEP, outline PCB, passing CI, simulated temperature or passing unit test as evidence of fit, electrical safety, performance, legal permission or manufacturing suitability.** Fabrication outputs are explicitly blocked until G3/G5 manual approval.

## Canonical product constraints

- Fixed event mounting; reference workload 1,000 passerby encounters/h × 10h/day × 5 days (simulation target only).
- Local offline model / 1:N matcher (research only), encrypted gallery and allow/watch policy; unknown is not denylisted.
- RGB+NIR with low-power wake, onboard supervisory MCU + calibrated/readable probes, distinct low-power encrypted RF short-message path to event organizer security dispatch.
- PoE or regulated DC primary; protected backup and possible battery hot-swap after independent electrical design; lab PC purely for metrology/replay.
- 100×150×30 mm head is an ASPIRATIONAL volume constraint, not demonstrated. Compare separate backup dock and total installed volume.
- Model/compression accuracy and physical performance are independent: preserve the Study 1B sealed screen/test and negative Study 0 history; no protected scientific data in this stack.

Start: python -m unittest discover engineering/sim/tests -v ; gcc -std=c11 -Wall -Wextra -Werror -pedantic engineering/firmware/mcu_supervisor.c engineering/firmware/test_mcu.c -o /tmp/edge_mcu_test && /tmp/edge_mcu_test ; openscad -D 'part="body"' -o /tmp/edge_body.stl engineering/mechanical/enclosure.scad .

See ARCHITECTURE.md, RELEASE_GATES.md and each package README.