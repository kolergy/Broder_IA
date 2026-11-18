#!/usr/bin/env python3
# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Vérification de l'installation de la chaîne de broderie (Ink/Stitch + pyembroidery/pystitch).

Usage : python verifier_installation.py <chemin vers inkstitch.py>

Crée un dessin de test connu (carré en remplissage 40 x 40 mm, ligne en point droit 80 mm,
colonne satin 4 x 40 mm), l'exporte en DST avec Ink/Stitch, relit le fichier et compare
aux valeurs attendues. Toute anomalie est signalée et le script sort en erreur.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

EXPECTED_VERSION_COMMIT = "b0edd96311ece82ee48816dc93466274b12c2a9c"  # Ink/Stitch v3.3.0
EXPECTED_SIZE_MM = (80.0, 60.0)
EXPECTED_COLOR_CHANGES = 2
EXPECTED_STITCHES = 1897  # export déterministe : égalité stricte (un écart signale une dérive de version)
TIMEOUT_S = 300

SVG_TEST = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg"
     xmlns:inkstitch="http://inkstitch.org/namespace"
     width="100mm" height="100mm" viewBox="0 0 100 100">
  <metadata><inkstitch:inkstitch_svg_version>4</inkstitch:inkstitch_svg_version></metadata>
  <rect id="square" x="10" y="10" width="40" height="40" style="fill:#ff0000;stroke:none"
        inkstitch:fill_method="tatami_fill" inkstitch:row_spacing_mm="0.4"/>
  <path id="runline" d="M 10,70 L 90,70" style="fill:none;stroke:#0000ff;stroke-width:0.3"
        inkstitch:stroke_method="running_stitch" inkstitch:running_stitch_length_mm="2.5"/>
  <path id="satin" d="M 60,10 L 60,50 M 64,10 L 64,50 M 58,30 L 66,30"
        style="fill:none;stroke:#00aa00;stroke-width:0.3" inkstitch:satin_column="true"/>
</svg>
"""

SVG_COUPE = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkstitch="http://inkstitch.org/namespace"
     width="100mm" height="40mm" viewBox="0 0 100 40">
  <metadata><inkstitch:inkstitch_svg_version>4</inkstitch:inkstitch_svg_version></metadata>
  <path id="a" d="M 10,20 L 30,20" style="fill:none;stroke:#000000;stroke-width:0.3"
        inkstitch:stroke_method="running_stitch" inkstitch:trim_after="true"/>
  <path id="b" d="M 70,20 L 90,20" style="fill:none;stroke:#000000;stroke-width:0.3"
        inkstitch:stroke_method="running_stitch"/>
</svg>
"""


def coupes_brutes(chemin):
    """Compte les motifs de coupe (3 petits sauts a, -2a, a) dans les enregistrements bruts du DST."""
    def bit(b, n):
        return (b >> n) & 1
    with open(chemin, "rb") as f:
        donnees = f.read()[512:]
    coupes, suite = 0, []
    for i in range(0, len(donnees) - 2, 3):
        b0, b1, b2 = donnees[i:i + 3]
        if b2 == 0xF3:
            break
        x = bit(b0, 0) - bit(b0, 1) + 9 * bit(b0, 2) - 9 * bit(b0, 3) + 3 * bit(b1, 0) - 3 * bit(b1, 1) \
            + 27 * bit(b1, 2) - 27 * bit(b1, 3) + 81 * bit(b2, 2) - 81 * bit(b2, 3)
        y = bit(b0, 7) - bit(b0, 6) + 9 * bit(b0, 5) - 9 * bit(b0, 4) + 3 * bit(b1, 7) - 3 * bit(b1, 6) \
            + 27 * bit(b1, 5) - 27 * bit(b1, 4) + 81 * bit(b2, 5) - 81 * bit(b2, 4)
        if (b2 & 0x83) == 0x83 and (b2 & 0xC3) != 0xC3:
            suite.append((x, y))
            continue
        k = 0
        while k + 3 <= len(suite):
            a, m, c = suite[k:k + 3]
            if a == c and m == (-2 * a[0], -2 * a[1]) and a != (0, 0) and max(map(abs, a)) <= 3:
                coupes += 1
                k += 3
            else:
                k += 1
        suite = []
    return coupes


failures = []


