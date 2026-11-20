# FLUX.AI — Start Here: Siamese Edge EO/NIR Device (v0.1)

**Use this file as the project brief and initial prompt for Flux.ai Copilot.**  
Date: 2026-11-20 · Source: draft PR #52 · **Exploratory engineering only; not an approved or build-ready PCB.**

GitHub source of truth: https://github.com/gharbonnier78/siamese-embedding-compression-lab/pull/52

## 1. FIRST MESSAGE TO PASTE INTO FLUX COPILOT

> You are assisting with the electrical architecture and *first-stage low-voltage carrier / measurement PCB* for a modular, privacy-preserving embedded vision and local biometric research device. Use this specification as an engineering input, not as permission to fabricate. **Before drawing any schematic or selecting a part, create a requirements-to-circuit traceability table, a system block diagram, an interface/power-domain matrix, and a list of unresolved specifications.** Distinguish explicitly among (A) validated requirements, (B) provisional concept choices, and (C) missing vendor evidence.
>
> The prototype must support an interchangeable Linux edge AI compute module (RK3588-class candidate, exact board/SoM TBD); RGB EO camera and near-infrared camera with trigger synchronization; low-power passage/motion trigger (PIR, with optional mmWave); an always-on low-power supervisory MCU; sensors to read device/input-rail power, both protected battery packs, PoE/DC status, SoC/heatsink/enclosure/ambient/NIR-emitter temperature, humidity, opening/tamper and communication health; and independent test points for an external calibrated power analyzer.
>
> Provide suitable mechanical/electrical connection options for wired Ethernet + PoE (power and data), optional Wi-Fi/5G modules, and an authenticated, low-energy maintenance/update interface. Distinguish PoE (power over Ethernet), PPPoE (a network protocol), and optional Single Pair Ethernet/PoDL. Do not assume that a physically smaller Ethernet connector is itself a separate protocol.
>
> The computer must independently host a versioned, locally executable vision model, a matching engine (verification 1:1, retrieval 1:N) and encrypted local galleries with separate allowlist/watchlist/denylist *policy* records. The hardware needs sufficient selectable RAM, nonvolatile storage, accelerator support and thermal headroom. **Do not design an on-PCB neural network or biometric algorithm**: define interfaces/resources to a qualified compute board instead. Any real biometric testing is separate and must be authorized; synthetic gallery/search replay first.
>
> Two independent protected commercial smart-battery packs with uninterrupted replacement are a *full-device requirement*, **not a validated circuit**. For this first step propose a verified power-path architecture, power budget and transient simulations (including removal at peak load), but **do not route or approve a lithium charging/hot-swap PCB before specialist safety review**. Start with approved bench DC power or a suitable vendor power module. Keep the MCU/RTC/probe log domain operating when the AI SoC and cameras are off, and define the cost of any always-available remote network interface.
>
> Deliver *Phase 0 only first*: (1) a functional block diagram; (2) component and interface shortlist with real manufacturers/MPNs, URLs to datasheets, availability and explicit "not yet selected" entries; (3) power-domain diagram and power-state truth table for OFF/SLEEP/IDLE/DETECT/VERIFY/IDENTIFY/BURST/UPDATE/BATTERY_SWAP; (4) probe and telemetry readout table identifying who reads each sensor, bus, sample frequency, timestamps, wake sources and retention; (5) BOM with reference designators, alternatives, estimated prices *only when quoted*, and unresolved items; (6) top electrical/thermal/security risks; (7) suggested manageable **Phase 1 first PCB** consisting solely of always-on MCU, probes, test points, power monitoring and headers to an external AI board; and (8) STOP/PIVOT/PERSEVERE review gates.
>
> Once Phase 0 is reviewed and approved, generate an **editable native schematic**, review electrical ratings and netlist, simulate necessary rail/trigger/power events, run ERC/DRC, define connector/footprint orientation and mechanically fit the PCB against actual physical board/camera drawings. Preserve all assumptions as explicit "TBD"; never fabricate part numbers, datasheet ratings, or simulation measurements. Do not claim the schematic, layout, batteries, thermal performance or complete device is production-ready based only on AI output. **Do not place fabrication orders.**

