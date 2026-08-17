# De la PCA à la projection siamoise : comprendre la compression 512D → 128D

> **Type de document :** note pédagogique et méthodologique reliée à Study 0  
> **Périmètre :** compression de représentations biométriques, baselines et protocole comparatif  
> **Statut scientifique :** explication valide du dispositif ; supériorité et non-infériorité
> `NOT_DEMONSTRATED`  
> **Important :** ce document n'ajoute aucun résultat et ne modifie aucun artefact historique.

## 1. Pourquoi cette note existe

Cette note vient d'une discussion déclenchée pendant un cours sur la réduction
dimensionnelle et la PCA. La question initiale était :

> **« PCA et “PCLS”, est-ce que cela a un rapport avec la réduction de notre embedding
> ResNet de 512D vers 128D au moyen de l'algorithme siamois ? »**

Oui. La relation est directe : la PCA et la projection siamoise cherchent toutes deux à
transformer un vecteur de grande dimension en un vecteur plus compact. Cependant, elles ne
choisissent pas la projection avec le même objectif, n'utilisent pas les mêmes informations
et ne permettent pas les mêmes conclusions.

Le terme « PCLS » était vraisemblablement une erreur de transcription de « PCA's » ou de
« PCA ». Aucun algorithme standard nommé PCLS n'est utilisé dans ce projet.

La discussion a ensuite fait apparaître deux prises de conscience :

> **« Et on fait des comparaisons avec d'autres modèles de compression, c'est bien ça ?
> Dont PCA ? »**

et :

> **« Waou, du coup je suis arrivé à un cas pratique de compression de modèle avant même
> que le cours commence, et pas à une partie optionnelle du module 3 d'Andrew Ng justement
> sur les réductions de modèles ! »**

Ces commentaires méritent d'être conservés, parce qu'ils rendent visible la genèse réelle
de l'étude : le problème d'ingénierie est apparu avant le vocabulaire académique qui permet
de le classer. Le chemin n'a pas été « apprendre PCA, puis chercher un exercice ». Il a été :

```text
contrainte biométrique réelle
    → représentation mathématique
    → réduction 512D vers 128D
    → nécessité de baselines
    → découverte du rôle de PCA
    → hypothèses falsifiables
    → protocole de non-infériorité
    → découverte d'un défaut d'estimation
    → correction méthodologique preregistrée
```

Ce chemin est précisément celui d'une micro-étude ML sérieuse.

## 2. Première correction de vocabulaire : que compresse-t-on exactement ?

Dans Study 0, nous ne comprimons pas le modèle ResNet-18 dans son ensemble. Nous
comprimons la **représentation produite par le modèle**, c'est-à-dire son embedding.

Le pipeline est :

\[
\text{image}
\xrightarrow{\text{ResNet-18 gelé}}
x\in\mathbb{R}^{512}
\xrightarrow{\text{route de projection}}
z\in\mathbb{R}^{128}.
\]

Le ResNet-18 reste présent, inchangé et gelé. Il continue à produire 512 valeurs pour
chaque image. Une transformation supplémentaire produit ensuite le gabarit 128D.

Il est donc plus exact de parler de :

- **compression d'embedding** ;
- **compression de représentation** ;
- **réduction dimensionnelle du gabarit** ;
- ou **projection 512D → 128D**.

Il serait prématuré de parler de compression complète du réseau ou de réduction du coût
d'extraction. Réduire le ResNet lui-même demanderait une autre intervention : backbone
plus petit, pruning, quantification, distillation ou apprentissage end-to-end produisant
directement un embedding 128D. Ces interventions ne font pas partie de Study 0.

### 2.1 Ce que 512D → 128D réduit

Le nombre de composantes par gabarit diminue de :

\[
\frac{512-128}{512}=0{,}75,
\]

soit **75 % de composantes en moins**, ou un facteur quatre sur le payload d'un gabarit de
même type numérique.

Avec des valeurs `float32` :

| Dimension | Octets par gabarit | 150 millions de gabarits |
|---:|---:|---:|
| 512D | 2 048 | environ 286,1 GiB |
| 128D | 512 | environ 71,5 GiB |

Cela peut réduire :

- le stockage des gabarits ;
- la mémoire nécessaire à une grande galerie ;
- le volume de données lu pendant une comparaison exhaustive ;
- le nombre de composantes manipulées pendant une recherche exacte 1:N ;
- potentiellement une partie de la latence de recherche.

### 2.2 Ce que cette transformation ne réduit pas automatiquement

