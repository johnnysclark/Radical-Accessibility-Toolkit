# Ethan's `fabric-accessible-graphics` Repository — Full Inventory & Comparative Analysis

> Source: [github.com/ethanshig/fabric-accessible-graphics](https://github.com/ethanshig/fabric-accessible-graphics)
> Surveyed: 2026-02-24

This document catalogs every component in Ethan's repo, organizes them into functional categories, and compares each category in detail against our Layout Jig (School Jig) toolchain. The goal is to identify what to reuse, what overlaps, what's complementary, and where to converge.

---

## Overview

**Package name**: `pai-radical-accessibility` v1.1.0
**License**: MIT
**Structure**: Two Python libraries (TACT + TASC), an MCP server, four PAI skills, TypeScript tool wrappers, a hooks/learning system, and reference documentation.

```
fabric-accessible-graphics/
├── lib/
│   ├── tactile-core/        # TACT — image-to-tactile PDF pipeline
│   └── tasc-core/           # TASC — programmatic Rhino design CLI
├── mcp/                     # Standalone MCP entry point
├── src/
│   ├── skills/              # 4 PAI skill definitions
│   ├── tools/               # TypeScript wrappers
│   ├── hooks/               # Learning/feedback system
│   └── shared/              # Cross-skill context docs
├── scripts/                 # Dev/test scripts
├── patterns/                # Tactile guidelines + hatch references
├── docs/                    # User guides
├── samples/                 # Test images
├── examples/                # Output demos
└── classroom_wing.py        # TASC DSL example
```

---

## The Broader Categories

Both projects address the same mission — making architectural education accessible — but they attack different parts of the workflow. When you lay them side by side, the tools fall into **nine functional categories**:

| # | Category | Ethan's Repo | Layout Jig | Overlap? |
|---|----------|-------------|------------|----------|
| 1 | Design Authoring | TASC | School Jig (controller_cli.py) | **High** — same intent, different architecture |
| 2 | Image-to-Tactile Conversion | TACT | — | **None** — Ethan only |
| 3 | Tactile Fabrication | TACT PDF generator (ReportLab) | tactile_print.py (STL mesh + Bambu) | **Low** — different output formats |
| 4 | Braille & Text Labeling | braille_converter.py (liblouis) | Built-in label/braille fields | **Medium** — both label, different methods |
| 5 | AI Integration (MCP) | TACT MCP (6 tools + 3 resources) | mcp_server.py (5 tools) | **Medium** — different scopes |
| 6 | Rhino Connection | RhinoMCP TCP socket (port 1999) | File-watcher (mtime polling) | **Low** — same goal, different transport |
| 7 | Accessibility Infrastructure | AccessibleLogger, PAI skills | TTS, OK:/ERROR: protocol | **Medium** — complementary patterns |
| 8 | State Management & Undo | 10-deep disk-persisted stack | Numbered history + named snapshots | **Medium** — Layout Jig more capable |
| 9 | Standards & Documentation | Hatch system, Arch-Alt-Text, guidelines | MANUAL.docx, CLAUDE.md | **Low** — Ethan has richer reference material |

---

## Category 1: Design Authoring

This is the core overlap. Both tools let a blind user create architectural floor plans by typing commands — no mouse, no screen required.

### TASC (Ethan)

- **Framework**: Click (external dependency). Each command is a decorated Click function.
- **State model**: Python dataclasses (`Site`, `Grid`, `Zone`, `Bay`, `Corridor`, `BayVoid`, `TASCModel`). Serialized to `.tasc_state.json`.
- **Design vocabulary**: Site boundary (polygon or rectangle) → structural grid (spacing + rotation) → zones (named regions with program types: residential, commercial, circulation, etc.) → bays (structural grids with columns) → corridors and voids attached to bays.
- **Command style**: `tasc zone "Classroom A" 30 40 --at 10,20 --type residential`. Each command is a separate invocation (Click subcommands, not a REPL).
- **DSL scripting**: A module-level API (`from tasc_core.dsl.api import *`) lets you write Python scripts like `boundary(300, 200)`, `grid(20, rotation=15)`, `zone("Library", 60, 40, at=(100, 80))`. The `classroom_wing.py` example shows a complete building.
- **Validation**: Ray-casting point-in-polygon checks that zones stay inside the site boundary. Segment intersection detects overlaps.
- **Export**: Rhino live (via socket), offline .3dm (via rhino3dm library), PIAF PDF (renders to PIL image then pipes through TACT), or text description.
- **Lines of code**: ~572 (CLI) + 482 (model) + 165 (feedback) + 120 (validation) + 170 (exporter) = ~1,509 total.
- **Tests**: 146 pytest tests covering CLI, model, Rhino connector, and validation.

### School Jig / Layout Jig (Ours)

- **Framework**: Python stdlib only. Zero external dependencies. Command dispatch via dict mapping.
- **State model**: Plain dicts/lists in a single JSON file (`state.json`). No dataclasses. Schema versioned via `"schema": "plan_layout_jig_v2.3"`.
- **Design vocabulary**: Site → bays (rectangular OR radial grids, with z-ordering for overlap) → corridors (x/y axis, single/double-loaded, dashed centerlines) → walls (with per-gridline segments) → apertures (doors, windows, portals with swing/hinge) → rooms (cells within bays with hatch images) → void cutouts → labels and Braille → legend → block symbols.
- **Command style**: Interactive REPL with space-separated tokens: `set bay A rotation 30`, `wall A on`, `aperture A add d1 door x 1 5 3 7`, `corridor A width 12`. Session stays open — type commands, get immediate feedback.
- **DSL scripting**: No separate DSL module. The REPL is the primary interface. MCP server provides a programmatic entry point.
- **Validation**: Input validation per-command (range checks, bay existence). No spatial overlap detection between bays.
- **Export**: JSON state → Rhino watcher rebuilds geometry. tactile_print.py generates STL for 3D printing. Section cut → SVG. Print command → raster image.
- **Lines of code**: ~1,800+ (controller_cli.py alone) + ~1,030 (tactile_print.py) + ~226 (mcp_server.py) = ~3,050+ total.
- **Tests**: No formal test suite yet.

### Deep Comparison

| Dimension | TASC | Layout Jig | Verdict |
|-----------|------|-----------|---------|
| **Dependencies** | Click, PyYAML, Rich, rhino3dm, tactile-core | stdlib only | Layout Jig wins for deployment simplicity. Anyone with Python 3 can run it. TASC requires `pip install` with compiled binaries (rhino3dm). |
| **Design depth** | Zones, bays, grids, corridors, voids | Bays, corridors, walls, apertures (doors/windows/portals), rooms with hatch fills, cells, block symbols, legend, radial grids, z-ordering | Layout Jig is significantly deeper. It models wall segments, door swings, window sills, hatch patterns per room, a legend system, and PIAF-optimized block symbols. TASC has zones and bays but no walls, doors, or interior detail. |
| **Radial grids** | Not supported | Full radial support: rings, arms, arc_deg, arc_start_deg | Layout Jig only |
| **Irregular spacing** | Supported via `spacing_x`/`spacing_y` lists | Supported via same pattern (`spacing_x`/`spacing_y`) | Parity |
| **Spatial validation** | Point-in-polygon, zone overlap detection | Per-command input validation only | TASC has geometric validation that Layout Jig lacks |
| **Interaction model** | Batch (one command per invocation) OR script file | Interactive REPL (persistent session) | Both valid. Layout Jig feels more like a conversation. TASC feels more like a build script. |
| **State format** | Python dataclasses → JSON via `to_dict()`/`from_dict()` | Raw dicts, hand-managed | TASC is more formally structured. Layout Jig is more flexible but less type-safe. |
| **Schema migration** | Via dataclass defaults (unrecognized fields ignored) | Auto-add missing keys with defaults on load | Similar approach, different mechanisms |
| **3D capabilities** | None | Tactile 3D: wall extrusion, cut heights, floor slabs, STL export, Bambu printer integration | Layout Jig only |
| **Hatch/texture system** | None | Image-based hatch fills per room/corridor, hatch library management, scalable/rotatable | Layout Jig only |

**Bottom line**: TASC is cleaner in software engineering terms (typed dataclasses, pytest suite, separated concerns) but covers maybe 30% of the architectural vocabulary that Layout Jig does. Layout Jig is a bigger, more battle-tested tool with significantly more design capability, but it's a monolithic 1,800-line file with no formal tests.

---

## Category 2: Image-to-Tactile Conversion

**This is entirely Ethan's territory.** Layout Jig has no equivalent.

TACT converts existing images (photographs, CAD screenshots, scanned plans, El Croquis pages) into PIAF-ready PDFs. This is a fundamentally different operation from design authoring — it's about translating visual information into tactile form, not creating new designs.

### TACT Pipeline

```
Input image (JPG, PNG, PDF, TIFF)
  → Load + color mode conversion
  → Optional contrast enhancement (S-curve, CLAHE, histogram EQ)
  → Grayscale conversion
  → Text detection (Tesseract / EasyOCR / Hybrid Claude Vision)
  → Threshold to B&W
  → Density check + auto-reduction (morphological erosion)
  → Braille label generation (liblouis Grade 1/2)
  → Label overlap detection + repositioning
  → Abbreviation key generation
  → Optional: zoom/crop, aspect ratio adjustment, tiling
  → Optional: RainbowTact color-to-tactile patterns
  → PDF output at 300 DPI (ReportLab)
  → Optional: sticker workflow (dual PDF), key pages
```

### Key Technical Details

- **10 presets** tuned for specific image types: floor_plan (threshold 100, auto_contrast), elevation (threshold 120, s_curve), photograph (threshold 90, clahe), sketch (threshold 140, none), etc.
- **Density management** is critical for PIAF: too many black pixels and the swell paper puffs up into an unreadable blob. TACT enforces <45% max, <30% target, and can auto-reduce via iterative morphological erosion.
- **Three OCR engines**: Tesseract (fast, good positions, mediocre text accuracy), EasyOCR (better accuracy, slow 12s init), and Hybrid (Tesseract positions + Claude Vision text readings, merged via `SequenceMatcher` fuzzy matching). The grid overlay system creates Excel-style cell labels so Claude Vision can report "text 'Kitchen' is at cell B3" and the tool maps that to pixel coordinates.
- **RainbowTact** (Ka & Kim, ICCHP 2024) converts color images to tactile patterns: K-means color segmentation → hue maps to wave frequency, saturation maps to wave amplitude, value maps to line width. Achromatic regions get dot grids instead. A color legend page shows each pattern-to-color mapping.
- **Sticker workflow** generates two PDFs: first pass prints the image (carbon toner only), second pass prints text labels separately on clear sticker paper for overlay.

### Why This Matters for Us

Layout Jig generates plans from scratch — it controls every line. But when Daniel or John encounter an existing drawing (a precedent study, a textbook figure, a classmate's work, a pin-up image from Ray-Ban Meta glasses), they need a conversion tool. TACT fills that gap completely.

### Integration Opportunity

TACT's MCP server (`tact-mcp`) could run alongside Layout Jig's MCP server. Claude could use Layout Jig to design, then TACT to convert reference images — all in the same conversation.

---

## Category 3: Tactile Fabrication

Both projects produce physical tactile output, but through different media.

### Ethan: PIAF PDF (2D swell paper)

- Output: PDF at 300 DPI via ReportLab.
- Physical process: Print on PIAF swell paper with carbon-based black toner → run through PIAF heater → black areas swell, creating raised tactile surface.
- Paper sizes: letter (8.5x11") and tabloid (11x17").
- The entire TACT pipeline is optimized for this: density limits, line weight standards (1.5–4mm), Braille sizing (BANA standard 6.2mm cell-to-cell), tiling with registration marks for large images.
- Also supports sticker workflow (overlay Braille on existing prints).

### Layout Jig: STL Mesh + Bambu (3D printing)

- Output: Binary STL via pure Python math (no numpy, no Rhino).
- Physical process: Wall segments extruded to configurable height, clipped at cut_height, optional floor slab → sliced to 3MF via Orca Slicer → uploaded to Bambu Lab printer via FTPS/MQTT.
- The mesh generation replicates the watcher's wall extrusion logic: rectangular bays → wall segments with gaps at aperture openings → extruded boxes.
- Section cut export to SVG provides 2D slices through the 3D model.
- Also has 2D raster print export (PNG/JPG) for scaled architectural printing.

### Deep Comparison

| Dimension | TACT (Ethan) | tactile_print.py (Layout Jig) |
|-----------|-------------|-------------------------------|
| **Output format** | PDF (2D) | STL (3D mesh) + SVG (section cuts) + PNG/JPG (raster) |
| **Target hardware** | PIAF swell paper machine + laser printer | Bambu Lab 3D printers (X1C, P1S, A1, etc.) |
| **What it produces** | Flat raised surfaces from existing images | 3D architectural section models from parametric state |
| **Dependencies** | ReportLab, Pillow, NumPy, OpenCV | Zero (pure Python stdlib — `struct` for binary STL, `math` for geometry) |
| **PIAF optimization** | Deep: density management, line standards, Braille sizing | None — different output medium |
| **3D printing integration** | None | Full: export → slice → FTP upload → MQTT print command → live status |
| **Section cuts** | None | Cut plane at X or Y offset → 2D line segments → SVG |
| **Scaling** | Image scaling with auto-fit to paper | Configurable representation scale (1:N), auto-centering on build plate |
| **Mesh generation** | N/A | Wall extrusion with aperture gaps, floor slab, all from state.json |

**Bottom line**: These are complementary, not competing. TACT makes 2D tactile prints from images. tactile_print.py makes 3D physical models from parametric designs. A complete workflow might be: design in Layout Jig → export 2D plan via TACT for swell paper review → export 3D section via tactile_print for physical model.

---

## Category 4: Braille & Text Labeling

Both projects generate Braille labels, but the implementations are profoundly different.

### Ethan: Standalone Braille Pipeline

`braille_converter.py` (796 lines) is a full Braille production system:

- **Liblouis integration**: Uses the open-source Braille translation library for proper Grade 1 and Grade 2 (contracted) Braille. Grade 2 Braille is significantly shorter than Grade 1 — "the" becomes a single character — which matters when space is tight.
- **Fallback converter**: When liblouis isn't installed, falls back to a character-by-character ASCII-to-Unicode Braille mapping. Only supports Grade 1 in fallback mode.
- **Physical accuracy**: BANA-standard sizing: 300 DPI, 24pt font (6.2mm cell-to-cell), ~60px per character width. These constants match real Braille embossing specifications.
- **Label overlap detection**: Before placing each label, checks all previously placed labels for bounding-box intersection (with configurable minimum spacing of 6px). Tries repositioning: below, above, right, left. If no clear position exists, replaces with a symbol (a, b, c...) and generates a key page.
- **Abbreviation key system**: When Braille text is wider than the original bounding box (or would bleed off the image edge), it abbreviates to a letter (A, B, C...) and generates a separate key page mapping letters to full text.
- **Symbol key system**: Separate from abbreviation — when labels overlap and can't be repositioned, they get symbols and a symbol key page.
- **Rotation support**: Labels carry `rotation_degrees` for angled text (0°, 90°, -90°).
- **Image space whiteout**: `processor.py` has `whiteout_braille_regions()` and `whiteout_text_regions()` — blanks out the area under each Braille label and the original text so the PIAF swell paper doesn't create interfering bumps.

### Layout Jig: Inline Label Fields

Layout Jig's Braille handling is simpler and structurally different:

- **Per-bay fields**: Each bay in state.json has `"label"` and `"braille"` string fields. The user sets them manually: `set bay A label "Gallery"`, `set bay A braille "⠠⠛⠁⠇⠇⠑⠗⠽"`.
- **Legend system**: A dedicated legend panel (`legend on`, `legend position bottom-right`) displays all bay labels with both English and Braille text. The legend itself has `title_braille`.
- **Rendering**: The Rhino watcher draws the labels as text objects on `JIG::` layers. The controller doesn't do Braille conversion — the user pastes in pre-converted Braille text or the watcher renders whatever string is in the field.
- **No liblouis**: No automatic text-to-Braille conversion. The user (or an external tool) must provide the Unicode Braille string.
- **No overlap detection**: Labels are placed at fixed positions based on bay geometry. No dynamic repositioning.

### Deep Comparison

| Dimension | Ethan (braille_converter.py) | Layout Jig |
|-----------|------------------------------|------------|
| **Automatic conversion** | Yes — text in, Braille out (Grade 1 or 2) | No — user provides Braille string manually |
| **Grade 2 (contracted)** | Yes, via liblouis | No |
| **Overlap handling** | Detect → reposition → symbolize → generate key page | None |
| **Abbreviation system** | Auto-abbreviate when label exceeds bounding box | None |
| **Physical standards** | BANA-compliant sizing at 300 DPI | User-configurable text height (but not BANA-calibrated) |
| **Image whiteout** | Clears underlying pixels for clean PIAF | N/A (vector rendering in Rhino, not raster) |
| **Integration** | Used by TACT pipeline (embedded in PDF) | Used by Rhino watcher (rendered as geometry) |

**Integration opportunity**: Ethan's `BrailleConverter.convert_text()` could be extracted as a utility that Layout Jig calls when the user types `set bay A label "Gallery"` — it would auto-populate the `braille` field. Would require liblouis as an optional dependency or using the fallback converter.

---

## Category 5: AI Integration (MCP Servers)

Both projects have MCP servers, but they serve fundamentally different purposes.

### Ethan: TACT MCP (Image Conversion)

- **Server**: FastMCP with stdio transport, registered as `tact-mcp`.
- **6 tools**: `image_to_piaf` (full conversion), `list_presets`, `analyze_image` (pre-flight analysis: dimensions, density, text detection, grid overlay for Claude Vision), `describe_image` (returns Arch-Alt-Text prompt for Claude to use with its own vision), `extract_text_with_vision` (two-phase hybrid OCR workflow), `assess_tactile_quality` (post-conversion quality check).
- **3 resources**: System prompts loaded as MCP resources — `arch-alt-text://prompt`, `ocr-extraction://prompt`, `zoom-region-finder://prompt`. These teach Claude how to describe images, extract text, and identify zoom regions.
- **Design pattern**: The MCP tools do heavy lifting — `image_to_piaf` runs the full conversion pipeline. The AI is an orchestrator that selects presets, adjusts parameters, and handles the multi-step OCR workflow.
- **Lines**: 200 (server.py) + 2,046 (tools.py) = 2,246 lines.

### Layout Jig: Design Command MCP

- **Server**: FastMCP with stdio transport, registered as `layout-jig`.
- **5 tools**: `run_command` (execute any CLI command), `describe` (full model description), `list_bays` (compact table), `get_state` (raw JSON), `get_help` (command reference).
- **Design pattern**: The MCP is a thin wrapper — `run_command()` loads state, tokenizes the command string, calls `apply_command()`, saves state. The AI constructs command strings from conversational input. All logic lives in `controller_cli.py`.
- **Undo handling**: Returns error suggesting snapshots (undo requires session state that doesn't exist in stateless MCP mode).
- **Print redirection**: `builtins.print` redirected to stderr since stdout is the JSON-RPC channel.
- **Lines**: 226 lines.

### Deep Comparison

| Dimension | TACT MCP | Layout Jig MCP |
|-----------|---------|----------------|
| **Scope** | Image conversion (input → output pipeline) | Design authoring (stateful model manipulation) |
| **Tool granularity** | Fine-grained: analyze, convert, assess as separate tools | Coarse: one `run_command` tool handles everything |
| **AI role** | Orchestrator (selects presets, adjusts parameters, runs multi-step OCR) | Translator (converts natural language to CLI commands) |
| **Resource prompts** | 3 (Arch-Alt-Text, OCR extraction, zoom finder) | None |
| **State management** | Stateless per-call (loads file, converts, writes output) | Stateless per-call (loads state, runs command, saves state) |
| **Complexity** | 2,246 lines | 226 lines |

**Integration opportunity**: Both servers could run simultaneously. Claude Desktop or Cursor would see `layout-jig` tools for design and `tact-mcp` tools for conversion in the same session. A workflow like "design a floor plan, then convert this reference image for comparison" becomes natural.

---

## Category 6: Rhino Connection

Both projects display geometry in Rhino, but they use completely different transport mechanisms.

### Ethan: RhinoMCP (TCP Socket)

TASC connects to Rhino via `RhinoMCP`, a TCP socket server (port 1999) running inside Rhino:

- **Three-tier fallback**: `MCPClient` (direct TCP) → `RhinoCodeClient` (via `rhinocode` CLI binary) → Offline mode (skip Rhino, just update state).
- **WSL2 awareness**: Auto-detects WSL2 via `/proc/version`, resolves Windows gateway IP via `ip route show default`. This lets TASC running in WSL2 talk to Rhino running on the Windows host.
- **Protocol**: JSON wire protocol matching the RhinoMCP specification. Commands like `create_polyline_cmd()`, `create_line_cmd()`, `set_layer_cmd()`.
- **Drawing**: `RhinoDrawer` class with methods for each architectural element: `draw_site()`, `draw_grid()`, `draw_zone()`, `draw_bay()`, `draw_columns()`, `draw_corridor()`, `draw_void()`. All geometry goes to `TASC_*` layers.
- **Advantage**: Real-time updates. Each command draws immediately.
- **Disadvantage**: Requires RhinoMCP to be running. Socket can break. WSL2 networking can be flaky. More moving parts.

### Layout Jig: File Watcher (mtime Polling)

Layout Jig uses the file-watching pattern described in CLAUDE.md:

- **One-way data flow**: CLI writes `state.json` → Rhino watcher polls `os.path.getmtime()` on idle event → watcher rebuilds geometry.
- **Atomic writes**: Write to `.tmp`, fsync, `os.replace()`. Watcher never reads a half-written file.
- **Full rebuild**: On every change, the watcher clears all `JIG::` layers and rebuilds from scratch. Correctness over speed.
- **Ownership tagging**: `JIG_OWNER`, `JIG_ID`, `JIG_SCHEMA` UserText on every object. Watcher only deletes what it created.
- **IronPython 2.7**: The watcher runs inside Rhino 8's Python environment, which is IronPython 2.7 on .NET. No f-strings, no pathlib.
- **Advantage**: Completely decoupled. CLI and Rhino are independent processes. If Rhino crashes, nothing is lost — restart, run watcher, everything rebuilds from state.json.
- **Disadvantage**: Not real-time in the socket sense. There's a polling interval (idle event frequency). Full rebuild on every change is wasteful for large models.

### Deep Comparison

| Dimension | RhinoMCP (Ethan) | File Watcher (Layout Jig) |
|-----------|------------------|---------------------------|
| **Latency** | Low (direct socket) | Higher (polling interval + full rebuild) |
| **Reliability** | Socket can break, needs RhinoMCP running | Rock-solid — just a file on disk |
| **Crash recovery** | Must reconnect | Automatic — restart watcher, it reads state.json |
| **Platform** | Works from WSL2 (with gateway detection) | Windows-native (IronPython in Rhino) |
| **Incremental update** | Yes (draws individual commands) | No (full layer clear + rebuild) |
| **Complexity** | 185 + 160 + 290 = 635 lines | ~500 lines (watcher script) |
| **Dependencies** | RhinoMCP server must be running | Just the Rhino idle event hook |

**Both are valid for their use cases.** The file-watcher pattern is simpler and more robust. The socket pattern is faster and supports WSL2. Long-term, the socket approach could adopt the ownership-tagging discipline from Layout Jig's watcher.

---

## Category 7: Accessibility Infrastructure

Both projects are built accessibility-first, but express it through different mechanisms.

### Ethan: AccessibleLogger + PAI Skills

- **AccessibleLogger** (`utils/logger.py`, 110 lines): All output uses semantic prefixes flushed immediately. Methods: `progress()`, `loading()`, `checking()`, `found()`, `generating()`, `success()`, `complete()`, `warning()`, `error()`, `solution()`, `info()`. Example: `Processing: Converting to grayscale`, `Success: Image processing complete`, `Error: File not found`.
- **PAI Skills**: Four skill definitions that teach an AI assistant how to interact accessibly:
  - `TactileConversion` — wraps `tact` CLI with preset selection workflow
  - `TactileGeneration` — AI image generation with mandatory tactile suffix
  - `AccessibleDescription` — Arch-Alt-Text framework (Macro/Meso/Micro)
  - `AccessibleRhino` — TASC command reference with parameter gathering rules
- **Shared context docs**: `ArchitecturalContext.md` (domain vocabulary), `TactileGuidelines.md` (PIAF specs)
- **`.claude/CLAUDE.md`**: AI interaction rules — screen-reader output must be plain text only (no markdown in output), parameter gathering instructions, feedback rules.
- **No TTS**: Does not include audio output.

### Layout Jig: OK:/ERROR: Protocol + TTS

- **Output protocol**: Every command response starts with `OK:` or `ERROR:`. Screen readers can parse the first token immediately. `describe` uses `LABEL: value` format, one item per line. No tables, no multi-column alignment. This is codified in the project CLAUDE.md.
- **TTS (Text-to-Speech)**: Fire-and-forget via PowerShell `System.Speech.Synthesis.SpeechSynthesizer`. Strips OK:/ERROR: prefixes for cleaner speech. Configurable rate (-10 to 10). The `_out()` wrapper in the main loop prints AND speaks every response when TTS is enabled.
- **No PAI skills**: No structured skill definitions for AI assistants. The MCP server provides tool access but doesn't include conversational guidelines.
- **No structured logging**: Direct `print()` calls, not a logger class. Works because the output protocol is consistent by convention.

### Deep Comparison

| Dimension | Ethan | Layout Jig |
|-----------|-------|-----------|
| **Output format** | Semantic prefixes via logger class (Processing:, Success:, Error:) | Manual OK:/ERROR: protocol via print() |
| **Screen reader optimization** | Yes — plain text only, flushed immediately | Yes — one line per item, predictable ordering |
| **TTS audio** | None | PowerShell SAPI with configurable rate |
| **AI interaction guidelines** | Detailed PAI skill definitions + .claude/CLAUDE.md rules | MCP server + project CLAUDE.md principles |
| **Structured logging** | AccessibleLogger class with rich methods | Convention-based print() |
| **Accessibility testing** | Not described | Flagged as untested if not tested with blind user |

**Integration opportunity**: Layout Jig's TTS system could be extracted as a shared utility. Ethan's `AccessibleLogger` pattern could replace Layout Jig's ad-hoc print() calls for more consistent output. The PAI skill definitions could be adapted for Layout Jig's MCP server.

---

## Category 8: State Management & Undo

### Ethan: Disk-Persisted Undo Stack

- **Mechanism**: `push_undo()` saves full state to `.tasc_undo.json` before each mutation. `pop_undo()` restores. Max 10 entries.
- **Storage**: Single JSON file containing a list of state snapshots.
- **Limitations**: Fixed depth (10). No named checkpoints. File gets large with many snapshots.

### Layout Jig: Numbered History + Named Snapshots

- **In-memory undo**: `copy.deepcopy(state)` pushed to a Python list before each mutation. `undo` pops the last entry.
- **Numbered history**: Every mutation writes `history/0001.json`, `history/0002.json`, etc. alongside the state file. Undo deletes the last history file.
- **Named snapshots**: `snapshot save midterm` writes `history/snapshot_midterm.json`. `snapshot load midterm` restores it. Snapshots persist across undo operations.
- **History browsing**: `history list` shows last 20 entries + all named snapshots with sizes and timestamps. `history count` shows total.
- **Unlimited depth**: History files accumulate until disk is full. No fixed cap.
- **Atomic writes**: All history files written via `_atomic_write()`.

### Deep Comparison

| Dimension | TASC | Layout Jig |
|-----------|------|-----------|
| **Undo depth** | 10 (fixed) | Unlimited (memory for in-session, disk for history) |
| **Named checkpoints** | No | Yes — snapshot save/load |
| **History browsing** | No | Yes — history list/count |
| **Persistence** | Single undo file | Individual history files (easier to inspect, diff, or version-control) |
| **Disk usage** | Bounded (10 snapshots in one file) | Unbounded (one file per mutation) |

**Layout Jig is clearly more capable here.** The numbered files are individually inspectable, diffable, and the named snapshot system lets Daniel checkpoint before major design changes ("snapshot save before_south_wing").

---

## Category 9: Standards & Documentation

### Ethan: Rich Reference Material

- **Hatch system** (`HATCH_SYSTEM.md`): 6 tactile hatch patterns (steel, concrete, masonry, wood, earth, glass) optimized for PIAF and BANA standards. Plus `TRADITIONAL_HATCHING.md` for AIA conventions. Plus generated PDF test sheets for physical testing.
- **Arch-Alt-Text** (`image_description_machine.md`): A structured framework for describing architectural images at three levels — Macro (3 sentences: type, composition, purpose), Meso (4+ sentences: spatial, structural, material, contextual), Micro (8+ sentences: every detail). This is loaded as an MCP resource so Claude knows how to describe images.
- **Tactile guidelines** (`ARCHITECTURAL_TACTILE_GUIDELINES.md`): Comprehensive conversion guidelines for both humans and LLMs. Plus floor-plan-specific rules.
- **Tactile standards** (`tactile_standards.yaml`): PIAF processing defaults, density limits, line standards, Braille settings.
- **Installation guides**: INSTALL.md, VERIFY.md, QUICKSTART.md, WALKTHROUGH.md, WINDOWS-QUICKSTART.md, MCP_SETUP.md, TEXT_DETECTION_QUICKSTART.md — thorough onboarding for different platforms.
- **Reference PDFs**: Tactile Graphics Standards and Guidelines 2022 (the published standard) included in the repo.

### Layout Jig: Operational Documentation

- **MANUAL.docx**: 19-section user manual covering all commands, including the four new extensions (TTS, Section Cut, History/Snapshots, MCP Server). Written for both sighted developers and blind users.
- **CLAUDE.md** (project-wide): Comprehensive project principles, architecture, conventions, and "Definition of Done" criteria. This is the primary reference for how tools should be built.
- **README.md**: Feature list, folder structure, quick start.
- **No standalone standards docs**: Relies on CLAUDE.md principles rather than separate reference documents.

### What Layout Jig Could Borrow

1. **Arch-Alt-Text framework**: Useful for any image description task. Could be loaded as an MCP resource in Layout Jig's server.
2. **Hatch system reference**: Layout Jig already has hatch patterns per room, but lacks a codified standard for which pattern represents which material. Ethan's 6-pattern system provides that.
3. **Tactile standards YAML**: Density limits, line weight standards, Braille sizing — all relevant to Layout Jig's PIAF output.

---

## Hooks / Learning System (Ethan only)

This is unique to Ethan's repo and has no Layout Jig equivalent. Located in `src/hooks/`, written in TypeScript (Bun runtime).

- **ConversionTracker.ts** (140 lines): PostToolUse hook that fires after every `image_to_piaf` MCP call. Records image type, preset, settings, success/failure to the memory system.
- **FeedbackCapture.ts** (120 lines): Captures student ratings (1–5) and tags (clear, detailed, readable, confusing, too-dense, missing-details) on conversion quality.
- **ImageDetector.ts** (100 lines): Proactively detects architectural images in conversation, classifies type (floor_plan, section, elevation, sketch...), suggests preset.
- **lib/memory.ts** (200 lines): Persistent memory system in `~/.radical-accessibility/memory/`. Functions: `recordConversion()`, `recordFeedback()`, `getConversionHistory()`, `getMemoryStats()`, `getLearnedPreferences()`.

**Why this matters**: Over time, the system learns which presets work best for which image types, which threshold values Daniel prefers, and which conversions need adjustment. This is a feedback loop that improves conversion quality through use.

**Integration opportunity**: This pattern could be adapted for Layout Jig's MCP server — tracking which commands Daniel uses most, which bay configurations he prefers, common correction sequences.

---

## Scripts, Samples, and Examples

### Ethan: Development/Testing Scripts

8 Python scripts in `scripts/` for OCR testing and visualization:

| File | Purpose |
|------|---------|
| `create_annex_visualization.py` | Bounding-box visualization of Tesseract OCR detections |
| `demo_text_detection.py` | Text detection pipeline demo |
| `manual_braille_placement.py` | Interactive manual text positioning → Braille PDF |
| `ocr_comparison_labeled.py` | Numbered/labeled OCR visualizations with legends |
| `ocr_comparison_test.py` | Tesseract vs Claude Vision comparison |
| `test_hybrid_ocr.py` | Hybrid Tesseract+Claude merging with cache |
| `test_text_detection.py` | Tesseract installation test |
| `test_zoom_scaling.py` | Zoom/scaling features test |

### Ethan: Sample Images

11 test images in `samples/`: official architectural plans (ANNEX-PLANS-OFFICIAL), CAD screenshots, El Croquis magazine pages, photographs, hand sketches, generated test images.

4 output examples in `examples/`: Braille overlay, B&W conversion, MCP-driven conversion, tiled output. Plus `braille_demo.py` showing Grade 1/2 conversion.

DSL example: `classroom_wing.py` — complete TASC script building a 300x200ft site with 4 classrooms, double-loaded corridor, entry, restrooms, and storage.

---

## File-Level Inventory

### TACT (lib/tactile-core/)

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 11 | Package metadata, exports ImageProcessor + PIAFPDFGenerator |
| `cli.py` | 1,369 | Click CLI — `convert`, `batch`, `presets` commands |
| `core/processor.py` | 961 | Image loading, grayscale, threshold, density, erosion, crop, scale |
| `core/contrast.py` | 231 | S-curve, CLAHE, histogram EQ, auto-enhance |
| `core/braille_converter.py` | 796 | Liblouis Grade 1/2, fallback, overlap detection, abbreviation keys |
| `core/pdf_generator.py` | 1,667 | ReportLab PDF output, Braille rendering, key pages, sticker workflow |
| `core/text_detector.py` | 270 | Tesseract OCR with dimension regex |
| `core/easyocr_detector.py` | 90 | EasyOCR wrapper (lazy singleton) |
| `core/hybrid_text_detector.py` | 270 | Merges Tesseract positions + Claude Vision text |
| `core/converter.py` | 1,159 | Orchestrates full conversion pipeline |
| `core/rainbowtact.py` | 355 | Color-to-tactile patterns (K-means → waves/dots) |
| `core/tiler.py` | 240 | Image tiling with registration marks |
| `core/grid_overlay.py` | 230 | Grid overlay for Claude Vision reference |
| `core/label_scaler.py` | 195 | Braille label fit analysis |
| `config/presets.py` | 200 | 10 presets manager |
| `config/standards_loader.py` | 155 | Loads tactile_standards.yaml |
| `utils/logger.py` | 110 | AccessibleLogger |
| `utils/validators.py` | 175 | Input validation |
| `utils/cache.py` | 180 | OCR result cache |
| `mcp_server/server.py` | 200 | FastMCP registration |
| `mcp_server/tools.py` | 2,046 | MCP tool implementations |
| **TACT total** | **~9,510** | |

### TASC (lib/tasc-core/)

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 9 | Package metadata, exports model classes |
| `cli.py` | 572 | Click CLI — 13 commands |
| `core/model.py` | 482 | Dataclasses + serialization |
| `core/feedback.py` | 165 | Screen-reader text formatters |
| `core/validation.py` | 120 | Point-in-polygon, overlap detection |
| `core/exporter.py` | 170 | PIL → PIAF PDF, .3dm, text |
| `rhino/connector.py` | 185 | Three-tier connection management |
| `rhino/protocol.py` | 160 | RhinoMCP JSON wire protocol |
| `rhino/commands.py` | 290 | RhinoDrawer high-level operations |
| `dsl/api.py` | 185 | Module-level DSL functions |
| `tests/test_cli.py` | ~350 | CLI tests |
| `tests/test_model.py` | ~400 | Model tests |
| `tests/test_rhino_connector.py` | ~150 | Connector tests |
| `tests/test_validation.py` | ~200 | Validation tests |
| **TASC total** | **~3,438** | |

### Layout Jig (Ours)

| File | Lines | Purpose |
|------|-------|---------|
| `controller_cli.py` | ~1,800+ | Everything: CLI, commands, describe, undo, TTS, history, section, dispatch |
| `tactile_print.py` | ~1,030 | STL mesh, section cuts, SVG, Bambu integration |
| `mcp_server.py` | 226 | FastMCP wrapper |
| `rhino_watcher.py` | ~500 | IronPython 2.7 Rhino geometry builder |
| `state.json` | ~200 | Canonical Model Artifact |
| **Layout Jig total** | **~3,750** | |

---

## Summary: What Each Project Does Best

### Ethan Excels At

1. **Image conversion** — TACT is a complete, well-tested pipeline for turning any image into a PIAF PDF. Nothing in Layout Jig competes.
2. **Braille production** — Liblouis Grade 2, overlap detection, abbreviation keys, image whiteout. Industrially correct.
3. **OCR** — Three-engine approach (Tesseract + EasyOCR + hybrid Claude Vision) with caching.
4. **Software engineering practices** — Typed dataclasses, 146 tests, separated modules, proper packaging (pyproject.toml, hatchling).
5. **Reference documentation** — Hatch standards, Arch-Alt-Text, tactile guidelines, installation guides.
6. **AI skill definitions** — PAI skills teach Claude how to orchestrate the tools conversationally.
7. **Learning/feedback loop** — Hooks track conversion quality over time.
8. **Color-to-tactile** — RainbowTact algorithm is unique and research-grade.

### Layout Jig Excels At

1. **Design depth** — Walls, doors, windows, portals, rooms, hatches, radial grids, z-ordering, legend system, block symbols. Far richer architectural vocabulary than TASC.
2. **Zero dependencies** — Runs on any machine with Python 3 installed. No pip install, no compiled binaries.
3. **3D fabrication** — STL mesh generation, section cuts to SVG, full Bambu printer pipeline (slice, FTP upload, MQTT print, live status). No equivalent in Ethan's repo.
4. **Interactive REPL** — Persistent session with immediate feedback. Feels like a conversation, not a build script.
5. **TTS audio** — PowerShell SAPI speech for every command response.
6. **History/snapshots** — Unlimited numbered history + named snapshots with browsing.
7. **File-watcher resilience** — If Rhino crashes, nothing is lost. The design lives in state.json.
8. **Crash-only viewer** — Fundamental architectural decision that Rhino is disposable. TASC's socket connection is tighter-coupled.

---

## Recommended Integration Paths

### Immediate (no code changes needed)

- Run both MCP servers simultaneously in Claude Desktop. Layout Jig for design authoring, TACT for image conversion. Claude sees both tool sets.
- Use TACT to convert reference images while using Layout Jig to design.

### Short-term (small adaptations)

- Extract Ethan's `BrailleConverter.convert_text()` as a utility for Layout Jig's `set bay A label` command to auto-populate Braille.
- Adopt Ethan's hatch material standard (6 patterns) into Layout Jig's room hatch system.
- Add Ethan's Arch-Alt-Text prompt as an MCP resource in Layout Jig's server.
- Port Ethan's `AccessibleLogger` pattern to replace Layout Jig's ad-hoc print() calls.

### Medium-term (architecture decisions needed)

- Unify TASC and Layout Jig design vocabulary into a shared command set. Challenge: TASC uses Click, Layout Jig uses stdlib. One would need to adopt the other's pattern.
- Add Layout Jig's TTS system to TACT's pipeline (announce conversion progress and results).
- Implement Ethan's hooks/learning pattern for Layout Jig's MCP server.
- Add TACT's density management to Layout Jig's 2D print export (relevant when printing to swell paper).

### Long-term (convergence)

- Single unified CLI that handles both design authoring (Layout Jig) and image conversion (TACT), with shared standards, shared MCP server, shared accessibility infrastructure.
- Shared state format where designs and converted images can reference each other (e.g., "overlay this PIAF plan at bay A").
- The physical round-trip: design in CLI → PIAF print → physical review on pegboard → camera digitization → feed back into tool.
