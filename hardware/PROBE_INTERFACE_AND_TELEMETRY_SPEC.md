# Probe, acquisition and secure telemetry architecture — design v0.1 (2026-11-20)

**Status:** preliminary engineering specification for the draft edge-device PR #52. No board schematic / firmware / electrical isolation or real-world test has been validated. This document distinguishes prior August 20 decisions from prospective design additions.

## Historical baseline (August 20, 2026)

- Low-power presence probe gates camera/NPU wake-up.
- Synchronized RGB and NIR imaging, hardware GPIO/TTL trigger and pulsed NIR illumination; NIR emitter off in idle.
- Wi-Fi as primary mobile uplink, 5G failover, buffered store-and-forward.
- Optional Gigabit Ethernet with PoE for fixed installation.
- Power from deep-idle -> wake -> acquisition -> embedding -> search -> sleep; thermal/throttling, camera sync, PoE/DC versus battery to be *measured*, not asserted.

Other items below are proposed engineering requirements, not claims of prior specification or implementation.

## Fundamental requirement: two independent measurement paths

**A. Onboard operational probes:** ultra-low-power supervision MCU (always-on domain), ADC/I2C/SPI/GPIO and nonvolatile timestamped ring-buffer; maintain monitoring even when AI SoC and cameras sleep. MCU wakes main SoC via interrupt and records wake/boot time, fault/tamper, power path, hot-swap. Calibrated/filtered metrics can be exported over an authenticated service when a gateway is active. MCU telemetry is not automatically a laboratory-grade measurement.

**B. External bench reference:** independent calibrated DC power analyzer/shunt at declared boundaries (PoE output / DC converter / device input / relevant rails), thermocouples/logger and optional IR thermography. Record in synchronized timestamps with known sampling bandwidth. Calibrate/compare onboard against external reference. Use external analyzer to substantiate joules/operation and wake peaks.

**Sensor readout is a required design deliverable:** interface pins and power domains, bus addresses, ADC ranges, sensor drivers, firmware versions, read intervals, timestamp provenance, accuracy/calibration, raw sample formats, logger retention and off-device transport. A BOM item with no documented readout is not accepted.

## Probe-to-readout matrix: minimal baseline and optional expansions

| Probe / quantity | Placement and observable | Electrical interface | Sleep-domain requirement | Exposed measure / failure |
|---|---|---|---|---|
| Presence/wake | PIR, optional mmWave for difficult targets | MCU GPIO IRQ, optional UART/I2C | **Always-on** | event count, wake cause, false wake; PIR vs mmWave power |
| Visible EO camera | RGB camera sensor and frame timestamps | CSI-2/USB to vision SoC + GPIO sync | Off when asleep | fps, capture/drop, exposure, trigger jitter; image data kept separate |
| NIR camera | NIR sensor, exposure/trigger | CSI-2/USB + GPIO/TTL to SoC | Off when asleep | frame sync delta, failed capture |
| NIR emitter | pulsed illumination current, pulse time, board temperature | MCU ADC + MOSFET driver enable / PWM / thermal I2C | **Off when asleep** | peak current, pulse energy, temperature, interlock / eye safety |
| DC/PoE input power | input voltage/current before and after DC conversion | shunt/power monitor I2C to MCU; independent bench analyzer | **Always-on** | instantaneous W, cumulative Wh, peak current, brownout |
| Battery A / B | pack voltage, temp, SoC / SoH if supported, pack presence | smart-pack SMBus/I2C or BMS status lines; ADC | **Always-on** | %SoC, pack health, missing battery, swap events, charge/discharge current |
| Power-path ORing / holdup | continuity and rail droop during removal | supervisor GPIO + ADC | **Always-on** | droop, uninterrupted runtime, reset count, isolation fault |
| AI SoC/NPU | die temperature, frequency, thermal throttle, accelerator utilization | kernel hwmon/sysfs / driver counters | unavailable while SoC off | temp, throttle events, inference clock, actual throughput |
| Thermal conduction | heatsink, enclosure exterior, camera/LED assembly | digital temp sensor I2C or thermocouple logger | critical hotspots on MCU if possible | `temp_C`, max/min, thermal time constant |
| Environmental | ambient temperature, RH; optional pressure | I2C sensor | MCU sampled intermittently | ambient_C, relative humidity, condensation risk estimate |
| Tamper/motion | enclosure open, accelerometer, shock/tilt | MCU GPIO, I2C interrupt | **Always-on** | tamper flag, impact, mounting orientation |
| Network links | Ethernet link, PoE classification, Wi-Fi RSSI, 5G link | PHY/MAC status, modem diagnostics, PSE/PD telemetry | conditional | link status, network failure, backlog size, modem energy |
| Cooling (if used) | fan tach, PWM, fan fault | MCU GPIO PWM + tach | depends thermal policy | rpm, fan failure, watts |
| Storage | free flash, write wear, queue depth | OS/block health or MCU NVM | depends domain | remaining endurance, queue loss / overflow, dropped samples |
| High-level 1:N runs | match pipeline traces, 100k/500k/1m galleries | app spans/OTEL + CPU/NPU profiler | active workload | J/query, p95 time, memory, result provenance; no biometric claims |

