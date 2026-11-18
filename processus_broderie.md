# Processus générique de broderie machine — D'un dessin à un fichier machine

> ⚠️ **Avertissement — contenu généré par intelligence artificielle.** Ce document a été produit avec l'aide d'une IA (Claude, Anthropic) et n'a pas été validé par un spécialiste de la broderie machine. Il peut contenir des erreurs. Toute information, tout réglage et tout fichier produit — en particulier les fichiers machine (.dst) — doivent être vérifiés par un professionnel qualifié avant usage. **Un fichier machine erroné peut endommager la brodeuse** (casse d'aiguille, bourrage, contrainte mécanique), abîmer le tissu et présenter un risque pour l'opérateur : ne jamais lancer une broderie sans contrôle préalable par un spécialiste et premier essai à vitesse réduite, sur chute de tissu.

> **Document vivant** — version **1.0** — 16 novembre 2026 (journal en fin de document).
> Ce document décrit l'**enchaînement des étapes**, les décisions et les contrôles. Les exigences mesurables sont dans `exigences_broderie.md` (citées « EX-… ») ; la réalisation technique dans `architecture_broderie.md` (« ARCH §n ») ; le savoir et les sources dans `collecte_de_savoir_broderie.md` (« CS §n »).

---

## 0. Périmètre et principes

**Entrée** : un dessin vectoriel (entrée principale) ; une image peut être acceptée après vectorisation, signalée comme telle.
**Sortie** : pour une taille, un tissu et une machine donnés : fichier machine, fiche couleurs, aperçu, rapport.

**Principes**
- **Générique** : décisions fondées sur la géométrie mesurée à la taille brodée et sur un profil de réglages.
- **Source unique** : le dessin d'entrée n'est jamais modifié ; tout est dérivé.
- **Taille = paramètre** ; plusieurs tailles = plusieurs passages indépendants (EX-FONC-03).
- **Aucune modification sans approbation** ; les modifications visibles d'un dessin client exigent l'accord du client (EX-COND-01, -03).
- **Échouer quand c'est utile, jamais en silence** : tout point bloquant arrête la chaîne avec la liste complète ; tout ce qui est écarté ou corrigé est journalisé (EX-COND-07, -08).
- **La qualité se mesure** : la grille de vérification décide (EX-VERIF-01) ; la silhouette n'est qu'un indicateur secondaire.
- **Aucune revendication de qualité sans broderie réelle** (EX-VERIF-05).
- Documentation en français.

---

## 1. Organisation en flux

| | **Flux A — Simple** | **Flux B — Avancé** |
|---|---|---|
| Couleurs | 1 fil | Plusieurs fils |
| Types de points | 1 seul, choisi selon le dessin | Plusieurs, par objet |
| Texte | Selon le type unique | Sous-flux texte (§5.2) |
| Usage | Dessins simples ; banc d'essai | Logos multicolores |

---

## 2. Entrées par commande (fiche de cadrage)

| Champ | Exemple | Effet |
|---|---|---|
| Taille(s) brodée(s) | 100 mm de large ; 250 mm | Une passe par taille |
| Tissu | Piqué, maille, sergé, polaire, casquette, éponge | Profil de réglages |
| Fil | 40 wt / 60 wt | Détail minimal, densités |
| Machine | Tajima ; nombre d'aiguilles ; tambour | Couleurs maximum, champ, format |
| **Réglage de coupe de la machine** | 3 sauts consécutifs = 1 coupe | Doit correspondre au fichier produit |
| **Zones de texte** | « le mot X est un texte » | Les textes vectorisés ne sont pas détectables automatiquement : ils doivent être déclarés pour que les règles de texte s'appliquent |
| Personne habilitée à approuver | Client / opérateur | Approbations (§3.3) |
| Flux | A / B | Chaîne utilisée |

---

## 3. Étapes communes

### 3.1 Mise à l'échelle
Conversion à la taille brodée réelle ; toutes les mesures suivantes se font à cette échelle. Contrôle : dimensions = taille demandée ; dessin dans le champ du tambour avec marge (EX-QUAL-02).

### 3.2 Normalisation du dessin
Chaque correction est journalisée ; ce qui ne peut pas être corrigé arrête la chaîne. Détails techniques : ARCH §2 et CS §6, §15.4.