Elle ne réduit pas nécessairement :

- le nombre de paramètres du ResNet-18 ;
- son temps d'inférence ;
- son coût énergétique ;
- la mémoire requise pour exécuter l'extracteur ;
- le temps total de réponse du système.

La projection siamoise ajoute même un calcul après l'extraction. Le coût total doit être
décomposé comme suit :

\[
T_{\mathrm{total}}
=T_{\mathrm{extract}}
+T_{\mathrm{project}}
+T_{\mathrm{search}}
+T_{\mathrm{postprocess}}.
\]

Study 0 ne mesure ni latence 1:N ni temps de bout en bout. Une réduction théorique de
`512N` à `128N` composantes comparées ne constitue donc pas la preuve d'une accélération
réelle par quatre.

### 2.3 Coût propre de la projection apprise

La tête linéaire contient :

\[
512\times128+128=65\,664
\]

paramètres entraînables, biais inclus. En `float32`, cela représente 262 656 octets, soit
environ 256,5 KiB.

En ne comptant que le stockage propre à chaque route :

\[
\operatorname{raw}(N)=2\,048N,
\]

\[
\operatorname{projected}(N)=512N+262\,656.
\]

Les deux quantités sont égales à 171 gabarits. Sous ces hypothèses, la route apprise ne
procure un gain net de stockage qu'au-delà de 171 gabarits. Le bénéfice est donc évident
pour une très grande galerie, mais pas nécessairement pour un téléphone contenant un ou
deux gabarits.

## 3. Le problème mathématique commun

Toutes les routes de compression étudiées reçoivent le même embedding gelé :

\[
x\in\mathbb{R}^{512}.
\]

Elles construisent une nouvelle représentation :

\[
z=f(x)\in\mathbb{R}^{128}.
\]

Le problème n'est donc pas simplement de produire 128 nombres. Il est de déterminer
**quelles propriétés de l'espace 512D doivent être conservées** dans ces 128 nombres.

Réduire la dimension entraîne nécessairement un choix. Une projection peut préserver :

- la variance globale ;
- les distances entre points ;
- la reconstruction des entrées ;
- les classes ;
- les voisinages ;
- ou, dans notre cas, la capacité à rapprocher des images de même identité et à séparer
  des images d'identités différentes.

PCA et la projection siamoise répondent au même besoin de compacité, mais elles ne
préservent pas explicitement la même chose.

## 4. Les quatre routes réellement exécutées dans Study 0

Study 0 compare exactement quatre routes. Elles reçoivent les mêmes embeddings ResNet-18
gelés et les mêmes splits de paires.

| Route | Sortie | Comment la transformation est-elle choisie ? | Identités/paires utilisées pour l'ajustement ? | Rôle expérimental |
|---|---:|---|---:|---|
| `raw` | 512D | aucune réduction ; normalisation L2 | non | référence sans compression |
| `random` | 128D | matrice gaussienne fixe et seedée | non | contrôle d'une réduction sans apprentissage |
| `pca` | 128D | axes expliquant le plus de variance sur TRAIN | non | forte baseline linéaire non supervisée |
| `siamese` | 128D | matrice partagée apprise par contrastive loss | oui | méthode supervisée par paires étudiée |

Cette table est normative pour la lecture de Study 0.

### 4.1 Routes évoquées dans la discussion mais non exécutées

La conversation a également mentionné :

- une troncature naïve des 128 premières composantes ;
- un autoencodeur non linéaire ;
- potentiellement d'autres familles de compression.

Ce sont des **candidats pour une ablation ou une étude future**, pas des routes exécutées
dans Study 0. Les ajouter a posteriori au tableau des résultats réécrirait le protocole.
Le placeholder `study_2_compression_ablation` prévoit actuellement les familles `raw`,
`random`, `pca` et `siamese` aux dimensions 64, 128 et 256 ; tout ajout d'une nouvelle
famille devra être preregistré avant exécution.

## 5. La route raw 512D : la référence sans compression

La route brute applique uniquement une normalisation L2 :

\[
z_{\mathrm{raw}}=\frac{x}{\lVert x\rVert_2}.
\]

Elle conserve les 512 composantes. Elle sert de référence pour la question principale :

> Peut-on réduire la représentation par quatre sans dégradation biométrique supérieure à
> la marge déclarée ?

La comparaison avec `raw512` n'a pas le même rôle que la comparaison avec PCA. Elle mesure
le prix de la compression, et non la valeur relative de deux méthodes de compression.

