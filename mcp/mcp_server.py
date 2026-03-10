# -*- coding: utf-8 -*-
"""
PLAN LAYOUT JIG — MCP Server  v3.5
====================================
Model Context Protocol wrapper around the Layout Jig CLI, plus:
  - Auditor: spatial validation, ADA checks, rich descriptions
  - Skill manager: save, list, and replay reusable command sequences (skills)
  - Template manager: list, show, and load startup state generators (templates)
  - Rhino client: optional TCP queries to the Rhino watcher
  - Controller extension: add new command handlers at runtime
  - State introspection: read/write individual JSON fields by path
  - Bay management: create, remove, and clone bays
  - Controller introspection: list commands, read handler source code
  - State comparison: diff snapshots, validate JSON structure
  - Swell-print: render state.json and convert images to PIAF tactile graphics
  - Style profiles: PIAF style system for tactile rendering control

v3.5 changes (from v3.4):
  - 5 style tools: style_use, style_show, style_set, style_save, style_list,
    style_test
  - 4 view tools: view_plan, view_section, view_axon, view_elevation
  Total: 65 tools (was 56)

v3.4 changes (from v3.3):
  - 3 template tools: template_list, template_show, template_load
  - 1 new resource: templates://list
  Total: 56 tools (was 53)

v3.3 changes (from v3.2):
  - 4 swell-print tools: render_tactile, convert_to_tactile,
    check_tactile_density, list_tactile_presets
  Total: 53 tools (was 49)

v3.2 changes (from v3.1):
  - 3 script generation tools: generate_script, list_scripts, show_script
  Total: 49 tools (was 46)

v3.1 changes (from v3.0):
  - 3 state introspection tools: get_field, set_field, list_fields
  - 3 bay management tools: add_bay, remove_bay, clone_bay
  - 2 controller introspection tools: list_commands, show_command_source
  - 2 state comparison tools: diff_snapshot, validate_state
  Total: 46 tools (was 35)

v3.0 changes (from v2.0):
  - 5 audit tools: audit_model, audit_bay, describe_bay,
    describe_circulation, measure
  - 4 skill tools: skill_list, skill_show, skill_run, skill_save
  - 3 rhino tools: rhino_status, rhino_query, rhino_run_script
  - 2 extension tools: extend_controller, list_extensions
  - 2 new resources: skills://list, extensions://list
  - 2 new prompts: accessibility_audit, skill_builder
  - All 21 v2.0 tools preserved unchanged

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
      "args": ["mcp/mcp_server.py", "--state", "controller/state.json"]
    }
  }
}
"""

import ast
import builtins
import importlib
import json
import os
import re as _re
import sys

# ── Redirect print to stderr (stdout is JSON-RPC) ──────
_real_print = builtins.print

def _stderr_print(*args, **kwargs):
    kwargs.setdefault("file", sys.stderr)
    _real_print(*args, **kwargs)

builtins.print = _stderr_print

# ── Import controller_cli from controller/ directory ───
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
_controller = os.path.join(_root, "controller")
if _controller not in sys.path:
    sys.path.insert(0, _controller)

_tools_rhino = os.path.join(_root, "tools", "rhino")
if _tools_rhino not in sys.path:
    sys.path.insert(0, _tools_rhino)

import controller_cli as cli
import braille

# ── Import engines (lazy-safe: all stdlib-only) ────────
import auditor
import skill_manager
import template_manager
import rhino_client

# ── Import swell-print tools (optional: requires Pillow, reportlab) ──
_tools_swell = os.path.join(_root, "tools", "swell-print")
if os.path.isdir(_tools_swell) and _tools_swell not in sys.path:
    sys.path.insert(0, _tools_swell)

try:
    import state_renderer
    import image_converter
    _swell_available = True
except ImportError:
    _swell_available = False

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
    for i, arg in enumerate(sys.argv):
        if arg == "--state" and i + 1 < len(sys.argv):
            return os.path.abspath(sys.argv[i + 1])
    env = os.environ.get("LAYOUT_JIG_STATE")
    if env:
        return os.path.abspath(env)
    return os.path.join(_controller, "state.json")


STATE_PATH = _resolve_state_path()

# ── Helper: load, run command, save ───────────────────

def _load_state():
    """Load state from disk with migration."""
    state = cli.load_state(STATE_PATH)
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
        t3 = state.get("tactile3d")
        if t3 and t3.get("_export_once"):
            t3["_export_once"] = False
    except Exception as e:
        return f"ERROR saving state: {e}"

    return msg


# ── Helper: resolve dot-notation path in state dict ────

def _resolve_path(state, path):
    """Resolve a dot-notation path against the state dict.

    Examples:
        "site.width" -> state["site"]["width"]
        "bays.A.origin" -> state["bays"]["A"]["origin"]
        "bays.A.apertures.0.width" -> state["bays"]["A"]["apertures"][0]["width"]

    Returns (parent_container, key, value).
    Raises ValueError if the path is invalid.
    """
    parts = path.split(".")
    current = state
    for i, part in enumerate(parts[:-1]):
        if isinstance(current, dict):
            if part not in current:
                avail = ", ".join(sorted(current.keys()))
                raise ValueError(
                    f"Key '{part}' not found at '{'.'.join(parts[:i+1])}'. "
                    f"Available: {avail}")
            current = current[part]
        elif isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx]
            except ValueError:
                raise ValueError(
                    f"Expected integer index, got '{part}' "
                    f"at '{'.'.join(parts[:i+1])}'")
            except IndexError:
                raise ValueError(
                    f"Index {part} out of range (list has {len(current)} items) "
                    f"at '{'.'.join(parts[:i+1])}'")
        else:
            raise ValueError(
                f"Cannot traverse into {type(current).__name__} "
                f"at '{'.'.join(parts[:i+1])}'")
    last = parts[-1]
    if isinstance(current, dict):
        if last not in current:
            avail = ", ".join(sorted(current.keys()))
            raise ValueError(
                f"Key '{last}' not found. Available: {avail}")
        return current, last, current[last]
    elif isinstance(current, list):
        try:
            idx = int(last)
            return current, idx, current[idx]
        except ValueError:
            raise ValueError(f"Expected integer index, got '{last}'")
        except IndexError:
            raise ValueError(
                f"Index {last} out of range (list has {len(current)} items)")
    else:
        raise ValueError(
            f"Cannot access '{last}' on {type(current).__name__}")


