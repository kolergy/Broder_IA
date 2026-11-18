# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Chaîne de numérisation : formes à la taille brodée → SVG paramétré → DST.

Principes appliqués : aucune modification sans approbation ; aucun repli silencieux ; tous les points
bloquants sont rassemblés puis la chaîne s'arrête (exception Arret) avec la liste complète.
Approbations : identifiants de défauts ou d'objets, ou « tout » (à réserver aux essais, journalisé).
"""
from pathlib import Path

from shapely.geometry import Polygon

from . import geometrie, inkstitch_io, satin, sequencer


class Arret(Exception):
    def __init__(self, bloquants, rapport):
        super().__init__(f"{len(bloquants)} point(s) bloquant(s)")
        self.bloquants = bloquants
        self.rapport = rapport


def _approuve(ident, approbations):
    return "tout" in approbations or ident in approbations


def numeriser(couches, W, H, r, dossier, nom, inkstitch_py, rangs, approbations=(), python_inkstitch=None):
    """couches : [(couleur, MultiPolygon en mm)] ; rangs : rang d'empilement par couche (0 = dessous)."""
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    rapport = {"approbations": sorted(approbations), "alertes": [], "bloquants": []}
    if "tout" in approbations:
        rapport["alertes"].append("approbation globale « tout » utilisée : réservée aux essais")

    # 1. Passe de simplification : détection, puis application des seules actions approuvées
    defauts = geometrie.detecter_defauts(couches, r)
    approuves = [d["id"] for d in defauts if _approuve(d["id"], approbations)]
    for d in defauts:
        if d["id"] not in approuves:
            rapport["bloquants"].append(f"défaut non approuvé {d['id']} : {d['defaut']} ({d['mesure']}), "
                                        f"action proposée : {d['action_proposee']}")
    couches, journal = geometrie.appliquer_corrections(couches, defauts, approuves)
    rapport["defauts"], rapport["corrections"] = defauts, journal

    # 2. Mesure et classement
    formes = []
    for ic, (couleur, geo) in enumerate(couches):
        for ip, poly in enumerate(geo.geoms):
            ident = f"c{ic}_f{ip}"
            m = geometrie.mesurer(poly, r)
            decision, mode, motif, drapeaux = geometrie.classer(m, r)
            for dr in drapeaux:
                rapport["alertes"].append(f"{ident} : {dr}")
            if mode in ("revue", "alerte") and not _approuve(ident, approbations):
                rapport["bloquants"].append(f"{ident} : décision « {decision} » en mode {mode} — {motif}")
            formes.append({"id": ident, "couleur": couleur, "rang": rangs[ic], "poly": poly, "mesures": m,
                           "decision": decision, "mode": mode, "motif": motif})

    # 3. Remplissage recouvert par une bordure satin d'une autre couleur : extension sous la bordure
    for f in formes:
        if f["decision"] != "remplissage":
            continue
        for s in formes:
            if s["decision"] == "satin" and s["couleur"] != f["couleur"] and s["mesures"]["trous"] == 1:
                exterieur = Polygon(s["poly"].exterior)
                if exterieur.contains(f["poly"].representative_point()):
                    extension = s["mesures"]["largeur_moyenne_mm"] / 2
                    etendu = f["poly"].buffer(extension, join_style="mitre").intersection(exterieur)
                    if etendu.geom_type == "Polygon":
                        f["extension_mm"] = round(extension, 2)
                        f["poly"] = etendu
                    else:
                        rapport["alertes"].append(f"{f['id']} : extension sous la bordure {s['id']} impossible "
                                                  f"({etendu.geom_type}) — risque de jour entre les deux")

    # 4. Construction des objets Ink/Stitch (sans repli silencieux)
    for f in formes:
        d, m = f["decision"], f["mesures"]
        if d == "supprimer":
            continue  # bloquant tant que non approuvé (étape 2) ; approuvé = non brodé
        if d == "satin":
            if m["trous"] != 1:
                rapport["bloquants"].append(f"{f['id']} : satin requis mais construction non disponible pour une forme "
                                            f"à {m['trous']} trou(s) (découpage en colonnes à faire)")
                continue
            rext, rint, barreaux = satin.anneau_vers_satin(f["poly"], r["pas_barreaux_mm"])
            try:
                f["controle_satin"] = satin.controler_barreaux(f["poly"], barreaux,
                                                               part_max=r["satin_part_biais_max"])
            except satin.SatinRefuse as e:
                if _approuve(f"{f['id']}:forcer_satin", approbations):
                    rapport["alertes"].append(f"{f['id']} : SATIN FORCÉ malgré le refus de la garde ({e}) — "
                                              "qualité non conforme attendue")
                    f["satin_force"] = True
                else:
                    rapport["bloquants"].append(f"{f['id']} : {e} (approbation possible : « {f['id']}:forcer_satin »)")
                    continue
            largeur = m["largeur_moyenne_mm"]
            sous_couches = (["contour_underlay", "zigzag_underlay"] if largeur >= 4 else
                            ["contour_underlay"] if largeur >= 2 else ["center_walk_underlay"])
            attributs = {"satin_column": "true", "zigzag_spacing_mm": r["satin_espacement_zigzag_mm"],
                         "pull_compensation_mm": r["compensation_traction_mm"],
                         "max_stitch_length_mm": r["satin_longueur_max_mm"]}
            attributs.update({s: "true" for s in sous_couches})
            f["objet"] = {"id": f["id"], "d": satin.chemin_svg(rext, rint, barreaux),
                          "style": f"fill:none;stroke:{f['couleur']};stroke-width:0.2", "attributs": attributs}
        elif d == "remplissage":
            angle_svg, _ = geometrie.angle_remplissage(f["poly"])
            f["angle_svg_deg"] = angle_svg
            f["objet"] = {"id": f["id"], "d": inkstitch_io.polygone_vers_chemin(f["poly"]),
                          "style": f"fill:{f['couleur']};stroke:none",
                          "attributs": {"fill_method": "tatami_fill",
                                        "row_spacing_mm": r["remplissage_espacement_mm"],
                                        "angle": geometrie.angle_inkstitch(angle_svg),
                                        "fill_underlay": "true",
                                        "fill_underlay_inset_mm": r["remplissage_sous_couche_retrait_mm"]}}
        elif d in ("point_droit", "decoupage_requis"):
            if d == "point_droit":
                rapport["bloquants"].append(f"{f['id']} : point droit requis mais construction de la ligne médiane "
                                            "non disponible dans le prototype")
    rapport["formes"] = [{k: v for k, v in f.items() if k not in ("poly", "objet")} for f in formes]
    if rapport["bloquants"]:
        raise Arret(rapport["bloquants"], rapport)

    # 5. Séquençage par recouvrements, puis couleur
    a_broder = [f for f in formes if "objet" in f]
    ordre, contraintes = sequencer.ordonner(a_broder)
    a_broder = [a_broder[i] for i in ordre]
    rapport["sequence"] = [f"{f['id']} ({f['decision']}, {f['couleur']}, rang {f['rang']})" for f in a_broder]
    rapport["contraintes_ordre"] = [(a_broder[ordre.index(i)]["id"], a_broder[ordre.index(j)]["id"])
                                    for i, j in contraintes]
    couleurs_sequence = [f["couleur"] for f in a_broder]
    rapport["blocs_couleur_prevus"] = 1 + sum(1 for a, b in zip(couleurs_sequence, couleurs_sequence[1:]) if a != b)

    # 6. SVG paramétré et exécution
    svg = dossier / f"{nom}_parametre.svg"
    dst = dossier / f"{nom}.dst"
    inkstitch_io.ecrire_svg(svg, W, H, [f["objet"] for f in a_broder], r["longueur_min_point_mm"])
    code, erreurs = inkstitch_io.executer(inkstitch_py, svg, dst, python_inkstitch=python_inkstitch)
    rapport["export"] = {"code_sortie": code, "octets": dst.stat().st_size, "sortie_erreur": erreurs}
    if erreurs:
        rapport["alertes"].append(f"sortie d'erreur d'Ink/Stitch non vide : {erreurs[:300]}")
    if code != 0:
        rapport["alertes"].append(f"code de sortie d'Ink/Stitch {code} avec fichier produit")
    return rapport, svg, dst
