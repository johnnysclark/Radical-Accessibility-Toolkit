# Layout Jig v3.1 Test Manual

This folder is a self-contained test copy of the Layout Jig system.
Everything you need is here. No other folders are required.

This manual walks through every way to interact with the Layout Jig:
the interactive CLI, the MCP server through Claude, editing state.json
by hand, and extending the controller with new commands. Each section
has step-by-step instructions and tells you exactly what to expect.

---

## What Is in This Test Project

The test project has a small building with two structural bays on a
200 by 200 foot site.

Bay A is called "Bay A - Square." It is a rectangular structural grid
with 3 columns across and 3 columns deep, making 9 structural sections.
The columns are spaced 24 feet apart in both directions, so the bay is
72 feet wide and 72 feet deep. Its anchor point (lower-left corner) is
at position (10, 10) on the site. It has walls turned on at 0.5 foot
thickness. It has a double-loaded corridor running east-west along the
x-axis at gridline 1, 8 feet wide. It has two apertures: a door called
d1 on the south wall (x-axis gridline 0, 3 feet wide, 7 feet tall) and
a window called w1 on the west wall (y-axis gridline 0, 6 feet wide,
4 feet tall). It has a rectangular void centered at (46, 46), sized
20 by 20 feet.

Bay B is called "Bay B - Circular." It is a radial structural grid
centered at position (140, 130) on the site. It has 9 arms radiating
outward and 3 concentric rings spaced 20 feet apart, making the outer
ring 60 feet from center. The arc spans a full 360 degrees. It has no
walls, no corridor, and no apertures. It has a circular void centered
at (140, 130), sized 15 by 15 feet.

---

## Files in This Folder

controller_cli.py: The command processor. This is the brain of the
system. It knows every legal operation on the model and validates
all input. About 2,000 lines of Python.

mcp_server.py: The MCP server. This wraps the controller so Claude
can call commands as typed function calls. It also has the audit
engine, skill engine, rhino bridge, controller extension tools,
state introspection tools, bay management tools, controller
introspection tools, and state comparison tools. 45 tools total.

audit_engine.py: Spatial analysis. Validates the model for
overlapping bays, ADA compliance, aperture placement, and missing
labels. Also produces rich text descriptions of individual bays
and corridor connectivity.

skill_engine.py: Reusable command macros. Saves sequences of
commands as JSON files in the skills/ folder and replays them
with different parameters.

rhino_bridge.py: Optional Rhino connection. Talks to the Rhino
watcher over TCP port 1998 to ask questions about the 3D model.
Returns OFFLINE messages when Rhino is not running.

state.json: The model itself. This JSON file contains every fact
about the design. It is the single source of truth.

run_tests.py: Automated test suite. Runs 115 tests covering every
engine and command family.

skills/: Folder containing saved skill files (JSON).

history/: Folder where snapshots are stored.

---

## Getting Started

### Step 1: Open a terminal

Open cmd.exe (not Windows Terminal, not PowerShell). If you use a
screen reader, NVDA with the Console Toolkit add-on gives the best
results in cmd.exe.

### Step 2: Navigate to this folder

Type this and press Enter:

    cd "C:\Users\su-jsclark2\Desktop\_CONTENT\Accessibility\CLI\CLI JIG TEST"

### Step 3: Verify Python works

Type this and press Enter:

    python --version

You should see Python 3.something. If you get an error, Python is
not installed or not on your PATH.

### Step 4: Run the automated tests

Type this and press Enter:

    python run_tests.py

This runs 115 tests in about 2 seconds. Every line should say PASS.
The last line should say ALL TESTS PASSED. If any test fails, something
is wrong with the setup.

### Step 5: Start the interactive CLI

Type this and press Enter:

    python controller_cli.py --state state.json

You will see a welcome message and a >> prompt. This is the interactive
command line. You type commands here and the controller executes them.

Type "describe" and press Enter to see the full model.

Type "quit" and press Enter when you are done.

---

## Part 1: Using the Interactive CLI

The interactive CLI is the most direct way to work with the model.
You type commands, the controller validates them, mutates the state,
writes state.json to disk, and prints a confirmation.

Start the CLI:

    python controller_cli.py --state state.json

### Reading the model (no changes)

These commands only read. They do not change anything.

Step 1: Type "describe" and press Enter.

    describe

