# Radical Accessibility Project

Architecture assumes you can see. Every mainstream design tool — CAD viewports, drawing sheets, pin-up critiques, even the vocabulary of studio culture — treats vision as a prerequisite for participation. If you're blind, or if you navigate the world through touch, sound, or speech rather than sight, you don't get a lesser version of architectural education. You get locked out entirely. The discipline's deepest bias isn't stylistic — it's perceptual.

The Radical Accessibility Project inverts the premise. Instead of retrofitting visual tools with accommodations, we build from scratch for non-visual interaction as the primary design case. A blind student designs a floor plan by typing commands in a terminal and hearing confirmations read back by a screen reader. A student with limited hand mobility speaks commands instead of dragging a mouse across a viewport. A deafblind student reads model descriptions on a refreshable braille display. A student with a traumatic brain injury or chronic fatigue works in short sessions against a deterministic state file that never loses progress and never demands sustained visual attention. The design itself lives in plain text that any input system — keyboard, voice, switch, sip-and-puff, braille keyboard — can write to, and any output system — speech, braille, tactile print, 3D model, haptic feedback — can read from.

What surprised us is that designing for blindness doesn't just make tools accessible — it makes them better for everyone. Semantic clarity, keyboard and voice operability, auditable state, deterministic output: these aren't accessibility features. They're engineering virtues that visual tools abandoned in favor of graphical convenience. A sighted architect benefits from a command that says exactly what changed and why. A studio instructor benefits from a design state they can diff and review like code. The constraints of non-visual design forced us to build what the discipline should have had all along.

Because the system separates input, logic, and output into independent layers, it extends naturally to disabilities beyond vision loss. Any condition that makes a mouse, a screen, or sustained visual focus unreliable becomes addressable by swapping the input or output layer — not rewriting the design tools. A voice interface serves someone with motor impairment as directly as it serves a blind user. A deterministic text-based state file serves someone with cognitive fatigue as directly as it serves someone using a braille display. The architecture of accessibility-first design turns out to be the architecture of universal design: build for the hardest case and the easier cases follow.

Based at the UIUC School of Architecture, the project is co-designed with Daniel Bein, a blind architecture student who is the primary user of everything we build. His daily workflow — designing, reviewing, fabricating, presenting — is the test case for every tool. Led by John Clark and Hugh Swiatek with student researchers Ethan Anderson, Isaac Tu, and Laura Heuser.

---

## The System

One platform with a shared command shell, undo stack, state management, and screen-reader-native output protocol. Tools plug into this shell. Each tool adds commands and capabilities without touching the others. The system is designed to grow — adding a new tool means writing a new module, not rebuilding the platform. All tools share a common pattern: typed or spoken input, text confirmation output, and a JSON state file as the canonical record of the design. Every tool follows one rule: if it can't be heard, felt, or read by a screen reader, it doesn't ship.

Three levels of organization:

- **Tool** — a major capability module (Layout Jig, Image Describer, Tactile Printer).
- **Command** — an individual action within a tool (`set bay A rotation 30`, `wall A on`).
- **Skill** — a saved sequence of commands, replayable with parameters (`enclose-bay-with-door`).

```
Terminal (controller/controller_cli.py)    Claude Code (mcp/mcp_server.py)
        |                                          |
        | writes                                   | calls controller + direct JSON
        v                                          v
              state.json  (canonical model artifact)
                      |
                      | watches (file mtime)
                      v
              Rhino 8 (tools/rhino/rhino_watcher.py)
                      |
                      v
              2D plan drawing | PIAF swell paper | 3D tactile model
```

---

## Tools

### Layout Jig — Architectural Modeler

The primary design tool. Commands like `set bay A rotation 30`, `wall A on`, `corridor A width 8` express design intent through text. A separate Rhino watcher reads the state file and rebuilds geometry. Supports rectangular and radial grids, walls with doors/windows/portals, corridors, rooms, hatches, braille legends, section cuts, and snapshots.

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

### Tactile Graphics — PIAF Swell Paper Pipeline

Converts designs into physical raised-line graphics readable by touch. The output is laser printed on PIAF microcapsule paper with carbon-based toner, then fed through a PIAF heater. Carbon absorbs heat, microcapsules in the paper swell, and black lines rise off the page as tactile ridges. Daniel reads his own floor plans this way.

