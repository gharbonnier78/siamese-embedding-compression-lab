# Build, instrument, fabricate — handoff plan

## Build sequence, lowest-cost discrimination first

**P0:** source actual vendor datasheets and mechanical dimensions for two global-shutter candidate modules, one edge SoM, lens holders, NIR-safe emitter, PoE/DC and radio; run fit model and bench workloads. A 100×150×30 mm front envelope is a target, not a locked mechanical drawing. Proto with PLA/PETG for dry fitting ONLY, not sun/rain/IP qualification.

**P1:** COTS SoM + two camera modules + PIR, external approved lab DC PSU, external calibrated power meter + thermal logger + small MCU development board + radio development board. Frame may be open. Trigger synchronization, camera data paths and local model must be tested against selected real modules. Dry and bench safe only.

**P2:** enclosure revision with replaceable gasket, optical window seals, external metallic fins/heat spreader, protected cable gland, secure bracket; independent power/thermal tests. Use commercial approved backup modules, not a self-built lithium charger/cell pack.

**P3:** select a low-voltage probe carrier KiCad schematic and component-specific footprints after voltage/current/connector pinouts verified, only then route copper, run KiCad ERC/DRC and inspect 3D STEP; request DFM from PCBA vendor. Validate RF antenna detuning, PoE/EMC and NIR photobiological safety.

**P4:** first article with assembly photos, sensors calibration, system and optical tests, environmental ingress/temperature/humidity cycles. Site pilots on synthetic/non-identifying events; no biometric public-space watchlists without authority.

**P5:** formal production pack: full design source, released STEP+STL+2D drawings, vendor material grade and coating, schematic and board, Gerber/Excellon, CPL, supplier MPN/eBOM, mechanical mBOM, test fixture and programming commands, firmware signing, calibration certificates and traceability. Volume/DFM assessment before molds.

## Deliverable matrix

| Artifact | Editable source | Fabrication or executable output | Check |
| --- | --- | --- | --- |
| Mechanical body/lid/bracket | mechanical/enclosure.scad | STL / CAD STEP via reviewed FreeCAD/CadQuery | fit + heat + materials + tolerances |
| Electronics | electronics/kicad/edge_probe_carrier.kicad_pcb | Gerber/Excellon only AFTER schematic/DRC/manual review | power, pinout and copper review |
| MCU supervision | firmware/* (C) | test executable; target binary ONLY after board port | timing, fault injection and safe state |
| Linux edge algorithm | device/synthetic_matcher.py | simulation binary; real model excluded | quality/data legal gate |
| PC acquisition | sim/bench.py | CSV/JSON reports | independently measured calibration data |
| BOM | bom/*.csv | vendor-priced purchase manifest ONLY after sourcing | exact MPN + footprint/revision + availability |
| Trace/requirements | docs/* and telemetry/schema.json | traceability/evidence bundle | owner/reviewer signature |

## Supplier instructions

For PCBA supply native KiCad design, ERC/DRC, standard fab output, placements, assembly PDFs, tested BOM and substitutions; require manufacturer sign-off to any alternative. For mechanical supply approved STEP, native source, tolerances, gasket compression/adhesive, window spectral data, surface finishing, fastener torque and support loading. For RF/environmental test provide COMPLETE assembled head and power dock in intended outdoor configuration.

Do not claim IP66/67, tropicalization, 20 Wh autonomy, hot-swap or 1:N real accuracy until independently verified; conformal coating is deferred until prototype probing/rework is stable.
