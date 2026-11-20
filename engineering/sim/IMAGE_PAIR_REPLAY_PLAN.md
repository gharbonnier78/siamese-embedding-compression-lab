# RGB + NIR image-pair replay — incremental implementation plan

**2026-11-20 · DESIGN/TEST CONTRACT.** A separate **non-human synthetic pixel demonstrator is now implemented**: `pixel_replay.py` generates RGB-like/NIR-like abstract patterns, reads PNG pixels, computes DCT512 and compares random128, outputting HTML/CSV/JSON. This is not the approved real-face EO/NIR replay defined by S1; that remains **unimplemented and unauthorized**.
The existing `digital_twin.py` demonstrates a control-flow simulation driven by **synthetic scene descriptors** and seeded vectors; it does not process actual images, model real optical physics or infer true biometric errors. The goal of this contract is to add a rigorously separated **offline consented acquisition replay adapter** without coupling field runtime to a PC.

## 1. Separate three types of simulation

- **S0 (already available): simulated people and measurements.** Fixed scene descriptors (yaw, RGB or NIR, lux, blur, occlusion, ambient temperature); synthetic normalized 128/512D vectors; fake allow/watch/unknown/no-decision cases; simulated readings; localhost HTTP telemetry to PC; radio ACK mocked. Supports deterministic integration, dashboard and fault tests, NOT recognition claims.
- **S1 (next): real recorded RGB/NIR image-pair replay.** Authorized, license-checked scenes held **only outside Git**, encrypted in an offline evidence store, with explicit participant/dataset conditions; the *same immutable capture* feeds sequential versions of a validated extractor and projection path. Qualifies differences of model output conditional on the fixed recorded pixels, not weatherproofing, camera sensitivity or current device energy.
- **S2 (later): physical hardware-in-loop.** Actual cameras/NIR, PIR, chosen SoM/NPU, external calibrated instruments, low-power MCU/RF and PoE/DC/backup. Tests optomechanical effects, environmental degradation, actual energy, thermal, timing, hot swap and radio coverage.

## 2. Proposed capture manifest contract for S1 — no personal images in Git

An offline capture set must supply a versioned manifest with:
- `capture_id` and source record cryptographic hash; **pseudonymous** session and approved-purpose ID.
- `visible_rgb_uri` / `nir_uri` as secure local vault references, not exposed filenames or Git URLs; `rgb_sha256` and `nir_sha256`.
- `sync_delta_ms` measured or explicitly unknown; capture timestamp and camera/driver/lens/illumination provenance.
- `pose_yaw_deg`, `pose_pitch_deg`, `pose_roll_deg` estimated/annotated with method and confidence, not automatically "ground truth".
- `subject_motion`, `motion_blur_estimate`, `occlusion_fraction`, `inter_subject_distance_m` if actually measured, `face_pixels` as derived from camera geometry.
- `illumination_lux`, `sun_backlight`, `rain_window_condition`, `ambient_c`, `relative_humidity_pct`, `mode` (RGB/NIR/both) and data gaps.
- Consent/license identifier, controller, permitted use, custody, access grant, retention expiry and deletion policy. No derived identity labels exported into ordinary telemetry.

**Example synthetic labels only**, to be generated without actual personal imagery:
`scene-001-front-day`, `scene-002-oblique-day`, `scene-003-night-nir`, `scene-004-occluded`, `scene-005-backlit`, `scene-006-wet-window`, `scene-007-empty-frame`.

## 3. Proposed S1 processing path

```text
Signed study manifest and legal/data gate
      |
Authorized offline encrypted capture vault (RGB and NIR)
      |
Immutable ImagePairReader -> sync/quality assessment -> preprocess version
      |
Extractor plug-in (ONLY selected validated model) -> 512D base embedding
      |
Frozen projection plug-in (none / PCA128 / Siamese128) -> 512D or 128D
      |
Exact reference index and optional ANN on SAME compatible gallery revision
      |
Score + independently frozen threshold (study gate) -> candidate/unknown/no-decision
      |
Separate synthetic policy labels for safe UI tests (no real blacklist)
      |
Trace/span, decision reason, version hashes, latency, resource use
      |
Separated PC research review UI, not organizer operator interface
```

