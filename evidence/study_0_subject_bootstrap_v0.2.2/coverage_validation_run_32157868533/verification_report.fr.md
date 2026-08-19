# Vérification préparatoire du run de couverture Study 0 — 32157868533

**Statut :** vérification préparatoire conservée pour provenance ; la revue indépendante finale round 2 est désormais `APPROVE` et se trouve dans `review_round2_approve.fr.md`. Cette note ne doit pas être confondue avec cette approbation indépendante.

**Run GitHub Actions :** `32157868533`  
**Commit exécuté :** `f542962a55a095193539a916705dba85d83f0af9`  
**Contrat :** `study_0_subject_bootstrap_coverage_v0_2_2`  
**SHA-256 du contrat :** `0f8c8623f6dc46edd893a48dde3832b0bc08c7b6655f7ef623ba46364c760641`

## 1. Chaîne d'exécution observée

- le preflight d'autorisation a terminé avec succès ;
- les cinq scénarios du checkpoint 2 000 ont terminé avec succès ;
- `precision-decision-2000` a produit `CONTINUE_MCSE_NOT_SATISFIED` ;
- aucun gate final n'a été matérialisé à 2 000 ;
- les cinq scénarios du checkpoint 4 000 ont terminé avec succès ;
- `precision-decision-4000` a produit `STOP_MCSE_SATISFIED` ;
- `Final coverage gate 4000` a terminé avec succès ;
- le checkpoint 10 000 et son gate ont été correctement ignorés.

La séquence respecte la règle preregistrée : sélectionner le premier checkpoint parmi `2000, 4000, 10000` pour lequel les 15 MCSE sont toutes `<= 0.005`.

## 2. Résultat final

`coverage_gate.json` déclare :

- `status = PASS` ;
- `selected_dataset_checkpoint = 4000` ;
- `bootstrap_replicates_per_dataset = 10000` ;
- `lower_bound_minimum = 0.93` ;
- `maximum_monte_carlo_standard_error = 0.005` ;
- `degenerate_dataset_tolerance = 0` ;
- `historical_study_0_scores_read = false` ;
- `production_coverage_gate_executed = true`.

Les 15 lignes de `coverage_simulation.csv` respectent chacune les trois conditions du gate : MCSE `<= 0.005`, borne inférieure Clopper–Pearson `>= 0.93`, et zéro dataset dégénéré.

Le cas avec la borne inférieure la plus basse dans **ce run** est :

- scénario : `subject_dependence_noninferior` ;
- métrique : `operational_fnmr` ;
- datasets simulés : `4000` ;
- couverts : `3781` ;
- couverture empirique : `0.94525` ;
- MCSE : `0.0035969583504677936` ;
- borne inférieure Clopper–Pearson 95 % : `0.937743380785155`.

Cette désignation « cas le plus difficile » est empirique et bornée à ce run : elle signifie seulement « marge la plus faible vis-à-vis du seuil de couverture ». Elle ne signifie pas que ce scénario est théoriquement le plus difficile pour toute procédure ni qu'il est le cas le plus délicat pour la décision de non-infériorité. Pour cette dernière, le scénario `subject_dependence_boundary` est conceptuellement central parce qu'il place `Delta_FNMR = 0.03` exactement sur la marge gelée.

## 3. Intégrité des cinq chunks 4 000

Chaque manifest de scénario déclare :

- `complete = true` ;
- `outcome_count = 4000` ;
- `dataset_start = 0`, `dataset_stop = 4000` ;
- `bootstrap_replicates = 10000` ;
- `engine = vectorized` ;
- `reference_oracle_engine = legacy` ;
- `workers = 4` ;
- `root_seed = 20260807` ;
- `historical_study_0_scores_read = false` ;
- `historical_study_0_scores_permitted = false` ;
- `progress_runtime_observability_only = true`.

Les SHA-256 internes de `dataset_outcomes.jsonl`, `execution_metadata.json` et `progress.jsonl` ont été vérifiés contre les manifests lors de l'inspection préparatoire. Le round 2 a ensuite refait ces contrôles indépendamment sur le bundle brut.

## 4. Propriété de préfixe 2 000 -> 4 000

Les 2 000 premiers outcomes du chunk 4 000 ont été comparés **octet pour octet** au `dataset_outcomes.jsonl` du checkpoint 2 000 correspondant :

- `independent_pair_null` : PASS — `2d759f498bbc3767a213647454f2ca5a7378684ba0fb2f60434cd7d0a4fcb6d7`
- `subject_dependence_null` : PASS — `232d2c809acd73391b2adcfb70656fc5f674dbe89b716a715f66084076a43f7e`
- `subject_dependence_noninferior` : PASS — `cee6bdb219ff53936659b4b8fd525072380e23ab9ccef1a58d602bb1ff6c03f5`
- `subject_dependence_boundary` : PASS — `a79485cd92d0e7b0a1995b896a66f81e8cb14c778592859096793905746ea540`
- `subject_dependence_inferior` : PASS — `29d083357771e06fc9d902c45c56fd04c5403f9c9a0e3924fb33c3b6b08a8da8`

Le round 2 a confirmé les cinq égalités directement sur les octets bruts, et pas uniquement par comparaison de hashes.

## 5. Intégrité de l'artefact final

Le manifest final lie :

- `coverage_gate.json` à `91b82f4584393256e86743be29c79af84bbbff9b89165735c2dd655b33edc0c5` ;
- `coverage_simulation.csv` à `6904e58a407ee36625ae28242f28a9a12e623f5a5d53755a9dbdecf1d5a1d9a9`.

Le premier miroir Git du CSV avait accidentellement normalisé CRLF -> LF ; le round 1 l'a détecté. Les octets CRLF originaux ont été restaurés et le round 2 a recalculé le SHA attendu ci-dessus.

Le ZIP final GitHub Actions est lui-même lié à :

`106d08bc771a66fccdcc5f925223e9d10f5be738619b80541a77cf0f207d6c3f`

## 6. Revue indépendante finale

Le round 2 a effectivement reçu le bundle brut de 13 ZIPs, confirmé son SHA-256 `01fec05bb8f635dec1216ed244c677b9ff3059d83641d3c807b121a923f2f96a`, confirmé 13/13 ZIPs, les hashes internes des dix chunks, les cinq préfixes, puis recompté les 20 000 outcomes bruts.

Les 15 lignes ont été recomputées indépendamment depuis les outcomes et correspondent exactement à `coverage_simulation.csv`. Zéro dégénérescence a été retrouvée. Verdict : **APPROVE, aucun finding bloquant ou non bloquant**.

## 7. Frontière scientifique

Le résultat validé et désormais indépendamment revu est borné à ceci : **la procédure d'intervalle subject-bootstrap satisfait le contrat de known-truth coverage sur les cinq scénarios et les trois métriques preregistrées, au checkpoint sélectionné 4 000**.

Ce résultat ne démontre pas encore :

- la non-infériorité de `siamese128` face à `raw512` ;
- la supériorité de `siamese128` sur `pca128` ou `random128` ;
- une validité biométrique industrielle ;
- la fermeture de `E-STAT-001` ;
- le passage de G2 ;
- le démarrage de Study 1.

`CHRON-20260819-008` résout le blocker de revue de coverage. La lecture effective des scores historiques reste une décision de gouvernance séparée et n'a pas eu lieu pendant cette validation ni pendant ses revues.
