# Layout Jig MCP Server v3.1 Manual

## What This Is

The MCP server is an intelligent layer between Claude and your Layout Jig.
It speaks the Model Context Protocol so Claude Code, Claude Desktop, and
Cursor can drive the jig conversationally.

v3.0 added four engines on top of the 21 existing v2.0 tools:

- Audit Engine: validates the model, checks ADA compliance, describes spaces
- Skill Engine: saves and replays reusable command sequences
- Rhino Bridge: optionally queries Rhino for geometry information
- Controller Extension: adds new commands to the CLI at runtime

v3.1 adds direct editing capabilities:

- State Introspection: read/write individual JSON fields by dot-path
- Bay Management: create, remove, and clone bays through MCP
- Controller Introspection: list commands, read handler source code
- State Comparison: diff snapshots, validate JSON structure

Total: 45 tools, 5 resources, 4 prompts.

---

## Architecture

```
You (speaking or typing to Claude)
        |
        v
  MCP Server (mcp_server.py v3.0)
    |       |         |           |
    v       v         v           v
  _run()  audit     skills     rhino_bridge
    |     engine     engine        |
    v       |         |            v
  controller_cli.py   |     rhino_watcher.py
    |                 |     (TCP listener on 1998)
    v                 v            |
  state.json          skills/     v
    |                            Rhino
    v
  rhino_watcher.py (polls state, rebuilds geometry)
```

Key principle: state.json is always the source of truth.
Rhino is a viewer. If Rhino crashes, nothing is lost.

---

## Files

