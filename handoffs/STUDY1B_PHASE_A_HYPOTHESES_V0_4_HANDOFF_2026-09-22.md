# État du programme et suite

Document de reprise. Il résume où en est la recherche, ce qui bloque, et dans quel
ordre continuer. Tout ce qui suit est vérifiable dans le dépôt au head
`cb43fdb1543700ae1429a0ed93ea99eed9065899`.

---

## 1. Où en est la recherche

**La question.** Peut-on comprimer une représentation faciale de 512 dimensions en 128
sans la rendre biométriquement inacceptable — et, si oui, ce gain vaut-il quelque chose
en ingénierie sur un appareil en périphérie ?

**La lignée.** Study 0 comparait quatre routes sur un extracteur ResNet-18 ImageNet ;
résultat négatif après correction de l'estimation d'incertitude, mais substrat non
représentatif. Study 1A a qualifié le substrat manquant, un AdaFace IR101 entraîné sur
WebFace12M. Study 1B reprend la comparaison sur ce substrat.

**Le volet statistique est clos négatif.** Les campagnes S4N1 et S4N2 ont établi que le
protocole confirmatoire n'atteint pas la puissance requise de 0,90 à
Δ FNMR = 0,01 : 0,869 et 0,849 pour le candidat préféré. Les deux campagnes partagent
la même population simulée : c'est **une** ligne de preuve examinée par deux procédures
d'incertitude, pas deux confirmations indépendantes.

**Les résultats biométriques réels restent scellés.** SCREEN, le TEST de qualification,
les performances réelles des routes et la géométrie de représentation n'ont jamais été
ouverts. S4N3 n'est pas lancé.

**Le volet ingénierie est conçu, revu, non exécuté.** Sept cycles de revue ont porté sur
la provenance, les pare-feux informationnels et le transport des paquets de revue. Un
huitième a porté sur la validité de construit de la Phase A : verdict
`ACCEPT_WITH_LIMITATIONS` sur le head `b5720dd7`, avec trois blocages prospectifs B1,
B2 et B3. Les corrections v0.1 y répondent au head `cb43fdb1`.

## 2. Ce qui bloque aujourd'hui

1. **La confirmation indépendante de B1/B2/B3 n'est pas obtenue.** Trois tentatives de
   seconde revue ont échoué de la même manière : paraphrase du contrat puis approbation,
   avec de l'invention pour combler les trous — dont une exigence attribuée à `AGENTS.md`
   qui n'y figure pas, et une déclaration « tests réussis » sans exécution. Le
   propriétaire envisage de faire cette passe lui-même, contresignée par un collègue de
   l'autorité technique.
2. **Quatorze décisions préalables ne sont pas prises.** Voir §3.
3. **La plateforme n'est pas matérialisée**, et ne doit pas l'être avant les deux points
   précédents.

## 3. Les quatorze décisions à geler

Aucune ne se tranche en regardant des données. Détail, justification et défauts
proposés : section 12 du chapitre, section 7 de la spécification de traçabilité.

| statut | décisions |
| --- | --- |
| défaut argumenté à accepter ou remplacer | D1 régime de saturation · D2 débit dérivé · D3 cache effectif · D4 caractérisation de bande passante · D5 comptes attendus et réalisés · D7 marge RAM · D9 régime thermique · D10 banc thermiquement représentatif |
| valeurs de scénario à déclarer | D6 échelle de paliers · D8 profils de service · D11 classes de déploiement · D14 requêtes par passage |
| arbitrage explicite attendu | D12 groupement des requêtes · D13 processus d'arrivée |

Deux décisions dominent : **D1** commande si la comparaison principale peut s'énoncer en
chiffre ; **D9** porte sur un mécanisme en marche d'escalier, sur le matériel qui reste à
choisir, et n'avait été vue par personne en sept cycles.

## 4. Questions ouvertes relevant du propriétaire

- **Scénario** : paliers matériels candidats et ordre d'essai ; profils horaires ;
  classes de déploiement avec alimentation, plafond, ambiant, boîtier et veille ;
  politique de sélection d'images et caméras par appareil ; nombre de passages attendus,
  densité d'appareils, taille de liste de surveillance, point de fonctionnement visé.
- **Gouvernance** : qui tient chacun des trois rôles de l'élicitation aveugle, sans
  qu'une même personne en tienne deux ; juridiction et opérateur de chaque branche ;
  qualification juridique par un conseil.
- **Produit** : faut-il ajouter une route 512D quantifiée sur 8 bits à la comparaison
  biométrique future, pour comparer à octets égaux ?

## 5. Ordre des étapes

```
1  Résoudre la seconde revue B1/B2/B3 liée à cb43fdb1
2  Prendre les quatorze décisions — sans regarder de données
3  Dériver STUDY1B_PHASE_A_EXECUTION_GUARD_SPEC_V0_1.yaml
4  Revue indépendante courte de cette spécification
5  Matérialiser la plateforme et lier les valeurs physiques
6  Geler l'enveloppe opérationnelle et les seuils experts   (parallèle à 5, jamais après 8)
7  Exécuter la Phase A
8  Ouvrir SCREEN
9  Croiser biométrie, ingénierie et conséquences opérationnelles
```

L'étape 8 vient **après** l'étape 5. Ouvrir SCREEN avant la matérialisation violerait la
règle d'interprétation n° 9 du benchmark : le palier matériel, la bibliothèque de calcul,
le nombre de fils d'exécution et le wattmètre seraient choisis par des personnes
connaissant les écarts biométriques.

## 6. Forme de la spécification de gardes

Un seul artefact normatif nouveau, pas une couche de gouvernance supplémentaire. Chaque
garde porte :

```yaml
guard_id: PHASE_A_ZERO_SWAP
source_clause: ram_residency_contract
guard_type: RUNTIME_ASSERTION
freeze_phase: PRE_PLATFORM_MATERIALIZATION
false_conclusion_if_violated: >-
  512D serait déclaré RAM-faisable alors que l'OS a compensé par le disque.
priority: CRITICAL
logic:
  assertion: swap_delta_pages == 0
  evaluated: per_measurement_window
  failure_mode: FAIL_CLOSED
evidence_retained: [swap_pages_before, swap_pages_after, observation_timestamp]
materialization:
  observation_method: null
  source_reference: null
```

Trois propriétés à ne pas perdre. **La logique se gèle avant la machine** ; seule la
matérialisation attend. **La conséquence fausse fixe la priorité**, et non la facilité du
test : le premier lot couvre le swap, l'isolement des bras, la sémantique de recherche
exacte, l'échauffement et l'alternance, le générateur hors appareil, le plan de mesure
énergétique, puis les deux classifieurs de régime. **Chaque garde conserve la valeur
observée**, pas seulement son verdict, sans quoi un relecteur ne peut pas distinguer
« vérifié et correct » de « n'a pas tourné ».

## 7. Le piège à ne pas retomber dedans

Sur huit cycles de revue, deux ont porté sur l'objet de l'étude et six sur le processus.
La raison est structurelle : un défaut de processus est bon marché à trouver, non ambigu,
et se ferme par une édition de texte prouvable par un hash ; une question de mesure
demande du jugement métier. Une chaîne de revue dérive vers le vérifiable. Et la revue de
processus s'auto-engendre, chaque correction créant le constat suivant, alors que la
revue de mesure termine.

La correction n'est pas moins de rigueur. C'est de déplacer la rigueur de la preuve que
le processus est propre vers la preuve que l'expérience exécutera réellement
l'expérience conçue. Concrètement : pas de N9, N10, N11 — une spécification de gardes,
puis un préflight qui les asserte.
