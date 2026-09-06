# Quand une règle prudente dit trop souvent « je ne sais pas » — Study 1B, S4N1 → S4N2

**Type :** étude de cas pédagogique dérivée  
**Source :** Study 1B, campagnes synthétiques S4N1 et S4N2 du 2026-09-04 au 2026-09-06  
**Statut :** pédagogie, **pas outcome evidence**  
**Autorité :** les contrats gelés, artefacts de workflow et entrées Chronicle restent autoritatifs. Cette note explique le raisonnement ; elle ne change aucun gate et n'ouvre aucun résultat réel.

## Pourquoi conserver cet épisode

Study 1B a rencontré un cas très instructif : une procédure statistique peut être **prudente et fiable sur sa couverture**, tout en étant **insuffisamment puissante pour prendre la décision demandée**.

C'est contre-intuitif. On pourrait penser :

> « Si mon intervalle de confiance est très sûr, ma décision doit être très bonne. »

Pas forcément.

Un casque de moto peut être extrêmement protecteur mais trop lourd pour courir un 100 mètres. De même, une marge statistique peut être assez prudente pour rarement oublier la vraie valeur, mais assez large pour empêcher souvent de conclure.

Cette étude de cas raconte pourquoi S4N1 plafonnait autour de 87 % de puissance, pourquoi nous avons essayé S4N2, ce qu'est **DAGJK20**, et pourquoi S4N2 peut passer les tests de couverture tout en échouant encore au test de puissance.

## 1. Le problème en langage de collège

Nous voulons comparer une représentation faciale compressée 128D à une référence raw512.

Au point d'utilisation gelé `FMR = 1 %`, on regarde la différence :

```text
Delta_FNMR = FNMR_compresse - FNMR_raw512
```

La limite acceptable du protocole est `+0.03`, c'est-à-dire **+3 points de FNMR**.

Supposons que, dans un monde synthétique dont nous connaissons la vérité, la compression soit réellement seulement `+0.01` moins bonne, donc **+1 point**. Elle est encore confortablement sous la limite de +3.

La question du banc d'essai est alors :

> Si cette situation acceptable est vraiment la réalité, notre expérience arrive-t-elle à le démontrer assez souvent ?

Le protocole avait fixé : **au moins 90 fois sur 100**.

## 2. Une estimation n'est pas encore une décision

Imagine que tu veuilles mesurer la longueur d'une table.

Tu mesures :

```text
2,00 m
```

Mais ta règle n'est pas parfaite. Tu ne dis donc pas seulement « 2,00 m ». Tu ajoutes une zone d'incertitude :

```text
probablement entre 1,97 m et 2,03 m
```

Dans Study 1B, c'est pareil : nous avons une estimation de `Delta_FNMR`, puis une marge de sécurité autour d'elle.

Pour déclarer la compression **non inférieure**, nous ne regardons pas seulement la meilleure estimation. Nous regardons surtout le côté dangereux :

> « Et si la vraie dégradation était un peu plus grande que ce que nous voyons ? »

C'est pourquoi la règle utilise une **borne supérieure de confiance**. Pour PASS, cette borne doit rester sous `+0.03`.

## 3. Qu'est-ce que la « couverture » ?

Dans la vraie étude, nous ne connaissons pas la vraie valeur de `Delta_FNMR`.

Dans une simulation, nous pouvons la connaître parce que nous construisons nous-mêmes le monde. C'est comme cacher volontairement une bille rouge dans une boîte puis tester si une méthode arrive à construire une zone qui contient bien l'endroit où nous savons que la bille se trouve.

Si un intervalle est annoncé comme « 95 % », alors sur beaucoup d'expériences répétées il devrait contenir la vraie valeur environ 95 fois sur 100.

C'est la **couverture**.

Donc :

```text
couverture = à quelle fréquence la zone d'incertitude contient vraiment la vérité connue
```

Important : une couverture de 99 % pour une cible nominale de 95 % n'est pas « encore meilleure » dans tous les sens. Elle indique que l'intervalle est **très prudent / conservateur**. Il oublie rarement la vérité, mais il peut être plus large que nécessaire et donc rendre la décision plus difficile.

Pour S4N2 à la vérité critique `Delta = +0.01`, la couverture bilatérale observée était environ 98,4–98,7 %, et la couverture de la borne supérieure environ 99,0–99,3 % selon le sélecteur. La formulation précise n'est donc pas « calibration parfaite » ; c'est :

> **S4N2 passe les gates de couverture gelés et ne sous-couvre pas ; elle est même plutôt conservatrice dans ce banc synthétique.**

## 4. Que veut dire « bilatéral » ?