Two pipelines produce PIAF output:

**Automated (swell-print tool, no Rhino needed).** The `swell-print` tool reads state.json directly and renders a complete PIAF-ready plan drawing. It draws columns, walls with aperture gaps, corridors (dashed), door/window/portal symbols, room hatches, English and braille labels, legend, and section cuts. Output is 300 DPI black-and-white, letter or tabloid paper, with density management to keep black pixels in the 25-40% range where PIAF gives the best tactile clarity. The same tool converts any image (photograph, sketch, CAD export, precedent drawing) to PIAF-ready output using ten presets tuned for different image types.

```
>> render
OK: Rendered state_tactile.pdf (Letter, 300 DPI, density 28.3%)

>> convert farnsworth.jpg --preset floor_plan
OK: Converted farnsworth.jpg -> farnsworth_tactile.png (density 31.2%)

>> presets
OK: 10 presets available:
  1. diagram — Conceptual and bubble diagrams (threshold 135, max density 35%)
  2. floor_plan — Architectural floor plans with walls and dimensions (threshold 140, max density 40%)
  3. photograph — Photos of buildings, models, or sites (threshold 120, max density 30%)
  ...
```

**Manual (Rhino export).** For drawings that include geometry beyond the state.json model — annotations, custom line work, overlaid analysis — export a high-contrast image from Rhino and run it through the `convert` command with the appropriate preset. The image converter applies contrast enhancement (S-curve, CLAHE, or auto-contrast depending on preset), thresholds to pure black and white, scales to fit the paper, and checks density before saving.

Both pipelines produce output that laser prints on PIAF microcapsule paper and heats to a raised tactile graphic. Braille labels use the stdlib-only `controller/braille.py` module (Grade 1 built-in, Grade 2 via liblouis). Density above 40% triggers a warning; above 45% the tool rejects the output because excessive swelling destroys tactile detail.

### 3D Print — Tactile Scale Models

Generates watertight triangle meshes from the parametric model (pure Python, no Rhino dependency), validates solidity, and exports binary STL scaled for a Bambu Lab P1S printer. Daniel holds the printed model during design review — walls, corridors, openings physically present at 1:200 scale.

### AI Integration — MCP Server v3.3

An [MCP server](docs/MCP_GUIDE.md) (53 MCP functions, 5 resources, 4 prompts) connects Claude Code to every tool through the Model Context Protocol. Claude makes design changes through natural language, audits the model for ADA compliance, saves and replays skills, queries Rhino geometry, reads or writes individual state fields directly, generates editable IronPython scripts for learning, and renders tactile graphics.

The system supports three interaction modes:
1. **Mode 1: Claude Code + MCP** — natural language, AI translates to commands
2. **Mode 2: Interactive CLI** — typed commands, direct control
3. **Mode 3: Rhino Python** — editable scripts the user writes and runs in Rhino

Beyond conversational commands, the AI generates annotated RhinoPython scripts that the user can open, study, modify, and run independently. Teaching comments explain each code pattern. Over time, Daniel builds fluency in scripting his own geometry. The AI is a bridge to self-sufficiency, not a permanent dependency. See [DESIGN_SESSION.md](DESIGN_SESSION.md) for a complete walkthrough of all three modes.

```
User (natural language)
        |
        | "make the corridor wider"
        v
    Claude Code + MCP Server (53 functions)
        |
        | validated: CLI command dispatch
        | direct: JSON field read/write
        | scripts: generate editable .py files
        v
    state.json mutation + confirmation readback
```

The MCP server has eight functional layers:

- **Core pipeline** (21) — semantic wrappers around CLI commands
- **Auditor** (5) — spatial validation, ADA checks, bay descriptions, circulation analysis, distance measurement
- **Skill manager** (4) — save, list, show, and replay skills
- **Rhino client** (4) — TCP queries to the Rhino watcher + auto-launch (offline-safe)
- **Controller extension** (2) — add new command handlers at runtime
- **State introspection** (7) — read/write individual JSON fields, create/delete/clone bays, list commands, show handler source
- **State comparison** (3) — diff against snapshots, validate JSON structure
- **Script generation** (3) — create, list, and view editable IronPython 2.7 scripts for learning
- **Swell-print** (4) — render state.json and convert images to PIAF tactile graphics

