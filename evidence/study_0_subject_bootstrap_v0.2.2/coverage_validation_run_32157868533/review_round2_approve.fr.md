# Revue indépendante — round 2 — APPROVE

**Objet :** PR #31 et run de production Study 0 `32157868533`  
**Statut :** revue indépendante finale du paquet de known-truth coverage  
**Frontière :** cette revue valide la chaîne de preuve du coverage gate ; elle ne conclut pas encore sur la non-infériorité 512D -> 128D et n'autorise pas à elle seule la lecture des scores historiques.

## Verdict

`VERDICT: APPROVE`

Aucun finding bloquant. Aucun finding non bloquant.

## Handoff brut effectivement contrôlé

Le reviewer a reçu et ouvert le bundle déterministe des 13 artifacts GitHub Actions :

```text
study0_run_32157868533_artifacts.tar.gz
size: 3754871 bytes
sha256: 01fec05bb8f635dec1216ed244c677b9ff3059d83641d3c807b121a923f2f96a
```

Le SHA-256 a été recalculé par le reviewer sur le fichier effectivement reçu et correspond à l'attendu.

## Intégrité des artifacts

- 13/13 ZIPs présents ;
- 13/13 SHA-256 recalculés et identiques à `archive_manifest.json` ;
- pour les 10 ZIPs scénario 2000/4000, les SHA de `dataset_outcomes.jsonl`, `execution_metadata.json` et `progress.jsonl` ont été recalculés et correspondent aux manifests internes ;
- `complete=true`, plages d'indices attendues, `workers=4`, `engine=vectorized`, oracle `legacy`, `root_seed=20260807`, 10 000 bootstrap replicates : confirmés ;
- `historical_study_0_scores_read=false` et `historical_study_0_scores_permitted=false` : confirmés ;
- les événements `progress.jsonl` sont `runtime_observability_only=true` et ne contiennent aucune clé de résultat scientifique.

Les cinq manifests 4000 versionnés dans le dépôt ont été confirmés identiques octet pour octet à ceux extraits des artifacts bruts.

## Réparation du CSV confirmée

Le finding bloquant du round 1 sur le miroir textuel est fermé.

Le reviewer a recalculé :

```text
coverage_simulation.csv
sha256 = 6904e58a407ee36625ae28242f28a9a12e623f5a5d53755a9dbdecf1d5a1d9a9
```

Cette valeur correspond désormais au `final_manifest.json`. La cause du mismatch précédent était bien la normalisation CRLF -> LF du premier miroir Git ; aucune valeur scientifique n'avait changé.

## Préfixes 2000 -> 4000

Les cinq comparaisons ont été refaites directement sur les octets bruts : le fichier `dataset_outcomes.jsonl` 2000 est exactement égal au préfixe constitué des 2 000 premières lignes du fichier 4000 correspondant.

Résultat : **5/5 CONFIRMED byte-for-byte**.

Les SHA-256 recalculés correspondent aux valeurs annoncées :

- `independent_pair_null`: `2d759f498bbc3767a213647454f2ca5a7378684ba0fb2f60434cd7d0a4fcb6d7`
- `subject_dependence_null`: `232d2c809acd73391b2adcfb70656fc5f674dbe89b716a715f66084076a43f7e`
- `subject_dependence_noninferior`: `cee6bdb219ff53936659b4b8fd525072380e23ab9ccef1a58d602bb1ff6c03f5`
- `subject_dependence_boundary`: `a79485cd92d0e7b0a1995b896a66f81e8cb14c778592859096793905746ea540`
- `subject_dependence_inferior`: `29d083357771e06fc9d902c45c56fd04c5403f9c9a0e3924fb33c3b6b08a8da8`

## Recalcul des 15 résultats depuis les outcomes bruts

Le reviewer a recompté ligne par ligne les booléens `representation_covered`, `operational_fnmr_covered`, `operational_fmr_covered` et `degenerate` sur les 5 × 4000 = 20 000 enregistrements bruts du checkpoint 4000.

Pour chacune des 15 combinaisons scénario × métrique, il a recalculé :

```text
p = covered / 4000
MCSE = sqrt(p * (1-p) / 4000)
borne inférieure Clopper-Pearson exacte deux côtés 95 %
```

Résultat : **15/15 lignes identiques à `coverage_simulation.csv`**.

Les 15 gates passent séparément, sans pooling :

- `MCSE <= 0.005` ;
- `lower_95_binomial_bound >= 0.93` ;
- `degenerate_datasets == 0`.

Zéro dataset dégénéré a été confirmé directement sur les 20 000 outcomes bruts.

La borne la plus faible est retrouvée exactement pour :

```text
subject_dependence_noninferior / operational_fnmr
covered = 3781 / 4000
empirical_coverage = 0.94525
MCSE = 0.0035969583504677936
lower_95_binomial_bound = 0.937743380785155
```

## Stopping rule

Reconfirmé depuis les artifacts :

```text
2000 -> CONTINUE_MCSE_NOT_SATISFIED
4000 -> STOP_MCSE_SATISFIED
10000 -> skipped
```

Le gate scientifique final n'a été matérialisé qu'à 4000.

## Gouvernance et frontières

Le reviewer a également reconfirmé :

- run head `f542962a55a095193539a916705dba85d83f0af9`, correspondant à la fusion de PR #30 ;
- chemin décomposé autorisé ;
- chemin monolithique toujours bloqué par `CHRON-20260818-006` ;
- `CHRON-20260818-007` encore OPEN pendant la revue ;
- `corrected_study_0_reanalysis` encore bloquée pendant la revue ;
- suite de tests complète : `100/100 OK` ;
- aucun score historique Study 0 lu ;
- claims, erratum, G2 et Study 1 inchangés.

## Conclusion scientifique bornée

Le reviewer confirme le PASS suivant :

> La procédure d'intervalle subject-bootstrap satisfait le contrat de known-truth coverage sur les cinq scénarios synthétiques et les trois métriques preregistrés au checkpoint 4000.

Ce PASS ne signifie toujours pas :

- non-infériorité de `siamese128` face à `raw512` ;
- supériorité sur PCA ou projection aléatoire ;
- fermeture immédiate de `E-STAT-001` ;
- G2 PASS ;
- autorisation de Study 1.

## Décision de gate demandée

Le reviewer conclut :

> **`corrected_study_0_reanalysis` peut être débloquée du point de vue de la validation indépendante du known-truth coverage.**

Il précise toutefois que la lecture effective des scores historiques Study 0 reste une décision de gouvernance distincte, qui n'était pas couverte par cette revue.
