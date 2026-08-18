# Étude de cas pédagogique — Pourquoi valider la couverture avant de croire un intervalle à 95 %

**Type :** étude de cas pédagogique dérivée du Scientific Research Harness  
**Source :** Siamese Embedding Compression Lab — Study 0 v0.2.2  
**Langue :** français dans le texte  
**Statut :** artefact d'apprentissage dérivé, **pas une preuve de résultat**  
**Frontière d'autorité :** le protocole gelé, le code, les tests, les artefacts du run et la Scientific Chronicle restent les sources d'autorité. Ce document explique le raisonnement ; il ne libère aucun gate.

## 1. Pourquoi cette note existe

Le chemin Study 0 a produit un apprentissage qui serait très facile à perdre si l'on ne conservait que le fichier final `coverage_gate.json`.

Au départ, le problème paraissait simple : comparer une représentation faciale brute de 512 dimensions à plusieurs projections 128 dimensions, dont une projection linéaire entraînée de façon siamoise. L'analyse historique avait utilisé un bootstrap sur les indices de paires et avait été décrite trop fortement comme « identity-aware ». Une revue méthodologique a ensuite fait apparaître `E-STAT-001` : plusieurs paires LFW partagent des identités, donc les observations ne sont pas indépendantes au niveau « paire ». Le bon objet de rééchantillonnage devait être le **sujet**, pas la paire.

Cette correction introduisait cependant une nouvelle question : même si le bootstrap par sujets paraît mieux adapté, **est-ce que les intervalles qu'il produit ont réellement la couverture qu'ils annoncent dans notre problème précis ?**

La réponse ne pouvait pas être supposée. Elle devait être testée avant d'ouvrir les résultats historiques.

## 2. Un intervalle à 95 % est une propriété d'une procédure

Un intervalle de confiance n'est pas fiable parce qu'il porte l'étiquette « 95 % ». Le sens fréquentiste de cette étiquette est une propriété de répétition : si l'on répétait l'expérience complète dans les mêmes conditions, la procédure devrait produire un intervalle contenant la vraie valeur environ 95 % du temps.

En notation compacte :

```text
P_theta(theta appartient a C(X)) ~= 0.95
```

La quantité `C(X)` est une **procédure aléatoire** construite à partir des données `X`. Ce qui doit être validé n'est donc pas seulement une valeur numérique observée une fois, mais le comportement de la procédure sur des répétitions de l'expérience.

Dans un cas régulier, certaines garanties asymptotiques peuvent être suffisantes. Ici, plusieurs complications s'empilent :

- une même identité apparaît dans plusieurs comparaisons ;
- les poids bootstrap sont induits par les multiplicités de sujets ;
- une paire imposteur porte un poids `m_i * m_j` ;
- le graphe LFW observé est sparse et ne contient pas toutes les paires possibles ;
- le seuil de représentation est lui-même choisi sous contrainte de FMR ;
- il existe des blocs d'égalité de distances et une règle sentinel ;
- le nombre d'imposteurs observés est seulement 500 ;
- candidate et référence sont corrélés ;
- les métriques finales sont des taux d'erreur et une différence de taux, pas une simple moyenne gaussienne.

Dans ce contexte, « utiliser le bootstrap » n'est pas une preuve que l'intervalle a la bonne couverture.

## 3. D'où vient cette logique dans les références du protocole

La spécification Study 0 v0.2.2 fixe comme fondation méthodologique :

1. Bolle, Ratha & Pankanti, *Error Analysis of Pattern Recognition Systems — The Subsets Bootstrap*, CVIU, 2004 ;
2. Poh & Bengio, *Estimating the Confidence Interval of Expected Performance Curve in Biometric Authentication Using Joint Bootstrap*, ICASSP, 2007 ;
3. ISO/IEC 19795-1:2021 pour la frontière générale d'évaluation et de reporting des performances biométriques.

Le protocole précise volontairement que notre **protocol-preserving weighted subject-slot bootstrap adapted to the sparse symmetric LFW pair graph** est une adaptation fondée sur des principes publiés de rééchantillonnage par sujets/subsets, et non une reproduction verbatim d'un algorithme de ces articles.

Cette nuance est importante : reprendre un principe reconnu ne dispense pas de vérifier que l'adaptation conserve les propriétés attendues dans le problème concret.