def check(ok, message):
    print(("  OK     " if ok else "  ÉCHEC  ") + message)
    if not ok:
        failures.append(message)


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage : python verifier_installation.py <chemin vers inkstitch.py>")
    inkstitch = Path(sys.argv[1]).resolve()

    print("1. Fichiers et version d'Ink/Stitch")
    check(inkstitch.is_file(), f"inkstitch.py trouvé : {inkstitch}")
    if inkstitch.is_file():
        rev = subprocess.run(["git", "-C", str(inkstitch.parent), "rev-parse", "HEAD"],
                             capture_output=True, text=True)
        commit = rev.stdout.strip()
        check(commit == EXPECTED_VERSION_COMMIT,
              f"version épinglée v3.3.0 (commit {commit[:12] or 'inconnu'})")

    print("2. Bibliothèques Python")
    for module in ("wx", "inkex", "shapely", "pystitch", "pyembroidery"):
        try:
            mod = __import__(module)
            check(True, f"import {module} {getattr(mod, '__version__', '')}")
        except Exception as exc:  # signalé, jamais masqué
            check(False, f"import {module} : {exc!r}")

    if failures:
        sys.exit(f"\n{len(failures)} échec(s) : installation incomplète, export non tenté.")

    print("3. Export DST du dessin de test")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        svg = tmp / "test.svg"
        dst = tmp / "test.dst"
        svg.write_text(SVG_TEST, encoding="utf-8")
        (tmp / "config").mkdir()
        env = dict(os.environ,
                   XDG_CONFIG_HOME=str(tmp / "config"),  # cache privé : pas de fuite entre fichiers
                   INKSTITCH_OFFLINE_SCRIPT="true",
                   PYTHONUTF8="1",
                   LANGUAGE="en_US")
        env.pop("PYTHONIOENCODING", None)
        try:
            run = subprocess.run([sys.executable, str(inkstitch), "--extension=output", "--format=dst", str(svg)],
                                 capture_output=True, env=env, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            sys.exit(f"  ÉCHEC  export bloqué au-delà de {TIMEOUT_S} s (balise de version ? dialogue wx ?)")
        dst.write_bytes(run.stdout)
        if run.stderr.strip():
            print("  (sortie d'erreur d'Ink/Stitch)\n    " + run.stderr.decode(errors="replace").strip().replace("\n", "\n    "))
        check(not run.stderr.strip(), "sortie d'erreur d'Ink/Stitch vide")
        check(run.returncode == 0, f"code de sortie {run.returncode}")
        check(len(run.stdout) > 0, f"fichier DST non vide ({len(run.stdout)} octets) — le code de sortie seul ne suffit pas")
        if not run.stdout:
            sys.exit(f"\n{len(failures)} échec(s).")

        print("4. Relecture et comparaison aux valeurs attendues")
        import pyembroidery
        import pystitch
        results = {}
        for lib in (pyembroidery, pystitch):
            p = lib.read(str(dst))
            b = p.bounds()
            results[lib.__name__] = (p.count_stitch_commands(lib.STITCH), p.count_color_changes(),
                                     round((b[2] - b[0]) / 10, 2), round((b[3] - b[1]) / 10, 2))
            print(f"  {lib.__name__} : points={results[lib.__name__][0]} changements de couleur={results[lib.__name__][1]} "
                  f"dimensions={results[lib.__name__][2]} x {results[lib.__name__][3]} mm")
        stitches, colors, width, height = results["pystitch"]
        check(results["pyembroidery"] == results["pystitch"], "pyembroidery et pystitch concordent")
        check(stitches == EXPECTED_STITCHES, f"nombre de points exact : {EXPECTED_STITCHES} (obtenu {stitches})")
        check(colors == EXPECTED_COLOR_CHANGES, f"{EXPECTED_COLOR_CHANGES} changements de couleur")
        check(abs(width - EXPECTED_SIZE_MM[0]) < 0.2 and abs(height - EXPECTED_SIZE_MM[1]) < 0.2,
              f"dimensions {EXPECTED_SIZE_MM[0]} x {EXPECTED_SIZE_MM[1]} mm")
        header = dst.read_bytes()[:512].decode("ascii", errors="replace")
        check("+X:" in header and " 400" in header.split("+X:")[1][:8], "en-tête DST : étendue +X = 400 (unité 0,1 mm)")

        print("5. Coupe : deux objets éloignés, coupe demandée après le premier")
        svg2, dst2 = tmp / "coupe.svg", tmp / "coupe.dst"
        svg2.write_text(SVG_COUPE, encoding="utf-8")
        run2 = subprocess.run([sys.executable, str(inkstitch), "--extension=output", "--format=dst", str(svg2)],
                              capture_output=True, env=env, timeout=TIMEOUT_S)
        dst2.write_bytes(run2.stdout)
        check(len(run2.stdout) > 0, "fichier avec coupe non vide")
        if run2.stdout:
            check(coupes_brutes(dst2) == 1, f"motif brut de coupe présent une fois (trouvé {coupes_brutes(dst2)})")

    if failures:
        sys.exit(f"\n{len(failures)} échec(s) : voir ci-dessus.")
    print("\nInstallation vérifiée : la chaîne est opérationnelle.")


if __name__ == "__main__":
    main()
