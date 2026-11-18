# Revue critique indépendante — Chaîne « dessin vers fichier DST »

> ⚠️ **Avertissement — contenu généré par intelligence artificielle.** Ce document a été produit avec l'aide d'une IA (Claude, Anthropic) et n'a pas été validé par un spécialiste de la broderie machine. Il peut contenir des erreurs. Toute information, tout réglage et tout fichier produit — en particulier les fichiers machine (.dst) — doivent être vérifiés par un professionnel qualifié avant usage. **Un fichier machine erroné peut endommager la brodeuse** (casse d'aiguille, bourrage, contrainte mécanique), abîmer le tissu et présenter un risque pour l'opérateur : ne jamais lancer une broderie sans contrôle préalable par un spécialiste et premier essai à vitesse réduite, sur chute de tissu.

> Date : 16 novembre 2026
> Objet : critique des documents, des essais et du prototype (collecte de savoir, processus, guide d'installation, essais techniques, prototype, essais trèfle et étoile).
> Méthode : lecture complète des pièces, puis expériences de contrôle dans `critique_scratch/` (scripts `exp1.py` à `exp7.py`, Ink/Stitch v3.3.0 de `install_test`). Aucun fichier du projet n'a été modifié.

**Légende.** Gravité : **bloquant** (invalide une conclusion ou produira un fichier défectueux), **majeur**, **mineur**. Statut de preuve : **vérifié** (expérience ou lecture du code faite pendant cette revue), **plausible** (raisonnement ou source, non rejoué), **faux** (affirmation du projet contredite par une mesure).
« IoU » désigne partout le recouvrement des surfaces cousues (intersection divisée par union) calculé par `prototype/chaine/comparer.py`.

---

## 0. Synthèse

Le socle technique est solide : installation reproductible, dix essais techniques bien menés, exports déterministes (vérifié : trois exports du même SVG, empreintes identiques), frontière de licence respectée dans le code. La collecte de savoir est large et honnête sur ses limites.

En revanche, **la conclusion « concluant » des deux essais de bout en bout n'est pas soutenue par les mesures**. Le critère de réussite (IoU 0,90 et 0,94) ne mesure que la silhouette couverte et ne voit ni la direction des points, ni l'ordre, ni la sous-couche, ni une surdensité. Les mesures de cette revue montrent que les deux fichiers produits sont, sur des critères de broderie, nettement moins bons que les originaux :

| Constat chiffré (cette revue) | Original | Notre fichier |
|---|---|---|
| Étoile — espacement réel entre rangs voisins du remplissage | 0,23 mm | 0,40 mm (≈ 43 % de fil de dessus en moins) |
| Trèfle — points de satin plus longs que 1,5 fois la largeur locale de la colonne (points en biais) | 0 % | 9 % |
| Étoile, bordure — même mesure | 0 % | 21 % |
| Étoile — « coupe au changement de couleur » annoncée | — | **absente** du fichier |

Cinq défauts sont à traiter avant tout nouvel essai : (1) densité de remplissage probablement fausse d'un facteur deux par confusion de convention ; (2) critère de réussite inadapté ; (3) signe de l'angle de remplissage inversé ; (4) satin « anneau » appliqué sans garde à des lettres ; (5) aucun essai à partir d'un vrai dessin vectoriel, alors que c'est l'entrée déclarée du processus.

---

## 1. Validité de la méthode d'essai

### 1.1 L'essai est circulaire et n'éprouve presque rien du processus — **bloquant** (plausible, étayé)
L'image d'entrée est le rendu du fichier auquel on se compare (`rapport_essai_trefle.md` l. 13, `rapport_essai_etoile.md` l. 13). Elle contient déjà le résultat des décisions du numériseur d'origine : largeur des colonnes, emprise après compensation, séparation remplissage / bordure. L'essai vérifie donc un aller-retour géométrique (rendu → contour → points couvrant la même surface), pas une numérisation.

Ce qui n'est **pas** éprouvé, bien que listé comme prototypé (`processus_broderie.md` l. 303) :
- la normalisation du SVG (§3.1) : aucune entrée SVG réelle n'a jamais traversé la chaîne ;
- la mise à l'échelle (§3.0) : la taille cible est celle de l'original, l'échelle vaut ≈ 1 ; aucune seconde taille, donc aucune décision qui change avec la taille ;
- le classement (§3.3) : trois formes en tout, toutes loin des seuils (allongement 35 et 37 contre un seuil de 3) ;
- le nettoyage (§3.4) : rien à nettoyer sur le trèfle ; sur l'étoile, seuls des artefacts du rendu ;
- le séquençage : un ou deux objets ; les couleurs : arbitraires ; le texte : absent.

Le rapport du trèfle le reconnaît en partie (l. 77 à 81), mais le résumé d'en-tête et le suivi (`processus_broderie.md` l. 304, « validé » l. 66 et l. 280) retiennent « concluant » et « validé ».

### 1.2 Deux cas, réglages ajustés sur ces deux cas, aucune donnée tenue à l'écart — **majeur** (vérifié par lecture)
Pas des barreaux 3 → 1 mm, appariement monotone, longueur minimale 0,3 mm, tolérance de grille, extension sous bordure : tous ces réglages ont été choisis en regardant les deux mêmes fichiers (`rapport_essai_trefle.md` l. 53 à 58 ; `rapport_essai_etoile.md` l. 55 à 61). La « non-régression » (étoile l. 78) rejoue l'autre fichier du même couple. Il n'y a ni jeu d'essai séparé, ni critère fixé avant l'essai. Le troisième fichier (lettrage) est la seule donnée encore vierge : **figer réglages et critères avant de le lancer**.

### 1.3 Le retrait de 0,15 mm et la compensation à zéro — **majeur** (vérifié)
- Le retrait n'est pas un sur-ajustement au sens strict : il correspond à la demi-épaisseur du trait du rendu (`tools/render_dst.py` : trait de 3 px à 10 px/mm) et il **fait baisser** l'IoU (0,918 → 0,90).
- Mais il est appliqué **en double**. La mise à l'échelle ramène déjà la largeur du contour tracé (points + trait de 0,3 mm) à la largeur des points de l'original : 502 px ramenés à 49,9 mm, soit 0,0994 mm/px au lieu de 0,1 (`trefle_rapport.json`, `mm_par_px`). Le retrait enlève ensuite 0,3 mm de plus. C'est l'origine exacte de l'écart de −0,3 mm, que le rapport attribue à un « retrait un peu fort » (trèfle l. 74). Correction : viser « largeur des points + épaisseur du trait » à l'échelle, ou ne pas retirer.
- Sur l'étoile, le retrait à onglets raccourcit chaque pointe d'environ 0,15 / sin(18°) ≈ 0,5 mm. Une part du défaut « pointes raccourcies », attribué à la construction du satin (étoile l. 67), vient donc du montage d'essai (plausible).
- **La configuration de production n'a jamais été évaluée.** Les essais tournent avec compensation de traction nulle et retrait de rendu ; un vrai dessin tournera avec compensation et sans retrait. Dernier chiffre connu dans cette configuration : IoU 0,86 et 17 points au-delà de 7 mm (trèfle l. 55-56).
- Le passage de 0,86 à 0,92 obtenu en supprimant la compensation (trèfle l. 57) montre que **le critère pénalise un réglage indispensable sur tissu**. Il pousse dans la mauvaise direction.

### 1.4 Affirmations des rapports contredites par les mesures
| Affirmation | Réalité mesurée | Gravité |
|---|---|---|
| Étoile : « Coupes : 1 — coupe au changement de couleur (bonne pratique) » (l. 46) | **Faux.** La seule suite de 3 sauts est le déplacement initial vers le premier point (enregistrements 0 à 2, pas de (−47, ±88) unités chacun). Au changement de couleur (enregistrement 1488), aucun saut, aucun motif de coupe (+2,+2)(−4,−4)(+2,+2). (`exp1.py` et lecture avec `trim_at=1000`) | majeur |
| Étoile : « angle 45° ; l'original est à environ −30° » (l. 28, l. 69) | **Faux.** Direction dominante lue : original 134,8° (95 % du fil), nous 135,0° (65 % du fil, dessus) et 45,0° (23 %, sous-couche). Les deux remplissages sont parallèles, par coïncidence (`exp4.py`) | mineur |
| Étoile : « points cousus +4 % », « longueur de fil +0,5 % » présentés comme une concordance | **Compensation d'erreurs.** Remplissage : 4530 mm de fil dans l'original contre 3778 mm chez nous, dont 23 % de sous-couche, soit ≈ 2570 mm de dessus (−43 %). Bordure : 2079 mm contre 2862 mm (+38 %) sur une surface plus petite (`exp3.py`) | majeur |
| Trèfle : « Densité plus faible… choix de réglage, pas une erreur » (l. 73) | Plausible pour le satin (voir 3.1), mais voir 5.1 pour le remplissage | — |
| « Points < 0,3 mm : mieux » | Comparaison à un fichier que l'amont déclare « possiblement invalide » (`INVENTORY.md` l. 12) : « mieux » n'a pas de valeur | mineur |
| « Le résultat ne dépend pas d'un réglage fin » (trèfle l. 60) | Vrai pour l'IoU, mais l'IoU ne dépend de presque rien (voir 2.1) : l'argument est vide | mineur |
| Tableau du rapport trèfle (1196 points, 13 < 1 mm, 1 < 0,3 mm) | Périmé : le JSON joint donne 1195 / 12 / 0 | mineur |
| « Sauts : 5 contre 3 » (étoile l. 45) | Artefact de lecture : le fichier brut de l'original contient 15 sauts (dont 10 de longueur nulle) | mineur |

---

## 2. Les mesures de comparaison

### 2.1 Le recouvrement des surfaces est aveugle à la qualité des points — **bloquant** (vérifié)
Variantes de l'étoile produites par Ink/Stitch à partir de `etoile_parametre.svg`, comparées à l'original (`exp2.py`) :

| Variante | IoU | Points | Fil (mm) |
|---|---|---|---|
| Référence de l'essai | 0,936 | 2643 | 6640 |
| Angle de remplissage 0° / 90° | 0,934 / 0,931 | 2703 / 2675 | — |
| **Bordure brodée avant le remplissage** (ordre faux) | **0,936** | 2670 | 6645 |
| **Aucune sous-couche** | 0,926 | 2066 | 5189 |
| **Densité doublée** (rangs à 0,2 mm) | **0,957** (meilleur) | 3664 | 9929 |
| Satin deux fois et demie trop clairsemé (zigzag 1,0 mm) | 0,899 | 2044 | 5254 |
| Compensation de traction 0,2 mm | 0,942 | 2645 | 7024 |
| Rangs à 0,8 mm | 0,707 | 2056 | 4959 |
| Sans bordure satin | 0,806 | 1472 | 3770 |

Lecture : un ordre de broderie faux donne la même note ; une surdensité de 50 % de fil **améliore** la note ; un satin clairsemé obtient 0,90, la note du trèfle déclaré « concluant ». L'IoU ne réagit qu'à la perte de couverture.

### 2.2 La note dépend d'un paramètre de rendu arbitraire — **majeur** (vérifié)
Épaisseur de fil dessinée (`largeur_fil_mm`, 0,4 par défaut, `comparer.py` l. 66) :

| Épaisseur dessinée | IoU trèfle | IoU étoile |
|---|---|---|
| 0,2 mm | 0,656 | 0,549 |
| 0,3 mm | 0,851 | 0,748 |
| 0,4 mm | 0,900 | 0,936 |
| 0,6 mm | 0,908 | 0,960 |

Avec un fil dessiné à 0,4 mm, des rangs espacés de 0,4 mm apparaissent « pleins ». La note de 0,94 de l'étoile tient donc à ce choix ; à 0,2 mm (épaisseur cohérente avec la règle de densité, voir 5.2) elle tombe à 0,55.

### 2.3 Alignement sur le centre des boîtes englobantes — **mineur** (vérifié)
- Fragile : un seul point parasite placé 2 mm hors de la boîte fait passer l'IoU d'un fichier comparé à lui-même de 1,0 à 0,65 (trèfle) (`exp1.py`).
- Biais faible ici : par recherche de la meilleure translation, l'étoile passe de 0,936 à 0,950 (décalage 0,3 mm), le trèfle reste à 0,900 (`exp4.py`).
- Recommandation : alignement par meilleure translation, et signalement séparé de l'écart de dimensions.

### 2.4 Ce qui manque pour juger sans essai sur tissu — **majeur**
Aucune de ces mesures n'existe dans `comparer.py`. Toutes sont calculables à partir du plan de points, à condition de conserver la correspondance point → objet (perdue dans le DST : prendre le plan de points d'Ink/Stitch ou exporter objet par objet).

