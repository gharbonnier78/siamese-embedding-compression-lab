# Archive durable — Study 0 coverage validation run 32157868533

Cette arborescence conserve le résultat de la campagne de validation de couverture connue avant la réanalyse historique Study 0.

## Autorité et statut

- run : `32157868533` ;
- commit : `f542962a55a095193539a916705dba85d83f0af9` ;
- résultat observé : `PASS` au checkpoint 4 000 ;
- revue indépendante : **PENDING** au moment de l'archivage ;
- scores historiques Study 0 lus : **non** ;
- réanalyse historique autorisée : **non**.

## Contenu lisible directement

- `coverage_gate.json` — copie octet-identique du gate final ;
- `coverage_simulation.csv` — les 15 résultats scénario x métrique ;
- `final_manifest.json` — manifest final ;
- `precision_decision_2000.json` et `precision_decision_4000.json` — stopping rule ;
- `manifest_4000_*.json` — manifests des cinq chunks finaux ;
- `verification_report.fr.md` — vérification préparatoire et frontière d'interprétation ;
- `archive_manifest.json` — inventaire exact des 13 artifacts GitHub Actions ;
- `review_request.fr.md` — contrat de revue indépendante.

## Conservation exacte des 13 artifacts Actions

Les 13 ZIPs téléchargés depuis GitHub Actions ont été vérifiés contre les digests GitHub et emballés **sans modification** dans un tar.gz déterministe. Son SHA-256 est :

`01fec05bb8f635dec1216ed244c677b9ff3059d83641d3c807b121a923f2f96a`

Le connecteur GitHub utilisé pendant cette session sait versionner du texte UTF-8 mais ne sait pas téléverser ce payload binaire. Le dépôt conserve donc durablement :

- l'inventaire exact des 13 artifacts avec IDs, tailles et SHA-256 ;
- les sorties finales lisibles ;
- les décisions MCSE ;
- les cinq manifests 4 000 ;
- les checks de préfixe et d'intégrité ;
- le récit Chronicle/pédagogique.

Le bundle binaire exact `study0_run_32157868533_artifacts.tar.gz` est fourni séparément comme handoff afin de pouvoir être ajouté ultérieurement à une release ou un stockage pérenne. Tant que les artifacts GitHub Actions ne sont pas expirés, le reviewer doit préférer les artifacts originaux du run pour la vérification indépendante.

## Pourquoi conserver aussi le récit pédagogique ?

Un replay numérique sans contexte ne permet pas de reconstruire les erreurs de raisonnement évitées : unité d'observation, dépendance par sujet, sens de la couverture, différence entre validation de l'instrument et non-infériorité 128D, deux sens du « cas difficile », contraintes de calcul, correction multiprocess, limite GitHub de six heures, decomposition et séparation observabilité/science.

L'étude de cas associée dans `pedagogy/case-studies/coverage-validation-metrologie-statistique.fr.md` conserve cette couche de compréhension sans devenir une nouvelle source de vérité scientifique.