## 6. La projection aléatoire 128D : le contrôle minimal

La route aléatoire utilise une matrice fixe :

\[
R\in\mathbb{R}^{512\times128},
\qquad
R_{ij}\sim\mathcal{N}\!\left(0,\frac{1}{128}\right),
\]

puis :

\[
z_{\mathrm{random}}
=\operatorname{L2Norm}(xR).
\]

Elle ne voit ni les labels de paires ni les identités. Elle répond à une question de
contrôle :

> Le résultat provient-il réellement d'une structure apprise, ou n'importe quelle
> réduction 512D → 128D produit-elle déjà un comportement comparable ?

Une projection aléatoire n'est pas « un mauvais modèle placé pour perdre ». C'est un
contrôle nécessaire pour isoler la valeur ajoutée de l'apprentissage.

## 7. PCA 512D → 128D

### 7.1 Ce que calcule PCA

PCA centre les embeddings à l'aide de la moyenne apprise sur TRAIN :

\[
\tilde{x}=x-\mu_{\mathrm{TRAIN}},
\]

puis projette les données sur les 128 directions principales :

\[
z_{\mathrm{PCA}}
=W_{\mathrm{PCA}}^{\top}(x-\mu_{\mathrm{TRAIN}}),
\qquad
W_{\mathrm{PCA}}\in\mathbb{R}^{512\times128}.
\]

Dans l'implémentation, PCA est ajustée sur les endpoints de TRAIN uniquement, avec un SVD
randomisé seedé, puis sa sortie est normalisée L2.

Les colonnes de \(W_{\mathrm{PCA}}\) correspondent aux directions orthogonales qui
expliquent le plus de variance parmi les embeddings d'entraînement.

### 7.2 La question posée par PCA

PCA demande essentiellement :

> Quelles directions permettent de conserver autant que possible la structure de variance
> globale des embeddings ?

Cette optimisation ne connaît pas les paires authentiques et imposteurs. Elle ne sait pas
qu'une image de la personne A doit être proche d'une autre image de A, ni qu'une image de A
doit être éloignée d'une image de B.

### 7.3 Pourquoi variance ne signifie pas automatiquement identité

Une direction de forte variance peut coder de l'information utile à l'identité, mais elle
peut aussi refléter :

- la pose ;
- l'éclairage ;
- le fond ;
- le cadrage ;
- la qualité de l'image ;
- ou une particularité du backbone ImageNet qui n'est pas optimisée pour la biométrie
  faciale.

PCA maximise la variance préservée, pas directement une métrique biométrique comme FNMR à
FMR fixé. Elle reste pourtant une baseline forte : si une transformation simple,
non supervisée et linéaire donne le même résultat que la projection siamoise, la valeur
ajoutée de la supervision par paires n'est pas démontrée.

### 7.4 Pourquoi PCA doit être ajustée sur TRAIN uniquement

Si PCA était ajustée sur TEST, même sans utiliser explicitement les labels de paires, elle
utiliserait la distribution des embeddings de TEST pour choisir ses axes. La comparaison
ne serait plus strictement indépendante.

Le protocole impose donc :

\[
W_{\mathrm{PCA}},\mu_{\mathrm{TRAIN}}
\leftarrow \mathrm{fit}(X_{\mathrm{TRAIN}}),
\]

puis applique cette transformation gelée à VALIDATION et TEST.

## 8. La projection siamoise 512D → 128D

### 8.1 Une projection linéaire partagée

La route siamoise apprend :

\[
z_{\mathrm{siamese}}
=\operatorname{L2Norm}(xW+b),
\]

avec :

\[
W\in\mathbb{R}^{512\times128},
\qquad
b\in\mathbb{R}^{128}.
\]

Selon la convention vecteur-colonne, la même expression peut s'écrire avec
\(W\in\mathbb{R}^{128\times512}\) et \(Wx+b\). Les deux notations décrivent la même
transformation ; le code utilise des lignes et calcule `x @ W + b`.

Deux embeddings passent par **la même** projection :

\[
z_1=f_{W,b}(x_1),
\qquad
z_2=f_{W,b}(x_2).
\]

Le mot « siamois » désigne ce partage des paramètres entre les deux branches. Il ne signifie
pas que deux ResNet distincts sont entraînés dans Study 0. Le ResNet-18 est gelé et la tête
linéaire partagée est la seule partie entraînée.

### 8.2 Distance et contrastive loss

Après normalisation L2, la distance utilisée est :

