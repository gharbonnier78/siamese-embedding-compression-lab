# Reusable visible EO / NIR image-pair + 512D/128D evaluation demonstrator

**Status:** Functional **pixel-based non-human lab fixture**, not a trained facial recognition system. The two generated image modalities represent geometrical patterns with different artificial contrast: they are **RGB-like and NIR-like**, not camera captures at NIR wavelengths. This is a deliberately honest step beyond the older metadata-only digital twin.

## Running the actual Python image-pixel comparison

From the repository root, with an isolated environment:

\`\`\`bash
python -m pip install -r engineering/requirements.txt
python engineering/sim/pixel_replay.py --out /tmp/siamese-pixel-demo
# open /tmp/siamese-pixel-demo/offline_replay_report.html
# inspect /tmp/siamese-pixel-demo/synthetic_fixture_images/*.png
# see /tmp/siamese-pixel-demo/image_comparison.json and .csv
\`\`\`

The code procedurally **creates real image files** representing abstract NON-HUMAN geometry, uses Pillow to read pixels, SciPy DCT-II to produce a 512D descriptor for each capture, unit-normalizes its vectors, runs exact cosine comparisons against a 512D enrollment gallery, and repeats on the **same unchanged input images** after a seeded random orthogonal 512→128 projection. Thus it tests reproducible data/model/lookup flow, shape compatibility, artifact hashing and report generation. It DOES NOT implement face detection, facial embedding extraction, multimodal NIR fusion, threshold calibration, real liveness or a qualified 1:N biometric.

**The 512D baseline is a DCT image feature, NOT AdaFace nor a learned Siamese network.** \`random128\` is NOT a measured quality-preserving compression. A 128D projection can only be meaningfully compared with exactly the same extractor, compatible enrollment/index and predeclared quality gate, not inferred from a few synthetic patterns.

The demo prohibits live or private photographs, refuses unauthorized dataset classes and revalidates each fixture SHA-256 before processing. Generated outputs are local, excluded from Git. It is OK to share the *abstract* generated images and CSV from this script to demonstrate the system architecture.

## What remains to connect an actual EO/NIR model — no weights in Git

A real 512D feature extractor requires:
- A **reviewed, legally usable and redistributable or locally licensed** architecture and checkpoint with verified SHA-256, provenance and NIR suitability. A RGB-trained network must not be assumed to work on NIR imagery simply by copying channels.
- Explicit image input shape, color order, dynamic range, crop/landmark rules, normalization and calibration, with frozen version identifiers.
- ONNX Runtime/OpenVINO/RKNN/TFLite/CPU execution provider and SoM-specific profiling; ONNX Runtime supplies \`InferenceSession\` but does not validate cross-spectral biometric quality.
- Real image-pair record in an external encrypted vault, timestamp alignment, site/dataset purpose authorization, split TRAIN/VALID/TEST; no person data in Git, public CI or generic alerts.
- Real dimension 512D output, L2 norm, exact and later ANN implementations, 100k/500k/1m compatible gallery, and pre-registered 1:N FPIR/FNIR power-qualified validation under independent reviewer.

For \`pca128\` or \`siamese128\` you may supply a local frozen \`.npz\` with \`matrix\` shape (512,128) and \`metadata\` JSON (method, \`data_split=TRAIN_ONLY\`, \`training_dataset_sha256\`, \`model_revision\`) using \`--pca-checkpoint\` or \`--siamese-checkpoint\`. This is a **linear projection compatibility interface**; a real nonlinear Siamese architecture cannot be represented faithfully by a fixed matrix, and requires its own signed runtime adapter. A trained 128D linear projection is not proof of Siamese superiority.

No checkpoint is downloaded, included, trained or run by the current demonstration.

## Compare two classes of evidence

- **Software/algorithm comparison:** same frozen acquisitions, same extracted 512D original embedding, one projection active per replay, compatible gallery, logged model and dataset hashes, classification of synthetic candidate/no-decision, CPU/host timings measured only with recorded configuration.
- **Physical experiments:** different real cameras/illumination settings, hardware synchronization, true EO/NIR capture, domain shift, actual full-system power + calibrated external meter, sustained thermal and RF. A replay of identical files cannot measure a future exposure or NIR light safety.

## Regulatory and scientific separation

Default operation for events does not retain visitor face images. Explicit, purpose-limited approved research can operate in an isolated vault only, after the LEG-01 legal and SCI-01 scientific gate. Unknown is not a blacklist member. No automatic adverse action or identity-containing radio payload. A fake watchlist simulation illustrates operator workflow only.

Related:
- [Existing control-flow + supervisor](README.md)
- [Image-pair acquisition and scientific plan](IMAGE_PAIR_REPLAY_PLAN.md)
- [Secure study storage design](../SECURE_RESEARCH_STORAGE.md)
- [NIST FRTE 1:N FPIR/FNIR methodology](https://pages.nist.gov/frvt/html/frvt1N.html)
- [ONNX Runtime Python inference](https://onnxruntime.ai/docs/get-started/with-python.html)
- [OpenCV DCT documentation](https://docs.opencv.org/4.11.0/d2/de8/group__core__array.html)
