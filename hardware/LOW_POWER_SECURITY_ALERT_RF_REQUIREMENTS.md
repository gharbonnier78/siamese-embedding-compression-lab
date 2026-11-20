# Dedicated low-power radio alert link to event security — Phase 0 extension

**Date:** 2026-11-20. **Status:** requirement recorded, transport not selected; no measured link budget, latency, power, coverage or legal operational authorization.

## Requirement and scope

The permanently installed EO/NIR event edge unit shall have a **separate, low-energy, authenticated radio channel for SHORT SECURITY ALERTS** to the event organizer's authorized security reception point. This radio channel is not equivalent to the Ethernet/PoE network, Wi-Fi/5G data/OTA connectivity, or the external analysis PC. Security notifications must not depend on the analysis PC, a remote AI inference server, or continuous streaming of video. No normal per-passerby message: a 1,000-people/hour walkthrough is a local workload, not a 1,000 RF-alert/hour design target.

Examples of allowed prototype alert **classes** (not identity declarations):
- `SUPERVISOR_TAMPER`, `POWER_FAILURE`, `DEVICE_OFFLINE`, `SENSOR_UNAVAILABLE` and `EXPLICIT_SECURITY_REVIEW_REQUEST`.
- Where an authorized, validated biometric policy and consent regime separately allow it, a **candidate requiring human review**, not a confirmed match, can create `REVIEW_REQUEST`. Do not include name, face, image, template, watchlist membership or score in untrusted RF payload. Do not disclose the existence of an actual watchlist to Flux or a public radio receiver.

## Design options to compare (do not freeze radio now)

| Option | Architecture | Pros | Limitations |
|---|---|---|---|
| **Private LoRaWAN Class A** | low-power EU-region LoRaWAN end-device -> event-owned on-site gateway/network server -> authenticated organizer security console/dispatcher | low-power, short uplink bursts, can be independent of Internet when local network server | Requires gateway, site coverage study, region/regulatory validation, end-to-end application security, confirmed uplink/ack policy and backend; handset cannot directly receive LoRaWAN. Downlink only after uplink in Class A |
| **Point-to-point sub-GHz radio** | local radio module -> physically controlled receiver at security office | fewer network components in some simple deployments | Application-level security, key lifecycle, retries/ack and spectrum coexistence must be engineered and tested; no assumption of guaranteed delivery |
| **Existing event wired/Wi-Fi** | local secure alert message over Ethernet/Wi-Fi to event security console | minimal extra radio hardware when LAN exists | not an independent radio fallback; power/base station availability and segmentation matter |
| **BLE to authorized nearby receiver** | fixed device -> local relay within controlled short range | low power and simple experiments | coverage obstructed by event crowd/walls; phone reception and background mode not guaranteed; not a general long-range alert path |
| **Cellular data** | secure 4G/5G message to organizer app | flexible reach | extra power, subscription, network coverage; not the preferred *low-power* alert by itself |

Select only after measured distance/site RF survey, number of installed units, burst/alert rate, deadline, path redundancy, legal RF band, operator response procedure and cost of false alerts. A low-data-rate radio is not inherently a reliable emergency alarm link.

**Regulatory note (France/EU):** spectrum use, ERP limits, duty-cycle / LBT and RED conformity must be verified for the actual band, module, antenna and emission pattern. Do not assume free unlimited use of 868 MHz. See ARCEP/Legifrance and LoRa Alliance below.

## End-to-end delivery chain

```text
Fixed EO/NIR unit:
  secure local event/policy engine
          |
          | REVIEW_REQUEST only where authorized and evidentially gated
          v
  low-power always-on MCU / alert manager + persistent queue
          |
          | RF message with pseudonymous device/site/zone ID,
          | alert type, sequence, timestamp, nonce, policy/evidence reference
          | (NO images/templates/identity)
          v
  [LP radio modem + antenna with sealed RF installation]
          |
          | LoRaWAN private gateway OR controlled peer receiver
          v
  organizer security receiver + local dispatch application
          |
          +--> receipt ACK (radio/network)
          +--> operator acknowledgement (distinct event)
          +--> human review/response, timestamped outcome
```

