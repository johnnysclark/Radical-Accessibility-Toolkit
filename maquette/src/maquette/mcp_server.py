"""MCP server: Claude Code drives Maquette over stdio.

Register in a project's .mcp.json:

    {
      "mcpServers": {
        "maquette": {
          "type": "stdio",
          "command": "python3",
          "args": ["-m", "maquette.mcp_server", "--project", "/path/to/project"]
        }
      }
    }

Without --project it discovers the project from the working directory
(or MAQUETTE_PROJECT). Thirteen MCP functions, all returning the same
OK:/ERROR:-prefixed text the user hears everywhere else.
"""

from __future__ import annotations

import os
import sys

from mcp.server.fastmcp import FastMCP

from maquette import VERSION
from maquette.project import find_project
from maquette.service import MaquetteService

mcp = FastMCP("maquette")
_service: MaquetteService | None = None


def service() -> MaquetteService:
    global _service
    if _service is None:
        start = None
        argv = sys.argv[1:]
        if "--project" in argv:
            start = argv[argv.index("--project") + 1]
        start = start or os.environ.get("MAQUETTE_PROJECT")
        _service = MaquetteService(find_project(start), actor="mcp")
    return _service


@mcp.tool()
def create_objects(ops: list[dict]) -> str:
    """Create geometry. Each item: {"op": NAME, "params": {...},
    "name": optional, "layer": optional}. Ops: create_point {at},
    create_line {start,end}, create_polyline {points,closed},
    create_circle {center,radius}, create_arc {p1,p2,p3},
    create_rectangle {corner,width,depth}, create_curve {points,degree},
    create_text {text,at,height}, create_box {corner,size:[w,d,h]},
    create_sphere {center,radius}, create_cylinder {base,radius,height},
    create_cone {base,radius,height}, extrude {source,height|vector},
    loft {sources}, revolve {source,axis_start,axis_end,angle},
    boolean_union {inputs}, boolean_difference {keep,cut},
    boolean_intersection {inputs}. Coordinates are [x,y,z] lists.
    Refer to existing objects by id like m3, by exact name, or last."""
    return service().create_objects(ops)


@mcp.tool()
def edit_objects(ops: list[dict]) -> str:
    """Change existing objects. Each item: {"op": NAME, "params": {...}}.
    Ops: move {ids,vector}, rotate {ids,angle,center?,axis?},
    scale {ids,factors,center?}, mirror {ids,plane_point,plane_normal},
    copy {ids,vector,count?}, delete {ids} or {all:true},
    set_name {id,name}, set_layer {ids,layer}, create_layer {name},
    group {members,name?}, ungroup {gid}."""
    return service().edit_objects(ops)


@mcp.tool()
def query_scene(layer: str | None = None, kind: str | None = None,
                name_contains: str | None = None) -> str:
    """List alive objects, optionally filtered by layer, kind (box,
    sphere, line, union, script, ...), or a name substring."""
    return service().query_scene(layer, kind, name_contains)


@mcp.tool()
def describe_scene(level: str = "brief") -> str:
    """Spoken summary of the model. level "brief" for counts and
    extents, "full" to also list every object."""
    return service().describe_scene(level)


@mcp.tool()
def describe_object(ref: str) -> str:
    """Everything known about one object: kind, layer, size, position,
    status, group, pending state. ref is an id, exact name, or last."""
    return service().describe_object(ref)


@mcp.tool()
def measure(a: str, b: str) -> str:
    """Distance and per-axis deltas between two objects (by id or name)
    or literal points written like 0,0,0."""
    return service().measure(a, b)


@mcp.tool()
def run_script(code: str, intent: str, name: str | None = None) -> str:
    """Run rhinoscriptsyntax Python inside Rhino for anything beyond the
    op vocabulary. The code is journaled and replays on rebuild; intent
    is one plain sentence describing what it does (it is read aloud).
    The namespace has rs (rhinoscriptsyntax), sc, Rhino; append created
    guids to __maq_created__ (untagged creations are tagged
    automatically). Needs the live Rhino connection."""
    return service().run_script(code, intent, name)


@mcp.tool()
def undo(steps: int = 1) -> str:
    """Undo the last N steps by appending compensating ops."""
    return service().undo(steps)


@mcp.tool()
def rebuild(backend: str | None = None) -> str:
    """Replay the whole journal into a backend ("live" rebuilds Rhino,
    "headless" rebuilds the 3dm file). Reports drift warnings."""
    return service().rebuild(backend)


@mcp.tool()
def journal_show(last: int = 10, search: str | None = None) -> str:
    """Recent journal steps, one speakable line each; search filters."""
    return service().journal_show(last, search)


@mcp.tool()
def export_model(path: str, format: str | None = None) -> str:
    """Write the model to a file: .3dm (real geometry) or .txt (spoken
    description). Format inferred from the extension."""
    return service().export_model(path, format)


@mcp.tool()
def doctor() -> str:
    """Check the whole setup and say exactly what to fix, in order."""
    return service().doctor()


@mcp.tool()
def project_info() -> str:
    """Project name, units, journal length, last step, listener address."""
    return service().project_info()


def main() -> None:
    sys.stderr.write("maquette mcp server {0} starting on stdio\n".format(
        VERSION))
    mcp.run()


if __name__ == "__main__":
    main()