This prints the entire model. You will see:
- Schema version (plan_layout_jig_v2.3)
- Site dimensions (200 x 200 ft)
- All style variables (lineweights, text heights)
- Bay A with all its properties
- Bay B with all its properties
- All rooms
- Legend settings
- Tactile 3D settings
- Print settings
- Totals (column count, total area)

This is long output. It is the most complete view of the model.

Step 2: Type "list bays" and press Enter.

    list bays

This prints a shorter summary showing just the bays. You will see
Bay A (rectangular, 16 columns) and Bay B (radial, 28 columns).

Step 3: Type "help" and press Enter.

    help

This prints the full command reference showing every command family
and its syntax.

Step 4: Type "status" and press Enter.

    status

This prints the file path and last modification time of state.json.

### Changing site dimensions

Step 1: Make the site wider.

    set site width 250

Expected output: OK message confirming width is now 250.

Step 2: Make the site taller.

    set site height 300

Expected output: OK message confirming height is now 300.

Step 3: Verify by describing the model.

    describe

Look at the SITE line. It should say 250 x 300 ft.

Step 4: Put it back.

    set site width 200
    set site height 200

### Changing bay properties

Step 1: Move Bay A to a new position.

    set bay A origin 20 20

This moves the anchor point of Bay A from (10, 10) to (20, 20).
The anchor is the lower-left corner of a rectangular bay.

Step 2: Rotate Bay A.

    set bay A rotation 15

This rotates the entire bay 15 degrees counterclockwise around
its anchor point. All gridlines, walls, and apertures rotate with it.

Step 3: Change the column spacing.

    set bay A spacing 30 30

This changes the distance between columns from 24 ft to 30 ft in
both directions. The bay is now 90 x 90 ft instead of 72 x 72 ft.

Step 4: Change the grid size.

    set bay A bays 4 4

This changes the grid from 3x3 to 4x4. There are now 16 structural
sections instead of 9, and 25 columns instead of 16.

Step 5: Set a label and braille label.

    set bay A label "Library Wing"
    set bay A braille "lib"

These change the text that appears on the drawing and in the Braille
legend.

Step 6: Reset everything back.

    set bay A origin 10 10
    set bay A rotation 0
    set bay A spacing 24 24
    set bay A bays 3 3
    set bay A label "Bay A - Square"

### Changing radial bay properties

Step 1: Change the number of arms.

    set bay B arms 12

Bay B now has 12 radial arms instead of 9.

Step 2: Add more rings.

    set bay B rings 5

Bay B now has 5 concentric rings. The outer ring is at 100 ft
from center (5 rings times 20 ft spacing).

Step 3: Change the arc span.

    set bay B arc_deg 270

Bay B is no longer a full circle. It spans 270 degrees, leaving
a 90-degree gap.

Step 4: Rotate the arc start.

    set bay B arc_start_deg 45

The arc now starts at 45 degrees instead of 0.

Step 5: Reset.

    set bay B arms 9
    set bay B rings 3
    set bay B ring_spacing 20
    set bay B arc_deg 360
    set bay B arc_start_deg 0

### Walls

Step 1: Turn off walls on Bay A.

    wall A off

The walls are now disabled. The bay is an open structural grid.

Step 2: Turn walls back on.

    wall A on

Step 3: Change wall thickness.

    wall A thickness 0.75

Walls are now 0.75 ft (9 inches) thick instead of 0.5 ft (6 inches).

Step 4: Reset.

    wall A thickness 0.5

Step 5: Try walls on Bay B (which starts without walls).

    wall B on

Bay B now has walls.

    wall B off

Reset.

### Corridors

Step 1: Turn off the corridor on Bay A.

    corridor A off

The corridor is now disabled.

Step 2: Turn it back on.

    corridor A on

Step 3: Change the width.

    corridor A width 10

The corridor is now 10 ft wide instead of 8 ft.

Step 4: Change the axis.

    corridor A axis y

The corridor now runs north-south instead of east-west.

Step 5: Change the loading type.

    corridor A loading single

The corridor is now single-loaded (rooms on one side only).

Step 6: Move the corridor to a different gridline.

    corridor A position 2

The corridor is now centered on gridline 2 instead of gridline 1.

Step 7: Reset everything.

    corridor A axis x
    corridor A position 1
    corridor A width 8
    corridor A loading double

### Apertures (doors, windows, portals)

Step 1: List existing apertures on Bay A.

    aperture A list

You will see two apertures: d1 (door) and w1 (window).

