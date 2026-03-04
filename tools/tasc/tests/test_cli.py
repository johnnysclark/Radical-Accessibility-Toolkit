"""Tests for TASC CLI commands."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from tasc_core.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def clean_state(tmp_path, monkeypatch):
    """Run CLI in a clean temp directory."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestVersion:
    def test_version_command(self, runner):
        result = runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "TASC" in result.output

    def test_version_flag(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestSite:
    def test_create_site(self, runner, clean_state):
        result = runner.invoke(main, ["site", "200", "150"])
        assert result.exit_code == 0
        assert "200" in result.output
        assert "150" in result.output
        assert "Site boundary created" in result.output

    def test_create_site_meters(self, runner, clean_state):
        result = runner.invoke(main, ["site", "60", "40", "--units", "meters"])
        assert result.exit_code == 0
        assert "meters" in result.output

    def test_site_persists_state(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        state_file = clean_state / ".tasc_state.json"
        assert state_file.exists()
        data = json.loads(state_file.read_text())
        assert data["site"]["corners"] is not None


class TestGrid:
    def test_grid_with_site(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        result = runner.invoke(main, ["grid", "10"])
        assert result.exit_code == 0
        assert "Grid applied" in result.output

    def test_grid_without_site(self, runner, clean_state):
        result = runner.invoke(main, ["grid", "10"])
        assert result.exit_code == 0
        assert "Grid set" in result.output

    def test_grid_with_rotation(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        result = runner.invoke(main, ["grid", "10", "--rotation", "45"])
        assert result.exit_code == 0


class TestZone:
    def test_rectangular_zone(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        result = runner.invoke(main, ["zone", "living", "50", "40", "--at", "10,10"])
        assert result.exit_code == 0
        assert "living zone placed" in result.output

    def test_zone_default_position(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        result = runner.invoke(main, ["zone", "hall", "20", "30"])
        assert result.exit_code == 0

    def test_zone_with_corners(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        result = runner.invoke(main, ["zone", "lobby", "--corners", "0,0 20,0 20,15 0,15"])
        assert result.exit_code == 0
        assert "lobby zone placed" in result.output

    def test_zone_with_type(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        result = runner.invoke(main, ["zone", "kitchen", "30", "20", "--at", "10,10", "--type", "service"])
        assert result.exit_code == 0

    def test_zone_outside_boundary_warns(self, runner, clean_state):
        runner.invoke(main, ["site", "100", "100"])
        result = runner.invoke(main, ["zone", "big", "150", "50", "--at", "0,0"])
        assert result.exit_code == 0
        assert "Warning" in result.output

    def test_missing_dimensions(self, runner, clean_state):
        result = runner.invoke(main, ["zone", "test"])
        assert result.exit_code != 0


class TestList:
    def test_list_empty(self, runner, clean_state):
        result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert "No zones" in result.output

    def test_list_with_data(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        runner.invoke(main, ["zone", "living", "50", "40", "--at", "10,10"])
        result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert "living" in result.output


class TestDescribe:
    def test_describe_empty(self, runner, clean_state):
        result = runner.invoke(main, ["describe"])
        assert result.exit_code == 0
        assert "No site" in result.output

    def test_describe_full(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        runner.invoke(main, ["grid", "10"])
        runner.invoke(main, ["zone", "living", "50", "40", "--at", "10,10"])
        result = runner.invoke(main, ["describe"])
        assert result.exit_code == 0
        assert "200" in result.output
        assert "living" in result.output
        assert "Area" in result.output


class TestRemove:
    def test_remove_existing(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        runner.invoke(main, ["zone", "living", "50", "40", "--at", "10,10"])
        result = runner.invoke(main, ["remove", "living"])
        assert result.exit_code == 0
        assert "removed" in result.output

    def test_remove_nonexistent(self, runner, clean_state):
        result = runner.invoke(main, ["remove", "nothing"])
        assert result.exit_code == 0
        assert "not found" in result.output


class TestReset:
    def test_reset(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        result = runner.invoke(main, ["reset"])
        assert result.exit_code == 0
        assert "cleared" in result.output


class TestConnect:
    def test_connect_offline(self, runner):
        result = runner.invoke(main, ["connect"])
        assert result.exit_code == 0
        # Should report offline or rhinocode


class TestDefaultGroup:
    def test_script_routing(self, runner, clean_state):
        # Create a simple script
        script = clean_state / "test_script.py"
        script.write_text('print("hello from script")\n')
        result = runner.invoke(main, [str(script)])
        assert result.exit_code == 0
        assert "hello from script" in result.output


class TestExport:
    def test_export_text(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        runner.invoke(main, ["zone", "living", "50", "40", "--at", "10,10"])
        result = runner.invoke(main, ["export", "text"])
        assert result.exit_code == 0
        assert "Exported" in result.output
        output_file = clean_state / "tasc_output.txt"
        assert output_file.exists()

    def test_export_no_site(self, runner, clean_state):
        result = runner.invoke(main, ["export", "text"])
        assert result.exit_code != 0


class TestBay:
    def test_create_bay(self, runner, clean_state):
        result = runner.invoke(main, ["bay", "A", "6x3", "--spacing", "24", "24", "--at", "18,8"])
        assert result.exit_code == 0
        assert "Bay A placed" in result.output
        assert "6 by 3" in result.output
        assert "28 columns" in result.output

    def test_create_bay_defaults(self, runner, clean_state):
        result = runner.invoke(main, ["bay", "B", "3x3"])
        assert result.exit_code == 0
        assert "Bay B placed" in result.output

    def test_update_bay_rotation(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3", "--spacing", "24", "24"])
        result = runner.invoke(main, ["bay", "A", "--rotation", "15"])
        assert result.exit_code == 0
        assert "rotation" in result.output
        assert "15" in result.output

    def test_update_bay_column_size(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3"])
        result = runner.invoke(main, ["bay", "A", "--column-size", "2.0"])
        assert result.exit_code == 0
        assert "column_size" in result.output

    def test_bay_persists(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3", "--spacing", "24", "24"])
        state_file = clean_state / ".tasc_state.json"
        data = json.loads(state_file.read_text())
        assert len(data["bays"]) == 1
        assert data["bays"][0]["name"] == "A"

    def test_bay_irregular_spacing(self, runner, clean_state):
        result = runner.invoke(main, ["bay", "A", "5x3", "--spacing-x", "24,30,24,18,24"])
        assert result.exit_code == 0

    def test_bay_in_describe(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        runner.invoke(main, ["bay", "A", "6x3", "--spacing", "24", "24", "--at", "18,8"])
        result = runner.invoke(main, ["describe"])
        assert result.exit_code == 0
        assert "Bays (1)" in result.output
        assert "A:" in result.output

    def test_bay_in_list(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3"])
        result = runner.invoke(main, ["list"])
        assert result.exit_code == 0
        assert "Bay A" in result.output


class TestCorridor:
    def test_corridor_on(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3"])
        result = runner.invoke(main, ["corridor", "A", "on", "--axis", "x", "--width", "8"])
        assert result.exit_code == 0
        assert "Corridor enabled" in result.output

    def test_corridor_off(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3"])
        runner.invoke(main, ["corridor", "A", "on"])
        result = runner.invoke(main, ["corridor", "A", "off"])
        assert result.exit_code == 0
        assert "disabled" in result.output

    def test_corridor_bay_not_found(self, runner, clean_state):
        result = runner.invoke(main, ["corridor", "Z", "on"])
        assert result.exit_code == 0
        assert "not found" in result.output

    def test_corridor_with_options(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3"])
        result = runner.invoke(main, ["corridor", "A", "on", "--axis", "y", "--width", "10", "--loading", "single", "--position", "2"])
        assert result.exit_code == 0
        assert "North-south" in result.output
        assert "single-loaded" in result.output


class TestVoid:
    def test_void_rectangle(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3"])
        result = runner.invoke(main, ["void", "A", "rectangle", "30x18", "--at", "90,44"])
        assert result.exit_code == 0
        assert "Void set" in result.output
        assert "Rectangle" in result.output

    def test_void_circle(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3"])
        result = runner.invoke(main, ["void", "A", "circle", "24"])
        assert result.exit_code == 0
        assert "Circle" in result.output

    def test_void_off(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3"])
        runner.invoke(main, ["void", "A", "rectangle", "30x18"])
        result = runner.invoke(main, ["void", "A", "off"])
        assert result.exit_code == 0
        assert "removed" in result.output

    def test_void_bay_not_found(self, runner, clean_state):
        result = runner.invoke(main, ["void", "Z", "rectangle", "30x18"])
        assert result.exit_code == 0
        assert "not found" in result.output


class TestLabel:
    def test_label_on_bay(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3"])
        result = runner.invoke(main, ["label", "A", "Library", "--braille", "⠇⠊⠃⠗⠁⠗⠽"])
        assert result.exit_code == 0
        assert "Label set" in result.output
        assert "Library" in result.output
        assert "⠇⠊⠃⠗⠁⠗⠽" in result.output

    def test_label_on_zone(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        runner.invoke(main, ["zone", "living", "50", "40", "--at", "10,10"])
        result = runner.invoke(main, ["label", "living", "Living Room"])
        assert result.exit_code == 0
        assert "Label set" in result.output
        assert "Living Room" in result.output

    def test_label_not_found(self, runner, clean_state):
        result = runner.invoke(main, ["label", "nonexistent", "Test"])
        assert result.exit_code == 0
        assert "not found" in result.output


class TestUndo:
    def test_undo_reverts(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        runner.invoke(main, ["bay", "A", "6x3"])
        result = runner.invoke(main, ["undo"])
        assert result.exit_code == 0
        assert "Undo" in result.output
        # After undo, bay should be gone
        list_result = runner.invoke(main, ["list"])
        assert "Bay A" not in list_result.output

    def test_undo_empty(self, runner, clean_state):
        result = runner.invoke(main, ["undo"])
        assert result.exit_code == 0
        assert "Nothing to undo" in result.output

    def test_undo_multiple(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        runner.invoke(main, ["bay", "A", "6x3"])
        runner.invoke(main, ["bay", "B", "3x3"])
        # Undo bay B
        runner.invoke(main, ["undo"])
        # Undo bay A
        runner.invoke(main, ["undo"])
        list_result = runner.invoke(main, ["list"])
        assert "Bay" not in list_result.output

    def test_undo_cleared_on_reset(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        runner.invoke(main, ["bay", "A", "6x3"])
        runner.invoke(main, ["reset"])
        result = runner.invoke(main, ["undo"])
        assert "Nothing to undo" in result.output


class TestRemoveBay:
    def test_remove_bay(self, runner, clean_state):
        runner.invoke(main, ["bay", "A", "6x3"])
        result = runner.invoke(main, ["remove", "A"])
        assert result.exit_code == 0
        assert "Bay A removed" in result.output

    def test_remove_bay_then_zone(self, runner, clean_state):
        runner.invoke(main, ["site", "200", "150"])
        runner.invoke(main, ["zone", "living", "50", "40"])
        result = runner.invoke(main, ["remove", "living"])
        assert result.exit_code == 0
        assert "removed" in result.output
