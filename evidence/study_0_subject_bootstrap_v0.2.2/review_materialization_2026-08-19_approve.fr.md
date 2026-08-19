# Revue indépendante formelle — matérialisation Study 0

Date: 2026-08-19
Scope: matérialisation/provenance uniquement, sans interprétation des résultats scientifiques.

## Frontière de résultat

Aucune valeur de résultat scientifique n'a été ouverte ni interprétée pendant cette revue. Les six CSV de résultats ont fait l'objet de vérifications de hash uniquement. Le ZIP historique original n'a pas été extrait et `test_pair_scores.csv` n'a pas été lu ; seules son identité, sa taille et sa présence dans l'archive ont été vérifiées.

## Vérifications

1. Archive historique originale: 4 158 610 octets, SHA-256 `7429c75a7da827281ca172d7a4184c65fcc27dbfa845eb9ffd27e04d81331897`; `test_pair_scores.csv` présent à 1 821 547 octets — CONFIRMED, recalculé sur le fichier réel.
2. Archive de matérialisation corrigée + `run_manifest.json` — CONFIRMED.
3. 13/13 hashes d'artefacts recalculés — CONFIRMED.
4. `run_status=MATERIALIZED_NOT_INTERPRETED`, `scientific_claim_allowed=false`, `interpretation_status=PENDING`, `runner_git_head=8a7f7deca349544667d9766b806dc5fa0d2701c5`, run ID historique, SHA de la source historique, `original_historical_artifacts_mutated=false` — CONFIRMED.
5. Méthode/configuration gelée depuis les métadonnées uniquement — CONFIRMED contre `protocol/studies/study_0_subject_bootstrap_v0.2.2.yaml`.
6. Run interrompu clairement non-concluant, sans manifeste de succès, non réutilisé — CONFIRMED avec réserve cosmétique: vérifié via l'enregistrement de traçabilité JSON, pas par inspection directe du répertoire interrompu.
7. Evidence de couverture known-truth copiée identique bit-à-bit à l'evidence déjà revue/acceptée — CONFIRMED.

## Findings

- BLOCKING: aucun.
- NON_BLOCKING: aucun.
- COSMETIC: item 6 repose sur l'enregistrement de traçabilité plutôt que l'inspection directe du répertoire interrompu; sans conséquence scientifique.

## VERDICT: APPROVE

Cette approbation autorise uniquement l'étape d'interprétation. Elle ne résout ni C-NI-001, ni E-STAT-001, ni G2, et n'autorise ni Study 1 ni l'exploration géométrique.

Historical Study 0 scores/valeurs de résultat scientifique ouverts ou interprétés pendant cette revue: NON.
