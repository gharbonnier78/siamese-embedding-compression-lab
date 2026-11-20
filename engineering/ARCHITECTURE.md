# Architecture and data/power boundaries

## Runtime separation

(1) **FIELD UNIT**: RGB EO + NIR + PIR, real acquisition and NIR eye-safety interlock; power switched Linux SoM/NPU + protected encrypted local storage and exact/ANN search; always-on low-power MCU with temperature, PoE/DC/BMS/case/tamper probes; short authenticated event notification over qualified RF; PoE/DC primary and electrical backup. All model/threshold/white/watch policies versioned. Hardware qualification and authorization are prerequisites for real identification.

(2) **EVENT SECURITY OPERATIONS RECEIVER**: local radio gateway (private LoRaWAN Class A is an option, not chosen), protected local console and dispatch operator; radio receipt ACK differs from human acknowledgement. NO personal identity/image/template in radio payload.

(3) **EXTERNAL EXPERIMENT BENCH**: PC, independent calibrated DC analyzer and thermocouple/logger, possible climatic/lighting rig, deterministic stress replay and result dashboard; attaches for experiments only, is never required to power the AI or store the only gallery.

(4) **BUILD/FAB TOOLCHAIN**: OpenSCAD or FreeCAD parametric MCAD → STL/STEP after fit; KiCad schematics/PCB → ERC/DRC and independent reviewer → Gerber/BOM/PNP; build provenance via GitHub Actions; no LLM in embedded runtime decision path.

## Interfaces — freeze after selecting actual components

| Interface | Type | Isolation/owner | Gate |
| --- | --- | --- | --- |
| Camera 1 RGB, Camera 2 NIR | CSI-2 or USB + hardware sync | AI compute and MCU trigger | exact connector / pinout TBD |
| PIR/tamper/ambient temp/RH | GPIO/I2C/ADC | MCU always-on | pull-ups/levels/EMI TBD |
| input/rail/BMS/shunt | isolated/rated shunt monitor + battery protection | MCU + independent external bench | electrical safety review mandatory |
| NIR emitter | MCU hardware inhibit plus approved LED driver | safety supervisor | optical radiation testing mandatory |
| MCU ↔ Linux | UART or USB protocol with CRC and power domain | buffered authenticated telemetry | pin map TBD |
| RF modem | UART/SPI, MCU-controlled duty cycle and supply | event security alert | module/antenna/country and encryption TBD |
| PoE/DC | qualified PD and protected regulation, backup | power safety domain | max power, surge and hot-swap TBD |
| external PC | authenticated Ethernet/USB diagnostic, instrument wiring | bench only | record no-PC test |

## Evidence taxonomy

Engineering evidence is a deterministic, versioned artifact with run_id; stage, device_id/pseudonym, site_profile, scenario_id, mode, firmware_model_gallery_config hashes, sample quality, calibration_id, timestamp+monotonic_ns, voltage/current/power, SoC/heatsink/ambient/case, capture/detection/ANN search/alert timing and trace/span IDs. External calibrated instruments are the ground truth for energy claims; MCU telemetry is supplemental.

Never upload authentic watchlists or face templates to a public repository, Flux.ai or public CI. Keep any protected research gates separate.

## Repository paths inherited from earlier work

- hardware/FIXED_EVENT_INSTALLATION_MISSION.md
- hardware/PROBE_INTERFACE_AND_TELEMETRY_SPEC.md
- hardware/LOW_POWER_SECURITY_ALERT_RF_REQUIREMENTS.md
- hardware/ULTRA_COMPACT_PACKAGE_STUDY_V0.md
- hardware/STAGED_ENVIRONMENTAL_PROTOTYPING_AND_DFM_V0.md
- business/ACTIVITY_SYSTEM_EX_ANTE_EXPLORATION_V0.md