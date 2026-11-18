# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Mise à l'échelle, mesures, classement, détection des défauts (processus : mise à l'échelle, mesure,
classement, passe de simplification). Aucune modification n'est appliquée sans approbation."""
import math

import shapely
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Polygon


def en_multi(g):
    if g.is_empty:
        return MultiPolygon([])
    if g.geom_type == "Polygon":
        return MultiPolygon([g])
    if g.geom_type == "MultiPolygon":
        return g
    return MultiPolygon([p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon"])


def mettre_a_l_echelle(couches, largeur_mm, marge_mm=5.0):
    """Mise à l'échelle commune de toutes les couches pour une largeur totale donnée (mm)."""
    tout = shapely.union_all([g for _, g in couches])
    minx, miny, maxx, maxy = tout.bounds
    facteur = largeur_mm / (maxx - minx)
    sorties = []
    for couleur, g in couches:
        g2 = affinity.translate(g, -minx, -miny)
        g2 = affinity.scale(g2, facteur, facteur, origin=(0, 0))
        g2 = affinity.translate(g2, marge_mm, marge_mm)
        sorties.append((couleur, en_multi(g2)))
    return sorties, largeur_mm + 2 * marge_mm, (maxy - miny) * facteur + 2 * marge_mm, facteur


def appendices(poly, r):
    """Parties plus fines que `appendice_largeur_mm` et plus longues que `appendice_longueur_min_mm`
    (ex. tige d'une sucette, filet attaché) : la forme est mixte et doit être découpée avant classement."""
    rayon = r["appendice_largeur_mm"] / 2
    corps = poly.buffer(-rayon).buffer(rayon)
    if corps.area < 0.2 * poly.area:
        return []  # forme fine partout (colonne, anneau) : pas une forme mixte
    reste = en_multi(poly.difference(corps.buffer(0.01)))
    sortie = []
    for p in reste.geoms:
        rect = p.minimum_rotated_rectangle
        coords = list(rect.exterior.coords)
        longueurs = sorted(math.dist(coords[i], coords[i + 1]) for i in range(4))
        if longueurs[-1] >= r["appendice_longueur_min_mm"]:
            sortie.append({"aire_mm2": p.area, "longueur_mm": longueurs[-1]})
    return sortie


def mesurer(poly, r=None):
    """Mesures géométriques d'une forme (mm)."""
    aire = poly.area
    perimetre = poly.length
    rayon = shapely.maximum_inscribed_circle(poly, 0.01).length
    largeur_max = 2 * rayon
    m = {
        "aire_mm2": aire,
        "perimetre_mm": perimetre,
        "largeur_max_mm": largeur_max,
        "largeur_moyenne_mm": 2 * aire / perimetre if perimetre else 0.0,
        "allongement": aire / largeur_max ** 2 if largeur_max else 0.0,
        "compacite": 4 * math.pi * aire / perimetre ** 2 if perimetre else 0.0,  # informatif seulement
        "trous": len(poly.interiors),
    }
    if r is not None:
        m["appendices"] = appendices(poly, r)
    return m


def _proche(valeur, seuil, marge):
    return abs(valeur - seuil) <= marge * seuil


def classer(m, r):
    """Table de décision (processus §3.3, version 1.0). Retourne (decision, mode, motif, drapeaux).

    Modes : auto (construit), semi_auto (construit si les gardes passent), revue (arrêt sans approbation),
    alerte (arrêt sans approbation).
    """
    drapeaux = []
    lmax, lmoy, allong = m["largeur_max_mm"], m["largeur_moyenne_mm"], m["allongement"]
    for nom, valeur, seuil in (("largeur max / détail minimal", lmax, r["detail_min_mm"]),
                               ("largeur max / satin minimal", lmax, r["satin_largeur_min_mm"]),
                               ("largeur max / satin maximal", lmax, r["satin_largeur_max_mm"]),
                               ("allongement", allong, r["allongement_min"])):
        if _proche(valeur, seuil, r["marge_seuil"]):
            drapeaux.append(f"proche d'un seuil : {nom} ({valeur:.2f} pour {seuil})")
    if m.get("appendices"):
        return ("decoupage_requis", "revue",
                f"forme mixte : {len(m['appendices'])} partie(s) fine(s) attachée(s) — découper en parties "
                "d'épaisseur homogène avant classement", drapeaux)
    if lmax < r["detail_min_mm"]:
        if allong >= r["allongement_min"]:
            return "point_droit", "auto", "filet long plus fin que le détail minimal", drapeaux
        return "supprimer", "alerte", "détail plus petit que l'épaisseur du fil", drapeaux
    if lmax < r["satin_largeur_min_mm"] or m["aire_mm2"] < r["aire_min_mm2"]:
        return "point_droit", "auto", "trop fin pour un satin ou un remplissage", drapeaux
    if lmax <= r["satin_largeur_max_mm"] and allong >= r["allongement_min"] and lmoy >= r["satin_largeur_min_mm"]:
        return "satin", "semi_auto", "colonne de largeur compatible satin", drapeaux
    if lmax <= r["petite_forme_largeur_max_mm"]:
        return "satin", "semi_auto", "petite forme compacte : satin (pratique professionnelle)", drapeaux
    if allong >= r["allongement_min"] and lmax <= r["satin_largeur_max_decoupe_mm"]:
        return "satin", "revue", "colonne large : satin découpé ou remplissage, décision humaine", drapeaux
    return "remplissage", "auto", "surface", drapeaux


def angle_remplissage(poly, n_angles=16, pas_mm=1.0):
    """Angle des rangées donnant le moins de fragments, dans le repère du SVG (y vers le bas).

    Retourne (angle_svg_deg, fragments). Pour Ink/Stitch (angle compté dans le sens inverse des aiguilles
    d'une montre, axe vertical vers le haut), utiliser angle_inkstitch() — signe opposé (vérifié : revue
    critique, exp7, et contrôle indépendant).
    """
    resultats = {}
    c = poly.centroid
    for k in range(n_angles):
        a = 180.0 * k / n_angles
        p = affinity.rotate(poly, -a, origin=c)
        minx, miny, maxx, maxy = p.bounds
        fragments, y = 0, miny + pas_mm / 2
        while y < maxy:
            inter = p.intersection(LineString([(minx - 1, y), (maxx + 1, y)]))
            fragments += len(inter.geoms) if hasattr(inter, "geoms") else (0 if inter.is_empty else 1)
            y += pas_mm
        resultats[a] = fragments
    meilleur = min(resultats, key=lambda a: (resultats[a], a))
    return meilleur, resultats


def angle_inkstitch(angle_svg_deg):
    """Conversion repère SVG → convention Ink/Stitch (signe opposé)."""
    return -angle_svg_deg


def detecter_defauts(couches, r):
    """Passe de simplification, étape 1 : DÉTECTION seulement. Chaque défaut porte une action proposée et
    un identifiant ; rien n'est modifié ici."""
    defauts = []
    for ic, (couleur, geo) in enumerate(couches):
        for ip, p in enumerate(geo.geoms):
            m = mesurer(p)
            ident = f"c{ic}_f{ip}"
            if m["aire_mm2"] < r["aire_min_mm2"] and m["largeur_max_mm"] < r["satin_largeur_min_mm"]:
                defauts.append({"id": f"{ident}:negligeable", "objet": ident, "couleur": couleur,
                                "defaut": "élément négligeable",
                                "mesure": f"aire {m['aire_mm2']:.2f} mm², largeur {m['largeur_max_mm']:.2f} mm",
                                "action_proposee": "supprimer"})
            for it, t in enumerate(p.interiors):
                largeur_trou = 2 * shapely.maximum_inscribed_circle(Polygon(t), 0.01).length
                if largeur_trou < r["ouverture_min_mm"]:
                    defauts.append({"id": f"{ident}:trou{it}", "objet": ident, "couleur": couleur,
                                    "defaut": "ouverture qui se refermera",
                                    "mesure": f"largeur {largeur_trou:.2f} mm < {r['ouverture_min_mm']} mm",
                                    "action_proposee": "boucher"})
    return defauts


def appliquer_corrections(couches, defauts, approuves):
    """Passe de simplification, étape 2 : application DÉTERMINISTE des seules actions approuvées.
    Contrôle d'invariant : les objets non concernés sont inchangés. Retourne (couches, journal)."""
    approuves = set(approuves)
    journal, sorties = [], []
    for ic, (couleur, geo) in enumerate(couches):
        gardes = []
        for ip, p in enumerate(geo.geoms):
            ident = f"c{ic}_f{ip}"
            mes = [d for d in defauts if d["objet"] == ident and d["id"] in approuves]
            if any(d["action_proposee"] == "supprimer" for d in mes):
                journal += [dict(d, applique="supprimé") for d in mes if d["action_proposee"] == "supprimer"]
                continue
            a_boucher = {int(d["id"].split(":trou")[1]) for d in mes if d["action_proposee"] == "boucher"}
            if a_boucher:
                p2 = Polygon(p.exterior, [t for i, t in enumerate(p.interiors) if i not in a_boucher])
                journal += [dict(d, applique="bouché") for d in mes if d["action_proposee"] == "boucher"]
            else:
                p2 = p
            gardes.append(p2)
        sorties.append((couleur, MultiPolygon(gardes)))
    # Invariant : tout objet sans action approuvée est identique au bit près
    concernes = {d["objet"] for d in defauts if d["id"] in approuves}
    for ic, ((_, g0), (_, g1)) in enumerate(zip(couches, sorties)):
        restants = [p for ip, p in enumerate(g0.geoms) if f"c{ic}_f{ip}" not in concernes]
        for p in restants:
            if not any(p.equals_exact(q, 0) for q in g1.geoms):
                raise RuntimeError(f"invariant violé : un objet non concerné de la couche {ic} a changé")
    return sorties, journal
