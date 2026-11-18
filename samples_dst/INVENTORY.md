> ⚠️ **Avertissement — contenu généré par intelligence artificielle.** Ce document a été produit avec l'aide d'une IA (Claude, Anthropic) et n'a pas été validé par un spécialiste de la broderie machine. Il peut contenir des erreurs. Toute information, tout réglage et tout fichier produit — en particulier les fichiers machine (.dst) — doivent être vérifiés par un professionnel qualifié avant usage. **Un fichier machine erroné peut endommager la brodeuse** (casse d'aiguille, bourrage, contrainte mécanique), abîmer le tissu et présenter un risque pour l'opérateur : ne jamais lancer une broderie sans contrôle préalable par un spécialiste et premier essai à vitesse réduite, sur chute de tissu.

> **Correction (16/11/2026)** : the "12 jump runs" of `Embroidermodder.DST` are long moves, not trims — raw-record pattern analysis finds 0 trims (see `collecte_de_savoir_broderie.md` §17).

# DST sample inventory

Compiled 2026-11-15. Files in this directory are untrusted data: never execute anything here.
Header reader: `tools/read_dst_header.py` (run as `python3 -I`, from outside this directory).

## 1. Downloaded files (GitHub only, open licence)

Source repository: https://github.com/Embroidermodder/Embroidermodder
Pinned commit: `537c9ddd710b8aaab02be634951f3d8e700d5155` (2026-04-21)
Licence: zlib/libpng (repo `LICENSE.md`, copied here as `embroidermodder/LICENSE.md`). Permissive: use, modify and redistribute, commercial use allowed. Keep the notice, do not misrepresent where it came from.

**Warning from the upstream `test/README.md`:** the test designs "should not be used unless you are a software developer testing libembroidery. They may not be valid files." So treat them as parser fixtures, including edge cases. They are **not** quality references.

DST coordinates are in 0.1 mm units.

| File | Source URL | Bytes | sha256 |
|---|---|---|---|
| `embroidermodder/Star.DST` | https://raw.githubusercontent.com/Embroidermodder/Embroidermodder/537c9ddd710b8aaab02be634951f3d8e700d5155/test/Star.DST | 8213 | `2a25d008514fa47b2fe435deacb3c8baee2ea021a3115a112cee6d7ccb912421` |
| `embroidermodder/Embroidermodder.DST` | https://raw.githubusercontent.com/Embroidermodder/Embroidermodder/537c9ddd710b8aaab02be634951f3d8e700d5155/test/Embroidermodder.DST | 10977 | `10ca026041bd152b07313efeccd0de332138349ca5c88c5d92d1f8a620387e11` |
| `embroidermodder/shamrockin.dst` | https://raw.githubusercontent.com/Embroidermodder/Embroidermodder/537c9ddd710b8aaab02be634951f3d8e700d5155/data/samples/shamrockin.dst | 4946 | `9b9a4a21d0c65e7d6120303758badd98c116160556d957fd6a2df6c79070b772` |

### Header fields (from the 512-byte header)

| File | LA | ST | CO | +X | -X | +Y | -Y | Approx. size (mm) |
|---|---|---|---|---|---|---|---|---|
| Star.DST | `Star.DST` | 2567 | 1 | 296 | 295 | 311 | 312 | 59.1 x 62.3 |
| Embroidermodder.DST | `Embroidermodder` | 3487 | 0 | 1114 | 1111 | 259 | 255 | 222.5 x 51.4 |
| shamrockin.dst | `Untitled` | 1477 | 0 | 249 | 249 | 285 | 207 | 49.8 x 49.2 |

### Body tally (3-byte records, from the same script) and observations

| File | Records (incl. END) | Stitch | Jump | Colour change | Jump runs (≥3 jumps, trim-like) | Bytes after END |
|---|---|---|---|---|---|---|
| Star.DST | 2567 | 2550 | 15 | 1 | 2 (lengths 5, 8) | 0 |
| Embroidermodder.DST | 3488 | 3407 | 80 | 0 | 12 (lengths 4, 15) | 1 (`0x1A`) |
| shamrockin.dst | 1477 | 1473 | 3 | 0 | 1 (length 3) | 3 (`a1 00 00`) |

