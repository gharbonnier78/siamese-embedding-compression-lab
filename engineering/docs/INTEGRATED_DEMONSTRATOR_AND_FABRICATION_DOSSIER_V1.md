# SIAMESE EMBEDDED — Integrated Engineering, Simulation & Fabrication Dossier
### V1 / 20 November 2026 / Design-controlled working baseline — not a manufactured product

**Source of truth:** this file complements (does not replace) [engineering/README.md](../README.md), [ARCHITECTURE.md](../ARCHITECTURE.md), [the inherited engineering study](../../hardware/README.md), [the six-option business analysis](../../business/ACTIVITY_SYSTEM_EX_ANTE_EXPLORATION_V0.md), [the scientific research program](../../RESEARCH_PROGRAM.md), and [the test/evidence matrix](SYSTEM_REQUIREMENTS_TEST_EVIDENCE_V1.csv). The separate ESSEC business dossier v3 remains unchanged in its conclusions; its future v4 adds the technical annex. Technical statements below are either current committed code, explicitly proposed specifications or external validation work to be done.

> **Executive position.** Present a beautiful and credible fixed-site security-adjacent edge research appliance through **three openly compared mechanical variants, one accessible P1 laboratory rig, a simulated PC supervisor, encrypted evidence, 512D/128D image-pixel experiments, and a clearly gated pathway to a real KiCad PCB**. Do not claim that a render is manufacturable, that RGB-like/NIR-like synthetic patterns validate real cameras, that a DCT descriptor is a trained facial recognizer, or that a private event organizer can use a generalized 1:N biometric watchlist.

## 1 — Executive deliverables and readiness

| End-to-end deliverable | Existing, functional or planned | Claim and gap |
| --- | --- | --- |
| P1 bench electronic architecture | **Documented** COTS BOM shortlist and interface matrix | Camera compatibility, power and cables need purchasing/measurement |
| MCAD ultra-thin head / three concepts | **Editable OpenSCAD P0**: Hull, Book, Cassette | No true fitted vendor STEP, FreeCAD assembly or verified sealing |
| KiCad PCB | **Board-outline placeholder** and real probe interface CSV | NO full schematic, routes, footprints, ERC/DRC or Gerbers; fabrication prohibited |
| Always-on MCU behavior | **C11 host test** for wake, queue, fault, NIR inhibit state | No board port, sensor drivers or safety-certified hardware |
| S0 digital twin: decisions / probes / PC | **Executable** Python synthetic scenes and loopback supervisor | Probes and policies are fake; HTTP loopback is not secure Ethernet |
| S0+ pixel demonstrator | **Executable** synthetic RGB-like/NIR-like PNG → 512D DCT → exact cosine → random128 | Not face AI, real NIR, measured energy or biometric accuracy |
| Real paired EO RGB / NIR model replay | **Specified** image contracts and external datastore architecture | Real images, ONNX/RKNN trained model adapter and consent permissions not delivered |
| Signed administration package and policy | **Demo** Ed25519 manifests / atomic active pointer | No device attestation, production RBAC/OTA/antirollback |
| Evidence encryption and backup | **Demo** AES-GCM local vault, signed manifest and restore | Not enterprise KMS/RBAC/retention/legal custody |
| Automated tests and artifacts | **CI configured** for synthetic Python, host MCU C, conceptual STL and BOM HOLD | CI runs require verification; no HIL/weather/IP/security qualification |
| Release pack / BOM | **P1 candidate SKU sheet** and procurement stages | Prices/stock, electrical components, production mBOM missing |

**Not merged/released:** work is conducted in draft GitHub PR #56 on branch \`engineering/edge-appliance-reference-stack-v0\`, based on design PR #52, neither a signed product baseline nor fabrication authorization.

## 2 — Exact mission and systems separation

Fixed temporary wall/pole/truss-mounted EO/RGB + near-IR unit at an approved event site. Illustrative stress: 1,000 passage encounters/h × 10h/day × 5 days (50,000 encounters); *encounters are NOT 50,000 RF alerts*. The device remains fixed while people move through the calibrated optical field. A tripod is for lab calibration, not the deployment product.

Four systems must remain separate:

