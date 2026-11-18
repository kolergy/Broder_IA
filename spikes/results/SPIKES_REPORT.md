# Ink/Stitch headless pipeline spikes: SVG → Ink/Stitch v3.3.0 → Tajima DST

> ⚠️ **Avertissement — contenu généré par intelligence artificielle.** Ce document a été produit avec l'aide d'une IA (Claude, Anthropic) et n'a pas été validé par un spécialiste de la broderie machine. Il peut contenir des erreurs. Toute information, tout réglage et tout fichier produit — en particulier les fichiers machine (.dst) — doivent être vérifiés par un professionnel qualifié avant usage. **Un fichier machine erroné peut endommager la brodeuse** (casse d'aiguille, bourrage, contrainte mécanique), abîmer le tissu et présenter un risque pour l'opérateur : ne jamais lancer une broderie sans contrôle préalable par un spécialiste et premier essai à vitesse réduite, sur chute de tissu.

Date: 2026-11-15. Host: Ubuntu 24.04.5 sandbox, no X display, sudo + apt available.
Layout: `spikes/{vendor,tests,results}`, venv at `spikes/venv312` (vendor and venv not included in this repository).
Every command below was actually run. All logs and outputs are in `results/`.

## Summary

| Spike | Topic | Outcome |
|---|---|---|
| S1 | Install v3.3.0 (inkex from PyPI, wx via apt) + param diff vs main | PASS |
| S2 | Smoke export (fill + running stitch + satin) → DST, read back | PASS |
| S3 | DST header extents unit | PASS (unit is 0.1 mm) |
| S4 | Empty / text-only export | PASS (exit 0, 0 bytes, message on stderr) |
| S5 | Missing `inkstitch_svg_version` | FAIL (as a pipeline behaviour): crash with no display, hangs under Xvfb |
| S6 | Gradients | PARTIAL: userSpaceOnUse works; objectBoundingBox/% is wrong; radial falls back to **black**, not the first stop |
| S7 | Opacity | PASS (opacity is ignored; see the `fill-opacity:0` exception) |
| S8 | Clip-path (transform inside clipPath, on the element and on a group) | PASS |
| S9 | Previews (stitch_plan_preview → rsvg/cairosvg; png_simple/png_realistic) | PASS |
| S10 | Trim encoding in DST | PASS: N = 3 jumps; readers' trim heuristic is misleading |

---

## S1: Install

**Goal:** run Ink/Stitch v3.3.0 from a git checkout, headless.

**Commands**
```
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-wxgtk4.0 inkscape xvfb
git clone --depth 1 --branch v3.3.0 --recurse-submodules --shallow-submodules \
    https://github.com/inkstitch/inkstitch.git vendor/inkstitch-v3.3.0
/usr/bin/python3.12 -m venv --system-site-packages venv312       # wx only exists for py3.12
venv312/bin/pip install "inkex==1.4.1"
grep -v -e '^inkex' -e '^wxPython' -e mypy -e flake8 -e '^types-' requirements.txt > tests/req_filtered.txt
venv312/bin/pip install -r tests/req_filtered.txt pyembroidery cairosvg
```
**Evidence**
- v3.3.0 commit `b0edd96311ece82ee48816dc93466274b12c2a9c` (2026-07-31). Fonts submodule cloned from GitHub without problems.
- Correction to the background notes: requirements.txt pins inkex to a GitLab **tag**, `git+https://gitlab.com/inkscape/extensions.git@EXTENSIONS_AT_INKSCAPE_1.4.1`, not a commit. GitLab is blocked: `git ls-remote` → `CONNECT tunnel failed, response 403`. PyPI `inkex==1.4.1` installs fine and was used for every spike.
- `/usr/bin/python3` and `/usr/local/bin/python3` are both 3.13.18. apt's `python3-wxgtk4.0` installs into the system Python **3.12** dist-packages only. So the working route was a py3.12 venv with `--system-site-packages`. wx is `4.2.1 gtk3 (phoenix) wxWidgets 3.2.4`. No wx stub was needed.
- Versions: inkex 1.4.1, pystitch 1.0.1, pyembroidery 1.5.1, shapely 2.2.0, numpy 2.2.6, networkx 3.7, Inkscape (apt) 1.2.2, rsvg-convert 2.58.0, cairosvg 2.9.1.
- Importing wx does not need a display. Only creating a wx App/dialog does (see S5).
- Side note: apt's Inkscape ships its own inkex 1.2.0 in `/usr/share/inkscape/extensions`. It is not on the venv's path and was not used.

