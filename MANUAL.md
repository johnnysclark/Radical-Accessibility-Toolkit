
PLAN
LAYOUT
JIG
Version 2.3  —  Manual

Non-Visual Architectural Design System
for blind, low-vision, and sighted designers

Radical Accessibility Project
University of Illinois Urbana-Champaign · School of Architecture

# Contents

# 1  Overview
The Plan Layout Jig is a text-based architectural design tool. You type commands in a terminal to define structural grids, walls, doors, corridors, rooms, and more. A companion script inside Rhino draws everything in real time.
The system has three components. The controller and watcher communicate through a single JSON file — the controller writes it, the watcher reads it and draws. They never interact directly. The tactile print module reads the same JSON to generate 3D-printable meshes without Rhino. This separation means a blind designer can build a complete plan without visual feedback, while a sighted collaborator can view the live drawing at any time.


The system can produce PIAF tactile prints (raised-line swell paper) and 3D-printed tactile plan models via STL export.
# 2  Getting Started
Requirements: Python 3.8 or later and Rhino 7 or 8 (Windows or Mac). The controller and tactile print module run in any terminal. The watcher runs inside Rhino. No additional packages are needed for basic operation. Bambu 3D printing (Section 10.3) optionally requires OrcaSlicer and paho-mqtt.
## 2.1  File Placement
Place all three Python files in the same folder: controller_cli_v2.py, rhino_watcher_v2.py, and tactile_print.py. The controller creates state_v2.json automatically on first run. Optionally create a hatches subfolder for image-based room fill patterns.
## 2.2  Start the Controller
Terminal
python controller_cli_v2.py

# Or specify a custom state file location:
python controller_cli_v2.py --state "/projects/studio/state_v2.json"
## 2.3  Start the Watcher
Open Rhino’s Python editor (EditPythonScript) or a GhPython component. Paste and run:
Rhino Python console
import sys
sys.path.insert(0, r"C:\path\to\your\folder")
import rhino_watcher_v2 as w
w.start_watcher()

## 2.4  Verify the Connection
Type describe in the controller. You should see a structured text report of the model. In Rhino, gridlines, columns, and a site boundary should appear. If Rhino is empty, confirm all files share the same folder and that state_v2.json exists.
# 3  Reading the Model: Describe
The describe command is the most important tool in the system. It prints a structured text report of every setting, piece of geometry, and spatial relationship in the model. For a designer working without visual feedback, this command replaces looking at the drawing.
CLI (both forms are equivalent)
describe
d
The output is divided into labeled sections. Here is what each contains and why it matters.
## 3.1  META and SITE
META confirms the schema version, creation date, last save time, and notes — useful for verifying you have the right file and that recent changes persisted. SITE reports dimensions in feet, total area, and origin coordinates.
## 3.2  STYLE VARIABLES
All 12 drawing parameters, each on its own line: column size, four lineweights (heavy, light, corridor, wall), two text heights (label, Braille), corridor dash/gap lengths, background padding, label offset, and arc segment count. These control both screen and tactile output.
## 3.3  BAY Sections
One block per bay, beginning with a header line showing bay letter, grid type, z-order, anchor point, and rotation.
Rectangular bays report bay count, spacing (uniform or irregular with the full list), footprint dimensions, gridline counts, column count, and area. Radial bays report ring count, arm count, ring spacing, arc angle, start angle, outer radius, column count, and area.
Each bay section then reports, in order:
- World bounds — min/max x and y after rotation. Use these to check overlaps or position new bays.
- Corridor — on/off, loading type, direction, gridline, width, hatch.
- Walls — on/off, thickness in feet and inches.
- Apertures — each door, window, or portal on its own line: ID, type, axis, gridline, corner, width, height. Doors add hinge and swing.
- Void — shape, size, center coordinates.
- Label — English text and Braille string.
- Cell rooms — if any cells are named: room count, cell count, each room with its cells, area in square feet, and hatch.
## 3.4  ROOMS, BLOCKS, LEGEND, TACTILE 3D, BAMBU, TTS, SECTION CUT, HATCH LIBRARY, PRINT
These sections report all remaining model state: room assignments and hatches, aperture symbol configuration, legend layout, 3D print settings, Bambu printer configuration and scale, TTS status and rate, section cut definition, hatch image inventory, and output format.
## 3.5  TOTALS
A numerical fingerprint of the model: total columns, bay count, combined area, site area, room count, hatched rooms, and total apertures. Useful for quickly confirming a command did what you intended.
## 3.6  Related Commands
# 4  Structural Grids
Each bay is an independent grid — rectangular or radial — with its own origin, rotation, and z-order. Higher z-order bays draw on top, with white background masks covering lower layers at overlaps.

