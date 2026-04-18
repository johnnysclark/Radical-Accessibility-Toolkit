# -*- coding: utf-8 -*-
"""
Laser Export -- export staged geometry to Adobe Illustrator (.ai) for the
Siebel Center for Design 24x40" laser cutter.

Produces an .ai that opens in Illustrator with the SCD shop spec already
applied: 40 x 24 inch artboard, RGB color mode, RGB 255/0/0 cut stroke,
0.001" stroke weight, and the "Cut Layer" / "Engrave Layer" names that the
shop's laser action script keys on. No Illustrator cleanup required.

Pipeline::

    (1) pre-scale selection by 24/D (compensates for Rhino's AI exporter
        writing 36 pt per doc unit instead of the 72 pt per inch that the
        AI spec expects, and bakes in the target print scale)
    (2) Rhino -_Export to .ai
    (3) undo the pre-scale so the source Rhino file is unchanged
    (4) laser_ai_postprocess.fix_ai_file to patch the five AI-format
        defects Rhino leaves behind. See that module's docstring for the
        full list.

Usage inside Rhino::

    import laser_export
    laser_export.export_laser_ai("C:/path/out.ai", 1, 100)          # 1:100
    laser_export.export_laser_ai("C:/path/out.ai", 1, 192)          # 1/16"=1'
    laser_export.export_laser_ai("C:/path/out.ai", 1, 48,           # 1/4"=1'
                                 selection_only=False)

Selection policy:
  - selection_only=True  (default): exports the current selection --
    matches the usual "Export Selected" habit.
  - selection_only=False: selects everything on Cut Layer and Engrave
    Layer (ignores Artboard), then exports.

After export, open the .ai in Illustrator and drop it into the SCD
template at::

  C:\\Users\\<you>\\OneDrive - University of Illinois - Urbana\\
     Spring 2026\\Arch 499\\Plaza Solar Furniture\\
     24x40in_laser_template--SCD.ait

IronPython 2.7 compatible.
"""

import os
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

import laser_setup as _ls
import laser_ai_postprocess as _ai


def _count_on_layer(layer_name):
    objs = rs.ObjectsByLayer(layer_name) or []
    return len(objs)


def _count_green_on_engrave():
    """How many objects on Engrave Layer have explicit green color?"""
    n = 0
    for guid in rs.ObjectsByLayer(_ls.LAYER_ENGRAVE) or []:
        src = rs.ObjectColorSource(guid)
        if src == 1:  # by object
            col = rs.ObjectColor(guid)
            try:
                r, g, b = col.R, col.G, col.B
            except AttributeError:
                continue
            if r == 0 and g == 255 and b == 0:
                n += 1
    return n


def _select_all_on_laser_layers():
    """Select every object on Cut Layer and Engrave Layer. Return count."""
    rs.UnselectAllObjects()
    targets = []
    for name in (_ls.LAYER_CUT, _ls.LAYER_ENGRAVE):
        objs = rs.ObjectsByLayer(name) or []
        targets.extend(objs)
    if targets:
        rs.SelectObjects(targets)
    return len(targets)


def _bounds_warn(path_warning_prefix, scale_num, scale_den):
    """Warn (non-blocking) if staged geometry exceeds the artboard at the
    requested scale. Purely informational; never raises.
    """
    artboard_objs = rs.ObjectsByLayer(_ls.LAYER_ARTBOARD) or []
    if not artboard_objs:
        return
    ab_bbox = rs.BoundingBox(artboard_objs)
    if not ab_bbox:
        return

    staged = []
    for name in (_ls.LAYER_CUT, _ls.LAYER_ENGRAVE):
        staged.extend(rs.ObjectsByLayer(name) or [])
    if not staged:
        return

    bb = rs.BoundingBox(staged)
    if not bb:
        return

    factor = float(scale_den) / float(scale_num)
    ab_min, ab_max = ab_bbox[0], ab_bbox[6]
    ab_w = (ab_max[0] - ab_min[0]) * factor
    ab_h = (ab_max[1] - ab_min[1]) * factor

    g_min, g_max = bb[0], bb[6]
    g_w = g_max[0] - g_min[0]
    g_h = g_max[1] - g_min[1]

    if g_w > ab_w or g_h > ab_h:
        print("{0}WARN: staged geometry ({1:.2f} x {2:.2f}) exceeds bed at 1:{3} ({4:.2f} x {5:.2f}).".format(
            path_warning_prefix, g_w, g_h, int(scale_den / scale_num), ab_w, ab_h))


def _compute_prescale_factor(scale_num, scale_den):
    """Return the factor to scale selected geometry by before -_Export so
    that the resulting .ai reads out at the correct 72 pt/in, at the
    requested print scale 1:D.

    Derivation:
      - Rhino's AI exporter writes 36 pt per doc unit (empirically -- half
        the 72 pt/in the AI format expects). Compensate with a 2.0 factor.
      - To reach print scale 1:D, multiply by num/den.
      - Doc units might be anything; UnitScale(Inches) tells us how many
        inches make up one doc unit. Multiply by that so one doc unit of
        geometry becomes (inches-per-unit * num/den * 2) inches on paper.
    """
    doc_to_inches = rs.UnitScale(Rhino.UnitSystem.Inches)
    return doc_to_inches * float(scale_num) / float(scale_den) * 2.0


