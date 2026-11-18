# Collecte de savoir — Broderie machine à partir de dessins vectoriels

> ⚠️ **Avertissement — contenu généré par intelligence artificielle.** Ce document a été produit avec l'aide d'une IA (Claude, Anthropic) et n'a pas été validé par un spécialiste de la broderie machine. Il peut contenir des erreurs. Toute information, tout réglage et tout fichier produit — en particulier les fichiers machine (.dst) — doivent être vérifiés par un professionnel qualifié avant usage. **Un fichier machine erroné peut endommager la brodeuse** (casse d'aiguille, bourrage, contrainte mécanique), abîmer le tissu et présenter un risque pour l'opérateur : ne jamais lancer une broderie sans contrôle préalable par un spécialiste et premier essai à vitesse réduite, sur chute de tissu.

> Statut : **version 0.5** — 4 recherches initiales + 6 recherches ciblées + 3 enquêtes de terrain + 10 essais techniques + revue critique indépendante intégrés. Les points non vérifiés sont signalés « non vérifié ». Journal des versions en fin de document.
> Légende des niveaux de preuve : **[ESSAI]** vérifié par exécution dans notre environnement ; **[SOURCE]** lu dans le code ou la documentation officielle ; **[ANECDOTE]** témoignage d'utilisateur ; **non vérifié**.
> Date : 15 novembre 2026
> Objet : réunir les connaissances vérifiées nécessaires pour produire un fichier machine (DST Tajima) à partir d'un dessin vectoriel quelconque. Les fichiers DST d'exemple (§17) servent de cas d'essai.

---

## 1. Principe fondamental : un SVG n'est pas un fichier de broderie

Un SVG décrit des **formes**. Un fichier de broderie décrit des **mouvements d'aiguille** (points, sauts, coupes, changements de couleur). Le passage de l'un à l'autre s'appelle la **numérisation** (« digitizing » / « punching ») : pour chaque forme, on décide du type de point, de l'angle, de la densité, de la sous-couche et de l'ordre de passage.

Chaîne classique : **Illustration → Vectorisation → Numérisation → Réglage des points → Export → Essai sur tissu.**

Un dessin vectoriel propre couvre déjà les deux premières étapes.

