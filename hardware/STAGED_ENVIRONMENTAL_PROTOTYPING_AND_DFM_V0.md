# Siamese Embedded — staged environmental design, prototype delivery and DFM strategy (v0.1)

**Date:** 2026-11-20  
**Engineering change:** evolve the 100×150×30 mm aspirational ultra-compact vertical concept so that external rain / humidity / condensation can be qualified later **without making the early prototype hard to manufacture or rework**. Applies to fixed temporary event installation, with a separate laboratory PC/metrology rig; **no rating or environmental survival has been demonstrated**.

## Design principle: "outdoor-upgradable, not waterproof on day one"

The current graphic of Concept A has apparent side vents: **these must not penetrate the sealed electronics cavity**. Use an external fin / ridge or conductive rear metal heat spreader with conduction from compute and NIR drivers; test heat against mounted wall clearance and solar soak. If sealed case cannot cool the real SoM, accept a larger/thicker chassis rather than claim a hypothetical heat path. Keep optical seals serviceable, protected cables and radio antenna outside RF-blocking metal (or on validated RF-transparent insert).

**Do now in CAD (cheap to incorporate even on P0/P1):**
- Structural base / removable front cover with a continuous gasket land, defined compression scheme and serviceable fasteners; keep closure design parametric and gasket dimensions TBD until selected.
- Two independent, dimensioned RGB and NIR optical windows with replaceable inserts, seal seats, adequate lens clearance and a replaceable sun visor.
- Internal electronics tray with standoffs, camera/sensor alignment, suitable service loops for CSI/USB flex cables, test points accessible when open, and an independent MCU/power domain.
- Rear heat spreader mechanically thermally connected to compute, but isolated from RF; wall attachment must not obstruct its transfer to ambient or create a tamper hazard.
- Weather protected cable inlet, drip loop and strain relief, with PoE/DC and optional backup dock. Spare space for vent membrane and environmental/humidity probe; pressure-equalizing membrane must be specified and validated, never assumed to eliminate condensation.
- Battery subsystem as a separate protected **wall-fixed dock** during early prototypes, preserving requirement evaluation for uninterrupted backup/hot-swap without fitting unsafe battery cells in thin head.
- Compare total head volume vs total installed volume including bracket, backup dock, electrical/optical overhangs, actual weight and expected site maintenance access.

**Defer until it provides evidence:** all-board conformal coating (it complicates probing/rework and may interfere with connectors/optics and thermal path), molded tooling, a custom high-speed NPU motherboard, custom Li-ion charging circuit, certified IP tests, and any declaration that the device is production-worthy.

## Staged releases and non-negotiable evidence

| Stage | Deliverable & most pragmatic build route | Physical tests / evidence | Gate and permissible claim |
|---|---|---|---|
| **P0 — Fit / risk study** | Parametric FreeCAD/STEP + quick additive prototype; use actual camera/SoM vendor dimensions once selected | component envelope, lens depth, connector clearance, light/IR windows, heat path risk map, bracket clearance | "form-factor proposal", no waterproof/thermal claim |
| **P1 — Open functional proof** | COTS SoM+camera+MCU/radio/PoE modules, safe regulated bench DC, open frame or 3D printed housing without gasket | local model and exact/ANN 1:N synthetic load, hardware trigger, probes vs external meter, W/J and thermal, actual low-power RF ACK to security receiver | repeatable function only; **never expose powered assembly to rain** |
| **P2 — Closed engineering enclosure** | Additive or CNC front/back, replaceable prototype gasket, optical windows, proper cable glands, heatsink; consider adapted commercially rated enclosure to reduce custom tooling | dry fit, water ingress visual test on unpowered housing, moisture/dry-out, thermal stable run in defined ambient, repeated assembly; validate any water tests on powered units only under reviewed electrical safety procedure | "sealed prototype under controlled tests"; no automatically inherited IP rating after drilling or alteration |
| **P3 — Environmental engineering validation** | CNC or production-like prototype and validated sealing stack; selectively coat suitable PCB regions only when rework stabilizes; optional ePTFE vent, qualified assembly and calibration procedures | rain/nozzle ingress per relevant method, wet-to-cold condensation, humidity cycles, solar heating + sustained NPU/NIR load, vibration of fixed mount, repeated open-close, backup power, cable issues | qualified **against documented test severity**, no IP label absent qualified complete assembly test |
| **P4 — Pre-series manufacturing design (DFM/DFA/DFT)** | released board fab and assembly pack, industrialized enclosure, toleranced drawings and inspection gauges; low-volume CNC/extrusion vs injection decisions by actual demand | supplier first-article inspection, 100% end-of-line electrical/optical/RF/safety checks as appropriate, lot repeatability, environmental sample test, maintenance procedures and full BOM cost | production claim only after independent compliance, EMC/RF/optical/electrical review and quality controls |

