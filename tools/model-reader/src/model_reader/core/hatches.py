"""Hatch pattern rendering for tactile floor plans.

Draws tactile fill patterns inside closed regions so different layers
or rooms are distinguishable by touch on PIAF prints. Each layer gets
a unique pattern automatically, or the user can assign patterns by name.

Available patterns:
  diagonal        — 45-degree parallel lines
  crosshatch      — 45 + 135-degree lines
  horizontal      — horizontal parallel lines
  dots            — regular dot grid
  dense_diagonal  — tighter-spaced diagonal lines
  sparse_diagonal — wider-spaced diagonal lines
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw

if TYPE_CHECKING:
    pass


# Hatch pattern definitions (spacing in pixels at 150 DPI)
HATCH_PATTERNS = {
    "diagonal": {"angles": [45], "spacing": 12, "weight": 2},
    "crosshatch": {"angles": [45, 135], "spacing": 12, "weight": 2},
    "horizontal": {"angles": [0], "spacing": 10, "weight": 2},
    "dots": {"type": "dots", "spacing": 10, "radius": 2},
    "dense_diagonal": {"angles": [45], "spacing": 8, "weight": 2},
    "sparse_diagonal": {"angles": [45], "spacing": 18, "weight": 1},
}

# Auto-assignment order: visually and tactilely distinct patterns
_AUTO_ORDER = [
    "diagonal",
    "crosshatch",
    "dots",
    "horizontal",
    "dense_diagonal",
    "sparse_diagonal",
]


def list_patterns() -> list[str]:
    """Return available hatch pattern names."""
    return list(HATCH_PATTERNS.keys())


def _draw_line_hatch(draw, polygon_pixels, angle_deg, spacing, weight, bbox):
    """Draw parallel lines at a given angle, clipped to a polygon.

    Uses a scanline approach: generate parallel lines across the bounding
    box, then for each line, find intersections with polygon edges to
    determine visible segments.
    """
    if len(polygon_pixels) < 3:
        return

    min_x, min_y, max_x, max_y = bbox
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    diag = math.sqrt((max_x - min_x) ** 2 + (max_y - min_y) ** 2)

    angle_rad = math.radians(angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)

    # Direction along the line
    dx = cos_a
    dy = sin_a
    # Normal to the line (perpendicular direction for offsetting)
    nx = -sin_a
    ny = cos_a

    # Generate parallel lines by offsetting along the normal
    half_extent = diag / 2 + spacing
    n_lines = int(half_extent * 2 / spacing) + 1

    for i in range(n_lines):
        offset = -half_extent + i * spacing
        # Line passes through (cx + offset*nx, cy + offset*ny)
        # extending in direction (dx, dy)
        lx = cx + offset * nx
        ly = cy + offset * ny
        p1 = (lx - diag * dx, ly - diag * dy)
        p2 = (lx + diag * dx, ly + diag * dy)

        # Clip to polygon using scanline intersection
        segments = _clip_line_to_polygon(p1, p2, polygon_pixels)
        for seg_start, seg_end in segments:
            draw.line([seg_start, seg_end], fill=0, width=weight)


def _clip_line_to_polygon(p1, p2, polygon):
    """Clip a line segment to the interior of a polygon.

    Returns list of (start, end) tuples for visible segments.
    Uses parametric intersection with polygon edges.
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    line_len = math.sqrt(dx * dx + dy * dy)
    if line_len < 1e-6:
        return []

    # Find all intersection parameters t where line crosses polygon edges
    t_values = []
    n = len(polygon)
    for i in range(n):
        j = (i + 1) % n
        ex = polygon[j][0] - polygon[i][0]
        ey = polygon[j][1] - polygon[i][1]

        denom = dx * ey - dy * ex
        if abs(denom) < 1e-10:
            continue

        t = ((polygon[i][0] - p1[0]) * ey - (polygon[i][1] - p1[1]) * ex) / denom
        s = ((polygon[i][0] - p1[0]) * dy - (polygon[i][1] - p1[1]) * dx) / denom

        if 0 <= s <= 1:
            t_values.append(t)

    t_values.sort()

    # Pair up intersections: odd crossings mean inside
    segments = []
    for k in range(0, len(t_values) - 1, 2):
        t_in = t_values[k]
        t_out = t_values[k + 1]
        start = (int(p1[0] + t_in * dx), int(p1[1] + t_in * dy))
        end = (int(p1[0] + t_out * dx), int(p1[1] + t_out * dy))
        segments.append((start, end))

    return segments


