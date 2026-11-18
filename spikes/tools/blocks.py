# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
import sys, pyembroidery as pe
p = pe.read(sys.argv[1])
for i,(blk,thr) in enumerate(p.get_as_colorblocks()):
    pts=[(x,y) for x,y,c in blk if (c&pe.COMMAND_MASK)==pe.STITCH]
    if not pts: print(f"block {i}: no stitches"); continue
    xs=[a for a,b in pts]; ys=[b for a,b in pts]
    print(f"block {i}: stitches={len(pts)} x[{min(xs)/10:.1f},{max(xs)/10:.1f}] y[{min(ys)/10:.1f},{max(ys)/10:.1f}] size={ (max(xs)-min(xs))/10:.2f}x{(max(ys)-min(ys))/10:.2f} mm")
