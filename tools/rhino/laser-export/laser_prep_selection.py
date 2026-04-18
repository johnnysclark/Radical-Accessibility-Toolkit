# -*- coding: utf-8 -*-
"""
Laser Prep (Selection) -- move currently-selected objects onto a laser layer.

Three operations:
  - cut             -> Cut Layer, color ByLayer (renders red)
  - engrave         -> Engrave Layer, color ByLayer (renders black)
  - vector_engrave  -> Engrave Layer, object color RGB(0, 255, 0)
                       overriding ByLayer so the shop reads it as vector engrave.
                       Also sets per-object plot width to 0.014 mm.

Usage inside Rhino:

    import laser_prep_selection as lps
    lps.stage("cut")
    lps.stage("engrave")
    lps.stage("vector_engrave")

Or via RhinoScript command line (if wrapped in a PythonScript alias):

    _-RunPythonScript "<path>/laser_prep_selection.py"
    -> operates on current selection, prompts for op if none given.

IronPython 2.7 compatible.
"""

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

import laser_setup as _ls


_GREEN_RGB = (0, 255, 0)
_VECTOR_ENGRAVE_PLOT_WIDTH_MM = 0.014


def _ensure_ready():
    """Make sure the laser layers exist before staging anything."""
    _ls.ensure_layers(draw_artboard=False)


def _set_object_color(guid, rgb):
    """Set an object's display color explicitly (overrides ByLayer)."""
    rs.ObjectColorSource(guid, 1)  # 1 = by object
    rs.ObjectColor(guid, rgb)


def _set_object_color_by_layer(guid):
    """Set an object to inherit layer color."""
    rs.ObjectColorSource(guid, 0)  # 0 = by layer


def _set_object_plot_weight(guid, width_mm):
    """Set per-object plot width in mm. -1 = default, 0 = no-plot."""
    try:
        rs.ObjectPrintWidth(guid, float(width_mm))
        rs.ObjectPrintWidthSource(guid, 1)  # 1 = by object
    except Exception:
        # Older Rhino APIs -- fall back silently
        pass


def stage(op):
    """Move the current selection onto the appropriate laser layer.

    Args:
        op: "cut", "engrave", or "vector_engrave"

    Returns:
        count of objects staged (int). Prints OK/ERROR/READY lines.
    """
    op = (op or "").strip().lower().replace("-", "_")
    if op not in ("cut", "engrave", "vector_engrave"):
        print("ERROR: laser_prep_selection.stage: op must be 'cut', 'engrave', or 'vector_engrave'. Got '{0}'.".format(op))
        print("READY:")
        return 0

    _ensure_ready()

    sel = rs.SelectedObjects() or []
    if not sel:
        print("ERROR: laser_prep_selection.stage('{0}'): no selection. Select objects first.".format(op))
        print("READY:")
        return 0

    if op == "cut":
        target_layer = _ls.LAYER_CUT
    else:
        target_layer = _ls.LAYER_ENGRAVE

    count = 0
    for guid in sel:
        rs.ObjectLayer(guid, target_layer)
        if op == "vector_engrave":
            _set_object_color(guid, _GREEN_RGB)
            _set_object_plot_weight(guid, _VECTOR_ENGRAVE_PLOT_WIDTH_MM)
        else:
            _set_object_color_by_layer(guid)
            # Clear any explicit per-object plot-width override so layer's value applies
            try:
                rs.ObjectPrintWidthSource(guid, 0)  # 0 = by layer
            except Exception:
                pass
        count += 1

    print("OK: staged {0} object(s) on '{1}' (op={2}).".format(count, target_layer, op))
    print("READY:")
    return count


if __name__ == "__main__":
    # When run as a script, prompt for the operation.
    choice = rs.GetString("Laser op", "cut", ["cut", "engrave", "vector_engrave"])
    if choice:
        stage(choice)
