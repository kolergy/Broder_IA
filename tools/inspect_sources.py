# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
import sys, pyembroidery as pe
import ezdxf
from ezdxf.addons.drawing import matplotlib as dmpl
repo = sys.argv[1]
for f in ("test/Star.pes", "test/Embroidermodder.PES", "test/Star.JEF"):
    try:
        p = pe.read(f"{repo}/{f}")
        print(f, "threads:", [(t.hex_color(), t.description) for t in p.threadlist], "stitches:", p.count_stitch_commands(pe.STITCH))
    except Exception as e:
        print(f, "ERR", e)
print("shamrockin.rgb bytes:", open(f"{repo}/data/samples/shamrockin.rgb","rb").read().hex())
for f, out in (("test/Embroidermodder.DXF","renders/em_test_dxf.png"),("data/samples/Embroidermodder-R2000.dxf","renders/em_samples_dxf.png")):
    try:
        doc = ezdxf.readfile(f"{repo}/{f}")
        msp = doc.modelspace()
        kinds = {}
        for e in msp: kinds[e.dxftype()] = kinds.get(e.dxftype(),0)+1
        print(f, "entities:", kinds)
        dmpl.qsave(msp, out, bg="#FFFFFF", fg="#000000")
        print("  ->", out)
    except Exception as e:
        print(f, "ERR", repr(e))
