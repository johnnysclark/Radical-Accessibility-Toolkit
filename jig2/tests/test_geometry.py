import math

from jig.geometry.bays import (bay_corners, cell_center, column_points,
                               gridlines, line_positions, to_world)
from jig.geometry.compile import (LAYER_APERTURES, LAYER_COLUMNS,
                                  LAYER_CORRIDORS, LAYER_GRIDLINES,
                                  LAYER_SITE, LAYER_WALLS, compile_scene)
from jig.geometry.corridors import corridor_band, corridor_primitives
from jig.geometry.primitives import Arc, arc_three_points, plan_bbox, plan_counts
from jig.geometry.walls import (aperture_symbols, subtract_intervals,
                                wall_segments)
from jig.model.schema import Aperture, Bay, Corridor, State, Walls


def make_bay(**overrides):
    fields = dict(id="b01", name="a", origin=[10.0, 20.0], rotation_deg=0.0,
                  counts=[2, 2], spacing_x=[10.0, 10.0], spacing_y=[10.0, 10.0])
    fields.update(overrides)
    return Bay(**fields)


def test_line_positions():
    assert line_positions([24, 30, 24]) == [0.0, 24.0, 54.0, 78.0]


def test_column_points_count_and_corners():
    bay = make_bay()
    points = column_points(bay)
    assert len(points) == 9  # (2+1) * (2+1)
    assert points[0] == (10.0, 20.0)
    assert points[-1] == (30.0, 40.0)


def test_rotation_90_degrees():
    bay = make_bay(rotation_deg=90.0)
    x, y = to_world(bay, 10.0, 0.0)
    assert math.isclose(x, 10.0, abs_tol=1e-9)
    assert math.isclose(y, 30.0, abs_tol=1e-9)


def test_gridline_count():
    bay = make_bay()
    runs = gridlines(bay)
    assert len(runs) == 6  # 3 x-lines + 3 y-lines


def test_subtract_intervals():
    assert subtract_intervals(20.0, []) == [(0.0, 20.0)]
    assert subtract_intervals(20.0, [(5.0, 8.0)]) == [(0.0, 5.0), (8.0, 20.0)]
    assert subtract_intervals(20.0, [(0.0, 5.0), (15.0, 20.0)]) == [(5.0, 15.0)]
    assert subtract_intervals(20.0, [(-5.0, 25.0)]) == []


def test_wall_segments_door_gap():
    door = Aperture(id="ap01", kind="door", axis="x", line=0,
                    offset=4.0, width=3.0)
    bay = make_bay(walls=Walls(enabled=True), apertures=[door])
    segments = wall_segments(bay)
    # south wall (y local 0 -> world y 20) is split into two pieces
    south = [s for s in segments
             if abs(s[0][1] - 20.0) < 1e-9 and abs(s[1][1] - 20.0) < 1e-9]
    assert len(south) == 2
    lengths = sorted(abs(s[1][0] - s[0][0]) for s in south)
    assert lengths == [4.0, 13.0]


def test_walls_off_no_segments():
    assert wall_segments(make_bay()) == []


def test_corridor_band_and_carving():
    corridor = Corridor(axis="x", line=1, width=4.0)
    bay = make_bay(walls=Walls(enabled=True), corridor=corridor)
    band = corridor_band(bay)
    assert band == ("x", 8.0, 12.0)
    segments = wall_segments(bay)
    # the wall along the corridor's own line (local y 10) is gone
    assert not any(abs(s[0][1] - 30.0) < 1e-9 and abs(s[1][1] - 30.0) < 1e-9
                   for s in segments)
    # perpendicular walls have a 4-unit gap: each y-run splits into 8 + 8
    vertical = [s for s in segments if abs(s[0][0] - s[1][0]) < 1e-9]
    assert len(vertical) == 6  # 3 lines, 2 pieces each
    for seg in vertical:
        assert math.isclose(abs(seg[1][1] - seg[0][1]), 8.0, abs_tol=1e-9)


def test_corridor_primitives_edges_and_dashes():
    corridor = Corridor(axis="x", line=1, width=4.0)
    bay = make_bay(corridor=corridor)
    edges, dashes = corridor_primitives(bay, dash_len=3.0, gap_len=2.0)
    assert len(edges) == 2
    assert len(dashes) == 4  # 20 long: dashes at 0,5,10,15
    assert edges[0][0] == (10.0, 28.0)
    assert edges[1][0] == (10.0, 32.0)


def test_door_symbols():
    door = Aperture(id="ap01", kind="door", axis="x", line=0,
                    offset=4.0, width=3.0, hinge="start", swing="in")
    bay = make_bay(apertures=[door])
    symbols = aperture_symbols(bay)
    kinds = [k for k, _ in symbols]
    assert kinds == ["line", "arc"]
    leaf = symbols[0][1]
    assert leaf[0] == (14.0, 20.0)  # hinge at offset 4 on south wall
    assert leaf[1] == (14.0, 23.0)  # leaf swings in (+y), length = width
    center, radius, start_deg, end_deg = symbols[1][1]
    assert center == (14.0, 20.0)
    assert radius == 3.0
    assert math.isclose((end_deg - start_deg) % 360.0, 90.0, abs_tol=1e-9)


def test_window_and_portal_symbols():
    window = Aperture(id="ap01", kind="window", axis="y", line=0,
                      offset=2.0, width=5.0)
    portal = Aperture(id="ap02", kind="portal", axis="x", line=2,
                      offset=1.0, width=4.0)
    bay = make_bay(apertures=[window, portal])
    symbols = aperture_symbols(bay)
    assert [k for k, _ in symbols] == ["line", "line", "line"]
    glass = symbols[0][1]
    assert glass == ((10.0, 22.0), (10.0, 27.0))


def test_arc_three_points():
    arc = Arc(center=(0.0, 0.0), radius=2.0, start_deg=0.0, end_deg=90.0)
    start, mid, end = arc_three_points(arc)
    assert math.isclose(start[0], 2.0, abs_tol=1e-9)
    assert math.isclose(mid[0], mid[1], abs_tol=1e-9)
    assert math.isclose(end[1], 2.0, abs_tol=1e-9)


def test_compile_scene_deterministic(school):
    plan_a = compile_scene(school.state)
    plan_b = compile_scene(school.state)
    assert plan_a == plan_b


def test_compile_scene_counts(school):
    plan = compile_scene(school.state)
    counts = plan_counts(plan)
    assert counts[LAYER_SITE] == 1
    assert counts[LAYER_COLUMNS] == 20  # 4x3 bay -> 5*4 intersections
    assert counts[LAYER_GRIDLINES] == 9  # 4 x-lines + 5 y-lines
    assert counts[LAYER_WALLS] > 0
    assert counts[LAYER_APERTURES] == 3  # door leaf + swing arc + window glass
    assert counts[LAYER_CORRIDORS] > 2
    assert plan_bbox(plan) is not None


def test_empty_state_compiles():
    plan = compile_scene(State.new())
    assert plan_counts(plan)["total"] == 0
