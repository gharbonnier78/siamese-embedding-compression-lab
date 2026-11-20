# Can physical Siamese experiments validate the six venture architectures?

**Design review v1 — 2026-11-20. This is a prospective evidence map, NOT measured outcomes.**

## Answer in one sentence

The fixed EO/NIR prototype and separate calibrated PC bench can establish **technical feasibility and comparative engineering claims**, and — only when combined with *real operators and lawful site trials* — some operational value. It **cannot by itself validate** customer pain, willingness to pay, procurement, market size, licensing demand, organizational governance, lawful 1:N watchlists or venture economics. **Do not treat a successful AI demo as a business model validation.**

## Experimental workstreams — physical unit ≠ business validation

- **PHY-0 / closest rival baseline:** existing steward + radio, simplest compliant PIR/counter, ordinary QR access or COTS edge camera as relevant. This must be measured before attributing value to the new device.
- **PHY-1 / stand-alone fixed-node engineering:** wall mock mounting, optical field and RGB/NIR acquisition; AI SoM/probe MCU, PoE/DC+protected backup, secure radio receiver, time-stamped power, thermal and mode states. Use synthetic sensor stimulus and consented controlled imagery only when separately approved.
- **PHY-2 / energy-performance comparisons:** calibrated DC meter; fixed 512D / 128D random / PCA / Siamese route, exact vs ANN index, 100k / 500k / 1m synthetic vector gallery, confidence intervals, software/model hashes, identical input scenarios and operator-free comparisons. Real biometric scores require an independent scientific/data permission gate. **The physical prototype alone cannot prove model accuracy.**
- **PHY-3 / end-to-end RF + operator:** authorized organizer staff receives synthetic, non-identifying messages; network ACK vs operator ACK logged separately; nuisance rate, missed actionable messages and response delay measured against PHY-0.
- **PHY-4 / site qualification:** 3 candidate event sites if access is granted, repeatable install/removal, legal/venue permission, light/day/night, weather only where applicable; real participant imagery only with written authorization.
- **PHY-5 / commercial experiments:** interviews, artifact review of historical events, written partner terms, paid scope, actual costs/prices and purchase/renewal decisions. A bench cannot replace these.
- **PHY-6 / independent third-party evaluation:** OEM or research sponsor defines test claim, pre-registers method, independent repeat runs, obtains a decision-ready deliverable and (separately) exhibits actual budget.

## Evidence coverage by architecture and its 18 registered experiments