| Mesure | Ce qu'elle détecte | Preuve de faisabilité |
|---|---|---|
| Espacement réel des rangs et densité de fil par zone (mm de fil par mm²), carte de densité cumulée | Sous-couverture, surdensité, empilement de couches (casse de fil, « pare-balles ») | `exp3.py` : la méthode « aire / fil dans la direction dominante » retrouve 0,403 mm pour notre réglage de 0,4 |
| Satin : longueur du point / largeur locale de la colonne ; angle du point par rapport à la normale | Points en biais, éventails | `exp4.py`, `exp6.py` : anneau parfait 0 % au-delà de 1,5 ; trèfle 9 % ; bordure d'étoile 21 % ; originaux 0 % |
| Distribution des directions par objet | Angle de remplissage, présence et angle de la sous-couche | `exp3.py` |
| Présence, type et retrait de la sous-couche par objet | Sous-couche absente ou débordante | Séparation par direction et par ordre |
| Jours entre objets voisins après retrait simulé (rétrécir chaque objet de la perte attendue) | Liserés de tissu visibles | À faire |
| Déplacements sans couture : longueur, coupe réelle (motif brut), nœud avant et après, trajets cachés ou visibles | Fils traînants | Motif brut déjà connu (essai technique n° 10) |
| Ordre : chaque objet de dessus après ceux qu'il recouvre ; nombre de changements de couleur contre le minimum possible | Erreurs de séquençage | Test géométrique simple |
| Concentration de piqûres (nombre de pénétrations par mm²) | Trous dans le tissu, casse d'aiguille | Histogramme 2D |
| Points courts **par objet** et points longs **par type** | Les seuils de §6 ne sont vérifiables qu'avec le type de l'objet | — |
| Temps de broderie estimé (points / cadence + coupes + changements) et longueur de fil par couleur | Coût, données de la fiche | Trivial |
| Poussée : allongement attendu en bout de colonne et de rang | Débord aux extrémités | Modèle simple à étalonner |

