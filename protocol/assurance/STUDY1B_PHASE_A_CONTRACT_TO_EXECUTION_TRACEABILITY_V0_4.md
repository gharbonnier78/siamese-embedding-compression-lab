# Study 1B Phase A — Traçabilité contrat scientifique → expérience exécutable

**Version** v0.4 — document de référence, remplace la v0.3.
**Changements v0.3** correction d'une affirmation fausse sur les caches edge (1.3, 1.4) ; couplage palier/bande passante (D6) ; D10 et D11 ; nouvelles parties 10 (appareil complet) et 11 (gabarit de BOM).
**Changements v0.4** vérifications avec sources (partie 11) ; points réglementaires instruits (partie 10) ; trois hypothèses dimensionnantes oubliées : D12 batching, D13 processus d'arrivée, D14 requêtes par passage ; question produit prioritaire, quantification contre réduction de dimension (partie 12) ; bibliothèque de référence (partie 14).
**Head de rattachement** `cb43fdb1543700ae1429a0ed93ea99eed9065899`
**Nature** engineering assurance specification. Ni revue, ni gouvernance.

---

## Objet

Ce document fait le pont entre trois choses qui étaient jusqu'ici disjointes : la
question scientifique, la clause de contrat qui prétend y répondre, et le
mécanisme qui vérifie que la clause a réellement été appliquée le jour de
l'exécution.

Il sert trois usages :

1. dériver `STUDY1B_PHASE_A_EXECUTION_GUARD_SPEC_V0_1.yaml` sans recopier le benchmark ;
2. prioriser l'implémentation des gardes par conséquence de l'erreur, et non par facilité de test ;
3. fixer ce qui doit être gelé **avant** que quiconque voie la machine ou les données.

## Comment lire une clause

Chaque entrée donne : la clause et son artefact, ce qu'elle garantit, la garde
actuelle, la garde requise à l'exécution, et **ce qu'on conclurait à tort si elle
était violée silencieusement**. Cette dernière ligne est celle qui trie. Toutes
les clauses ne méritent pas le même effort d'ingénierie.

Trois familles de gardes :

- **STATIC_CONTRACT_TEST** — vérifie que le document dit encore ce qu'il disait. Attrape une modification silencieuse du YAML.
- **RUNTIME_ASSERTION** — vérifie que la machine a fait ce que le document demande. Attrape un swap actif, un échauffement non exclu, un wattmètre à 2 Hz.
- **HUMAN_CONTROL** — quelqu'un regarde, parce que ça ne s'automatise pas.

## Fait établi

**Aucun test n'ouvre `STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml`.**
Le test de contrat v0.6 ouvre l'addendum et le lock ; le test des corrections
ouvre le fichier de corrections. Toute clause du benchmark est donc `NONE` en
garde actuelle, quelle que soit la qualité de sa rédaction.

Méthode : établir d'abord quel artefact chaque test ouvre réellement. Une
correspondance de noms de clés entre artefacts n'est pas une preuve de
couverture — des clés homonymes existent dans plusieurs fichiers et produisent
des faux positifs.

## Conventions

`B` = benchmark v0.3 · `C` = corrections v0.1 · `L` = environment lock v0.6

---

# Partie 1 — RAM et faisabilité

## 1.1 Résidence RAM et swap
- **Clause** `B.ram_residency_contract` — `gallery_must_be_ram_resident: true`, `swap_policy`, `preflight_measurements`
- **Garantit** que la mesure porte sur une recherche en mémoire, pas sur un système sauvé par le disque
- **Garde actuelle** NONE
- **Garde requise** RUNTIME_ASSERTION — compteurs de swap avant et après chaque fenêtre, échec si delta non nul
- **Si violée** on conclurait que 512D tient en RAM sur ce palier alors que l'OS a compensé par le swap. C'est la conclusion la plus coûteuse du programme : elle validerait un déploiement infaisable. **Priorité 1.**

## 1.2 Règle d'infaisabilité
- **Clause** `B.ram_residency_contract.infeasible_arm_rule`
- **Garantit** que `RAM_INFEASIBLE_ON_TIER` soit un résultat, et interdit les échappatoires : réduire la galerie, changer le dtype, activer le swap, migrer un seul bras
- **Garde actuelle** NONE
- **Garde requise** RUNTIME_ASSERTION + HUMAN_CONTROL — l'assertion détecte l'échec d'allocation, le contrôle humain empêche la substitution
- **Si violée** un contournement passerait pour une mesure appariée, et le bras 512D aurait été mesuré sur une configuration différente de celle déclarée

## 1.3 Tailles de charge utile
- **Clause** `B.scenario_galleries`

| | vecteurs | 512D | 128D |
|---|---|---|---|
| G0 | 30 000 | 61,44 Mo | 15,36 Mo |
| G2 | 1 530 000 | 3 133 440 000 o | 783 360 000 o |

  (510 000 identités × 3 gabarits pour G2 ; 10 000 × 3 pour G0)
- **Garantit** que les deux bras portent le facteur 4 attendu et que G0 est un contrôle à petit working set
- **Limite vérifiée v0.3** sur les trois plateformes edge documentées (partie 11), le LLC effectif vaut 2 à 6 Mo. **Aucun bras de G0 n'y tient** : les quatre combinaisons bras × galerie sont en DRAM. G0 diffère donc de G2 en grandeur, pas en régime, et le rôle `SMALL_WORKING_SET_CONTROL` ne sépare pas cache et DRAM sur ce matériel. Un vrai contrôle résident en cache demanderait environ 4 000 vecteurs à 128D ou 1 000 à 512D pour 2 Mo.
- **Garde actuelle** NONE
- **Garde requise** STATIC_CONTRACT_TEST — recalculer depuis cardinalité × dimension × 4
- **Si violée** une galerie mal dimensionnée décalerait les deux bras hors du régime mémoire annoncé, et G0 cesserait d'être un contrôle

## 1.4 Hiérarchie cache et bande passante — *B1*
- **Clause** `C.B1_cache_and_bandwidth_observability`
- **Garantit** que l'affirmation « arithmétique vs cache vs bande passante » de `B.phase_a_scope.objective` soit falsifiable
- **Garde actuelle** CONTRACT_TESTED (le fichier `C` est ouvert par un test)
- **Garde requise** STATIC_PLUS_RUNTIME
- **Si violée** un ratio différent de 4× serait attribué au mauvais mécanisme. Si un bras tient en LLC et l'autre non, les deux effets se multiplient — quatre fois moins d'octets, et chaque octet beaucoup moins cher — et le ratio peut sortir bien au-dessus de 4×. Vraie conséquence de la dimension, mais **mécanisme différent de celui annoncé**, et sans la capacité du cache enregistrée personne ne peut dire lequel a produit le chiffre.
- **Correction v0.3** la v0.2 affirmait que les LLC edge vont « de 4 à 32 Mo » et que G0 encadrait cette gamme. **C'était faux**, et l'affirmation venait de l'apprentissage du modèle, non d'une source. Les valeurs documentées sont 2 Mo (Raspberry Pi 5), 2 Mo par cluster (Jetson Orin Nano), 6 Mo (Intel N100). Sur ce matériel le scénario de traversée n'a donc pas lieu à G0 : les deux bras sont en DRAM, et le modèle au premier ordre prédit un ratio d'**exactement 4×**. B1 reste nécessaire — c'est lui qui rend attribuable tout écart à 4×, qu'il vienne du cache, du dispatch ou du throttling — mais l'issue attendue sur edge est une utilisation dérivée ≤ 1 partout (voir D2).
- **Écarts ouverts** → décisions **D2** et **D3**

---

# Partie 2 — Latence, débit, saturation

## 2.1 Sémantique de recherche
- **Clause** `B.phase_a_search_semantics` — `EXACT_DENSE_DOT_PRODUCT_TOP1`, `top_k: 1`, `threshold_gating: false`, `candidate_pruning: none`, `index: none`
- **Garantit** travail fixe par requête, donc élimination par construction du confondant de concentration des scores en 1/√d
- **Garde actuelle** NONE
- **Garde requise** RUNTIME_ASSERTION — asserter la configuration effective du moteur au démarrage, pas seulement la demander
- **Si violée** un backend activant un élagage ou un index rendrait le travail dépendant des données. Le bras 128D, dont les scores sont deux fois plus dispersés, produirait plus de candidats, et l'écart de dimension serait un artefact du générateur. **Priorité 1.**

