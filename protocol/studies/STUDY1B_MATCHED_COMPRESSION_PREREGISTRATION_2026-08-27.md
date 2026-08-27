# Study 1B — Matched compression preregistration

Status: `FROZEN_DESIGN_PENDING_NONOUTCOME_PREFLIGHT_AND_INDEPENDENT_REVIEW`

Date: 2026-08-27

This amendment closes the scientific and execution choices for Study 1B as far as they can be closed without opening Study 1B outcomes. It does **not** authorize SCREEN or qualification outcome execution.

Authoritative methodological dependency: `harness-adoption.yaml`, pinning `scientific-research-harness` at `3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`. The older textual pin `422e08f3d6483ca11fa5a4767cffa99ce386bde5` in `study_1_preregistration.md` is superseded for current Study 1 work by the adoption manifest; historical artifacts retain their original provenance.

## 1. Research question and bounded claims

Starting from the Study 1A-qualified frozen AdaFace 512D embedding, compare four matched routes:

1. `raw512` — no dimensionality reduction;
2. `random128` — Gaussian random projection;
3. `pca128` — unsupervised PCA;
4. `siamese128` — supervised shared linear metric projection.

Primary method-specific question for candidate route `m` at target FMR `alpha`:

`Delta_FNMR(m, alpha) = FNMR_m(alpha) - FNMR_raw512(alpha)`.

A route may support the bounded wording **non-inferiority demonstrated on this frozen Study 1B protocol** only if its entire preregistered method-level rule passes. Failure is `NOT_DEMONSTRATED`, not proof of general inferiority.

Study 1B does not authorize claims about production readiness, 1:N identification, fairness, PAD/security, regulatory conformity, universal superiority/inferiority, SOTA, or representation geometry.

## 2. Frozen source representation

Study 1B consumes the exact Study 1A substrate and must not re-extract with changed semantics:

- method: AdaFace;
- architecture: IR101 / R100;
- released training corpus: WebFace12M;
- output: 512D;
- AdaFace code commit: `c60eaa786a42c03444f3df7096dbaf9d57ae010d`;
- checkpoint SHA-256: `0e7a3238d2a50f3fe3860782534928ac7cb2598977cf897f6869fd5ac2493fd0`;
- frozen preprocessing/inference semantics: aligned 112x112 input where supplied by the benchmark derivative, BGR evaluator boundary, normalization `(pixel/255 - 0.5)/0.5`, original + horizontal flip, AdaFace norm-aware fusion, final L2-normalized 512D embedding.

Any mismatch in checkpoint, code pin, preprocessing or embedding digest is an infrastructure/provenance failure and makes the affected execution inadmissible rather than a scientific negative result.

## 3. Data roles — frozen design

Study 1B uses the LFW View 1 development/test identity boundary for the bounded compression experiment. This choice is deliberately modest: it provides an identity-disjoint, reproducible public research protocol, not industrial biometric qualification.

### 3.1 Identity universe

- `peopleDevTrain.txt`: development-side identities only;
- `peopleDevTest.txt`: untouched qualification TEST identities only;
- no `peopleDevTest` capture, score or route outcome may be used to fit PCA, train Siamese, select a checkpoint, alter a threshold rule or alter the protocol.

The official View 1 identity boundary is retained. A non-outcome preflight must materialize the exact source files, hashes, image/capture manifest and confirm the expected identity counts before independent review.

### 3.2 Development-side role split

Sort `peopleDevTrain` identity names by `SHA256("study1b-role-v1|" + identity)` and assign, in that deterministic order:

- first 2,827 identities -> `TRAIN`;
- next 606 identities -> `VALIDATION`;
- remaining 605 identities -> `SCREEN`.

`TEST` is all 1,711 `peopleDevTest` identities.

If the materialized official metadata does not reproduce 4,038 DevTrain and 1,711 DevTest identities, execution fails closed and this protocol must be amended before any outcome is opened.

All available authorized captures of an assigned identity belong to that identity's single role. Cross-role duplicate/near-duplicate evidence is audited before outcomes. Any discovered cross-role identity equivalence or material near-duplicate leakage is a blocker, not an exclusion chosen after scores are seen.

### 3.3 Frozen pair-graph construction

Pair graphs are generated once from identity/capture metadata before route outcomes and are shared by all routes and all model seeds.

For each role:

