# Layout Jig MCP Server -- Guide

How the AI layer works and how to use it.


## 1. What This Is

The MCP (Model Context Protocol) server is a bridge between AI assistants and the Layout Jig. It wraps the entire CLI command vocabulary as structured MCP functions that an AI can call with typed parameters. The AI becomes a collaborator that can read the model, make changes, answer questions, generate code, and critique designs -- all through the same state file that drives the Rhino watcher.

The server lives in one file: `mcp/mcp_server.py`. It imports `controller_cli.py` directly, so every MCP function call runs exactly the same code path as typing a command in the terminal. The Rhino watcher does not know or care whether a command came from a human or an AI -- it just watches the state file for changes.

This is not a separate system. It is another input device for the same platform, like voice or the pegboard. The canonical model artifact (`state.json`) remains the single source of truth.

MCP stands for Model Context Protocol, a standard created by Anthropic that lets an AI assistant call functions on your computer. Instead of you typing commands, Claude reads the MCP function descriptions, decides which one to call, fills in the parameters, and sends the call. The server executes it and returns the result.

Without MCP: you type `set bay A rotation 30` into a terminal.

With MCP: you say "rotate bay A by 30 degrees" and Claude calls `set_bay(bay="A", field="rotation", value="30")`.

The MCP server is the translator between Claude's intent and your CLI.

MCP also enables the code generation workflow. The AI can inspect the current model, write RhinoPython or Grasshopper scripts targeting that specific geometry, explain the code, and iterate -- all while the user learns the underlying language.

The same model drives three physical output modes: 2D plan drawings for pen plotting and PDF export, PIAF swell paper tactile graphics for reading floor plans by touch, and 3D printed tactile models via the Bambu pipeline. All three are configured and triggered through the same MCP functions.


## 2. Architecture

The Layout Jig has three files that form a pipeline. The MCP server sits in front of this pipeline as a fourth layer.

### Layer 1: state.json (the Canonical Model Artifact)

Path: `controller/state.json`

A JSON file on disk containing every fact about your design: site dimensions, bay positions, wall thicknesses, door locations, corridor widths, labels, hatches, and print settings.

This file is the single source of truth. If Rhino crashes, the model is still safe in this file. If the MCP server crashes, the model is still safe in this file. If the computer restarts, the model is still here.

Everything else reads from or writes to this file. Nothing else is authoritative.

### Layer 2: controller_cli.py (the state machine)

Path: `controller/controller_cli.py`

A Python script that knows every legal operation on the model. It has about 2,000 lines of code organized into command handlers: cmd_corridor, cmd_wall, cmd_aperture, cmd_cell, cmd_room, cmd_legend, cmd_tactile3d, cmd_section, and about a dozen more.

Every command handler follows the same pattern:

    def cmd_something(state, tokens):
        # validate input
        # mutate the state dict
        # return (state, "OK: what changed")

The controller reads state.json, applies your command, and writes the modified state back to state.json. It uses atomic writes (write to a `.tmp` file, fsync, then `os.replace`) so the file is never half-written.

The controller also maintains an undo stack. Before every mutation, it stores a deep copy of the state. If you type "undo", it restores the previous copy.

### Layer 3: rhino_watcher.py (the geometry renderer)

Path: `tools/rhino/rhino_watcher.py`

An IronPython 2.7 script that runs inside Rhino. Every half second, it checks if state.json has been modified. If it has, the watcher deletes all geometry in Rhino and rebuilds everything from scratch based on the new state.

The watcher never writes to state.json. It is read-only. It translates the semantic model (bays, walls, apertures) into actual Rhino geometry (lines, rectangles, arcs, hatches, text labels).

If Rhino crashes, you restart it, run the watcher again, and everything rebuilds automatically from state.json.

### Layer 4: mcp_server.py (the MCP orchestrator)

Path: `mcp/mcp_server.py`

The newest layer. It wraps the controller CLI so that Claude can call commands as typed function calls instead of raw strings.

Supporting modules:

- `controller/auditor.py` -- spatial validation, descriptions, ADA checks
- `controller/skill_manager.py` -- save and replay reusable command sequences
- `tools/rhino/rhino_client.py` -- TCP client to query Rhino
- `tools/rhino/tactile_print.py` -- tactile printing utilities

### Data flow: what happens when Claude says "rotate bay A by 30 degrees"

Step 1. Claude reads the set_bay MCP function description.

Step 2. Claude calls set_bay(bay="A", field="rotation", value="30").

