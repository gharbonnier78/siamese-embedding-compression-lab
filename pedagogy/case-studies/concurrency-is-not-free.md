# Case study: when concurrency becomes a scientific blocker

**Type:** pedagogical case study  
**Source:** Siamese Embedding Compression Lab, Study 0 v0.2.2 coverage campaign  
**Status:** derived learning artifact, not outcome evidence  
**Authority boundary:** removing this file changes no runner behavior. The project
Scientific Chronicle and executable contracts constrain the run; this file explains why.

## Pedagogical concept contract

This case instantiates `pedagogy/PEDAGOGICAL_CONCEPT_CONTRACT.md`. Its target concept is:

> How can parallel execution alter the scientific meaning of a simulation, even when every
> worker appears to run the same correct estimator?

### Prerequisites

```text
repeatable pseudo-random numbers
        |
        v
seed -> generator state -> random stream
        |                    |
        +---------+----------+
                  v
          independent datasets
                  |
                  v
       Monte Carlo coverage estimate
                  |
                  v
     serial / parallel equivalence
```

The learner does not need prior knowledge of multiprocessing or probability theory for the
first view. The engineering view assumes basic Python and testing. The scientific view
introduces the variance consequence mathematically.

## Essential vocabulary and acronyms

| Term | Meaning here | Why it matters |
|---|---|---|
| **RNG** | Random Number Generator: the general mechanism that produces pseudo-random values | The coverage experiment depends on many reproducible random draws |
| **PRNG** | Pseudo-Random Number Generator: deterministic algorithm whose output looks random | Reusing or overlapping its stream can create hidden dependence |
| **Seed** | Input used to initialize random-state construction | The same seed and construction reproduce the same stream |
| **State** | Mutable internal position of a PRNG | Copying the same state into two processes can duplicate future draws |
| **Stream** | Ordered sequence emitted by one PRNG state evolution | Logical datasets need distinct, controlled streams |
| **Seed lineage** | Root entropy plus the recorded path used to derive a child stream | It gives each dataset a stable identity independent of its worker |
| **Process** | Separate operating-system execution context with separate Python memory | It can use another CPU core, but data and state must be transferred safely |
| **Worker** | Process assigned one or more logical tasks | A worker is an execution resource, not a scientific dataset identity |
| **GIL** | Global Interpreter Lock in ordinary CPython | It limits simultaneous Python bytecode, but many NumPy operations release it |
| **Serialization** | Encoding an object so it can be sent to another process; Python commonly uses pickle | Transfer cost and exactly what state crosses the process boundary matter |
| **Deterministic** | Same frozen inputs and lineage produce the same output | Necessary for replay, but not by itself proof of statistical independence |
| **Digest** | Cryptographic summary such as SHA-256 of output bytes | A compact way to test byte-identical replay |
| **Vectorization** | Replacing repeated Python operations with array-level operations | It changes implementation cost and requires reference equivalence evidence |
| **Concurrency** | Several tasks are in progress during overlapping time | Does not automatically mean several CPU cores execute simultaneously |
| **Parallelism** | Tasks actually execute simultaneously on different compute resources | Can accelerate work while introducing scheduling and state-management risks |

## View A — intuition for a first encounter

Imagine that each simulated dataset is a numbered laboratory vial. Every vial needs its own
recipe for generating random ingredients.

A worker is only a laboratory assistant. If vial 17 is handled today by assistant A and
tomorrow by assistant B, vial 17 must still receive the same recipe. Therefore the recipe
must belong to **vial 17**, not to **assistant A**.

Two naive failures are possible:

1. give two assistants the same copied recipe state: they may produce the same sequence of
   supposedly random ingredients;
2. define recipes from assistant numbers: changing the number of assistants changes the
   experiment.

The adopted design gives every vial a recorded recipe lineage before assistants begin.
Assistants never share one mutable random generator.

**En français dans le texte:** le nombre de processus peut changer le temps de calcul, mais
ne doit jamais changer l'expérience scientifique effectivement réalisée.

## View B — the engineering object

The parent process constructs immutable descriptors for logical units:

```text
root seed
  -> scenario 0..4
       -> one graph stream
       -> dataset 0..N-1
            -> one distance stream
            -> one bootstrap stream
```

Only after this plan exists are tasks sent to workers. A worker materializes local RNGs from
the descriptor assigned to the dataset. There is no shared mutable `Generator`, and the
worker number is absent from the scientific lineage.

