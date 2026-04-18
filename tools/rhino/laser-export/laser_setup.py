# -*- coding: utf-8 -*-
"""
Laser Setup -- ensure SCD laser layers exist in the current Rhino document.

Creates two layers that match the exact names the Siebel Center for Design
laser Illustrator template expects:

  - Cut Layer       RGB (255,   0,   0)   -- full cut
  - Engrave Layer   RGB (  0,   0,   0)   -- general engrave + vector engrave
                                             (vector engrave is green-stroked
                                              on this layer, per SCD spec)

Plus a reference-only "Artboard" layer holding a 24 x 40 inch rectangle
(non-plotting) at world origin so the user can see the bed boundary.

IronPython 2.7 compatible:
  - no f-strings
  - no pathlib
  - uses rhinoscriptsyntax + scriptcontext
"""

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino


# Inches -> feet (Rhino doc units are feet per startup.py)
_IN_TO_FT = 1.0 / 12.0
_MM_TO_IN = 1.0 / 25.4

# SCD laser bed dimensions (landscape: 40" wide, 24" tall)
_BED_W_IN = 40.0
_BED_H_IN = 24.0

# Stroke width the SCD spec calls for on cut / vector-engrave lines.
# The spec lists "0.001" / 0.014 mm" but those two values aren't equal --
# 0.001 inch is 0.0254 mm, while 0.014 mm is only 0.000551 inch. The shop
# accepts either since both are hairline, but we use 0.001" (= 0.0254 mm)
# as the canonical value so Illustrator's stroke-width readout matches
# the "0.001 in" half of the spec exactly.
_CUT_PLOT_WIDTH_MM = 0.0254
_ENGRAVE_PLOT_WIDTH_MM = 0.25       # thicker stroke for general engrave, reasonable default
_ARTBOARD_PLOT_WIDTH_MM = -1.0      # no-plot

LAYER_CUT = "Cut Layer"
LAYER_ENGRAVE = "Engrave Layer"
LAYER_ARTBOARD = "Artboard"

_CUT_COLOR = (255, 0, 0)
_ENGRAVE_COLOR = (0, 0, 0)
_ARTBOARD_COLOR = (200, 200, 200)


def _set_plot_weight(layer_name, width_mm):
    """Set a layer's plot weight by name. Silently no-op if layer missing."""
    doc = sc.doc if hasattr(sc, "doc") else Rhino.RhinoDoc.ActiveDoc
    idx = doc.Layers.FindByFullPath(layer_name, -1)
    if idx < 0:
        # Older Rhino API
        layer = doc.Layers.FindName(layer_name) if hasattr(doc.Layers, "FindName") else None
        if layer is None:
            return False
    else:
        layer = doc.Layers[idx]
    layer.PlotWeight = float(width_mm)
    layer.CommitChanges()
    return True


def _ensure_layer(name, color_rgb, plot_weight_mm):
    """Create layer if missing, set its display color and plot weight."""
    if not rs.IsLayer(name):
        rs.AddLayer(name, color=color_rgb)
    else:
        # Refresh color in case the user changed it
        rs.LayerColor(name, color_rgb)
    _set_plot_weight(name, plot_weight_mm)


def _ensure_artboard_rectangle():
    """Draw the 24 x 40 inch bed outline on LAYER_ARTBOARD if not present.

    Placed at world origin, landscape orientation (40" along X, 24" along Y).
    Geometry is tagged with UserText so we can find it on re-run without
    relying on uniqueness of the bounding box.
    """
    existing = rs.ObjectsByLayer(LAYER_ARTBOARD) or []
    for obj in existing:
        if rs.GetUserText(obj, "scd_artboard") == "1":
            return obj  # already there

    w = _BED_W_IN * _IN_TO_FT
    h = _BED_H_IN * _IN_TO_FT
    rect = rs.AddRectangle(rs.WorldXYPlane(), w, h)
    if rect is None:
        return None
    rs.ObjectLayer(rect, LAYER_ARTBOARD)
    rs.SetUserText(rect, "scd_artboard", "1")
    rs.SetUserText(rect, "scd_bed_inches", "{0}x{1}".format(_BED_W_IN, _BED_H_IN))
    return rect


def ensure_layers(draw_artboard=True):
    """Idempotent. Create Cut Layer, Engrave Layer, Artboard if missing.

    Args:
        draw_artboard: if True (default), also draw the 24x40" bed rectangle.

    Returns:
        (created, total) tuple of layer counts for a one-line status print.
    """
    before = 0
    for name in (LAYER_CUT, LAYER_ENGRAVE, LAYER_ARTBOARD):
        if rs.IsLayer(name):
            before += 1

    _ensure_layer(LAYER_CUT, _CUT_COLOR, _CUT_PLOT_WIDTH_MM)
    _ensure_layer(LAYER_ENGRAVE, _ENGRAVE_COLOR, _ENGRAVE_PLOT_WIDTH_MM)
    _ensure_layer(LAYER_ARTBOARD, _ARTBOARD_COLOR, _ARTBOARD_PLOT_WIDTH_MM)

    if draw_artboard:
        _ensure_artboard_rectangle()

    after = 3
    created = after - before
    print("OK: laser layers ready ({0} created, {1} present). Cut Layer, Engrave Layer, Artboard.".format(
        created, after))
    print("READY:")
    return (created, after)


if __name__ == "__main__":
    ensure_layers()
