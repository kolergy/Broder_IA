# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Batterie de mesures de qualité d'un fichier de broderie, calculées sur les points eux-mêmes.

Les mesures n'utilisent pas la géométrie d'origine : elles s'appliquent de la même façon à notre fichier
et à un fichier de référence. Méthodes reprises et généralisées de la revue critique (exp3, exp4).

Limites : un bloc de couleur peut contenir plusieurs objets ; le type de bloc (remplissage / satin /
point droit) est déduit des points (heuristique signalée comme telle).
"""
import math

import numpy as np
import pyembroidery as pe
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage import morphology

from . import dst_brut


def blocs(chemin):
    """Segments cousus par bloc de couleur : liste de tableaux (x1, y1, x2, y2) en mm."""
    m = pe.read(str(chemin))
    sortie, prec = [[]], None
    for x, y, c in m.stitches:
        c &= pe.COMMAND_MASK
        if c == pe.STITCH:
            if prec is not None:
                sortie[-1].append((prec[0] / 10, prec[1] / 10, x / 10, y / 10))
            prec = (x, y)
        elif c == pe.COLOR_CHANGE:
            sortie.append([])
            prec = None
        elif c in (pe.JUMP, pe.TRIM, pe.STOP):
            prec = None
    return [np.array(b) for b in sortie if b]


def _raster(segs, px, largeur_px, marge=2.0):
    mn = segs[:, [0, 2]].min(), segs[:, [1, 3]].min()
    W = int((segs[:, [0, 2]].max() - mn[0] + 2 * marge) * px)
    H = int((segs[:, [1, 3]].max() - mn[1] + 2 * marge) * px)
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    for x1, y1, x2, y2 in segs:
        d.line([((x1 - mn[0] + marge) * px, (y1 - mn[1] + marge) * px),
                ((x2 - mn[0] + marge) * px, (y2 - mn[1] + marge) * px)], fill=255, width=largeur_px)
    return np.array(img) > 0, mn, marge


def mesurer_bloc(segs, px=20):
    d = segs[:, 2:] - segs[:, :2]
    L = np.hypot(d[:, 0], d[:, 1])
    ang = np.degrees(np.arctan2(d[:, 1], d[:, 0])) % 180
    hist, _ = np.histogram(ang, bins=18, range=(0, 180), weights=L)
    dom = hist.argmax() * 10 + 5
    proche = np.abs(((ang - dom + 90) % 180) - 90) < 15
    part_dominante = float(L[proche].sum() / L.sum())

    # Surface couverte (fermeture morphologique) et largeur locale (transformée de distance)
    masque, mn, marge = _raster(segs, px, max(1, int(0.4 * px)))
    masque = morphology.closing(masque, morphology.disk(int(0.6 * px)))
    aire = float(masque.sum() / px ** 2)
    dt = ndi.distance_transform_edt(masque) / px
    H, W = masque.shape
    rapports = []
    for (x1, y1, x2, y2), l in zip(segs, L):
        if l < 1.2:
            continue
        t = np.linspace(0.1, 0.9, 9)
        xs = ((x1 + (x2 - x1) * t) - mn[0] + marge) * px
        ys = ((y1 + (y2 - y1) * t) - mn[1] + marge) * px
        w = 2 * dt[ys.astype(int).clip(0, H - 1), xs.astype(int).clip(0, W - 1)].max()
        if w > 0.5:
            rapports.append(l / w)
    r = np.array(rapports) if rapports else np.array([0.0])
    # Rapport pour TOUS les points (0 si largeur indéterminée) : sert à isoler les points de dessus d'un satin
    r_tous = np.zeros(len(L))
    for k, ((x1, y1, x2, y2), l) in enumerate(zip(segs, L)):
        t = np.linspace(0.1, 0.9, 9)
        xs = ((x1 + (x2 - x1) * t) - mn[0] + marge) * px
        ys = ((y1 + (y2 - y1) * t) - mn[1] + marge) * px
        w = 2 * dt[ys.astype(int).clip(0, H - 1), xs.astype(int).clip(0, W - 1)].max()
        r_tous[k] = l / w if w > 0.5 else 0.0

    # Type de bloc (heuristique) : remplissage = fil majoritairement dans une direction ;
    # satin = points traversant la colonne (rapport longueur / largeur locale proche de 1).
    if part_dominante >= 0.5:
        type_bloc = "remplissage"
    elif np.median(r) > 0.6:
        type_bloc = "satin"
    else:
        type_bloc = "point_droit"

    # Sous-couche : les premiers 15 % du fil diffèrent du reste (direction pour un remplissage,
    # rapport longueur / largeur pour un satin).
    cum = np.cumsum(L) / L.sum()
    debut = cum <= 0.15
    sous_couche = False
    if debut.sum() >= 5 and (~debut).sum() >= 5:
        if type_bloc == "remplissage":
            h_debut, _ = np.histogram(ang[debut], bins=18, range=(0, 180), weights=L[debut])
            dom_debut = h_debut.argmax() * 10 + 5
            sous_couche = abs(((dom_debut - dom + 90) % 180) - 90) > 30
        else:
            # Satin : le dessus alterne d'un bord à l'autre (demi-tour à chaque point) ; une sous-couche
            # (marche centrale, contour, zigzag espacé) avance sans demi-tour systématique.
            u = d / np.maximum(L, 1e-9)[:, None]
            cos_virage = (u[1:] * u[:-1]).sum(1)          # +1 : tout droit, -1 : demi-tour
            avance = np.r_[cos_virage[0], cos_virage] > -0.5
            debut10 = cum <= 0.10
            sous_couche = bool(L[debut10 & avance].sum() > 0.5 * L[debut10].sum())

    # Concentration de pénétrations : points par cellule de 1 mm²
    pts = np.vstack([segs[:, :2], segs[-1:, 2:]])
    gx = np.floor(pts[:, 0]).astype(int)
    gy = np.floor(pts[:, 1]).astype(int)
    _, comptes = np.unique(np.stack([gx, gy], 1), axis=0, return_counts=True)

    return {
        "type_deduit": type_bloc,
        "points": int(len(L)),
        "fil_mm": float(L.sum()),
        "aire_couverte_mm2": aire,
        "direction_dominante_deg": int(dom),
        "part_fil_direction_dominante": part_dominante,
        "espacement_rangs_estime_mm": float(aire / L[proche].sum()) if type_bloc == "remplissage" else None,
        "satin_part_points_en_biais": float((r > 1.5).mean()) if type_bloc == "satin" else None,
        "satin_rapport_p99": float(np.percentile(r, 99)) if type_bloc == "satin" else None,
        # Satin : espacement de crête à crête ≈ 2 × aire / fil des points de dessus (qui traversent la colonne)
        "satin_espacement_estime_mm": (float(2 * aire / L[r_tous > 0.6].sum())
                                       if type_bloc == "satin" and L[r_tous > 0.6].sum() > 0 else None),
        "sous_couche_detectee": bool(sous_couche),
        "point_median_mm": float(np.median(L)),
        "point_max_mm": float(L.max()),
        "points_moins_1mm": int((L < 1.0).sum()),
        "points_moins_0_25mm": int((L < 0.25).sum()),  # 0,3 mm moins la quantification de la grille DST
        "penetrations_max_par_mm2": int(comptes.max()),
    }


def ordre_recouvrements(chemin, px=10):
    """Défauts d'ordre : un bloc satin (bordure) brodé AVANT un bloc remplissage qu'il recouvre."""
    bl = blocs(chemin)
    mesures = [mesurer_bloc(b) for b in bl]
    mn = min(b[:, [0, 2]].min() for b in bl), min(b[:, [1, 3]].min() for b in bl)
    mx = max(b[:, [0, 2]].max() for b in bl), max(b[:, [1, 3]].max() for b in bl)
    W, H = int((mx[0] - mn[0] + 4) * px), int((mx[1] - mn[1] + 4) * px)
    masques = []
    for b in bl:
        img = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(img)
        for x1, y1, x2, y2 in b:
            d.line([((x1 - mn[0] + 2) * px, (y1 - mn[1] + 2) * px), ((x2 - mn[0] + 2) * px, (y2 - mn[1] + 2) * px)],
                   fill=255, width=max(1, int(0.4 * px)))
        masques.append(morphology.closing(np.array(img) > 0, morphology.disk(int(0.6 * px))))
    defauts = []
    for i in range(len(bl)):
        for j in range(i + 1, len(bl)):
            if mesures[i]["type_deduit"] == "satin" and mesures[j]["type_deduit"] == "remplissage":
                commun = (masques[i] & masques[j]).sum() / max(masques[i].sum(), 1)
                if commun > 0.2:
                    defauts.append(f"bloc {i + 1} (satin) brodé avant le bloc {j + 1} (remplissage) qu'il recouvre "
                                   f"({commun:.0%} de sa surface)")
    return defauts


def temps_estime_s(points, coupes, changements, r):
    return points / r["vitesse_points_par_min"] * 60 + coupes * r["duree_coupe_s"] + changements * r["duree_changement_s"]


def mesurer_fichier(chemin, r):
    bl = blocs(chemin)
    brut = dst_brut.analyser(chemin)
    par_bloc = [mesurer_bloc(b) for b in bl]
    points = sum(m["points"] for m in par_bloc)
    m = pe.read(str(chemin))
    b = m.bounds()
    return {
        "dimensions_mm": [(b[2] - b[0]) / 10, (b[3] - b[1]) / 10],
        "points": points,
        "fil_mm": sum(x["fil_mm"] for x in par_bloc),
        "changements_couleur": brut["changements_couleur"],
        "coupes_reelles": brut["coupes"],
        "deplacements": brut["deplacements"],
        "defauts_ordre": ordre_recouvrements(chemin),
        "temps_estime_min": temps_estime_s(points, brut["coupes"], brut["changements_couleur"], r) / 60,
        "blocs": par_bloc,
    }