\[
d=\lVert z_1-z_2\rVert_2.
\]

Pour une étiquette \(y=1\) lorsqu'il s'agit de la même identité et \(y=0\) sinon, la loss
implémentée est :

\[
\mathcal{L}
=\frac{1}{2}y\,d^2
+\frac{1}{2}(1-y)\max(0,m-d)^2,
\]

où \(m\) est la marge contrastive.

Elle encourage :

\[
\text{même identité}
\Rightarrow d(z_1,z_2)\ \text{petite},
\]

et :

\[
\text{identités différentes}
\Rightarrow d(z_1,z_2)\ \text{au moins aussi grande que la marge}.
\]

### 8.3 La question posée par la projection siamoise

Elle demande :

> Quelles directions dans l'espace 512D sont les plus utiles pour organiser un espace 128D
> où les paires authentiques sont rapprochées et les paires imposteurs séparées ?

Elle peut donc être décrite comme une **réduction dimensionnelle supervisée par paires** ou
comme un cas d'**apprentissage de métrique**. Elle n'est pas une PCA supervisée au sens
strict et ne doit pas être nommée ainsi.

## 9. PCA et siamois : relation exacte et différence essentielle

Les deux méthodes sont liées parce qu'elles apprennent une transformation linéaire vers le
même espace 128D :

\[
\mathbb{R}^{512}\longrightarrow\mathbb{R}^{128}.
\]

Mais elles optimisent des critères différents :

| Dimension de comparaison | PCA 128D | Siamois 128D |
|---|---|---|
| Nature | linéaire | linéaire dans Study 0 |
| Supervision | non supervisée | supervisée par paires |
| Entrée d'ajustement | endpoints TRAIN | paires TRAIN avec labels |
| Critère | variance expliquée | contrastive loss |
| Information explicitement conservée | structure statistique globale | séparabilité authentique/imposteur |
| Normalisation finale | L2 | L2 |
| Risque principal | conserver des nuisances à forte variance | surapprendre les paires ou le domaine TRAIN |
| Question scientifique | la compression générique suffit-elle ? | la supervision ajoute-t-elle une valeur mesurable ? |

La formulation la plus courte est :

> **PCA conserve ce qui varie le plus ; le siamois cherche à conserver ce qui aide le plus
> la décision de similarité d'identité.**

Cette phrase est utile pédagogiquement, mais elle ne garantit pas que le siamois sera
meilleur. Une supervision mal adaptée, un jeu de données trop petit, un backbone inadéquat
ou une optimisation instable peuvent conduire à un résultat inférieur à PCA.

## 10. Pourquoi il faut plusieurs baselines

Une seule comparaison ne permet pas d'isoler toutes les causes possibles d'un résultat.
Chaque paire de routes répond à une question différente.

### 10.1 Siamois 128D contre raw 512D

\[
\mathrm{Siamois}_{128}
\quad\text{vs}\quad
\mathrm{Raw}_{512}
\]

Question :

> Peut-on compresser par quatre sans dégradation biométrique supérieure à la marge
> acceptable déclarée ?

C'est une question de **non-infériorité sous compression**.

### 10.2 Siamois 128D contre PCA 128D

\[
\mathrm{Siamois}_{128}
\quad\text{vs}\quad
\mathrm{PCA}_{128}
\]

Question :

> La supervision par les paires apporte-t-elle davantage qu'une compression linéaire
> statistique standard, à dimension identique ?

C'est une question de **valeur ajoutée de la supervision**.

### 10.3 Siamois 128D contre random 128D

\[
\mathrm{Siamois}_{128}
\quad\text{vs}\quad
\mathrm{Random}_{128}
\]

Question :

> Le modèle apprend-il une structure utile au-delà de l'effet mécanique d'une projection
> dans un espace plus petit ?

C'est une question de **réalité du signal appris**.

### 10.4 PCA 128D contre random 128D

\[
\mathrm{PCA}_{128}
\quad\text{vs}\quad
\mathrm{Random}_{128}
\]

Question :

> Préserver les directions de variance apporte-t-il davantage qu'une projection non
> ajustée aux données ?

Cette comparaison aide à interpréter le rôle de la structure globale des embeddings.

### 10.5 La logique de falsification

Les baselines empêchent une conclusion trop facile :

- si `siamese128` bat `random128` mais pas `pca128`, la supervision ne démontre pas encore
  une valeur au-delà d'une forte baseline non supervisée ;
