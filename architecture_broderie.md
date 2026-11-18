# Architecture — Chaîne de broderie machine

> ⚠️ **Avertissement — contenu généré par intelligence artificielle.** Ce document a été produit avec l'aide d'une IA (Claude, Anthropic) et n'a pas été validé par un spécialiste de la broderie machine. Il peut contenir des erreurs. Toute information, tout réglage et tout fichier produit — en particulier les fichiers machine (.dst) — doivent être vérifiés par un professionnel qualifié avant usage. **Un fichier machine erroné peut endommager la brodeuse** (casse d'aiguille, bourrage, contrainte mécanique), abîmer le tissu et présenter un risque pour l'opérateur : ne jamais lancer une broderie sans contrôle préalable par un spécialiste et premier essai à vitesse réduite, sur chute de tissu.

> Version 1.0 — 16 novembre 2026
> Ce document dit **comment** les exigences (`exigences_broderie.md`) sont réalisées : composants, conventions, algorithmes, réglages techniques, essais. L'enchaînement des étapes est dans `processus_broderie.md` ; le savoir et les sources dans `collecte_de_savoir_broderie.md` (cité « CS §n »).

---

## 1. Vue d'ensemble

```
dessin (SVG) ──┐
               ├─► mise à l'échelle ─► normalisation ─► détection des défauts ─► approbations ─► corrections
image (PNG) ─► vectorisation ┘                                                                      │
                                                                                                    ▼
          fichier machine ◄─ Ink/Stitch (programme séparé) ◄─ SVG paramétré ◄─ séquençage ◄─ construction ◄─ classement ◄─ mesures
                │
                └─► vérification (grille) ─► fiche couleurs, aperçu, rapport ; code de résultat 0 / 1 / 2
```

| Composant | Choix | Raison | Licence |
|---|---|---|---|
| Conversion points | Ink/Stitch **v3.3.0** (commit `b0edd963…`), appelé en sous-processus | Seul convertisseur libre complet ; version figée (comportement non contractuel aux cas limites) | GPL-3.0 — programme séparé (EX-EXPL-03) |
| Lecture / écriture des fichiers machine | pystitch 1.0.1 (dans Ink/Stitch), pyembroidery 1.5.1 (vérification, TBF possible) | Lecture des points pour la vérification | MIT |
| Géométrie | shapely ≥ 2.1 (cercle inscrit maximal, ouvertures, intersections) | Mesures vectorielles | BSD |
| Images, rastérisation | numpy, scipy, scikit-image, Pillow | Traçage d'images, mesures sur les points | BSD / HPND |
| Langage | Python 3.12 | Paquet wxPython du système (import obligatoire par Ink/Stitch) | — |

Environnements : **cible** = deux environnements Python séparés (le nôtre ; celui d'Ink/Stitch, désigné par `INKSTITCH_PYTHON`). **Prototype actuel** : un seul environnement (signalé, revue critique §6.7).

---

## 2. Conventions d'unités (à respecter partout)

| Grandeur | Convention retenue | Piège relevé |
|---|---|---|
| Espacement de remplissage | Distance entre **rangs voisins** (convention Ink/Stitch, `row_spacing_mm`) | Wilcom mesure **un rang sur deux** : « 0,40 » Wilcom ≈ 0,20 entre rangs voisins (CS §8, revue §5.1) |
| Espacement de satin | **Crête à crête** (même côté) — Ink/Stitch `zigzag_spacing_mm` = Wilcom | — |
| Compensation de traction | **Par côté** (Ink/Stitch et Wilcom) | Certaines sources donnent une perte totale (≈ 0,17–0,25 mm) |
| Angle de remplissage | Calculé dans le repère du SVG (axe vertical vers le bas) ; transmis à Ink/Stitch avec le **signe opposé** | Signe inversé dans la v0 du prototype (revue §6.1) |
| Coordonnées du fichier machine | Unités de 0,1 mm ; en-tête aussi en 0,1 mm ; axe vertical inversé dans les enregistrements bruts | — |
| Coupe dans le fichier machine | 3 sauts a, −2a, a de faible amplitude (≤ 0,3 mm) | Une suite de sauts qui déplace l'aiguille n'est pas une coupe |
| Longueur minimale de point | 0,3 mm, à 0,05 mm près (pas diagonal 2 × 2 unités = 0,28 mm) | — |

---

## 3. Modules (prototype `prototype/chaine/`)

| Module | Rôle | Exigences |
|---|---|---|
| `tracer.py` | Image → formes par couleur : fond = couleur dominante du bord ; k-moyennes ; fermeture ; contours ; imbrication. Journalise contours et trous écartés | EX-FONC-02, EX-COND-07 |
| `geometrie.py` | Mise à l'échelle ; mesures ; détection des appendices ; classement ; angle de remplissage et conversion de signe ; détection des défauts ; application déterministe des corrections approuvées avec contrôle d'invariant | EX-FONC-03, EX-COND-01/02/04/05/11 |
| `satin.py` | Satin en anneau (rails = contours, barreaux par appariement monotone) ; **garde** `controler_barreaux` | EX-COND-10 |
| `sequencer.py` | Ordre par recouvrements (graphe de précédence), puis regroupement par couleur | EX-QUAL-08/09 |
| `inkstitch_io.py` | Écriture du SVG paramétré ; exécution d'Ink/Stitch (règles §5) | EX-FONC-04/08 |
| `processus.py` | Enchaînement ; rassemble tous les points bloquants ; exception `Arret` | EX-COND-07/08/09 |
| `dst_brut.py` | Lecture brute des enregistrements : coupes réelles, déplacements, changements de couleur | EX-QUAL-10 |
| `qualite.py` | Mesures par bloc de couleur (§7) | EX-QUAL-03 à 13 |
| `verifier.py` | Grille : une ligne par critère, statut OK / ECHEC / INFO | EX-VERIF-01 |
| `fiche.py` | Fiche couleurs | EX-FONC-05 |
| `comparer.py` | Silhouette (IoU, meilleure translation) et images de comparaison — **indicateur secondaire** | — |
| `reglages.py` | Profil de réglages avec conventions et statut de chaque valeur | §6 |

Outils d'essai : `essai_dessin.py` (montage d'essai, §9), `mutations.py` (validation par mutation, §8), `tests/test_chaine.py` (tests automatiques, §8).