- genuine draw: choose an eligible identity uniformly among identities with at least two captures, then choose two distinct captures uniformly; canonicalize and reject duplicate edges;
- impostor draw: choose two distinct identities uniformly, choose one capture uniformly from each, canonicalize and reject duplicate edges;
- pair-graph randomness is derived from a dedicated `SeedSequence` lineage and is not model/projection randomness or bootstrap randomness;
- pair labels and graph membership are frozen before any route score is computed.

Requested graph sizes are:

| Role | Genuine | Impostor |
|---|---:|---:|
| TRAIN | 20,000 | 20,000 |
| VALIDATION | 5,000 | 20,000 |
| SCREEN | 5,000 | 50,000 |
| TEST | 10,000 | 100,000 |

If a role cannot materialize the requested number of unique edges under the frozen rules, the preflight fails closed; pair counts may not be reduced after outcomes.

The preflight must archive role identity count, capture count, eligible-genuine identity count, realized pair counts, source hashes and graph hashes. These are design/provenance evidence, not scientific outcomes.

## 4. Routes and transformation semantics

All routes consume the exact same frozen raw512 embeddings and pair graphs.

### 4.1 raw512

- one L2-normalized 512D representation;
- no projection seed and no artificial seed variability;
- serialized source-embedding manifest/hash is the reference.

### 4.2 random128

For each candidate seed in the applicable stage:

- matrix shape `512 x 128`;
- entries independently distributed `N(0, 1/128)` (standard deviation `1/sqrt(128)`);
- no orthonormalization;
- transform `xR`, then L2 normalize;
- serialize matrix, seed and SHA-256.

### 4.3 pca128

For each candidate seed:

- fit on **unique TRAIN captures exactly once**, never pair-duplicated endpoints;
- center using the TRAIN mean;
- scikit-learn PCA, `n_components=128`, `svd_solver="randomized"`, `whiten=False`, `random_state=seed`;
- no VALIDATION, SCREEN or TEST capture may enter the fit;
- L2 normalize after transformation;
- serialize mean, components, explained variance, seed and transform SHA-256.

The seed-dependent randomized SVD is intentional and remains part of the method-level seed rule.

### 4.4 siamese128

Shared affine projection:

`z = L2_normalize(x W + b)`, with `W in R^(512x128)` and `b in R^128`.

Verification distance is Euclidean distance between normalized outputs. The training loss is contrastive loss:

- genuine: `0.5 d^2`;
- impostor: `0.5 max(0, 1-d)^2`.

Frozen optimizer/training semantics follow the current reviewed repository implementation:

- Adam semantics: `beta1=0.9`, `beta2=0.999`, `epsilon=1e-8`;
- learning rate `0.002`;
- weight decay `0.0001` on `W`;
- batch size `128`;
- maximum epochs `35`;
- early-stopping patience `6`;
- minimum validation-loss improvement `0.0001`;
- checkpoint = lowest VALIDATION contrastive loss satisfying the minimum-improvement rule;
- margin `1.0`;
- TRAIN pair graph fixed independently of the model seed;
- the model seed controls initialization and minibatch permutation only;
- no SCREEN/TEST hyperparameter tuning.

A Stage A `REDIRECT` may propose a new protocol, but no changed architecture/loss/hyperparameter may enter Stage B without a new preregistration amendment and independent review.

## 5. Seeds and randomness lineage

Stage A SCREEN route seeds: `[11, 29]`.

Stage B qualification route seeds: `[11, 29, 47, 71, 101]`.

Use one frozen root entropy value `20260827` with task-bound `numpy.random.SeedSequence` child lineages for at least:

- data-role/pair-graph generation;
- each random projection seed;
- each PCA randomized-SVD seed;
- each Siamese initialization/training-order seed;
- each uncertainty/bootstrap task;
- each known-truth simulation task.

Route/model lineages and bootstrap lineages must never share a child stream. Worker count, shard id and restart position must not define scientific randomness.

## 6. Primary operating point and non-inferiority rule

Freeze:

- target FMR `alpha = 0.01`;
- non-inferiority margin `delta = 0.03` absolute FNMR;
- primary endpoint: **equal-FMR representation comparison on TEST**, explicitly non-deployable.

