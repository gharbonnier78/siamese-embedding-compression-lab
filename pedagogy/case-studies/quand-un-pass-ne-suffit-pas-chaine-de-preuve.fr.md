# Quand un PASS ne suffit pas : la chaîne de preuve fait partie du résultat

**Type :** étude de cas pédagogique dérivée  
**Source :** Study 0 v0.2.2, run de known-truth coverage `32157868533`, PR #31  
**Statut :** pédagogie, pas outcome evidence  
**Autorité :** les artifacts originaux, contrats, manifests, Chronicle et verdicts de review restent autoritatifs.

## Pourquoi conserver cet épisode

La campagne de couverture a produit un résultat arithmétiquement favorable. Le premier reviewer a confirmé l'ascendance d'autorisation, le stopping rule, les agrégats, la valeur minimale de borne Clopper-Pearson, la frontière historique et 100/100 tests. Pourtant son verdict a été :

```text
REQUEST_CHANGES
```

Ce n'est pas une contradiction.

Le reviewer a séparé deux questions :

1. **les nombres visibles sont-ils cohérents ?** — oui, sur ce qu'il pouvait recalculer ;
2. **la chaîne de preuve permet-elle de reproduire indépendamment ces nombres depuis la donnée brute et de vérifier son intégrité byte-level ?** — pas encore complètement.

Cette distinction est une leçon générale de recherche reproductible.

## 1. Cinq niveaux qui ne doivent pas être confondus

Un résultat scientifique reproductible peut être vu comme une pile :

```text
interprétation scientifique
        ^
statistique / décision
        ^
agrégats calculés
        ^
données brutes / outcomes
        ^
provenance + identité + intégrité des octets
```

Un niveau supérieur peut être parfaitement plausible alors qu'une rupture existe plus bas.

Dans notre cas, l'arithmétique des agrégats était correcte, mais le reviewer ne pouvait pas retracer cette arithmétique jusqu'aux `dataset_outcomes.jsonl` et a trouvé un digest incohérent dans le miroir Git d'un CSV.

Il était donc rationnel de ne pas approuver.

## 2. Le piège CRLF/LF : même tableau, fichier différent

Le workflow avait généré `coverage_simulation.csv` avec des fins de ligne `CRLF`.

Fichier original :

```text
2361 octets
SHA-256 = 6904e58a407ee36625ae28242f28a9a12e623f5a5d53755a9dbdecf1d5a1d9a9
```

Lors du premier archivage textuel dans Git, les fins de ligne ont été normalisées en `LF`.

Le contenu tabulaire était visuellement et sémantiquement identique, mais le fichier faisait alors :

```text
2345 octets
SHA-256 = 816b2f2cd583ef6e982e33a9a799ca42f65832d785cb8b53ecec71251560db28
```

Pourquoi ?

Il y avait 16 fins de ligne. `CRLF` occupe deux octets (`\r\n`) alors que `LF` en occupe un (`\n`). La différence de taille est donc exactement 16 octets.

Le hash n'est pas un résumé de la **signification logique du CSV**. C'est un résumé des **octets exacts**.

### Leçon

Deux fichiers peuvent produire exactement le même DataFrame et pourtant être différents pour une preuve d'intégrité.

C'est précisément ce que l'on veut d'un digest cryptographique : il doit détecter toute modification byte-level, même bénigne du point de vue sémantique.

Le mauvais réflexe aurait été :

> « Ce ne sont que des fins de ligne, ignorons le finding. »

Le bon réflexe est :

> « Expliquons exactement pourquoi le digest diffère, restaurons les octets autoritatifs et faisons recalculer le hash par le reviewer. »

Aucun changement du manifeste scientifique n'était nécessaire : le manifeste original était correct ; c'était la copie qui avait dérivé.

## 3. Pourquoi le reviewer n'a pas accepté notre rapport de vérification

Le rapport préparatoire disait que les cinq préfixes 2000 -> 4000 avaient été vérifiés byte-for-byte et que les 15 lignes avaient été recomputées depuis les outcomes.

Mais le reviewer n'avait pas accès aux outcomes bruts.

Il aurait pu dire :

> « Le rapport affirme PASS, donc je coche PASS. »

Il ne l'a pas fait.

Il a correctement classé ces assertions comme :

```text
NOT_VERIFIED
```

C'est exactement ce qu'est une revue indépendante : ne pas transformer l'affirmation du producteur de preuve en preuve indépendante.

## 4. « Disponible quelque part » n'est pas « auditable »

Les ZIPs existaient toujours dans GitHub Actions et nous avions nous-mêmes pu les télécharger avec un connecteur authentifié.

Mais le reviewer travaillait avec un accès GitHub non authentifié/rate-limité. Pour lui, les données brutes étaient effectivement indisponibles.

Cette situation montre une différence souvent oubliée :

