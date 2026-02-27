# Layout Jig MCP Server — Guide

## What This Is

The MCP (Model Context Protocol) server is a bridge between AI assistants and the Layout Jig. It wraps the entire CLI command vocabulary — every command Daniel types in the terminal — as structured tools that an AI can call with typed parameters. The AI becomes a collaborator that can read the model, make changes, answer questions, generate code, and critique designs, all through the same state file that drives the Rhino watcher.

The server lives in one file: `mcp_server.py`. It imports `controller_cli.py` directly, so every MCP tool call runs exactly the same code path as typing a command in the terminal. The Rhino watcher doesn't know or care whether a command came from a human or an AI — it just watches the state file for changes.

This is not a separate system. It's another input device for the same platform, like voice or the pegboard. The canonical model artifact (`state.json`) remains the single source of truth.

---

## Why MCP

Without MCP, you'd have to tell the AI your exact CLI syntax and hope it formats the command correctly. With MCP, the AI calls `add_aperture(bay="A", id="d1", type="door", axis="x", gridline=0, corner=5.0, width=3.0, height=7.0)` — typed, validated, no guessing. The AI can also read the model state, list snapshots, and run design reviews without you having to copy-paste state files into the conversation.

MCP also enables the code generation workflow. The AI can inspect the current model, write RhinoPython or Grasshopper scripts targeting that specific geometry, explain the code, and iterate — all while the user learns the underlying language.

---

## Setup

### 1. Install the MCP package

This is the only external dependency in the entire project:

```
pip install mcp
```

Tested with mcp 1.26.0.

### 2. Configure your AI client

**Claude Code** — Create `.mcp.json` at the project root:

```json
{
  "mcpServers": {
    "layout-jig": {
      "command": "python",
      "args": ["layout-jig/mcp_server.py", "--state", "layout-jig/state.json"]
    }
  }
}
```

**Claude Desktop** — Add the same entry to `claude_desktop_config.json` (found in your Claude Desktop settings directory).

**Cursor** — Add it via Settings > MCP Servers with the same command and args.

Adjust the paths to match your folder layout. You can also set the environment variable instead of passing `--state`:

```
LAYOUT_JIG_STATE=path/to/state.json python mcp_server.py
```

### 3. Run standalone (for testing)

```
python layout-jig/mcp_server.py --state layout-jig/state.json
```

The server communicates over stdio using JSON-RPC. All normal print output is redirected to stderr so it doesn't interfere with the protocol. You'll see startup messages like:

```
Layout Jig MCP Server v2.0 starting...
State file: /path/to/state.json
Tools: 21 registered
```

---

## How It Works

```
User: "Add a 3-foot door on the south wall of bay A, 5 feet from the corner"
  |
  v
AI client (Claude) interprets intent
  |
  v
AI calls MCP tool: add_aperture(bay="A", id="d1", type="door",
                                axis="x", gridline=0, corner=5.0,
                                width=3.0, height=7.0)
  |
  v
mcp_server.py receives the JSON-RPC call
  |
  v
Translates to CLI command string: "aperture A add d1 door x 0 5.0 3.0 7.0"
  |
  v
controller_cli.py validates, updates state in memory
  |
  v
Atomic write: state.json.tmp -> fsync -> os.replace -> state.json
  |
  v
Rhino watcher detects mtime change on next idle cycle -> rebuilds geometry
  |
  v
AI receives confirmation: "OK: Added door d1 to Bay A, x-axis gridline 0,
  corner 5.0 ft, width 3.0 ft, height 7.0 ft."
```

Every tool call follows this pattern: load state from disk, run the command, save state back to disk, return the confirmation message. The MCP server is stateless between calls — it reads and writes the same `state.json` that the terminal CLI uses.

---

## The 21 Tools

### Read Tools (no state mutation)

These tools inspect the model without changing anything.

**`describe()`** — Full text description of the entire model. Returns every setting: site dimensions, style variables, each bay with its grid type, origin, rotation, spacing, walls, apertures, corridor, void, labels, cell rooms — plus rooms, blocks, legend, tactile 3D, printer config, section cut, hatch library, print settings, and totals.

Example response (abbreviated):

