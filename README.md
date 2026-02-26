# Radical Accessibility Project

Terminal-driven architectural design tools built for blind and low-vision architecture students. Part of the Radical Accessibility Project at UIUC School of Architecture.

The project treats non-visual interaction as the primary design case. All design intent is expressed through typed commands and confirmed through text output compatible with screen readers (JAWS, NVDA) and braille displays.

Led by John Clark and Hugh Swiatek, UIUC School of Architecture. The primary user and co-designer is Daniel, a blind sophomore architecture student.

## Tools

### [Layout Jig](layout-jig/) — 2D/3D Architectural Plan Generator

A terminal CLI that generates architectural floor plans with structural grids, walls, apertures, corridors, rooms, and braille labels. Outputs to Rhino via a file-watching pattern.

```
Terminal (controller_cli.py)
        |
        | writes
        v
    state.json  (canonical model artifact)
        |
        | watches (file mtime)
        v
Rhino 8 (rhino_watcher.py)
        |
        v
    2D plan drawing + optional 3D tactile model
```

**Features:** Rectangular/radial grids, walls with doors/windows/portals, corridors, cell rooms with hatch patterns, braille legends, PIAF-optimized line weights, 3D printing pipeline (Bambu Lab), section cuts, text-to-speech, history/snapshots, MCP server for AI integration.

```
>> set bay A origin 20 10
OK: Bay A origin = (20.0, 10.0). Was (18.0, 8.0).

>> wall A on
OK: Bay A walls ON, 6-inch thick.

>> describe
(full model description, screen-reader-friendly)
```

[Full Layout Jig documentation](layout-jig/)

---

### [Arch-Alt-Text](arch-alt-text/) — Architectural Image Describer

A terminal CLI that describes architectural images for blind users using Claude's vision API. Produces structured Macro / Meso / Micro descriptions optimized for screen readers.

Replaces visual image interpretation with detailed text descriptions covering composition, materials, spatial relationships, and multi-sensory analogies.

```
python arch-alt-text/arch_alt_text.py

>> describe farnsworth_plan.jpg
Processing... this may take a moment.

Title: Farnsworth House — Floor Plan

Macro: A measured architectural floor plan rendered in fine black lines
on white background depicts a single-story residential pavilion...

Meso: The rectangular plan occupies the center of the sheet, oriented
with its long axis running left to right...

Micro: Eight wide-flange steel columns support the roof plane, spaced
in two rows of four along the long edges...
```

**Features:**
- Structured output: Title, Macro (3 sentences), Meso (4+ sentences), Micro (8+ sentences)
- Handles photos, drawings, plans, sections, diagrams, charts, simulations, fabrication images
- Interactive mode with command history and description archive
- Single-shot mode for scripting: `python arch_alt_text.py photo.jpg`
- Saves descriptions as text files beside the original image
- Multi-sensory analogies (tactile, acoustic, thermal) to strengthen spatial imagination
- Python stdlib only — no pip installs. Just needs an Anthropic API key.

**Setup:**
```
cd arch-alt-text
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
python arch_alt_text.py
```

**Commands:**
```
describe <path-or-url> .... Describe an image
save ....................... Save last description as .txt beside the image
last ....................... Repeat the last description
history .................... List all past descriptions
history <n> ................ Show description number N
model <name> ............... Change the Claude model
help ....................... All commands
quit ....................... Exit
```

---

### Tactile Paper Output — PIAF Swell Paper Pipeline (Working)

Converts digital architectural drawings into tactile graphics on PIAF swell paper. This workflow is in daily use for producing plan drawings, diagrams, and precedent studies that Daniel can read by touch.

```
Digital drawing (Rhino / image file)
        |
        | convert to grayscale / vector
        v
    High-contrast black-and-white image
        |
        | laser print (carbon-based black toner required)
        v
    Printed sheet on swell paper (microcapsule paper)
        |
        | feed through PIAF heater
        v
    Raised tactile graphic (carbon toner swells, white stays flat)
```

**Features:**
- Image-to-grayscale conversion optimized for tactile legibility
- Four line weight conventions: heavy (columns/structure), medium (corridors/walls), light (grid lines), fine (hatches/textures)
- Halftone and dithering for tonal areas (e.g., shading, material fills)
- Braille label integration using Grade 2 contracted braille
- Page tiling with registration marks aligned to the Layout Jig grid for multi-sheet drawings
- Carbon-based black toner is required — only carbon toner swells when heated by the PIAF machine

---

### 3D Printer Output — Tactile Model Pipeline (Partially Working)

Generates watertight STL meshes from parametric models for 3D printing on a Bambu Lab P1S. Produces scale tactile models that Daniel can hold and feel during design review. The `tactile_print.py` script in the layout-jig folder handles mesh generation.

