# LFW exploratory result — v0.1

## Question and verdict

Can a learned Siamese linear projection compress the frozen 512D ImageNet ResNet-18
representation to 128D without losing more than 0.03 absolute FNMR versus raw 512D at
the same benchmark FMR of 0.01?

**Not demonstrated.** The same conclusion holds for the random and PCA controls. This is
a negative result for this specific backbone, dataset and protocol—not evidence that
metric learning or embedding compression is generally ineffective.

## Frozen comparison

Every route received the same pair splits:

| Route | Dimension | Learning |
|---|---:|---|
| raw | 512 | none beyond the frozen ImageNet backbone |
| random | 128 | seeded Gaussian projection |
| PCA | 128 | fitted on TRAIN endpoints only |
| Siamese | 128 | shared linear projection trained on TRAIN pairs with contrastive loss |

TRAIN contained 842 pairs, VALIDATION 795 pairs and the untouched LFW DevTest set 1,000
pairs. TRAIN and VALIDATION identities were disjoint; TEST was opened only after all
models and deployable-style validation thresholds had been frozen. Five seeds were
predeclared for every stochastic 128D route.

## Results

At a separately located **TEST equal-FMR benchmark point** (`FMR = 0.01`):

| Route | FNMR mean | ROC AUC mean | EER mean |
|---|---:|---:|---:|
| raw 512D | 0.8060 | 0.7931 | 0.2890 |
| PCA 128D | 0.8216 | 0.8058 | 0.2704 |
| random 128D | 0.8416 | 0.7726 | 0.3104 |
| Siamese 128D | 0.8288 | 0.8167 | 0.2662 |

The Siamese projection has the highest mean AUC and lowest mean EER in this run, but that
does **not** establish preservation at the low-FMR endpoint. Its mean FNMR is 0.0228 worse
than raw, the five seeds vary, and the worst paired-bootstrap upper confidence bound is
0.156—above the predeclared non-inferiority margin of 0.03. All five seeds had to pass;
none of the 128D methods met that method-level rule.

With thresholds selected on VALIDATION and frozen before TEST, mean `(FNMR, FMR)` was:

| Route | FNMR | FMR |
|---|---:|---:|
| raw 512D | 0.8940 | 0.0020 |
| PCA 128D | 0.8468 | 0.0020 |
| random 128D | 0.8940 | 0.0024 |
| Siamese 128D | 0.9312 | 0.0016 |

Those numbers expose threshold-transfer/calibration behavior. They must not be compared as
if every route operated at exactly the same TEST FMR. Conversely, the TEST equal-FMR
thresholds above are descriptive benchmark thresholds and are explicitly non-deployable.

## What the run establishes

- Antonio's central training mechanism is real: pair labels update a shared 512→128
  projection through contrastive loss.
- A cosine/distance matcher can consume the resulting 128D templates, but computability
  alone is not evidence of added value.
- Against raw, random and PCA controls, this run does not show that the learned projection
  preserves low-FMR verification performance.
- Reducing 512 float32 values to 128 cuts template storage from 2,048 to 512 bytes. At
  150 million templates, the payload-only estimate falls from about 286.1 to 71.5 GiB.

## Limits and next gate

ImageNet ResNet-18 is not a face-recognition backbone, which is consistent with the poor
absolute error rates. LFW DevTest contains only 500 impostor pairs, giving an empirical FMR
step of 0.002; it cannot support industrial claims at very low FMR. The next bounded gate
is therefore to repeat the unchanged protocol with a recognized face-specific extractor,
then evaluate 64D/128D/256D, latency and 1:N retrieval. No production, fairness, PAD or
national-gallery claim follows from v0.1.

## Replay identity

- Run: `lfw_resnet18_siamese_projection_v0_1-89179914-911192ee-64559cbd`
- Configuration SHA-256: `89179914fce181e9544ab79e97cb42dc1571e786a46cf21c09a2414ae4bea4e7`
- Implementation SHA-256: `64559cbddeede132ddeeb4c88dfd5bfcb8f54d171daf802602f3420c9b6d337c`
- Status: `BENCHMARK_EXECUTED`

All declared artifact hashes were verified after execution: 36/36 present and valid.
