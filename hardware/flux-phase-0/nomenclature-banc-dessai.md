# Nomenclature banc d’essai

**Équipement indépendant, jamais embarqué.** Aucun achat, prix ou stock vérifié. Les modèles cités sont des candidats et non des configurations qualifiées.

| ID | Qté | Équipement / source | À vérifier |
|---|---:|---|---|
| BN-01 | 1 | PC existant ou poste de banc, scripts de replay + ingestion et tableau de bord | débit horodaté, reproductibilité, capacité et stockage des seules données autorisées |
| BN-02 | 1 | [Keysight N6705C](https://www.keysight.com/us/en/product/N6705C/dc-power-analyzer-modular-600-w-4-slots.html), châssis, module de mesure/source à sélectionner ; alternative analyseur DC passif indépendant | plages, chute d'insertion, capture d'impulsion, étalonnage, distinguer mesure sur PSU et mesure en mission sur packs |
| BN-03 | 1+sondes | [Keysight DAQ970A](https://www.keysight.com/us/en/product/DAQ970A/data-acquisition-system.html), configuration thermocouples/accessoires à confirmer ; alternative logger calibré autonome | voies, compensation jonction froide, certificats, implantation et incertitude |
| BN-04 | 1 | Alimentation DC de laboratoire approuvée + charge électronique ; non sélectionnées | courant crête, protections et réponse transitoire |
| BN-05 | 1 jeu | Oscilloscope, sonde différentielle, générateur/marqueur sync, shunts et câbles | bande passante, isolation et dérive d'horloge |
| BN-06 | 1 jeu | Luxmètre/radiomètre, cibles visible/NIR et source contrôlée | bande spectrale et calibration ; évaluation NIR par spécialiste |
| BN-07 | accès labo | Enceinte climatique, pluie dirigée contrôlée, irradiation/vent, montage mécanique/système de mouvement | sévérités et instrumentation selon mission ; laboratoire externe si nécessaire |
| BN-08 | option | Thermographie et acquisition vidéo de référence sans données personnelles | émissivité, repères temporels et données autorisées |
| BN-09 | 1 jeu | Harnais de mesure et capteurs de référence, protection de test packs | raccords validés, méthode Kelvin, limites et procédure d'arrêt |
| BN-10 | 1 jeu | Trépied de calibration uniquement, maquette murale rigide, cibles et repères amovibles | répétabilité de géométrie et preuve de repositionnement |
| BN-11 | 1 jeu | Source PoE et instrumentation de coupure/DC, charge de test et relevé de puissance au PD | classe et chute avec câble représentatif, coupure de données distincte de la coupure d'énergie, bascule et reprise |

Le banc peut alimenter et instrumenter le prototype en laboratoire. La preuve de fonctionnement autonome exige des sessions sans PC ni accès réseau, avec DC régulé ou PoE sans service réseau et instrumentation indépendante qui ne commande pas le produit. Une coupure d'énergie est un essai distinct.
