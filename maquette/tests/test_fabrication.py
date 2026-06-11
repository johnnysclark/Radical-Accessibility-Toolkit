"""STL, plan, and section exports at the engine level.

A stub stands in for the live Rhino connection and answers the same
mesh and section queries the listener would, so the whole path from
command to file bytes runs in CI. The live snippets themselves are
covered by test_compiler.py and the Mac verify script.
"""

import struct

import pytest

from maquette.engine import Engine
from maquette.ops import OpError

CUBE_VERTICES = [
    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
]
CUBE_FACES = [
    [0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
    [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
    [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7],
]


def cube_mesh(closed=True):
    return {"found": 1, "closed": closed, "solid": closed,
            "vertices": CUBE_VERTICES, "faces": CUBE_FACES, "skipped": []}


def square_cut(z=1.0):
    return {"found": 1, "skipped": [], "polylines": [
        {"points": [[0, 0, z], [2, 0, z], [2, 2, z], [0, 2, z]],
         "closed": True}]}


class StubLive:
    """Answers live queries from canned data, like the listener would."""

    def __init__(self, mesh=None, section=None):
        self.mesh = mesh or {}
        self.section = section or {}
        self.section_calls = []

    def query_mesh(self, maq_id):
        return self.mesh.get(maq_id, {"found": 0})

    def query_section(self, maq_id, origin, normal):
        self.section_calls.append((maq_id, tuple(origin), tuple(normal)))
        return self.section.get(maq_id, {"found": 0})


def live_stub(monkeypatch, stub):
    monkeypatch.setattr(Engine, "_live_queries",
                        lambda self, purpose: stub)


@pytest.fixture
def tower(engine):
    engine.run_text('box 2 2 3 at 0,0,0 name "tower"')
    return engine


# -- STL -------------------------------------------------------------------


def test_stl_export_writes_watertight_file(tower, tmp_path, monkeypatch):
    live_stub(monkeypatch, StubLive(mesh={"m1": cube_mesh()}))
    path = str(tmp_path / "tower.stl")
    result = tower.export(path)
    text = "\n".join(result["lines"])
    assert "wrote {0}.".format(path) in text
    assert "1 solids, 12 triangles, scale 1 to 100" in text
    assert "print size: 10 by 10 by 10 millimeters." in text
    assert "watertight: yes" in text
    assert result["warnings"] == []
    blob = open(path, "rb").read()
    assert len(blob) == 84 + 12 * 50
    assert struct.unpack_from("<I", blob, 80)[0] == 12


def test_stl_export_honors_scale_flag(tower, tmp_path, monkeypatch):
    live_stub(monkeypatch, StubLive(mesh={"m1": cube_mesh()}))
    result = tower.export(str(tmp_path / "big.stl"), scale="1:50")
    text = "\n".join(result["lines"])
    assert "scale 1 to 50" in text
    assert "print size: 20 by 20 by 20 millimeters." in text


def test_stl_export_warns_when_a_shell_is_open(tower, tmp_path, monkeypatch):
    live_stub(monkeypatch, StubLive(mesh={"m1": cube_mesh(closed=False)}))
    result = tower.export(str(tmp_path / "open.stl"))
    assert not any("watertight: yes" in line for line in result["lines"])
    warning = " ".join(result["warnings"])
    assert "not watertight" in warning
    assert 'm1 "tower"' in warning


def test_stl_export_with_no_solids_says_so(engine, tmp_path):
    engine.run_text("line 0,0 to 5,5")
    with pytest.raises(OpError) as caught:
        engine.export(str(tmp_path / "flat.stl"))
    assert "nothing printable" in str(caught.value)


def test_stl_export_when_rhino_is_empty_says_rebuild(tower, tmp_path,
                                                     monkeypatch):
    live_stub(monkeypatch, StubLive())  # nothing tagged in Rhino
    with pytest.raises(OpError) as caught:
        tower.export(str(tmp_path / "missing.stl"))
    assert "maquette rebuild" in str(caught.value)


# -- plans and sections ---------------------------------------------------


def test_plan_writes_svg_with_cut_summary(tower, tmp_path, monkeypatch):
    stub = StubLive(section={"m1": square_cut()})
    live_stub(monkeypatch, stub)
    path = str(tmp_path / "plan.svg")
    result = tower.export_plan(1.0, path)
    text = "\n".join(result["lines"])
    assert "plan cut at height 1 meters through 1 objects; 1 outlines." in text
    assert "scale 1 to 100; sheet 40 by 40 millimeters." in text
    svg = open(path, encoding="utf-8").read()
    assert "<path" in svg and "Z\"" in svg
    # The cut ran against a horizontal plane at the asked height.
    assert stub.section_calls == [("m1", (0.0, 0.0, 1.0), (0.0, 0.0, 1.0))]


def test_section_writes_dxf_and_cuts_across_x(tower, tmp_path, monkeypatch):
    stub = StubLive(section={"m1": square_cut()})
    live_stub(monkeypatch, stub)
    path = str(tmp_path / "section-a.dxf")
    result = tower.export_section("x", 1.5, path)
    text = "\n".join(result["lines"])
    assert "section cut at x 1.5 meters" in text
    assert "POLYLINE" in open(path, encoding="utf-8").read()
    assert stub.section_calls == [("m1", (1.5, 0.0, 0.0), (1.0, 0.0, 0.0))]


def test_plan_above_the_model_reports_the_span(tower, tmp_path, monkeypatch):
    live_stub(monkeypatch, StubLive(
        section={"m1": {"found": 1, "polylines": [], "skipped": []}}))
    with pytest.raises(OpError) as caught:
        tower.export_plan(50, str(tmp_path / "plan.svg"))
    message = str(caught.value)
    assert "does not cut anything" in message
    assert "spans height 0 to 3 meters" in message


def test_plan_needs_svg_or_dxf_path(tower, tmp_path):
    with pytest.raises(OpError) as caught:
        tower.export_plan(1.0, str(tmp_path / "plan.pdf"))
    assert ".svg or .dxf" in str(caught.value)


def test_plan_height_must_be_a_number(tower, tmp_path):
    with pytest.raises(OpError) as caught:
        tower.export_plan("tall", str(tmp_path / "plan.svg"))
    assert "must be a number" in str(caught.value)


def test_section_axis_must_be_x_or_y(tower, tmp_path):
    with pytest.raises(OpError) as caught:
        tower.export_section("z", 1.0, str(tmp_path / "s.svg"))
    assert "say which way to cut" in str(caught.value)


def test_fabrication_refuses_record_backend(tower, tmp_path):
    # The conftest engine runs on the record backend; without a stub the
    # real _live_queries must refuse rather than downgrade silently.
    with pytest.raises(OpError) as caught:
        tower.export_plan(1.0, str(tmp_path / "plan.svg"))
    assert "live Rhino connection" in str(caught.value)
    with pytest.raises(OpError) as caught:
        tower.export(str(tmp_path / "tower.stl"))
    assert "live Rhino connection" in str(caught.value)