- si `siamese128` bat PCA et random mais perd trop contre `raw512`, l'apprentissage apporte
  quelque chose entre méthodes compressées sans satisfaire la contrainte de
  non-infériorité ;
- si `siamese128` est non inférieur à raw mais pas supérieur aux contrôles compressés, la
  compression peut être intéressante mais le mécanisme siamois n'est pas nécessairement
  la cause ;
- si les résultats varient fortement selon les seeds, une bonne moyenne ne suffit pas à
  établir la robustesse de la méthode.

## 11. Un protocole comparatif équitable

Toutes les routes doivent être évaluées :

- sur le même backbone gelé ;
- sur les mêmes embeddings d'entrée ;
- sur les mêmes splits TRAIN, VALIDATION et TEST ;
- sur les mêmes paires TEST ;
- avec la même convention de distance ;
- aux mêmes points opératoires ;
- avec les mêmes unités de rééchantillonnage ;
- avec tous les seeds preregistrés, sans sélectionner le meilleur sur TEST.

L'ordre expérimental est :

1. geler configuration, hypothèses, marges et seeds ;
2. vérifier les séparations d'identités entre splits ;
3. ajuster PCA sur TRAIN uniquement ;
4. entraîner la tête siamoise sur TRAIN uniquement ;
5. utiliser VALIDATION pour l'arrêt anticipé et les seuils opérationnels ;
6. geler modèles et seuils ;
7. ouvrir TEST une seule fois ;
8. rapporter les métriques avec seuils gelés ;
9. calculer séparément les points TEST à FMR égal pour la comparaison descriptive des
   représentations ;
10. rapporter tous les seeds.

## 12. Métriques : ce que « conserver l'information » signifie ici

Dans un cours introductif à PCA, « conserver l'information » est souvent approché par la
variance expliquée ou par la qualité d'une reconstruction. Dans notre étude, ce terme doit
être traduit en objectifs biométriques observables.

Les principales métriques sont :

- ROC AUC ;
- EER ;
- courbe DET ;
- FNMR à FMR fixé ;
- FMR et FNMR avec seuil choisi sur VALIDATION puis gelé ;
- taille de gabarit ;
- à terme, mémoire, débit, latence et performance 1:N.

La métrique principale exploratoire de représentation est :

\[
\Delta_{\mathrm{FNMR}}
=\mathrm{FNMR}_{\mathrm{candidate}}
-\mathrm{FNMR}_{\mathrm{raw512}}
\]

au même point TEST \(\mathrm{FMR}=0{,}01\).

La marge exploratoire de non-infériorité a été fixée à :

\[
\delta=0{,}03.
\]

Pour déclarer une non-infériorité sous la convention prévue, la borne supérieure de
l'intervalle apparié de \(\Delta_{\mathrm{FNMR}}\) doit rester sous cette marge pour tous
les seeds preregistrés.

## 13. Ce que Study 0 a observé — et ce qu'elle n'a pas démontré

Au point TEST descriptif de même FMR (`FMR = 0.01`), Study 0 a rapporté :

| Route | FNMR moyen | ROC AUC moyen | EER moyen |
|---|---:|---:|---:|
| raw 512D | 0,8060 | 0,7931 | 0,2890 |
| PCA 128D | 0,8216 | 0,8058 | 0,2704 |
| random 128D | 0,8416 | 0,7726 | 0,3104 |
| Siamese 128D | 0,8288 | 0,8167 | 0,2662 |

Le siamois possède, dans ce run, la meilleure AUC moyenne et le plus faible EER moyen.
Cela ne prouve pourtant ni la non-infériorité au point FNMR/FMR principal, ni la supériorité
robuste sur PCA.

Son FNMR moyen est supérieur de 0,0228 au raw512. Le pire upper bound historique rapporté
était 0,156, au-dessus de la marge de 0,03, et tous les seeds devaient passer.

Le verdict conservé est donc :

```text
NOT_DEMONSTRATED
```

Cela signifie :

- non-infériorité du siamois 128D face au raw 512D non démontrée ;
- supériorité du siamois face à PCA/random non démontrée ;
- performance biométrique industrielle non démontrée ;
- gain de latence 1:N non mesuré et non démontré.

Ce résultat négatif est limité à ce backbone ImageNet ResNet-18, ce dataset LFW, cette
dimension, ces paires et ce protocole. Il ne démontre pas que la compression d'embeddings
ou l'apprentissage de métrique sont inefficaces en général.

## 14. Pourquoi G2 reste en échec

