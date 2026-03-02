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

Swell Print (tools/swell-print/)
  Converts designs and images into high-contrast black and white
  output for PIAF swell paper. Two modes: render state.json directly
  (no Rhino needed) or convert any image (photo, sketch, CAD export).
  Ten presets, density management, braille labels. Requires Pillow
  and reportlab (pip install -r tools/swell-print/requirements.txt).

Braille Module (controller/braille.py)
  Translates ASCII text to Unicode Braille (U+2800-U+28FF).
  Grade 1 (uncontracted) built-in using stdlib only. Grade 2
  (contracted) available when liblouis is installed. Used by
  all tools for braille label generation.

Rhino Viewer (tools/rhino/rhino_watcher.py)
  Watches the state file and renders geometry in Rhino.
  Read-only viewer — Rhino is never the source of truth.

Setup Script (setup.py)
  One-command setup for the entire system. Checks Python version,
  installs dependencies (mcp, Pillow, reportlab), creates .mcp.json,
  validates state.json, and tests MCP server readiness.
  Run: python setup.py


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
Claude can call commands as typed function calls. It also has the
auditor, skill manager, rhino client, controller extension tools,
state introspection tools, bay management tools, controller
introspection tools, state comparison tools, script generation
tools, and swell-print tactile graphics tools. 53 tools total (v3.3).

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
For the MCP server: pip install mcp (the only external dependency for MCP).
For swell-print: pip install -r tools/swell-print/requirements.txt (Pillow, reportlab).
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


## 12. Text-to-Speech

Enable spoken confirmation of commands:

    tts on

Disable:

    tts off

Change the speech rate (-10 to 10):

    tts rate 4

When TTS is on, every command confirmation is spoken aloud via
Windows PowerShell SpeechSynthesizer. This includes describe and
list bays output — the full model description is read aloud when
requested.

TTS is OFF by default. It works on Windows only.


## 13. Quit

    quit

This saves the state and exits the CLI.


## 14. Output Modes

The toolkit produces three kinds of physical output from the same
model. All three are equally important. A blind designer can touch
a swell paper plan, hold a 3D printed model, or read a section cut.
A sighted collaborator can review a pen-plotted drawing. All outputs
come from the same state.json, so they are always in sync.


### 2D Plan Drawing (Pen Plot / PDF)

The Layout Jig is first and foremost a 2D plan drawing tool. The
Rhino watcher renders the model as a black and white architectural
plan with columns, walls, corridors, doors, windows, hatches,
braille labels, and a legend. This drawing can be:

- Pen-plotted on an architectural pen plotter
- Exported as PDF or PNG from Rhino
- Printed on standard paper for sighted review

Configure the 2D output:

    set print scale 8
    set print paper 24x36
    set print margin 0.5
    set print dpi 300
    set print format png

Print scale uses the architectural convention of feet per inch.
Scale 8 means 1/8" = 1'-0" (a common schematic scale). Scale 4
means 1/4" = 1'-0" (a detail scale).

Trigger a print request:

    print

This bumps the request_id in state.json, which the watcher detects
and uses to trigger export.

The drawing style controls how the plan looks:

    set style heavy 1.4
    set style light 0.08
    set style wall 0.25
    set style corridor 0.35
    set style text_height 0.3
    set style braille_height 0.5

Heavy lines are outer boundaries. Light lines are gridlines. Wall
and corridor lines have their own weights. All lineweights are in
millimeters, matching pen plotter conventions.


### PIAF / Swell Paper Output

PIAF (Pictures In A Flash) is a machine that heats special
microcapsule paper ("swell paper"). Dark areas on the printed image
swell up and become raised, creating a tactile graphic readable by
touch. This is one of the most important outputs of the system —
it lets a blind designer feel the floor plan.

The workflow:

1. Design the plan using the CLI or MCP.
2. The Rhino watcher renders the plan in black and white with
   PIAF-optimised settings: high-contrast hatches, braille labels,
   tactile block symbols, and a braille legend.