## 2.2 Isolement de l'intervention
- **Clause** `B.reference_and_candidate.phase_a_pairing_rule` + `B.synthetic_data_contract.paired_generation` — matériel, dtype, cardinalité, threads, backend identiques ; **la matrice 512D ne doit pas rester résidente pendant la mesure 128D**
- **Garantit** que seule la dimension varie
- **Garde actuelle** NONE
- **Garde requise** RUNTIME_ASSERTION — vérifier le RSS et l'absence de la matrice 512D avant le bloc 128D
- **Si violée** le bras 128D mesuré sur un cache chaud et une matrice déjà résidente paraîtrait meilleur pour une raison sans rapport avec la dimension. **Priorité 1.**

## 2.3 Génération synthétique
- **Clause** `B.synthetic_data_contract` — `root_seed: 20260908`, `PCG64_NORMAL_FLOAT32`, normalisation L2, `nan_inf_subnormal_guard`
- **Garantit** reproductibilité et absence de valeurs pathologiques qui fausseraient le débit FPU
- **Garde actuelle** NONE
- **Garde requise** RUNTIME_ASSERTION — échec sur NaN/Inf, comptage des subnormaux
- **Marge réelle** RMS de composante 0,0442 à 512D et 0,0884 à 128D, soit ~36 ordres de grandeur au-dessus du plus petit normal FP32. Le garde est une ceinture, pas la protection porteuse.
- **Si violée** une graine différente casse la reproductibilité sans que rien ne le signale

## 2.4 Génération de charge
- **Clause** `B.load_generation` — générateur **hors appareil**, arrivée déterministe en boucle ouverte, grille 0,25 / 0,5 / 1 / 2 / 4 / 8 QPS, burst 16 QPS sur 30 s avec 600 s d'observation de résorption
- **Garantit** que la charge offerte soit indépendante de la réponse du système, condition nécessaire pour observer la file d'attente
- **Garde actuelle** NONE
- **Garde requise** RUNTIME_ASSERTION — enregistrer l'hôte du générateur et le QPS offert réel
- **Si violée** un générateur sur l'appareil injecterait son propre CPU et sa propre consommation dans la mesure, attribués à la recherche ; une boucle fermée masquerait la saturation. **Priorité 1.**

## 2.5 Statistiques de mesure
- **Clause** `B.measurement_statistics` — 5 redémarrages indépendants, 60 s d'échauffement **exclus**, fenêtre 600 s, 5 répétitions de burst, ordre des bras contrebalancé, rétention des échantillons bruts, `no_silent_failed_run_exclusion`
- **Garantit** répétabilité, dispersion, absence de biais de dérive et de sélection
- **Garde actuelle** NONE
- **Garde requise** RUNTIME_ASSERTION
- **Si violée** échauffement non exclu → coût de cache froid attribué à la dimension. Ordre non contrebalancé → dérive thermique attribuée au second bras. Exclusion silencieuse d'un run raté → biais de survie. **Priorité 1.**

## 2.6 Support des percentiles
- **Clause** `B.measurement_statistics.percentile_support_rules` — p95 ≥ 200, p99 ≥ 1000 échantillons **complétés** par redémarrage
- **Garantit** qu'un percentile publié repose sur assez d'observations
- **Garde actuelle** NONE
- **Garde requise** RUNTIME_ASSERTION
- **Attendus calculables dès maintenant** 600 s × grille → 150 / 300 / 600 / 1200 / 2400 / 4800. Donc p95 supprimé par conception à 0,25 QPS ; p99 à 0,25, 0,5 et 1,0.
- **Si violée** un p99 sur 150 points passerait pour une mesure. Et une cellule vide est ambiguë : suppression par conception, ou bras saturé n'ayant pas complété assez de requêtes ? Deux sens opposés.
- **Écart ouvert** → décision **D5**

## 2.7 Régime de saturation — *B2*
- **Clause** `B.saturation_characterization` + `C.B2_saturation_and_censoring_pairwise_interpretation`
- **Garantit** qu'un ratio 512D/128D ne soit publié que si les deux bras sont dans le même régime non censuré
- **Garde actuelle** CONTRACT_TESTED côté `C`, NONE côté `B`
- **Garde requise** STATIC_PLUS_RUNTIME
- **Si violée** à QPS offert égal, le bras 512D — qui diffuse quatre fois plus d'octets — peut saturer quand 128D ne sature pas. Le delta comparerait de la file d'attente à du temps de service, présenté comme un effet de dimension.
- **Écart ouvert** les cinq étiquettes sont gelées, **la règle qui affecte une cellule à une étiquette ne l'est pas** → décision **D1**

## 2.8 Régime thermique
- **Clause à créer.** `B` enregistre `cpu_frequency_and_throttling_if_observable` et `temperature_if_observable`, et contrebalance l'ordre des bras contre la dérive. **Aucune règle d'appariement.**
- **Garantit** ce qu'aucune clause ne garantit aujourd'hui : qu'un ratio n'enjambe pas une frontière de throttling
- **Garde actuelle** NONE
- **Garde requise** STATIC_PLUS_RUNTIME, classifieur gelé avant matérialisation
- **Si violée** le throttling est une fonction en marche d'escalier. À G2 le bras 512D fait quatre fois plus de trafic mémoire et chauffera davantage. S'il franchit le seuil et que 128D ne le franchit pas, le ratio confond « quatre fois plus de travail » et « à une fréquence plus basse ». Sur un device edge à refroidissement passif — le cas de déploiement réaliste — c'est probable, pas exotique.
- **Analogue structurel exact de 2.7.** Même construction requise → décision **D9**
- **Note** le `if_observable` sur les compteurs de throttling pose le même problème que le `when_observable` de B1c : il faut un repli si la puce n'expose rien — température seule, ou dérive de latence intra-fenêtre.

## 2.9 Dispatch du backend — *B3*
- **Clause** `C.B3_backend_dispatch_observability`
- **Garantit** qu'un écart inattendu soit diagnosticable comme dimensionnel ou comme artefact de micro-noyau
- **Garde actuelle** CONTRACT_TESTED
- **Garde requise** RUNTIME_ASSERTION — enregistrement, pas égalité forcée
- **Si violée** rien de faux n'est conclu, mais un résultat surprenant devient ininterprétable
- **État** fermé. La partition entre champs déterminés par l'appelant — forme d'appel, toujours exigible — et champs exposés par le backend — échappatoire légitime — est correcte.

---

# Partie 3 — Énergie et autonomie

## 3.1 Plan de mesure
- **Clause** `B.energy_measurement` — `EXTERNAL_DEVICE_INPUT_OR_WALL` canonique, ≥ 10 Hz, télémétrie interne `SUPPORTING_DIAGNOSTIC_ONLY`, ligne de base au repos 300 s appariée à chaque bloc
- **Garantit** une affirmation énergétique au niveau de l'appareil, DRAM et pertes de carte incluses
- **Garde actuelle** NONE
- **Garde requise** RUNTIME_ASSERTION — vérifier le taux d'échantillonnage **atteint**, pas le taux nominal du wattmètre
- **Si violée** les compteurs internes excluent la DRAM sur beaucoup de pièces, or c'est exactement là que se voit l'écart 2,92 Gio contre 0,73 Gio. Une mesure par télémétrie biaiserait la comparaison **en faveur du bras évalué**. Sous 10 Hz, les transitoires de burst sont sous-estimés. **Priorité 1.**

## 3.2 Conventions de J/identification
- **Clause** `B.energy_measurement` — `canonical_joules_per_identification` (total, ligne de base incluse) et `diagnostic_incremental_...` (diagnostic seul, **négatifs non écrêtés**)
- **Garantit** deux nombres non confondables, et l'honnêteté du signal incrémental près du plancher de bruit
- **Garde actuelle** NONE
- **Garde requise** STATIC_PLUS_RUNTIME
- **Si violée** écrêter les négatifs à zéro transforme un bruit symétrique en biais positif. Et le total est une fonction forte du QPS : un chiffre sans son point de charge n'a pas de sens.