| Experiment | Claim to validate | Physical prototype contribution | Still mandatory external proof | Disposition |
|---|---|---|---|---|
| **O1-D1** | Recurring financially important detection/dispatch gap | **NONE:** the device cannot observe buyer budgets or establish historic pain | 12 multi-event buyer/operator interviews, incident records, budget owners | Discovery before build |
| **O1-D2** | Actionable alerts outperform incumbent workflow | **PARTIAL:** PHY-3 real event receiver, mock/authorized operator response; no face ID | Controlled paired operator workflow vs PHY-0, record false actions and uncertainty | Operator trial |
| **O1-D3** | RF/setup deliver reliable positive unit economics | **PARTIAL:** PHY-1/4 RF, power, mounting data; no price/invoice | Two venue site surveys, vendor quotes, staff/travel costs, priced offer | Paired field + commercial |
| **O2-S1** | Buyer prefers a managed service over rental | **NONE** | Compare real priced offers and commitments from 8 qualified buyers | Discovery |
| **O2-S2** | Managed triage is faster and no less safe | **PARTIAL:** PHY-3 can feed synthetic events | True staffing/dispatch tabletop and paired workflow with operators | Operator/service trial |
| **O2-S3** | Service staffing/SLA contribution can scale | **NONE** for contract/economics; uptime telemetry is an input only | Cost and shift models from 3 integrators, liability, scenario stress, funded contract | Commercial model |
| **O3-V1** | Voluntary 1:1 use case lawful and alternative accessible | **NONE** | Written purpose/site legal assessment + viable equal access route | Legal hard gate |
| **O3-V2** | Users genuinely choose 1:1 instead of QR alternative | **NONE** before permission; UX fixture can be later instrumented | Consented user experiment with genuinely equal alternative, no coercion | Permission first |
| **O3-V3** | 1:1 reduces end-to-end check-in time safely | **PARTIAL only AFTER O3-V1:** device timing/FTA capture | Controlled permitted subject flow vs real QR/staff baseline, queues/exclusions | Consented ops |
| **O4-L1** | OEMs have a make-vs-buy problem worth paying to solve | **NONE** | 10 engineering/procurement interviews + quantified integration costs | Partner discovery |
| **O4-L2** | Reusable module integrates better than COTS | **DIRECT for engineering, PARTIAL for venture:** COTS SoM+MCU/telemetry/radio demo | 2 independent OEM design reviews and COTS alternative comparison | Co-design |
| **O4-L3** | Licensing price/volume/support economics work | **NONE** | Signed NRE or design-in terms, liability/support model, conservative volume | Commercial gate |
| **O5-E1** | Sponsors pay for independent measurement | **NONE** | 6 scoped real sponsor offers, written funded PO/pilot | Paid discovery |
| **O5-E2** | Calibrated independent evidence reproducible | **DIRECT:** PHY-2 + PHY-6 independent repeats and uncertainty | Reviewer signoff, independent meter/calibration and protocol freeze | Technical evidence |
| **O5-E3** | Benchmark changes actual sponsor decision | **PARTIAL:** device produces evidence package | 3 eligible sponsor decision makers document before/after engineering decision | Decision validation |
| **O6-R1** | Institution has lawful specifically authorized mission | **NONE** | Statutory route, named accountable sponsor, formal permissions and independent counsel | Hard STOP until proof |
| **O6-R2** | Scientifically credible low-error 1:N is feasible | **PARTIAL** synthetic 1m throughput and power only; does not estimate real FPIR/FNIR | Approved protected representative biometric test with frozen thresholds and adequate sample; preserve Study 1B firewall | Research only |
| **O6-R3** | Institutional procurement absorbs actual compliance costs | **NONE** | Written funded RFI/contract path, obligations, independent cost review | Procurement validation |

**Coverage count:** 1 direct technical demonstration (O5-E2), 7 partial *conditional* demonstrations (O1-D2/D3, O2-S2, O3-V3, O4-L2, O5-E3, O6-R2), and 10 that primarily demand customer/legal/economic evidence (O1-D1, O2-S1/S3, O3-V1/V2, O4-L1/L3, O5-E1, O6-R1/R3). **Classification reflects ability to collect some evidence; NONE means not sufficient by itself, not that a prototype never helps sales or stakeholder discussion.** O4-L2 also has a direct engineering component but still requires two OEMs to validate licensing value.

## Select tests before custom PCB

| Order | Cheapest learning act | Required artifact | Does it require the bespoke Siamese hardware? |
|---|---|---|---|
| 1 | O1 buyer/operator/venue discovery and historic incident review (H01) | interview notes, identifiable decision owner, disconfirming evidence | **No** |
| 2 | O5 sponsor scoping and O4 OEM interviews (H09 and O4-L1) | written scoped technical problem and possible budget | **No** |
| 3 | Written legal and site constraints for non-biometric O1, voluntary O3 and restricted O6 separately | scope, site permission, DPO reviewer decision | **No**; no 1:N trial until approved |
| 4 | Tabletop operator dispatch vs current radio/stewards, with synthetic messages | observed ACK times, mistakes, workload and alternate causes | **No**; a radio emulator suffices |
| 5 | Fixed PoE/DC COTS rig + standalone MCU + external calibrated meter and basic RF gateway | camera/thermal/power/transport trace, independently measured costs | COTS first, **not custom PCB** |
| 6 | Synthetic 100k–1m exact/ANN search and raw/PCA/random/Siamese computational comparisons | frozen scripts, CPU/NPU compatibility, J/query, memory/latency and negative results | COTS compute + meter only |
| 7 | Indoor/outdoor installation and real-security-operator simulation (no biometric IDs) | setup/maintenance records, practical RF site coverage, purchase-eligible venue report | fixed device prototype yes |
| 8 | Conditional technical license/OEM evaluation or scientific paid pilot | partner acceptance report or purchase order | only after explicit partner request |
| 9 | Legally approved real-biometric research, separated from organizer markets | domain-specific FPIR/FNIR evaluation with independent reviewer | special approval/data; synthetic tests never suffice |