**Param diff, v3.3.0 vs main** (main = `42e771e`, 2026-11-03). I compared the sorted `@param('name'` sets:
- `fill_stitch.py` (55 params): identical names. The only code change is a 3-line guard `if not stitches: return stitch_groups`.
- `stroke.py` (33 params): file identical.
- Satin: in v3.3.0 it is a single file, `lib/elements/satin_column.py` (40 `@param`s). main split it into the package `lib/elements/satin_column/` (satin_column.py, rails.py, underlay.py, ...). The param name set is **identical** (34 distinct names).
- `lib/metadata.py`, `lib/update.py`: identical. **`INKSTITCH_SVG_VERSION = 4`** in both.
- No params were renamed, added or removed. Values available in v3.3.0:
  - `fill_method`: tatami_fill, linear_gradient_fill, contour_fill, guided_fill, meander_fill, circular_fill, tartan_fill, legacy_fill, cross-stitch variants.
  - `stroke_method`: running_stitch, ripple_stitch, zigzag_stitch, manual_stitch.

**Conclusion:** PASS. The apt wx + py3.12 venv + PyPI inkex route is reproducible.

## S2: Smoke export

**Goal:** export a mixed design and verify it by reading the file back.
**Input:** `tests/s2_smoke.svg`, 100×100 mm, viewBox 0 0 100 100:
- 40×40 mm tatami square at (10,10), red
- running-stitch line from (10,70) to (90,70), blue, 2.5 mm stitch length
- satin column with rails at x=60 and x=64 (4 mm wide), y 10–50, one rung, green

**Command:** `venv312/bin/python vendor/inkstitch-v3.3.0/inkstitch.py --extension=output --format=dst tests/s2_smoke.svg > results/s2_smoke.dst`
**Evidence:** exit 0, 6239 bytes, 9.4 s wall time, empty stderr. pyembroidery and pystitch give identical results:
```
records=1909 stitches=1897 jumps=9 trims=0 color_changes=2 bounds_0.1mm=(-400,-300,400,300) → 80.00 x 60.00 mm
block 0: 1628 st, 40.00 x 40.00 mm   (square)
block 1:   42 st, 80.00 x 0.00 mm    (running line)
block 2:  227 st,  4.00 x 40.00 mm   (satin)
```
Expected overall size: 80 × 60 mm (x 10–90, y 10–70). **Exact match.** Each block's size matches its object, and blocks follow SVG document order. The DST origin is the design centre. DST carries no thread colours (`threadlist` is empty), so the colours in the pyembroidery PNG are arbitrary. Preview: `results/s2_smoke_preview.png`.
**Conclusion:** PASS.

## S3: DST header units

**Command:** `venv312/bin/python tools/dsthdr.py results/s2_smoke.dst v` (my own raw decoder)
**Evidence:**
```
ST:   1909   CO:  2   +X:  400  -X:  400  +Y:  300  -Y:  300   AX:+  140  AY:-  100
raw extents from decoded records: +X 400 -X 400 +Y 300 -Y 300
```
The header +X/−X equals 400, matching bounds() = ±400 and the 80 mm width.
**Conclusion:** PASS. Header extents are in **0.1 mm**, not cm. `ST` counts every record (stitches + jumps + colour changes + END), not just stitches. `CO` is the number of colour changes. AX/AY is the end position relative to the origin.

## S4: Empty export

**Inputs:** `tests/s4_textonly.svg` (a single `<text>`), `tests/s4_empty.svg` (metadata only).
**Evidence:** both give `EXIT=0 bytes=0`, and stderr says:
`There are no objects in the entire document that Ink/Stitch knows how to work with.` plus a Troubleshoot tip.
**Conclusion:** PASS (confirmed). The pipeline must check for empty output and/or stderr itself, because the exit code is 0.

## S5: Missing version tag

