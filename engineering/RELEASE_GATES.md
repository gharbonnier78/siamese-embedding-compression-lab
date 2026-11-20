# Engineering release/acceptance register (NOT approval)

| ID | Exit criterion | Owner / evidence | Current status |
| --- | --- | --- | --- |
| SYS-01 | fixed-site functional/system scope reviewed, no PC runtime dependency | system architect and proof | OPEN |
| OPT-01 | RGB/NIR resolution, common FOV, sync, eye-safety on chosen lenses | optics engineer, data sheet + test | OPEN |
| CPU-01 | chosen compute SoM runs pinned model, 1m vector stress, sustained thermal | software/SoM reviewer, signed bench report | OPEN |
| POW-01 | PoE/DC transient and brownout/backup, protected batteries/charging | qualified power engineer / hardware log | OPEN |
| PROBE-01 | every sensor has documented bus/IRQ/power/driver and independent calibration | electrical and metrology reviewer | OPEN |
| RF-01 | low-power event organizer alert coverage, receipt ACK vs human ACK, duty cycle and RF compliance | radio/ops reviewer | OPEN |
| EMC-01 | emissions and electromagnetic compatibility appropriately assessed | certification lead | OPEN |
| CASE-01 | assembly STEP drawing, thermal path, RF window, gasket, cable inlet, fasteners verified | mechanical reviewer + FAI | OPEN |
| ENV-01 | selected outdoor ingress/humidity/cold/sun/thermal tests on COMPLETE assembly | environmental lab | OPEN |
| DATA-01 | signed update/rollback, storage encryption, loss/tamper events, access control | cyber/security reviewer | OPEN |
| LEG-01 | written purpose-specific legal authorization before real-world biometric testing | accountable controller/legal reviewer | HARD STOP |
| SCI-01 | separate independent biometric model validation without breaching sealed scientific gates | scientific authority | HARD STOP |
| FAB-01 | complete schematics, routed PCB, ERC/DRC, netlist parity, qualified BOM, vendor approval | qualified EE; signed build pack | HARD STOP |
| BIZ-01 | customer pain/paid pilot/legal pathway validated against simpler baseline | venture reviewer | OPEN |

## Demonstrator readiness and proposed acceptance thresholds

The evidence-class and 26 traceable proposed requirements are in [SYSTEM_REQUIREMENTS_TEST_EVIDENCE_V1.csv](docs/SYSTEM_REQUIREMENTS_TEST_EVIDENCE_V1.csv). **S0 512D/128D DCT-based image tests and S0 digital twin are permitted synthetic demos**; these do not change CPU-01/SCI-01/LEG-01 from OPEN/HARD STOP. Three OpenSCAD conceptual 3D variants are not CASE-01 validation. Passing GitHub CI is only software/build assurance, not a signal to fabricate KiCad or deploy biometric screening.

## Release rule

Every gate requires a named person, date, referenced commit SHA, measured configuration, raw immutable evidence and explicit signed GO/CONDITIONAL GO/NO GO. P0/P1 source files alone do not make G3/G5 pass.

**This branch intentionally contains an unrouted KiCad board-outline study and software simulations. Never supply its PCB to a fabrication service as if electrically complete.**