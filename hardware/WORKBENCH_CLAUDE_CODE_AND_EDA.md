# CAD / PCB / electronics / BOM + coding agent workbench

**Recommendation:** use an agentic coding environment on a reproducible local workstation or configured Codespace; **Claude Code is one possible orchestrator, not the design authority**. Tools, checked-in native files and independent simulation / engineering review are authoritative. No purchase or fabrication implied.

## Tool roles (verified from official documentation, November 2026)

| Responsibility | Software and deliverable | Required check |
|---|---|---|
| Requirements / change history | GitHub repo, Issues/PR, Markdown/YAML, interface-control documents | Review named design revisions, acceptance tests and adverse outcomes |
| Coding agent | Claude Code + optional MCP tools, or another coding agent with shell/Git access | Agent cannot approve itself; explicit human review |
| Early product idea / BOM storyboard | Blueprint by 3E8 Robotics, https://www.blueprint.io/ | NOT a certified electronic schematic or fabricator-ready PCB; check invented parts |
| AI-assisted board exploration | Phaestus, https://phaestus.app/ (advertises KiCad, Gerber, STEP/STL) | Export and check *native editable* projects and source integrity |
| Production ECAD source | KiCad 10 https://www.kicad.org/ ; `.kicad_sch`, `.kicad_pcb`, libraries, full BOM | ERC, DRC, manual electrical/high-speed/PD safety review, net/class rules |
| ECAD automation | `kicad-cli sch erc`, `sch export bom`, `pcb drc`, `pcb export gerbers` | CI artifact reports + reproducible generation |
| Circuit & rail simulation | ngspice via KiCad + appropriate vendor SPICE models | Battery removal transient, PoE/DC power, brownout, inrush, thermal driver margins |
| Native parametric MCAD | FreeCAD 1.1 (or OpenSCAD for initial geometry) | Actual mechanical component dimensions, fit/interference checks, drawings and STEP |
| ECAD / MCAD link | KiCad StepUp (https://www.kicad.org/external-tools/stepup/) | Check PCB footprint/connector orientation against 3D assembly |
| Functional / energy simulator | Python fixed workload replay + profiling, model-level power-state assumptions | Simulation is not a substitute for external power and thermal metrology |
| BOM procurement | KiCad-generated component BOM + supplier MPN, quote and lifecycle audit | No bogus unit price or unavailable PCB footprint |
| Real metrology | Calibrated external DC power analyzer and thermocouples/logger | Raw samples + calibration ID + linked run hashes |

Sources: KiCad CLI https://docs.kicad.org/10.0/en/cli/cli.html ; KiCad/ngspice https://www.kicad.org/discover/spice/ ; FreeCAD https://www.freecad.org/features ; StepUp https://www.kicad.org/external-tools/stepup/ ; Anthropic MCP https://docs.anthropic.com/en/docs/mcp .

## Environment

- Start with `git clone` (or a controlled Codespace) of this repository. Use the `design/edge-device-metrology-20261120` branch / PR #52.
- Install pinned KiCad, ngspice, FreeCAD, OpenSCAD, Python and validation scripts on a supported workstation. Some GUI CAD/meter drivers require **local hardware**; a cloud-only coding agent cannot access physical instrument ports or safely validate thermal, fit, or battery swap.
- An agent may scaffold Python scripts, KiCad-native schematics, parametric FreeCAD/OpenSCAD geometry, BOM reconciliation, CI checks and experiment reports via terminal/MCP adapters. Disallow autonomous order placement, unsupported PCB fabrication assertions, secret export, unreviewed repository merges or direct control of hazardous battery testing.
- Prefer deterministic code generation from machine-readable schemas and pinned library revisions, with simulation inputs/checkpoints/hashes. **No runtime LLM** in embedded matching, biometric decisions, monitoring and signed update acceptance.
- Use `kicad-cli` for electrical-rule and design-rule checks and artifact export, then engineer-led review of Schematic / PCB / power/thermal/mechanical integration; passing ERC/DRC is not sufficient to assert safety.
- Start with an off-the-shelf SoM/SBC and small instrumentation/carrier PCB; do not attempt a first custom high-density SoC/NPU board with DDR/PCIe/MIPI without dedicated expertise.
- If cloud software/AI tools are used, never upload sensitive face embeddings, person/deny lists, secret keys or proprietary hardware documents outside an approved environment.

## Start with these five deliverables

1. **Use case and claims contract:** value hypotheses, permitted sensors, model test/data limitations, STOP/PIVOT/PERSEVERE decisions.
2. **System Block Diagram + Interface Control:** validated computing module, vision module pinouts, MCU wake domain, battery A/B, PoE PD, shunts, temperature probes, debug and secure LAN.
3. **Two independent benchmark harnesses:** synthetic 100k/500k/1m gallery 512D vs 128D measured 1:N energy/latency vs external meter, plus reference camera frames (consented or non-biometric phantom) and actual model inference.
4. **EDA source and BOM:** KiCad project for only the low-voltage monitoring board first, linked sensor readout matrix, BOM with real part numbers and supplier links; SPICE on power path; no fabricated board before verified protection.
5. **Fit and test plan:** parametric STEP/STL created from sourced dimensions, 3D check with KiCad, thermal/connector/battery serviceability tests, controlled milestone review.

## Pass / stop criteria

**PERSEVERE:** documented user benefit + measurement replication + operational/biometric feasibility.
**PIVOT:** justified architecture change (e.g. 1:1 local, off-device index, larger battery, no 5G, sensor-only detection) based on a measured bottleneck.
**STOP:** unacceptable false alerts / operator burden, no comparative value over simpler designs, cannot achieve safe battery/temperature/profile, or cannot lawfully carry out the proposed identification use case.

**This is a suggested toolchain, not a claim that Blueprint, Phaestus, KiCad, FreeCAD, Claude Code or actual hardware have already generated a production-valid design.**
