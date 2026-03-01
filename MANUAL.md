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

## Step 1: Start the Controller

```
python controller/controller_cli.py
```

Or with a custom state file location:
```
python controller/controller_cli.py --state "/projects/studio/state.json"
```

## Step 2: Connect Rhino (Optional)

If you want visual output, type inside the controller:
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

## Step 3: Verify

Type `describe` to hear a summary of the current model.
Type `help` for a list of all commands.

## Requirements

Python 3.8 or later (stdlib only — no pip install needed for the CLI).
Rhino 7 or 8 with IronPython 2.7 (only if you want the visual viewer).
For the MCP server: pip install mcp (see controller/requirements.txt).
For image description: a Claude API key.

## Full Documentation

Complete manual with all commands, tools, and extension guide:
  docs/MANUAL.md

AI layer — MCP architecture, setup, and 46-function reference:
  docs/MCP_GUIDE.md

Test walkthrough — how to verify everything works:
  docs/TEST_MANUAL.md