```
PLAN LAYOUT JIG — Full Model Description

Schema: plan_layout_jig_v2.3
Created: 2026-02-15 09:30:00   Last saved: 2026-02-27 14:22:18

SITE: 200 x 300 ft  (60,000 sq ft)
  Origin: (0.0, 0.0)

BAY A  (rectangular, z_order=0)  anchor (18.0, 8.0), rotated 30.0 deg
  6 bays across @ 24 ft
  3 bays deep @ 24 ft
  Footprint: 144 x 72 ft   28 columns   area: 10,368 sq ft
  Corridor: double-loaded, east-west (x-axis), gridline 1, 8 ft wide
  Walls: ON, thickness 0.500 ft (6.0 inches)
  Apertures: 3
    d1: door  axis=x  gridline=0  corner=5.0 ft  width=3.0 ft  height=7.0 ft
    w1: window  axis=y  gridline=2  corner=8.0 ft  width=6.0 ft  height=4.0 ft
    p1: portal  axis=x  gridline=1  corner=0.0 ft  width=8.0 ft  height=9.0 ft

TOTALS: 28 columns across 1 bays
  Combined bay area: 10,368 sq ft
```

**`list_bays()`** — Compact summary of all bays in one view.

**`get_state()`** — The raw JSON contents of state.json. Useful when the AI needs to inspect specific values or generate code targeting exact coordinates.

**`get_help()`** — The full CLI command reference (all commands, syntax, examples).

**`list_apertures(bay)`** — All doors, windows, and portals on a specific bay with full details.

**`list_cells(bay)`** — All cells in a rectangular bay's grid with names, areas, and hatch patterns.

**`list_rooms()`** — All named rooms across the entire model.

**`list_snapshots()`** — All saved snapshots with file sizes and timestamps.

---

### Bay Configuration

**`set_bay(bay, field, value)`** — The workhorse for configuring bays. The `field` parameter determines what gets set.

Examples:

```
set_bay(bay="A", field="origin", value="20 10")
  -> moves bay A's anchor point to (20, 10)

set_bay(bay="A", field="rotation", value="30")
  -> rotates bay A to 30 degrees

set_bay(bay="A", field="bays", value="6 3")
  -> sets bay A to a 6x3 grid (6 columns across, 3 deep)

set_bay(bay="A", field="spacing", value="24 24")
  -> sets uniform 24-foot spacing in both directions

set_bay(bay="A", field="spacing_x", value="20 20 25 25 20 20")
  -> sets irregular x-spacing (one value per bay span)

set_bay(bay="A", field="grid_type", value="radial")
  -> switches bay A to a radial grid

set_bay(bay="A", field="rings", value="6")
  -> sets 6 concentric rings (radial grid)

set_bay(bay="A", field="arms", value="12")
  -> sets 12 radial arms (radial grid)

set_bay(bay="A", field="arc_deg", value="180")
  -> limits the radial grid to a 180-degree arc

set_bay(bay="A", field="label", value="Main Hall")
  -> sets the display label

set_bay(bay="A", field="z_order", value="1")
  -> changes draw order (higher draws on top)
```

---

### Walls and Corridors

**`set_walls(bay, enabled, thickness)`** — Toggle walls and optionally set thickness.

```
set_walls(bay="A", enabled=True)
  -> turns walls on with default 6-inch thickness

set_walls(bay="A", enabled=True, thickness=0.75)
  -> turns walls on at 9 inches thick

set_walls(bay="A", enabled=False)
  -> turns walls off
```

**`set_corridor(bay, enabled, field, value)`** — Toggle corridor and configure properties.

```
set_corridor(bay="A", enabled=True)
  -> turns corridor on with defaults (x-axis, double-loaded, 8 ft wide)

set_corridor(bay="A", enabled=True, field="width", value="10")
  -> turns corridor on and sets width to 10 feet

set_corridor(bay="A", enabled=True, field="axis", value="y")
  -> north-south corridor

set_corridor(bay="A", enabled=True, field="position", value="2")
  -> corridor centered on gridline 2

set_corridor(bay="A", enabled=True, field="loading", value="single")
  -> single-loaded corridor (rooms on one side only)

set_corridor(bay="A", enabled=True, field="hatch", value="diagonal")
  -> applies diagonal hatch pattern to corridor zone
```