**EO/IR clarification:** this stage specifies RGB plus NIR. Long-wave IR thermal imaging (LWIR) is a separate camera class and has **not** been selected. The low-cost thermal probe used to measure device heat is not an LWIR scene camera.

## Interface architecture and physical connection options

### Fixed-installation wired path (proposed)
- **Ethernet:** 1000BASE-T wired LAN for high-rate telemetry, signed software updates, diagnostics and optional local streaming. Choose connector after mechanical environmental requirements: full RJ45, ruggedized connector or board-to-board internal Ethernet; "micro-Ethernet" is not a uniquely defined interface specification.
- **PoE:** IEEE 802.3at Type 2 PoE+ provides up to 25.5 W to a powered device; IEEE 802.3bt Type 3 can allow up to 51 W at PD, subject to class and design. Choose PD controller/DC converter based on *measured* peak SoC + RGB/NIR + illumination + peripherals. PoE delivers **power and Ethernet data**, but does not directly read I2C probe buses.
- **If 'micro Ethernet' means Single-Pair Ethernet (SPE):** 10BASE-T1L + optional PoDL is a distinct physical interface suitable for remote distributed low-rate sensors. It is **optional** and likely unnecessary for probes placed centimetres away on the same PCB. 10BASE-T1L does not substitute for Gigabit video/firmware uplink.
- **PPPoE**, if that is what 'ppoe' means, is Point-to-Point Protocol over Ethernet for network access/session management; it is not PoE electrical power. Do not treat these names interchangeably.
- Use power-good, reset and watchdog monitoring across the Ethernet/PoE DC paths; expose link degradation and PoE-class/power budget as telemetry.

### Mobile / battery path (prior design and proposed details)
- **Wi-Fi primary / 5G fallback**, with tested failover, link authentication, store-and-forward; 5G is a significant load so test separate energy and reconnect scenarios.
- **Hot-swap without interruption** needs two independently protected commercial packs or one pack plus a validated holdup supply, power-path management with ideal-diode/ORing architecture, compatible charger/BMS, and a provable minimum voltage during removal/insert. Actual uninterrupted swap must be lab-proven under worst-case active load, with safe mechanical isolation.
- This project does **not** prescribe building DIY lithium packs or hot-swap circuits from untested cells. Certified components, battery safety review and appropriate protections are required.
- In deep sleep, the main SoC, high-power ethernet PHY and 5G may all be off. A constantly reachable network management endpoint while asleep requires a separate powered networking domain and substantially changes idle energy. **Freeze which of three service levels is required:** (i) local log and wake only, (ii) scheduled low-duty-cycle authenticated reporting, (iii) network always-reachable in sleep. All three require different battery lifetime estimates.

## Secure telemetry / maintenance contract