A projection to 128D is **not** a different extractor automatically; compare exactly matched backbone/preprocessing and enforce model/projection compatibility for the gallery. Use one active package at a time on the simulated device, with offline sequential comparisons on the analysis PC. Control threshold calibration on permitted VALIDATION only, never tune on independent TEST.

## 4. Functional tests and expected external PC displays

| Test ID | Injected condition / action | Expected simulated station result | What it does NOT prove |
|---|---|---|---|
| S0-01 | Front-lit RGB fake allowlisted label | ALLOWLIST_CANDIDATE, confidence proxy labeled synthetic | Real recognition |
| S0-02 | NIR night fake watchlisted label | REVIEW_REQUIRED and short radio event with no identity, human ACK PENDING | Lawful/watchlist match |
| S0-03 | Oblique/blurred/occluded synthetic scene | NO_DECISION + capture-quality diagnostic | Physical camera FTA |
| S0-04 | Unknown synthetic vector | UNKNOWN; not auto-blacklisted | Actual FPIR |
| S0-05 | Ethernet unplugged | Local processing continues, telemetry QUEUED_OFFLINE; eventual forwarding to be implemented | Reliable field buffering |
| S0-06 | RF outage | Radio short alert QUEUED; distinct human ACK, no leaked identifying data | RF link budget |
| S0-07 | 128D vs 512D on same synthetic seeds | Different versioned run output, preserved manifest and exact vector size | Compression preserves biometric accuracy |
| S0-08 | Change signed synthetic policy/model package | Reject modified signature; active pointer version recorded | Production hardware anti-rollback |
| S0-09 | Sensor fault/power mode synthetic | Simulated W, temperatures, SoC, last-good-sample and flag | Real energy/thermal safe operating area |
| S1-01 | Approved real paired RGB/NIR captures | Paired camera image quality and extractor scores, repeatable offline benchmark with declared uncertainties | Lawful live-event 1:N, physical thermal/power |
| S2-01 | Device fixed on event wall; safe lab stimuli | Independent calibrated J/op, sensor power, real hot-swap and thermal | Market demand, legal permission |

## 5. Administration and secure data design

- **External PC admin** controls versioned signed updates, allowed gallery snapshots and test schedules. Split `control_plane` (models, gallery, policy, firmware) from `experiment_plane` (immutable capture and raw evidence). Device continues if PC absent.
- Do not put real names, face images, templates, watchlists or signing keys into GitHub, Flux.ai, public GitHub Actions, generic MQTT metrics, or radio events.
- Keep live-event default to no image retention. An explicit authorized research mode may securely acquire and upload selected recordings to an isolated private vault, not to the organizer security console.
- Transport for the *simulation* uses HTTP over localhost in `console.py` with a throwaway token, **not actual Ethernet or authenticated production management**. Next integration is optional isolated test LAN with mTLS, server-side RBAC, audit and replay prevention, all independent of event operations.
- Retain raw evidence only per purpose, encryption, signed manifest/attestation, restore rehearsal and configured deletion schedule. The existing AES-GCM `vault.py` illustrates encryption but does not implement an enterprise secure evidence platform.

## 6. Next measurable deliverables

**P1 software:** `ImagePairReader` interface with synthetic fixtures and controlled local file reader restricted to a separate authorized storage root; documented capture manifest schema + validation; plug-in API for extractor and projection with hashes; offline multiple-model replay ledger. No AI model weights, persons or proprietary images checked in.

**P2 system integration:** choose SoM camera/connector revisions, camera sync, radio receiver and safe MCU probes; authenticated transport and device inventory with encrypted model/gallery policy management.

**P3 physical evidence:** instrumented field-unit on wall with rain/sun/night/cold scenarios, capture quality and independent energy. Operators review *synthetic* policy events before any separately authorized real-person evaluation.

**Decision boundary:** simulated UI and even correct image-processing code cannot validate the commercial value hypotheses, legal permission, true biometric accuracy or physical thermal/radio/ingress robustness.