## 4.1  Rectangular Grids
CLI
set bay A bays 6 4                  # 6 bays across, 4 deep
set bay A spacing 24 24             # uniform 24 ft in both directions

# Irregular spacing (one value per span):
set bay A spacing_x 20 24 24 24 24 20
set bay A spacing_y 30 24 24 30
## 4.2  Radial Grids
CLI
set bay B grid_type radial
set bay B rings 5
set bay B ring_spacing 18
set bay B arms 12
set bay B arc_deg 270              # partial arc (default 360)
set bay B arc_start_deg 45
## 4.3  Position and Layering
CLI
set bay A origin 20 10
set bay A rotation 15              # degrees counterclockwise
set bay A z_order 2                # higher = draws on top
set site width 200
set site height 300
# 5  Walls and Apertures
Walls are drawn as offset parallel lines along every gridline of a rectangular bay. Apertures — doors, windows, portals — cut gaps in those walls and draw symbols in the openings.
## 5.1  Enabling Walls
CLI
wall A on
wall A thickness 0.667             # in feet (= 8 inches)
## 5.2  Adding Apertures
Each aperture sits on one gridline. Specify axis (x = horizontal, y = vertical), gridline index (0 = first), corner offset from the gridline’s start, width, and height.
CLI
aperture A add d2 door x 1 12.0 3.0 7.0
# id=d2, type=door, horizontal gridline 1, 12 ft from start, 3 wide, 7 tall

aperture A add w2 window y 0 8.0 6.0 4.0
aperture A add p2 portal x 3 20.0 10.0 9.0
## 5.3  Door Hinge and Swing
Hinge position (start or end of the opening) and swing direction (positive or negative) control the arc symbol.
CLI
aperture A set d2 hinge end
aperture A set d2 swing neg
## 5.4  Listing, Modifying, Removing
CLI
aperture A list                    # formatted table
aperture A set d1 width 4.0
aperture A set d1 gridline 2
aperture A remove d2
Modifiable fields: type, axis, gridline, corner, width, height, hinge, swing.
# 6  Corridors
A corridor is a circulation zone centered on one gridline, drawn with edge lines, a dashed centerline, and an optional hatch fill. Each bay can have one. Loading can be single (rooms on one side) or double (rooms on both sides).
CLI
corridor A on
corridor A axis x                  # east–west
corridor A position 2              # centered on gridline 2
corridor A width 10
corridor A loading double
corridor A hatch Hatch1
corridor A hatch_scale 3.0
corridor A off
Corridor hatch names: Hatch1, Grid, Dots, Dash, Solid (these are Rhino’s built-in pattern names). Room hatches in Section 7 use friendlier aliases.
# 7  Rooms and Hatch Patterns
Rooms are named regions that receive hatch fills for tactile differentiation. On PIAF swell paper, different patterns produce distinct textures distinguishable by touch. Rooms are auto-generated for each bay and void at startup.
## 7.1  Assign Hatches and Labels
CLI
room bay_A hatch diagonal
room bay_A hatch_scale 2.0
room bay_A hatch_rotation 45
room bay_A label "Main Hall"
room bay_A braille "⠍⠁⠒⠝ ⠓⠁⠇⠇"
Built-in hatch names: diagonal, crosshatch, dots, horizontal, solid.
## 7.2  Custom Rooms and Refresh
CLI
room add lobby bay A               # new room tied to bay A
room remove lobby
room list                          # full room table
room refresh                       # regenerate defaults from current bays
## 7.3  Cell Rooms: Subdividing Bays
Rooms and hatches (Sections 7.1–7.2) apply to entire bays. Cell rooms break each rectangular bay into individual grid cells and let you name, label, and hatch them independently. Each cell is the rectangle between two adjacent vertical gridlines and two adjacent horizontal gridlines. A 6×3 bay produces 18 cells. Cells are addressed by column,row coordinates starting from the bottom-left at 0,0.

Cells are created automatically the first time you use the cell command on a bay. They start unnamed.
CLI
cell A list                         # table of all cells with areas

# Name a single cell:
cell A 2,0 name "Office"
cell A 2,0 label "Corner Office"    # display label (defaults to name)
cell A 2,0 hatch diagonal           # assign hatch

