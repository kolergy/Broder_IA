# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Construction d'une colonne satin à partir d'une forme en anneau (un contour extérieur, un trou).

Rails = contour extérieur et contour intérieur, orientés dans le même sens, ouverts au même
point de départ. Barreaux = segments reliant les deux rails à intervalle régulier, choisis de
façon monotone le long du rail intérieur pour éviter les croisements.
"""
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient


def _reechantillonner(anneau, pas):
    ligne = LineString(anneau.coords)
    n = max(int(ligne.length / pas), 8)
    return np.array([ligne.interpolate(i / n, normalized=True).coords[0] for i in range(n)])


def _appariement_monotone(a, b):
    """Chemin monotone (i, j) de (0, 0) à (n-1, m-1) minimisant la somme des distances |a_i - b_j|."""
    n, m = len(a), len(b)
    d = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=-1)
    cout = np.full((n, m), np.inf)
    cout[0, 0] = d[0, 0]
    for j in range(1, m):
        cout[0, j] = cout[0, j - 1] + d[0, j]
    for i in range(1, n):
        cout[i, 0] = cout[i - 1, 0] + d[i, 0]
        ligne_prec = cout[i - 1]
        diag = np.minimum(ligne_prec[1:], ligne_prec[:-1]) + d[i, 1:]
        ligne = cout[i]
        for j in range(1, m):  # dépendance horizontale : boucle
            ligne[j] = min(diag[j - 1], ligne[j - 1] + d[i, j])
    # Remontée
    i, j = n - 1, m - 1
    chemin = [(i, j)]
    while i > 0 or j > 0:
        candidats = []
        if i > 0 and j > 0:
            candidats.append((cout[i - 1, j - 1], i - 1, j - 1))
        if i > 0:
            candidats.append((cout[i - 1, j], i - 1, j))
        if j > 0:
            candidats.append((cout[i, j - 1], i, j - 1))
        _, i, j = min(candidats)
        chemin.append((i, j))
    return chemin[::-1]


def anneau_vers_satin(poly, pas_barreaux_mm=1.0, pas_rail_mm=0.5, depassement_mm=0.4):
    if len(poly.interiors) != 1:
        raise ValueError(f"anneau attendu (1 trou), trouvé {len(poly.interiors)} trou(s)")
    p = orient(poly, 1.0)  # extérieur antihoraire, trou horaire
    ext = _reechantillonner(p.exterior, pas_rail_mm)
    inte = _reechantillonner(p.interiors[0], pas_rail_mm)[::-1]  # même sens que l'extérieur

    # Point de départ commun : point extérieur le plus proche du rail intérieur
    d = ((ext[:, None, :] - inte[None]) ** 2).sum(-1)
    i0, j0 = np.unravel_index(d.argmin(), d.shape)
    ext = np.roll(ext, -i0, axis=0)
    inte = np.roll(inte, -j0, axis=0)

    # Appariement monotone des deux rails minimisant la longueur cumulée des barreaux
    # (déformation temporelle dynamique) : pas de croisement, pas de saut aux angles vifs.
    appariement = _appariement_monotone(ext, inte)
    longueur_ext = np.r_[0, np.cumsum(np.linalg.norm(np.diff(ext, axis=0), axis=1))]
    barreaux = []
    dernier_s = -np.inf
    for i, j in appariement:
        if longueur_ext[i] - dernier_s < pas_barreaux_mm:
            continue
        a, b = ext[i], inte[j]
        v = b - a
        n = np.linalg.norm(v)
        if n == 0:
            continue
        u = v / n
        barreaux.append([tuple(a - u * depassement_mm), tuple(b + u * depassement_mm)])
        dernier_s = longueur_ext[i]
    rail_ext = np.vstack([ext, ext[:1]])
    rail_int = np.vstack([inte, inte[:1]])
    return rail_ext, rail_int, barreaux


class SatinRefuse(Exception):
    """La forme n'est pas une colonne annulaire constructible : arrêt, revue nécessaire."""


def controler_barreaux(poly, barreaux, depassement_mm=0.4, rapport_max=1.5, part_max=0.02, tolerance_mm=0.05):
    """Garde de forme : chaque barreau doit rester dans la forme et traverser la colonne à peu près
    perpendiculairement (longueur ≈ largeur locale). Retourne les statistiques ; lève SatinRefuse sinon.

    Largeur locale = 2 × distance du milieu du barreau au bord de la forme.
    """
    from shapely.geometry import LineString as _LS
    forme = poly.buffer(tolerance_mm)
    rapports, hors_forme = [], 0
    for (a, b) in barreaux:
        a, b = np.array(a), np.array(b)
        u = (b - a) / np.linalg.norm(b - a)
        a0, b0 = a + u * depassement_mm, b - u * depassement_mm      # barreau sans dépassement
        if not forme.contains(_LS([tuple(a0), tuple(b0)])):
            hors_forme += 1
        milieu = Point(*((a0 + b0) / 2))
        largeur = 2 * poly.boundary.distance(milieu) if poly.contains(milieu) else 0.0
        rapports.append(np.linalg.norm(b0 - a0) / largeur if largeur > 0 else np.inf)
    r = np.array(rapports)
    stats = {"barreaux": len(r), "hors_forme": hors_forme,
             "part_rapport_sup_1_5": float((r > rapport_max).mean()) if len(r) else 1.0,
             "rapport_p99": float(np.percentile(r[np.isfinite(r)], 99)) if np.isfinite(r).any() else float("inf")}
    if hors_forme or stats["part_rapport_sup_1_5"] > part_max:
        raise SatinRefuse(f"satin en anneau refusé : {hors_forme} barreau(x) hors de la forme, "
                          f"{stats['part_rapport_sup_1_5']:.0%} de barreaux en biais (seuil {part_max:.0%}) "
                          "— la forme n'est pas une colonne annulaire (lettre à contre-forme ?)")
    return stats


def chemin_svg(rail_ext, rail_int, barreaux):
    def sous_chemin(points):
        return "M " + " L ".join(f"{x:.3f},{y:.3f}" for x, y in points)
    parties = [sous_chemin(rail_ext), sous_chemin(rail_int)] + [sous_chemin(b) for b in barreaux]
    return " ".join(parties)
