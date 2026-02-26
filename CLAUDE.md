# CLAUDE.md — Radical Accessibility Project

## Project Overview

The Radical Accessibility Project develops tools and workflows that make architectural education fully accessible to blind and low-vision students. Led by John (architecture professor, UIUC School of Architecture), the project treats non-visual interaction as the *primary* design case rather than an accommodation. The core collaborator is Daniel, a blind graduate architecture student.

The thesis: by designing for blindness first, we create tools that are not only accessible but often superior to their visual-centric counterparts. This is disciplinarily transformative, not assistive.

## Key People

- **John Clark** — PI, architecture professor at UIUC School of Architecture. Expertise in computational design, architectural theory, and accessibility technology. Teaches "Paradise on the Prairie" graduate studio.
- **Hugh Swiatek** — Co-PI, teaching assistant professor at UIUC School of Architecture. Co-leads the Radical Accessibility Project with John.
- **Daniel** — Blind sophomore architecture student. Primary user and co-designer of all tools. Uses JAWS/NVDA screen readers, braille display, and iPhone with VoiceOver.

---

## Core Principles (do not violate)

### Accessibility-First IO
- All CLI output must be screen-reader-friendly: short labeled lines, predictable ordering, no dense blocks, no wide tables, no ASCII art.
- Every command prints a single-line summary of what changed. Silence after a command means something broke.
- No visual dependencies. Never require the user to look at a screen, inspect a viewport, or click a GUI dialog. If information exists only visually, it's inaccessible and broken.
- Text is the universal interface. Commands are typed or spoken. Responses are printed or spoken. Everything passes through text.

### Controller / Viewer Separation
- The CLI controller is authoritative for model intent.
- Rhino is a **consumer** — it renders and exports, never the source of truth.
- Rhino must not require UI interaction for core modeling flows.

### Crash-Only Viewer
- Rhino may crash at any time. The model must remain consistent and recoverable from disk state alone.
- The user's work lives in the JSON file, not in Rhino's memory. If Rhino crashes, nothing is lost. Restart Rhino, run the watcher, everything rebuilds.

### Determinism and Auditability
- Same inputs → same `state.json` → same geometry (within tolerance).
- All mutations produce printed confirmation. Undo is accomplished via the CLI undo stack (and optionally Git history of `state.json`).

### Semantic Over Geometric
- Describe *what things are* ("bay A", "north corridor", "entry column"), not just coordinates. The JSON state is semantic; the watcher translates to geometry. Maintain this separation.
- Prefer IDs + names over spatial descriptions unless explicitly requested.

### Physical-Digital Round-Trip
- Tactile input (pegboard, swell paper, 3D prints) must digitize cleanly. Digital output must physicalize cleanly. The loop must be bidirectional and lossless at the semantic level.

---

## Screen Reader Rules

- Never use progress spinners, animated output, or streaming indicators.
- Keep responses under 20 lines when possible; offer "more" for longer output.
- When asking questions, always number options and restate the question clearly.
- Prefix every response with OK: or ERROR: for quick parsing.
- No tables, no multi-column layouts, no decorative separators (no box-drawing characters).
- After completing a command, print READY: so the screen reader detects the state change.
- Use NVDA with Console Toolkit add-on for best results; run in cmd.exe, not Windows Terminal.
- For Claude Code headless mode: use `claude -p "prompt" --output-format text` to avoid streaming.

---

## Current Working Architecture: CLI → JSON → Rhino Watcher

The proven, working pipeline uses a **file-watching pattern** with JSON as the interchange format. This is the backbone of the project and the pattern all new tools should follow unless there's a compelling reason not to.

### How It Works

```
Daniel types command in terminal
        ↓
Controller CLI (Python 3) validates input, updates in-memory state
        ↓
Atomic write to state JSON (write .tmp → fsync → os.replace)
        ↓
Rhino Watcher (IronPython 2.7 inside Rhino 8) checks file mtime on idle event
        ↓
Watcher reads JSON, reconciles geometry, rebuilds
        ↓
Rhino viewport updates
```

### The Three Files

Every tool built on this pattern consists of three files living in the same folder:

