# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Séquençage : ordre de broderie respectant les recouvrements, puis regroupement par couleur.

Règle : si deux objets se recouvrent (ou se touchent), celui du dessous (rang le plus bas dans l'ordre
d'empilement) est brodé en premier. Parmi les objets disponibles, on préfère la couleur courante
(moins de changements), puis le rang d'empilement. Déterministe.
"""


def ordonner(objets, tolerance_mm=0.1):
    """objets : liste de dict avec 'poly' (géométrie), 'couleur', 'rang' (empilement, 0 = dessous).
    Retourne (ordre, contraintes) ; ordre = liste d'indices."""
    n = len(objets)
    avant = {j: set() for j in range(n)}          # avant[j] = objets à broder avant j
    contraintes = []
    zones = [o["poly"].buffer(tolerance_mm) for o in objets]
    for i in range(n):
        for j in range(n):
            if objets[i]["rang"] < objets[j]["rang"] and zones[i].intersects(zones[j]):
                avant[j].add(i)
                contraintes.append((i, j))
    ordre, fait, courante = [], set(), None
    while len(ordre) < n:
        dispo = [j for j in range(n) if j not in fait and avant[j] <= fait]
        if not dispo:
            raise RuntimeError("cycle dans les recouvrements : ordre d'empilement incohérent")
        dispo.sort(key=lambda j: (objets[j]["couleur"] != courante, objets[j]["rang"], j))
        j = dispo[0]
        ordre.append(j)
        fait.add(j)
        courante = objets[j]["couleur"]
    return ordre, contraintes


def changements_minimum(objets):
    """Borne basse du nombre de changements de couleur : nombre de couleurs distinctes − 1."""
    return max(len({o["couleur"] for o in objets}) - 1, 0)
