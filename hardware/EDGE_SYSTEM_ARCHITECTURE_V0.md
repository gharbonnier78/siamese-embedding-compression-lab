# Fixed event-mounted EO/NIR + 1:N system architecture — engineering contract v0.2

**Canonical deployment constraint:** [FIXED_EVENT_INSTALLATION_MISSION.md](FIXED_EVENT_INSTALLATION_MISSION.md): temporary wall/support installation, fixed geometry; tripod only for measurements. Operating power preferred from PoE/DC with protected battery backup; PC bench-only. People move; the product does not.

**Status: PROPOSED (2026-11-20), subject to technical/electrical/privacy review; not built, certified or deployed.** This document extends the August 20 prototype concept. It does not assert prior implementation of a whitelist/blacklist engine or that 1:N performance is proven. Keep Study 1B protected SCREEN/TEST sealed and unaffected.

## Mission and falsifiable value claim

Validate, using synthetic replay first and properly authorized small-scale captures later, whether a self-contained edge device offers a material benefit over a camera+server, non-biometric sensor, or 1:1 verification. The research question is not whether a particular learned embedding **must** win. Compare raw512, PCA128, random128 and Siamese128 when scientific gates permit; otherwise benchmark synthetic vectors only. Device design is permitted to **STOP** if deployment is economically, ergonomically, thermally, biometrically, legally or operationally unjustified.

Reference demand, not qualification: 100k, 500k and 1M local gallery records; 1,000 encountered visitors/hour; ten hours/day for five days. This is a workload to challenge, not an authorization for surveillance or an achieved capability. Use consented test subjects or synthetic gallery vectors; no public-space or unconsented blacklist enrollment.

## Functional decomposition

```text
PIR / optional mmWave -----> ALWAYS-ON SUPERVISOR MCU  <--- battery A/B BMS and power-path sensing
     |                              | IRQ/wake     | samples / fault log
     |                              v              v
     |                     SWITCHABLE HIGH-POWER DOMAIN
     |                              |
RGB EO camera ------ capture timestamp / trigger ----+
NIR camera + safe emitter ------ synchronization ----+-> quality / PAD (only if validated)
                                                        -> face detection -> alignment
                                                        -> on-device extractor (AdaFace or proven substitute)
                                                        -> post-extractor projection (raw/PCA/random/Siamese)
                                                        -> 1:1 verification OR 1:N retrieval
                                                        -> threshold and policy decision
                                                        -> optional human review / event notification
                                                        -> privacy-preserving operational telemetry
                 [encrypted gallery vectors and ANN index] -> matching
                 [separate policy/identity metadata store] -> allow/deny/watch semantics
    OPERATIONAL SECURITY PLANE: secure boot, signed A/B updates, mTLS access, secrets/keys
     CONNECTIVITY: Gigabit Ethernet / PoE(+), Wi-Fi, optional 5G and offline local queue
    INDEPENDENT METER: external power analyzer / probes with shared experiment timeline
```

**EO/IR terminology:** RGB-visible plus NIR near-infrared was the recovered baseline for capture/illumination. A thermal IR (LWIR) scene camera is a distinct optional sensor and should not be silently substituted for NIR. Thermal sensing of enclosure/SoC is a separate metrology function.

## Where the model lives

- Main compute: Linux SoM/SBC with CPU + GPU/NPU and **verified runtime support** for extractor operator graph (ONNX export feasibility and target NPU conversion are not assumed); sufficient RAM and eMMC/NVMe.
- **Pinned model package:** network-independent inference, immutable version/hash/signature, preprocessing contract, embedding dimension and normalization, quantization parameters, runtime driver/firmware, benchmark recipe and rollback.
- **Pinned gallery and index:** encrypted-at-rest gallery templates; per-template `embedding_model_id` + `projection_id`; bounded versions and atomic index snapshot. Do not compare embeddings originating from incompatible extractor/projection versions without explicit validated migration.
- **Separate metadata and policy:** enrollment identifier/pseudonym, authorized source and consent, policy membership, effective start/end, revocation, audit and access rights. Avoid embedding personal data in logs/ANN index. Never publish facial image or raw vectors in telemetry.
- **On-device matching:** explicit 1:1 (claimed ID) and 1:N (unknown probe) paths; exact search reference and optional ANN index; validate ANN recall separately from biometric error.
- **Continuous offline operation:** keep model, gallery snapshot, thresholds and policy rules locally; network only required for authorized updates/synchronization and outbound notifications. Queue signed/hashed event metadata during outages; bound local retention.

## Whitelist / blacklist semantics: make policies explicit, not a shortcut

Historical discussion raised local 1:N whitelist and blacklist use; exact policy detail and legal basis are **not yet validated as previously frozen design**. Proposed safe contract:

