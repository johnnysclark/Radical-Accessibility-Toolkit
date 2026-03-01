# Radical Accessibility Toolkit — Full Manual

This is the comprehensive manual for the Radical Accessibility Toolkit,
a text-based architectural design platform for blind, low-vision, and
sighted designers. You type commands in a terminal to create building
layouts, generate tactile output, and describe images — no screen required.

This manual covers every tool, every command, and every way to interact
with the system: the interactive CLI, the MCP server through Claude,
editing state.json by hand, and extending the controller with new commands.


## 1. Tools

Layout Jig (controller/controller_cli.py)
  The primary design tool. Define structural grids, walls, doors,
  corridors, rooms, and more via typed or spoken commands.

Image Describer (tools/image-describer/arch_alt_text.py)
  Generates structured text descriptions of architectural images
  using Claude vision.

Tactile Printer (tools/rhino/tactile_print.py)
  Exports the model as watertight STL mesh for 3D printing
  on Bambu Lab printers. No Rhino required.

Rhino Viewer (tools/rhino/rhino_watcher.py)
  Watches the state file and renders geometry in Rhino.
  Read-only viewer — Rhino is never the source of truth.


## 2. Taxonomy

Tool — a major capability module (Layout Jig, Image Describer, etc.).
Command — an individual action within a tool ("set bay A rotation 30").
Skill — a saved sequence of commands, replayable with parameters.
  Stored as JSON in controller/skills/.
MCP function — a Model Context Protocol entry point that Claude calls.
  Maps to one or more commands.


## 3. Files

controller/controller_cli.py: The command processor. This is the brain
of the system. It knows every legal operation on the model and validates
all input.

mcp/mcp_server.py: The MCP server. This wraps the controller so
Claude can call commands as typed function calls. It also has the audit
engine, skill engine, rhino bridge, controller extension tools, state
introspection tools, bay management tools, controller introspection
tools, and state comparison tools. 45 tools total.

controller/auditor.py: Spatial analysis. Validates the model for
overlapping bays, ADA compliance, aperture placement, and missing
labels. Also produces rich text descriptions of individual bays
and corridor connectivity.

controller/skill_manager.py: Reusable command macros. Saves sequences
of commands as JSON files in controller/skills/ and replays them with
different parameters.

tools/rhino/rhino_watcher.py: The Rhino viewer. This script runs
INSIDE Rhino. It watches state.json for changes and rebuilds all
geometry when the file changes. Run it in Rhino with
exec(open(...).read()).

tools/rhino/rhino_client.py: Optional Rhino query client. This does NOT
run inside Rhino. It is imported by the MCP server and talks to the
watcher over TCP port 1998 to ask read-only questions about the 3D
model. Returns OFFLINE messages when Rhino is not running.

controller/state.json: The model itself. This JSON file contains
every fact about the design. It is the single source of truth.

controller/skills/: Folder containing saved skill files (JSON).

tools/rhino/tactile_print.py: Exports the current model as a
watertight STL mesh suitable for 3D printing.


## 4. Requirements

Python 3.8 or later (stdlib only — no pip install needed for the CLI).
Rhino 7 or 8 with IronPython 2.7 (only if you want the visual viewer).
For the MCP server: pip install mcp (the only external dependency).
For image description: a Claude API key.


## 5. Getting Started

### Step 1: Open a terminal

Open cmd.exe (not Windows Terminal, not PowerShell). If you use a
screen reader, NVDA with the Console Toolkit add-on gives the best
results in cmd.exe.

### Step 2: Verify Python works

Type this and press Enter:

    python --version

You should see Python 3.something. If you get an error, Python is
not installed or not on your PATH.

### Step 3: Start the interactive CLI

Type this and press Enter:

    python controller/controller_cli.py

You will see a welcome message and a >> prompt. This is the interactive
command line. You type commands here and the controller executes them.

Type "describe" and press Enter to see the full model.

Type "help" for a list of all commands.

Type "quit" and press Enter when you are done.

### Step 4: Optionally connect Rhino for visual output

Rhino is the viewer. It reads state.json and draws the geometry.
You do not need Rhino to use the CLI or MCP. But if you want to
see the drawing update as you make changes, follow these steps.

There are two Rhino-related files. They do different things:

    tools/rhino/rhino_watcher.py — Runs INSIDE Rhino. This is the viewer.
    tools/rhino/rhino_client.py — Runs OUTSIDE Rhino. This is a query client
                                  used by the MCP server. Do not open this
                                  file in Rhino.

