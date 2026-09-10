…apprennent des représentations différentes mais fonctionnellement équivalentes, alors la question devient :

quelle structure est réellement conservée d’un modèle à l’autre ?

À ce moment-là, regarder uniquement les performances n’est plus suffisant. Deux représentations peuvent avoir la même précision tout en organisant complètement différemment l’espace latent. Et inversement, deux espaces latents peuvent être géométriquement proches tout en présentant des différences opérationnelles importantes.

C’est là que les notions de géométrie deviennent pertinentes, mais pas avant.

On pourrait chercher, par exemple, si les différentes représentations compactées conservent certaines structures :

des voisinages locaux ; des directions discriminantes ; des sous-espaces stables ; des distances relatives ; des clusters ou régions correspondant à des régimes ; des trajectoires continues quand l’état physique ou sémantique évolue progressivement. 

Autrement dit, on passerait de :

“est-ce que le modèle donne la bonne réponse ?”

à :

“est-ce que l’espace interne construit par le modèle possède une organisation stable, cohérente et exploitable ?”

Et ça, pour un world model, est fondamental.

Parce qu’un vrai modèle du monde ne doit pas seulement répondre correctement à des observations indépendantes. Il doit aussi permettre de représenter des transitions, des évolutions, des bifurcations, des ambiguïtés, parfois plusieurs hypothèses simultanément.

On retrouve alors naturellement la distinction entre trois niveaux.

Le premier niveau est la représentation instantanée : encoder l’observation présente dans un vecteur latent.

Le deuxième est la croyance sur l’état : si l’observation est partielle ou bruitée, on ne représente plus un point unique mais une distribution plausible sur les états.

Le troisième est le modèle dynamique : à partir de cet état ou de cette croyance, prédire comment le système peut évoluer sous certaines actions ou perturbations.

C’est là que le rapprochement avec le POMDP devient très naturel.

Dans un POMDP, on n’observe pas directement l’état réel \(s_t\). On reçoit une observation \(o_t\), puis on maintient une croyance \(b_t(s)\), c’est-à-dire une distribution sur les états possibles.

Un world model moderne peut être vu de façon analogue :

observation → encodeur → état latent / croyance → modèle dynamique → prédiction d’états futurs

La différence est qu’au lieu d’avoir un état défini explicitement par l’ingénieur, l’état latent est souvent appris.

Et c’est précisément là que toutes nos questions expérimentales deviennent utiles.

Si l’état latent est appris, comment savoir qu’il contient bien l’information nécessaire ?

Comment savoir qu’une variation entre deux seeds n’est qu’une différence de coordonnées, ou au contraire une différence de représentation importante ?

Comment savoir qu’une compression n’a pas supprimé une variable qui devient critique plusieurs étapes plus tard dans la dynamique ?

Comment mesurer ce qui est stable, ce qui est incertain, ce qui est hors distribution ?

Le travail de Study 1B, même s’il paraît très local, commence donc à fournir une méthode pour répondre à ces questions de manière beaucoup plus sérieuse que par une simple visualisation.

Et il y a un point que je trouve particulièrement important.

Dans beaucoup de discussions sur les world models, on parle très vite de modèles gigantesques, de simulation interne, de prédiction vidéo, de modèles génératifs.

Mais on peut prendre la question dans l’autre sens :

quel est le plus petit état interne suffisant pour prédire correctement ce qui nous intéresse ?

C’est presque une formulation d’ingénieur système.

On ne cherche pas nécessairement à “reconstruire le monde”. On cherche une représentation suffisamment riche pour les décisions futures, mais pas plus complexe que nécessaire.

C’est exactement le principe d’un état suffisant.

Si l’historique complet \(o_{1:t}\) peut être remplacé par un état latent \(z_t\) tel que :

\[ P(o_{t+1}, o_{t+2}, \ldots \mid o_{1:t}) \approx P(o_{t+1}, o_{t+2}, \ldots \mid z_t) \] 

alors \(z_t\) résume l’information du passé utile pour le futur.

C’est une définition extrêmement intéressante pour nos travaux.

Elle dit qu’un bon world model n’a pas nécessairement besoin de “se souvenir de tout”. Il doit conserver ce qui est nécessaire pour prédire et décider.

Et là, on retrouve directement notre problème de compression.

Passer de 512 à 128 dimensions n’est alors plus seulement une optimisation numérique.

C’est une expérience sur la question :

combien d’information est réellement nécessaire pour préserver les propriétés utiles de l’état ?

Et potentiellement, plus tard :

