# PR #50 — D2 bounded backward audit of the public-information bound

Date: 2026-09-10  
Scope: non-outcome provenance / pre-execution firewall only  
Harness: `gharbonnier78/scientific-research-harness@3b109adcdd9a8cba4df029d3803ee0e5cb5bdf98`  
Protected boundary: no Study 1B SCREEN, qualification TEST, real-route performance, representation geometry, amendment, or S4N3 is opened.

## 1. Question

The focused reviewer accepted the D2 correction on head `022e8f50437dca4b2aa56a034a5fb63e7751301b`, but explicitly made that closure depend on a repository-side fact the reviewer could not verify: whether `878bfe2a64b34cce474a627d04b30233e2356958` was the earliest public commit carrying information capable of informing the later Phase A engineering workload.

The first repository-side audit disproved that claim by finding earlier relevant commits, including `eb4ac74a9afd0516d727a7f0c714964b9b198e03` at `2026-09-07T04:36:17Z`.

This second audit goes backwards to the repository root and asks a deliberately narrower question:

> What is the earliest immutable repository commit after which public project information could no longer be ruled out as a source of influence on a materially relevant 512D-versus-128D engineering measurement?

This is a negative-fact / public-knowability bound. It is not a claim that the final Phase A contract already existed at that time.

## 2. Repository root is the earliest public project-content bound

GitHub repository history identifies:

- commit: `4b40e7254bff1b88a44d13fb55b366bc7d3fc263`
- timestamp: `2026-08-07T08:23:56Z`
- message: `Initialize reproducible Siamese compression study`
- parents: `[]`
- initial public artifact: `README.md`

The empty parent list makes this the repository root. There is no earlier commit in this repository whose content could have published the project design.

Immutable commit URL:
`https://github.com/gharbonnier78/siamese-embedding-compression-lab/commit/4b40e7254bff1b88a44d13fb55b366bc7d3fc263`

Immutable README URL:
`https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/4b40e7254bff1b88a44d13fb55b366bc7d3fc263/README.md`

## 3. What the root commit already made public

The initial README already states all of the following:

1. the central compression question is `512 -> 128`;
2. the raw route is a 512D embedding and the candidate routes include 128D projections;
3. a float32 edge-storage calculation is provided for 512D and 128D templates;
4. the future bounded roadmap explicitly includes `1:N retrieval, gallery indexing and latency measurements`.

The root commit does **not** contain the later complete Phase A contract. In particular, it does not freeze the eventual `EXACT_DENSE_DOT_PRODUCT_TOP1` implementation, the Jungle Championship G0/G2 scenarios, the final CPU-only Phase A envelope, the off-device load generator, or the external-power-meter contract.

That distinction is intentional. D2 is being used only as a conservative proof of **absence of influence from public repository information**. Once the repository publicly disclosed the dimensions and a planned 1:N/gallery/latency engineering direction, later evidence can no longer be declared structurally uninformed by the project merely because the exact later benchmark syntax had not yet been committed.

## 4. Consequence for D2

For v0.5, the safest public-ordering rule is therefore:

- evidence strictly earlier than `2026-08-07T08:23:56Z` may use D2 to establish that it could not have been informed by this repository's public design;
- evidence at or after that timestamp may **not** use repository-public ordering alone to establish non-influence;
- such later evidence may still be admissible, but its provenance and informational overlap must be handled explicitly rather than cleared by structural impossibility.

This is deliberately conservative. It may reject some genuinely independent evidence created after repository initialization. That false rejection is preferable to a permissive bound that incorrectly labels potentially informed evidence as structurally impossible to have been informed.

The previous candidate anchors remain useful chronology, but they are no longer D2 bounds:

- `eb4ac74a9afd0516d727a7f0c714964b9b198e03` — 2026-09-07T04:36:17Z — explicit 512D/128D dense-comparison engineering note;
- `e8e82475c23968ec4a624460575a7948bf218bf4` — 2026-09-07T05:17:08Z — edge engineering input sheet;
- `034e465c355468a56cd13332b10d6c971ff19d71` — 2026-09-07T05:17:38Z — hardware/energy trade-off note;
- `878bfe2a64b34cce474a627d04b30233e2356958` — 2026-09-07T06:33:05Z — benchmark v0.1.

## 5. D1 and D2 solve different negative-fact problems

The reviewer correctly identified that a public commit timestamp bounds **public** knowability, not the knowledge of the person who authored or commissioned the work before publication.

The prospective v0.5 rule therefore separates the mechanisms explicitly:

- **D2 — public ordering:** can discharge the public-information negative only for genuinely third-party or pre-existing external evidence, and only when the evidence timestamp is strictly earlier than the conservative public bound.
- **D1 — accountable attestation:** carries the negative for evidence produced, commissioned, requested, selected, or otherwise known by the attesting party. D2 never substitutes for D1 in that case, even when the evidence timestamp is earlier than the public commit.

This closes the gap in which an author could know an in-preparation design before its public commit while a timestamp-only rule incorrectly treated a prior measurement as uninformed.

## 6. What this audit does not close

### R1 / N2 — portable-choice informational overlap

Still open. The current D3 classifier requires conjunction of vector dimension, search family and hardware class. That can under-classify measurements on another hardware class that nevertheless inform portable lock choices such as BLAS/backend, thread/affinity policy or energy-measurement methodology.

This audit does not silently modify D3. R1/N2 remains a separate prospective pre-execution hardening item requiring its own review.

### Construct validity

Not reviewed. This audit says nothing about whether Phase A measures the engineering construct it claims to measure.

### Execution admissibility

Not changed. Target edge hardware, external meter, off-device load generator and configuration-choice provenance are not materialized. Canonical Phase A remains prohibited.

## 7. Audit conclusion

Within the immutable history of this repository, the conservative public-information anchor is the repository root:

`4b40e7254bff1b88a44d13fb55b366bc7d3fc263 @ 2026-08-07T08:23:56Z`.

This conclusion is stronger and simpler than attempting to identify the exact moment every later Phase A classifier attribute became public: it guarantees that evidence strictly before the repository's first project content could not have been informed by the repository's public design. It does not claim anything about private pre-publication knowledge; D1 attestation remains responsible for that case.

## 8. Next admissible action

Create environment lock v0.5 prospectively, without rewriting v0.4, using this conservative root bound and an explicit D1/D2 responsibility split. Keep R1/N2 open and canonical Phase A blocked. Run bounded assurance and obtain focused independent re-review before declaring D2 closed again.