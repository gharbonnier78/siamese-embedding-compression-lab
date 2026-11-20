# Nomenclature produit

**Présélection de phase 0, non achetable en bloc.** Base : [BOM historique](https://github.com/gharbonnier78/siamese-embedding-compression-lab/blob/83c70dde825c/hardware/BOM_PROVISIONAL.csv), corrigée à la frontière v0.2. IDs fonctionnels, pas des désignateurs de schéma. Pas de prix, disponibilité ni durée de livraison vérifiés.

| ID | Qté indicative | Bloc / candidat documenté | Donnée bloquante et poste de puissance |
|---|---:|---|---|
| PR-01 | 1 | Calcul Linux : [Radxa ROCK 5B](https://docs.radxa.com/en/rock5/rock5b) à évaluer ; alternative CPU Linux | SKU, RAM, double capture/trigger, runtime ; veille, démarrage, rafale |
| PR-02 | 1 | eMMC ou NVMe + identité protégée/TPM selon plateforme | MPN, endurance, boot/clé, réserve A/B ; accès et idle |
| PR-03/04 | 1+1 | RGB grand angle + caméra NIR, modules et optiques TBD | obturateur, courbes spectrales, déclenchement, FOV ; capture simultanée |
| PR-05 | 1 | Émetteur/driver/interverrouillage, non sélectionnés | sécurité spectrale et thermique, courant pulsé, repos |
| PR-06 | 1+option | PIR ; mmWave en alternative d'essai, IMU | faux réveils selon mode, IRQ, veille et acquisition |
| PR-07 | 1 jeu | MCU, watchdog, RTC, mémoire durable : non sélectionnés | courant en veille réel avec horloge, persistance, consommation de réveil |
| PR-08 | TBD | Surveillance rails : [TI INA228AIDGKR](https://www.ti.com/product/INA228) candidat ; ADC/moniteurs alternatifs | plage, shunt, dissipation, adressage ; consommation continue et pertes shunt |
| PR-09 | ≥4+1 | Thermiques, ambiant/humidité, tamper, IMU si non inclus | implantations, étalonnage, périodes, veille |
| PR-10 | 1 système, capacité TBD | Secours commercial protégé avec BMS et solution de charge constructeur ; UPS amont en alternative | durée de coupure, Wh utiles au froid, protections et durée de recharge ; échange à chaud non présumé |
| PR-11 | 1 jeu | DC régulé protégé et bascule de secours ; PD PoE externe candidat si bilan validé | pics, creux de rail, chute câble, puissance au PD, courant de recharge, absence de retour source |
| PR-12 | 1 jeu | Châssis, joints/fenêtres, plaque murale ou adaptateur rigide, retenue, presse-étoupe et tamper | données site, charges et dégagements, conduction thermique, transmission et ingress ; trépied hors produit |
| PR-13 | 1 service + options | Service authentifié, Ethernet données si prévu, Wi-Fi/5G optionnels | indépendance réseau, marchés, W veille/TX ; pas de lien requis en exploitation locale |
| PR-14 | TBD | Harnais, connecteurs, accès test et éventuelle carte d'interface | données de géométrie ; architecture de cartes non décomposée |

Tous les budgets numériques par bloc sont ouverts : mesurer idle, actif, p95/pic et temps par état sur modules réels, puis vérifier puissance moyenne et thermiques du boîtier. Ne pas additionner deux fois les pertes si l'énergie est mesurée à l'entrée. LCSC prioritaire pour composants électroniques le moment venu ; COTS, packs et métrologie à sourcer séparément.
