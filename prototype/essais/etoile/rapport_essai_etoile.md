# Rapport d'essai n° 2 — Étoile (deux couleurs, remplissage + bordure satin)

> ⚠️ **Avertissement — contenu généré par intelligence artificielle.** Ce document a été produit avec l'aide d'une IA (Claude, Anthropic) et n'a pas été validé par un spécialiste de la broderie machine. Il peut contenir des erreurs. Toute information, tout réglage et tout fichier produit — en particulier les fichiers machine (.dst) — doivent être vérifiés par un professionnel qualifié avant usage. **Un fichier machine erroné peut endommager la brodeuse** (casse d'aiguille, bourrage, contrainte mécanique), abîmer le tissu et présenter un risque pour l'opérateur : ne jamais lancer une broderie sans contrôle préalable par un spécialiste et premier essai à vitesse réduite, sur chute de tissu.

> Version 2.0 — 16 novembre 2026 (remplace la version 1.0 du même jour, voir §6)
> Résultat : **REFUSÉ par la grille de vérification** dans les deux configurations (largeur trop faible de 0,7 à 1,1 mm aux pointes ; points de satin en biais). Sans approbation, la chaîne **s'arrête** (garde du satin : 19 % de barreaux en biais ; un éclat de traçage à supprimer). Le remplissage, en revanche, a désormais une densité comparable à l'original.

---

## 1. Données de l'essai

| Élément | Valeur |
|---|---|
| Image d'entrée | Rendu PNG du DST d'origine (594 × 626 px), couleurs arbitraires, trait de rendu 0,3 mm |
| DST d'origine | `Star.DST` (Embroidermodder, zlib), 59,1 × 62,3 mm, remplissage + bordure satin. **Fichier de test, pas une référence de qualité** |
| Chaîne, commande, configurations | Comme l'essai n° 1 (`--config essai|production`, `--approuver-tout` pour forcer) |

Même limite que l'essai n° 1 : entrée = rendu du fichier de comparaison.

## 2. Déroulé

| Étape | Résultat |
|---|---|
| Traçage, 2 couleurs | Couche 1 : bordure (anneau) + 1 éclat ; couche 2 : intérieur + 280 éclats de reflets |
| Retrait de rendu | 280 éclats (0,90 mm²) et 2 petits trous supprimés — **journalisés** |
| Passe de simplification | 1 défaut : éclat de 0,03 mm² → suppression **proposée**, bloquante sans approbation |
| Classement | Bordure → satin ; intérieur → remplissage |
| Garde du satin | **Refus** : 2 barreaux hors de la forme, 19 % en biais (pointes aiguës de l'étoile) |
| Sans approbation | **Arrêt** (code 2) avec les 3 points bloquants listés ensemble |
| Avec approbation d'essai | Extension du remplissage sous la bordure (0,8 mm) ; angle de remplissage converti vers la convention Ink/Stitch ; séquençage par recouvrement : remplissage puis bordure |

## 3. Vérification

| Mesure | Original | Nous — essai | Nous — production |
|---|---|---|---|
| Dimensions (mm) | 59,1 × 62,3 | 58,0 × 61,4 ✗ | 58,4 × 61,8 ✗ |
| Points / fil cousu | 2548 / 6609 mm | 3291 / 8349 mm | 3292 / 8764 mm |
| **Remplissage** : espacement entre rangs voisins | 0,227 mm | **0,255 mm** ✓ | **0,255 mm** ✓ |
| Remplissage : direction dominante | 135° | 135° | 135° |
| Remplissage : sous-couche | non ✗ | oui | oui |
| Remplissage : fil | 4530 mm | 5689 mm (dont sous-couche) | 5686 mm |
| **Bordure** : points en biais (seuil 2 %) | 0 % | **4,0 %** ✗ | 1,0 % |
| Bordure : rapport longueur / largeur, 99ᵉ centile (seuil 1,4) | 1,23 | **1,63** ✗ | **1,50** ✗ |
| Bordure : espacement estimé (crête à crête) | 0,48 mm | 0,31 mm | 0,32 mm |
| Bordure : fil | 2079 mm | 2660 mm | 3077 mm |
| Points < 0,3 mm | 38 ✗ | 0 | 0 |
| Changements de couleur | 1 | 1 | 1 |
| Coupes réelles / déplacements non coupés > 10 mm | 0 / **13,8 mm** ✗ | 0 / aucun | 0 / aucun |
| Temps estimé | 3,6 min | 4,6 min | 4,6 min |
| **Verdict** | **REFUSÉ** | **REFUSÉ** | **REFUSÉ** |
| Silhouette (IoU, secondaire) | — | 0,975 | 0,977 |

## 4. Interprétation
- **Remplissage** : la correction de la densité (0,40 → 0,25 mm entre rangs voisins, après clarification des conventions) amène notre remplissage au niveau de l'original. La sous-couche ajoute ≈ 25 % de fil.
- **Bordure** : trop lourde (+28 à +48 % de fil) — satin plus dense que l'original (0,40 mm de crête à crête contre ≈ 0,44–0,48 mesurés) et sous-couche ; points en biais aux pointes.
- **Pointes raccourcies** (−0,7 à −1,1 mm) : satin unique sur des angles saillants aigus ; une part provient du retrait en onglet du montage d'essai (≈ 0,5 mm par pointe selon la revue).
- L'original est lui-même refusé (points courts, pas de sous-couche, déplacement non coupé de 13,8 mm).

## 5. Validation de la grille par mutation
Sur ce dessin, 7 mutations sur 8 s'appliquent et **toutes sont détectées** : ordre inversé, remplissage sans sous-couche, satin sans sous-couche, remplissage deux fois trop dense, deux fois trop clair, satin clairsemé, longueur minimale 0,1 mm. « Satin sans longueur maximale » est sans objet (aucun point > 7 mm même sans limite). Résultats : `production/mutations_resultats.json`.

## 6. Corrections par rapport à la version 1.0
| Version 1.0 | Correction |
|---|---|
| « Résultat : concluant » | **Retiré** (critère de silhouette seulement) |
| « Coupe au changement de couleur (bonne pratique) » | **Faux** : la suite de 3 sauts était le déplacement initial ; aucune coupe au changement de couleur. Les coupes sont désormais comptées par motif brut |
| « Angle 45° ; l'original à environ −30° » | **Faux** : les deux remplissages sont à 135° ; de plus, le signe de l'angle transmis à Ink/Stitch était inversé (corrigé, test automatique ajouté) |
| « Points +4 %, fil +0,5 % : concordance » | Compensation d'erreurs : remplissage trop clair (0,40 mm) et bordure trop lourde |
| « Points < 0,3 mm : mieux que l'original » | Comparaison sans valeur à un fichier de test ; remplacée par la grille absolue |
| Séquençage par code de couleur | Remplacé par un séquençage fondé sur les recouvrements |

## 7. Suite
Découpage du satin aux angles vifs ; mesure de la densité de satin sur fichiers professionnels ; essai sur un vrai dessin vectoriel à deux tailles, critères figés avant exécution.
