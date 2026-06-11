"""drawing.py: scale math and the STL/SVG/DXF writers, no Rhino needed."""

import struct

import pytest

from maquette import drawing
from maquette.drawing import DrawingError

# A unit cube: 8 vertices, 12 triangles, watertight.
CUBE_VERTICES = [
    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
]
CUBE_FACES = [
    [0, 2, 1], [0, 3, 2],  # bottom
    [4, 5, 6], [4, 6, 7],  # top
    [0, 1, 5], [0, 5, 4],  # front
    [1, 2, 6], [1, 6, 5],  # right
    [2, 3, 7], [2, 7, 6],  # back
    [3, 0, 4], [3, 4, 7],  # left
]


def test_parse_scale_meters_to_paper_millimeters():
    factor, spoken = drawing.parse_scale("1:100", "meters")
    assert factor == 10.0
    assert spoken == "1 to 100"


def test_parse_scale_default_is_one_to_one_hundred():
    factor, spoken = drawing.parse_scale(None, "meters")
    assert factor == 10.0
    assert spoken == "1 to 100"


def test_parse_scale_other_units():
    assert drawing.parse_scale("1:1", "millimeters")[0] == 1.0
    assert drawing.parse_scale("1:48", "feet")[0] == pytest.approx(6.35)


def test_parse_scale_rejects_gibberish():
    with pytest.raises(DrawingError) as caught:
        drawing.parse_scale("really big", "meters")
    assert "1:100" in str(caught.value)
    with pytest.raises(DrawingError):
        drawing.parse_scale("0:100", "meters")


def test_to_paper_keeps_up_up():
    assert drawing.to_paper("z", [1, 2, 3]) == (1, 2)   # plan: x across, y up
    assert drawing.to_paper("x", [1, 2, 3]) == (2, 3)   # section: z up
    assert drawing.to_paper("y", [1, 2, 3]) == (1, 3)


def test_write_stl_binary_layout(tmp_path):
    path = str(tmp_path / "cube.stl")
    stats = drawing.write_stl(
        path, [{"vertices": CUBE_VERTICES, "faces": CUBE_FACES}], 10.0)
    assert stats["triangles"] == 12
    assert stats["size_mm"] == [10.0, 10.0, 10.0]
    with open(path, "rb") as handle:
        blob = handle.read()
    assert len(blob) == 84 + 12 * 50
    assert blob[:8] == b"Maquette"
    (count,) = struct.unpack_from("<I", blob, 80)
    assert count == 12
    # First triangle is the bottom; its normal must point straight down.
    values = struct.unpack_from("<12f", blob, 84)
    assert values[:3] == (0.0, 0.0, -1.0)
    # Vertices are scaled into millimeters.
    assert max(values[3:]) == 10.0


def test_write_stl_with_nothing_fails_loudly(tmp_path):
    with pytest.raises(DrawingError):
        drawing.write_stl(str(tmp_path / "empty.stl"),
                          [{"vertices": [], "faces": []}], 1.0)


def test_write_svg_flips_v_and_sizes_sheet(tmp_path):
    path = str(tmp_path / "plan.svg")
    outlines = [
        {"points": [(0, 0), (100, 0), (100, 50), (0, 50), (0, 0)],
         "closed": True},
        {"points": [(10, 10), (90, 10)], "closed": False},
    ]
    stats = drawing.write_svg(path, outlines, "Maquette plan, scale 1 to 100")
    assert stats["outlines"] == 2
    assert stats["sheet_mm"] == [120.0, 70.0]  # extents plus 10 mm margins
    text = open(path, encoding="utf-8").read()
    assert text.startswith("<?xml")
    assert 'width="120.0mm"' in text
    assert "<title>Maquette plan, scale 1 to 100</title>" in text
    assert text.count("<path") == 2
    assert '"M' in text and "Z\"" in text
    # v=0 (model ground) lands at the sheet bottom, larger SVG y.
    assert "M10.000 60.000" in text


def test_write_dxf_polylines(tmp_path):
    path = str(tmp_path / "section.dxf")
    outlines = [
        {"points": [(0, 0), (50, 0), (50, 30), (0, 30)], "closed": True},
        {"points": [(0, 35), (50, 35)], "closed": False},
    ]
    stats = drawing.write_dxf(path, outlines, "Maquette section")
    assert stats["outlines"] == 2
    text = open(path, encoding="utf-8").read()
    assert text.count("POLYLINE") == 2
    assert text.count("SEQEND") == 2
    assert text.count("VERTEX") == 6
    assert "AC1009" in text
    assert text.rstrip().endswith("EOF")
    # Closed flag: group 70 value 1 once, value 0 once.
    assert "70\n1\n" in text and "70\n0\n" in text


def test_writers_reject_empty_outline_lists(tmp_path):
    with pytest.raises(DrawingError):
        drawing.write_svg(str(tmp_path / "a.svg"), [], "t")
    with pytest.raises(DrawingError):
        drawing.write_dxf(str(tmp_path / "a.dxf"), [], "t")