See [docs/MCP_GUIDE.md](docs/MCP_GUIDE.md) for architecture, setup, and the full tool reference. See [DESIGN_SESSION.md](DESIGN_SESSION.md) for a complete design session walkthrough.

---

## End-to-End Workflows

These workflows show complete sequences from intent to physical output, using real commands. Each shows both the interactive CLI (Mode 2) and Claude Code (Mode 1) approaches where applicable.

### Workflow 1: Design a School Building from Scratch

Daniel needs to design a small school building with classrooms, a corridor, and an accessible entrance. Starting from an empty state, he builds the design, audits it for ADA compliance, and produces a tactile print and 3D model.

**Step 1 — Create the structural grid.**

CLI:
```
>> set site width 200
OK: Site width = 200.0 ft.

>> set site height 150
OK: Site height = 150.0 ft.

>> set bay A origin 20 10
OK: Bay A origin = (20.0, 10.0).

>> set bay A bays 6 3
OK: Bay A grid = 6 x 3.

>> set bay A spacing 24 24
OK: Bay A spacing = (24.0, 24.0).
```

Claude Code:
```
You: Create a 6 by 3 bay grid for a school building, 24-foot spacing, origin at 20, 10.
     Set the site to 200 by 150.

Claude: I'll set up the site and bay grid.
OK: Site width = 200.0 ft.
OK: Site height = 150.0 ft.
OK: Bay A origin = (20.0, 10.0).
OK: Bay A grid = 6 x 3.
OK: Bay A spacing = (24.0, 24.0).
```

**Step 2 — Add walls and a corridor.**

```
>> wall A on
OK: Bay A walls ON, 6-inch thick.

>> corridor A on
OK: Bay A corridor ON.

>> corridor A axis x
OK: Bay A corridor axis = x.

>> corridor A position 1
OK: Bay A corridor position = gridline 1.

>> corridor A width 8
OK: Bay A corridor width = 8.0 ft.

>> corridor A loading double
OK: Bay A corridor loading = double.
```

**Step 3 — Add doors for accessible entry.**

```
>> aperture A d1 door x 0 2 3 7
OK: Added door d1 to bay A. Axis x, gridline 0, corner 2.0, width 3.0, height 7.0.

>> aperture A d2 door x 3 2 3 7
OK: Added door d2 to bay A. Axis x, gridline 3, corner 2.0, width 3.0, height 7.0.
```

**Step 4 — Name rooms and assign hatches.**

```
>> cell A 0 0 name Classroom_1
OK: Bay A cell (0,0) name = Classroom_1.

>> cell A 0 0 hatch diagonal
OK: Bay A cell (0,0) hatch = diagonal.

>> cell A 1 0 name Classroom_2
OK: Bay A cell (1,0) name = Classroom_2.

>> cell A 1 0 hatch crosshatch
OK: Bay A cell (1,0) hatch = crosshatch.

>> auto_corridor A
OK: 6 cells named "Corridor" in bay A.
```

**Step 5 — Audit for ADA compliance.**

CLI:
```
>> audit
OK: 2 issues found.
  1. WARNING: Door d1 width 3.0 ft meets ADA minimum (3.0 ft). Consider 3.5 ft for comfort.
  2. OK: Corridor width 8.0 ft exceeds ADA minimum (5.0 ft).
```

Claude Code:
```
You: Check my design for ADA compliance.

Claude: Running the full audit.
OK: 2 issues found.
  1. WARNING: Door d1 width 3.0 ft meets ADA minimum (3.0 ft). Consider 3.5 ft for comfort.
  2. OK: Corridor width 8.0 ft exceeds ADA minimum (5.0 ft).
I recommend widening doors d1 and d2 to 3.5 feet. Want me to make that change?
```

**Step 6 — Produce tactile output.**

Render a PIAF swell paper print:
```
>> render
OK: Rendered state_tactile.pdf (Letter, 300 DPI, density 28.3%)
```

Print on the laser printer with carbon-based toner, then feed through the PIAF heater. The raised lines are ready for Daniel to read by touch.

Generate a 3D tactile model:
```
>> tactile3d export school_model.stl
OK: Exported school_model.stl (4,218 triangles, 1:200 scale).
```

