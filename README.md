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

---

## Skills

### [Layout Jig](layout-jig/) — Architectural Modeler

The primary design skill. Commands like `set bay A rotation 30`, `wall A on`, `corridor A width 8` express design intent through text. A separate Rhino watcher reads the state file and rebuilds geometry. Supports rectangular and radial grids, walls with doors/windows/portals, corridors, rooms, hatches, braille legends, section cuts, and snapshots.

```
>> set bay A origin 20 10
OK: Bay A origin = (20.0, 10.0). Was (18.0, 8.0).

>> wall A on
OK: Bay A walls ON, 6-inch thick.

>> describe
(full model description, screen-reader-friendly)
```

### [Arch-Alt-Text](arch-alt-text/) — Image Description

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

### [Image to PIAF](tactile/) — Tactile Image Conversion

Converts any architectural image — photographs, CAD screenshots, scanned plans, textbook figures, precedent studies — into PIAF-ready output for swell paper printing. Ten presets tuned for different image types (floor plans, elevations, photographs, sketches, sections, site plans, renderings, diagrams, historic photos, hand drawings). Density management ensures the swell paper doesn't overload. Braille labels are rendered directly as dot patterns. Large images tile across multiple pages with registration marks for assembly.

```
>> python tactile/image_to_piaf.py plan.jpg --preset floor_plan --labels "Kitchen;Living Room"
OK: Converted plan.jpg using preset 'floor_plan'.
  Output: plan_piaf.png
  Density: 28%
  Labels: 2 placed.

>> python tactile/image_to_piaf.py photo.jpg --analyze
OK: Analysis of photo.jpg
  Size: 4032 x 3024 px (12.2 MP)
  Suggested preset: photograph
  Density at thresholds:
    Threshold 80: 32%
    Threshold 100: 25%
```

Also runs as an interactive REPL (`python tactile/image_to_piaf.py`) and as an [MCP server](tactile/mcp_server.py) (6 tools, 3 resources, 2 prompts) for AI-driven conversion workflows.

Pipeline: image → contrast enhancement → grayscale → threshold → density management → braille labels → PIAF-ready output at 300 DPI. Printed on PIAF microcapsule paper with carbon-based toner, then heated — the carbon absorbs heat, the microcapsules swell, black lines rise off the page. Daniel reads his own floor plans through this pipeline.

### 3D Print — Tactile Scale Models

Generates watertight triangle meshes from the parametric model (pure Python, no Rhino dependency), validates solidity, and exports binary STL scaled for a Bambu Lab P1S printer. Daniel holds the printed model during design review — walls, corridors, openings physically present at 1:200 scale.

### AI Code Generation — Path to Self-Sufficiency

An AI layer that goes beyond conversational design commands. The [MCP server](layout-jig/MCP_GUIDE.md) (21 semantic tools) lets Claude make design changes through natural language, but the deeper goal is code generation: the AI writes RhinoPython, Grasshopper scripts, or other code-based CAD operations on the user's behalf, then explains what it produced so the user learns the underlying language. Over time, Daniel builds fluency in scripting his own geometry. The AI is a bridge to self-sufficiency, not a permanent dependency. Every generated script is readable, commented, and available to modify and reuse.

```
User (natural language)
        |
        | "make the corridor wider"
        v
    LLM (Claude) interprets intent
        |
        | calls semantic MCP tool (e.g. set_corridor)
        v
    CLI command dispatch / state mutation
        |
        | update state.json
        v
    Confirmation + description readback
```

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
- **Pillow** (`pip install Pillow`) for Image-to-PIAF tactile conversion
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
    mcp_server.py ........ MCP server v2.0 (21 tools, 3 resources, 2 prompts)
    MCP_GUIDE.md ......... Full MCP server documentation
    state.json ........... Canonical model artifact
    MANUAL.docx .......... Full user documentation
  tactile/
    image_to_piaf.py ..... Image-to-PIAF tactile conversion (Python 3, Pillow)
    mcp_server.py ........ MCP server v1.0 (6 tools, 3 resources, 2 prompts)
  CLAUDE.md .............. Project instructions for AI coding assistants
  README.md
```

## License

MIT
