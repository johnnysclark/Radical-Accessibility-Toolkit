# -*- coding: utf-8 -*-
"""
PLAN LAYOUT JIG — MCP Server  v2.0
====================================
Model Context Protocol wrapper around the Layout Jig CLI.

Exposes the CLI's command vocabulary as semantic MCP tools so that Claude Code,
Claude Desktop, Cursor, or any MCP-compatible client can drive the jig
conversationally using typed parameters instead of raw CLI strings.

v2.0 changes (from v1.0):
  - 15+ new semantic tools for typed parameter access
  - MCP resources for state and snapshot introspection
  - MCP prompts for common workflows
  - Upgraded from mcp 1.9.1 to 1.26.0
  - run_command kept as escape hatch for advanced/rare commands

Requires: pip install mcp  (tested with mcp 1.26.0)

Usage:
    python mcp_server.py --state path/to/state.json

Or set the environment variable:
    LAYOUT_JIG_STATE=path/to/state.json python mcp_server.py

Claude Code config (.mcp.json at project root):
{
  "mcpServers": {
    "layout-jig": {
      "command": "python",
      "args": ["Layout Jig/layout-jig/mcp_server.py", "--state",
               "Layout Jig/layout-jig/state.json"]
    }
  }
}
"""

import builtins
import json
import os
import sys

# ── Redirect print to stderr (stdout is JSON-RPC) ──────
_real_print = builtins.print

def _stderr_print(*args, **kwargs):
    kwargs.setdefault("file", sys.stderr)
    _real_print(*args, **kwargs)

builtins.print = _stderr_print

# ── Import controller_cli from same directory ──────────
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

import controller_cli as cli

# ── MCP dependency ─────────────────────────────────────
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    _real_print(
        "ERROR: mcp package not found. Install with: pip install mcp",
        file=sys.stderr)
    sys.exit(1)

# ── Resolve state file path ───────────────────────────
def _resolve_state_path():
    """Resolve state file from CLI args or environment variable."""
    # Check CLI args
    for i, arg in enumerate(sys.argv):
        if arg == "--state" and i + 1 < len(sys.argv):
            return os.path.abspath(sys.argv[i + 1])
    # Check environment variable
    env = os.environ.get("LAYOUT_JIG_STATE")
    if env:
        return os.path.abspath(env)
    # Default: state.json in same folder as this script
    return os.path.join(_here, "state.json")


STATE_PATH = _resolve_state_path()

# ── Helper: load, run command, save ───────────────────

def _load_state():
    """Load state from disk with migration."""
    state = cli.load_state(STATE_PATH)
    # Apply same migrations as main()
    if state.get("schema") not in (cli.SCHEMA, "school_jig_2d_v2.2"):
        state = cli.default_state()
    if state.get("schema") == "school_jig_2d_v2.2":
        state["schema"] = cli.SCHEMA
    if "legend" not in state:
        state["legend"] = cli._default_legend()
    if "tactile3d" not in state:
        state["tactile3d"] = cli._default_tactile3d()
    if "auto_export" not in state.get("tactile3d", {}):
        state["tactile3d"]["auto_export"] = False
    if "bambu" not in state:
        state["bambu"] = cli._default_bambu()
    if "tts" not in state:
        state["tts"] = cli._default_tts()
    if "section" not in state:
        state["section"] = cli._default_section()
    return state