Send to the Bambu Lab P1S. Daniel holds the printed model during design review.

### Workflow 2: Study a Precedent Building

Daniel wants to study the Farnsworth House by Mies van der Rohe. Someone gives him a floor plan image. He needs to understand the spatial organization through touch, then recreate it in the Layout Jig.

**Step 1 — Describe the image.**

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

Daniel now understands the building's organization through the text description: a rectangular glass pavilion with eight steel columns, a central service core, and open living spaces.

**Step 2 — Convert the image to a tactile print.**

```
>> convert farnsworth_plan.jpg --preset floor_plan --paper tabloid
OK: Converted farnsworth_plan.jpg -> farnsworth_plan_tactile.png (density 31.2%)
```

Print on PIAF paper at tabloid size. Daniel traces the walls, columns, and core with his fingers. He feels the spatial relationships the text described — the separation between the service core and the perimeter, the column rhythm along the long edges.

**Step 3 — Recreate the building in the Layout Jig.**

Based on what he learned from the description and tactile print, Daniel builds a simplified version:

```
You: Create a model of the Farnsworth House. It's a single rectangle, roughly 77 by 29 feet,
     with 8 steel columns in 2 rows of 4. There's a central service core that contains the
     kitchen and bathrooms. The rest is open plan.

Claude: I'll set up the Farnsworth House model.
OK: Site width = 120.0 ft.
OK: Site height = 80.0 ft.
OK: Bay A origin = (20.0, 25.0).
OK: Bay A grid = 4 x 2.
OK: Bay A spacing_x set to [19.25, 19.25, 19.25].
OK: Bay A spacing_y set to [28.75].
OK: Bay A walls ON, 6-inch thick.
OK: Bay A cell (1,0) name = Service_Core.
OK: Bay A cell (1,0) hatch = crosshatch.
OK: Bay A cell (0,0) name = Living.
OK: Bay A cell (2,0) name = Living.
OK: Bay A cell (3,0) name = Sleeping.

You: Render that as a tactile print so I can compare it to the original.

Claude: Rendering now.
OK: Rendered state_tactile.pdf (Letter, 300 DPI, density 22.1%)
```

Daniel prints both tactile sheets — the original and his recreation — and compares them side by side on the table. He refines his model based on what his fingers tell him.

### Workflow 3: Prepare for a Design Review

Daniel has a building design and needs to prepare materials for a studio review: an ADA-compliant plan, a tactile print, a 3D model, and a verbal presentation.

**Step 1 — Audit the design.**

```
You: Run a full audit of my design. Check everything — ADA, spatial issues, missing labels.

Claude: Running the full model audit.
OK: 4 issues found.
  1. ERROR: Door d3 width 2.5 ft is below ADA minimum (3.0 ft).
  2. WARNING: Bay B has no braille label.
  3. OK: All corridors meet ADA minimum width.
  4. WARNING: Room "Office" has no hatch pattern — it will be blank on tactile prints.

I'll fix the door width and add the missing braille label. Want me to also add a hatch
to the Office room?

You: Yes, fix all of them. Use dots for the office.

Claude: Making the changes.
OK: Door d3 width = 3.5 ft. Was 2.5 ft.
OK: Bay B braille set.
OK: Bay B cell (2,1) hatch = dots.
```

**Step 2 — Generate the tactile print.**

```
>> render --paper tabloid
OK: Rendered state_tactile.pdf (Tabloid, 300 DPI, density 33.1%)
```

**Step 3 — Generate the 3D tactile model.**

```
>> tactile3d export review_model.stl
OK: Exported review_model.stl (6,832 triangles, 1:200 scale).
```

Send to the Bambu P1S. Print overnight.

**Step 4 — Get a design critique.**

```
You: Give me a design critique of this building. Focus on circulation, spatial quality,
     and how the rooms relate to each other.

Claude: Looking at your model, here are observations about the design:

Circulation: The double-loaded corridor in Bay A efficiently serves rooms on both sides,
but the corridor dead-ends at the east wall. Consider adding a door or portal at gridline 6
to allow through-circulation...

Spatial quality: The classrooms are uniform 24x24 bays. This creates clear, predictable
spaces, but every room feels the same. You could vary the spacing_y on one bay to create
a taller classroom for art or music...

Room relationships: The office is isolated in Bay B with no direct corridor connection
to Bay A. A portal between the two bays at their shared boundary would improve wayfinding...
```