Imagine une cible avec un centre.

Une erreur peut être :

```text
trop à gauche  <--- vérité --->  trop à droite
```

Un intervalle **bilatéral** protège des deux côtés : il demande si la vraie valeur peut être plus petite **ou** plus grande que notre estimation.

Dans Study 1B, cette vérification bilatérale sert à contrôler la santé générale de l'estimateur d'incertitude.

Mais pour la décision de non-infériorité, le danger principal est surtout d'un côté :

> la compression pourrait-elle être **plus mauvaise** que nous le pensons ?

C'est pourquoi la décision scientifique utilise surtout une **borne supérieure unilatérale à 97,5 %**.

En version très courte :

```text
bilatéral : je surveille les deux côtés
unilatéral supérieur : je surveille surtout le côté « pourrait être pire »
```

## 5. Que veut dire « zéro dégénérescence » ?

DAGJK20 refait le calcul en retirant certaines identités. Il pourrait arriver, dans un cas malchanceux, que le jeu restant devienne impossible à utiliser : plus assez de comparaisons genuine, plus assez d'imposteurs, seuil FMR impossible à calculer, variance non finie, etc.

Une telle répétition est dite ici **dégénérée** : la machine statistique n'arrive plus à produire un résultat valide.

`degenerate_fraction = 0` signifie :

> sur les milliers de datasets synthétiques testés, aucune répétition n'a cassé de cette manière.

Cela ne signifie absolument pas :

> « zéro erreur biométrique ».

Ce sont deux choses sans rapport direct.

## 6. S4N1 : le premier « thermomètre d'incertitude »

S4N1 utilisait un **bootstrap par sujets**.

Image simple : nous avons une classe d'élèves et nous voulons savoir à quel point la moyenne observée dépend des élèves présents. Nous fabriquons beaucoup de classes virtuelles en repiochant des élèves avec remise, puis nous regardons comment le résultat bouge.

Si les résultats bougent beaucoup, l'incertitude est grande. S'ils bougent peu, elle est petite.

S4N1 était capable de couvrir correctement la vérité synthétique. Mais au cas critique `Delta = +0.01`, sa puissance était :

| Sélecteur | S4N1 — puissance |
|---|---:|
| FIXED | 86,55 % |
| BEST | 86,90 % |
| MEDIAN | 86,95 % |
| objectif gelé | **>= 90 %** |

Cela veut dire : si la compression est réellement acceptable avec seulement +1 point de FNMR, le banc S4N1 réussit à le démontrer environ **87 fois sur 100**, et répond environ **13 fois sur 100 « pas démontré »**.

Ce n'est pas 13 % de personnes mal reconnues. C'est un risque au niveau de la **décision de toute l'étude**.

## 7. Pourquoi ne pas simplement passer l'objectif de 90 % à 85 % ?

Parce que nous aurions déplacé la ligne d'arrivée après avoir vu que nous la manquions.

Nous avons donc conservé :

- la marge de non-infériorité `+0.03` ;
- le FMR `1 %` ;
- la confiance supérieure `97,5 %` ;
- l'objectif de puissance `90 %` ;
- les mêmes sélecteurs et leur ordre ;
- la même vérité synthétique critique `Delta = +0.01`.

La question est restée la même. Nous avons seulement cherché à savoir si notre **façon de mesurer l'incertitude** pouvait être améliorée.

## 8. Le diagnostic S4N1 : où semblait être le problème ?

Le diagnostic a montré trois choses importantes.

Premièrement, l'estimation centrale n'était pratiquement pas biaisée : la règle ne se trompait pas systématiquement de direction.

Deuxièmement, BEST, MEDIAN et FIXED avaient des puissances très proches : changer opportunément de sélecteur ne semblait pas être la solution.

Troisièmement, la marge d'incertitude produite par S4N1 paraissait assez conservatrice sous le générateur synthétique. Une approximation de son erreur standard était environ 1,39–1,40 fois la variabilité réellement observée de l'estimation à travers les datasets simulés.

Cela a produit une **hypothèse de travail**, pas une conclusion :

> peut-être qu'un autre estimateur d'incertitude, toujours prudent et prospectivement gelé, construirait une borne plus adaptée et récupérerait assez de puissance pour atteindre 90 %.

C'est ce que S4N2 a testé.

## 9. DAGJK20 expliqué à 12 ans

`DAGJK20` signifie ici une variante **Delete-A-Group Jackknife avec 20 groupes**.

Imagine 1 710 élèves répartis de manière fixe dans **20 équipes**.

On calcule une première fois le résultat avec tout le monde. Puis :

