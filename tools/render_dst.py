# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
import sys, pyembroidery as pe
for src, out in zip(sys.argv[1::2], sys.argv[2::2]):
    p = pe.read(src)
    pe.write_png(p, out, {"background": "#ffffff", "linewidth": 3, "fancy": True})
    print(src, "->", out, "threads:", [t.hex_color() for t in p.threadlist])