Source : [Maggie Frames — how to digitize](https://www.maggieframes.com/nl/blogs/embroidery-blogs/how-to-digitize-embroidery-designs-master-software-techniques-for-flawless-results), [Hoopingstation — DST logo files](https://hoopingstation.com/blogs/news/the-ultimate-guide-to-creating-professional-dst-logo-files)

---

## 2. Formats de fichiers

| Format | Éditeur | Contenu | Usage |
|---|---|---|---|
| **DST** (Data Stitch Tajima) | Tajima | Coordonnées et commandes uniquement — **pas de couleurs, pas d'affectation d'aiguille** | Format d'échange universel en broderie industrielle |
| **TBF** (Tajima Binary Format) | Tajima | DST + adressage des aiguilles | Machines Tajima avec adressage d'aiguille (ex. paillettes double) |
| **T01** | Tajima | — | Machines Tajima chenille |
| **EMB** | Wilcom | Fichier de travail éditable (objets, paramètres) | Fichier maître Wilcom |
| **PXF** | Pulse (Tajima DG/ML, DG16) | Fichier de travail éditable | Fichier maître du logiciel Tajima |
| **PES / EXP / JEF / VP3** | Brother / Melco / Janome / Husqvarna | Formats machine propriétaires | Machines domestiques ou d'autres marques |

Points clés :
- Le DST ne stocke **aucune couleur** : il faut fournir à l'opérateur une **fiche de séquence des couleurs** séparée.
- Dans un DST, **changement de couleur et arrêt utilisent le même code** (`0xC3`) ; une **coupe** est codée comme une suite de sauts.
- Bonne pratique : toujours conserver un **fichier maître éditable** (EMB, PXF ou SVG Ink/Stitch) et n'exporter le DST qu'en fin de chaîne.
- « tajma.tds » : **aucun format de broderie n'utilise l'extension .TDS** (seuls des fichiers Adobe et Borland). Lecture la plus probable : **faute de frappe pour Tajima .DST** (mêmes lettres) ; sinon le format riche Tajima **.TBF**. Voir §15.

Sources : [Wilcom — Tajima](https://wilcom.com/tajima), [filext — PXF](https://filext.com/file-extension/PXF), source Ink/Stitch / pystitch `DstWriter.py` ([dépôt](https://github.com/inkstitch/inkstitch))

---

## 3. Les deux filières logicielles

### 3.1 Wilcom EmbroideryStudio (référence industrielle)
- Deux modes : espace de numérisation Wilcom et mode graphique CorelDRAW intégré ; l'import SVG passe souvent par ce dernier.
- Flux : import de l'illustration → conversion automatique ou numérisation manuelle → enregistrement EMB → export DST / TBF / T01.
- Licence coûteuse, Windows uniquement. Hatch est la gamme grand public de Wilcom.
- Un test indépendant signale un léger décalage géométrique entre vecteur importé et DST ré-importé dans Wilcom (≈ 0,1 mm).

Sources : [Wilcom Quick Reference](https://docs.wilcom.com/embroiderystudio/28/en/downloads/QuickReference.pdf), [Hatch](https://hatchembroidery.com/business), [Test Pulse / Wilcom / Chroma / DesignShop](https://embroideryhooping.com/blogs/articles/the-hidden-0-1-mm-shift-testing-svg-import-and-dst-output-accuracy-in-pulse-wilcom-chroma-and-designshop)

### 3.2 Inkscape + Ink/Stitch (libre, scriptable) — **filière retenue pour l'étude**
- Extension libre (GPL v3) d'Inkscape.
- Écrit : CSV, DST, EXP, JEF, PEC, PES, SVG, TXT (G-code), U01, VP3. Ink/Stitch n'expose pas le TBF, **mais ses bibliothèques sous licence MIT pyembroidery et pystitch savent écrire le TBF** (§15) → TBF atteignable par conversion.
- Remplissage en dégradé linéaire natif ; outils de commande (coupe, arrêt, point de départ/fin).
- Pas de bouton « image → broderie » : on part d'un dessin vectoriel propre.

Sources : [Ink/Stitch — fonctionnalités](https://inkstitch.org/features), [Ink/Stitch — dégradé linéaire](https://inkstitch.org/docs/stitches/linear-gradient-fill/), [Ink/Stitch — mélange de couleurs](https://inkstitch.org/tutorials/color-blending/)

---

## 4. Contraintes physiques de la broderie

| Contrainte | Valeur indicative | Source |
|---|---|---|
| Hauteur minimale de texte (casse mixte) | ≈ 5 mm | [PIWorld](https://www.piworld.com/embroidery-digitizing-tips-on-creating-designs-with-letters/all), [Wilcom 10 tips](https://www.vitordigitizing.net/uploads/1/1/0/6/11065424/10_tips_to_get_the_best_embroidery_logo_results_by_wilcom.pdf) |
| Hauteur minimale de texte (capitales) | ≈ 3,8 mm | [PIWorld](https://www.piworld.com/embroidery-digitizing-tips-on-creating-designs-with-letters/all) |
| Largeur minimale d'une colonne (jambage de lettre) | ≈ 0,8 mm | [PIWorld](https://www.piworld.com/embroidery-digitizing-tips-on-creating-designs-with-letters/all) |
| Dégradés | Le fil ne se mélange pas ; dégradés **radiaux impossibles** en point tatami | [Printful](https://www.printful.com/blog/gradient-embroidery) |
| Petits détails | À supprimer, agrandir ou simplifier | [Made Good Designs](https://madegooddesigns.com/embroidery-design/) |
| Plusieurs tailles | Un logo graphique = plusieurs fichiers de broderie selon la taille | [Wilcom 10 tips](https://www.vitordigitizing.net/uploads/1/1/0/6/11065424/10_tips_to_get_the_best_embroidery_logo_results_by_wilcom.pdf) |

---

## 5. Analyse d'un dessin avant numérisation (méthode)

Toute analyse se fait **à la taille brodée** : échelle (mm par unité du dessin) = largeur brodée / largeur utile du dessin.

| Élément à mesurer | Seuil de référence (§4) | Diagnostic type |
|---|---|---|
| Hauteur des minuscules / des capitales | 5 mm / 3,8 mm | Sous le seuil → agrandir, épaissir, fil 60 wt |
| Largeur des jambages de lettres | 0,8 mm absolu, 1 mm conseillé | Sous le seuil → satin impossible |
| Traits fins | < 1 mm | Point droit ou point triple ; < 0,4 mm : rendu ≈ épaisseur du fil |
| Petits détails (points, pastilles) | ≈ 0,4 mm (non brodable) ; ≈ 1 mm (risque de nœud) | Supprimer, fusionner ou agrandir |
| Dégradés | Linéaires seulement | Couleur à plat ou dégradé linéaire sur les grandes surfaces ; radial → à plat |
| Nombre de teintes | ≤ nombre d'aiguilles | Réduction de palette ; moins de fils pour les petits formats |
| Texte vivant, images intégrées | — | À convertir ou à refuser |
| Calques, masques, effets | — | Voir §15.4 |

---

## 6. Ink/Stitch : paramètres stockés dans le SVG

Source unique de cette section : code source Ink/Stitch (branche `main`, commit `42e771e`, 3 novembre 2026), [dépôt GitHub](https://github.com/inkstitch/inkstitch) — fichiers `lib/svg/tags.py`, `lib/elements/*.py`, `lib/metadata.py`, `lib/update.py`.

### 6.1 Mécanisme
- Espace de noms : `xmlns:inkstitch="http://inkstitch.org/namespace"`.
- Chaque paramètre est un attribut `inkstitch:<nom>` posé sur la forme.
- Suffixe `_mm` = millimètres, quelles que soient les unités du document.
- Booléens : `true` / `yes` / `1`.
- **Conséquence : tout le paramétrage peut être écrit par un script Python, sans interface graphique.**

### 6.2 Paramètres principaux (valeur par défaut)

**Remplissage** — `fill_method` (`tatami_fill` ; aussi `contour_fill`, `guided_fill`, `meander_fill`, `circular_fill`, `linear_gradient_fill`…), `angle` (0° = rangs horizontaux, compté **dans le sens inverse des aiguilles d'une montre**, axe vertical vers le haut : signe opposé au repère du SVG [ESSAI]), `row_spacing_mm` (0,25, **entre rangs voisins**), `max_stitch_length_mm` (4,0), `pull_compensation_mm` (0), `fill_underlay` (vrai), `fill_underlay_angle`, `fill_underlay_row_spacing_mm`, `fill_underlay_inset_mm` (0).

**Trait** — `stroke_method` (`running_stitch` ; aussi `zigzag_stitch`, `ripple_stitch`, `manual_stitch`), `running_stitch_length_mm` (2,5), `repeats` (1), `bean_stitch_repeats` (0 ; point triple = 1).

**Colonne satin** — `satin_column` (`true` pour activer), `zigzag_spacing_mm` (0,4), `pull_compensation_mm` (0), `contour_underlay`, `center_walk_underlay`, `zigzag_underlay` (désactivés par défaut).

**Communs** — `trim_after` (coupe après l'objet), `stop_after` (arrêt), `ignore_object`, `stroke_first`.

### 6.3 Règles d'interprétation
- **Remplissage par défaut = noir** si aucune couleur de remplissage n'est donnée : un tracé « trait seul » doit avoir `fill:none` explicitement.
- Fond + trait sur un même objet → deux objets brodés (fond d'abord).
- Colonne satin si `satin_column="true"` **et** (plusieurs sous-chemins **ou** épaisseur > 1 mm).
- **Les masques de découpe (`clipPath`) sont appliqués** → les éléments découpés par un masque sont brodés découpés.
- **Dégradé linéaire** : brodé dans la couleur du premier arrêt, sauf si `fill_method="linear_gradient_fill"`. **[ESSAI]** Les coordonnées en pourcentage (`gradientUnits` par défaut, `objectBoundingBox`) sont **lues comme des millimètres** → bandes mal placées, arrêt intermédiaire perdu. Seules les coordonnées absolues (`gradientUnits="userSpaceOnUse"`) fonctionnent.
- **Dégradé radial** : **[ESSAI]** brodé en **noir** (et non dans la couleur du premier arrêt). À remplacer par une couleur à plat avant Ink/Stitch.
- **Opacité** : **[ESSAI]** `opacity` est ignorée, même à 0 (l'objet est brodé). Seul `fill-opacity:0` supprime l'objet. Les objets invisibles doivent être retirés par notre préparation.
- Éléments ignorés : `display:none`, `<defs>`, `<clipPath>`, `<mask>`, texte vivant, images.

### 6.4 Ordre et couleurs
- Ordre de broderie = **ordre du document SVG**. Pas de regroupement automatique par couleur.
- Changement de couleur émis **uniquement** quand deux objets consécutifs diffèrent → **le script doit regrouper par couleur**.

### 6.5 Réglages du document (bloc `<svg:metadata>`)
- `min_stitch_len_mm` = 0,1 ; `collapse_len_mm` = 3 (saut minimal) ; `min_satin_stroke_width_mm` = 1.
- **Indispensable** : `<inkstitch:inkstitch_svg_version>4</inkstitch:inkstitch_svg_version>`.
  Sans cette balise, le fichier est traité comme ancien : ouverture d'une **boîte de dialogue bloquante** et réécriture silencieuse de paramètres (traits convertis en zigzag, longueur de point forcée à 1,5 mm, rails de satin modifiés).

---

## 7. Installation et usage en ligne de commande

Sources : [Ink/Stitch — installation Linux](https://inkstitch.org/docs/install-linux/), [Ink/Stitch — ligne de commande](https://inkstitch.org/docs/command-line), [installation manuelle développeur](https://inkstitch.org/developers/inkstitch/manual-setup/), code source (`inkstitch.py`, `lib/extensions/output.py`, `zip.py`, `update.py`).

### 7.1 Version et paquets
- Dernière version : **v3.3.0 (31 juillet 2026)**. Inkscape ≥ 1.0.2 requis pour l'usage graphique.
- Paquets Linux : `.deb`, `.rpm`, installeur `.sh`, archive `.tar.xz` (x86_64, i386, arm64). **Pas de paquet pip, pas d'AppImage.** L'exécutable empaqueté est `bin/inkstitch`.
- Alternative : dépôt git (`git clone --recurse-submodules`) + `pip install -r requirements.txt`, Python ≥ 3.11.

### 7.2 Export sans interface graphique — **possible**
`inkstitch.py` est un programme autonome ; il charge le SVG via la bibliothèque `inkex`. Inkscape n'est appelé **que** pour le rendu PNG.

```bash
# DST seul (forme vérifiée dans le code source, non documentée telle quelle)
python3 inkstitch.py --extension=output --format=dst dessin.svg > dessin.dst

# Archive multi-formats + liste des fils (documenté)
./inkstitch --extension=zip --format-dst=True --format-threadlist=True dessin.svg > dessin.zip

# Aperçu du plan de broderie en SVG (mode simple, sans Inkscape)
./inkstitch --extension=stitch_plan_preview --render-mode=simple dessin.svg > apercu.svg
```

- Le DST sort sur la sortie standard ; les erreurs sur la sortie d'erreur.
- ⚠ **Si aucun objet brodable n'est trouvé, le programme sort avec le code 0 et un fichier vide** → toujours vérifier que la sortie n'est pas vide.
- `--id=<id>` limite l'export à certains éléments.
- `inkscape --actions=org.inkstitch…` ne permet pas de passer des paramètres → appeler `inkstitch.py` directement.

### 7.3 Aperçus
- `png_simple` et `png_realistic` (et leurs options dans `zip`) **appellent Inkscape** en ligne de commande.
- `stitch_plan_preview` en mode simple produit un SVG pur ; conversion PNG possible avec `rsvg-convert` ou `cairosvg` (piste personnelle, non documentée).

### 7.4 Dépendances et pièges
| Point | Détail | Contournement |
|---|---|---|
| `wxPython` | Bibliothèque d'interface, mais **importée obligatoirement** même pour l'export | **[ESSAI]** `apt install python3-wxgtk4.0` ; ce paquet n'existe que pour Python 3.12 → environnement virtuel Python 3.12 avec `--system-site-packages`. Alternative éprouvée par d'autres : module `wx` factice (§16) |
| `inkex` | Épinglé sur une **étiquette** GitLab `EXTENSIONS_AT_INKSCAPE_1.4.1` (GitLab bloqué par le proxy) | **[ESSAI]** `inkex==1.4.1` de PyPI fonctionne pour tous les essais |
| Dialogue de mise à jour | Fenêtre wx ouverte si le SVG a des attributs Ink/Stitch sans balise de version | Écrire `inkstitch_svg_version = 4` dans les métadonnées |
| Extensions graphiques | `params`, `simulator`, `print_pdf`, `lettering` ouvrent des fenêtres | Inutilisables sans écran ; non nécessaires ici |
| Bibliothèque de points | Ink/Stitch utilise désormais **pystitch** (fork mis à jour de pyembroidery, v1.0.1) | Utiliser pystitch ou pyembroidery pour la vérification |

---

## 8. Choix des points par type d'élément

Sources principales : [Ink/Stitch — mélange de couleurs](https://inkstitch.org/tutorials/color-blending/), [dégradé linéaire](https://inkstitch.org/docs/stitches/linear-gradient-fill/), [point droit](https://inkstitch.org/docs/stitches/running-stitch/), [colonne satin](https://inkstitch.org/docs/stitches/satin-column/), [outils satin](https://inkstitch.org/docs/satin-tools/), [sous-couches](https://inkstitch.org/tutorials/underlay/), [préférences](https://inkstitch.org/docs/preferences/), [Mr X Stitch — compensation](https://www.mrxstitch.com/pull-compensation/), [ASI — petites lettres](https://members.asicentral.com/news/how-to/may-2018/keep-your-small-letters-crisp/).

### 8.1 Recommandation par type d'élément (dimensions à la taille brodée)

| Type d'élément | Type de point | Réglages / remarques |
|---|---|---|
| Surface avec dégradé linéaire | **Remplissage en dégradé linéaire** | Rangs perpendiculaires à la direction du dégradé ; sous-couche comme un remplissage automatique |
| Surface avec dégradé, plusieurs formes | **Remplissage en dégradé linéaire** par forme | « Convertir en blocs de dégradé » : expérimental, qualité moindre |
| Contour fin (≈ 0,4 mm) par-dessus une surface | **Point triple** (`bean_stitch_repeats = 1`) | Un satin exigerait ≥ 1 mm de large ; longueur de point ≈ 2–2,5 mm (non vérifié) |
| Trait très fin (≈ 0,25 mm) | **Point droit simple** | Rendu réel ≈ épaisseur du fil (≈ 0,2 mm selon fiches techniques, voir §19.9) ; outil « Autoroute Running Stitch » pour l'ordre |
| Petit cercle (≈ 1 mm) | Petit cercle en point droit ou point manuel | Points ≥ 0,3 mm |
| Détail minuscule (≈ 0,4 mm) | **Supprimer** ou remplacer par un point unique | Plus petit que l'épaisseur du fil |
| Petit texte vectorisé (jambages ≈ 1 mm) | **Colonnes satin dessinées** depuis les contours | Sous-couche « marche centrale » ou aucune ; jambages < 1 mm → **sous la limite** du satin |

### 8.2 Constats importants
- **Texte** : aucune conversion automatique fiable « lettre vectorisée → satin » ; chaque lettre demande deux rails et des barreaux, et les lettres complexes (B, g, a…) doivent être découpées. Seuil usuel de hauteur : 5 à 6,35 mm. Leviers pour un texte trop petit : agrandir le dessin, épaissir les lettres, fil 60 wt avec aiguille 70/10.
- **Polices intégrées** Ink/Stitch : ne reproduisent pas un lettrage de marque spécifique.
- **Superpositions** : Ink/Stitch n'a **pas de commande de découpe des points cachés** (« Knockdown Fill » fait autre chose). Découper les formes dans Inkscape (différence de chemins) puis utiliser `expand_mm` pour refermer les jours.

### 8.3 Sous-couches et valeurs physiques
| Paramètre | Valeur | Source |
|---|---|---|
| Satin 1–2 mm | Sous-couche marche centrale | [Ink/Stitch underlay](https://inkstitch.org/tutorials/underlay/) |
| Satin 2–3,5 mm | Sous-couche contour (retrait 0,4–0,6 mm) | idem |
| Satin > 4 mm | Contour + zigzag | idem |
| Remplissage | Sous-couche à 90° de l'angle de dessus, espacement ≈ 3× | [Ink/Stitch fill](https://inkstitch.org/docs/stitches/fill-stitch/) |
| Densité de couverture | « ≈ 0,4 mm » chez les sources professionnelles — **convention non précisée** ; Wilcom mesure un rang sur deux, soit ≈ 0,20 mm entre rangs voisins (§19.1). **Ancienne mention « sourcé 0,40 mm entre rangs » retirée** | [Mr X Stitch](https://www.mrxstitch.com/pull-compensation/), [Wilcom](https://wilcom.com/resources/blog/stitch-spacing-or-density) |
| Valeur par défaut Ink/Stitch | Espacement 0,25 mm **entre rangs voisins**, longueur max 4 mm — proche de la pratique professionnelle ; [MESURE] original de test : 0,23 mm | Code source (`fill_stitch.py`) |
| Perte de largeur d'un satin | ≈ 0,17–0,25 mm sur tissu stable — **total ou par côté non précisé** ; Wilcom et Ink/Stitch appliquent la compensation **par côté** (§19.2) | [Mr X Stitch](https://www.mrxstitch.com/pull-compensation/) |
| Largeur maximale d'un satin | ≤ 7 mm (découpage automatique Wilcom) ; ≤ 10 mm conseillé, ≈ 12 mm plafond | [Wilcom quality-17](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Quality/quality/quality-17.htm), [Wilcom blog](https://wilcom.com/resources/blog/mastering-basic-stitch-types-satin-stitch-and-tatami-stitch) |
| Largeur minimale d'un satin (Ink/Stitch) | > 1 mm (préférences) ; ≥ 1,5 mm (tutoriel polices) | [Ink/Stitch préférences](https://inkstitch.org/docs/preferences/), [tutoriel polices](https://inkstitch.org/tutorials/font-creation/) |
| Longueur minimale de point | ≥ 0,3 mm (Ink/Stitch) ; ≥ 1 mm conseillé (Melco) | [Ink/Stitch préférences](https://inkstitch.org/docs/preferences/), [Melco](https://melco-service.com/source1/Stitches_Too_Small.htm) |
| Épaisseur d'un fil 40 wt | Fiches techniques : 27 tex (Madeira Polyneon 40, Isacord 40) ; diamètre calculé ≈ 0,16 mm, ≈ 0,2 mm aplati. La valeur « 0,4 mm » d'une source grand public est **douteuse** (la même source donne aussi 0,2 mm) | §19.9 |

---

## 9. Vérification du fichier DST

Sources : [pyembroidery](https://github.com/EmbroidePy/pyembroidery) (v1.5.1), [pystitch](https://pypi.org/project/pystitch/) (v1.0.1), [EduTech Wiki — DST](https://edutechwiki.unige.ch/en/Embroidery_format_DST), [KDE — Tajima Ternary](https://community.kde.org/Projects/Liberty/File_Formats/Tajima_Ternary), [Wilcom — machines](https://docs.wilcom.com/embroiderystudio/27/en/OnlineHelp/Setup/machines/machines-3.htm), [Embrilliance — DST](https://embrilliance.zendesk.com/hc/en-us/articles/360052392074-DST-Conversion-Preferences).

### 9.1 Le format DST
- En-tête ASCII de 512 octets : `LA` (nom, 16 car.), `ST` (nombre d'enregistrements), `CO` (changements de couleur), `+X -X +Y -Y` (étendue), `AX AY` (point final), `MX MY`, `PD`.
- Unité des coordonnées : **0,1 mm**. **[ESSAI]** L'étendue de l'en-tête est aussi en **0,1 mm** (tranché : `+X/−X = 400` pour une demi-largeur de 40 mm ; EduTech Wiki, qui indique des cm, se trompe). `ST` compte **tous** les enregistrements, pas seulement les points.
- Chaque enregistrement fait 3 octets, codage ternaire → **déplacement maximal ±12,1 mm par axe**. Au-delà, l'encodeur découpe en plusieurs sauts.
- Pas de couleurs. Changement de couleur et arrêt : **même code**. Pas de code de coupe : la machine interprète **3 à 5 sauts consécutifs** comme une coupe (Ink/Stitch en écrit 3 par défaut).

### 9.2 Lecture en Python
```python
import pyembroidery as pe          # ou pystitch, même API
p = pe.read("dessin.dst")
p.count_stitch_commands(pe.STITCH)  # vrais points (count_stitches() compte TOUT)
p.count_color_changes()
p.bounds()                          # (xmin, ymin, xmax, ymax) en 0,1 mm
pe.write_png(p, "apercu.png", {"guides": True})
```
Constantes : `STITCH=0, JUMP=1, TRIM=2, STOP=3, END=4, COLOR_CHANGE=5` (masquer avec `COMMAND_MASK`).

**[ESSAI]** Pièges de relecture :
- Ink/Stitch écrit le DST via **pystitch** (fork de pyembroidery) ; les deux bibliothèques donnent des résultats identiques.
- À la lecture, **toute suite de ≥ 3 sauts est interprétée comme une coupe** : un long déplacement sans coupe apparaît aussi comme « coupe ». Pour vérifier une vraie coupe Ink/Stitch, rechercher le motif brut de 3 petits sauts a, −2a, a : (+2,+2) (−4,−4) (+2,+2) dans le repère de pystitch, soit (2,−2) (−4,4) (2,−2) dans les enregistrements bruts (axe vertical inversé) [ESSAI, test automatique].
- Fichiers réels (§17) : `ST` parfois décalé d'une unité selon que la marque de fin est comptée ; octets parasites après la fin → tolérer avec avertissement.

### 9.3 Grille de contrôle qualité
| # | Contrôle | Critère |
|---|---|---|
| 1 | Fichier lisible, se termine par END | Obligatoire |
| 2 | Nombre de vrais points | Rapporté (pas de seuil sourcé) |
| 3 | Point le plus long | ≤ 12,1 mm par axe (garanti) ; ≤ 7 mm pour satin/remplissage (non vérifié) |
| 4 | Points courts | Signaler < 1 mm, refuser < 0,3 mm |
| 5 | Coupes et sauts | Coupes = suites de ≥ 3 sauts ; cohérent avec le réglage machine |
| 6 | Changements de couleur | = nombre de blocs de couleur − 1 ; cohérent avec `CO` |
| 7 | Dimensions | `bounds()` / 10 = mm ; dans le champ du tambour avec marge |
| 8 | Cohérence en-tête / corps | `ST` = nombre d'enregistrements ; étendue = `bounds()` |

### 9.4 Visualiseurs gratuits
Ink/Stitch (import DST), Wilcom TrueSizer, et l'aperçu PNG généré par pyembroidery (sans interface).

---

## 10. Résultats des essais techniques

Environnement : Ubuntu 24.04, sans écran ; Ink/Stitch **v3.3.0** (commit `b0edd96`), inkex 1.4.1, pystitch 1.0.1, pyembroidery 1.5.1, shapely 2.2.0, Inkscape 1.2.2 (apt). Rapport complet, commandes et fichiers : `spikes/results/SPIKES_REPORT.md`.

| Essai | Objet | Résultat | Constat |
|---|---|---|---|
| 1 | Installation sans interface | **Réussi** | wx par apt (Python 3.12), inkex PyPI ; pas de module factice nécessaire |
| 1b | Paramètres v3.3.0 vs branche principale | **Identiques** | Aucun paramètre renommé ; balise de version = 4 dans les deux |
| 2 | Export d'un remplissage + point droit + satin | **Réussi** | 1897 points, 2 changements de couleur, dimensions exactes au 1/100 mm ; 9,4 s |
| 3 | Unité de l'étendue dans l'en-tête DST | **Tranché** | 0,1 mm |
| 4 | Export sans objet brodable | **Confirmé** | Code de sortie 0, fichier vide, message sur la sortie d'erreur |
| 5 | Balise de version absente | **Échec bloquant** | Sans écran : plantage ; avec écran virtuel : blocage infini. Aucun contournement en ligne de commande |
| 6 | Dégradés | **Partiel** | Coordonnées absolues : correct ; pourcentages : faux ; radial : noir |
| 7 | Opacité | **Confirmé** | Ignorée ; seul `fill-opacity:0` supprime |
| 8 | Masque de découpe avec transformation | **Réussi** | Appliqué sur l'élément et sur un groupe |
| 9 | Aperçus sans écran | **Réussi** | Aperçu SVG → PNG (rsvg-convert, cairosvg) ; PNG simples et réalistes via Inkscape 1.2.2 |
| 10 | Codage des coupes | **Confirmé** | 3 sauts (+2,+2) (−4,−4) (+2,+2) |

Options d'aperçu utiles : `--move-to-side=false` (sinon aperçu hors page), le dessin doit être dans un calque pour `--layer-visibility=hidden`.

---

## 11. Mesure des formes et classement automatique

Sources : [shapely — cercle inscrit maximal](https://shapely.readthedocs.io/en/stable/reference/shapely.maximum_inscribed_circle.html), [shapely — rectangle orienté](https://shapely.readthedocs.io/en/stable/reference/shapely.oriented_envelope.html), [scikit-image — morphologie](https://scikit-image.org/docs/stable/api/skimage.morphology.html), [scikit-image — regionprops](https://scikit-image.org/docs/stable/auto_examples/segmentation/plot_regionprops.html), [CGAL squelette droit](https://doc.cgal.org/6.1/Straight_skeleton_2/index.html), [brevet US 6 947 808](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6947808), [Ink/Stitch outils de trait](https://inkstitch.org/docs/stroke-tools/), [centerline](https://github.com/fitodic/centerline).

### 11.1 Mesures retenues (essais synthétiques de l'agent de recherche, scripts non archivés ; mesures reprises dans les tests automatiques du prototype)
| Mesure | Calcul | Comportement observé |
|---|---|---|
| **Largeur maximale** | 2 × rayon du cercle inscrit maximal (`shapely.maximum_inscribed_circle`) | Barre de 3 mm : 3,00 ; forme en L de 3 mm : 3,51 (gonflée aux angles) |
| **Largeur moyenne** | 2 × aire / périmètre (valable pour les formes allongées) | Barre : 2,79 ; colonne courbe de 3 mm : 2,87 |
| **Distribution des largeurs** | 2 × distance au bord le long du squelette (Voronoi élagué) | Médiane et 90ᵉ centile ; élagage des branches indispensable |
| **Allongement** | aire / largeur maximale² (≈ longueur / largeur) | Barre 13,3 ; colonne courbe 10,8 ; disque 0,8 |
| **Compacité** | 4π × aire / périmètre² | Disque 1,0 ; colonnes ≈ 0,2 |
| ✗ Rectangle orienté, `minimum_width` | — | **Faux sur les colonnes courbes** (13 mm pour une colonne de 3 mm) → à proscrire pour le satin |

### 11.2 Angle de remplissage
- Formes droites : grand côté du rectangle orienté.
- Méthode du brevet Soft Sight : tester 16 angles et retenir celui qui produit **le moins de fragments** (balayage par lignes parallèles).
- Ink/Stitch ne choisit pas l'angle automatiquement.

### 11.3 Classement : état de l'art
- **Ink/Stitch n'a pas de classeur automatique** : il avertit seulement (petit remplissage < 20 px² rendu en contour ; satin < 1 mm rendu en point droit).
- Brevet Soft Sight : forme « régulière » (→ satin) si 2σ < μ < ½·max de l'épaisseur mesurée sur le squelette ; sinon remplissage.
- Wilcom : satin ≤ 7 à 10 mm.
- Recherche (Liu *et al.* 2023 ; Chen *et al.*) : pas de règle de classement publiée.
- **Aucun numériseur automatique libre mature** (§16).

### 11.4 Jeu de règles proposé (seuils à étalonner)
> **Remplacé** par la table de `processus_broderie.md` §3.5 (version 1.0) : la condition de compacité excluait à tort les colonnes de rapport < 4 (revue critique §3.1) ; ajout des petites formes compactes, des filets en point droit et des formes mixtes. Conservé ici pour l'historique.

1. Largeur maximale < 1 mm **ou** aire < ≈ 1,5 mm² → **point droit** sur la ligne médiane.
2. Allongement ≥ 3, compacité < 0,5, largeur moyenne ≥ 1 mm et largeur (90ᵉ centile) ≤ 7 mm → **satin**.
3. Allongement ≥ 3 et largeur ≤ 10 mm → satin découpé **ou revue humaine**.
4. Sinon → **remplissage**, angle « moins de fragments ».
5. Tout objet proche d'un seuil ou à squelette anormal → **signalé**.
Seuils sourcés : 1 mm (Ink/Stitch), 7–10 mm (Wilcom). Les autres (3 ; 0,5 ; 1,5 mm²) sont des valeurs de départ.

### 11.5 Ligne médiane → satin
« Fill to Stroke » d'Ink/Stitch : densification → Voronoi → arêtes intérieures → fusion → élagage des bouts morts (< 10 mm par défaut) → simplification. Code GPL : **réutiliser la méthode, pas le code**. La génération des rails et barreaux à partir de la ligne médiane reste à concevoir.

---

## 12. Texte en satin

Sources : [Ink/Stitch outils satin](https://inkstitch.org/docs/satin-tools/#fill-to-satin), [colonne satin](https://inkstitch.org/docs/stitches/satin-column/), [tutoriel polices](https://inkstitch.org/tutorials/font-creation/), [outils polices](https://inkstitch.org/docs/font-tools/), [lettrage](https://inkstitch.org/docs/lettering/), [polices](https://inkstitch.org/docs/fonts), [notes v3.3.0](https://inkstitch.org/en/2026-07-31-v3.3.0), [EduTech — lettres](https://edutechwiki.unige.ch/en/InkStitch_-_design_letters), [forum Inkscape](https://inkscape.org/forums/embroidery/1-click-solution-to-convert-object-to-a-stain-stitch).

- **Aucune conversion automatique fiable** lettre vectorisée → satin. Toutes les voies exigent des barreaux, lignes de coupe ou rails tracés par un humain.
- Outils (tous appelables en ligne de commande, sélection par `--id=`) :

| Outil | Entrée | Limite |
|---|---|---|
| Fill to Satin | Remplissage + barreaux dessinés | « Semi-automatique » ; plantages signalés (#4530, #4561) |
| Fill to Stroke | Remplissage (+ lignes de coupe) | Ligne médiane avec éperons aux jonctions |
| Stroke to Satin | Trait simple | « Seules les lignes simples » |
| Trait large brodé en satin (nouveau v3.3.0) | Trait plus large que `min_satin_stroke_width_mm` (1 mm) | En dessous : point droit |
| Auto-route Satin, Cut, Flip | Satins existants | Ordonnancement seulement |

- **Voie semi-automatique proposée (non testée)** : ligne médiane (Fill to Stroke, lignes de coupe aux jonctions) → nettoyage → épaisseur = largeur + compensation → abaisser `min_satin_stroke_width_mm` → Auto-route Satin.
- **Polices intégrées** les plus petites : Glacial Tiny ≈ 2,8 mm, Ink/Stitch Small Font ≈ 3,6 mm, Caffeine tiny ≈ 4,0 mm (fil 60 wt et aiguille fine souvent exigés). Ne reproduisent pas un dessin de marque.
- **Police Ink/Stitch personnalisée** : un calque par lettre (`GlyphLayer-A`), un guide `baseline`, `font.json` (`size`, `min_scale`, `max_scale`, `kerning_pairs`…). Numérisation une seule fois, réutilisation à toutes les tailles admises. Lettrage scriptable : `--extension=batch_lettering`.
- **Remplissage** pour les lettres : « assez laid sauf pour de très grandes lettres ».
- Petits textes [SOURCE] : capitales seules sous 4 mm de hauteur.

---

## 13. Couleurs, nuanciers et fiche couleurs

Sources : [palettes Ink/Stitch](https://github.com/inkstitch/inkstitch/tree/main/palettes), [catalog.py](https://github.com/inkstitch/inkstitch/blob/main/lib/threads/catalog.py), [palette.py](https://github.com/inkstitch/inkstitch/blob/main/lib/threads/palette.py), [Ink/Stitch couleurs de fil](https://inkstitch.org/docs/thread-color/), [EmbThread.py](https://github.com/EmbroidePy/pyembroidery/blob/main/pyembroidery/EmbThread.py), [EduTech — nuanciers](https://edutechwiki.unige.ch/en/Embroidery_thread_color_and_chart), [Wilcom — nuanciers](https://help.wilcom.com/portal/en/kb/articles/thread-charts-color-index).

### 13.1 Données de couleurs de fils
- Ink/Stitch fournit **75 palettes** `.gpl` (format GIMP : `R G B  Nom Numéro`) : Madeira (Rayon, Polyneon, Burmilana, Matt), Isacord, Isafil, Isalon, Gunold, Robison-Anton, Brother, Brothread, Sulky, Mettler, Floriani, Marathon, DMC, RAL… Licence GPL-3 (celle du dépôt). **Origine des valeurs RVB non documentée.**
- Correspondance Ink/Stitch : sRVB → Lab → **CIE94, pondération textile (k_L = 2)** via colormath2. Détection automatique de palette si ≥ 80 % des couleurs correspondent exactement.
- pyembroidery : tables par format machine (PEC, JEF…), pas par marque ; distance RVB pondérée.
- Fabricants : nuanciers surtout en PDF (Sulky publie un tableau RVB en PDF/Excel). **Aucune donnée Lab officielle** trouvée.
- Les couleurs écran sont approximatives : contrôle sur nuancier physique indispensable.

### 13.2 Distance de couleur
- [colour-science](https://colour.readthedocs.io/en/master/_modules/colour/difference/delta_e.html) : CIE1976, CIE1994 et CIEDE2000 (option textile), CMC ; seuil JND CIE1976 = 2,3.
- [scikit-image](https://scikit-image.org/docs/stable/api/skimage.color.html) : `deltaE_ciede2000`, `deltaE_ciede94`, `deltaE_cmc` (CMC 2:1 = norme textile d'acceptabilité).
- [colormath2](https://github.com/pushfoo/python-colormath2) ([PyPI](https://pypi.org/project/colormath2/)).
- Validation : données de test CIEDE2000 de Sharma, Wu, Dalal 2005 ([article](https://hajim.rochester.edu/ece/sites/gsharma/papers/CIEDE2000CRNAFeb05.pdf), [données](https://www.ece.rochester.edu/~gsharma/ciede2000/)).
- JND CIEDE2000 ≈ 1 : non vérifié. L'imprécision des palettes domine le choix de la formule.

### 13.3 Réduction de palette
Quantification k-moyennes ([Celebi](https://arxiv.org/abs/1101.0395), [arXiv 2601.19117](https://arxiv.org/html/2601.19117v2)). Méthode proposée **non sourcée pour la broderie** : couleurs de marque figées ; échantillonnage des arrêts de dégradé pondéré par l'aire ; fusion sous ΔE00 ≈ 2–3 ; centres choisis **dans la palette de fils** ; écart résiduel signalé.

### 13.4 Fiche couleurs
- Wilcom ([fiches de production](https://help.wilcom.com/portal/en/kb/wilcom-international/wilcom-truesizer/finalize-designs/articles/production-worksheets), [exemple réel](https://abdigitizing.com/wp-content/uploads/2024/04/Floral-Swoosh-02-4x4-1.pdf), [séquences d'arrêt](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Production/reports/reports-14.htm)) : aperçu, nom, format, dimensions, nombre de points, changements de couleur, arrêts, coupes, longueurs min/max, point final, longueur de fil, et par arrêt : n°, code et nom du fil.
- Ink/Stitch PDF ([modèles](https://github.com/inkstitch/inkstitch/tree/main/print/templates)) : client, commande, dimensions, points, couleurs, blocs, arrêts, coupes, temps et fil estimés ; par bloc : fabricant, code, points.
- Liste des fils Ink/Stitch ([thread_list.py](https://github.com/inkstitch/inkstitch/blob/main/lib/extensions/thread_list.py), [zip.py](https://github.com/inkstitch/inkstitch/blob/main/lib/extensions/zip.py), [apply_threadlist.py](https://github.com/inkstitch/inkstitch/blob/main/lib/extensions/apply_threadlist.py)) : texte simple, **sans nombre de points par couleur**, ordre de la section « fils utilisés » instable.
- Tissu et entoilage absents des deux → à ajouter dans notre fiche.

---

## 14. Séquençage, origine, arrêts, coupes, tissus, tambours, essai

### 14.1 Ordre de broderie
- Arrière → avant, grandes surfaces d'abord, du centre vers l'extérieur, bordures et détails fins en dernier, pas de broderie vers une zone déjà fixée ([Mr X Stitch — pathing](https://www.mrxstitch.com/pathing/), [embroideres](https://forum.embroideres.com/articles.html/articles/embroidery-navigation-r212), [Wilcom](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Modifying/combine/combine-12.htm)).
- **Conflit ordre des calques / nombre de changements de couleur : la qualité l'emporte** ; accepter un changement de couleur supplémentaire plutôt que dégrader le repérage ([embroideres](https://forum.embroideres.com/articles.html/articles/embroidery-navigation-r212), [Ink/Stitch — routage](https://inkstitch.org/tutorials/routing/)).
- Ink/Stitch : ordre = panneau Objets ; outil de réempilement ([édition](https://inkstitch.org/docs/edit)) ; Auto-route satin avec ordre préservé ; points de départ/fin par commandes ([remplissage](https://inkstitch.org/docs/stitches/fill-stitch/)).

### 14.2 Origine et centrage
- Ink/Stitch : origine par défaut = **centre de la boîte englobante** ; commandes « origin » et « stop position » ([commandes](https://inkstitch.org/docs/commands/)).
- Bonne pratique : départ et fin au centre ([Melco](https://melco.zendesk.com/hc/en-us/articles/360004994672-Centering-Designs)) ; casquettes : départ en bas au centre ([Wilcom](https://wilcom.com/resources/blog/auto-start-end)).
- Tajima : la position où l'opérateur lance le traçage devient le point de départ ([manuel TEJT-II](https://www.silmaq.com.br/wp-content/uploads/downloads/MANUAIS/TAJIMA/Manual%20de%20Instru%C3%A7%C3%A3o/tejtii-c-m-ic2-11-e-2014-04.pdf)) ; certaines machines centrent d'office ([Wilcom](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Production/hoops/hoops-10.htm)).

### 14.3 Points d'arrêt (nœuds)
- Pratique : nœud de fin avant chaque coupe ou changement de couleur, nœud de départ après ([Wilcom fin](https://docs.wilcom.com/embroiderystudio/27/en/OnlineHelp/Quality/connectors/connectors-7.htm), [Wilcom départ](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Quality/connectors/connectors-6.htm)).
- Ink/Stitch : `ties=0` (avant et après), `lock_start`/`lock_end=half_stitch`, ajoutés si le saut dépasse `collapse_len_mm` = 3 mm ([nœuds](https://inkstitch.org/docs/stitches/lock-stitches/)). **Défauts suffisants pour démarrer.**

### 14.4 Coupes : réglage machine
- Ink/Stitch écrit **3 sauts** par coupe [ESSAI].
- Brother PR : 3 sauts en sortie d'usine ([manuel PR650e](https://www.manualslib.com/manual/976950/Brother-Pr650e.html?page=201)).
- Tajima : réglage « JUMP CONV » modifiable (3 et 5 apparaissent dans le manuel) ; valeur d'usine non vérifiée.
- Barudan, SWF, Melco : non vérifié.
- **Incohérence = longs fils au lieu de coupes** ([artapli](https://artapli.shop/blogs/embroidery-technical-reference/why-dst-files-create-long-jump-threads-on-commercial-embroidery-machines)) → réglage à confirmer par machine.

### 14.5 Profils de tissus
| Tissu | Ajustement (Wilcom) |
|---|---|
| Maille extensible | + compensation, sous-couche zigzag supplémentaire, densité un peu réduite |
| Piqué | + sous-couche bord et zigzag, densité un peu plus lâche |
| Sergé épais | densité réduite, compensation minimale, points plus longs |
| Polaire | espacement plus large, sous-couche lourde, + compensation |
| Casquette structurée | densité plus serrée, sous-couche bord forte, + nœuds |
| Éponge | sous-couche bord + double zigzag, densité plus forte, film soluble dessus |

Sources : [Wilcom properties-9](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Digitizing/properties/properties-9.htm) (lu via un outil de résumé, à relire), [Wilcom properties-12](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Digitizing/properties/properties-12.htm).
- Compensation de traction de départ (**par côté**, confirmé par Wilcom) : coutil/coton 0,20 mm ; tee-shirt 0,35 mm ; polaire/pull 0,40 mm ; lettrage 0,2–0,3 mm ([Wilcom](https://docs.wilcom.com/embroiderystudio/26/en/OnlineHelp/Quality/underlays/Apply_automatic_pull_compensation.htm)).
- Fil 40 wt : dessus rarement plus dense que 0,40 mm ; sous-couche 3–4 mm, retrait ≥ 0,4 mm ; ouvertures < 0,8–1,0 mm se bouchent ([Impressions](https://impressionsmagazine.com/process-technique/preventing-embroidery-digitizing-disasters-part-2preventing-embroidery-digitizing-disasters-lettering-density-underlay-problems/169753/)).
- ~~Défaut Ink/Stitch (0,25 mm) plus dense que la pratique (0,40 mm) → à surcharger~~ : **erreur de convention, retirée** (revue critique §5.1). Le « 0,40 mm » professionnel se mesure un rang sur deux ; le défaut d'Ink/Stitch (0,25 mm entre rangs voisins) est dans la bonne plage.
- Entoilage : découpable pour les mailles ; déchirable pour tissés solides, casquettes, serviettes ; film soluble dessus sur éponge et polaire ([Melco](https://melco.com/selecting-stabilizer-backing-for-embroidery/)).
- Écussons : non vérifié.

### 14.6 Tambours et champs de broderie
- Tajima TMEZ-SC : cadre 360 × 500 mm ; tubulaire 335 × 453 mm ; casquette large 75 × 360 mm ([TMEZ-SC](https://www.tajima.com/product/tmez-sc/), [TMBP2-SC](https://www.tajima.com/product/tmbp2-sc/)).
- Tambours ronds 9, 12, 15, 18, 21 cm ([HoopMaster](https://hoopmaster.com/support/hoop-identifier), [AllStitch](https://allstitch.com/collections/embroidery-hoops-for-tajima-and-compatible-embroidery-machines)).
- Marge ≈ 13 mm du bord intérieur ([RBD](https://www.rbdblog.com/?p=22815), non vérifié pour Tajima).
- Casquettes : hauteur sûre = visière → début de courbure − 1 pouce ; broder du bas vers le haut, du centre vers l'extérieur ([Melco](https://melco-service.com/source1/Digitizing_for_Caps.htm)).

### 14.7 Essai sur tissu
- Protocole d'un prestataire ([digitizing.us](https://digitizing.us/howwetest/)) : revue (petits textes, couleurs, densité), broderie sur le vrai tissu, observation tension / repérage / coupes, numérisation de l'échantillon comme épreuve.
- Observer la déformation pendant la broderie ; augmenter la compensation si les satins sortent étroits ([Impressions](https://impressionsmagazine.com/process-technique/preventing-embroidery-digitizing-disasters-part-2preventing-embroidery-digitizing-disasters-lettering-density-underlay-problems/169753/)).
- **Aucune tolérance chiffrée publiée** → grille maison : repérage, rétrécissement, fronces, couverture, lisibilité, points et durée.

---

## 15. Format « tajma.tds », TBF, licence, fonctionnalités SVG

### 15.1 Formats
- `.TDS` : Adobe LiveCycle Designer et Borland Turbo Debugger uniquement ([fileinfo](https://fileinfo.com/extension/tds)) → **« tajma.tds » ≈ Tajima .DST**.
- Famille Tajima : DST ; DSB (Barudan) et DSZ (ZSK) à en-tête DST ; T01 et TAP sans en-tête ([EduTech](https://edutechwiki.unige.ch/en/Embroidery_format)) ; TBF ([Wilcom](https://docs.wilcom.com/embroiderystudio/e4/fr/MainHelp/Chenille/chenille_basics/Standard_machine_formats.htm)).

### 15.2 TBF
- Apports : commande d'aiguille à chaque changement, champ `DO:` (ordre des aiguilles), champ `DA:` (liste RVB des fils), coupes explicites ([TbfWriter.py](https://raw.githubusercontent.com/EmbroidePy/pyembroidery/main/pyembroidery/TbfWriter.py)) ; ≤ 256 changements ([Wilcom](https://docs.wilcom.com/embroiderystudio/e4/en/MainHelp/New_features/rn_-_update-4/TBF_machine_file_issues.htm)) ; [comparatif](https://embroideryhoopstore.com/blogs/articles/tajima-tbf-vs-dst-pick-the-right-file-format-and-stop-losing-time-on-the-shop-floor).
- Usage : machines Tajima chenille et paillettes ([Wilcom paillettes](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Mixed/sequin_basics/sequin_basics-4.htm)) ; Tajima standard : DST suffit.
- Écrivains : Wilcom ; **pyembroidery et pystitch (MIT)** ([README pyembroidery](https://raw.githubusercontent.com/EmbroidePy/pyembroidery/main/README.md), [README pystitch](https://raw.githubusercontent.com/inkstitch/pystitch/main/README.md)).

### 15.3 Licence (lecture de la FSF, pas un avis juridique)
Licences : Ink/Stitch GPL-3.0 ou ultérieure ([LICENSE](https://github.com/inkstitch/inkstitch/blob/main/LICENSE)) ; pyembroidery MIT ([LICENSE](https://raw.githubusercontent.com/EmbroidePy/pyembroidery/main/LICENSE)) ; pystitch MIT ([LICENSE](https://raw.githubusercontent.com/inkstitch/pystitch/main/LICENSE)). Réf. : [FAQ GPL](https://www.gnu.org/licenses/gpl-faq).

| Usage | Obligation |
|---|---|
| Appel d'Ink/Stitch comme **programme séparé** | Aucune sur nos scripts ; si on distribue Ink/Stitch avec, fournir ses sources et sa licence |
| **Import** de modules Ink/Stitch | Programme combiné → GPL-3.0 **à la distribution** |
| Génération de SVG lus par Ink/Stitch | Aucune |
| Usage interne, service en ligne | Pas de distribution (Ink/Stitch n'est pas AGPL) |
| Fichiers de broderie produits | Non couverts par la GPL ; appartiennent au propriétaire du dessin (réserve : polices intégrées) |

**Recommandation : appel en programme séparé, code propre.**

### 15.4 Fonctionnalités SVG dans Ink/Stitch
| Fonction | Traitement |
|---|---|
| Styles CSS, `<style>` | Pris en charge |
| Transformations imbriquées | Prises en charge |
| Clones `<use>`, `<symbol>` | Pris en charge ([clones](https://inkstitch.org/docs/stitches/clone/)) |
| `clip-path` | Appliqué [ESSAI] |
| Masques | **Ignorés en silence** |
| Filtres | **Ignorés en silence** |
| Marqueurs ordinaires | **Ignorés** |
| Pointillés | Sans effet sur la broderie |
| Motifs (`pattern`) | Non vérifié |
| Dégradés | Voir §6.3 [ESSAI] |
| Opacité | Ignorée [ESSAI] |
→ Notre préparation doit aplatir ou refuser masques, filtres, marqueurs, motifs, et le signaler.

---

## 16. Retours d'expérience et pipelines existants

### 16.1 Pipelines automatisés
| Projet | Méthode | Gestion de wx / écran |
|---|---|---|
| [InkStitchMCP](https://github.com/GreerBK/InkStitchMCP) ([runner](https://github.com/GreerBK/InkStitchMCP/blob/main/src/inkstitch_mcp/runner.py)) | Sources, inkex épinglé | Contrôle préalable du dialogue de mise à jour |
| [cli-anything-inkstitch](https://github.com/bobbymarko/cli-anything-inkstitch) ([SPEC](https://github.com/bobbymarko/cli-anything-inkstitch/blob/main/SPEC.md)) | Attributs posés par lxml, binaire en sous-processus | Balise de version écrite systématiquement |
| [stitchcraft](https://github.com/KaboomFox/stitchcraft) ([differential.rs](https://github.com/KaboomFox/stitchcraft/blob/main/xtask/src/conformance/differential.rs), [pin.toml](https://github.com/KaboomFox/stitchcraft/blob/main/conformance/inkstitch/pin.toml), [module wx factice](https://github.com/KaboomFox/stitchcraft/blob/main/conformance/inkstitch/stubs/wx/__init__.py), [action CI](https://github.com/KaboomFox/stitchcraft/blob/main/.github/actions/inkstitch/action.yml)) | Référence en CI nocturne | **Module `wx` factice**, aucun écran |
| [Jawetzel](https://github.com/jawetzel/Jawetzel/blob/main/worker/Dockerfile) | v3.2.2 sources | wx Debian + écran virtuel |
| [rodrigozago](https://github.com/rodrigozago/bit-lab-contabo/blob/main/ponto-studio/workers/embroidery/Dockerfile) ([runner](https://github.com/rodrigozago/bit-lab-contabo/blob/main/ponto-studio/workers/embroidery/inkstitch_runner.py)) | Binaire sous écran virtuel | Séparé exprès pour la frontière GPL |
| [OpenMates](https://github.com/glowingkitty/OpenMates/blob/main/backend/scripts/build_embroidery_template.py) | v3.3.0 vérifiée par empreinte | Bibliothèques GTK |
| [pic-to-patch](https://github.com/maxwofford/pic-to-patch/blob/main/Dockerfile.worker) | Image → vtracer → Ink/Stitch | Non vérifié |
| [Stitch-Forge CI](https://github.com/sapiverpress-studio/Stitch-Forge/blob/main/.github/workflows/real-engine-smoke.yml) | Test de fumée | Écran virtuel |
| [inkstitch-lib](https://github.com/jlyon1/inkstitch-lib/blob/main/Dockerfile.api) | Fork importé | wx retiré, inkex sans dépendances |
| [InkstitchPipeline](https://github.com/DavidSchoenholz/InkstitchPipeline) | Photo → vtracer → Ink/Stitch | Windows |

**Leçons** : blocage silencieux sans balise de version (trouvé au débogueur) ; code de sortie non fiable ; fichier de débogage susceptible de bloquer ; journalisation désactivée : 10 s → 1,6 s à sortie identique ; **cache de plans de broderie qui fuit d'un fichier à l'autre** → `XDG_CONFIG_HOME` privé ; `PYTHONUTF8=1`, `LANGUAGE=en_US` ; dessins denses > 15 min ; un appel à la fois.

Générateurs DST directs : [pystitch](https://github.com/inkstitch/pystitch), [stitch_generator](https://github.com/bastanja/stitch_generator), [TurtleThread](https://github.com/TurtleThread/TurtleThread), [Hedy](https://github.com/hedyorg/hedy/blob/main/app.py), [vpype-embroidery](https://github.com/EmbroidePy/vpype-embroidery), [PEmbroider](https://github.com/CreativeInquiry/PEmbroider), [TurtleStitch](https://github.com/backface/turtlestitch), [embroidery-streamlines](https://github.com/desmondlzy/embroidery-streamlines), [bytes-to-bobbins-talk](https://github.com/kantoniak/bytes-to-bobbins-talk) ; [autodigitization](https://github.com/kenny240tech/autodigitization) (vide). **Aucun numériseur automatique libre mature.**

### 16.2 Retours d'utilisateurs [ANECDOTE sauf mention]
- **Lecture des DST sur machines Tajima : tickets ouverts** (seuls les **titres** ont été lus ; corps non accessibles — risque **à vérifier**, et non « risque principal » établi) — [#2388](https://github.com/inkstitch/inkstitch/issues/2388) (DST non lu), [#2673](https://github.com/inkstitch/inkstitch/issues/2673), [#3544](https://github.com/inkstitch/inkstitch/issues/3544) (arrêts inopérants), [#1296](https://github.com/inkstitch/inkstitch/issues/1296), [#4260](https://github.com/inkstitch/inkstitch/issues/4260), [#3923](https://github.com/inkstitch/inkstitch/issues/3923) (fermé). **Risque principal.**
- Coupes non exécutées : seuil de la machine, pas le fichier ([forum](https://inkscape.org/forums/embroidery/command-to-stopcut-stitch-not-working-between-letters)) ; certaines machines ignorent les coupes ([forum](https://inkscape.org/hu/forums/embroidery/trim-jump-stitches)) ; arrêt = changement de couleur supplémentaire ([commandes](https://www.inkstitch.org/docs/commands/)).
- Petit texte sur remplissage : rester dans la plage de la police, ne pas évider le remplissage, supprimer la sous-couche du texte, fil fin ([forum](https://inkscape.org/forums/embroidery/techniques-for-making-text-on-top-of-a-fill-more-crisp)).
- Compensation uniquement par objet, 0,15–0,4 mm, toujours valider sur tissu ([forum](https://inkscape.org/forums/embroidery/global-parameters-for-shrink-compensation_QLAQ1)).
- Densité et aiguilles cassées ; zigzag ≥ 0,4 mm ; contour qui se croise = remplissage invalide ([wiki makerspace](https://sites.google.com/view/makerlabsinternalwiki/education/cnc-embroidery-101), [Happylab](https://www.happylab.at/en/news/ink-stitch)).
- Fond + trait sur un même objet = changement de couleur en plus ; PES ≤ 255 changements [SOURCE] ([FAQ](https://inkstitch.org/docs/faq/)).
- Aiguille 75/11, fil 60 wt conseillé ([Coastal Carolina](https://libraries.coastal.edu/makerspace/embroidery)).
- Comparaison avec Wilcom/Hatch : opinions de 2018 seulement ([Seamly](https://forum.seamly.io/t/inkstitch-embroidery-software/3130)) ; courbe d'apprentissage raisonnable pour qui connaît le vectoriel ([SaaSHub](https://www.saashub.com/ink-stitch-reviews)) ; ≈ 2 h de préparation pour un motif à 10 couleurs (Happylab).

---

## 17. Fichiers DST d'exemple

Dossier local `samples_dst/` ; inventaire `samples_dst/INVENTORY.md` ; lecteur d'en-tête `tools/read_dst_header.py`.

| Fichier | Source et licence | En-tête | Usage |
|---|---|---|---|
| Star.DST | [Embroidermodder](https://github.com/Embroidermodder/Embroidermodder) (commit `537c9dd`), zlib | ST 2567, CO 1, 59 × 62 mm | Tests du lecteur |
| Embroidermodder.DST | idem | ST 3487 (3488 enregistrements), CO 0, 222 × 51 mm ; les « 12 suites de sauts » sont des **déplacements longs, pas des coupes** (0 coupe au motif brut) | Test de lecture des déplacements |
| shamrockin.dst | idem | ST 1477, CO 0, 50 × 49 mm, octets parasites | Tests de tolérance |

Avertissement amont : fichiers « possiblement invalides » → cas de test uniquement.

**Recherche des dessins d'origine (16/11/2026)** — rendu des DST et fouille du dépôt Embroidermodder (commit `537c9dd`) :

| Fichier | Contenu réel (rendu) | Ce qui existe en amont | Dessin d'origine ? |
|---|---|---|---|
| Star.DST | Étoile : remplissage tatami + bordure satin, 2 couleurs | Fichiers maîtres de numérisation `test/Star.EMB` (Wilcom) et `test/Star.PXF` (Pulse), propriétaires ; ~50 conversions du même dessin (PES, JEF, TBF…) ; couleurs selon PES : rouge `#ed171f` + blanc `#f0f0f0`, selon JEF : orange brûlé + ivoire (palettes de format incohérentes) | **Non** (pas de vectoriel) |
| Embroidermodder.DST | Mot « Embroidermodder » en arc, satin, 1 couleur (PES : bleu de Prusse) | `test/Embroidermodder.DXF` : 189 polylignes = **contours des colonnes satin** (dérivé de la broderie, pas une illustration) ; `test/Embroidermodder.pxf` (Pulse) ; `data/samples/Embroidermodder-R2000.dxf` = logo du projet, **autre lettrage**, sans rapport | **Non** (seulement un dérivé) |
| shamrockin.dst | Contour de trèfle en satin seul, sans remplissage | `data/samples/shamrockin.rgb` : 4 octets `00 ff 00 00` (probablement une seule couleur verte) ; aucune trace en ligne (recherche web : seulement des trèfles commerciaux sans rapport) | **Non** |

Conséquence : ces fichiers ne fournissent **aucune paire dessin d'entrée → DST** pour tester notre chaîne. Sources de paires possibles : échantillons SVG d'Ink/Stitch (dessins paramétrés), ou reconstruction d'un vectoriel à partir du rendu des DST.
Références de qualité (téléchargement manuel, usage local) : [Madeira UK](https://www.madeira.co.uk/dstfiles/) (« gratuit pour usage commercial et domestique », sans licence formelle), [Madeira USA](https://www.madeirausa.com/resources/free-embroidery-design-downloads/), [Æthelmearc](https://aeans.aethelmearc.org/machine-embroidery-files/). Non retenus : [free-embroidery-files.com](https://free-embroidery-files.com/faq/) (usage personnel), [Emoji Embroidery Project](https://edutechwiki.unige.ch/en/Emoji_Embroidery_Project) (licences contradictoires). Échantillons Ink/Stitch ([page](https://inkstitch.org/tutorials/resources/samples)) : SVG uniquement, licence du site non trouvée.

---

## 18. Références (liste exhaustive)

Toutes les sources consultées au cours de l'étude, regroupées par thème. Les liens cités dans le corps du document y figurent tous.

### 18.1 Ink/Stitch — documentation officielle
- Fonctionnalités : https://inkstitch.org/features
- Installation Linux (et annonce v3.3.0) : https://inkstitch.org/docs/install-linux/
- Ligne de commande : https://inkstitch.org/docs/command-line
- Installation manuelle (développeurs) : https://inkstitch.org/developers/inkstitch/manual-setup/
- Formats de fichiers : https://inkstitch.org/docs/file-formats
- Préférences : https://inkstitch.org/docs/preferences/
- Flux de travail : https://inkstitch.org/docs/workflow/
- Visualisation (simulateur, aperçu, carte de densité) : https://inkstitch.org/docs/visualize/
- Dépannage : https://inkstitch.org/docs/troubleshoot/
- Commandes : https://inkstitch.org/docs/commands/
- Point de remplissage : https://inkstitch.org/docs/stitches/fill-stitch/
- Remplissage en contour : https://inkstitch.org/docs/stitches/contour-fill/
- Remplissage guidé : https://inkstitch.org/docs/stitches/guided-fill/
- Remplissage méandre : https://inkstitch.org/docs/stitches/meander-fill/
- Remplissage circulaire : https://inkstitch.org/docs/stitches/circular-fill/
- Remplissage en dégradé linéaire : https://inkstitch.org/docs/stitches/linear-gradient-fill/
- Remplissage tartan : https://inkstitch.org/docs/stitches/tartan-fill/
- Point droit : https://inkstitch.org/docs/stitches/running-stitch/
- Colonne satin : https://inkstitch.org/docs/stitches/satin-column/
- Outils satin : https://inkstitch.org/docs/satin-tools/
- Outils de remplissage : https://inkstitch.org/docs/fill-tools/
- Lettrage : https://inkstitch.org/docs/lettering/
- Police « Ink/Stitch Small Font » : https://inkstitch.org/fonts/ink_stitch/
- Tutoriel mélange de couleurs : https://inkstitch.org/tutorials/color-blending/
- Tutoriel sous-couches : https://inkstitch.org/tutorials/underlay/
- Tutoriel vidéo débutant — types de points : https://inkstitch.org/tutorials/resources/beginner-video-tutorials/04-stitch-types-transcript

### 18.2 Ink/Stitch — code source et communauté
- Dépôt principal : https://github.com/inkstitch/inkstitch
  (fichiers lus : `inkstitch.py`, `lib/svg/tags.py`, `lib/svg/path.py`, `lib/svg/units.py`, `lib/elements/element.py`, `lib/elements/fill_stitch.py`, `lib/elements/stroke.py`, `lib/elements/satin_column/satin_column.py`, `lib/elements/utils/nodes.py`, `lib/stitch_plan/stitch_plan.py`, `lib/output.py`, `lib/commands.py`, `lib/metadata.py`, `lib/utils/settings.py`, `lib/update.py`, `lib/extensions/__init__.py`, `lib/extensions/output.py`, `lib/extensions/zip.py`, `lib/extensions/utils/inkex_command.py`, `lib/inx/utils.py`, `requirements.txt`, `pyproject.toml` — branche `main`, commit `42e771e`, 3 novembre 2026)
- Miroir (export DST) : https://git.push-f.com/inkstitch/tree/lib/output.py?h=nix
- Forum Inkscape — paramètres via `--actions` : https://inkscape.org/forums/embroidery/passing-arguments-in-inkscape-cli-actions-orginkstitchstitch-plan-preview
- EduTech Wiki — remplissages programmables : https://edutechwiki.unige.ch/en/InkStitch_-_fills_with_programmable_stitches
- EduTech Wiki — dessiner des lettres : https://edutechwiki.unige.ch/en/InkStitch_-_design_letters
- Présentation (makerspace) : https://sites.google.com/view/inkstitchmakerspace/about-inkstitch
- Présentations tierces : https://sourceforge.net/mirror/ink-stitch/ , https://www.linuxlinks.com/ink-stitch-machine-embroidery-design-platform-inkscape/ , https://toolfox.ru/services/s/inkstitch , https://w.arbores.tech/wiki/InkStitch
- Comparatif logiciels DST : https://gitnux.org/best/dst-file-embroidery-software/
- Logiciels gratuits : https://printify.com/knowledge-hub/free-embroidery-digitizing-software/

### 18.3 Bibliothèques Python et format DST
- pyembroidery (dépôt) : https://github.com/EmbroidePy/pyembroidery
- pyembroidery (PyPI) : https://pypi.org/project/pyembroidery/
- pyembroidery (résumé d'API) : https://context7.com/embroidepy/pyembroidery/llms.txt
- pystitch (PyPI) : https://pypi.org/project/pystitch/
- EduTech Wiki — format DST : https://edutechwiki.unige.ch/en/Embroidery_format_DST
- EduTech Wiki — formats de broderie : https://edutechwiki.unige.ch/en/Embroidery_format
- KDE Liberty — Tajima Ternary : https://community.kde.org/Projects/Liberty/File_Formats/Tajima_Ternary
- Wilcom — réglages machines (12,1 mm) : https://docs.wilcom.com/embroiderystudio/27/en/OnlineHelp/Setup/machines/machines-3.htm
- Embrilliance — préférences de conversion DST : https://embrilliance.zendesk.com/hc/en-us/articles/360052392074-DST-Conversion-Preferences
- Melco — points trop courts : https://melco-service.com/source1/Stitches_Too_Small.htm

### 18.4 Formats de fichiers (généralités)
- Wilcom — formats Tajima (DST, TBF, T01) : https://wilcom.com/tajima
- Filestar — TBF vs DST : https://filestar.com/skills/tbf/convert-tbf-to-dst
- Filext — PXF : https://filext.com/file-extension/PXF
- Forum Pulse — sortie PXF / DST : https://community.pulsemicro.com/topic2242-dg-template-function--output-file-format.aspx?lastpage=1 , https://community.pulsemicro.com/topic2324-mass-dst-files.aspx , https://community.pulsemicro.com/topic84-changing-a-bunch-of-pxf-files-into-dst.aspx
- Bighorn Threads — formats : https://bighorn-threads.pages.dev/blog/embroidery-file-formats-explained/
- Zdigitizing — qu'est-ce qu'un DST : https://zdigitizing.com/what-is-a-dst-file/
- Hooptalent — DST : https://www.hooptalent.com/blogs/news/mastering-dst-embroidery-files-creation-conversion-and-machine-optimization
- Hooptalent — formats 2025 : https://www.hooptalent.com/blogs/news/embroidery-file-formats-demystified-2025-guide-to-compatibility-conversion-best-practices
- Dynamic Mockups — DST : https://dynamicmockups.com/?p=58815
- StitchPilot — formats : https://stitchpilot-frontend.pages.dev/embroidery-file-formats
- StitchPilot — PES vs DST : https://stitchpilot-frontend.pages.dev/guides/pes-vs-dst
- Magnetic Hoop — DST : https://www.magnetichoop.com/blogs/news/mastering-dst-files-essential-guide-to-creation-conversion-and-embroidery-success
- Magnetic Hoop — créer un DST : https://www.magnetichoop.com/blogs/news/how-to-make-a-dst-file-a-step-by-step-guide-for-flawless-embroidery
- Embroidery Hooping — guide DST : https://embroideryhooping.com/blogs/articles/the-ultimate-guide-to-dst-files-for-embroidery-creation-conversion-and-compatibility

### 18.5 Wilcom et flux de numérisation
- Wilcom Quick Reference (EmbroideryStudio) : https://docs.wilcom.com/embroiderystudio/28/en/downloads/QuickReference.pdf
- Wilcom — dégradés (e4) : https://legacy.wilcom.com/Help/e4/es/en/MainHelp/Decorative/specialty/Gradient_stitching.htm
- Wilcom — dégradés (v27) : https://docs.wilcom.com/embroiderystudio/27/en/OnlineHelp/Decorative/specialty/specialty-15.htm
- Wilcom — suppression des points cachés : https://docs.wilcom.com/embroiderystudio/e4/en/MainHelp/Quality/quality/Removing_underlying_stitching.htm
- Wilcom — solutions professionnelles : https://wilcom.com/Solu%C3%A7%C3%B5es/Profissional.aspx
- Hatch — offre professionnelle : https://hatchembroidery.com/business
- Hatch — découpes (knockout) : https://hatchembroidery.com/resources/blog/create-knockout-designs-with-hatch-embroidery
- Test de précision SVG → DST (Pulse, Wilcom, Chroma, DesignShop) : https://embroideryhooping.com/blogs/articles/the-hidden-0-1-mm-shift-testing-svg-import-and-dst-output-accuracy-in-pulse-wilcom-chroma-and-designshop
- Auto-numérisation Wilcom : https://embroideryhoopstore.com/blogs/articles/auto-digitizing-a-logo-in-wilcom-embroidery-studio-the-fast-emb-dst-jef-workflow-and-the-quality-traps-to-avoid
- Wilcom e4.2 depuis CorelDRAW : https://hoopingstation.com/nl/blogs/articles/from-coreldraw-cdr-to-clean-stitches-in-wilcom-embroiderystudio-e4-2-the-conversion-workflow-that-won-t-bite-you-later
- Wilcom e4 — import d'un logo : https://hoopingstation.com/blogs/articles/wilcom-embroiderystudio-e4-import-a-logo-the-right-way-so-auto-digitizing-doesn-t-embarrass-you
- Wilcom TrueSizer : https://embroideryhooping.com/blogs/articles/wilcom-truesizer-embroidery-file-conversion
- Swing Design — logiciels : https://www.swingdesign.com/collections/embroidery-digitizing-design-software
- Hoopingstation — logos DST professionnels : https://hoopingstation.com/blogs/news/the-ultimate-guide-to-creating-professional-dst-logo-files
- Hoopingstation — choisir un logiciel : https://hoopingstation.com/blogs/news/embroidery-software-digitizing-ultimate-guide-to-choosing-using-and-mastering-top-tools
- Maggie Frames — numériser : https://www.maggieframes.com/nl/blogs/embroidery-blogs/how-to-digitize-embroidery-designs-master-software-techniques-for-flawless-results
- Maggie Frames — graphismes pour broderie : https://www.maggieframes.com/es/blogs/embroidery-blogs/graphics-for-embroidery-your-complete-digitizing-guide
- Maggie Frames — formats numérisés : https://www.maggieframes.com/blogs/embroidery-blogs/digitized-format-mastery-the-complete-guide-to-machine-embroidery-files
- Maggie Frame Store — créer un fichier : https://maggieframestore.com/blogs/maggieframe-news/how-to-create-an-embroidery-file-master-digitization-for-flawless-stitching
- Maggie Frame Store — guide DST : https://maggieframestore.com/blogs/maggieframe-news/the-complete-guide-to-dst-files-for-embroidery-creation-conversion-optimization
- Maggie Frame Store — logiciels libres : https://maggieframestore.com/blogs/maggieframe-news/open-source-embroidery-software-the-ultimate-guide-to-features-comparisons-and-getting-started
- Zdigitizing — SVG vers broderie : https://zdigitizing.com/how-to-convert-svg-to-embroidery-file/
- TrueDigitizing — SVG est-il un DST : https://www.truedigitizing.com/blog/is-svg-a-dst-file
- TrueDigitizing — convertir un SVG : https://www.truedigitizing.com/blog/convert-svg-to-embroidery-file
- StitchBase — SVG vers broderie : https://stitchbase.vercel.app/blog/how-to-convert-svg-to-embroidery-file
- Embroidery Hoop Store — numérisation gratuite : https://embroideryhoopstore.com/blogs/articles/master-free-embroidery-digitizing-top-software-expert-techniques

### 18.6 Contraintes physiques, texte et densité
- Made Good Designs — limites de conception : https://madegooddesigns.com/embroidery-design/
- PIWorld — lettres (hauteurs, colonnes) : https://www.piworld.com/embroidery-digitizing-tips-on-creating-designs-with-letters/all
- Wilcom — 10 conseils logo (PDF) : https://www.vitordigitizing.net/uploads/1/1/0/6/11065424/10_tips_to_get_the_best_embroidery_logo_results_by_wilcom.pdf
- ASI — petites lettres nettes : https://members.asicentral.com/news/how-to/may-2018/keep-your-small-letters-crisp/
- Impressions — petits lettrages : https://impressionsmagazine.com/how-to-digitize-small-lettering/
- Mr X Stitch — compensation de traction : https://www.mrxstitch.com/pull-compensation/
- Supply Crew — texte minimal : https://go.supplycrew.com.au/resource-centre/what-is-the-smallest-size-text-can-be-embroidered
- Rush Order Tees — logo pour broderie : https://www.rushordertees.com/blog/how-to-design-a-logo-for-embroidery
- Printful — logo pour broderie : https://www.printful.com/blog/how-to-design-a-logo-for-embroidery
- Inkthreadable — designs premium : https://help.inkthreadable.co.uk/en/articles/6541709-how-to-create-premium-embroidery-designs
- Hoopingstation — poitrine gauche : https://hoopingstation.com/blogs/news/mastering-left-chest-embroidery-sizes-and-placement
- AB Digitizing — texte < 5 mm : https://abdigitizing.com/how-to-digitize-small-text-for-embroidery-under-5mm-without-messing-up/
- Pack for Camp — casquettes : https://packforcamp.com/pages/custom-embroidered-hats-the-guide-to-creating-an-embroidery-design
- Maggie Frame Store — casquettes : https://maggieframestore.com/blogs/maggieframe-news/hat-logo-size-chart-optimal-dimensions-and-placement-for-professional-embroidery
- EmbDesignTube — petits textes : https://stagingg.embdesigntube.com/en-gb/blog/why-customer-logos-dont-sew-clean-how-to-digitize-small-text-perfectly
- Embroidery Hoop Store — petites polices : https://embroideryhoopstore.com/blogs/articles/stop-shrinking-fonts-crisp-small-lettering-in-stitch-sew-2-0-for-happy-embroidery-machine-jobs
- Exclaim — exigences logo : https://exclaim.gg/guide/logo-requirements/embroidery
- Lead Apparel — tailles : https://leadapparel.com/pages/recommended-logo-sizing-and-placement

### 18.7 Dégradés
- Printful — broderie en dégradé : https://www.printful.com/blog/gradient-embroidery
- Graphics Pro — dégradés au fil : https://graphics-pro.com/?p=95632
- Embroidery Hooping — dégradé poitrine gauche : https://embroideryhooping.com/blogs/articles/digitizing-a-clean-gradient-fill-for-a-3-25-left-chest-logo-without-sloppy-edges
- Embroidery Hooping — dégradé Hatch : https://embroideryhooping.com/blogs/articles/hatch-digitize-blocks-gradient-fill-the-seahorse-shading-workflow-that-won-t-stitch-bullet-proof
- Janome — remplissage dégradé : https://janome.com/learn/software-lessons/digitizer-pro-mb/gradient-fill
- OML Embroidery — dégradés : https://omlembroidery.com/gradient-fills/

---

### 18.8 Mesure des formes et numérisation automatique
- shapely — cercle inscrit maximal : https://shapely.readthedocs.io/en/stable/reference/shapely.maximum_inscribed_circle.html
- shapely — rectangle orienté : https://shapely.readthedocs.io/en/stable/reference/shapely.oriented_envelope.html
- scikit-image — morphologie (axe médian) : https://scikit-image.org/docs/stable/api/skimage.morphology.html
- scikit-image — regionprops : https://scikit-image.org/docs/stable/auto_examples/segmentation/plot_regionprops.html
- CGAL — squelette droit : https://doc.cgal.org/6.1/Straight_skeleton_2/index.html
- centerline (Python) : https://github.com/fitodic/centerline
- Ink/Stitch — outils de trait (Fill to Stroke) : https://inkstitch.org/docs/stroke-tools/
- Brevet US 6 947 808 (Soft Sight, numérisation automatique) : https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6947808
- Brevet US 8 532 810 (Cimpress) : https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8532810
- Brevet US 9 200 397 : https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9200397
- Liu, Piovarči, Hafner, Charrondière, Bickel 2023 — Directionality-Aware Design of Embroidery Patterns : https://diglib.eg.org/handle/10.1111/cgf14770
- Chen, McCool, Mann, Kitamoto — Embroidery Modeling and Rendering in Real Time : https://cgl.uwaterloo.ca/poster/xinling_SIGGRAPH11.pdf
- Wilcom — satin et tatami : https://wilcom.com/resources/blog/mastering-basic-stitch-types-satin-stitch-and-tatami-stitch
- Wilcom — découpage automatique des satins : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Quality/quality/quality-17.htm
- Wilcom — numérisation automatique : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Automatic/automatic/automatic-11.htm

### 18.9 Texte et satin
- Ink/Stitch — Fill to Satin : https://inkstitch.org/docs/satin-tools/#fill-to-satin
- Ink/Stitch — tutoriel création de police : https://inkstitch.org/tutorials/font-creation/
- Ink/Stitch — outils de police : https://inkstitch.org/docs/font-tools/
- Ink/Stitch — polices : https://inkstitch.org/docs/fonts
- Ink/Stitch — notes de version v3.3.0 : https://inkstitch.org/en/2026-07-31-v3.3.0
- Ink/Stitch — tickets Fill to Satin : https://github.com/inkstitch/inkstitch/issues/4530 , https://github.com/inkstitch/inkstitch/issues/4561
- Ink/Stitch — proposition de contour satin : https://github.com/inkstitch/inkstitch/issues/3812
- Forum Inkscape — conversion satin en un clic : https://inkscape.org/forums/embroidery/1-click-solution-to-convert-object-to-a-stain-stitch

### 18.10 Couleurs et nuanciers
- Palettes Ink/Stitch : https://github.com/inkstitch/inkstitch/tree/main/palettes
- Ink/Stitch — catalogue et correspondance : https://github.com/inkstitch/inkstitch/blob/main/lib/threads/catalog.py , https://github.com/inkstitch/inkstitch/blob/main/lib/threads/palette.py
- Ink/Stitch — couleurs de fil : https://inkstitch.org/docs/thread-color/
- Ink/Stitch — licence : https://github.com/inkstitch/inkstitch/blob/main/LICENSE
- Ink/Stitch — liste des fils : https://github.com/inkstitch/inkstitch/blob/main/lib/extensions/thread_list.py , https://github.com/inkstitch/inkstitch/blob/main/lib/extensions/zip.py , https://github.com/inkstitch/inkstitch/blob/main/lib/extensions/apply_threadlist.py
- Ink/Stitch — modèles d'impression : https://github.com/inkstitch/inkstitch/tree/main/print/templates
- pyembroidery — EmbThread : https://github.com/EmbroidePy/pyembroidery/blob/main/pyembroidery/EmbThread.py
- EduTech Wiki — nuanciers : https://edutechwiki.unige.ch/en/Embroidery_thread_color_and_chart
- Wilcom — nuanciers : https://help.wilcom.com/portal/en/kb/articles/thread-charts-color-index
- Wilcom — fiches de production : https://help.wilcom.com/portal/en/kb/wilcom-international/wilcom-truesizer/finalize-designs/articles/production-worksheets
- Wilcom — séquences d'arrêt : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Production/reports/reports-14.htm
- Exemple de fiche Wilcom (PDF) : https://abdigitizing.com/wp-content/uploads/2024/04/Floral-Swoosh-02-4x4-1.pdf
- colour-science — ΔE : https://colour.readthedocs.io/en/master/_modules/colour/difference/delta_e.html
- scikit-image — couleur : https://scikit-image.org/docs/stable/api/skimage.color.html
- colormath2 : https://github.com/pushfoo/python-colormath2 , https://pypi.org/project/colormath2/
- Sharma, Wu, Dalal 2005 — CIEDE2000 : https://hajim.rochester.edu/ece/sites/gsharma/papers/CIEDE2000CRNAFeb05.pdf (données : https://www.ece.rochester.edu/~gsharma/ciede2000/)
- Celebi — quantification k-moyennes : https://arxiv.org/abs/1101.0395
- Quantification de couleurs (2026) : https://arxiv.org/html/2601.19117v2

### 18.11 Séquençage, origine, nœuds, coupes, tissus, tambours, essai
- Mr X Stitch — cheminement : https://www.mrxstitch.com/pathing/
- Embroideres — navigation : https://forum.embroideres.com/articles.html/articles/embroidery-navigation-r212
- Wilcom — ordre des objets : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Modifying/combine/combine-12.htm
- Ink/Stitch — routage : https://inkstitch.org/tutorials/routing/
- Ink/Stitch — édition : https://inkstitch.org/docs/edit
- Ink/Stitch — nœuds d'arrêt : https://inkstitch.org/docs/stitches/lock-stitches/
- Melco — centrage : https://melco.zendesk.com/hc/en-us/articles/360004994672-Centering-Designs
- Wilcom — départ/fin automatiques : https://wilcom.com/resources/blog/auto-start-end
- Wilcom — tambours : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Production/hoops/hoops-10.htm
- Wilcom — nœuds de fin / départ : https://docs.wilcom.com/embroiderystudio/27/en/OnlineHelp/Quality/connectors/connectors-7.htm , https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Quality/connectors/connectors-6.htm
- Manuel Tajima TEJT-II : https://www.silmaq.com.br/wp-content/uploads/downloads/MANUAIS/TAJIMA/Manual%20de%20Instru%C3%A7%C3%A3o/tejtii-c-m-ic2-11-e-2014-04.pdf
- Manuel Brother PR650e : https://www.manualslib.com/manual/976950/Brother-Pr650e.html?page=201
- Artapli — longs fils de saut : https://artapli.shop/blogs/embroidery-technical-reference/why-dst-files-create-long-jump-threads-on-commercial-embroidery-machines
- Wilcom — tissus automatiques : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Digitizing/properties/properties-9.htm , https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Digitizing/properties/properties-12.htm
- Wilcom — compensation automatique : https://docs.wilcom.com/embroiderystudio/26/en/OnlineHelp/Quality/underlays/Apply_automatic_pull_compensation.htm
- Impressions — densité et sous-couche : https://impressionsmagazine.com/process-technique/preventing-embroidery-digitizing-disasters-part-2preventing-embroidery-digitizing-disasters-lettering-density-underlay-problems/169753/
- Melco — entoilage : https://melco.com/selecting-stabilizer-backing-for-embroidery/
- Melco — casquettes : https://melco-service.com/source1/Digitizing_for_Caps.htm
- Digitizing.us — protocole d'essai : https://digitizing.us/howwetest/
- Tajima TMEZ-SC / TMBP2-SC : https://www.tajima.com/product/tmez-sc/ , https://www.tajima.com/product/tmbp2-sc/
- HoopMaster — tambours : https://hoopmaster.com/support/hoop-identifier
- AllStitch — tambours Tajima : https://allstitch.com/collections/embroidery-hoops-for-tajima-and-compatible-embroidery-machines
- RBD — marge : https://www.rbdblog.com/?p=22815

### 18.12 Formats TBF, licence, SVG
- FileInfo — .TDS : https://fileinfo.com/extension/tds
- Wilcom — formats machine standard : https://docs.wilcom.com/embroiderystudio/e4/fr/MainHelp/Chenille/chenille_basics/Standard_machine_formats.htm
- Wilcom — TBF : https://docs.wilcom.com/embroiderystudio/e4/en/MainHelp/New_features/rn_-_update-4/TBF_machine_file_issues.htm
- Wilcom — paillettes : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Mixed/sequin_basics/sequin_basics-4.htm
- TBF vs DST : https://embroideryhoopstore.com/blogs/articles/tajima-tbf-vs-dst-pick-the-right-file-format-and-stop-losing-time-on-the-shop-floor
- pyembroidery — TbfWriter, README, licence : https://raw.githubusercontent.com/EmbroidePy/pyembroidery/main/pyembroidery/TbfWriter.py , https://raw.githubusercontent.com/EmbroidePy/pyembroidery/main/README.md , https://raw.githubusercontent.com/EmbroidePy/pyembroidery/main/LICENSE
- pystitch — dépôt, README, licence : https://github.com/inkstitch/pystitch , https://raw.githubusercontent.com/inkstitch/pystitch/main/README.md , https://raw.githubusercontent.com/inkstitch/pystitch/main/LICENSE
- FAQ GPL (FSF) : https://www.gnu.org/licenses/gpl-faq
- Ink/Stitch — clones : https://inkstitch.org/docs/stitches/clone/

### 18.13 Pipelines automatisés et générateurs
- InkStitchMCP : https://github.com/GreerBK/InkStitchMCP (runner : https://github.com/GreerBK/InkStitchMCP/blob/main/src/inkstitch_mcp/runner.py)
- cli-anything-inkstitch : https://github.com/bobbymarko/cli-anything-inkstitch (SPEC : https://github.com/bobbymarko/cli-anything-inkstitch/blob/main/SPEC.md)
- stitchcraft : https://github.com/KaboomFox/stitchcraft (https://github.com/KaboomFox/stitchcraft/blob/main/xtask/src/conformance/differential.rs , https://github.com/KaboomFox/stitchcraft/blob/main/conformance/inkstitch/pin.toml , https://github.com/KaboomFox/stitchcraft/blob/main/conformance/inkstitch/stubs/wx/__init__.py , https://github.com/KaboomFox/stitchcraft/blob/main/.github/actions/inkstitch/action.yml)
- Jawetzel worker : https://github.com/jawetzel/Jawetzel/blob/main/worker/Dockerfile
- rodrigozago worker : https://github.com/rodrigozago/bit-lab-contabo/blob/main/ponto-studio/workers/embroidery/Dockerfile , https://github.com/rodrigozago/bit-lab-contabo/blob/main/ponto-studio/workers/embroidery/inkstitch_runner.py
- OpenMates : https://github.com/glowingkitty/OpenMates/blob/main/backend/scripts/build_embroidery_template.py
- pic-to-patch : https://github.com/maxwofford/pic-to-patch/blob/main/Dockerfile.worker
- Stitch-Forge CI : https://github.com/sapiverpress-studio/Stitch-Forge/blob/main/.github/workflows/real-engine-smoke.yml
- inkstitch-lib : https://github.com/jlyon1/inkstitch-lib/blob/main/Dockerfile.api
- InkstitchPipeline : https://github.com/DavidSchoenholz/InkstitchPipeline
- stitch_generator : https://github.com/bastanja/stitch_generator
- TurtleThread : https://github.com/TurtleThread/TurtleThread
- Hedy : https://github.com/hedyorg/hedy/blob/main/app.py
- vpype-embroidery : https://github.com/EmbroidePy/vpype-embroidery
- PEmbroider : https://github.com/CreativeInquiry/PEmbroider
- TurtleStitch : https://github.com/backface/turtlestitch
- embroidery-streamlines : https://github.com/desmondlzy/embroidery-streamlines
- bytes-to-bobbins-talk : https://github.com/kantoniak/bytes-to-bobbins-talk
- autodigitization : https://github.com/kenny240tech/autodigitization

### 18.14 Retours d'expérience
- Happylab Vienne : https://www.happylab.at/en/news/ink-stitch
- Forum Inkscape — texte sur remplissage : https://inkscape.org/forums/embroidery/techniques-for-making-text-on-top-of-a-fill-more-crisp
- Forum Inkscape — compensation globale : https://inkscape.org/forums/embroidery/global-parameters-for-shrink-compensation_QLAQ1
- Forum Inkscape — arrêt/coupe entre lettres : https://inkscape.org/forums/embroidery/command-to-stopcut-stitch-not-working-between-letters
- Forum Inkscape — sauts et coupes : https://inkscape.org/hu/forums/embroidery/trim-jump-stitches
- Ink/Stitch — commandes (www) : https://www.inkstitch.org/docs/commands/
- Ink/Stitch — FAQ : https://inkstitch.org/docs/faq/
- Wiki makerspace — broderie CNC : https://sites.google.com/view/makerlabsinternalwiki/education/cnc-embroidery-101
- Coastal Carolina University — makerspace : https://libraries.coastal.edu/makerspace/embroidery
- Forum Seamly : https://forum.seamly.io/t/inkstitch-embroidery-software/3130
- SaaSHub — avis : https://www.saashub.com/ink-stitch-reviews
- Tickets Ink/Stitch DST / Tajima : https://github.com/inkstitch/inkstitch/issues/2388 , https://github.com/inkstitch/inkstitch/issues/2673 , https://github.com/inkstitch/inkstitch/issues/3544 , https://github.com/inkstitch/inkstitch/issues/1296 , https://github.com/inkstitch/inkstitch/issues/4260 , https://github.com/inkstitch/inkstitch/issues/3923

### 18.15 Fichiers d'exemple
- Embroidermodder : https://github.com/Embroidermodder/Embroidermodder
- Ink/Stitch — échantillons : https://inkstitch.org/tutorials/resources/samples
- EduTech Wiki — Emoji Embroidery Project : https://edutechwiki.unige.ch/en/Emoji_Embroidery_Project
- Madeira UK : https://www.madeira.co.uk/dstfiles/
- Madeira USA : https://www.madeirausa.com/resources/free-embroidery-design-downloads/
- Æthelmearc : https://aeans.aethelmearc.org/machine-embroidery-files/
- free-embroidery-files.com : https://free-embroidery-files.com/faq/

### 18.16 Savoir de métier complémentaire et revue critique
- Wilcom — glossaire : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/glossary/glossary.htm
- Wilcom — espacement ou densité (billet) : https://wilcom.com/resources/blog/stitch-spacing-or-density
- Wilcom — densité tatami : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Digitizing/stitches/stitches-14.htm
- Wilcom — compensation de traction (par côté) : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Quality/stabilizing/stabilizing-17.htm
- Wilcom — poussée et traction (billet) : https://wilcom.com/resources/blog/push-and-pull-compensation
- Wilcom — angles : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Quality/quality/quality-9.htm
- Wilcom — points courts : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Quality/quality/quality-15.htm
- Wilcom — chevauchements : https://docs.wilcom.com/embroiderystudio/27/en/OnlineHelp/Quality/quality/quality-2.htm
- Bernina — chevauchements : https://softwarehelp.bernina.com/en/MainHelp/PART_Basics/setup/Setting_overlap_removal_options.htm
- Wilcom — dessins à faible nombre de points (vitesse, coupes) : https://wilcom.com/resources/blog/high-impact-low-stitch-count-designs
- Wilcom — temps de production : https://docs.wilcom.com/embroiderystudio/e4/en/MainHelp/Setup/hardware/Configure_machine_runtime_settings.htm
- Wilcom — espacement satin selon le fil : https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Digitizing/stitches/stitches-10.htm
- Ink/Stitch v3.3.0 — fill_stitch.py : https://github.com/inkstitch/inkstitch/blob/v3.3.0/lib/elements/fill_stitch.py
- Ink/Stitch v3.3.0 — satin_column.py : https://github.com/inkstitch/inkstitch/blob/v3.3.0/lib/elements/satin_column.py
- Impressions — distorsions de poussée et traction : https://impressionsmagazine.com/process-technique/isolating-embroidery-problems-digitizing-vs-execution-pull-push-distortion/168424/
- Impressions — angles et coiffes : https://impressionsmagazine.com/process-technique/embroidery-tips-for-corners-and-capping/16307/
- Impressions — anticiper poussée et traction : https://impressionsmagazine.com/process-technique/anticipate-push-pull-in-designs/16265/
- Impressions — commande d'un écusson (approbation) : https://impressionsmagazine.com/build-your-business/ordering-perfect-embroidered-emblem/37029/
- Mr X Stitch — quatre bases de la numérisation : https://www.mrxstitch.com/4-basic-digitizing-skills/
- Mr X Stitch — densité : https://www.mrxstitch.com/density/
- Tajima TMBR2-SC : https://www.tajima.com/?p=556
- Tajima TMCR : https://www.tajima.com/?p=820
- Madeira Polyneon 40 — fiche technique : https://www.madeira.com/fileadmin/user_upload/Downloads/Data_Sheets/Data_Sheet_POLYNEON_40__EN.pdf
- Amann Isacord : https://amann.com/products/product/isacord
- Prestataire — échantillons d'approbation : https://www.ignitiondrawing.com/blog/we-offer-exact-sew-outs

---

## 19. Savoir de métier complémentaire (recherche du 16/11/2026, après revue critique)

### 19.1 Conventions d'espacement
- Wilcom : l'espacement est mesuré « entre deux pénétrations consécutives du même côté » ; en tatami, un rang aller est suivi d'un rang retour, la mesure se fait **un rang sur deux** ([glossaire Wilcom](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/glossary/glossary.htm), [billet Wilcom](https://wilcom.com/resources/blog/stitch-spacing-or-density)). La page Wilcom sur la densité tatami ne précise pas la convention ([Wilcom](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Digitizing/stitches/stitches-14.htm)).
- Ink/Stitch : `row_spacing_mm` = rangs voisins (défaut 0,25) ; `zigzag_spacing_mm` = crête à crête (défaut 0,40), soit la même convention que l'espacement satin Wilcom ([source v3.3.0 fill_stitch.py](https://github.com/inkstitch/inkstitch/blob/v3.3.0/lib/elements/fill_stitch.py), [satin_column.py](https://github.com/inkstitch/inkstitch/blob/v3.3.0/lib/elements/satin_column.py)).
- Sources professionnelles : « 40 wt rarement plus dense que 0,40 mm », « 0,4 mm = couverture complète » — convention non précisée ([Impressions](https://impressionsmagazine.com/process-technique/preventing-embroidery-digitizing-disasters-part-2preventing-embroidery-digitizing-disasters-lettering-density-underlay-problems/169753/), [Mr X Stitch](https://www.mrxstitch.com/4-basic-digitizing-skills/)).
- Conclusion : **0,20–0,25 mm entre rangs voisins** (≈ 0,40–0,50 mm « Wilcom ») ; [MESURE] fichier de test d'origine : 0,23 mm. À confirmer sur fichiers professionnels et broderie réelle. Pulse, Hatch : non vérifié.

### 19.2 Compensation de traction : par côté
Wilcom : « par défaut, la même valeur est appliquée aux deux côtés » (valeur **par côté**, côtés réglables séparément) ; valeurs indicatives : coton/sergé 0,20, tee-shirt 0,35, polaire 0,40, lettrage 0,2–0,3 mm ([Wilcom](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Quality/stabilizing/stabilizing-17.htm)). Ink/Stitch : « (chaque côté) ». Campbell : un satin perd 0,17–0,25 mm sur tissu stable, sans préciser total ou par côté ([Impressions](https://impressionsmagazine.com/process-technique/isolating-embroidery-problems-digitizing-vs-execution-pull-push-distortion/168424/)).

### 19.3 Compensation de poussée
Allongement des colonnes dans le sens des points, à leurs extrémités ([Wilcom](https://wilcom.com/resources/blog/push-and-pull-compensation)). Campbell : 0,13–0,20 mm pour une colonne pleine en 40 wt ; terminer l'élément 0,17–0,20 mm avant la bordure dans l'axe de la poussée (même source Impressions). Ink/Stitch : pas de paramètre dédié (raccourcir les rails : non vérifié comme pratique documentée).

### 19.4 Angles et extrémités de colonnes
Wilcom : sans angle, onglet, coiffe (segment parallèle à la colonne), recouvrement (angle en deux segments), arrondis ; pas de seuils publiés ([Wilcom](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Quality/quality/quality-9.htm)). Elliott : recouvrement de l'onglet selon le tissu (plus sur maille) ; bordures ≤ 1,5 mm d'angle en angle ; ajouter des lignes perpendiculaires aux pointes aiguës ([Impressions](https://impressionsmagazine.com/process-technique/embroidery-tips-for-corners-and-capping/16307/)). Ink/Stitch : contrôle par barreaux, inversion des rails et méthodes de découpe ([satin](https://inkstitch.org/docs/stitches/satin-column/)). Jonctions en T et en Y : non vérifié.

### 19.5 Points courts dans les courbes serrées
Wilcom : raccourcissement dès que l'espacement tombe sous un pourcentage de l'espacement nominal, au plus 5 points courts consécutifs ([Wilcom](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Quality/quality/quality-15.htm)). Ink/Stitch : `short_stitch_inset` 15 % (plafond 50 %), `short_stitch_distance_mm` 0,25 (source satin_column.py).

### 19.6 Chevauchement entre aplats, sous-couche de bord
Wilcom et Bernina proposent un réglage de chevauchement sans valeur par défaut publiée ([Wilcom](https://docs.wilcom.com/embroiderystudio/27/en/OnlineHelp/Quality/quality/quality-2.htm), [Bernina](https://softwarehelp.bernina.com/en/MainHelp/PART_Basics/setup/Setting_overlap_removal_options.htm)). Campbell : prolonger l'élément inférieur sous la bordure, sans chiffre. Valeur en mm : non vérifiée (seulement des blogs de vendeurs). Sous-couche de remplissage : retrait ≥ 0,40 mm, espacement et longueur 3–4 mm (Campbell) ; défaut Ink/Stitch du retrait : 0.

### 19.7 Empilement et surdensité
Campbell : les empilements « pare-balles » cassent fils et aiguilles ([Mr X Stitch](https://www.mrxstitch.com/density/)) ; Caroselli-Barnes : trois couches à un tiers de densité chacune ([Impressions](https://impressionsmagazine.com/process-technique/anticipate-push-pull-in-designs/16265/)). Nombre maximal de couches, pénétrations par mm² : non vérifié.

### 19.8 Temps de broderie
Tajima TMBR2-SC : 1200 tr/min (1000 en casquette) ([Tajima](https://www.tajima.com/?p=556)) ; TMCR : 1100 tr/min ([Tajima](https://www.tajima.com/?p=820)). Wilcom : 700–800 points/min en pratique ; chaque coupe 3–4 s ([Wilcom](https://wilcom.com/resources/blog/high-impact-low-stitch-count-designs)) ; paramètres de temps de production ([Wilcom](https://docs.wilcom.com/embroiderystudio/e4/en/MainHelp/Setup/hardware/Configure_machine_runtime_settings.htm)). Durée d'un changement de couleur : non vérifiée.

### 19.9 Épaisseur du fil 40 wt
Madeira Polyneon 40 : dtex 135 × 2 (27 tex), aiguille 60/8–75/11 ([fiche](https://www.madeira.com/fileadmin/user_upload/Downloads/Data_Sheets/Data_Sheet_POLYNEON_40__EN.pdf)) ; Isacord 40 : 27 tex ([Amann](https://amann.com/products/product/isacord)). Diamètre calculé (polyester massif) ≈ 0,16 mm, ≈ 0,2 mm aplati : cohérent avec une couverture complète à ≈ 0,2 mm entre rangs voisins.

### 19.10 Approbation du client
Épreuve en ligne ou échantillon brodé ; l'approbation transfère la responsabilité et déclenche la production ([Impressions](https://impressionsmagazine.com/build-your-business/ordering-perfect-embroidered-emblem/37029/), [exemple de prestataire](https://www.ignitiondrawing.com/blog/we-offer-exact-sew-outs)).

### 19.11 Grosseur de fil, contraste, sens du tissu
Wilcom : décalage d'espacement satin selon la grosseur du fil (+0,03 mm pour un fil plus gros, −0,03 à −0,06 mm pour un fil fin) ([Wilcom](https://docs.wilcom.com/embroiderystudio/28/en/OnlineHelp/Digitizing/stitches/stitches-10.htm)) ; le contraste fil / tissu conditionne la densité minimale (échantillons) ; angle de remplissage à 15–20° de l'horizontale pour limiter l'éclatement des bords (source Impressions 168424).

---

## 20. Questions ouvertes
Le suivi détaillé des points ouverts est tenu dans `processus_broderie.md` (§ « Suivi des points ouverts »). Questions de connaissance restant sans réponse sourcée :
1. Réglage d'usine du nombre de sauts déclenchant une coupe sur Tajima, Barudan, SWF, Melco.
7. Convention d'espacement chez Pulse et Hatch ; valeur professionnelle de l'espacement de remplissage entre rangs voisins (à mesurer sur fichiers professionnels).
8. Valeur de chevauchement entre aplats voisins ; traitement des jonctions en T et en Y ; nombre maximal de couches superposées.
9. Durée d'un changement de couleur sur machine Tajima.
2. Comportement d'Ink/Stitch avec les remplissages par motif (`pattern`).
3. Tolérances chiffrées pour juger un essai sur tissu (aucune publiée).
4. Profil de réglages pour les écussons.
5. Origine et exactitude des valeurs RVB des palettes de fils.
6. Cause des tickets ouverts « DST non lu sur Tajima » (corps des tickets non accessibles depuis l'environnement).

---

## Journal des versions
| Version | Date | Changements |
|---|---|---|
| 0.1 | 15/11/2026 | Principes, formats, filières, contraintes, analyse d'un dessin, attributs Ink/Stitch |
| 0.2 | 15/11/2026 | Installation et ligne de commande, choix des points, vérification DST ; liste exhaustive des références |
| 0.3 | 15/11/2026 | Document rendu générique ; essais techniques (§10) ; mesure et classement (§11) ; texte en satin (§12) ; couleurs (§13) ; séquençage, tissus, tambours, essai (§14) ; formats, licence, SVG (§15) ; retours d'expérience (§16) ; fichiers d'exemple (§17) ; corrections : « tajma.tds » ≈ DST, TBF atteignable via pystitch, unité d'en-tête tranchée, dégradés et opacité vérifiés, installation vérifiée |
| 0.4 | 16/11/2026 | Retrait de toute référence à un dessin particulier : §5 devient une méthode d'analyse générique, §8 classé par type d'élément ; recherche des dessins d'origine des DST d'exemple (§17) |
| 0.5 | 16/11/2026 | **Après revue critique** : convention d'espacement corrigée (0,40 « professionnel » = un rang sur deux ; défaut Ink/Stitch 0,25 entre rangs voisins conservé), compensation par côté confirmée, épaisseur du fil revue (≈ 0,2 mm), signe de l'angle, motif brut des coupes, « risque principal » rétrogradé, résidus d'un dessin particulier retirés, coupes d'Embroidermodder.DST corrigées ; nouveau §19 savoir de métier (poussée, angles, points courts, chevauchements, empilement, temps, fil, approbation) ; références §18.16 |
