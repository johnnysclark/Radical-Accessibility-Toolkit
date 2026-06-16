"""Boundary checks and overlap detection for controller zones.

Dict-based port of tools/tasc/src/tasc/core/validation.py. Operates directly
on the controller's state.json schema: sites and zones are plain dicts.

State schema (relevant subset):
    state["site"]   = {"origin": [x, y], "width": w, "height": h,
                       "corners": [[x, y], ...]}
    state["zones"]  = {name: {"corners": [[x, y], ...], ...}, ...}

Bounds tuple order used internally: (min_x, min_y, max_x, max_y) -- matches
TASC convention, NOT the controller's _zone_bounds() helper.

Stdlib only. Python 3.10+.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Geometry primitives (ported verbatim from TASC validation.py)
# ---------------------------------------------------------------------------


def _point_in_polygon(px: float, py: float, polygon: list) -> bool:
    """Ray-casting point-in-polygon test."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i][0], polygon[i][1]
        xj, yj = polygon[j][0], polygon[j][1]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _on_segment(p, q, r) -> bool:
    """Check if point r lies on segment p-q (assuming collinear)."""
    return (
        min(p[0], q[0]) <= r[0] <= max(p[0], q[0])
        and min(p[1], q[1]) <= r[1] <= max(p[1], q[1])
    )


def _segments_intersect(p1, p2, p3, p4) -> bool:
    """Check if line segment p1-p2 intersects p3-p4."""

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    d1 = cross(p3, p4, p1)
    d2 = cross(p3, p4, p2)
    d3 = cross(p1, p2, p3)
    d4 = cross(p1, p2, p4)

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and (
        (d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)
    ):
        return True

    # Collinear cases
    if d1 == 0 and _on_segment(p3, p4, p1):
        return True
    if d2 == 0 and _on_segment(p3, p4, p2):
        return True
    if d3 == 0 and _on_segment(p1, p2, p3):
        return True
    if d4 == 0 and _on_segment(p1, p2, p4):
        return True
    return False


def _polygons_overlap(poly_a: list, poly_b: list) -> bool:
    """Check if two simple polygons overlap (vertex-in-polygon or edge intersect)."""
    for p in poly_a:
        if _point_in_polygon(p[0], p[1], poly_b):
            return True
    for p in poly_b:
        if _point_in_polygon(p[0], p[1], poly_a):
            return True
    na = len(poly_a)
    nb = len(poly_b)
    for i in range(na):
        for j in range(nb):
            if _segments_intersect(
                poly_a[i], poly_a[(i + 1) % na], poly_b[j], poly_b[(j + 1) % nb]
            ):
                return True
    return False


# ---------------------------------------------------------------------------
# Dict-shape helpers
# ---------------------------------------------------------------------------


def _site_corners(site_dict: dict) -> list:
    """Return site corners. Synthesize from origin+width+height if absent."""
    corners = site_dict.get("corners")
    if corners:
        return corners
    origin = site_dict.get("origin", [0.0, 0.0])
    w = site_dict.get("width", 0.0)
    h = site_dict.get("height", 0.0)
    ox, oy = origin[0], origin[1]
    return [
        [ox, oy],
        [ox + w, oy],
        [ox + w, oy + h],
        [ox, oy + h],
    ]


def _bounds(corners: list) -> tuple:
    """Return (min_x, min_y, max_x, max_y) for a list of [x, y] points."""
    xs = [c[0] for c in corners]
    ys = [c[1] for c in corners]
    return (min(xs), min(ys), max(xs), max(ys))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def check_zone_in_boundary_dict(
    zone_name: str,
    zone_dict: dict,
    site_dict: dict,
    units: str = "feet",
) -> list:
    """Return list of warning strings if zone extends past site boundary."""
    warnings: list = []
    zone_corners = zone_dict.get("corners", [])
    if not zone_corners:
        return warnings

    site_corners = _site_corners(site_dict)
    if len(site_corners) < 3:
        return warnings

    site_min_x, site_min_y, site_max_x, site_max_y = _bounds(site_corners)

    for c in zone_corners:
        cx, cy = c[0], c[1]
        if not _point_in_polygon(cx, cy, site_corners):
            if cx < site_min_x:
                warnings.append(
                    f"Zone {zone_name} extends {site_min_x - cx:.1f} {units} past west boundary"
                )
            if cx > site_max_x:
                warnings.append(
                    f"Zone {zone_name} extends {cx - site_max_x:.1f} {units} past east boundary"
                )
            if cy < site_min_y:
                warnings.append(
                    f"Zone {zone_name} extends {site_min_y - cy:.1f} {units} past south boundary"
                )
            if cy > site_max_y:
                warnings.append(
                    f"Zone {zone_name} extends {cy - site_max_y:.1f} {units} past north boundary"
                )

    return list(dict.fromkeys(warnings))


