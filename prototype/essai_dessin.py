#!/usr/bin/env python3
# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Montage d'essai (distinct de la chaîne) : rendu d'un DST connu → chaîne → DST → vérification et
comparaison avec l'original.

Usage :
  python essai_dessin.py <nom> <image.png> <original.dst> <inkstitch.py> <n_couleurs>
                         [--config essai|production] [--approuver-tout]

Spécificités de l'essai (ne font PAS partie du processus) :
- l'image est un RENDU de broderie : le contour tracé = étendue des points + épaisseur du trait de rendu
  (0,3 mm). La largeur cible de mise à l'échelle inclut donc ce trait, puis on retire sa demi-épaisseur
  (correction du double retrait relevé par la revue critique §1.3) ;
- configuration « essai » : compensation de traction nulle (l'image montre déjà l'étalement du fil) ;
  configuration « production » : compensation du profil (seule configuration représentative d'un vrai dessin) ;
- rang d'empilement des couches tracées : la plus grande surface dessous (heuristique d'essai).
Code de sortie : 0 accepté, 1 refusé par la grille, 2 arrêt de la chaîne (points bloquants).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pyembroidery as pe  # noqa: E402
from shapely.geometry import MultiPolygon  # noqa: E402

from chaine import comparer, fiche, geometrie, processus, qualite, tracer, verifier  # noqa: E402
from chaine.reglages import PROFIL_DEFAUT  # noqa: E402

EPAISSEUR_TRAIT_RENDU_MM = 0.3   # tools/render_dst.py : trait de 3 px à 10 px/mm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nom"), ap.add_argument("png"), ap.add_argument("original"), ap.add_argument("inkstitch")
    ap.add_argument("n_couleurs", type=int)
    ap.add_argument("--config", choices=["essai", "production"], default="essai")
    ap.add_argument("--approuver-tout", action="store_true")
    a = ap.parse_args()

    r = dict(PROFIL_DEFAUT)
    if a.config == "essai":
        r["compensation_traction_mm"] = 0.0
    nom = f"{a.nom}_{a.config}"
    dossier = Path(__file__).parent / "essais" / a.nom / a.config
    dossier.mkdir(parents=True, exist_ok=True)
    rapport = {"avertissement": "Généré avec l'aide d'une IA, non validé par un spécialiste. Le fichier machine (.dst) "
                                "doit être vérifié par un professionnel avant usage : un fichier erroné peut endommager la "
                                "brodeuse ou présenter un risque pour l'opérateur.",
               "nom": nom, "config": a.config, "reglages": {k: v for k, v in r.items()}}

    ref = pe.read(a.original)
    b = ref.bounds()
    largeur_points = (b[2] - b[0]) / 10
    rapport["cible"] = {"largeur_points_original_mm": largeur_points}

    couches, wpx, hpx, journal_trace = tracer.tracer(a.png, a.n_couleurs)
    rapport["tracage"] = {"journal": journal_trace,
                          "couches": [{"couleur": c, "formes": len(g.geoms)} for c, g in couches]}

    # Mise à l'échelle : contour tracé = points + trait de rendu ; puis retrait de la demi-épaisseur du trait
    couches, W, H, facteur = geometrie.mettre_a_l_echelle(couches, largeur_points + EPAISSEUR_TRAIT_RENDU_MM)
    journal_retrait = []
    avant = couches
    couches = [(c, geometrie.en_multi(g.buffer(-EPAISSEUR_TRAIT_RENDU_MM / 2, join_style="mitre"))) for c, g in couches]
    for (c, g0), (_, g1) in zip(avant, couches):
        perdues = [p for p in g0.geoms if not g1.intersects(p.representative_point())]
        if perdues:
            journal_retrait.append(f"{c} : {len(perdues)} élément(s) plus petit(s) que le retrait de rendu supprimé(s) "
                                   f"({sum(p.area for p in perdues):.2f} mm²)")
        t0, t1 = sum(len(p.interiors) for p in g0.geoms), sum(len(p.interiors) for p in g1.geoms)
        if t0 != t1:
            journal_retrait.append(f"{c} : trous {t0} → {t1} après retrait de rendu")
    rapport["mise_a_l_echelle"] = {"mm_par_px": facteur, "journal_retrait": journal_retrait}

    aires = [sum(p.area for p in g.geoms) for _, g in couches]
    rangs = [sorted(aires, reverse=True).index(x) for x in aires]

    approbations = ("tout",) if a.approuver_tout else ()
    try:
        rp, svg, dst = processus.numeriser(couches, W, H, r, dossier, nom, a.inkstitch, rangs, approbations)
    except processus.Arret as e:
        rapport["chaine"] = e.rapport
        rapport["resultat"] = "ARRET"
        (dossier / f"{nom}_rapport.json").write_text(json.dumps(rapport, indent=2, ensure_ascii=False, default=str))
        print("ARRÊT DE LA CHAÎNE — points bloquants :\n- " + "\n- ".join(e.bloquants))
        sys.exit(2)
    rapport["chaine"] = rp

    # Vérification de notre fichier (grille exécutable), puis mêmes mesures sur l'original
    lignes, refuse, q_nous = verifier.verifier(dst, r, {"largeur_mm": largeur_points,
                                                       "blocs_couleur": rp["blocs_couleur_prevus"]})
    lignes_ref, refuse_ref, q_ref = verifier.verifier(a.original, r, {"largeur_mm": largeur_points,
                                                                      "blocs_couleur": rp["blocs_couleur_prevus"]})
    rapport["verification"] = {"refuse": refuse, "lignes": lignes}
    rapport["verification_original"] = {"refuse": refuse_ref, "lignes": lignes_ref}
    rapport["mesures"] = {"nous": q_nous, "original": q_ref}

    _, m_ref = comparer.statistiques(a.original)
    _, m_nous = comparer.statistiques(dst)
    rec, ma, mb = comparer.recouvrement(m_ref, m_nous)
    rapport["silhouette"] = rec
    comparer.image_comparaison(ma, mb, dossier / f"{nom}_superposition.png")
    comparer.image_cote_a_cote(a.original, dst, dossier / f"{nom}_cote_a_cote.png")
    sequence_couleurs = []
    for f in rp["sequence"]:
        c = f.split(", ")[1]
        if not sequence_couleurs or sequence_couleurs[-1] != c:
            sequence_couleurs.append(c)
    fiche.fiche_couleurs(nom, sequence_couleurs, q_nous, r, dossier / f"{nom}_fiche_couleurs.md")

    rapport["resultat"] = "REFUSE" if refuse else "ACCEPTE"
    (dossier / f"{nom}_rapport.json").write_text(json.dumps(rapport, indent=2, ensure_ascii=False, default=str))
    print(f"{nom} : {rapport['resultat']} (original évalué par la même grille : "
          f"{'REFUSE' if refuse_ref else 'ACCEPTE'})")
    for l_n, l_o in zip(lignes, lignes_ref + [None] * len(lignes)):
        print(f"  [{l_n['statut']:5s}] {l_n['exigence']} {l_n['critere']} : {l_n['valeur']} (seuil {l_n['seuil']})")
    print("  original :", "; ".join(f"{l['critere']} = {l['valeur']} [{l['statut']}]" for l in lignes_ref))
    print(f"  silhouette (indicateur secondaire) : IoU {rec['iou']:.3f}, translation {rec['translation_mm']}")
    print("  alertes :", rp["alertes"] or "aucune")
    sys.exit(1 if refuse else 0)


if __name__ == "__main__":
    main()
