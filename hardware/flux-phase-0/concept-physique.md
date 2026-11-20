# Concept physique

**Installation temporaire fixe, sans cotation ni choix final de boîtier.** Mur ou structure rigide autorisée (poteau/truss via adaptateur qualifié). Trépied uniquement pour calibration et essais contrôlés. Les personnes marchent ; l'appareil ne se déplace pas. Toutes dimensions, charges et fixations réelles restent à vérifier sur site.

```text
Élévation : support fixe ║ platine + retenue → [ RGB | NIR | émetteur ]
                         ║                     axe incliné vers zone utile (hauteur H à relever)
                   câble fixé ↓ / boucle goutte      ↘ zone de passage
Profil : mur ║ entretoise → réglage yaw/tilt verrouillable → axes optiques
                 sortie de câble protégée                  ↘ proche → loin
Plan : support ■ ── zone RGB ∩ NIR ── repères de calibration
                  → flux piéton / occultations / surfaces réfléchissantes
```

**Montage** : plaque murale ou adaptateur structure agréé par le site, platine de réglage verrouillable, repères d'angle/repositionnement, retenue secondaire indépendante si nécessaire après revue, visserie anti-manipulation et détection d'ouverture, soulagement de traction et boucle goutte hors passage. Vérifier charge statique, torsion câble, vent/vibration, dégagements et accès service ; interdire montage public tant que fixations, support, retenue et dégagement ne sont pas validés. Séparer accès réserve et volume électronique si nécessaire, sans supposer maintien IP porte ouverte.

**Optique** : caméra RGB et NIR rigidement solidaires, émetteur séparé pour réduire les réflexions internes, pare-soleil et fenêtres aux transmissions mesurées. Au relevé, mesurer hauteur, yaw/tilt, distances proche/lointaine, largeur/flux, ligne de déclenchement, éclairage, surfaces réfléchissantes et occlusions ; qualifier champ commun et densité de pixels sur cible à plusieurs hauteurs. Premier contrôle géométrique : largeur fronto-parallèle ≈ 2d·tan(FOV horizontal/2), puis mesurer sur site car obliquité, distorsion et recouvrement invalident une simple extrapolation. Fixer critères avant capture. Relier délai PIR→première image, vitesse, temps de pose et flou ; mesurer écart d'exposition RGB/NIR. Tester NIR sur cibles inertes, inhibition matérielle au défaut, évaluation photobiologique avant toute exposition humaine. Pas de puissance NIR ou géométrie définitive présumée.

**Enveloppe** : châssis vers coque pour dissiper calcul/NIR, séparation thermique de la réserve ; conduction passive d'abord à évaluer. En extérieur, drainage, joints et fenêtre nettoyable, essais condensation, froid, pluie et soleil sur l'assemblage complet ; aucune classe IP revendiquée. En intérieur, vérifier reflets, transitions, éclairage artificiel, ventilation et accès public.

**Mise en service** : (1) approuver le site et relever la géométrie ; (2) installer, retenir et inspecter support/câbles ; (3) sur repères inertes, mesurer orientation, champ commun, densité de pixels, délai/écart de capture et sécurité optique ; (4) vérifier signatures et versions du modèle/index/politique, horloge, horodatage et état local ; (5) tester sans réseau avec alimentation assurée, puis coupure et retour de source, rétention et reprise ; (6) archiver profil et preuves d'acceptation. Refaire calibrage et contrôles après déplacement, choc ou changement de champ.