Reuse is justified rather than automatic: Study 1B asks the same 4x 512D-to-128D representation-compression question as Study 0, and retaining the same 1% FMR operating point and 3 percentage-point FNMR tolerance gives direct cross-study interpretability while changing the source representation only. Neither value was selected from Study 1B outcomes.

For each candidate route and each preregistered seed, compute a one-sided **97.5% upper confidence bound** for paired `Delta_FNMR` using the frozen identity-aware procedure. A candidate method demonstrates non-inferiority only if **every** preregistered Stage B seed satisfies `UCB_97.5 <= 0.03`.

Multiplicity treatment: the three candidate-vs-raw hypotheses are fully preregistered and all will be reported. Each is an independent method-specific claim at one-sided alpha 0.025; no post-hoc selection or omnibus wording such as "at least one compression method is non-inferior" is allowed. The all-seeds condition is an intersection-union rule and no favorable seed may be removed. If a later publication wants a family-wise "any route" claim, it requires a separately adjusted analysis.

## 7. Confirmatory comparison of Siamese against simple controls

To answer whether supervision preserves performance **better than** the controls, preregister two secondary confirmatory paired estimands on the same TEST draws:

- `Delta_SP = FNMR_siamese - FNMR_pca` at equal FMR 0.01;
- `Delta_SR = FNMR_siamese - FNMR_random` at equal FMR 0.01.

Seed matching is by identical seed label. The two direct superiority hypotheses use Holm-adjusted one-sided alpha 0.025 across the two comparisons. For a route-level superiority statement, all five matched seeds must have adjusted upper bounds below zero. Otherwise superiority is `NOT_DEMONSTRATED`.

ROC, DET, AUC and EER are descriptive unless promoted by a later preregistered amendment.

## 8. Identity-aware uncertainty

Naive row bootstrap is prohibited.

Reuse the corrected Study 0 subject-slot bootstrap semantics, generalized to the frozen Study 1B graph and revalidated before TEST outcomes:

1. resample the TEST identity slots with replacement;
2. let `m_i` be the multiplicity of identity `i`;
3. genuine edge weight = `m_i`;
4. impostor edge weight = `m_i * m_j`;
5. never create an edge absent from the frozen TEST graph;
6. use the **same identity draw** for raw512 and every candidate route in a paired comparison;
7. use 10,000 bootstrap replicates in Stage B;
8. threshold/tie/sentinel semantics follow the corrected Study 0 v0.2.2 implementation unless an implementation-level difference is explicitly reviewed before outcomes.

A replicate with zero effective genuine mass, zero effective impostor mass, or an unresolvable target-FMR threshold is `DEGENERATE`. If more than 0.1% of replicates are degenerate for any primary comparison, that comparison is `INDETERMINATE`; no replicate may be silently discarded and replaced until a desired count is obtained.

Before TEST outcomes, known-truth simulations on the exact frozen graph family must demonstrate acceptable one-sided interval coverage. The preregistered validity criterion is the corrected Study 0 convention: the exact lower 95% Clopper-Pearson bound for empirical coverage must be at least `0.93` for every declared scenario/metric cell.

## 9. Stage A SCREEN — non-claim-bearing promotion rule

SCREEN never releases a scientific compression claim and qualification TEST remains sealed.

For seeds `[11,29]`, calculate each route's equal-FMR `Delta_FNMR` at FMR 0.01 with a 95% one-sided identity-aware UCB on the frozen SCREEN graph.

Decision:

- `CONTINUE`: at least one candidate route has both screen seeds with `UCB_95 <= 0.06`, no provenance/assurance blocker exists, and the qualification power preflight passes;
- `STOP`: every candidate route has both screen-seed point estimates `Delta_FNMR > 0.06`;
- `REDIRECT`: all other cases.

The `0.06` screen boundary is deliberately twice the final NI margin: it is a cost-control signal, not an inferential claim. A `REDIRECT` cannot open TEST; it requires a protocol amendment and independent review.

Maximum Stage A scientific budget: two route seeds, the frozen SCREEN graph, and no additional route/loss/dimension search. Engineering dry-runs on synthetic fixtures remain non-outcome-bearing.

## 10. Stage B sample-size / power contract

Power is evaluated **before TEST route outcomes** from identity/capture metadata and synthetic known-truth simulations, never at the null boundary.

Effect scenarios: true `Delta_FNMR = 0.00` and `0.01`.

Target: for each scenario, `P(UCB_97.5(Delta) < 0.03) >= 0.90` under the frozen method-level all-seeds rule.