**Independent halt/pivot rules:**
- If the compute SoM cannot meet tested thermal limits in a sealed 30mm volume, increase thickness or move power into a dock; do not add unqualified air slots.
- If window condensation/drop contamination makes the relevant capture scenario fail, experiment with hydrophobic/AR coatings, shelter geometry, window heating with explicit energy accounting, or a protected installation location.
- If 1:N 512D→128D benefits vanish end-to-end or deployment legally/economically fails, preserve technical evidence but STOP the identity-based product claim.
- If off-the-shelf enclosure + inexpensive bracket delivers the required ingress at lower risk, adopt it even if less aesthetically minimal during pilot.

## How to make a manufacturer's job easy

**Use specialist suppliers for distinct work packages**; no need to find a single company that makes everything at P1.
1. **Mechanical shop / additive producer:** give STEP/native CAD, detailed drawings, dimensional tolerances, surface finish, optical window/gasket materials, wall mounting and number of units; request DFM and first-article measurement.
2. **PCB fab and assembly (PCBA):** supply native KiCad project, Gerbers, Excellon drills, BOM with actual manufacturer part numbers and alternates, pick-and-place, paste files, DRC/ERC log, assembly drawings and electrical test points; confirm actual chosen SoM carrier interfaces first.
3. **Electronics integration:** installation instructions, camera flex orientation, harness/cable drawing, seal torque and gasket compression, antitamper, secure firmware provisioning/OTA, metrology probe calibration and built-in-test acceptance.
4. **Environmental/RF test house:** actual full assembly with mounting, cables and power dock, specific test methods/severity/duration, radio regulation and optical hazard documentation; a declared housing IP is **not** inherited after redesign.
5. **Small-scale venue pilot:** signed permissions, fixed mounting and dismounting schedule, repair kit, replacement modules, recorded baseline power/incident workflow and explicitly legal/synthetic data use.

At P0/P1 **do not buy tooling or order custom PCBA**. Use vendor carrier boards and a cheap printed frame. Begin a small supervisor-board KiCad design only when pinouts and actual probe/voltage range are known.

## Original design aesthetic evolution

**A-v2:** graphite anodized-aluminum vertical flat appliance; flush RGB/NIR optical cassette, concealed PIR and NIR illuminator, single lower protected PoE/DC cable outlet, tamper screws, external rear cooling ribs without through-wall ventilation, replaceable front gasket, thin RF-transparent antenna insert. Photorealistic sketches must label target 100×150×30mm as *aspirational*, with no IP label, thermal performance or certified environmental temperature claim.

**B-v2 comparator:** horizontal camera-like form with visor and larger thermal volume, but similarly sealed housing, removable optics, independent bracket and external services; no assumed IP either. Compare **total installed volume, servicing time, materials cost, optical geometry and experimentally verified heat**, not visual appeal only.

## Technical references (design techniques, not endorsement of chosen parts)

- Hammond Manufacturing, catalogued gasketed die-cast aluminum IP66 enclosures as stock bases; modifying apertures/cable inlets requires reassessing resulting assembly: https://www.hammfg.com/files/downloads/catalog/epg/03-e7-aluminum_enclosures.pdf
- W. L. Gore, ePTFE protective vent pressure equalization and condensation limitation: https://www.gore.com/resources/faq-gorer-protective-vents
- Protolabs, stages of enclosure prototype (additive vs CNC vs molding): https://www.protolabs.com/resources/blog/selecting-a-manufacturing-method-for-electronic-enclosures/
- Protolabs, prototype to low-volume production / tooling decisions: https://www.protolabs.com/en-gb/resources/guides-and-trend-reports/prototype-to-production/
