"""compile_scene(state) -> ScenePlan: the single source of geometry truth.

A ScenePlan is {layer_name: [primitive, ...]} with layers and primitives
emitted in deterministic order, so the same state always produces an
identical plan — and therefore identical geometry in Rhino and in .3dm
export. Presentation defaults live in STYLE; geometry-affecting values
never do.
"""

import math

from jig.geometry import bays as bay_math
from jig.geometry import corridors as corridor_math
from jig.geometry import walls as wall_math
from jig.geometry.primitives import Arc, Circle, Polyline, TextLabel

LAYER_SITE = "JIG::Site"
LAYER_ZONES = "JIG::Zones"
LAYER_GRID = "JIG::Grid"
LAYER_GRIDLINES = "JIG::Gridlines"
LAYER_COLUMNS = "JIG::Columns"
LAYER_WALLS = "JIG::Walls"
LAYER_APERTURES = "JIG::Apertures"
LAYER_CORRIDORS = "JIG::Corridors"
LAYER_VOIDS = "JIG::Voids"
LAYER_LABELS = "JIG::Labels"

ALL_LAYERS = (LAYER_SITE, LAYER_ZONES, LAYER_GRID, LAYER_GRIDLINES,
              LAYER_COLUMNS, LAYER_WALLS, LAYER_APERTURES, LAYER_CORRIDORS,
              LAYER_VOIDS, LAYER_LABELS)

STYLE = {
    "column_radius": 0.75,
    "label_height": 3.0,
    "cell_label_height": 2.0,
    "wall_weight_mm": 0.5,
    "site_weight_mm": 0.7,
    "corridor_dash": 3.0,
    "corridor_gap": 2.0,
    "label_bays": True,
    "label_cells": True,
}


def compile_scene(state, style=None):
    s = dict(STYLE)
    if style:
        s.update(style)
    plan = {layer: [] for layer in ALL_LAYERS}

    if state.site.boundary:
        plan[LAYER_SITE].append(Polyline(state.site.boundary, closed=True,
                                         weight_mm=s["site_weight_mm"]))

    for zone in state.zones:
        plan[LAYER_ZONES].append(Polyline(zone.boundary, closed=True))
        plan[LAYER_LABELS].append(TextLabel(zone.label, _centroid(zone.boundary),
                                            s["label_height"]))

    if state.grid.enabled and state.site.boundary:
        plan[LAYER_GRID].extend(_global_grid(state.grid, state.site))

    for bay in state.bays:
        _compile_bay(plan, bay, s)

    return plan


def _compile_bay(plan, bay, s):
    for _axis, _line, start, end in bay_math.gridlines(bay):
        plan[LAYER_GRIDLINES].append(Polyline((start, end)))

    for point in bay_math.column_points(bay):
        plan[LAYER_COLUMNS].append(Circle(point, s["column_radius"]))

    for start, end in wall_math.wall_segments(bay):
        plan[LAYER_WALLS].append(Polyline((start, end), weight_mm=s["wall_weight_mm"]))

    for kind, payload in wall_math.aperture_symbols(bay):
        if kind == "line":
            plan[LAYER_APERTURES].append(Polyline(payload))
        else:
            center, radius, start_deg, end_deg = payload
            plan[LAYER_APERTURES].append(Arc(center, radius, start_deg, end_deg))

    edges, dashes = corridor_math.corridor_primitives(
        bay, s["corridor_dash"], s["corridor_gap"])
    for start, end in edges + dashes:
        plan[LAYER_CORRIDORS].append(Polyline((start, end)))

    for void in bay.voids:
        plan[LAYER_VOIDS].append(_void_primitive(bay, void))

    if s["label_bays"]:
        plan[LAYER_LABELS].append(TextLabel(bay.name.upper(),
                                            bay_math.bay_center(bay),
                                            s["label_height"]))
    if s["label_cells"]:
        for cell in bay.cells:
            plan[LAYER_LABELS].append(TextLabel(cell.label,
                                                bay_math.cell_center(bay, *cell.at),
                                                s["cell_label_height"]))


def _void_primitive(bay, void):
    cx, cy = void.center
    if void.shape == "circle":
        return Circle(bay_math.to_world(bay, cx, cy), void.size[0] / 2.0)
    w, d = void.size
    corners = [
        bay_math.to_world(bay, cx - w / 2.0, cy - d / 2.0),
        bay_math.to_world(bay, cx + w / 2.0, cy - d / 2.0),
        bay_math.to_world(bay, cx + w / 2.0, cy + d / 2.0),
        bay_math.to_world(bay, cx - w / 2.0, cy + d / 2.0),
    ]
    return Polyline(corners, closed=True)


def _centroid(polygon):
    n = float(len(polygon))
    return (sum(p[0] for p in polygon) / n, sum(p[1] for p in polygon) / n)


def _global_grid(grid, site):
    """Structural grid lines clipped to the site bounding box."""
    xs = [p[0] for p in site.boundary]
    ys = [p[1] for p in site.boundary]
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
    span = math.hypot(max_x - min_x, max_y - min_y)
    rad = math.radians(grid.rotation_deg)
    cos_r, sin_r = math.cos(rad), math.sin(rad)
    ox, oy = grid.origin
    out = []

    pad = max(grid.spacing)

    def rotated_line(along_u, along_v, offset):
        # line through origin + offset*v, running along u, length 2*span
        px, py = ox + offset * along_v[0], oy + offset * along_v[1]
        if not (min_x - pad <= px <= max_x + pad and min_y - pad <= py <= max_y + pad):
            return None
        a = (px - along_u[0] * span, py - along_u[1] * span)
        b = (px + along_u[0] * span, py + along_u[1] * span)
        return Polyline((a, b))

    u_x, v_x = (cos_r, sin_r), (-sin_r, cos_r)
    count_v = int(span / grid.spacing[1]) + 1
    for k in range(-count_v, count_v + 1):
        line = rotated_line(u_x, v_x, k * grid.spacing[1])
        if line:
            out.append(line)
    count_u = int(span / grid.spacing[0]) + 1
    for k in range(-count_u, count_u + 1):
        line = rotated_line(v_x, u_x, k * grid.spacing[0])
        if line:
            out.append(line)
    return out
