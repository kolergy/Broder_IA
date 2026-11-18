# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Comparaison de deux fichiers de broderie (notre DST vs l'original)."""
import math

import numpy as np
import pyembroidery as pe
from PIL import Image, ImageDraw


def _segments(motif):
    """Segments cousus (points consécutifs sans saut/coupe/changement entre eux), en mm."""
    segs, prec = [], None
    for x, y, c in motif.stitches:
        cmd = c & pe.COMMAND_MASK
        if cmd == pe.STITCH:
            if prec is not None:
                segs.append((prec[0] / 10, prec[1] / 10, x / 10, y / 10))
            prec = (x, y)
        else:
            prec = None if cmd in (pe.JUMP, pe.TRIM, pe.COLOR_CHANGE, pe.STOP) else prec
    return segs


def _suites_de_sauts(motif, n_min=3):
    suites, n = 0, 0
    for _, _, c in motif.stitches:
        if c & pe.COMMAND_MASK == pe.JUMP:
            n += 1
        else:
            if n >= n_min:
                suites += 1
            n = 0
    return suites


def statistiques(chemin):
    m = pe.read(str(chemin))
    b = m.bounds()
    segs = _segments(m)
    longueurs = np.array([math.hypot(x2 - x1, y2 - y1) for x1, y1, x2, y2 in segs]) if segs else np.array([0.0])
    return {
        "points": m.count_stitch_commands(pe.STITCH),
        "sauts": m.count_stitch_commands(pe.JUMP),
        "suites_de_sauts_coupes": _suites_de_sauts(m),
        "changements_couleur": m.count_color_changes(),
        "largeur_mm": (b[2] - b[0]) / 10,
        "hauteur_mm": (b[3] - b[1]) / 10,
        "longueur_fil_cousu_mm": float(longueurs.sum()),
        "point_min_mm": float(longueurs.min()),
        "point_max_mm": float(longueurs.max()),
        "point_median_mm": float(np.median(longueurs)),
        "points_courts_moins_1mm": int((longueurs < 1).sum()),
        "points_tres_courts_moins_0_3mm": int((longueurs < 0.3).sum()),
    }, m


def _masque(motif, px_par_mm, largeur_fil_mm, decalage, taille):
    img = Image.new("L", taille, 0)
    d = ImageDraw.Draw(img)
    w = max(1, int(round(largeur_fil_mm * px_par_mm)))
    for x1, y1, x2, y2 in _segments(motif):
        d.line([((x1 - decalage[0]) * px_par_mm, (y1 - decalage[1]) * px_par_mm),
                ((x2 - decalage[0]) * px_par_mm, (y2 - decalage[1]) * px_par_mm)], fill=255, width=w)
    return np.array(img) > 0


def recouvrement(m_ref, m_test, px_par_mm=20, largeur_fil_mm=0.4, marge_mm=3):
    """Indicateur secondaire de silhouette (IoU). Sensible à largeur_fil_mm (revue critique §2.2)."""
    """Surfaces cousues des deux fichiers, alignées sur le centre de leur boîte englobante.

    Retourne IoU, part de l'original couverte, part de notre broderie hors de l'original, densités.
    """
    def centre(m):
        b = m.bounds()
        return ((b[0] + b[2]) / 20, (b[1] + b[3]) / 20), ((b[2] - b[0]) / 10, (b[3] - b[1]) / 10)
    (cr, tr), (ct, tt) = centre(m_ref), centre(m_test)
    demi = (max(tr[0], tt[0]) / 2 + marge_mm, max(tr[1], tt[1]) / 2 + marge_mm)
    taille = (int(2 * demi[0] * px_par_mm), int(2 * demi[1] * px_par_mm))
    a = _masque(m_ref, px_par_mm, largeur_fil_mm, (cr[0] - demi[0], cr[1] - demi[1]), taille)
    b = _masque(m_test, px_par_mm, largeur_fil_mm, (ct[0] - demi[0], ct[1] - demi[1]), taille)
    # Alignement par meilleure translation (pas de 0,1 mm, ±1 mm) plutôt que par centre des boîtes
    meilleur = (-1.0, 0, 0)
    pas = max(1, int(round(0.1 * px_par_mm)))
    for dx in range(-px_par_mm, px_par_mm + 1, pas):
        for dy in range(-px_par_mm, px_par_mm + 1, pas):
            bs = np.roll(np.roll(b, dx, 1), dy, 0)
            i = (a & bs).sum() / max((a | bs).sum(), 1)
            if i > meilleur[0]:
                meilleur = (i, dx, dy)
    b = np.roll(np.roll(b, meilleur[1], 1), meilleur[2], 0)
    inter, union = (a & b).sum(), (a | b).sum()
    px2 = px_par_mm ** 2
    return {
        "iou": float(inter / union) if union else 0.0,
        "original_couvert_par_nous": float(inter / a.sum()) if a.sum() else 0.0,
        "notre_broderie_hors_original": float((b & ~a).sum() / b.sum()) if b.sum() else 0.0,
        "surface_original_mm2": float(a.sum() / px2),
        "surface_notre_mm2": float(b.sum() / px2),
        "translation_mm": [meilleur[1] / px_par_mm, meilleur[2] / px_par_mm],
        "avertissement": "silhouette seulement : ne mesure ni la direction, ni la densité, ni l'ordre",
    }, a, b


def image_comparaison(a, b, chemin):
    """Superposition : original en bleu, nous en rouge, commun en violet."""
    rgb = np.full(a.shape + (3,), 255, dtype=np.uint8)
    rgb[a & ~b] = (40, 90, 220)
    rgb[b & ~a] = (220, 50, 40)
    rgb[a & b] = (120, 40, 140)
    Image.fromarray(rgb).save(chemin)


def image_cote_a_cote(chemin_ref, chemin_test, chemin_png, couleur_ref="#1f6fd0", couleur_test="#d03020", px_par_mm=10):
    """Deux rendus de points côte à côte (couleurs fixes, le DST n'en contient pas)."""
    images = []
    for chemin, couleur in ((chemin_ref, couleur_ref), (chemin_test, couleur_test)):
        m = pe.read(str(chemin))
        b = m.bounds()
        w, h = int((b[2] - b[0]) / 10 * px_par_mm) + 20, int((b[3] - b[1]) / 10 * px_par_mm) + 20
        img = Image.new("RGB", (w, h), "white")
        d = ImageDraw.Draw(img)
        for x1, y1, x2, y2 in _segments(m):
            d.line([((x1 - b[0] / 10) * px_par_mm + 10, (y1 - b[1] / 10) * px_par_mm + 10),
                    ((x2 - b[0] / 10) * px_par_mm + 10, (y2 - b[1] / 10) * px_par_mm + 10)], fill=couleur, width=1)
        images.append(img)
    H = max(i.height for i in images)
    sortie = Image.new("RGB", (sum(i.width for i in images) + 30, H), "white")
    x = 0
    for i in images:
        sortie.paste(i, (x, 0))
        x += i.width + 30
    sortie.save(chemin_png)
