# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Grille de vérification exécutable d'un DST produit (exigences de qualité, voir exigences_broderie.md).

Chaque critère rend OK, ECHEC ou INFO. Toute ligne ECHEC rend le fichier refusé.
"""
from . import qualite


def verifier(dst, r, attendu):
    """attendu : {'largeur_mm': ..., 'blocs_couleur': ...}. Retourne (lignes, refuse)."""
    q = qualite.mesurer_fichier(dst, r)
    lignes = []

    def ligne(code, critere, ok, valeur, seuil, info=False):
        lignes.append({"exigence": code, "critere": critere, "statut": "INFO" if info else ("OK" if ok else "ECHEC"),
                       "valeur": valeur, "seuil": seuil})

    ligne("EX-QUAL-01", "fichier lisible et non vide", q["points"] > 0, q["points"], "> 0")
    larg = q["dimensions_mm"][0]
    ligne("EX-QUAL-02", "largeur conforme à la taille demandée", abs(larg - attendu["largeur_mm"]) <= 0.5,
          round(larg, 2), f"{attendu['largeur_mm']:.2f} ± 0,5 mm")
    courts = sum(b["points_moins_0_25mm"] for b in q["blocs"])
    ligne("EX-QUAL-03", "aucun point trop court (< 0,3 mm, tolérance de grille)", courts == 0, courts, "0")
    for i, b in enumerate(q["blocs"], 1):
        t = b["type_deduit"]
        if t == "satin":
            ligne("EX-QUAL-04", f"bloc {i} satin : points ≤ 7 mm", b["point_max_mm"] <= r["satin_longueur_max_mm"] + 0.05,
                  round(b["point_max_mm"], 2), "≤ 7 mm")
            ligne("EX-QUAL-05", f"bloc {i} satin : points en biais", b["satin_part_points_en_biais"] <= r["satin_part_biais_max"],
                  f"{b['satin_part_points_en_biais']:.1%}", f"≤ {r['satin_part_biais_max']:.0%}")
            ligne("EX-QUAL-05", f"bloc {i} satin : rapport longueur / largeur (99e centile)",
                  b["satin_rapport_p99"] <= r["satin_rapport_p99_max"], round(b["satin_rapport_p99"], 2),
                  f"≤ {r['satin_rapport_p99_max']}")
            lo_s, hi_s = r["satin_espacement_plage_mm"]
            es = b["satin_espacement_estime_mm"]
            ligne("EX-QUAL-13", f"bloc {i} satin : espacement de crête à crête", es is not None and lo_s <= es <= hi_s,
                  round(es, 3) if es else None, f"{lo_s}–{hi_s} mm (à étalonner)")
            if b["point_median_mm"] >= 2:
                ligne("EX-QUAL-07", f"bloc {i} satin ≥ 2 mm : sous-couche présente", b["sous_couche_detectee"],
                      b["sous_couche_detectee"], "oui")
        elif t == "remplissage":
            lo, hi = r["remplissage_espacement_plage_mm"]
            e = b["espacement_rangs_estime_mm"]
            ligne("EX-QUAL-06", f"bloc {i} remplissage : espacement entre rangs voisins", lo <= e <= hi,
                  round(e, 3), f"{lo}–{hi} mm (à étalonner)")
            if b["aire_couverte_mm2"] > 20:
                ligne("EX-QUAL-07", f"bloc {i} remplissage : sous-couche présente", b["sous_couche_detectee"],
                      b["sous_couche_detectee"], "oui")
        ligne("EX-QUAL-11", f"bloc {i} : pénétrations max par mm²", True, b["penetrations_max_par_mm2"],
              "à étalonner", info=True)
    ligne("EX-QUAL-08", "ordre : aucune bordure brodée avant ce qu'elle recouvre", not q["defauts_ordre"],
          "; ".join(q["defauts_ordre"]) or "aucun défaut", "aucun défaut")
    ligne("EX-QUAL-09", "nombre de blocs de couleur = prévu", q["changements_couleur"] + 1 == attendu["blocs_couleur"],
          q["changements_couleur"] + 1, attendu["blocs_couleur"])
    non_coupes = [d for d in q["deplacements"] if not d["initial"] and not d["coupe"]
                  and d["longueur_mm"] > r["seuil_coupe_deplacement_mm"]]
    ligne("EX-QUAL-10", f"déplacements de plus de {r['seuil_coupe_deplacement_mm']} mm coupés", not non_coupes,
          [round(d["longueur_mm"], 1) for d in non_coupes] or "aucun", "aucun non coupé")
    ligne("EX-QUAL-12", "temps de broderie estimé (paramètres non vérifiés)", True,
          f"{q['temps_estime_min']:.1f} min", "—", info=True)
    refuse = any(l["statut"] == "ECHEC" for l in lignes)
    return lignes, refuse, q
