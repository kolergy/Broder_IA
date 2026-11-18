# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Lecture brute d'un fichier DST (enregistrements de 3 octets), sans interprétation par une bibliothèque.

Sert à vérifier ce que la machine lira réellement : coupes (motif de sauts), sauts, changements de couleur.
Une coupe écrite par Ink/Stitch / pystitch = 3 petits sauts qui s'annulent : a, −2a, a (pystitch écrit
(+2,+2) (−4,−4) (+2,+2) dans son repère ; dans les enregistrements bruts, l'axe vertical est inversé, d'où
(2,−2) (−4,4) (2,−2)). Une suite de sauts qui DÉPLACE l'aiguille n'est pas une coupe.
"""


def _bit(b, n):
    return (b >> n) & 1


def _decoder(b0, b1, b2):
    x = _bit(b0, 0) - _bit(b0, 1) + 9 * _bit(b0, 2) - 9 * _bit(b0, 3)
    y = _bit(b0, 7) - _bit(b0, 6) + 9 * _bit(b0, 5) - 9 * _bit(b0, 4)
    x += 3 * _bit(b1, 0) - 3 * _bit(b1, 1) + 27 * _bit(b1, 2) - 27 * _bit(b1, 3)
    y += 3 * _bit(b1, 7) - 3 * _bit(b1, 6) + 27 * _bit(b1, 5) - 27 * _bit(b1, 4)
    x += 81 * _bit(b2, 2) - 81 * _bit(b2, 3)
    y += 81 * _bit(b2, 5) - 81 * _bit(b2, 4)
    return x, y


def enregistrements(chemin):
    """Liste de (type, dx, dy) en unités de 0,1 mm ; type parmi POINT, SAUT, COULEUR, FIN."""
    donnees = open(chemin, "rb").read()[512:]
    sortie = []
    for i in range(0, len(donnees) - 2, 3):
        b0, b1, b2 = donnees[i:i + 3]
        if b2 == 0xF3:
            sortie.append(("FIN", 0, 0))
            break
        dx, dy = _decoder(b0, b1, b2)
        if (b2 & 0xC3) == 0xC3:
            t = "COULEUR"
        elif (b2 & 0x83) == 0x83:
            t = "SAUT"
        else:
            t = "POINT"
        sortie.append((t, dx, dy))
    return sortie


def _est_motif_coupe(trois):
    """Trois sauts a, −2a, a de faible amplitude (≤ 0,3 mm par axe) : motif de coupe."""
    if len(trois) != 3:
        return False
    (x1, y1), (x2, y2), (x3, y3) = trois
    return ((x1, y1) == (x3, y3) and (x2, y2) == (-2 * x1, -2 * y1) and (x1, y1) != (0, 0)
            and max(abs(x1), abs(y1)) <= 3)


def analyser(chemin):
    """Coupes réelles (motif), déplacements sans couture (longueur, coupés ou non), changements de couleur."""
    rec = enregistrements(chemin)
    coupes, deplacements, couleurs = 0, [], 0
    premier_point_vu = False
    i = 0
    while i < len(rec):
        t = rec[i][0]
        if t == "POINT":
            premier_point_vu = True
            i += 1
        elif t == "COULEUR":
            couleurs += 1
            i += 1
        elif t == "SAUT":
            j = i
            while j < len(rec) and rec[j][0] == "SAUT":
                j += 1
            suite = [(dx, dy) for _, dx, dy in rec[i:j]]
            # repérer les motifs de coupe dans la suite
            k, coupe_ici, deplacement = 0, False, [0, 0]
            while k < len(suite):
                if _est_motif_coupe(suite[k:k + 3]):
                    coupes += 1
                    coupe_ici = True
                    k += 3
                else:
                    deplacement[0] += suite[k][0]
                    deplacement[1] += suite[k][1]
                    k += 1
            longueur_mm = (deplacement[0] ** 2 + deplacement[1] ** 2) ** 0.5 / 10
            if longueur_mm > 0:
                deplacements.append({"longueur_mm": longueur_mm, "coupe": coupe_ici,
                                     "initial": not premier_point_vu})
            i = j
        else:
            i += 1
    return {"enregistrements": len(rec), "coupes": coupes, "changements_couleur": couleurs,
            "deplacements": deplacements}