## 3.3 Modèle de batterie
- **Clause** `B.battery_model` — `autonomy_h = usable_Wh / total_average_power_W` sous profil nommé. Règle : toute autonomie nomme son profil de charge, et **l'énergie incrémentale compute-only ne doit pas servir à l'autonomie**.
- **Garantit** qu'une autonomie ne soit pas calculée sur le chiffre le plus flatteur
- **Garde actuelle** NONE
- **Garde requise** STATIC_CONTRACT_TEST + HUMAN_CONTROL
- **Si violée** l'autonomie serait surestimée du rapport entre puissance totale et puissance incrémentale — l'erreur la plus facile à commettre et la plus visible dans un dossier de décision
- **Écart ouvert** `duty_cycle_definition` est une entrée vide. Aucun profil n'est déclaré nulle part → décision **D8**

---

# Partie 4 — Faisabilité par palier matériel

## 4.1 Déclaration prospective de l'échelle de paliers
- **Clause à créer.** `B.infeasible_arm_rule` autorise déjà la reprise sur un palier supérieur *« if a larger tier was prospectively declared »*. Aucune échelle n'est déclarée.
- **Garantit** que la revendication économique — 128D évite le SKU supérieur — repose sur une comparaison construite avant d'en connaître l'issue
- **Garde requise** STATIC_CONTRACT_TEST, gel PRE_PLATFORM_MATERIALIZATION
- **Si violée** le second palier serait choisi après avoir vu le premier échouer. « 128D tient à 4 Go, 512D exige 8 Go » sur une échelle sélectionnée pour produire ce résultat : l'argument le plus fort du dossier, et le plus facile à démonter en revue externe.
- → décision **D6**

## 4.2 RAM requise totale, pas charge utile
- **Clause à créer.** La faisabilité se prononce sur `galerie + processus + runtime + OS + buffers + autres services + marge`, pas sur les octets de galerie. `B` mesure déjà RSS avant/après et le pic de working set ; il ne définit pas la marge.
- **Garantit** qu'un « ça tient » corresponde à un déploiement réel et non à un ajustement au dernier octet
- **Garde requise** RUNTIME_ASSERTION, fraction de marge gelée avant matérialisation
- **Si violée** on déclarerait 512D faisable sur un palier où il tient avec 2 % de marge, c'est-à-dire qu'il ne tient pas. Et une marge fixée après avoir vu les RSS sera fixée à ce qui fait passer la conclusion voulue.
- → décision **D7**

## 4.3 Cascade matérielle non inférée
- **Clause à créer.** Aucune conséquence en aval d'un changement de palier — puissance, batterie, thermique, masse, coût — ne s'infère du seul écart de RAM. Chaque terme est mesuré ou marqué `ASSUMED_NOT_MEASURED`.
- **Garantit** que le TCO ne soit pas un empilement d'hypothèses présenté comme un résultat
- **Garde requise** HUMAN_CONTROL + STATIC
- **Si violée** la cascade « moins de RAM → palier inférieur → moins de puissance → plus d'autonomie » se lit comme démontrée alors qu'un seul maillon l'a été

---

# Partie 5 — Conséquence opérationnelle

## 5.1 Séparation des familles métriques
- **Clause à créer.** 1:1 utilise FMR/FNMR ; 1:N utilise FPIR/FNIR. Un FMR 1:1 ne peut en aucun cas être multiplié par la taille de galerie ou le nombre de gabarits pour produire un risque opérationnel 1:N.
- **Garantit** que les deux branches du scénario soient chiffrées avec la bonne grandeur
- **Garde requise** STATIC_CONTRACT_TEST (interdiction de la formule) + HUMAN_CONTROL
- **Si violée** c'est l'erreur classique. Elle produit un nombre d'alertes fausses qui paraît rigoureux, qui est faux d'un facteur inconnu, et qui portera la décision d'acceptabilité.

## 5.2 Structure de corrélation déclarée, jamais supposée
- **Clause à créer.** Pour tout scénario multi-passage ou multi-device, l'indépendance est une hypothèse **déclarée et justifiée**, ou un modèle de corrélation est utilisé. Tout chiffre opérationnel est rapporté comme une **bande** entre indépendance et corrélation forte, jamais comme un point.
- **Garantit** que la difficulté latente par personne et l'effet device ne soient pas dissous par une hypothèse de commodité
- **Garde requise** HUMAN_CONTROL + STATIC — la bande est obligatoire
- **Si violée** rater une personne sur *m* observations vaut `p^m` sous indépendance, environ `p` sous corrélation forte. Pour `p = 0,1` et `m = 3` : 0,1 % contre 10 %. Deux ordres de grandeur, et la conclusion bascule.
- **C'est l'erreur de Study 0 remontée d'un niveau.** Là, des paires rééchantillonnées comme indépendantes alors que les identités revenaient. Ici, des observations traitées comme indépendantes alors que c'est la même personne difficile. Même fait statistique, même conséquence : intervalles trop étroits, confiance excessive.

## 5.3 Ancrage de la baseline
- **Clause à créer.** Toute valeur de référence nomme sa source, son jeu de données et son operating point. Aucune baseline n'est transportée d'un operating point à un autre, ni d'une modalité à une autre.
- **Garantit** qu'on ne fasse pas dire à une référence ce qu'elle ne dit pas
- **Garde requise** STATIC + HUMAN_CONTROL
- **Si violée** LFW ne peut pas soutenir un FMR de 10⁻⁶. Le plafond ne vient pas du nombre de paires — l'appariement exhaustif en produit ~10⁸ — mais des **5 749 identités** : les paires se recouvrent et l'information effective est bornée par le nombre de sujets. C'est encore le même fait statistique que 5.2. Une marge dérivée d'un chiffre LFW à 10⁻⁶ serait dérivée de bruit ; une tolérance empreinte transportée vers le facial serait une justification de convenance.

---

# Partie 6 — Marge de non-infériorité

## 6.1 Immuabilité de δ_NI sous l'identité courante
- **Clause à créer.** `δ_NI = 0,03` est documenté comme tolérance de recherche gelée, non dérivée d'un organisme externe. Elle ne peut pas être remplacée à l'intérieur de Study 1B. Toute marge issue d'un travail de justification crée une **nouvelle identité prospective de protocole**.
- **Garantit** qu'un manque de puissance ne se résolve pas par un élargissement de marge
- **Garde requise** STATIC_CONTRACT_TEST
- **Si violée** un `NOT_DEMONSTRATED` deviendrait un `DEMONSTRATED` par redéfinition. La forme la plus grave de post-hoc du programme, parce qu'invisible dans les résultats : seul l'historique du contrat la révèle.

## 6.2 Élicitation experte aveugle
- **Clause à créer.** Grille Δ, paramètres de scénario et seuil d'acceptabilité construits et gelés **avant** toute ouverture de SCREEN. L'expert ne voit pas où tombent les valeurs réelles.
- **Garantit** que l'élicitation soit une élicitation et pas une ratification
- **Garde requise** HUMAN_CONTROL, gel PRE_SCREEN_OPENING
- **Si violée** connaissant le Δ réel, tout ce qui est discrétionnaire dans l'enveloppe — scénarios, N, hypothèse de corrélation, operating point — se forme autour de la réponse. L'expert croira décider librement sur une grille déjà cadrée, et rien dans le livrable ne montrera la différence.
- → **Partie 8**

## 6.3 Gate d'ouverture de SCREEN
- **Clause à créer.** SCREEN ne peut pas être ouvert avant que la spec de gardes soit gelée et revue, la plateforme matérialisée et liée, et l'enveloppe + seuils de 6.2 gelés.
- **Garantit** le respect littéral de `B.interpretation_rules` n° 9 : *« No protected Study 1B outcome may be opened to select or tune an engineering configuration. »*
- **Garde requise** HUMAN_CONTROL, inscrit comme gate d'exécution au même titre que les deux existants
- **Si violée** palier matériel, backend, nombre de threads et wattmètre restent à choisir. Choisis après SCREEN, ils le sont par des gens qui connaissent les deltas biométriques — et si 128D tient bien, l'incitation est de choisir le palier où il paraît le plus avantageux. C'est la contamination que la règle 9 nomme, dans la direction qu'elle nomme.