This separates two mappings:

```text
scientific identity: (scenario, dataset index) -> seed lineage -> outcome
execution mapping:   scheduler -> worker -> task
```

The first mapping is frozen. The second may change without changing outputs.

## View C — the scientific object

The coverage campaign estimates the probability that an interval procedure covers a known
truth. For simulated dataset `d`, define:

```text
I_d = 1  if the interval covers the known truth
I_d = 0  otherwise
```

For `D` simulated datasets:

```text
C_hat = (1 / D) * sum(I_d)
```

If the `I_d` values are independent Bernoulli draws with coverage probability `C`, then:

```text
Var(C_hat) = C * (1 - C) / D
```

If hidden dependence is introduced between datasets, the general expression contains
covariance terms:

```text
Var(C_hat)
  = C * (1 - C) / D
    + (2 / D^2) * sum_{i<j} Cov(I_i, I_j)
```

The usual Monte Carlo standard error omits those covariance terms. A flawed parallel RNG
construction can therefore invalidate the precision calculation without raising a software
exception.

**Plain-language interpretation:** parallelism can damage the measuring instrument used to
validate the bootstrap. The numerical output may look reasonable while its claimed
uncertainty no longer has the intended meaning.

## Relationship to `profile-before-optimize.md`

`profile-before-optimize.md` teaches that a plausible hotspot hypothesis can be overturned
by measurement. This case study teaches a different lesson: correct parallel execution of
a bootstrap may be a precondition for producing interpretable scientific evidence at all.
The two case studies are siblings, not duplicates.

## 1. The naive assumption

The coverage validation is, on paper, embarrassingly parallel: five scenarios, thousands
of independently simulated datasets, and 10,000 bootstrap replicates per dataset. The
instinctive move is to map datasets onto workers and call the execution problem solved.

That instinct is right about the high-level structure. It is incomplete about what must be
true before that structure can be used safely.

## 2. Why processes were selected for this workload

In ordinary GIL-enabled CPython, one thread executes Python bytecode at a time. That fact
alone does **not** prove that threads cannot accelerate a NumPy workload: NumPy releases
the GIL for many low-level operations, and threads can run such operations in parallel.

The defensible conclusion is workload-specific. Profiling showed substantial repeated
Python control and many relatively small random-draw and edge-weight operations. The
project therefore selected `ProcessPoolExecutor` and measured it rather than inferring the
execution model from the word "NumPy" or from the GIL alone.

Separate processes introduce their own costs. Tasks and graph data must be serialized and
sent to workers; process startup, scheduling and memory traffic are not free. These costs
are part of the measured scaling evidence.

## 3. Why arithmetic worker seeds were rejected

A common shortcut is to seed worker `k` with `root_seed + k`. It can produce plausible,
distinct-looking streams within one run, but it creates two problems for this experiment.

First, NumPy documents that arithmetic worker seeds can overlap across repeated runs when
both the root seed and worker identifiers are changed by small increments. Second, tying a
stream to a worker makes the logical dataset-to-stream mapping depend on the execution
topology. Changing the worker count or scheduler can then change which random stream a
dataset consumes.

That violates the required replay contract even before asking whether the resulting
streams have acceptable probabilistic properties. A scheme that "runs fine" is not
evidence that it preserves the experiment.

## 4. The adopted random-lineage construction

The project uses a NumPy `SeedSequence.spawn()` hierarchy:

```text
root
  -> scenario
       -> graph
       -> dataset
            -> distances
            -> bootstrap
```

NumPy describes spawned streams as independent and non-overlapping with very high
probability. With the default 128-bit entropy pool, its documentation gives a pessimistic
collision estimate of approximately `n² × 2⁻¹²⁸` for `n` spawned streams. This is strong,
quantified engineering support, but it should not be rewritten as a universal mathematical
proof of independence.

The project adds deterministic evidence around that construction:

- each logical dataset records its seed lineage and can be replayed in isolation;
- worker assignment is separated from dataset identity;
- `workers=1` and `workers=4` must produce identical ordered
  `DatasetCoverageOutcome` objects, including bootstrap digests;
- `executor.map()` preserves the input order used by final aggregation.

