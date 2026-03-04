# CLAUDE.md — Radical Accessibility Project

## Taxonomy (use these terms consistently)

- **Tool** — a major capability module. Layout Jig, Image Describer, Tactile Printer, Rhino Viewer.
- **Command** — an individual action within a tool. `set bay A rotation 30`, `wall A on`, `describe image.jpg`.
- **Skill** — a saved sequence of commands, replayable with parameters. Stored as JSON in `controller/skills/`.
- **MCP function** — a Model Context Protocol entry point that Claude calls. Maps to one or more commands. The MCP protocol uses the word "tool" for these; in project conversation, prefer "MCP function" to avoid confusion with our tools.

When writing docs, CLI output, or code comments, use these terms precisely. "Tool" never means a saved macro. "Skill" never means a whole capability module.

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
- **Zero external dependencies** in `controller/`. Python stdlib only. No pip installs, no conda environments.
- **Exception:** `tools/swell-print/` and `mcp/` are allowed pip dependencies (Pillow, reportlab, mcp). The controller itself stays stdlib-only.

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

## Student Extensions (Ethan Anderson)

The following tools extend the project with advanced tactile conversion, accessible Rhino design, and screen reader integration.

### TACT -- Tactile Conversion CLI (tools/tact/)

Converts architectural images to PIAF-ready tactile PDFs. More advanced than tools/swell-print/ with EasyOCR text detection, RainbowTact color-to-tactile patterns, 10 presets, auto-scaling, and abbreviation keys.

Key commands:
- `tact convert IMAGE --preset NAME --verbose` -- convert one image
- `tact convert IMAGE --detect-text --braille-grade 2 --verbose` -- with Braille
- `tact presets` -- show available presets

Install: `pip install -e tools/tact`

MCP server: `python tools/tact/mcp_entry.py` (6 tools: image_to_piaf, list_presets, analyze_image, describe_image, extract_text_with_vision, assess_tactile_quality)

### TASC -- Tactile Architecture Scripting Console (tools/tasc/)

Accessible programmatic Rhino design via text commands. Complementary to the Layout Jig -- TASC focuses on site planning (zones, bays, corridors) with live MCP socket connection to Rhino.

Key commands:
- `tasc site W D` -- site boundary
- `tasc zone NAME W D --at X,Y` -- program zone
- `tasc bay NAME NxN --spacing SX SY --at X,Y` -- structural bay
- `tasc describe` -- full text description
- `tasc export piaf|3dm|text` -- export

Install: `pip install -e tools/tact && pip install -e tools/tasc` (tasc depends on tact)

### acclaude -- Accessible Claude Client (tools/accessible-client/)

JAWS/NVDA-compatible wrapper around Claude Code that bypasses the Ink TUI. Uses `claude -p` headless mode with `--resume SESSION_ID` for multi-turn conversations.

Requires: Node.js, npx tsx

### Screen Reader Hooks (tools/screen-reader-hooks/)

Claude Code lifecycle hooks for JAWS/NVDA announcements. Includes WSL2-to-PowerShell bridge for JAWS TTS via JFWSayString API.
