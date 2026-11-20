# Siamese Embedded — FIXED event installation (canonical mission corrected 2026-11-20)

**Start with [fixed event-installation mission](FIXED_EVENT_INSTALLATION_MISSION.md) and [corrected Flux.ai starting prompt](FLUX_AI_START_HERE.md).** The product is an autonomous, temporarily wall-/support-mounted EO/NIR + local 1:N device. Tripod = controlled measurement/calibration only, not the target product. People move; the installed device remains stationary. The low-voltage sensor PCB is only one subassembly; the PC, calibrated instruments and environmental rigs are a SEPARATE qualification bench. Two discrete BOMs exist: [device](BOM_PRODUCT_FIELD_DEVICE_V0.csv) and [bench](BOM_EXTERNAL_TEST_BENCH_V0.csv). The prior exploratory combined BOM is retained for historical traceability only.

---
# Edge biometric-device engineering track (exploratory, 2026-11-20)

Status: **DESIGN EXPLORATION / NOT YET BUILDABLE / NO PROCUREMENT APPROVAL**.

This track reconstructs the Aug 20 2026 discussion ("Projection Siamois 19 08 26", preceded by "PCA et projection siamoise") about a compact on-device detection, verification and 1:N search demonstrator. It is independent from biometric scientific qualification. The existing Study 0 negative result and Study 1B sealed outcomes are unchanged; **do not consume protected Study 1B SCREEN/TEST or claim deployable biometric performance**.

## Objective and key falsifiable proposition

**Source hierarchy:** [FIXED_EVENT_INSTALLATION_MISSION.md](FIXED_EVENT_INSTALLATION_MISSION.md) supersedes earlier handheld/harness/walking-device design ideas. Prefer PoE/regulated DC for event operation, with reviewed backup continuity and optional hot-swap; the external PC is bench-only.


Not "prove Siamese is better" but determine whether 512D -> 128D compression (random/PCA/learned with matched controls) produces a **measured beneficial trade-off** on a real edge workload, after accounting for biometric degradation and operational cost. A technically interesting device may have **no justified real-world use case**; the STOP result must be admissible and documented.

## Prior design recovered from chat (not verified drawings)

Conceptual ~EUR 700 RK3588-class SBC, RGB wide-angle + IR/NIR camera, PIR sensor, Ethernet/PoE, optional Wi-Fi + 5G communications, optional secure element, roughly 20 Wh demonstration battery. Assumptions only, NOT manufacturer specifications or current price quotations. Reference deployment: 1,000 visitor encounters/hour, 10h/day for five days; reference galleries 100,000 / 500,000 / 1,000,000 identities. Power scenarios historically hypothesized: 8W / 12W / 18W; none has been measured. Thermal limits, battery runtime, compute headroom, enclosure dimensions and optical arrangement are **TBD**.

Note that 20 Wh is a small bench battery, not evidence of multi-day stand-alone operation. The 10h/day x five-day operational workload needs an explicit external power/charging strategy.

## System architecture

- Isolate sensing (PIR / RGB / NIR), pipeline execution (detect, quality, PAD gate where justified, align, feature extraction), post-extractor projection, storage, ANN indexing, 1:1 verification, 1:N candidate identification, event policy, communication, and maintenance.
- Compare at least raw512, PCA128, random128, Siamese128 **only when scientific access gates permit**. Meanwhile use deterministic non-biometric synthetic embeddings and reference workload replay for engineering-only tests.
- The 512->128 projection does not automatically reduce RGB/NIR capture or extractor compute. Separate baseline cost: acquisition + detect + quality + PAD + extraction + projection + indexing + search + reporting + communications.
- Local privacy-by-design: consented lab subjects or synthetic data, purpose-limited records, encrypted templates, retention controls, enrollment deduplication, signed software artifacts, instrumented audit; no public-space identification deployment for this research prototype.

## Modes and scenarios

1. OFF / transit-storage (leakage and safety).
2. SLEEP / low-power wake (PIR optional, camera off).
3. IDLE WATCH (monitoring/polling, no matching).
4. DETECT ONLY (RGB capture, presence detection, quality gate).
5. VERIFY 1:1 (authorized enrolled test subjects; threshold frozen on VALIDATION).
6. IDENTIFY 1:N (synthetic gallery sizes and/or authorized benchmark; report FPIR/FNIR at preselected operating points).
7. BURST (1,000 visitors/hour workload replay).
8. TRANSMIT (alert payload, Wi-Fi/Ethernet and optional cellular; no real biometric upload by default).
9. THERMAL SOAK / FAILURE (ambient temperature, thermal throttling, network outages, camera downtime, reboot; watchdog and recovery).

