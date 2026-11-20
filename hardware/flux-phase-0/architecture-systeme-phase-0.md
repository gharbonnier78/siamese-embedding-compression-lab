# System Architecture — Phase 0

**Fixed EO/NIR unit for temporary event-entrance installation — review draft.** [Canonical mission](https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/8605b80dbd90/hardware/FIXED_EVENT_INSTALLATION_MISSION.md). The unit is transported between sites but remains stationary in service. The original dual hot-swappable battery requirement remains **under evaluation**, not deleted or selected. Reference load: ~1,000 passages/hour × 10 hours/day × 5 days = ~50,000 nominal passages over 50 active hours, not achieved performance. Include clustered arrivals; a 3.6-second mean interarrival interval is not a latency budget. Benchmark galleries of 100k, 500k and 1M separately.

```text
PASSAGE → PIR/sensor → always-on MCU → wake/shared trigger
        → RGB + NIR → quality → local CPU/NPU → local 1:N search
                         encrypted storage ↔ index + signed policy
                         → unknown / no decision / candidate for human review
Qualified PoE PD OR regulated DC → protection and switchover ← protected reserve
                                  → MCU/RTC/probes; switched compute, vision, NIR
Ethernet / radios / authenticated service: optional for local functions
External PC and instruments: experimentation, measurement and analysis only
```

| Requirement | Provisional approach | Evidence needed |
|---|---|---|
| Local operation without network or PC | Signed versions, encrypted storage, separate index and policy, MCU watchdog and log | Interrupt Ethernet data while maintaining power, then test combined loss and recovery; no runtime PC |
| Synchronized capture in fixed geometry | Calibratable mount, shared RGB/NIR field, trigger and exposure feedback, PIR or equivalent | Site survey, wake-to-capture delay, overlap, blur and optical safety |
| Fixed primary supply with backup | Regulated DC for prototype; PoE subject to class, cable, peak and thermal validation; backup topology open | Load profiles, reserve operating range, interruption duration, startup/recharge current and peak-load transfer |
| Indoor/outdoor operation | Rigid mount, protected enclosure and conduction to shell | Mount authorization and water, corrosion, sun, condensation, thermal and structural vibration tests |
| Onboard and independent metrology | MCU observes source/reserve BMS, optics/emitter/SoC/heatsink/shell temperatures, ambient conditions, tamper, link and log integrity; independent instruments only for tests | Ranges, calibration, timestamps and uncertainty |

## Primary power and continuity trade-off

Normal operation uses regulated DC or qualified PoE. The following options are alternatives to evaluate against the same primary supply and critical-load profile, not selected circuits.

| Continuity option | Coverage | Trade-offs and evidence |
|---|---|---|
| Two protected hot-swappable commercial packs | Can bridge source loss at the unit and allow one pack to be exchanged while the other carries the critical load | Greatest service continuity potential, but more volume, mass, connectors, charging coordination, sealing and validation effort. Prove transfer with either pack removed at peak load, lowest admissible pack state and cold/aged cases; characterize droop, inrush, contact events, backfeed, BMS cutoff and recovery. Verify safe usable access before approval. |
| Protected local backup module | Covers loss of the final supply cable while the reserve is available; may be sufficient for brief outages or controlled shutdown | Simpler first comparator, but reserve cannot be presumed replaceable without interruption. Validate transfer, usable runtime, charge/temperature limits and restart; characterize internal failure and service downtime. |
| Upstream UPS for PoE switch/injector or regulated DC supply | Bridges upstream mains loss for one or more loads | Centralized maintenance, but no coverage for loss of the final cable or downstream supply failure. Verify actual supported loads, UPS runtime, PoE behavior during transfer, and site responsibility. |
| Battery-only operation | Allows deployment with no site supply | Only if an explicit site requirement emerges; higher cycling and service burden over 50 active hours. Not the reference case. |

**Proposed decision, not a freeze:** start on protected regulated DC. Profile real loads and compare a local protected backup module and upstream UPS as reference cases. Evaluate dual hot-swap as a distinct design requirement and retain it if the agreed interruption coverage or live-service interval cannot be met by simpler options. Resolve required backup duration, covered fault cases and whether replacement must occur live before down-selection. A later decision to relax dual hot-swap must be explicit at review. No custom charger or unreviewed lithium power path.

Mission energy is the sum of power by state × time, including off-hours standby if required. Historical 8/12/18 W cases held for 50 hours give 400/600/900 Wh, illustrative only, excluding standby and any additional losses. Do not size reserve for these 50 hours. Reserve nameplate energy ≥ (critical-load power × outage duration + recovery/shutdown energy, in Wh) / (backup path efficiency × usable fraction at cold/end of life). Duration and critical load TBD. Check peak current and rail minimum separately. Size PoE from power available at the powered device (PD), not nominal port power; test cable drop, temperature, inrush, negotiation and recharge. Prevent backfeed between sources. For continuity candidates, use independent transient measurement under worst active load; require no reset, corruption or critical rail below its limit during the agreed continuity window.

## States and verification

Transport off: safe isolation per pack. Standby: MCU/RTC/IRQ and essential probes, with compute/cameras/emitter off as wake latency permits. Detection, 1:1/1:N and bursts: local compute and vision; NIR defaults inhibited and is inhibited on faults. Supply loss: instrument transfer, maintain critical load for the agreed interval or shut down and recover safely without corruption. Service/update: signed artifacts, rollback and logging; measure any network-reachable standby cost separately. Distinguish Ethernet data loss from PoE power loss. No automatic action on a candidate; synthetic and consent-based evaluations only, no real watchlists or non-consensual identification.

## Increments and review

1. Fixed optical kit and wall-mount mockup; tripod for calibration and controlled measurement only. 2. Integrate COTS compute offline and measure load profiles/transients. 3. Independent instrumentation and possible probe board after whole-device review. 4. Enclosure, thermal and environmental qualification, then a limited consented pilot after authorization. No schematic or routing before whole-device review.

**STOP** for unsafe mounting, optical/electrical risk or lack of authorization. **PIVOT** if 1:N does not improve on passage-only or local 1:1 within energy, latency and operator workload limits. **PERSEVERE** only against preregistered criteria with independent evidence. Open: site survey, camera/compute configuration and drawings, covered interruption and live-service requirements, PoE class or DC specification, test thresholds and authorization.
