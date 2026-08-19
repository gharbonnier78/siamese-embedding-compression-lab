# Archive durable — Study 0 coverage validation run 32157868533

Cette arborescence conserve le résultat, les incidents d'archivage, les deux rounds de revue et la couche pédagogique de la campagne de validation de couverture connue avant toute lecture des scores historiques Study 0.

## Autorité et statut

- run : `32157868533` ;
- commit exécuté : `f542962a55a095193539a916705dba85d83f0af9` ;
- résultat : **PASS** au checkpoint 4 000 ;
- revue indépendante round 1 : **REQUEST_CHANGES** ;
- revue indépendante round 2 : **APPROVE**, aucun finding restant ;
- intégrité brute : **13/13 ZIPs, hashes internes, 5/5 préfixes et 15/15 recomputations confirmés indépendamment** ;
- scores historiques Study 0 lus : **non** ;
- prérequis known-truth coverage pour `corrected_study_0_reanalysis` : **satisfait** ;
- accès effectif aux scores historiques : **non encore autorisé — décision de gouvernance séparée**.

## Contenu lisible directement

- `coverage_gate.json` — copie octet-identique du gate final ;
- `coverage_simulation.csv` — copie byte-exacte CRLF du CSV autoritatif ;
- `final_manifest.json` — manifest final ;
- `precision_decision_2000.json` et `precision_decision_4000.json` — stopping rule ;
- `manifest_2000_*.json` et `manifest_4000_*.json` — manifests des dix chunks de scénario ;
- `archive_manifest.json` — inventaire exact des 13 artifacts et statut de revue ;
- `verification_report.fr.md` — vérification préparatoire, qui ne remplace pas la revue ;
- `review_round1_request_changes.fr.md` — premier verdict et findings conservés ;
- `review_round2_request.fr.md` — contrat de re-review ;
- `review_round2_approve.fr.md` — verdict final indépendant et contrôles réellement refaits.

## Conservation exacte des 13 artifacts Actions

Les 13 ZIPs téléchargés depuis GitHub Actions ont été emballés **sans modification** dans un tar.gz déterministe :

```text
study0_run_32157868533_artifacts.tar.gz
size = 3754871 bytes
sha256 = 01fec05bb8f635dec1216ed244c677b9ff3059d83641d3c807b121a923f2f96a
```

Le round 2 a effectivement reçu ce bundle, recalculé son SHA-256, confirmé les 13 SHA-256 des ZIPs puis audité les outcomes bruts. Le connecteur GitHub utilisé pour versionner ce dépôt ne téléverse pas directement ce binaire ; le dépôt conserve donc son identité cryptographique, l'inventaire exact, les manifests, résultats et comptes rendus de revue. Le bundle reste un handoff séparé à verser ultérieurement dans une Release ou un stockage pérenne si souhaité.

## Incident CRLF/LF conservé

Le premier miroir Git de `coverage_simulation.csv` avait normalisé les fins de ligne CRLF en LF. Les valeurs étaient identiques mais le fichier n'était plus byte-identique au manifest. Le round 1 l'a détecté et a refusé l'approbation. Le fichier a été restauré avec les octets CRLF d'origine ; le round 2 a recalculé et confirmé le SHA-256 autoritatif :

`6904e58a407ee36625ae28242f28a9a12e623f5a5d53755a9dbdecf1d5a1d9a9`

Cet incident n'est pas effacé : il fait partie de la provenance de la preuve.

## Frontière scientifique

Le résultat validé et revu est strictement :

> la procédure d'intervalle subject-bootstrap satisfait le contrat preregistré de known-truth coverage sur les cinq scénarios synthétiques et les trois métriques au checkpoint sélectionné 4 000.

Il ne démontre toujours pas la non-infériorité 512D -> 128D, la supériorité de `siamese128`, la fermeture de `E-STAT-001`, le passage de G2 ou l'autorisation de Study 1.

`CHRON-20260819-008` résout le blocker de revue de couverture sans réécrire `CHRON-20260818-007`. Une décision séparée reste requise avant d'ouvrir les scores historiques.

## Pourquoi conserver aussi le récit pédagogique ?

Un replay numérique sans contexte ne permet pas de reconstruire les erreurs de raisonnement évitées : unité d'observation, dépendance par sujet, sens fréquentiste de la couverture, vérité synthétique, différence entre validation de l'instrument et non-infériorité 128D, contraintes de calcul, multiprocess, limite de six heures, décomposition, observabilité sans fuite scientifique, puis distinction entre cohérence arithmétique et auditabilité byte-level.

Les études de cas `coverage-validation-metrologie-statistique.fr.md` et `quand-un-pass-ne-suffit-pas-chaine-de-preuve.fr.md` conservent cette couche de compréhension sans devenir de nouvelles sources de vérité scientifique.