1. **Controller CLI** (e.g., `controller_cli_v2.py`) — Pure Python 3. No dependencies beyond stdlib. The blind user interacts here. Handles input validation, undo stack, help text, and all user-facing output. Has zero knowledge of Rhino.

2. **State JSON** (e.g., `state_v2.json`) — The **Canonical Model Artifact (CMA)**. Schema-versioned. Contains the complete design state — every parameter, every setting. Written only by the controller, read by the watcher. The single source of truth.

3. **Rhino Watcher** (e.g., `rhino_watcher_v2.py`) — IronPython 2.7 script run inside Rhino 8's EditPythonScript editor. Hooks `Rhino.RhinoApp.Idle`, checks file mtime each cycle, calls rebuild when changed. Uses `rhinoscriptsyntax` (rs) for geometry and RhinoCommon for events. Has zero knowledge of the CLI.

### Why This Architecture

- **Decoupled.** CLI and Rhino are completely independent. If Rhino crashes, the terminal keeps working.
- **Screen-reader-native.** The CLI is pure text in/out. Works perfectly with JAWS, NVDA, and braille displays.
- **Debuggable.** The JSON file is human-readable. Open it in any editor, inspect, hand-edit, diff.
- **No infrastructure.** No sockets, no shared memory, no servers, no network. Just a file on disk.
- **Atomic and safe.** Writes go to `.tmp` first, then `os.replace`. The watcher never reads a half-written file.
- **Auto-migrating.** When new fields are added, the CLI detects old state files and adds defaults on load. Existing designs never break.

### Current Tools Using This Pattern

**School Jig (2D Plan Generator)** — The most developed tool. Generates 2D architectural floor plans with structural bays, columns, corridors, voids, braille labels, and hatch patterns. Supports both rectangular and radial grids with irregular spacing. Commands like `set bay A rotation 30`, `corridor A width 8`, `swap A` (toggle grid type), `hatch A room crosshatch`. Four lineweight layers: heavy (columns), medium (corridors), light (grid), fine (hatches).

---

## State File Contract (Canonical Model Artifact)

`state.json` is the Canonical Model Artifact (CMA). Every controller — current CLI, future MCP agent, hypothetical GUI — must produce valid CMA output.

### Required Top-Level Fields
- `"schema"` — string identifying the tool and version (e.g., `"school_jig_2d_v2"`)
- `"meta"` — object with `created`, `last_saved`, `notes`

### Stable IDs
- All addressable objects (bays, corridors, voids, etc.) must have stable IDs.
- IDs must not depend on list ordering.
- Renaming or reordering must not change an object's ID.
- This is critical for future incremental rebuild and for MCP compatibility.

### Schema Versioning
- `schema` field is required and must change when the structure changes.
- Backward compatibility: viewers should ignore unknown fields; controllers should not drop fields they don't understand.
- Migration: the CLI auto-adds new fields with defaults on load. Old state files always work.

### JSON Formatting
- Human-readable: indent with 2 spaces on write.
- Descriptive keys: `"spacing_x"`, `"corridor_width"`, `"grid_type"`.
- Arrays for irregular spacing: `"spacing_x": [20.0, 20.0, 25.0]`.
- Nested objects for complex features: `"corridor": {"enabled": true, "axis": "x", ...}`.

---

## Owned Objects Safety Rule (Rhino Watcher)

The watcher must only delete or update geometry it created. It must never touch user-placed objects.

### Ownership Tagging
Every object created by the watcher should carry:
- **UserText** keys:
  - `JIG_OWNER = "RHINO_WATCHER"`
  - `JIG_ID = "<stable id from state.json>"`
  - `JIG_SCHEMA = "<schema_version>"`
- **Layer namespace**: all watcher geometry lives on `JIG::` prefixed layers (e.g., `JIG::Columns`, `JIG::Grid`, `JIG::Corridors`, `JIG::Hatch`)

### Deletion Rule
- Only delete objects where `JIG_OWNER == "RHINO_WATCHER"`.
- Never delete objects on layers outside the `JIG::` namespace.
- If Daniel or a sighted collaborator places geometry in the Rhino file, it must survive any watcher rebuild.