Le calcul historique était apparié entre les routes, mais il rééchantillonnait des indices
de paires authentiques et imposteurs. Plusieurs paires peuvent partager une même identité ;
elles ne sont donc pas indépendantes.

Le défaut `E-STAT-001` est précisément :

```text
l'analyse exécutée était un bootstrap au niveau des paires,
alors que le contrat d'incertitude la décrivait comme identity-aware.
```

Par conséquent :

- G2 `estimator_and_statistical_validity` reste `FAIL` ;
- la non-infériorité reste `NOT_DEMONSTRATED` ;
- Study 1 reste bloquée ;
- les intervalles historiques restent visibles et reproductibles, mais ils ne peuvent pas
  être renommés rétroactivement « identity-aware ».

La correction v0.2.2 preregistrée prévoit un **protocol-preserving weighted subject-slot
bootstrap adapted to the sparse symmetric LFW pair graph** :

- 963 identités TEST sont rééchantillonnées avec remise ;
- une arête authentique \((i,i)\) reçoit le poids \(m_i\) ;
- une arête imposteur observée \((i,j)\) reçoit le poids \(m_i m_j\) ;
- aucune paire absente du protocole LFW DevTest n'est inventée ;
- la couverture doit être validée par simulation ;
- de nouveaux artefacts versionnés devront être publiés sans écraser Study 0.

La spécification n'est pas encore une implémentation ni un résultat. Même une couverture
validée ne suffirait pas, à elle seule, à déclarer `128D is non-inferior` : elle rendrait
l'estimateur admissible, puis les résultats corrigés devraient encore satisfaire la règle
de décision.

## 15. Ce que cette étude anticipe du cours de réduction dimensionnelle

La micro-étude rend concrètes plusieurs notions qui peuvent sinon rester abstraites.

| Notion pédagogique | Manifestation dans Study 0 |
|---|---|
| donnée en haute dimension | embedding ResNet-18 512D |
| réduction dimensionnelle | projection vers 128D |
| PCA | baseline non supervisée ajustée sur TRAIN |
| représentation latente | gabarit 128D normalisé |
| conservation de l'information | maintien de la discrimination biométrique |
| apprentissage supervisé | labels de paires authentiques/imposteurs |
| apprentissage de métrique | optimisation des distances entre embeddings |
| baselines | raw, random, PCA, siamois |
| compromis d'ingénierie | stockage et coût de recherche contre FNMR/FMR |
| généralisation | TRAIN/VALIDATION/TEST séparés |
| robustesse | plusieurs seeds et règle tous-seeds |
| incertitude | bootstrap apparié et dépendance par identité |
| falsification | une hypothèse peut échouer sans être réinterprétée comme succès |

Le cours pose typiquement :

> Comment représenter des données de grande dimension dans un espace plus petit ?

Notre étude pose une question plus exigeante :

> Jusqu'où peut-on réduire un embedding biométrique sans perdre une capacité de
> discrimination jugée indispensable, et une projection supervisée est-elle meilleure
> qu'une PCA à dimension égale ?

La formulation expérimentale devient :

\[
\underbrace{\mathrm{Raw}_{512}}_{\text{référence sans compression}}
\quad\text{vs}\quad
\underbrace{\mathrm{PCA}_{128}}_{\text{compression générique}}
\quad\text{vs}\quad
\underbrace{\mathrm{Random}_{128}}_{\text{contrôle}}
\quad\text{vs}\quad
\underbrace{\mathrm{Siamois}_{128}}_{\text{compression orientée paires}}.
\]

## 16. Les questions scientifiques apparues « dans le bon ordre »

Le projet a commencé avec une contrainte concrète :

> **« 512 dimensions peuvent-elles être ramenées à 128 pour une galerie ou un dispositif
> contraint ? »**

Cette question a naturellement produit les suivantes :

1. Que perd-on lors de la réduction ?
2. Comment traduire « perdre de l'information » en métriques biométriques ?
3. Quelle référence représente l'absence de compression ?
4. Quelle baseline représente une compression simple mais sérieuse ?
5. PCA suffit-elle ?
6. Une projection aléatoire suffit-elle déjà ?
7. La supervision par paires apporte-t-elle quelque chose ?
8. Le gain éventuel est-il stable pour tous les seeds ?
9. Comment séparer performance de représentation et transfert d'un seuil opérationnel ?
10. Comment démontrer la non-infériorité ?
11. Les paires sont-elles réellement indépendantes ?
12. Les conclusions résistent-elles à un bootstrap au niveau des identités ?
13. Les économies théoriques produisent-elles un gain réel de latence 1:N ?
14. Le résultat se reproduit-il avec un backbone facial reconnu et des données plus
    représentatives ?