3. Export the view from Rhino as a high-resolution PNG or PDF.
4. Print the image on swell paper using a standard laser printer.
5. Run the printed sheet through the PIAF machine. Dark areas
   rise. Light areas stay flat.
6. The designer reads the tactile floor plan by touch.

The system has several features specifically designed for PIAF:

Block symbols — doors, windows, and portals use symbols optimised
for tactile readability. Each has a tactile_weight_mm setting that
controls line thickness for swell paper:

    block door tactile_weight_mm 0.35
    block window tactile_weight_mm 0.25
    block portal tactile_weight_mm 0.35

Hatch patterns — rooms use hatch fills (diagonal, crosshatch, dots,
horizontal, vertical) so a blind reader can tell rooms apart by
texture. Different room types get different hatches:

    cell A 0,0 hatch crosshatch
    cell A 1,0 hatch dots
    cell A 2,0 hatch diagonal

Braille labels — every bay, room, and legend entry can have both
an English label and a braille label:

    set bay A label "Library Wing"
    set bay A braille "lib"
    legend show_braille on

Legend — the legend includes both English text and braille, plus
hatch swatches and aperture symbols:

    legend on
    legend show_braille on
    legend show_hatches on
    legend show_apertures on

Hatch library — you can add custom hatch images for more texture
variety:

    hatch list
    hatch path ./hatches/
    hatch add weave ./source_images/weave.png

The swell-print tool (tools/swell-print/) automates the entire
export-to-PIAF pipeline. It can render state.json directly to
a 300 DPI B&W image (no Rhino needed) or convert any image file
to PIAF-ready output. Ten conversion presets are available for
different image types (floor plans, sketches, photographs, etc.).

From the swell-print CLI:

    python tools/swell-print/swell_print.py
    >> render
    OK: Rendered state_tactile.pdf (Letter, 300 DPI, density 28.3%)

Or from Claude via MCP:

    render_tactile(paper_size="letter", output_format="pdf")

The tool manages black pixel density to ensure optimal swell
results: target 25-40%, warning above 40%, rejection above 45%.
Labels are rendered in both English and Grade 1 braille using
the stdlib-only controller/braille.py module.

The CLI print command now generates tactile output directly. Type
print in the interactive CLI and it renders state_tactile.pdf in
the controller/ directory using the swell-print renderer. If
swell-print dependencies are not installed, the command still
reports print settings but notes that no image was generated.

Braille labels on PIAF output use paper-absolute sizing conforming
to BANA standards (Braille Authority of North America): 30pt font
producing approximately 10mm line spacing. English text renders at
12pt. These sizes are fixed regardless of model scale — the same
braille is readable whether the site is 100 feet or 1000 feet wide.


### 3D Tactile Print

The tactile 3D system extrudes the 2D plan into a physical model
you can hold. Walls become solid volumes. A floor plate provides a
base. The model is clipped at a configurable cut height (typically
4 feet) so you feel the wall layout without the ceiling. The result
is exported as an STL mesh and sent to a 3D printer.

Configure tactile 3D:

    tactile3d on
    tactile3d wall_height 9
    tactile3d cut_height 4
    tactile3d floor on
    tactile3d floor_thickness 0.5
    tactile3d scale_factor 1.0

Export an STL mesh:

    tactile3d export_path ./my_model.stl
    tactile3d export

Or use auto-export to regenerate the STL every time the model changes:

    tactile3d auto_export on

When auto_export is on and tactile3d is enabled, every command
that changes the model automatically exports a new STL file to
the configured export_path. This means the 3D model stays in
sync with your design without manual export commands.

The Bambu printer pipeline handles the full path from model to print:

    bambu config ip 192.168.1.100
    bambu config access_code 12345678
    bambu config serial 01P00C000000001
    bambu config printer_model p1s
    bambu config print_scale 200
    bambu preview
    bambu export
    bambu slice
    bambu send
    bambu print
    bambu status

"bambu preview" shows whether the model fits on the build plate.
"bambu print" runs the full pipeline: export STL, slice to 3MF,
upload to printer, and start printing.


