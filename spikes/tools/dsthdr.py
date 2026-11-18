# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
import sys
def bit(b,n): return (b>>n)&1
def decode(b0,b1,b2):
    x = y = 0
    x += bit(b2,2)*81 - bit(b2,3)*81 + bit(b1,2)*27 - bit(b1,3)*27 + bit(b0,2)*9 - bit(b0,3)*9 \
       + bit(b1,0)*3 - bit(b1,1)*3 + bit(b0,0)*1 - bit(b0,1)*1
    y += bit(b2,5)*81 - bit(b2,4)*81 + bit(b1,5)*27 - bit(b1,4)*27 + bit(b0,5)*9 - bit(b0,4)*9 \
       + bit(b1,7)*3 - bit(b1,6)*3 + bit(b0,7)*1 - bit(b0,6)*1
    if b2 == 0xF3: kind='END'
    elif b2 & 0xC3 == 0xC3: kind='COLOR'
    elif b2 & 0x80: kind='JUMP'
    else: kind='STITCH'
    return x,y,kind
data = open(sys.argv[1],'rb').read()
hdr = data[:512]
print("file size", len(data), "records", (len(data)-512)/3)
fields = hdr.split(b'\r')
for f in fields:
    f=f.replace(b'\x1a',b'').replace(b'\x20\x20\x20\x20',b' ').strip()
    if f: print("  HDR:", f.decode('latin1'))
recs = [decode(*data[i:i+3]) for i in range(512, len(data)-2, 3)]
x=y=0; xs=[0]; ys=[0]
runs=[]; cur=None; n=0
for dx,dy,k in recs:
    x+=dx; y+=dy; xs.append(x); ys.append(y)
    if k!=cur:
        if cur: runs.append((cur,n))
        cur,n=k,0
    n+=1
runs.append((cur,n))
print("raw extents 0.1mm: +X", max(xs), "-X", -min(xs), "+Y", max(ys), "-Y", -min(ys))
print("record run-length sequence:", runs)
if len(sys.argv)>2:
    x=y=0
    for i,(dx,dy,k) in enumerate(recs):
        x+=dx;y+=dy
        if k!='STITCH': print(f"   rec {i}: {k} d=({dx},{dy}) pos=({x},{y})")