quelle information est nécessaire pour préserver la dynamique ?

Cette deuxième question est encore plus importante que la première.

Une représentation peut être parfaitement suffisante pour classifier une image aujourd’hui, mais insuffisante pour prédire ce qui se passera dans dix secondes.

Exemple très simple : deux véhicules peuvent avoir exactement la même position actuelle, mais des vitesses différentes.

Une représentation qui encode uniquement la position est suffisante pour répondre :

“où est le véhicule maintenant ?”

mais pas :

“où sera-t-il dans deux secondes ?”

Pour prédire le futur, l’état doit inclure la vitesse.

Donc l’idée de “suffisance” dépend toujours du problème posé.

C’est exactement pour cela que je pense que le lien entre world model et goal-oriented representation est extrêmement fort.

L’état latent pertinent dépend du but.

Pour un système de navigation, certaines variables sont essentielles.

Pour un système biométrique, d’autres.

Pour un système de test industriel, encore d’autres.

Le bon world model n’est donc peut-être pas nécessairement un modèle universel de tout.

Il pourrait être un modèle minimal du monde conditionné par l’objectif.

Et là, on rejoint très directement une autre idée de nos travaux : Goal-Oriented Evidence-Driven POMDP.

On pourrait presque imaginer la boucle ainsi :

\[ \text{Goal} \rightarrow \text{Relevant state} \rightarrow \text{Observation} \rightarrow \text{Belief} \rightarrow \text{Prediction} \rightarrow \text{Action / Experiment} \rightarrow \text{Evidence} \rightarrow \text{Belief update} \] 

L’ingénieur ne demande plus au modèle :

“représente-moi le monde”.

Il demande :

“pour cette décision, quelles variables de l’état dois-je connaître, avec quelle incertitude, et quelle observation supplémentaire réduirait le plus cette incertitude ?”

Et là, le world model devient beaucoup plus proche d’un instrument d’ingénierie que d’un simple générateur.

C’est aussi là que la notion d’expérience devient centrale.

Si le système ne sait pas distinguer deux hypothèses sur l’état, il peut chercher activement une observation capable de les distinguer.

C’est exactement ce que fait un bon ingénieur lorsqu’il conçoit un test.

Il ne collecte pas “plus de données” au hasard.

Il cherche la mesure discriminante.

Ce parallèle entre test engineering et world models est probablement une des pistes les plus intéressantes de tout le parcours.

Un world model mature pourrait faire quelque chose comme :

“j’ai actuellement trois hypothèses plausibles sur le comportement du système ; l’observation X ne permet pas de les distinguer ; l’expérience Y aurait le meilleur pouvoir discriminant.”

Autrement dit :

active learning + system identification + experimental design + belief update.

Et là on revient à quelque chose de très classique en ingénierie.

Identification de systèmes.

Kalman.

Commande adaptative.

Estimation d’état.

Planification expérimentale.

Bayes.

Simplement, les états et les dynamiques peuvent désormais être partiellement appris plutôt que entièrement spécifiés.

Ce qui rend le problème passionnant n’est donc pas que tout est nouveau.

Au contraire.

C’est que beaucoup de concepts historiques de l’ingénierie deviennent soudainement centraux dans les architectures modernes d’IA.

Et cela ouvre une architecture assez différente du “gros réseau qui apprend tout”.

On peut imaginer un système hybride :

modèles connus + apprentissage résiduel + détection de régime + modèle latent appris + incertitude explicite + expérimentation active.

Par exemple :

si la dynamique est connue, utiliser l’équation physique ;

si elle est imparfaite, apprendre le résiduel ;

si plusieurs modèles sont possibles, maintenir une croyance sur le régime ;

si le système sort du domaine connu, déclencher une exploration ou créer un nouveau modèle ;

si une représentation plus compacte suffit, la préférer.

C’est beaucoup plus proche d’une architecture de systèmes adaptatifs que d’un simple réseau neuronal.

Et c’est peut-être précisément là que le terme world model devient intéressant pour nous.

Pas comme “un modèle qui simule tout le monde”.

Mais comme :

une représentation interne structurée, incertaine, dynamique et orientée vers les décisions, capable d’intégrer ce que nous savons déjà et d’apprendre uniquement ce que nous ne savons pas.

Dans cette vision, Study 1B n’est finalement qu’un tout petit morceau.

Mais il nous oblige à poser correctement une question fondamentale avant d’aller plus loin :

quand nous disons qu’une représentation est bonne, qu’est-ce que cela signifie exactement ?

