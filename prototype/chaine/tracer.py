# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Image matricielle → formes vectorielles, une liste par couleur (entrée « image », hors flux vectoriel).

Méthode : couleur de fond = couleur dominante du bord de l'image (les éléments blancs du dessin sont
conservés si le fond n'est pas blanc) ; regroupement des couleurs (k-moyennes) ; fermeture morphologique ;
contours ; polygones avec trous par imbrication. Tout ce qui est écarté est journalisé.
"""
import numpy as np
from PIL import Image
from shapely.geometry import MultiPolygon, Polygon
from shapely.validation import make_valid
from skimage import measure, morphology


def _kmeans(pixels, k, iterations=30, graine=0):
    rng = np.random.default_rng(graine)
    centres = pixels[rng.choice(len(pixels), k, replace=False)].astype(float)
    for _ in range(iterations):
        d = ((pixels[:, None, :] - centres[None]) ** 2).sum(-1)
        etiquettes = d.argmin(1)
        for i in range(k):
            if (etiquettes == i).any():
                centres[i] = pixels[etiquettes == i].mean(0)
    return centres, etiquettes


def _masque_vers_polygones(masque, journal, couleur):
    padded = np.pad(masque, 1)
    contours = measure.find_contours(padded.astype(float), 0.5)
    anneaux, ecartes = [], 0
    for c in contours:
        if len(c) < 4:
            ecartes += 1
            continue
        poly = Polygon([(p[1] - 1, p[0] - 1) for p in c])
        if not poly.is_valid:
            poly = make_valid(poly).buffer(0)
        if poly.area > 0:
            anneaux.append(poly)
    if ecartes:
        journal.append({"couleur": couleur, "evenement": f"{ecartes} contour(s) de moins de 4 points écarté(s)"})
    anneaux.sort(key=lambda p: p.area, reverse=True)
    resultat, orphelins = [], 0
    for i, a in enumerate(anneaux):
        profondeur = sum(1 for b in anneaux[:i] if b.contains(a.representative_point()))
        if profondeur % 2 == 0:
            resultat.append([a, []])
        else:
            parent = next((r for r in reversed(resultat) if r[0].contains(a.representative_point())), None)
            if parent:
                parent[1].append(a)
            else:
                orphelins += 1
    if orphelins:
        journal.append({"couleur": couleur, "evenement": f"{orphelins} trou(s) sans forme parente écarté(s)"})
    polys = []
    for ext, trous in resultat:
        p = ext
        for t in trous:
            p = p.difference(t)
        polys.extend(p.geoms if hasattr(p, "geoms") else [p])
    return MultiPolygon([g for g in polys if g.geom_type == "Polygon" and g.area > 0])


def tracer(chemin_png, n_couleurs=1, tolerance_fond=12, rayon_fermeture_px=2, tolerance_px=0.6):
    """Retourne ([(couleur_hex, MultiPolygon en pixels), ...], largeur_px, hauteur_px, journal)."""
    journal = []
    image = np.array(Image.open(chemin_png).convert("RGB")).astype(int)
    bord = np.concatenate([image[0], image[-1], image[:, 0], image[:, -1]])
    valeurs, comptes = np.unique(bord, axis=0, return_counts=True)
    fond = valeurs[comptes.argmax()]
    premier_plan = (np.abs(image - fond).max(-1) > tolerance_fond)
    journal.append({"evenement": f"couleur de fond détectée sur le bord : #{''.join(f'{v:02x}' for v in fond)}"})
    if not premier_plan.any():
        raise ValueError("Image vide : aucun pixel hors du fond")
    pixels = image[premier_plan]
    if n_couleurs == 1:
        centres = np.array([pixels.mean(0)])
        etiquettes = np.zeros(len(pixels), dtype=int)
    else:
        centres, etiquettes = _kmeans(pixels.astype(float), n_couleurs)
    carte = np.full(premier_plan.shape, -1)
    carte[premier_plan] = etiquettes
    couches = []
    for i, c in enumerate(centres):
        hexa = "#%02x%02x%02x" % tuple(int(round(v)) for v in c)
        masque = carte == i
        if rayon_fermeture_px:
            masque = morphology.closing(masque, morphology.disk(rayon_fermeture_px))
        geo = _masque_vers_polygones(masque, journal, hexa).simplify(tolerance_px, preserve_topology=True)
        if geo.geom_type == "Polygon":
            geo = MultiPolygon([geo])
        couches.append((hexa, geo))
    return couches, image.shape[1], image.shape[0], journal