---

# Partie 7 — Les quatorze décisions pré-matérialisation

Toutes se tranchent sans regarder aucune donnée. Chacune propose un défaut
argumenté : acceptez-le ou remplacez-le, mais gelez la valeur avant que
quiconque voie la machine.

## D1 — Règle d'affectation de régime de saturation *(ferme 2.7)*

La plus lourde de conséquence : elle commande si la comparaison principale peut
s'énoncer en chiffre.

Défaut — primaire sur le rapport débit complété / débit offert, sur la fenêtre de 600 s :

| condition | étiquette |
|---|---|
| ratio ≥ 0,98 | `UNSATURATED` |
| 0,90 ≤ ratio < 0,98 | `SATURATION_TRANSITION` |
| ratio < 0,90 | `SATURATED` |
| file non résorbée en fin de fenêtre | `RIGHT_CENSORED` |
| primaire et départage en désaccord | `INDETERMINATE` |

Départage : pente de la profondeur de file. Pente statistiquement nulle →
cohérent avec `UNSATURATED` ; croissance monotone → cohérent avec `SATURATED`.

Justification des seuils : en arrivée déterministe en boucle ouverte sur 600 s,
un déficit de 2 % reste dans la gigue d'ordonnancement ; 10 % ne peut pas s'expliquer ainsi.

`INDETERMINATE` compte comme régimes différents. Aucun ratio apparié. Échec fermé.

## D2 — Ratio de bande passante dérivé obligatoire *(ferme 1.4, B1c)*

```
derived_stream_rate_GB_s = gallery_payload_bytes × completed_QPS / 1e9
bandwidth_utilization    = derived_stream_rate_GB_s / measured_achievable_bandwidth_GB_s
```

Obligatoire, deux bras, chaque point de charge, sans condition d'observabilité.
Les compteurs restent optionnels et corroborants.

À inscrire dans le contrat parce que c'est utile et non gênant : le numérateur
suppose que chaque requête balaie toute la galerie depuis la RAM. Si une partie
réside en cache, le trafic DRAM réel est plus faible. Le chiffre dérivé est donc
une **borne supérieure** du trafic mémoire.

Conséquence : **une utilisation supérieure à 1 n'est pas une erreur, c'est une
preuve de résidence cache.** À G0, où toute la question est de savoir si 128D
tient en LLC, le diagnostic tombe gratuitement du même calcul. Inscrivez
l'interprétation maintenant, sinon quelqu'un traitera un ratio de 1,4 comme une
anomalie de mesure.

## D3 — LLC effectif *(ferme 1.4, B1b)*

`llc_capacity_bytes_effective_for_benchmark_thread_set`, dérivé avant de
connaître la puce : somme des capacités de tranche LLC de tous les clusters
contenant au moins un cœur du jeu d'affinité — pas un prorata par cœur, un cache
n'étant pas partitionné par cœur. Assorti d'une déclaration qu'aucun autre
processus significatif n'est co-résident.

`l3_or_llc_capacity_bytes_total` reste enregistré, mais le ratio publié utilise
le chiffre effectif.

## D4 — Position de la caractérisation de bande passante et palier thermique *(ferme A2)*

Une seule fois, en début de session, avant tout bloc mesuré — les corrections
exigent que la valeur soit enregistrée avant la phase porteuse de résultats.
Suivie d'au moins 300 s de repos, la même constante que la ligne de base
énergétique déjà au contrat. Température enregistrée à l'ouverture du premier
bloc mesuré. **Jamais rejouée entre deux blocs mesurés.**

## D5 — Comptes attendus et réalisés *(ferme 2.6, L3b)*

Par cellule : `expected_completed_samples = offered_QPS × 600` et
`actual_completed_samples`. Puis un drapeau :

- `SUPPRESSED_BY_DESIGN` — l'attendu est déjà sous le seuil de support
- `SUPPRESSED_BY_SHORTFALL` — l'attendu suffit, le réalisé non

Le second est un résultat de saturation, pas une lacune. Sans ce vocabulaire les
deux se lisent identiquement : une cellule vide.

## D6 — Échelle de paliers matériels *(ferme 4.1 — valeurs à vous)*

Au moins deux paliers, déclarés maintenant, avec l'ordre d'essai. Découvrir
qu'aucun ne convient crée une nouvelle identité prospective ; cela n'autorise pas
à ajouter un palier en cours de route.

Critère : placez-les de part et d'autre de la ligne de faisabilité plausible pour
512D à G2. La charge utile seule vaut 3,13 Go ; avec OS, runtime, buffers et
marge, un 4 Go est très probablement infaisable et un 8 Go probablement faisable.
C'est l'écart que la revendication économique doit démontrer, donc les deux
paliers doivent l'encadrer.

**Couplage palier / bande passante — v0.3.** Sur le Jetson Orin Nano, la version
4 Go utilise un bus LPDDR5 de 64 bits à 34 Go/s, la version 8 Go un bus de
128 bits à 68 Go/s. Descendre au SKU inférieur ne retire pas seulement de la RAM :
**il divise la bande passante par deux**. Or la recherche est limitée par la bande
passante. L'argument « 128D permet le palier 4 Go » doit donc être évalué avec la
bande passante de ce palier-là, pas avec celle du palier supérieur. Chaque palier
déclaré porte sa bande passante documentée, et la comparaison se fait palier par
palier.

## D7 — Marge de sécurité RAM *(ferme 4.2 — jugement d'ingénierie)*

Défaut : la plus grande des deux — 20 % de la RAM totale libre au pic, ou 512 Mo
libres au pic. Mesuré contre le **pic** de working set, pas contre le RSS en régime.

Pourquoi les deux : un pourcentage seul est trop permissif sur un 4 Go — 800 Mo,
à peine l'OS et les services ; un absolu seul est trop permissif sur un 16 Go.

## D8 — Profils de cycle de service *(ferme 3.3 — valeurs à vous)*

`duty_cycle_definition` est une entrée vide et aucun profil n'est déclaré.
L'autonomie à 0,25 QPS et à 8 QPS diffère bien plus que tout écart 512D/128D.

Déclarez maintenant deux ou trois profils nommés avec leur composition horaire —
pointe de flux avant match, régime de croisière, veille. C'est une décision de
scénario : vous savez déjà à quoi ressemble une journée de stade. Choisi après
coup, le profil sera choisi pour que la conclusion tombe juste.

## D9 — Classifieur de régime thermique *(ferme 2.8)*

Même construction que D1 : trois issues au minimum, échec fermé, interdiction de
réduire à un ratio une paire qui traverse la frontière de throttling.

Décider aussi le repli si la puce n'expose pas de compteurs : température seule,
ou dérive de latence intra-fenêtre. Le `if_observable` du contrat pose ici le
même problème que le `when_observable` de B1c.

À traiter en priorité avec D1 : c'est un mécanisme en marche d'escalier, sur le
matériel que vous allez précisément choisir, et personne ne l'avait vu en sept
cycles de revue.

## D10 — Représentativité thermique du banc *(ferme 2.8 et 3.1)*

`L` enregistre `cooling_configuration` et `ambient_temperature_C`, mais n'exige pas
qu'ils correspondent au déploiement. Mesurer sur banc ventilé et déployer en
boîtier fanless donne un résultat qui ne se transfère pas — et qui se trompe
**dans le sens flatteur**.

Base vérifiée : la Fondation Raspberry Pi indique que ses cartes réduisent la
fréquence à partir de 80 °C, davantage à 85 °C, et que sans refroidissement un
Pi 5 sous charge soutenue se stabilise juste au-dessus de 85 °C en throttling
permanent — **mesuré à l'air libre sur un banc de labo**. Un boîtier étanche au
soleil est pire.

Défaut proposé : déclarer par classe de déploiement (D11) la configuration
thermique — type de boîtier, refroidissement passif ou actif, plage d'ambiant — et
exiger que Phase A mesure au moins dans la configuration déclarée la plus
défavorable. À défaut, le résultat est étiqueté `THERMAL_BEST_CASE_NOT_TRANSFERABLE`.

