# Demande de revue indépendante — Study 0 known-truth coverage run 32157868533

Je te demande une **revue indépendante et evidence-based** du paquet de validation de couverture Study 0 v0.2.2. Merci de ne pas prendre le statut vert GitHub ni mon interprétation comme preuve suffisante : pars des contrats, artefacts et hashes.

## Objet exact de la revue

Déterminer si le run GitHub Actions `32157868533`, exécuté sur le commit `f542962a55a095193539a916705dba85d83f0af9`, constitue une exécution valide du contrat `study_0_subject_bootstrap_coverage_v0_2_2` et si le résultat final `PASS` est supporté par les artefacts sans violation de la frontière préhistorique.

Cette revue **ne doit pas** décider encore si la compression 512D -> 128D est non-inférieure. Les scores historiques Study 0 doivent rester non lus.

## Sources à considérer

1. `protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml`
2. `protocol/studies/study_0_subject_bootstrap_spec.md`
3. `protocol/scientific_chronicle.yaml`
4. `.github/workflows/production-subject-bootstrap-coverage-decomposed-candidate.yml`
5. `scripts/preflight_decomposed_coverage.py`
6. `scripts/run_subject_bootstrap_coverage_scenario.py`
7. `scripts/aggregate_subject_bootstrap_coverage_checkpoint.py`
8. `scripts/finalize_subject_bootstrap_coverage.py`
9. `src/siamese_compression_lab/decomposed_coverage.py`
10. `src/siamese_compression_lab/coverage_execution.py`
11. `src/siamese_compression_lab/coverage_simulation.py`
12. le run Actions `32157868533` et ses 13 artifacts ;
13. l'archive de conservation proposée dans cette PR, sous `evidence/study_0_subject_bootstrap_v0.2.2/coverage_validation_run_32157868533/`.

## Contrôles obligatoires

### A. Identité d'exécution

- workflow dispatch manuel avec confirmation explicite ;
- run ID exact `32157868533` ;
- branche `main` ;
- head SHA exact `f542962a55a095193539a916705dba85d83f0af9` ;
- contrat `EXECUTION_AUTHORIZED` ;
- `decomposed_production_coverage_gate` non bloqué ;
- chemin monolithique toujours bloqué par `CHRON-20260818-006`.

### B. Respect du stopping rule

- cinq scénarios complets à 2 000 ;
- décision 2 000 = `CONTINUE_MCSE_NOT_SATISFIED` ;
- aucun gate final exécuté à 2 000 ;
- cinq scénarios complets à 4 000 ;
- décision 4 000 = `STOP_MCSE_SATISFIED` ;
- 10 000 correctement skipped ;
- aucun checkpoint n'a été choisi après inspection d'un résultat substantif ; l'agrégation intermédiaire n'expose que le signal stop/continue MCSE.

### C. Intégrité des artifacts

- 13 artifacts attendus ;
- vérifier leurs SHA-256 GitHub contre `archive_manifest.json` ;
- chaque chunk 4 000 doit déclarer `complete=true`, `outcome_count=4000`, indices canoniques 0..3999, `workers=4`, `engine=vectorized`, oracle `legacy`, root seed `20260807`, 10 000 bootstraps ;
- recalculer les SHA-256 internes de `dataset_outcomes.jsonl`, `execution_metadata.json` et `progress.jsonl` et les comparer au manifest ;
- vérifier `historical_study_0_scores_read=false` et `historical_study_0_scores_permitted=false` partout où applicable ;
- vérifier que `runtime_observability_only=true` ne porte pas de clé de résultat scientifique dans les logs de progression.

### D. Préfixe déterministe

Pour chaque scénario, comparer le `dataset_outcomes.jsonl` du checkpoint 2 000 aux 2 000 premières lignes du chunk 4 000. L'égalité doit être byte-for-byte.

Les SHA attendus de ces préfixes sont :

- `independent_pair_null`: `2d759f498bbc3767a213647454f2ca5a7378684ba0fb2f60434cd7d0a4fcb6d7`
- `subject_dependence_null`: `232d2c809acd73391b2adcfb70656fc5f674dbe89b716a715f66084076a43f7e`
- `subject_dependence_noninferior`: `cee6bdb219ff53936659b4b8fd525072380e23ab9ccef1a58d602bb1ff6c03f5`
- `subject_dependence_boundary`: `a79485cd92d0e7b0a1995b896a66f81e8cb14c778592859096793905746ea540`
- `subject_dependence_inferior`: `29d083357771e06fc9d902c45c56fd04c5403f9c9a0e3924fb33c3b6b08a8da8`

### E. Recalcul scientifique du gate

Ne te contente pas de `coverage_gate.json`.

À partir des cinq `dataset_outcomes.jsonl` 4 000 :

- recompter les trois booléens de couverture par scénario ;
- recalculer `empirical_coverage` ;
- recalculer `MCSE = sqrt(p*(1-p)/N)` ;
- recalculer la borne inférieure exacte binomiale Clopper–Pearson deux côtés 95 % ;
- vérifier zéro dataset dégénéré ;
- comparer les 15 lignes à `coverage_simulation.csv` ;
- appliquer le gate séparément, sans pooling : MCSE `<=0.005`, lower bound `>=0.93`, degeneracy = 0.

Le résultat préalablement observé est `PASS`, checkpoint sélectionné 4 000. Le cas dont la borne inférieure est la plus basse dans ce run est `subject_dependence_noninferior / operational_fnmr` avec :

- `covered = 3781 / 4000` ;
- couverture empirique `0.94525` ;
- MCSE `0.0035969583504677936` ;
- lower bound `0.937743380785155`.

Merci de considérer ces chiffres comme **des assertions à vérifier**, pas comme des prémisses.

### F. Archive durable

Vérifier l'inventaire et la frontière de conservation :

- `archive_manifest.json` doit lister les 13 artifacts, leurs IDs, tailles et SHA-256 ;
- les sorties finales et décisions MCSE versionnées dans le dépôt doivent correspondre aux artifacts originaux ;
- les cinq manifests 4 000 doivent conserver les hashes des outcomes, métadonnées et progress logs ;
- un bundle tar.gz déterministe de tous les ZIPs originaux a été construit avec SHA-256 `01fec05bb8f635dec1216ed244c677b9ff3059d83641d3c807b121a923f2f96a` ; le connecteur de cette session ne pouvant pas pousser le binaire, l'archive Git conserve le manifeste/digests et le bundle reste un handoff séparé. Tant que les artifacts Actions sont vivants, privilégier leur contenu original pour l'audit.

### G. Frontière d'interprétation

Confirmer explicitement que, même si le gate de known-truth coverage passe :

- `E-STAT-001` n'est pas encore fermé ;
- G2 n'est pas encore passé ;
- `C-NI-001` reste `NOT_DEMONSTRATED` ;
- `C-SUP-001` reste `NOT_DEMONSTRATED` ;
- aucun score historique n'a été lu ;
- la réanalyse historique ne doit être autorisée qu'après ta revue ;
- Study 1 reste non démarrée.

## Format de verdict demandé

Merci de répondre avec :

- `VERDICT: APPROVE` ou `REQUEST_CHANGES` ;
- findings bloquants, s'il y en a, chacun avec preuve précise ;
- findings non bloquants séparés ;
- résultats des recomputations indépendantes ;
- confirmation ou infirmation du PASS de couverture ;
- confirmation de l'intégrité de l'archive ;
- une phrase explicite indiquant si `corrected_study_0_reanalysis` peut être débloqué.

Si un point ne peut pas être vérifié, préfère `REQUEST_CHANGES` ou une limitation explicite à une approbation implicite.
