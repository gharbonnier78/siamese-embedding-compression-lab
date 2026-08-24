# Study 1A — Low-FMR benchmark and checkpoint-rights disposition

Status: `PREEXECUTION_DECISION_SUPPORT`

This note records a bounded pre-execution investigation. It does **not** open scientific benchmark outcomes, change Gate A, or authorize Study 1B.

## 1. Question

Close, or sharply reduce, two remaining Study 1A blockers before outcome-bearing qualification:

1. identify a lawful, reproducible low-FMR path for Gate A3;
2. establish a defensible disposition for use of the exact AdaFace R100 / WebFace12M checkpoint.

## 2. Low-FMR path

### 2.1 IJB-C remains the scientifically preferred benchmark, but public distribution is no longer available

NIST states that distribution of IJB-A, IJB-B and IJB-C was discontinued on 2023-03-14. Therefore the study MUST NOT reacquire IJB-C from an unofficial mirror merely to satisfy Gate A3.

The existing preregistration remains scientifically well matched to the published AdaFace R100 / WebFace12M reference (`TAR=97.66% @ FAR=1e-4`), but a local replay is admissible only if a lawful copy already held by the researcher/institution can be demonstrated together with the official protocol metadata and provenance.

Authoritative references:
- https://www.nist.gov/programs-projects/face-challenges
- https://github.com/mk-minchul/AdaFace

### 2.2 MegaFace was evaluated as a possible replacement and rejected for Gate A3

MegaFace is attractive methodologically because its verification benchmark reaches very low FAR (commonly `1e-6`) and its original dataset terms explicitly limited use to non-commercial research and education. However, the University of Washington now states that MegaFace is being decommissioned and that the data are no longer distributed.

Therefore MegaFace is **not** a robust new replacement for this study: choosing it now would replace one discontinued-access dependency with another. Historical copies or third-party mirrors are not acceptable without a separately demonstrated lawful provenance chain.

References:
- https://megaface.cs.washington.edu/
- https://megaface.cs.washington.edu/dataset/download.html
- https://megaface.cs.washington.edu/participate/challenge.html

### 2.3 WebFace260M test protocols are scientifically relevant but not an immediate drop-in Gate A3 replacement

The WebFace260M work includes low-FMR evaluation (`FNMR@FMR=1e-5`) on its test protocols and provides a natural training-data-family connection to WebFace12M. However:

- the published table is not an AdaFace R100 / WebFace12M replay reference for the exact frozen checkpoint;
- replacing IJB-C would therefore require a new benchmark-specific reference criterion and independent preregistration review before outcomes;
- access and applicable dataset terms must be demonstrated before use.

Thus WebFace260M test protocols remain a **candidate for a future amended A3**, not an authorized substitute today.

Reference:
- WebFace260M paper, DOI 10.1109/TPAMI.2022.3169734
- https://github.com/mk-minchul/CVLface/blob/main/cvlface/data_utils/recognition/training_data/README_TRAIN_DATA.md

### 2.4 Decision on A3

Current disposition:

- `IJB-C`: preferred and already preregistered; admissible only if lawful pre-existing access + official protocol provenance are demonstrated.
- `MegaFace`: rejected as a new replacement because official distribution is decommissioned.
- `WebFace260M low-FMR test`: scientifically promising replacement candidate, but requires a separate preregistration amendment, exact reference criterion, rights/access evidence, and independent review before any result is inspected.
- NIST FRTE remains external-validity context only; it is a sequestered evaluator and cannot be treated as a local downloadable substitute.

Gate A3 therefore remains `INDETERMINATE` for now. This is an access/provenance state, not a model-performance failure.

## 3. Checkpoint and training-data rights

### 3.1 What is positively demonstrated

The author-maintained Hugging Face model card for `minchul/cvlface_adaface_ir101_webface12m` declares metadata `license: mit`, identifies the artifact as `ADAFACE IR101 WEBFACE12M`, and explicitly instructs users to **follow the license of the training dataset**.

The exact hash-pinned safetensors artifact used in this study is:

- repository: `minchul/cvlface_adaface_ir101_webface12m`
- file: `model.safetensors`
- SHA-256: `2ea535a43877bd3de8091903935c783ce335be66a9f8917fae9a7a18ae4bbf56`

References:
- https://huggingface.co/minchul/cvlface_adaface_ir101_webface12m
- https://huggingface.co/minchul/cvlface_adaface_ir101_webface12m/blob/cc0182931c6b82d0de9fe007f96fd7a221c5c2eb/README.md
- https://huggingface.co/minchul/cvlface_adaface_ir101_webface12m/blob/main/model.safetensors

### 3.2 What is not yet demonstrated

The model card's MIT metadata is **not sufficient by itself** to waive upstream training-data restrictions because the same card explicitly delegates to the training-dataset license. The current investigation did not recover an authoritative WebFace12M terms page with a stable legal text that can be archived and reviewed.

Therefore the study MUST NOT claim unrestricted/commercial rights to the checkpoint merely from the repository's MIT label.

### 3.3 Bounded research-use disposition

For this repository, the technically correct disposition is:

- source-code licence: `MIT`;
- model-card metadata: `MIT`;
- checkpoint/training-data-derived rights: `CONDITIONAL_ON_WEBFACE12M_TERMS`;
- redistribution of checkpoint bytes: `NOT_AUTHORIZED_BY_THIS_STUDY`;
- commercial/product use: `NOT_CLEARED`;
- local scientific evaluation: may proceed only after the accountable researcher confirms that the intended use is compatible with the applicable WebFace12M terms or an institutional/legal review closes the point.

The study should retain only hash/provenance metadata in Git and should not redistribute model bytes.

## 4. Recommended next admissible actions

1. **Checkpoint E2 review:** formally review and close the already demonstrated IR101/R100 + RGB/BGR-equivalence chain for the exact inference backbone.
2. **Rights:** obtain/archive the authoritative WebFace12M terms applicable to the checkpoint or record an institutional/legal determination for this research use.
3. **A3:** first check whether the researcher/institution already holds a lawful IJB-C copy with official protocol metadata. Do not search unofficial mirrors.
4. If no lawful IJB-C exists, prepare a **separate preregistration amendment** for a genuinely available low-FMR benchmark; WebFace260M test protocols are the first candidate to investigate, but no numeric criterion may be selected after inspecting this model's outcome.
5. Continue the already authorized non-outcome-bearing input-pipeline, deterministic replay, worker-count and restart/resume controls in parallel.

## 5. Inferential boundary

Nothing in this note demonstrates AdaFace performance, passes Gate A, establishes production fitness, or authorizes Study 1B. It narrows the legal/provenance and benchmark-choice uncertainty before scientific outcomes are opened.
