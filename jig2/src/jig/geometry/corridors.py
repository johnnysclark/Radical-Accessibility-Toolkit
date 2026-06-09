"""Corridor math: the band a corridor occupies and its drawn linework."""

from jig.geometry.bays import line_positions, to_world


def corridor_band(bay):
    """The corridor's occupied interval on its perpendicular axis, in bay-local
    coordinates: (axis, lo, hi). None when the bay has no corridor."""
    c = bay.corridor
    if not c:
        return None
    perpendicular = line_positions(bay.spacing_y if c.axis == "x" else bay.spacing_x)
    center = perpendicular[c.line]
    return (c.axis, center - c.width / 2.0, center + c.width / 2.0)


def corridor_primitives(bay, dash_len=3.0, gap_len=2.0):
    """Edge lines plus a dashed centerline, as world-coordinate point pairs.

    Returns (edges, dashes): lists of (start, end) world tuples.
    """
    band = corridor_band(bay)
    if not band:
        return [], []
    axis, lo, hi = band
    run = bay.width if axis == "x" else bay.depth
    center = (lo + hi) / 2.0

    def pt(along, across):
        if axis == "x":
            return to_world(bay, along, across)
        return to_world(bay, across, along)

    edges = [
        (pt(0.0, lo), pt(run, lo)),
        (pt(0.0, hi), pt(run, hi)),
    ]
    dashes = []
    pos = 0.0
    while pos < run:
        end = min(pos + dash_len, run)
        dashes.append((pt(pos, center), pt(end, center)))
        pos = end + gap_len
    return edges, dashes
