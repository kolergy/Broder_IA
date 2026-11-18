# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Écriture du SVG paramétré et exécution d'Ink/Stitch selon les règles du processus (§2.4)."""
import os
import subprocess
import tempfile
from pathlib import Path
from xml.sax.saxutils import quoteattr

INKSTITCH_SVG_VERSION = 4


def polygone_vers_chemin(poly):
    def anneau(coords):
        pts = list(coords)
        return "M " + " L ".join(f"{x:.3f},{y:.3f}" for x, y in pts) + " Z"
    return " ".join([anneau(poly.exterior.coords)] + [anneau(i.coords) for i in poly.interiors])


def ecrire_svg(chemin, largeur_mm, hauteur_mm, objets, longueur_min_point_mm=0.3):
    """objets : liste de dict {id, d, style, attributs:{nom: valeur}} dans l'ordre de broderie.

    longueur_min_point_mm : réglage de document Ink/Stitch (défaut Ink/Stitch 0,1 mm) ;
    notre vérification refuse les points < 0,3 mm.
    """
    lignes = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!-- AVERTISSEMENT : fichier généré avec l\'aide d\'une IA, non validé par un spécialiste. Le fichier machine '
        'qui en est tiré doit être vérifié par un professionnel avant usage (risque pour la brodeuse et l\'opérateur). -->',
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"',
        '     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"',
        '     xmlns:inkstitch="http://inkstitch.org/namespace"',
        f'     width="{largeur_mm:.3f}mm" height="{hauteur_mm:.3f}mm" viewBox="0 0 {largeur_mm:.3f} {hauteur_mm:.3f}">',
        f'  <metadata><inkstitch:inkstitch_svg_version>{INKSTITCH_SVG_VERSION}</inkstitch:inkstitch_svg_version>'
        f'<inkstitch:min_stitch_len_mm>{longueur_min_point_mm}</inkstitch:min_stitch_len_mm></metadata>',
        '  <g id="calque_broderie" inkscape:groupmode="layer" inkscape:label="Broderie">',
    ]
    for o in objets:
        attrs = " ".join(f'inkstitch:{k}={quoteattr(str(v))}' for k, v in o.get("attributs", {}).items())
        lignes.append(f'    <path id="{o["id"]}" d="{o["d"]}" style="{o["style"]}" {attrs}/>')
    lignes += ["  </g>", "</svg>"]
    Path(chemin).write_text("\n".join(lignes), encoding="utf-8")


def executer(inkstitch_py, svg, sortie, extension="output", options=("--format=dst",), delai_s=1800,
             python_inkstitch=None):
    """Appel d'Ink/Stitch en programme séparé. Le succès est jugé sur le contenu, pas le code de sortie.

    python_inkstitch : interpréteur de l'environnement d'Ink/Stitch (séparé du nôtre). Par défaut, variable
    d'environnement INKSTITCH_PYTHON, sinon l'interpréteur courant (signalé).
    Une sortie d'erreur non vide avec un fichier produit est renvoyée pour être signalée.
    """
    import sys
    python_inkstitch = python_inkstitch or os.environ.get("INKSTITCH_PYTHON") or sys.executable
    with tempfile.TemporaryDirectory() as config:
        env = dict(os.environ, XDG_CONFIG_HOME=config, INKSTITCH_OFFLINE_SCRIPT="true",
                   PYTHONUTF8="1", LANGUAGE="en_US")
        env.pop("PYTHONIOENCODING", None)
        try:
            run = subprocess.run([python_inkstitch, str(inkstitch_py), f"--extension={extension}", *options, str(svg)],
                                 capture_output=True, env=env, timeout=delai_s)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Ink/Stitch a dépassé le délai de {delai_s} s (dessin trop dense ? blocage ?)")
    Path(sortie).write_bytes(run.stdout)
    erreurs = run.stderr.decode(errors="replace").strip()
    if not run.stdout:
        raise RuntimeError(f"Ink/Stitch n'a rien produit (code {run.returncode}). Sortie d'erreur :\n{erreurs}")
    return run.returncode, erreurs