To start the watcher:

1. Open Rhino 8.

2. In the Rhino command line, type EditPythonScript and press Enter.
   This opens the Rhino Python editor.

3. In the editor, paste this one line and run it:

    exec(open(r"path\to\tools\rhino\rhino_watcher.py").read())

4. The watcher prints a startup message to the Rhino command line:

    [PLJ] Watching: path\to\controller\state.json
    [PLJ] TCP listener on 127.0.0.1:1998

5. The watcher reads state.json and draws all geometry. You should
   see columns, walls, corridors, and bays appear in the viewport.

6. From now on, every time the CLI or MCP writes state.json, the
   watcher detects the file change and rebuilds the geometry. You
   do not need to do anything in Rhino. Just work in the terminal
   or with Claude and watch the viewport update.

If Rhino crashes, nothing is lost. The model is in state.json.
Restart Rhino, run the watcher again, and everything rebuilds.


## 6. Using the Interactive CLI

The interactive CLI is the most direct way to work with the model.
You type commands, the controller validates them, mutates the state,
writes state.json to disk, and prints a confirmation.

Start the CLI:

    python controller/controller_cli.py

### Reading the model (no changes)

These commands only read. They do not change anything.

describe — prints the entire model. You will see: schema version,
site dimensions, all style variables, every bay with all properties,
all rooms, legend settings, tactile 3D settings, print settings,
and totals (column count, total area).

list bays — prints a shorter summary showing just the bays.

help — prints the full command reference showing every command family
and its syntax.

status — prints the file path and last modification time of state.json.

### Changing site dimensions

    set site width 250

OK message confirms width is now 250.

    set site height 300

OK message confirms height is now 300.

### Changing bay properties

Move a bay:

    set bay A origin 20 20

This moves the anchor point of Bay A. The anchor is the lower-left
corner of a rectangular bay.

Rotate a bay:

    set bay A rotation 15

This rotates the entire bay 15 degrees counterclockwise around
its anchor point. All gridlines, walls, and apertures rotate with it.

Change the column spacing:

    set bay A spacing 30 30

This changes the distance between columns.

Change the grid size:

    set bay A bays 4 4

This changes the grid from 3x3 to 4x4.

Set a label and braille label:

    set bay A label "Library Wing"
    set bay A braille "lib"

### Changing radial bay properties

Change the number of arms:

    set bay B arms 12

Add more rings:

    set bay B rings 5

Change the arc span:

    set bay B arc_deg 270

Rotate the arc start:

    set bay B arc_start_deg 45

Change ring spacing:

    set bay B ring_spacing 20


## 7. Walls

Turn off walls:

    wall A off

Turn walls on:

    wall A on

Change wall thickness:

    wall A thickness 0.75

Walls are now 0.75 ft (9 inches) thick.


## 8. Corridors

Turn off the corridor:

    corridor A off

Turn the corridor on:

    corridor A on

Change the width:

    corridor A width 10

Change the axis:

    corridor A axis y

The corridor now runs north-south instead of east-west.

Change the loading type:

    corridor A loading single

The corridor is now single-loaded (rooms on one side only).

Move the corridor to a different gridline:

    corridor A position 2

The corridor is now centered on gridline 2 instead of gridline 1.


## 9. Apertures (Doors, Windows, Portals)

List existing apertures on a bay:

    aperture A list

Add a new door. The syntax is:
aperture <bay> add <id> <type> <axis> <gridline> <corner> <width> <height>

    aperture A add d2 door y 0 5 3.5 7

This adds a door called d2 on the y-axis (west/east wall), at
gridline 0 (the west wall), 5 feet from the corner, 3.5 feet wide
and 7 feet tall.

Add a window:

    aperture A add w2 window y 3 10 6 4

Window w2 on the east wall (y-axis gridline 3), 10 feet from corner,
6 feet wide, 4 feet tall.

Add a portal (a large opening without a door):

    aperture A add p1 portal x 3 20 10 9

Portal p1 on the north wall (x-axis gridline 3), 20 feet from corner,
10 feet wide, 9 feet tall.

Modify an aperture:

    aperture A set d2 width 4
    aperture A set d2 hinge end
    aperture A set d2 swing negative

Remove an aperture:

    aperture A remove d2

Aperture fields:
- "id": a unique name you choose (d3, w2, p1, etc.)
- "type": "door", "window", or "portal"
- "axis": "x" means the aperture is on a horizontal wall (south
  or north edge). "y" means it is on a vertical wall (west or east).
