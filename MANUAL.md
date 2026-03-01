# Radical Accessibility Toolkit — Quick Start

The Radical Accessibility Toolkit is a text-based architectural design platform
for blind, low-vision, and sighted designers. You type commands in a terminal
to create building layouts, generate tactile output, and describe images —
no screen required.

## Tools

Layout Jig (controller/controller_cli.py)
  The primary design tool. Define structural grids, walls, doors,
  corridors, rooms, and more via typed or spoken commands.

Image Describer (image-describer/arch_alt_text.py)
  Generates structured text descriptions of architectural images
  using Claude vision.

Tactile Printer (controller/rhino/tactile_print.py)
  Exports the model as watertight STL mesh for 3D printing
  on Bambu Lab printers. No Rhino required.

Rhino Viewer (controller/rhino/rhino_watcher.py)
  Watches the state file and renders geometry in Rhino.
  Read-only viewer — Rhino is never the source of truth.

## Taxonomy

Tool — a major capability module (Layout Jig, Image Describer, etc.).
Command — an individual action within a tool ("set bay A rotation 30").
Skill — a saved sequence of commands, replayable with parameters.
  Stored as JSON in skills/.

## Quick Start

1. Start the controller:
   python controller/controller_cli.py

2. Optionally connect Rhino for visual output:
   setup rhino

3. Type "describe" to hear a summary of the current model.

4. Type "help" for a list of all commands.

## Requirements

Python 3.8 or later (stdlib only — no pip install needed for the CLI).
Rhino 7 or 8 with IronPython 2.7 (only if you want the visual viewer).
For the MCP server: see controller/requirements.txt.
For image description: a Claude API key.

## Full Documentation

Complete manual with all commands and tools:
  docs/MANUAL.md

AI integration and MCP function reference:
  docs/MCP_GUIDE.md
