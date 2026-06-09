"""Wall math: gridline wall runs minus aperture and corridor gaps,
plus aperture symbol linework (door swings, window glass, portal jambs).

Wall runs follow every gridline of a walled bay. Gaps come from two
sources: apertures placed on that (axis, line), and the corridor band
crossing perpendicular walls. The wall run that coincides with the
corridor's own line is removed entirely (the corridor replaces it).
"""

import math

from jig.geometry.bays import line_positions, to_world
from jig.geometry.corridors import corridor_band

EPSILON = 1e-6
PORTAL_TICK = 1.0  # length of portal jamb ticks, model units


def subtract_intervals(length, gaps):
    """Remove [a, b] gaps from the interval [0, length]; returns kept segments."""
    gaps = sorted((max(0.0, a), min(length, b)) for a, b in gaps if b > 0 and a < length)
    segments = []
    cursor = 0.0
    for a, b in gaps:
        if a > cursor + EPSILON:
            segments.append((cursor, a))
        cursor = max(cursor, b)
    if cursor < length - EPSILON:
        segments.append((cursor, length))
    return segments


def _runs(bay):
    """Every wall run: (axis, line_index, perpendicular_position, run_length)."""
    xs = line_positions(bay.spacing_x)
    ys = line_positions(bay.spacing_y)
    runs = []
    for j, y in enumerate(ys):
        runs.append(("x", j, y, xs[-1]))
    for i, x in enumerate(xs):
        runs.append(("y", i, x, ys[-1]))
    return runs


def _local(axis, along, across):
    return (along, across) if axis == "x" else (across, along)


def wall_segments(bay):
    """Wall linework as world (start, end) pairs, gaps already subtracted."""
    if not bay.walls.enabled:
        return []
    band = corridor_band(bay)
    segments = []
    for axis, line, across, length in _runs(bay):
        if band and band[0] == axis and band[1] - EPSILON < across < band[2] + EPSILON:
            continue  # this run lies inside the corridor band; corridor replaces it
        gaps = [(ap.offset, ap.offset + ap.width)
                for ap in bay.apertures if ap.axis == axis and ap.line == line]
        if band and band[0] != axis:
            gaps.append((band[1], band[2]))  # corridor crosses this perpendicular wall
        for a, b in subtract_intervals(length, gaps):
            p0 = _local(axis, a, across)
            p1 = _local(axis, b, across)
            segments.append((to_world(bay, *p0), to_world(bay, *p1)))
    return segments


def aperture_symbols(bay):
    """Symbol linework per aperture, in world coordinates.

    Returns a list of (kind, payload) entries:
    - ("line", (start, end)) for door leaves, window glass, portal ticks
    - ("arc", (center, radius, start_deg, end_deg)) for door swings
    """
    xs = line_positions(bay.spacing_x)
    ys = line_positions(bay.spacing_y)
    out = []
    for ap in bay.apertures:
        across = (ys if ap.axis == "x" else xs)[ap.line]
        if ap.kind == "door":
            out += _door(bay, ap, across)
        elif ap.kind == "window":
            start = _local(ap.axis, ap.offset, across)
            end = _local(ap.axis, ap.offset + ap.width, across)
            out.append(("line", (to_world(bay, *start), to_world(bay, *end))))
        elif ap.kind == "portal":
            for along in (ap.offset, ap.offset + ap.width):
                lo = _local(ap.axis, along, across - PORTAL_TICK / 2.0)
                hi = _local(ap.axis, along, across + PORTAL_TICK / 2.0)
                out.append(("line", (to_world(bay, *lo), to_world(bay, *hi))))
    return out


def _door(bay, ap, across):
    """Door leaf line + quarter-circle swing arc."""
    hinge_along = ap.offset if ap.hinge == "start" else ap.offset + ap.width
    latch_along = ap.offset + ap.width if ap.hinge == "start" else ap.offset
    swing_sign = 1.0 if ap.swing == "in" else -1.0

    hinge = _local(ap.axis, hinge_along, across)
    leaf_end = _local(ap.axis, hinge_along, across + swing_sign * ap.width)
    latch = _local(ap.axis, latch_along, across)

    leaf_angle = _angle(hinge, leaf_end)
    latch_angle = _angle(hinge, latch)
    sweep = (leaf_angle - latch_angle) % 360.0
    if sweep <= 180.0:
        start_deg, end_deg = latch_angle, leaf_angle
    else:
        start_deg, end_deg = leaf_angle, latch_angle

    world_hinge = to_world(bay, *hinge)
    world_leaf = to_world(bay, *leaf_end)
    return [
        ("line", (world_hinge, world_leaf)),
        ("arc", (world_hinge, ap.width,
                 start_deg + bay.rotation_deg, end_deg + bay.rotation_deg)),
    ]


def _angle(origin, target):
    return math.degrees(math.atan2(target[1] - origin[1], target[0] - origin[0])) % 360.0