## 4. La « toise » de référence : une vérité synthétique connue par construction

Parler de « calibration » peut induire une mauvaise image si l'on imagine que nous avons ajusté la méthode après avoir vu les résultats. Ce n'est pas ce qui a été fait. Le terme précis est **validation de couverture**.

La toise n'est pas un fichier historique caché. Elle est mathématique : pour chaque scénario synthétique, le générateur fixe des paramètres dont on peut dériver les vraies quantités d'intérêt avant de générer le moindre dataset fini.

La fonction `scenario_truth(...)` calcule notamment :

- le vrai seuil de référence ;
- le vrai seuil candidat ;
- le vrai FNMR de référence ;
- le vrai FNMR candidat ;
- le vrai `Delta_FNMR` ;
- le vrai FMR opérationnel.

Le simulateur génère ensuite un dataset fini à partir de ce monde connu. L'estimateur n'utilise pas la vérité analytique pour construire son intervalle. Après calcul, on regarde simplement si la vérité connue tombe entre les quantiles 2,5 % et 97,5 % des 10 000 réplications bootstrap.

Autrement dit :

```text
vérité connue du générateur
          |
          v
  dataset fini simulé
          |
          v
subject-bootstrap x 10 000
          |
          v
intervalle percentile 95 %
          |
          v
la vérité connue est-elle dedans ?  oui / non
```

Un dataset simulé produit donc un indicateur binaire de couverture. Des milliers de datasets indépendants permettent d'estimer la fréquence de succès de cette procédure.

## 5. Quelle est exactement notre « règle de mesure » ?

La règle n'est pas une simple graduation. C'est une chaîne de mesure statistique :

1. tirer avec remise `N = 963` slots sujets ;
2. compter la multiplicité `m_i` de chaque identité ;
3. donner à une paire genuine `(i,i)` le poids `m_i` ;
4. donner à une paire imposteur `(i,j)` le poids `m_i * m_j` ;
5. ne jamais synthétiser une arête absente du protocole LFW observé ;
6. calculer FMR et FNMR pondérés ;
7. pour l'estimand de représentation, choisir le plus grand seuil observé dont le bloc complet d'égalités garde `FMR <= 0.01`, avec la règle sentinel si aucun seuil observé n'est admissible ;
8. utiliser exactement le même tirage sujet pour candidate et référence ;
9. répéter 10 000 fois ;
10. former l'intervalle percentile à 95 %.

Pour la sensibilité opérationnelle, le seuil est au contraire gelé depuis VALIDATION et n'est jamais recalibré avec TEST.

## 6. Que mesure-t-on et dans quelles unités ?

Les distances d'embedding sont des nombres sans unité physique dans l'espace de représentation. Elles servent à ordonner les comparaisons et à définir des seuils.

Les grandeurs scientifiques principales sont des proportions :

- **FMR** : False Match Rate, proportion d'imposteurs acceptés à tort ;
- **FNMR** : False Non-Match Rate, proportion de genuines rejetés à tort ;
- **Delta_FNMR** : différence absolue entre deux FNMR.

On peut les exprimer en proportion ou en pourcentage. Ainsi `FMR = 0.01` signifie 1 %. Une marge `Delta_FNMR = 0.03` signifie **3 points de pourcentage absolus de FNMR**, pas « 3 % relatif ».

Les trois métriques dont la couverture est validée séparément sont :

- `representation_delta_fnmr` ;
- `operational_fnmr` ;
- `operational_fmr`.

## 7. Pourquoi il y avait un vrai risque de « mauvaise règle »

Le défaut historique `E-STAT-001` est précisément un exemple de ce risque. Le bootstrap par paires pouvait sous-estimer ou mal caractériser l'incertitude parce qu'il traitait comme unités séparées des observations partageant la même identité.

Changer l'unité de rééchantillonnage vers les sujets est méthodologiquement mieux motivé, mais cette correction ne prouve pas automatiquement que l'intervalle percentile produit est bien calibré en couverture dans toutes les zones du problème.

Plusieurs modes de défaillance restent possibles :

