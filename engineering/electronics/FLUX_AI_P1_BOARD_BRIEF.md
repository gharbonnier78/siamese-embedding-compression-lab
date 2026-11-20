# Flux.ai — P1 electronics design instructions: NO FPGA

**2026-11-20 · status: technical brief, no released schematic, no routed PCB, no fabrication approval.** This explicitly corrects the preceding misunderstanding: **Flux.ai is the cloud electronic-design tool, NOT a Field Programmable Gate Array**. No FPGA is currently planned.

## Objective

Develop a small, manufacturable **LOW-VOLTAGE supervisor/probe interface PCB**, not a custom AI computer or a dangerous/unreviewed PoE/Li-ion charger, for a temporary fixed-site EO/RGB + NIR research unit. Start from ready-made Radxa ROCK 5B, Arducam B0385 and B0332 USB modules, Pico 2 and INA228/SHT45 breakouts. The board integrates/provides connectors for low-power MCU, shunt readout, ambient/thermal probes, PIR, tamper, RTC/FRAM, NIR safety interlock *command* and optional EU868 alert radio development module. **Pinouts, rail budgets and electric schematic must be derived from actual vendor datasheets/revisions and independently checked.**

## Must-have source-control/fabrication deliverables from Flux

1. **Design review packet:** block diagram, formal pin map and voltage table, named rails and worst-case power budget, sleep and active states, out-of-range interlock behavior and boot/reset interactions.
2. **Source project:** full editable native Flux electronics project plus time-stamped, version-locked README, symbol/footprint/STEP references, *non-secret* component/vendor data and a reviewed compatibility record. Do not claim complete native KiCad reverse-export unless an actual compatibility-tested path is demonstrated.
3. **Schematic:** selected MPNs, protection against miswiring and power sequencing and correctly dimensioned shunts; no unqualified rechargeable battery packs, laser/eye-safety emitters or hand-built mains/PoE circuits.
4. **PCB review:** validate board outline and connector position against CAD head. Run DRC, layout checking, EMC/ESD/return-current and antenna-clearance reviews; record issues, decisions and sign-off.
5. **Releasable outputs LATER:** verified Gerber/drill, pick-and-place, eBOM, PCB STEP, assembly notes, DFT/test point list and testing firmware; **do not output or place fabrication order until approved G3/G5.** Flux supports manufacturing exports in its docs; exports do not certify the board.

## Phase separation

- **P1A**: COTS breadboard / manufacturer accessory interfaces, no custom PCB at all. Test RGB, simulation PC, SoM energy meter, MCU sensor measurements.
- **P1B**: add second UVC camera to compare RGB/NIR, sleep PIR and optional LoRaWAN dev board; characterize actual UVC timestamp alignment/hardware trigger. Do not assume either camera sync pin or safe NIR illumination works merely because the sensor is global shutter.
- **P2**: compact sensor carrier with reviewed MCU input protection, zero custom high-speed USB/CSI or PoE distribution, unless clearly needed and electrically reviewed.
- **P3**: optomechanical integration with sealed-serviceable head, no vent-to-electronics, thermal conduction to enclosure, vibration/humidity tests.
- **P4**: professional manufacturing release only with MPN qualified BOM, 3D STEP fit, ERC/DRC, signal integrity where relevant, factory programming, EOL tests and sign-offs.

## Simulation/demo and production boundaries

The existing \`engineering/sim/digital_twin.py\` uses fake vectors/conditions, localhost-only console and synthetic watch/allow cases for behavior testing. No real biometrics or confidential watchlist is included. The field node must remain autonomous and keep exactly **one active model/projection/gallery**; the external PC does optional secure offline replay of approved RGB/NIR recordings with different 512D/128D model variants. External security operator alert receiver is separate from this lab PC. No biometric personal data in Flux or this public repository.

## Questions to ask Flux this weekend

- Can Flux maintain the full native electronics project, engineering change log, exact manufacturer part numbers, variants, tolerances and component 3D bodies with exports into GitHub?
- How does Flux handle handoff of schematic/PCB manufacturing files, editable STEP mechanical assembly and checks for correct footprint-to-MPN matching?
- Can it produce an ERC/DRC review log and test-point table and identify the weakest assumptions in PoE vs backup/RTC/always-on MCU?
- Which functions would a separate small carrier PCB **actually** improve over already available breakouts? Is the smaller board justified by measured fit/cost and repeatability?
- Can we model the real heat source, seal geometries and camera lens depth from exact STEP inputs, not invented masses?
- Can the selected UVC cameras share a demonstrated hardware sync source, or do we need an alternative paired industrial camera family?
- What specific validation evidence would a professional PCBA house demand before quoting a quantity of 5–10 assembled units?

Primary Flux docs: https://docs.flux.ai/reference/data-portability ; https://docs.flux.ai/reference/manufacturing .