Il ne s'agit donc pas d'une simple application décorative de PCA. Le projet relie réduction
dimensionnelle, metric learning, biométrie, ingénierie des performances, falsification et
assurance de recherche.

## 17. Lecture à trois niveaux

### 17.1 Vue pédagogique

Un embedding est une liste de nombres qui résume une image. Passer de 512 à 128 nombres
revient à fabriquer un résumé quatre fois plus court.

PCA fabrique le résumé en gardant surtout les directions où les données changent le plus.
Le siamois fabrique le résumé en utilisant des exemples de « même personne » et de
« personnes différentes ». Il essaie d'organiser le résumé pour que cette distinction
reste facile.

Le fait que le siamois utilise plus d'information ne garantit pas qu'il gagne. Il faut le
tester contre PCA, contre une projection aléatoire et contre l'embedding original.

### 17.2 Vue ingénieur

Le système ajoute une tête linéaire de 65 664 paramètres après un ResNet-18 gelé. Le
payload par gabarit passe de 2 048 à 512 octets en float32. Le coût de comparaison exacte
descend théoriquement de 512N à 128N composantes, mais le coût d'extraction reste inchangé
et la latence de bout en bout n'est pas mesurée.

La décision d'adoption doit donc combiner :

- performance biométrique au point opératoire pertinent ;
- robustesse statistique ;
- taille de galerie ;
- coût de la projection ;
- architecture d'indexation ;
- latence mesurée ;
- contraintes de déploiement.

### 17.3 Vue recherche

Study 0 compare un estimateur non comprimé et trois transformations 128D sous splits
communs. La revendication primaire est une non-infériorité en
\(\Delta_{\mathrm{FNMR}}\) à FMR fixé, avec marge absolue 0,03 et règle tous-seeds.

PCA isole une compression linéaire non supervisée ; random isole une projection sans
apprentissage ; siamese teste l'apport de la supervision par paires. Le défaut
`E-STAT-001` invalide la qualification identity-aware des intervalles historiques. La
réanalyse preregistrée doit restaurer les endpoints sujets, préserver le graphe sparse
observé, appliquer les multiplicités sujet et démontrer sa couverture avant toute nouvelle
inférence.

## 18. Réponses complètes aux trois interventions de la discussion

### 18.1 « PCA/PCLS est-elle liée à notre réduction 512D → 128D ? »

Oui. PCA et la projection siamoise réalisent toutes deux une réduction dimensionnelle
linéaire 512D → 128D. PCA choisit les axes de variance maximale sans utiliser les identités.
Le siamois choisit une projection au moyen des paires annotées et d'une contrastive loss.

PCA demande :

> Quelles directions conservent le mieux la structure statistique générale des données ?

Le siamois demande :

> Quelles directions 128D sont les plus utiles pour rapprocher les mêmes identités et
> séparer les identités différentes ?

La projection siamoise peut donc être vue comme une réduction supervisée par paires, mais
elle n'est pas une PCA. PCA est précisément une baseline indispensable pour déterminer si
la supervision apporte réellement quelque chose.

### 18.2 « On compare bien à d'autres modèles, dont PCA ? »

Oui. Les comparaisons exécutées sont `raw512`, `random128`, `pca128` et `siamese128`. Elles
doivent utiliser le même TEST, les mêmes paires, les mêmes métriques et le même cadre
d'incertitude. PCA doit être ajustée sur TRAIN uniquement.

La troncature et l'autoencodeur ont été évoqués comme extensions possibles, mais ne font
pas partie de Study 0. Ils ne doivent pas être présentés comme résultats existants.

Les trois comparaisons centrales restent :

\[
\mathrm{Siamois}_{128}\ \text{vs}\ \mathrm{Raw}_{512},
\]

\[
\mathrm{Siamois}_{128}\ \text{vs}\ \mathrm{PCA}_{128},
\]

\[
\mathrm{Siamois}_{128}\ \text{vs}\ \mathrm{Random}_{128}.
\]

Elles testent respectivement le prix de la compression, la valeur de la supervision face à
une forte baseline et l'existence d'une structure apprise au-delà d'une projection
quelconque.

### 18.3 « J'étais donc déjà dans un cas pratique avant le cours ? »

Oui, avec la correction terminologique suivante : il s'agit d'abord d'un cas de
**compression de représentation**, pas encore de compression complète du ResNet.