- "gridline": which gridline the wall is on (0 is the first).
  For x-axis: 0 is the south wall, the last gridline is the north wall.
  For y-axis: 0 is the west wall, the last gridline is the east wall.
- "corner": how far from the gridline intersection, in feet
- "width": opening width in feet
- "height": opening height in feet
- "hinge": which end the door hinges on ("start" or "end")
- "swing": which direction the door swings ("positive" or "negative")


## 10. Snapshots (Save and Restore)

Save the current state:

    snapshot save clean_state

This writes a copy of the entire state to the history/ folder.

Make some changes, then restore:

    snapshot load clean_state

Everything is back to the way it was when you saved.

List all snapshots:

    snapshot list


## 11. Undo

Undo reverts the last command. It works like Ctrl-Z.

    set bay A rotation 30
    undo

Bay A rotation is back to the previous value.

Note: Undo only works in the interactive CLI. It does not work
through the MCP server because MCP calls are stateless. Through
MCP, use snapshots instead.


## 12. Quit

    quit

This saves the state and exits the CLI.


## 13. Audit Tools

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

### audit_bay

Deep audit of a single bay: grid type, dimensions, area, column count,
walls, corridor, apertures, void, labels, and any issues found.

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

Valid location references:
- "bay A origin" (the anchor point)
- "bay A center" (the center of the footprint)
- "bay A void" (the center of the void)
- "site origin" (the origin of the site)
- "site center" (the center of the site)


## 14. MCP Server

The MCP server (mcp/mcp_server.py) wraps the CLI so that AI
assistants like Claude can call commands as structured function calls.
It speaks the Model Context Protocol so Claude Code, Claude Desktop,
and Cursor can drive the jig conversationally.

The server imports controller/controller_cli.py directly, so every MCP
tool call runs exactly the same code path as typing a command in the
terminal. The canonical model artifact (controller/state.json)
remains the single source of truth.

For full MCP setup, tool reference, and integration details, see
MCP_GUIDE.md.

### Quick MCP setup

Install the MCP package (the only external dependency):

    pip install mcp

Configure your AI client with .mcp.json at the project root:

    {
      "mcpServers": {
        "layout-jig": {
          "command": "python",
          "args": [
            "mcp/mcp_server.py",
            "--state",
            "controller/state.json"
          ]
        }
      }
    }

### All 45 MCP Functions

Querying (read-only, no changes):
 1. describe - full model description
 2. list_bays - compact bay summary
 3. get_state - raw JSON
 4. get_help - command reference
 5. list_apertures - apertures in one bay
 6. list_cells - cells in one bay
 7. list_rooms - all named rooms
 8. list_snapshots - saved snapshots
 9. audit_model - run all validation checks
10. audit_bay - deep audit of one bay
11. describe_bay - rich narrative of one bay
12. describe_circulation - corridor connectivity
13. measure - distance between locations
14. skill_list - available skills
15. skill_show - skill details
16. list_extensions - added commands
17. rhino_status - Rhino connection check
18. rhino_query - ask Rhino a question
19. rhino_run_script - run Python in Rhino
20. get_field - read one JSON field by path
21. list_fields - list keys at a JSON path
22. list_commands - all CLI commands with handlers
23. show_command_source - handler source code
24. diff_snapshot - compare state to snapshot
25. validate_state - check JSON structure

Editing (changes state.json):
26. run_command - raw CLI command
27. set_bay - change bay property
28. set_walls - toggle walls
29. set_corridor - toggle corridor
30. add_aperture - add door/window/portal
31. remove_aperture - remove aperture
32. modify_aperture - change aperture property
33. set_cell - set cell room property
34. auto_corridor_cells - auto-name corridor cells
35. set_site - change site dimensions
36. set_style - change drawing style
37. save_snapshot - save checkpoint
38. load_snapshot - restore checkpoint
39. skill_run - execute a skill
40. skill_save - save a new skill
41. extend_controller - add new command
42. set_field - write one JSON field by path
43. add_bay - create a new bay
44. remove_bay - delete a bay
45. clone_bay - duplicate a bay


## 15. State Introspection

### Dot-notation paths

All state introspection tools use dot-notation paths to navigate
the state.json structure. Examples:

- "site.width" reads state["site"]["width"]
- "bays.A.origin" reads state["bays"]["A"]["origin"]
- "bays.A.corridor.width" reads state["bays"]["A"]["corridor"]["width"]
- "bays.A.apertures.0.type" reads the first aperture's type
- "meta.notes" reads project notes
- "print.dpi" reads print resolution
- "bambu.printer_ip" reads the Bambu printer IP address

