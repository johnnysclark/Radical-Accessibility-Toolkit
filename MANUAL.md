# Radical Accessibility Toolkit — Startup Instructions

How to get the system running. For the full manual see docs/MANUAL.md.
For the AI integration guide see docs/MCP_GUIDE.md.

## What This Is

A text-based architectural design platform for blind, low-vision,
and sighted designers. You type commands in a terminal to create
building layouts, generate tactile output, and describe images.
No screen required.

## Tools

Layout Jig (controller/controller_cli.py)
  The primary design tool. Structural grids, walls, doors,
  corridors, rooms, legends, section cuts, 3D tactile export.

Image Describer (tools/image-describer/arch_alt_text.py)
  Structured text descriptions of architectural images
  using Claude vision.

Tactile Printer (tools/rhino/tactile_print.py)
  Watertight STL mesh export for 3D printing on Bambu Lab printers.
  No Rhino required.

Rhino Viewer (tools/rhino/rhino_watcher.py)
  Watches the state file and renders geometry in Rhino.
  Read-only viewer — Rhino is never the source of truth.

## Two Ways to Use the System

There are two independent ways to interact with the Layout Jig.
You can use either one or both at the same time.

1. Interactive CLI — you type commands directly in a terminal.
   This is the controller. It gives you a >> prompt and you
   type commands like "set bay A rotation 30". No setup needed
   beyond Python.

2. AI assistant via MCP — Claude types the commands for you.
   You talk to Claude in natural language ("rotate bay A by 30
   degrees") and Claude calls the right MCP function. This
   requires the MCP server (a separate process) and pip install mcp.

Both write to the same state.json file. The Rhino viewer watches
that file and redraws whenever it changes, regardless of which
method made the change.

## Step 1: Start the Controller (Interactive CLI)

```
python controller/controller_cli.py
```

This starts the interactive terminal. You will see:

```
PLAN LAYOUT JIG v2.3 — Terminal CLI
State: /path/to/controller/state.json
Type 'help' for commands, 'describe' for full model info.

>>
```

What is now available:
- A >> prompt where you type commands
- Full undo stack (type "undo" to revert the last change)
- Automatic history (every change is saved to history/)
- Named snapshots (save and restore design states)
- Text-to-speech (add --tts flag to enable, or type "tts on")
- Bambu 3D printing (if tactile_print.py is available)

What is NOT started:
- The MCP server (that is a separate process, see Step 3)
- Rhino (that is optional, see Step 2)

Or with a custom state file location:
```
python controller/controller_cli.py --state "/projects/studio/state.json"
```

## Step 2: Connect Rhino (Optional)

You do not need Rhino to design. The model lives in state.json
and the CLI works without any visual output. But if you or a
sighted collaborator wants to see the drawing update live:

Type inside the controller:
```
>> setup rhino
OK: Launching Rhino with watcher...
OK: Connected. Rhino is ready. Units: Feet.
```

Or start the watcher manually in Rhino's Python editor:
```python
import sys
sys.path.insert(0, r"C:\path\to\tools\rhino")
import rhino_watcher as w
w.start_watcher()
```

If Rhino crashes, nothing is lost. Restart Rhino, run the watcher
again, and everything rebuilds from state.json.

## Step 3: Enable AI Assistant via MCP (Optional)

To let Claude drive the system conversationally:

```
pip install mcp
```

Then create .mcp.json at the project root:
```json
{
  "mcpServers": {
    "layout-jig": {
      "command": "python",
      "args": ["mcp/mcp_server.py", "--state", "controller/state.json"]
    }
  }
}
```

Claude Code, Claude Desktop, or Cursor will start the MCP server
automatically when they connect. You do not need to run it manually.

The MCP server gives Claude access to 46 functions: everything
the CLI can do, plus auditing, skills, Rhino queries, and direct
state editing. See docs/MCP_GUIDE.md for the full reference.

## Step 4: Verify

Type `describe` to hear a summary of the current model.
Type `help` for a list of all commands.

## Requirements

Python 3.8 or later (stdlib only — no pip install needed for the CLI).
Rhino 7 or 8 with IronPython 2.7 (only if you want the visual viewer).
For the MCP server: pip install mcp (see mcp/requirements.txt).
For image description: a Claude API key.

## Full Documentation

Complete manual with all commands, tools, and extension guide:
  docs/MANUAL.md

AI layer — MCP architecture, setup, and 46-function reference:
  docs/MCP_GUIDE.md

Test walkthrough — how to verify everything works:
  docs/TEST_MANUAL.md