def _scale_selection(selected_ids, factor):
    """Scale selection about world origin by factor. Returns True on success."""
    if not selected_ids:
        return False
    rs.UnselectAllObjects()
    rs.SelectObjects(selected_ids)
    cmd = "_-Scale 0,0,0 {0} _Enter".format(factor)
    return rs.Command(cmd, False)


def export_laser_ai(output_path, scale_numerator, scale_denominator,
                    selection_only=True,
                    artboard_w_in=40.0, artboard_h_in=24.0):
    """Export staged geometry to an Illustrator-ready .ai at 1:D scale.

    The produced file has: 40 x 24 in artboard (or custom), RGB color
    mode, RGB 255/0/0 / 0/255/0 / 0/0/0 strokes for cut / vector-engrave /
    engrave, 0.001" stroke weight, and the Cut Layer / Engrave Layer
    names preserved. No Illustrator cleanup is needed.

    Args:
        output_path: absolute path to the .ai file to write.
        scale_numerator: numerator of print scale (usually 1).
        scale_denominator: denominator (e.g. 100 for 1:100).
        selection_only: if True, export current selection. If False,
                        select all geometry on Cut Layer + Engrave Layer.
        artboard_w_in: artboard width in inches (default 40").
        artboard_h_in: artboard height in inches (default 24").

    Returns: True on success, False otherwise. Prints OK/ERROR/READY.
    """
    if not output_path:
        print("ERROR: export_laser_ai: output_path is required.")
        print("READY:")
        return False

    if int(scale_numerator) <= 0 or int(scale_denominator) <= 0:
        print("ERROR: export_laser_ai: scale must be positive (e.g. 1:100).")
        print("READY:")
        return False

    _ls.ensure_layers(draw_artboard=False)

    # Choose selection set
    if selection_only:
        sel = rs.SelectedObjects() or []
        if not sel:
            print("ERROR: export_laser_ai: selection_only=True but nothing is selected.")
            print("READY:")
            return False
    else:
        n = _select_all_on_laser_layers()
        if n == 0:
            print("ERROR: export_laser_ai: no geometry on Cut Layer or Engrave Layer.")
            print("READY:")
            return False
        sel = rs.SelectedObjects() or []

    _bounds_warn("", scale_numerator, scale_denominator)

    # Ensure output dir exists
    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.isdir(out_dir):
        try:
            os.makedirs(out_dir)
        except Exception as e:
            print("ERROR: export_laser_ai: cannot create output dir {0}: {1}".format(out_dir, e))
            print("READY:")
            return False

    # (1) pre-scale
    pre_scale = _compute_prescale_factor(scale_numerator, scale_denominator)
    scaled = False
    if abs(pre_scale - 1.0) > 1e-9:
        if not _scale_selection(sel, pre_scale):
            print("ERROR: export_laser_ai: pre-scale by {0} failed.".format(pre_scale))
            print("READY:")
            return False
        scaled = True

    # (2) export
    rs.UnselectAllObjects()
    rs.SelectObjects(sel)
    quoted = '"' + output_path + '"'
    cmd = "-_Export {0} _Enter".format(quoted)
    ok = rs.Command(cmd, False)

    # (3) undo pre-scale regardless of export success -- never leave the
    # source .3dm with mutated geometry.
    if scaled:
        _scale_selection(sel, 1.0 / pre_scale)

    if not ok:
        print("ERROR: export_laser_ai: -_Export command failed.")
        print("READY:")
        return False

    if not os.path.isfile(output_path):
        print("ERROR: export_laser_ai: -_Export returned OK but no file at {0}.".format(output_path))
        print("READY:")
        return False

    # (4) patch the AI file to match the SCD shop spec
    _ai.fix_ai_file(output_path, artboard_w_in, artboard_h_in)

    cut_n = _count_on_layer(_ls.LAYER_CUT)
    eng_n = _count_on_layer(_ls.LAYER_ENGRAVE)
    vec_n = _count_green_on_engrave()

    print("OK: exported {0} at 1:{1} -- {2} on Cut Layer, {3} on Engrave Layer ({4} vector-engrave green).".format(
        output_path, int(scale_denominator / scale_numerator), cut_n, eng_n, vec_n))
    print("READY:")
    return True


if __name__ == "__main__":
    path = rs.GetString("Output .ai path")
    if not path:
        print("ERROR: no path given.")
    else:
        num = rs.GetInteger("Scale numerator", 1, 1, 1000)
        den = rs.GetInteger("Scale denominator", 100, 1, 10000)
        if num and den:
            export_laser_ai(path, num, den)
