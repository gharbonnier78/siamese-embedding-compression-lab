# Study 1B — demande de revue indépendante du projet d'amendement de frontière de données

**Date :** 2026-08-28  
**Objet revu :** `protocol/studies/STUDY1B_DATA_BOUNDARY_AMENDMENT_DRAFT_2026-08-28.md`  
**Statut de l'amendement :** DRAFT — NON ACTIF

## Question de revue

Le contrôle pré-exécution a identifié, selon une règle déterministe figée avant observation, un quasi-doublon candidat bloquant entre SCREEN et TRAIN et un cas ambigu entre TEST et TRAIN. Est-il scientifiquement et statistiquement acceptable, avant toute ouverture de résultat biométrique Study 1B, de mettre en quarantaine au niveau identité les quatre identifiants pseudonymisés impliqués, sans les remplacer, tout en conservant les effectifs préenregistrés de paires et en régénérant les graphes/hashes ?

## Points à challenger explicitement

Le reviewer doit notamment vérifier :

- que la quarantaine est une correction de frontière de données pré-exécution et non une sélection guidée par des résultats biométriques ;
- que l'exclusion au niveau identité est suffisamment conservatrice par rapport à une exclusion de capture ;
- qu'il n'est pas préférable de bloquer complètement Study 1B ou d'utiliser une autre frontière publique préexistante ;
- que l'absence de remplacement d'identités évite une nouvelle sélection opportuniste ;
- que les capacités de paires après exclusion restent suffisantes pour les effectifs préenregistrés ;
- que les nouvelles tailles d'identités TRAIN/SCREEN/TEST doivent être explicitement amendées dans le protocole machine et humain ;
- que les seeds/RNG et la règle de génération des graphes restent suffisamment bien définies après changement du corpus ;
- qu'un nouveau contrôle exact + perceptuel doit être exécuté sur la frontière amendée avant toute simulation complète de couverture/puissance ou tout outcome biométrique.

## Evidence non-outcome disponible

- 18 quasi-doublons candidats au premier filtre dHash64 ;
- 16 écartés par la seconde règle ;
- 1 cas `AMBIGUOUS_REVIEW` ;
- 1 cas `BLOCK_DUPLICATE_LIKE` satisfaisant 3/3 critères ;
- les quatre identités concernées n'ont qu'une capture chacune ;
- après leur quarantaine, les capacités de paires restent supérieures aux besoins préenregistrés dans les quatre rôles ;
- aucun score AdaFace, FNMR/FMR Study 1B SCREEN/TEST ni géométrie de représentation n'a été consulté.

## Verdict demandé

`ACCEPT`, `ACCEPT_WITH_REQUIRED_CHANGES` ou `REJECT`, avec justification et liste explicite des changements requis. Aucune activation automatique de l'amendement ne doit résulter de cette revue : un GO humain explicite restera requis.
