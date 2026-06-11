"""Spawn the MCP server over stdio and drive it like Claude Code would."""

import sys

import pytest

pytest.importorskip("mcp")

import anyio  # noqa: E402  (a dependency of mcp)
from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

EXPECTED_FUNCTIONS = {
    "create_objects", "edit_objects", "query_scene", "describe_scene",
    "describe_object", "measure", "run_script", "undo", "rebuild",
    "journal_show", "export_model", "export_plan", "export_section",
    "doctor", "project_info",
}


def run_session(project_root, calls):
    """Start the server, run (tool, args) calls, return list of texts."""
    results = {}

    async def go():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "maquette.mcp_server", "--project", project_root])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                listed = await session.list_tools()
                results["tools"] = {tool.name for tool in listed.tools}
                texts = []
                for name, arguments in calls:
                    outcome = await session.call_tool(name, arguments)
                    texts.append(outcome.content[0].text)
                results["texts"] = texts

    anyio.run(go)
    return results


def test_mcp_server_lists_and_runs_functions(project):
    results = run_session(project.root, [
        ("project_info", {}),
        ("create_objects", {"ops": [
            {"op": "create_box", "params": {"corner": [0, 0, 0],
                                            "size": [10, 10, 30]},
             "name": "tower base"},
            {"op": "create_sphere", "params": {"center": [5, 5, 34],
                                               "radius": 4}},
        ]}),
        ("edit_objects", {"ops": [
            {"op": "move", "params": {"ids": ["m1"], "vector": [0, 0, 1]}},
        ]}),
        ("query_scene", {}),
        ("describe_object", {"ref": "tower base"}),
        ("measure", {"a": "m1", "b": "m2"}),
        ("undo", {}),
        ("journal_show", {}),
    ])
    assert results["tools"] == EXPECTED_FUNCTIONS
    info, created, edited, queried, detail, measured, undone, journal = \
        results["texts"]
    assert info.startswith("OK: project testproj")
    assert created.startswith("OK: created m1 \"tower base\" (box)")
    assert "m2" in created
    assert edited.startswith("OK: moved m1")
    assert queried.startswith("OK: 2 matching objects.")
    assert "kind: box." in detail
    assert "distance:" in measured
    assert undone.startswith("OK: undoing step 3")
    assert "create_box m1 tower base" in journal


def test_mcp_server_speaks_errors(project):
    results = run_session(project.root, [
        ("create_objects", {"ops": [
            {"op": "create_box", "params": {"corner": [0, 0, 0],
                                            "size": [10, 10]}}]}),
        ("describe_object", {"ref": "nothing"}),
        ("run_script", {"code": "print(1)", "intent": ""}),
        ("export_plan", {"height": 1.0, "path": "exports/plan.svg"}),
        ("export_section", {"axis": "q", "position": 1.0,
                            "path": "exports/section.svg"}),
    ])
    bad_box, missing, no_intent, no_cut, bad_axis = results["texts"]
    assert bad_box.startswith("ERROR: item 1:")
    assert missing.startswith("ERROR: no object called")
    assert no_intent.startswith("ERROR:")
    assert "intent" in no_intent
    assert no_cut.startswith("ERROR: nothing to cut yet")
    assert bad_axis.startswith("ERROR: say which way to cut")