The planning simulation must include:

- the realized TEST identity/capture structure;
- the realized genuine/impostor graph;
- identity clustering;
- uncertainty in locating the 1% FMR threshold;
- paired raw/candidate correlation;
- seed-to-seed variation;
- the five-seed intersection rule.

At least 4,000 simulated datasets per declared scenario are required. The simulation configuration, root seed lineage and output must be archived before qualification TEST is opened. The design passes only if the estimated power is at least 0.90 for both effect scenarios. If it fails, Study 1B qualification is blocked and the TEST remains unopened; sample size/data design must be amended and independently reviewed.

The primary sampling unit is identity/capture structure, never nominal pair count.

## 11. Operational threshold transfer — secondary

For each frozen route/seed, VALIDATION selects the largest distance threshold satisfying empirical FMR <= 0.01 under the frozen tie rule. That threshold is frozen and transferred once to TEST.

Report TEST FMR and FNMR at the transferred threshold descriptively. This is not the primary equal-FMR representation NI claim and does not establish deployable production thresholds.

## 12. Execution and replay contract

Before any outcome-bearing run:

- materialize a content-hashed AdaFace raw512 embedding manifest;
- materialize and hash data-role and pair-graph manifests;
- serialize every random/PCA/Siamese transform with SHA-256;
- capture Python/library/OS/hardware environment and machine-readable SBOM;
- route outputs must carry source embedding hash, graph hash, transform hash, route seed and protocol id;
- outcome workflows are `workflow_dispatch` only and fail closed without an explicit authorization artifact;
- parent process owns progress reporting and append-only `progress.jsonl`;
- scientific identity is independent of worker count;
- deterministic `workers=1` vs multi-worker digest equivalence is required;
- interruption/resume equivalence is required if sharding/resume is used;
- aggregation rejects mixed provenance;
- infrastructure failure remains infrastructure failure.

## 13. POC engineering assurance

Before GO-ready state:

- pipeline/system decomposition updated for Study 1B;
- focused unit tests for route transforms, role isolation, pair-graph generation, thresholding, identity bootstrap, degeneracy and seed lineage;
- deterministic transform/hash replay tests;
- lint/static checks green;
- dependency/supply-chain review recorded;
- secret scan green;
- static security analysis where supported;
- explicit security assumptions/residual risks;
- deterministic smoke path;
- worker-count and restart equivalence where applicable;
- CI and Research Assurance green on the exact reviewed head.

Telemetry is not scientific evidence unless separately promoted by a predeclared contract.

## 14. Pre-outcome blockers that must close before independent ACCEPT reviews

The scientific design above is frozen. The following **non-outcome** bindings still have to be materialized on this PR head before it can become `READY_FOR_STUDY1B_GO`:

1. exact LFW View 1 source-file hashes and capture manifest;
2. exact TRAIN/VALIDATION/SCREEN/TEST capture counts and graph hashes;
3. overlap/near-duplicate audit result;
4. known-truth coverage simulation on the Study 1B graph family;
5. a-priori power simulation meeting the 0.90 criterion for both effect scenarios;
6. Study 1B implementation/tests/replay/environment/SBOM assurance;
7. two independent reviews returning `ACCEPT` on the final unchanged head.

None requires opening SCREEN or TEST route outcomes.

## 15. Review and authorization sequence

Two independently navigable reviews are mandatory on the final material head:

- Review A: scientific/harness — claims, data roles, leakage, estimands, operating point, NI, dependence-aware uncertainty, Stage A rule, power, seeds, multiplicity, prohibited inferences, evidence/Chronicle/pedagogy separation.
- Review B: technical/reproducibility — exact raw512 source, pair graph, route semantics, preprocessing, RNG lineage, threshold logic, transform serialization, environment/replay, architecture/tests/static/security/dependency assurance.

Both must return `ACCEPT`. The exact reviewed head must remain unchanged and CI/Research Assurance must be green. Only then may the Chronicle move to `READY_FOR_STUDY1B_GO`, and only then may the human researcher be asked for a separate explicit **Study 1B GO**.

No SCREEN or TEST outcome is authorized by this document.

## 16. Geometry boundary

Representation geometry remains out of scope. The sequence is compression result first; geometry receives its own question and preregistration only if the compression evidence later motivates it.
