# Architecture système — Phase 0

**Unité EO/NIR fixe, installation temporaire à une entrée événementielle — brouillon de revue.** [Mission canonique](https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/8605b80dbd90/hardware/FIXED_EVENT_INSTALLATION_MISSION.md). Elle remplace la mission portée et l'obligation de deux batteries échangeables. L'appareil est transporté entre sites, mais immobile en service. Référence de charge : ~1 000 passages/h × 10 h/j × 5 j = ~50 000 passages nominaux sur 50 h actives, pas un résultat. Rejouer aussi les arrivées en grappes ; 3,6 s d'intervalle moyen n'est pas un budget de latence. Les galeries 100 k/500 k/1 M restent des scénarios séparés.

```text
PASSAGE → PIR/capteur → MCU permanent → réveil / trigger commun
        → RGB + NIR → qualité → CPU/NPU local → recherche 1:N locale
                           stockage chiffré ↔ index + politique signée
                      → inconnu / non-décision / candidat à revue humaine
PoE PD qualifié OU DC régulé → protection et bascule ← réserve protégée
                            → MCU/RTC/probes ; rails calcul, vision, NIR commutés
Ethernet / radios / service authentifié : facultatifs pour les fonctions locales
PC et instruments externes : essais, mesures et analyse uniquement
```

| Exigence | Choix provisoire | Évidence à obtenir |
|---|---|---|
| Fonctionnement local sans réseau/PC | versions signées, stockage chiffré, index distinct de la politique, watchdog et journal MCU | essai Ethernet données/liaison coupée en conservant l'alimentation, puis perte conjointe et reprise ; aucun PC runtime |
| Capture synchronisée en géométrie fixe | support calibrable, zone commune RGB/NIR, déclenchement/retour d'exposition, PIR ou équivalent | relevé de site, délai réveil-capture, zone commune, flou et sécurité optique |
| Alimentation fixe + réserve | DC régulé comme référence de prototype ; PoE si classe, câblage, pics et thermique validés | profils de charge, plage source pack, durée de coupure, courants de démarrage/recharge, bascule au pic |
| Environnement intérieur/extérieur | fixation rigide, boîtier protégé et conduction vers coque | autorisation de fixation, essais eau, corrosion, soleil, condensation, thermique, vibration structurelle |
| Métrologie embarquée et indépendante | MCU lit alimentation et réserve/BMS, température optiques/émetteur/SoC/dissipateur/coque, ambiance, tamper, lien et intégrité de log ; instrument indépendant seulement aux essais | plages, calibration, horodatage et incertitude |

## Choix d'alimentation

| Variante | Usage et compromis | Décision |
|---|---|---|
| PoE ou DC régulé + secours protégé local | permet continuité lors de la perte de la source ; PoE simplifie le câble mais doit couvrir les pointes et la recharge sans déclencher le port. DC permet une alimentation distincte du réseau | référence : DC protégé au prototype ; PoE candidat terrain après qualification |
| Alimentation secteur via adaptateur externe + UPS amont | mutualisable et maintenable, mais perte du dernier câble/connexion non couverte. Vérifier aussi l'onduleur du commutateur PoE le cas échéant | alternative si infrastructure site fiable et continuité au dernier câble non requise |
| Batterie seule | installation sans arrivée, mais cycles, logistique et interruption accrues sur 50 h | uniquement si besoin site explicite, pas la base |

Budget : énergie mission = somme des puissances par état × leur durée, avec veille hors des 50 h si exigée. Cas historiques 8/12/18 W constants pendant 50 h : 400/600/900 Wh, illustrations non mesurées, hors veille et pertes supplémentaires. **Ne pas dimensionner le secours sur ces 50 h** : à l'entrée du produit, E réserve nominale ≥ (P critique × durée de coupure + énergie de reprise/arrêt, en Wh) / (rendement chemin secours × fraction utilisable au froid/en vieillissement). Durée et charge critique TBD ; pic et tension minimale se vérifient séparément. Dimensionner puissance PoE sur la puissance disponible au **PD**, pas la seule puissance nominale du port ; vérifier câble, chute, température, inrush, comportements de négociation et recharge. Éviter retour de courant entre sources ; protections et charge par solution qualifiée. Pas de chargeur personnalisé, pas de double pack/hot-swap sans besoin démontré et revue indépendante.

## États et vérifications

Arrêt transport : coupure sûre selon pack. Veille : MCU/RTC/IRQ et sondes essentielles ; calcul/caméras/émetteur arrêtés selon latence admissible. Détection, 1:1/1:N et rafale : calcul et vision localement, NIR inhibé par défaut ou si défaut. Coupure : bascule instrumentée, maintien de la charge critique pendant la cible ou arrêt et reprise propres ; pas de corruption. Service/mise à jour : signature, rollback et journal, sans rendre le réseau nécessaire. Mesurer coût de veille joignable séparément. Distinguer perte de données Ethernet et perte d'alimentation PoE. Pas d'action automatique sur un candidat ; évaluations synthétiques et consenties uniquement, pas de listes réelles ni identification non consentie.

## Incréments et revue

1. Kit optique fixe et maquette de support mural ; trépied seulement pour calibration/essais. 2. Intégrer calcul COTS hors réseau, mesurer profils et transitoires. 3. Instrumentation indépendante et éventuelle carte de sondes après revue. 4. Enveloppe, thermique, qualification environnementale et pilote restreint consenti après autorisations. Aucun schéma/routage avant revue globale.

**STOP** fixation dangereuse, risque optique/électrique ou absence d'autorisation ; **PIVOT** si 1:N n'apporte pas de gain face à passage seul/1:1 dans les limites d'énergie, latence et charge opérateur ; **PERSEVERE** si critères préenregistrés sont atteints avec preuves indépendantes. À fermer : relevé de site, configuration caméras/calcul et dessins, plage de coupure à couvrir, classe PoE ou spécification DC, seuils d'essais et autorisations.