**Avantage candidat de 128D, invisible sur banc ventilé.** À QPS égal, le bras
128D fait quatre fois moins de trafic mémoire, donc dissipe moins. Il peut rester
sous le seuil de throttling là où 512D le franchit. Ce serait un gain opérationnel
indépendant de la RAM. Il n'apparaît qu'en conditions de déploiement : ventilés,
les deux bras restent froids. D9 cesse alors d'être seulement un garde contre un
confondant — le throttling devient le régime d'exploitation, et la question
devient : quel bras throttle en premier, et de combien.

## D11 — Classes de déploiement et source d'énergie *(valeurs à vous)*

Décision de scénario, pas de données, et c'est elle qui décide quelle contrainte
mord. « Dans et autour des stades » suggère au moins deux classes.

| classe | alimentation | plafond | contrainte dominante |
|---|---|---|---|
| portique fixe | PoE ou secteur | PoE 802.3af : 12,95 W au PD · 802.3at : 25,5 W au PD | chaleur, puis plafond PoE |
| point mobile ou temporaire | batterie | capacité × cycle de service (D8) | batterie et chaleur |

Le plafond PoE s'applique à **l'appareil entier** — calcul, caméras,
illumination, radio. Voir partie 10.

Pour chaque classe déclarer : alimentation, plafond, plage d'ambiant, boîtier,
et si l'appareil peut dormir entre deux passages.

**Couplage batterie / boîtier — v0.4.** La batterie partage le boîtier avec le
SoC. Selon Battery University, une cellule Li-ion se charge entre 0 °C et 45 °C
et se décharge entre −20 °C et 60 °C ; la charge sous le point de congélation
n'est pas permise. Le plafond haut compte autant que le bas : dans un boîtier
fermé au soleil, chauffé par le SoC, la cellule peut sortir de sa fenêtre de
charge **par le haut**. Un point mobile en été peut alors fonctionner sans pouvoir
se recharger. Piège de lecture de fiche : la plage « operating temperature » d'une
cellule reflète souvent la décharge ; la plage de charge est plus étroite.

## D12 — Politique de batching et scénario de charge *(hypothèse oubliée)*

**Constat.** `phase_a_search_semantics` fixe l'algorithme, le top-1, l'absence de
seuil et d'index. **Il ne fixe pas la politique de batching.** Le mot n'apparaît
pas dans le benchmark v0.3.

**Pourquoi c'est dimensionnant.** Par le modèle Roofline, la performance
atteignable est le minimum entre la crête de calcul et le produit bande passante ×
intensité opérationnelle. Un scan exact non groupé fait 2d opérations pour 4d
octets lus : **intensité 0,5 FLOP/octet, quelle que soit la dimension**. C'est
pourquoi les deux bras sont profondément limités par la mémoire, et pourquoi le
modèle prédit exactement 4×. Grouper B requêtes lit chaque vecteur une fois pour
B usages : l'intensité devient **0,5 × B**. Jusqu'au point de crête, le débit
croît d'environ B fois — pour les deux bras.

Donc une variable non gelée peut déplacer tous les points de saturation d'un ordre
de grandeur, et avec eux toutes les cellules de D1. Or à un portique en rafale,
les requêtes s'accumulent : un serveur réel les grouperait.

**Défaut proposé** — reprendre la taxonomie de MLPerf Inference, qui sépare
explicitement les cas au lieu de laisser le batching libre : un scénario **Server**,
requête par requête, arrivées aléatoires, contrainte de latence au p99 ; et un
scénario **Offline**, toutes les requêtes disponibles, débit maximal. Phase A
déclare lequel elle mesure, ou les deux, et **la taille de lot est gelée par
scénario**.

## D13 — Processus d'arrivée *(hypothèse oubliée)*

**Constat.** Le contrat prévoit des arrivées **déterministes** en boucle ouverte.
MLPerf, dans son scénario Server, utilise des arrivées **Poisson**.

**Pourquoi c'est dimensionnant.** C'est un résultat classique de théorie des
files. Avec arrivées et service déterministes, il n'y a aucune attente tant que
la charge reste sous la capacité. Avec arrivées Poisson et service déterministe
(M/D/1), l'attente moyenne vaut ρ / (2μ(1 − ρ)) : une demi-durée de service à
ρ = 0,5, deux à ρ = 0,8, quatre et demie à ρ = 0,9. **L'écart explose précisément
près de la saturation**, c'est-à-dire là où D1 et B2 travaillent. Des arrivées de
stade sont au moins aussi irrégulières que Poisson, souvent plus.

Des arrivées déterministes rendent le banc reproductible, mais **optimiste sur la
latence de queue**. Défaut proposé : ajouter une variante Poisson à graine gelée,
ou déclarer explicitement que les latences de queue publiées sont une borne basse.

## D14 — Requêtes par passage et caméras par appareil *(hypothèse oubliée, valeurs à vous)*

**Constat.** La grille est en QPS. Le scénario est en passages. **La conversion
n'est écrite nulle part** — zéro occurrence de « passage » ou de « caméra » dans
le benchmark.

**Pourquoi c'est dimensionnant.** Une personne qui franchit un portique produit
plusieurs images. Chercher chaque visage détecté ou seulement la meilleure image
change le QPS d'un facteur 5 à 10 pour le même flux humain. Et un SoC qui sert
plusieurs caméras le multiplie encore : la fiche NVIDIA de l'Orin Nano indique
jusqu'à 16 canaux virtuels caméra.

**Défaut proposé** : déclarer la politique de sélection d'images — meilleure image
par passage, ou toutes les détections — le nombre de caméras par appareil, et en
déduire explicitement la conversion passages/heure → QPS offert, qui alimente D8.

---

# Partie 8 — Protocole d'élicitation aveugle

## Le principe qui rend le reste presque superflu

**L'expert ne voit jamais un Δ. Il voit des conséquences.**

« +3 points de FNMR » est un objet statistique sur lequel un expert n'a pas
d'intuition calibrée et qui invite l'ancrage sur 0,03. « 22 500 passages
supplémentaires en revue manuelle sur 750 000 » est un objet opérationnel sur
lequel il en a une.

Traduire Δ → conséquence est le travail de l'enveloppe. Juger l'acceptabilité de
la conséquence est celui de l'expert. Séparés ainsi, l'aveuglement devient
**structurel** : l'expert ne peut pas reconnaître où tombent les valeurs réelles
parce qu'il ne voit pas l'échelle sur laquelle elles tombent.

## Séparation des rôles

| rôle | interdit |
|---|---|
| détenteur des résultats SCREEN | construire l'enveloppe, assister à l'élicitation |
| constructeur de l'enveloppe | avoir vu un résultat SCREEN |
| expert | voir des Δ, voir des noms de route |

Si une même personne tient deux de ces rôles, aucune procédure ne rétablit
l'aveuglement. À vérifier avant toute mécanique.

## Ordre de gel

```
paramètres opérationnels     N passages, densité devices, watchlist, operating point
    ↓
enveloppe Δ → conséquence    deux branches séparées
    ↓
grille de présentation       scellée, hachée, liée au commit
    ↓
séance d'élicitation         enregistrée, signée, horodatée
    ↓
scellement du seuil
    ↓
──────────── seulement ici ────────────
    ↓
ouverture de SCREEN
```

## Construction de la grille

**Deux branches élicitées séparément.** Contrôle 1:1 de type boarding et
watchlist 1:N ne sont pas la même décision et n'utilisent pas les mêmes
grandeurs. Les mélanger dans une séance invite l'erreur FMR × N de 5.1.

**La grille déborde le plausible des deux côtés.** Si elle va de 0 à +10 et que
chacun sait que les valeurs réelles tournent autour de +2, l'expert lit la
grille. Incluez des niveaux que personne n'attend et ne centrez rien sur 0,03.

**Ordre de présentation randomisé.** Une progression monotone invite à chercher
le premier chiffre inconfortable — heuristique de rupture, pas jugement
d'acceptabilité.

**Chaque cellule montre une bande, pas un point.** Intervalle entre indépendance
et corrélation forte pour le multi-passage et le multi-device. L'expert se
prononce sur la borne haute, ou sur les deux explicitement, jamais sur une valeur
ponctuelle qui aurait dissous la corrélation.

