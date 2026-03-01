# How the MCP Layer Works

This document explains what the MCP server does, how it fits into the
Layout Jig architecture, and how every piece connects.

---

## What MCP Is

MCP stands for Model Context Protocol. It is a standard created by
Anthropic that lets an AI assistant (Claude) call functions on your
computer. Instead of you typing commands, Claude reads the tool
descriptions, decides which one to call, fills in the parameters,
and sends the call. The MCP server executes it and returns the result.

Think of it this way:

- Without MCP: you type "set bay A rotation 30" into a terminal.
- With MCP: you say "rotate bay A by 30 degrees" and Claude types the
  command for you by calling set_bay("A", "rotation", "30").

The MCP server is the translator between Claude's intent and your CLI.

---

## The Three-File Architecture

The Layout Jig has three files that form a pipeline. The MCP server
sits in front of this pipeline as a fourth layer.

### Layer 1: state.json (the Canonical Model Artifact)

This is a JSON file on disk. It contains every fact about your design:
site dimensions, bay positions, wall thicknesses, door locations,
corridor widths, labels, hatches, and print settings.

This file is the single source of truth. If Rhino crashes, the model
is still safe in this file. If the MCP server crashes, the model is
still safe in this file. If the computer restarts, the model is still
here.

Everything else reads from or writes to this file. Nothing else is
authoritative.

### Layer 2: controller_cli.py (the state machine)

This is a Python script that knows every legal operation on the model.
It has about 2,000 lines of code organized into command handlers:

- cmd_corridor: turn corridors on/off, set width/axis/loading
- cmd_wall: turn walls on/off, set thickness
- cmd_aperture: add/remove/modify doors, windows, portals
- cmd_cell: name cells, assign hatches
- cmd_room: list named rooms
- cmd_legend: configure the legend
- cmd_tactile3d: configure 3D printing parameters
- cmd_section: set section cuts
- And about a dozen more

Every command handler follows the same pattern:

    def cmd_something(state, tokens):
        # validate input
        # mutate the state dict
        # return (state, "OK: what changed")

The controller reads state.json, applies your command, and writes
the modified state back to state.json. It uses atomic writes (write
to a .tmp file, then rename) so the file is never half-written.

The controller also maintains an undo stack. Before every mutation,
it stores a deep copy of the state. If you type "undo", it restores
the previous copy.

### Layer 3: rhino_watcher.py (the geometry renderer)

This is an IronPython 2.7 script that runs inside Rhino. Every half
second, it checks if state.json has been modified. If it has, the
watcher deletes all geometry in Rhino and rebuilds everything from
scratch based on the new state.

The watcher never writes to state.json. It is read-only. It translates
the semantic model (bays, walls, apertures) into actual Rhino geometry
(lines, rectangles, arcs, hatches, text labels).

If Rhino crashes, you restart it, run the watcher again, and everything
rebuilds automatically from state.json.

### Layer 4: mcp_server.py (the MCP orchestrator)

This is the newest layer. It wraps the controller CLI so that Claude
can call commands as typed function calls instead of raw strings.

Most MCP tools delegate to the controller for validation and state
mutation. There is exactly one code path for validated mutations:
MCP tool -> _run() -> controller_cli.apply_command() -> state.json.

The v3.1 tools add a second code path for direct editing. Tools
like set_field, add_bay, remove_bay, and clone_bay read and write
state.json directly, bypassing the controller's validation. This is
intentional: some fields (meta.notes, print.dpi, bambu.printer_ip)
have no CLI command, and operations like creating or deleting bays
were previously impossible through the CLI. The trade-off is that
direct edits are not validated by the controller, so incorrect
values are possible. The validate_state tool catches structural
errors after direct edits.

---

## How the MCP Server Connects to the Controller

The central function is _run():

    def _run(command_str):
        state = _load_state()           # read state.json from disk
        tokens = cli.tokenize(cmd)      # split into words
        state, msg = cli.apply_command(state, tokens)  # execute
        cli.save_state(STATE_PATH, state)              # write back
        return msg                      # return result to Claude

Every MCP tool eventually calls _run() with a CLI command string.
For example:

    set_bay("A", "rotation", "30")

becomes:

    _run("set bay A rotation 30")

which calls:

    cli.apply_command(state, ["set", "bay", "A", "rotation", "30"])

which calls:

    _cmd_set_bay(state, ["set", "bay", "A", "rotation", "30"])

which mutates state["bays"]["A"]["rotation_deg"] = 30.0 and returns:

    (state, "OK: Bay A rotation = 30.0 deg. Was 0.0 deg.")

The MCP server saves the state and returns that message to Claude.

---

## The Engines

The MCP v3.0 server added four engines onto this core pipeline.
v3.1 added direct-editing tools built into the MCP server itself.
Each engine is a separate Python file with zero external dependencies.

