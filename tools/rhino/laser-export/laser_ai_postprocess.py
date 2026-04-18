# -*- coding: utf-8 -*-
"""
Laser AI Post-Process -- patch a Rhino-generated .ai so it opens cleanly
in Adobe Illustrator with the SCD shop spec already applied.

Rhino's native -_Export to .ai has five defects that the SCD template
expects you to fix by hand. This module fixes all five in one pass so the
exported .ai is ready to send straight to the laser.

The five fixes
--------------
1. Artboard size. Rhino writes no AI7_ArtboardBox, so Illustrator falls back
   to a default 8.5 x 11 letter page. We inject the correct artboard box,
   ArtSize, and RulerUnits headers, plus correct TileBox and TemplateBox.

2. Bounding box. Rhino's BoundingBox header wraps only the geometry, not
   the artboard, so it can be wrong when the artboard extends past the
   drawn content. We rewrite it to the artboard rectangle.

3. Color model. Rhino writes colors as CMYK (K/k operators) with no
   AI9_ColorModel header, so Illustrator opens in CMYK mode and the RGB
   values the shop needs are wrong. We add AI9_ColorModel: 1 (RGB) and
   substitute RGB stroke/fill operators (XA/Xa) for the CMYK ones Rhino
   emitted.

4. Color values. Pure-red CMYK (0,1,1,0), pure-green (1,0,1,0), and
   pure-black (0,0,0,1) are substituted for their RGB equivalents so
   the shop's action script sees the exact triples it keys on.

5. Stroke weight. Rhino writes "1.0000 w" for every line, ignoring the
   layer PlotWeight. We replace with 0.0720 w, which is 0.001 inch at
   72 pt/in -- the SCD shop spec for both cut and vector-engrave.

This patching is pure text substitution on the AI file, which is AI3
PostScript format. IronPython 2.7 compatible.

Usage::

    import laser_ai_postprocess
    laser_ai_postprocess.fix_ai_file("C:/tmp/plaza.ai")               # 40x24
    laser_ai_postprocess.fix_ai_file("C:/tmp/plaza.ai", 24.0, 18.0)   # custom bed
"""

import os
import re


# SCD laser bed default: 40 wide x 24 tall, inches. Landscape.
_DEFAULT_W_IN = 40.0
_DEFAULT_H_IN = 24.0

# SCD shop stroke spec: 0.001 inch. 72 pt/in => 0.072 pt.
_SCD_STROKE_PT = 0.072

# CMYK triples Rhino writes for the three Rhino layer colors that matter
# to the SCD workflow. Values must match the Rhino export verbatim
# (four decimals, CMYK order).
_CMYK_TO_RGB = [
    # (cmyk operand string, rgb operand string)
    ("0.0000 1.0000 1.0000 0.0000", "1.0000 0.0000 0.0000"),  # pure red  (cut)
    ("1.0000 0.0000 1.0000 0.0000", "0.0000 1.0000 0.0000"),  # pure green (vector engrave)
    ("0.0000 0.0000 0.0000 1.0000", "0.0000 0.0000 0.0000"),  # pure black (engrave)
]


def _replace_first(content, pattern, replacement):
    """Replace first regex match; return content unchanged if no match."""
    return re.sub(pattern, replacement, content, count=1)


