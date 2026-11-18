# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Tests automatiques des défauts relevés par la revue critique et des règles du processus.

Lancer depuis la racine du dépôt : uv run pytest
Le test qui appelle Ink/Stitch est marqué `slow` et sauté si INKSTITCH=<chemin vers inkstitch.py> n'est pas défini.
Les décisions attendues du classement sont écrites à l'avance (jugement de numériseur), pas déduites du code.
"""

import os
import tempfile
from pathlib import Path
from typing import Any

import pytest
from chaine import (
    dst_brut,
    geometrie,
    inkstitch_io,
    processus,
    qualite,
    satin,
    sequencer,
)
from chaine.reglages import PROFIL_DEFAUT as R
from shapely import affinity, union_all
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.geometry.base import BaseGeometry

RACINE_DEPOT = Path(__file__).resolve().parents[2]
SPIKES = Path(os.environ.get("SPIKES", RACINE_DEPOT / "spikes" / "results"))
INKSTITCH = os.environ.get("INKSTITCH", "")
INKSTITCH_NON_APPELE = (
    "ink_stitch_non_appele"  # le processus doit s'arrêter avant d'appeler Ink/Stitch
)

avec_inkstitch = pytest.mark.skipif(
    not (INKSTITCH and Path(INKSTITCH).is_file()),
    reason="Ink/Stitch introuvable : définir INKSTITCH=<chemin vers inkstitch.py>",
)


def trait(coords: list[tuple[float, float]], w: float) -> Polygon:
    return LineString(coords).buffer(w / 2, cap_style="flat", join_style="mitre")


def _objet_remplissage_tatami(forme: Polygon, angle_svg: float) -> dict[str, Any]:
    """Un objet SVG unique, rempli en tatami sans sous-couche, rangs à l'angle donné."""
    return {
        "id": "b",
        "d": inkstitch_io.polygone_vers_chemin(forme),
        "style": "fill:#f00;stroke:none",
        "attributs": {
            "fill_method": "tatami_fill",
            "row_spacing_mm": 0.4,
            "angle": geometrie.angle_inkstitch(angle_svg),
            "fill_underlay": "false",
        },
    }


# --- 1. Signe de l'angle de remplissage (revue §6.1) ---
@pytest.mark.slow
@avec_inkstitch
def test_angle_remplissage_suit_l_axe_de_la_forme() -> None:
    barre = affinity.rotate(
        Polygon([(0, 0), (40, 0), (40, 6), (0, 6)]), 30, origin=(20, 3)
    )
    barre = affinity.translate(barre, 10, 20)
    angle_svg, _ = geometrie.angle_remplissage(barre)
    with tempfile.TemporaryDirectory() as t:
        svg, dst = Path(t) / "b.svg", Path(t) / "b.dst"
        inkstitch_io.ecrire_svg(
            svg, 70, 60, [_objet_remplissage_tatami(barre, angle_svg)]
        )
        inkstitch_io.executer(INKSTITCH, svg, dst)
        b = qualite.mesurer_bloc(qualite.blocs(dst)[0])
    ecart = abs(((b["direction_dominante_deg"] - 30) + 90) % 180 - 90)
    assert ecart <= 10, f"rangs à {b['direction_dominante_deg']}° pour une barre à 30°"


# --- 2. Coupes réelles par motif brut, déplacement initial exclu (revue §6.2) ---
def test_coupes_detectees_par_motif_brut() -> None:
    avec = dst_brut.analyser(SPIKES / "s10_trim_true.dst")
    sans = dst_brut.analyser(SPIKES / "s10_trim_false.dst")
    assert avec["coupes"] == 1, (
        f"fichier avec coupe : {avec['coupes']} coupe(s) détectée(s) au lieu de 1"
    )
    assert sans["coupes"] == 0, (
        f"fichier sans coupe : {sans['coupes']} coupe(s) détectée(s) au lieu de 0"
    )
    assert sans["deplacements"], "aucun déplacement détecté dans le fichier sans coupe"
    nuls = [
        d for d in sans["deplacements"] if not d["initial"] and d["longueur_mm"] <= 0
    ]
    assert not nuls, f"déplacements non initiaux de longueur nulle : {nuls}"


# --- 3. Garde du satin en anneau : lettres à contre-forme refusées (revue §3.3) ---
LETTRE_A = union_all(
    [
        trait([(0, 0), (7, 20)], 2.5),
        trait([(14, 0), (7, 20)], 2.5),
        trait([(2.5, 7), (11.5, 7)], 2.5),
    ]
)
LETTRE_P = union_all(
    [
        trait([(0, 0), (0, 20)], 2.5),
        Point(4, 15)
        .buffer(6.25)
        .difference(Point(4, 15).buffer(3.75))
        .intersection(box(0, 0, 30, 30)),
        trait([(0, 18.75), (4, 18.75)], 2.5),
        trait([(0, 10), (4, 10)], 2.5),
    ]
)
ANNEAU = Point(0, 0).buffer(10).difference(Point(0, 0).buffer(8))


def _une_forme(g: BaseGeometry) -> Polygon:
    return g if g.geom_type == "Polygon" else max(g.geoms, key=lambda p: p.area)


@pytest.mark.parametrize("forme", [LETTRE_A, LETTRE_P], ids=["A", "P"])
def test_satin_anneau_refuse_les_lettres(forme: BaseGeometry) -> None:
    p = _une_forme(forme)
    assert len(p.interiors) == 1, (
        f"la lettre doit avoir une seule contre-forme, elle en a {len(p.interiors)}"
    )
    _, _, barreaux = satin.anneau_vers_satin(p, 1.0)
    with pytest.raises(satin.SatinRefuse):
        satin.controler_barreaux(p, barreaux)


