# -*- coding: utf-8 -*-
"""
Fabrication Validation for Layout Jig state.json
==================================================
Validates properties affecting physical output:
  - STL export readiness (tactile3d settings)
  - minimum printable wall thickness
  - export path sanity
  - Bambu printer configuration

Python 3 stdlib only.
"""
import os


def _issue(level, code, message, path=""):
    return {"level": level, "code": code, "message": message, "path": path}


# Minimum wall thickness for FDM 3D printing (mm at model scale)
MIN_WALL_THICKNESS_FT = 0.25  # quarter foot at design scale
MIN_FLOOR_THICKNESS_FT = 0.25


def validate_fabrication(state):
    """Validate fabrication readiness (3D print, STL export).

    Returns a list of issues.
    """
    issues = []

    t3d = state.get("tactile3d", {})
    if not t3d.get("enabled", False):
        return issues  # Tactile 3D not enabled; nothing to check

    # Wall height must be positive
    wall_height = t3d.get("wall_height", 9.0)
    if wall_height <= 0:
        issues.append(_issue("error", "wall_height_zero",
                             "Tactile3D wall_height must be positive (got {}).".format(
                                 wall_height),
                             "tactile3d.wall_height"))

    # Cut height should be less than wall height
    cut_height = t3d.get("cut_height", 4.0)
    if cut_height >= wall_height:
        issues.append(_issue("warning", "cut_above_wall",
                             "Tactile3D cut_height ({}) >= wall_height ({}). "
                             "Model will have no visible walls above cut.".format(
                                 cut_height, wall_height),
                             "tactile3d.cut_height"))

    # Floor thickness check
    floor_thickness = t3d.get("floor_thickness", 0.5)
    if t3d.get("floor_enabled", True) and floor_thickness < MIN_FLOOR_THICKNESS_FT:
        issues.append(_issue("warning", "thin_floor",
                             "Floor thickness {} ft may be too thin for printing.".format(
                                 floor_thickness),
                             "tactile3d.floor_thickness"))

    # Wall thickness from the bay walls
    bays = state.get("bays", {})
    for bay_name, bay in bays.items():
        walls = bay.get("walls", {})
        if walls.get("enabled", False):
            thickness = walls.get("thickness", 0.5)
            if thickness < MIN_WALL_THICKNESS_FT:
                issues.append(_issue("warning", "thin_walls",
                                     "Bay {} wall thickness {} ft may be too thin "
                                     "for 3D printing.".format(bay_name, thickness),
                                     "bays.{}.walls.thickness".format(bay_name)))

    # Export path check
    export_path = t3d.get("export_path", "")
    if t3d.get("auto_export", False) and not export_path:
        issues.append(_issue("error", "no_export_path",
                             "Auto-export is on but export_path is empty.",
                             "tactile3d.export_path"))

    # Scale factor
    scale = t3d.get("scale_factor", 1.0)
    if scale <= 0:
        issues.append(_issue("error", "bad_scale",
                             "Scale factor must be positive (got {}).".format(scale),
                             "tactile3d.scale_factor"))

    # Bambu printer config
    bambu = state.get("bambu", {})
    if bambu:
        print_scale = bambu.get("print_scale", 200)
        if print_scale <= 0:
            issues.append(_issue("error", "bad_print_scale",
                                 "Bambu print_scale must be positive.".format(print_scale),
                                 "bambu.print_scale"))

    return issues


def format_results(issues):
    """Format fabrication validation issues as screen-reader-friendly text."""
    if not issues:
        return "OK: Fabrication validation passed. No issues."
    lines = []
    errors = sum(1 for i in issues if i["level"] == "error")
    warnings = sum(1 for i in issues if i["level"] == "warning")
    lines.append("{} issues ({} errors, {} warnings):".format(
        len(issues), errors, warnings))
    for idx, issue in enumerate(issues, 1):
        level = issue["level"].upper()
        lines.append("  {}. {}: {} [{}]".format(
            idx, level, issue["message"], issue["path"]))
    return "\n".join(lines)