- `ALLOWLIST`: persons enrolled for a consented and documented local authorization workflow, checked against a frozen threshold and authorization validity window. A match alone is not an unconditional "admit".
- `DENYLIST` / `WATCHLIST`: exceptional *explicitly authorized* review scenario, not an implicit negative identity claim. Candidate alert requires predeclared score and 1:N FPIR budget, documented purpose, human confirmation where consequential, rollback/revocation and conservative handling of ambiguous results.
- `UNKNOWN`: no sufficiently confident match or inadequate capture; never automatically classified as denylisted because a candidate was returned.
- `NO_DECISION`: poor quality, PAD failure, sensor outage, stale gallery/config or model health issue; fail safe and request an approved alternative process.
- Policy membership may vary independently of embedding records. Manage changes via signed updates, atomic activation, version ID and audit trail.
- For consented prototype pilots, first simulate policy labels with synthetic records and avoid any deployment in public or decision about real people without a separately approved legal/privacy and validation review.

1:N false positive identification probability increases as a function of gallery composition/size and similarity score distributions. Face 1:1 FMR/FNMR **cannot** be substituted for 1:N FPIR/FNIR; predeclare operating thresholds, demographic/domain shifts, misidentification response and operator burden.

## Hardware split: start with SoM + carrier

**Compute / AI board (replaceable):** start from an available RK3588-class development board or SoM with accessible vendor documentation. Choose only after a small real inference test: AdaFace or selected backbone, fixed capture pipeline, 100k/500k/1M ANN load, NPU availability, p50/p95/p99 latency and sustained temperature. 6 TOPS marketing figures are not evidence of end-to-end performance.

**Carrier / auxiliary PCB:** power-path, PoE PD/DC conversion, dual approved smart-pack connections for hot-swap (only after specialist design), secure element, always-on MCU, wake/motion sensors, temperature + humidity + tamper, shunt monitors, NIR driver and interlocks, exposed test points and service connectors. Start with COTS breakouts and a small sensor-measurement PCB, not a custom high-speed DDR/MIPI/PCIe board. Camera flex, thermal/mechanical envelopes and RF antenna isolation must be verified.

**Protected hot-swap:** ensure continuity under worst-case burst load and swap event; use redundant approved BMS packs or commercial hot-swap/holdup subsystem. Qualify brownout, charger, backfeed, removal lockout, battery temperatures and cutoffs. A rough 20 Wh pack is a lab buffer only; at 8 W/12 W/18 W continuous power it implies nominal ~2.5h/1.67h/1.11h *before* conversion losses and usable energy derating, not 5 days.

**External metrology:** independently measure supply boundaries, energy, wake peaks, SoC/battery/heatsink/window/enclosure temperatures, fan/fanless state. Compare MCU probe readings against external reference; do not use internal telemetry alone to establish power claims. Probe wiring and acquisition are a schematic-level requirement, not just a sensor BOM line. See `PROBE_INTERFACE_AND_TELEMETRY_SPEC.md` and `PROBE_INTERFACE_MATRIX.csv`.

## Secure low-power communications

Gigabit Ethernet with measured PoE(+)/PoE++ budget for fixed use. On battery, Wi-Fi primary / optional 5G fallback and store-and-forward. **PoE power is not PPPoE.** A tiny Ethernet physical connector is mechanically different from Single-Pair Ethernet (10BASE-T1L); decide any optional SPE/PoDL sensor interface from actual cable lengths. Critical distinction: fully sleeping SoC + radio cannot be continuously remotely reachable without separate powered wake/management hardware or a schedule. Select between (a) MCU local accumulation, (b) periodic authenticated uploads, (c) always-reachable service and measure idle energy penalty.

Device identity, mTLS, access control, rollback-safe signed OTA for SoC and MCU, per-sensor calibration/version, tamper events, logs separated from image data. Align traces on all `wake -> capture -> detect -> align -> extract -> project -> 1:N lookup -> policy -> alert` transitions using local monotonic clock and stable trace/span IDs. Do **not** place an LLM on inference or decision critical path.

## Modularity and independent revision artifacts

- `device_contract.yaml`: requirements, modes, power budgets (TBD until measured), fixed interface decisions.
- `models/*.json`: model version, preprocessing, signature, library checksums and permitted execution operator list.
- `gallery/manifest.json`: encrypted gallery schema version, snapshot and index version, enrollment/revocation rule; **no facial templates checked into Git**.
- `pcb/*`: KiCad native project, ERC/DRC outputs, STEP board, Gerber/Excellon/CPL where applicable.
- `cad/*`: native parametric source, fabricated enclosure STEP/STL only after dimensions verified.
- `bom/*`: MPN, supplier, source data sheet, quantity, variant, price as-of date, revision, availability.
- `evidence/*`: independent calibrated power/thermal data, test manifests, build logs, decisions with STOP/PIVOT/PERSEVERE.

## Milestones

**D0** freeze candidate hardware module and capture interfaces, evaluate model deployment feasibility on board with synthetic vectors. **D1** MCU+external instrumentation breadboard. **D2** synthetic 1:N index performance and energy-vs-dimensionality comparison. **D3** carrier schematic and mechanical part freeze; layout ERC/DRC. **D4** 3D fit check, first assembly, thermal/PoE/hotswap experiments. **D5** separately approved consented biometric performance and operational comparison; otherwise STOP/PIVOT.

## Technical boundaries (no overclaim)

No verified AI runtime, output distributions, biometric model license, 1:N real error rates, PCB routing, fabricated enclosure, power budget, hot-swap electronics or production-grade secure OTA has been qualified. The external laboratory and design tools must be used to establish these facts.
