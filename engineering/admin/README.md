# Offline administration, configuration and secure evaluation

**This is an engineering demonstrator, not approved for biometric deployments.** Only synthetic model/vector/policy examples are included. Real templates, faces, allow/deny/watchlists and private keys MUST stay outside Git and public CI, under separately authorized purpose-limited governance.

## Intended device administration

1. Provision unique node identity and public verification key in a protected hardware trust path (implementation TBD). Separate operations and research tenants.
2. Stage **one selected extractor/projection pair** plus versioned preprocessing contract, on-device gallery/index and authorized policy revision. Active config must be atomically switched only after signature and compatibility checks; preserve previous healthy image for recovery. No assumption that 512D+128D configurations run simultaneously.
3. Log hashes of firmware, model, projection, dataset/index and policy plus device mode, temperature and tracing IDs; never raw face data in diagnostic logs.
4. On missing/invalid signature, rollback and do not activate the candidate. A changed projection must trigger a matching-gallery/index rebuild and separately approved quality gate.
5. Operator security console receives **short pseudonymous event refs** and independent radio/network delivery vs human acknowledgement. It cannot fetch or change real lists without specific authorization.
6. **External research PC** can capture only explicitly permitted data, place it into encrypted evidence storage, preserve provenance, and run multiple frozen models OFFLINE on identical recordings. Field operation does not record all passer-by images by default. The user must establish lawful dataset rights and documented retention policies before any human acquisitions.

## Files

- package_manager.py: testable **signed manifest verification and atomic model-slot pointer staging** (no production secure boot).
- ../sim/vault.py: local AES-GCM encrypted research artifact vault, key supplied externally; no keys in Git.
- ../sim/replay.py: synthetic 512D and 128D computational replay, NOT a face-recognition accuracy test.

Minimum functional evaluation:

python engineering/admin/package_manager.py demo --out /tmp/edge_admin_demo

Production gaps: real device attestation, TPM/SE integration, authenticated remote provisioning, per-device key lifecycle, anti-rollback hardware, encrypted eMMC, firmware A/B, database compatibility checks, secure OTA transport, access policy, legal review and authenticated operational administration. These are release gates, not achieved properties.