Step 3. MCP server receives the call.

Step 4. MCP server calls _run("set bay A rotation 30").

Step 5. _run() reads state.json from disk.

Step 6. _run() tokenizes the command into ["set","bay","A","rotation","30"].

Step 7. _run() calls cli.apply_command(state, tokens).

Step 8. Controller dispatches to _cmd_set_bay(state, tokens).

Step 9. _cmd_set_bay validates and sets state["bays"]["A"]["rotation_deg"] = 30.0.

Step 10. _cmd_set_bay returns (state, "OK: Bay A rotation = 30.0 deg. Was 0.0 deg.").

Step 11. _run() calls cli.save_state() which atomic-writes state.json.

Step 12. _run() returns the message to MCP server.

Step 13. MCP server returns the message to Claude.

Step 14. Claude reads the message and reports it to you.

Step 15. Meanwhile, rhino_watcher.py detects the file change.

Step 16. Watcher reloads state.json and rebuilds all geometry in Rhino.

Steps 15-16 happen independently. The MCP call is already done by step 14. Rhino updates on its own schedule (within 0.5 seconds).

### What the MCP server does NOT do

- It does not store state. State lives in state.json only.
- It does not talk to Rhino for mutations. Only the watcher reads state.json and creates geometry.
- It does not duplicate business logic. Validation rules and command handlers live in controller_cli.py.
- It does not require Rhino to be running. Every MCP function works offline except the rhino_client functions, and even those return graceful OFFLINE messages.


## 3. Setup

### Install the MCP package

This is the only external dependency in the entire project:

    pip install mcp

Tested with mcp 1.26.0. Everything else is Python stdlib.

### Configure Claude Code

Create `.mcp.json` at the project root:

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

### Configure Claude Desktop

Add the same entry to `claude_desktop_config.json` (found in your Claude Desktop settings directory). Adjust paths to be absolute if needed.

### Configure Cursor

Add via Settings > MCP Servers with the same command and args.

### Environment variable alternative

Instead of passing `--state`, you can set the environment variable:

    LAYOUT_JIG_STATE=controller/state.json python mcp/mcp_server.py

### Run standalone (for testing)

    python mcp/mcp_server.py --state controller/state.json

The server communicates over stdio using JSON-RPC. All normal print output is redirected to stderr so it does not interfere with the protocol. You will see startup messages on stderr like:

    Layout Jig MCP Server v3.3 starting...
    State file: /path/to/state.json
    Tools: 49 registered

### Optional: Rhino connection

If you want live Rhino queries (object counts, bounding boxes):

1. Open Rhino.
2. Run the watcher: `exec(open("path/to/rhino_watcher.py").read())`.
3. The watcher starts a TCP listener on port 1998 automatically.
4. MCP functions like rhino_status and rhino_query will connect.

If Rhino is not running, those functions return OFFLINE messages. Everything else works without Rhino.


## 4. Tool Reference

49 MCP functions organized by category.

### Core pipeline (21 functions)

Semantic wrappers around CLI commands. These all go through `_run()` which delegates to the controller for validation and state mutation.

`run_command(command: str)` -- Execute any raw CLI command string. Escape hatch for commands not covered by typed functions.

`describe()` -- Full text description of the entire model: site, style, every bay with all properties, rooms, legend, print settings, totals.

`list_bays()` -- Compact summary of all bays.

`get_state()` -- Raw JSON contents of state.json. Useful when the AI needs to inspect specific values or generate code targeting exact coordinates.

`get_help()` -- The full CLI command reference.

`list_apertures(bay: str)` -- All doors, windows, and portals on a specific bay with full details.

`list_cells(bay: str)` -- All cells in a rectangular bay's grid with names, areas, and hatch patterns.

`list_rooms()` -- All named rooms across the entire model.

`list_snapshots()` -- All saved snapshots with file sizes and timestamps.

`set_bay(bay: str, field: str, value: str)` -- Set any bay property. The field parameter determines what gets set: origin, rotation, bays, spacing, spacing_x, spacing_y, grid_type, rings, ring_spacing, arms, arc_deg, arc_start_deg, label, braille, z_order, void_center, void_size, void_shape.

`set_walls(bay: str, enabled: bool, thickness: float = None)` -- Toggle walls on/off and optionally set thickness in feet.

`set_corridor(bay: str, enabled: bool, field: str = None, value: str = None)` -- Toggle corridor and configure properties: axis, position, width, loading, hatch, hatch_scale.

