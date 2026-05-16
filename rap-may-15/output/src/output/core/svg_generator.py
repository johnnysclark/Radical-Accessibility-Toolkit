"""SVG generator for controller state.json plan views.

Stdlib-only renderer that produces a 2D vector SVG plan view from a
Radical Accessibility Toolkit controller state dict. No external
dependencies (no Pillow, no svgwrite) -- plain string-building.

Public API:
    export_svg(state, output_path, stroke_width=0.5) -> str
"""

import json
import sys


def _escape_xml(text):
    """Escape XML special characters in label text."""
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _site_corners(state):
    """Return list of (x, y) site corners. Synthesize from origin+width+height if missing."""
    site = state.get("site", {}) or {}
    corners = site.get("corners")
    if corners:
        return [(float(c[0]), float(c[1])) for c in corners]
    ox, oy = 0.0, 0.0
    origin = site.get("origin")
    if origin:
        ox, oy = float(origin[0]), float(origin[1])
    w = float(site.get("width", 0.0))
    h = float(site.get("height", 0.0))
    # CCW from origin
    return [(ox, oy), (ox + w, oy), (ox + w, oy + h), (ox, oy + h)]


def _bounds(corners):
    """Return (min_x, min_y, width, height) for a list of points."""
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    min_x = min(xs)
    min_y = min(ys)
    max_x = max(xs)
    max_y = max(ys)
    return min_x, min_y, max_x - min_x, max_y - min_y


def _centroid(points):
    """Average a list of (x, y) tuples."""
    if not points:
        return (0.0, 0.0)
    sx = sum(p[0] for p in points)
    sy = sum(p[1] for p in points)
    n = float(len(points))
    return (sx / n, sy / n)


def _zone_corners(zone):
    """Return zone corner list. Supports explicit corners or origin+width+height."""
    corners = zone.get("corners")
    if corners:
        return [(float(c[0]), float(c[1])) for c in corners]
    origin = zone.get("origin") or [zone.get("x", 0.0), zone.get("y", 0.0)]
    ox, oy = float(origin[0]), float(origin[1])
    w = float(zone.get("width", 0.0))
    h = float(zone.get("height", 0.0))
    return [(ox, oy), (ox + w, oy), (ox + w, oy + h), (ox, oy + h)]


def _bay_grid_points(bay):
    """Compute column grid intersection points for a bay.

    Uses spacing arrays if provided, else uniform spacing * count.
    """
    origin = bay.get("origin") or [bay.get("x", 0.0), bay.get("y", 0.0)]
    ox, oy = float(origin[0]), float(origin[1])

    # Spacing arrays preferred (variable bay sizes)
    sx_arr = bay.get("spacing_x") or bay.get("x_spacings")
    sy_arr = bay.get("spacing_y") or bay.get("y_spacings")

    if sx_arr is None:
        nx = int(bay.get("nx") or bay.get("count_x") or bay.get("bays_x") or 1)
        spacing = bay.get("spacing")
        if isinstance(spacing, (list, tuple)) and len(spacing) >= 1:
            sx = float(spacing[0])
        else:
            sx = float(spacing if spacing is not None else bay.get("spacing_x_uniform", 1.0))
        sx_arr = [sx] * nx
    if sy_arr is None:
        ny = int(bay.get("ny") or bay.get("count_y") or bay.get("bays_y") or 1)
        spacing = bay.get("spacing")
        if isinstance(spacing, (list, tuple)) and len(spacing) >= 2:
            sy = float(spacing[1])
        else:
            sy = float(spacing if spacing is not None else bay.get("spacing_y_uniform", 1.0))
        sy_arr = [sy] * ny

    # Build cumulative coordinates: (nx+1) x (ny+1) intersections
    xs = [ox]
    for s in sx_arr:
        xs.append(xs[-1] + float(s))
    ys = [oy]
    for s in sy_arr:
        ys.append(ys[-1] + float(s))

    points = []
    for y in ys:
        for x in xs:
            points.append((x, y))
    return points


