# -*- coding: utf-8 -*-
"""
Laser Prep (Make2D) -- run Rhino's Make2D on the current selection, then
stage the resulting 2D curves onto a laser layer.

Usage inside Rhino:

    import laser_prep_make2d as lpm
    lpm.make2d_and_stage("cut")      # flatten + send to Cut Layer
    lpm.make2d_and_stage("engrave")
    lpm.make2d_and_stage("vector_engrave")

Notes on scope and layout:

- Make2D projects the selection onto the active construction plane (CPlane)
  and creates 2D curves grouped by visibility:
  visible / hidden / tangent visible / tangent hidden / clipping.
- This helper only keeps the *visible* curves; hidden lines are deleted
  to keep the laser output clean. Users who want hidden-line dashed
  engraving can stage them manually after running standard _Make2D.
- Output curves land on Rhino's generated Make2D layers first, then this
  helper moves them to the chosen laser layer.

IronPython 2.7 compatible.
"""

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

import laser_setup as _ls
import laser_prep_selection as _lps


def _active_view_is_3d():
    view = rs.CurrentView()
    if not view:
        return False
    cplane = rs.ViewCPlane(view)
    # heuristic: in plan views, CPlane z-axis is (0,0,1); in 3D views too,
    # but Make2D behavior is sensitive to viewport projection. We'll just
    # trust the user to pick the view they want projected.
    return True


def _collect_make2d_curves_before_after(existing_curves):
    """Return curves that exist now but didn't before -- the Make2D output."""
    all_curves = rs.ObjectsByType(4) or []  # 4 = curve
    new = [g for g in all_curves if g not in existing_curves]
    return new


def make2d_and_stage(op):
    """Run Make2D on the current selection and stage visible output curves.

    Args:
        op: "cut", "engrave", or "vector_engrave"

    Returns:
        count of resulting 2D curves staged (int). Prints OK/ERROR/READY.
    """
    op = (op or "").strip().lower().replace("-", "_")
    if op not in ("cut", "engrave", "vector_engrave"):
        print("ERROR: laser_prep_make2d: op must be 'cut', 'engrave', or 'vector_engrave'. Got '{0}'.".format(op))
        print("READY:")
        return 0

    sel = rs.SelectedObjects() or []
    if not sel:
        print("ERROR: laser_prep_make2d: no selection. Select 3D geometry first.")
        print("READY:")
        return 0

    _ls.ensure_layers(draw_artboard=False)

    # Snapshot existing curves so we can identify the Make2D output
    existing_curves = set(rs.ObjectsByType(4) or [])

    # Run Make2D via command line.  _NoGroup keeps pieces editable.
    # _Project=_CPlane projects onto the active construction plane.
    ok = rs.Command("_-Make2D _SelectedObjects=_Yes _DrawingLayout=_CurrentView"
                    " _ShowTangentEdges=_No _ShowHiddenLines=_No _Enter", False)
    if not ok:
        print("ERROR: laser_prep_make2d: Make2D command failed.")
        print("READY:")
        return 0

    new_curves = [g for g in (rs.ObjectsByType(4) or []) if g not in existing_curves]
    if not new_curves:
        print("ERROR: laser_prep_make2d: Make2D produced no new curves.")
        print("READY:")
        return 0

    # Keep only "visible" curves; delete the hidden-line variants that Rhino
    # puts on auto-generated Make2D layers named "...hidden"/"...dashed".
    visible = []
    for guid in new_curves:
        layer = rs.ObjectLayer(guid) or ""
        low = layer.lower()
        if "hidden" in low or "dashed" in low or "clipping" in low:
            rs.DeleteObject(guid)
        else:
            visible.append(guid)

    if not visible:
        print("ERROR: laser_prep_make2d: Make2D produced only hidden/dashed lines; nothing visible to stage.")
        print("READY:")
        return 0

    # Select the visible curves and stage them
    rs.UnselectAllObjects()
    rs.SelectObjects(visible)
    return _lps.stage(op)


if __name__ == "__main__":
    choice = rs.GetString("Laser op (after Make2D)", "cut", ["cut", "engrave", "vector_engrave"])
    if choice:
        make2d_and_stage(choice)