| Constat | Traitement |
|---|---|
| Dégradé linéaire défini relativement à l'objet | Converti en coordonnées absolues |
| Dégradé radial, transparence partielle | Couleur à plat équivalente |
| Objet invisible | Supprimé |
| Masque, filtre, marqueur, motif | Aplati si possible, sinon arrêt |
| Contour qui se croise | Réparé |
| Objet avec fond et trait | Séparé en deux objets |
| Texte non vectorisé, image intégrée | Arrêt : décision humaine |

**Statut** : non implémenté dans le prototype (aucune entrée vectorielle réelle traitée à ce jour).

### 3.3 Passe de simplification (systématique, encadrée)
1. **Détection** (automatique) : éléments négligeables, ouvertures qui se refermeront (< 0,8 mm), détails sous l'épaisseur du fil, jambages sous la largeur satin minimale, couleurs en excès. Chaque défaut reçoit un identifiant, une mesure, un seuil et une **action proposée**.
2. **Proposition** : un agent (humain ou logiciel) peut proposer des actions, **uniquement dans une liste fermée et paramétrée** (aujourd'hui : supprimer, boucher ; prévues : agrandir, épaissir, fusionner, simplifier, aplatir) (EX-COND-04).
3. **Approbation** : toute action est approuvée explicitement ; toute **modification visible** d'un dessin client est approuvée par le client sur aperçu avant / après (EX-COND-03). Sans approbation : arrêt avec la liste des actions proposées (EX-COND-01).
4. **Application déterministe** des seules actions approuvées ; contrôle que les éléments non visés sont inchangés au bit près (EX-COND-02) ; journal rejouable (EX-COND-05).
5. **Re-mesure** ; **au plus 3 tours** ; au-delà, arrêt avec les défauts restants (EX-COND-06).
6. Le dessin approuvé est figé et versionné.

### 3.4 Mesures et découpage
- Mesures par forme : largeur maximale, largeur moyenne, allongement, nombre de trous, appendices fins (ARCH §4.1).
- **Forme mixte** (partie épaisse avec appendice fin, ex. disque avec tige) : découpage en parties d'épaisseur homogène **avant** classement. Statut : détecté, découpage non implémenté ⇒ arrêt « découpage requis ».
- Toute mesure à ±10 % d'un seuil est signalée (EX-COND-11).

### 3.5 Classement (table de décision)
| Condition, à la taille brodée | Décision | Mode |
|---|---|---|
| Forme mixte | Découpage requis | Revue (arrêt) |
| Largeur < 0,4 mm et forme allongée (filet) | Point droit sur la ligne médiane | Auto |
| Largeur < 0,4 mm et forme compacte | Supprimer | Alerte (approbation requise) |
| Largeur < 1 mm ou aire < 1,5 mm² | Point droit | Auto |
| Colonne : allongement ≥ 3, largeur moyenne ≥ 1 mm, largeur maximale ≤ 7 mm | Satin | Semi-auto (garde, §3.6) |
| Petite forme compacte, largeur maximale ≤ 6 mm (points, pastilles, barres courtes) | Satin | Semi-auto |
| Colonne large (allongement ≥ 3, largeur ≤ 10 mm) | Satin découpé ou remplissage | Revue (arrêt) |
| Sinon | Remplissage | Auto |
| Texte déclaré sous la hauteur minimale (5 mm ; capitales 3,8 mm) | Agrandir, épaissir, fil 60 wt ou supprimer | Alerte bloquante |
| Dégradé linéaire sur une surface | Remplissage en dégradé (flux B) ou couleur à plat | Choix humain (critère à définir) |

Seuils 3 / 6 mm / 1,5 mm² / ±10 % : à étalonner. Décisions comparées à un jugement écrit à l'avance (EX-VERIF-06).

### 3.6 Construction et gardes
- **Aucun repli silencieux** : une construction non disponible arrête la chaîne (EX-COND-07).
- Satin : construction en anneau disponible ; **garde** de qualité avant production (EX-COND-10). Refus = arrêt, sauf approbation explicite de forcer (journalisée). Satins ouverts, satins découpés aux angles, point droit sur ligne médiane : non disponibles.
- Remplissage : angle choisi, sous-couche avec retrait, extension sous une bordure qui le recouvre.

### 3.7 Séquençage
1. Un objet qui en recouvre un autre est brodé après lui (EX-QUAL-08).
2. Parmi les objets libres : même couleur d'abord (moins de changements), puis ordre d'empilement.
3. En cas de conflit entre recouvrement et nombre de couleurs, **le recouvrement l'emporte**.
4. Bordures, contours et détails fins en dernier ; travail du centre vers l'extérieur ; départ et fin au centre (casquette : bas-centre).
5. Tout déplacement de plus de 10 mm est coupé (EX-QUAL-10).

### 3.8 Production du fichier
Conversion par un composant tiers appelé comme programme séparé (ARCH §5). Le succès se juge sur le contenu, jamais sur le seul code de retour.

### 3.9 Vérification
Grille exécutable (EX-QUAL-01 à -13) ; refus dès qu'un critère n'est pas tenu ; code de résultat : 0 accepté, 1 refusé, 2 arrêté. La grille est validée par mutation (EX-VERIF-02) et sera étalonnée sur fichiers professionnels (EX-VERIF-03).

### 3.10 Livrables
Fichier machine, fiche couleurs, aperçu, rapport (corrections, approbations, mesures, décisions, alertes, grille), dessin approuvé figé.

---

## 4. Flux A — Simple
Type unique selon le dessin dominant : trait → point triple ; aplats → remplissage ; lettrage épais → satin. Les éléments incompatibles sont convertis ou signalés. Étapes : §3.1 à §3.10, avec 0 changement de couleur attendu.

## 5. Flux B — Avancé

### 5.1 Spécificités
- **Réduction de palette** : couleurs de marque figées ; fusion des teintes proches ; choix dans le nuancier de l'atelier ; écart résiduel signalé (méthode non éprouvée).
- **Recouvrements** : découpe des parties cachées ; chevauchement entre aplats voisins pour compenser le retrait (valeur à étalonner) ; pas d'évidement sous un petit texte.

### 5.2 Sous-flux texte (zones de texte déclarées)
| Taille | Traitement |
|---|---|
| Jambages > 7 mm | Remplissage, bordure satin éventuelle |
| Jambages 1,5–7 mm | Satin semi-automatique, revue humaine obligatoire |
| Petit texte de marque récurrent | Police numérisée une fois, réutilisée |
| Jambages 1–1,5 mm | Satin étroit, fil fin conseillé, revue obligatoire |
| Sous les seuils | Alerte bloquante |
Capitales seules sous 4 mm de hauteur.

---

## 6. Broderie réelle (indispensable avant toute revendication)
- **Recette machine** (une fois par machine) : fichier à 2 couleurs, 1 coupe, 1 arrêt ; vérifier lecture, coupe, arrêt.
- **Mire d'étalonnage** (sans machine propre : atelier partagé, prestataire, revendeur) : colonnes satin de 1 à 8 mm ; remplissages à 0,20 / 0,25 / 0,30 / 0,40 mm entre rangs voisins ; texte de 3 à 8 mm ; sur deux tissus. Mesures au pied à coulisse reportées dans le profil.
- **Par dessin** : tissu et entoilage réels ; observation : repérage, rétrécissement, fronces, couverture, lisibilité, jours entre objets (EX-QUAL-14, -15) ; photo jointe ; réglages ajustés.
- **Comparaison de référence** : même dessin numérisé par un professionnel.

---

## 7. Profil de réglages (valeurs de départ, conventions : ARCH §2)

| Réglage | Valeur | Statut |
|---|---|---|
| Espacement de remplissage (rangs voisins) | 0,25 mm | À étalonner (plage 0,20–0,25 ; original mesuré 0,23) |
| Sous-couche de remplissage | Retrait 0,4 mm ; espacement 3 × | Sourcé |
| Espacement de satin (crête à crête) | 0,40 mm | Sourcé |
| Longueur maximale de point de satin | 7 mm, toujours imposée | Sourcé |
| Sous-couche satin | < 2 mm marche centrale ; 2–4 mm contour ; ≥ 4 mm contour + zigzag | Sourcé |
| Compensation de traction (par côté) | Coton/sergé 0,20 ; tee-shirt 0,35 ; polaire 0,40 mm | Sourcé (Wilcom), à étalonner |
| Compensation de poussée | ≈ 0,2 mm en bout de colonne | Sourcé, non appliqué |
| Longueur minimale de point | 0,3 mm | Sourcé |
| Détail minimal | 0,4 mm | À étalonner (épaisseur du fil ≈ 0,2 mm selon fiches techniques) |
| Seuils de classement | Allongement 3 ; petite forme 6 mm ; aire 1,5 mm² ; marge ±10 % | À étalonner |
| Seuil de coupe des déplacements | 10 mm | À étalonner |
| Vitesse / coupe / changement de couleur | 750 points/min ; 3,5 s ; 10 s | Sourcé / sourcé / non vérifié |

---

## 8. Suivi des points ouverts

Légende : ✅ fermé · 🟡 partiel · ⛔ ouvert · 🧑 décision de l'utilisateur.

### 8.1 Issus de la revue critique (16/11/2026)
| # | Point | Statut |
|---|---|---|
| R1 | Conclusions « concluant » des essais | ✅ Retirées ; rapports réécrits (v2.0) |
| R2 | Densité de remplissage (confusion de conventions) | 🟡 Corrigée (0,25 mm entre rangs voisins) ; à confirmer sur fichiers professionnels |
| R3 | Critère de réussite limité à la silhouette | ✅ Grille de 13 critères, validée par mutation ; silhouette en indicateur secondaire |
| R4 | Signe de l'angle de remplissage | ✅ Corrigé, test automatique |
| R5 | Satin en anneau appliqué aux lettres | ✅ Garde de construction, test automatique |
| R6 | Coupes comptées sur le déplacement initial | ✅ Lecture brute par motif, test automatique |
| R7 | Séquençage par code de couleur | ✅ Séquençage par recouvrements, test automatique |
| R8 | Comportements silencieux (suppressions, replis, sorties d'erreur) | ✅ Arrêts et alertes ; approbations explicites |
| R9 | Exigences mesurables absentes | ✅ `exigences_broderie.md` |
| R10 | « Quoi » et « comment » mêlés | ✅ Séparés (exigences / architecture / processus) |
| R11 | Agent de mise à jour non encadré | 🟡 Encadré par écrit (§3.3) ; liste d'actions et boucle bornée à implémenter |
| R12 | Règles de classement (compacité, filets, petites formes, formes mixtes) | ✅ Refondues, 11 formes testées contre un jugement écrit |
| R13 | Double retrait dans le montage d'essai | ✅ Corrigé |
| R14 | Configuration de production jamais évaluée | ✅ Évaluée |
| R15 | Savoir de métier absent (poussée, angles, points courts, temps) | 🟡 Documenté (CS §19) ; pas encore appliqué |
| R16 | Jeu d'essai figé avec part tenue à l'écart | ⛔ À constituer (le lettrage reste vierge) |
| R17 | Fichiers professionnels de référence | ⛔ 🧑 Téléchargement manuel nécessaire |
| R18 | Broderie réelle | ⛔ Pas de machine |
| R19 | Environnements Python séparés, versions figées | 🟡 Variable prévue ; un seul environnement dans le prototype ; liste des versions consignée |

### 8.2 Points antérieurs encore ouverts
| # | Point | Statut |
|---|---|---|
| P1 | Normalisation d'un vrai dessin vectoriel | ⛔ Non implémentée, jamais essayée |
| P2 | Deux tailles d'un même dessin | ⛔ Jamais essayé |
| P3 | Satins ouverts, découpage aux angles, formes mixtes | ⛔ Chantier principal |
| P4 | Réduction de palette, références de fil | ⛔ |
| P5 | Recette machine | ⛔ Dépend de R18 |
| P6 | Réglage de coupe des machines (3 à 5 sauts) | 🟡 Champ de la fiche de cadrage |

---

## Journal des versions
| Version | Date | Changements |
|---|---|---|
| 0.1 | 15/11/2026 | Ébauche |
| 0.2 | 15/11/2026 | Export, choix des points, vérification |
| 0.3 | 15/11/2026 | Flux A et B |
| 0.4 | 15/11/2026 | Processus générique ; dessin d'exemple en annexe |
| 0.5 | 15/11/2026 | Intégration des essais techniques et recherches ; suivi des points ouverts |
| 0.5.1 | 15/11/2026 | Renvoi vers le guide d'installation |
| 0.6 | 15/11/2026 | Décisions : format, taille en paramètre, passe de simplification, français |
| 0.7 | 16/11/2026 | Essai n° 1 (trèfle) |
| 0.8 | 16/11/2026 | Essai n° 2 (étoile) |
| 0.9 | 16/11/2026 | Retrait des références à un dessin particulier |
| 1.0 | 16/11/2026 | **Refonte après revue critique** : exigences et architecture séparées ; passe de simplification encadrée (liste fermée, approbation, application déterministe, 3 tours) ; table de classement refondue ; séquençage par recouvrements ; densité corrigée ; vérification exécutable ; textes déclarés ; mire d'étalonnage ; suivi R1–R19 |