### Migration Note
The current School Jig watcher uses full layer clears (`rs.DeleteObjects` on layer contents). This works because the layers are watcher-owned. As tools mature, adopt per-object ownership tagging for finer-grained reconciliation. The layer-clear approach is acceptable for now but should not be extended to tools where users might add their own geometry to watcher layers.

---

## Export Contract

Keep model intent separate from export side effects.

### Principle
- The controller writes design intent to `state.json`.
- The watcher renders geometry and fulfills export requests.
- The watcher **never writes back to `state.json`**.

### Export Results
When the watcher produces exports (screenshots, STL, 3dm, PDF), it writes results to a separate file (e.g., `viewer_status.json` or files in an `exports/` folder) — never into the CMA.

This keeps the data flow one-directional: controller → state → watcher → exports.

---

## CLI Output Protocol

For screen reader predictability, CLI output should follow consistent patterns:

### Command Responses
```
OK: Bay A rotation set to 30°.
OK: Added corridor to Bay A, axis X, width 8.0.
ERROR: Bay "Z" does not exist. Available bays: A, B, C.
```

### Rules
- First token is `OK:` or `ERROR:` — screen readers can parse this immediately.
- Mutating commands include a `CHANGED:` line when useful for complex operations.
- `show` / `describe` commands use `LABEL: value` format, one item per line.
- No tables, no multi-column alignment, no color-only indicators.
- Optional `--json` flag for structured output, but never replace the human-readable default.

### Error Messages Always Include
- What failed
- Why (if known)
- How to fix
- Where to look (file path, command to retry)

---

## Future / Alternative Pipelines

The JSON file-watching pattern is proven. The project is open to other transport layers as tools mature. The key invariant: **every controller must produce valid CMA output, and every viewer must consume CMA without side-channel dependencies.**

### Transport vs. State (critical distinction)
- `state.json` is **storage + interchange** — the canonical artifact.
- MCP, HTTP, OSC, COM, sockets are **transport** — ways to move commands or updates.
- Do not conflate transport with state. If streaming updates are adopted, they must still serialize to stable CMA snapshots.

### MCP (Model Context Protocol)
- AI ↔ CAD bridge using stdio transport.
- Would enable conversational interaction: "describe the north elevation" → AI queries scene state and responds.
- Explored via `GH_mcp_server` pattern (CodeListener in Rhino, Claude Desktop or Cursor as client).
- **Status:** Prototyped, not yet in Daniel's daily workflow. MCP becomes compelling when we need real-time AI dialogue with the model rather than one-way command → rebuild.

### COM Automation (Windows)
- Direct programmatic control of Rhino via `win32com.client`.
- Faster round-trip than file watching, but Windows-only and more fragile.
- **Status:** Tested early on, set aside in favor of the more portable JSON approach.

### HTTP Server in Rhino
- REST API inside Rhino accepting commands.
- Would enable web-based or remote clients, collaborative scenarios.
- **Status:** Conceptual.

### Graph Description Language (GDL)
- Text-based parametric definition language as alternative to visual Grasshopper canvas.
- **Status:** Conceptual. Interesting where JSON state model becomes unwieldy for complex parametric definitions.

### Spoken Command Interface
- Windows SAPI text-to-speech for parameter readback and confirmations.
- Voice input via speech recognition → CLI command dispatch.
- META Ray-Ban glasses integration for real-time scene description ("Hey Meta, describe what's in front of me").
- Auditory feedback loops for spatial awareness during design review.
- **Status:** Early prototype. Voice input and TTS readback work independently; full pipeline integration in development.

### Sonification
- Binaural audio spatial walkthroughs of 3D models.
- Room volume → reverb, wall proximity → tonal shift, ceiling height → pitch.
- **Status:** Research direction, no prototype yet.

---

## Project Components (Beyond the CLI Pipeline)

### The Desk — BLV Workstation Concept
An all-in-one workstation designed for blind and low-vision architecture students. Consolidates the tools and hardware needed for accessible design work into a single integrated workspace.
- **Components:** Tactile gridded baseboard (pegboard surface), PIAF swell paper printer, Bambu Lab P1S 3D printer, large monitor (for sighted collaborators), laser printer with carbon-based toner
- **Future additions:** Overhead camera for digitizing physical constructions, smart tactile board with embedded sensors
- **Design principle:** Everything within arm's reach, every device addressable from the terminal