**Step 5 — Prepare a verbal presentation.**

```
>> describe

Site: 200 x 150 ft.
Bay A: 6 x 3 rectangular grid at (20, 10), 24 ft spacing. Walls on, 6-inch thick.
  Corridor: x-axis at gridline 1, 8 ft wide, double-loaded.
  Rooms: Classroom_1 (diagonal hatch), Classroom_2 (crosshatch), ...
  Doors: d1 (3.5 ft, x-axis, gridline 0), d2 (3.5 ft, x-axis, gridline 3).
Bay B: 3 x 2 rectangular grid at (170, 10), 20 ft spacing. Walls on.
  Rooms: Office (dots hatch), Storage (horizontal hatch).
```

Daniel uses this structured description as the basis for his verbal presentation. Every dimension, room name, and spatial relationship is in text he can rehearse with his screen reader.

### Workflow 4: Iterate on a Design with Claude

Daniel works conversationally with Claude, making changes, printing tactile sheets, feeling the results, and refining. This shows the design loop in practice.

```
You: I want to start a new school design. Give me a basic L-shaped plan with a
     corridor connecting two wings.

Claude: I'll create an L-shaped plan using two bays.
OK: Bay A origin = (10.0, 10.0). Grid = 4 x 2, spacing 24 x 24.
OK: Bay B origin = (10.0, 58.0). Grid = 2 x 4, spacing 24 x 24.
OK: Bay A corridor ON, x-axis, gridline 1, width 8.
OK: Bay B corridor ON, y-axis, gridline 1, width 8.
OK: Added portal p1 connecting Bay A and Bay B corridors.

You: Render that so I can feel it.

Claude: OK: Rendered state_tactile.pdf (Letter, 300 DPI, density 24.7%)
```

Daniel prints the PIAF sheet, heats it, and traces the L-shape with his fingers. He feels the corridor junction where the two wings meet.

```
You: The junction feels awkward. The corridors meet at a right angle with no
     transition space. Can you add a wider area at the corner?

Claude: I'll widen the corridor at the junction. I'll increase Bay A's last
column spacing to 30 feet and add a portal between the bays at that wider point.
OK: Bay A spacing_x set to [24.0, 24.0, 30.0].
OK: Moved portal p1 to wider junction.

You: Render again.

Claude: OK: Rendered state_tactile.pdf (Letter, 300 DPI, density 25.1%)
```

Daniel prints and feels the updated plan. The wider junction now has a clear transition space.

```
You: Better. Now name all the rooms — classrooms in Wing A, labs in Wing B.
     Then give me a snapshot so I don't lose this version.

Claude: Naming rooms and saving.
OK: Bay A cell (0,0) name = Classroom_1. (+ 5 more rooms named)
OK: Bay B cell (0,0) name = Lab_1. (+ 5 more rooms named)
OK: Snapshot saved: "l-shaped-v1".

You: Run the audit.

Claude: OK: All clear. No ADA issues found. 2 suggestions:
  1. Consider adding braille labels to both bays for tactile print legibility.
  2. Lab rooms have no hatches — they will be blank on PIAF prints.

You: Add hatches and braille to everything. Then render at tabloid size for the
     final review print.

Claude: Done.
OK: Hatches assigned (classrooms: diagonal, labs: crosshatch, corridor: none).
OK: Braille labels added to Bay A and Bay B.
OK: Rendered state_tactile.pdf (Tabloid, 300 DPI, density 31.8%)
```

The cycle repeats: command, render, print, feel, refine. Each iteration takes minutes. The state file records every change. Snapshots mark milestones. The undo stack catches mistakes. Daniel stays in control of the design at every step.

---

## Use Cases

The system's separation of input, logic, and output means different disabilities are addressed by swapping the interface layer, not rewriting the design tools.

**Blind architecture student (primary case).** Daniel's daily workflow. Commands typed or spoken in a terminal. Confirmations read by JAWS or NVDA. Design state explored through `describe`, audited with `audit`, and physicalized through PIAF swell prints and 3D-printed tactile models. Braille labels on all outputs. The braille display shows command output directly. Claude provides natural-language design conversation and critique. Every piece of information that a sighted student would get from looking at a screen, Daniel gets from text, touch, or speech.