def _run(command_str):
    """Load state, tokenize+run one command, save, return message.

    Handles all special sentinels (__DESCRIBE__, __HELP__, etc.)
    except __QUIT__ (not meaningful over MCP) and __UNDO__ (returns
    an error suggesting snapshots instead).
    """
    state = _load_state()
    tokens = cli.tokenize(command_str)
    if not tokens:
        return "No command provided."

    try:
        state, msg = cli.apply_command(state, tokens, state_file=STATE_PATH)
    except Exception as e:
        return f"ERROR: {e}"

    # Handle sentinels
    if msg == "__QUIT__":
        return "Use 'snapshot save <name>' to checkpoint. Quit is not available in MCP mode."
    if msg == "__HELP__":
        return cli.HELP_TEXT
    if msg == "__DESCRIBE__":
        return cli.describe(state)
    if msg == "__LIST_BAYS__":
        return cli.list_bays(state)
    if msg == "__STATUS__":
        try:
            st = os.stat(STATE_PATH)
            import time
            return (f"State: {STATE_PATH}\n"
                    f"Modified: {time.ctime(st.st_mtime)}  "
                    f"Size: {st.st_size} bytes")
        except Exception:
            return f"State: {STATE_PATH}"
    if msg == "__UNDO__":
        return ("ERROR: Undo is not available in MCP mode. "
                "Use 'snapshot save <name>' before changes and "
                "'snapshot load <name>' to restore.")
    if msg == "__PRINT__":
        result = cli.do_print(state, STATE_PATH)
        return result

    # Normal command — save state
    try:
        cli.save_state(STATE_PATH, state)
        # Clear one-shot export flag
        t3 = state.get("tactile3d")
        if t3 and t3.get("_export_once"):
            t3["_export_once"] = False
    except Exception as e:
        return f"ERROR saving state: {e}"

    return msg


# ══════════════════════════════════════════════════════════
# MCP SERVER
# ══════════════════════════════════════════════════════════

mcp = FastMCP("layout-jig")


# ──────────────────────────────────────────────────────────
# EXISTING TOOLS (v1.0) — kept unchanged
# ──────────────────────────────────────────────────────────

@mcp.tool()
def run_command(command: str) -> str:
    """Execute any Layout Jig CLI command as a raw string.

    This is the escape hatch for advanced or rare commands not covered
    by the semantic tools. Prefer the typed tools when available.

    Examples:
        run_command("set bay A rotation 30")
        run_command("block door symbol arc_swing")
        run_command("legend position bottom-left")
        run_command("tactile3d wall_height 12")
        run_command("section x 50")
    """
    return _run(command)


@mcp.tool()
def describe() -> str:
    """Get a full text description of the current model state.

    Returns all settings: site, style, bays, corridors, walls,
    apertures, rooms, legend, tactile3d, TTS, section cut, and totals.
    """
    state = _load_state()
    return cli.describe(state)


@mcp.tool()
def list_bays() -> str:
    """Get a compact table of all bays with key properties.

    Shows: name, grid type, z-order, anchor, rotation, columns,
    walls, apertures, and corridor status.
    """
    state = _load_state()
    return cli.list_bays(state)


@mcp.tool()
def get_state() -> str:
    """Get the raw JSON contents of the state file.

    Returns the complete Canonical Model Artifact (CMA) as a
    formatted JSON string.
    """
    state = _load_state()
    return json.dumps(state, indent=2, ensure_ascii=False)


@mcp.tool()
def get_help() -> str:
    """Get the full command reference for the Layout Jig CLI.

    Lists all available commands with syntax and examples.
    """
    return cli.HELP_TEXT


# ──────────────────────────────────────────────────────────
# NEW READ TOOLS (v2.0) — no state mutation
# ──────────────────────────────────────────────────────────

@mcp.tool()
def list_apertures(bay: str) -> str:
    """List all apertures for a bay with full details.

    Args:
        bay: Bay name (e.g. "A", "B", "C")
    """
    return _run(f"aperture {bay} list")


@mcp.tool()
def list_cells(bay: str) -> str:
    """List all cells in a rectangular bay with names, areas, and hatches.

    Args:
        bay: Bay name (e.g. "A"). Must be a rectangular bay.
    """
    return _run(f"cell {bay} list")


@mcp.tool()
def list_rooms() -> str:
    """List all named rooms with type, label, braille, and hatch info."""
    return _run("room list")