### get_field

Returns the value of a single field. Use this to check specific
properties without loading the entire state.

    get_field("site.width")             -> "OK: site.width = 200.0"
    get_field("bays.A.corridor.enabled") -> "OK: bays.A.corridor.enabled = true"

### set_field

Writes a value directly to state.json. The value is parsed as JSON.
This bypasses CLI validation — use for fields that have no CLI
command (meta.notes, print.dpi, bambu.*, blocks.*) or when you
know the value is correct.

    set_field("meta.notes", "\"Library renovation\"")
    set_field("print.dpi", "600")
    set_field("legend.enabled", "false")
    set_field("bays.A.origin", "[50.0, 50.0]")

Important: set_field bypasses CLI validation. The CLI validates
that bay names exist, that door widths meet minimums, that gridline
indices are in range. set_field writes the raw value directly. For
bay configuration, prefer the semantic tools (set_bay, set_walls,
add_aperture) because they validate input.

### list_fields

Lists all keys at a given path. Use to explore the schema.

    list_fields("")           -> top-level keys
    list_fields("bays")       -> bay names (A, B, ...)
    list_fields("bays.A")     -> all bay A properties
    list_fields("style")      -> all style properties


## 16. Bay Management

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


## 17. Skill Manager

### What is a skill?

A skill is a saved sequence of CLI commands with parameters.
Think of it as a macro or recipe. Example:

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

Skills are stored as .json files in the controller/skills/ folder. You
can also create them by hand — just put a .json file in controller/skills/
following the format above.

### Included skills

1. add-double-loaded-corridor: Enable corridor with configurable axis and width
2. enclose-bay-with-door: Turn on walls and add a single entry door


## 18. Rhino Client

### How it works

The Rhino watcher (tools/rhino/rhino_watcher.py) starts a TCP
listener on port 1998 alongside its file-polling loop. The MCP server's
rhino_client.py connects to this listener to ask read-only questions.

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

Important: IronPython 2.7 — use .format() not f-strings.


## 19. Extending the Jig

### What extend_controller does

1. You provide a function name (must start with "cmd_") and Python code
2. The server validates the code with ast.parse()
3. Checks the function signature: must accept (state, tokens)
4. Checks the command word does not conflict with existing commands
5. Appends the function to controller/controller_cli.py
6. Adds a dispatch line to apply_command()
7. Reloads the module with importlib.reload()
8. Records the extension in state.json meta

### Example

Add a command to report total wall area:

    extend_controller("cmd_wallarea", '''
    def cmd_wallarea(state, tokens):
        total = 0
        for name, bay in state.get("bays", {}).items():
            walls = bay.get("walls", {})
            if not walls.get("enabled"):
                continue
            if bay.get("grid_type") == "rectangular":
                nx, ny = bay["bays"]
                sx, sy = bay["spacing"]
                w, h = nx * sx, ny * sy
                perim = 2 * (w + h)
            else:
                continue
            total += perim * 9
        return state, "OK: Estimated total wall area: {:.0f} sq ft".format(total)
    ''')

After this, you can use: run_command("wallarea")

### Adding a command by hand

Step 1: Open controller/controller_cli.py in a text editor.

Step 2: Scroll to just before the line that says:

    def apply_command(state, tokens, state_file=None):

Step 3: Add your function above that line:

    def cmd_floorarea(state, tokens):
        # your code here
        return state, "OK: message"

Step 4: Inside apply_command, add a dispatch line. Find the block
of if statements and add yours before the line that says:

    if cmd != "set":

Add this line right before it:

    if cmd == "floorarea": return cmd_floorarea(state, tokens)

Step 5: Save the file. If the MCP server is running, it will not
pick up the change until it is restarted.

### Prompt template for generating extensions

When asking an AI to write a new command, use this prompt template:

    You are extending the Layout Jig controller.
    The controller lives at controller/controller_cli.py.
    The state file is at controller/state.json.
    Skills are stored in controller/skills/.

    Write a function called cmd_YOURCOMMAND(state, tokens) that:
    - Reads from the state dict
    - Validates input from tokens
    - Mutates state if needed
    - Returns (state, "OK: description of what changed")
    - Returns (state, "ERROR: description") on bad input
    - Uses .format() not f-strings (IronPython 2.7 compatibility)

### Safety