Step 2: Add a new door. The syntax is:
aperture <bay> add <id> <type> <axis> <gridline> <corner> <width> <height>

    aperture A add d2 door y 0 5 3.5 7

This adds a door called d2 on the y-axis (west/east wall), at
gridline 0 (the west wall), 5 feet from the corner, 3.5 feet wide
and 7 feet tall.

Step 3: Add a window.

    aperture A add w2 window y 3 10 6 4

Window w2 on the east wall (y-axis gridline 3), 10 feet from corner,
6 feet wide, 4 feet tall.

Step 4: Add a portal (a large opening without a door).

    aperture A add p1 portal x 3 20 10 9

Portal p1 on the north wall (x-axis gridline 3), 20 feet from corner,
10 feet wide, 9 feet tall (full height).

Step 5: List all apertures to see them.

    aperture A list

You should see d1, w1, d2, w2, and p1.

Step 6: Modify an aperture. Change the door width.

    aperture A set d2 width 4

Door d2 is now 4 feet wide.

Step 7: Change the hinge side.

    aperture A set d2 hinge end

The hinge is now on the "end" side instead of "start."

Step 8: Change the swing direction.

    aperture A set d2 swing negative

The door now swings the opposite direction.

Step 9: Remove the apertures you added.

    aperture A remove p1
    aperture A remove w2
    aperture A remove d2

Step 10: Verify only the originals remain.

    aperture A list

Should show only d1 and w1.

### Snapshots (save and restore)

Step 1: Save the current state.

    snapshot save clean_state

This writes a copy of the entire state to the history/ folder.

Step 2: Make some destructive changes.

    set site width 999
    set bay A rotation 45
    corridor A off

Step 3: Realize you made a mistake. Restore the snapshot.

    snapshot load clean_state

Everything is back to the way it was when you saved. Site is 200 ft,
Bay A has no rotation, corridor is on.

Step 4: List all snapshots.

    snapshot list

You will see clean_state in the list.

### Undo (interactive CLI only)

Undo reverts the last command. It works like Ctrl-Z.

Step 1: Make a change.

    set bay A rotation 30

Step 2: Undo it.

    undo

Bay A rotation is back to 0.

Note: Undo only works in the interactive CLI. It does not work
through the MCP server because MCP calls are stateless. Through
MCP, use snapshots instead.

### Quit

    quit

This saves the state and exits the CLI.

---

## Part 2: Using the MCP Server Through Claude

The MCP server lets Claude call commands on your behalf. Instead of
you typing commands into the CLI, you speak or type natural language
and Claude figures out which tool to call.

### Setting up the MCP server

Step 1: Create a file called .mcp.json in the CLI JIG TEST folder
with this content:

    {
      "mcpServers": {
        "layout-jig": {
          "command": "python",
          "args": [
            "mcp_server.py",
            "--state",
            "state.json"
          ]
        }
      }
    }

Step 2: Open Claude Code in the CLI JIG TEST folder.

Claude Code reads .mcp.json on startup. It launches the MCP server
as a background process. Claude now has access to all 45 tools.

### Querying the model through MCP

These are things you can say to Claude. Claude will call the
appropriate MCP tool and read back the result.

To get the full model description, say:

    "Describe the current layout."

Claude calls the describe() tool. This is the same output you get
from typing "describe" in the CLI. Claude will summarize it for you,
reading back the important parts: site dimensions, bay positions,
corridor configuration, aperture list.

To get just the bay list, say:

    "List all the bays."

Claude calls list_bays(). Shorter output, just the bay names and
key properties.

To get the raw JSON state, say:

    "Show me the raw state JSON."

Claude calls get_state(). This returns the entire state.json content
as formatted JSON. Claude can read specific fields from it.

To get detailed information about one bay, say:

    "Describe bay A in detail."

Claude calls describe_bay("A"). This is a rich narrative description
including the dimensions, area in square feet, column count, wall and
corridor configuration, every aperture, the void, and the spatial
relationship to Bay B (how far away and in what direction).

To understand the corridors, say:

    "Describe the circulation in this building."

Claude calls describe_circulation(). This reports which bays have
corridors, which do not, what doors and portals are near each
corridor, and whether any corridors are dead ends.

To measure distances, say:

    "How far is bay A from bay B?"

Claude calls measure("bay A center", "bay B center"). This returns
the straight-line distance, horizontal distance, and vertical
distance in feet.

