"""Boundary checks and overlap detection for TASC zones."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tasc_core.core.model import Site, Zone


def _point_in_polygon(px: float, py: float, polygon: list[tuple[float, float]]) -> bool:
    """Ray-casting point-in-polygon test."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _segments_intersect(
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    p4: tuple[float, float],
) -> bool:
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


def _on_segment(p: tuple, q: tuple, r: tuple) -> bool:
    """Check if point r lies on segment p-q (assuming collinear)."""
    return (
        min(p[0], q[0]) <= r[0] <= max(p[0], q[0])
        and min(p[1], q[1]) <= r[1] <= max(p[1], q[1])
    )


def _polygons_overlap(poly_a: list[tuple[float, float]], poly_b: list[tuple[float, float]]) -> bool:
    """Check if two convex/simple polygons overlap (vertex-in-polygon or edge intersection)."""
    # Check if any vertex of A is inside B
    for p in poly_a:
        if _point_in_polygon(p[0], p[1], poly_b):
            return True
    # Check if any vertex of B is inside A
    for p in poly_b:
        if _point_in_polygon(p[0], p[1], poly_a):
            return True
    # Check edge intersections
    na = len(poly_a)
    nb = len(poly_b)
    for i in range(na):
        for j in range(nb):
            if _segments_intersect(
                poly_a[i], poly_a[(i + 1) % na], poly_b[j], poly_b[(j + 1) % nb]
            ):
                return True
    return False


def _estimate_overlap_area(zone_a: "Zone", zone_b: "Zone") -> float:
    """Estimate overlap area between two axis-aligned rectangles.

    For non-axis-aligned polygons, returns a rough estimate.
    """
    a_min_x, a_min_y, a_max_x, a_max_y = zone_a.bounds
    b_min_x, b_min_y, b_max_x, b_max_y = zone_b.bounds

    overlap_x = max(0, min(a_max_x, b_max_x) - max(a_min_x, b_min_x))
    overlap_y = max(0, min(a_max_y, b_max_y) - max(a_min_y, b_min_y))
    return overlap_x * overlap_y


def check_zone_in_boundary(zone: "Zone", site: "Site") -> list[str]:
    """Check if zone fits within site boundary. Returns warnings."""
    warnings = []
    site_min_x, site_min_y, site_max_x, site_max_y = site.bounds

    for cx, cy in zone.corners:
        if not _point_in_polygon(cx, cy, site.corners):
            # Determine which direction(s) it extends past
            if cx < site_min_x:
                warnings.append(
                    f"Zone {zone.name} extends {site_min_x - cx:.1f} {site.units} past west boundary"
                )
            if cx > site_max_x:
                warnings.append(
                    f"Zone {zone.name} extends {cx - site_max_x:.1f} {site.units} past east boundary"
                )
            if cy < site_min_y:
                warnings.append(
                    f"Zone {zone.name} extends {site_min_y - cy:.1f} {site.units} past south boundary"
                )
            if cy > site_max_y:
                warnings.append(
                    f"Zone {zone.name} extends {cy - site_max_y:.1f} {site.units} past north boundary"
                )

    # Deduplicate
    return list(dict.fromkeys(warnings))


def check_zone_overlaps(new_zone: "Zone", existing_zones: list["Zone"]) -> list[str]:
    """Check if new zone overlaps with any existing zones."""
    warnings = []
    for existing in existing_zones:
        if _polygons_overlap(new_zone.corners, existing.corners):
            overlap = _estimate_overlap_area(new_zone, existing)
            if overlap > 0:
                warnings.append(
                    f"Zone {new_zone.name} overlaps with zone {existing.name} by approximately {overlap:.0f} square units"
                )
            else:
                warnings.append(
                    f"Zone {new_zone.name} overlaps with zone {existing.name}"
                )
    return warnings


def validate_site(site: "Site") -> list[str]:
    """Validate site polygon."""
    warnings = []
    if len(site.corners) < 3:
        warnings.append("Site must have at least 3 corners")
    if site.area == 0:
        warnings.append("Site has zero area (degenerate polygon)")
    if site.width == 0 or site.depth == 0:
        warnings.append("Site has zero width or depth")
    return warnings
