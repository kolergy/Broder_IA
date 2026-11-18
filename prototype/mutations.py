#!/usr/bin/env python3
# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Validation par mutation de la grille de vérification.

Chaque variante dégradée du SVG paramétré de référence doit faire apparaître un ECHEC NOUVEAU sur
l'exigence qui la vise (par rapport à la référence). Une variante non détectée = grille insuffisante.

Usage : python mutations.py <svg_parametre_reference> <largeur_attendue_mm> <inkstitch.py>
Code de sortie : 0 si toutes les mutations sont détectées, 1 sinon.
"""
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from chaine import inkstitch_io, verifier  # noqa: E402
from chaine.reglages import PROFIL_DEFAUT as R  # noqa: E402


def attr(svg, nom, valeur, selecteur):
    """Pose / remplace inkstitch:<nom> sur les <path> dont le style contient `selecteur`."""
    def repl(m):
        balise = m.group(0)
        if selecteur not in balise:
            return balise
        if f"inkstitch:{nom}=" in balise:
            return re.sub(rf'inkstitch:{nom}="[^"]*"', f'inkstitch:{nom}="{valeur}"', balise)
        return balise.replace("/>", f' inkstitch:{nom}="{valeur}"/>')
    return re.sub(r"<path [^>]*/>", repl, svg)


def sans_attr(svg, noms, selecteur):
    def repl(m):
        balise = m.group(0)
        if selecteur not in balise:
            return balise
        for n in noms:
            balise = re.sub(rf'\s*inkstitch:{n}="[^"]*"', "", balise)
        return balise
    return re.sub(r"<path [^>]*/>", repl, svg)


def inverser_ordre(svg):
    chemins = re.findall(r"    <path [^>]*/>", svg)
    corps = svg
    for c in chemins:
        corps = corps.replace(c + "\n", "", 1)
    return corps.replace("  </g>", "\n".join(reversed(chemins)) + "\n  </g>", 1)


MUTATIONS = {
    # nom : (fonction, exigences dont un ECHEC nouveau est attendu)
    "ordre inversé (bordure avant remplissage)": (inverser_ordre, {"EX-QUAL-08"}),
    "remplissage sans sous-couche": (lambda s: attr(s, "fill_underlay", "false", "fill:#"), {"EX-QUAL-07"}),
    "satin sans sous-couche": (lambda s: sans_attr(s, ["contour_underlay", "zigzag_underlay", "center_walk_underlay"],
                                                     "stroke:#"), {"EX-QUAL-07"}),
    "remplissage deux fois trop dense (0,125 mm)": (lambda s: attr(s, "row_spacing_mm", "0.125", "fill:#"), {"EX-QUAL-06"}),
    "remplissage deux fois trop clair (0,5 mm)": (lambda s: attr(s, "row_spacing_mm", "0.5", "fill:#"), {"EX-QUAL-06"}),
    "satin clairsemé (zigzag 1,0 mm)": (lambda s: attr(s, "zigzag_spacing_mm", "1.0", "stroke:#"), {"EX-QUAL-05", "EX-QUAL-13"}),
    "satin sans longueur maximale": (lambda s: sans_attr(s, ["max_stitch_length_mm"], "stroke:#"), {"EX-QUAL-04"}),
    "longueur minimale de point 0,1 mm": (lambda s: s.replace("<inkstitch:min_stitch_len_mm>0.3", "<inkstitch:min_stitch_len_mm>0.1"),
                                          {"EX-QUAL-03"}),
}

# Présence effective de la dégradation (sinon la mutation est sans objet pour ce dessin)
EFFET = {
    "satin sans longueur maximale": lambda q: any(b["type_deduit"] == "satin" and b["point_max_mm"] > 7.05
                                                  for b in q["blocs"]),
}


def echecs(lignes):
    return {(l["exigence"], l["critere"]) for l in lignes if l["statut"] == "ECHEC"}


def main():
    ref_svg, largeur, ink = Path(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    base = ref_svg.read_text()
    blocs = 1 + len(set(re.findall(r'(?:fill|stroke):(#[0-9a-f]{6})', base))) - 1
    attendu = {"largeur_mm": largeur, "blocs_couleur": blocs}
    resultats, ok_global = [], True
    with tempfile.TemporaryDirectory() as tmp:
        def evaluer(texte, nom):
            svg, dst = Path(tmp) / f"{nom}.svg", Path(tmp) / f"{nom}.dst"
            svg.write_text(texte)
            inkstitch_io.executer(ink, svg, dst)
            lignes, _, q = verifier.verifier(dst, R, attendu)
            return lignes, dst.read_bytes(), q
        lignes_base, octets_base, _ = evaluer(base, "reference")
        e_base = echecs(lignes_base)
        for i, (nom, (f, vise)) in enumerate(MUTATIONS.items()):
            lignes, octets, q = evaluer(f(base), f"m{i}")
            if octets != octets_base and nom in EFFET and not EFFET[nom](q):
                resultats.append({"mutation": nom, "exigences_visees": sorted(vise), "detectee": None,
                                  "statut": "sans objet (fichier modifié mais dégradation absente sur ce dessin)"})
                print(f"[SANS OBJET] {nom} → fichier modifié, dégradation absente sur ce dessin")
                continue
            if octets == octets_base:
                resultats.append({"mutation": nom, "exigences_visees": sorted(vise), "detectee": None,
                                  "statut": "sans objet (fichier identique : la mutation ne s'applique pas à ce dessin)"})
                print(f"[SANS OBJET] {nom} → fichier identique à la référence")
                continue
            nouveaux = echecs(lignes) - e_base
            codes = {c for c, _ in nouveaux}
            detecte = bool(codes & vise)
            ok_global &= detecte
            resultats.append({"mutation": nom, "exigences_visees": sorted(vise), "detectee": detecte,
                              "nouveaux_echecs": sorted(f"{c} {t}" for c, t in nouveaux)})
            print(f"[{'DÉTECTÉE  ' if detecte else 'NON VUE   '}] {nom} → {sorted(f'{c} {t}' for c, t in nouveaux) or 'aucun nouvel échec'}")
    avertissement = ("Généré avec l'aide d'une IA, non validé par un spécialiste. Le fichier machine (.dst) doit être "
                     "vérifié par un professionnel avant usage : un fichier erroné peut endommager la brodeuse ou "
                     "présenter un risque pour l'opérateur.")
    Path(ref_svg.parent / "mutations_resultats.json").write_text(
        json.dumps({"avertissement": avertissement, "resultats": resultats}, indent=2, ensure_ascii=False))
    print("Toutes les mutations détectées" if ok_global else "AU MOINS UNE MUTATION NON DÉTECTÉE")
    sys.exit(0 if ok_global else 1)


if __name__ == "__main__":
    main()