---

## 4. Algorithmes

### 4.1 Mesures (CS §11)
- Largeur maximale = 2 × rayon du cercle inscrit maximal ; largeur moyenne = 2 × aire / périmètre ; allongement = aire / largeur maximale².
- La compacité est calculée mais **n'intervient plus** dans le classement (elle excluait les colonnes de rapport < 4, revue §3.1).
- **Appendices** : ouverture morphologique de rayon 1 mm ; parties retirées plus longues que 5 mm ⇒ forme mixte, découpage requis. Si le corps restant fait moins de 20 % de l'aire, la forme est fine partout (colonne, anneau) et n'est pas mixte.

### 4.2 Classement
Voir la table du processus (§3.5). Mesures à ±10 % d'un seuil signalées.

### 4.3 Angle de remplissage
16 angles candidats, nombre de fragments de rangs (pas 1 mm) ; le plus petit gagne. Limite connue : le critère compte surtout le nombre de rangs (choisit l'axe long), ne tient pas compte de la tenue ni du sens du tissu (revue §3.7). Transmission à Ink/Stitch : signe opposé (test automatique).

### 4.4 Satin en anneau et garde
- Rails rééchantillonnés à 0,5 mm, orientés dans le même sens, ouverts à la paire de points la plus proche.
- Appariement monotone minimisant la somme des longueurs (programmation dynamique) ; barreaux tous les ≈ 1 mm, prolongés de 0,4 mm.
- **Garde** : pour chaque barreau, rapport longueur / (2 × distance du milieu au bord) ; refus si un barreau sort de la forme ou si plus de 2 % des barreaux dépassent 1,5. Refus = point bloquant, sauf approbation explicite `<objet>:forcer_satin` (journalisée « SATIN FORCÉ »).
- Limites : un seul satin pour tout l'anneau (éventails aux angles rentrants, pointes saillantes raccourcies) ; espacement des barreaux sur le seul rail extérieur ; appariement en temps quadratique.

### 4.5 Séquençage
Contrainte « i avant j » pour tout couple qui se touche (tolérance 0,1 mm) avec rang d'empilement(i) < rang(j). Parmi les objets disponibles : même couleur que le précédent d'abord, puis rang, puis indice. Cycle ⇒ erreur.

### 4.6 Extension sous bordure
Un remplissage contenu dans l'extérieur d'une bordure satin d'une autre couleur est étendu de la moitié de la largeur moyenne de la bordure, puis découpé par l'extérieur de la bordure. Échec ⇒ alerte (plus d'abandon silencieux).

---

## 5. Règles d'exécution d'Ink/Stitch

1. Sous-processus : `<python d'Ink/Stitch> inkstitch.py --extension=output --format=dst <svg>` ; sortie capturée en octets.
2. Métadonnées obligatoires du SVG : `inkstitch_svg_version` = 4 (sinon plantage sans écran ou blocage infini) ; `min_stitch_len_mm` = 0,3.
3. Environnement par appel : `XDG_CONFIG_HOME` = dossier temporaire privé ; `INKSTITCH_OFFLINE_SCRIPT=true` ; `PYTHONUTF8=1` ; `LANGUAGE=en_US` ; `PYTHONIOENCODING` retiré.
4. Délai maximal (défaut 1800 s) ; dépassement ⇒ erreur explicite.
5. Un appel à la fois.
6. Succès = fichier non vide **et** vérification ; sortie d'erreur non vide ou code non nul avec fichier produit ⇒ alerte au rapport.
7. Non retenu à ce stade : désactivation de la journalisation d'Ink/Stitch (gain de temps mesuré par un tiers, non mis en œuvre) ; export en archive avec liste des fils (remplacé par notre fiche couleurs).

---

## 6. Attributs Ink/Stitch écrits (valeurs du profil par défaut)

| Objet | Attributs |
|---|---|
| Remplissage | `fill_method=tatami_fill`, `row_spacing_mm=0.25`, `angle=<signe opposé>`, `fill_underlay=true`, `fill_underlay_inset_mm=0.4` |
| Satin | `satin_column=true`, `zigzag_spacing_mm=0.4`, `pull_compensation_mm=0.20` (par côté), `max_stitch_length_mm=7` ; sous-couche : `center_walk_underlay` (< 2 mm), `contour_underlay` (2–4 mm), `contour_underlay` + `zigzag_underlay` (≥ 4 mm) |
| Document | `inkstitch_svg_version=4`, `min_stitch_len_mm=0.3` |

Non encore exploités : raccourcissement des points en courbe serrée (`short_stitch_inset` 15 %, `short_stitch_distance_mm` 0,25 — défauts d'Ink/Stitch conservés) ; compensation de poussée (≈ 0,2 mm en bout de colonne, aucun paramètre Ink/Stitch dédié) ; chevauchement entre aplats voisins (`expand_mm`).

---

## 7. Mesures de qualité (`qualite.py`)

Calculées sur les points eux-mêmes, par bloc de couleur, de la même façon pour notre fichier et pour un fichier de comparaison.

| Mesure | Méthode | Limite |
|---|---|---|
| Type de bloc | Remplissage si ≥ 50 % du fil dans une direction (± 15°) ; satin si rapport médian longueur / largeur locale > 0,6 ; sinon point droit | Heuristique ; un bloc peut mélanger plusieurs objets |
| Surface couverte | Rastérisation (20 px/mm, trait 0,4 mm) + fermeture morphologique 0,6 mm | Dépend de ces paramètres |
| Espacement entre rangs (remplissage) | Surface / fil dans la direction dominante | Méthode de la revue (retrouve 0,403 pour un réglage de 0,40) |
| Largeur locale, points en biais | Transformée de distance de la surface couverte ; largeur = 2 × max sur le point ; biais si longueur > 1,5 × largeur | Approximation |
| Espacement du satin | 2 × surface / fil des points traversants (rapport > 0,6) | Biais ≈ −20 % (réglage 0,40 lu 0,32) |
| Sous-couche | Remplissage : direction dominante des premiers 15 % du fil différente de plus de 30° ; satin : plus de la moitié des premiers 10 % du fil sans demi-tour | Heuristique validée par mutation |
| Ordre | Bloc satin brodé avant un bloc remplissage qu'il recouvre à plus de 20 % | Cas bordure / remplissage seulement |
| Coupes, déplacements | Lecture brute (`dst_brut.py`) | — |
| Pénétrations | Maximum de points par cellule de 1 mm² | Pas de seuil |
| Temps | Points / 750 par minute + 3,5 s par coupe + 10 s par changement (non vérifié) | Paramètres en partie non vérifiés |

---

## 8. Essais automatiques et validation

- **Tests** (`tests/test_chaine.py`, 19 tests) : signe de l'angle (barre inclinée), coupes par motif brut, lettres A et P refusées par la garde, anneau accepté, classement de 11 formes contre un jugement écrit à l'avance, séquençage par recouvrements, aucune suppression sans approbation, invariant des corrections.
- **Mutations** (`mutations.py`) : 8 dégradations (ordre inversé, sous-couches retirées, densité doublée ou divisée par deux, satin clairsemé, longueur max retirée, longueur min 0,1 mm). Une mutation qui ne change pas le fichier, ou dont la dégradation n'est pas présente, est « sans objet ». Exigence : toute mutation applicable détectée par l'exigence qu'elle vise.

## 9. Montage d'essai (`essai_dessin.py`) — ne fait pas partie de la chaîne
- Entrée = rendu d'un fichier connu : largeur cible = largeur des points + 0,3 mm (trait de rendu), puis retrait de 0,15 mm.
- Configurations : `essai` (compensation nulle) et `production` (compensation du profil).
- Rang d'empilement des couches tracées : plus grande surface dessous (heuristique d'essai).
- Approbation globale `--approuver-tout` réservée aux essais, journalisée.

## 10. Limites connues de l'architecture
- Satins ouverts (traits, lettres), découpage des formes mixtes, point droit sur ligne médiane : non construits (arrêt).
- Normalisation SVG (§3.2 du processus) : non implémentée — aucune entrée vectorielle réelle traitée.
- Réduction de palette, références de fil : non implémentées.
- Seuils non étalonnés faute de fichiers professionnels et de broderies réelles.

---

## Journal des versions
| Version | Date | Changements |
|---|---|---|
| 1.0 | 16/11/2026 | Première version : séparation du « comment » hors du processus, après la revue critique |