Le cas pratique est même plus exigeant qu'un exercice introductif, car il ne s'arrête pas à
la visualisation d'un espace réduit. Il demande :

- quelle propriété doit être préservée ;
- quelle baseline pourrait expliquer le même résultat ;
- quelle dégradation est acceptable ;
- comment choisir les seuils sans fuite de TEST ;
- comment mesurer l'incertitude sous dépendance entre paires ;
- et quelles économies sont effectivement mesurées plutôt que supposées.

Le gate en échec n'enlève rien à la valeur pédagogique du cas. Au contraire, il transforme
une démonstration technique en étude falsifiable : le mécanisme fonctionne, mais la
revendication de performance reste non démontrée.

## 19. Ce que le lecteur ne doit pas conclure

Ce document ne permet pas d'affirmer que :

- le siamois est supérieur à PCA ;
- le siamois est non inférieur au raw512 ;
- 128D est optimal ;
- PCA échoue en biométrie ;
- la compression divise automatiquement la latence par quatre ;
- ResNet-18 ImageNet est un extracteur biométrique industriel ;
- les résultats LFW se généralisent à une galerie nationale ;
- le bootstrap sujet corrigé a déjà été exécuté ;
- G2 est clos ;
- Study 1 a commencé.

Les formulations admissibles à ce stade sont :

- le mécanisme de projection partagée a été exécuté ;
- la supervision par paires modifie la projection ;
- quatre routes comparables ont été évaluées dans un cadre exploratoire ;
- la réduction apporte un gain déterministe sur le payload des gabarits ;
- la revendication de non-infériorité demeure `NOT_DEMONSTRATED` ;
- l'estimateur identity-aware reste à implémenter et valider selon la spécification v0.2.2.

## 20. Prochaines extensions, sans les confondre avec Study 0

Après résolution de `E-STAT-001` et passage des gates préalables, des études séparées
pourront examiner :

1. un backbone facial reconnu ;
2. plusieurs dimensions : 64D, 128D, 256D ;
3. différentes familles de compression sous budgets appariés ;
4. quantification des gabarits ;
5. indexation et recherche 1:N ;
6. latence, mémoire et débit mesurés ;
7. décalages de domaine, capteurs, qualité et âge des templates ;
8. réplication indépendante.

Un autoencodeur, une troncature, une projection supervisée non linéaire ou une distillation
peuvent être de bonnes hypothèses futures. Ils doivent néanmoins être introduits dans une
nouvelle preregistration avec budgets, données, dimensions, seeds, métriques et règle de
décision gelés avant l'ouverture de TEST.

## 21. Liens internes

- [README du projet](../README.md)
- [Résultats historiques de Study 0](../RESULTS_LFW_V0.1.md)
- [Erratum E-STAT-001](../ERRATA_STUDY_0.md)
- [Spécification v0.2.2 du bootstrap sujet](../protocol/studies/study_0_subject_bootstrap_spec.md)
- [Placeholder de l'ablation de compression](../protocol/studies/study_2_compression_ablation.yaml)
- [Contrat d'histoire expérimentale et d'errata](EXPERIMENT_HISTORY_AND_ERRATA.md)
- [Programme de recherche](../RESEARCH_PROGRAM.md)

## 22. Conclusion

PCA et la projection siamoise sont bien deux réponses au même problème de départ : réduire
un embedding ResNet-18 de 512 à 128 dimensions. PCA conserve prioritairement la variance
globale ; la projection siamoise apprend, à partir de paires, un espace destiné à préserver
la décision de similarité d'identité.

La comparaison avec PCA n'est donc pas un ajout pédagogique périphérique. Elle est une
condition de falsification de la valeur ajoutée du siamois. La comparaison avec raw512
teste le prix biométrique de la compression. La comparaison avec random128 vérifie que le
résultat ne provient pas simplement du changement de dimension.

Le cas pratique a effectivement précédé le cours et lui donne un ancrage concret. Mais sa
valeur scientifique vient de la discipline conservée à la fin de l'histoire : un mécanisme
exécuté n'est pas une performance démontrée, une moyenne favorable n'est pas une preuve de
robustesse, et un défaut statistique découvert doit rester visible jusqu'à sa correction.

Le statut final ne change pas :

```text
G2 = FAIL
NON-INFERIORITY = NOT_DEMONSTRATED
STUDY 0 REANALYSIS v0.2.2 = PREREGISTERED, NOT IMPLEMENTED
STUDY 1 = BLOCKED
```
