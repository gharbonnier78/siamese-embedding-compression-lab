# Product Bill of Materials

**Phase 0 shortlist, not a procurement BOM.** Source: [historical BOM](https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/83c70dde825c/hardware/BOM_PROVISIONAL.csv), revised for the fixed mission. IDs are functional, not schematic designators. Prices, availability and lead times are unverified.

| ID | Indicative qty | Block / documented candidate | Open evidence and power item |
|---|---:|---|---|
| PR-01 | 1 | Linux compute: [Radxa ROCK 5B](https://docs.radxa.com/en/rock5/rock5b) candidate; Linux CPU alternative | SKU, RAM, dual capture/trigger and runtime; standby, startup and burst |
| PR-02 | 1 | eMMC or NVMe plus protected identity/TPM as supported | MPN, endurance, boot/key and space for A/B software versions; access and idle power |
| PR-03/04 | 1+1 | Wide-angle RGB and NIR cameras; modules and optics TBD | Shutter, spectral response, trigger and FOV; simultaneous capture |
| PR-05 | 1 | Emitter, driver and interlock unselected | Spectral and thermal safety, pulse current and idle |
| PR-06 | 1 + option | PIR; mmWave test alternative; IMU | False wakes by mode, IRQ, standby and acquisition |
| PR-07 | 1 set | MCU, watchdog, RTC and durable memory unselected | Clocked sleep current, retention and wake consumption |
| PR-08 | TBD | Rail monitoring: [TI INA228AIDGKR](https://www.ti.com/product/INA228) candidate; alternative ADC/monitors | Range, shunt, dissipation, addressing, continuous power and shunt loss |
| PR-09 | ≥4+1 | Thermal probes, ambient/humidity, tamper and IMU if not included | Locations, calibration, sampling and standby |
| PR-10 | Alternatives only | Two protected commercial hot-swappable packs with vendor-approved charge/power path (requirement under evaluation); protected local backup module as baseline comparator; upstream UPS as site-side alternative, not embedded BOM | Outage coverage, live-service need, cold usable Wh, BMS, recharge and review; if dual packs, demonstrate continuity on removal of either at worst load |
| PR-11 | 1 set | Protected regulated DC and backup transfer; external PoE PD candidate if budget passes | Peak, dips, cable drop, power at PD, recharge current and no backfeed |
| PR-12 | 1 set | Chassis, seals/windows, wall plate or rigid adapter, retention, cable gland and tamper detection | Site data, loads, clearance, conduction, transmission and ingress; tripod excluded |
| PR-13 | 1 service + options | Authenticated service; Ethernet data if planned; optional Wi-Fi/5G | Network independence, markets, standby/TX energy; no runtime link requirement |
| PR-14 | TBD | **Electrical wiring harness** (cable assembly, not a body-worn mount), connectors, test access and possible interface board | Geometry TBD; PCB partition not yet defined. Device remains fixed in operation. |

Numerical budgets remain open: measure idle, active, p95/peak and time in each state on actual modules, then verify average input power and enclosure temperatures. Do not double-count losses when measuring at input. Prefer LCSC for electronic components when sourcing; source COTS assemblies, batteries and instruments separately.
