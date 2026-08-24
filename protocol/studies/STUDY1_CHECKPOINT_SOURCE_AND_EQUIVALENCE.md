# Study 1 — Checkpoint source, artifact identity and equivalence contract

Status: `PREEXECUTION_ENGINEERING_CONTRACT`

## Purpose

Study 1 must not depend on one rate-limited mutable download endpoint, but it also must not silently replace the preregistered checkpoint with a merely similar model. This contract separates **locator availability**, **artifact identity**, and **scientific equivalence**.

## Current sources

### Frozen preregistered source

- AdaFace R100 / WebFace12M
- Google Drive file id: `1dswnavflETcnAuplZj1IOKKP0eM8ITgT`
- original AdaFace code/protocol ref: `c60eaa786a42c03444f3df7096dbaf9d57ae010d`
- checkpoint bytes SHA-256: still to be materialized

The Google Drive endpoint is a locator, not the scientific identity. A temporary quota failure is an infrastructure failure and must not be turned into a scientific result.

### Author-maintained Hugging Face candidate

- repository: `minchul/cvlface_adaface_ir101_webface12m`
- advertised model identity: `ADAFACE IR101 WEBFACE12M`
- candidate file: `model.safetensors`
- published file SHA-256: `2ea535a43877bd3de8091903935c783ce335be66a9f8917fae9a7a18ae4bbf56`
- model card explicitly says to follow the training-dataset licence

This is a strong provenance candidate because it is maintained under the same author's ecosystem and names the same architecture/loss/training corpus. It is **not automatically the same scientific artifact** as the original Google Drive checkpoint.

The CVLFace performance board also reports slightly different reproduced values for some benchmarks from the original AdaFace table (for example CFP-FP and IJB-C), which is enough reason not to assert byte or functional identity without direct evidence.

## Equivalence levels

### E0 — same label only

Same architecture / method / training-corpus name. This is not sufficient for substitution.

### E1 — byte identity

Two downloaded files have the same SHA-256. They are the same byte artifact and may be treated as interchangeable locators without changing scientific meaning.

### E2 — tensor identity after deterministic format conversion

If formats differ (for example Lightning checkpoint versus safetensors), a documented converter extracts corresponding state tensors and proves:

- same parameter keys after declared name mapping;
- same shapes and dtypes;
- exact tensor equality, or a predeclared lossless representation equivalence;
- no missing or additional trainable state relevant to inference;
- deterministic conversion hash and replay command.

If E2 is demonstrated, the alternate format may be accepted as an equivalent mirror after technical review. The original and converted byte hashes remain distinct and both are recorded.

### E3 — functional equivalence only

If tensors are not identical but outputs are claimed equivalent, this is a scientific/model substitution question, not merely storage engineering. It requires a preregistration amendment and review before protected benchmark outcomes are used to justify the switch.

## Fail-closed rule

Until E1 or E2 is demonstrated against the preregistered original checkpoint, the Hugging Face artifact remains `CANDIDATE_ALTERNATE_SOURCE_EQUIVALENCE_UNPROVEN` and cannot release the checkpoint-identity blocker.

No benchmark result may be opened merely to decide whether the alternate checkpoint is 'close enough'.

## Durable acquisition policy

Once the canonical artifact is lawfully obtained and its redistribution/storage terms are reviewed:

1. Record a content-addressed manifest with SHA-256, byte size, logical model id, source commit/revision, licence/usage disposition and provenance chain.
2. Maintain at least two independent locators where lawful (for example upstream Hugging Face plus controlled object storage).
3. CI always verifies the expected content hash after download; a locator never defines identity by itself.
4. Cache by content hash, not by mutable filename or `main` branch.
5. Never make GitHub Actions artifacts the only source of truth because retention is temporary.
6. Do not commit large/restricted model bytes into a public Git repository.
7. For restricted artifacts, use controlled object storage or package/model registry access via short-lived credentials, while keeping only hashes/manifests in Git.
8. If redistribution is not lawful, keep a reproducible acquisition recipe plus hash and require the investigator to provision the exact artifact into the controlled cache.

Recommended storage hierarchy:

`authoritative upstream -> verified content hash -> controlled immutable cache -> CI/local consumers`

The upstream URL may disappear or rate-limit without changing the scientific identity once the content hash and lawful controlled cache exist.

## Current admissible next action

Materialize the Hugging Face candidate and its hash as non-outcome-bearing provenance evidence. Retry the original Google Drive source later or obtain the exact original bytes through another lawful source. If both become available, perform E1/E2 equivalence before deciding whether Hugging Face can become a canonical mirror.
