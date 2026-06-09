import rhino3dm

from jig.export.text import export_text
from jig.export.threedm import export_3dm
from jig.geometry.compile import compile_scene
from jig.geometry.primitives import plan_counts


def test_export_3dm_round_trip(tmp_path, school):
    path = str(tmp_path / "model.3dm")
    written = export_3dm(school.state, path)
    expected = plan_counts(compile_scene(school.state))["total"]
    assert written == expected

    model = rhino3dm.File3dm.Read(path)
    assert len(model.Objects) == expected
    layer_names = {layer.Name for layer in model.Layers}
    assert "JIG" in layer_names
    assert "Columns" in layer_names
    assert "Walls" in layer_names
    assert model.Settings.ModelUnitSystem == rhino3dm.UnitSystem.Feet


def test_export_3dm_skips_empty_layers(tmp_path, session):
    session.execute("site set 50 50")
    path = str(tmp_path / "site-only.3dm")
    export_3dm(session.state, path)
    model = rhino3dm.File3dm.Read(path)
    layer_names = {layer.Name for layer in model.Layers}
    assert layer_names == {"JIG", "Site"}


def test_export_text(tmp_path, school):
    path = str(tmp_path / "model.txt")
    export_text(school.state, path)
    content = open(path).read()
    assert "bay a" in content
    assert "site: 4 corners" in content


def test_export_commands(tmp_path, school):
    message = school.execute("export 3dm {}".format(tmp_path / "out.3dm"))
    assert "objects" in message
    message = school.execute("export text {}".format(tmp_path / "out.txt"))
    assert "description" in message