### Tactile Graphics Production Pipeline
- **PIAF swell paper workflow**: Image/drawing → grayscale/vector conversion → laser print on microcapsule paper using carbon-based black toner → feed through PIAF heater → carbon toner swells to create raised tactile surface. Only carbon-based black toner works; other toners and inks do not swell.
- **Image-to-PIAF converter**: Converts architectural drawings to PIAF-optimized format with high-contrast black-and-white output
- **Halftone tactile converter**: Translates images to tactile-legible halftone and dithering patterns for tonal areas
- **Line weight conventions**: Heavy (columns/structure), medium (corridors/walls), light (grid lines), fine (hatches/textures)
- **Automatic braille translator**: Integrates Grade 2 contracted braille labels into graphics workflows
- **Page tiling**: Registration marks aligned to Layout Jig grid for multi-sheet drawings
- **Tactile precedent library**: Canonical buildings (Mies, Kahn, Zumthor, etc.) as standardized PIAF tactile cards
- **3D print pipeline**: Vector geometry → Rhino/Grasshopper multipipe → watertight mesh validation (naked edges, self-intersections, hole-fill) → STL export → Bambu Lab P1S printing → tactile scale model for design review

### Physical Teaching Tools
- **Tactile pegboard system**: Pegboard with 0.065" rebar tie wire as lines. Overhead camera + OpenCV for wire position detection. Digitizes physical constructions into Rhino geometry. Audio feedback confirms spatial relationships.
- **Structural taxonomy kits**: 3D-printed template pieces for free-body diagrams and structural concepts
- **3D-printed jigs**: Physical guides for model-making that register to digital coordinate systems

### AI Vision + Description System
- **Ray-Ban Meta glasses pipeline**: "Hey Meta" voice-activated image descriptions of surroundings, classmates' work, pin-ups, physical models
- **AI critique partner**: Beyond description — Socratic design questions ("The southern facade appears mostly solid — how are you thinking about daylight?")
- **Image description archive**: Persistent, searchable database of all AI descriptions (Obsidian vault with metadata)
- **Custom training dataset**: Building an architectural description dataset for fine-tuning

---

## Tech Stack

### Languages & Runtimes
- **Python 3.x** — Controller CLIs, all external tools, pipelines, scripts
- **IronPython 2.7** — Rhino watcher scripts (inside Rhino 8 on .NET)

### Core Software
- **Rhino 8** + **Grasshopper** — Primary CAD environment
- **Obsidian** — Knowledge base, project documentation, research archive
- **VS Code / Cursor** — Code editing (screen-reader-compatible modes)

### Key Libraries
- **rhinoscriptsyntax** (`rs`) — Rhino geometry creation (watcher side)
- **RhinoCommon** — Events, low-level Rhino operations (watcher side)
- **OpenCV** (`cv2`) — Computer vision for pegboard tracking
- **Windows SAPI** (`win32com.client`) — Text-to-speech for audio feedback
- **json** / **os** / **copy** — Core stdlib modules powering the CLI pipeline