def _diff_dicts(prefix, current, snapshot, diffs, max_depth=5):
    """Recursively compare two dicts/values and collect differences."""
    if max_depth <= 0:
        if current != snapshot:
            diffs.append((prefix or "(root)", current, snapshot))
        return

    if isinstance(current, dict) and isinstance(snapshot, dict):
        all_keys = set(current.keys()) | set(snapshot.keys())
        for key in sorted(all_keys):
            path = f"{prefix}.{key}" if prefix else key
            if key not in current:
                diffs.append((path, "(missing)", snapshot[key]))
            elif key not in snapshot:
                diffs.append((path, current[key], "(missing)"))
            else:
                _diff_dicts(path, current[key], snapshot[key],
                            diffs, max_depth - 1)
    elif isinstance(current, list) and isinstance(snapshot, list):
        if current != snapshot:
            if len(current) == len(snapshot):
                for i in range(len(current)):
                    path = f"{prefix}[{i}]"
                    _diff_dicts(path, current[i], snapshot[i],
                                diffs, max_depth - 1)
            else:
                diffs.append((prefix, current, snapshot))
    else:
        if current != snapshot:
            diffs.append((prefix, current, snapshot))


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
# READ TOOLS (v2.0) — no state mutation
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
            - "origin" -- anchor point, value = "x y" (e.g. "18 8")
            - "rotation" -- degrees, value = number (e.g. "30")
            - "bays" -- grid dimensions, value = "nx ny" (e.g. "6 3")
            - "spacing" -- uniform spacing, value = "sx sy" (e.g. "24 24")
            - "spacing_x" -- irregular x spacing, value = "s1 s2 ..."
            - "spacing_y" -- irregular y spacing, value = "s1 s2 ..."
            - "grid_type" -- "rectangular" or "radial"
            - "z_order" -- integer draw order (e.g. "0", "1", "2")
            - "void_center" -- void center point, value = "x y"
            - "void_size" -- void dimensions, value = "w h"
            - "void_shape" -- "rectangle" or "circle"
            - "label" -- display label text
            - "braille" -- braille label text
            - "rings" -- radial grid ring count
            - "ring_spacing" -- radial grid ring spacing in feet
            - "arms" -- radial grid arm count
            - "arc_deg" -- radial arc sweep in degrees
            - "arc_start_deg" -- radial arc start angle in degrees
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
            - "axis" -- "x" (east-west) or "y" (north-south)
            - "position" -- gridline index (integer)
            - "width" -- corridor width in feet
            - "loading" -- "single" or "double"
            - "hatch" -- hatch pattern name or "none"
            - "hatch_scale" -- hatch scale factor
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
        axis: "x" or "y" -- which gridline axis the aperture is on
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
            - "type" -- "door", "window", or "portal"
            - "axis" -- "x" or "y"
            - "gridline" -- gridline index (0-based integer)
            - "corner" -- distance from intersection in feet
            - "width" -- aperture width in feet
            - "height" -- aperture height in feet
            - "hinge" -- "start" or "end" (doors only)
            - "swing" -- "positive" or "negative" (doors only)
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
            - "name" -- room name (cells with the same name form a room)
            - "label" -- display label (defaults to name if blank)
            - "braille" -- braille label text
            - "hatch" -- hatch pattern (e.g. "diagonal", "crosshatch", "dots", or "none")
            - "hatch_scale" -- hatch scale factor
            - "hatch_rotation" -- hatch rotation in degrees
        value: Value to set
    """
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
            - "heavy" -- heavy lineweight in mm (columns/structure)
            - "light" -- light lineweight in mm (grid lines)
            - "corridor" -- corridor lineweight in mm
            - "wall" -- wall lineweight in mm
            - "text_height" -- label text height in ft
            - "braille_height" -- braille text height in ft
            - "dash_len" -- corridor dash length in ft
            - "gap_len" -- corridor gap length in ft
            - "bg_pad" -- background padding in ft
            - "label_offset" -- label offset distance in ft
            - "arc_segments" -- number of segments for arc approximation
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
# NEW v3.0 TOOLS — AUDIT ENGINE
# ══════════════════════════════════════════════════════════

@mcp.tool()
def audit_model() -> str:
    """Run all validation checks on the current model.

    Checks for: overlapping bays, bays outside site, aperture errors,
    corridor sizing, ADA compliance (door widths, corridor widths),
    orphan room references, and missing labels.

    Returns a numbered list of issues, or a clean bill of health.
    Works offline -- reads state.json only, no Rhino needed.
    """
    state = _load_state()
    issues = auditor.audit_model(state)
    return auditor.format_audit(issues)


@mcp.tool()
def audit_bay(bay: str) -> str:
    """Deep audit of a single bay with all properties and issues.

    Reports: grid type, dimensions, area, column count, walls, corridor,
    apertures, void, labels, and any validation issues specific to this bay.

    Args:
        bay: Bay name (e.g. "A", "B")
    """
    state = _load_state()
    return auditor.audit_bay(state, bay)


@mcp.tool()
def describe_bay(bay: str) -> str:
    """Rich narrative description of a single bay for screen readers.

    More detailed than the main describe() output. Includes spatial
    relationships to other bays, accessibility observations, and
    a natural-language summary.

    Args:
        bay: Bay name (e.g. "A", "B")
    """
    state = _load_state()
    return auditor.describe_bay(state, bay)


@mcp.tool()
def describe_circulation() -> str:
    """Describe corridor connectivity across all bays.

    Reports which bays have corridors, their alignment, whether doors
    or portals connect them, and identifies dead ends or isolated bays.
    Works offline -- reads state.json only, no Rhino needed.
    """
    state = _load_state()
    return auditor.describe_circulation(state)


@mcp.tool()
def measure(from_location: str, to_location: str) -> str:
    """Measure distance between two semantic locations.

    Calculates straight-line, horizontal, and vertical distances.

    Args:
        from_location: Starting point. Format examples:
            - "bay A origin" -- origin point of bay A
            - "bay A center" -- center of bay A footprint
            - "bay A void" -- center of bay A void
            - "site origin" -- site origin point
            - "site center" -- center of site
        to_location: Ending point (same format as from_location)
    """
    state = _load_state()
    return auditor.measure(state, from_location, to_location)


# ══════════════════════════════════════════════════════════
# NEW v3.0 TOOLS — SKILL ENGINE
# ══════════════════════════════════════════════════════════

@mcp.tool()
def skill_list() -> str:
    """List all saved skills with names, descriptions, and command counts.

    Skills are reusable command sequences stored as JSON files in the
    skills/ folder. They can be replayed with different parameters.
    """
    skills = skill_manager.list_skills()
    return skill_manager.format_skill_list(skills)


@mcp.tool()
def skill_show(name: str) -> str:
    """Show a skill's full details: description, parameters, and commands.

    Args:
        name: Skill name (e.g. "add-double-loaded-corridor")
    """
    try:
        skill = skill_manager.load_skill(name)
        return skill_manager.format_skill_detail(skill)
    except ValueError as e:
        return f"ERROR: {e}"


@mcp.tool()
def skill_run(name: str, overrides: str = "") -> str:
    """Execute a saved skill, substituting parameters.

    Runs each command in the skill's sequence through the controller.
    Stops on first error.

    Args:
        name: Skill name to execute
        overrides: Parameter overrides as "key=value key2=value2" string.
                   Overrides the skill's default parameter values.
                   Example: "bay=B width=10"
    """
    # Parse overrides string into dict
    override_dict = {}
    if overrides.strip():
        for pair in overrides.strip().split():
            if "=" in pair:
                k, v = pair.split("=", 1)
                override_dict[k] = v

    return skill_manager.run_skill(name, override_dict, _run)


@mcp.tool()
def skill_save(name: str, description: str, commands: str,
               params: str = "") -> str:
    """Save a new skill (reusable command sequence).

    Skills are macros -- named sequences of CLI commands that can be
    saved once and replayed with different parameters. Use {param_name}
    placeholders in commands for variable values.

    Args:
        name: Skill name in kebab-case (e.g. "add-corridor-with-doors")
        description: What this skill does (one sentence)
        commands: Newline-separated CLI commands.
            Example: "corridor {bay} on\\ncorridor {bay} width {width}"
        params: Optional parameter definitions as "name=default" pairs,
            space-separated. Example: "bay=A width=8"
            If omitted, params are auto-detected from {placeholders}.
    """
    cmd_list = [c.strip() for c in commands.split("\n") if c.strip()]
    if not cmd_list:
        return "ERROR: No commands provided. Separate commands with newlines."

    # Parse params string
    param_dict = None
    if params.strip():
        param_dict = {}
        for pair in params.strip().split():
            if "=" in pair:
                k, v = pair.split("=", 1)
                param_dict[k] = {"description": f"Value for {k}", "default": v}

    return skill_manager.save_skill(name, description, cmd_list, param_dict)


# ══════════════════════════════════════════════════════════
# NEW v3.4 TOOLS — TEMPLATE ENGINE
# ══════════════════════════════════════════════════════════

@mcp.tool()
def template_list() -> str:
    """List all available templates with names, descriptions, and param counts.

    Templates are startup state generators that produce complete state.json
    configurations from parameters. Different from skills: templates replace
    state, skills replay commands on existing state.
    """
    templates = template_manager.list_templates()
    return template_manager.format_template_list(templates)


@mcp.tool()
def template_show(name: str) -> str:
    """Show a template's full details: description, parameters, and defaults.

    Args:
        name: Template name (e.g. "sonsbeek-pavilion", "aggregate-ranch")
    """
    try:
        return template_manager.show_template(name)
    except ValueError as e:
        return f"ERROR: {e}"


@mcp.tool()
def template_load(name: str, overrides: str = "") -> str:
    """Load a template, replacing the current state with a new configuration.

    Generates a complete state from the template's parameters, saves it,
    and returns a summary. The previous state is lost (use snapshot save
    first if you want to preserve it).

    Args:
        name: Template name to load (e.g. "sonsbeek-pavilion")
        overrides: Parameter overrides as "key=value key2=value2" string.
                   For complex params (lists/dicts), use JSON:
                   'rooms=[{"name":"Hall","width":30}]'
    """
    import json as _json

    # Parse overrides string into dict
    override_dict = {}
    if overrides.strip():
        for pair in overrides.strip().split():
            if "=" in pair:
                k, v = pair.split("=", 1)
                if v.startswith(("[", "{")):
                    try:
                        v = _json.loads(v)
                    except _json.JSONDecodeError:
                        return f"ERROR: Invalid JSON for parameter '{k}': {v}"
                else:
                    try:
                        v = float(v)
                        if v == int(v):
                            v = int(v)
                    except ValueError:
                        pass
                override_dict[k] = v

    try:
        new_state = template_manager.generate(name, override_dict)
    except ValueError as e:
        return f"ERROR: {e}"

    cli.save_state(STATE_PATH, new_state)
    bay_count = len(new_state.get("bays", {}))
    bay_names = ", ".join(sorted(new_state.get("bays", {}).keys()))
    return (
        f"OK: Loaded template '{name}' with {bay_count} bay(s): {bay_names}. "
        f"State saved.\nREADY:"
    )


# ══════════════════════════════════════════════════════════
# NEW v3.0 TOOLS — RHINO BRIDGE (optional)
# ══════════════════════════════════════════════════════════

@mcp.tool()
def rhino_status() -> str:
    """Check if Rhino is connected via the watcher's TCP listener.

    Returns connection status, layer count, object count, and last
    rebuild time if connected. Returns OFFLINE message if not.
    Never fails -- offline mode is a first-class result.
    """
    bridge = rhino_client.get_bridge()
    return bridge.status()


@mcp.tool()
def rhino_query(query_type: str, layer: str = "") -> str:
    """Ask Rhino a read-only question via the watcher's TCP listener.

    Works only when Rhino is running with the watcher active.
    Returns OFFLINE message if Rhino is not available.

    Args:
        query_type: Type of query. One of:
            - "status" -- layer count, object count, last rebuild
            - "layer_stats" -- per-layer object counts
            - "bounding_box" -- world-space bounding box of all geometry
            - "object_count" -- total or per-layer object count
        layer: Optional layer name for "object_count" query
            (e.g. "JIG_COLUMNS", "JIG_WALLS"). Omit for total count.
    """
    bridge = rhino_client.get_bridge()
    params = {}
    if layer:
        params["layer"] = layer
    return bridge.query(query_type, params if params else None)


@mcp.tool()
def rhino_run_script(code: str) -> str:
    """Execute a read-only Python snippet inside Rhino.

    The code runs in the watcher's IronPython 2.7 context with access
    to rhinoscriptsyntax. Use for queries like measuring geometry or
    counting objects. The watcher blocks geometry-modifying calls.

    Returns OFFLINE message if Rhino is not available.

    IMPORTANT: Use .format() syntax, NOT f-strings (IronPython 2.7).

    Args:
        code: Python code to execute. Must use print() for output.
            Example: "import rhinoscriptsyntax as rs\\nprint(rs.ObjectsByLayer('JIG_COLUMNS'))"
    """
    bridge = rhino_client.get_bridge()
    return bridge.run_script(code)


@mcp.tool()
def setup_rhino(rhino_path: str = "") -> str:
    """Launch Rhino with the watcher auto-loaded and units set to Feet.

    Automates the manual startup workflow: opens Rhino, runs the watcher
    script, and sets document units to Feet. Polls for connection on
    port 1998 for up to 30 seconds.

    If Rhino is already connected, returns the current status instead
    of launching a new instance.

    Args:
        rhino_path: Optional path to Rhino.exe. If omitted, searches
            standard install locations (Program Files).
    """
    # Check if already connected
    bridge = rhino_client.get_bridge()
    if bridge.is_connected():
        return bridge.status()

    # Delegate to the CLI setup command
    tokens = ["setup", "rhino"]
    if rhino_path:
        tokens.extend(["--path", rhino_path])
    state = _load()
    _, msg = cli.cmd_setup(state, tokens, STATE_PATH)
    return msg


# ══════════════════════════════════════════════════════════
# NEW v3.0 TOOLS — CONTROLLER EXTENSION
# ══════════════════════════════════════════════════════════

@mcp.tool()
def extend_controller(function_name: str, code: str) -> str:
    """Add a new command handler function to the controller CLI.

    This extends the Layout Jig with new commands at runtime. The
    function is appended to controller_cli.py and registered in the
    command dispatch chain.

    The function MUST follow this signature:
        def cmd_something(state, tokens):
            # ... process tokens, mutate state ...
            return state, "OK: message describing what changed."

    Args:
        function_name: Function name (e.g. "cmd_canopy"). Must start
            with "cmd_".
        code: Complete Python function source code. Must define exactly
            one function matching function_name.
    """
    # Validate function name
    if not function_name.startswith("cmd_"):
        return "ERROR: Function name must start with 'cmd_' (e.g. 'cmd_canopy')."

    cmd_word = function_name[4:]  # strip "cmd_" prefix
    if not cmd_word.isalpha():
        return "ERROR: Command word must be alphabetic (e.g. 'cmd_canopy' -> 'canopy')."

    # Validate code parses
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"ERROR: Syntax error in code: {e}"

    # Must contain exactly one function definition with the right name
    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    if len(funcs) != 1:
        return (f"ERROR: Code must define exactly one function. "
                f"Found {len(funcs)}.")
    if funcs[0].name != function_name:
        return (f"ERROR: Function name mismatch. Expected '{function_name}', "
                f"found '{funcs[0].name}'.")

    # Check signature has (state, tokens) args
    args = funcs[0].args
    arg_names = [a.arg for a in args.args]
    if len(arg_names) < 2 or arg_names[0] != "state" or arg_names[1] != "tokens":
        return "ERROR: Function must accept (state, tokens) as first two args."

    # Check command word doesn't conflict with existing commands
    existing_commands = [
        "corridor", "wall", "aperture", "room", "cell", "block",
        "hatch", "legend", "tactile3d", "bambu", "tts", "section",
        "history", "snapshot", "set", "quit", "q", "exit", "help",
        "h", "describe", "d", "list", "l", "undo", "status", "print", "p"
    ]
    if cmd_word in existing_commands:
        return f"ERROR: Command '{cmd_word}' already exists. Choose a different name."

    # Read current controller file
    cli_path = os.path.join(_controller, "controller_cli.py")
    try:
        with open(cli_path, "r", encoding="utf-8") as f:
            cli_source = f.read()
    except OSError as e:
        return f"ERROR: Cannot read controller_cli.py: {e}"

    # Check if function already exists
    if f"def {function_name}(" in cli_source:
        return f"ERROR: Function '{function_name}' already exists in controller_cli.py."

    # Find the dispatch insertion point (before "if cmd != \"set\":")
    dispatch_marker = 'if cmd != "set":'
    if dispatch_marker not in cli_source:
        return "ERROR: Cannot find dispatch insertion point in controller_cli.py."

    # Build new dispatch line
    dispatch_line = f'    if cmd == "{cmd_word}": return {function_name}(state, tokens)\n'

    # Insert dispatch line before the "set" fallthrough
    cli_source = cli_source.replace(
        f"    {dispatch_marker}",
        f"{dispatch_line}    {dispatch_marker}"
    )

    # Append function before apply_command
    apply_marker = "def apply_command(state, tokens, state_file=None):"
    if apply_marker not in cli_source:
        return "ERROR: Cannot find apply_command in controller_cli.py."

    cli_source = cli_source.replace(
        apply_marker,
        f"\n# ── Extension: {function_name} ──\n{code}\n\n{apply_marker}"
    )

    # Atomic write
    try:
        tmp = cli_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(cli_source)
        os.replace(tmp, cli_path)
    except OSError as e:
        return f"ERROR: Cannot write controller_cli.py: {e}"

    # Reload the controller module
    try:
        importlib.reload(cli)
    except Exception as e:
        return f"WARNING: Extension written but module reload failed: {e}. Restart MCP server."

    # Track extension in state
    state = _load_state()
    meta = state.setdefault("meta", {})
    extensions = meta.setdefault("extensions", [])
    extensions.append({
        "function": function_name,
        "command": cmd_word,
        "added": cli._now(),
    })
    try:
        cli.save_state(STATE_PATH, state)
    except Exception:
        pass  # non-fatal

    return (f"OK: Added command '{cmd_word}' via {function_name}(). "
            f"Controller reloaded. Test with: run_command(\"{cmd_word} ...\")")


@mcp.tool()
def list_extensions() -> str:
    """List all command handler extensions added via extend_controller.

    Shows function name, command word, and when it was added.
    """
    state = _load_state()
    extensions = state.get("meta", {}).get("extensions", [])
    if not extensions:
        return "OK: No extensions added yet.\nREADY:"

    lines = [f"OK: {len(extensions)} extension(s):", ""]
    for i, ext in enumerate(extensions, 1):
        lines.append(
            f"  {i}. {ext['command']} -> {ext['function']}()  "
            f"(added {ext.get('added', '?')})")
    lines.append("READY:")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
# NEW v3.1 TOOLS — STATE INTROSPECTION
# ══════════════════════════════════════════════════════════

@mcp.tool()
def get_field(path: str) -> str:
    """Read a specific field from state.json by dot-notation path.

    Use this to read individual values without loading the entire state.
    Supports nested paths and list indices.

    Args:
        path: Dot-separated path. Examples:
            - "site.width" -> site width in feet
            - "bays.A.origin" -> [x, y] anchor point
            - "bays.A.rotation_deg" -> rotation in degrees
            - "bays.A.corridor.width" -> corridor width
            - "bays.A.corridor.enabled" -> whether corridor is on
            - "bays.A.walls.thickness" -> wall thickness
            - "bays.A.apertures.0.width" -> first aperture width
            - "style.heavy_lineweight_mm" -> heavy lineweight
            - "legend.enabled" -> whether legend is on
            - "meta.notes" -> project notes
            - "print.dpi" -> print resolution
            - "bambu.printer_ip" -> Bambu printer IP
    """
    state = _load_state()
    try:
        _, key, value = _resolve_path(state, path)
        return f"OK: {path} = {json.dumps(value, ensure_ascii=False)}"
    except ValueError as e:
        return f"ERROR: {e}"


@mcp.tool()
def set_field(path: str, value: str) -> str:
    """Write a specific field in state.json by dot-notation path.

    This writes directly to the JSON, bypassing CLI validation.
    Use for fields that have no CLI command (meta.notes, blocks.*,
    print.dpi, bambu.*, etc.) or for power-user edits.

    The value is parsed as JSON first. If that fails, it is stored
    as a plain string.

    Args:
        path: Dot-separated path (same format as get_field)
        value: JSON value to set. Examples:
            - "250" for a number
            - "\"new label\"" for a string (with escaped quotes)
            - "[50.0, 50.0]" for a list
            - "true" or "false" for booleans
            - "null" for null
    """
    state = _load_state()
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        parsed = value

    try:
        parent, key, old_value = _resolve_path(state, path)
        parent[key] = parsed
        cli.save_state(STATE_PATH, state)
        return (f"OK: {path} = {json.dumps(parsed, ensure_ascii=False)}. "
                f"Was {json.dumps(old_value, ensure_ascii=False)}.")
    except ValueError as e:
        return f"ERROR: {e}"


@mcp.tool()
def list_fields(path: str = "") -> str:
    """List all keys at a given path in state.json.

    Use this to explore the state structure without reading the
    entire JSON. With no path, lists top-level sections. With a
    path, lists fields within that section.

    Args:
        path: Dot-separated path (optional). Examples:
            - "" (empty) -> top-level: schema, meta, site, bays, ...
            - "bays" -> bay names: A, B, ...
            - "bays.A" -> bay fields: grid_type, origin, ...
            - "bays.A.corridor" -> corridor fields
            - "style" -> all style properties
            - "legend" -> all legend properties
    """
    state = _load_state()
    if not path:
        target = state
    else:
        try:
            _, _, target = _resolve_path(state, path)
        except ValueError as e:
            return f"ERROR: {e}"

    if isinstance(target, dict):
        lines = [f"OK: {len(target)} fields at '{path or '(root)'}':"]
        for k in sorted(target.keys()):
            v = target[k]
            if isinstance(v, dict):
                lines.append(f"  {k}: {{...}} ({len(v)} fields)")
            elif isinstance(v, list):
                lines.append(f"  {k}: [...] ({len(v)} items)")
            else:
                val_str = json.dumps(v, ensure_ascii=False)
                if len(val_str) > 60:
                    val_str = val_str[:57] + "..."
                lines.append(f"  {k}: {val_str}")
        lines.append("READY:")
        return "\n".join(lines)
    elif isinstance(target, list):
        lines = [f"OK: {len(target)} items at '{path}':"]
        for i, v in enumerate(target):
            if isinstance(v, dict):
                preview_parts = []
                for pk, pv in list(v.items())[:3]:
                    preview_parts.append(
                        f"{pk}={json.dumps(pv, ensure_ascii=False)}")
                preview = ", ".join(preview_parts)
                lines.append(f"  [{i}]: {{{preview}, ...}}")
            else:
                lines.append(
                    f"  [{i}]: {json.dumps(v, ensure_ascii=False)}")
        lines.append("READY:")
        return "\n".join(lines)
    else:
        return (f"OK: {path} = "
                f"{json.dumps(target, ensure_ascii=False)} "
                f"(leaf value, not a container)")


# ══════════════════════════════════════════════════════════
# NEW v3.1 TOOLS — BAY MANAGEMENT
# ══════════════════════════════════════════════════════════

@mcp.tool()
def add_bay(name: str, grid_type: str = "rectangular",
            origin_x: float = 0.0, origin_y: float = 0.0) -> str:
    """Create a new bay with default settings.

    Creates a bay using the controller's default template. The bay
    starts with walls off, corridor off, no apertures. Use set_bay,
    set_walls, set_corridor, and add_aperture to configure it.

    After creation, room references are regenerated automatically.

    Args:
        name: Bay name (single uppercase letter recommended: "C", "D")
        grid_type: "rectangular" or "radial" (default: rectangular)
        origin_x: X position of anchor point in feet (default: 0)
        origin_y: Y position of anchor point in feet (default: 0)
    """
    state = _load_state()
    if name in state.get("bays", {}):
        return f"ERROR: Bay '{name}' already exists."
    if grid_type not in ("rectangular", "radial"):
        return "ERROR: grid_type must be 'rectangular' or 'radial'."

    bay = cli._default_bay(name, [origin_x, origin_y],
                           grid_type=grid_type)
    state.setdefault("bays", {})[name] = bay
    state["rooms"] = cli._auto_rooms(state["bays"])
    cli.save_state(STATE_PATH, state)
    return (f"OK: Created bay '{name}' ({grid_type}) "
            f"at ({origin_x}, {origin_y}). "
            f"Rooms regenerated. "
            f"Use set_bay, set_walls, etc. to configure.")


@mcp.tool()
def remove_bay(name: str) -> str:
    """Remove a bay and its room references from the model.

    This permanently deletes the bay. Room references are
    regenerated automatically. Use save_snapshot first if you
    might want to undo this.

    Args:
        name: Bay name to remove (e.g. "A", "B")
    """
    state = _load_state()
    bays = state.get("bays", {})
    if name not in bays:
        avail = ", ".join(sorted(bays.keys())) or "(none)"
        return f"ERROR: Bay '{name}' does not exist. Available: {avail}"

    del state["bays"][name]
    state["rooms"] = cli._auto_rooms(state["bays"])
    cli.save_state(STATE_PATH, state)
    remaining = ", ".join(sorted(state["bays"].keys())) or "(none)"
    return (f"OK: Removed bay '{name}'. "
            f"Rooms regenerated. Remaining bays: {remaining}")


@mcp.tool()
def clone_bay(source: str, target: str,
              origin_x: float = None,
              origin_y: float = None) -> str:
    """Duplicate a bay with a new name and optional new position.

    Deep copies all properties (walls, corridor, apertures, void)
    from the source bay. If no origin is given, the clone is placed
    at the same position as the source.

    Args:
        source: Bay name to copy from (e.g. "A")
        target: New bay name (e.g. "C")
        origin_x: Optional new X position in feet
        origin_y: Optional new Y position in feet
    """
    import copy
    state = _load_state()
    bays = state.get("bays", {})
    if source not in bays:
        return f"ERROR: Source bay '{source}' does not exist."
    if target in bays:
        return f"ERROR: Target bay '{target}' already exists."

    new_bay = copy.deepcopy(bays[source])
    if origin_x is not None and origin_y is not None:
        new_bay["origin"] = [origin_x, origin_y]
    new_bay["label"] = f"Bay {target}"
    new_bay["braille"] = ""

    state["bays"][target] = new_bay
    state["rooms"] = cli._auto_rooms(state["bays"])
    cli.save_state(STATE_PATH, state)
    origin = new_bay["origin"]
    return (f"OK: Cloned bay '{source}' to '{target}' "
            f"at ({origin[0]}, {origin[1]}). Rooms regenerated.")


# ══════════════════════════════════════════════════════════
# NEW v3.1 TOOLS — CONTROLLER INTROSPECTION
# ══════════════════════════════════════════════════════════

@mcp.tool()
def list_commands() -> str:
    """List all available CLI commands with handler functions.

    Shows every command the controller understands, organized by
    category. Includes commands added via extend_controller.
    """
    import re
    cli_path = os.path.join(_controller, "controller_cli.py")
    try:
        with open(cli_path, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        return f"ERROR: Cannot read controller_cli.py: {e}"

    # Find dispatch lines: if cmd == "xxx": return cmd_xxx(...)
    pattern = r'if cmd == "(\w+)":\s*return (\w+)\('
    matches = re.findall(pattern, source)

    # Find set sub-commands
    set_pattern = r'"(\w+)":\s*_cmd_set_(\w+)'
    set_matches = re.findall(set_pattern, source)

    sentinel_cmds = [
        ("describe / d", "Full model description"),
        ("list bays / l bays", "Compact bay table"),
        ("undo", "Revert last change (CLI only)"),
        ("status", "State file path and timestamp"),
        ("help / h / ?", "Command reference"),
        ("print / p", "Request print export"),
        ("quit / q / exit", "Save and exit (CLI only)"),
    ]

    lines = ["OK: Available commands:", ""]

    lines.append("Navigation:")
    for cmd, desc in sentinel_cmds:
        lines.append(f"  {cmd}: {desc}")

    lines.append("")
    lines.append("Handlers:")
    for cmd_word, func_name in sorted(matches):
        lines.append(f"  {cmd_word}: -> {func_name}()")

    lines.append("")
    lines.append("Set sub-commands:")
    for target, func in sorted(set_matches):
        lines.append(f"  set {target}: -> _cmd_set_{func}()")

    total = len(sentinel_cmds) + len(matches) + len(set_matches)
    lines.append("")
    lines.append(f"Total: {total} commands")
    lines.append("READY:")
    return "\n".join(lines)


@mcp.tool()
def show_command_source(command: str) -> str:
    """Show the source code of a CLI command handler function.

    Use this to understand how existing commands work before
    writing extensions with extend_controller.

    Args:
        command: Command word (e.g. "corridor", "wall", "aperture")
            or full function name (e.g. "cmd_corridor", "_cmd_set_bay")
    """
    cli_path = os.path.join(_controller, "controller_cli.py")
    try:
        with open(cli_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        return f"ERROR: Cannot read controller_cli.py: {e}"

    # Normalize to function name
    if command.startswith("cmd_") or command.startswith("_cmd_"):
        func_name = command
    else:
        # Try cmd_<command> first, then _cmd_set_<command>
        func_name = f"cmd_{command}"
        found = False
        for line in lines:
            if f"def {func_name}(" in line:
                found = True
                break
        if not found:
            func_name = f"_cmd_set_{command}"

    # Find function start
    start = None
    for i, line in enumerate(lines):
        if f"def {func_name}(" in line:
            start = i
            break

    if start is None:
        return (f"ERROR: Function for '{command}' not found. "
                f"Try list_commands() to see available commands.")

    # Find function end (next def at same or lower indentation)
    indent = len(lines[start]) - len(lines[start].lstrip())
    end = len(lines)
    for i in range(start + 1, len(lines)):
        stripped = lines[i].lstrip()
        if stripped.startswith("def ") or stripped.startswith("class "):
            current_indent = len(lines[i]) - len(stripped)
            if current_indent <= indent:
                end = i
                break

    source = "".join(lines[start:end]).rstrip()
    line_count = end - start
    return (f"OK: Source of {func_name} "
            f"(lines {start + 1}-{end}, {line_count} lines):\n\n{source}")


# ══════════════════════════════════════════════════════════
# NEW v3.1 TOOLS — STATE COMPARISON
# ══════════════════════════════════════════════════════════

@mcp.tool()
def diff_snapshot(snapshot_name: str) -> str:
    """Compare current state to a named snapshot.

    Shows which fields differ between the current state.json and
    a previously saved snapshot. Use this to review what changed
    since a checkpoint.

    Args:
        snapshot_name: Name of a saved snapshot to compare against
    """
    state = _load_state()

    # Load snapshot
    history_dir = os.path.join(os.path.dirname(STATE_PATH), "history")
    snap_path = os.path.join(
        history_dir, f"snapshot_{snapshot_name}.json")
    if not os.path.exists(snap_path):
        return (f"ERROR: Snapshot '{snapshot_name}' not found. "
                f"Use list_snapshots() to see available snapshots.")

    try:
        with open(snap_path, "r", encoding="utf-8") as f:
            snap_state = json.load(f)
    except Exception as e:
        return f"ERROR: Cannot read snapshot: {e}"

    diffs = []
    _diff_dicts("", state, snap_state, diffs)

    if not diffs:
        return (f"OK: Current state matches snapshot "
                f"'{snapshot_name}'. No differences.")

    lines = [f"OK: {len(diffs)} difference(s) vs "
             f"snapshot '{snapshot_name}':", ""]
    for i, (path, current, snapshot) in enumerate(diffs[:50], 1):
        cur_str = json.dumps(current, ensure_ascii=False)
        snap_str = json.dumps(snapshot, ensure_ascii=False)
        if len(cur_str) > 80:
            cur_str = cur_str[:77] + "..."
        if len(snap_str) > 80:
            snap_str = snap_str[:77] + "..."
        lines.append(f"  {i}. {path}:")
        lines.append(f"     now: {cur_str}")
        lines.append(f"     was: {snap_str}")
    if len(diffs) > 50:
        lines.append(f"  ... and {len(diffs) - 50} more differences")
    lines.append("READY:")
    return "\n".join(lines)


@mcp.tool()
def validate_state() -> str:
    """Validate the current state.json for structural correctness.

    Checks that state.json is valid JSON, has required top-level
    sections, and that each bay has required fields with correct
    types. Use this after editing state.json by hand.

    This is different from audit_model, which checks spatial and
    ADA rules. validate_state checks the JSON structure itself.
    """
    # Try to load raw JSON
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        return f"ERROR: Cannot read {STATE_PATH}: {e}"

    try:
        state = json.loads(raw)
    except json.JSONDecodeError as e:
        return (f"ERROR: Invalid JSON at line {e.lineno}, "
                f"column {e.colno}: {e.msg}")

    issues = []

    # Check required top-level keys
    required = ["schema", "meta", "site", "bays"]
    for key in required:
        if key not in state:
            issues.append(f"Missing required top-level key: '{key}'")

    # Check site
    site = state.get("site", {})
    if isinstance(site, dict):
        if "width" not in site or "height" not in site:
            issues.append("Site missing 'width' or 'height'")
        else:
            if not isinstance(site["width"], (int, float)):
                issues.append("Site width must be a number")
            if not isinstance(site["height"], (int, float)):
                issues.append("Site height must be a number")

    # Check each bay
    for name, bay in state.get("bays", {}).items():
        if not isinstance(bay, dict):
            issues.append(f"Bay {name}: must be a dict")
            continue

        required_bay = ["grid_type", "origin", "bays", "spacing"]
        for key in required_bay:
            if key not in bay:
                issues.append(
                    f"Bay {name}: missing required field '{key}'")

        # Check origin is [x, y]
        origin = bay.get("origin")
        if origin is not None:
            if not isinstance(origin, list) or len(origin) != 2:
                issues.append(f"Bay {name}: origin must be [x, y]")

        # Check bays is [nx, ny]
        bays_val = bay.get("bays")
        if bays_val is not None:
            if not isinstance(bays_val, list) or len(bays_val) != 2:
                issues.append(f"Bay {name}: bays must be [nx, ny]")

        # Check grid_type
        gt = bay.get("grid_type")
        if gt not in ("rectangular", "radial", None):
            issues.append(
                f"Bay {name}: grid_type must be "
                f"'rectangular' or 'radial', got '{gt}'")

        # Check apertures
        for ap in bay.get("apertures", []):
            if not isinstance(ap, dict):
                issues.append(f"Bay {name}: aperture must be a dict")
                continue
            if "id" not in ap:
                issues.append(f"Bay {name}: aperture missing 'id'")
            ap_type = ap.get("type")
            if ap_type not in ("door", "window", "portal", None):
                issues.append(
                    f"Bay {name}: aperture {ap.get('id', '?')} "
                    f"has invalid type '{ap_type}'")

        # Check corridor structure
        cor = bay.get("corridor")
        if cor is not None and not isinstance(cor, dict):
            issues.append(f"Bay {name}: corridor must be a dict")

        # Check walls structure
        walls = bay.get("walls")
        if walls is not None and not isinstance(walls, dict):
            issues.append(f"Bay {name}: walls must be a dict")

    if not issues:
        bay_count = len(state.get("bays", {}))
        ap_count = sum(
            len(b.get("apertures", []))
            for b in state.get("bays", {}).values())
        return (f"OK: state.json is valid. "
                f"Schema: {state.get('schema', '?')}. "
                f"{bay_count} bay(s), {ap_count} aperture(s). "
                f"File size: {len(raw)} bytes.")

    lines = [f"ISSUES: {len(issues)} problem(s) found:", ""]
    for i, issue in enumerate(issues, 1):
        lines.append(f"  {i}. {issue}")
    lines.append("READY:")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
# MCP RESOURCES
# ══════════════════════════════════════════════════════════

# ── v2.0 resources (unchanged) ────────────────────────────

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


# ── v3.0 resources ────────────────────────────────────────

@mcp.resource("skills://list")
def resource_skill_list() -> str:
    """List of all saved skills with summaries."""
    skills = skill_manager.list_skills()
    return skill_manager.format_skill_list(skills)


@mcp.resource("templates://list")
def resource_template_list() -> str:
    """List of all available templates with summaries."""
    templates = template_manager.list_templates()
    return template_manager.format_template_list(templates)


@mcp.resource("extensions://list")
def resource_extension_list() -> str:
    """List of controller extensions added this session."""
    state = _load_state()
    extensions = state.get("meta", {}).get("extensions", [])
    if not extensions:
        return "No extensions added."
    lines = []
    for ext in extensions:
        lines.append(f"{ext['command']} -> {ext['function']}()")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
# MCP PROMPTS
# ══════════════════════════════════════════════════════════

# ── v2.0 prompts (unchanged) ─────────────────────────────

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


# ── v3.0 prompts ─────────────────────────────────────────

@mcp.prompt()
def accessibility_audit() -> str:
    """Run a comprehensive accessibility audit of the design.

    Checks ADA compliance, corridor widths, door clearances,
    turning radii, and tactile readability.
    """
    state = _load_state()
    desc = cli.describe(state)
    issues = auditor.audit_model(state)
    audit_text = auditor.format_audit(issues)
    circulation = auditor.describe_circulation(state)

    return (
        f"ACCESSIBILITY AUDIT REQUEST\n\n"
        f"Model state:\n{desc}\n\n"
        f"Automated checks:\n{audit_text}\n\n"
        f"Circulation analysis:\n{circulation}\n\n"
        f"Please provide a comprehensive accessibility review:\n"
        f"1. ADA compliance: door widths (min 3 ft clear), corridor widths "
        f"(min 5 ft for wheelchair passing, 6 ft preferred)\n"
        f"2. Turning radii: 5 ft minimum at corridor intersections\n"
        f"3. Egress: at least 2 exits from each major space\n"
        f"4. Tactile readability: distinct hatches for adjacent rooms, "
        f"Braille labels present, legend completeness\n"
        f"5. Wayfinding: logical room naming, consistent labeling"
    )


@mcp.prompt()
def skill_builder() -> str:
    """Guide through creating a new reusable skill.

    Provides the current command reference and skill format
    so Claude can help compose a new skill.
    """
    state = _load_state()
    skills = skill_manager.list_skills()
    skill_text = skill_manager.format_skill_list(skills)

    return (
        f"SKILL BUILDER\n\n"
        f"I want to create a new reusable skill (command macro) for the "
        f"Layout Jig. Here is the current command reference:\n\n"
        f"{cli.HELP_TEXT}\n\n"
        f"Existing skills:\n{skill_text}\n\n"
        f"A skill is a JSON file with:\n"
        f"  - name: kebab-case identifier\n"
        f"  - description: what it does\n"
        f"  - commands: list of CLI commands with {{param}} placeholders\n"
        f"  - params: dict of param_name -> {{description, default}}\n\n"
        f"Please help me design a new skill. Ask me:\n"
        f"1. What should the skill do?\n"
        f"2. What parameters should be configurable?\n"
        f"3. Then compose the command sequence and save it."
    )


# ── Script generation tools (Mode 3: Learning Rhino Python) ──

SCRIPTS_DIR = os.path.join(os.path.dirname(STATE_PATH), "scripts")


def _safe_script_name(name):
    """Normalize to kebab-case filename."""
    name = name.strip().lower()
    name = _re.sub(r"[^a-z0-9\-]", "-", name)
    name = _re.sub(r"-+", "-", name).strip("-")
    return name or "untitled"


@mcp.tool()
def generate_script(name: str, description: str, code: str,
                    teach: bool = True) -> str:
    """Generate an editable IronPython 2.7 script file for Rhino.

    Creates a .py file in the scripts/ folder that the user can open
    in Rhino's EditPythonScript editor, study, modify, and run.

    The script is validated for IronPython 2.7 compatibility:
    no f-strings, no pathlib, valid Python syntax.

    Args:
        name: Script name in kebab-case (e.g. "draw-column-grid")
        description: One-line summary of what the script does
        code: Complete IronPython 2.7 script body
        teach: If True, prepend commented explanation (default True)
    """
    safe = _safe_script_name(name)
    if not safe:
        return "ERROR: Invalid script name."

    # Validate: no f-strings
    fstring_hits = _re.findall(r'(?<!\w)f"[^"]*\{', code)
    fstring_hits += _re.findall(r"(?<!\w)f'[^']*\{", code)
    if fstring_hits:
        return ("ERROR: Code contains f-strings which are not supported "
                "in IronPython 2.7. Use .format() instead.")

    # Validate: no pathlib
    if "import pathlib" in code or "from pathlib" in code:
        return ("ERROR: Code uses pathlib which is not available in "
                "IronPython 2.7. Use os.path instead.")

    # Validate: parseable
    try:
        ast.parse(code)
    except SyntaxError as e:
        return f"ERROR: Syntax error in script: {e}"

    # Warn about geometry-modifying calls (non-blocking)
    warnings = []
    if _re.search(r"rs\.(Add|Delete|Move|Copy|Rotate|Scale|Mirror)", code):
        warnings.append("Note: Script contains geometry-modifying calls. "
                        "These are allowed but will change the Rhino document.")

    # Build header
    header_lines = [
        "# -*- coding: utf-8 -*-",
        f"# Script: {safe}",
        f"# {description}",
        "# Generated by Layout Jig — edit freely!",
        "#",
        "# HOW TO RUN:",
        "#   In Rhino, type EditPythonScript to open the editor.",
        "#   Open this file, then press F5 (or the Run button).",
        "#   Output appears in the Rhino command line.",
    ]

    if teach:
        header_lines.extend([
            "#",
            "# LEARNING NOTES:",
            "# - Lines starting with 'import' load libraries",
            "# - rhinoscriptsyntax (rs) provides Rhino geometry functions",
            "# - json.load() reads data from JSON files",
            "# - print() sends text to the Rhino command line",
            "# - Try changing values and re-running to see what happens",
        ])

    header_lines.append("")

    full_code = "\n".join(header_lines) + "\n" + code
    if not full_code.endswith("\n"):
        full_code += "\n"

    # Write atomically
    os.makedirs(SCRIPTS_DIR, exist_ok=True)
    out_path = os.path.join(SCRIPTS_DIR, f"{safe}.py")
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(full_code)
    os.replace(tmp_path, out_path)

    parts = [f"OK: Script saved to scripts/{safe}.py"]
    parts.append(f"  To run: open {safe}.py in Rhino's EditPythonScript, press F5.")
    if warnings:
        for w in warnings:
            parts.append(f"  {w}")
    parts.append("READY:")
    return "\n".join(parts)


@mcp.tool()
def list_scripts() -> str:
    """List all generated script files in the scripts/ folder.

    Shows name, description, size, and modification date for each .py file.
    """
    if not os.path.isdir(SCRIPTS_DIR):
        return "OK: No scripts folder yet. Use generate_script to create one.\nREADY:"

    py_files = sorted(f for f in os.listdir(SCRIPTS_DIR)
                      if f.endswith(".py") and not f.startswith("_"))

    if not py_files:
        return "OK: No scripts found. Use generate_script to create one.\nREADY:"

    lines = [f"OK: {len(py_files)} script(s) in scripts/:"]
    for fname in py_files:
        fpath = os.path.join(SCRIPTS_DIR, fname)
        size = os.path.getsize(fpath)
        # Read first comment line for description
        desc = ""
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# Script:"):
                        continue
                    if line.startswith("# -*- coding"):
                        continue
                    if line.startswith("#") and len(line) > 2:
                        desc = line[2:].strip()
                        break
        except Exception:
            desc = "(unreadable)"

        name_no_ext = fname[:-3]
        lines.append(f"  {name_no_ext}: {desc} ({size} bytes)")

    lines.append("READY:")
    return "\n".join(lines)


@mcp.tool()
def show_script(name: str) -> str:
    """Show the full contents of a generated script file.

    Args:
        name: Script name (with or without .py extension)
    """
    safe = _safe_script_name(name)
    if not safe:
        return "ERROR: Invalid script name."

    fpath = os.path.join(SCRIPTS_DIR, f"{safe}.py")

    if not os.path.exists(fpath):
        # Try fuzzy match
        if os.path.isdir(SCRIPTS_DIR):
            candidates = [f[:-3] for f in os.listdir(SCRIPTS_DIR)
                          if f.endswith(".py")]
            matches = [c for c in candidates if safe in c or c in safe]
            if matches:
                return (f"ERROR: Script '{safe}' not found. "
                        f"Did you mean: {', '.join(matches)}?")
        return f"ERROR: Script '{safe}' not found."

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return f"ERROR: Could not read script: {e}"

    return f"OK: Contents of scripts/{safe}.py:\n\n{content}\nREADY:"


# ══════════════════════════════════════════════════════
# MODE 4: SWELL-PRINT — PIAF TACTILE GRAPHICS
# ══════════════════════════════════════════════════════

_SWELL_MISSING_MSG = (
    "ERROR: Swell-print dependencies not installed. "
    "Run: pip install -r tools/swell-print/requirements.txt"
)


@mcp.tool()
def render_tactile(paper_size: str = "letter",
                   output_format: str = "pdf") -> str:
    """Render state.json to a PIAF-ready tactile graphic. No Rhino needed.

    Produces a 300 DPI black-and-white image suitable for swell-paper
    printing. Draws columns, walls, corridors, apertures, room hatches,
    labels (English + Braille), legend, and section cuts.

    Args:
        paper_size: "letter" (8.5x11) or "tabloid" (11x17)
        output_format: "pdf" or "png"
    """
    if not _swell_available:
        return _SWELL_MISSING_MSG

    state = _load_state()
    dpi = 300

    try:
        img = state_renderer.render(state, dpi=dpi, paper_size=paper_size)
    except Exception as e:
        return f"ERROR: Render failed: {e}"

    # Determine output path
    base = os.path.splitext(os.path.basename(STATE_PATH))[0]
    fmt = output_format.lower()
    if fmt not in ("pdf", "png"):
        fmt = "pdf"
    out_name = f"{base}_tactile.{fmt}"
    out_path = os.path.join(os.path.dirname(STATE_PATH), out_name)

    try:
        if fmt == "pdf":
            try:
                import pdf_generator
                pdf_generator.generate_pdf(
                    img, out_path, paper_size=paper_size,
                    metadata={"source": os.path.basename(STATE_PATH)})
            except ImportError:
                # reportlab not available — fall back to PNG
                out_path = os.path.splitext(out_path)[0] + ".png"
                img.save(out_path, dpi=(dpi, dpi))
        else:
            img.save(out_path, dpi=(dpi, dpi))
    except Exception as e:
        return f"ERROR: Could not save output: {e}"

    d = state_renderer.density(img)
    return (f"OK: Rendered {out_name} "
            f"({paper_size.title()}, {dpi} DPI, density {d:.1f}%)\n"
            f"  Path: {out_path}\nREADY:")


@mcp.tool()
def convert_to_tactile(image_path: str,
                       preset: str = "floor_plan",
                       threshold: int = None,
                       paper_size: str = "letter") -> str:
    """Convert any image to a PIAF-ready tactile graphic.

    Takes a photograph, sketch, CAD export, or any image and converts
    it to high-contrast black-and-white output suitable for swell-paper
    printing.

    Args:
        image_path: Path to the input image (JPG, PNG, TIFF, BMP)
        preset: Conversion preset (floor_plan, sketch, photograph, etc.)
        threshold: Optional B&W threshold 0-255 (overrides preset)
        paper_size: "letter" or "tabloid"
    """
    if not _swell_available:
        return _SWELL_MISSING_MSG

    if not os.path.isfile(image_path):
        return f"ERROR: Image not found: {image_path}"

    dpi = 300

    try:
        result = image_converter.convert(
            image_path,
            output_path=None,
            preset=preset,
            threshold=threshold,
            paper_size=paper_size,
            dpi=dpi,
        )
    except (FileNotFoundError, ValueError) as e:
        return f"ERROR: {e}"
    except Exception as e:
        return f"ERROR: Conversion failed: {e}"

    out_path = result["output_path"]
    density = result["density"]
    message = result["message"]

    return (f"OK: Converted {os.path.basename(image_path)} -> "
            f"{os.path.basename(out_path)} "
            f"(density {density:.1f}%, {message})\n"
            f"  Path: {out_path}\nREADY:")


@mcp.tool()
def check_tactile_density(image_path: str) -> str:
    """Check if an image's black pixel density is suitable for PIAF printing.

    PIAF swell paper works best with 25-40% black pixel density.
    Above 45% causes excessive swelling and loss of detail.

    Args:
        image_path: Path to a B&W image file
    """
    if not _swell_available:
        return _SWELL_MISSING_MSG

    if not os.path.isfile(image_path):
        return f"ERROR: Image not found: {image_path}"

    try:
        from PIL import Image
        img = Image.open(image_path)
        if img.mode != '1':
            img = img.convert('1')
        ok, density, msg = image_converter.check_density(img)
        status = "OK" if ok else "WARNING"
        return f"{status}: {msg}\nREADY:"
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def list_tactile_presets() -> str:
    """List available image conversion presets with their settings.

    Each preset is optimised for a specific type of architectural
    image (floor plan, sketch, photograph, etc.).
    """
    if not _swell_available:
        return _SWELL_MISSING_MSG

    try:
        presets = image_converter.list_presets()
        lines = [f"OK: {len(presets)} presets available:"]
        for i, (name, desc) in enumerate(presets, 1):
            p = image_converter.PRESETS[name]
            lines.append(f"  {i}. {name} — {desc} "
                         f"(threshold {p['threshold']}, "
                         f"max density {p['max_density']}%)")
        lines.append("READY:")
        return "\n".join(lines)
    except Exception as e:
        return f"ERROR: {e}"


# ══════════════════════════════════════════════════════════
# Style profile tools (v3.5)
# ══════════════════════════════════════════════════════════

# Import style manager
try:
    import style_manager as _style_mod
    _style_mgr = _style_mod.StyleManager()
    _style_available = True
except ImportError:
    _style_mgr = None
    _style_available = False


@mcp.tool()
def style_use(name: str) -> str:
    """Switch the active PIAF rendering style profile.

    Args:
        name: Style name (e.g. "working", "presentation", "detail")
    """
    if not _style_available:
        return "ERROR: Style manager not available."
    try:
        sname, desc = _style_mgr.use(name)
        return f"OK: Style \"{sname}\" active. {desc}\nREADY:"
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def style_show(category: str = None) -> str:
    """Show current style settings.

    Args:
        category: Optional filter — lineweights, hatches, labels, layout, density.
                  If omitted, shows a summary of all categories.
    """
    if not _style_available:
        return "ERROR: Style manager not available."
    try:
        result = _style_mgr.show(category)
        return f"OK: {result}\nREADY:"
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def style_set(key: str, value: str) -> str:
    """Set a style value using dot notation.

    Args:
        key: Dot-notation path (e.g. "lineweights.wall_exterior", "layout.paper")
        value: New value (e.g. "3.0", "tabloid", "true")
    """
    if not _style_available:
        return "ERROR: Style manager not available."
    try:
        new_val, old_val = _style_mgr.set(key, value)
        parts = key.split(".")
        short = parts[-1] if parts else key
        return f"OK: {short} = {new_val}. Was {old_val}.\nREADY:"
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def style_save(name: str = None) -> str:
    """Save active style. If name given, save as new style file.

    Args:
        name: Optional new name for save-as. Omit to save in place.
    """
    if not _style_available:
        return "ERROR: Style manager not available."
    try:
        fpath = _style_mgr.save(name)
        saved = name or _style_mgr.active_name
        return f"OK: Saved style \"{saved}\" to {os.path.basename(fpath)}.\nREADY:"
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def style_list() -> str:
    """List all available PIAF style profiles."""
    if not _style_available:
        return "ERROR: Style manager not available."
    try:
        styles = _style_mgr.list_styles()
        lines = [f"OK: {len(styles)} styles available:"]
        for i, (sname, desc, active) in enumerate(styles, 1):
            marker = " (active)" if active else ""
            lines.append(f"  {i}. {sname}{marker}")
        lines.append("READY:")
        return "\n".join(lines)
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def style_test() -> str:
    """Generate a calibration test swatch showing all lineweights and hatches.

    Creates a B&W image with labeled samples of every lineweight
    and hatch pattern at the current style settings. Print on PIAF
    swell paper to calibrate tactile output.
    """
    if not _style_available:
        return "ERROR: Style manager not available."
    if not _swell_available:
        return _SWELL_MISSING_MSG
    try:
        out_dir = os.path.dirname(STATE_PATH)
        png_path = os.path.join(out_dir, "style_test.png")
        _style_mgr.generate_test_swatch(png_path)
        # Try PDF
        try:
            import pdf_generator
            pdf_path = os.path.join(out_dir, "style_test.pdf")
            from PIL import Image
            img = Image.open(png_path)
            paper = _style_mgr.get("layout.paper", "letter")
            pdf_generator.generate_pdf(img, pdf_path, paper_size=paper)
            return f"OK: Rendered style_test.pdf ({paper.title()}, all lineweights and hatches).\n  Path: {pdf_path}\nREADY:"
        except ImportError:
            return f"OK: Rendered style_test.png (all lineweights and hatches).\n  Path: {png_path}\nREADY:"
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def view_plan(style: str = None, paper: str = None,
              scale: str = None) -> str:
    """Render a plan view with the active or specified style.

    Args:
        style: Optional style name to use (e.g. "presentation")
        paper: Optional paper size override ("letter" or "tabloid")
        scale: Optional scale override (default: "auto")
    """
    if not _swell_available:
        return _SWELL_MISSING_MSG
    if not _style_available:
        return "ERROR: Style manager not available."
    try:
        state = _load_state()
        sm = _style_mgr
        original = sm.active_name
        if style:
            sm.use(style)
        paper_size = paper or sm.get("layout.paper", "letter")
        dpi = 300
        margin = sm.get("layout.margin_inches", 0.5)
        img = state_renderer.render(state, dpi=dpi, paper_size=paper_size,
                                    margin_in=margin, style_manager=sm)
        out_dir = os.path.dirname(STATE_PATH)
        out_path = os.path.join(out_dir, "plan.png")
        img.save(out_path, dpi=(dpi, dpi))
        try:
            import pdf_generator
            pdf_path = os.path.join(out_dir, "plan.pdf")
            pdf_generator.generate_pdf(img, pdf_path, paper_size=paper_size)
            out_path = pdf_path
        except ImportError:
            pass
        d = state_renderer.density(img)
        if style:
            sm.use(original)
        return (f"OK: Rendered {os.path.basename(out_path)} "
                f"({paper_size.title()}, {dpi} DPI, density {d:.1f}%)\n"
                f"  Path: {out_path}\nREADY:")
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def view_section(axis: str, gridline: int, style: str = None) -> str:
    """Render a section cut at the given axis and gridline.

    Args:
        axis: "x" or "y"
        gridline: Which gridline to cut at (0-based integer)
        style: Optional style name
    """
    if not _swell_available:
        return _SWELL_MISSING_MSG
    if not _style_available:
        return "ERROR: Style manager not available."
    try:
        state = _load_state()
        sm = _style_mgr
        original = sm.active_name
        if style:
            sm.use(style)
        paper_size = sm.get("layout.paper", "letter")
        dpi = 300
        overrides = sm.get("drawing_overrides.section", {})
        poche = overrides.get("poche_fill", True)
        beyond = overrides.get("beyond_weight_factor", 0.5)
        img = state_renderer.render_section(state, axis, gridline, dpi=dpi,
                                            paper_size=paper_size,
                                            style_manager=sm,
                                            poche_fill=poche,
                                            beyond_weight_factor=beyond)
        out_dir = os.path.dirname(STATE_PATH)
        out_name = f"section_{axis}_{gridline}.png"
        out_path = os.path.join(out_dir, out_name)
        img.save(out_path, dpi=(dpi, dpi))
        try:
            import pdf_generator
            pdf_name = f"section_{axis}_{gridline}.pdf"
            pdf_path = os.path.join(out_dir, pdf_name)
            pdf_generator.generate_pdf(img, pdf_path, paper_size=paper_size)
            out_path = pdf_path
            out_name = pdf_name
        except ImportError:
            pass
        d = state_renderer.density(img)
        if style:
            sm.use(original)
        return (f"OK: Rendered {out_name} "
                f"(section cut at {axis}-gridline {gridline}, density {d:.1f}%)\n"
                f"  Path: {out_path}\nREADY:")
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def view_axon(angle1: float = 30, angle2: float = 60,
              hidden: bool = False, style: str = None) -> str:
    """Render an axonometric projection.

    Args:
        angle1: Rotation around vertical axis in degrees (default 30)
        angle2: Tilt angle in degrees (default 60)
        hidden: Enable hidden-line removal
        style: Optional style name
    """
    if not _swell_available:
        return _SWELL_MISSING_MSG
    if not _style_available:
        return "ERROR: Style manager not available."
    try:
        state = _load_state()
        sm = _style_mgr
        original = sm.active_name
        if style:
            sm.use(style)
        paper_size = sm.get("layout.paper", "letter")
        dpi = 300
        overrides = sm.get("drawing_overrides.axon", {})
        depth_fade = overrides.get("depth_fade", True)
        depth_min = overrides.get("depth_fade_min_factor", 0.3)
        img = state_renderer.render_axon(state, angle1, angle2, dpi=dpi,
                                         paper_size=paper_size,
                                         style_manager=sm,
                                         hidden_line=hidden,
                                         depth_fade=depth_fade,
                                         depth_fade_min=depth_min)
        suffix = "_hidden" if hidden else ""
        out_dir = os.path.dirname(STATE_PATH)
        out_name = f"axon{suffix}.png"
        out_path = os.path.join(out_dir, out_name)
        img.save(out_path, dpi=(dpi, dpi))
        try:
            import pdf_generator
            pdf_name = f"axon{suffix}.pdf"
            pdf_path = os.path.join(out_dir, pdf_name)
            pdf_generator.generate_pdf(img, pdf_path, paper_size=paper_size)
            out_path = pdf_path
            out_name = pdf_name
        except ImportError:
            pass
        d = state_renderer.density(img)
        if style:
            sm.use(original)
        a1 = int(angle1) if angle1 == int(angle1) else angle1
        a2 = int(angle2) if angle2 == int(angle2) else angle2
        mode = "hidden-line" if hidden else "wireframe"
        return (f"OK: Rendered {out_name} "
                f"({a1}/{a2} projection, {mode}, density {d:.1f}%)\n"
                f"  Path: {out_path}\nREADY:")
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def view_elevation(direction: str, style: str = None) -> str:
    """Render a building elevation.

    Args:
        direction: "north", "south", "east", or "west"
        style: Optional style name
    """
    if not _swell_available:
        return _SWELL_MISSING_MSG
    if not _style_available:
        return "ERROR: Style manager not available."
    try:
        state = _load_state()
        sm = _style_mgr
        original = sm.active_name
        if style:
            sm.use(style)
        paper_size = sm.get("layout.paper", "letter")
        dpi = 300
        img = state_renderer.render_elevation(state, direction, dpi=dpi,
                                              paper_size=paper_size,
                                              style_manager=sm)
        out_dir = os.path.dirname(STATE_PATH)
        out_name = f"elevation_{direction}.png"
        out_path = os.path.join(out_dir, out_name)
        img.save(out_path, dpi=(dpi, dpi))
        try:
            import pdf_generator
            pdf_name = f"elevation_{direction}.pdf"
            pdf_path = os.path.join(out_dir, pdf_name)
            pdf_generator.generate_pdf(img, pdf_path, paper_size=paper_size)
            out_path = pdf_path
            out_name = pdf_name
        except ImportError:
            pass
        d = state_renderer.density(img)
        if style:
            sm.use(original)
        return (f"OK: Rendered {out_name} (density {d:.1f}%)\n"
                f"  Path: {out_path}\nREADY:")
    except Exception as e:
        return f"ERROR: {e}"


# ── Entry point ────────────────────────────────────────

if __name__ == "__main__":
    _real_print(f"Layout Jig MCP Server v3.5 starting...", file=sys.stderr)
    _real_print(f"State file: {STATE_PATH}", file=sys.stderr)
    _real_print(f"Tools: 65 (56 v3.4 + 9 v3.5 style/view)", file=sys.stderr)
    _real_print(f"Engines: auditor, skill_manager, rhino_client", file=sys.stderr)
    _real_print(f"Swell-print: {'available' if _swell_available else 'not installed'}", file=sys.stderr)
    _real_print(f"Style profiles: {'available' if _style_available else 'not available'}", file=sys.stderr)
    _real_print(f"Skills dir: {skill_manager.SKILLS_DIR}", file=sys.stderr)
    _real_print(f"Scripts dir: {SCRIPTS_DIR}", file=sys.stderr)
    mcp.run()