# Name a range (col0,row0-col1,row1, inclusive):
cell A 0,0-1,2 name "Lobby"         # 6 cells become one room
cell A 0,0 label "Main Lobby"
cell A 0,0-1,2 hatch dots

When multiple cells share the same name, they form a single room. The describe command reports each room with its cell count and total area. In Rhino, the watcher draws boundary lines around each room, a centered label, and the area in square feet.
## 7.4  Room Summary
The cell <bay> rooms command groups cells by name and totals their areas:
CLI
cell A rooms

# Output:
#  Bay A rooms:
#    Name                     Cells        Area
#    Conference                   2     1,152 sf
#    Corridor                     6     3,456 sf
#    Studio                       3     1,728 sf
#    (unnamed)                    7     4,032 sf
#    Total                       18    10,368 sf
## 7.5  Auto-Corridor and Clear
If a bay has an enabled corridor, auto_corridor names every cell that overlaps the corridor zone:
CLI
cell A auto_corridor                # marks overlapping cells
cell A 2,1 clear                    # reset one cell to unnamed
cell A clear_all                    # reset all cells

# 8  Legend
The legend draws a bordered key beside the plan showing hatched room swatches and aperture symbols, labeled in English and Braille. It makes tactile prints self-documenting.
CLI
legend on
legend position bottom-right
legend width 50
legend title "Drawing Key"
legend title_braille "⠙⠗⠁⠺⠒⠝⠛ ⠅⠑⠽"
legend show_braille on
legend show_hatches on
legend show_apertures on
Position options: bottom-right, bottom-left, top-right, top-left, custom <x> <y>.
Sizing parameters: swatch_size, row_height, text_height, braille_height, padding, border_weight_mm.
# 9  Block Symbols and Voids
## 9.1  Block Symbols
Each aperture type (door, window, portal) and the room label have configurable drawing properties: symbol name, label visibility, prefix letter, label height, and tactile lineweight.
CLI
block list
block door symbol arc_swing
block door label on
block door label_prefix D
block door label_height 1.5
block door tactile_weight 0.35
## 9.2  Voids
Every bay has a void — a courtyard, atrium, or light well — drawn as an outline on the JIG_VOIDS layer.
CLI
set bay A void_center 90 44
set bay A void_size 30 18
set bay A void_shape rectangle      # or circle
# 10  Tactile 3D
Tactile 3D extrudes wall geometry into solid shapes for 3D printing. Walls become raised ridges; apertures become gaps you can feel. A horizontal clipping plane creates a plan-section view. An optional floor slab provides a base.
## 10.1  Enable and Configure
CLI
tactile3d on
tactile3d wall_height 9.0
tactile3d cut_height 4.0
tactile3d floor on
tactile3d floor_thickness 0.5
## 10.2  Export STL
One-shot export (recommended) triggers a single STL write on the next watcher redraw:
CLI
tactile3d export_path "./my_model.stl"
tactile3d scale_factor 0.04167
tactile3d export
Auto-export writes the STL on every redraw — useful during rapid iteration:
CLI
tactile3d auto_export on

## 10.3  Bambu 3D Printer Pipeline
The Bambu pipeline generates a scaled, watertight triangle mesh directly from the plan state — no Rhino needed — and can slice and send it to a Bambu Lab printer over the local network. The pipeline lives in a companion module (tactile_print.py) that the controller imports automatically.

### Setup
Place tactile_print.py in the same folder as the controller. Then configure your printer:
CLI
bambu config ip 192.168.1.100
bambu config access_code 12345678
bambu config serial 01S00A000000001
bambu config printer_model p1s
bambu config print_scale 200         # 1:200 representation scale

The access code is displayed on the printer’s touchscreen under Settings → Network → Access Code. The serial number is on a sticker inside the top cover.
### Preview
Preview builds the mesh and reports dimensions, triangle count, and whether the model fits on the printer’s build plate. If it doesn’t fit, it suggests a scale that would.
CLI
bambu preview
### Export, Slice, Send
CLI
bambu export                         # mesh → binary STL
bambu export ./my_model.stl          # export to specific path

# Slice requires OrcaSlicer (free, open source):
bambu config slicer_path "/path/to/orca-slicer-console"
bambu slice                          # export + slice → 3MF

bambu send                           # upload 3MF + start print
bambu print                          # full pipeline: export+slice+send
bambu status                         # poll printer progress