def test_satin_anneau_accepte_un_anneau() -> None:
    _, _, barreaux = satin.anneau_vers_satin(ANNEAU, 1.0)
    stats = satin.controler_barreaux(ANNEAU, barreaux)
    assert stats["hors_forme"] == 0, (
        f"{stats['hors_forme']} barreau(x) hors de la forme"
    )
    assert stats["part_rapport_sup_1_5"] <= 0.02, (
        f"part des barreaux de rapport > 1,5 : {stats['part_rapport_sup_1_5']:.3f} (maximum 0,02)"
    )


# --- 4. Classement : décisions attendues écrites à l'avance (revue §3.1, §3.2, §3.4) ---
ATTENDU = {
    "disque 0,3 mm": (Point(0, 0).buffer(0.15), "supprimer"),
    "filet 0,3 x 30 mm": (box(0, 0, 30, 0.3), "point_droit"),
    "trait 0,8 x 20 mm": (box(0, 0, 20, 0.8), "point_droit"),
    "disque 2 mm": (Point(0, 0).buffer(1), "satin"),
    "carré 3 mm": (box(0, 0, 3, 3), "satin"),
    "barre 3 x 9 mm": (box(0, 0, 9, 3), "satin"),
    "barre 5 x 20 mm": (box(0, 0, 20, 5), "satin"),
    "anneau 2 mm": (ANNEAU, "satin"),
    "sucette (disque 20 mm + tige 1,5 mm)": (
        union_all([Point(0, 0).buffer(10), box(-0.75, -40, 0.75, 0)]),
        "decoupage_requis",
    ),
    "barre 12 x 80 mm": (box(0, 0, 80, 12), "remplissage"),
    "disque 30 mm": (Point(0, 0).buffer(15), "remplissage"),
}


@pytest.mark.parametrize("nom", list(ATTENDU))
def test_classement_conforme_au_jugement_ecrit(nom: str) -> None:
    g, attendu = ATTENDU[nom]
    m = geometrie.mesurer(_une_forme(g), R)
    decision, _mode, motif, _ = geometrie.classer(m, R)
    assert decision == attendu, f"{nom} : {decision} ({motif}) au lieu de {attendu}"


# --- 5. Séquençage par recouvrements, puis couleur (revue §6.5) ---
def test_sequencement_respecte_recouvrements_et_regroupe_les_couleurs() -> None:
    objets = [
        {"poly": box(0, 0, 10, 10), "couleur": "#aa0000", "rang": 0},
        {"poly": box(20, 0, 30, 10), "couleur": "#0000aa", "rang": 0},
        {
            "poly": box(8, 0, 22, 10),
            "couleur": "#00aa00",
            "rang": 1,
        },  # recouvre les deux premiers
        {
            "poly": box(40, 0, 50, 10),
            "couleur": "#aa0000",
            "rang": 0,
        },  # isolé, même couleur que le premier
    ]
    ordre, contraintes = sequencer.ordonner(objets)
    position = {j: k for k, j in enumerate(ordre)}
    attendues = {(0, 2), (1, 2)}
    assert attendues <= set(contraintes), (
        f"contraintes de recouvrement manquantes : {attendues - set(contraintes)}"
    )
    mal_ordonnees = [(i, j) for i, j in contraintes if position[i] >= position[j]]
    assert not mal_ordonnees, (
        f"contraintes non respectées dans l'ordre {ordre} : {mal_ordonnees}"
    )
    assert position[3] == position[0] + 1, (
        "l'objet isolé de même couleur doit suivre sans changement de couleur"
    )


# --- 6. Rien n'est modifié sans approbation ; invariant des objets non concernés (revue §3.4, §4.3) ---
def _couches_avec_defauts() -> list[tuple[str, MultiPolygon]]:
    grande = Polygon(
        [(0, 0), (30, 0), (30, 30), (0, 30)],
        [[(10, 10), (10.5, 10), (10.5, 10.5), (10, 10.5)]],
    )
    eclat = Point(50, 50).buffer(0.2)
    return [
        ("#112233", MultiPolygon([grande, eclat])),
        ("#445566", MultiPolygon([box(60, 0, 80, 20)])),
    ]


def test_aucune_suppression_sans_approbation() -> None:
    couches = _couches_avec_defauts()
    with tempfile.TemporaryDirectory() as t, pytest.raises(processus.Arret) as e:
        processus.numeriser(
            couches,
            100,
            100,
            R,
            t,
            "x",
            INKSTITCH_NON_APPELE,
            [0, 1],
            approbations=(),
        )
    texte = " ".join(e.value.bloquants)
    assert "négligeable" in texte, (
        f"l'éclat négligeable n'est pas signalé comme bloquant : {texte}"
    )
    assert "ouverture" in texte, (
        f"la petite ouverture n'est pas signalée comme bloquante : {texte}"
    )


def test_corrections_approuvees_ne_touchent_que_les_objets_vises() -> None:
    couches = _couches_avec_defauts()
    defauts = geometrie.detecter_defauts(couches, R)
    approuve = [d["id"] for d in defauts if d["action_proposee"] == "supprimer"]
    sorties, journal = geometrie.appliquer_corrections(couches, defauts, approuve)
    assert len(journal) == len(approuve), (
        f"journal de {len(journal)} entrée(s) pour {len(approuve)} approbation(s)"
    )
    assert sorties[1][1].geoms[0].equals_exact(couches[1][1].geoms[0], 0), (
        "la couche non concernée a été modifiée"
    )
    assert len(sorties[0][1].geoms[0].interiors) == 1, (
        "le trou non approuvé doit rester"
    )