```text
calcul 1 : on cache l'équipe 1
calcul 2 : on cache l'équipe 2
...
calcul 20 : on cache l'équipe 20
```

Quand une équipe est cachée, nous retirons toutes les comparaisons qui touchent un membre de cette équipe. Puis nous recalculons les seuils FMR et `Delta_FNMR` avec ce qui reste.

Ensuite nous posons la question :

> Le résultat change-t-il beaucoup quand j'enlève un groupe ?

S'il change beaucoup, les données sont fragiles à la composition des identités : incertitude élevée.

S'il change peu, le résultat est plus stable : incertitude plus faible.

Les 20 résultats « un groupe retiré » servent à estimer une variance et une erreur standard. Une loi de Student à 19 degrés de liberté transforme ensuite cette erreur standard en borne de sécurité à 97,5 %.

Ce n'est donc pas une nouvelle façon de reconnaître un visage. C'est **une nouvelle façon de poser une barre d'erreur autour du même résultat biométrique estimé**.

## 10. Qu'avons-nous essayé de faire exactement ?

Une analogie résume tout :

```text
même voiture
même circuit
même ligne d'arrivée
même règle « il faut être sous 3 minutes »
mais un autre chronomètre pour quantifier l'incertitude du temps mesuré
```

Nous n'avons pas essayé d'améliorer le modèle Siamese, de changer la compression ou de modifier les données réelles.

Nous avons essayé de construire une **règle d'incertitude moins inutilement conservatrice**, sans diminuer le niveau de confiance demandé.

Cette distinction est centrale : S4N2 est une expérience sur le **banc de qualification statistique**, pas sur la qualité réelle du modèle.

## 11. S4N2 : qu'a-t-elle réussi ?

Elle a réussi son gate de couverture.

Sur les mondes synthétiques où la vérité était connue, sa zone de confiance contenait la vérité assez souvent pour passer tous les critères gelés. Elle n'a eu aucune dégénérescence.

De plus, le rapport entre l'erreur standard médiane estimée et la variabilité observée de l'estimation est descendu autour de **1,25–1,28**, contre environ **1,39–1,40** dans le diagnostic S4N1.

Cela va dans la direction recherchée : au centre de la distribution, S4N2 paraît moins gonfler l'incertitude que S4N1.

Mais ce n'est qu'une propriété intermédiaire. La question finale était :

> Cela permet-il réellement au banc de prendre la bonne décision au moins 90 fois sur 100 ?

## 12. Et pourtant S4N2 a moins de puissance

Au cas critique `Delta = +0.01`, le résultat final sur 4 000 datasets par vérité est :

| Sélecteur | S4N1 | S4N2 DAGJK20 | différence S4N2 - S4N1 |
|---|---:|---:|---:|
| FIXED | 86,55 % | 84,70 % | -1,85 point |
| BEST | 86,90 % | 84,90 % | -2,00 points |
| MEDIAN | 86,95 % | 85,35 % | -1,60 point |
| objectif | **90 %** | **90 %** | — |

Donc, sur le critère final de décision, S4N2 est **légèrement moins bonne que S4N1**, de 1,6 à 2,0 points de puissance selon le sélecteur.

Cela ne veut pas dire que le modèle biométrique est devenu moins bon. Dans cette comparaison synthétique, nous avons changé **la méthode d'incertitude**, pas la vérité du modèle.

## 13. Comment peut-elle avoir une meilleure « taille d'erreur standard » et moins de puissance ?

Parce qu'une décision ne dépend pas seulement de la **taille moyenne ou médiane** de l'erreur standard.

Elle dépend de toute la procédure :

- comment l'incertitude varie d'un dataset à l'autre ;
- quelles valeurs apparaissent dans les queues de distribution ;
- comment le jackknife réagit au retrait des groupes ;
- comment la constante de Student transforme l'erreur standard ;
- comment la borne supérieure finale se place par rapport à `+0.03`.

Ainsi, « SE médiane plus petite » n'implique pas automatiquement « plus de PASS corrects ».

C'est une leçon générale :

> optimiser une métrique intermédiaire n'est pas la même chose qu'améliorer le critère de décision final.

Nous n'avons donc pas le droit de dire « DAGJK20 est statistiquement meilleur » simplement parce que son ratio SE/variabilité est plus proche de 1.

## 14. « Ne récupère pas la puissance attendue » — formulation à corriger

Le mot **attendue** peut prêter à confusion.

Il n'existait pas de théorème disant :

> « DAGJK20 donnera au moins 90 % de puissance. »

Le 90 % était le **niveau requis prospectivement par le protocole**.