### Engine 1: Audit Engine (audit_engine.py)

Purpose: answer questions about the model without changing it.

The audit engine reads state.json and computes spatial relationships
using the same math functions the controller uses. It can:

- Check for overlapping bays
- Check if bays extend outside the site
- Validate that apertures fit within their walls
- Check ADA compliance (door widths, corridor widths)
- Find orphaned room references
- Flag missing labels

It also produces rich narrative descriptions of individual bays and
corridor connectivity, designed for screen readers.

The audit engine never writes to state.json. It is purely analytical.

How it connects to MCP: Five tools call directly into audit_engine
functions, passing the loaded state dict. No CLI commands involved.

    audit_model() -> audit_engine.audit_model(state)
    audit_bay("A") -> audit_engine.audit_bay(state, "A")
    describe_bay("A") -> audit_engine.describe_bay(state, "A")
    describe_circulation() -> audit_engine.describe_circulation(state)
    measure("bay A origin", "bay B center") -> audit_engine.measure(state, ...)

### Engine 2: Skill Engine (skill_engine.py)

Purpose: save and replay reusable command sequences.

A skill is a JSON file in the skills/ folder. It contains a list of
CLI commands with {parameter} placeholders. When you run a skill,
the engine substitutes parameter values into the commands and executes
each one through _run().

Example skill file (skills/add-double-loaded-corridor.json):

    {
      "name": "add-double-loaded-corridor",
      "commands": [
        "corridor {bay} on",
        "corridor {bay} axis {axis}",
        "corridor {bay} width {width}",
        "corridor {bay} loading double"
      ],
      "params": {
        "bay": {"default": "A"},
        "axis": {"default": "x"},
        "width": {"default": "8"}
      }
    }

When you call skill_run("add-double-loaded-corridor", "bay=B"), the
engine substitutes {bay} with "B" and runs each command:

    _run("corridor B on")
    _run("corridor B axis x")
    _run("corridor B width 8")
    _run("corridor B loading double")

If any command fails, execution stops and the error is reported.

The skill engine reads and writes only to the skills/ folder. It
never touches state.json directly — it goes through _run() which
goes through the controller.

How it connects to MCP: Four tools.

    skill_list() -> skill_engine.list_skills()
    skill_show("name") -> skill_engine.load_skill("name")
    skill_run("name", "bay=B") -> skill_engine.run_skill("name", overrides, _run)
    skill_save("name", "desc", "commands") -> skill_engine.save_skill(...)

### Engine 3: Rhino Bridge (rhino_bridge.py)

Purpose: ask Rhino questions without going through state.json.

The controller and audit engine work entirely from state.json. They
know what the model should look like. But sometimes you want to know
what Rhino actually has: how many objects are on each layer, what the
bounding box of the geometry is, or whether a custom script produces
the expected output.

The rhino bridge is a TCP client. It connects to port 1998 on
localhost. The Rhino watcher has a TCP listener thread that accepts
these connections and answers questions.

Protocol:

    Client sends:  {"type": "layer_stats"}\n
    Server returns: {"status": "ok", "result": {"JIG_COLUMNS": 16, ...}}\n

Supported queries: ping, status, layer_stats, bounding_box,
object_count, run_script.

The run_script query sends Python code to Rhino's IronPython engine.
The watcher blocks any geometry-modifying calls (AddLine, DeleteObject,
etc.) so this is strictly read-only.

Critical design: if Rhino is not running, the bridge returns an
OFFLINE message. It never crashes. It never blocks. Every tool that
uses the bridge can handle the offline case gracefully. The model
is always accessible through state.json regardless of Rhino's status.

Port 1998 was chosen (not 1999) to avoid conflicting with rhinomcp,
a different project that uses port 1999.

How it connects to MCP: Three tools.

    rhino_status() -> bridge.status()
    rhino_query("layer_stats") -> bridge.query("layer_stats")
    rhino_run_script("import rhinoscriptsyntax as rs\n...") -> bridge.run_script(code)

### Engine 4: Controller Extension (built into mcp_server.py)

Purpose: add new commands to the controller at runtime.

This is the most experimental engine. It lets Claude write a new
command handler function, append it to controller_cli.py, register
it in the dispatch chain, and reload the module — all without
restarting the MCP server.

The process:

1. Claude provides a function name (e.g. cmd_wallarea) and Python
   source code.
2. The MCP server validates the code with ast.parse() to catch
   syntax errors before writing anything.
3. It checks that the function signature is (state, tokens).
4. It checks that the command word does not conflict with existing
   commands (corridor, wall, aperture, etc.).
5. It appends the function to the end of controller_cli.py, just
   before apply_command().
6. It inserts a dispatch line into apply_command():
   if cmd == "wallarea": return cmd_wallarea(state, tokens)