def export_svg(state, output_path, stroke_width=0.5):
    """Render state.json plan view as a 2D vector SVG. Returns output_path."""
    corners = _site_corners(state)
    min_x, min_y, width, height = _bounds(corners)
    if width <= 0:
        width = 1.0
    if height <= 0:
        height = 1.0

    parts = []
    parts.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'viewBox="{0} {1} {2} {3}" '
        'width="{2}" height="{3}">'.format(min_x, min_y, width, height)
    )
    parts.append(
        '<style>'
        '.zone { fill: #eee; stroke: #888; stroke-dasharray: 2,2; }'
        '.wall { stroke: #000; }'
        '.label { font-family: sans-serif; font-size: 4px; fill: #222; }'
        '</style>'
    )
    # Flip y so positive y points up like in plan drawings.
    parts.append(
        '<g transform="translate(0, {0}) scale(1, -1)">'.format(2 * min_y + height)
    )

    # 1. Site polygon
    site_pts = " ".join("{0},{1}".format(p[0], p[1]) for p in corners)
    parts.append(
        '<polygon points="{0}" fill="#fff" stroke="#000" stroke-width="1.0"/>'.format(site_pts)
    )

    # 2. Zones (with label at centroid)
    for zone in (state.get("zones") or []):
        zc = _zone_corners(zone)
        if not zc:
            continue
        pts = " ".join("{0},{1}".format(p[0], p[1]) for p in zc)
        parts.append('<polygon class="zone" points="{0}"/>'.format(pts))
        cx, cy = _centroid(zc)
        label = zone.get("label") or zone.get("name") or zone.get("id") or ""
        # Counter-flip the text so it's readable despite the group transform.
        parts.append(
            '<text class="label" x="{0}" y="{1}" '
            'text-anchor="middle" transform="translate(0, {1}) scale(1, -1) translate(0, -{1})">'
            '{2}</text>'.format(cx, cy, _escape_xml(label))
        )

    # 3. Bays - column dots at every grid intersection
    for bay in (state.get("bays") or []):
        for (px, py) in _bay_grid_points(bay):
            parts.append(
                '<circle cx="{0}" cy="{1}" r="0.4" fill="#000"/>'.format(px, py)
            )

    # 4. Walls - line segments
    for wall in (state.get("walls") or []):
        # Support several shapes: {start:[x,y], end:[x,y]} or {x1,y1,x2,y2} or {a:[x,y], b:[x,y]}
        s = wall.get("start") or wall.get("a") or wall.get("p1")
        e = wall.get("end") or wall.get("b") or wall.get("p2")
        if s is None or e is None:
            if all(k in wall for k in ("x1", "y1", "x2", "y2")):
                s = [wall["x1"], wall["y1"]]
                e = [wall["x2"], wall["y2"]]
            else:
                continue
        parts.append(
            '<line class="wall" x1="{0}" y1="{1}" x2="{2}" y2="{3}" '
            'stroke="#000" stroke-width="{4}px"/>'.format(
                float(s[0]), float(s[1]), float(e[0]), float(e[1]), stroke_width
            )
        )

    # 5. Apertures (v1: render as thin rect overlays if dims present, else skip)
    for ap in (state.get("apertures") or []):
        origin = ap.get("origin") or ap.get("position")
        w = ap.get("width")
        h = ap.get("height")
        if origin is None or w is None or h is None:
            continue
        parts.append(
            '<rect x="{0}" y="{1}" width="{2}" height="{3}" '
            'fill="#fff" stroke="#444" stroke-width="0.2"/>'.format(
                float(origin[0]), float(origin[1]), float(w), float(h)
            )
        )

    parts.append('</g>')
    parts.append('</svg>')

    svg_text = "\n".join(parts) + "\n"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_text)
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 svg_generator.py <state.json> <out.svg>")
        sys.exit(1)
    state_path = sys.argv[1]
    out_path = sys.argv[2]
    with open(state_path, "r", encoding="utf-8") as f:
        state_data = json.load(f)
    export_svg(state_data, out_path)
    print("OK: SVG written to {0}".format(out_path))
