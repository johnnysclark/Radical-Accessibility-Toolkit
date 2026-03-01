# Radical Accessibility Project

Architecture assumes you can see. Every mainstream design tool — CAD viewports, drawing sheets, pin-up critiques, even the vocabulary of studio culture — treats vision as a prerequisite for participation. If you're blind, or if you navigate the world through touch, sound, or speech rather than sight, you don't get a lesser version of architectural education. You get locked out entirely. The discipline's deepest bias isn't stylistic — it's perceptual.

The Radical Accessibility Project inverts the premise. Instead of retrofitting visual tools with accommodations, we build from scratch for non-visual interaction as the primary design case. A blind student designs a floor plan by typing commands in a terminal and hearing confirmations read back by a screen reader. A student with limited hand mobility speaks commands instead of dragging a mouse across a viewport. A deafblind student reads model descriptions on a refreshable braille display. A student with a traumatic brain injury or chronic fatigue works in short sessions against a deterministic state file that never loses progress and never demands sustained visual attention. The design itself lives in plain text that any input system — keyboard, voice, switch, sip-and-puff, braille keyboard — can write to, and any output system — speech, braille, tactile print, 3D model, haptic feedback — can read from.

What surprised us is that designing for blindness doesn't just make tools accessible — it makes them better for everyone. Semantic clarity, keyboard and voice operability, auditable state, deterministic output: these aren't accessibility features. They're engineering virtues that visual tools abandoned in favor of graphical convenience. A sighted architect benefits from a command that says exactly what changed and why. A studio instructor benefits from a design state they can diff and review like code. The constraints of non-visual design forced us to build what the discipline should have had all along.

Because the system separates input, logic, and output into independent layers, it extends naturally to disabilities beyond vision loss. Any condition that makes a mouse, a screen, or sustained visual focus unreliable becomes addressable by swapping the input or output layer — not rewriting the design tools. A voice interface serves someone with motor impairment as directly as it serves a blind user. A deterministic text-based state file serves someone with cognitive fatigue as directly as it serves someone using a braille display. The architecture of accessibility-first design turns out to be the architecture of universal design: build for the hardest case and the easier cases follow.

Based at the UIUC School of Architecture, the project is co-designed with Daniel Bein, a blind architecture student who is the primary user of everything we build. His daily workflow — designing, reviewing, fabricating, presenting — is the test case for every tool. Led by John Clark and Hugh Swiatek with student researchers Ethan Anderson, Isaac Tu, and Laura Heuser.

---

## The System

One platform with a shared command shell, undo stack, state management, and screen-reader-native output protocol. Skills plug into this shell. Each skill adds commands and capabilities without touching the others. The system is designed to grow — adding a new skill means writing a new module, not rebuilding the platform. All skills share a common pattern: typed or spoken input, text confirmation output, and a JSON state file as the canonical record of the design. Every skill follows one rule: if it can't be heard, felt, or read by a screen reader, it doesn't ship.

```
Terminal (controller_cli.py)    Claude Code (mcp_server.py)
        |                               |
        | writes                        | calls controller + direct JSON
        v                               v
              state.json  (canonical model artifact)
                      |
                      | watches (file mtime)
                      v
              Rhino 8 (rhino_watcher.py)
                      |
                      v
              2D plan drawing + optional 3D tactile model
```

---

## Skills

### Layout Jig — Architectural Modeler

The primary design skill. Commands like `set bay A rotation 30`, `wall A on`, `corridor A width 8` express design intent through text. A separate Rhino watcher reads the state file and rebuilds geometry. Supports rectangular and radial grids, walls with doors/windows/portals, corridors, rooms, hatches, braille legends, section cuts, and snapshots.

```
>> set bay A origin 20 10
OK: Bay A origin = (20.0, 10.0). Was (18.0, 8.0).

>> wall A on
OK: Bay A walls ON, 6-inch thick.

>> describe
(full model description, screen-reader-friendly)
```

### [Image Describer](image-describer/) — Image Description