- intervalle trop étroit : sous-couverture, confiance exagérée ;
- intervalle trop large : sur-couverture, perte de puissance ;
- biais ou asymétrie de la statistique ;
- mauvaise prise en compte de la dépendance sujet ;
- instabilité de la sélection de seuil FMR ;
- dégénérescences lorsque certains poids deviennent nuls ;
- comportement différent près d'une frontière de non-infériorité.

La validation de couverture sert à confronter la procédure complète à ces difficultés sans regarder les scores historiques.

## 8. Les cinq mondes preregistrés

### 8.1 `independent_pair_null`

Contrôle simple. `Delta_FNMR = 0`. Les effets sujets genuine et imposteur sont nuls. Si la procédure échoue déjà ici, les scénarios plus réalistes n'ont pas besoin d'être interprétés.

### 8.2 `subject_dependence_null`

Toujours `Delta_FNMR = 0`, mais avec dépendance par sujets : écart-type d'effet sujet `0.08` sur genuine et `0.05` sur imposteur. Ce scénario attaque directement la faiblesse qui avait motivé `E-STAT-001`.

### 8.3 `subject_dependence_noninferior`

Même dépendance, avec `Delta_FNMR = 0.015`, soit 1,5 point de dégradation absolue : encore à l'intérieur de la marge exploratoire gelée de 3 points.

### 8.4 `subject_dependence_boundary`

`Delta_FNMR = 0.03`, exactement sur la frontière gelée de non-infériorité. C'est le scénario conceptuellement le plus important lorsqu'on pense à la **décision de non-infériorité**.

### 8.5 `subject_dependence_inferior`

`Delta_FNMR = 0.05`, soit 5 points : au-delà de la marge. Dans cette campagne, il sert à tester la couverture de l'intervalle dans un régime clairement inférieur ; il ne crée pas un nouveau gate d'infériorité.

Tous utilisent un graphe de 963 sujets, 500 genuine, 500 impostor, une sparsité de type LFW et une corrélation candidate/référence de 0.7.

## 9. Deux sens différents de « cas difficile »

Il faut conserver cette distinction, car elle a émergé pendant l'interprétation du run.

**Difficile pour le gate de couverture.** Dans le run `32157868533`, la combinaison dont la borne inférieure de couverture est la plus basse est `subject_dependence_noninferior / operational_fnmr` : couverture empirique `0.94525`, MCSE `0.003596958...`, borne Clopper–Pearson `0.937743380...`. C'est le cas « le plus proche du seuil » de 0.93 dans cette exécution.

**Difficile pour la décision de non-infériorité.** Conceptuellement, `subject_dependence_boundary` est le cas de frontière parce que `Delta_FNMR = 0.03` égale exactement la marge gelée.

Ces deux notions ne doivent pas être confondues. Le premier est un constat empirique sur la validation de couverture ; le second concerne la future règle de décision de non-infériorité.

## 10. Comment avoir le réflexe avant de tomber dans le piège

Un petit questionnaire de sûreté statistique aurait permis de détecter le danger très tôt :

1. **Quelle est l'unité réellement indépendante ?** Paire, sujet, session, device, site ?
2. **La même entité réapparaît-elle dans plusieurs observations ?** Si oui, l'indépendance naïve est suspecte.
3. **Quel est exactement l'estimand ?** Moyenne, quantile, taux d'erreur, différence de taux, seuil transféré ?
4. **Est-ce qu'une autre quantité est estimée en cours de route ?** Ici le seuil FMR de représentation est lui-même une statistique.
5. **La garantie théorique de l'intervalle correspond-elle vraiment à ma structure de données ?** « Bootstrap » n'est pas une garantie universelle.
6. **Puis-je créer un monde synthétique dont je connais la vérité ?** Si oui, c'est un banc d'essai naturel.
7. **Ai-je testé les cas de dépendance, frontière, faible nombre d'événements et corrélation ?**
8. **Ai-je fixé ces scénarios et critères avant de regarder le résultat qui m'intéresse ?** Sinon le banc d'essai peut devenir une optimisation post-hoc.

Cette grille est transposable bien au-delà de la biométrie : mesures industrielles, simulations, tests de performance, A/B tests, modèles de fiabilité, validation de systèmes de décision.

## 11. L'aventure d'exécution est aussi une aventure scientifique

