# Study 1B — amendement actif de frontière de données

**Date :** 2026-08-28  
**Statut :** `ACTIVE_PREOUTCOME_DATA_BOUNDARY`  
**Portée :** correction pré-exécution uniquement ; aucun GO SCREEN/TEST  
**Supersède pour la frontière de données :** `STUDY1B_DATA_BOUNDARY_AMENDMENT_DRAFT_2026-08-28.md`

## Décision

Après contrôle déterministe, revue visuelle humaine limitée à la question « même photographie / dérivé du même cliché ? », dry-run non-outcome et revue indépendante, les quatre identités pseudonymisées suivantes sont exclues de la frontière Study 1B active :

- `subject_1070cf723eb7b93398de` — SCREEN — paire bloquante SCREEN/TRAIN, 3/3 critères figés ; doublon visuel confirmé ;
- `subject_97df35f042b9b8c49b8e` — TRAIN — même paire bloquante ;
- `subject_fb92b5fb0163ff4b3751` — TEST — paire initialement ambiguë TEST/TRAIN, 2/3 critères figés ; doublon visuel confirmé ;
- `subject_815e0549ed1f8d0514b4` — TRAIN — même paire initialement ambiguë.

L'exclusion est au niveau identité. Aucune identité de remplacement n'est introduite.

## Frontière amendée

| Rôle | Identités actives |
|---|---:|
| TRAIN | 2825 |
| VALIDATION | 606 |
| SCREEN | 604 |
| TEST | 1710 |

Les effectifs de paires restent inchangés : TRAIN 20k/20k, VALIDATION 5k/20k, SCREEN 5k/50k, TEST 10k/100k (genuine/impostor).

Les seeds, la racine d'aléa, la règle de génération des graphes, les seuils statistiques, les cinq graines de qualification et les 10 000 réplications bootstrap restent inchangés.

## Evidence du dry-run ayant précédé l'activation

Capacités après exclusion :

- TRAIN : 174920 genuine / 21083540 impostor ;
- VALIDATION : 34331 / 1277059 ;
- SCREEN : 8386 / 944504 ;
- TEST : 24620 / 6844451.

Hashes proposés par le dry-run :

- manifeste captures : `767f9fe8d1d8466a0e722f826b26875a0e852f525f7413a9658a307a9639366e` ;
- TRAIN : `a0951ead4109d615d6854b7e60cc16d62319ae828137d160d3e08f5e669d0706` ;
- VALIDATION : `fb849558e0b09b0fa7ff301991af010815f0b4ee98ab62faa1c585477f9f8601` ;
- SCREEN : `c0d36757121f54c4585d2298a1b02c401606ce939c7be2bedd070c03adf233f7` ;
- TEST : `08c86ca9a641fc96b74014ae1974f713cd00e558dd98946ac32ff440c4666f85`.

Ces hashes deviennent autoritatifs uniquement s'ils sont reproduits par le preflight actif après activation.

## Gate suivant

Le preflight actif doit maintenant rematérialiser la frontière amendée, reproduire les hashes attendus, refaire l'audit exact + perceptuel et confirmer que les 16 candidats restants sont tous `CLEAR_NOT_DUPLICATE_LIKE`. Coverage/power restent bloqués jusqu'à ce PASS. SCREEN et TEST restent interdits.