**Low-vision designer.** The same CLI works without modification — all output is text, scalable by the terminal's font settings. PIAF prints at tabloid size with heavy line weights (adjust `style heavy 2.0` for thicker columns) provide higher contrast and larger tactile features. The `--paper tabloid` flag on render produces larger prints. Rhino's viewport, when used, supports system-level magnification and high-contrast display modes.

**Motor impairment (voice input).** Speech recognition (Dragon, Windows Voice Access, macOS Voice Control) dispatches spoken commands to the same CLI that accepts typed input. "Set bay A rotation thirty" works identically whether typed or spoken. No mouse interaction is required for any core modeling flow. Skills (saved command sequences) reduce the number of commands needed for common operations — one spoken command replays a multi-step sequence.

**Cognitive fatigue and traumatic brain injury.** The deterministic state file means work is never lost. Every command is atomic — it either succeeds with a confirmation or fails with an error. Sessions can be as short as one command. The undo stack reverses mistakes. Snapshots save progress at named checkpoints. There is no ambient state to track, no unsaved changes to worry about, no modal dialogs to navigate. The system waits. The user works at their own pace.

**Deafblind (braille display + braille labels).** All CLI output is plain text, compatible with refreshable braille displays. The `controller/braille.py` module translates all labels to Unicode Braille (Grade 1 built-in, Grade 2 via liblouis). PIAF tactile prints include braille room labels and legends. The `describe` command produces structured text that reads linearly on a braille display — no spatial layout to interpret, no visual formatting to decode.

**Sighted instructor reviewing a blind student's work.** The same state.json file that Daniel edits through the CLI renders as full 2D drawings and 3D geometry in Rhino when the watcher runs. An instructor opens the Rhino viewport and sees the same design Daniel built by touch and text. They can run `describe` to see exactly what Daniel sees. They can run `audit` to check what Daniel checked. The design review happens on equal footing — both participants work from the same canonical model, through their preferred interface.

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
- **New tools** — The system is built to extend. Future tools could include structural analysis, environmental simulation, collaborative multi-user design, accessibility auditing of buildings themselves, or direct fabrication machine control — each plugging into the same shell without disrupting existing workflows.

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
  CLAUDE.md ................. Project instructions for AI assistants
  STARTUP.md ................ Startup instructions
  DESIGN_SESSION.md ......... Full design session walkthrough (all 3 modes)
  README.md ................. This file (detailed overview)
  controller/ ............... Core platform (CLI + supporting modules)
    controller_cli.py ....... Terminal CLI v2.3 (Python 3, stdlib only)
    auditor.py .............. Spatial validation, ADA checks
    braille.py .............. Grade 1/2 braille translation (stdlib only)
    skill_manager.py ........ Skill CRUD and replay
    skills/ ................. Bundled reusable command sequences
    scripts/ ................ Generated IronPython scripts (Mode 3)
    state.json .............. Canonical Model Artifact (created on first run)
  mcp/ ...................... AI integration layer
    mcp_server.py ........... MCP server v3.3 (53 functions)
    requirements.txt ........ Python dependencies (mcp only)
  tools/
    rhino/ .................. Rhino integration
      rhino_watcher.py ...... File watcher + geometry renderer (IronPython 2.7)
      tactile_print.py ...... STL mesh generation + Bambu printing
      rhino_client.py ....... TCP client for querying Rhino
    image-describer/ ........ Image description (Claude vision API)
    swell-print/ ............ PIAF tactile graphics pipeline
      swell_print.py ........ CLI entry point (REPL + single-shot)
      state_renderer.py ..... Render state.json to B&W image (no Rhino)
      image_converter.py .... Convert any image to PIAF-ready B&W
      pdf_generator.py ...... Wrap B&W images in PIAF-ready PDF
      requirements.txt ...... Python dependencies (Pillow, reportlab)
  tests/
    run_tests.py ............ End-to-end test suite (149 tests)
  docs/
    MANUAL.md ............... Full manual (all commands and tools)
    MCP_GUIDE.md ............ AI layer (MCP architecture, setup, tool reference)
    TEST_MANUAL.md .......... Test walkthrough
    archive/ ................ Older reference docs
```

## License

MIT