7. It calls importlib.reload(cli) to pick up the new code.
8. It records the extension in state["meta"]["extensions"].

After this, you can use run_command("wallarea") and the new handler
executes like any built-in command.

Safety: This engine only adds code. It never modifies or removes
existing functions. To undo an extension, you would manually edit
controller_cli.py or restore a snapshot.

How it connects to MCP: Two tools.

    extend_controller("cmd_wallarea", "def cmd_wallarea(state, tokens):...")
    list_extensions()

### Engine 5: Direct State Editing (built into mcp_server.py, v3.1)

Purpose: read and write state.json fields without going through
the controller, and manage bays that have no CLI commands.

This engine provides two kinds of tools:

State introspection tools let you access individual JSON fields
using dot-notation paths like "bays.A.corridor.width" or
"style.heavy_lineweight_mm". These paths work at any depth and
support list indices (e.g. "bays.A.apertures.0.type"). Three tools:

    get_field("bays.A.rotation_deg") -> reads one value
    set_field("meta.notes", "\"Library project\"") -> writes one value
    list_fields("bays.A") -> lists all keys in a section

Bay management tools create, delete, and duplicate bays. The CLI
has no commands for this because bays were originally defined in
the initial state.json. Three tools:

    add_bay("C", "rectangular", 50.0, 50.0) -> creates bay C
    remove_bay("C") -> deletes bay C
    clone_bay("A", "D", 80.0, 80.0) -> copies bay A to D

Both sets of tools write to state.json directly without going
through _run() or the controller. They use the controller's
save_state() function for atomic writes, and they call
_auto_rooms() to regenerate room references after bay changes.

### Engine 6: Controller Introspection (built into mcp_server.py, v3.1)

Purpose: let Claude read and understand the controller's source code
before writing extensions.

The list_commands tool parses controller_cli.py with regex to find
all dispatch lines and command handlers. It returns an organized
list of every command the controller understands.

The show_command_source tool reads controller_cli.py and extracts
the full function definition for a named handler. You give it a
command word like "corridor" and it returns the complete source of
cmd_corridor(). This lets Claude study existing patterns before
writing new command handlers with extend_controller.

    list_commands() -> all commands organized by category
    show_command_source("corridor") -> source of cmd_corridor()
    show_command_source("_cmd_set_bay") -> source of _cmd_set_bay()

### Engine 7: State Comparison (built into mcp_server.py, v3.1)

Purpose: compare states and validate JSON structure.

The diff_snapshot tool loads both the current state.json and a saved
snapshot, then walks both dictionaries recursively to find every
field that differs. This is like "git diff" for your model.

The validate_state tool checks that state.json is well-formed: valid
JSON, required sections present, bay fields have correct types,
aperture types are valid. Use this after editing state.json by hand.

    diff_snapshot("before-experiment") -> list of changed fields
    validate_state() -> structural validation report

---

## Data Flow Diagram

When Claude says "rotate bay A by 30 degrees":

    1. Claude reads the set_bay tool description
    2. Claude calls set_bay(bay="A", field="rotation", value="30")
    3. MCP server receives the call
    4. MCP server calls _run("set bay A rotation 30")
    5. _run() reads state.json from disk
    6. _run() tokenizes the command into ["set","bay","A","rotation","30"]
    7. _run() calls cli.apply_command(state, tokens)
    8. Controller dispatches to _cmd_set_bay(state, tokens)
    9. _cmd_set_bay validates and sets state["bays"]["A"]["rotation_deg"] = 30.0
    10. _cmd_set_bay returns (state, "OK: Bay A rotation = 30.0 deg.")
    11. _run() calls cli.save_state() which atomic-writes state.json
    12. _run() returns the message to MCP server
    13. MCP server returns the message to Claude
    14. Claude reads the message and reports it to you
    15. Meanwhile, rhino_watcher.py detects the file change
    16. Watcher reloads state.json and rebuilds all geometry in Rhino

Steps 15-16 happen independently. The MCP call is already done by
step 14. Rhino updates on its own schedule (within 0.5 seconds).

---

## What the MCP Server Does NOT Do

- It does not store state. State lives in state.json only.
- It does not talk to Rhino for mutations. Only the watcher reads
  state.json and creates geometry. The MCP server never tells Rhino
  to draw anything.
- It does not duplicate business logic. Validation rules and command
  handlers live in controller_cli.py. The MCP server delegates to
  the controller for all validated mutations.
- It does not require Rhino to be running. Every tool works offline
  except the three rhino_bridge tools, and even those return graceful
  OFFLINE messages.

Note on v3.1 direct editing: The set_field, add_bay, remove_bay,
and clone_bay tools DO bypass the controller for writes. This is
by design — they handle fields and operations that the controller
has no commands for. The controller remains the authority for
validated mutations (set_bay, add_aperture, etc.). The two code
paths serve different purposes:

    Validated path:  MCP tool -> _run() -> controller -> state.json
    Direct path:     MCP tool -> state.json (no controller validation)