`add_aperture(bay: str, id: str, type: str, axis: str, gridline: int, corner: float, width: float, height: float)` -- Add a door, window, or portal. Walls must be enabled first.

`remove_aperture(bay: str, id: str)` -- Remove an aperture by ID.

`modify_aperture(bay: str, id: str, field: str, value: str)` -- Change one property of an existing aperture: type, axis, gridline, corner, width, height, hinge, swing.

`set_cell(bay: str, col: int, row: int, field: str, value: str)` -- Set a property on one cell: name, label, braille, hatch, hatch_scale, hatch_rotation.

`auto_corridor_cells(bay: str)` -- Automatically name all cells overlapping the corridor zone as "Corridor".

`set_site(field: str, value: float)` -- Set site width or height in feet.

`set_style(field: str, value: str)` -- Set drawing style parameter: heavy, light, corridor, wall, text_height, braille_height, dash_len, gap_len, bg_pad, label_offset, arc_segments.

`save_snapshot(name: str)` -- Save current state to history/snapshot_{name}.json.

`load_snapshot(name: str)` -- Restore a previously saved snapshot.

### Auditor (5 functions)

These call directly into auditor.py, passing the loaded state dict. No CLI commands involved. All are read-only.

`audit_model()` -- Run all validation checks: bay overlap, site bounds, aperture validity, apertures without walls, corridor sizing, ADA door widths (min 3 ft), ADA corridor widths (min 5 ft), orphaned room references, missing labels. Returns a numbered list of issues or "0 issues found."

`audit_bay(bay: str)` -- Deep audit of a single bay covering all the same checks scoped to that bay.

`describe_bay(bay: str)` -- Rich narrative description of one bay: grid type, dimensions, area, column count, walls, corridor, each aperture, void, cell rooms, and spatial relationships to every other bay (distance and direction).

`describe_circulation()` -- Corridor connectivity analysis: which bays have corridors, their configuration, doors and portals near corridors, dead-end warnings, potential inter-bay connections (bays within 10 ft of each other).

`measure(from_location: str, to_location: str)` -- Distance between semantic locations like "bay A origin" and "bay B center". Returns straight-line, horizontal (X), and vertical (Y) distances.

### Skill manager (4 functions)

Skills are saved sequences of CLI commands with {parameter} placeholders, stored as JSON in skills/. These functions read/write the skills folder and execute commands through _run().

`skill_list()` -- List all saved skills with names and descriptions.

`skill_show(name: str)` -- Show a skill's details: commands, parameters, and defaults.

`skill_run(name: str, overrides: str = "")` -- Execute a skill with optional parameter overrides. Format: "bay=B width=10". Each command runs through _run(). Execution stops on first error.

`skill_save(name: str, description: str, commands: str, params: str)` -- Save a new skill. Commands are newline-separated CLI command strings with {param} placeholders. Params are space-separated key=default pairs.

### Rhino client (4 functions)

TCP client connecting to port 1998 on localhost, where the Rhino watcher listens. All are read-only. All return OFFLINE gracefully if Rhino is not running.

`rhino_status()` -- Check if Rhino is connected. Returns layer count, object count, last rebuild time, or OFFLINE.

`rhino_query(query_type: str, layer: str = "")` -- Ask Rhino a read-only question. Query types: status, layer_stats, bounding_box, object_count.

`rhino_run_script(code: str)` -- Run a Python snippet inside Rhino's IronPython engine. The watcher blocks geometry-modifying calls (AddLine, DeleteObject, etc.) so this is strictly read-only. Important: IronPython 2.7 -- use .format() not f-strings.

`setup_rhino(rhino_path: str = "")` -- Launch Rhino with the watcher auto-loaded and units set to Feet. If already connected, returns current status instead. Searches standard install locations if no path given.

### Controller extension (2 functions)

The most experimental capability. Lets Claude write new command handlers and register them at runtime.

`extend_controller(function_name: str, code: str)` -- Add a new CLI command. Validates syntax with ast.parse(), checks function signature (must accept state, tokens), checks for name conflicts, appends to controller_cli.py, adds dispatch line, reloads module, records in state metadata.

`list_extensions()` -- Show all extensions that have been added to the controller.

### State introspection (7 functions)

Direct state access using dot-notation paths like "bays.A.corridor.width" or "meta.notes". These bypass the controller -- use for fields that have no CLI command.

`get_field(path: str)` -- Read the value of a single field. Example: get_field("site.width") returns "OK: site.width = 200.0".