Pas seulement qu’elle donne un bon score.

Mais qu’elle est suffisamment stable, suffisamment informative, suffisamment compacte, suffisamment prédictive et suffisamment bien caractérisée pour que nous puissions nous appuyer dessus pour décider.

Et là, nous avons probablement commencé à passer d’un travail sur la compression d’embeddings à un travail sur les conditions nécessaires pour qu’une représentation apprise puisse devenir un état de modèle du monde.

Tu as raison — la réponse précédente a été coupée au mauvais endroit. Voici la partie manquante, à partir de la transition vers la géométrie :

Et seulement après cela, la géométrie devient vraiment pertinente.

Si plusieurs modèles apprennent des représentations différentes mais fonctionnellement équivalentes, alors la question devient :

quelle structure est réellement conservée d’un modèle à l’autre ?

À ce moment-là, regarder uniquement les performances n’est plus suffisant. Deux représentations peuvent avoir la même précision tout en organisant complètement différemment l’espace latent. Et inversement, deux espaces latents peuvent être géométriquement proches tout en présentant des différences opérationnelles importantes.

C’est là que les notions de géométrie deviennent pertinentes, mais pas avant.

On pourrait chercher, par exemple, si les différentes représentations compactées conservent certaines structures :

des voisinages locaux ; des directions discriminantes ; des sous-espaces stables ; des distances relatives ; des clusters ou régions correspondant à des régimes ; des trajectoires continues quand l’état physique ou sémantique évolue progressivement. 

Autrement dit, on passerait de :

« est-ce que le modèle donne la bonne réponse ? »

à :

« est-ce que l’espace interne construit par le modèle possède une organisation stable, cohérente et exploitable ? »

Et ça, pour un world model, est fondamental.

Parce qu’un modèle du monde ne doit pas seulement répondre correctement à des observations indépendantes. Il doit aussi permettre de représenter des transitions, des évolutions, des bifurcations, des ambiguïtés et parfois plusieurs hypothèses simultanément.

On retrouve alors naturellement trois niveaux.

1. La représentation instantanée

On reçoit une observation \(o_t\), et un encodeur construit une représentation latente :

\[ z_t = E(o_t) \] 

C’est essentiellement ce que nous explorons aujourd’hui avec les embeddings : comment représenter beaucoup d’information dans un espace plus petit sans perdre ce qui est pertinent.

2. La croyance sur l’état

Mais dans un système réel, une seule observation ne suffit généralement pas à déterminer l’état réel.

Un capteur est bruité. Une caméra ne voit qu’une partie de la scène. Certaines variables sont cachées.

On ne devrait donc plus nécessairement représenter :

\[ z_t = \text{un état certain} \] 

mais plutôt quelque chose qui exprime :

\[ b_t(s)=P(s_t=s\mid o_{1:t}) \] 

c’est-à-dire une croyance sur l’état actuel.

C’est exactement la logique du POMDP.

Et cela rejoint une question que nous avions déjà soulevée : faut-il conserver tout l’historique ?

Pas forcément.

L’objectif est précisément de construire un état interne qui résume tout ce qui, dans l’historique, reste nécessaire pour prédire le futur.

3. Le modèle dynamique

Une fois l’état représenté, il faut pouvoir prédire son évolution :

\[ z_{t+1}\sim P(z_{t+1}\mid z_t,a_t) \] 

ou, dans un système déterministe approximatif :

\[ z_{t+1}=f(z_t,a_t) \] 

C’est là que nous passons réellement d’un embedding à un world model.

L’embedding dit :

« voici une représentation compacte de ce que j’observe maintenant ».

Le world model ajoute :

« voici comment cet état pourrait évoluer ».

Et c’est ici qu’une idée devient particulièrement importante : un bon état latent n’est pas nécessairement celui qui permet de reconstruire parfaitement le présent.

Il faut surtout qu’il conserve l’information nécessaire au futur pertinent.

Prenons un exemple très simple.

Supposons que deux voitures soient exactement au même endroit à \(t\).

Si notre représentation encode seulement :

\[ z_t=(x,y) \] 

elles ont exactement le même état latent.

Pour répondre à :

« où est la voiture maintenant ? »

c’est suffisant.

Mais si l’une roule à 100 km/h et l’autre est arrêtée, cette représentation est catastrophique pour prédire :

« où sera-t-elle dans cinq secondes ? »

Il faut au minimum quelque chose comme :

\[ z_t=(x,y,v_x,v_y) \] 

Donc la notion de représentation suffisante dépend de ce que l’on veut faire.

