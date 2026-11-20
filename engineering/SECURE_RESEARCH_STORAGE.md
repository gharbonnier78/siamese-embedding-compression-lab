# Secure evidence and replay — threat and retention contract

**Confidentiality by design; this is a proposed architecture, not an operational guarantee.**

The **field appliance** shall only keep: one active signed model/extractor/projection, compatible local encrypted index/gallery, purpose-limited policy, power/sensor/alert operational events, bounded encrypted queue and minimal audit pointers. An event radio payload is only pseudonymous zone+event+nonce/sequence/receipt refs; no names, faces or templates.

The **external authorized research evidence system** is physically/logically separate from the operations receiver. It may capture *all evidence types* needed for reproducibility **only when that specific data capture is lawful, approved, necessary and purpose-limited**, including calibrated raw sensor/probe streams, timestamps, captured images if explicitly authorized, environmental settings, run/config/model/firmware/algorithm/projection/index hashes, selected gallery version, RF packet/ack metrics, operator response observations and experiment decisions. In field events, default to **no retention of images or personal biometric content**; use synthetic or consented controlled studies.

**Secure data path / roles**
1. Field device: authenticated time-correlated logging and minimal event stream.
2. Approved acquisition gateway: encrypted transfer with device identity, authenticated purpose/mode and signed run manifest; separate operational and research tenants.
3. Encrypted evidence vault: AEAD ciphertext at rest, per-study keys from enterprise KMS/HSM or offline controlled key custody; immutable metadata/versioned objects and encrypted deduplicated offline backup with two-person restore control.
4. Offline replay workstation: explicitly authorized analyst role; local decryption only into protected workspace, replays the SAME permitted acquisition against one selected 512D or 128D model at a time and separates projection/extractor/threshold changes; compares deterministic outputs and energy under matched controlled conditions.
5. Audit and lifecycle: named controller, access logs, purpose+retention policy, access expiry, deletion method, recovery exercises, immutable audit of legal authorizations and independent scientific reviewer.

**No real images, embeddings, lists, encryption keys or sensitive policy data in GitHub, ordinary Issues, cloud CI logs, telemetry, radio payload, or Flux.ai.** Public repo may contain dummy data and schemas only. Not even Git LFS is an acceptable sensitive-data store by default.

The source demonstration in sim/vault.py uses cryptography/AESGCM with a random nonce and an externally provided 256-bit key. **It is not a production backup, authentication, DLP, retention, secure-deletion, authorization or KMS implementation.** A real implementation needs secure transfer, vault service identity, KMS envelope encryption and rotation, RBAC/ABAC, database backups, disaster recovery tests, restricted data-bearing workloads, anti-exfiltration and legal assessment. Encrypted data without access control and proven restore is not a secure operational backup.

Model packages: externally signed manifest with per-model version, preprocessing, projection and embedding dimension; activate only after cryptographic, compatibility and index quality checks. Do not silently change gallery model/projection; one active pair per unit at a time. Scientific result sets are bound to exact inputs, versions and calibration. Results from different capture sessions are not interchangeable; replay cannot reproduce the optics or physical energy of a hypothetical new sensor exposure.

**Qualification check**: (a) offline unit works without research PC (b) unauthorized/modified manifest is rejected (c) vault tampering is detected (d) authorized encrypted backup can be restored on a separate workstation (e) all relevant versions/samples remain traceable and replay produces same algorithm output on fixed seeds (f) access and deletion obligations satisfied. All six are OPEN until evidenced on real configured platforms.

Legal hard gate: generalized face 1:N in public events is not presumed lawful; exceptional institutional uses require independent, purpose-specific authorization. Backup storage may intensify legal exposure — minimise collection at source and separate from device operations.