You can measure between these locations:
- "bay A origin" (the anchor point)
- "bay A center" (the center of the footprint)
- "bay A void" (the center of the void)
- "site origin" (the origin of the site)
- "site center" (the center of the site)

To run a validation audit, say:

    "Audit the model for problems."

Claude calls audit_model(). This checks for overlapping bays, bays
outside the site boundary, apertures that do not fit their walls,
corridor widths below ADA minimum (5 ft), door widths below ADA
minimum (3 ft clear), orphaned room references, and missing labels.
If there are issues, they are listed and numbered. If not, it says
0 issues found.

To audit one specific bay, say:

    "Audit bay B."

Claude calls audit_bay("B"). This is a detailed report on just that
bay: grid type, dimensions, area, column count, walls, corridor,
apertures, void, labels, and any issues found.

### Editing the model through MCP

These are things you can say to Claude to change the model. Claude
calls the appropriate MCP tool, which runs the command through the
controller, which updates state.json.

To change site dimensions:

    "Make the site 300 feet wide."

Claude calls set_site("width", 300). The controller updates
state["site"]["width"] to 300 and writes state.json.

To move a bay:

    "Move bay A to position 50, 50."

Claude calls set_bay("A", "origin", "50 50"). The controller
updates state["bays"]["A"]["origin"] to [50.0, 50.0].

To rotate a bay:

    "Rotate bay A by 30 degrees."

Claude calls set_bay("A", "rotation", "30").

To change column spacing:

    "Set bay A spacing to 30 by 30 feet."

Claude calls set_bay("A", "spacing", "30 30").

To turn walls on or off:

    "Turn on walls for bay B with half-foot thickness."

Claude calls set_walls("B", true, 0.5). This runs two commands:
"wall B on" and "wall B thickness 0.5".

To add a corridor:

    "Add an 8-foot double-loaded corridor to bay B on the x-axis."

Claude calls set_corridor("B", true, "axis", "x") and then
additional calls to set width and loading.

To add a door:

    "Add a 3-foot door called d3 to bay A on the south wall, 15 feet from the corner."

Claude calls add_aperture("A", "d3", "door", "x", 0, 15.0, 3.0, 7.0).
The parameters are: bay name, aperture ID, type, axis, gridline,
corner offset, width, height.

To modify a door:

    "Make door d1 wider, 4 feet."

Claude calls modify_aperture("A", "d1", "width", "4").

To remove a door:

    "Remove door d3 from bay A."

Claude calls remove_aperture("A", "d3").

To save a safety checkpoint:

    "Save a snapshot called before-experiment."

Claude calls save_snapshot("before-experiment").

To restore from a checkpoint:

    "Restore the before-experiment snapshot."

Claude calls load_snapshot("before-experiment").

### Using skills through MCP

Skills are saved command sequences that can be replayed.

To see what skills are available:

    "What skills are available?"

Claude calls skill_list(). It will read back the names and
descriptions of all saved skills.

To see the details of a specific skill:

    "Show me the double-loaded corridor skill."

Claude calls skill_show("add-double-loaded-corridor"). It will
read back the parameter names, their defaults, and the exact
sequence of commands the skill runs.

To run a skill with defaults:

    "Run the corridor skill on bay B."

Claude calls skill_run("add-double-loaded-corridor", "bay=B").
The skill runs 4 commands: turns the corridor on, sets the axis
to x, sets the width to 8, and sets the loading to double. Claude
reads back the result of each command.

To run a skill with custom parameters:

    "Run the corridor skill on bay B with 10-foot width on the y-axis."

Claude calls skill_run("add-double-loaded-corridor", "bay=B width=10 axis=y").

To create a new skill:

    "Save a new skill called quick-enclose that turns on walls at 0.5 thickness and adds a 3-foot door on the south wall."

Claude calls skill_save() with the name, description, command list,
and parameters. The skill is saved as a JSON file in skills/.

### Extending the controller through MCP

This is the most advanced feature. Claude can write new Python
functions and add them to the controller at runtime.

To add a new command:

    "Add a new command called wallarea that calculates the total wall area in the building."

Claude will do several things:
1. Write a Python function called cmd_wallarea(state, tokens)
2. Call extend_controller("cmd_wallarea", code)
3. The MCP server validates the code (checks syntax, signature,
   name conflicts)
4. Appends the function to controller_cli.py
5. Registers it in the dispatch chain
6. Reloads the controller module
7. Tests it by calling run_command("wallarea")

