# Demande de revue indépendante — round 2 après REQUEST_CHANGES

Merci de reprendre la revue de PR #31 **depuis son head courant**, sans hériter automatiquement d'un verdict favorable ou défavorable du round 1.

Le round 1 a rendu `REQUEST_CHANGES` pour deux raisons précises :

1. le miroir Git de `coverage_simulation.csv` ne correspondait pas byte-for-byte au digest du manifeste ;
2. les données brutes `dataset_outcomes.jsonl` n'étaient pas accessibles au reviewer, donc le recalcul depuis les outcomes et l'égalité des préfixes 2000 -> 4000 restaient `NOT_VERIFIED`.

Le résultat scientifique historique reste interdit pendant cette revue.

## Remédiation 1 — CSV exact

L'investigation a établi que la première copie Git avait normalisé les fins de ligne `CRLF` du fichier produit par le workflow en `LF`.

- SHA du miroir LF rejeté au round 1 :
  `816b2f2cd583ef6e982e33a9a799ca42f65832d785cb8b53ecec71251560db28`
- SHA du CSV original contenu dans l'artifact final :
  `6904e58a407ee36625ae28242f28a9a12e623f5a5d53755a9dbdecf1d5a1d9a9`
- commit de réparation :
  `48529a5d3de6c9e4ddb0a1009b1348a5292c083b`

Merci de **recalculer toi-même** le SHA-256 du fichier actuel du dépôt et de confirmer qu'il vaut désormais `6904e58a...`. Ne te contente pas du texte de cette demande.

## Remédiation 2 — manifests 2000 et bundle brut

Les cinq manifests de scénario du checkpoint 2000 ont été ajoutés au dépôt :

- `manifest_2000_independent_pair_null.json`
- `manifest_2000_subject_dependence_null.json`
- `manifest_2000_subject_dependence_noninferior.json`
- `manifest_2000_subject_dependence_boundary.json`
- `manifest_2000_subject_dependence_inferior.json`

Un **handoff binaire séparé** doit également t'être fourni avec cette demande :

`study0_run_32157868533_artifacts.tar.gz`

Avant toute lecture du contenu, vérifie :

```text
size = 3754871 bytes
sha256 = 01fec05bb8f635dec1216ed244c677b9ff3059d83641d3c807b121a923f2f96a
```

Ce bundle contient exactement les 13 ZIPs téléchargés du run Actions `32157868533`. Vérifie les 13 SHA-256 de ZIP contre `archive_manifest.json` avant de les considérer comme evidence.

## Contrôles round 2 obligatoires

### 1. Revalider l'identité et la gouvernance

- PR #31 basée sur `main` post-PR #30 ;
- run `32157868533` ;
- run head `f542962a55a095193539a916705dba85d83f0af9` ;
- contrat `EXECUTION_AUTHORIZED` ;
- chemin décomposé autorisé ;
- monolithique toujours bloqué ;
- `CHRON-20260818-007` reste OPEN pendant cette revue ;
- `corrected_study_0_reanalysis` doit rester bloquée jusqu'au verdict.

### 2. Vérifier le CSV réparé

Recalculer les SHA-256 du fichier courant :

- `coverage_simulation.csv` doit être `6904e58a407ee36625ae28242f28a9a12e623f5a5d53755a9dbdecf1d5a1d9a9` ;
- `coverage_gate.json` doit rester `91b82f4584393256e86743be29c79af84bbbff9b89165735c2dd655b33edc0c5`.

Confirmer que `final_manifest.json` correspond à ces deux digests.

### 3. Vérifier le bundle brut

Après vérification du SHA du tar.gz puis des 13 ZIPs, ouvrir directement les artifacts.

Pour chacun des 10 ZIPs de scénario 2000/4000 :

- recalculer le SHA de `dataset_outcomes.jsonl` ;
- recalculer le SHA de `execution_metadata.json` ;
- recalculer le SHA de `progress.jsonl` ;
- comparer aux valeurs du `manifest.json` contenu dans le même ZIP ;
- vérifier `complete=true` ;
- vérifier la plage d'indices attendue ;
- vérifier `workers=4`, `engine=vectorized`, oracle `legacy`, root seed `20260807`, 10 000 bootstraps ;
- vérifier `historical_study_0_scores_read=false` et `historical_study_0_scores_permitted=false` ;
- vérifier que les événements de progress sont `runtime_observability_only=true` et n'exposent aucune clé de résultat scientifique.