- Only adds code. Never modifies existing functions.
- Validates syntax before writing.
- Checks for command name conflicts.
- Tracks all extensions in state.json for auditability.
- To undo: manually remove the function and dispatch line from
  controller/controller_cli.py, or restore a snapshot.


## 20. Controller Introspection

### list_commands

Parses controller/controller_cli.py and shows all commands organized
by category: navigation (describe, help, undo), handlers (corridor,
wall, aperture, etc.), and set sub-commands.

### show_command_source

Extracts the complete function definition for a command handler.
Accepts either the command word ("corridor") or the function
name ("cmd_corridor", "_cmd_set_bay").

    show_command_source("wall")        -> source of cmd_wall()
    show_command_source("_cmd_set_bay") -> source of _cmd_set_bay()

Use this before writing extensions with extend_controller.


## 21. State Comparison

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

Checks performed:
- Is the file valid JSON?
- Does it have required top-level keys? (schema, meta, site, bays)
- Does each bay have required fields? (grid_type, origin, bays)
- Are field types correct? (origin is [x,y], bays is [nx,ny])
- Are aperture types valid? (door, window, or portal)


## 22. Editing state.json by Hand

You do not need the CLI or MCP to change the model. state.json is a
plain text file. You can open it in any text editor and change values
directly.

### Understanding the structure

The file has these top-level sections:

"schema": The version string. Do not change this unless you are
migrating to a new schema version.

"meta": Created date, last saved date, notes. You can edit notes
freely. The dates are updated automatically when the controller saves.

"site": The site boundary. It has "origin" (an [x, y] pair),
"width" (number), and "height" (number). All units are feet.

"style": Drawing parameters. Column size, lineweights (in mm),
text heights (in feet), corridor dash/gap lengths, and arc segment
count. These control how things look when rendered.

"bays": A dictionary where each key is a bay name (like "A" or "B")
and each value is a bay object. This is the most complex section.

"blocks": Symbol settings for doors, windows, portals, and rooms.
Controls what graphic symbol is drawn for each type.

"rooms": Named rooms with type, label, braille, and hatch info.
Each room references a source bay.

"legend", "tactile3d", "print", "bambu", "tts", "section": Settings
for the legend, 3D printing, 2D printing, Bambu printer, text-to-
speech, and section cuts. Most of these have enable/disable flags.

### Editing a bay by hand

Here is what a rectangular bay looks like in the JSON:

    "A": {
      "grid_type": "rectangular",
      "z_order": 0,
      "origin": [10.0, 10.0],
      "rotation_deg": 0.0,
      "bays": [3, 3],
      "spacing": [24.0, 24.0],
      ...
    }

To move Bay A to position (50, 50), change "origin" to [50.0, 50.0].

To change the spacing, change "spacing" to [30.0, 30.0].

To make it a 4x4 grid, change "bays" to [4, 4].

### Adding an aperture by hand

Apertures are inside a bay's "apertures" list. Each aperture is a
JSON object:

    {
      "id": "d1",
      "type": "door",
      "axis": "x",
      "gridline": 0,
      "corner": 10.0,
      "width": 3.0,
      "height": 7.0,
      "hinge": "start",
      "swing": "positive"
    }

### Enabling walls by hand

Find the bay's "walls" section and change "enabled" to true:

    "walls": {
      "enabled": true,
      "thickness": 0.5
    }

### Enabling a corridor by hand

Find the bay's "corridor" section and change "enabled" to true:

    "corridor": {
      "enabled": true,
      "axis": "x",
      "position": 1,
      "width": 8.0,
      "loading": "double",
      "hatch": "none",
      "hatch_scale": 4.0
    }

Corridor fields:
- "axis": "x" runs east-west, "y" runs north-south
- "position": which gridline the corridor is centered on
- "width": corridor width in feet
- "loading": "single" (rooms on one side) or "double" (rooms on both)
- "hatch": hatch pattern name for the corridor fill, or "none"

### Important: save and verify

After editing state.json by hand, verify it is valid JSON. Load it
with the CLI:

    python controller/controller_cli.py

Type "describe" to see if your changes look right. If the JSON is
malformed (missing comma, unmatched bracket), the CLI will show an
error when it tries to load the file.

If the Rhino watcher is running, it will detect the file change and
rebuild the geometry automatically within half a second.


## 23. How Things Work Under the Hood

### When you type a command in the CLI

1. You type "set bay A rotation 30" and press Enter.
2. The CLI's main loop calls tokenize() to split the input into
   ["set", "bay", "A", "rotation", "30"].