def check_zone_overlaps_dict(
    new_zone_name: str,
    new_zone_dict: dict,
    all_zones_dict: dict,
    units: str = "feet",
) -> list:
    """Return overlap warnings between new_zone and any OTHER existing zone."""
    warnings: list = []
    new_corners = new_zone_dict.get("corners", [])
    if not new_corners:
        return warnings

    a_min_x, a_min_y, a_max_x, a_max_y = _bounds(new_corners)

    for other_name, other_dict in all_zones_dict.items():
        if other_name == new_zone_name:
            continue
        other_corners = other_dict.get("corners", [])
        if not other_corners:
            continue
        if not _polygons_overlap(new_corners, other_corners):
            continue

        b_min_x, b_min_y, b_max_x, b_max_y = _bounds(other_corners)
        overlap_x = max(0.0, min(a_max_x, b_max_x) - max(a_min_x, b_min_x))
        overlap_y = max(0.0, min(a_max_y, b_max_y) - max(a_min_y, b_min_y))
        overlap = overlap_x * overlap_y

        if overlap > 0:
            warnings.append(
                f"Zone {new_zone_name} overlaps with zone {other_name} "
                f"by approximately {overlap:.0f} square {units}"
            )
        else:
            warnings.append(
                f"Zone {new_zone_name} overlaps with zone {other_name}"
            )
    return warnings


def validate_site_dict(site_dict: dict) -> list:
    """Return warnings for degenerate site geometry."""
    warnings: list = []
    corners = _site_corners(site_dict)
    if len(corners) < 3:
        warnings.append("Site must have at least 3 corners")

    width = site_dict.get("width")
    height = site_dict.get("height")
    if width == 0 or height == 0:
        warnings.append("Site has zero width or height")

    # Degenerate area: shoelace formula on corners.
    if len(corners) >= 3:
        area = 0.0
        n = len(corners)
        for i in range(n):
            x1, y1 = corners[i][0], corners[i][1]
            x2, y2 = corners[(i + 1) % n][0], corners[(i + 1) % n][1]
            area += x1 * y2 - x2 * y1
        if abs(area) / 2.0 == 0:
            warnings.append("Site has zero area (degenerate polygon)")

    return warnings


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # 1. Zone fully inside site -> 0 boundary warnings.
    site = {"origin": [0, 0], "width": 100, "height": 100}
    inside_zone = {"corners": [[10, 10], [30, 10], [30, 30], [10, 30]]}
    w1 = check_zone_in_boundary_dict("A", inside_zone, site)
    assert w1 == [], f"expected no warnings, got {w1}"

    # 2. Zone half-outside site -> at least 1 boundary warning.
    half_out_zone = {"corners": [[90, 10], [120, 10], [120, 30], [90, 30]]}
    w2 = check_zone_in_boundary_dict("B", half_out_zone, site)
    assert len(w2) >= 1, f"expected >=1 warning, got {w2}"
    assert any("east" in w for w in w2), f"expected east warning, got {w2}"

    # 3. Two overlapping zones -> 1 overlap warning.
    zones = {
        "A": {"corners": [[0, 0], [20, 0], [20, 20], [0, 20]]},
        "B": {"corners": [[10, 10], [30, 10], [30, 30], [10, 30]]},
    }
    w3 = check_zone_overlaps_dict("A", zones["A"], zones)
    assert len(w3) == 1, f"expected exactly 1 overlap warning, got {w3}"
    assert "B" in w3[0], f"expected mention of zone B, got {w3}"

    # Bonus: self-exclusion -- zone vs. itself in dict should not warn.
    w4 = check_zone_overlaps_dict("A", zones["A"], {"A": zones["A"]})
    assert w4 == [], f"expected no self-overlap, got {w4}"

    # Bonus: validate_site_dict on a healthy site.
    assert validate_site_dict(site) == []
    assert "zero width or height" in " ".join(
        validate_site_dict({"origin": [0, 0], "width": 0, "height": 10})
    )

    print("OK: validation self-tests passed")