1. MCU keeps clocked samples/interrupt events in a bounded nonvolatile queue. Define durable event type, timestamp (monotonic + periodically disciplined wall-clock), sensor ID, calibration ID, sensor/driver firmware and sample quality.
2. Linux/AI SoC gathers burst samples and OTEL spans into an event-correlated local log. Each 1:N operation carries `trace_id/span_id`, `device_id`, `scenario_id`, `run_id`, `mode`, gallery size and frozen code/model versions. No image/template in standard metrics.
3. Gateway exports aggregate operational metrics over **MQTT/TLS (mutual certificates)** or HTTPS/mTLS, with replay protection, device identity, RBAC, signed firmware and hash-tagged batches. Select one production protocol after network threat review; no mandatory cloud.
4. Independently allow an authorized local Ethernet maintenance/debug service with authenticated access, audit trail and limited diagnostic modes. Default deny network access to raw image/templates; mTLS/VPN where appropriate.
5. **Secure OTA:** signed update manifests; verified boot where platform permits; image hashes, dual-bank/A-B OS partitions or equivalent rollback, power-loss-safe update sequencing, independently updateable MCU firmware, key rotation, anti-rollback policy and human GO for major model/security changes.
6. **Failure behavior:** power loss, link outage, buffer full, sensor fault, clock loss, stale calibration, BMS fault and watchdog reset each logged with durable counter. Expose `last_good_sample`, `device_health`, `sensor_health`, `backlog`, `firmware_versions`.
7. Science gates: updates must not alter protocol-locked experiment runs; mark device and run configs immutable; separate operational metrics from scientific study outcomes.

## Preliminary observability data contract

| Metric or event | Suggested unit / type | Source / cadence |
|---|---|---|
| `device.power.input_w`, `energy.input_wh` | W, Wh | MCU meter; per-mode 1 Hz idle, 10–100 Hz active to *trial* |
| `device.energy.operation_j` | J/operation | external bench analyzer matched to span timestamps |
| `battery.a.soc_pct`, `battery.b.soc_pct`, `battery.swap_count` | %, count | smart BMS/MCU, events immediate |
| `device.temp.soc_c`, `device.temp.surface_c`, `device.temp.ambient_c` | °C | MCU/OS/thermocouples |
| `vision.trigger.delta_ms`, `vision.frame.drop_count` | ms, count | hardware sync / app |
| `device.wake.cause`, `device.wake.latency_ms` | enum, ms | MCU+host |
| `network.link.state`, `network.queue.bytes`, `network.failover_count` | enum, bytes, count | gateway |
| `device.firmware.version`, `device.sensor.calibration_id` | string | signed config manifest |
| `device.thermal.throttle_count`, `device.brownout_count` | count | OS+MCU |

Rates above are **exploratory suggestions**: sampling suitability must be validated against peak durations and sensor conversion times. External bench capture may require much higher bandwidth. Measure logging overhead/power so telemetry does not distort the claimed energy savings.

## Verification gates

- [ ] V0: full sensor map with selected electrical parts, pins, bus address conflicts, power domains, calibration method, software driver and state-machine.
- [ ] V1: compare onboard voltage/current/temperature data against external calibrated instruments, and validate timestamps/offsets.
- [ ] V2: prove zero sample gaps at relevant mode transitions; interruptions explicitly flagged.
- [ ] V3: prove minimum real battery life in defined 1,000 events/hour duty-cycle; no extrapolation-only claim.
- [ ] V4: simulate Ethernet unplug, Wi-Fi/5G failover, tamper, storage full, PoE fault, single-battery extraction and replacement; report resets/lost data.
- [ ] V5: prove encrypted authenticated probe retrieval, least privileges, signed update and rollback/power-loss safety.
- [ ] V6: test idle low-power domain separately from optional network-always-available domain and quantify baseline watts.

## Sources / technical references

- Ethernet Alliance, overview IEEE 802.3bt, class/PD delivery: https://ethernetalliance.org/wp-content/uploads/2019/12/WP_EA_Overview8023bt_V2p1_FINAL.pdf
- Cisco PoE classification reference: https://www.cisco.com/en/us/td/docs/switches/lan/c9000/infra/poe/poe-configuration-guide/g-poe/c-poe.html
- TI 10BASE-T1L PoDL reference design: https://www.ti.com/tool/TIDA-010261
- Microchip SPE industrial interfaces: https://www.microchip.com/en-us/products/interface-networking-connectivity/ethernet/single-pair-ethernet