`set_field(path: str, value: str)` -- Write a value directly to state.json. The value is parsed as JSON. Bypasses CLI validation. Use for fields like meta.notes, print.dpi, bambu.printer_ip that have no CLI command.

`list_fields(path: str = "")` -- List all keys at a path. Use to explore the schema. Example: list_fields("bays.A") lists all bay A properties.

`add_bay(name: str, grid_type: str = "rectangular", origin_x: float = 0.0, origin_y: float = 0.0)` -- Create a new bay with default settings: 3x3 rectangular grid, 24 ft spacing, walls off, corridor off. Room references are regenerated automatically.

`remove_bay(name: str)` -- Permanently delete a bay and regenerate room references. Use save_snapshot first if you might want to undo.

`clone_bay(source: str, target: str, origin_x: float = 0.0, origin_y: float = 0.0)` -- Deep copy all properties from an existing bay. Only the label and origin change.

`list_commands()` -- Parse controller_cli.py and list all commands organized by category. Useful before writing extensions.

### State comparison (3 functions)

`show_command_source(command: str)` -- Read the full function definition for a command handler. Accepts either the command word ("corridor") or the function name ("cmd_corridor", "_cmd_set_bay").

`diff_snapshot(snapshot_name: str)` -- Compare the current state.json to a saved snapshot and list all fields that differ. Like "git diff" for your model.

`validate_state()` -- Check that state.json is structurally correct: valid JSON, required sections present, bay fields have correct types. This is different from audit_model which checks spatial/ADA rules. validate_state checks JSON structure. Use after hand-editing state.json or after set_field changes.

### Script generation (3 functions)

Mode 3: Learning Rhino Python. These tools generate editable IronPython 2.7 scripts that the user can open, study, modify, and run in Rhino. The goal is to build scripting fluency over time so the user is not permanently dependent on the AI.

`generate_script(name: str, description: str, code: str, teach: bool)` -- Create a .py file in the scripts/ folder. Validates for IronPython 2.7 compatibility (rejects f-strings and pathlib). If teach=True (default), prepends commented learning notes. Returns the file path and instructions for running in Rhino's EditPythonScript.

`list_scripts()` -- List all .py files in scripts/ with name, description, and size.

`show_script(name: str)` -- Return the full contents of a script. Supports fuzzy name matching if the exact name is not found.

### Swell-print (4 functions)

PIAF tactile graphics generation. Render state.json directly to B&W output (no Rhino needed) or convert any image to tactile-ready format. Requires Pillow and reportlab (`pip install -r tools/swell-print/requirements.txt`). Tools degrade gracefully if dependencies are not installed.

`render_tactile(paper_size: str, output_format: str)` -- Render state.json to a PIAF-ready tactile graphic. Draws columns, walls, corridors, apertures, room hatches, labels (English + Braille), legend, and section cuts. Output is 300 DPI B&W in PDF or PNG format. No Rhino needed.

`convert_to_tactile(image_path: str, preset: str, threshold: int, paper_size: str)` -- Convert any image (photo, sketch, CAD export) to PIAF-ready B&W output. Ten presets available for different image types.

`check_tactile_density(image_path: str)` -- Check if an image's black pixel density is suitable for PIAF printing. Optimal range is 25-40%, maximum 45%.

`list_tactile_presets()` -- List all available conversion presets with threshold and density settings.


## 5. Resources and Prompts

### Resources (5)

Resources let the AI read context passively without calling an MCP function.

`state://current` -- The full JSON state file (the Canonical Model Artifact).

`snapshots://list` -- All saved snapshots with sizes and timestamps.

`help://commands` -- The complete CLI command reference.

`skills://list` -- All saved skills with names and descriptions.

`extensions://list` -- All controller extensions that have been added.

### Prompts (4)

Pre-built prompts for common design workflows. These load the current model state and frame a specific task for the AI.

`design_review` -- Loads the full model description and asks for a critique covering spatial organization, circulation paths, room naming, and hatch differentiation for tactile readability.

`aperture_audit` -- Lists every aperture across every bay and asks the AI to check for missing doors in corridors, window placement, portal sizing, and consistent heights.

`accessibility_audit` -- Runs automated audit checks and circulation analysis, then asks for a comprehensive ADA review: door widths, corridor widths, turning radii, egress paths, tactile readability, and wayfinding.

`skill_builder` -- Provides the command reference and existing skills, then guides through composing a new skill step by step.


## 6. Example Conversations

### Starting a new design

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

### Adding rooms and doors

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