Ces mesures doivent être **étalonnées sur des fichiers professionnels** (plages admises) et **validées par mutation** : chaque variante dégradée du tableau 2.1 doit être détectée par au moins une mesure.

---

## 3. Règles de décision et seuils

Classement de formes synthétiques par `geometrie.classer` avec le profil par défaut (`exp5.py`) :

| Forme | Largeur max | Allongement | Compacité | Décision obtenue | Avis |
|---|---|---|---|---|---|
| Disque 2 mm, disque 3 mm, carré 3 mm | 2 à 3 mm | 0,8 à 1,0 | 0,8 à 1,0 | Remplissage, auto | **Mauvais** : un tatami sur 2 à 3 mm est médiocre ; la pratique est le satin |
| Barre 2 × 5 mm, 3 × 9 mm, 5 × 20 mm | 2 à 5 mm | 2,5 à 4 | 0,50 à 0,64 | Remplissage, auto | **Mauvais** : colonnes typiques de satin |
| Barre 6 × 30 mm | 6 mm | 5 | 0,44 | Satin | Correct |
| Filet 0,3 × 30 mm | 0,3 mm | 100 | 0,03 | **Supprimer** | **Mauvais** : un filet long se brode en point droit (la collecte le dit, §8.1) |
| Sucette (disque 20 mm + tige 1,5 mm) | 20 mm | 0,9 | 0,30 | Remplissage, auto | **Mauvais** : la tige de 1,5 mm sera en tatami |
| Coin effilé 0,3 → 6 mm | 5,6 mm | 4 | 0,21 | Satin | Pointe sous la largeur minimale non vue |
| Lettre E (sans trou) | 2,5 mm | 11 | 0,16 | Satin → non constructible | Alerte « non construit » |
| Lettres A et P (un trou) | 3,7 mm | 8 | 0,2 | **Satin en anneau, sans alerte** | **Faux**, voir 3.3 |
| Lettre B, grille (plusieurs trous) | ≈ 3 mm | 12 à 28 | < 0,2 | Satin → repli en remplissage + alerte | Tatami sur des fûts de 2 mm : médiocre |
| Barre 12 × 80 mm | 12 mm | 6,7 | 0,36 | Remplissage | Correct |