---

### Apertures

**`add_aperture(bay, id, type, axis, gridline, corner, width, height)`** — Add a door, window, or portal. Walls must be enabled first.

```
add_aperture(bay="A", id="d1", type="door", axis="x", gridline=0,
             corner=5.0, width=3.0, height=7.0)
  -> 3-foot door on the south wall, 5 feet from the left corner, 7 feet tall

add_aperture(bay="A", id="w1", type="window", axis="y", gridline=2,
             corner=8.0, width=6.0, height=4.0)
  -> 6-foot window on the 3rd vertical gridline

add_aperture(bay="A", id="p1", type="portal", axis="x", gridline=1,
             corner=0.0, width=8.0, height=9.0)
  -> full-height 8-foot portal at the corridor gridline
```

Axis and gridline explanation:
- `axis="x"` means the aperture is on a horizontal wall (east-west). `gridline=0` is the bottom wall, `gridline=1` is the next horizontal gridline up, etc.
- `axis="y"` means the aperture is on a vertical wall (north-south). `gridline=0` is the left wall, `gridline=1` is the next vertical gridline right, etc.
- `corner` is the distance in feet from the gridline intersection to the start of the opening.

**`remove_aperture(bay, id)`** — Remove an aperture by ID.

**`modify_aperture(bay, id, field, value)`** — Change one property of an existing aperture.

```
modify_aperture(bay="A", id="d1", field="width", value="4")
  -> widens door d1 to 4 feet

modify_aperture(bay="A", id="d1", field="hinge", value="end")
  -> moves the hinge to the other side

modify_aperture(bay="A", id="d1", field="swing", value="negative")
  -> reverses the door swing direction
```

---

### Cells and Rooms

Cells subdivide a rectangular bay's grid into named rooms. Each cell is identified by its column and row index (0-based). Cells with the same name form a room, and the system calculates combined areas automatically.

**`set_cell(bay, col, row, field, value)`** — Set a property on one cell.

```
set_cell(bay="A", col=0, row=0, field="name", value="Office")
  -> names the bottom-left cell "Office"

set_cell(bay="A", col=1, row=0, field="name", value="Office")
  -> adds the adjacent cell to the same "Office" room (areas combine)

set_cell(bay="A", col=0, row=0, field="hatch", value="crosshatch")
  -> applies a crosshatch pattern for tactile differentiation

set_cell(bay="A", col=2, row=0, field="hatch", value="dots")
  -> dot pattern so a blind reader can distinguish rooms by touch
```

**`auto_corridor_cells(bay)`** — Automatically names all cells overlapping the corridor zone as "Corridor".

---

### Site and Style

**`set_site(field, value)`** — Set site boundary dimensions.

**`set_style(field, value)`** — Control lineweights, text sizes, and drawing parameters. These directly affect the PIAF tactile output quality.

```
set_style(field="heavy", value="1.4")
  -> heavy lineweight (columns/structure) at 1.4 mm

set_style(field="wall", value="0.25")
  -> wall lineweight at 0.25 mm

set_style(field="text_height", value="0.5")
  -> label text at 0.5 ft height

set_style(field="arc_segments", value="32")
  -> smoother arcs for radial grids
```

---

### Snapshots

