# Du REQUEST_CHANGES à APPROVE : renforcer la preuve sans changer le résultat

**Type :** étude de cas pédagogique dérivée  
**Source :** Study 0 v0.2.2, known-truth coverage run `32157868533`, PR #31  
**Statut :** pédagogie, pas outcome evidence  
**Autorité :** artifacts bruts, manifests, contrats, Chronicle et comptes rendus de revue.

## 1. Pourquoi le deuxième verdict est important

Le round 1 avait rendu `REQUEST_CHANGES` alors même que les nombres agrégés semblaient corrects. Deux problèmes empêchaient une approbation indépendante : le CSV archivé n'était pas byte-identique au fichier manifesté à cause d'une conversion CRLF -> LF, et le reviewer n'avait pas accès aux outcomes bruts nécessaires au recalcul demandé.

La réponse n'a pas consisté à réduire l'exigence de revue, à changer le gate, ni à expliquer que « les valeurs sont quand même les mêmes ». Elle a consisté à renforcer la chaîne de preuve : restaurer les octets autoritatifs, ajouter les manifests 2000 manquants, fournir réellement le bundle brut et demander une nouvelle revue depuis zéro.

Le round 2 a alors rendu :

```text
VERDICT: APPROVE
blocking findings: none
non-blocking findings: none
```

Le point essentiel est que **le résultat scientifique n'a pas changé entre les deux rounds**. Ce qui a changé est la capacité d'un tiers à démontrer indépendamment que le résultat est bien celui produit par l'expérience gelée.

## 2. Trois états différents d'une même assertion

Cette séquence permet de distinguer trois niveaux :

```text
Assertion plausible
    -> « les agrégats disent PASS »

Assertion reproductible partiellement
    -> « un tiers recalcule les statistiques depuis covered/n »

Assertion auditée de bout en bout
    -> « un tiers part du bundle brut, vérifie chaque hash,
        recompte chaque outcome et retrouve le même PASS »
```

Ces trois phrases peuvent porter sur le même nombre, mais elles n'ont pas la même force probante.

## 3. Ce que le round 2 a réellement refait

Le reviewer n'a pas simplement relu la remédiation. Il a reçu `study0_run_32157868533_artifacts.tar.gz`, recalculé son SHA-256, puis vérifié chacun des 13 ZIPs contre `archive_manifest.json`.

Il a ensuite ouvert les 10 chunks de scénario 2000/4000 et recalculé les hashes de :

- `dataset_outcomes.jsonl` ;
- `execution_metadata.json` ;
- `progress.jsonl`.

Il a vérifié les champs d'identité d'exécution, l'absence de lecture historique et l'absence de fuite de résultats dans les événements de progression.

Enfin, il a comparé directement les octets des cinq fichiers 2000 aux préfixes correspondants des fichiers 4000, puis recompté les trois booléens de couverture et les dégénérescences sur les 20 000 outcomes bruts.

Ce n'est qu'après cette reconstruction qu'il a recalculé les 15 couvertures, MCSE et bornes Clopper-Pearson et confirmé le PASS.

## 4. Le même nombre, mais désormais une chaîne vérifiée

Le cas à borne la plus faible reste :

```text
subject_dependence_noninferior / operational_fnmr
3781 / 4000
coverage = 0.94525
MCSE = 0.0035969583504677936
lower CP 95% = 0.937743380785155
```

Il n'est pas devenu « plus vrai » parce qu'un reviewer l'a approuvé. Ce qui s'est renforcé est le lien démontré :

```text
run autorisé
 -> artifacts exacts
 -> outcomes exacts
 -> agrégation exacte
 -> statistique exacte
 -> gate preregistré
 -> interprétation bornée
```

## 5. Pourquoi le CRLF/LF était une vraie leçon et non du formalisme

La correction n'a pas consisté à modifier le digest attendu dans le manifeste. Le manifeste du workflow était correct. C'était la copie qui avait dérivé.

Le bon sens de provenance est donc :

```text
source autoritative -> copie
```

et non :

```text
copie modifiée -> réécrire l'identité de la source pour la faire correspondre
```

Cette règle est généralisable à des modèles, datasets, exports CSV, images, rapports et binaires : lorsqu'un artefact est lié par hash, une transformation apparemment innocente doit être explicitée comme transformation, pas masquée comme identité.

## 6. Pourquoi le bundle devait être réellement accessible

Au round 1, nous savions que les ZIPs existaient et nous les avions nous-mêmes contrôlés. Cela n'a pas suffi. L'indépendance de la revue exige que le reviewer puisse inspecter le matériau lui-même.

Le round 2 a donc transformé :

```text
preuve existante mais inaccessible au reviewer
```

en :

```text
preuve effectivement remise, hashée et auditée par le reviewer
```

Cette différence est particulièrement importante dans des environnements industriels où droits d'accès, rétention, réseaux isolés, secrets, stockage objet ou expirations d'artifacts peuvent casser une chaîne d'audit pourtant techniquement « existante ».

## 7. Ce que CHRON-20260819-008 résout — et ce qu'il ne résout pas

La nouvelle entrée append-only ne réécrit pas `CHRON-20260818-007`. Elle la supersède après que la condition annoncée dans son `next_action` a effectivement été satisfaite : revue indépendante complète et verdict APPROVE.

Le blocker de known-truth coverage pour `corrected_study_0_reanalysis` peut donc être libéré.

Mais une autre frontière demeure : **le reviewer n'a pas autorisé la lecture effective des scores historiques**. Il a explicitement indiqué qu'il s'agit d'une décision de gouvernance séparée.

Cette séparation empêche une dérive classique : transformer « le prérequis A est satisfait » en « toutes les étapes B, C et D sont automatiquement autorisées ».

## 8. Leçon réutilisable pour un Research Harness

Une chaîne de preuve robuste devrait permettre de répondre séparément à cinq questions :

1. **Identité** — ai-je le bon run, commit, contrat et dataset ?
2. **Intégrité** — les octets sont-ils ceux qui ont été manifestés ?
3. **Complétude** — ai-je tous les éléments nécessaires pour refaire le contrôle ?
4. **Recalculabilité** — puis-je repartir de la donnée suffisamment basse dans la chaîne ?
5. **Autorité de décision** — ce contrôle autorise-t-il réellement l'étape suivante, et seulement celle-là ?

Le round 2 a fermé les quatre premières questions pour la validation de couverture. La cinquième reste volontairement granulaire : coverage prerequisite satisfait, accès historique encore séparé.

## 9. Pourquoi cette aventure mérite d'être conservée

Si l'on ne conservait que le résultat final `PASS + APPROVE`, on raconterait une histoire artificiellement propre : une méthode, un run, un succès.

La vraie séquence est plus utile : défaut statistique initial, correction de l'unité de resampling, validation à vérité connue, coût de calcul, vectorisation, multiprocess, timeout, décomposition, observabilité, run de production, PASS, premier archivage imparfait, reviewer qui refuse d'approuver, correction de la chaîne de preuve, puis APPROVE indépendant.

C'est précisément cette séquence qui montre comment une conclusion devient progressivement crédible sans que les critères soient déplacés pour obtenir le résultat souhaité.