La validation de couverture était tellement imbriquée — cinq scénarios, jusqu'à 10 000 datasets simulés et 10 000 bootstraps par dataset — que le coût de calcul est devenu un risque méthodologique.

La mauvaise réponse aurait été de réduire silencieusement le nombre de réplications ou de scénarios pour tenir dans le temps disponible. Le Chronicle a interdit cette dérive.

Le chemin suivi a été :

- profiler plutôt que supposer ;
- vectoriser la logique sensible tout en conservant le moteur legacy comme oracle ;
- démontrer l'équivalence exacte avant de revendiquer le gain de vitesse ;
- passer au multiprocess avec une hiérarchie `SeedSequence.spawn` liée au dataset et non au worker ;
- ajouter un suivi live `progress.jsonl` et console sans exposer de résultat scientifique intermédiaire ;
- constater un run monolithique annulé autour de six heures, limite réelle du runner GitHub-hosted ;
- refuser de réutiliser scientifiquement un scénario incomplet ;
- décomposer le workflow par scénario et checkpoint ;
- prouver l'équivalence monolithique/décomposée, l'invariance au nombre de workers, l'idempotence et les guards de corruption ;
- faire revoir indépendamment cette architecture ;
- autoriser uniquement le chemin décomposé et laisser le chemin monolithique explicitement bloqué ;
- lancer la production seulement après un GO humain explicite et une confirmation `workflow_dispatch`.

Le premier dispatch manuel sans case de confirmation a échoué immédiatement, sans calcul scientifique. Ce petit incident est pédagogiquement utile : la garde n'était pas décorative. Une seconde exécution avec la confirmation correcte a lancé la campagne réelle.

## 12. Pourquoi le suivi live n'était pas une fuite de résultat

Pendant l'exécution, les lignes `[coverage-progress]` contenaient uniquement : nombre de datasets terminés, total, pourcentage, temps écoulé, débit et ETA. Chaque événement portait `runtime_observability_only = true`.

Cette séparation est importante : **l'observabilité opérationnelle peut être riche sans autoriser l'interprétation scientifique prématurée**. Le workflow n'agrégeait au checkpoint intermédiaire que le critère MCSE stop/continue. Les valeurs de couverture n'étaient matérialisées dans le gate final qu'au checkpoint sélectionné.

## 13. Ce que le run 32157868533 a réellement démontré

Le checkpoint 2 000 n'a pas satisfait le critère de précision Monte Carlo : continuation automatique.

Le checkpoint 4 000 a satisfait les 15 MCSE `<= 0.005` : arrêt au premier checkpoint admissible.

Le gate final 4 000 a passé les 15 combinaisons scénario x métrique :

- borne inférieure Clopper–Pearson 95 % `>= 0.93` ;
- MCSE `<= 0.005` ;
- zéro dataset dégénéré.

Le checkpoint 10 000 a donc été correctement ignoré.

Le résultat scientifique borné est :

> La procédure d'intervalle subject-bootstrap, appliquée selon le contrat v0.2.2 gelé, présente une couverture empirique compatible avec les exigences preregistrées sur les cinq scénarios synthétiques et les trois métriques testées.

## 14. Ce que ce PASS ne dit toujours pas

Il ne dit pas que `siamese128` est non-inférieur à `raw512`.

Il ne dit pas que la projection siamoise est meilleure que PCA ou projection aléatoire.

Il ne ferme pas `E-STAT-001` à lui seul.

Il ne passe pas G2 à lui seul.

Il ne valide pas une chaîne biométrique industrielle ni un backbone spécialisé visage.

Il ne démarre pas Study 1.

Il dit seulement que **l'instrument statistique que nous allons utiliser pour réexaminer la question historique a franchi son banc d'essai à vérité connue**.

## 15. L'analogie métrologique, avec sa limite

L'analogie utile est : « avant de mesurer la pièce, vérifier l'instrument sur une référence connue ».

Mais ce n'est pas une calibration métrologique stricte : nous n'avons pas ajusté l'instrument en fonction de l'écart observé. Les règles, scénarios, seuils et critères d'acceptation étaient gelés avant cette campagne et avant lecture des scores historiques.

La formulation la plus exacte est donc : **validation de couverture de la procédure d'intervalle sur un banc synthétique à vérité connue**.

## 16. Trois plans à ne jamais mélanger