**Aucun nom de route.** Ni Siamese128, ni PCA128, ni random128. L'expert juge des
conséquences, pas des méthodes.

## Contrôle de cohérence

Deuxième passe, séance séparée, scénarios factices intercalés dont certains
reprennent des niveaux déjà jugés sous une autre présentation. Si le seuil énoncé
n'est pas reproductible, ce n'est pas une mesure. C'est une information en soi :
la question n'est pas décidable sous cette forme et doit être reformulée.

## Ce qui invalide l'élicitation

- Un participant ayant vu un résultat SCREEN, à quelque titre que ce soit
- Une modification de la grille après la première séance
- Une reprise après descellement partiel
- Un seuil énoncé sur un Δ plutôt que sur une conséquence

Remède dans chaque cas : nouvelle identité prospective d'élicitation, pas rattrapage.

## Produit de la séance

Pas « la marge vaut X ». Un tableau `conséquence → acceptable / limite /
inacceptable` par branche, avec la bande de corrélation. La conversion en marge
se lit ensuite mécaniquement, à l'envers — et donnera **une marge par branche,
pas une marge unique**. C'est probablement le résultat le plus honnête que ce
travail puisse produire, et il vaut mieux le dire avant la séance qu'après.

---

# Partie 9 — Schéma de `STUDY1B_PHASE_A_EXECUTION_GUARD_SPEC_V0_1.yaml`

```yaml
guard_id: PHASE_A_ZERO_SWAP
source_clause: ram_residency_contract
source_artifact: STUDY1B_JUNGLE_CHAMPIONSHIP_ENGINEERING_BENCHMARK_V0_3_2026-09-08.yaml
guard_type: RUNTIME_ASSERTION
freeze_phase: PRE_PLATFORM_MATERIALIZATION

false_conclusion_if_violated: >-
  512D serait déclaré RAM-faisable sur ce palier alors que l'OS a compensé
  par le disque. Validerait un déploiement matériellement infaisable.
priority: CRITICAL

logic:
  assertion: swap_delta_pages == 0
  evaluated: per_measurement_window
  failure_mode: FAIL_CLOSED

evidence_retained:
  - swap_pages_before
  - swap_pages_after
  - observation_timestamp

materialization:
  observation_method: null      # rempli après matérialisation
  source_reference: null
```

**`false_conclusion_if_violated` + `priority`** — permet de ne pas automatiser
seize choses à la fois. Le premier lot se lit dans les `CRITICAL`.

**`evidence_retained`** — un garde qui échoue fermé sans laisser de trace n'est
pas auditable. Chaque garde écrit sa **valeur observée**, pas seulement son
verdict. Sans cela un reviewer ultérieur ne peut pas distinguer « vérifié et
bon » de « n'a pas tourné ».

**`logic` / `materialization`** — la séparation porteuse. La logique se gèle
maintenant ; la valeur physique vient avec la machine. Dans l'autre sens on écrit
des assertions qui décrivent ce que la plateforme fait au lieu de contraindre ce
qu'elle doit faire.

## Premier lot d'implémentation

Par conséquence, pas par facilité : **1.1** swap · **2.2** isolement des bras ·
**2.1** sémantique exact-dense · **2.5** échauffement et contrebalancement ·
**2.4** générateur hors appareil et boucle ouverte · **3.1** plan de mesure
énergie · puis **2.7** et **2.8** classifieurs de régime.

---

# Partie 10 — L'appareil complet

## Principe

Phase A mesure la recherche **seule** : `L` exige qu'aucun autre processus
significatif ne soit co-résident. C'est la bonne première mesure — elle isole la
demande de ressources de la recherche. Mais la faisabilité ne se décide pas sur le
budget total de l'appareil. **Elle se décide sur le budget résiduel, après les
autres composants.**

Quatre budgets sont partagés : **puissance, chaleur dans le boîtier, bande
passante mémoire, RAM**. Phase A fournit une ligne de chaque. Les autres lignes
viennent des composants ci-dessous.

La recherche n'est peut-être pas le plus gros consommateur. Une illumination IR
peut dépasser le SoC. Sur un portique en 802.3af, 12,95 W doivent couvrir
**tout** l'appareil. Si caméras, illumination et détection en consomment déjà
l'essentiel, les quelques watts d'écart entre recherche 512D et 128D sont peut-être
précisément ce qui décide de la faisabilité — ou n'y changent rien. On ne le saura
qu'avec les autres lignes du budget.

## Composants

| composant | puissance | chaleur | bande passante mémoire | RAM | point de vigilance |
|---|---|---|---|---|---|
| SoC — recherche | Phase A | Phase A | Phase A | Phase A | objet mesuré |
| caméra visible | ● | ● | ● flux ISP | ● tampons | résolution × cadence |
| caméra NIR | ● | ● | ● | ● | utile aussi à la détection de fraude (PAD) |
| illumination IR 850 / 940 nm | **●●** | **●●** | — | — | peut dépasser le SoC ; sécurité oculaire |
| détection de mouvement PIR / radar | ○ | ○ | — | — | conditionne la veille |
| chaîne de capture : détection, alignement, encodage | ●● | ●● | **●●** | ●● | tourne en continu, rivalise avec la recherche |
| radio : WiFi sur alerte, LTE, Ethernet | ● en rafale | ● | — | ○ | conditionne la propagation de galerie |
| stockage : galerie au repos | ○ | ○ | — | — | chiffrement, temps de chargement |
| élément sécurisé, TPM, démarrage sécurisé | ○ | ○ | — | — | vol d'appareil = fuite de watchlist |
| alimentation : PD PoE ou batterie + BMS | pertes | ● | — | — | plafond dur (D11) |
| chauffage, en climat froid | **●●** | — | — | — | peut dominer l'hiver |
| boîtier IP / IK, fenêtre optique | — | détermine la dissipation | — | — | reflets IR dans la caméra |

● charge significative · ●● charge potentiellement dominante · ○ charge faible.
Toutes les valeurs sont `ASSUMED_NOT_MEASURED` tant qu'elles ne figurent pas dans
la partie 11 avec une source.

Sur le chauffage : un exemple documenté de caméras PTZ extérieures équipées de
chauffage et d'essuie-glace montre jusqu'à 32 W par caméra en conditions froides —
plus que le plafond 802.3af à lui seul.

## Quatre interactions où les composants changent la réponse 512D / 128D

Ce sont les points qui relient la BOM à l'étude. Dans chacun, un choix de
composant fait dépendre un coût opérationnel **de la taille de galerie**.

**1. Veille et galerie résidente.** Un appareil déclenché par détection de
mouvement dort entre deux passages. Au réveil, la galerie doit être en mémoire.
Deux voies, et toutes deux dépendent de la taille. Soit la RAM reste alimentée en
veille — son coût croît avec la capacité mémoire. Soit la galerie est rechargée
depuis le stockage — 3,13 Go contre 783 Mo, avec déchiffrement. Et le réveil n'est
utile que si le délai *réveil → prêt* est inférieur au temps qu'une personne met
à entrer dans le champ. C'est une latence qui dépend directement de la dimension,
et Phase A ne la mesure pas.

**2. Radio en rafale et propagation.** Une radio active seulement sur alerte
économise l'énergie, mais alors la mise à jour de la watchlist attend une fenêtre
radio. La durée de propagation devient le produit de la taille de galerie et du
cycle radio. Cela aggrave directement le point « propagation » de la partie 12.

**3. Galerie chiffrée au repos.** Des données biométriques sur un appareil en
espace public doivent être chiffrées au repos. Le déchiffrement au démarrage ou au
réveil coûte du temps et du calcul proportionnels à la taille, et la galerie en
clair occupe 3,13 Go contre 783 Mo de RAM.

**4. Bande passante partagée.** Le traitement du signal d'image et la détection
de visage consomment de la bande passante mémoire en continu. Or la recherche est
limitée par la bande passante. Le modèle au premier ordre doit donc utiliser la
bande passante **disponible**, pas la bande passante totale. À 17 Go/s sur un
Raspberry Pi 5, quelques Go/s pris par la détection déplacent sensiblement le
point de saturation.

