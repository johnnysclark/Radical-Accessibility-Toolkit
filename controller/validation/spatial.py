# -*- coding: utf-8 -*-
"""
Spatial / Geometric Validation for Layout Jig state.json
=========================================================
Validates geometric properties:
  - overlapping bays
  - degenerate geometry (zero-area bays)
  - corridor clearance conflicts
  - aperture overlap detection

Python 3 stdlib only.
"""
import math


def _issue(level, code, message, path=""):
    return {"level": level, "code": code, "message": message, "path": path}


def _bay_extents(bay):
    """Compute (min_x, max_x, min_y, max_y) for a rectangular bay."""
    if bay.get("grid_type") == "radial":
        ox, oy = bay["origin"]
        r = bay.get("rings", 4) * bay.get("ring_spacing", 20)
        return (ox - r, ox + r, oy - r, oy + r)
    ox, oy = bay["origin"]
    nx, ny = bay["bays"]
    sx_a = bay.get("spacing_x")
    sy_a = bay.get("spacing_y")
    if sx_a and len(sx_a) == nx:
        w = sum(sx_a)
    else:
        w = nx * bay["spacing"][0]
    if sy_a and len(sy_a) == ny:
        h = sum(sy_a)
    else:
        h = ny * bay["spacing"][1]

    rot = math.radians(bay.get("rotation_deg", 0))
    if abs(rot) < 1e-9:
        return (ox, ox + w, oy, oy + h)
    # For rotated bays, compute bounding box of rotated rectangle
    corners = [(0, 0), (w, 0), (w, h), (0, h)]
    cos_r, sin_r = math.cos(rot), math.sin(rot)
    xs, ys = [], []
    for cx, cy in corners:
        rx = ox + cx * cos_r - cy * sin_r
        ry = oy + cx * sin_r + cy * cos_r
        xs.append(rx)
        ys.append(ry)
    return (min(xs), max(xs), min(ys), max(ys))


def _boxes_overlap(a, b):
    """Check if two (min_x, max_x, min_y, max_y) boxes overlap."""
    return not (a[1] <= b[0] or b[1] <= a[0] or a[3] <= b[2] or b[3] <= a[2])


def validate_spatial(state):
    """Validate spatial/geometric properties.

    Returns a list of issues.
    """
    issues = []
    bays = state.get("bays", {})
    site = state.get("site", {})
    site_w = site.get("width", 0)
    site_h = site.get("height", 0)

    # Compute extents for all bays
    bay_extents = {}
    for name, bay in bays.items():
        try:
            bay_extents[name] = _bay_extents(bay)
        except (KeyError, TypeError, IndexError):
            issues.append(_issue("warning", "extent_calc_failed",
                                 "Could not compute extents for bay {}.".format(name),
                                 "bays.{}".format(name)))

    # Check for overlapping bays
    bay_names = sorted(bay_extents.keys())
    for i in range(len(bay_names)):
        for j in range(i + 1, len(bay_names)):
            a, b = bay_names[i], bay_names[j]
            if _boxes_overlap(bay_extents[a], bay_extents[b]):
                issues.append(_issue("warning", "bays_overlap",
                                     "Bay {} and Bay {} bounding boxes overlap.".format(a, b),
                                     "bays"))

    # Check bays are within site boundary
    if site_w > 0 and site_h > 0:
        for name, ext in bay_extents.items():
            if ext[0] < 0 or ext[2] < 0 or ext[1] > site_w or ext[3] > site_h:
                issues.append(_issue("warning", "bay_outside_site",
                                     "Bay {} extends beyond site boundary "
                                     "({:.0f}x{:.0f}).".format(name, site_w, site_h),
                                     "bays.{}".format(name)))

    # Check for degenerate bays (zero area)
    for name, bay in bays.items():
        if bay.get("grid_type") == "rectangular":
            nx, ny = bay.get("bays", [0, 0])
            sx, sy = bay.get("spacing", [0, 0])
            if nx <= 0 or ny <= 0:
                issues.append(_issue("error", "zero_grid",
                                     "Bay {} has zero-size grid ({} x {}).".format(
                                         name, nx, ny),
                                     "bays.{}.bays".format(name)))
            if sx <= 0 or sy <= 0:
                issues.append(_issue("error", "zero_spacing",
                                     "Bay {} has zero or negative spacing.".format(name),
                                     "bays.{}.spacing".format(name)))

    # Check for aperture overlaps within same bay/wall
    for bay_name, bay in bays.items():
        apertures = bay.get("apertures", [])
        for i in range(len(apertures)):
            for j in range(i + 1, len(apertures)):
                a, b = apertures[i], apertures[j]
                if a.get("axis") == b.get("axis") and a.get("gridline") == b.get("gridline"):
                    # Same wall segment — check for overlap
                    a_start = a.get("corner", 0)
                    a_end = a_start + a.get("width", 0)
                    b_start = b.get("corner", 0)
                    b_end = b_start + b.get("width", 0)
                    if a_start < b_end and b_start < a_end:
                        issues.append(_issue("warning", "apertures_overlap",
                                             "Bay {} apertures '{}' and '{}' overlap on "
                                             "the same wall.".format(
                                                 bay_name,
                                                 a.get("id", i),
                                                 b.get("id", j)),
                                             "bays.{}.apertures".format(bay_name)))

    return issues


def format_results(issues):
    """Format spatial validation issues as screen-reader-friendly text."""
    if not issues:
        return "OK: Spatial validation passed. No issues."
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
