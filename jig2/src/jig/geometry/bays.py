"""Bay grid math: gridline positions, column points, cell rectangles.

Local bay coordinates put the bay's first gridline intersection at (0, 0);
``to_world`` applies the bay's rotation about its origin, then translation.
"""

import math


def line_positions(spacings):
    """Cumulative gridline positions for a spacing list: n intervals -> n+1 positions."""
    positions = [0.0]
    for s in spacings:
        positions.append(positions[-1] + float(s))
    return positions


def to_world(bay, x, y):
    """Bay-local (x, y) -> world: rotate about local origin, translate to bay origin."""
    rad = math.radians(bay.rotation_deg)
    cos_r, sin_r = math.cos(rad), math.sin(rad)
    wx = bay.origin[0] + x * cos_r - y * sin_r
    wy = bay.origin[1] + x * sin_r + y * cos_r
    return (wx, wy)


def column_points(bay):
    """World coordinates of every gridline intersection, sorted by (j, i)."""
    xs = line_positions(bay.spacing_x)
    ys = line_positions(bay.spacing_y)
    return [to_world(bay, x, y) for y in ys for x in xs]


def gridlines(bay):
    """All gridline runs as (axis, line_index, start_world, end_world).

    axis "x" lines run along x at each y position (ny+1 of them);
    axis "y" lines run along y at each x position (nx+1 of them).
    """
    xs = line_positions(bay.spacing_x)
    ys = line_positions(bay.spacing_y)
    runs = []
    for j, y in enumerate(ys):
        runs.append(("x", j, to_world(bay, 0.0, y), to_world(bay, xs[-1], y)))
    for i, x in enumerate(xs):
        runs.append(("y", i, to_world(bay, x, 0.0), to_world(bay, x, ys[-1])))
    return runs


def cell_rect(bay, i, j):
    """World corners of cell (i, j), counter-clockwise from its low corner."""
    xs = line_positions(bay.spacing_x)
    ys = line_positions(bay.spacing_y)
    return [
        to_world(bay, xs[i], ys[j]),
        to_world(bay, xs[i + 1], ys[j]),
        to_world(bay, xs[i + 1], ys[j + 1]),
        to_world(bay, xs[i], ys[j + 1]),
    ]


def cell_center(bay, i, j):
    xs = line_positions(bay.spacing_x)
    ys = line_positions(bay.spacing_y)
    return to_world(bay, (xs[i] + xs[i + 1]) / 2.0, (ys[j] + ys[j + 1]) / 2.0)


def bay_corners(bay):
    """World corners of the bay's overall rectangle."""
    return [
        to_world(bay, 0.0, 0.0),
        to_world(bay, bay.width, 0.0),
        to_world(bay, bay.width, bay.depth),
        to_world(bay, 0.0, bay.depth),
    ]


def bay_center(bay):
    return to_world(bay, bay.width / 2.0, bay.depth / 2.0)