## 2. SYSTEM BOUNDARY AND ORIGINAL INTENT

**Research question:** Does an embedded EO/NIR 1:N device create value compared with simpler alternatives, including standalone passage detection, on-device 1:1, or camera + centralized server, after accounting for biometric errors, power consumption, thermal headroom, autonomy, lifecycle and maintenance?

Historical exploratory workloads — not achieved performance: 100,000 / 500,000 / 1,000,000 gallery entries; peak 1,000 encounters/h; 10h/day across 5 days. Original hypothesized power cases: 8/12/18 W, **not measured**. Proposed 20 Wh demonstration pack is not a five-day energy solution.

Keep the following subassemblies separate:

1. **Scene sensing:** RGB visible (EO); NIR camera with safe NIR illumination and hardware capture timing; low-power wake via PIR/mmWave; optional additional thermal LWIR only if a *new separate* need is validated (an LWIR scene camera is not a device temperature probe).
2. **Edge SoM/SBC:** replaceable Linux computing board with verified model runtime, RAM and encrypted eMMC/NVMe; external cameras and optional NPU acceleration; no assumption that quoted TOPS equals real inference throughput.
3. **Secure local model/gallery subsystem:** 512D vs 128D raw/PCA/random/Siamese research paths only under independent scientific gates; local approximate/exact 1:N index, versioned model, indexed gallery, allowlist/watchlist/denylist metadata separately maintained and authorized. Unknown/no match does **not** mean denylisted.
4. **Always-on supervisory domain:** low-power MCU + watchdog + RTC + nonvolatile buffer; power-input monitors; two battery smart-BMS status lines; thermistors/thermocouples/ambient probe; tamper; GPIO wake and safe shutdown. Readouts must work with AI SoC asleep.
5. **Power and interfaces:** approved DC bench input first; PoE(+) PD and safe regulated conversion for fixed device after power budget; separate protected battery A/B and power ORing/hold-up after electrical review; Ethernet data, Wi-Fi, optional 5G, service/debug; signed OTA and rollback are functional requirements.
6. **External metrology:** calibrated external DC analyzer and temperature logger (do not make claims solely from firmware sensors), hardware time alignment to workload trace/span identifiers.

## 3. MINIMUM PHASE 1 PCB — IN SCOPE

A low-voltage telemetry + sensor-interface carrier, NOT a custom high-speed CPU/NPU board or lithium charger.

- Supervisor low-power MCU, watchdog, RTC and durable event buffer.
- Digital supply shunt monitors and voltage ADC at safe, labelled power rails; explicit voltage/current range and calibration plan.
- Four or more planned thermal measurement locations, humidity/temp ambient, optional enclosure tamper + PIR IRQ; documented I2C address/pullup, GPIO voltage levels and sensor regulator domains.
- Board-to-board header to SoM for wake/power_good/IRQ/UART or USB telemetry; **exact electrical levels and pinouts TBD until SoM selected**.
- Reserved interfaces for RGB + NIR trigger sync and NIR emitter interlocks; CSI-2 itself stays on vendor-approved host/camera connections, not improvised on a hobby 2-layer carrier.
- Removable calibrated shunt/test points and external meter/logger synchronization.
- Ethernet/PoE subsystem as a defined external module or clearly separate later PCB phase; plan power, pin, shielding, connector, emissions and safety properly.

## 4. READOUT / POWER STATE REQUIREMENTS

Every probe must have **an owner/readout**, wiring/bus, sleep-domain power, firmware driver, sample rate, time base, calibration, traceable test point and retained data format. Log MCU wake reason, PoE/battery input switching and camera/NIR sync. Separate:
- External calibrated **measurement** vs onboard health **telemetry**.
- Nominal Wh capacity vs effective autonomy under actual temperature, aging, duty cycle and DC conversion losses.
- Uninterrupted battery swap vs nominal "2 packs": actual inrush, cutoffs and supply droop must be simulated and measured.
- Deep sleep with local buffering vs always-reachable remote access; latter consumes power.
- RGB/NIR scene imaging vs thermal probes on the device.

