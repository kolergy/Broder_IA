# Rapport d'essai n° 1 — Trèfle (une couleur, satin seul)

> ⚠️ **Avertissement — contenu généré par intelligence artificielle.** Ce document a été produit avec l'aide d'une IA (Claude, Anthropic) et n'a pas été validé par un spécialiste de la broderie machine. Il peut contenir des erreurs. Toute information, tout réglage et tout fichier produit — en particulier les fichiers machine (.dst) — doivent être vérifiés par un professionnel qualifié avant usage. **Un fichier machine erroné peut endommager la brodeuse** (casse d'aiguille, bourrage, contrainte mécanique), abîmer le tissu et présenter un risque pour l'opérateur : ne jamais lancer une broderie sans contrôle préalable par un spécialiste et premier essai à vitesse réduite, sur chute de tissu.

> Version 2.0 — 16 novembre 2026 (remplace la version 1.0 du même jour, voir §6)
> Résultat : **REFUSÉ par la grille de vérification** dans les deux configurations. La chaîne **s'arrête** sans approbation : la garde du satin refuse la forme (7 % de barreaux en biais). Avec approbation forcée (essai seulement), le fichier produit a **15 % de points de satin en biais** contre 0 % dans l'original.

---

## 1. Données de l'essai

| Élément | Valeur |
|---|---|
| Image d'entrée | Rendu PNG du DST d'origine (502 × 496 px, ≈ 10 px/mm, trait de rendu 0,3 mm) |
| DST d'origine | `shamrockin.dst` (Embroidermodder, zlib) : 49,9 × 49,3 mm, contour en satin seul. **Fichier de test, pas une référence de qualité** |
| Chaîne | `prototype/chaine/` version issue de la revue critique ; Ink/Stitch v3.3.0 |
| Commande | `python essai_dessin.py trefle <image> <original.dst> <inkstitch.py> 1 --config essai|production [--approuver-tout]` |
| Configurations | **essai** : compensation de traction nulle (l'image montre déjà l'étalement du fil) ; **production** : compensation du profil (0,20 mm par côté), seule représentative d'un vrai dessin |

Nature de l'essai (limite principale) : l'entrée est le **rendu du fichier auquel on se compare**. L'essai vérifie la capacité à retrouver une broderie connue ; il n'éprouve ni la normalisation d'un vrai SVG, ni une seconde taille, ni les décisions proches des seuils.

## 2. Déroulé

| Étape | Résultat |
|---|---|
| Traçage | Fond détecté sur le bord (blanc) ; 1 couleur, 1 forme en anneau |
| Mise à l'échelle | Largeur cible = largeur des points de l'original + épaisseur du trait de rendu (0,3 mm), puis retrait de la demi-épaisseur (correction du double retrait de la version 1.0) |
| Passe de simplification | Aucun défaut détecté |
| Classement | Satin (colonne, largeur moyenne 2,3 mm) |
| Garde du satin | **Refus** : 7 % de barreaux en biais (seuil 2 %), aux angles rentrants |
| Sans approbation | **Arrêt de la chaîne** (code 2), point bloquant affiché |
| Avec approbation d'essai (`--approuver-tout`, satin forcé) | Export, alerte « SATIN FORCÉ » au rapport |

## 3. Vérification (grille exécutable, `chaine/verifier.py`)

| Mesure | Original | Nous — essai | Nous — production |
|---|---|---|---|
| Dimensions (mm) | 49,9 × 49,3 | 50,0 × 49,4 | 50,2 × 49,6 |
| Points / fil cousu | 1472 / 3482 mm | 1205 / 3484 mm | 1210 / 3874 mm |
| Points de satin en biais (> 1,5 × largeur locale) | **0 %** | **14,9 %** ✗ | **13,6 %** ✗ |
| Rapport longueur / largeur, 99ᵉ centile (seuil 1,4) | 1,16 | **3,86** ✗ | **2,69** ✗ |
| Point le plus long (seuil 7 mm) | 3,6 mm | 6,9 mm | 6,9 mm |
| Espacement du satin estimé (crête à crête) | 0,36 mm | 0,31 mm | 0,32 mm |
| Sous-couche détectée | non ✗ | oui | oui |
| Points < 0,3 mm (tolérance de grille) | 19 ✗ | 0 | 0 |
| Coupes réelles (motif brut) / déplacements non coupés > 10 mm | 0 / aucun | 0 / aucun | 0 / aucun |
| Temps estimé (750 points/min, paramètres partiellement vérifiés) | 2,0 min | 1,6 min | 1,6 min |
| **Verdict de la grille** | **REFUSÉ** (points courts, pas de sous-couche) | **REFUSÉ** (biais) | **REFUSÉ** (biais) |
| Silhouette (IoU, indicateur secondaire) | — | 0,92 | 0,93 |

L'IoU est donné pour information seulement : la revue a montré qu'il ne voit ni la direction, ni la densité, ni l'ordre des points.

## 4. Interprétation
- Le défaut principal est **réel et mesuré** : les points de satin en éventail aux angles rentrants (pointes de la tige, creux entre lobes). Un satin unique faisant tout le tour ne peut pas traiter ces angles ; la pratique professionnelle découpe la colonne aux angles vifs.
- La garde du satin le détecte **avant** export et arrête la chaîne : le comportement est conforme au principe « échouer quand c'est utile ».
- L'original est lui-même refusé par la grille (19 points < 0,3 mm, aucune sous-couche) : il ne peut pas servir d'étalon de qualité.

## 5. Validation de la grille par mutation (`mutations.py`)
Sur ce dessin : « satin sans sous-couche », « satin clairsemé », « satin sans longueur maximale », « longueur minimale 0,1 mm » sont **toutes détectées** ; les mutations portant sur un remplissage ou sur l'ordre sont **sans objet** (fichier identique). Résultats : `production/mutations_resultats.json`.

## 6. Corrections par rapport à la version 1.0
| Version 1.0 | Correction |
|---|---|
| « Résultat : concluant » | **Retiré.** Le critère (IoU) ne mesurait que la silhouette ; mesuré sur des critères de broderie, le fichier est refusé |
| Écart de −0,3 mm attribué à un « retrait un peu fort » | Cause exacte : retrait appliqué en double (mise à l'échelle + retrait) — corrigé |
| Réglages présentés comme validés (barreaux à 1 mm, longueur max 7 mm) | Ils réduisent le défaut sans le supprimer ; « validé » retiré |
| Tableau 1196 points / 13 < 1 mm / 1 < 0,3 mm | Périmé dès la v1.0 (le JSON donnait 1195 / 12 / 0) ; remplacé |
| Configuration de production jamais évaluée | Évaluée (§3) |

## 7. Suite
Découpage du satin aux angles vifs, puis nouvel essai avec critères figés **avant** l'exécution.