### 3.1 La compacité exclut à tort les colonnes courtes — **majeur** (vérifié)
La compacité d'un rectangle de rapport r vaut π·r / (r + 1)². Le seuil « < 0,5 » exige r > 4 environ. Toute colonne de rapport inférieur à 4 (barres de lettres, petits traits épais, points, pastilles) part en remplissage automatique, sans alerte. La condition est redondante avec l'allongement pour les formes longues et nuisible pour les courtes. Il manque une règle « petite forme compacte de 1 à ≈ 6 mm de large → satin ».

### 3.2 Une forme, une décision : pas de décomposition — **majeur** (vérifié)
Le cercle inscrit maximal est dominé par la partie la plus large (sucette, logo avec filet attaché, lettre avec empattement). Les formes mixtes reçoivent une seule décision. Le processus (§3.3, dernière ligne) parle de « squelette anormal » sans définition ; il faut une étape explicite de **découpage en parties d'épaisseur homogène** avant classement, fondée sur le profil de largeur le long de la ligne médiane.

### 3.3 Satin « anneau » appliqué à toute forme à un trou — **bloquant** (vérifié)
La seule garde est le nombre de trous égal à un (`essai_dessin.py` l. 82, `satin.py` l. 50). Les lettres A et P passent : export avec code 0, sortie d'erreur vide, aucune alerte, et 16 à 20 % des points de dessus plus longs que 1,5 fois la largeur locale (99ᵉ centile : 3,7 à 5 fois), points jusqu'à 6,8 mm sur des fûts de 2,5 mm (`exp5.py`, `exp6.py`). Les lettres A, D, O, P, Q, R, a, b, d, e, g, o, p, q, 4, 6, 9, 0 sont toutes concernées. C'est une défaillance silencieuse, contraire au principe « rien n'est masqué ».

### 3.4 Écarts entre la règle écrite et la règle codée — **majeur** (vérifié)
- Largeur au 90ᵉ centile (`processus_broderie.md` l. 135 et 148) : non calculée ; le code utilise la largeur maximale (`geometrie.py` l. 73).
- Mode « revue » : aucun effet ; le satin est construit et exporté quand même (anneau de 8 mm de large → « satin (revue) » → export).
- Ligne « Supprimer ou agrandir — Alerte » (l. 146) : le nettoyage supprime d'office tout élément de moins de 1,5 mm² et de moins de 1 mm (`geometrie.py` l. 92), journalisé mais non bloquant. Un point sur un « i », un signe ®, une étoile de 1 mm disparaissent sans décision humaine.
- Trous de moins de 0,8 mm bouchés d'office (`geometrie.py` l. 101) : les contre-formes des petites lettres (e, a) sont comblées sans arrêt.
- « Objet proche d'un seuil » (l. 153) : aucune marge définie, aucune mise en œuvre.

### 3.5 Règles non testables telles qu'écrites — **majeur**
- **Texte** (l. 152, §5.2) : un texte vectorisé n'est qu'un ensemble de contours. Sans indication humaine dans la fiche de cadrage ou sans détecteur, les règles « hauteur minimale 5 mm », « capitales seules sous 4 mm » ne peuvent pas se déclencher.
- **Dégradé** : la ligne « Dégradé linéaire → choix » n'a pas de critère (taille minimale, nombre de couleurs).
- « Aire négligeable », « squelette anormal », « détails trop rapprochés », « trait trop fin pour son rôle » : pas de définition mesurable.
- Jambages de 1 à 1,5 mm : aucune case de §5.2 ne les couvre ; la largeur minimale vaut 0,8 mm (collecte §4), 1 mm (§2.2) ou 1,5 mm (§5.2) selon l'endroit.

### 3.6 Seuils de largeur du satin (1, 7 et 10 mm) — **mineur** (plausible)
Ordres de grandeur conformes à la pratique. Manquent : dépendance au tissu et à l'usage (un satin de 7 mm s'accroche sur un vêtement porté ; limite plus basse pour les vêtements de travail), et le traitement des largeurs variables (colonne de 1 à 9 mm).

### 3.7 Angle « moins de fragments » — **mineur** (vérifié)
Tel que codé (pas fixe de 1 mm), le critère compte surtout le **nombre de rangs**, donc choisit l'axe long de la forme, pas la moindre fragmentation. Sur une forme à symétrie d'ordre 5, il départage au hasard. Aucun critère de tenue (rangs le long de l'axe long = retrait maximal dans cet axe) ni de variété visuelle entre objets voisins.

---

## 4. Document de processus

### 4.1 Aucune exigence mesurable de qualité — **bloquant**
Le but est « qualité professionnelle », mais aucun document ne dit ce que cela signifie de façon vérifiable. Sans critère d'acceptation fixé d'avance, tout essai peut être déclaré concluant. Le point 4.1 du suivi (« mêle encore le quoi et le comment », l. 292) est ouvert depuis la version 0.5 ; c'est le défaut de structure le plus coûteux. À écrire séparément : exigences (quoi : « tout déplacement sans couture de plus de N mm est coupé et noué », « aucun objet de dessus n'est brodé avant ce qu'il recouvre », « toute modification du dessin est approuvée »), puis architecture (noms de scripts, variables d'environnement, options d'Ink/Stitch, attributs `inkstitch:*`, aujourd'hui dans §0, §2.3, §2.4, §2.5).