Le diagnostic S4N1 nous avait donné une raison scientifique de tester l'hypothèse qu'un autre estimateur d'incertitude pourrait suffire. S4N2 était précisément l'expérience destinée à falsifier ou soutenir cette hypothèse.

La phrase la plus juste est donc :

> **S4N2 ne permet pas d'atteindre l'objectif de puissance gelé à 90 %, malgré une couverture satisfaisante.**

## 15. Pourquoi une couverture très élevée peut aller avec une faible puissance

Imagine un professeur qui corrige un résultat de physique.

Pour ne presque jamais accuser à tort un élève, il dit :

> « Je ne valide la réponse que si je suis absolument, absolument, absolument certain. »

Il fera très peu de faux PASS. Mais il risque aussi de dire souvent « je ne peux pas confirmer » à des élèves qui avaient en réalité la bonne réponse.

C'est le compromis entre :

```text
prudence contre le faux PASS
        et
capacité à reconnaître un vrai PASS
```

La **couverture** demande si la règle d'incertitude raconte une histoire suffisamment prudente sur la vérité.

La **puissance** demande si cette règle permet effectivement de reconnaître assez souvent une situation acceptable.

Les deux sont nécessaires. L'une ne remplace pas l'autre.

## 16. Que nous apprend le résultat négatif ?

Le résultat n'est pas « nous avons raté deux fois ».

Il élimine une explication simple :

> **remplacer uniquement l'estimateur d'incertitude S4N1 par DAGJK20 ne suffit pas à obtenir le niveau de décision demandé.**

S4N1 indiquait déjà que le biais central et le choix du sélecteur n'étaient probablement pas le cœur du problème. S4N2 montre maintenant qu'une autre règle d'incertitude raisonnable et prospectivement gelée ne résout pas non plus le problème.

Cela augmente la crédibilité d'une autre lecture : le niveau de puissance demandé est contraint par **l'ensemble information disponible + dépendances + estimateur + décision**, pas par un seul mauvais réglage facile à remplacer.

Cette lecture doit encore être traduite en risque de décision et en impact opérationnel avant de décider si le déficit 85–87 % versus 90 % est réellement important pour l'usage visé.

## 17. Ce que nous avons volontairement refusé de faire

Après S4N1 puis S4N2, plusieurs raccourcis auraient pu produire un PASS : diminuer 90 %, agrandir la marge de +3 points, baisser le niveau de confiance, modifier le nombre de groupes, choisir après coup le sélecteur qui échoue le moins, ou regarder les vrais résultats pour décider quelle méthode utiliser.

Aucun de ces raccourcis n'est admissible dans la campagne actuelle.

Le résultat négatif est donc conservé tel quel.

## 18. Test de compréhension

Avant de considérer l'épisode compris, on devrait pouvoir répondre sans formule à ces questions :

1. Pourquoi « couverture 99 % » ne veut-elle pas dire « puissance 99 % » ?
2. Pourquoi `degenerate_fraction = 0` ne veut-il pas dire « zéro erreur biométrique » ?
3. Quelle différence y a-t-il entre intervalle bilatéral et borne supérieure unilatérale ?
4. Que fait DAGJK20 quand il retire une équipe d'identités ?
5. Pourquoi S4N2 peut-elle avoir un ratio SE/variabilité plus proche de 1 mais une puissance finale plus faible ?
6. Pourquoi 84,9 % de puissance ne signifie-t-il pas « 15,1 % des personnes seront mal reconnues » ?
7. Pourquoi changer la barre de 90 % après avoir obtenu 84,9 % serait-il un autre problème scientifique ?

## 19. Provenance et frontière

Les résultats scientifiques autoritatifs sont notamment :

- `protocol/chronicle/STUDY1B_S4N1_CORE_POWER_CALIBRATION_RESULT_2026-09-06.yaml` ;
- `protocol/chronicle/STUDY1B_S4N1_POWER_PLATEAU_DIAGNOSTIC_RESULT_2026-09-06.yaml` ;
- `protocol/simulations/STUDY1B_S4N2_DAGJK20_CALIBRATION_V0_1_2026-09-06.yaml` ;
- `protocol/chronicle/STUDY1B_S4N2_DAGJK20_COVERAGE_1000_RESULT_2026-09-06.yaml` ;
- `protocol/chronicle/STUDY1B_S4N2_DAGJK20_POWER_4000_RESULT_2026-09-06.yaml`.

Cette note n'ouvre aucun SCREEN, aucun TEST réel, aucune performance raw512/PCA/random/Siamese et aucune géométrie de représentation. Elle capitalise uniquement un apprentissage méthodologique issu de simulations à vérité connue.