After this, the command "wallarea" works everywhere: in the CLI,
through the MCP server, and in skills.

To see what extensions have been added:

    "What extensions have been added?"

Claude calls list_extensions(). Each extension shows the command
word, function name, and when it was added.

### Checking the Rhino connection

To see if Rhino is running and connected:

    "Is Rhino connected?"

Claude calls rhino_status(). If Rhino is running with the watcher
active, this returns the layer count, object count, and last rebuild
time. If Rhino is not running, it returns OFFLINE with a message
explaining that all model data is available in state.json.

To ask Rhino how many objects are on a layer:

    "How many objects are on the JIG_COLUMNS layer in Rhino?"

Claude calls rhino_query("object_count", "JIG_COLUMNS").

To get per-layer statistics:

    "Show me the Rhino layer statistics."

Claude calls rhino_query("layer_stats").

---

## Part 2b: Editing JSON and Controller Through MCP (v3.1)

The v3.1 tools let Claude read and write individual fields in
state.json, create and manage bays, inspect the controller source
code, and compare states to snapshots. These bridge the gap between
the high-level semantic tools and raw file editing.

### Reading specific fields

Instead of loading the entire state JSON, you can ask for one field.

To read one value, say:

    "What is bay A's rotation?"

Claude calls get_field("bays.A.rotation_deg"). This returns just
that one number: 0.0. No other data is returned.

To read a nested value, say:

    "What is the corridor width on bay A?"

Claude calls get_field("bays.A.corridor.width"). Returns: 8.0.

To read a list item, say:

    "What type is bay A's first aperture?"

Claude calls get_field("bays.A.apertures.0.type"). Returns: "door".

The dot-notation path works at any depth:
- "site.width" reads the site width
- "bays.A.origin" reads bay A's anchor point as [x, y]
- "bays.A.walls.enabled" reads whether walls are on
- "style.heavy_lineweight_mm" reads the heavy lineweight
- "legend.enabled" reads whether the legend is on
- "meta.notes" reads the project notes
- "print.dpi" reads the print resolution
- "bambu.printer_ip" reads the Bambu printer IP

### Exploring the state structure

To see what sections exist in state.json, say:

    "List the top-level fields in the state."

Claude calls list_fields(""). This returns all top-level keys:
schema, meta, site, style, bays, blocks, rooms, legend, tactile3d,
print, bambu, tts, section. Each key shows whether it is a dict,
a list, or a simple value.

To drill into a section, say:

    "What fields does bay A have?"

Claude calls list_fields("bays.A"). This returns all bay properties:
grid_type, z_order, origin, rotation_deg, bays, spacing, corridor,
walls, apertures, void_center, void_size, void_shape, label, braille.
Dict fields show their child count; list fields show their item count;
simple values show their current value.

To explore deeper, say:

    "What fields does bay A's corridor have?"

Claude calls list_fields("bays.A.corridor"). Returns: enabled, axis,
position, width, loading, hatch, hatch_scale.

### Writing specific fields

To change a field that has no CLI command, say:

    "Set the project notes to 'Library renovation phase 2'."

Claude calls set_field("meta.notes", "\"Library renovation phase 2\"").
This writes directly to state.json. The old value is reported back.

To change the print DPI, say:

    "Set the print DPI to 600."

Claude calls set_field("print.dpi", "600"). The value "600" is
parsed as JSON (a number). The old value (300) is reported.

To change a boolean, say:

    "Turn off the legend."

Claude calls set_field("legend.enabled", "false"). The value "false"
is parsed as JSON boolean false.

To change a list, say:

    "Set bay A's origin to [50, 50]."

Claude calls set_field("bays.A.origin", "[50.0, 50.0]"). The entire
list is replaced.

Important: set_field bypasses CLI validation. The CLI validates
that bay names exist, that door widths meet minimums, that gridline
indices are in range. set_field writes the raw value directly. Use
it for fields that have no CLI command (meta, blocks, print, bambu)
or when you know the value is correct. For bay configuration, prefer
the semantic tools (set_bay, set_walls, add_aperture) because they
validate input.

### Creating new bays

There is no CLI command to create a bay from scratch. With v3.1,
you can do it through MCP.

To create a new bay, say:

    "Create a new rectangular bay called C at position 50, 50."