| File | Purpose | Lines |
|------|---------|-------|
| mcp_server.py | MCP orchestrator, all 45 tools | ~1100 |
| controller_cli.py | Authoritative state machine | ~2000 |
| audit_engine.py | Spatial validation, descriptions | ~350 |
| skill_engine.py | Skill CRUD and replay | ~280 |
| rhino_bridge.py | TCP client to Rhino watcher | ~180 |
| rhino_watcher.py | Geometry renderer + TCP listener | ~1200 |
| skills/*.json | Saved skill files | varies |
| state.json | Canonical Model Artifact (CMA) | varies |

---

## Setup

### 1. Install MCP package

```
pip install mcp
```

This is the only external dependency. Everything else is Python stdlib.

### 2. Configure Claude Code

Your .mcp.json at the project root:

```json
{
  "mcpServers": {
    "layout-jig": {
      "command": "python",
      "args": [
        "rhino-python-driver/mcp_server.py",
        "--state",
        "rhino-python-driver/state.json"
      ]
    }
  }
}
```

### 3. Optional: Rhino connection

If you want live Rhino queries (object counts, bounding boxes):

1. Open Rhino
2. Run the watcher: `exec(open("path/to/rhino_watcher.py").read())`
3. The watcher starts a TCP listener on port 1998 automatically
4. MCP tools like rhino_status and rhino_query will connect

If Rhino is not running, those tools return "OFFLINE" messages.
Everything else works without Rhino.

---

## Tool Reference

### Original Tools (v1.0, unchanged)

| # | Tool | What it does |
|---|------|-------------|
| 1 | run_command(command) | Execute any raw CLI command string |
| 2 | describe() | Full text model description |
| 3 | list_bays() | Compact bay table |
| 4 | get_state() | Raw JSON state |
| 5 | get_help() | CLI command reference |

### Read Tools (v2.0)

| # | Tool | What it does |
|---|------|-------------|
| 6 | list_apertures(bay) | All apertures in a bay |
| 7 | list_cells(bay) | All cells in a rectangular bay |
| 8 | list_rooms() | All named rooms |
| 9 | list_snapshots() | All saved snapshots |

### Bay Configuration (v2.0)

| # | Tool | What it does |
|---|------|-------------|
| 10 | set_bay(bay, field, value) | Set any bay property |
| 11 | set_walls(bay, enabled, thickness) | Toggle walls on/off |
| 12 | set_corridor(bay, enabled, field, value) | Toggle corridor on/off |
| 13 | add_aperture(bay, id, type, axis, gridline, corner, width, height) | Add door/window/portal |
| 14 | remove_aperture(bay, id) | Remove an aperture |
| 15 | modify_aperture(bay, id, field, value) | Change aperture property |
| 16 | set_cell(bay, col, row, field, value) | Set cell room property |
| 17 | auto_corridor_cells(bay) | Auto-name corridor cells |
| 18 | set_site(field, value) | Set site width or height |
| 19 | set_style(field, value) | Set drawing style parameter |
| 20 | save_snapshot(name) | Save current state as checkpoint |
| 21 | load_snapshot(name) | Restore a saved snapshot |

### Audit Tools (v3.0 NEW)

| # | Tool | What it does |
|---|------|-------------|
| 22 | audit_model() | Run all validation checks on the model |
| 23 | audit_bay(bay) | Deep audit of a single bay |
| 24 | describe_bay(bay) | Rich narrative description of a bay |
| 25 | describe_circulation() | Corridor connectivity analysis |
| 26 | measure(from, to) | Distance between semantic locations |

### Skill Tools (v3.0 NEW)

| # | Tool | What it does |
|---|------|-------------|
| 27 | skill_list() | List all saved skills |
| 28 | skill_show(name) | Show skill details and commands |
| 29 | skill_run(name, overrides) | Execute a skill with parameters |
| 30 | skill_save(name, desc, commands, params) | Save a new skill |

### Rhino Bridge Tools (v3.0 NEW)

| # | Tool | What it does |
|---|------|-------------|
| 31 | rhino_status() | Check if Rhino is connected |
| 32 | rhino_query(query_type, layer) | Ask Rhino a read-only question |
| 33 | rhino_run_script(code) | Run a Python snippet inside Rhino |

### Extension Tools (v3.0 NEW)

| # | Tool | What it does |
|---|------|-------------|
| 34 | extend_controller(function_name, code) | Add a new CLI command |
| 35 | list_extensions() | Show all added extensions |

### State Introspection Tools (v3.1 NEW)

| # | Tool | What it does |
|---|------|-------------|
| 36 | get_field(path) | Read a specific field by dot-notation path |
| 37 | set_field(path, value) | Write a field by dot-notation path (bypasses CLI) |
| 38 | list_fields(path) | List all keys at a path (explore structure) |

### Bay Management Tools (v3.1 NEW)

| # | Tool | What it does |
|---|------|-------------|
| 39 | add_bay(name, grid_type, origin_x, origin_y) | Create a new bay |
| 40 | remove_bay(name) | Delete a bay and its room refs |
| 41 | clone_bay(source, target, origin_x, origin_y) | Duplicate a bay |

### Controller Introspection Tools (v3.1 NEW)

| # | Tool | What it does |
|---|------|-------------|
| 42 | list_commands() | All CLI commands with handler functions |
| 43 | show_command_source(command) | Source code of a handler |

### State Comparison Tools (v3.1 NEW)

| # | Tool | What it does |
|---|------|-------------|
| 44 | diff_snapshot(snapshot_name) | Compare current state to a snapshot |
| 45 | validate_state() | Check JSON structure for errors |

---

## State Introspection Details (v3.1)

### Dot-Notation Paths

All state introspection tools use dot-notation paths to navigate
the state.json structure. Examples:

- "site.width" -> state["site"]["width"]
- "bays.A.origin" -> state["bays"]["A"]["origin"]
- "bays.A.corridor.width" -> state["bays"]["A"]["corridor"]["width"]
- "bays.A.apertures.0.type" -> first aperture's type
- "meta.notes" -> project notes
- "print.dpi" -> print resolution
- "bambu.printer_ip" -> Bambu printer IP address

### get_field

Returns the value of a single field. Use this to check specific
properties without loading the entire state.

    get_field("site.width")        -> "OK: site.width = 200.0"
    get_field("bays.A.corridor.enabled") -> "OK: bays.A.corridor.enabled = true"

### set_field

Writes a value directly to state.json. The value is parsed as JSON.
This bypasses CLI validation -- use for fields that have no CLI
command (meta.notes, print.dpi, bambu.*, blocks.*) or when you
know the value is correct.

    set_field("meta.notes", "\"Library renovation\"")
    set_field("print.dpi", "600")
    set_field("legend.enabled", "false")
    set_field("bays.A.origin", "[50.0, 50.0]")

### list_fields

Lists all keys at a given path. Use to explore the schema.

    list_fields("")           -> top-level keys
    list_fields("bays")       -> bay names (A, B, ...)
    list_fields("bays.A")     -> all bay A properties
    list_fields("style")      -> all style properties

---

## Bay Management Details (v3.1)

### add_bay

Creates a new bay with the controller's default settings: 3x3
rectangular grid, 24 ft spacing, walls off, corridor off. Room
references are regenerated automatically.

    add_bay("C", "rectangular", 50.0, 50.0)
    add_bay("D", "radial", 100.0, 100.0)

### remove_bay

Permanently deletes a bay and regenerates room references. Use
save_snapshot first if you might want to undo.

    remove_bay("C")

### clone_bay

Deep copies all properties (walls, corridor, apertures, void)
from an existing bay. Only the label and optionally the origin
change.

    clone_bay("A", "E", 80.0, 80.0)

---

## Controller Introspection Details (v3.1)

### list_commands

Parses controller_cli.py and shows all commands organized by
category: navigation (describe, help, undo), handlers (corridor,
wall, aperture, etc.), and set sub-commands.

### show_command_source

Extracts the complete function definition for a command handler.
Accepts either the command word ("corridor") or the function
name ("cmd_corridor", "_cmd_set_bay").

    show_command_source("wall")       -> source of cmd_wall()
    show_command_source("_cmd_set_bay") -> source of _cmd_set_bay()

Use this before writing extensions with extend_controller.

---

## State Comparison Details (v3.1)

### diff_snapshot

Compares the current state.json to a saved snapshot and lists
all fields that differ. Like "git diff" for your model.

    diff_snapshot("before-experiment")

### validate_state

Checks that state.json is structurally correct: valid JSON,
required sections present, bay fields have correct types. Use
after editing state.json by hand.

This is different from audit_model which checks spatial/ADA
rules. validate_state checks JSON structure.

---

## Audit Engine Details

### audit_model

Runs these checks:

1. Bay overlap: do any bay footprints overlap?
2. Site bounds: do bays extend outside the site boundary?
3. Aperture validity: are gridlines in range? Do apertures fit walls?
4. Apertures without walls: apertures defined but walls are OFF?
5. Corridor sizing: does the corridor fit within the bay?
6. ADA door widths: doors must be at least 3 ft clear
7. ADA corridor widths: corridors must be at least 5 ft for wheelchair passing
8. Room references: do rooms reference bays that exist?
9. Missing labels: every bay should have a label for accessibility

Returns a numbered list of issues, or "0 issues found."

### describe_bay

Gives a narrative description of one bay:

- Grid type, dimensions, area, column count
- Walls and corridor configuration
- Each aperture with dimensions and location
- Void shape and area
- Cell room summary
- Spatial relationships to every other bay (distance and direction)

### describe_circulation

Reports corridor connectivity:

- Which bays have corridors and which do not
- Corridor configuration for each bay (axis, width, loading)
- Doors and portals near each corridor
- Dead-end warnings (corridors with no doors)
- Potential inter-bay connections (bays within 10 ft of each other)

### measure

Measures distance between semantic locations:

- "bay A origin" to "bay B center"
- "site origin" to "bay C void"

Returns straight-line, horizontal (X), and vertical (Y) distances.

---

## Skill Engine Details

### What is a skill?

A skill is a saved sequence of CLI commands with parameters.
Think of it as a macro or recipe. Example:

```json
{
  "name": "add-double-loaded-corridor",
  "description": "Enable a double-loaded corridor on a bay.",
  "version": 1,
  "commands": [
    "corridor {bay} on",
    "corridor {bay} axis {axis}",
    "corridor {bay} width {width}",
    "corridor {bay} loading double"
  ],
  "params": {
    "bay": {"description": "Target bay name", "default": "A"},
    "axis": {"description": "Corridor axis", "default": "x"},
    "width": {"description": "Width in feet", "default": "8"}
  }
}
```

### Using skills

List available skills:

    skill_list()

Show a skill's details:

    skill_show("add-double-loaded-corridor")

Run a skill with default parameters:

    skill_run("add-double-loaded-corridor")

Run with overrides:

    skill_run("add-double-loaded-corridor", "bay=B width=10")

### Creating skills

Save a new skill:

    skill_save(
      "enclose-and-label",
      "Turn on walls and set a label for a bay",
      "wall {bay} on\nset bay {bay} label {label}",
      "bay=A label=Library"
    )

Skills are stored as .json files in the skills/ folder. You can also
create them by hand -- just put a .json file in skills/ following the
format above.

### Included skills

1. add-double-loaded-corridor: Enable corridor with configurable axis and width
2. enclose-bay-with-door: Turn on walls and add a single entry door

---

## Rhino Bridge Details

### How it works

The Rhino watcher (rhino_watcher.py) now starts a TCP listener on
port 1998 alongside its file-polling loop. The MCP server's
rhino_bridge.py connects to this listener to ask read-only questions.

Port 1998 is used (not 1999) to avoid conflicting with rhinomcp.

### Offline mode

If Rhino is not running, every bridge tool returns an OFFLINE message.
No tool ever fails. This is by design: the model lives in state.json,
not in Rhino. You can design, audit, and use skills without Rhino.

### Query types

- "status": layer count, object count, last rebuild time
- "layer_stats": per-layer object counts
- "bounding_box": world-space bounding box of all geometry
- "object_count": total or filtered by layer name

### Script execution

rhino_run_script sends Python code to the watcher's IronPython context.
This is for READ-ONLY queries only. The watcher blocks calls to
geometry-modifying functions like rs.AddLine or rs.DeleteObject.

IMPORTANT: IronPython 2.7 -- use .format() not f-strings.

---

## Controller Extension Details

### What extend_controller does

1. You provide a function name (must start with "cmd_") and Python code
2. The server validates the code with ast.parse()
3. Checks the function signature: must accept (state, tokens)
4. Checks the command word does not conflict with existing commands
5. Appends the function to controller_cli.py
6. Adds a dispatch line to apply_command()
7. Reloads the module with importlib.reload()
8. Records the extension in state.json meta

### Example

Add a command to report total wall area:

```python
extend_controller("cmd_wallarea", '''
def cmd_wallarea(state, tokens):
    total = 0
    for name, bay in state.get("bays", {}).items():
        walls = bay.get("walls", {})
        if not walls.get("enabled"):
            continue
        # Simple perimeter * wall height estimate
        if bay.get("grid_type") == "rectangular":
            nx, ny = bay["bays"]
            sx, sy = bay["spacing"]
            w, h = nx * sx, ny * sy
            perim = 2 * (w + h)
        else:
            continue
        total += perim * 9  # assume 9 ft wall height
    return state, "OK: Estimated total wall area: {:.0f} sq ft".format(total)
''')
```

After this, you can use: run_command("wallarea")

### Safety

- Only adds code. Never modifies existing functions.
- Validates syntax before writing.
- Checks for command name conflicts.
- Tracks all extensions in state.json for auditability.
- To undo: manually remove the function and dispatch line from
  controller_cli.py, or restore a snapshot.

---

## Resources

| URI | What it returns |
|-----|----------------|
| state://current | Full CMA as JSON |
| snapshots://list | Available snapshots |
| help://commands | CLI command reference |
| skills://list | All saved skills |
| extensions://list | All controller extensions |

---

## Prompts

| Prompt | Purpose |
|--------|---------|
| design_review | Get feedback on spatial organization and circulation |
| aperture_audit | Check aperture consistency across bays |
| accessibility_audit | ADA compliance, corridor widths, tactile readability |
| skill_builder | Guide through creating a new skill step by step |

---

## Why We Built Our Own (Not rhinomcp)

rhinomcp is a direct socket bridge to Rhino. It treats Rhino as the
source of truth. That conflicts with our architecture:

| Our approach | rhinomcp |
|-------------|----------|
| JSON state file is truth | Rhino document is truth |
| Rhino is a disposable viewer | Rhino is essential |
| Crash-safe: restart, rebuild | Crash = lost work |
| Semantic model (bays, rooms) | Generic geometry (GUIDs) |
| Screen-reader-first | Visual-first |
| Zero external deps on CLI | Requires C# plugin install |

Our Rhino bridge is a small TCP client that talks to our existing
watcher. No C# plugin needed. No new Rhino installation steps.
Just run the watcher and the bridge auto-connects.

---

## Comparison: Three MCP Approaches

### 1. Layout Jig (this project)

```
Claude -> MCP Server -> Controller CLI -> state.json -> Watcher -> Rhino
```

- 45 tools, semantic, accessibility-first
- JSON is truth, Rhino is viewer
- Skills for reusable command sequences
- Audit engine for validation
- Optional Rhino queries via TCP bridge

### 2. Ethan's TASC/TACT

```
CLI -> state.json -> RhinoConnector (3 fallbacks) -> Rhino
MCP -> tactile image conversion (separate from spatial)
```

- TASC has no MCP server yet (CLI-only)
- TACT has MCP for image-to-tactile conversion
- 3-tier Rhino fallback: socket, RhinoCode CLI, offline
- Click-based CLI with external dependencies

### 3. rhinomcp

```
Claude -> MCP Server -> TCP socket -> C# Plugin -> Rhino document
```

- 24 tools, generic geometry CRUD
- Rhino is truth, no state file
- No semantic layer, no crash recovery
- Arbitrary code execution in Rhino
- Requires C# plugin installation

---

## Quick Start

1. Open Claude Code in the project folder
2. Claude sees the MCP server via .mcp.json
3. Ask Claude to describe the model: "describe the layout"
4. Ask Claude to audit: "run an audit"
5. Ask Claude to measure: "how far is bay A from bay B?"
6. Ask Claude to use a skill: "list skills" then "run the corridor skill on bay B"
7. Ask Claude to create a skill: "save a skill that sets up a 4x2 bay with walls"

All output is screen-reader-friendly: short lines, numbered lists,
OK:/ERROR: prefixes, READY: at the end.