Snapshots are named checkpoints saved alongside the state file. In MCP mode, these replace the in-memory undo stack (which doesn't persist between separate tool calls).

**`save_snapshot(name)`** — Save current state.

```
save_snapshot(name="before-redesign")
  -> saves to history/snapshot_before-redesign.json
```

**`load_snapshot(name)`** — Restore a previous state.

**`list_snapshots()`** — See what's available.

---

### Escape Hatch

**`run_command(command)`** — Pass any raw CLI command string. Use this for commands not covered by the typed tools, or for advanced operations.

```
run_command(command="block door symbol arc_swing")
run_command(command="legend position bottom-left")
run_command(command="tactile3d wall_height 12")
run_command(command="section x 50")
run_command(command="section export ./my_section.svg")
run_command(command="bambu preview")
run_command(command="bambu export")
run_command(command="hatch list")
run_command(command="tts on")
run_command(command="history list")
```

---

## Resources

Resources let the AI read context passively without calling a tool.

- `state://current` — The full JSON state file (the Canonical Model Artifact)
- `snapshots://list` — All saved snapshots with sizes and timestamps
- `help://commands` — The complete CLI command reference

---

## Prompt Templates

Pre-built prompts for common design workflows. These load the current model state and frame a specific task for the AI.

**`design_review`** — Loads the full model description and asks the AI to critique spatial organization, circulation, room naming, hatch differentiation for tactile readability, and potential issues.

**`aperture_audit`** — Lists every aperture across every bay and asks the AI to check for missing doors in corridors, window placement, portal sizing, and consistent heights.

---

## Example Conversations

### Starting a new design

```
User: Start a new school layout. I need a main building 6 bays by 3 bays
      at 24-foot spacing, with a central east-west corridor.

AI calls: set_bay(bay="A", field="bays", value="6 3")
AI calls: set_bay(bay="A", field="spacing", value="24 24")
AI calls: set_corridor(bay="A", enabled=True, field="axis", value="x")
AI calls: set_corridor(bay="A", enabled=True, field="width", value="8")
AI calls: set_walls(bay="A", enabled=True)
AI calls: describe()

AI: OK. Bay A is now a 6x3 rectangular grid at 24-foot spacing.
    Footprint is 144 x 72 feet with 28 columns. The corridor runs
    east-west at gridline 1, 8 feet wide, double-loaded. Walls are
    on at 6 inches thick. What rooms do you want?
```

### Adding rooms and doors

```
User: Name the top row of cells "Classroom" and the bottom row "Lab".
      Put crosshatch on classrooms and dots on labs. Then add a door
      to each classroom from the corridor.

AI calls: set_cell(bay="A", col=0, row=2, field="name", value="Classroom")
          ... (repeats for cols 1-5, row 2)
AI calls: set_cell(bay="A", col=0, row=2, field="hatch", value="crosshatch")
          ... (repeats for all classroom cells)
AI calls: set_cell(bay="A", col=0, row=0, field="name", value="Lab")
          ... (repeats for cols 0-5, row 0)
AI calls: set_cell(bay="A", col=0, row=0, field="hatch", value="dots")
          ... (repeats for all lab cells)
AI calls: auto_corridor_cells(bay="A")
AI calls: add_aperture(bay="A", id="d1", type="door", axis="x",
                       gridline=2, corner=10.0, width=3.0, height=7.0)
          ... (repeats for each classroom)

AI: Done. 6 classrooms across the top with crosshatch, 6 labs across
    the bottom with dots, corridor cells auto-marked. 6 doors connect
    classrooms to the corridor at gridline 2.
```

### Design review

```
User: Review my design. What's missing?

AI uses prompt template: design_review

AI: Looking at the model:
    1. The labs on the south side have no doors. Add apertures on
       gridline 1 to connect labs to the corridor.
    2. No windows on the exterior walls. Consider adding windows on
       gridlines 0 and 3 for natural light.
    3. Hatch patterns are good for tactile differentiation — crosshatch
       vs. dots will read clearly on PIAF paper.
    4. No snapshot saved yet. Save one before adding more apertures.
```

### Working with multiple bays

```
User: Add a radial auditorium east of the main building.

AI calls: run_command(command="set bay B grid_type radial")
AI calls: set_bay(bay="B", field="origin", value="180 40")
AI calls: set_bay(bay="B", field="rings", value="5")
AI calls: set_bay(bay="B", field="ring_spacing", value="15")
AI calls: set_bay(bay="B", field="arms", value="10")
AI calls: set_bay(bay="B", field="arc_deg", value="180")
AI calls: set_bay(bay="B", field="z_order", value="1")
AI calls: list_bays()

AI: Bay B is a radial half-circle east of the main building.
    5 rings at 15-foot spacing, 10 arms, 180-degree arc.
    Outer radius 75 feet.
```

### 3D printing workflow

```
User: I want to 3D print this for design review.

AI calls: run_command(command="tactile3d on")
AI calls: run_command(command="tactile3d wall_height 9")
AI calls: run_command(command="tactile3d cut_height 4")
AI calls: run_command(command="bambu config print_scale 200")
AI calls: run_command(command="bambu preview")

AI: Tactile 3D is on. Walls at 9 feet, section cut at 4 feet.
    At 1:200 scale on the P1S: 219.5 x 109.7 x 6.1 mm.
    Fits on the build plate. 1,440 triangles.
    Say "bambu export" to write the STL, or "bambu print" for
    the full pipeline (export, slice, upload, print).
```

---

## How Undo Works in MCP Mode

The terminal CLI has an in-memory undo stack powered by `copy.deepcopy(state)` before each mutation. This stack does not persist between MCP calls because each tool invocation loads fresh from disk.

Instead, MCP mode uses named snapshots:

```
save_snapshot(name="before-big-change")
... make changes ...
... something went wrong ...
load_snapshot(name="before-big-change")
  -> state restored to the checkpoint
```

The numbered history system (`history/0001.json`, `0002.json`, etc.) is also available. Each mutating command writes a numbered history file, so you can trace every change.

---

## Extending the MCP Server

The MCP server is designed to grow with the platform. Adding a new tool follows a simple pattern.

### Adding a new tool

Every tool is a Python function decorated with `@mcp.tool()`:

```python
@mcp.tool()
def my_new_tool(param1: str, param2: float) -> str:
    """Description of what this tool does.

    This docstring becomes the tool description that the AI reads
    to understand when and how to use the tool.

    Args:
        param1: What this parameter means
        param2: What this parameter means
    """
    return _run(f"my_cli_command {param1} {param2}")
```

The `_run()` helper handles the full cycle: load state from disk, tokenize and execute the command via `controller_cli.apply_command()`, save state back to disk, return the confirmation message.

If the tool needs read-only access (no state mutation), load state directly:

```python
@mcp.tool()
def my_read_tool(bay: str) -> str:
    """Read something from the model without changing it."""
    state = _load_state()
    # ... inspect state ...
    return result_string
```

### Adding a new resource

```python
@mcp.resource("myresource://name")
def resource_my_data() -> str:
    """Description of this resource."""
    state = _load_state()
    return json.dumps(some_data, indent=2)
```

### Adding a new prompt template

```python
@mcp.prompt()
def my_workflow() -> str:
    """Description of the workflow."""
    state = _load_state()
    desc = cli.describe(state)
    return (
        f"Here is the current model:\n\n{desc}\n\n"
        f"Please do the following:\n"
        f"1. First thing\n"
        f"2. Second thing\n"
    )
```

### Adding a new skill to the platform

When a new skill is added to the CLI (e.g., structural analysis), extending MCP coverage follows this pattern:

1. The new skill adds commands to `controller_cli.py` via the `apply_command` dispatch.
2. The MCP server adds typed tool wrappers for those commands.
3. Read-only inspection tools are added for the new skill's state.
4. A prompt template is added for the skill's primary workflow.
5. The escape hatch (`run_command`) covers any commands not yet wrapped.

The key constraint: every MCP tool must ultimately call through `_run()` or `_load_state()`. The MCP server never modifies state directly — it always goes through the CLI's command dispatch. This guarantees that MCP and terminal commands produce identical results.

### Example: wrapping a hypothetical structural skill

If the CLI gained structural analysis commands, the MCP wrapper would look like:

```python
@mcp.tool()
def set_structural_load(bay: str, load_psf: float) -> str:
    """Set the design load for a bay in pounds per square foot.

    Args:
        bay: Bay name (e.g. "A")
        load_psf: Design load in PSF
    """
    return _run(f"structural {bay} load {load_psf}")


@mcp.tool()
def check_structure(bay: str) -> str:
    """Run a structural check on a bay and report pass/fail.

    Args:
        bay: Bay name (e.g. "A")
    """
    return _run(f"structural {bay} check")


@mcp.prompt()
def structural_review() -> str:
    """Review structural adequacy of all bays."""
    state = _load_state()
    desc = cli.describe(state)
    return (
        f"Current model:\n\n{desc}\n\n"
        f"Review the structural configuration of each bay:\n"
        f"1. Are design loads reasonable for the room types?\n"
        f"2. Do column spacings support the specified loads?\n"
        f"3. Are there any bays that need structural attention?"
    )
```

---

## Technical Details

### stdout vs stderr

MCP communicates over stdio using JSON-RPC. The server redirects Python's `print()` to stderr at startup so that CLI debug output doesn't corrupt the protocol stream.

### State file concurrency

There is no file locking. The MCP server and the terminal CLI should not write to the same state file simultaneously. In practice this is fine — they take turns. The Rhino watcher is read-only.

### Migration

The MCP server applies the same schema migrations as the terminal CLI on every load. Old state files always work.

### Error handling

If a command fails, the tool returns a string starting with `ERROR:`. The AI sees this and can retry, adjust parameters, or ask the user for clarification. The state file is not modified on error.

---

## Full CLI Command Reference

For completeness, here is every command available through the terminal CLI (and therefore through `run_command`):

```
describe / d ............. Full model description
list bays / l bays ....... Compact bay table
undo ..................... Revert last change
status ................... State file path and timestamp
help / h / ? ............. Command reference
quit / q / exit .......... Save and exit

SITE AND STYLE:
  set site width|height <ft>
  set column size <ft>
  set style heavy|light|corridor|wall|text_height|braille_height|
           dash_len|gap_len|bg_pad|label_offset|arc_segments <value>

BAY CONFIGURATION:
  set bay <name> grid_type rectangular|radial
  set bay <name> z_order|origin|rotation|bays|spacing <value(s)>
  set bay <name> spacing_x <s1 s2 ...>  /  spacing_y <s1 s2 ...>
  set bay <name> rings|ring_spacing|arms|arc_deg|arc_start_deg <value>
  set bay <name> void_center <x y>  /  void_size <w h>  /  void_shape rect|circle
  set bay <name> label|braille <text>

CORRIDOR:
  corridor <bay> on|off
  corridor <bay> axis|position|width|loading|hatch|hatch_scale <value>

WALLS:
  wall <bay> on|off
  wall <bay> thickness <feet>

APERTURES:
  aperture <bay> add <id> <door|window|portal> <x|y> <gridline> <corner> <width> <height>
  aperture <bay> remove <id>
  aperture <bay> set <id> <field> <value>
     fields: type, axis, gridline, corner, width, height, hinge, swing
  aperture <bay> list

BLOCKS:
  block list
  block <door|window|portal|room> [field] [value]

ROOMS:
  room list  /  room refresh
  room <id> label|braille|hatch|hatch_scale|hatch_rotation <value>
  room add <id> bay|void|landscape [bay_name]
  room remove <id>

CELLS:
  cell <bay> list
  cell <bay> rooms
  cell <bay> <col,row> name|label|braille|hatch|hatch_scale|hatch_rotation <value>
  cell <bay> <c0,r0-c1,r1> name|label|hatch <value>  (range)
  cell <bay> <col,row> clear
  cell <bay> clear_all
  cell <bay> auto_corridor

LEGEND:
  legend on|off
  legend position bottom-right|bottom-left|top-right|top-left|custom [x y]
  legend width|title|title_braille <value>
  legend swatch_size|row_height|text_height|braille_height|padding|border_weight_mm <value>
  legend show_braille|show_hatches|show_apertures on|off

TACTILE 3D:
  tactile3d on|off
  tactile3d wall_height|cut_height|floor_thickness <feet>
  tactile3d floor on|off
  tactile3d auto_export on|off
  tactile3d export_path <filepath>
  tactile3d scale_factor <value>
  tactile3d export

BAMBU PRINTER:
  bambu config ip|access_code|serial|printer_model|print_scale|stl_path|slicer_path <value>
  bambu preview
  bambu export [path]
  bambu slice
  bambu send [path]
  bambu print
  bambu status

HATCH LIBRARY:
  hatch list
  hatch path <folder>
  hatch add <name> <source_image_path>

SECTION CUT:
  section x|y <offset>
  section preview
  section export [path]
  section list
  section clear

HISTORY AND SNAPSHOTS:
  history list
  history count
  snapshot save <name>
  snapshot load <name>
  snapshot list

TEXT-TO-SPEECH:
  tts on|off
  tts rate <-10..10>
```