```text
existence de l'evidence != accessibilité de l'evidence != auditabilité indépendante
```

Une preuve à laquelle seul le producteur peut accéder est plus faible, pour une revue indépendante, qu'une preuve durablement accessible au reviewer.

### Conséquence opérationnelle

L'archivage scientifique doit penser non seulement à :

- conserver ;
- hasher ;
- versionner ;

mais aussi à :

- **rendre effectivement accessible au reviewer le matériau nécessaire au recalcul.**

Cela peut demander un dépôt, une Release, un object store durable, une pièce jointe ou un autre canal contrôlé.

## 5. Pourquoi nous ne réduisons pas l'exigence de revue après coup

Une réaction tentante aurait été de modifier la demande de revue :

> « Puisque les agrégats sont cohérents, ne demandons finalement plus le recalcul brut. »

Ce serait méthodologiquement mauvais.

La demande initiale avait explicitement exigé :

- recomputation depuis les `dataset_outcomes.jsonl` ;
- égalité byte-for-byte des préfixes 2000 -> 4000 ;
- vérification des hashes internes.

Ces exigences ont été posées parce qu'elles protègent contre des erreurs réelles : mauvaise agrégation, fichier incomplet, mélange de checkpoints, réexécution non déterministe, modification de données, etc.

Le fait qu'elles deviennent gênantes au moment de la revue n'est pas une raison valable pour les supprimer.

Le gate reste donc bloqué.

## 6. Le résultat du reviewer est lui-même une donnée scientifique/process importante

Le harness exige de conserver les difficultés, objections et changements de croyance qui comptent.

Le round 1 nous apprend au moins trois choses :

1. **le calcul semble robuste sur les agrégats**, car un reviewer indépendant a reproduit les 15 statistiques à partir des comptes ;
2. **notre premier archivage n'était pas byte-exact**, malgré notre intention ;
3. **notre canal de conservation n'était pas suffisant pour une revue brute indépendante dans l'environnement réel du reviewer**.

Le deuxième et le troisième points ne sont pas des détails administratifs. Ils affectent directement la force de la chaîne de preuve.

## 7. Ce qui a été corrigé — et ce qui reste volontairement ouvert

Après le round 1 :

- le CSV a été restauré avec ses fins de ligne CRLF exactes ;
- les cinq manifests 2000 ont été ajoutés ;
- le verdict REQUEST_CHANGES a été archivé ;
- une demande de revue round 2 a été créée ;
- le bundle déterministe des 13 ZIPs originaux reste disponible comme handoff brut ;
- `CHRON-20260818-007` reste OPEN ;
- `corrected_study_0_reanalysis` reste bloquée.

Ce que nous **n'avons pas** fait :

- remplacer silencieusement l'ancien rapport ;
- effacer le finding ;
- changer le seuil de gate ;
- lire les scores historiques ;
- déclarer la non-infériorité ;
- transformer un résultat de review gênant en finding « non bloquant ».

## 8. La symétrie avec l'épisode précédent

Un épisode précédent avait montré :

> **engineering correctness can become scientific correctness**

quand le multiprocess, les RNG et le scheduling peuvent changer l'expérience.

Ce nouvel épisode ajoute :

> **evidence engineering can become scientific auditability**

quand une normalisation de fichier ou un canal inaccessible empêche de vérifier indépendamment ce qui a été exécuté.

Dans les deux cas, le problème n'est pas cosmétique : il touche le lien entre une assertion et la preuve qui la supporte.

## 9. Une grille simple à réutiliser

Avant de déclarer une preuve « archivée », poser cinq questions :

### Identité

Est-ce exactement le bon run, commit, contrat et checkpoint ?

### Intégrité

Les octets présents sont-ils ceux que les manifests hashent ?

### Complétude

Le reviewer possède-t-il les données nécessaires pour refaire les contrôles demandés ?

### Reproductibilité

Peut-il recalculer la statistique ou au moins la partie déclarée reproductible ?

### Accessibilité

Peut-il réellement ouvrir la preuve dans son environnement, sans devoir croire celui qui l'a produite ?

Une réponse « non » à la dernière question peut rendre inutiles les quatre premières pour une revue indépendante.

## 10. Où se trouve le vrai progrès scientifique ?

Le progrès n'est pas que le reviewer dise « PASS ».

Le progrès est que chaque couche soit suffisamment explicite pour permettre au reviewer de dire, avec justification :

- **APPROVE**, ou
- **REQUEST_CHANGES**.

Le round 1 est donc un bon résultat du système de gouvernance scientifique, même si ce n'est pas le verdict souhaité à court terme.

Il a empêché de confondre :

```text
« les nombres semblent corrects »
```

avec :

```text
« la preuve complète de ces nombres a été auditée indépendamment ».
```

C'est exactement la différence que le Chronicle et le harness cherchent à préserver.