@mcp.tool()
def list_snapshots() -> str:
    """List all named snapshots with size and modification time."""
    return _run("snapshot list")


# ──────────────────────────────────────────────────────────
# BAY CONFIGURATION (v2.0)
# ──────────────────────────────────────────────────────────

@mcp.tool()
def set_bay(bay: str, field: str, value: str) -> str:
    """Set a bay property.

    This is the main tool for configuring bay parameters. Pass the
    field name and value as strings; the server maps to the correct
    CLI command.

    Args:
        bay: Bay name (e.g. "A", "B")
        field: Property to set. One of:
            - "origin" — anchor point, value = "x y" (e.g. "18 8")
            - "rotation" — degrees, value = number (e.g. "30")
            - "bays" — grid dimensions, value = "nx ny" (e.g. "6 3")
            - "spacing" — uniform spacing, value = "sx sy" (e.g. "24 24")
            - "spacing_x" — irregular x spacing, value = "s1 s2 ..." (one per bay span)
            - "spacing_y" — irregular y spacing, value = "s1 s2 ..." (one per bay span)
            - "grid_type" — "rectangular" or "radial"
            - "z_order" — integer draw order (e.g. "0", "1", "2")
            - "void_center" — void center point, value = "x y"
            - "void_size" — void dimensions, value = "w h"
            - "void_shape" — "rectangle" or "circle"
            - "label" — display label text
            - "braille" — braille label text
            - "rings" — radial grid ring count
            - "ring_spacing" — radial grid ring spacing in feet
            - "arms" — radial grid arm count
            - "arc_deg" — radial arc sweep in degrees
            - "arc_start_deg" — radial arc start angle in degrees
        value: The value to set (as a string, space-separated for multi-value fields)
    """
    return _run(f"set bay {bay} {field} {value}")


# ──────────────────────────────────────────────────────────
# WALLS AND CORRIDORS (v2.0)
# ──────────────────────────────────────────────────────────

@mcp.tool()
def set_walls(bay: str, enabled: bool, thickness: float = None) -> str:
    """Toggle walls on/off for a bay, optionally setting thickness.

    Args:
        bay: Bay name (e.g. "A")
        enabled: True to turn walls on, False to turn off
        thickness: Wall thickness in feet (optional, e.g. 0.5 = 6 inches).
                   Only applied when enabled=True.
    """
    if enabled:
        result = _run(f"wall {bay} on")
        if thickness is not None:
            result2 = _run(f"wall {bay} thickness {thickness}")
            result = result + "\n" + result2
        return result
    else:
        return _run(f"wall {bay} off")


@mcp.tool()
def set_corridor(
    bay: str,
    enabled: bool,
    field: str = None,
    value: str = None,
) -> str:
    """Toggle corridor on/off for a bay, optionally configuring a property.

    Args:
        bay: Bay name (e.g. "A")
        enabled: True to turn corridor on, False to turn off
        field: Optional property to set. One of:
            - "axis" — "x" (east-west) or "y" (north-south)
            - "position" — gridline index (integer)
            - "width" — corridor width in feet
            - "loading" — "single" or "double"
            - "hatch" — hatch pattern name or "none"
            - "hatch_scale" — hatch scale factor
        value: Value for the field (required if field is provided)
    """
    if enabled:
        result = _run(f"corridor {bay} on")
        if field is not None and value is not None:
            result2 = _run(f"corridor {bay} {field} {value}")
            result = result + "\n" + result2
        return result
    else:
        return _run(f"corridor {bay} off")


# ──────────────────────────────────────────────────────────
# APERTURES (v2.0)
# ──────────────────────────────────────────────────────────

