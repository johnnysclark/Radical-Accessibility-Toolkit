# CLAUDE.md — Radical Accessibility Project

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

### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- CLI commands: short lowercase words, space-separated (`set bay A rotation 30`)
- JSON keys: `snake_case`
- Tool folders: `kebab-case`
- Rhino layers: `JIG::<Category>` (PascalCase category)