Edge cases a verification script should handle (these are useful *because* they differ):
- **ST convention differs:** in Star and shamrockin, ST equals the record count including END. In Embroidermodder.DST, ST excludes END (3487 vs 3488). The check should accept a difference of 1, or report it as a warning, not an error.
- **Trailing bytes after END:** a single `0x1A` (DOS EOF) in Embroidermodder.DST, and 3 junk bytes in shamrockin.dst.
- **CO semantics:** Star has CO=1 and one colour-change record. So CO counts *changes*, not colours (2 colours).
- **Trims:** DST has no trim command. Trims show up as runs of jumps. Embroidermodder.DST (lettering, 12 runs) is the best fixture for trim detection.
- The **AX/AY** end-offset fields are non-zero in Star (+295/+311) and Embroidermodder (+5/−5).
- What each file depicts comes from file names and extents. They were **not** rendered visually. Embroidermodder.DST is likely the word "Embroidermodder" as lettering (wide and short, many jump runs). Star is a 2-colour star. shamrockin is a single-colour shamrock.

## 2. Other sources checked (not downloaded)

| Source | Format | Licence | Notes |
|---|---|---|---|
| EmbroidePy/pyembroidery (GitHub) | none | MIT | No DST fixtures in the repo. Tests build patterns in code. |
| Embroidermodder/libembroidery (GitHub) | none | zlib | No DST files at HEAD. |
| inkstitch/inkstitch, `main` branch (GitHub) | none | GPL-3.0 | No DST files. |
| inkstitch/inkstitch, `gh-pages` branch (website) | **SVG only** (incl. zips of SVGs, e.g. `assets/images/stitch-type-butterflies/*.zip`; logo SVGs in `assets/images/tutorials/logo/`) | No explicit content licence found in the site config | Sample list: https://inkstitch.org/tutorials/resources/samples. The SVGs could be exported to DST with Ink/Stitch to get logo-like references (satin, fill, lettering), but that is a derived artifact. Check the content licence before redistributing. |
| rustitch (crates.io) | PES fixtures only | not verified | No DST files. |
| Wikimedia Commons, Thingiverse, Printables | — | — | Searches found no openly licensed DST files. Printables results are hardware (hoops), not designs. |
| Emoji Embroidery Project (TECFA, Univ. Geneva) https://edutechwiki.unige.ch/en/Emoji_Embroidery_Project | DST mentioned, hosting unclear | **Contradictory:** the page says CC BY-SA 4.0 in one section and CC BY-NC-SA 4.0 in another | Emoji designs. Confirm the licence with the project before using. |

## 3. Free-design sites for manual download (not downloaded)

| Site | Formats | Terms (as stated on the page) | Logo-relevance |
|---|---|---|---|
| Madeira UK https://www.madeira.co.uk/dstfiles/ | DST (formats not listed on the page itself) | "Completely free for commercial and domestic use". Asks for #MadeiraThreads when shared on social media. No full licence text. | Includes a "60-weight Logo", flag sets, badges and a **Tension Test** design. Professionally digitized, so the best quality references among these. |
| Madeira USA https://www.madeirausa.com/resources/free-embroidery-design-downloads/ | DST + run sheets | No terms stated | 5 seasonal designs, incl. a multi-thread scuba diver. |
| Æthelmearc (SCA) https://aeans.aethelmearc.org/machine-embroidery-files/ | DST, EMB, EXP, HUS, PES (zip, 9.6 MB) | "For anyone to use in their embroidery projects". Digitized by Absolute Digitizing, shared with permission. No named licence. | Heraldic arms and badges: crest-like fills and satin. |
| free-embroidery-files.com https://free-embroidery-files.com/faq/ | DST, PES, JEF, EXP, HUS, VP3, VIP, XXX | Personal use only. **No redistribution**. Commercial licence costs EUR 100. | Not usable as shared test fixtures. |

None of the sites in section 3 gives an open licence that allows redistribution in a test repository. Use their files locally as references only, or ask the publisher for permission.