### Design review and iteration

    User: Review my design. What's missing?

    AI uses prompt template: design_review

    AI: Looking at the model:
        1. The labs on the south side have no doors. Add apertures on
           gridline 1 to connect labs to the corridor.
        2. No windows on the exterior walls. Consider adding windows on
           gridlines 0 and 3 for natural light.
        3. Hatch patterns are good for tactile differentiation -- crosshatch
           vs. dots will read clearly on PIAF paper.
        4. No snapshot saved yet. Save one before adding more apertures.

    User: Good catches. Add lab doors and save a snapshot.

    AI calls: add_aperture(bay="A", id="lab-d1", type="door", axis="x",
                           gridline=1, corner=10.0, width=3.0, height=7.0)
              ... (repeats for each lab)
    AI calls: save_snapshot(name="school-v1-rooms-and-doors")

    AI: OK. 6 lab doors added at gridline 1. Snapshot saved as
        school-v1-rooms-and-doors.

### Preparing tactile output

    User: Set up the drawing for PIAF swell paper. Make sure every
          room has a different hatch and braille labels are on.

    AI calls: run_command("legend on")
    AI calls: run_command("legend show_braille on")
    AI calls: run_command("legend show_hatches on")
    AI calls: set_cell(bay="A", col=0, row=2, field="hatch", value="crosshatch")
    AI calls: set_cell(bay="A", col=0, row=0, field="hatch", value="dots")
    AI calls: run_command("set style heavy 1.4")
    AI calls: run_command("set style light 0.08")
    AI calls: run_command("set print scale 4")
    AI calls: run_command("set print paper 11x11.5")

    AI: OK. Legend is on with braille and hatch swatches. Classrooms
        have crosshatch, labs have dots. Style set for high-contrast
        output. Print scale is 1/4" = 1'-0" on 11 x 11.5 inch paper
        (standard PIAF sheet). Export the view from Rhino as a
        high-resolution PNG, print it on swell paper, and run it
        through the PIAF machine.

### 3D printing a tactile model

    User: Print a 3D model of bay A on the Bambu printer.

    AI calls: run_command("tactile3d on")
    AI calls: run_command("tactile3d wall_height 9")
    AI calls: run_command("tactile3d cut_height 4")
    AI calls: run_command("bambu config ip 192.168.1.100")
    AI calls: run_command("bambu preview")

    AI: Tactile 3D is on. Walls extruded to 9 ft, clipped at 4 ft.
        The model fits on the 256x256mm build plate at 1:200 scale.
        Ready to print. Say "print it" and I will run the full
        pipeline: export STL, slice, and send to the printer.

    User: Print it.

    AI calls: run_command("bambu print")

    AI: Full pipeline complete. STL exported, sliced to 3MF, uploaded
        to printer at 192.168.1.100. Print started.


## 7. How Undo Works in MCP Mode

The terminal CLI has an in-memory undo stack powered by `copy.deepcopy(state)` before each mutation. This stack does not persist between MCP calls because each function invocation loads fresh from disk.

Instead, MCP mode uses named snapshots:

    save_snapshot(name="before-big-change")
    ... make changes ...
    ... something went wrong ...
    load_snapshot(name="before-big-change")
    -> state restored to the checkpoint

The numbered history system (`history/0001.json`, `0002.json`, etc.) is also available. Each mutating command writes a numbered history file, so you can trace every change.

You can also use diff_snapshot to compare the current state against a checkpoint before deciding whether to revert:

    diff_snapshot("before-big-change")
    -> lists every field that changed since the snapshot


## 8. Extending the MCP Server

The MCP server is designed to grow with the platform. Adding a new MCP function follows a simple pattern.

### Adding a new MCP function (tool)

Every function is a Python function decorated with `@mcp.tool()`:

    @mcp.tool()
    def my_new_tool(param1: str, param2: float) -> str:
        """Description of what this tool does.

        This docstring becomes the description that the AI reads
        to understand when and how to use the function.

        Args:
            param1: What this parameter means
            param2: What this parameter means
        """
        return _run(f"my_cli_command {param1} {param2}")

The `_run()` helper handles the full cycle: load state from disk, tokenize and execute the command via `controller_cli.apply_command()`, save state back to disk, return the confirmation message.

If the function needs read-only access (no state mutation), load state directly:

    @mcp.tool()
    def my_read_tool(bay: str) -> str:
        """Read something from the model without changing it."""
        state = _load_state()
        # ... inspect state ...
        return result_string