1. **FIELD APPLIANCE** — RGB+NIR optics and protected illumination, low-power PIR wake, one active signed feature extractor/projection/index/policy, local encrypted gallery if specifically authorized, exact/ANN retrieval, always-on MCU, thermals, power and tamper probes, autonomously queued event metadata. PoE/DC preferred, qualified backup optional; model execution and every consequential action under explicit authorization and human responsibility.
2. **ORGANIZER SECURITY RECEIVER** — dedicated low-power alert-radio option and private gateway, short pseudonymous event with ACK; existing authenticated Ethernet/Wi-Fi alternative may be evaluated. An RF receipt is not a human confirmation. No face image, embedding, candidate identity or person score on the radio.
3. **EXTERNAL SCIENTIFIC / ADMIN PC** — separate laboratory workstation and independent power/temperature instruments; signed model management, simulation, controlled image-pair acquisition when authorized, immutable study datasets, replay, comparison, dashboard and decision records. The appliance is operational without it.
4. **SOURCE/FAB CHAIN** — OpenSCAD + FreeCAD/Build123d STEP, KiCad and ngspice, C MCU, Python AI/replay, GitHub Actions and evidence manifests. No LLM on an embedded decision critical path; use LLMs only to help upstream draft, not to establish results.

\`\`\`mermaid
flowchart LR
    SCN["P1 generated scenes / approved EO RGB+NIR dataset"] --> ACQ["Versioned acquisition, time sync, quality"]
    ACQ --> EXT["Chosen 512D extractor"]
    EXT --> PROJ{"One active projection"}
    PROJ -->|Raw 512D| IDX["Compatible exact / ANN index"]
    PROJ -->|PCA128, random128 or trained Siamese128| IDX
    IDX --> POLICY["Versioned policy / unknown / no-decision"]
    POLICY --> QUEUE["Durable operational events"]
    QUEUE --> LINK["Authenticated Ethernet / sparse alert radio"]
    LINK --> OPS["Authorized security dispatcher, human ACK"]
    MCU["Always-on MCU: PIR, thermals, V/I, RH, tamper, battery"] --> QUEUE
    MCU --> EXT
    PC["Separate PC: administration, replay, independent instruments"] -. "optional, never required at runtime" .-> ACQ
    PC --> VAULT["Restricted encrypted research evidence"]
\`\`\`

In today's S0 simulation, acquisition events and radio statuses are fake. This diagram is a proposed production separation, not a deployed secure network.

## 3 — Mechanical design portfolio, not a single arbitrary box

All three A-v2 styles share the *aspirational* 100 mm (W) × 150 mm (H) × 30 mm (D) head (0.45 L outer bounding box). A fourth comparator is the earlier horizontal camera-like design with visor; the P1 test fixture is independent. The installed system is larger if bracket, cable gland, antenna or battery dock extends beyond the head.

- **A — Hull:** visually uninterrupted rounded rear shell with removable front. Candidate for the fewest sealing interfaces and simple passive rear heat spreader, but service access may require opening the whole head.
- **B — Book:** hinged side access, easiest in concept for servicing breakouts, but complex moving seals/latches and hinge clearance.
- **C — Cassette:** separate repeatable optical cassette/window while electronics compartment stays closed; potentially attractive for window replacement and optics upgrades, at the price of extra seals and a critical alignment datum.
- **D — Horizontal comparator:** short visor, larger optomechanical volume and aiming bracket; potentially easier lens/thermal packaging, not necessarily more discreet.

**Source:** [concept_variants.scad](../mechanical/concept_variants.scad) and [variant comparison](../mechanical/VARIANT_COMPARISON.md), with earlier [enclosure.scad](../mechanical/enclosure.scad). Geometry is illustrative; never quote an IP rating from a picture.

**Material/design candidates (not selected):** CNC aluminium 6061-T6 rear conduction path, corrosion-compatible coating, PC/ABS or aluminium front, RF-transmissive antenna insert, selectable visible/NIR-transmitting glass windows, silicone/EPDM replaceable gasket, thermal interface pads with verified compression; vent membrane for pressure equalization if needed. No penetrative "ventilation slots" through protected electronics.

**Critical interference and qualification questions:** lens protrusion, light baffles, camera field overlap and synch, CSI/USB connector backshell/cable bend radius, SoM NPU sustained heat under solar soak, NIR illumination/eye safety, RF antenna detuning, ingress/condensation, PoE cable strain, backup dock total installed volume. No custom tooling before actual vendor STEP bodies and P0 dry-fit.

### MCAD test plan

1. Export identical hull/book/cassette STL studies automatically and review front/side/3/4, consistent scale.
2. Reconstruct **vendor-specific** bodies and materials in FreeCAD/Build123d, preserve native editable source, export STEP; do not invent part-specific geometry.
3. Compute interferences at mechanical tolerance extremes and wall-bracket angle limits, then dry-fit P1 fixture.
4. Compare shape attractiveness, maintenance, environmental seals, optical field and total installed volume before design freeze.

## 4 — Electrical architecture and pragmatic procurement

**Compute:** a Radxa ROCK 5B development board is useful for P1 *bench* only; RK3588 NPU marketing TOPS do not demonstrate support for our exact extractor model. Its size (~100×75 mm) must not dictate the final head. A Radxa CM5-class SoM is a compact A-v2 candidate after CPU/NPU compatibility and thermal testing. A separate full GPU or FPGA is **not** assumed necessary; the earlier mention of FPGA was a misunderstanding of **Flux.ai**. We are now pursuing free/open CAD and PCB workflows.

**P1A order candidates:** ROCK 5B (8 or 16GB variant after 1m vector RAM experiment), approved PD supply/heatsink/storage, first Arducam OV9782 UVC RGB camera B0385, Raspberry Pi Pico 2, two INA228 I2C breakout modules Adafruit 5832, SHT45 temperature/RH Adafruit 5665, cables/CAT6 and a borrowed/rented calibrated DC meter. **P1B** adds Arducam B0332 OV9281 monochrome camera, Panasonic PaPIRs sensor, and possibly EU868 RAK3172 LoRa evaluation hardware/gateway after RF scoping. NIR emitter/driver, 5G, hot-swap battery hardware, weatherproofed enclosure and all custom PCBs are DEFERRED until individual requirements and safe designs are reviewed.

**eBOM:** [P1 candidate procurement list](../bom/P1_PROCUREMENT_CANDIDATES_2026-11-20.csv) and [minimal order decision](../bom/P1_MINIMAL_PURCHASE_GUIDE.md). Prices, inventory, compatibility and manufacturer revision are *not* frozen; no instructions to blindly order battery cells or an NIR illuminator.

**Prototype PCB:** only a small low-voltage MCU/probe carrier is justified after pinouts. The present [KiCad placeholder](../electronics/kicad/README.md) is an empty board outline — not a legitimate schematic and NOT acceptable to JLCPCB/PCBWay/other vendors. Full KiCad work shall cover MCU, I2C/ADC/RTC/FRAM, shunt placement, temperature/RH/tamper/PIR, UART/SPI radio integration, safe I/O voltage domains and connectors. Qualified commercial PoE PD / DC converter / smart battery backup remain independent modules at first. No custom high-speed DDR/MIPI/PCIe and no prototype Li-ion charge circuits.

**Required PCB release:** chosen MPN + datasheet revision, schematic+netlist, KiCad ERC, routed board+footprints+DRC, power integrity/return path/ESD/EMC review, reviewed safe power switching and NIR hardware interlock, independent qualified EE sign-off, PCB STEP fit, reviewed BOM substitutions, Gerber/drill/CPL assembly pack, first-article and EOL tests. **FAB-01 remains HARD STOP.**

## 5 — Firmware and Linux edge work packages

- **Always-on MCU:** PIR/tamper interrupt, real RTC/sequence counters, shunt/temperature/RH sampling, power-domain wake/sleep, NIR hardware enable interlock, watchdog, persistent ring buffer, radio TX and delivery state, version reports, secure MCU updates.
- **Current C host prototype:** [mcu_supervisor.c](../firmware/mcu_supervisor.c) tests wake/sleep, fail-safe software interlock, queue overflow and power-fault states. No verified protective hardware or actual electrical sensor driver exists.
- **Linux SoM:** independent secure boot/update, camera device interface, timestamps, quality/PAD checks, pinned extractor model and projection package, encrypted compatible gallery/index, lookup/policy engine, signed local configuration, health and instrumented trace IDs. A/B OS OTA, antirollback and secure element integration are NOT implemented.
- **One configuration active per device:** \`extractor_hash, preprocess_hash, projection_id/dimension, gallery_snapshot_id, thresholds, policies, firmware/driver\`; a gallery built from one projection cannot be silently reused with another. The external PC may sequentially replay many model variants from a frozen approved dataset.
- **No real-world automated blacklist action:** policy mock uses \`ALLOWLIST_CANDIDATE\`, \`REVIEW_REQUIRED\`, \`UNKNOWN\`, \`NO_DECISION\` on lab-generated IDs only. Production purpose and authorization are separate hard gates.

## 6 — Three levels of simulation and physical evidence

| Level | Input and code | Meaningful deliverables | DOES NOT establish |
| --- | --- | --- | --- |
| **S0 control** | seeded scene descriptors, synthetic gallery and fake probe values: [digital_twin.py](../sim/digital_twin.py) | state machine, 512/128 comparison shape, fake policies, fake offline queue, loopback console | EO/NIR image quality, real matching, watts, RF or safe operations |
| **S0+ pixel** | generated abstract RGB-like/NIR-like PNG files and DCT 512D, optional projection: [pixel_replay.py](../sim/pixel_replay.py) | actual image I/O, hashes, cosine exact search, same-acquisition 512D vs random128, HTML/CSV/JSON | real human-face biometric embeddings, true IR optics, accurate FPIR/FNIR |
| **S1 approved real replay** | **NOT IMPLEMENTED** secure paired RGB/NIR captures plus vetted trained 512D extractor/128D projections | cross-modal domain shift and quality vs algorithm baselines on fixed pixels | actual sensor acquisition changes, field/optical physics, real hardware energy |
| **S2 HIL / physical** | approved cameras+SoM+MCU+RF+external calibrated meter, real controlled setup | time, power, heat, light sensitivity, RF and installation metrics | market demand or permission to conduct 1:N in public |

### 6.1 Pixel demonstrator that can be presented NOW

\`\`\`bash
python -m pip install -r engineering/requirements.txt
python engineering/sim/pixel_replay.py --out /tmp/siamese-pixel-demo
# Open the generated offline_replay_report.html on the same PC.
# Inspect image_comparison.csv / .json and synthetic_fixture_images/*.png.
python -m unittest discover -s engineering/sim/tests -v
\`\`\`

The generator makes actual files containing **abstract non-human geometric motifs** in RGB and NIR-like contrast, not real people and not genuine NIR. The image arrays are decoded into 64×64 grayscale, whitened within the image, transformed with DCT-II; the first 512 prescribed non-DC low-frequency coefficients are L2 normalized. The same 512D vector is matched by exact cosine to the synthetic enrolled RGB gallery, then transformed by a fixed seeded 512×128 orthogonal matrix and searched again. This demonstrates a matching *program*, **not biometric identity recognition**.

Why this distinction matters: a visual demo with artificial pattern matches is useful to debug dimensions, signatures, gallery compatibility, trace IDs and UI; even very high toy accuracy is completely irrelevant to real-world false identification rates. PCA128 and real Siamese128 require frozen TRAIN-only projections with provenance. A nonlinear Siamese embedding cannot simply be substituted by a linear weight matrix; a genuine model runner needs a separate adapter.

### 6.2 Real EO/NIR image work planned, not assumed

The offline \`ImagePairReader\` needs legally obtained **paired** acquisitions under the same physical scene and time alignment: camera/lens/sensor ids; RGB and genuinely NIR raw imagery, light source, shutter/exposure, distance, image pose/yaw/pitch/roll, occlusion and motion, illumination, moisture/temperature, synchronization offset, annotated quality and protected ground-truth status. No cloud distribution, no re-hosting datasets or enrollment imagery, no real passenger capture default.

Real model pipeline:
\`\`\`text
Approved encrypted pairs + signed data purpose and split manifest
 -> decode & timestamp checks -> model-defined alignment/normalization
 -> frozen trained 512D extractor with modality qualification
 -> RAW512 | PCA128 | RANDOM128 | Siamese128 trained checkpoint
 -> compatible exact / ANN gallery, frozen threshold and no-decision gate
 -> score/uncertainty + trace/span + version hashes, offline decision review
\`\`\`

Use ONNX Runtime or target-compatible NPU runtime only after profiling operator compatibility and calibration. Need modality-specific validation: merely converting visible RGB to gray is NOT NIR. A model trained for RGB must not be asserted cross-modal for NIR.

S1 design source: [image-pair replay plan](../sim/IMAGE_PAIR_REPLAY_PLAN.md) and [pixel adapter note](../sim/PIXEL_REPLAY_AND_MODEL_ADAPTERS.md). **Protected Study 1B SCREEN/TEST remain sealed; never alter thresholds after seeing TEST data.** Real 1:N search accuracy requires FPIR/FNIR, confidence intervals and sufficient impostor/nonmate counts for intended gallery sizes. No statistical accuracy statement from synthetic images.

### 6.3 Memory and scalability

Raw vector storage size only (float32, excluding index/OS/model):
- 100,000 × 512 × 4B ≈ **204.8 MB**; ×128 = **51.2 MB**
- 500,000 × 512 × 4B ≈ **1,024 MB**; ×128 = **256 MB**
- 1,000,000 × 512 × 4B ≈ **2,048 MB**; ×128 = **512 MB**

This is a 4× reduction in raw vector bytes, **NOT automatically a 4× product energy or search-latency gain**. Exact CPU+SIMD vs indexed ANN, indexing overhead, preprocessing/extractor and power are benchmark factors. Use identical gallery, fixed seeds and profiles. Gate proposal: search energy reduction ≥20%, **full energy/accepted event** reduction ≥10% and all independent accuracy thresholds met, otherwise stop compression route; these values are *targets to challenge*, not achieved results.

## 7 — Live-style PC supervisor and simulated Ethernet/radio

Today \`console.py\` binds to **127.0.0.1** with a temporary token and gets sanitized JSON from the simulated fixed node. It displays model dimension, Ethernet UP/DOWN, RF UP/DOWN, synthetic temperatures and power, radio receipt ACK and separate human ACK. This exercises HTTP/loopback behavior, **not authenticated network equipment management**. \`digital_twin.py\` simulates queue states while disconnected; full durable reconciliation/retry and real LoRa gateway are future.

Next: on a physically isolated LAN build a documented device inventory and command API:
- \`GET /devices/{id}/health\`, versions, last seen, active profile, calibration and radio status.
- \`POST /packages/stage\`, verify Ed25519 signature + version compatibility + index/policy schema, \`POST /devices/{id}/activate\` atomically with rollback.
- \`POST /studies/{id}/execute\` for lab-only simulation; \`GET /studies/{id}/evidence\`, RBAC and purpose checks.
- \`POST /alerts/{id}/acknowledge\` by authorized on-duty user; distinguish network ACK, queue delivery, human ACK and response decision.
- mTLS, strong identity, least privilege, signed audit, disconnected replay/recovery, abuse/rate controls; ALL unimplemented until verified.

The **security operator console** does not become a research image vault.

## 8 — Evidence, storage, data governance

Four retention zones:
1. **Operational field**: minimal health/config audit and a bounded encrypted event queue; one approved active gallery/policy as needed. Never store raw captures by default.
2. **Authorized acquisition**: separate lab collection with legal purpose, independent approval, exposure controls and per-sample permission. Real RGB/NIR images remain physically outside public Git.
3. **Research evidence vault**: calibrated measurements, immutable run hashes, trace/span parent relations, model/gallery/projection configs and optional restricted images, per-purpose ciphertext, KMS/separate encrypted backup, revocable access, scheduled expiry, full restore drills.
4. **Public repository**: schemas, generated **non-human** fixtures, mock configurations, procedures, anonymous test results and code. No real lists, templates, faces, model proprietary weights or secrets.

The current [vault.py](../sim/vault.py), [backup.py](../sim/backup.py) and [admin/package_manager.py](../admin/package_manager.py) demonstrate AES-GCM encryption, signed backup integrity and a signed active pointer. They are **not** full backup/KMS/RBAC solutions. Before any regulated study, require DPIA/legal basis, storage threat model, keyed retention, immutable data access audit, restored ciphertext on another authorized workstation and signed independent acceptance.

**Evidence contract:** \`AS_ID → OPTION_ID → HYPOTHESIS_ID → EXPERIMENT_ID → BR_ID → CAP_ID → FEATURE_ID → UC_ID → RUN_ID → DEVICE_PROFILE → MODEL_HASH → GALLERY_HASH → INPUT_HASH → CONFIG_HASH → CALIBRATION_ID → TRACE/SPAN → RAW_METER_SHA → RESULT_WITH_CI → REVIEWER_DECISION\`.

## 9 — Acceptance matrix, stage gates and scientific honesty

The **26-item** matrix [SYSTEM_REQUIREMENTS_TEST_EVIDENCE_V1.csv](SYSTEM_REQUIREMENTS_TEST_EVIDENCE_V1.csv) links business/system requirements to capabilities, features, use cases, test artifacts, preliminary numeric thresholds, maturity and authorization gates. Entries explicitly say \`SIMULATED\`, \`EXECUTABLE_SYNTHETIC\`, \`NOT_MEASURED\`, \`NOT_IMPLEMENTED\` or \`HARD STOP\`.

Selected *prospective* targets, only frozen with owner before trial:
- **Functional/autonomy:** 8h without PC/WAN and zero unexplained event loss; distinguish missing Ethernet data from missing PoE power.
- **Radio operations:** ≥99% short-event delivery to the authorized console within 10s in a specified RF condition, 100% missed messages shown as undelivered; no human action inferred from a network ACK.
- **Installation:** ≤30min at 3 approved mock sites by trained 2-person crew with all mandatory safety checks passed.
- **Image/replay:** all hashes and input pairing verified, 512D/128D dimensions consistent, fixed-seed output reproducible; real modality quality and FPIR/FNIR not claimed.
- **Synthetic index:** 1m vectors without OOM, proposed ANN recall ≥99.5% compared to exact top-1 and proposed p95 lookup ≤150ms in declared hardware config.
- **Thermal/power:** independent calibrated external J/event and worst-case thermal envelope without any exceeded selected manufacturer rating.
- **Business:** ≥2 written design partners, ≥1 funded pilot/benchmark and positive event contribution in ≥2 genuine priced event trials — separate from successful hardware.

Not every draft threshold is appropriate for every option; pre-register by cohort/site/mission. An illegal application is a **hard STOP**, not a weighted score compensated by good accuracy.

## 10 — Test campaign and demo script for stakeholders

**D0 (today; no hardware, 15-min guided demonstration):**
1. Open the three concept variants at same scale (Hull, Book, Cassette); show why P1 rig remains separate.
2. Run \`python engineering/sim/pixel_replay.py --out /tmp/demo\`; show the *generated non-human image pairs* and 512D vs random128 identical-acquisition comparison in the local HTML report.
3. Run \`python engineering/sim/digital_twin.py --dim 128 --out /tmp/twin\` and \`--dim 512\`; show policy-state simulations and sensor value flags.
4. Start the loopback PC console, post synthetic telemetry, inject \`--ethernet-down --rf-down\`, show QUEUED_OFFLINE / RF QUEUED and pending human ACK.
5. Demonstrate the demo signing/manifest corruption test, encrypted vault backup and synthetic restore; do not demonstrate with real lists/keys.
6. Open [KiCad PLACEHOLDER](../electronics/kicad/README.md) and [BOM](../bom/P1_PROCUREMENT_CANDIDATES_2026-11-20.csv); explain G1–G5 and explicit NO FAB.
7. Finish with proposed independent test proof and **stop/pivot criteria**, not unsupported efficiency/security claims.

**D1 (after P1 COTS assembly):** controlled RGB camera output and first device power meter; separate NIR trial after optical and model compatibility. Operator demo stays synthetic.
**D2 (after G1 & lawful approval):** paired EO/NIR real controlled captures replayed offline on frozen versions, no public default retention. Measure source/image metadata and domain shift.
**D3 (after G3):** fully integrated fixed head and simulated security operator plus physically qualified thermal, ingress, radio and backup.

### Demo evidence bundle structure

\`\`\`text
run-<id>/
  run_manifest.json               # source SHA, model/projection, purpose, profiles, consent class
  image_comparison.csv            # synthetic today; restricted elsewhere for real data
  image_comparison.json
  offline_replay_report.html      # non-human synthetic only public
  synthetic_digital_twin.json
  synthetic_probes.csv
  telemetry.ndjson                # future OTEL trace/span alignment
  source-and-calibration.json     # no fake instruments
  acceptance_verdict.json         # PASS/FAIL/BLOCKED, reviewer/date
  secure_vault/                   # NOT GIT for approved protected records
\`\`\`

Each run must explicitly distinguish **proposed target**, **simulation**, **instrument measurement**, **inference from observations**, **independent verified claim**. No fabricated measured values.

## 11 — Reusable open-source fabrication/toolchain delivery

- **MCAD:** OpenSCAD P0 source → FreeCAD/Build123d native solid-model STEP and reviewed section/tolerances → 3D printing/CNC P1/P2 → DFM and first-article drawing. Models must not be imported from 3D pictures as if dimensionally accurate.
- **ECAD:** KiCad native \`.kicad_sch\`, \`.kicad_pcb\`, footprints and 3D STEP, electrical review/ERC/DRC/netlist/PoE or low-voltage ngspice; signed design freeze → *only then* Gerber/Excellon/CPL and fab release. Current PCB has just a blank outline.
- **Firmware:** portable C11 MCU state machine → selected MCU HAL/drivers → hardware-in-loop, signed update and safe interlock evidence; embedded model runtimes as independent pinned artifacts.
- **PC / ML:** Python packages, local synthetic fixtures and provenance, tests/CI; real experimental files encrypted offline; ONNX Runtime is a possible execution adapter, not the chosen trained model.
- **GitHub:** code/docs/eBOM/schematics; protected rules, reviewers, release manifest; CI must not upload sensitive data. PR #56 is engineering draft.
- **Supply chain:** vendor sourcing verified MPN/date/stock and alternates, materials and assembly drawings, DFT points, firmware provisioning/calibration, unit identity, test log and recall/rework instructions. Reproducible source ≠ manufacturability.

### CI/CD gates and release discipline

Existing workflow [edge-appliance-engineering.yml](../../.github/workflows/edge-appliance-engineering.yml) checks Python syntax, synthetic tests, control-flow twin, image demo, C host MCU, OpenSCAD concept geometry and BOM HOLD. CI uploads only synthetic short-retention artifacts. **No auto-generated Gerber in current CI**, no product firmware deploy or automatic clinical/biometric quality claim.

Future guarded jobs:
- \`lint\` code, schemas, source licenses and no-secrets checks;
- \`simulation\` deterministic seeds and regression baselines, checked manifest hashes;
- \`ecad-erc-drc\` after real schematic/PCB with reviewed KiCad CLI;
- \`mcad-fit\` component STEP inspection + dimension/gasket/thermal checks with actual vendor parts;
- \`hil\` manual approved powered bench and external instrument sync;
- \`security\` signature/replay/provisioning and network authorization;
- \`release\` **requires manual multi-party signed gates** for firmware and fabrication, never auto-orders PCB.

## 12 — Prototype phases with real STOP/PIVOT checkpoints

| Phase | Demonstrable outcome | Cheapest build | Decision to advance |
| --- | --- | --- | --- |
| **P0 / now** | 3 design variants, requirement trace, S0 and S0+ Python demo, provisional BOM, operator workflow | GitHub + local PC + OpenSCAD | Clear value/risks, source repeatability and not misleading claims |
| **P1A / COTS** | ROCK 5B+camera, Pico 2+INA228/SHT45, mock bracket, external meter, local PC dashboard | One camera first, no custom PCB or battery | Can run actual selected model? Hardware synchronized paths and thermal feasible? |
| **P1B / options** | RGB+true NIR camera support, PIR, LoRa eval, full telemetry | Additional COTS only if P1A evidence supports | Modality sync and power tradeoff viable? |
| **P2 / design integration** | Selected Hull/Book/Cassette, complete measured STEP, small low-voltage KiCad PCB, verified model runtime | CNC/3D + reviewed commercial power | **G3 review before any PCB manufacture** |
| **P3 / environmental/field engineering** | qualified ingress/humidity/heat/illumination, backup, RF, independent energy | Tested assembled prototype | Do actual data/purpose and measured performance satisfy approved contract? |
| **P4 / preseries** | controlled manufacturing files, supplier first article and EOL/acceptance suite | Quote small series (e.g. 5–10) | Only approved G5 + lawful business model and procurement economics |

Do not schedule guaranteed dates or commit costs before availability, test venue, reviewer and suppliers are known. **No algorithm is worth implementing if a simpler, lawful non-biometric event workflow dominates the outcome.**

## 13 — Entrepreneurship / marketing / value connection

The device is a **hypothesis tester**, not a validated product business. The ESSEC-linked [activity-system ex ante study](../../business/ACTIVITY_SYSTEM_EX_ANTE_EXPLORATION_V0.md) and [six independent Canvases](../../business/SIX_BUSINESS_MODEL_CANVASES_V1.md) keep six distinct options:

| Opportunity | What this demonstrator can validate | What it cannot validate |
| --- | --- | --- |
| O1 non-identifying event signal device | technical alert and simple site workflow simulations; later operator triage | purchasing need, lawful purpose, actual net savings |
| O2 managed event service | sensor and staff workflow, uptime observability | willingness to pay and true service labor contribution |
| O3 voluntary 1:1 access | later approved UX and 1:1 technical performance | independent lawful consent, equal alternative and procurement |
| O4 OEM reference design license | replicable KiCad/CAD/firmware and COTS-vs-build integration | OEM paid design-in, IP freedom-to-operate |
| O5 independent edge benchmark | exact power/science/reproducibility package and reports; strongest immediate technical fit | buyer funding and business profitability |
| O6 narrow institutional research | secure research simulation and later authorized controlled 1:N method | statutory mandate, license to collect data or deploy at civilian events |

**Marketing claims** must say "prototype", "demonstrator", "synthetic", "measured by independent instrument", "site tested", or "independently approved" as applicable. No invented security incident reduction, face-recognition accuracy, IP66 or AI performance.

## 14 — Critical open questions to bring to electronics/materials laboratory

- Which ROCK SoM or external accelerator really runs *our frozen model* on 100k/500k/1m galleries under full thermal load; what memory/config drivers are actually supported?
- Can Arducam selected USB global-shutter boards share trustworthy synchronized RGB/NIR triggers? If not, which matched MIPI/industrial pair is appropriate? What is minimum face pixels at measured distances?
- What optical spectrum/window transmission and NIR emitter hardware eye-safety/thermal interlocks are required? Can low-power PIR wake avoid false triggers at 1,000 people/h?
- Can a sealed, 30-mm head dissipate measured SoM/NIR peak wattage in sunlight when mounted against a wall? Which minimum thickness or external dock trades are acceptable?
- Which enclosure material/gasket/vent and service pattern yields repeatable IP testing after maintenance and cleaning? What coating/tropicalization may complicate repair?
- Which commercial protected power/PoE and hot-swap approach provides bounded continuous operation without building unsafe battery electronics?
- Can the actual MCU/probe board be assembled with readily available connectors, accessible measurement test pads and no custom high-speed links?
- What specific COTS-to-PCB transition minimizes nonrecurring engineering, supplier risk and parts lead-time? What would a manufacturer demand for a 5–10 unit quotation?
- What independently calibrated meter/thermal/light/RF instruments and environmental chambers can the lab provide; what *exactly* is the contract of evidence?
- Which relevant work packages are in the lab's capability, and which require an external accredited/qualified test house?

## 15 — Decisions needed, ownership and next deliverables

**Decision D01:** approve P1 first purchase subset only after camera/ROCK driver compatibility, RAM and thermal/power paths are vetted.
**D02:** score A Hull/B Book/C Cassette plus horizontal comparator as alternatives; do not choose from one glossy render.
**D03:** approve a signed, controlled *non-identifying* demo as market discovery; keep biometric face 1:N completely gated.
**D04:** identify a model checkpoint whose license and RGB/NIR domain support are documented, otherwise continue the honest DCT512 control-flow lab.
**D05:** agree who owns evidence-vault KMS/data governance and live retention limitations.
**D06:** commission exact vendor STEP models and a low-voltage supervisor carrier only when COTS pinout and critical thermal feasibility become known.
**D07:** freeze test criteria before physical data and claim review.
**D08:** independent GO/CONDITIONAL GO/NO GO for P2 custom PCB and P3 environmental work, then separately for any manufacturing release.

## Provenance and links

Internal: [mission](../../hardware/FIXED_EVENT_INSTALLATION_MISSION.md), [full system architecture](../../hardware/EDGE_SYSTEM_ARCHITECTURE_V0.md), [probe requirements](../../hardware/PROBE_INTERFACE_AND_TELEMETRY_SPEC.md), [radio alerts](../../hardware/LOW_POWER_SECURITY_ALERT_RF_REQUIREMENTS.md), [staged environmental plan](../../hardware/STAGED_ENVIRONMENTAL_PROTOTYPING_AND_DFM_V0.md), [business evidence matrix](../../business/PHYSICAL_PROTOTYPE_HYPOTHESIS_EVIDENCE_V1.md), [release gates](../RELEASE_GATES.md), [lab questions](LAB_MATERIALS_AND_PROTOTYPE_QUESTIONS.md), [mechanics](../mechanical/VARIANT_COMPARISON.md), [simulator](../sim/README.md), [pixel replay](../sim/PIXEL_REPLAY_AND_MODEL_ADAPTERS.md).

External normative/reference material (for technical interpretation, *not evidence that we comply*):
- NIST FRTE 1:N, FPIR/FNIR benchmark methodology: https://pages.nist.gov/frvt/html/frvt1N.html
- ONNX Runtime Python: https://onnxruntime.ai/docs/get-started/with-python.html
- OpenCV DCT (algorithm reference): https://docs.opencv.org/4.11.0/d2/de8/group__core__array.html
- KiCad documentation: https://docs.kicad.org/
- FreeCAD: https://www.freecad.org/
- Build123d: https://build123d.readthedocs.io/
- Zott & Amit (2010) business model activity systems: https://doi.org/10.1016/j.lrp.2009.07.004

**This technical dossier is version controlled. It is not an audited product specification, test report or compliance certificate.**