@mcp.tool()
def add_aperture(
    bay: str,
    id: str,
    type: str,
    axis: str,
    gridline: int,
    corner: float,
    width: float,
    height: float,
) -> str:
    """Add a door, window, or portal to a bay's walls.

    Walls must be enabled on the bay first (use set_walls).

    Args:
        bay: Bay name (e.g. "A", "B")
        id: Unique aperture ID (e.g. "d1", "w2", "p1")
        type: "door", "window", or "portal"
        axis: "x" or "y" — which gridline axis the aperture is on
        gridline: Gridline index (0-based)
        corner: Distance from gridline intersection in feet
        width: Aperture width in feet
        height: Aperture height in feet
    """
    cmd = f"aperture {bay} add {id} {type} {axis} {gridline} {corner} {width} {height}"
    return _run(cmd)


@mcp.tool()
def remove_aperture(bay: str, id: str) -> str:
    """Remove an aperture from a bay.

    Args:
        bay: Bay name (e.g. "A")
        id: Aperture ID to remove (e.g. "d1", "w2")
    """
    return _run(f"aperture {bay} remove {id}")


@mcp.tool()
def modify_aperture(bay: str, id: str, field: str, value: str) -> str:
    """Modify a property of an existing aperture.

    Args:
        bay: Bay name (e.g. "A")
        id: Aperture ID (e.g. "d1", "w2")
        field: Property to change. One of:
            - "type" — "door", "window", or "portal"
            - "axis" — "x" or "y"
            - "gridline" — gridline index (0-based integer)
            - "corner" — distance from intersection in feet
            - "width" — aperture width in feet
            - "height" — aperture height in feet
            - "hinge" — "start" or "end" (doors only)
            - "swing" — "positive" or "negative" (doors only)
        value: New value for the field
    """
    return _run(f"aperture {bay} set {id} {field} {value}")


# ──────────────────────────────────────────────────────────
# CELLS AND ROOMS (v2.0)
# ──────────────────────────────────────────────────────────

@mcp.tool()
def set_cell(
    bay: str,
    col: int,
    row: int,
    field: str,
    value: str,
) -> str:
    """Set a property on a cell in a rectangular bay's grid.

    Cells subdivide bays into named rooms with areas and hatch patterns.

    Args:
        bay: Bay name (e.g. "A")
        col: Column index (0-based, left to right)
        row: Row index (0-based, bottom to top)
        field: Property to set. One of:
            - "name" — room name (cells with the same name form a room)
            - "label" — display label (defaults to name if blank)
            - "braille" — braille label text
            - "hatch" — hatch pattern (e.g. "diagonal", "crosshatch", "dots", or "none")
            - "hatch_scale" — hatch scale factor
            - "hatch_rotation" — hatch rotation in degrees
        value: Value to set
    """
    # Quote the value if it contains spaces
    if " " in value:
        value = f'"{value}"'
    return _run(f"cell {bay} {col},{row} {field} {value}")


@mcp.tool()
def auto_corridor_cells(bay: str) -> str:
    """Auto-name cells in the corridor zone as "Corridor".

    Detects which cells overlap the corridor and marks them.
    The corridor must be enabled on the bay first.

    Args:
        bay: Bay name (e.g. "A")
    """
    return _run(f"cell {bay} auto_corridor")


# ──────────────────────────────────────────────────────────
# SITE AND STYLE (v2.0)
# ──────────────────────────────────────────────────────────

@mcp.tool()
def set_site(field: str, value: float) -> str:
    """Set site dimensions.

    Args:
        field: "width" or "height"
        value: Dimension in feet (must be > 0)
    """
    return _run(f"set site {field} {value}")


@mcp.tool()
def set_style(field: str, value: str) -> str:
    """Set a drawing style parameter.

    Args:
        field: Style property to set. One of:
            - "heavy" — heavy lineweight in mm (columns/structure)
            - "light" — light lineweight in mm (grid lines)
            - "corridor" — corridor lineweight in mm
            - "wall" — wall lineweight in mm
            - "text_height" — label text height in ft
            - "braille_height" — braille text height in ft
            - "dash_len" — corridor dash length in ft
            - "gap_len" — corridor gap length in ft
            - "bg_pad" — background padding in ft
            - "label_offset" — label offset distance in ft
            - "arc_segments" — number of segments for arc approximation
        value: Numeric value
    """
    return _run(f"set style {field} {value}")


