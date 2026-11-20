# Three visual/mechanical enclosure variants — compare before choosing

**Status:** editable OpenSCAD P0 study; not a complete FreeCAD assembly, final cosmetic surfacing or proven STEP/production geometry. All three intentionally target **head W100 × H150 × D30 mm** as an *aspiration*. P1 bench hardware (ROCK 5B, breakout MCU, USB cameras) stays on a separate accessible fixture; never pretend it fits into the A-v2 thin product.

Source: [concept_variants.scad](concept_variants.scad). OpenSCAD command examples:
\`\`\`sh
for variant in hull book cassette; do
  openscad -D "style=\"$variant\"" -D 'part="assembly"' \
    -o "/tmp/siamese-$variant-study.stl" \
    engineering/mechanical/concept_variants.scad
done
\`\`\`

## Why three architectures are genuinely different

| | **A: Hull** | **B: Book** | **C: Cassette** |
|---|---|---|---|
| Industrial aesthetic | Single rounded, understated shell | Side-hinged service form | Rounded shell with deliberately replaceable front optical insert |
| Content/functional purpose | Minimize service seams | Frequent internal repair/diagnostic access | Optical module/lens replacement without opening electronics cavity |
| Enclosure joint complexity | Simplest conceptual main perimeter | Hinged moving gasket + latch | Main housing gasket plus distinct optical cassette seal |
| Alignment | Potentially fixed at assembly | Risk of recalibration after opening | Replaceable cassette needs repeatable mechanical datum |
| Thermal | Continuous rear metal conduction candidate | Hinge/cover may interrupt thermal path | Separate front cassette may isolate optical heat |
| Assembly | Nominally simplest | More hinge/latch work | More part/cassette work |
| Prototype difficulty | Low–medium | Medium | Medium–high |
| Status | EVALUATE | EVALUATE | EVALUATE |

This is not a measured performance ranking. The \`book\` SCAD hinge and \`cassette\` joint are **only suggestive visual geometry**, not engineered watertight parts. Thermal ribs do not penetrate electronics. No claim of IP65/IP66, UV stability, tropicalization, cooling or field reliability.

## Cross-variant measurement workbook — do not choose purely on beauty

- External head volume and installed volume including wall bracket, cable connector and any remote battery dock.
- Actual SoM, carrier, MCU probes, cable bend radius and camera lens STEP; integration/service clearance and optical axis geometry.
- NIR transparent window material, seal compression, anti-fog/drip mitigation, RF-transparent antenna zone.
- Measured/instrumented heat path with full sunlight and PoE/DC worst-case NPU+NIR load.
- Mounting and retention; real wall/truss connection load cases and anti-tamper.
- Price at 1 / 5 / 20 / 100 units, actual CNC/3D/finished materials, tooling and repair.
- P1 fixture and A-v2 head are separate CAD assemblies with independent acceptance.
- Select architecture with signed decision board (aesthetic fit, feasible environmental protection, physical fit, total installed volume, tool-free/repair access, cost, safety).

## Proposed parametric material stack

Rear base **CNC 6061 aluminium** with validated electrical and optical isolation; front **PC/ABS or anodized aluminium with independent polymer RF window**; **tempered/AR optical glass or selected NIR-compatible polymer**; **silicone/EPDM gasket** with defined compression, pressure equalizing vent candidate, conduction TIM; fasteners with corrosion resistance. These are *material candidates*, not selected grades or IP-tested assemblies. Follow [MATERIALS_AND_PROCESS_V0.csv](MATERIALS_AND_PROCESS_V0.csv) and [staged environmental plan](../../hardware/STAGED_ENVIRONMENTAL_PROTOTYPING_AND_DFM_V0.md).

**Recommended sequence:** render three comparable studies → inspect aesthetically → import exact vendor STEP bodies and perform 3D clearance checks → calculate thermal and power budget → print P0 dry-fit → build P1 fixture → only then freeze A-v2 and custom carrier.
