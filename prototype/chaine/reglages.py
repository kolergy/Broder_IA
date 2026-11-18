# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Réglages par défaut (profil « tissé stable »), issus de collecte_de_savoir_broderie.md.

Conventions d'unités (essentiel, voir revue critique §5) :
- espacements de remplissage = distance entre RANGS VOISINS (convention Ink/Stitch) ;
- espacement du satin = de CRÊTE À CRÊTE (convention Ink/Stitch) ;
- compensation de traction = PAR CÔTÉ (convention Ink/Stitch).
Statuts : SOURCE (source primaire concordante), A_ETALONNER (valeur de départ à mesurer sur tissu),
NON_VERIFIE.
"""

PROFIL_DEFAUT = {
    "nom": "tisse_stable",
    # --- Seuils de détection et de classement (mm, mm²) ---
    "detail_min_mm": 0.4,                 # A_ETALONNER (épaisseur du fil, une seule source)
    "satin_largeur_min_mm": 1.0,          # SOURCE (Ink/Stitch)
    "satin_largeur_max_mm": 7.0,          # SOURCE (Wilcom, découpage automatique)
    "satin_largeur_max_decoupe_mm": 10.0, # SOURCE (Wilcom, plafond conseillé)
    "petite_forme_largeur_max_mm": 6.0,   # A_ETALONNER (petite forme compacte → satin)
    "aire_min_mm2": 1.5,                  # A_ETALONNER
    "allongement_min": 3.0,               # A_ETALONNER
    "appendice_largeur_mm": 2.0,          # A_ETALONNER (partie plus fine que ceci = appendice)
    "appendice_longueur_min_mm": 5.0,     # A_ETALONNER
    "marge_seuil": 0.10,                  # A_ETALONNER : mesure à ±10 % d'un seuil → « proche d'un seuil »
    "ouverture_min_mm": 0.8,              # SOURCE (Impressions)
    # --- Points ---
    "remplissage_espacement_mm": 0.25,    # A_ETALONNER : rangs voisins ; original professionnel mesuré 0,23 mm ;
                                          # l'ancienne valeur « 0,40 » confondait les conventions
    "remplissage_sous_couche_retrait_mm": 0.4,  # SOURCE (Impressions, retrait ≥ 0,4 mm)
    "satin_espacement_zigzag_mm": 0.40,   # SOURCE + mesure (crête à crête ; original ≈ 0,44)
    "satin_longueur_max_mm": 7.0,         # SOURCE (Wilcom) — découpe des points trop longs
    "compensation_traction_mm": 0.20,     # SOURCE (Wilcom, par côté, coton / sergé) ; A_ETALONNER sur tissu
    "point_droit_longueur_mm": 2.5,       # NON_VERIFIE
    "pas_barreaux_mm": 1.0,               # A_ETALONNER
    "longueur_min_point_mm": 0.3,         # SOURCE (Ink/Stitch, préférences)
    # --- Vérification ---
    "satin_part_biais_max": 0.02,         # A_ETALONNER (originaux : 0 %)
    "satin_rapport_p99_max": 1.4,         # A_ETALONNER (originaux : 1,16 à 1,23)
    "remplissage_espacement_plage_mm": (0.20, 0.30),  # A_ETALONNER (rangs voisins)
    "satin_espacement_plage_mm": (0.25, 0.55),        # A_ETALONNER (crête à crête ; estimateur biaisé ≈ −20 % :
                                                      # réglage 0,40 lu 0,32 ; originaux lus 0,36 et 0,48)
    "seuil_coupe_deplacement_mm": 10.0,   # A_ETALONNER : tout déplacement plus long doit être coupé
    "vitesse_points_par_min": 750,        # SOURCE (Wilcom : 700–800 points/min en pratique ; Tajima max 1200)
    "duree_coupe_s": 3.5,                 # SOURCE (Wilcom : 3 à 4 s par coupe)
    "duree_changement_s": 10,             # NON_VERIFIE (à mesurer sur la machine)
    "poussee_raccourcissement_mm": 0.20,  # SOURCE (Campbell, Impressions) — non encore appliqué
    "satin_points_courts_retrait_pct": 15,       # SOURCE (Ink/Stitch, défaut)
    "satin_points_courts_distance_mm": 0.25,     # SOURCE (Ink/Stitch, défaut)
}
