"""MCP server: exercise the underlying functions directly (the FastMCP
decorators wrap these same callables) plus a registration smoke check."""

import pytest

import jig.mcp_server as server


@pytest.fixture(autouse=True)
def fresh_session(tmp_path, monkeypatch):
    monkeypatch.setenv("JIG_STATE", str(tmp_path / "state.json"))
    monkeypatch.setattr(server, "_session", None)


def test_run_command_ok():
    result = server.run_command("site set 100 120")
    assert result == "OK: site set to 100 by 120 feet"


def test_run_command_error_is_prefixed():
    result = server.run_command("bogus")
    assert result.startswith("ERROR:")


def test_run_script_atomic():
    result = server.run_script(["site set 100 100", "nope"])
    assert result.startswith("ERROR:")
    assert server.session().state.site.boundary == []


def test_describe_and_state_path():
    server.run_command("bay add a 2x2 --spacing 24")
    assert "bay a" in server.describe_model()
    assert '"name": "a"' in server.get_state("bays.0")
    assert server.get_state("bays.9.name").startswith("ERROR:")


def test_validate_and_measure():
    server.run_command("site set 200 200")
    server.run_command("bay add a 2x2 --spacing 24 --at 10,10")
    server.run_command("zone add entry 40 30 --at 100,100")
    assert "clean" in server.validate_model()
    assert "distance" in server.measure("a", "entry")


def test_snapshot_undo_export(tmp_path):
    server.run_command("site set 100 100")
    assert "OK" in server.snapshot("save", "base")
    server.run_command("bay add a 2x2 --spacing 24")
    assert "OK" in server.undo(1)
    assert server.session().state.bays == []
    out = str(tmp_path / "out.3dm")
    assert "OK" in server.export_model("3dm", out)


def test_registered_surface():
    grammar = server.list_commands()
    assert "bay add" in grammar and "export 3dm" in grammar
    assert "jig" == server.mcp.name


def test_resources():
    server.run_command("site set 100 100")
    assert '"schema": "jig_v4"' in server.state_resource()
    assert "site: 4 corners" in server.describe_resource()
    assert "snapshot save" in server.grammar_resource()