# ──────────────────────────────────────────────────────────
# SNAPSHOTS (v2.0) — safety checkpoints
# ──────────────────────────────────────────────────────────

@mcp.tool()
def save_snapshot(name: str) -> str:
    """Save the current state as a named snapshot.

    Use this before making significant changes so you can restore later.

    Args:
        name: Snapshot name (alphanumeric, hyphens, underscores)
    """
    return _run(f"snapshot save {name}")


@mcp.tool()
def load_snapshot(name: str) -> str:
    """Restore a previously saved named snapshot.

    This replaces the current state with the snapshot contents.

    Args:
        name: Snapshot name to restore
    """
    return _run(f"snapshot load {name}")


# ══════════════════════════════════════════════════════════
# MCP RESOURCES (v2.0)
# ══════════════════════════════════════════════════════════

@mcp.resource("state://current")
def resource_current_state() -> str:
    """The current design state as formatted JSON.

    Read this resource to get the full Canonical Model Artifact (CMA)
    without calling a tool.
    """
    state = _load_state()
    return json.dumps(state, indent=2, ensure_ascii=False)


@mcp.resource("snapshots://list")
def resource_snapshot_list() -> str:
    """List of available named snapshots."""
    return _run("snapshot list")


@mcp.resource("help://commands")
def resource_help() -> str:
    """Full CLI command reference."""
    return cli.HELP_TEXT


# ══════════════════════════════════════════════════════════
# MCP PROMPTS (v2.0)
# ══════════════════════════════════════════════════════════

@mcp.prompt()
def design_review() -> str:
    """Review the current architectural plan and suggest improvements.

    Loads the full model description and asks for a design critique
    covering spatial organization, circulation, and accessibility.
    """
    state = _load_state()
    desc = cli.describe(state)
    return (
        f"Here is the current architectural plan state:\n\n"
        f"{desc}\n\n"
        f"Please review this design and provide feedback on:\n"
        f"1. Spatial organization and bay layout\n"
        f"2. Circulation paths (corridors, aperture placement)\n"
        f"3. Room naming and hatch differentiation for tactile readability\n"
        f"4. Any potential issues or improvements"
    )


@mcp.prompt()
def aperture_audit() -> str:
    """Audit all apertures across all bays for consistency.

    Checks for missing doors in corridors, window placement,
    and portal sizing.
    """
    state = _load_state()
    lines = ["Aperture audit for all bays:\n"]
    for name in sorted(state.get("bays", {})):
        bay = state["bays"][name]
        aps = bay.get("apertures", [])
        walls = bay.get("walls", {})
        cor = bay.get("corridor", {})
        lines.append(f"Bay {name}: walls={'ON' if walls.get('enabled') else 'OFF'}, "
                     f"corridor={'ON' if cor.get('enabled') else 'OFF'}, "
                     f"{len(aps)} apertures")
        for a in aps:
            lines.append(f"  {a['id']}: {a['type']} on {a['axis']}-{a['gridline']} "
                         f"at corner={a['corner']} width={a['width']} height={a['height']}")
    lines.append("\nPlease review these apertures for:\n"
                 "1. Every corridor bay should have doors connecting to adjacent spaces\n"
                 "2. Window placement for natural light\n"
                 "3. Portal sizing for circulation flow\n"
                 "4. Consistent heights across similar aperture types")
    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────

if __name__ == "__main__":
    _real_print(f"Layout Jig MCP Server v2.0 starting...", file=sys.stderr)
    _real_print(f"State file: {STATE_PATH}", file=sys.stderr)
    _real_print(f"Tools: {len(mcp._tool_manager._tools)} registered", file=sys.stderr)
    mcp.run()