## Points réglementaires — instruits en v0.4

Ce qui suit établit **quelles règles existent**. Leur application au programme
dépend de la juridiction, de l'opérateur et de la finalité : c'est une
qualification juridique qui relève d'un conseil, pas de ce document.

**Sécurité photobiologique de l'illumination IR.** L'IEC 62471:2006 fixe les
limites d'exposition, la méthode de mesure et la classification des risques pour
les sources optiques incohérentes, LED comprises et lasers exclus, entre 200 et
3000 nm. C'est une norme **horizontale** : elle attribue un groupe de risque,
mais les exigences de sécurité qui en découlent relèvent des normes de produit
verticales. La BOM doit donc porter le groupe de risque IEC 62471 de
l'illuminateur, et l'obligation qui en résulte dépend de la norme produit de
l'appareil.

**Batteries lithium-ion.** Instruit en D11 : fenêtre de charge 0–45 °C, pas de
charge sous 0 °C, et risque de sortie par le haut en boîtier chaud.

**Données biométriques — si le déploiement relève de l'UE.** Le RGPD, article
9(1), interdit par principe le traitement des données biométriques aux fins
d'identifier une personne de manière unique, sauf exceptions de l'article 9(2).

**IA en espace public — si le déploiement relève de l'UE, et c'est
potentiellement décisif.** L'AI Act interdit en principe l'identification
biométrique à distance en temps réel dans les espaces accessibles au public
à des fins répressives (article 5(1)(h)), sauf exceptions étroites. Les systèmes
d'identification biométrique non interdits sont classés à haut risque (annexe III).

Conséquence pour le programme : **les deux branches de l'enveloppe ne sont pas
seulement deux métriques, elles peuvent relever de deux régimes juridiques.** Un
contrôle d'accès de porteurs de billets et une watchlist opérée à des fins
répressives ne se qualifient pas pareil. Dans l'UE, la seconde peut être interdite
par défaut, quelle que soit la qualité de l'ingénierie. La juridiction et
l'opérateur de chaque branche sont des paramètres de scénario à déclarer **avant**
de dimensionner la branche correspondante.

---

# Partie 11 — Gabarit de BOM avec provenance

Même discipline que pour le contrat : chaque valeur porte sa source et sa nature.
La session qui a produit cette version en a montré la nécessité — une valeur de
cache tirée de l'apprentissage du modèle s'est révélée fausse et changeait une
conclusion.

## Natures

- **`DATASHEET_PRIMARY`** — fiche ou documentation du fabricant
- **`DATASHEET_SECONDARY`** — reprise par un tiers : presse technique, distributeur, wiki
- **`DERIVED`** — calculé à partir d'une valeur documentée ; la formule est donnée
- **`MEASURED`** — mesuré sur l'appareil, avec la méthode et la date
- **`ASSUMED_NOT_MEASURED`** — hypothèse ; interdite comme base d'une conclusion

Une conclusion ne peut reposer que sur les quatre premières. Une valeur
`DATASHEET_SECONDARY` qui porte une décision doit être remontée à sa source
primaire avant le gel.

**Ce qui n'est jamais une source — ajouté en v0.4.** En cherchant la fiche Intel
ARK du N100, le premier résultat était un **résumé généré par IA** d'une page ARK
archivée. Il attribuait au N100 le double et le triple canal mémoire,
l'Hyper-Threading à deux threads par cœur et la mémoire ECC — trois affirmations
que contredisent toutes les autres sources, qui décrivent un 4 cœurs / 4 threads à
canal unique. Un résumé IA d'une source primaire **n'hérite pas** de son autorité ;
ici il la contredisait. Il est exclu du tableau, au même titre que les réponses
d'un assistant — y compris celles qui ont produit ce document.

## Gabarit

| composant | paramètre | valeur | unité | nature | source |
|---|---|---|---|---|---|

## Valeurs déjà documentées

| composant | paramètre | valeur | nature | source |
|---|---|---|---|---|
| Raspberry Pi 5 — BCM2712 | CPU | 4 × Cortex-A76, 2,4 GHz | PRIMARY | documentation Raspberry Pi |
| | L2 | 512 Ko par cœur | PRIMARY | documentation Raspberry Pi |
| | L3 partagé | 2 Mo | PRIMARY | documentation Raspberry Pi |
| | bande passante mémoire | jusqu'à 17 Go/s, LPDDR4X 32 bits | PRIMARY | documentation Raspberry Pi |
| | seuils de throttling | 80 °C début, 85 °C renforcé | PRIMARY | blog Raspberry Pi, *Heating and cooling Raspberry Pi 5* |
| | comportement sans refroidissement | throttling permanent sous charge soutenue, à l'air libre | PRIMARY | idem |
| | puissance sous charge | ~12 W | SECONDARY | Notebookcheck, raspberry.tips |
| | dimensions carte | 85 × 56 mm | SECONDARY | CNX Software |
| Jetson Orin Nano | CPU | 6 × Cortex-A78AE, 1,5 GHz | SECONDARY | JetsonHacks, CNX Software |
| | L3 | 2 Mo par cluster, clusters de 4 et 2 cœurs | SECONDARY | RidgeRun |
| | bande passante mémoire, crête théorique | 34 Go/s (4 Go) · 68 Go/s (8 Go) | **PRIMARY** | NVIDIA, *Jetson Orin Nano Series Data Sheet*, DS-11105-001 |
| | fréquence mémoire max | 2133 MHz | **PRIMARY** | idem |
| | canaux virtuels caméra | jusqu'à 16 | **PRIMARY** | idem |
| | conception thermique | la solution thermique client doit maintenir le SoC sous sa température max | **PRIMARY** | NVIDIA, *Thermal Design Guide*, TDG-11127-001 |
| | modes de puissance | 5–10 W (4 Go), 7–15 W (8 Go) | SECONDARY | JetsonHacks, CNX Software |
| | module | 69,6 × 45 mm, SO-DIMM 260 broches | SECONDARY | JetsonHacks |
| Intel N100 | CPU | 4 cœurs | SECONDARY | Notebookcheck |
| | L3 | 6 Mo | SECONDARY | Notebookcheck, TechPowerUp |
| | température de jonction max | 105 °C | SECONDARY | Notebookcheck |
| | mémoire | canal unique, DDR5-4800 / DDR4-3200 | SECONDARY | Notebookcheck |
| | bande passante mémoire | 38,4 Go/s | **DERIVED** | 4800 MT/s × 8 octets, canal unique DDR5 ; théorique |
| | puissance de base | 6 W, compatible fanless | SECONDARY | Notebookcheck |
| PoE 802.3af | puissance garantie au PD | 12,95 W | SECONDARY | quatre sources concordantes ; norme IEEE 802.3 payante |
| PoE 802.3at | puissance garantie au PD | 25,5 W | SECONDARY | idem |
| Cellule Li-ion | plage de charge | 0 à 45 °C, pas de charge sous 0 °C | SECONDARY | Battery University, BU-410 ; à confirmer sur la fiche de la cellule retenue |
| | plage de décharge | −20 à 60 °C | SECONDARY | idem |
| Illumination IR | norme de sécurité photobiologique | IEC 62471:2006, 200–3000 nm, horizontale | CATALOGUE NORMATIF | SCC, SIS, iTeh ; norme payante |
| Mesure de bande passante | méthode de référence | STREAM, noyau Triad | SECONDARY | documentation STREAM, Microsoft Learn |

**Bilan de la remontée v0.4.** Jetson : bande passante, fréquence mémoire,
canaux caméra et conception thermique désormais **primaires** ; le détail du cache
L3 figure dans la même fiche DS-11105-001 et reste à y lire. N100 : fiche ARK **non
atteinte**, valeurs secondaires concordantes, et un résumé IA contradictoire écarté
(voir plus haut). PoE : norme primaire payante, quatre secondaires concordants.

**Reste à remonter avant le gel** : L3 du Jetson dans DS-11105-001 ; tout le N100
sur Intel ARK ; la fiche de la cellule Li-ion effectivement retenue.

**Note sur les bandes passantes** : toutes sont des valeurs théoriques de crête.
L'efficacité réelle en lecture continue est `ASSUMED_NOT_MEASURED` — c'est le
curseur du toy — et devient `MEASURED` par la caractérisation D4.