**Safety separation:** if the host SoC is sleeping, MCU-originated hardware/tamper/power alarms can be sent without waking the AI pipeline when RF stack permits. A **biometric recognition alert cannot be generated when its model/host is asleep**; it requires wake -> acquisition -> inference -> permitted policy review event first.

## Requirements to engineer and test

- `AL-001` dedicated low-power radio or explicitly justified secure shared alert infrastructure. Design power domain, MCU UART/SPI, modem wake, TX peak current, hardware reset and antenna/mounting clearance.
- `AL-002` **no sensitive biometric data over radio**; payload only event ID, pseudonymous device/site/zone, code, severity, time and optionally signed evidence reference to authorized system.
- `AL-003` delivery quality: idempotent event ID + sequence counter, replay protection, auth/confidentiality, queued retries, bounded age/expiry, flood limiting, deduplication and privacy-safe audit. LoRaWAN provides application security but keys, gateway and app server require secure configuration; avoid claiming reliable delivery from cryptography alone.
- `AL-004` distinguish **RF/network receipt ACK** from **human operator acknowledgement**. If no RF ACK/connection, persist locally, retry within legal duty-cycle and feasible power, escalate over configured alternate path when available, then record undelivered status. NO guarantee of successful response.
- `AL-005` site survey: range with walls/crowds/metal truss, antenna detuning near enclosure, simultaneous units, channel occupancy/interference, gateway offline/power loss, local-dispatch independence from WAN, stress tests and environmental IP/RF survivability.
- `AL-006` power: meter idle/sleep TX current, joules per sent and successfully acknowledged alert, retries and heartbeat daily energy, reserve operation after loss of primary PoE/DC, plus impact of always-on listener vs Class A uplink.
- `AL-007` update security: signed modem/MCU firmware, identity provisioning, per-device key rotation/revocation, no default passwords, fail-closed on expired permissions.
- `AL-008` establish target event rate, latency SLO and allowed RF retries with organizer **before choosing a modem**. Do not send a radio packet for each person detected.
- `AL-009` evaluate external security dispatcher: physical receiver, local gateway if needed, operator display/pager/phone interface, role-based access, logged acknowledgement and response. This is **event operations equipment** separate from the independent *scientific test PC*.
- `AL-010` target radio must be *optional to AI functions*: no radio, gateway or network -> local detection/search continues and alerts enter bounded queue with a diagnostic of missing dispatch connectivity.

## Minimum procurement and schematic handoff

For both product and security-office equipment add separate provisional BOM lines for regional-certified radio module, antenna & RF connector, mounting/interface, validated supply path, optional on-site gateway/receiver and operator display/pager gateway. Identify real manufacturer part number and datasheet only after link budget and integration decisions. Do not guess current prices or regulatory certification.

Handoff to Flux.ai Phase 0: add an ALERT COMMUNICATION block and SECURITY OPERATIONS RECEIVER block to full system architecture; evaluate LoRaWAN private gateway vs authenticated P2P sub-GHz and current event LAN/Wi-Fi. Include a power-state/readout matrix and site radio qualification plan, not a final routed RF PCB.

## Reference sources

- LoRa Alliance — About LoRaWAN / Class A low power: https://lora-alliance.org/about-lorawan-old/
- LoRa Alliance — LoRaWAN is secure but implementation matters: https://lora-alliance.org/resource_hub/lorawan-is-secure-but-implementation-matters/
- The Things Network — classes: https://www.thethingsnetwork.org/docs/lorawan/classes/
- ARCEP — Bandes libres and radio restrictions: https://www.arcep.fr/la-regulation/grands-dossiers-reseaux-mobiles/le-guichet-start-up-et-innovation/le-portail-bandes-libres.html
- Legifrance — 2023-1412 short-range device regulations: https://www.legifrance.gouv.fr/jorf/id/JORFSCTA000048119816