### Adding a new resource

    @mcp.resource("myresource://name")
    def resource_my_data() -> str:
        """Description of this resource."""
        state = _load_state()
        return json.dumps(some_data, indent=2)

### Adding a new prompt template

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

### Adding runtime commands via extend_controller

You can also add new commands without editing the server code. The extend_controller function lets Claude write and register a new command handler at runtime:

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
            total += perim * 9  # assume 9 ft wall height
        return state, "OK: Estimated total wall area: {:.0f} sq ft".format(total)
    ''')

After this, `run_command("wallarea")` executes the new handler.

Safety: extend_controller only adds code, never modifies or removes existing functions. It validates syntax before writing, checks for command name conflicts, and tracks all extensions in state metadata.

### Pattern for wrapping a new CLI skill

When a new skill is added to the CLI (e.g., structural analysis), extending MCP coverage follows this pattern:

1. The new skill adds commands to controller_cli.py via the apply_command dispatch.
2. The MCP server adds typed function wrappers for those commands.
3. Read-only inspection functions are added for the new skill's state.
4. A prompt template is added for the skill's primary workflow.
5. The escape hatch (run_command) covers any commands not yet wrapped.


## 9. Technical Notes

### Dual code path (validated vs direct)

Most MCP functions delegate to the controller for validation and state mutation. There is one code path for validated mutations:

    MCP function -> _run() -> controller_cli.apply_command() -> state.json

The direct-editing functions (set_field, add_bay, remove_bay, clone_bay) read and write state.json directly, bypassing the controller's validation:

    MCP function -> state.json (no controller validation)

This is intentional. Some fields (meta.notes, print.dpi, bambu.printer_ip) have no CLI command, and operations like creating or deleting bays were previously impossible through the CLI. The trade-off is that direct edits are not validated by the controller, so incorrect values are possible. The validate_state function catches structural errors after direct edits.

Use the validated path when the controller has a command for what you want to do. Use the direct path when it does not.

### stdout vs stderr

MCP communicates over stdio using JSON-RPC. The server redirects Python's `print()` to stderr at startup so that CLI debug output does not corrupt the protocol stream. stdout is reserved exclusively for JSON-RPC messages.

### State file concurrency

There is no file locking. The MCP server and the terminal CLI should not write to the same state file simultaneously. In practice this is fine -- they take turns. The Rhino watcher is read-only.

### Schema migration

The MCP server applies the same schema migrations as the terminal CLI on every load. Old state files always work.

### Error handling

If a command fails, the function returns a string starting with `ERROR:`. The AI sees this and can retry, adjust parameters, or ask the user for clarification. The state file is not modified on error.

### Dependencies

    mcp (pip package, v1.26.0)
      Only external dependency.
      Provides FastMCP class for tool/resource/prompt registration.
      Handles JSON-RPC protocol over stdio.

    controller_cli.py -- Python 3 stdlib only. No pip packages.
    auditor.py -- Imports controller_cli for geometry helpers. Python 3 stdlib only.
    skill_manager.py -- Python 3 stdlib only (json, os, re). Reads/writes skills/*.json.
    rhino_client.py -- Python 3 stdlib only (socket, json, threading). Connects to localhost:1998.
    rhino_watcher.py -- IronPython 2.7 (runs inside Rhino, not standalone). No pip packages.

The only pip install you ever need is: `pip install mcp`.

### Why not rhinomcp

rhinomcp is a different project that connects Claude directly to Rhino's geometry engine over a TCP socket. It has a C# plugin inside Rhino and a Python MCP server outside.

We chose not to use it for five reasons:

1. rhinomcp treats Rhino as the source of truth. We treat state.json as the source of truth. These are incompatible philosophies.

2. rhinomcp requires installing a C# plugin in Rhino. We already have a watcher running inside Rhino via IronPython. Adding a second integration point creates complexity.

3. rhinomcp has no semantic layer. It works with GUIDs and geometry primitives (spheres, boxes, curves). We work with bays, corridors, doors, and rooms. Our abstraction level is higher.

4. rhinomcp's viewport capture tool is visual-only. Our project is accessibility-first. Information must be available as text.

5. If Rhino crashes with rhinomcp, your work is gone (unless you saved the .3dm file). With our approach, the state.json file is always current and Rhino can be restarted at any time.

We built our own Rhino bridge instead: a small TCP listener inside the watcher that answers read-only queries on port 1998 (not 1999, to avoid conflicting with rhinomcp). This gives us the useful parts (querying object counts, bounding boxes, running diagnostic scripts) without the architectural conflicts.
