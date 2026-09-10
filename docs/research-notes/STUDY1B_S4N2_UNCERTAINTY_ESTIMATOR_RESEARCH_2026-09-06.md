# Study 1B S4N2 — uncertainty-estimator research basis

Date: 2026-09-06

Status: **NON-OUTCOME METHODOLOGICAL NOTE**

This note supports prospective S4N2 design only. It does not reopen S4N1, activate an amendment,
or inspect Study 1B SCREEN/TEST route outcomes.

## 1. Problem localized by the archived S4N1 diagnostic

S4N1 remains `CLOSED_NEGATIVE`. At exact synthetic TEST truth `Delta_FNMR = 0.01`, the three
frozen selection rules produced power between 0.8655 and 0.8695 against the prospectively frozen
0.90 requirement. The post-closure diagnostic found:

- selected-artifact TEST point-estimation error mean close to zero;
- only 0.004 absolute power range among the three selectors;
- repeated-sampling point-error SD around 0.0051;
- median current UCB97.5 headroom around 0.0140;
- one-sided upper coverage around 0.9963–0.9975;
- an archived-generator headroom scale of roughly 0.941–0.946 would have reached 0.90 power.

This localizes S4N2 to uncertainty estimation or genuinely additional independent information. It
does **not** authorize scaling the existing UCB after observing S4N1.

## 2. External evidence reviewed

### NIST biometric ROC/FMR/FNMR uncertainty work

NISTIR 7449 studies non-parametric two-sample bootstrap uncertainty for operational ROC
measurement, specifically true-accept performance at a specified false-accept operating point.
It also discusses threshold ties and bootstrap replication variability.

Source: Jin Chu Wu, *Studies of Operational Measurement of ROC Curve on Large Fingerprint Data
Sets Using Two-Sample Bootstrap*, NISTIR 7449 (2007),
https://doi.org/10.6028/NIST.IR.7449

NISTIR 7740 compares confidence intervals for biometric FAR/FRR using sampling-variance,
binomial, and non-parametric bootstrap approaches and explicitly validates variance estimators
against variance observed over repeated experiments. That repeated-experiment comparison is
methodologically close to the known-truth calibration role used here, although the NIST data
structure is not identical to Study 1B's identity-dependent graph.

Source: Su L. Cheng, Ross J. Micheals, Z. Q. John Lu, *Comparison of Confidence Intervals for
Large Operational Biometric Data by Parametric and Non-parametric Methods*, NISTIR 7740
(2010), https://www.nist.gov/publications/comparison-confidence-intervals-large-operational-biometric-data-parametric-and-non

NIST's operational ROC significance-test work also uses bootstrap standard errors for comparison
of a matcher against a hypothesized value or another matcher while accounting for correlation.

Source: Wu, Martin, Kacker, Hagwood, *Significance Test in Operational ROC Analysis* (2010),
https://www.nist.gov/publications/significance-test-operational-roc-analysis

These sources support the general use of repeated-experiment validation and dependence-aware ROC
uncertainty analysis. They do **not** establish conformity of Study 1B or validate the exact S4N2
estimator proposed below.

### Resampling-unit structure and conservative variance

Owen's pigeonhole-bootstrap work shows that the choice of resampling unit matters for crossed or
graph-like random-effects data and notes that the proposed resampling variance can overestimate a
random-effects variance by an asymptotically negligible amount. Study 1B is not the same crossed
bipartite design, so this is a warning and analogy rather than a direct theorem for the current
subject-slot bootstrap.

Source: Art B. Owen, *The Pigeonhole Bootstrap*, Annals of Applied Statistics 1(2), 386–411
(2007), DOI 10.1214/07-AOAS122.

### Jackknife / delete-a-group variance estimation

The delete-a-group jackknife (DAGJK) is an established replication approach for variance
estimation when full leave-one-unit-out recomputation is expensive. It partitions primary units
into mutually exclusive groups, deletes one group at a time, and recomputes the complete
estimation procedure. Its attraction for Study 1B is that an **identity** can remain the primary
resampling unit while the full nonlinear equal-FMR statistic—including threshold re-estimation—can
be recomputed in each replicate.

Source: Phillip S. Kott, *The Delete-a-Group Jackknife*, Journal of Official Statistics 17(4),
521–526 (2001), summary at https://www.rti.org/publication/delete-group-jackknife

Related methodological literature on U-statistics supports jackknife variance estimation for
statistics built from pairwise kernels, while dyadic-data literature emphasizes that observations
sharing an endpoint can be dependent. These results motivate, but do not by themselves prove,
validity for Study 1B's equal-FMR difference statistic with threshold ties.

For this reason **synthetic known-truth coverage remains a mandatory gate** rather than treating
DAGJK theory as sufficient proof.

## 3. Prospective S4N2 estimator direction

The preferred methodological candidate to freeze and calibrate is an identity-level
**delete-20-group jackknife**:

1. retain the unchanged unbootstrapped paired equal-FMR `Delta_FNMR` point estimate;
2. deterministically partition TEST identities into 20 nearly equal groups without using scores or
   outcomes;
3. delete one identity group at a time, removing every genuine or impostor edge touching a deleted
   identity;
4. recompute candidate and raw thresholds separately at FMR 0.01 with the same whole-tie-block
   semantics and recompute `Delta_FNMR`;
5. estimate variance from the 20 delete-group replicates;
6. form the one-sided 97.5% upper bound using a Student-t critical value with 19 degrees of
   freedom.

Why 20 groups: it reduces the roughly 1,710 full leave-one-identity recomputations to 20 while
keeping identities—not individual pairs—as the deleted primary units. Twenty is frozen for the
first S4N2 candidate; it will not be tuned after synthetic results.

## 4. What S4N2 is not allowed to do

S4N2 must not:

- replace 97.5% by 95% because the latter looked favorable in the S4N1 diagnostic;
- multiply the old UCB by the observed 0.94–0.95 headroom factor;
- pick the least-failing S4N1 selector post hoc;
- treat pair rows as independent observations;
- claim the DAGJK estimator is valid solely because it is established in other domains;
- open any real Study 1B performance outcome.

The candidate earns eligibility only by passing a newly frozen known-truth coverage/power
contract.
