# PR #50 — bounded backward repository-history audit for D2

Date: 2026-09-10  
Scope: non-outcome provenance / temporal-information audit only  
Protected boundary: no Study 1B SCREEN, qualification TEST, real route performance, representation geometry, amendment, or S4N3 is opened.

## Trigger

The focused reviewer accepted the D2 correction on head `022e8f50437dca4b2aa56a034a5fb63e7751301b`, but made closure depend on one repository-side fact they could not verify: that the then-declared anchor `878bfe2a64b34cce474a627d04b30233e2356958` was the earliest repository publication sufficient to construct a materially informative prior measurement.

Repository inspection subsequently showed that this was false. Earlier commits on 2026-09-07 already published enough dimensional and dense-comparison engineering information to make the claimed anchor too late. D2 was therefore reopened prospectively in `CHRON-20260910-045`.

This audit continues backward until a bound is reached that is both conservative and mechanically terminal.

## Audit criterion

The purpose of D2 is not to identify the first commit containing every final Phase A field. That would create a late and fragile bound. The relevant question is earlier:

> When did this repository first publish enough of the 512D-versus-128D engineering problem and retrieval/latency measurement family that a repository-informed prior measurement could plausibly become materially informative for later lock-defining choices?

A conservative bound is preferred. It may reject genuinely uninformed later evidence; it must not admit evidence merely because some later Phase A detail had not yet been committed.

## Terminal repository fact

Commit:
`4b40e7254bff1b88a44d13fb55b366bc7d3fc263`

Timestamp UTC:
`2026-08-07T08:23:56Z`

Message:
`Initialize reproducible Siamese compression study`

GitHub repository metadata reports:

```text
parents: []
```

Therefore this commit is the repository root. There is no earlier commit in this repository to inspect.

Immutable commit URL:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/commit/4b40e7254bff1b88a44d13fb55b366bc7d3fc263

Immutable README URL:
https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/4b40e7254bff1b88a44d13fb55b366bc7d3fc263/README.md

## Information already public at repository inception

The root README already states all of the following:

- the project question is a supervised `512→128` linear metric projection;
- the uncompressed route is an L2-normalized `512D` embedding;
- the random, PCA and Siamese routes are `512→128` transformations;
- the project explicitly quantifies float32 template storage for 512D versus 128D;
- the roadmap explicitly names future `1:N retrieval`, `gallery indexing` and `latency measurements` as an engineering gate.

This does **not** mean that the final Jungle Championship Phase A contract, CPU choice, G0/G2 scenarios, exact dense top-1 semantics, threading policy or power methodology were frozen in August. They were not.

It means something narrower and sufficient for D2: from repository inception onward, a repository-informed measurement comparing the 512D-versus-128D representation family in retrieval/storage/latency terms could already be materially informative to later engineering choices. The temporal firewall should therefore not use a later public commit to certify such evidence as structurally uninformed.

## Corrected D2 bound

The conservative public-information bound is the repository root commit:

```text
D2_PUBLIC_INFORMATION_BOUND_SHA = 4b40e7254bff1b88a44d13fb55b366bc7d3fc263
D2_PUBLIC_INFORMATION_BOUND_UTC = 2026-08-07T08:23:56Z
```

For structural-impossibility reasoning, qualifying evidence must be strictly earlier than that timestamp.

Because this is the repository root, the claim “no earlier repository commit exists” is structurally checkable from the empty parent list. This is stronger than asserting that a later domain-specific benchmark commit happened to be the earliest relevant one.

## D1 / D2 responsibility split

The reviewer correctly observed that a public commit timestamp bounds public knowability, not the private knowability of the person who authored or commissioned the design before committing it.

The prospective lock must therefore state explicitly:

- **D2 ordering** may discharge the negative only for genuinely third-party or pre-existing external evidence whose provenance demonstrates that it predates the repository public-information bound;
- **D1 accountable attestation** carries the negative for evidence produced, commissioned, requested, reviewed, received, or otherwise known by the attesting party, including evidence predating public commit time;
- the D2 public timestamp never substitutes for D1 attestation.

This division prevents a pre-publication internal measurement from being treated as uninformed merely because its timestamp precedes the first public commit.

## R1 / N2 remains separate

This audit does not modify the information-overlap classifier. The reviewer’s R1/N2 observation remains open: the current conjunction of vector dimension, search family and hardware class can under-classify evidence that is informative for portable choices such as BLAS/backend selection, threading/affinity or energy-measurement methodology.

That is a distinct semantic-hardening item. It must be handled prospectively and independently reviewed before an execution-specific lock is frozen. It is not silently folded into this D2 correction.

## Conclusion

The bounded backward audit terminates at repository inception and establishes a conservative, mechanically terminal public-information bound. The earlier `878bfe2a...` anchor is superseded for future execution by the repository-root bound above.

This audit does not itself close D2. Closure requires a prospective environment-lock revision implementing this bound and the explicit D1/D2 responsibility split, focused assurance on the exact new head, and independent re-review.

Canonical Phase A execution remains prohibited. Construct validity remains unreviewed.