def _draw_dot_hatch(draw, polygon_pixels, spacing, radius, bbox):
    """Draw a regular dot grid clipped to a polygon."""
    if len(polygon_pixels) < 3:
        return

    min_x, min_y, max_x, max_y = bbox

    # Generate dots on a grid
    x = int(min_x)
    while x <= max_x:
        y = int(min_y)
        while y <= max_y:
            if _point_in_polygon(x, y, polygon_pixels):
                draw.ellipse(
                    [x - radius, y - radius, x + radius, y + radius],
                    fill=0,
                )
            y += spacing
        x += spacing


def _point_in_polygon(px, py, polygon):
    """Ray casting point-in-polygon test."""
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


def _find_closed_regions(polylines_2d):
    """Identify closed polylines (regions) from 2D projected geometry.

    A polyline is considered closed if first and last points are within
    a small tolerance of each other.
    """
    regions = []
    tolerance = 2.0  # pixels

    for poly in polylines_2d:
        if len(poly) < 3:
            continue
        # Check if closed
        dx = poly[0][0] - poly[-1][0]
        dy = poly[0][1] - poly[-1][1]
        if math.sqrt(dx * dx + dy * dy) < tolerance:
            regions.append(poly)

    return regions


def render_hatched_plan(
    polylines_2d,
    regions_with_patterns,
    img_w,
    img_h,
    scale,
    offset_x,
    offset_y,
    min_x,
    max_y,
    line_width=2,
):
    """Render a plan view with hatch patterns in closed regions.

    Args:
        polylines_2d: All geometry polylines in model coords [(x,y), ...].
        regions_with_patterns: List of (polygon_model_coords, pattern_name) tuples.
        img_w, img_h: Canvas size in pixels.
        scale, offset_x, offset_y: Transform parameters.
        min_x, max_y: Model coordinate bounds for transform.
        line_width: Stroke width for outlines.

    Returns:
        PIL Image in mode '1' (1-bit B&W).
    """
    img = Image.new("L", (img_w, img_h), 255)
    draw = ImageDraw.Draw(img)

    def to_px(x, y):
        px = int((x - min_x) * scale + offset_x)
        py = int((max_y - y) * scale + offset_y)
        return (px, py)

    # Draw hatch fills first (behind outlines)
    for region_coords, pattern_name in regions_with_patterns:
        if pattern_name == "none" or pattern_name not in HATCH_PATTERNS:
            continue

        pattern = HATCH_PATTERNS[pattern_name]
        polygon_px = [to_px(x, y) for x, y in region_coords]

        if len(polygon_px) < 3:
            continue

        # Compute pixel bounding box
        xs = [p[0] for p in polygon_px]
        ys = [p[1] for p in polygon_px]
        bbox = (min(xs), min(ys), max(xs), max(ys))

        if pattern.get("type") == "dots":
            _draw_dot_hatch(draw, polygon_px, pattern["spacing"], pattern["radius"], bbox)
        else:
            for angle in pattern["angles"]:
                _draw_line_hatch(draw, polygon_px, angle, pattern["spacing"], pattern["weight"], bbox)

    # Draw all outlines on top
    for poly in polylines_2d:
        if len(poly) < 2:
            if poly:
                px, py = to_px(poly[0][0], poly[0][1])
                r = max(1, line_width)
                draw.ellipse([px - r, py - r, px + r, py + r], fill=0)
            continue
        pixel_coords = [to_px(x, y) for x, y in poly]
        draw.line(pixel_coords, fill=0, width=line_width)

    return img.convert("1")


def auto_assign_patterns(layer_names: list[str]) -> dict[str, str]:
    """Assign distinct hatch patterns to layers automatically.

    Args:
        layer_names: List of layer names to assign patterns to.

    Returns:
        Dict mapping layer name -> pattern name.
    """
    assignments = {}
    for i, name in enumerate(layer_names):
        pattern = _AUTO_ORDER[i % len(_AUTO_ORDER)]
        assignments[name] = pattern
    return assignments