Claude calls add_bay("C", "rectangular", 50.0, 50.0). This creates
bay C with default settings: 3x3 grid, 24 ft spacing, no walls, no
corridor, no apertures. Room references are regenerated automatically
so bay_C and void_C appear in the rooms list.

After creating the bay, configure it with the semantic tools:

    "Set bay C to 4x4 with 30 foot spacing."
    "Turn on walls for bay C at half-foot thickness."
    "Add a corridor to bay C, 8 feet wide, east-west."

To create a radial bay, say:

    "Create a radial bay called D at position 100, 100."

Claude calls add_bay("D", "radial", 100.0, 100.0). This creates
bay D with default settings: 8 arms, 4 rings, 20 ft ring spacing.

### Removing bays

To delete a bay, say:

    "Remove bay C from the model."

Claude calls remove_bay("C"). The bay and its room references are
deleted. This is permanent. Save a snapshot first if you might
want to undo it.

### Duplicating bays

To copy a bay with all its settings, say:

    "Clone bay A to bay E at position 80, 80."

Claude calls clone_bay("A", "E", 80.0, 80.0). This deep copies
everything: walls, corridor, apertures, void, spacing. Only the
label and origin change. Use this to quickly create variations
of an existing bay.

### Inspecting controller commands

To see what commands the controller understands, say:

    "List all available commands."

Claude calls list_commands(). This parses the controller source
code and shows every command with its handler function. The output
is organized into categories: navigation (describe, help, undo),
handlers (corridor, wall, aperture, etc.), and set sub-commands
(set site, set bay, set style, etc.).

To see the source code of a specific handler, say:

    "Show me the source code for the wall command."

Claude calls show_command_source("wall"). This reads controller_cli.py
and extracts the full function definition for cmd_wall. You can see
exactly what the function does, what it validates, and how it mutates
the state.

To see how bay properties are set, say:

    "Show me the source code for set bay."

Claude calls show_command_source("_cmd_set_bay"). This shows the
function that handles all "set bay" commands (origin, rotation,
spacing, etc.). Use this before writing extensions so you understand
the patterns.

### Comparing states to snapshots

To see what changed since a checkpoint, say:

    "Compare the current state to the before-experiment snapshot."

Claude calls diff_snapshot("before-experiment"). This loads both
states and compares every field. Changed fields are listed with
their current and previous values. This is like a "git diff" for
your model.

### Validating the state file

After editing state.json by hand, you can check it for errors:

    "Validate the state file."

Claude calls validate_state(). This checks:
- Is the file valid JSON? (catches missing commas, bad brackets)
- Does it have required top-level keys? (schema, meta, site, bays)
- Does each bay have required fields? (grid_type, origin, bays)
- Are field types correct? (origin is [x,y], bays is [nx,ny])
- Are aperture types valid? (door, window, or portal)

This is different from audit_model, which checks spatial and ADA
rules. validate_state checks the JSON structure itself.

---

## Part 3: Editing state.json by Hand

You do not need the CLI or MCP to change the model. state.json is a
plain text file. You can open it in any text editor and change values
directly.

This is useful when you want to understand the data structure, make
bulk edits, or work without any software running.

### Opening state.json

Open the file in any text editor. On Windows:

    notepad state.json

Or use any editor: VS Code, Notepad++, or whatever you prefer.

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

To move Bay A to position (50, 50), change:

    "origin": [10.0, 10.0]

to:

    "origin": [50.0, 50.0]

To change the spacing to 30 feet, change:

    "spacing": [24.0, 24.0]

to:

    "spacing": [30.0, 30.0]

To make it a 4x4 grid, change:

    "bays": [3, 3]

to:

    "bays": [4, 4]

### Adding an aperture by hand

Apertures are inside a bay's "apertures" list. Each aperture is a
JSON object. To add a door to Bay A, add an entry to the
"apertures" array:

    "apertures": [
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
      },
      ... existing apertures ...
      {
        "id": "d3",
        "type": "door",
        "axis": "y",
        "gridline": 3,
        "corner": 5.0,
        "width": 3.5,
        "height": 7.0,
        "hinge": "start",
        "swing": "positive"
      }
    ]

The fields mean:
- "id": a unique name you choose (d3, w2, p1, etc.)
- "type": "door", "window", or "portal"
- "axis": "x" means the aperture is on a horizontal wall (south
  or north edge). "y" means it is on a vertical wall (west or east).