```
Parametric model (state.json)
        |
        | generate geometry (Rhino/Grasshopper)
        v
    3D mesh
        |
        | solid checks: naked edges, self-intersections, hole-fill
        v
    Watertight STL
        |
        | export to Bambu Lab P1S
        v
    3D-printed tactile model
        |
        | feel, review, iterate
        v
    Design feedback back to CLI
```

**Features:**
- Parametric model to watertight STL mesh generation
- Solid validation: naked edge detection, self-intersection checks, automatic hole-filling
- Export pipeline to Bambu Lab P1S printer
- Scale model output calibrated for tactile design review
- Physical-digital feedback loop: model digitally, print, feel, iterate

---

### Spoken Command Interface (Early Prototype)

Voice-based interaction layer for hands-free operation. Combines Windows speech recognition for input with text-to-speech for output, plus META Ray-Ban glasses for real-time scene description.

```
Voice input (Windows SAPI / speech recognition)
        |
        | transcribe to text
        v
    CLI command dispatch
        |
        | execute command, update state
        v
    Text-to-speech readback (Windows SAPI TTS)
        |
        v
    Spoken confirmation of parameter changes
```

**Features:**
- Windows SAPI text-to-speech for parameter readback and confirmations
- Voice input via speech recognition dispatched to CLI commands
- META Ray-Ban glasses integration for real-time scene description ("Hey Meta, describe what's in front of me")
- Auditory feedback loops for spatial awareness during design review
- **Status:** Early prototype. Voice input and TTS readback work independently; full pipeline integration is in development.

---

### AI Assistant Layer (In Development)

Natural language interface for design operations using an MCP (Model Context Protocol) server. Enables conversational interaction with the model — ask questions, request changes, and get descriptions in plain English. The MCP server (`mcp_server.py`) is in the layout-jig folder.

```
User (natural language)
        |
        | "make the corridor wider"
        v
    LLM (Claude) interprets intent
        |
        | generates CLI command or Python code
        v
    CLI command dispatch / code execution
        |
        | update state.json
        v
    Confirmation + description readback
```

**Features:**
- MCP server for natural language to Rhino/Grasshopper commands
- LLM-powered code generation: plain English to Python to geometry
- Conversational model queries ("describe the north elevation", "how wide is bay A?")
- Error-aware retries from stack traces
- Integration with Arch-Alt-Text for image description of exported views
- **Status:** Actively prototyped. MCP server is in the repo (`layout-jig/mcp_server.py`). LLM workflow is proven; integration into Daniel's daily workflow is ongoing.

---

## Architecture Principles

All tools in this project follow these principles:

- **Text is the universal interface.** Every command is typed. Every response is printed. Everything works with screen readers.
- **The JSON is the design.** State files capture complete design intent. Viewports are renderings, not the source of truth.
- **Crash-only viewer.** Rhino can crash anytime. The design lives in state files, not in application memory.
- **Zero dependencies.** Controllers use Python stdlib only. No pip, no conda, no venv.
- **Atomic writes.** State is written via tmp file + os.replace. Watchers never read half-written files.
- **Accessibility is not an add-on.** If it can't be heard, felt, or read by a screen reader, it doesn't ship.

## Requirements

- **Python 3.8+** (stdlib only for controllers — no pip installs)
- **Rhino 8** (for layout-jig watcher; controllers run independently)
- **Windows** (Rhino requirement; controllers work cross-platform)
- **Anthropic API key** (for arch-alt-text and AI assistant layer)
- **PIAF machine + laser printer with carbon-based toner** (for tactile paper output)
- **Bambu Lab P1S 3D printer** (for tactile model output)
- **META Ray-Ban glasses** (optional — for spoken/vision features)

## Repository Structure

```
radical-accessibility/
  arch-alt-text/
    arch_alt_text.py ..... Image description CLI (Python 3, Claude vision API)
  layout-jig/
    controller_cli.py .... Terminal CLI (Python 3, stdlib only)
    rhino_watcher.py ..... Rhino file watcher (IronPython 2.7)
    tactile_print.py ..... STL mesh generation + Bambu printing
    mcp_server.py ........ MCP server for AI assistant integration
    state.json ........... Canonical model artifact
    MANUAL.docx .......... Full user documentation
  tactile-output/ ........ Tactile graphics pipeline (planned)
  CLAUDE.md .............. Project instructions for AI coding assistants
  README.md
```

## Project Context

This project explores what happens when architectural design tools are built for blindness first. The thesis: accessibility constraints produce genuinely better workflows — crash resilience, semantic clarity, auditable state, and full keyboard operability emerge naturally when visual interaction is removed as a dependency.

The primary user is Daniel, a blind sophomore architecture student at UIUC who co-designs all tools and uses JAWS/NVDA with a braille display.

Led by John Clark and Hugh Swiatek, UIUC School of Architecture.

## License

MIT