**Input:** `tests/s5_noversion.svg` (S2 without `<metadata>`).
**Evidence:**
- No DISPLAY: `EXIT=1 bytes=0`, stderr `Unable to access the X Display, is $DISPLAY set properly?`
- Under `timeout 40 xvfb-run -a ...`: `EXIT=124`. The process blocks on the modal wx "update document" dialog until it is killed.
- Control case `tests/s5b_noattrs.svg` (no version tag **and** no `inkstitch:` attributes): exit 0, 8222 bytes. Code path (`lib/update.py`): if no element has an Ink/Stitch-namespace attribute, the document is treated as new and the version is set silently. Only a document that has inkstitch attributes but no version (version 0) calls `RequestUpdate()` (wx). The xmlns declaration alone does not trigger it. There is no CLI switch for `warn_unversioned`.

**Conclusion:** the behaviour is confirmed and it is a hard failure mode. The pipeline **must** always write `<inkstitch:inkstitch_svg_version>4</...>` in `<metadata>`. Otherwise it crashes headless, or hangs forever under Xvfb.

## S6: Gradients

Commands: export each file to dst, pes and csv. The csv export gives exact thread RGB values; the PES export gives coloured PNGs through pyembroidery `write_png`.

| File | Gradient | Result |
|---|---|---|
| `s6a_lin_pct_bbox.svg` | linear, x1=0% y1=0% x2=100% y2=70%, 3 stops, default (objectBoundingBox) units, `linear_gradient_fill` | **Wrong.** Only 2 colour blocks (#ff0000, #0000ff). The green stop is missing, and the preview shows repeating vertical red/blue bands (`results/s6a_lin_pct_bbox_preview.png`). |
| `s6b_lin_userspace.svg` | linear, userSpaceOnUse, (10,10)→(70,50), `linear_gradient_fill` | **Correct.** 3 blocks red/green/blue (1063/1153/395 stitches), with diagonal colour bands in the expected direction (`results/s6b_lin_userspace_preview.png`). |
| `s6c_radial_default.svg` | radial, default fill | 1 block, thread **#000000 (Black)**, not the first stop #ffaa00. |
| `s6d_lin_default_fill.svg` | linear, default (tatami) fill | 1 block, #ff0000 = first stop (as expected). |

**Root cause, s6a:** `lib/stitches/linear_gradient_fill.py::gradient_start_end` reads `gradient.x1()..y2()` as user-space coordinates. It applies only the node transform and ignores `gradientUnits`. inkex turns "100%" into 1.0. So the gradient vector becomes (0,0)→(1,0.7) mm, outside the shape, and the colour bands are mis-placed.
**Root cause, s6c:** `FillStitch.color` takes the first stop only for `isinstance(color, LinearGradient)`. A RadialGradient is not a LinearGradient, so the colour ends up black.
**Conclusion:** PARTIAL. The pipeline must convert gradients to `gradientUnits="userSpaceOnUse"` with absolute coordinates (resolving any gradientTransform) before export. Radial gradients must be replaced by an explicit solid fill.

## S7: Opacity

All on a 40×40 red rect; `results/s7_*.dst`:

| Style | Result |
|---|---|
| `opacity:1` / `opacity:0.5` / **`opacity:0`** | Stitched normally: 2567 stitches, 40×40 mm, all identical. |
| `fill-opacity:0.5` | Stitched normally, identical. |
| `fill-opacity:0` | **Not stitched.** Exit 0, 0 bytes, "no objects..." message. |

**Conclusion:** PASS. Opacity has no effect on stitching. Even fully transparent objects (`opacity:0`) get stitched, while `fill-opacity:0` removes the fill. The pipeline should remove invisible objects itself.

## S8: Clip-path

Clip: `<clipPath clipPathUnits="userSpaceOnUse"><path d="M0,0H20V20H0Z" transform="translate(20,20)"/>`. Clipped objects: a fill rect (10..50) and a running line at y=30 from x 10 to 90.
- `s8_clip.svg` (clip-path on each element) and `s8b_clip_group.svg` (clip-path on a parent `<g>`) give identical results:
```
block 0 (fill): 763 st, 20.00 x 20.00 mm      block 1 (line): 18 st, 20.00 mm long
overall bounds 20 x 20 mm
```
If the transform had been ignored, the result would be 10×10 mm (clip box 0..20 ∩ rect 10..50). 20×20 mm proves the transform inside clipPath is applied.
**Conclusion:** PASS. Clip-paths (with an internal transform, on the element or on a group) are respected for both fill and stroke.

## S9: Previews

(a) `stitch_plan_preview`:
```
inkstitch.py --extension=stitch_plan_preview --render-mode=simple tests/s2_smoke.svg > results/s9a_preview_simple.svg        # exit 0
inkstitch.py --extension=stitch_plan_preview --render-mode=simple --move-to-side=false --layer-visibility=hidden tests/s2_smoke.svg > results/s9a_preview_simple_inplace.svg
inkstitch.py --extension=stitch_plan_preview --render-mode=realistic-300 --move-to-side=false tests/s2_smoke.svg > results/s9a_realistic_inplace.svg
rsvg-convert -w 1000 -b white -o results/s9a_simple_page_rsvg.png    results/s9a_preview_simple_inplace.svg   # OK
rsvg-convert -w 1000 -b white -o results/s9a_realistic_page_rsvg.png results/s9a_realistic_inplace.svg       # OK, filters rendered
cairosvg (output_width=1000) on the realistic SVG                                                             # OK
```
Gotchas:
- By default (`--move-to-side=true`) the plan layer gets `transform="translate(100,0)"`, which is off-page. A full-page render then shows only the original design (`s9a_preview_simple_rsvg.png`). Use `--move-to-side=false`.
- `--layer-visibility=hidden` hides only **layers**. My test objects sit directly under `<svg>`, so they stay visible. Put the design inside a layer.
- `rsvg-convert --export-id=__inkstitch_stitch_plan__` on the realistic SVG fails with `has no dimensions` (filter region). Render the whole page instead.

(b) `png_simple` / `png_realistic` use the Inkscape binary (`inkscape` 1.2.2 from apt), headless, with no DISPLAY:
```
inkstitch.py --extension=png_simple    --dpi=150 tests/s2_smoke.svg > results/s9b_png_simple.png     # exit 0, 474x356 PNG
inkstitch.py --extension=png_realistic --dpi=150 tests/s2_smoke.svg > results/s9b_png_realistic.png  # exit 0, 474x357 PNG
```
474 px = 80 mm at 150 dpi (expected 472). The output is cropped to the stitch plan and has correct colours.
**Conclusion:** PASS for both routes. png_realistic is the best one-step visual check. The `INKSCAPE_COMMAND` env var can point at a different Inkscape binary.

## S10: Trims

Inputs: two 15×15 mm red squares at (5,5) and (75,75), same colour. Variant 1 has `inkstitch:trim_after="true"` on the first square, variant 2 has `"false"`.
Raw records (`tools/dsthdr.py`; dy shown in my decoder's sign convention):
```
trim_after=true : [JUMP 4][STITCH 471][JUMP 8][STITCH 472][END]
   rec 475 JUMP (2,-2) / rec 476 JUMP (-4,4) / rec 477 JUMP (2,-2)   ← trim, net displacement 0
   rec 478-482 JUMP (110,-110) x5                                     ← travel
trim_after=false: [JUMP 4][STITCH 471][JUMP 5][STITCH 472][END]       ← travel only
```
This matches the pystitch DstWriter source: a TRIM is written as `trim_at` (default **3**) jumps: +2, −4, +2 (0.1 mm units per axis). Ink/Stitch writes through **pystitch** (`lib/output.py`) with `trims=True, full_jump=True`.
**N = 3.**

Surprise: on read, pyembroidery and pystitch report **`trims=1` for both files**. `dst_read_stitches` calls `interpolate_trims(trim_at=3)`, which turns any run of ≥3 jumps into a TRIM, so the 5-jump travel is also reported as a trim. Reading with `{'trim_at': 1000}` gives trims=0 for both files. To check trims, use the raw records (the ±2/∓4/±2 signature), not `count_stitch_commands(TRIM)`. Real machines may apply a similar jump-count trim setting.
**Conclusion:** PASS.

## Artefacts
- Scripts: `tools/readdst.py` (read-back summary via both libraries), `tools/blocks.py` (per-colour-block bounds), `tools/dsthdr.py` (raw DST header and record decoder).
- PNGs in `results/`: `s2_smoke_preview.png`, `s6a_lin_pct_bbox_preview.png`, `s6b_lin_userspace_preview.png`, `s6c_radial_default_preview.png`, `s6d_lin_default_fill_preview.png`, `s9a_simple_page_rsvg.png`, `s9a_realistic_page_rsvg.png`, `s9a_realistic_page_cairosvg.png`, `s9a_preview_simple_rsvg.png` (the off-page gotcha), `s9b_png_simple.png`, `s9b_png_realistic.png`.