Initial measurement modes: OFF, SLEEP, IDLE WATCH, DETECT ONLY, VERIFY 1:1, IDENTIFY 1:N, BURST, TRANSMIT, OTA, THERMAL SOAK, BATTERY SWAP, FAULT RECOVERY. Required metrics: W, Wh/day, J/event, J/query, peak current, measured p50/p95/p99, throttle count, surface and battery temperatures, data backlog/loss and battery life.

## 5. MANDATORY ENGINEERING RELEASE CONDITIONS

**Phase 0:** only requirements, functional decomposition, architecture tradeoffs, data sheet/part shortlist, block/power diagrams and BOM draft. User approval needed to proceed.

**Phase 1:** select actual MCU and sensors; produce native editable schematic and verified pin/bus/power mappings; qualify safe bench regulated supply; electrical and thermal design review, supported circuit models and ERC.

**Phase 2:** layout/routing/DRC + PCB STEP + 3D mechanical fit + supplier-qualified BOM, manufacturer assembly constraints and test plan. Never treat ERC/DRC alone as validation.

**Phase 3:** only after human sign-off, request manufacturing files (Gerbers, drills, placement, BOM); fabrication itself, component purchase and battery safety approval are separate actions.

**Phase 4:** externally instrumented deterministic trials; log uncertainties; STOP, PIVOT or PERSEVERE. No biometric operational claims from PCB tests.

Absolutely no uploading of real face templates, watchlists, secret credentials or identifiable imagery to this external AI design project.

## 6. AUTHORITATIVE RELATED FILES IN GITHUB

Read, or attach as files in Flux, before committing any design selection:

- Full edge architecture: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/design/edge-device-metrology-20261120/hardware/EDGE_SYSTEM_ARCHITECTURE_V0.md
- Machine-readable device constraints: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/design/edge-device-metrology-20261120/hardware/DEVICE_CONTRACT_V0.yaml
- Probe wiring, Ethernet/PoE and telemetry: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/design/edge-device-metrology-20261120/hardware/PROBE_INTERFACE_AND_TELEMETRY_SPEC.md
- Per-probe acquisition matrix: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/design/edge-device-metrology-20261120/hardware/PROBE_INTERFACE_MATRIX.csv
- Provisional BOM (36 equipment lines): https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/design/edge-device-metrology-20261120/hardware/BOM_PROVISIONAL.csv
- Experiment and value-falsification protocol: https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/design/edge-device-metrology-20261120/hardware/METROLOGY_AND_DECISION_PROTOCOL.md
- Conceptual OpenSCAD (NOT print-ready): https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/design/edge-device-metrology-20261120/hardware/cad/edge_enclosure_concept_v0.scad

For Flux.ai guidance on attaching or importing project files see https://docs.flux.ai/reference/reference-import-designs and https://docs.flux.ai/reference/copilot . If a GitHub link cannot be fetched directly by Flux, paste the text in the project chat, upload the downloaded .md and companion .yaml/.csv files, or upload an appropriate repository subset; **do not assume that a link automatically imports project context.**

## 7. FIRST DECISION AFTER FLUX PHASE 0

Before authorizing Phase 1, require:

- Chosen SoM/board & runtime support verified for actual on-device model, CSI/USB cameras and flash/RAM.
- All chosen MCU, sensor, shunt, PoE, power-path and connector parts sourced to real datasheets; no hallucinated availability or price.
- Confirmed power-domain truth table, sensor acquisition while sleeping and expected rail budgets.
- A small and auditable first PCB scope; dual-battery hot-swap electronics not released without power safety engineering review.
- Mechanical envelope verified by manufacturer drawings rather than guessed from a rendered 3D image.
