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
  corridors, rooms, legends, section cuts, zones, grids,
  export, and all output modes.

Image Describer (tools/image-describer/arch_alt_text.py)
  Structured text descriptions of architectural images
  using Claude vision.

Braille Module (controller/braille.py)
  Grade 1/2 braille translation. Stdlib-only. Used by all tools.

Rhino Viewer (tools/rhino/rhino_watcher.py)
  Watches the state file and renders geometry in Rhino.
  Read-only viewer — Rhino is never the source of truth.

TACT -- Tactile Conversion (tools/tact/)
  All tactile output in one tool. Renders state.json to PIAF-ready
  tactile PDFs (replaces swell-print) and converts images to tactile
  graphics. Ten presets, density management, braille labels, OCR text
  detection, color-to-tactile pattern mapping, Grade 2 Braille, and
  7 MCP functions. Optional.

acclaude -- Accessible Claude Client (tools/accessible-client/)
  Screen-reader-friendly Claude Code wrapper. Bypasses the
  Ink TUI for JAWS/NVDA compatibility. Optional.

## Three Output Modes

The same model produces three kinds of physical output:

1. 2D Plan Drawing — black and white architectural plan for
   pen plotting or PDF export. Configure with "set print" and
   "set style" commands. Output from Rhino as PDF or PNG.

2. PIAF / Swell Paper — the 2D plan printed on microcapsule
   paper and run through a swell machine. Dark areas rise to
   create a tactile floor plan readable by touch. The system
   has PIAF-optimised hatches, braille labels, tactile block
   symbols, and a braille legend specifically for this.

3. 3D Tactile Print — walls extruded into a physical model,
   exported as STL, and 3D printed on a Bambu Lab printer.
   Configure with "tactile3d" and "bambu" commands.

All three outputs come from the same state.json. Change the
model once, all outputs update.

## IMPORTANT: What Runs Where

The system has TWO separate Python environments. Do not mix them.

1. cmd.exe terminal (Python 3) — runs the controller, MCP server,
   TACT, and all design tools. Open a Windows Command
   Prompt (cmd.exe) and type commands there.

2. Rhino Python editor (IronPython 2.7) — runs ONLY the watcher
   script (tools/rhino/rhino_watcher.py). Nothing else.

Do NOT open controller_cli.py in Rhino. It uses Python 3 syntax
(f-strings, pathlib, etc.) and will show "SyntaxError: invalid
syntax" if you try to run it in Rhino's IronPython 2.7.

## Two Ways to Use the System

There are two independent ways to interact with the Layout Jig.
You can use either one or both at the same time.

1. Interactive CLI — you type commands directly in a cmd.exe
   terminal. This is the controller. It gives you a >> prompt
   and you type commands like "set bay A rotation 30". Requires
   Python 3.10 or later. No setup needed beyond Python.