def fix_ai_file(path, artboard_w_in=None, artboard_h_in=None):
    """Patch a Rhino-exported .ai in place to match the SCD laser spec.

    Args:
        path: absolute path to the .ai file Rhino just wrote.
        artboard_w_in: artboard width in inches (default 40").
        artboard_h_in: artboard height in inches (default 24").

    Returns:
        True on success, False otherwise. Prints OK/ERROR/READY lines.
    """
    if not os.path.isfile(path):
        print("ERROR: fix_ai_file: file not found: {0}".format(path))
        print("READY:")
        return False

    if artboard_w_in is None:
        artboard_w_in = _DEFAULT_W_IN
    if artboard_h_in is None:
        artboard_h_in = _DEFAULT_H_IN

    w_pt = artboard_w_in * 72.0
    h_pt = artboard_h_in * 72.0
    w_pt_int = int(round(w_pt))
    h_pt_int = int(round(h_pt))

    try:
        f = open(path, "r")
        try:
            content = f.read()
        finally:
            f.close()
    except Exception as e:
        print("ERROR: fix_ai_file: cannot read {0}: {1}".format(path, e))
        print("READY:")
        return False

    # --- Fix 1 + 2: BoundingBox and HiResBoundingBox -> artboard rectangle
    content = _replace_first(
        content,
        r"%%BoundingBox:[^\r\n]*",
        "%%BoundingBox: 0 0 {0} {1}".format(w_pt_int, h_pt_int),
    )
    content = _replace_first(
        content,
        r"%%HiResBoundingBox:[^\r\n]*",
        "%%HiResBoundingBox: 0 0 {0:.4f} {1:.4f}".format(w_pt, h_pt),
    )

    # --- Fix 1 continued: artboard + ruler + color-model headers, injected
    # just after the AI3_ColorUsage line so downstream procsets see them.
    inject = "\n".join([
        "%AI9_ColorModel: 1",          # 1 = RGB, 2 = CMYK
        "%AI5_RulerUnits: 0",          # 0 = inches
        "%AI7_ArtboardBox: 0 0 {0} {1}".format(w_pt_int, h_pt_int),
        "%AI5_ArtSize: {0} {1}".format(w_pt_int, h_pt_int),
    ])
    if "%AI9_ColorModel" not in content:
        content = content.replace(
            "%AI3_ColorUsage: Color",
            "%AI3_ColorUsage: Color\n" + inject,
            1,
        )

    # --- Fix 1 continued: TileBox and TemplateBox need to match artboard
    content = _replace_first(
        content,
        r"%AI3_TileBox:[^\r\n]*",
        "%AI3_TileBox: 0 0 {0} {1}".format(w_pt_int, h_pt_int),
    )
    content = _replace_first(
        content,
        r"%AI3_TemplateBox:[^\r\n]*",
        "%AI3_TemplateBox: {0} {1} {0} {1}".format(w_pt_int // 2, h_pt_int // 2),
    )

    # --- Fix 3 + 4: CMYK K/k operators -> RGB XA/Xa operators, for the
    # three Rhino layer colors the SCD workflow cares about.
    for cmyk, rgb in _CMYK_TO_RGB:
        content = content.replace(cmyk + " K", rgb + " XA")
        content = content.replace(cmyk + " k", rgb + " Xa")

    # --- Fix 5: stroke weight -> 0.001 inch at 72 pt/in
    # Rhino writes whatever the layer PlotWeight resolves to, so we can't
    # predict the exact value. Match any decimal followed by " w " -- this is
    # the AI3 line-width operator and it always appears after a numeric
    # operand. Use a regex with a leading space boundary so we don't chew
    # through unrelated tokens (for example "1 j" or "4 M" that live on the
    # same line as the stroke-width command).
    stroke_pt = "{0:.4f}".format(_SCD_STROKE_PT)
    content = re.sub(
        r"(?<= )\d+(?:\.\d+)? w ",
        stroke_pt + " w ",
        content,
    )

    try:
        f = open(path, "w")
        try:
            f.write(content)
        finally:
            f.close()
    except Exception as e:
        print("ERROR: fix_ai_file: cannot write {0}: {1}".format(path, e))
        print("READY:")
        return False

    print("OK: patched {0} for SCD spec (artboard {1}x{2}\", RGB, 0.001\" stroke).".format(
        path, artboard_w_in, artboard_h_in))
    print("READY:")
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2:
        fix_ai_file(sys.argv[1])
    else:
        print("Usage: python laser_ai_postprocess.py <path-to-ai>")