## Architecture options: trial and reject

A. Passive controlled USB/PoE-powered rig with external meter, RGB only. Cheapest and lowest scientific coupling; preferred FIRST BUILD.
B. Dual RGB + NIR enclosure with local search and passively cooled SBC; proceed only after A's metrology and fit checks.
C. Battery-powered field-representative unit; proceed only after measured idle and active duty cycles show attainable autonomy.
D. Full outdoor or large-scale 1:N unit; defer unless justified by credible user discovery, privacy/regulatory feasibility and comparison to distributed or centralized alternatives.

## Design and build gates

**G0: use-case falsification.** Named user, operating boundary, false-alert workload, alternatives, economic model; explicit STOP criteria.
**G1: metrology rig.** Hardware selection, safe regulated power supply, characterized external instrumentation, replay harness and repeatability demonstrated; BOM cost estimates independently checked.
**G2: breadboard performance.** Measured mode-by-mode watts, joules/transaction, temperatures, thermal throttling, p50/p95 latency, RAM, gallery footprint, index recall and data-transfer volume. Produce raw CSV and hashes.
**G3: mechanical prototype.** Freeze exact board/camera connector geometries, connector cutouts, optics, ventilation, CAD dimensioned drawings and BOM revisions before ordering/printing an enclosure.
**G4: optional field trial.** Consent/privacy review, authorized biometric performance, threat model, operational TCO, acceptance criteria; do not infer qualification from hardware tests.

## Arkema visit (3 December 2026)

The visit to Arkema's "Le Lab" at La Défense is an opportunity for material-selection discussion, introductions and potentially referral to additive-manufacturing / thermal-management experts, **not a confirmed access to an engineering or fabrication laboratory**. Prepared questions: polymers for enclosures and flame rating; additive-manufacturing shrinkage/tolerance; optical NIR window materials; heat spreader and thermal interfaces; battery compartment material/safety; environmental aging, repair and end-of-life. Do not share proprietary design files or biometric data without appropriate agreements.

## Links / limitations

- Existing research programme: `RESEARCH_PROGRAM.md`.
- Existing Study 1B engineering PR #50: https://github.com/gharbonnier78/siamese-embedding-compression-lab/pull/50 ; do not change its independent-review or protected-outcome rules.
- See `hardware/BOM_PROVISIONAL.csv` (placeholder, not validated for purchase) and `hardware/METROLOGY_AND_DECISION_PROTOCOL.md`.
- See `hardware/cad/README.md` for mechanically unverified placeholder enclosure and fabrication handoff.

## Updated November 20 design baselines

- [Full local model / 1:N system architecture and whitelist/blacklist policy semantics](EDGE_SYSTEM_ARCHITECTURE_V0.md) — distinction between matched candidate and a confirmed identity, signed atomic gallery/policy revisions and privacy limits.
- [Structured system contract (YAML)](DEVICE_CONTRACT_V0.yaml) — research workloads, sensor/power domains, hot-swap and contract-level gates.
- [Probe readout / PoE / Ethernet / low-power secure telemetry](PROBE_INTERFACE_AND_TELEMETRY_SPEC.md) — always-on MCU, external metrology, low-power readout, network sleep trade-off.
- [Probe readout matrix](PROBE_INTERFACE_MATRIX.csv) — sensor observables, physical acquisition interface, firmware readout and reporting requirements.
- [CAD / KiCad / SPICE / Claude Code or alternative workstation workflow](WORKBENCH_CLAUDE_CODE_AND_EDA.md) — use real native engineering files and validation tools.
- **BOM revised:** 36 provisional equipment lines including dual approved protected battery modules, PoE PD, probe ADCs/shunts, MCU, independent thermocouple logger, encrypted storage, secure identity and power-loss-safe OTA. This is not a priced or approved BOM.

**Design choice not yet made:** exact compute module and accelerator, model NPU compatibility, camera/NIR timing/pinouts, power domains, electrical schematic and actual PCB, verified connectors and enclosure dimensions. The early CAD model is a shape prototype, **not a manufacturing file**.