### 4.2 Contradictions et incohérences internes — **majeur** (vérifié par lecture)
| Sujet | Constat |
|---|---|
| Version | En-tête « 0.5 » (l. 6) ; journal jusqu'à 0.9, dans le désordre (0.9, 0.8, 0.7, 0.6 après 0.5.1) |
| Entrée | §0 : image matricielle « hors périmètre » ; `LISEZMOI.md` : « dessin vectoriel ou image » ; les deux seuls essais partent d'images |
| Briques | §2.5 liste huit scripts qui n'existent pas ; le prototype a d'autres modules |
| Coupes | §6.4 : vérification par motif brut ; le prototype compte les suites de 3 sauts (`comparer.py` l. 23), d'où l'erreur de 1.4 |
| Sous-couche | §2.2 : remplissage « 90°, 3 à 4 mm, retrait ≥ 0,4 mm » ; satin de plus de 4 mm « contour + zigzag » ; le prototype n'écrit aucun réglage de sous-couche de remplissage (retrait par défaut d'Ink/Stitch : 0) et jamais de zigzag |
| Séquençage | §5.3 (arrière → avant, calques) ; le prototype trie par type, puis **par code hexadécimal de couleur**, puis par aire (`essai_dessin.py` l. 131) : ni calques, ni recouvrements |
| Export | §2.4 règle 7 : archive avec liste des fils ; prototype : DST seul. Règle 3 : journalisation désactivée ; rien dans `executer` |
| Longueur minimale de point | Deux lignes dans §2.2 (l. 68 et l. 73) |
| Fil très fin | Collecte §8.1 : trait de 0,25 mm → point droit ; processus §3.3 : largeur < 0,4 mm → supprimer |
| Contrôle A4 | « Aucun saut > 12,1 mm non coupé » : un DST ne peut pas contenir de saut de plus de 12,1 mm (il est découpé). Le critère utile est « tout déplacement sans couture au-delà du seuil de coupe est noué puis coupé » |
| §6.3 | « Points ≤ 7 mm en satin » : invérifiable sur le DST seul (pas de type d'objet) |
| §6.6 | « Aperçu comparé au dessin d'origine » : ni méthode ni seuil |
| Résidu | Collecte §1 l. 16 : « Notre SVG… en trois calques » et §3.2 « ce qui est notre cas » : restes d'un dessin particulier, contraires à la version 0.4 |

### 4.3 L'étape « un agent met à jour le SVG » — **bloquant** tant qu'elle n'est pas encadrée
Telle qu'écrite (§3.4), elle est contraire à trois principes du même document : reproductibilité, « rien n'est masqué », arrêt quand une décision humaine est requise.
- « En préservant l'intention graphique » : non vérifiable.
- Boucle « jusqu'à zéro défaut bloquant » : pas de nombre maximal de tours, pas de garantie de convergence (épaissir un trait peut refermer une ouverture, qui redevient un défaut).
- Aucun contrôle que l'agent n'a touché **que** les éléments signalés.
- **Un logo est une marque** : agrandir, épaissir, supprimer un élément exige l'accord du client (bon à tirer). Rien de tel n'est prévu ; le prototype supprime et bouche déjà d'office (3.4).
- Non déterministe : deux passages peuvent donner deux fichiers.

Encadrement proposé (à écrire en exigences) : liste fermée d'actions paramétrées ; l'agent **propose**, un script déterministe **applique** ; invariants contrôlés par script (éléments non signalés identiques au bit près, variation d'aire et de position bornée par élément, nombre de composantes) ; plafond de tours ; journal rejouable ; toute suppression ou tout changement visible soumis à approbation humaine avec aperçu avant / après ; résultat approuvé figé et versionné.

### 4.4 Lacunes — **majeur**
- **Plusieurs tailles** : principe posé, jamais essayé ; rien sur la cohérence entre tailles (même ordre, mêmes couleurs) ni sur les seuils qui basculent.
- **Fiche couleurs** : non réalisée ; le DST n'a pas de couleurs, c'est un livrable obligatoire.
- **Réduction de palette** : « non sourcée » ; le traçage ignore tout élément blanc (voir 6.6).
- **Recouvrements entre couleurs voisines** : §5.1 B4 parle des formes cachées ; rien sur le chevauchement à donner aux aplats **adjacents** pour compenser le retrait.
- **Poussée**, traitement des angles et des extrémités de colonnes, raccourcissement des points en courbe serrée : absents (voir 5.4).
- **Points de départ et de fin par objet**, trajets cachés sous les objets suivants, minimisation des coupes : seulement « nœuds par défaut ».
- **Grille de vérification non exécutable** : aucune fonction ne renvoie « refusé » ; le prototype produit des statistiques, jamais un arrêt (les alertes vont dans un JSON, le programme sort en succès).
- **Défaillances d'Ink/Stitch** en cours de chaîne (délai dépassé, sortie d'erreur non vide avec fichier non vide) : comportement non spécifié.

---

## 5. Collecte de savoir

### 5.1 Densité du remplissage : confusion de convention probable — **bloquant** (source + mesure concordantes)
Le processus impose 0,40 mm entre rangs « en surcharge du défaut d'Ink/Stitch (0,25 mm) » (`processus_broderie.md` l. 61 ; collecte l. 206, 407, 408 ; `reglages.py` l. 18).
- Ink/Stitch : `row_spacing_mm` = distance entre **rangs voisins** (`fill_stitch.py` l. 364).
- Wilcom : d'après son propre billet, l'espacement du tatami se mesure un rang sur deux, parce qu'un rang aller est suivi d'un rang retour ([Wilcom — stitch spacing or density](https://wilcom.com/resources/blog/stitch-spacing-or-density)). Un « 0,4 mm » de cette convention vaut ≈ 0,2 mm entre rangs voisins.
- Mesure : l'étoile d'origine (issue d'un fichier maître de numérisation, collecte l. 515) a ses rangs voisins à **0,23 mm** ; notre fichier à 0,40 mm (`exp3.py`). L'image `etoile_cote_a_cote.png` le montre : original plein, le nôtre en croisillons clairs.

Conséquence : le réglage « sourcé » donnerait environ moitié moins de fil de dessus que la pratique. Le défaut d'Ink/Stitch (0,25 mm) était proche de la bonne valeur. À confirmer sur trois ou quatre fichiers professionnels (Madeira) avant de trancher ; d'ici là, statut « sourcé » à retirer.
Pour le satin, la valeur de 0,4 mm est cohérente : Ink/Stitch la définit de crête à crête (`satin_column.py` l. 263-265) et la bordure de l'étoile d'origine mesure ≈ 0,44 mm de crête à crête.

### 5.2 Épaisseur du fil de 0,4 mm — **majeur** (plausible)
« Fil 40 wt ≈ 0,4 mm » (l. 212) repose sur une seule source grand public et contredit la règle de densité : un satin à 0,4 mm de crête à crête pose un fil tous les 0,2 mm. Ce chiffre sert de « détail minimal » (seuil de suppression) et d'épaisseur de rendu dans la comparaison (2.2). À vérifier sur fiche technique de fabricant.

### 5.3 Compensation de traction : par côté ou au total — **majeur** (vérifié côté Ink/Stitch, à vérifier côté sources)
Ink/Stitch applique `pull_compensation_mm` **de chaque côté** (`satin_column.py` l. 296 ; mesure : 0,2 → étoile plus large de 0,4 mm, `exp2.py`). La collecte donne en regard une perte de largeur **totale** de 0,17 à 0,25 mm (l. 208) et des valeurs Wilcom de 0,20 à 0,40 mm (l. 406) sans dire si elles sont par côté. Risque de compensation double. La page Wilcom consultée pendant cette revue ne tranche pas.

### 5.4 Savoir de métier absent — **majeur**
Recherche par mots-clés dans la collecte : aucune occurrence pour la **poussée** (allongement dans le sens des points, à retirer en bout de colonne et de rang), le **traitement des angles** (onglet, recouvrement, coiffe), le **raccourcissement des points** dans les courbes serrées (Ink/Stitch a pourtant `short_stitch_inset`), la **cadence** et le **temps de broderie**, le **sens du tissu**, l'**accord du client**. Manquent aussi : chevauchement entre aplats voisins, sous-couche de bord des remplissages, découpage des colonnes aux jonctions en T et en Y, variation de densité avec le grammage du fil et le contraste fil / tissu, limite de couches superposées, coût d'une coupe (plusieurs secondes) et règle d'arbitrage coupe / trajet caché. Ce sont précisément les savoirs qui séparent un fichier « qui se brode » d'un fichier professionnel.

### 5.5 Affirmations fragiles ou surévaluées — **mineur à majeur**
| Affirmation | Remarque |
|---|---|
| « Risque principal : DST non lus sur Tajima » (l. 488) | Fondé sur des titres de tickets dont le corps n'a pas été lu (l. 790). Niveau « anecdote non lue », pas « risque principal » |
| Profils de tissus (l. 396-405) | Source « lue via un outil de résumé, à relire » : non vérifié, alors que le tableau §2.2 du processus les dit « sourcés » |
| Mesures de formes (§11.1) | « Essais synthétiques réalisés par l'agent de recherche » : scripts et données absents de l'archive, non rejouables |
| « Fill to Satin : plantages signalés » ; masques et filtres « ignorés en silence » | Non éprouvés ici alors qu'un essai de dix minutes suffit |
| Balises de preuve | 12 [ESSAI], 3 [SOURCE], 2 [ANECDOTE], 10 « non vérifié » pour environ 250 liens : la plupart des affirmations n'ont pas de niveau de preuve explicite |
| Sources | Forte part de blogs de vendeurs d'accessoires (hoopingstation, embroideryhooping, embroideryhoopstore, maggieframes) pour des valeurs physiques : fiabilité faible, à doubler par un manuel ou un fabricant |
| `collecte` §6.2 « angle (0°) » | Ne précise pas le sens de rotation, d'où le défaut 6.1 |

### 5.6 Références de comparaison manquantes — **majeur**
Aucun fichier numérisé par un professionnel n'a été téléchargé (point 2.6 laissé à l'utilisateur), alors que tout l'étalonnage en dépend. Aucun numériseur automatique du commerce n'a été pris comme point de comparaison ; c'est pourtant le concurrent direct de l'objectif visé.

---

## 6. Ingénierie du prototype

### 6.1 Signe de l'angle de remplissage inversé — **bloquant** (vérifié)
`geometrie.angle_remplissage` travaille dans le repère du SVG (axe vertical vers le bas) ; Ink/Stitch compte l'angle dans le sens inverse des aiguilles d'une montre (`fill_stitch.py` l. 302). Essai sur une barre de 40 × 8 mm inclinée de 33,75° (`exp7.py`) : la fonction rend 33,75 ; transmis tel quel, Ink/Stitch brode des rangs à ≈ 67° de l'axe long (410 points, 137 de moins de 1 mm) ; avec −33,75 les rangs suivent l'axe (281 points, 36 de moins de 1 mm). Le défaut est resté invisible parce que l'étoile est symétrique. Correctif : transmettre l'opposé de l'angle, et ajouter ce cas aux essais.

### 6.2 Détection des coupes fausse — **majeur** (vérifié)
`comparer._suites_de_sauts` compte toute suite d'au moins 3 sauts, y compris le déplacement initial. C'est exactement le piège décrit par l'essai technique n° 10 et par §6.4 du processus. Voir 1.4.

### 6.3 Comportements silencieux — **majeur** (vérifié par lecture)
- `essai_dessin.py` l. 99 : si l'extension sous bordure ne donne pas un polygone simple, elle est abandonnée sans message.
- Alertes écrites dans le JSON seulement ; code de sortie 0 dans tous les cas ; aucune étape ne s'arrête.
- `inkstitch_io.executer` renvoie la sortie d'erreur d'Ink/Stitch sans jamais la traiter ; un avertissement avec fichier non vide passe.
- `tracer.py` l. 47-49 : un trou sans parent trouvé est ignoré sans message ; l. 32 : contours de moins de 4 points ignorés.
- Suppressions et bouchages d'office du nettoyage (voir 3.4).

### 6.4 Construction du satin — **majeur** (vérifié et plausible)
- Aucune garde de forme (3.3) ; aucune mesure de qualité du résultat (rapport longueur / largeur locale) alors qu'elle suffirait à refuser les cas ratés.
- Les barreaux sont espacés selon le rail extérieur seulement (`satin.py` l. 69) : là où le rail intérieur avance seul, aucun barreau ; dans un éventail, plusieurs barreaux aboutissent au même point intérieur et se touchent sur le rail (plausible : comportement d'Ink/Stitch non garanti dans ce cas).
- Un seul satin pour tout le tour : 89 points de plus de 4 mm sur le trèfle, pour une colonne de 2,3 mm de large en moyenne. « Longueur maximale 7 mm validée » (processus l. 66) signifie seulement qu'Ink/Stitch recoupe les points, pas que le résultat est bon.
- Appariement en temps quadratique avec boucle Python (`satin.py` l. 26-32) : acceptable ici (≈ 860 × 860), lent sur un grand contour.

### 6.5 Séquençage — **majeur** (vérifié par lecture)
Tri par type, puis par chaîne hexadécimale de la couleur, puis par aire. Avec trois couleurs et deux types, les changements de couleur se multiplient et l'ordre des recouvrements n'est pas respecté. L'étoile réussit par chance (deux objets).

### 6.6 Traçage — **mineur** pour le processus (hors périmètre), **majeur** pour les essais
Le fond est « tout pixel dont un canal est sous 245 » : tout élément blanc du dessin disparaît (l'étoile réelle est rouge et **blanche**, collecte l. 515). Les pixels de lissage aux frontières créent des franges ; les calques ne sont ni disjoints ni jointifs par construction.

### 6.7 Testabilité et reproductibilité — **majeur**
- Aucun test automatique ; `essai_dessin.py` est un script unique de 164 lignes qui mêle montage d'essai (retrait, compensation nulle) et logique du processus.
- Dépendances non figées : le guide installe la liste d'Ink/Stitch sans versions exactes ni empreintes ; scikit-image, scipy et Pillow, nécessaires au prototype, ne sont pas dans le guide (seulement dans `LISEZMOI.md`).
- Nos scripts tournent dans l'environnement Python d'Ink/Stitch (`sys.executable`, `inkstitch_io.py` l. 48) : couplage des versions de bibliothèques ; préférable de séparer les deux environnements.
- `verifier_installation.py` : plage de points très large (1700 à 2100 pour 1897 attendus, alors que l'export est déterministe : une égalité stricte détecterait une dérive de version) ; ne contrôle ni le satin isolément, ni une coupe, ni la sortie d'erreur vide.
- Guide §8 : dossier de configuration fixe `/tmp/inkstitch_config`, contraire à la règle « privé par appel ».

### 6.8 Frontière de licence — respectée dans le code, deux points à surveiller — **mineur** (vérifié)
Aucun import d'Ink/Stitch ni d'`inkex` dans `prototype/` ; appel en sous-processus. À surveiller : (a) les palettes de fils `.gpl` du dépôt Ink/Stitch sont sous GPL-3 (collecte l. 348) : les lire sur place ne pose pas de difficulté, les **redistribuer** avec notre outil en pose ; (b) « réutiliser la méthode, pas le code » de Fill to Stroke (collecte l. 316) : garder une trace écrite d'une réécriture indépendante.

---

## 7. Risques majeurs pour l'objectif

1. **Croire à une qualité non mesurée** (bloquant). Le critère actuel valide des fichiers visiblement inférieurs ; chaque itération optimisée sur lui peut dégrader le résultat réel (cas de la compensation).
2. **Absence d'essai sur tissu** (bloquant pour toute revendication). Retrait, fronces, couverture, lisibilité ne se déduisent pas d'un fichier. Sans au moins quelques broderies sous-traitées, la densité (5.1), la compensation (5.3) et l'épaisseur du fil (5.2) restent des paris.
3. **Le satin automatique est le cœur du problème et il n'est qu'effleuré.** Logos = lettres et traits. Seul l'anneau existe, il échoue sur les lettres à contre-forme. Découper une forme en colonnes aux angles et aux jonctions est le problème qu'aucun outil libre n'a résolu (collecte l. 305). Le risque d'aboutir à « revue humaine obligatoire partout » est élevé ; il faut le dire et prévoir le poste de revue comme partie normale du flux.
4. **Entrée réelle jamais essayée.** Dessins vectoriels de clients : formes superposées, traits, textes vectorisés, dégradés, découpes, unités variées. Rien de cela n'a traversé la chaîne.
5. **Agent modifiant un logo sans contrôle ni accord.** Risque de qualité et risque commercial.
6. **Conventions d'unités entre sources** (espacement un rang sur deux, crête à crête, par côté). Trois cas relevés dans cette revue ; d'autres sont probables.
7. **Dépendance à une version figée d'Ink/Stitch** dont le comportement en cas limites (barreaux qui se touchent, satins fermés) n'est pas contractuel.

---

## 8. Les dix actions prioritaires

| # | Action | Pourquoi | Comment vérifier |
|---|---|---|---|
| 1 | **Retirer le statut « concluant » des deux essais et le statut « sourcé » de la densité de remplissage ; trancher la convention d'espacement** | Constats 1.4, 2.1, 5.1 : conclusions non soutenues, densité probablement moitié trop faible | Mesurer l'espacement entre rangs voisins et la densité de fil sur au moins quatre fichiers professionnels (Madeira) avec la méthode de `exp3.py` ; fixer le réglage dans la plage observée |
| 2 | **Remplacer le recouvrement des surfaces par une batterie de mesures de qualité** (tableau 2.4), avec plages admises tirées de fichiers professionnels | Le critère actuel ne voit ni l'ordre, ni la sous-couche, ni la direction, et récompense la surdensité | Essai par mutation : chacune des variantes dégradées du tableau 2.1 doit être refusée par au moins une mesure ; les fichiers professionnels doivent tous passer |
| 3 | **Corriger les défauts vérifiés du prototype** : signe de l'angle (6.1), détection des coupes par motif brut (6.2), garde et mesure de qualité du satin (3.3), séquençage par recouvrement (6.5), abandons silencieux (6.3) | Défauts certains, peu coûteux, qui faussent tout essai suivant | Un test automatique par défaut : barre inclinée, fichier avec et sans coupe, lettres A et P refusées, trois couleurs superposées |
| 4 | **Écrire les exigences séparément, avec critères d'acceptation mesurables, avant tout nouveau code** | 4.1 : sans définition de « réussi », pas de méthode scientifique possible ; demande explicite du commanditaire (quoi, pas comment) | Chaque exigence a un essai nommé ; aucun nom d'outil, d'option ou de format interne dans le document d'exigences |
| 5 | **Constituer un jeu d'essai réel et le figer** : dessins vectoriels variés (échantillons SVG d'Ink/Stitch, logos libres, formes synthétiques de `exp5.py`), fichiers professionnels de référence, et une part tenue à l'écart | 1.1, 1.2 : deux cas circulaires, réglages ajustés dessus | Liste versionnée avec empreintes ; réglages et seuils figés avant passage de la part tenue à l'écart ; le lettrage « Embroidermodder » en fait partie |
| 6 | **Obtenir des broderies réelles sans posséder de machine** : atelier partagé, prestataire, démonstration chez un revendeur ; à défaut, relecture à l'aveugle de quelques fichiers par un numériseur professionnel | Risque n° 2 : seul juge de la densité, de la compensation, de la lisibilité | Mire d'étalonnage (colonnes de 1 à 8 mm, remplissages à 0,2 / 0,25 / 0,3 / 0,4 mm, texte de 3 à 8 mm) brodée sur deux tissus ; mesures au pied à coulisse reportées dans le profil |
| 7 | **Traiter le satin comme le chantier principal** : découpage des formes en parties d'épaisseur homogène, colonnes ouvertes, coupe aux angles vifs et aux jonctions, extrémités ; refus automatique au-delà d'un taux de points en biais | Risque n° 3 ; 3.2, 3.3, 6.4 | Mesure « longueur / largeur locale » : cible proche des originaux (99ᵉ centile sous ≈ 1,4) sur anneau, cadre, lettres E, A, P, B et trèfle |
| 8 | **Encadrer l'étape de mise à jour du dessin par un agent** (4.3) : actions fermées, application par script, invariants, plafond de tours, approbation humaine de toute modification visible | Contraire aux principes du projet telle qu'écrite ; risque commercial sur les marques | Essais : l'agent ne peut pas modifier un élément non signalé (contrôle au bit près) ; rejouer le journal redonne le même fichier ; aucune suppression sans trace d'approbation |
| 9 | **Refondre les règles de classement** : retirer la compacité comme condition, ajouter la règle des petites formes compactes, traiter les filets fins en point droit, appliquer réellement le mode « revue » (arrêt), définir la marge « proche d'un seuil », déclarer le texte dans la fiche de cadrage | 3.1, 3.4, 3.5 | Tableau de formes synthétiques de `exp5.py` étendu, avec la décision attendue écrite à l'avance par un humain ; taux d'accord rapporté |
| 10 | **Rendre la vérification exécutable et la chaîne reproductible** : grille de §6 codée avec refus et code de sortie, fiche couleurs, temps estimé ; versions figées avec empreintes ; essai d'une entrée SVG réelle à deux tailles ; mise en cohérence des documents (version, journal, briques, contradictions de 4.2) ; vérification des conventions d'unités de chaque valeur reprise d'une source (5.3, 5.2) | 4.2, 4.4, 6.7 ; risque n° 6 | Une commande unique rejoue tous les essais et sort en erreur au premier refus ; même empreinte de fichier sur deux installations propres |

---

## Annexe — Expériences de cette revue

| Script (`critique_scratch/`) | Objet |
|---|---|
| `exp1.py` | Reproduction des IoU (0,900 et 0,936, identiques aux rapports) ; enregistrements bruts ; sensibilité à l'épaisseur dessinée et à l'alignement |
| `exp2.py` | Onze variantes de l'étoile (angle, densité, sous-couche, ordre, bordure) et leur IoU |
| `exp3.py` | Densité de fil, espacement des rangs, distribution des directions par bloc de couleur |
| `exp4.py` | Direction précise des remplissages ; rapport longueur / largeur locale des satins ; IoU sous meilleure translation |
| `exp5.py`, `exp6.py` | Classement de 24 formes synthétiques ; satin « anneau » sur lettres A et P, cadre, anneau ; mesure sans sous-couche |
| `exp7.py` | Convention de signe de l'angle de remplissage |
| (en ligne) | Déterminisme : trois exports du même SVG, empreintes identiques |

Limites de cette revue : pas plus d'essai sur tissu que le projet ; la mesure « longueur / largeur locale » est une approximation (largeur estimée sur l'emprise des points eux-mêmes) étalonnée sur un anneau parfait et sur les originaux ; la convention Wilcom d'espacement repose sur un billet de l'éditeur et une mesure sur un seul fichier, à confirmer (action n° 1) ; la sémantique Wilcom de la compensation n'a pas pu être tranchée.