## Pre-registered technical thresholds — illustrative, to freeze with owners before testing

- **RF dispatch (O1-D3 / H06):** target ≥99% console delivery within 10s in a declared RF/site-load condition; count transmitted events, attempts, network receipt, human ACK separately; choose sample size for desired confidence. Alarm distribution is sparse and must not reveal face identity.
- **Operator value (O1-D2 / O2-S2):** target ≥20% faster median triage/ack time versus incumbent workflow with no unacceptable increase in unnecessary interventions; report critical misses. Do not infer from lab packet latency alone.
- **Fixed installation (H05):** target ≤30 min commissioning by trained two-person team in 3 representative permitted sites, with 100% mandatory safety checks, before expensive enclosure iteration.
- **Standalone resilience (H07):** 8h no-WAN/no-PC exercise (not mains disconnection), no unexplained local-log gaps; independently test PoE loss vs data link loss.
- **1m vector search (BR-11):** zero OOM; ≥99.5% ANN recall versus exact baseline, p95 search ≤150 ms — **not** face identification performance.
- **Compression value (BR-12):** target ≥20% reduction in search J/query and ≥10% reduction in total J/accepted event versus matched raw512, with all separately frozen scientific quality constraints met. If extractor/optics dominate end-to-end energy, a negative result is informative and can justify abandoning this route.
- **Thermal/environmental:** no violation of selected manufacturer ratings under approved ambient/solar burden, capture and alert outcomes recorded for sun, night, rain, cold/heat. Actual IP ratings and NIR ocular safety require product-level specialist checks.

These targets are deliberately **NOT measured results**. They are candidate gates to challenge the first versions of the test plan. Do not raise or lower them after viewing the TEST results to manufacture a pass.

## Explicit experiment evidence record schema

`AS_ID → BMC_OPTION_ID → HYPOTHESIS_ID → EXPERIMENT_ID → USE_CASE_ID → BR_ID → CAP_ID → FEATURE_ID → RUN_ID → SITE_PROFILE → MODEL_HASH → GALLERY_HASH/SYNTHETIC_SEED → SENSOR_CALIBRATION_ID → RAW_METER_FILE_SHA → BASELINE_MEASUREMENT → RESULT_WITH_CI → DECISION → REVIEWER → DATE`

For customer/business tests replace `MODEL_HASH` with `INTERVIEW_SCRIPT_VERSION`, `BUYER_ROLE`, `SOURCE_RECORD_ID`, `PRICED_OFFER_VERSION` and `PURCHASE_COMMITMENT`. Don't generate fabricated experiment IDs or pretend interviews occurred.

## Commercial measurement discipline

- **Separate** laboratory power efficiency, contribution margin per event, and sponsor willingness to pay. These are related but not exchangeable.
- A technically superior device can be commercial STOP; a negative compression result can coexist with an attractive sensor-only O1 business model.
- At least one cheaper adequately lawful rival must be run alongside each candidate.
- Never assert regulated 1:N watchlist deployment from a synthetic accuracy result, a government actor, a consent checkbox or an AI Act exception headline.
- **Product marketing is contingent on factual legal review**; avoid projecting institutional restricted-use demand onto civilian event buyers.

## Source documents

- [Ex-ante activity-system model](ACTIVITY_SYSTEM_EX_ANTE_EXPLORATION_V0.md)
- [Venture thesis and gates](VENTURE_THESIS_AND_GATES_V0.md)
- [Existing 16-requirement traceability baseline](BUSINESS_TO_VERIFICATION_TRACEABILITY_V0.csv)
- [Fixed event hardware mission](../hardware/FIXED_EVENT_INSTALLATION_MISSION.md)
- [Radio alert engineering contract](../hardware/LOW_POWER_SECURITY_ALERT_RF_REQUIREMENTS.md)