### Section Cuts (SVG)

Section cuts slice through the 3D model along a vertical plane and
export the result as an SVG file. These are useful for understanding
wall heights and spatial relationships.

    section x 50
    section preview
    section export ./section_x_50.svg
    section list
    section clear

Section export requires tactile_print.py to be available (it uses
the mesh engine to compute the cut).


## 15. Audit Tools

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


## 16. MCP Server

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

### All 53 MCP Functions

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

Rhino setup:
46. setup_rhino - configure Rhino path

Script generation (Mode 3 learning):
47. generate_script - create a .py script file
48. list_scripts - list generated scripts
49. show_script - show script contents

Swell-print (tactile graphics):
50. render_tactile - render state.json to tactile output
51. convert_to_tactile - convert image to tactile output
52. check_tactile_density - check image density for PIAF
53. list_tactile_presets - list conversion presets


## 17. State Introspection

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


## 18. Bay Management

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


## 19. Skill Manager

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


## 20. Rhino Client

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


## 21. Extending the Jig

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


## 22. Controller Introspection

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


## 23. State Comparison

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


## 24. Mode 3: Learning Rhino Python

The system supports three interaction modes:

Mode 1: Claude Code + MCP. Natural language. Claude translates your
intent into model changes. Best for getting started and complex
multi-step operations.

Mode 2: Interactive CLI. Typed commands in a terminal. Direct control.
Best for fine-tuning and learning the command vocabulary.

Mode 3: Rhino Python editor. You write and run IronPython 2.7 scripts
that create geometry, query the model, or automate tasks directly
inside Rhino. Best for building scripting fluency.

Mode 3 matters because the AI should be a bridge to self-sufficiency.
Over time, you learn to write your own scripts. The system generates
annotated scripts you can study, modify, and run.

### Script generation tools (MCP)

generate_script: Creates a .py file in the scripts/ folder with
teaching comments and IronPython 2.7 validation.

list_scripts: Lists all generated scripts with descriptions.

show_script: Shows the full contents of a script file.

### Workflow