Takes an architectural image — a plan, photo, section, diagram — and produces a structured text description at three scales: Macro (what the image is), Meso (how it's organized), Micro (specific elements and measurements). Replaces "looking at a drawing" with text a screen reader can parse.

```
>> describe farnsworth_plan.jpg

Title: Farnsworth House — Floor Plan

Macro: A measured architectural floor plan rendered in fine black lines
on white background depicts a single-story residential pavilion...

Meso: The rectangular plan occupies the center of the sheet, oriented
with its long axis running left to right...

Micro: Eight wide-flange steel columns support the roof plane, spaced
in two rows of four along the long edges...
```

### Image to PIAF — Tactile Drawing Fabrication

Converts digital drawings into physical raised-line graphics readable by touch. High-contrast black-and-white conversion with four line weights (heavy for columns, medium for walls, light for grid, fine for hatches), halftone dithering for tonal areas, Grade 2 contracted braille labels, and page tiling with registration marks. Laser printed on PIAF microcapsule paper with carbon-based toner, then heated — the carbon absorbs heat, the microcapsules swell, and black lines rise off the page. Daniel reads his own floor plans through this pipeline.

```
Digital drawing (Rhino export, image file, or vector graphic)
      |
      v
High-contrast black-and-white conversion
  - Four line weights: heavy (columns), medium (walls), light (grid), fine (hatches)
  - Halftone/dithering for tonal areas (material fills, shading)
  - Grade 2 contracted braille labels
  - Page tiling with registration marks
      |
      v
Laser print on PIAF microcapsule paper (carbon-based black toner required)
      |
      v
Feed through PIAF heater -> raised tactile graphic readable by touch
```

### 3D Print — Tactile Scale Models

Generates watertight triangle meshes from the parametric model (pure Python, no Rhino dependency), validates solidity, and exports binary STL scaled for a Bambu Lab P1S printer. Daniel holds the printed model during design review — walls, corridors, openings physically present at 1:200 scale.

### AI Integration — MCP Server v3.1

An [MCP server](docs/MCP_V3_MANUAL.md) (46 tools, 5 resources, 4 prompts) connects Claude Code to the design system through the Model Context Protocol. Claude makes design changes through natural language, audits the model for ADA compliance, saves and replays reusable command sequences (skills), queries Rhino geometry, and reads or writes individual state fields directly. The server delegates validated mutations to the controller CLI and provides direct JSON access for fields with no CLI command.

Beyond conversational commands, the AI writes RhinoPython, Grasshopper scripts, or other code-based CAD operations on the user's behalf, then explains what it produced so the user learns the underlying language. Over time, Daniel builds fluency in scripting his own geometry. The AI is a bridge to self-sufficiency, not a permanent dependency.

```
User (natural language)
        |
        | "make the corridor wider"
        v
    Claude Code + MCP Server (46 tools)
        |
        | validated: CLI command dispatch
        | direct: JSON field read/write
        v
    state.json mutation + confirmation readback
```

The MCP server has seven functional layers:

- **Core pipeline** (21 tools) — semantic wrappers around CLI commands
- **Auditor** (5 tools) — spatial validation, ADA checks, bay descriptions, circulation analysis, distance measurement
- **Skill manager** (4 tools) — save, list, show, and replay reusable command sequences
- **Rhino client** (4 tools) — TCP queries to the Rhino watcher + auto-launch (offline-safe)
- **Controller extension** (2 tools) — add new command handlers at runtime
- **State introspection** (7 tools) — read/write individual JSON fields, create/delete/clone bays, list commands, show handler source
- **State comparison** (3 tools) — diff against snapshots, validate JSON structure

See [docs/HOW_THE_MCP_WORKS.md](docs/HOW_THE_MCP_WORKS.md) for architecture details, [docs/MCP_V3_MANUAL.md](docs/MCP_V3_MANUAL.md) for the full tool reference, and [docs/TEST_MANUAL.md](docs/TEST_MANUAL.md) for a walkthrough of every workflow.

---

## Input Devices

**Keyboard + Terminal.** The primary interface. All commands are typed. All output is text. Works with JAWS, NVDA, and braille displays.

**Voice.** Speech recognition dispatches spoken commands to the same CLI. Text-to-speech reads back confirmations and descriptions. Hands-free operation for design sessions and reviews.

**Pegboard + Overhead Camera.** A tactile pegboard where Daniel constructs spatial layouts by hand using wire and pegs on a gridded surface. An overhead camera captures the physical construction, OpenCV detects wire positions and peg locations, and the arrangement digitizes into coordinates that feed back into the model. Design by touch, capture by camera, rebuild in CAD. Audio feedback confirms spatial relationships as pieces are placed.

---

## Future Directions

- **Audio simulation of designs** — Spatial audio rendering of architectural models using binaural sound. Walk through a design and hear the space: room volume mapped to reverb, wall proximity to tonal shift, ceiling height to pitch, material hardness to timbre. A blind designer could evaluate the acoustic character of a corridor versus an atrium by listening, building spatial intuition without sight.
- **Vibrotactile interfaces and models** — Physical models and surfaces embedded with vibration motors that encode design information through haptic patterns. A scale model where different vibration frequencies indicate material type, structural load, or thermal zones. A flat surface where vibrotactile feedback traces wall edges and opening locations under the user's fingertips as they explore.
- **Haptic gloves** — Direct tactile feedback on the hands during digital model navigation. Feel wall edges, surface textures, and spatial boundaries without a physical print. Navigate a 3D model by moving your hands through space and feeling the geometry push back.
- **High-resolution interactive tactile display** — A pin-array or similar surface that renders the current design state as a dynamic tactile image, updated live as the model changes. Replaces static PIAF prints with a reusable, real-time tactile screen that redraws when the model is edited.
- **Live AI descriptions with META Ray-Ban glasses** — Continuous scene narration during studio, pin-ups, site visits, and design reviews. Architectural description in real time — not just what's there, but Socratic design questions ("The southern facade is mostly solid — how are you thinking about daylight?").
- **New skills** — The system is built to extend. Future skills could include structural analysis, environmental simulation, collaborative multi-user design, accessibility auditing of buildings themselves, or direct fabrication machine control — each plugging into the same shell without disrupting existing workflows.

---

## Requirements

- **Python 3.8+** (stdlib only for controllers — no pip installs)
- **Rhino 8** (for layout-jig watcher; controllers run independently)
- **Windows** (Rhino requirement; controllers work cross-platform)
- **Claude Code + MCP** (`pip install mcp` — the only pip dependency, for the MCP server only)
- **Anthropic API key** (for image-describer and AI assistant layer)
- **PIAF machine + laser printer with carbon-based toner** (for tactile paper output)
- **Bambu Lab P1S 3D printer** (for tactile model output)
- **META Ray-Ban glasses** (optional — for spoken/vision features)

## Repository Structure

```
radical-accessibility/
  CLAUDE.md .............. Project instructions for AI assistants
  controller_cli.py ...... Terminal CLI, v2.3 (Python 3, stdlib only)
  mcp_server.py .......... MCP server v3.1 (46 tools, 5 resources, 4 prompts)
  auditor.py ............. Spatial validation, ADA checks, descriptions
  skill_manager.py ....... Skill CRUD and replay
  rhino_client.py ........ TCP client to Rhino watcher
  requirements.txt ....... Python dependencies (mcp only)
  skills/ ................ Bundled reusable command sequences
  rhino/ ................. Rhino watcher scripts (IronPython 2.7)
    rhino_watcher.py ..... File watcher + geometry renderer
    tactile_print.py ..... STL mesh generation + Bambu printing
    state.json ........... Canonical Model Artifact (created on first run)
  image-describer/ ....... Image description CLI (Claude vision API)
  tests/
    run_tests.py ......... End-to-end test suite (115 tests)
  docs/
    HOW_THE_MCP_WORKS.md . MCP architecture deep dive
    MCP_V3_MANUAL.md ..... Full MCP tool reference
    TEST_MANUAL.md ....... Step-by-step test walkthrough
    MCP_GUIDE.md ......... Original v2.0 MCP guide
  MANUAL.md .............. Full user documentation
  README.md
```

## License

MIT
