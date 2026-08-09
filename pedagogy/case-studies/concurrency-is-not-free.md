# Case study: when concurrency becomes a scientific blocker

**Type:** pedagogical case study  
**Source:** Siamese Embedding Compression Lab, Study 0 v0.2.2 coverage campaign  
**Status:** derived learning artifact, not outcome evidence  
**Authority boundary:** removing this file changes no runner behavior. The project
Scientific Chronicle and executable contracts constrain the run; this file explains why.

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

## Sources for the general mechanisms

- [NumPy: parallel random number generation](https://numpy.org/doc/stable/reference/random/parallel.html)
- [NumPy: `SeedSequence`](https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.html)
- [NumPy: thread safety](https://numpy.org/doc/stable/reference/thread_safety.html)
- [Python: thread-based parallelism](https://docs.python.org/3/library/threading.html)