The mesh generator replicates the watcher’s wall extrusion logic in pure Python: each wall segment becomes a watertight box, apertures create gaps, and the floor slab is a flat box beneath. Every mesh passes manifold edge checks — every edge is shared by exactly two faces.

# 11  Text-to-Speech
The controller can speak command responses aloud using Windows text-to-speech. This provides immediate audio confirmation of every action without requiring a screen reader to be active.
## 11.1  Enable TTS
CLI
tts on                             # start speaking responses
tts off                            # silence
tts                                # show current status
You can also enable TTS at startup with the --tts flag:
python controller_cli.py --tts
## 11.2  Speech Rate
Rate ranges from -10 (slowest) to 10 (fastest). The default is 2.
CLI
tts rate 5                         # faster
tts rate -2                        # slower
tts rate 0                         # normal Windows default
## 11.3  How It Works
TTS uses PowerShell's System.Speech.Synthesis.SpeechSynthesizer, which is built into Windows. No additional software is needed. Each response is spoken in a fire-and-forget subprocess so it does not block typing the next command.
The OK: and ERROR: prefixes are stripped before speaking for cleaner audio. If speech fails on the first attempt (for example, on a system without the speech assembly), TTS is silently disabled for the rest of the session.
TTS settings are saved in the state file and persist across sessions.

# 12  Section Cut
A section cut slices the 3D wall mesh with a vertical plane and exports the resulting profile as SVG. This is useful for understanding wall relationships in section and for producing tactile section drawings.
## 12.1  Define a Cut Plane
Specify the axis the plane is perpendicular to and the position along that axis in feet. Walls must be enabled on at least one rectangular bay.
CLI
section x 42                       # cut perpendicular to X at 42 ft
section y 100                      # cut perpendicular to Y at 100 ft
## 12.2  Preview
Preview shows how many wall segments the plane intersects and the extent of the resulting section profile, without writing a file.
CLI
section preview
# Section X=42.0: 48 segments, extent 260.0 x 4.5 ft.
## 12.3  Export SVG
Export writes an SVG file with black lines on white background. The default filename is section_<axis>_<offset>.svg in the current folder.
CLI
section export                     # default path
section export "./cuts/north.svg"  # custom path
## 12.4  List and Clear
CLI
section list                       # show current settings
section clear                      # remove section definition
The section cut definition is saved in the state file and persists across sessions. Radial bays are not included in the mesh — only rectangular bays with walls enabled.

# 13  History and Snapshots
Every mutating command automatically saves a numbered copy of the state to a history folder alongside the state file. Named snapshots let you bookmark important design states and return to them later.
## 13.1  Automatic History
Each time you run a command that changes the model, the controller writes a copy to history/0001.json, history/0002.json, and so on. Undo deletes the most recent history entry. The history folder is created automatically next to the state file.
CLI
history count                      # number of history entries
history list                       # last 20 entries + named snapshots
## 13.2  Named Snapshots
Snapshots are named bookmarks saved in the same history folder. Unlike numbered entries, they are not affected by undo.
CLI
snapshot save before_walls          # save current state
snapshot save "end of day"          # names with spaces
snapshot list                       # show all named snapshots
snapshot load before_walls          # restore a snapshot
Loading a snapshot replaces the entire current state. The previous state is pushed onto the undo stack, so you can undo the load if needed.
## 13.3  History Folder
The history folder is a sibling of the state file and is not part of the JSON state. It is excluded from version control by the .gitignore file.
history/
0001.json                        # numbered entries
0002.json
snapshot_before_walls.json        # named snapshots

