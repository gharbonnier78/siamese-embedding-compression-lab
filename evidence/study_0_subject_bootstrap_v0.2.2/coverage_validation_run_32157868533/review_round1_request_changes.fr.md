# Revue indépendante — round 1 — REQUEST_CHANGES

**Objet :** PR #31 et run de production Study 0 `32157868533`  
**Statut :** résultat de revue conservé tel quel dans son sens ; remédiations en cours  
**Frontière :** ce document ne débloque aucun gate scientifique et ne modifie aucune conclusion Study 0.

## Verdict reçu

`VERDICT: REQUEST_CHANGES`

Le reviewer n'a identifié **aucune anomalie scientifique dans l'arithmétique qu'il a pu recalculer**, mais deux findings bloquants d'intégrité/auditabilité empêchent l'approbation du paquet de preuve et donc le déblocage de `corrected_study_0_reanalysis`.

## Ce que le reviewer a vérifié indépendamment

- ascendance PR #31 et ancrage sur `main` post-PR #30 ;
- run sur `f542962a55a095193539a916705dba85d83f0af9` ;
- contrat et Chronicle identiques au chemin d'exécution autorisé ;
- `decomposed_production_coverage_gate` débloqué et chemin monolithique bloqué ;
- séquence `2000 -> CONTINUE`, `4000 -> STOP`, `10000 -> skipped` ;
- séparation entre stopping MCSE intermédiaire et gate scientifique final ;
- recalcul des 15 lignes depuis les comptes agrégés `(covered, n)` ;
- minimum de borne Clopper-Pearson confirmé à `0.937743380785155` pour `subject_dependence_noninferior / operational_fnmr`, `3781/4000` ;
- PASS arithmétique confirmé sur les agrégats : 15/15 MCSE `<= 0.005`, 15/15 lower bounds `>= 0.93`, zéro dégénérescence déclarée ;
- aucune lecture historique déclarée ;
- claims, erratum, G2 et Study 1 inchangés ;
- `CHRON-20260818-007` OPEN bloque réellement `corrected_study_0_reanalysis` ;
- suite de tests complète : `100/100 OK`.

## Finding bloquant 1 — digest du CSV archivé

Le reviewer a recalculé sur la première version de la PR :

```text
coverage_simulation.csv commité :
816b2f2cd583ef6e982e33a9a799ca42f65832d785cb8b53ecec71251560db28

final_manifest.json attendu :
6904e58a407ee36625ae28242f28a9a12e623f5a5d53755a9dbdecf1d5a1d9a9
```

### Investigation après revue

La cause est maintenant identifiée : **normalisation involontaire des fins de ligne lors du miroir textuel initial**.

Le fichier original issu directement de l'artifact final GitHub Actions fait `2361` octets, utilise `CRLF` sur ses 16 lignes et possède exactement le SHA-256 attendu :

```text
6904e58a407ee36625ae28242f28a9a12e623f5a5d53755a9dbdecf1d5a1d9a9
```

Le même contenu logique converti en `LF` fait `2345` octets et produit exactement le hash observé par le reviewer :

```text
816b2f2cd583ef6e982e33a9a799ca42f65832d785cb8b53ecec71251560db28
```

Il ne s'agissait donc pas d'un changement de résultat scientifique, mais d'une altération byte-level introduite pendant l'archivage. Cette distinction est importante : le manifeste du run était correct, le premier miroir Git ne l'était pas exactement.

### Remédiation appliquée

Le fichier du dépôt a été remplacé par les **octets textuels exacts du fichier original**, en conservant `CRLF`, commit de correction :

`48529a5d3de6c9e4ddb0a1009b1348a5292c083b`

Le reviewer round 2 doit recalculer lui-même le SHA-256 du fichier du dépôt et confirmer `6904e58a...`.

## Finding bloquant 2 — données brutes non accessibles au reviewer

Le reviewer ne pouvait pas accéder aux ZIPs Actions avec son contexte GitHub non authentifié et le dépôt ne contenait pas les `dataset_outcomes.jsonl`. Il a donc explicitement classé comme `NOT_VERIFIED` :

1. le recalcul des 15 lignes depuis les 5 × 4000 outcomes bruts ;
2. l'égalité byte-for-byte des préfixes 2000 -> 4000.

Le reviewer a correctement refusé de transformer le rapport préparatoire en preuve indépendante.

### Remédiation appliquée dans le dépôt

Les cinq manifests du checkpoint 2000, absents du premier archivage, sont maintenant ajoutés :

- `manifest_2000_independent_pair_null.json`
- `manifest_2000_subject_dependence_null.json`
- `manifest_2000_subject_dependence_noninferior.json`
- `manifest_2000_subject_dependence_boundary.json`
- `manifest_2000_subject_dependence_inferior.json`

Ils conservent notamment les SHA-256 exacts des cinq `dataset_outcomes.jsonl` à 2000 nécessaires à la vérification des préfixes.

### Handoff brut requis pour round 2

Le bundle déterministe contenant **les 13 ZIPs originaux exacts** reste l'objet de référence pour la revue brute :

```text
study0_run_32157868533_artifacts.tar.gz
size: 3754871 bytes
sha256: 01fec05bb8f635dec1216ed244c677b9ff3059d83641d3c807b121a923f2f96a
```

Il doit être fourni directement au reviewer round 2 si son accès aux artifacts Actions reste indisponible. Le reviewer doit travailler sur les ZIPs contenus dans ce bundle, vérifier d'abord le SHA du bundle et les 13 SHA des ZIPs contre `archive_manifest.json`, puis refaire les contrôles sur les `dataset_outcomes.jsonl` eux-mêmes.

## Décision après round 1

Le verdict `REQUEST_CHANGES` est accepté.

Aucune tentative n'est faite pour réduire la portée de la revue demandée. `CHRON-20260818-007` reste OPEN et `corrected_study_0_reanalysis` reste bloquée.

Le round 2 doit, au minimum :

1. confirmer le digest réparé de `coverage_simulation.csv` ;
2. vérifier le bundle brut `01fec05bb...` ;
3. recalculer les 15 lignes depuis les outcomes 4000 ;
4. vérifier les cinq préfixes 2000 -> 4000 byte-for-byte ;
5. confirmer les hashes internes des manifests, metadata et progress logs ;
6. confirmer l'absence de données historiques ;
7. rendre un nouveau verdict explicite sur le déblocage de `corrected_study_0_reanalysis`.

## Leçon de méthode

Cette revue illustre précisément l'utilité du harness : un résultat arithmétiquement cohérent ne suffit pas si la chaîne de preuve byte-level n'est pas auditable par le reviewer. Inversement, un digest cassé par une normalisation CRLF/LF ne doit pas être réinterprété comme une anomalie scientifique ; il doit être diagnostiqué, corrigé explicitement et conservé comme incident d'archivage.