Leaf `SeedSequence` nodes are converted through `generate_state()` to the integer seed
accepted by the already-reviewed estimator APIs. The stream identity is established by the
spawn hierarchy before that adapter boundary; no arithmetic seed offset is introduced.

### What is actually passed between processes?

The project does not pass one live RNG object around for several workers to mutate. It
passes ordinary immutable task data:

- the scenario definition;
- the fixed sparse graph;
- one dataset lineage descriptor;
- the number of bootstrap replicates;
- the selected execution engine.

The lineage descriptor records entropy, `spawn_key` and pool size. Inside the worker, that
descriptor is reconstructed as a local `SeedSequence`, then adapted to the local PRNG used
by the estimator. The mutable generator state remains local to that one task.

This avoids four distinct hazards:

| Hazard | Failure |
|---|---|
| Same seed reused for several datasets | identical pseudo-random streams |
| Mutable generator state copied during process creation | workers may continue from duplicated state |
| Seed derived from worker number | changing worker count changes the experiment |
| Retry that requests a new child seed | the retried dataset is no longer an exact replay |

### Small executable-pattern toy

Unsafe worker-bound design:

```python
def worker(worker_id, root_seed):
    rng = np.random.default_rng(root_seed + worker_id)
    return simulate_many_datasets(rng)
```

The worker owns the stream. Reassigning datasets or changing the number of workers changes
which stream generates which dataset.

Dataset-bound design used conceptually by the project:

```python
root = np.random.SeedSequence(20260807)
scenario_seeds = root.spawn(5)

scenario_seed = scenario_seeds[scenario_index]
graph_seed, *dataset_seeds = scenario_seed.spawn(dataset_count + 1)

dataset_seed = dataset_seeds[dataset_index]
distance_seed, bootstrap_seed = dataset_seed.spawn(2)
```

The tuple `(scenario_index, dataset_index)` selects the same lineage before any worker is
chosen. A scheduler may send that task to worker 0, 1 or 3 without changing the lineage.

This toy explains the construction; the authoritative implementation and tests remain in
the consumer study repository.

## 4a. The intermediate engineering-science path

The parallel runner was not one optimization step. It was a sequence of bounded claims:

1. **Freeze the scientific scale.** Five scenarios, contract-driven dataset checkpoints
   and 10,000 bootstrap replicates could not be reduced for convenience.
2. **Estimate and measure cost.** A non-outcome benchmark showed whether the reviewed path
   was operationally credible.
3. **Profile the actual workload.** The measured hotspots replaced inspection-based guesses.
4. **Choose the parallel unit.** One independently simulated dataset became one task because
   it matches the scientific Monte Carlo unit.
5. **Separate identity from resources.** Dataset index and lineage were fixed before worker
   scheduling.
6. **Preserve a serial reference.** The concurrent path needed an oracle for comparison.
7. **Test worker-count invariance.** Serial and multi-process executions had to return the
   same ordered outcome objects.
8. **Test isolated replay.** One dataset reconstructed from its recorded lineage had to
   reproduce its bootstrap digests.
9. **Measure acceleration only after equivalence.** Runtime evidence was reported only after
   correctness checks passed.
10. **Release only the bounded gate.** The evidence released execution feasibility; it did
    not validate coverage or prove 128D non-inferiority.

The current decomposition proposal adds an eleventh step:

11. **Re-prove equivalence for the new architecture.** A checkpoint-by-scenario workflow
    must equal the monolithic workflow on outcomes, aggregation, degeneracy handling and
    stopping decisions before it may run as production evidence.

## 4b. The exact invariance claim

Let `F` denote the frozen dataset execution function and `L_d` the lineage descriptor for
dataset `d`. The required bounded claim is:

```text
F(contract, scenario, graph, L_d, engine, workers=1)
  ==
F(contract, scenario, graph, L_d, engine, workers=k)
```

for every tested worker count `k`, where equality includes the ordered outcome fields and
bootstrap-array digests.

This demonstrates that the tested scheduling topology does not change the deterministic
scientific output. It does **not** prove every abstract property of the PRNG, nor does it
validate the statistical coverage procedure. Those are different claims with different
evidence.

## 5. What the speedup evidence does and does not say

The campaign measured an end-to-end legacy/vectorized speedup of about `4.80×` at the same
four-worker count. That is an **implementation-engine comparison**, not proof of `4×`
parallel scaling and not an ML-performance result.