# 14  MCP Server
The MCP (Model Context Protocol) server wraps the CLI so that AI assistants can drive the jig conversationally. Version 2.0 adds 16 semantic tools with typed parameters, MCP resources, and prompt templates. The AI calls add_aperture(bay="A", id="d1", type="door", ...) instead of guessing raw CLI syntax.
## 14.1  Setup
Install the MCP package (v1.26.0 or later):
pip install mcp
For Claude Code, place .mcp.json at the project root:
{ "mcpServers": { "layout-jig": { "command": "python", "args": ["Layout Jig/layout-jig/mcp_server.py", "--state", "Layout Jig/layout-jig/state.json"] } } }
For Claude Desktop, add the same entry to claude_desktop_config.json. Or set the environment variable LAYOUT_JIG_STATE and omit --state.
## 14.2  Available Tools
The server exposes 21 tools in five categories. All semantic tools are thin wrappers that construct CLI command strings internally, so validation and error messages are identical to the terminal.
Read tools (no state mutation): describe(), list_bays(), get_state(), get_help(), list_apertures(bay), list_cells(bay), list_rooms(), list_snapshots().
Bay configuration: set_bay(bay, field, value) sets any bay property. The field parameter accepts: origin, rotation, bays, spacing, spacing_x, spacing_y, grid_type, z_order, void_center, void_size, void_shape, label, braille, rings, ring_spacing, arms, arc_deg, arc_start_deg.
Walls and corridors: set_walls(bay, enabled, thickness) toggles walls on/off with optional thickness. set_corridor(bay, enabled, field, value) toggles corridors and optionally sets axis, position, width, loading, hatch, or hatch_scale.
Apertures: add_aperture(bay, id, type, axis, gridline, corner, width, height) adds a door, window, or portal. remove_aperture(bay, id) removes one. modify_aperture(bay, id, field, value) changes any property: type, axis, gridline, corner, width, height, hinge, swing.
Cells and rooms: set_cell(bay, col, row, field, value) sets a cell's name, label, braille, hatch, hatch_scale, or hatch_rotation. auto_corridor_cells(bay) detects and labels corridor-zone cells.
Site and style: set_site(field, value) sets width or height. set_style(field, value) sets any of: heavy, light, corridor, wall, text_height, braille_height, dash_len, gap_len, bg_pad, label_offset, arc_segments.
Snapshots: save_snapshot(name) checkpoints the current state. load_snapshot(name) restores it. Use snapshots before significant changes since undo is not available in MCP mode.
Escape hatch: run_command(command) executes any raw CLI command string. Use this for advanced operations not covered by the semantic tools.
## 14.3  MCP Resources
Three read-only resources let the AI load context without calling a tool: state://current returns the full JSON state, snapshots://list shows available checkpoints, and help://commands provides the CLI reference.
## 14.4  MCP Prompts
Two prompt templates are registered: design_review loads the full model description and asks for spatial, circulation, and tactile feedback. aperture_audit lists all apertures across all bays and checks for missing doors, window placement, and portal sizing.
## 14.5  Design Notes
Each tool call loads state from disk, runs the command, and saves back. There is no persistent session, so undo is not available. Use named snapshots to checkpoint before major changes.
Stdout is reserved for JSON-RPC transport. All print output from the controller is redirected to stderr.

# 15  Style Variables
Style variables control lineweights, text sizes, and spacing for both screen and tactile output. Set them individually:
CLI
set style heavy 1.60
set column size 2.0    # column_size uses its own command


# 16  Output and Utilities
## 16.1  Print Output
CLI
set print scale 8                  # 1/8" = 1'-0"
set print paper 24x36
set print margin 0.5
set print dpi 300
set print format png               # or jpg
print                              # request print from watcher
## 16.2  Hatch Library
Manage a folder of hatch images assignable to rooms.
CLI
hatch list
hatch path "C:/my_hatches/"
hatch add stripes "C:/source/stripes.png"
## 16.3  Undo, History, Help, Quit
CLI
undo                               # revert last change
Each undo also removes the last history entry. See Section 13 for named snapshots.
help                               # command summary (also h, ?)
status                             # state file path and timestamp
quit                               # save and exit (also q, exit)

# 17  Command Reference
Angle brackets = required.  Vertical bars = alternatives.  Square brackets = optional.
## 17.1  General
## 17.2  Site and Style
## 17.3  Bay Configuration
## 17.4  Walls and Apertures
## 17.5  Corridors
## 17.6  Rooms
## 17.7  Cell Rooms
## 17.8  Legend
## 17.9  Block Symbols
## 17.10  Tactile 3D
## 17.11  Bambu Printer
## 17.12  Hatch Library and Print

## 17.13  Text-to-Speech
## 17.14  Section Cut
## 17.15  History and Snapshots
## 17.16  MCP Server (tools)
# 18  Rhino Layer Map
The watcher organizes all geometry into named layers. Toggle layer visibility in Rhino to isolate parts of the drawing.


