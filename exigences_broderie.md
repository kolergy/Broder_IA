# Exigences — Chaîne de broderie machine

> ⚠️ **Avertissement — contenu généré par intelligence artificielle.** Ce document a été produit avec l'aide d'une IA (Claude, Anthropic) et n'a pas été validé par un spécialiste de la broderie machine. Il peut contenir des erreurs. Toute information, tout réglage et tout fichier produit — en particulier les fichiers machine (.dst) — doivent être vérifiés par un professionnel qualifié avant usage. **Un fichier machine erroné peut endommager la brodeuse** (casse d'aiguille, bourrage, contrainte mécanique), abîmer le tissu et présenter un risque pour l'opérateur : ne jamais lancer une broderie sans contrôle préalable par un spécialiste et premier essai à vitesse réduite, sur chute de tissu.

> Version 1.0 — 16 novembre 2026
> Ce document dit **ce qui est exigé**, jamais comment le réaliser : aucun nom d'outil, de bibliothèque, de format interne ou d'algorithme. Les choix de réalisation sont dans `architecture_broderie.md` ; l'enchaînement des étapes dans `processus_broderie.md`.
> Chaque exigence a un critère d'acceptation mesurable, un essai nommé et un statut : **vérifié** (essai automatique ou mesure passés), **partiel**, **non vérifié**. Les seuils marqués « à étalonner » sont des valeurs de départ qui seront fixées après mesure sur fichiers professionnels et broderies réelles.

---

## 1. Objet et définitions

**Objet** : produire, à partir d'un dessin fourni par un client, un fichier machine de broderie de qualité professionnelle, à une ou plusieurs tailles, avec les documents nécessaires à l'atelier.

| Terme | Définition |
|---|---|
| Dessin | Illustration vectorielle fournie par le client (formes, traits, textes vectorisés, couleurs) |
| Fichier machine | Fichier lu par la brodeuse : suite de points, sauts, coupes, changements de couleur |
| Objet | Partie du dessin brodée d'un seul tenant, avec un seul type de point |
| Point en biais | Point de satin plus long que 1,5 fois la largeur locale de la colonne qu'il traverse |
| Déplacement | Mouvement de l'aiguille sans couture entre deux objets |
| Modification visible | Toute modification du dessin qui change son apparence (suppression, agrandissement, épaississement, fusion, simplification, changement de couleur) |
| Approbation | Accord explicite et tracé d'une personne habilitée (client ou opérateur selon le cas) |

---

## 2. Exigences fonctionnelles

| N° | Exigence | Critère d'acceptation | Essai | Statut |
|---|---|---|---|---|
| EX-FONC-01 | Le système accepte un dessin vectoriel en entrée | Un dessin vectoriel de référence est traité de bout en bout | Essai « dessin vectoriel réel » | **non vérifié** (seules des images ont été traitées) |
| EX-FONC-02 | Le système peut accepter une image matricielle, après vectorisation signalée comme telle | Le rapport indique que l'entrée a été vectorisée et journalise tout élément écarté | Essais trèfle et étoile | partiel |
| EX-FONC-03 | La taille brodée est un paramètre ; plusieurs tailles peuvent être demandées pour un même dessin | Deux tailles d'un même dessin donnent deux fichiers dont les dimensions respectent EX-QUAL-02 ; les décisions dépendantes de la taille sont recalculées et rapportées | Essai « deux tailles » | **non vérifié** |
| EX-FONC-04 | Le système produit un fichier machine lisible par une brodeuse Tajima standard | Le fichier est lu sans erreur par la brodeuse cible ; coupes, arrêts et changements de couleur exécutés | Recette machine | **non vérifié** (pas de machine) |
| EX-FONC-05 | Le système produit une fiche couleurs | La fiche donne, par bloc : ordre, couleur, référence de fil, nombre de points, longueur de fil ; plus dimensions, temps estimé, réglage de coupe attendu de la machine | Contrôle de la fiche | partiel (référence de fil non renseignée) |
| EX-FONC-06 | Le système produit un rapport | Le rapport contient : corrections, mesures, décisions, alertes, approbations, résultat de la vérification | Contrôle du rapport | partiel |
| EX-FONC-07 | Le système produit un aperçu du résultat | Image du plan de points jointe au rapport | Contrôle de l'aperçu | partiel |
| EX-FONC-08 | Reproductibilité | Mêmes entrées, mêmes réglages, mêmes approbations → fichier machine identique octet pour octet | Trois exécutions identiques | vérifié (revue critique) |

