# Radical Accessibility Project

## Mission Statement

Architecture assumes you can see. Every mainstream design tool — CAD viewports, drawing sheets, pin-up critiques, even the vocabulary of studio culture — treats vision as a prerequisite for participation. If you're blind, or if you navigate the world through touch, sound, or speech rather than sight, you don't get a lesser version of architectural education. You get locked out entirely. The discipline's deepest bias isn't stylistic — it's perceptual.

The Radical Accessibility Project inverts the premise. Instead of retrofitting visual tools with accommodations, we build from scratch for non-visual interaction as the primary design case. A blind student designs a floor plan by typing commands in a terminal and hearing confirmations read back by a screen reader. A student with limited hand mobility speaks commands instead of dragging a mouse across a viewport. A deafblind student reads model descriptions on a refreshable braille display. A student with a traumatic brain injury or chronic fatigue works in short sessions against a deterministic state file that never loses progress and never demands sustained visual attention. The design itself lives in plain text that any input system — keyboard, voice, switch, sip-and-puff, braille keyboard — can write to, and any output system — speech, braille, tactile print, 3D model, haptic feedback — can read from.

What surprised us is that designing for blindness doesn't just make tools accessible — it makes them better for everyone. Semantic clarity, keyboard and voice operability, auditable state, deterministic output: these aren't accessibility features. They're engineering virtues that visual tools abandoned in favor of graphical convenience. A sighted architect benefits from a command that says exactly what changed and why. A studio instructor benefits from a design state they can diff and review like code. The constraints of non-visual design forced us to build what the discipline should have had all along.

Because the system separates input, logic, and output into independent layers, it extends naturally to disabilities beyond vision loss. Any condition that makes a mouse, a screen, or sustained visual focus unreliable becomes addressable by swapping the input or output layer — not rewriting the design tools. A voice interface serves someone with motor impairment as directly as it serves a blind user. A deterministic text-based state file serves someone with cognitive fatigue as directly as it serves someone using a braille display. The architecture of accessibility-first design turns out to be the architecture of universal design: build for the hardest case and the easier cases follow.

The project produces a single extensible system — a unified platform with pluggable skills — that lets a blind student design a building from an empty site to a printed tactile model entirely through text and speech. One skill generates floor plans from typed commands. Another describes architectural images in structured text. Another converts digital drawings into raised-line tactile prints readable by touch. Another 3D-prints scale models for hands-on design review. Another lets an AI write CAD scripts on the student's behalf while teaching them the underlying language. Each skill is a module within one platform, and new skills can be added without rebuilding what exists. Every skill follows one rule: if it can't be heard, felt, or read by a screen reader, it doesn't ship.

Based at the UIUC School of Architecture, the project is co-designed with Daniel Bein, a blind architecture student who is the primary user of everything we build. His daily workflow — designing, reviewing, fabricating, presenting — is the test case for every tool. Led by John Clark and Hugh Swiatek with student researchers Ethan Anderson, Isaac Tu, and Laura Heuser.

---

## Project Layout

### The System

One platform with a shared command shell, undo stack, state management, and screen-reader-native output protocol. Skills plug into this shell. Each skill adds commands and capabilities without touching the others. The system is designed to grow — adding a new skill means writing a new module, not rebuilding the platform. All skills share a common pattern: typed or spoken input, text confirmation output, and a JSON state file as the canonical record of the design.

### Skills (Current)

**Layout Jig — Architectural Modeler.** The primary design skill. Commands like `set bay A rotation 30`, `wall A on`, `corridor A width 8` express design intent through text. A separate Rhino watcher reads the state file and rebuilds geometry. Supports rectangular and radial grids, walls with doors/windows/portals, corridors, rooms, hatches, braille legends, section cuts, and snapshots.

**Arch-Alt-Text — Image Description.** Takes an architectural image — a plan, photo, section, diagram — and produces a structured text description at three scales: Macro (what the image is), Meso (how it's organized), Micro (specific elements and measurements). Replaces "looking at a drawing" with text a screen reader can parse.

**Image to PIAF — Tactile Drawing Fabrication.** Converts digital drawings into physical raised-line graphics readable by touch. High-contrast black-and-white conversion with four line weights (heavy for columns, medium for walls, light for grid, fine for hatches), halftone dithering for tonal areas, Grade 2 contracted braille labels, and page tiling with registration marks. Laser printed on PIAF microcapsule paper with carbon-based toner, then heated — the carbon absorbs heat, the microcapsules swell, and black lines rise off the page. Daniel reads his own floor plans through this pipeline.

**3D Print — Tactile Scale Models.** Generates watertight triangle meshes from the parametric model (pure Python, no Rhino dependency), validates solidity, and exports binary STL scaled for a Bambu Lab P1S printer. Daniel holds the printed model during design review — walls, corridors, openings physically present at 1:200 scale.

**AI Code Generation — Path to Self-Sufficiency.** An AI layer that goes beyond conversational design commands. The MCP server (21 semantic tools) lets Claude make design changes through natural language, but the deeper goal is code generation: the AI writes RhinoPython, Grasshopper scripts, or other code-based CAD operations on the user's behalf, then explains what it produced so the user learns the underlying language. Over time, Daniel builds fluency in scripting his own geometry. The AI is a bridge to self-sufficiency, not a permanent dependency. Every generated script is readable, commented, and available to modify and reuse.

### Input Devices

**Keyboard + Terminal.** The primary interface. All commands are typed. All output is text. Works with JAWS, NVDA, and braille displays.

**Voice.** Speech recognition dispatches spoken commands to the same CLI. Text-to-speech reads back confirmations and descriptions. Hands-free operation for design sessions and reviews.

**Pegboard + Overhead Camera.** A tactile pegboard where Daniel constructs spatial layouts by hand using wire and pegs on a gridded surface. An overhead camera captures the physical construction, OpenCV detects wire positions and peg locations, and the arrangement digitizes into coordinates that feed back into the model. Design by touch, capture by camera, rebuild in CAD. Audio feedback confirms spatial relationships as pieces are placed.

### Future Directions

- **Audio simulation of designs** — Spatial audio rendering of architectural models using binaural sound. Walk through a design and hear the space: room volume mapped to reverb, wall proximity to tonal shift, ceiling height to pitch, material hardness to timbre. A blind designer could evaluate the acoustic character of a corridor versus an atrium by listening, building spatial intuition without sight.
- **Vibrotactile interfaces and models** — Physical models and surfaces embedded with vibration motors that encode design information through haptic patterns. A scale model where different vibration frequencies indicate material type, structural load, or thermal zones. A flat surface where vibrotactile feedback traces wall edges and opening locations under the user's fingertips as they explore.
- **Haptic gloves** — Direct tactile feedback on the hands during digital model navigation. Feel wall edges, surface textures, and spatial boundaries without a physical print. Navigate a 3D model by moving your hands through space and feeling the geometry push back.
- **High-resolution interactive tactile display** — A pin-array or similar surface that renders the current design state as a dynamic tactile image, updated live as the model changes. Replaces static PIAF prints with a reusable, real-time tactile screen that redraws when the model is edited.
- **Live AI descriptions with META Ray-Ban glasses** — Continuous scene narration during studio, pin-ups, site visits, and design reviews. Architectural description in real time — not just what's there, but Socratic design questions ("The southern facade is mostly solid — how are you thinking about daylight?").
- **New skills** — The system is built to extend. Future skills could include structural analysis, environmental simulation, collaborative multi-user design, accessibility auditing of buildings themselves, or direct fabrication machine control — each plugging into the same shell without disrupting existing workflows.