**Evidence plane.** Les ZIPs, manifests, outcomes, hashes, décisions MCSE et gate final montrent ce qui a été exécuté.

**Chronicle plane.** Le Chronicle enregistre pourquoi certaines exécutions étaient bloquées, quelles difficultés ont été découvertes, quelles décisions ont été prises avant/après outcome, et ce qui doit rester interdit.

**Pedagogy plane.** Cette note explique la logique de façon progressive et conserve les clarifications qui ont été nécessaires pendant le travail.

Un texte pédagogique ne rend pas un résultat vrai. Un Chronicle ne remplace pas les outcomes. Un ZIP vert ne raconte pas pourquoi la méthode est crédible. La force vient de l'alignement des trois.

## 17. Misconceptions à conserver explicitement

| Idée plausible | Correction |
|---|---|
| « Un intervalle à 95 % contient 95 % de probabilité la vraie valeur dans ce dataset. » | Ce n'est pas l'interprétation fréquentiste standard ; 95 % caractérise la procédure sur des répétitions. |
| « Le bootstrap est connu, donc il est fiable ici. » | Une adaptation à données dépendantes et statistique de seuil doit être validée dans son domaine d'usage. |
| « Passer du pair-bootstrap au subject-bootstrap suffit. » | C'est une correction méthodologiquement motivée, pas une preuve automatique de bonne couverture. |
| « Le scénario boundary doit forcément avoir la pire couverture. » | Boundary est central pour la décision NI ; la pire marge de couverture de ce run est apparue ailleurs. |
| « 94,525 % est trop bas puisque l'on voulait 95 %. » | Le gate preregistré porte sur l'incertitude autour de la couverture empirique : borne CP >= 0.93 et MCSE <= 0.005. |
| « Le PASS prouve la non-infériorité 128D. » | Non : il valide l'instrument d'incertitude avant réanalyse historique. |
| « Le run vert suffit comme archive. » | Non : les artifacts Actions expirent. Il faut une archive liée par hashes et une Chronicle durable. |
| « Une optimisation de runtime est purement engineering. » | Si elle peut changer RNG, seuil, ordre, stopping ou outputs, elle touche la validité scientifique. |

## 18. Gate de compréhension avant la suite

Avant d'ouvrir les scores historiques, un lecteur devrait pouvoir répondre correctement à ces questions :

1. Pourquoi les paires LFW ne sont-elles pas l'unité indépendante évidente ?
2. Quelle est la différence entre `FMR`, `FNMR` et `Delta_FNMR` ?
3. Pourquoi `0.03` signifie-t-il 3 points de pourcentage et non 3 % relatifs ?
4. Quelle est la vérité connue dans la simulation et où est-elle calculée ?
5. Pourquoi la validation de couverture ne lit-elle aucun score historique ?
6. Que teste le scénario `subject_dependence_boundary` ?
7. Pourquoi le « pire cas de couverture observé » et le « cas frontière NI » sont-ils deux notions différentes ?
8. Que signifie le passage de 2 000 à 4 000 datasets ?
9. Pourquoi le checkpoint 10 000 a-t-il été ignoré ?
10. Quelle nouvelle question devient admissible seulement après revue indépendante ?

Si ces réponses sont claires, la suite peut commencer sans transformer le PASS actuel en conclusion qu'il ne porte pas.

## 19. Sources d'autorité locales

- `protocol/studies/study_0_subject_bootstrap_spec.md` — estimands, bootstrap, coverage validation, gate et frontières ;
- `protocol/coverage/study_0_subject_bootstrap_v0.2.2.yaml` — contrat executable gelé ;
- `src/siamese_compression_lab/coverage_simulation.py` — générateur synthétique, vérité connue et agrégation ;
- `src/siamese_compression_lab/coverage_execution.py` — exécution, lignées RNG et outcomes ;
- `protocol/scientific_chronicle.yaml` — décisions et blockers ;
- run GitHub Actions `32157868533` et son archive durable dans `evidence/study_0_subject_bootstrap_v0.2.2/coverage_validation_run_32157868533/`.

Cette note peut être redondante avec ces sources. Cette redondance est volontaire : elle conserve les questions et clarifications qui ont été nécessaires pour comprendre correctement ce que le résultat signifie.
