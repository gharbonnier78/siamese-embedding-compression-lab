# Study 1B — projet d'amendement de frontière de données

**Date :** 2026-08-28  
**Statut :** DRAFT — NON ACTIF — revue et GO humain requis avant activation  
**Portée :** pré-exécution, sans résultat biométrique SCREEN/TEST

## 1. Motif

Le contrôle pré-exécution a signalé 18 quasi-doublons candidats entre rôles. L'examen déterministe de seconde étape, dont la règle avait été figée avant observation des résultats, classe :

- 16 cas `CLEAR_NOT_DUPLICATE_LIKE` ;
- 1 cas `AMBIGUOUS_REVIEW` ;
- 1 cas `BLOCK_DUPLICATE_LIKE`.

Le cas bloquant satisfait les trois critères figés (NRMSE, corrélation des pixels, corrélation des gradients) entre une capture SCREEN et une capture TRAIN. Le cas ambigu satisfait deux critères sur trois entre TEST et TRAIN.

Les seuils d'examen ne doivent pas être modifiés après cette observation. Le preflight reste donc bloqué.

## 2. Option conservatrice proposée

Avant toute ouverture de résultat Study 1B, mettre en quarantaine **au niveau identité** les quatre identifiants pseudonymisés impliqués dans le cas bloquant et le cas ambigu :

- `subject_1070cf723eb7b93398de` — SCREEN ;
- `subject_97df35f042b9b8c49b8e` — TRAIN ;
- `subject_fb92b5fb0163ff4b3751` — TEST ;
- `subject_815e0549ed1f8d0514b4` — TRAIN.

La quarantaine au niveau identité est volontairement plus conservatrice qu'une suppression de capture : elle évite de conserver une autre capture d'une identité potentiellement affectée par un défaut de séparation des données.

Aucune identité de remplacement ne serait introduite pour retrouver artificiellement les effectifs initiaux. Les effectifs d'identités deviendraient donc :

| Rôle | Avant | Après quarantaine proposée |
|---|---:|---:|
| TRAIN | 2827 | 2825 |
| VALIDATION | 606 | 606 |
| SCREEN | 605 | 604 |
| TEST | 1711 | 1710 |

Les quatre identités concernées n'ont qu'une capture chacune dans le corpus matérialisé. Une vérification de capacité effectuée sans scores biométriques montre que les nombres de paires préenregistrés restent largement réalisables après quarantaine :

| Rôle | Capacité paires genuines | Besoin | Capacité paires imposteurs | Besoin |
|---|---:|---:|---:|---:|
| TRAIN | 174920 | 20000 | 21083540 | 20000 |
| VALIDATION | 34331 | 5000 | 1277059 | 20000 |
| SCREEN | 8386 | 5000 | 944504 | 50000 |
| TEST | 24620 | 10000 | 6844451 | 100000 |

## 3. Conséquence si l'amendement est activé

Après GO explicite et revue de cet amendement :

1. régénérer les quatre graphes de paires à partir des captures restantes, avec la même racine d'aléa et les mêmes règles de construction ;
2. figer et publier les nouveaux hashes de graphes et du manifeste de captures ;
3. refaire l'audit de doublons/quasi-doublons sur la nouvelle frontière ;
4. exiger un preflight sans cas `BLOCK_DUPLICATE_LIKE` ni `AMBIGUOUS_REVIEW` avant les simulations complètes de couverture/puissance ;
5. ne changer ni les effectifs de paires, ni les 10 000 réplications bootstrap, ni les seuils statistiques, ni les cinq graines de qualification.

## 4. Ce que cet amendement ne permet pas

Cet amendement ne constitue pas un GO pour SCREEN ou TEST, ne permet aucune consultation de performance biométrique Study 1B et ne permet pas de lancer les lots complets de couverture/puissance tant que le preflight amendé n'est pas clos.

## 5. Décision requise

Ce document est seulement une proposition pré-exécution. Son activation est un changement matériel de la frontière de données préenregistrée et requiert donc une revue indépendante puis un GO humain explicite. Jusqu'à cette activation éventuelle, la frontière actuelle reste la seule frontière officielle et le preflight reste `BLOCKED`.