---

# Partie 12 — Hors périmètre Phase A, à nommer maintenant

Ces points ne sont pas des lacunes de Phase A. Ils doivent être nommés
maintenant pour ne pas surgir après la décision.

**Question produit prioritaire — quantification contre réduction de dimension.**
C'est la plus importante de cette partie, et elle ne se voit que depuis la
question produit.

| représentation | octets par vecteur |
|---|---|
| 512D en FP32 | 2 048 |
| 512D en FP16 | 1 024 |
| **512D en INT8** | **512** |
| **128D en FP32** | **512** |

**512D quantifié en INT8 occupe exactement la même mémoire que 128D en FP32.** Même
charge utile, même bande passante par requête, même palier matériel. Tout
l'argument RAM et palier en faveur de 128D peut donc être obtenu **sans réduire la
dimension**, par quantification seule.

Le benchmark a raison de séparer les deux : `engineering_axes_later_phases` place
la quantification en Phase C, comme intervention distincte, et c'est la bonne
construction pour isoler l'effet de la dimension. Mais la **décision produit** ne
porte pas sur « 512D contre 128D ». Elle porte sur « quelle représentation de 512
octets préserve le mieux la performance biométrique ». Si 512D-INT8 dégrade moins
que 128D-FP32 à mémoire égale, la réduction de dimension perd sa raison d'être
côté ingénierie.

Conséquence : l'étude biométrique doit comparer les routes **à octets égaux**, pas
seulement à dimension égale. Et le tableau conjoint de la décision doit porter la
colonne « octets par vecteur », pas seulement la colonne « dimension ».

**Propagation et mise à jour de galerie.** Zéro occurrence dans le contrat.
Pousser 3,13 Go contre 783 Mo vers N devices autour des stades, c'est de la bande
passante réseau, du temps, et surtout une **fenêtre pendant laquelle un device a
une watchlist périmée**. Quatre fois plus long à propager est une propriété de
sécurité, pas seulement d'ingénierie. C'est peut-être la différence la plus
décisive opérationnellement du dossier, et elle n'est mesurée nulle part.

**Temps de disponibilité après redémarrage.** Charger 3,13 Go depuis le stockage
flash prend un temps non nul. Sur un device susceptible de redémarrer, « le
device redevient opérationnel 40 s plus tard » est une conséquence réelle.

**L'autonomie mesurée est une autonomie de recherche seule.** `L` exige qu'aucun
autre processus significatif ne soit co-résident. Le device réel fait aussi
capture, détection, alignement, encodage, réseau, journalisation. L'autonomie
publiée surestime l'autonomie réelle d'un facteur inconnu. À déclarer comme
limitation explicite, pas à découvrir au déploiement.

**Gabarit contre identité.** Phase A fait un top-1 sur 1 530 000 gabarits. Une
watchlist veut le meilleur match par **identité** — trois gabarits par personne,
donc une agrégation. Le travail d'ingénierie est le même, donc Phase A reste
valide. Mais la branche conséquence opérationnelle ne peut pas consommer le top-1
brut : FPIR et FNIR se définissent par identité. À poser avant de construire
l'enveloppe, sinon vous compterez des alertes de gabarit pour des alertes de
personne.

---

# Partie 13 — Ordre de gel

```
1  Geler la logique des gardes            D1 à D14
2  Revue indépendante courte de la spec de gardes
3  Matérialiser la plateforme, lier les valeurs physiques
4  Geler l'enveloppe opérationnelle et les seuils experts    5.1 5.2 5.3 6.2
5  Exécuter Phase A
6  Ouvrir SCREEN                                             6.3
7  Croiser les trois branches — biométrique, ingénierie, opérationnelle
```

L'étape 4 peut se faire en parallèle de 3, jamais après 6.

Le seul réordonnancement que la discussion produit impose est l'échange de
position entre SCREEN et la matérialisation. Il ne coûte rien et il évite une
violation littérale de la règle 9.

## Contract tests à ajouter en parallèle

Quelques tests très simples qui **ouvrent enfin le benchmark v0.3** : recalculer
les octets de charge utile, vérifier les 5 redémarrages, 60/600 s, la grille QPS,
exact dense top-1, ≥ 10 Hz, les règles p95/p99. Ce ne sont pas des gardes
d'exécution. Leur seule fonction est d'empêcher que le contrat scientifique revu
change silencieusement.

---

# Partie 14 — Bibliothèque de référence

Ce n'est pas un moyen de compléter l'apprentissage d'un assistant : un modèle ne
s'entraîne pas pendant une conversation, et une erreur de son apprentissage reste
invisible tant qu'on ne la confronte pas à une source. C'est l'inverse : une
**autorité externe fixe**, contre laquelle toute affirmation — humaine ou générée —
doit pouvoir être vérifiée. La règle de la partie 11 s'applique : ce qui n'est
pas dans la bibliothèque avec sa source n'est pas acquis.

Chaque entrée ci-dessous a été vérifiée en v0.4 comme existante et correctement
citée. Leur pertinence est expliquée ; leur contenu intégral n'a pas été relu.

## Performance et mémoire — le cadre de tout le raisonnement de Phase A

- **Williams, Waterman, Patterson** — *Roofline: An Insightful Visual Performance
  Model for Multicore Architectures*. Communications of the ACM 52(4), avril 2009,
  p. 65–76. DOI 10.1145/1498765.1498785. Version libre : rapport technique
  UC Berkeley UCB/EECS-2008-134. **Le texte à lire en premier** : c'est le modèle
  sous-jacent au toy, à D2 et à D12.
- **Hennessy, Patterson** — *Computer Architecture: A Quantitative Approach*,
  6ᵉ édition, Morgan Kaufmann, 2017. La référence de fond sur la hiérarchie
  mémoire, la bande passante et les caches.
- **STREAM** — le standard de fait pour la bande passante mémoire soutenue ; le
  noyau Triad est la métrique de comparaison de référence. C'est la méthode à
  geler dans D4.

## Méthodologie de benchmark

- **MLPerf Inference, règles officielles** — MLCommons, dépôt
  `mlperf/inference_policies`, `inference_rules.adoc`. Quatre scénarios définis
  (Single stream, Server, Offline, Multistream), 600 s de durée, p99 pour Server.
  Ne couvre pas la recherche vectorielle, mais sa **taxonomie de scénarios** est
  exactement ce qui manque pour D12 et D13.

## Plateformes — sources primaires

- **Raspberry Pi** — documentation matérielle BCM2712 ; billet *Heating and
  cooling Raspberry Pi 5* pour le comportement thermique.
- **NVIDIA** — *Jetson Orin Nano Series Data Sheet* DS-11105-001 ; *Jetson Orin
  NX Series and Jetson Orin Nano Series Thermal Design Guide* TDG-11127-001.
- **Intel ARK** — à consulter directement pour le N100 ; non atteint en v0.4.

## Sécurité, énergie, réglementation

- **IEC 62471:2006** — sécurité photobiologique des lampes et appareils,
  illuminateurs IR compris. Payante.
- **Battery University, BU-410** — charge à haute et basse température. Source
  secondaire largement citée ; la fiche de la cellule retenue prime.
- **RGPD, article 9** et **AI Act, article 5** — si le déploiement relève de l'UE.

## À vérifier avant d'entrer dans la bibliothèque

- **ISO/IEC 19795** — série de normes d'évaluation des performances biométriques,
  évoquée plus tôt dans le programme pour cadrer la marge de non-infériorité. Non
  vérifiée dans cette version.

## Ce qu'une bibliothèque ne remplace pas

Les trois hypothèses oubliées de la v0.4 — batching, processus d'arrivée,
requêtes par passage — ne sont dans aucune fiche technique. Elles ont été
trouvées en confrontant le contrat à un cadre (Roofline, MLPerf, théorie des
files) et en posant une question simple : *qu'est-ce qui, dans ce contrat, n'est
fixé nulle part ?* Une bibliothèque vérifie ce qu'on affirme. Elle ne dit pas ce
qu'on a oublié d'affirmer. Ça reste le travail du reviewer.
