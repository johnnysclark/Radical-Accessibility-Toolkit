# -*- coding: utf-8 -*-
"""
Semantic Validation for Layout Jig state.json
===============================================
Validates logical relationships between model elements:
  - corridor references valid gridlines
  - aperture placement is within bay bounds
  - cell references are within grid dimensions
  - room/cell naming consistency
  - bay naming conventions

Python 3 stdlib only.
"""


def _issue(level, code, message, path=""):
    return {"level": level, "code": code, "message": message, "path": path}


def validate_semantic(state):
    """Validate semantic correctness of the model.

    Returns a list of issues.
    """
    issues = []
    bays = state.get("bays", {})

    for bay_name, bay in bays.items():
        prefix = "bays.{}".format(bay_name)
        grid_type = bay.get("grid_type", "rectangular")
        nx, ny = bay.get("bays", [1, 1])

        # Corridor position must reference a valid gridline
        corridor = bay.get("corridor", {})
        if corridor.get("enabled", False):
            axis = corridor.get("axis", "x")
            pos = corridor.get("position", 0)
            max_pos = ny if axis == "x" else nx
            if pos < 0 or pos >= max_pos:
                issues.append(_issue("error", "corridor_out_of_range",
                                     "Bay {} corridor position {} is out of range "
                                     "(0 to {} for axis {}).".format(
                                         bay_name, pos, max_pos - 1, axis),
                                     "{}.corridor.position".format(prefix)))

            width = corridor.get("width", 0)
            if width <= 0:
                issues.append(_issue("error", "corridor_zero_width",
                                     "Bay {} corridor width must be positive.".format(
                                         bay_name),
                                     "{}.corridor.width".format(prefix)))

        # Aperture gridline references
        apertures = bay.get("apertures", [])
        for i, ap in enumerate(apertures):
            ap_axis = ap.get("axis", "x")
            ap_gridline = ap.get("gridline", 0)
            max_gl = ny + 1 if ap_axis == "x" else nx + 1
            if ap_gridline < 0 or ap_gridline > max_gl:
                issues.append(_issue("error", "aperture_gridline_out_of_range",
                                     "Bay {} aperture '{}' gridline {} is out of range "
                                     "(0 to {}).".format(
                                         bay_name, ap.get("id", i),
                                         ap_gridline, max_gl),
                                     "{}.apertures[{}]".format(prefix, i)))

            # Aperture width must be positive
            ap_width = ap.get("width", 0)
            if ap_width <= 0:
                issues.append(_issue("error", "aperture_zero_width",
                                     "Bay {} aperture '{}' width must be positive.".format(
                                         bay_name, ap.get("id", i)),
                                     "{}.apertures[{}]".format(prefix, i)))

        # Cell references (for rectangular grids)
        cells = bay.get("cells", {})
        if grid_type == "rectangular" and cells:
            for cell_key in cells:
                try:
                    parts = cell_key.replace(".", ",").split(",")
                    c, r = int(parts[0]), int(parts[1])
                    if c < 0 or c >= nx or r < 0 or r >= ny:
                        issues.append(_issue("warning", "cell_out_of_range",
                                             "Bay {} cell {} is outside grid "
                                             "({}x{}).".format(
                                                 bay_name, cell_key, nx, ny),
                                             "{}.cells.{}".format(prefix, cell_key)))
                except (ValueError, IndexError):
                    issues.append(_issue("error", "bad_cell_key",
                                         "Bay {} cell key '{}' is not a valid "
                                         "col,row reference.".format(
                                             bay_name, cell_key),
                                         "{}.cells.{}".format(prefix, cell_key)))

        # Bay label should exist
        if not bay.get("label"):
            issues.append(_issue("warning", "missing_bay_label",
                                 "Bay {} has no label.".format(bay_name),
                                 "{}.label".format(prefix)))

    # Site dimensions should be positive
    site = state.get("site", {})
    for dim in ("width", "height"):
        val = site.get(dim, 0)
        if isinstance(val, (int, float)) and val <= 0:
            issues.append(_issue("error", "site_non_positive",
                                 "Site {} must be positive (got {}).".format(
                                     dim, val),
                                 "site.{}".format(dim)))

    return issues


def format_results(issues):
    """Format semantic validation issues as screen-reader-friendly text."""
    if not issues:
        return "OK: Semantic validation passed. No issues."
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
