# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
import sys
def report(lib, path):
    m = __import__(lib)
    p = m.read(path)
    st = p.stitches
    b = p.bounds()
    cmds = {}
    for x,y,c in st:
        cmds[c & m.COMMAND_MASK] = cmds.get(c & m.COMMAND_MASK,0)+1
    names = {m.STITCH:'STITCH',m.JUMP:'JUMP',m.TRIM:'TRIM',m.COLOR_CHANGE:'COLOR_CHANGE',m.STOP:'STOP',m.END:'END'}
    print(f"[{lib} {getattr(m,'__version__','?')}] records={len(st)} stitches={p.count_stitch_commands(m.STITCH)} "
          f"jumps={p.count_stitch_commands(m.JUMP)} trims={p.count_stitch_commands(m.TRIM)} color_changes={p.count_color_changes()} "
          f"threads={len(p.threadlist)} bounds_0.1mm={b} size_mm=({(b[2]-b[0])/10:.2f} x {(b[3]-b[1])/10:.2f})")
    print("   cmd histogram:", {names.get(k,k):v for k,v in cmds.items()})
    print("   threads:", [t.hex_color() for t in p.threadlist])
for path in sys.argv[1:]:
    print("==", path)
    for lib in ("pyembroidery","pystitch"):
        try: report(lib, path)
        except Exception as e: print(lib, "FAILED", repr(e))