### 4. Vérifier les cinq préfixes 2000 -> 4000

Pour chaque scénario, les octets complets du `dataset_outcomes.jsonl` 2000 doivent être exactement égaux aux octets formés par les 2000 premières lignes, fins de ligne incluses, du `dataset_outcomes.jsonl` 4000.

Les SHA attendus sont :

- `independent_pair_null`: `2d759f498bbc3767a213647454f2ca5a7378684ba0fb2f60434cd7d0a4fcb6d7`
- `subject_dependence_null`: `232d2c809acd73391b2adcfb70656fc5f674dbe89b716a715f66084076a43f7e`
- `subject_dependence_noninferior`: `cee6bdb219ff53936659b4b8fd525072380e23ab9ccef1a58d602bb1ff6c03f5`
- `subject_dependence_boundary`: `a79485cd92d0e7b0a1995b896a66f81e8cb14c778592859096793905746ea540`
- `subject_dependence_inferior`: `29d083357771e06fc9d902c45c56fd04c5403f9c9a0e3924fb33c3b6b08a8da8`

Ces valeurs sont des assertions à vérifier depuis le bundle, pas des prémisses.

### 5. Recalculer les 15 résultats depuis les outcomes bruts

À partir des cinq `dataset_outcomes.jsonl` 4000, recompter séparément :

- `representation_covered` ;
- `operational_fnmr_covered` ;
- `operational_fmr_covered` ;
- les datasets `degenerate`.

Pour chaque combinaison scénario × métrique :

```text
p = covered / 4000
MCSE = sqrt(p * (1-p) / 4000)
```

Recalculer également la borne inférieure Clopper-Pearson exacte deux côtés 95 % et comparer les 15 lignes obtenues à `coverage_simulation.csv`.

Puis appliquer le gate séparément à chaque ligne :

```text
MCSE <= 0.005
lower_95_binomial_bound >= 0.93
degenerate_datasets == 0
```

Aucun pooling n'est autorisé.

Le résultat précédemment observé est `PASS`; le cas à borne la plus faible annoncé est `subject_dependence_noninferior / operational_fnmr`, `3781/4000`, `0.94525`, MCSE `0.0035969583504677936`, lower `0.937743380785155`. Vérifie-le sans le supposer.

### 6. Revalider le stopping rule

Confirmer à nouveau :

- 2000 = `CONTINUE_MCSE_NOT_SATISFIED` ;
- pas de gate final 2000 ;
- 4000 = `STOP_MCSE_SATISFIED` ;
- gate final exécuté seulement à 4000 ;
- 10000 skipped.

### 7. Frontière scientifique

Même si le round 2 confirme le PASS, confirmer explicitement que ce PASS signifie uniquement :

> la procédure d'intervalle subject-bootstrap satisfait le contrat de known-truth coverage dans les cinq scénarios synthétiques et trois métriques preregistrés.

Il ne signifie toujours pas :

- non-infériorité 512D -> 128D ;
- supériorité du Siamese sur PCA/random ;
- fermeture immédiate de `E-STAT-001` ;
- G2 PASS ;
- autorisation de Study 1.

## Verdict demandé

Répondre avec :

- `VERDICT: APPROVE` ou `REQUEST_CHANGES` ;
- findings bloquants ;
- findings non bloquants ;
- SHA du bundle effectivement contrôlé ;
- résultat des 13 SHA de ZIP ;
- résultat des hashes internes ;
- résultat des 5 comparaisons de préfixe ;
- table ou synthèse des 15 recomputations depuis les outcomes bruts ;
- confirmation/infirmation du PASS ;
- confirmation/infirmation de la réparation du CSV ;
- phrase explicite : **`corrected_study_0_reanalysis` peut / ne peut pas être débloquée.**

Si le bundle joint n'est pas réellement accessible dans ton environnement, ne remplace pas cette étape par les agrégats : retourne une limitation explicite.