---

## 3. Exigences de qualité du fichier machine

Toutes se mesurent sur le fichier produit. Elles s'appliquent de la même façon à tout fichier de comparaison.

| N° | Exigence | Critère d'acceptation | Essai | Statut |
|---|---|---|---|---|
| EX-QUAL-01 | Le fichier est complet et lisible | Lecture sans erreur, au moins un point, marque de fin présente | Grille | vérifié |
| EX-QUAL-02 | Les dimensions respectent la taille demandée | Écart ≤ 0,5 mm sur la dimension demandée (à étalonner) | Grille | vérifié (mesure) |
| EX-QUAL-03 | Aucun point trop court | Aucun point < 0,3 mm, à la précision de la grille du fichier près (tolérance 0,05 mm) | Grille + mutation | vérifié |
| EX-QUAL-04 | Points de satin non excessifs | Aucun point de satin > 7 mm | Grille + mutation | vérifié |
| EX-QUAL-05 | Satin sans points en biais | Part de points en biais ≤ 2 % ; 99ᵉ centile du rapport longueur / largeur locale ≤ 1,4 (à étalonner ; fichiers de comparaison : 0 % et 1,16 à 1,23) | Grille + mutation | vérifié (la mesure détecte ; nos fichiers ne passent pas) |
| EX-QUAL-06 | Densité de remplissage dans la plage professionnelle | Espacement entre rangs voisins dans 0,20–0,30 mm (à étalonner sur fichiers professionnels) | Grille + mutation | vérifié (mesure) ; plage non étalonnée |
| EX-QUAL-07 | Sous-couche présente là où elle est nécessaire | Sous-couche détectée sur tout remplissage de plus de 20 mm² et tout satin de largeur ≥ 2 mm | Grille + mutation | vérifié |
| EX-QUAL-08 | Ordre de broderie respectant les recouvrements | Aucun objet de dessus brodé avant un objet qu'il recouvre | Grille + mutation | vérifié (cas bordure / remplissage) |
| EX-QUAL-09 | Nombre de changements de couleur maîtrisé | Nombre de blocs = nombre prévu par le séquençage ; écart au minimum possible rapporté | Grille | vérifié |
| EX-QUAL-10 | Déplacements longs coupés | Tout déplacement (hors déplacement initial) de plus de 10 mm est coupé (à étalonner) | Grille | vérifié (mesure) |
| EX-QUAL-11 | Concentration de pénétrations maîtrisée | Maximum de pénétrations par mm² rapporté ; seuil à fixer | Grille (information) | non vérifié (seuil inconnu) |
| EX-QUAL-12 | Temps de broderie estimé | Temps estimé rapporté, avec l'origine des paramètres de vitesse | Grille (information) | partiel |
| EX-QUAL-13 | Densité du satin dans la plage professionnelle | Espacement de crête à crête estimé dans 0,25–0,55 mm (à étalonner ; estimateur biaisé d'environ −20 %) | Grille + mutation | vérifié (mesure) ; plage non étalonnée |
| EX-QUAL-14 | Pas de jour visible entre objets voisins après retrait du tissu | Aucun liseré de tissu visible à l'essai sur tissu | Essai sur tissu | **non vérifié** |
| EX-QUAL-15 | Lisibilité des textes | Texte lisible à l'essai sur tissu, à la taille demandée | Essai sur tissu | **non vérifié** |

---

## 4. Exigences de conduite (comportement du système)

| N° | Exigence | Critère d'acceptation | Essai | Statut |
|---|---|---|---|---|
| EX-COND-01 | Aucune modification du dessin sans approbation | Toute suppression, tout bouchage, toute modification visible non approuvée arrête la chaîne avec la liste des actions proposées | Test automatique « aucune suppression sans approbation » | vérifié |
| EX-COND-02 | Les modifications approuvées ne touchent que les éléments visés | Éléments non visés identiques au bit près après application | Test automatique « corrections approuvées » | vérifié |
| EX-COND-03 | Les modifications visibles d'un dessin client sont approuvées par le client | Trace d'approbation client (aperçu avant / après) pour toute modification visible avant production | Contrôle du rapport | **non vérifié** (procédure à définir) |
| EX-COND-04 | Les actions de mise à jour du dessin forment une liste fermée et paramétrée | Aucune action hors liste ne peut être appliquée ; chaque action a ses paramètres et ses bornes | Test « action hors liste refusée » | partiel (supprimer, boucher seulement) |
| EX-COND-05 | Les actions sont appliquées de façon déterministe ; le journal permet de rejouer | Rejouer le journal sur le dessin d'origine redonne le même dessin modifié | Test « rejeu du journal » | partiel |
| EX-COND-06 | La boucle de correction est bornée | Nombre maximal de tours fixé ; au-delà, arrêt avec les défauts restants | Test « plafond de tours » | **non vérifié** (boucle non implémentée) |
| EX-COND-07 | Aucun comportement silencieux | Tout élément écarté, tout repli, toute sortie d'erreur d'un composant tiers apparaît au rapport ; aucun repli d'un type de point vers un autre sans approbation | Revue de code + tests | partiel |
| EX-COND-08 | Arrêt quand une décision humaine est requise | Tout objet en mode « revue » ou « alerte » arrête la chaîne s'il n'est pas approuvé ; tous les points bloquants sont listés ensemble | Essais trèfle et étoile sans approbation | vérifié |
| EX-COND-09 | Code de résultat exploitable | Résultat distinct pour : accepté, refusé par la vérification, arrêté (points bloquants) | Essais | vérifié |
| EX-COND-10 | Garde de construction des colonnes | Une forme dont la colonne construite aurait plus de 2 % de traverses en biais ou une traverse hors de la forme est refusée avant production | Test automatique « lettres A et P refusées » | vérifié |
| EX-COND-11 | Mesures proches d'un seuil signalées | Toute mesure à ±10 % d'un seuil de décision est signalée | Contrôle du rapport | vérifié (signalement) |

---

## 5. Exigences de vérification et de validation

| N° | Exigence | Critère d'acceptation | Essai | Statut |
|---|---|---|---|---|
| EX-VERIF-01 | La vérification est exécutable et refuse | La grille renvoie « refusé » dès qu'un critère n'est pas tenu | Essais | vérifié |
| EX-VERIF-02 | La grille est validée par mutation | Chaque dégradation applicable d'un fichier de référence est détectée par l'exigence qui la vise | Validation par mutation | vérifié (8 types de dégradations sur 2 dessins) |
| EX-VERIF-03 | Les seuils sont étalonnés sur des fichiers professionnels | Au moins quatre fichiers numérisés par des professionnels passent la grille ; plages fixées à partir de leurs mesures | Étalonnage | **non vérifié** (aucun fichier professionnel disponible) |
| EX-VERIF-04 | Un jeu d'essai figé comporte une part tenue à l'écart | Liste versionnée avec empreintes ; réglages et critères figés avant passage de la part tenue à l'écart | Jeu d'essai | **non vérifié** |
| EX-VERIF-05 | Aucune revendication de qualité sans broderie réelle | Toute affirmation de qualité « production » s'appuie sur au moins une broderie réelle mesurée | Revue des rapports | appliqué (aucune revendication) |
| EX-VERIF-06 | Les décisions de classement sont comparées à un jugement écrit à l'avance | Taux d'accord rapporté sur un tableau de formes dont la décision attendue est écrite par un humain avant l'essai | Test automatique « classement » | vérifié (11 formes) |

---

## 6. Exigences d'exploitation

| N° | Exigence | Critère d'acceptation | Essai | Statut |
|---|---|---|---|---|
| EX-EXPL-01 | Installation reproductible | Une installation propre suivant le guide passe la vérification d'installation avec des résultats identiques | Vérification d'installation | vérifié (une installation) |
| EX-EXPL-02 | Versions des composants figées | Versions exactes consignées ; toute autre version est refusée ou signalée | Vérification d'installation | partiel |
| EX-EXPL-03 | Respect des licences des composants tiers | Le code propre n'incorpore pas de code sous licence incompatible ; les composants sous licence réciproque sont utilisés comme programmes séparés ; aucune ressource sous licence réciproque n'est redistribuée avec l'outil | Revue de licence | vérifié (code) |
| EX-EXPL-04 | Une commande unique rejoue tous les essais | Sortie en erreur au premier refus inattendu | Rejeu | partiel |
| EX-EXPL-05 | Documentation en français | Tous les documents du projet en français | Revue | vérifié |

---

## Journal des versions
| Version | Date | Changements |
|---|---|---|
| 1.0 | 16/11/2026 | Première version, issue de la revue critique : exigences séparées du processus, critères mesurables, essais nommés, statuts |
