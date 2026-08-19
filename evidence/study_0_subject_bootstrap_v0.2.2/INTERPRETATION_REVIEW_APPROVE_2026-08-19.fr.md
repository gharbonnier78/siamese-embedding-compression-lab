# Revue indépendante — interprétation Study 0 corrigée

Date : 2026-08-19
Verdict : **APPROVE**

## Frontière de revue

Cette revue intervient après l'APPROVE indépendant de la matérialisation `MATERIALIZED_NOT_INTERPRETED`. Le reviewer a donc ouvert et analysé les données de résultat du bundle déjà matérialisé uniquement pour vérifier l'interprétation proposée.

## Vérifications numériques indépendantes

Le reviewer a recalculé les valeurs citées dans `INTERPRETATION_DRAFT_2026-08-19.md` depuis les fichiers de résultat matérialisés et a confirmé :

- deltas ponctuels Siamese : `+0.034, +0.064, -0.006, +0.050, +0.010` ;
- moyennes bootstrap Siamese : `+0.0392, +0.0438, +0.0024, +0.0372, +0.0113` ;
- UCB 97,5 % Siamese : `0.176584` à `0.189156` ;
- UCB 97,5 % PCA : `0.125556` à `0.133606` ;
- UCB 97,5 % random : `0.112649` à `0.151768` ;
- non-infériorité : `0/5` seeds passent pour chacune des trois routes 128D ;
- largeurs d'intervalle pair-level vs subject-level : environ `1.57x / 1.52x / 1.54x` pour random / PCA / Siamese, cohérent avec l'arrondi `~1.55x` du brouillon ;
- tableau de transfert opérationnel recalculé depuis `threshold_transfer_uncertainty.csv`, avec `threshold_source=validation` sur toutes les lignes examinées.

Vérifications méthodologiques supplémentaires :

- `delta_fnmr_ucb_97_5 == delta_fnmr_ci_high` sur les 15 lignes ;
- convergence 2000 → 5000 → 10000 stable, avec dérive seulement de l'ordre de `0.001–0.002` entre checkpoints successifs ;
- aucune requalification abusive du tableau opérationnel en classement equal-FMR.

## Évaluation du raisonnement

Le reviewer confirme que le document :

- distingue correctement `non-inferiority NOT_DEMONSTRATED` de `inferiority proven` ;
- maintient `C-SUP-001 = NOT_DEMONSTRATED` sans créer une règle de supériorité post hoc ;
- ne transforme pas les résultats à seuils VALIDATION gelés en comparaison equal-FMR ;
- ne marque pas G2 PASS avant revue ;
- ne ferme E-STAT-001 qu'après acceptation indépendante ;
- maintient Study 1 et la géométrie hors du périmètre de cette interprétation.

## Findings

- **BLOCKING** : aucun.
- **NON_BLOCKING** : aucun.
- **COSMETIC** : aucun.

## VERDICT: APPROVE

L'interprétation est fidèle aux données sous-jacentes et reste bornée par la règle de décision gelée.

Décisions autorisées par cette revue :

- `C-NI-001`: reste `NOT_DEMONSTRATED` ;
- `C-SUP-001`: reste `NOT_DEMONSTRATED` ;
- `E-STAT-001`: peut passer à `REANALYZED` ;
- `G2 estimator_and_statistical_validity`: peut passer à `PASS` pour la réanalyse Study 0 corrigée ;
- cette fermeture ne valide ni ne rouvre les claims négatifs ci-dessus ;
- Study 1 reste une décision de gouvernance distincte ;
- géométrie reste hors périmètre.

Prochaine action autorisée par le reviewer : enregistrer la décision terminale append-only dans la Chronicle, mettre à jour `claims/registry.yaml` et ajouter la résolution d'E-STAT-001 sans réécrire l'historique original.