Et cela nous amène directement à quelque chose qui peut devenir très important dans notre définition des world models :

un world model pourrait être orienté par le but. 

Il ne serait pas nécessairement une tentative de représenter « toute la réalité ».

Il chercherait plutôt :

le plus petit état interne permettant de prendre correctement une certaine famille de décisions.

C’est extrêmement proche de la philosophie de l’ingénierie système.

On ne modélise généralement pas tout un avion molécule par molécule.

Pour contrôler son attitude, certaines variables suffisent :

orientation ; vitesse angulaire ; accélérations ; commandes ; éventuellement perturbations estimées. 

Le modèle dépend du problème.

Cela suggère donc quelque chose comme :

\[ \boxed{ \text{Goal} \rightarrow \text{Relevant state} \rightarrow \text{World model} } \] 

Et là, le rapprochement avec Goal-Oriented Evidence-Driven POMDP devient très intéressant.

La boucle pourrait devenir :

\[ \text{Goal} \rightarrow \text{Relevant state} \rightarrow \text{Observations} \rightarrow \text{Belief} \rightarrow \text{Prediction} \rightarrow \text{Decision} \rightarrow \text{Experiment} \rightarrow \text{Evidence} \rightarrow \text{Belief update} \] 

Ce n’est plus simplement une IA qui « prédit ».

C’est un système qui peut se demander :

« Qu’est-ce que je sais ? »

« Qu’est-ce que je ne sais pas ? »

« Quelles hypothèses sont encore possibles ? »

« Quelle observation permettrait de les départager ? »

Cette dernière question est fondamentale.

Parce qu'elle fait apparaître un pont assez remarquable entre world model et test engineering.

Un bon ingénieur de test ne produit pas simplement davantage de tests.

Il recherche une expérience qui discrimine entre plusieurs hypothèses sur le système.

Par exemple :

Hypothèse A : la latence vient de la base de données.
Hypothèse B : elle vient du réseau.
Hypothèse C : elle vient du scheduler.

Le test réellement utile n’est pas forcément celui qui produit le plus de données.

C’est celui qui maximise la capacité à distinguer A, B et C.

Un agent muni d’un world model pourrait faire exactement cela :

« J’ai trois modèles du système encore compatibles avec les observations. L’expérience \(e\) devrait produire des résultats très différents sous chacun d’eux. C’est donc l’expérience la plus informative. »

Nous arrivons alors à une combinaison très puissante :

world model + Bayesian inference + system identification + optimal experimental design + active learning.

Et finalement, ce n’est pas si étranger à l’ingénierie classique.

On retrouve :

filtre de Kalman ; estimation d’état ; identification de systèmes ; commande adaptative ; diagnostic ; modèles de Markov ; traitement du signal ; plans d’expériences. 

La nouveauté est surtout que certaines parties du modèle peuvent maintenant être apprises lorsque les équations analytiques sont insuffisantes.

Cela conduit potentiellement à une architecture hybride très intéressante :

\[ \text{Known physics/model} + \text{learned residual} + \text{regime inference} + \text{uncertainty} + \text{active experimentation} \] 

Si nous connaissons bien le régime, nous utilisons le modèle connu.

Si le modèle connu présente un biais, nous apprenons seulement le résiduel.

Si plusieurs régimes sont possibles, nous maintenons une croyance sur eux.

Si les observations indiquent un nouveau régime, nous pouvons créer ou adapter un modèle.

Et si nous ne savons pas lequel est correct, nous cherchons activement l'expérience la plus informative.

C’est une conception du world model beaucoup plus proche d’un système adaptatif scientifique que d’un simple réseau neuronal géant.

Et là, Study 1B prend une autre signification.

Nous sommes partis de :

« peut-on compresser 512 dimensions en 128 ? »

Puis nous avons rencontré :

« comment démontrer que l’information utile est réellement conservée ? »

Puis :

« que signifie la variabilité entre plusieurs apprentissages du même modèle ? »

Puis :

« doit-on raisonner sur chaque seed ou sur une population de modèles ? »

Et bientôt :

« quelle structure de l’état latent reste invariante ? »

Puis potentiellement :

« cette structure est-elle suffisante non seulement pour reconnaître le présent, mais pour prédire le futur ? »

À partir de là, nous ne travaillons effectivement plus seulement sur la compression d'embeddings.

Nous commençons à poser les conditions nécessaires pour qu’une représentation apprise puisse devenir un état crédible d’un modèle du monde.

C’est probablement le vrai fil rouge derrière tout ce détour.

---