1. Ask Claude: "Generate a script that draws a circle at each column"
2. Claude calls generate_script — file appears in scripts/
3. Open the file in any text editor (or Rhino's EditPythonScript)
4. Read the teaching comments to understand what each line does
5. Modify the script (change values, add features)
6. Run in Rhino with F5
7. Ask Claude to explain errors or help debug

### IronPython 2.7 rules

Scripts run inside Rhino's IronPython 2.7 interpreter:
- No f-strings. Use .format() instead.
- No pathlib. Use os.path instead.
- No type hints.
- print() works as a function.

The generate_script tool checks for these automatically.

### Example: read state.json and print room info

    import json
    import os

    here = os.path.dirname(os.path.abspath(__file__))
    state_path = os.path.join(here, "..", "state.json")

    with open(state_path, "r") as f:
        state = json.load(f)

    rooms = state.get("rooms", {})
    for name, info in sorted(rooms.items()):
        label = info.get("label", name)
        print("{0}: {1}".format(name, label))

See DESIGN_SESSION.md for a complete walkthrough showing all three
modes in action during a school building design project.


## 25. Swell-Print: PIAF Tactile Graphics

The swell-print tool converts designs into physical tactile graphics
readable by touch on PIAF swell paper. Two modes of operation:

1. Render state.json directly to PIAF-ready output (no Rhino needed)
2. Convert any image (photo, sketch, CAD export) to PIAF-ready B&W

### Setup

Install the swell-print dependencies (the controller CLI itself
does not need these, only the swell-print tool does):

    pip install -r tools/swell-print/requirements.txt

### CLI usage

Interactive mode:

    python tools/swell-print/swell_print.py
    >> render
    OK: Rendered state_tactile.pdf (Letter, 300 DPI, density 28.3%)
    >> convert photo.jpg --preset floor_plan
    OK: Converted photo.jpg -> photo_tactile.png (density 31.2%)
    >> presets
    OK: 10 presets available: ...
    >> density output.png
    OK: Density 31.2% (good for PIAF)

Single-shot mode:

    python tools/swell-print/swell_print.py render state.json -o plan.pdf
    python tools/swell-print/swell_print.py convert photo.jpg --preset sketch

### MCP usage

Four MCP tools are available (v3.3):

render_tactile: Renders state.json to B&W tactile output.
convert_to_tactile: Converts any image to PIAF-ready B&W.
check_tactile_density: Checks black pixel density of an output image.
list_tactile_presets: Lists all conversion presets.

### Conversion presets

floor_plan: threshold 140, max 40% density. CAD or hand-drawn plans.
elevation: threshold 135, max 35%. Building elevations.
section: threshold 145, max 35%. Section cuts with material hatching.
photograph: threshold 120, max 30%. Photos with varying light.
sketch: threshold 130, max 35%. Pencil and pen sketches.
technical_drawing: threshold 150, max 45%. CAD with crisp lines.
diagram: threshold 135, max 35%. Diagrams with mixed content.
site_plan: threshold 130, max 40%. Site plans with landscape.
detail_drawing: threshold 145, max 40%. Construction details.
presentation: threshold 125, max 35%. Presentation boards.

### Density management

PIAF swell paper works best with 25-40% black pixel density.
Above 45%, excessive swelling reduces tactile clarity. The tool
warns when density exceeds 40% and rejects output above 45%.

### Braille module

The braille translation module (controller/braille.py) is stdlib-only
and available to all tools. Grade 1 (uncontracted) is built-in.
Grade 2 (contracted) is available when liblouis is installed.

    import braille
    braille.to_braille("Bay A")       # Grade 1
    braille.to_braille("Bay A", 2)    # Grade 2 (requires liblouis)
    braille.from_braille(text)        # Reverse: braille -> ASCII

On PIAF swell paper output, braille is rendered at the BANA standard
size (approximately 30pt, producing 10mm line spacing) regardless of
model scale. English labels render at 12pt. The state.json
style.braille_text_height and label_text_height values (in feet)
control the Rhino watcher only; the swell-print renderer uses
paper-absolute sizes for PIAF compliance.


## 26. End-to-End Workflows

These workflows show complete sequences from start to finish,
combining multiple tools for real tasks.


### Workflow A: Complete System Walkthrough

This walkthrough takes you from first setup through design,
audit, physical output, and iteration. It shows both the
interactive CLI (Mode 2) and Claude/MCP (Mode 1) for every
step, so you can use whichever you prefer.

The scenario: Daniel is designing a small community library with
a reading room, a study room, and an accessible corridor. He
wants a tactile floor plan on swell paper and a 3D printed model
to bring to his design review.


Step 1: System setup.

Run the setup script to verify Python, install dependencies,
and configure the MCP server:

    python setup.py

Expected output:

    OK: Python 3.11.5 detected.
    OK: mcp package installed.
    OK: Pillow installed.
    OK: reportlab installed.
    OK: .mcp.json created.
    OK: state.json is valid.
    OK: Setup complete. All systems ready.

If any step fails, setup.py tells you exactly what to install.


Step 2: Start the CLI and see the model.

    python controller/controller_cli.py

    >> describe

This prints the full model: schema version, site dimensions, all
bays, all rooms, and totals.

Claude/MCP equivalent: ask Claude "describe the current model."
Claude calls describe() and reads the output to you.


Step 3: Set up the site.

    >> set site width 150
    OK: Site width = 150.0 ft. Was 200.0 ft.

    >> set site height 100
    OK: Site height = 100.0 ft. Was 200.0 ft.

Claude/MCP equivalent: "set the site to 150 by 100 feet."
Claude calls set_site(field="width", value=150) and
set_site(field="height", value=100).


Step 4: Position and size the main bay.

    >> set bay A origin 10 10
    OK: Bay A origin = [10.0, 10.0]. Was [10.0, 10.0].

    >> set bay A bays 4 3
    OK: Bay A grid = [4, 3]. Was [3, 3].

    >> set bay A spacing 24 24
    OK: Bay A spacing = [24.0, 24.0]. Was [24.0, 24.0].

    >> set bay A label "Community Library"
    OK: Bay A label = "Community Library". Was "".

Claude/MCP equivalent: "set bay A to a 4 by 3 grid at origin
10,10 with 24 foot spacing, label it Community Library."
Claude calls set_bay for each property.


Step 5: Turn on walls with a corridor.

    >> wall A on
    OK: Bay A walls ON.

    >> wall A thickness 0.5
    OK: Bay A wall thickness = 0.50 ft. Was 0.50 ft.

    >> corridor A on
    OK: Bay A corridor ON.

    >> corridor A width 8
    OK: Bay A corridor width = 8.0 ft. Was 8.0 ft.

    >> corridor A axis x
    OK: Bay A corridor axis = x. Was x.

    >> corridor A loading double
    OK: Bay A corridor loading = double. Was double.

Claude/MCP equivalent: "turn on walls for bay A, then enable
a double-loaded east-west corridor, 8 feet wide."
Claude calls set_walls(bay="A", enabled=true) and
set_corridor(bay="A", enabled=true, field="width", value="8").


Step 6: Add doors.

    >> aperture A add d1 door x 0 10 3.5 7
    OK: Added door d1 to bay A.

    >> aperture A add d2 door x 3 10 3.5 7
    OK: Added door d2 to bay A.

    >> aperture A add d3 door y 0 5 3.5 7
    OK: Added door d3 to bay A.

d1 is on the south wall (x-axis gridline 0), 10 feet from the
corner, 3.5 feet wide, 7 feet tall. d2 is on the north wall.
d3 is on the west wall. All doors are 3.5 feet wide, which
meets the ADA minimum of 3 feet clear width.

Claude/MCP equivalent: "add three doors: d1 on the south wall
at 10 feet, d2 on the north wall at 10 feet, d3 on the west
wall at 5 feet. All 3.5 feet wide, 7 feet tall."
Claude calls add_aperture three times.


Step 7: Name rooms and assign hatches.

    >> cell A 0,0 name "Reading Room"
    OK: Cell A(0,0) name = "Reading Room".

    >> cell A 0,0 hatch diagonal
    OK: Cell A(0,0) hatch = diagonal.

    >> cell A 1,0 name "Reading Room"
    OK: Cell A(1,0) name = "Reading Room".

    >> cell A 1,0 hatch diagonal
    OK: Cell A(1,0) hatch = diagonal.

    >> cell A 0,2 name "Study Room"
    OK: Cell A(0,2) name = "Study Room".

    >> cell A 0,2 hatch crosshatch
    OK: Cell A(0,2) hatch = crosshatch.

    >> cell A 1,2 name "Study Room"
    OK: Cell A(1,2) name = "Study Room".

    >> cell A 1,2 hatch crosshatch
    OK: Cell A(1,2) hatch = crosshatch.

Cells with the same name merge into one room. The Reading Room
is on the south side (two cells with diagonal hatch), the Study
Room is on the north side (two cells with crosshatch). A blind
reader can tell the rooms apart by texture on the swell paper.

Claude/MCP equivalent: "name the bottom two cells Reading Room
with diagonal hatch, and the top two cells Study Room with
crosshatch." Claude calls set_cell for each.


Step 8: Save a snapshot before auditing.

    >> snapshot save before-audit
    OK: Snapshot "before-audit" saved.

This preserves the current state so you can roll back if needed.

Claude/MCP equivalent: "save a snapshot called before-audit."
Claude calls save_snapshot(name="before-audit").


Step 9: Ask Claude for a design critique.

Mode 1 only (this is where MCP shines). Ask Claude:

    "Review my library design. Check for ADA issues and
    suggest improvements to the spatial layout."

Claude calls audit_model(), describe_bay(bay="A"), and
describe_circulation(). It reports back in natural language:

    "Your design has 0 ADA issues. All three doors meet the
    3.5 foot minimum. The 8-foot corridor supports wheelchair
    passing. I notice the Reading Room has no windows. Consider
    adding a window on the east wall for daylight access."


Step 10: Fix an issue based on the critique.

    >> aperture A add w1 window y 4 12 6 4
    OK: Added window w1 to bay A.

A 6-foot window on the east wall of the Reading Room.

Claude/MCP equivalent: "add a 6-foot window on the east wall,
12 feet from the corner, 4 feet tall."
Claude calls add_aperture(bay="A", id="w1", type="window",
axis="y", gridline=4, corner=12, width=6, height=4).


Step 11: Run the formal audit.

    >> audit
    OK: 0 issues found.

If there were problems, the audit lists them with numbers:

    1. Bay A door d3 width 2.5 ft is below ADA minimum 3.0 ft.
    2. Bay A corridor width 4.0 ft is below ADA minimum 5.0 ft.

Claude/MCP equivalent: "run an accessibility audit."
Claude calls audit_model() and reads each issue.


Step 12: Extend the controller with a custom command.

Mode 1 only. Ask Claude:

    "Add a command called floorarea that calculates the
    total floor area of all rectangular bays."

Claude calls extend_controller with:

    function_name: "cmd_floorarea"
    code: '''
    def cmd_floorarea(state, tokens):
        total = 0
        for name, bay in state.get("bays", {}).items():
            if bay.get("grid_type") != "rectangular":
                continue
            nx, ny = bay["bays"]
            sx = bay.get("spacing", [24, 24])
            w = nx * sx[0]
            h = ny * sx[1]
            total += w * h
        msg = "OK: Total floor area: {:.0f} sq ft.".format(total)
        return state, msg
    '''

Now use it from the CLI:

    >> floorarea
    OK: Total floor area: 6912 sq ft.

The command persists across sessions because it is written into
controller_cli.py. It also works through MCP via run_command.


Step 13: Generate 2D tactile output (PIAF swell paper).

    >> print
    OK: Rendered state_tactile.pdf (Letter, 300 DPI, density 28.3%)

The print command generates a PDF ready for swell paper. The
braille labels are rendered at BANA standard size (30pt, 10mm
line spacing), readable by touch regardless of drawing scale.

Print the PDF on swell paper with a laser printer, then run it
through the PIAF heater. Dark areas swell up. Daniel reads the
floor plan by touch: diagonal hatch is the Reading Room,
crosshatch is the Study Room, and the corridor is between them.

Claude/MCP equivalent: "generate a tactile PDF for swell paper."
Claude calls render_tactile(paper_size="letter", output_format="pdf").

To convert a reference image instead of the model:

    python tools/swell-print/swell_print.py convert photo.jpg --preset floor_plan
    OK: Converted photo.jpg -> photo_tactile.png (density 31.2%)


Step 14: Generate 3D tactile output (3D print).

    >> tactile3d on
    OK: Tactile 3D: ON.

    >> tactile3d wall_height 9
    OK: Tactile 3D wall height = 9.0 ft.

    >> tactile3d cut_height 4
    OK: Tactile 3D cut height = 4.0 ft.

    >> tactile3d floor on
    OK: Tactile 3D floor: ON.

    >> tactile3d export_path ./library_model.stl
    OK: Tactile 3D export path = "./library_model.stl".

    >> tactile3d export
    OK: Exported STL to ./library_model.stl (12,456 triangles).

For continuous sync during design iteration:

    >> tactile3d auto_export on
    OK: Tactile 3D auto-export: ON.

Now every model change regenerates the STL automatically.

Claude/MCP equivalent: "enable tactile 3D with 9-foot walls,
cut at 4 feet, export to library_model.stl."
Claude calls run_command for each tactile3d setting.


Step 15: Send to the Bambu 3D printer.

    >> bambu config ip 192.168.1.100
    OK: Bambu printer IP = 192.168.1.100.

    >> bambu config access_code 12345678
    OK: Bambu access code set.

    >> bambu config serial 01P00C000000001
    OK: Bambu serial = 01P00C000000001.

    >> bambu preview
    OK: Model fits on build plate. Dimensions: 120mm x 80mm x 24mm.

    >> bambu print
    OK: STL exported, sliced, uploaded. Print started.

Claude/MCP equivalent: "configure the Bambu printer at
192.168.1.100 and start printing." Claude calls run_command
for each bambu config, then run_command("bambu print").


Step 16: Iterate with snapshots.

    >> snapshot save with-window
    OK: Snapshot "with-window" saved.

Make an experimental change:

    >> set bay A rotation 15
    OK: Bay A rotation = 15.0 deg. Was 0.0 deg.

Compare what changed:

Claude/MCP: "compare the current state to snapshot with-window."
Claude calls diff_snapshot(snapshot_name="with-window") and reports:

    "One field changed: bays.A.rotation_deg was 0.0, now 15.0."

Decide the rotation does not work. Restore:

    >> snapshot load with-window
    OK: Snapshot "with-window" loaded.

    >> describe
    (Bay A rotation is back to 0 degrees.)

Claude/MCP equivalent: "restore the with-window snapshot."
Claude calls load_snapshot(name="with-window").


Step 17: Final check.

    >> describe
    >> audit

Review the full model description. Confirm zero audit issues.
Daniel now has:

- A tactile floor plan on swell paper for the pinup wall.
- A 3D printed model for the jury to hold.
- A practiced verbal description from the describe output.
- A saved snapshot he can restore and continue iterating from.

The entire session used one terminal window and one JSON file.
No screen was required at any point.


### Workflow B: Studying a Precedent

Daniel wants to understand an existing building plan he cannot
see. He uses the image describer to get a text description, then
converts the image to a tactile print, and finally recreates the
design in the Layout Jig.

    # Step 1: Get a description of the building plan image
    python tools/image-describer/arch_alt_text.py farnsworth_plan.jpg
    # Claude vision describes the plan in structured text

    # Step 2: Convert the image to a tactile print
    python tools/swell-print/swell_print.py convert farnsworth_plan.jpg --preset floor_plan
    OK: Converted farnsworth_plan.jpg -> farnsworth_plan_tactile.png (density 31.2%)

    # Step 3: Print on swell paper, run through PIAF
    # Daniel now has a tactile version of the Farnsworth House plan

    # Step 4: Recreate in the Layout Jig based on what he learned
    python controller/controller_cli.py
    >> set site width 120
    >> set site height 60
    >> set bay A bays 4 1
    >> set bay A spacing 22 28
    # Continue building the design from tactile + text understanding


### Workflow C: Design Review Preparation

Daniel prepares three physical artifacts for a design review:
a tactile floor plan, a 3D printed model, and a practiced
verbal description.

    # 1. Audit the design for issues
    # Ask Claude: "Run an accessibility audit on my design"
    # Claude calls audit_model() and reports any ADA issues
    # Fix any problems before generating output

    # 2. Generate a tactile floor plan (swell paper)
    python tools/swell-print/swell_print.py
    >> render --paper tabloid
    OK: Rendered state_tactile.pdf (Tabloid, 300 DPI, density 26.1%)

    # 3. Generate a 3D tactile model
    python controller/controller_cli.py
    >> tactile3d on
    >> tactile3d wall_height 9
    >> tactile3d cut_height 4
    >> tactile3d export
    >> bambu print
    OK: STL sent to Bambu printer.

    # 4. Prepare the verbal description
    >> describe
    # Read the full model description to practice presenting
    # The describe output covers: site, bays, walls, corridors,
    # apertures, rooms, and any validation issues

    # Daniel brings to the review:
    # - Tactile floor plan (swell paper) for pinup
    # - 3D printed model for the jury to hold
    # - Practiced verbal description of the design intent


## 27. Editing state.json by Hand

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


## 28. How Things Work Under the Hood

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


## 29. MCP Resources and Prompts

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


## 30. Troubleshooting

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
