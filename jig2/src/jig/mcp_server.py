"""jig MCP server: 12 functions, 3 resources, 2 prompts.

A thin shim over the command registry — the LLM mutates the model with the
exact same grammar a human types, so nothing here duplicates command logic.

Run with:  python -m jig.mcp_server
State file: $JIG_STATE, defaulting to ./state.json in the working directory.
"""

import json
import os

from mcp.server.fastmcp import FastMCP

from jig import describe as describe_mod
from jig.commands import CommandError, Session
from jig.commands.registry import all_commands
from jig.model.validate import validate as validate_state

mcp = FastMCP("jig")
_session = None


def session():
    global _session
    if _session is None:
        _session = Session(os.environ.get("JIG_STATE", "state.json"))
    return _session


def _run(line):
    try:
        return "OK: " + session().execute(line)
    except CommandError as exc:
        return "ERROR: " + str(exc)


# -- functions ---------------------------------------------------------------

@mcp.tool()
def run_command(line: str) -> str:
    """Run one jig command, e.g. 'bay add a 6x4 --spacing 24 --at 18,8'.
    Same grammar as the human CLI; call list_commands for the reference."""
    return _run(line)


@mcp.tool()
def run_script(lines: list[str]) -> str:
    """Run several jig commands as one undo step. Rolls everything back and
    reports the failing line if any command fails."""
    try:
        outputs = session().run_script(lines)
    except CommandError as exc:
        return "ERROR: " + str(exc)
    return "OK: {} commands ran\n".format(len(outputs)) + "\n".join(outputs)


@mcp.tool()
def list_commands() -> str:
    """The full command grammar: usage line and summary for every command."""
    return "\n".join("{}\n  {}".format(s.usage, s.summary) for s in all_commands())


@mcp.tool()
def describe_model(section: str = "all") -> str:
    """Prose description of the model. Sections: all, meta, site, zones,
    grid, bays."""
    return describe_mod.describe(session().state, section)


@mcp.tool()
def get_state(path: str = "") -> str:
    """The raw state JSON, or one part of it via a dotted path like
    'bays.0.apertures' (list indices are numeric)."""
    node = session().state.to_dict()
    if path:
        for part in path.split("."):
            try:
                node = node[int(part)] if isinstance(node, list) else node[part]
            except (KeyError, IndexError, ValueError):
                return "ERROR: no path {} in the state".format(path)
    return json.dumps(node, indent=2)


@mcp.tool()
def validate_model() -> str:
    """Check the model for semantic problems: out-of-range apertures,
    overlapping cells, bays outside the site."""
    findings = validate_state(session().state)
    if not findings:
        return "OK: model is clean, no findings"
    return "OK: {} findings\n".format(len(findings)) + "\n".join(findings)


@mcp.tool()
def measure(from_name: str, to_name: str) -> str:
    """Center-to-center distance between two named things: bays, zones, or
    cells addressed as BAY/I,J."""
    return _run("measure {} {}".format(from_name, to_name))


@mcp.tool()
def snapshot(action: str, name: str = "") -> str:
    """Named checkpoints. Actions: save, load, list, diff."""
    line = "snapshot {} {}".format(action, name).strip()
    return _run(line)


@mcp.tool()
def undo(steps: int = 1) -> str:
    """Undo the last change, or several."""
    return _run("undo {}".format(steps))


@mcp.tool()
def export_model(format: str, path: str) -> str:
    """Export the model. Formats: 3dm (Rhino file, works offline), text
    (prose description)."""
    return _run("export {} {}".format(format, path))


@mcp.tool()
def rhino_status() -> str:
    """What the Rhino watcher last drew, from scene_report.json."""
    return _run("rhino status")


@mcp.tool()
def rhino_start() -> str:
    """Launch Rhino 8 on macOS and inject the live watcher."""
    return _run("rhino start")


# -- resources ---------------------------------------------------------------

@mcp.resource("jig://state")
def state_resource() -> str:
    """The raw model state JSON."""
    return json.dumps(session().state.to_dict(), indent=2)


@mcp.resource("jig://describe")
def describe_resource() -> str:
    """The full prose description of the model."""
    return describe_mod.describe(session().state)


@mcp.resource("jig://grammar")
def grammar_resource() -> str:
    """The full command grammar reference."""
    return "\n".join("{}\n  {}".format(s.usage, s.summary) for s in all_commands())


# -- prompts -----------------------------------------------------------------

@mcp.prompt()
def design_review() -> str:
    """Walk the current model and critique it."""
    return ("Review the current jig model. First call describe_model and "
            "validate_model. Then assess: structural clarity of the bay "
            "grids, circulation (corridor widths and door placement), and "
            "whether named cells form a coherent program. Report findings "
            "as short labeled lines a screen reader can step through, "
            "most important first.")


@mcp.prompt()
def start_layout() -> str:
    """Guided setup of a new site layout."""
    return ("Help me start a layout. Ask me, one question at a time, with "
            "numbered options: site size, structural bay spacing, how many "
            "bay grids, corridor needs. After each answer, issue the "
            "matching jig commands with run_command and read back the OK "
            "line. Finish with describe_model.")


def main():
    mcp.run()


if __name__ == "__main__":
    main()
