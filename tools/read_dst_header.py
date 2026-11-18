# AVERTISSEMENT : code généré avec l'aide d'une intelligence artificielle (Claude, Anthropic), non validé par
# un spécialiste de la broderie machine. Les fichiers machine (.dst) produits doivent être vérifiés par un
# professionnel qualifié avant usage : un fichier erroné peut endommager la brodeuse ou présenter un risque
# pour l'opérateur. Premier essai à vitesse réduite, sur chute de tissu.
"""Read Tajima DST 512-byte header fields and tally 3-byte records.

Usage: python3 -I read_dst_header.py FILE [FILE ...]
Read-only; never executes anything from the input files.
Prints JSON per file: header fields (LA, ST, CO, +X, -X, +Y, -Y, AX, AY, MX, MY, PD)
and a record tally (stitch / jump / colour-change / end) from the body, so header
claims can be compared with the body. Header values are reported as found; mismatches
are flagged, not hidden.
"""
import hashlib
import json
import re
import sys

FIELDS = ["LA", "ST", "CO", "+X", "-X", "+Y", "-Y", "AX", "AY", "MX", "MY", "PD"]


def parse_header(h: bytes) -> dict:
    text = h.decode("latin-1")
    out = {}
    for key in FIELDS:
        m = re.search(re.escape(key) + r":([^\r\x1a]*)\r", text)
        out[key] = m.group(1).strip() if m else None
    return out


def tally(body: bytes) -> dict:
    counts = {"records": 0, "stitch": 0, "jump": 0, "color_change": 0, "end": 0, "trailing_bytes_after_end": 0}
    i = 0
    while i + 3 <= len(body):
        b2 = body[i + 2]
        counts["records"] += 1
        if body[i:i + 3] == b"\x00\x00\xf3" or (b2 & 0xF3) == 0xF3:
            counts["end"] += 1
            counts["trailing_bytes_after_end"] = len(body) - (i + 3)
            break
        if b2 & 0xC3 == 0xC3:
            counts["color_change"] += 1
        elif b2 & 0x80:
            counts["jump"] += 1
        else:
            counts["stitch"] += 1
        i += 3
    return counts


def main(paths):
    for p in paths:
        data = open(p, "rb").read()
        res = {"path": p, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        if len(data) < 512:
            res["error"] = "file shorter than 512-byte header"
        else:
            res["header"] = parse_header(data[:512])
            t = tally(data[512:])
            res["body_tally"] = t
            st = res["header"].get("ST")
            if st and st.isdigit() and int(st) != t["records"]:
                res["warning_ST_vs_records"] = f"header ST={int(st)} but body has {t['records']} records"
        print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