Parallel scaling must be measured separately against a one-worker execution on the same
engine and environment. It can be limited by serial work, process overhead, data movement,
CPU availability and oversubscription. Runtime extrapolations remain feasibility estimates,
not guarantees.

This distinction matters because three different ratios answer three different questions:

1. legacy versus vectorized at the same worker count;
2. one worker versus several workers on the same engine;
3. estimated small benchmark versus measured frozen production execution.

They must not be substituted for one another.

## 6. Why GPU/CUDA was not treated as a free acceleration

The measured hotspot consisted of many relatively small operations repeated many times,
not a few already-batched tensor operations. A naive accelerator port would add kernel
launch, transfer and redesign costs whose benefit was unmeasured.

A GPU-relevant reformulation may exist by batching bootstrap draws and threshold operations,
but that would require proving that tie blocks, sentinel thresholds, RNG semantics and
degenerate-case behavior remain equivalent to the reviewed reference. It is a new execution
experiment, not a drop-in replacement.

## 7. Why concurrency became a blocker

Without a reviewed concurrent path, the honest choices were an operationally prohibitive
serial run or an unverified execution whose random streams and replay semantics could
invalidate the validation instrument.

The project therefore used a Scientific Chronicle entry to block production until a
deterministic, replay-verified execution route existed. That resolution established
execution feasibility only. It did not establish estimator coverage and did not reopen the
historical Study 0 result.

This is the crossing the case study exposes:

> When an engineering property is a precondition for the estimand or uncertainty procedure
> to retain its meaning, engineering correctness becomes part of scientific correctness.

## 8. The three-plane boundary

- **Evidence** supports the bounded execution claim: profiling, equivalence tests,
  benchmarks and replay digests.
- **Chronicle** constrains the decision: a named production step remains blocked until the
  required evidence exists.
- **Pedagogy** explains the decision: this case study connects the execution mechanism to
  the inferential assumptions.

None substitutes for another. A completed benchmark does not validate coverage; an exact
replay test does not prove the substantive claim; a clear explanation does not release a
gate.

## Misconception checks

| Plausible misconception | Correction |
|---|---|
| “A seed is the random sequence.” | A seed initializes a construction that creates mutable generator state; the stream is the sequence emitted as that state evolves |
| “Different integer seeds guarantee independent streams.” | Distinct numbers alone are not the project’s independence and replay contract |
| “We should share one seed between processes.” | Logical tasks receive distinct child lineages; workers do not share one mutable generator |
| “Deterministic means statistically independent.” | Determinism supports replay; probabilistic stream quality comes from the documented PRNG construction |
| “If serial and parallel outputs match once, parallelism is proven safe forever.” | The claim is bounded to frozen code, contract, engine, lineage design and tested topology |
| “A faster workflow is better scientific evidence.” | Speed changes feasibility; it does not improve estimator validity |
| “The 4.80x number proves four-worker scaling.” | It compares legacy and vectorized engines at the same worker count |
| “A red infrastructure job is a scientific failure.” | A scientific failure requires complete outcome evidence violating a frozen criterion |

## Understanding gates

A learner should be able to do all of the following before this concept is treated as
understood:

### First-encounter gate

- explain why the random recipe belongs to the dataset rather than the worker;
- distinguish a seed from a mutable generator state;
- explain why more workers may change runtime but must not change the experiment.

### Engineering gate

- identify the four levels of the project’s seed-lineage tree;
- predict what can fail when a generator state is copied or a seed is derived from a worker
  number;
- explain why task ordering and result ordering are separate;
- reproduce the small dataset-bound spawning toy.

### Scientific/PhD gate

- derive the covariance term in the variance of a Monte Carlo mean;
- explain why hidden inter-dataset dependence can invalidate MCSE;
- distinguish exact deterministic replay evidence from evidence about probabilistic stream
  independence;
- state exactly which gate serial/parallel equivalence can release and which scientific
  claims it cannot support.

These are understanding gates only. They do not alter the scientific runner or substitute
for the Chronicle blocker and its required evidence.

## Sources for the general mechanisms

- [NumPy: parallel random number generation](https://numpy.org/doc/stable/reference/random/parallel.html)
- [NumPy: `SeedSequence`](https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.html)
- [NumPy: thread safety](https://numpy.org/doc/stable/reference/thread_safety.html)
- [Python: thread-based parallelism](https://docs.python.org/3/library/threading.html)