- "gridline": which gridline the wall is on (0 is the first).
  For x-axis: 0 is the south wall, 3 is the north wall (in a 3x3).
  For y-axis: 0 is the west wall, 3 is the east wall.
- "corner": how far from the gridline intersection, in feet
- "width": opening width in feet
- "height": opening height in feet
- "hinge": which end the door hinges on ("start" or "end")
- "swing": which direction the door swings ("positive" or "negative")

### Enabling walls by hand

Find the bay's "walls" section:

    "walls": {
      "enabled": false,
      "thickness": 0.5
    }

Change "enabled" to true:

    "walls": {
      "enabled": true,
      "thickness": 0.5
    }

### Enabling a corridor by hand

Find the bay's "corridor" section:

    "corridor": {
      "enabled": false,
      "axis": "x",
      "position": 1,
      "width": 8.0,
      "loading": "double",
      "hatch": "none",
      "hatch_scale": 4.0
    }

Change "enabled" to true and set the properties you want:

    "corridor": {
      "enabled": true,
      "axis": "x",
      "position": 1,
      "width": 8.0,
      "loading": "double",
      "hatch": "none",
      "hatch_scale": 4.0
    }

The fields mean:
- "axis": "x" runs east-west, "y" runs north-south
- "position": which gridline the corridor is centered on
- "width": corridor width in feet
- "loading": "single" (rooms on one side) or "double" (rooms on both)
- "hatch": hatch pattern name for the corridor fill, or "none"

### Important: save and verify

After editing state.json by hand, verify it is valid JSON. An easy
way is to load it with the CLI:

    python controller_cli.py --state state.json

Type "describe" to see if your changes look right. If the JSON is
malformed (missing comma, unmatched bracket), the CLI will show an
error when it tries to load the file.

If the Rhino watcher is running, it will detect the file change and
rebuild the geometry automatically within half a second.

---

## Part 4: Editing the Controller Code

The controller (controller_cli.py) is a Python file that defines
every command the Layout Jig understands. You can add new commands
in two ways: through the MCP's extend_controller tool, or by
editing the Python file directly.

### How command handlers work

Every command handler is a Python function with this pattern:

    def cmd_something(state, tokens):
        # tokens is a list of strings from the user's input
        # state is the full model dictionary
        # do validation and mutation here
        return state, "OK: What changed."

The function receives the current state and the tokenized command.
It validates the input, modifies the state dictionary, and returns
the modified state plus a confirmation message.

For example, if the user types "something A 30", the tokens list is:
["something", "A", "30"]. The function reads tokens[1] to get "A"
and tokens[2] to get "30".

### Where commands are registered

Near line 1754 of controller_cli.py is the apply_command function.
It has a series of if/elif statements that dispatch commands:

    def apply_command(state, tokens, state_file=None):
        if not tokens: return state, ""
        cmd = tokens[0].lower()
        if cmd == "corridor": return cmd_corridor(state, tokens)
        if cmd == "wall":     return cmd_wall(state, tokens)
        if cmd == "aperture": return cmd_aperture(state, tokens)
        ... and so on ...

To add a new command, you need two things:
1. A handler function (def cmd_yourcommand)
2. A dispatch line (if cmd == "yourcommand": return cmd_yourcommand)

### Adding a command through MCP (the easy way)

Ask Claude:

    "Add a new command called floorarea that prints the total floor area of all bays."

Claude writes the function, calls extend_controller(), and the
command is immediately available. You do not need to restart anything.

Here is what Claude might write:

    def cmd_floorarea(state, tokens):
        import math
        total = 0
        for name, bay in sorted(state.get("bays", {}).items()):
            if bay.get("grid_type") == "radial":
                outer = bay.get("rings", 4) * bay.get("ring_spacing", 20)
                arc = bay.get("arc_deg", 360)
                area = math.pi * outer**2 * (arc / 360.0)
            else:
                nx, ny = bay["bays"]
                sx, sy = bay["spacing"]
                area = nx * sx * ny * sy
            total += area
        lines = []
        for name, bay in sorted(state.get("bays", {}).items()):
            if bay.get("grid_type") == "radial":
                outer = bay.get("rings", 4) * bay.get("ring_spacing", 20)
                arc = bay.get("arc_deg", 360)
                a = math.pi * outer**2 * (arc / 360.0)
            else:
                nx, ny = bay["bays"]
                sx, sy = bay["spacing"]
                a = nx * sx * ny * sy
            lines.append("  Bay {}: {:,.0f} sq ft".format(name, a))
        lines.append("  Total: {:,.0f} sq ft".format(total))
        return state, "OK: Floor areas:\n" + "\n".join(lines)