# 19  Extending the Jig with an LLM
The Plan Layout Jig was built to be extended. Its architecture — a state-writing controller cleanly separated from a geometry-drawing watcher — makes it straightforward to add features by working with a large language model. This section is a practical guide to vibe-coding additions.
## 19.1  The Key Principle
Every feature in the system follows the same pattern. The controller owns the data: it parses commands, validates input, and mutates a Python dictionary that gets written as JSON. The watcher owns the geometry: it reads that JSON and calls Rhino drawing functions. The tactile print module owns standalone mesh generation and printer communication. When you ask an LLM to add something, you need changes to the relevant files, and the LLM needs to understand the boundaries between them.

## 19.2  Recipe for a New Command
Every command added to the system follows these six steps. You can paste this list directly into your LLM prompt:

- Default data. Write a _default_X() function in the controller. Add the key to default_state(). Add migration logic in main() so older JSON files that lack the key get back-filled.
- Command handler. Write cmd_X(state, tokens). Parse tokens positionally, validate with _float/_int_pos/_int_nn, mutate the state dict, return (state, message). Handle all subcommands (on/off/set/list) in one function.
- Dispatch. Add one line in apply_command(): if cmd == "x": return cmd_X(state, tokens).
- Describe. Add a section to describe() so the new data appears in the text report.
- Help text. Add the syntax to HELP_TEXT.
- Watcher drawing. Write _draw_X(state) in the watcher. Call it from redraw(). Use existing primitives — _add_line, _add_polyline, _add_text, _local_to_world — so geometry respects bay rotation. Never call rs.* directly; always go through the helpers.
## 19.3  Adding a Bay Property
If you just need a new property on bays (like a floor-to-floor height), the pattern is simpler:

- Add the default value to _default_bay().
- Add a handler in _cmd_set_bay() following the existing if-chain.
- Add a line in describe()’s bay section.
- In the watcher, read it with bay.get("new_field", default).
## 19.4  Pitfalls to Warn the LLM About
Include these in your prompt so the LLM avoids common mistakes:

Rhino API hallucinations. LLMs sometimes invent rhinoscriptsyntax methods that don’t exist. All watcher geometry must go through the guarded helper functions (_add_line, _add_rect, _add_circle, _add_polyline, _add_text, _add_hatch). These check IN_RHINO before calling Rhino.
State migration. Existing JSON files won’t have new keys. The controller’s main() back-fills missing keys with if-blocks. The LLM needs to add one for each new field.
The _export_once pattern. Transient flags set by the controller and consumed by the watcher need special handling. The flag is set to True, saved to JSON, read by the watcher, then cleared in memory. The controller’s main loop also clears it after save so it doesn’t re-fire on the next command. Any new one-shot trigger should follow this pattern.
Undo and deepcopy. The controller runs copy.deepcopy(state) before every command for undo. New data structures with mutable objects (nested dicts, lists) survive this automatically, but be aware of it.
Screen reader considerations. Avoid decorative characters in output strings (long lines of ═ or ─). JAWS reads every character aloud. Use short text labels instead.
## 19.5  Feature Ideas
These extensions fit naturally into the existing architecture:

- Bay add/remove commands — create and delete bays from the CLI instead of editing JSON directly.
- Stair and elevator symbols — new object types with standardized plan symbols, similar to apertures.
- Dimension annotations — draw dimension lines with measurement text between gridlines or along walls.
- Bambu printer enhancements — the basic pipeline (Section 10.3) is implemented. Extensions: automatic scale-to-fit, multi-plate splitting for large models, print time estimation, filament color selection.
- JAWS screen reader mode — a --sr flag that reformats all output for linear reading. (See also Section 11 for the TTS feature, now implemented.)
- Tab completion — use Python’s readline module to auto-complete commands, bay letters, and aperture IDs.
- Multi-floor stacking — manage multiple floor states and compose them vertically for sections or multi-story 3D prints.
## 19.6  Prompt Template
When you sit down to extend the Jig, this structure works well:

I'm working on the Plan Layout Jig, a CLI + Rhino watcher system.
Here are the source files:
[paste controller_cli_v2.py]
[paste rhino_watcher_v2.py]
[paste tactile_print.py if relevant]

I want to add [feature]. It should:
- [what the user types]
- [what data is stored in the JSON state]
- [what geometry the watcher draws in Rhino]

Follow the existing code patterns:
- Controller: _default_X(), cmd_X(), dispatch, describe, help
- Watcher: _draw_X(), called from redraw()
- Use _local_to_world() for bay-relative geometry
- Guard all Rhino calls through helper functions
- Add state migration for older JSON files
- Handle the undo/deepcopy cycle

Show the complete changes to all affected files.