Use the validated path when the controller has a command for what
you want to do. Use the direct path when it does not.

---

## Why Not rhinomcp

rhinomcp is a different project that connects Claude directly to
Rhino's geometry engine over a TCP socket. It has a C# plugin inside
Rhino and a Python MCP server outside.

We chose not to use it because:

1. rhinomcp treats Rhino as the source of truth. We treat state.json
   as the source of truth. These are incompatible philosophies.

2. rhinomcp requires installing a C# plugin in Rhino. We already
   have a watcher running inside Rhino via IronPython. Adding a
   second integration point creates complexity.

3. rhinomcp has no semantic layer. It works with GUIDs and geometry
   primitives (spheres, boxes, curves). We work with bays, corridors,
   doors, and rooms. Our abstraction level is higher.

4. rhinomcp's viewport capture tool is visual-only. Our project is
   accessibility-first. Information must be available as text.

5. If Rhino crashes with rhinomcp, your work is gone (unless you
   saved the .3dm file). With our approach, the state.json file is
   always current and Rhino can be restarted at any time.

We built our own Rhino bridge instead: a small TCP listener inside
the watcher that answers read-only queries. This gives us the useful
parts of rhinomcp (querying object counts, bounding boxes, running
diagnostic scripts) without the architectural conflicts.

---

## How the MCP Server Starts

When Claude Code reads .mcp.json, it sees:

    {
      "mcpServers": {
        "layout-jig": {
          "command": "python",
          "args": ["mcp_server.py", "--state", "state.json"]
        }
      }
    }

Claude Code launches: python mcp_server.py --state state.json

The server:
1. Redirects print() to stderr (stdout is reserved for JSON-RPC)
2. Imports controller_cli.py from the same directory
3. Imports audit_engine.py, skill_engine.py, rhino_bridge.py
4. Registers all 45 tools, 5 resources, and 4 prompts with FastMCP
5. Calls mcp.run() which starts the JSON-RPC stdio loop

From this point, Claude sends JSON-RPC messages over stdin, the
server executes them, and sends results back over stdout. Claude
Code handles all the protocol details. You never see the JSON-RPC
traffic.

---

## Tool Count Summary

| Category | Count | Source |
|----------|-------|--------|
| Original v1.0 tools | 5 | _run() passthrough |
| v2.0 read tools | 4 | _run() passthrough |
| v2.0 bay config tools | 12 | _run() passthrough |
| v3.0 audit tools | 5 | audit_engine.py |
| v3.0 skill tools | 4 | skill_engine.py |
| v3.0 rhino tools | 3 | rhino_bridge.py |
| v3.0 extension tools | 2 | built-in |
| v3.1 state introspection | 3 | get_field, set_field, list_fields |
| v3.1 bay management | 3 | add_bay, remove_bay, clone_bay |
| v3.1 controller introspection | 2 | list_commands, show_command_source |
| v3.1 state comparison | 2 | diff_snapshot, validate_state |
| Total | 45 | |

| Resources | 5 | state, snapshots, help, skills, extensions |
| Prompts | 4 | design_review, aperture_audit, accessibility_audit, skill_builder |

The v3.1 tools bridge three layers:

1. State introspection: Read and write individual JSON fields by
   dot-notation path. This lets Claude (and the user) edit any
   field without needing a CLI command for it. Fields like
   meta.notes, print.dpi, and bambu.printer_ip have no CLI
   command, so set_field is the only MCP way to change them.

2. Bay management: Create, delete, and duplicate bays. The CLI
   has no command for this; bays were previously created by
   hand-editing state.json. Now Claude can do it through MCP.

3. Controller introspection: List all commands and read their
   source code. This lets Claude understand how existing handlers
   work before writing extensions with extend_controller.

4. State comparison: Diff the current state against a snapshot
   (like git diff for your model) and validate JSON structure
   after hand edits.

---

## Dependency Chain

    mcp (pip package, v1.26.0)
      only external dependency
      provides FastMCP class for tool/resource/prompt registration
      handles JSON-RPC protocol over stdio

    controller_cli.py
      Python 3 stdlib only
      no pip packages, no conda, no virtual environment

    audit_engine.py
      imports controller_cli for geometry helpers
      Python 3 stdlib only

    skill_engine.py
      Python 3 stdlib only (json, os, re)
      reads/writes skills/*.json files

    rhino_bridge.py
      Python 3 stdlib only (socket, json, threading)
      connects to localhost:1998 if available

    rhino_watcher.py
      IronPython 2.7 (runs inside Rhino, not standalone)
      uses rhinoscriptsyntax (rs) for geometry
      uses socket for TCP listener
      no pip packages

The only pip install you ever need is: pip install mcp