After extend_controller runs this, you can type "floorarea" in the
CLI or call run_command("floorarea") through MCP.

### Adding a command by hand (the full-control way)

Step 1: Open controller_cli.py in a text editor.

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
pick up the change until it is restarted. In the interactive CLI,
you need to restart it.

### What extend_controller does behind the scenes

When you call extend_controller through MCP, it does exactly what
the manual process does, but automatically:

1. Validates the Python code by parsing it with the ast module.
   If there is a syntax error, it stops and reports the error.

2. Checks that the function name starts with "cmd_".

3. Checks that the function takes (state, tokens) as parameters.

4. Checks that the command word does not conflict with existing
   commands like "corridor", "wall", "aperture", etc.

5. Appends the function to the end of controller_cli.py (before
   apply_command).

6. Inserts the dispatch line into apply_command.

7. Reloads the controller module using importlib.reload so the
   new command is available immediately without restarting.

8. Records the extension in state.json under meta/extensions so
   there is a log of what was added and when.

---

## Part 5: Resetting the Test Project

### Quick reset

Run the automated tests:

    python run_tests.py

The test suite resets state.json to its original configuration at
the end of every run.

### Manual reset

If you need to reset state.json and the test suite is not working,
you can recreate the original state by starting the CLI and loading
a snapshot (if you saved one at the beginning), or by copying a
fresh state.json from the main project.

### Cleaning up extensions

If you used extend_controller and want to remove the added code,
open controller_cli.py in a text editor and:

1. Find the added function (it will be near the end of the file,
   marked with a comment like "Extension: cmd_floorarea").
2. Delete the function.
3. Find the dispatch line in apply_command (it will say something
   like: if cmd == "floorarea": return cmd_floorarea).
4. Delete that line.
5. Save the file.

---

## Part 6: Understanding What Happens When

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

The key point: steps 6-10 are identical whether the command comes
from the CLI or from MCP. The controller is the single authority.

### When you edit state.json by hand

1. You open state.json in a text editor.
2. You change a value and save.
3. If the Rhino watcher is running, it detects the file change
   and rebuilds geometry.
4. The next time you open the CLI or Claude calls an MCP tool,
   the updated state is loaded from disk.

There is no validation when you edit by hand. The CLI and MCP
validate input before writing. If you introduce an error in the
JSON (like a string where a number should be), the controller
will either ignore it or crash. The Rhino watcher may also crash.
So always test your edits by loading the file in the CLI afterward.

---

## Troubleshooting

### "mcp package not found"

Run this in your terminal:

    pip install mcp

### "No module named controller_cli"

You are not in the right folder. Run:

    cd "C:\Users\su-jsclark2\Desktop\_CONTENT\Accessibility\CLI\CLI JIG TEST"

Then try again.

### "state.json not found" or "No state file"

Run from the folder that contains state.json, or specify the path:

    python controller_cli.py --state "C:\full\path\to\state.json"

### CLI shows garbage characters

You may be running in Windows Terminal or PowerShell, which handle
Unicode differently. Use cmd.exe instead. The decoration characters
in the describe output use Unicode em-dashes and box characters that
display best in cmd.exe with a Unicode-capable font.

### Rhino watcher not connecting to the bridge

The bridge connects on TCP port 1998. Make sure:
- The watcher is running INSIDE Rhino (via exec(open(...).read()))
- The watcher printed "[PLJ] TCP listener on 127.0.0.1:1998"
- No firewall is blocking localhost port 1998
- You are not also running rhinomcp (which uses port 1999, but
  check for conflicts)

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

---

## Quick Reference

### All 45 MCP Tools

Querying (read-only, no changes):
 1. describe - full model description
 2. list_bays - compact bay table
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
20. get_field - read one JSON field by path (v3.1)
21. list_fields - list keys at a JSON path (v3.1)
22. list_commands - all CLI commands with handlers (v3.1)
23. show_command_source - handler source code (v3.1)
24. diff_snapshot - compare state to snapshot (v3.1)
25. validate_state - check JSON structure (v3.1)

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
42. set_field - write one JSON field by path (v3.1)
43. add_bay - create a new bay (v3.1)
44. remove_bay - delete a bay (v3.1)
45. clone_bay - duplicate a bay (v3.1)
