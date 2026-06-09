"""Headless backend: real geometry in a .3dm, written and read back."""

import os

import pytest

rhino3dm = pytest.importorskip("rhino3dm")

from maquette.engine import Engine  # noqa: E402


@pytest.fixture
def hengine(project):
    return Engine(project, backend="headless", actor="test")


def model_path(project):
    return os.path.join(project.exports_dir, "model.3dm")


def read_model(project):
    model = rhino3dm.File3dm.Read(model_path(project))
    assert model is not None
    return model


def by_maq_id(model):
    out = {}
    for obj in model.Objects:
        out.setdefault(obj.Attributes.GetUserString("MAQ_ID"), []).append(obj)
    return out


def test_create_ops_write_real_geometry(hengine, project):
    commands = [
        'box 10 10 30 name "tower base"',
        "sphere radius 4 at 30,0,0",
        "cylinder radius 2 height 12 at 40,0,0",
        "cone radius 3 height 9 at 50,0,0",
        "point 1,2,3",
        "line 0,20 to 10,20",
        "polyline 0,30 10,30 10,40 closed",
        "circle radius 5 at 30,30",
        "arc 50,30 55,35 60,30",
        "rect 8 6 at 70,0",
        "curve 0,50 5,55 10,50 15,58",
        'text "north entry" at 80,0 height 2',
    ]
    for command in commands:
        hengine.run_text(command)
    model = read_model(project)
    found = by_maq_id(model)
    assert len(found) == len(commands)
    box_obj = found["m1"][0]
    bb = box_obj.Geometry.GetBoundingBox()
    assert (bb.Min.X, bb.Min.Y, bb.Min.Z) == (0, 0, 0)
    assert (bb.Max.X, bb.Max.Y, bb.Max.Z) == (10, 10, 30)
    assert box_obj.Attributes.Name == "tower base"
    assert box_obj.Attributes.GetUserString("MAQ_OP") == "create_box"
    # The journal records measured fingerprints from rhino3dm.
    entry = hengine.entries()[0]
    assert entry["result"]["status"] == "applied"
    assert entry["result"]["fingerprint"]["quality"] == "measured"


def test_extrude_and_revolve_realize(hengine, project):
    hengine.run_text("rect 10 6")
    hengine.run_text("extrude m1 height 12")
    hengine.run_text("line 0,0,0 to 0,0,5")
    result = hengine.run_op({"op": "revolve", "params": {
        "source": "m3", "axis_start": [2, 0, 0], "axis_end": [2, 0, 5],
        "angle": 360}})
    assert result["lines"]
    found = by_maq_id(read_model(project))
    extrusion = found["m2"][0].Geometry
    bb = extrusion.GetBoundingBox()
    assert round(bb.Max.Z, 6) == 12
    assert "m4" in found


def test_booleans_record_and_keep_inputs_visible(hengine, project):
    hengine.run_text("box 10 10 10")
    hengine.run_text("sphere radius 3 at 10,5,5")
    result = hengine.run_text("union m1 m2")
    assert any("needs Rhino" in w for w in result["warnings"])
    entry = hengine.entries()[-1]
    assert entry["result"]["status"] == "recorded"
    found = by_maq_id(read_model(project))
    assert "m1" in found and "m2" in found and "m3" not in found


def test_transforms_move_geometry_in_file(hengine, project):
    hengine.run_text("box 10 10 10")
    hengine.run_text("move m1 by 100,0,0")
    found = by_maq_id(read_model(project))
    assert found["m1"][0].Geometry.GetBoundingBox().Min.X == 100
    hengine.run_text("rotate m1 by 90 around 100,0,0")
    found = by_maq_id(read_model(project))
    bb = found["m1"][0].Geometry.GetBoundingBox()
    assert round(bb.Min.X, 6) == 90
    # Journal fingerprint for the rotate is measured, not predicted.
    assert hengine.entries()[-1]["result"]["fingerprint"]["quality"] == "measured"


def test_delete_and_undo_restore_in_file(hengine, project):
    hengine.run_text("box 10 10 10")
    hengine.run_text("move m1 by 5,0,0")
    hengine.run_text("delete m1")
    assert by_maq_id(read_model(project)) == {}
    hengine.undo_steps()  # restore, with its transform history
    found = by_maq_id(read_model(project))
    assert found["m1"][0].Geometry.GetBoundingBox().Min.X == 5


def test_copy_count_places_clones(hengine, project):
    hengine.run_text("box 5 5 5")
    hengine.run_text("copy m1 by 10,0,0 count 2")
    found = by_maq_id(read_model(project))
    assert found["m2"][0].Geometry.GetBoundingBox().Min.X == 10
    assert found["m3"][0].Geometry.GetBoundingBox().Min.X == 20


def test_layers_nest_under_maq(hengine, project):
    hengine.run_text("box 1 1 1 layer Walls")
    model = read_model(project)
    paths = [layer.FullPath for layer in model.Layers]
    assert "MAQ::Walls" in paths
    assert "MAQ" in paths
    found = by_maq_id(model)
    layer_index = found["m1"][0].Attributes.LayerIndex
    by_index = {layer.Index: layer.FullPath for layer in model.Layers}
    assert by_index[layer_index] == "MAQ::Walls"


def test_rename_and_set_layer_persist(hengine, project):
    hengine.run_text("box 1 1 1")
    hengine.run_text('rename m1 "the plinth"')
    hengine.run_text("put m1 on Podium")
    found = by_maq_id(read_model(project))
    assert found["m1"][0].Attributes.Name == "the plinth"


def test_rebuild_headless_regenerates_file(hengine, project):
    hengine.run_text("box 10 10 10")
    hengine.run_text("move m1 by 5,0,0")
    os.remove(model_path(project))
    result = hengine.rebuild("headless")
    assert any("rebuilt" in line for line in result["lines"])
    found = by_maq_id(read_model(project))
    assert found["m1"][0].Geometry.GetBoundingBox().Min.X == 5
    # Reconcile entry cleared nothing pending but recorded fingerprints.
    assert hengine.entries()[-1]["op"] == "reconcile"


def test_export_3dm_to_custom_path(hengine, project, tmp_path):
    hengine.run_text("box 10 10 10")
    hengine.run_text("box 5 5 5 at 20,0,0")
    hengine.run_text("union m1 m2")
    out = str(tmp_path / "out.3dm")
    result = hengine.export(out, "3dm")
    assert os.path.exists(out)
    assert any("m3" in w for w in result["warnings"])  # pending not in file
    model = rhino3dm.File3dm.Read(out)
    assert len(list(model.Objects)) == 2


def test_record_then_headless_rebuild_catches_up(project):
    record_engine = Engine(project, backend="record", actor="test")
    record_engine.run_text("box 10 10 10")
    record_engine.run_text("move m1 by 0,50,0")
    headless_engine = Engine(project, backend="headless", actor="test")
    headless_engine.rebuild("headless")
    found = by_maq_id(read_model(project))
    assert found["m1"][0].Geometry.GetBoundingBox().Min.Y == 50