3. It pushes a deep copy of the current state onto the undo stack.
4. It calls apply_command(state, tokens).
5. apply_command sees tokens[0] is "set" and dispatches to
   _cmd_set_bay(state, tokens).
6. _cmd_set_bay validates that "A" is a real bay, "rotation" is
   a valid field, and "30" is a valid number.
7. It sets state["bays"]["A"]["rotation_deg"] = 30.0.
8. It returns (state, "OK: Bay A rotation = 30.0 deg. Was 0.0 deg.")
9. The CLI's main loop prints the message.
10. The CLI calls save_state() which writes state.json atomically.
11. If the Rhino watcher is running, it detects the file change
    within 0.5 seconds and rebuilds all geometry.

### When Claude calls an MCP tool

1. You say "rotate bay A by 30 degrees."
2. Claude reads the set_bay tool description and determines the
   correct parameters: bay="A", field="rotation", value="30".
3. Claude sends a JSON-RPC call to the MCP server over stdin.
4. The MCP server's set_bay function builds the command string:
   "set bay A rotation 30".
5. It calls _run("set bay A rotation 30").
6. _run loads state.json from disk.
7. _run tokenizes the command.
8. _run calls cli.apply_command (same function as the CLI uses).
9. The command executes and returns (state, "OK: ...").
10. _run saves state.json atomically.
11. _run returns the message to Claude.
12. Claude reads the message and tells you what happened.
13. If the Rhino watcher is running, it picks up the file change.

The key point: the controller is the single authority. Steps 6-10
are identical whether the command comes from the CLI or from MCP.

### When you edit state.json by hand

1. You open state.json in a text editor.
2. You change a value and save.
3. If the Rhino watcher is running, it detects the file change
   and rebuilds geometry.
4. The next time you open the CLI or Claude calls an MCP tool,
   the updated state is loaded from disk.

There is no validation when you edit by hand. Always test your
edits by loading the file in the CLI afterward.


## 24. MCP Resources and Prompts

### Resources

state://current — Full CMA as JSON.
snapshots://list — Available snapshots.
help://commands — CLI command reference.
skills://list — All saved skills.
extensions://list — All controller extensions.

### Prompts

design_review — Get feedback on spatial organization and circulation.
aperture_audit — Check aperture consistency across bays.
accessibility_audit — ADA compliance, corridor widths, tactile readability.
skill_builder — Guide through creating a new skill step by step.


## 25. Troubleshooting

### "mcp package not found"

Run this in your terminal:

    pip install mcp

### "No module named controller_cli"

You are not in the right folder, or the path is wrong. Make sure
you are running from the project root and specifying the correct
path to controller/controller_cli.py.

### "state.json not found" or "No state file"

Run from the project root, or specify the full path:

    python controller/controller_cli.py

### CLI shows garbage characters

You may be running in Windows Terminal or PowerShell, which handle
Unicode differently. Use cmd.exe instead.

### Rhino watcher not connecting to the bridge

The bridge connects on TCP port 1998. Make sure:
- The watcher is running INSIDE Rhino (via exec(open(...).read()))
- The watcher printed "[PLJ] TCP listener on 127.0.0.1:1998"
- No firewall is blocking localhost port 1998
- You are not also running rhinomcp (which uses port 1999, but
  check for conflicts)

### SyntaxError when opening a file in Rhino

If you get "SyntaxError: unexpected token 'f'" or similar, you
opened the wrong file in Rhino. Only tools/rhino/rhino_watcher.py
runs inside Rhino. All other Python files (controller/controller_cli.py,
mcp/mcp_server.py, controller/auditor.py, controller/skill_manager.py,
tools/rhino/rhino_client.py) are Python 3 and will not work in Rhino's
IronPython 2.7.

### Snapshot not found

Snapshots are saved in the history/ subfolder as files named
snapshot_yourname.json. Run "snapshot list" to see what is
available. If history/ does not exist, save a snapshot first
and the folder will be created automatically.

### extend_controller says "command already exists"

You tried to add a command with a name that is already taken.
Choose a different name. The built-in commands are: corridor,
wall, aperture, room, cell, block, hatch, legend, tactile3d,
bambu, tts, section, history, snapshot, set, describe, list,
undo, status, help, quit, print.

### extend_controller says "module reload failed"

The function was written to the file but the module could not be
reloaded. This can happen if the function has a runtime error (not
a syntax error). Restart the MCP server to pick up the change.
