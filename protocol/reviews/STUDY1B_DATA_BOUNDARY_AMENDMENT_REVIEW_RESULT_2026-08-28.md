# Study 1B — revue indépendante de l'amendement de frontière de données

**Date :** 2026-08-28  
**Objet :** `protocol/studies/STUDY1B_DATA_BOUNDARY_AMENDMENT_DRAFT_2026-08-28.md`  
**Verdict :** `ACCEPT_WITH_REQUIRED_CHANGES`  
**Nature de la revue :** revue méthodologique indépendante des outcomes biométriques ; aucun score AdaFace, FNMR/FMR Study 1B, ni géométrie de représentation n'a été consulté.

## Conclusion

La mise en quarantaine au niveau identité des quatre identifiants pseudonymisés est scientifiquement acceptable comme correction pré-exécution de la frontière de données. Elle est préférable à une suppression de capture seule car les deux paires litigieuses sont inter-rôles et la contamination potentielle porte sur la séparation de données elle-même.

Le dry-run montre que :

- les quatre identités n'ont qu'une capture chacune ;
- aucun remplacement opportuniste n'est nécessaire ;
- les effectifs préenregistrés de paires restent réalisables dans les quatre rôles ;
- les graphes sont régénérables avec les mêmes règles et la même lignée de hasard ;
- aucun outcome biométrique Study 1B n'a été ouvert ;
- après exclusion, les deux paires litigieuses disparaissent et il reste 16 candidats dHash déjà classés `CLEAR_NOT_DUPLICATE_LIKE` par la règle de seconde étape figée.

La revue humaine du 2026-08-28 a en outre conclu, sur la question limitée « même photographie / dérivé du même cliché ? », que les deux paires litigieuses sont visuellement des doublons. Cette revue humaine ne modifie pas les seuils déterministes et ne cherche pas à identifier les personnes.

## Changements requis avant activation

1. tracer explicitement les quatre identités exclues, leurs rôles et la raison ;
2. inscrire la revue humaine et le GO humain explicite dans la Chronicle ;
3. créer un amendement humain et machine lisible actif, sans réécrire l'historique ;
4. conserver exactement les effectifs de paires préenregistrés, les seeds/RNG, les 10 000 réplications bootstrap et les seuils statistiques ;
5. régénérer le manifeste et les graphes officiels sur la frontière amendée et publier leurs SHA-256 ;
6. rerun l'audit exact + perceptuel sur la frontière amendée avant coverage/power ;
7. ne pas considérer cette activation comme un GO pour SCREEN ou TEST.

Sous réserve de ces changements, verdict final de l'amendement : `ACCEPT`.