### Hardware
- PIAF machine + laser printer (carbon toner) for tactile graphics
- Ray-Ban Meta glasses for AI-powered image capture/description
- Pegboard + overhead camera for physical input
- 3D printer for jigs, structural kits, tactile models
- Braille display (Daniel's primary text output)

### AI Services
- Anthropic Claude API (vision, code generation, descriptions)
- Meta AI (glasses integration, Be My Eyes)
- OpenAI / Google Gemini APIs (alternative pipelines)

---

## Code Conventions

### CLI Side (Python 3)
- **PEP 8** baseline.
- Command dispatch via `dict` mapping strings to handler functions.
- Undo via `copy.deepcopy(state)` stored in a stack before each mutation.
- All file writes through `_atomic_write(path, text)` — write `.tmp`, fsync, then `os.replace`.
- All user-facing output through `print()` with `OK:` / `ERROR:` prefixes.
- `--state` flag for custom state file path; default is same-folder.
- `--verbose` / `-v` flags where appropriate.
- `--json` flag for machine-readable output (supplements, never replaces, human output).
- Schema migration on load: detect old schemas, add new fields with defaults, never break old files.
- **Zero external dependencies.** Python stdlib only. No pip installs, no conda environments.

### Watcher Side (IronPython 2.7)
- Use `rhinoscriptsyntax as rs` for all geometry.
- Hook `Rhino.RhinoApp.Idle += on_idle` for file watching.
- Check `os.path.getmtime()` to detect changes.
- Full rebuild on change (correctness > speed). If incremental rebuild is added later, it must be layer-scoped and deterministic.
- Tag all created objects with `JIG_OWNER`, `JIG_ID`, `JIG_SCHEMA` UserText.
- Print status to Rhino command line: `"[ToolName] Rebuilt: 42 columns."`.
- **No f-strings** — IronPython 2.7 doesn't support them. Use `.format()`.
- **No pathlib** — use `os.path` throughout.
- **No writing to state.json** — watcher is read-only on the CMA.

### JSON State Files
- Always include `"schema"` and `"meta"` at top level.
- Stable IDs for all addressable objects.
- Human-readable: 2-space indent on write.
- Descriptive `snake_case` keys.

### File Organization
```
radical-accessibility/
├── CLAUDE.md                    # This file
├── README.md                    # Public-facing project description
├── tools/
│   ├── school-jig/              # 2D plan generator (working)
│   │   ├── controller_cli_v2.py
│   │   ├── rhino_watcher_v2.py
│   │   ├── state_v2.json
│   │   └── manual.docx
│   ├── [future-tool]/           # Same three-file pattern
│   │   ├── controller.py
│   │   ├── watcher.py
│   │   └── state.json
│   └── shared/                  # Shared utilities
│       ├── atomic_write.py
│       ├── audio_feedback.py
│       └── schema_migrate.py
├── cv/                          # Computer vision (pegboard)
├── tactile/                     # Tactile graphics pipeline
├── vision/                      # AI vision/description
├── docs/
│   ├── CHANGELOG.md
│   ├── setup.md
│   ├── workflows.md
│   └── tactile-standards.md
└── tests/
    ├── test_cli_commands.py
    ├── test_state_migration.py
    └── test_round_trip.py
```

### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- CLI commands: short lowercase words, space-separated (`set bay A rotation 30`)
- JSON keys: `snake_case`
- Tool folders: `kebab-case`
- Rhino layers: `JIG::<Category>` (PascalCase category)

---

## Definition of Done

A change is complete only when:

- **CLI**: help text and examples updated for any new/changed commands.
- **Schema**: version bumped if structure changed; migration logic added so old files still load.
- **Watcher**: ownership-safe behavior verified (no deletion of non-owned objects).
- **Tests**:
  - Schema validation: invalid state files are rejected with clear errors.
  - Golden-state tests: input commands → expected `state.json` (exact match).
  - At least one integration state file that rebuilds in Rhino without errors.
- **Docs**: entry in `CHANGELOG.md`. New tools get a manual.
- **Accessibility**: output tested with a screen reader (or simulated: pipe to text, verify linear readability). If not tested with a blind user, flagged as untested.

---

## Building New Tools on This Pattern

1. **Start with the state schema.** Define the JSON structure first. What parameters does the user control? What are the defaults? Include `"schema"` and `"meta"`. Give every addressable object a stable ID.
2. **Build the CLI.** Pure Python 3, stdlib only. Command dispatch via dict. Undo stack. Atomic writes. `OK:` / `ERROR:` output protocol. Help text for every command.
3. **Build the watcher.** IronPython 2.7 inside Rhino. Idle event hook. Mtime check. Ownership-tagged geometry on `JIG::` layers. Status printed to command line. Never writes to state.json.
4. **Keep them ignorant of each other.** The CLI doesn't import Rhino. The watcher doesn't import the CLI. The JSON file is the only coupling.
5. **Write the manual.** Two audiences: sighted developers maintaining code, and blind users operating tools. Both get text-based docs with numbered steps and expected output.

---

## Grant & Publication Context

### Target Venues
- **ACADIA 2026** (Association for Computer Aided Design in Architecture) — primary target
- **CHI / ASSETS** — HCI and accessibility conferences
- **Journal of Architectural Education (JAE)**

### Framing
Disciplinarily transformative, not assistive. Designing for blindness reveals deep biases in architectural tools and pedagogy. The resulting tools often improve workflows for *all* users. This is a critique of architecture's ocularcentrism that produces genuinely novel computational design methods.

### Key Grant Targets
- NSF DARE (Disability and Rehabilitation Engineering)
- NEA Design grants
- Graham Foundation
- Spencer Foundation (education research)
- NIDILRR (disability, independent living, rehabilitation research)

---

## Legal and Institutional Context

- **Section 504 of the Rehabilitation Act** and **ADA Title II** require equal access to educational programs and activities at public universities.
- **Illinois Information Technology Accessibility Act (IITAA)** applies to all Illinois public universities including UIUC.
- **WCAG 2.1 Level AA** is the institutional benchmark for digital accessibility.
- UIUC's Disability Resources and Educational Services (DRES) provides accommodations; this project goes beyond accommodation to redesign the tools themselves.
- See the project working document for full legal and policy detail.

---

## Collaborator Network

Key subject matter experts and collaborators supporting the project:

- **JooYoung Seo** — Assistant professor, UIUC School of Information Sciences. Expertise in accessible data science, assistive technology, and blind/low-vision HCI research.
- **Marc Thompson** — UIUC Disability Resources and Educational Services (DRES). Assistive technology specialist.
- **Bob Dignan** — UIUC DRES. Accessibility and accommodations.
- **Ann Fredricksen** — UIUC DRES. Accessibility and accommodations.
- **Christy Blew** — UIUC Library. Accessible publishing and document remediation.
- **Deana McDonagh** — Professor, UIUC School of Art + Design. Inclusive design, empathic design research.
- **Keith Hays** — UIUC School of Architecture. Structural engineering and pedagogy.
- **Michael Curtin** — UIUC School of Architecture. Digital fabrication and computational design.

---

## Bibliography

Key references informing the project:

- Melendez, F. (2022). "Disabling Architecture: A Non-visual Approach to Architectural Design." *Journal of Architectural Education*, 76(2).
- Kennedy, J. M. (1993). *Drawing and the Blind: Pictures to Touch*. Yale University Press.
- Gipe-Lazarou, C. (2020). "Haptic Architecture: Designing for Touch-First Spatial Experience." *ACADIA Proceedings*.
- Bartlett School of Architecture / DisOrdinary Architecture Project. Ongoing practice-based research on disability-led design.
- Ghosh, S., & Coppola, M. (2012). "Assistive Technology for Visually Impaired Users: Accessibility Evaluation of Digital Maps." *ASSETS*.
- Kłopotowska, A., & Magdziak, R. (2021). "Architectural Education of Visually Impaired Students: From Theory to Practice." *World Transactions on Engineering and Technology Education*.

---

## Working With This Project

1. **Follow the three-file pattern.** Controller CLI, state JSON, Rhino watcher. Deviate only with good reason.
2. **Never add a visual-only feature.** If it can't be heard, felt, or read by a screen reader, it doesn't ship.
3. **Maintain the CMA contract.** The JSON state describes *what the design is*. The watcher translates to geometry. Keep this separation clean.
4. **Keep the CLI dependency-free.** Python stdlib only.
5. **Respect object ownership.** The watcher only touches geometry it created. Tag everything. Delete only what you own.
6. **Keep Daniel in the loop.** Every tool is co-designed. If you can't test with a blind user, flag it.
7. **Prefer simple, auditable code.** Verbose but predictable beats clever but opaque.
8. **Audio/text feedback is not optional.** Every state change gets confirmation.
9. **Document for two audiences.** Developers maintaining code, and blind users operating tools.
10. **Design for the next transport.** Structure state schemas and command vocabularies so they work over MCP, HTTP, or sockets later. Keep transport and domain logic separate. The CMA stays canonical regardless of how commands arrive.

### When Proposing a New Workflow (MCP, etc.)
Specify:
- What remains canonical (the CMA)
- What becomes transport
- How it serializes to CMA snapshots
- How accessibility guarantees are preserved

### If Uncertain
Provide two options:
- **Option A**: minimal, preserves current working pipeline
- **Option B**: adds capability while keeping CMA stable

Include tradeoffs. Default to A unless B is clearly better.