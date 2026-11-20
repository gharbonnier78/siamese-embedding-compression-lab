# Matrice d’essais environnementaux

**Plan proposé, aucun essai passé.** Références de méthodes : IEC 60068 (environnement), [IEC 60529](https://webstore.iec.ch/en/publication/2452) (ingress), IEC 62471 (photobiologie), [ISO/IEC 30107-1](https://www.iso.org/standard/83828.html) (cadre PAD). Fixer sévérités/durées et critères avant essai selon la mission, les dessins et limites constructeur. Vérifier d'abord sur cibles inertes/synthétiques, puis sujets consentants uniquement après autorisations spécifiques ; pas de listes réelles ni d'essai de rue, jeux protégés non utilisés. Étude 0 reste négative.

| Essai | Méthode et témoins | Preuve / critère de revue |
|---|---|---|
| Soleil direct, contre-jour, ombre rapide | angle/irradiance et lux mesurés ; référence scène reproductible | saturation RGB/NIR, récupération exposition, rendement capture et température ; seuils à fixer |
| Nuit et réflexions | cibles mobiles inertes et surfaces réfléchissantes ; lux, courant et durée NIR en parallèle | interverrouillage défaut, exposition approuvée avant sujets, énergie et rendement de capture |
| Pluie, film d'eau et ingress | pluie dirigée, lentilles sèches/mouillées, inspection avant/après, version complète fermée | continuité, absence de pénétration dommageable, taux d'occlusion/non-décision ; classe IP jamais déduite de cet essai exploratoire |
| Froid et transition humide | démarrage à froid, cycle humide-froid-réchauffement, décharge sous limites pack | réveil, Wh utiles, coupures BMS, récupération buée ; pas de recharge hors plage |
| Chaleur + soleil + rafale | enveloppe fermée, sollicitation radiative et charge soutenue | température jonction/coque/pack/optique, bridage et arrêt sûr ; marges aux limites confirmées |
| Humidité et condensation | cycler humidité et température, comparer à sec | qualité, temps de récupération, inspection eau et corrosion |
| Piétons en mouvement, dispositif fixe | maquette murale fixe, trépied seulement pour calibration ; passages groupés et occlusions, ~1 000/h sur fenêtres de 10 h × 5 j ; vibration structurelle testée séparément | flou, écarts RGB/NIR, doublons, pertes et p95/p99 soutenus, J/événement, fausses alertes par heure et charge opérateur |
| Hors réseau | débrancher Ethernet et désactiver radios pendant la mission complète ; PC absent | 100 % de continuité de la chaîne locale visée, alerte politique périmée et export ultérieur sans perte non signalée |
| Coupure et reprise PoE/DC | distinguer perte de données et perte de source ; essais au pic avec secours au plus faible état admissible ; contrôler retour et recharge | continuité pendant durée cible, zéro reset ou corruption dans cette fenêtre, arrêt sûr au-delà ; mesurer creux, inrush et température. Échange sous charge seulement si retenu et qualifié. |
| Mise à jour / panne / saturation | coupure en phases distinctes, paquet invalide, disque plein, tamper | signature refusée, retour intégral, journal intact ou pertes signalées, jamais de mode non sûr |

Comparer au banc témoin dans des blocs répétés. Journaliser versions, unités, référence et étalonnage, conditions et exclusions avant analyse. Rapporter W, Wh/j, J/événement, J/requête, courant crête, p50/p95/p99, bridage, températures, perte et backlog. Séparer échec acquisition/traitement, qualité, PAD, FMR/FNMR 1:1 et FPIR/FNIR 1:N ; donner dénominateurs, intervalles d'incertitude et résultats par condition. Les limites de performance restent à fixer avant essais, pas après observation.
