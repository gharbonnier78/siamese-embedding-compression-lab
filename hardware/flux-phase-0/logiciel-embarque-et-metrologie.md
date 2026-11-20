# Logiciel embarqué et métrologie

## Produit, hors ligne par conception

Mission fixe sur support calibré. Associer aux traces le profil du site, la version de calibration et la direction du flux. Vérifier le fonctionnement local sans accès réseau indépendamment de la disponibilité du PoE ; journaliser perte de données, perte de puissance, bascule, durée de secours et reprise comme événements distincts. Les métadonnées de galerie et la politique signée restent distinctes ; aucun candidat ne déclenche d'action sans revue humaine.

- MCU : machine d'états, watchdog et RTC, journal circulaire non volatil, réveil, contrôle de rails et inhibition NIR. Linux ne peut contourner les protections matérielles. Synchronisation des horloges au réveil ; compteur séquentiel et identifiant de session en cas de reset.
- Linux : capture et horodatage matériel → contrôle qualité → détection/alignement → modèle et prétraitement figés → embeddings → recherche exacte de référence ou index approximatif évalué sur les mêmes requêtes → moteur de politique local séparé. Sorties distinctes : candidat, inconnu, absence de décision ; inconnu ne déclenche pas une règle de liste. Pas de LLM sur le chemin critique. Aucun PAD supposé validé.
- Données : stockage chiffré, clé protégée matériellement si la plateforme le permet, droits minimaux, modèles/index et politiques signés et versionnés, journaux minimisés sans image par défaut. Mise à jour locale ou réseau autorisé, signatures, partitions A/B ou équivalent, retour à version connue après coupure et politique de fraîcheur hors ligne. Vérifier chaînage démarrage sécurisé/mise à jour/retour arrière sur le SKU cible. Pas de vraies listes ni de données identifiables dans Flux.
- Banc : scénarios déterministes et galeries synthétiques, enregistrement d'instruments, analyses d'incertitude et distributions, tableau de bord et registre de décision. L'absence du PC n'interrompt aucune fonction du produit.

## Faisabilité calcul

Candidat d'évaluation : [Radxa ROCK 5B](https://docs.radxa.com/en/rock5/rock5b), famille RK3588 ; révision/SKU/RAM exacts non sélectionnés. Alternative de référence : CPU Linux sans NPU pour comparaison identique. Porte de qualification : figer OS, modèle, précision, versions des pilotes, opérations non prises en charge et repli CPU ; mesurer latence de bout en bout, RAM crête, débit du stockage, J/requête et température avec deux caméras et tous les traitements concurrents. Double capture synchronisée et compatibilité des modules non démontrées. Vérifier démarrage sécurisé, eMMC/NVMe, endurance et espace pour versions A/B. Puissances non mesurées ; TOPS non utilisés comme prédiction.

| Galerie | 512D float32 | 128D float32 |
|---|---:|---:|
| 100 k | 204,8 Mo | 51,2 Mo |
| 500 k | 1 024 Mo | 256 Mo |
| 1 M | 2 048 Mo | 512 Mo |

Taille décimale des vecteurs seuls, N × D × 4 octets. Mesurer séparément copie en RAM, page cache, index, métadonnées, extraction et double version sur disque. Comparer rappel de l'index approximatif par rapport à la recherche exacte, taille et durée de reconstruction, et p50/p95/p99 sous rafales. Aucun de ces chiffres n'est une mesure matérielle.

## Contrat de télémétrie — cadence de départ, non figée

| Sonde | Lecteur et interface | Cadence / conservation |
|---|---|---|
| PIR, tamper, reset, Power Good | MCU GPIO IRQ permanent | chaque front ; RTC + monotone, journal durable |
| Entrée DC/PoE, rails et réserve protégée | MCU moniteur I²C/ADC et BMS constructeur | 1 Hz actif, 0,1 Hz veille en hypothèse + fronts défaut ; analyseur rapide indépendant pour creux |
| Thermique dissipateur/coque/ambiante/émetteur, humidité | MCU I²C/ADC ; protections NIR séparées | 1 Hz actif, 0,1 Hz veille comme point de départ ; points mappés sur logger externe |
| SoC/bridage, espace libre, communications | Linux pilotes, MCU pour signal d'état | 1 Hz en essais et événements ; local sans réseau |
| Caméras / impulsions NIR / IMU | compteur déclenchement, métadonnées capteurs, IMU SPI/I²C | par image/impulsion ; IMU 100 Hz initial, à adapter à vibration |
| Références DC / thermique / éclairage et pluie | banc | cadence d'après événement le plus court et incertitude ; marqueur commun et calibration indépendante |

Événement : identifiant trace/span, horodatages et décalage estimé MCU–Linux–banc, conditions, exposition/gain, version capteur/calibration/micrologiciel/modèle/galerie, compte des pertes et motif de non-décision. Rétention bornée, export authentifié et signal de saturation ; durées et taille tampon à fixer à partir de la mission. Calibrer courant/tension/température vs références ; publier offset, dérive et incertitude. Cadences de log ne sont pas des cadences de protection.
