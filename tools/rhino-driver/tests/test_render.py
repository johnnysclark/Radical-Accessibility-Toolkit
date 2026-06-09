"""Tests for the model -> RhinoPython script renderer.

These guard the two original macOS show-stoppers:
1. command-shape translation (every create_object must produce real rs.* calls), and
2. string escaping (a quote/Braille name must never break the generated source).

The strongest check is ``compile(script, ...)``: it proves the generated script is
always syntactically valid Python, for any input, without needing Rhino.
"""

from tasc.core.model import Bay, BayVoid, Corridor, Grid, Site, TASCModel, Zone
from tasc.rhino.protocol import (
    create_circle_cmd,
    create_layer_cmd,
    create_line_cmd,
    create_polyline_cmd,
    create_text_cmd,
    delete_all_cmd,
    delete_by_name_cmd,
    execute_script_cmd,
    set_layer_cmd,
)

from rhino_driver.render import commands_to_script, model_to_commands, render_model


def _compiles(script: str) -> bool:
    compile(script, "<generated>", "exec")
    return True


class TestCommandTranslation:
    def test_polyline_emits_addpolyline_and_layer(self):
        cmds = create_polyline_cmd([(0, 0), (10, 0), (10, 10), (0, 10)], "site", "TASC_Site")
        script = commands_to_script(cmds)
        assert "rs.AddPolyline(" in script
        assert 'rs.CurrentLayer("TASC_Site")' in script
        assert _compiles(script)

    def test_line_emits_addline(self):
        script = commands_to_script(create_line_cmd((0, 0), (10, 10), "TASC_Grid"))
        assert "rs.AddLine(" in script
        assert _compiles(script)

    def test_circle_emits_addcircle(self):
        script = commands_to_script(create_circle_cmd((5, 5), 3.0, "TASC_Voids"))
        assert "rs.AddCircle(" in script
        assert _compiles(script)

    def test_text_emits_textdot(self):
        script = commands_to_script(create_text_cmd("Living", (25, 25), "TASC_Labels"))
        assert "rs.AddTextDot(" in script
        assert "Living" in script
        assert _compiles(script)

    def test_layer_is_guarded(self):
        script = commands_to_script([create_layer_cmd("TASC_Site", (0, 0, 0))])
        assert "rs.IsLayer(" in script
        assert "rs.AddLayer(" in script
        assert _compiles(script)

    def test_set_layer(self):
        script = commands_to_script([set_layer_cmd("TASC_Zones")])
        assert 'rs.CurrentLayer("TASC_Zones")' in script
        assert _compiles(script)

    def test_delete_all(self):
        script = commands_to_script([delete_all_cmd()])
        assert "rs.AllObjects()" in script
        assert "rs.DeleteObjects(" in script
        assert _compiles(script)

    def test_delete_by_name(self):
        script = commands_to_script([delete_by_name_cmd("site_boundary")])
        assert "rs.ObjectsByName(" in script
        assert "site_boundary" in script
        assert _compiles(script)

    def test_execute_script_is_inlined(self):
        code = "import rhinoscriptsyntax as rs\nrs.AddLine((0,0,0),(1,1,1))"
        script = commands_to_script([execute_script_cmd(code)])
        assert "rs.AddLine((0,0,0),(1,1,1))" in script
        assert _compiles(script)


class TestEscaping:
    def test_apostrophe_and_quotes_and_newline(self):
        # The exact failure class the old translator could not survive.
        cmds = create_text_cmd('O\'Brien "Wing"\nB', (0, 0), "TASC_Labels")
        script = commands_to_script(cmds)
        assert _compiles(script)

    def test_braille_unicode_name(self):
        cmds = create_text_cmd("⠇⠊⠃", (0, 0), "TASC_Labels")
        script = commands_to_script(cmds)
        # Non-ASCII is escaped to \\uXXXX so no source-encoding is needed.
        assert _compiles(script)


class TestModelRender:
    def _model(self) -> TASCModel:
        model = TASCModel()
        model.site = Site.rectangle(200, 150)
        model.add_zone(Zone.rectangle("O'Brien", 50, 40, at=(10, 10)))
        model.add_bay(Bay(name="A", origin=(18, 8), grid=(6, 3), spacing=(24, 24)))
        return model

    def test_model_to_commands_nonempty(self):
        cmds = model_to_commands(self._model())
        assert len(cmds) > 5
        types = {c["type"] for c in cmds}
        assert "create_object" in types
        assert "create_layer" in types

    def test_render_model_has_geometry_and_compiles(self):
        script = render_model(self._model())
        assert "import rhinoscriptsyntax as rs" in script
        assert "rs.AddPolyline(" in script  # site + zone + columns
        assert "rs.AddLine(" in script  # bay gridlines
        assert "rs.AddTextDot(" in script  # zone label
        assert _compiles(script)

    def test_empty_model_still_clears_and_sets_up(self):
        # No site: still a valid full-rebuild script (clear + layers).
        script = render_model(TASCModel())
        assert "rs.IsLayer(" in script
        assert _compiles(script)

    def test_rich_model_with_grid_corridor_circular_void_compiles(self):
        # Exercises the grid, corridor, and CIRCLE paths through the full pipeline.
        model = TASCModel()
        model.site = Site.rectangle(200, 150)
        model.grid = Grid(spacing=10, rotation=0)
        bay = Bay(name="A", origin=(18, 8), grid=(6, 3), spacing=(24, 24))
        bay.corridor = Corridor(enabled=True, axis="x", width=8, position=1)
        bay.void = BayVoid(center=(70, 36), size=(24, 24), shape="circle")
        model.add_bay(bay)
        script = render_model(model)
        assert "rs.AddCircle(" in script  # circular void
        assert _compiles(script)

    def test_inlined_import_is_deduplicated(self):
        # The combined script imports rhinoscriptsyntax exactly once at the top.
        script = render_model(TASCModel())
        assert script.count("import rhinoscriptsyntax as rs") == 1