2. AI assistant via MCP — Claude types the commands for you.
   You talk to Claude in natural language ("rotate bay A by 30
   degrees") and Claude calls the right MCP function. This
   requires the MCP server (a separate process) and pip install mcp.

Both write to the same state.json file. The Rhino viewer watches
that file and redraws whenever it changes, regardless of which
method made the change.

## Step 1: Start the Controller (Interactive CLI)

Open cmd.exe (not Rhino, not Windows Terminal). Then type:

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
- 2D plan output settings (set print scale, paper, dpi)
- PIAF-ready hatches, braille labels, and tactile symbols
- 3D tactile print pipeline (tactile3d and bambu commands)
- Section cuts exported as SVG

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

Open Rhino, then open the Python editor (EditPythonScript or F2).
Paste these TWO lines and press F5 to run them:

```
__file__ = r"C:\path\to\Radical-Accessibility-Toolkit\tools\rhino\rhino_watcher.py"
exec(open(__file__).read())
```

Replace the path with wherever your CONTROLLER folder is. The
first line tells the watcher where it lives so it can find
state.json automatically (at controller/state.json, two folders
up from the watcher).

The watcher will print status to the Rhino command line. It reads
state.json and rebuilds geometry automatically.

IMPORTANT: Only rhino_watcher.py runs inside Rhino. Do NOT open
controller_cli.py, mcp_server.py, or any other file in Rhino.
Those are Python 3 files and will fail with syntax errors.

If Rhino crashes, nothing is lost. Restart Rhino, run the watcher
again, and everything rebuilds from state.json.

## Step 3: Enable AI Assistant via MCP (Optional)

To let Claude drive the system conversationally, run the setup
script from the repo root:

```
python setup.py
```

This does everything: checks Python 3.10+, installs dependencies
(mcp, tact with easyocr), creates .mcp.json with correct paths,
initializes state.json if missing, and tests MCP server readiness.
Output uses OK:/ERROR: prefixes for screen readers.

If you prefer manual setup, create .mcp.json in the repo root:

```json
{
  "mcpServers": {
    "layout-jig": {
      "command": "python",
      "args": [
        "mcp/mcp_server.py",
        "--state",
        "controller/state.json"
      ]
    },
    "tactile": {
      "command": "python",
      "args": ["tools/tact/mcp_entry.py"]
    }
  }
}
```

Claude Code, Claude Desktop, or Cursor will start the MCP servers
automatically when they connect. You do not need to run them manually.
No API keys needed — MCP servers run through the Claude Code subscription.

The MCP server gives Claude access to 58 functions: everything
the CLI can do, plus zone/grid/export, auditing, skills, Rhino
queries, direct state editing, and script generation. TACT adds
7 more tactile-specific MCP functions via its own server.
See docs/MCP_GUIDE.md for the full reference.

## Step 4: Verify

Type `describe` to hear a summary of the current model.
Type `help` for a list of all commands.

## Step 5: Learn Scripting (Mode 3 — Optional)

Once you are comfortable with Mode 1 (Claude) and Mode 2 (CLI), you
can start writing your own Rhino Python scripts.

Ask Claude: "Generate a script that draws a circle at each column"

Claude creates a .py file in the controller/scripts/ folder with
teaching comments explaining each line. Open it in any text editor,
modify it, and run it in Rhino's EditPythonScript (F5). Over time,
you build fluency in Python and rhinoscriptsyntax.

See DESIGN_SESSION.md for a complete walkthrough showing all three
modes during a school building design project.

## Step 6: Install Tactile Tools (Optional)

TACT handles all tactile conversion. It renders state.json to
PIAF-ready tactile PDFs and converts images to tactile graphics.
It also provides OCR text detection, color-to-tactile pattern
mapping, and Grade 2 Braille output.

Install TACT:

```
pip install -e tools/tact
```

System dependencies (for text detection -- Tesseract is the
fallback OCR engine; EasyOCR is primary and installs via pip):

```
apt install tesseract-ocr poppler-utils    # Ubuntu/Debian
brew install tesseract poppler              # macOS
```

LibLouis for Grade 2 Braille (optional):

```
apt install liblouis-dev python3-louis      # Ubuntu/Debian
brew install liblouis                        # macOS
```

Key commands:

```
tact render                          # render state.json to tactile PDF
tact render --state /path/state.json # render a specific state file
tact convert photo.jpg               # convert image to tactile
tact convert photo.jpg --preset high_contrast --verbose
tact presets                         # list all 10 presets
```

To add TACT's MCP server to Claude Code, add a "tactile" entry to
your .mcp.json. See .mcp.json.example for the correct format. This
gives Claude 7 MCP functions for tactile conversion (image_to_piaf,
list_presets, analyze_image, describe_image, extract_text_with_vision,
assess_tactile_quality, state_to_piaf). All tactile MCP functions live in TACT's
server, not in the main layout-jig server.

## Step 7: Set Up Accessible Client (Optional)

If you use JAWS or NVDA and find Claude Code's Ink TUI difficult
to read, use acclaude instead. It wraps Claude Code in headless
mode with plain text output.

Requirements: Node.js 18 or later, Claude Code CLI installed.

Windows:

```
tools\accessible-client\acclaude.bat
```

WSL2 or Linux:

```
./tools/accessible-client/acclaude
```

Type /help at the prompt for available commands. Sessions persist
across restarts at ~/.radical-accessibility/memory/.

For screen reader event hooks (automatic image detection, conversion
tracking), see tools/screen-reader-hooks/README.md for installation
into your Claude Code settings.

## Quick Start Workflow: Design to Tactile Print

This shows the full path from an empty model to a physical
tactile floor plan Daniel can read by touch. Takes about
10 minutes.

```
# 1. Start the CLI
python controller/controller_cli.py

# 2. Set up the site and bay
>> set site width 150
>> set site height 100
>> set bay A origin 20 20
>> set bay A bays 3 2
>> set bay A spacing 24 24

# 3. Add walls, corridor, and a door
>> wall A on
>> corridor A on
>> corridor A width 8
>> aperture A add d1 door x 0 10 3.5 7

# 4. Name rooms with different hatches (so Daniel can
#    tell them apart by texture)
>> cell A 0,0 name "Classroom"
>> cell A 0,0 hatch diagonal
>> cell A 2,0 name "Office"
>> cell A 2,0 hatch crosshatch

# 5. Check your work
>> describe

# 6. Generate a tactile print directly from the CLI
#    (the print command calls tact render internally)
>> print
OK: Print requested (id=1).
  Output: /path/to/controller/state_tactile.pdf
  Density: 24.1%

# 7. Print the PDF on swell paper with a laser printer
#    (must use carbon-based black toner)
# 8. Feed the printed sheet through the PIAF heater
# 9. Dark areas swell into raised lines — Daniel reads
#    the floor plan by touch
#
# Braille labels are rendered at BANA standard size
# (30pt, 10mm line spacing) regardless of model scale.
# English text renders at 12pt.
```

The same model also produces a 3D printed tactile model
(via tactile3d and bambu commands) and a standard 2D plan
drawing (via Rhino). Change the model once, all outputs update.

## Requirements

Python 3.10 or later (stdlib only — no pip install needed for the CLI).
Rhino 7 or 8 with IronPython 2.7 (only if you want the visual viewer).
For MCP + TACT: python setup.py (installs everything).
No API keys needed — MCP servers run through the Claude Code subscription.
For acclaude: Node.js 18+ and Claude Code CLI.

## Full Documentation

Complete manual with all commands, tools, and extension guide:
  docs/MANUAL.md

AI layer — MCP architecture, setup, and function reference:
  docs/MCP_GUIDE.md

Design session walkthrough (all 3 interaction modes):
  DESIGN_SESSION.md

Test walkthrough — how to verify everything works:
  docs/TEST_MANUAL.md

Tactile conversion (TACT):
  tools/tact/README.md

Accessible client (acclaude):
  tools/accessible-client/README.md
