# CLAUDE.md — Radical Accessibility Project

## Taxonomy (use these terms consistently)

- **Tool** — a major capability module. Layout Jig, Image Describer, Tactile Printer, TACT, Rhino Viewer.
- **Command** — an individual action within a tool. `set bay A rotation 30`, `wall A on`, `describe image.jpg`.
- **Skill** — a saved sequence of commands, replayable with parameters. Stored as JSON in `controller/skills/`.
- **MCP function** — a Model Context Protocol entry point that Claude calls. Maps to one or more commands. The MCP protocol uses the word "tool" for these; in project conversation, prefer "MCP function" to avoid confusion with our tools.

When writing docs, CLI output, or code comments, use these terms precisely. "Tool" never means a saved macro. "Skill" never means a whole capability module.

---

## First-Time Setup

If `controller/state.json` does not exist, this is a fresh clone. Run:

    python setup.py

This installs all dependencies (mcp, tact, easyocr), creates `.mcp.json`,
and initializes `state.json`. The MCP servers will be available immediately
after setup completes.

No API keys needed — MCP servers run through the Claude Code subscription.

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
- **Exception:** `tools/tact/` and `mcp/` are allowed pip dependencies. The controller itself stays stdlib-only.

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

## Controller Extensions

The Layout Jig controller (`controller/controller_cli.py`) includes zone, grid, and export commands for site-scale planning. Zone commands (`zone add`, `zone remove`, `zone list`, `zone describe`) manage named program zones. Grid commands (`grid set`, `grid describe`) manage structural grid overlays. Export commands (`export 3dm`, `export text`, `export piaf`) output the model in multiple formats. These are built into the controller.

## Advanced Tactile Tools

### TACT -- Tactile Conversion CLI (tools/tact/)

Converts architectural images to PIAF-ready tactile PDFs with EasyOCR text detection, RainbowTact color-to-tactile patterns, 10 presets, auto-scaling, and abbreviation keys. Grade 2 Braille output via liblouis. Also renders state.json directly to tactile PDF via `tact render`.

Key commands:
- `tact convert IMAGE --preset NAME --verbose` -- convert one image
- `tact convert IMAGE --detect-text --braille-grade 2 --verbose` -- with Braille
- `tact render STATE.json --output OUTPUT.pdf` -- render state.json to tactile PDF
- `tact presets` -- show available presets

Install: `pip install -e tools/tact`

MCP server: `python tools/tact/mcp_entry.py` (7 MCP functions: image_to_piaf, list_presets, analyze_image, describe_image, extract_text_with_vision, assess_tactile_quality, state_to_piaf)

## Screen Reader Integration

### acclaude -- Accessible Claude Client (tools/accessible-client/)

JAWS/NVDA-compatible wrapper around Claude Code that bypasses the Ink TUI. Uses `claude -p` headless mode with `--resume SESSION_ID` for multi-turn conversations.

Requires: Node.js 18+, npx tsx

### Screen Reader Hooks (tools/screen-reader-hooks/)

Claude Code lifecycle hooks for JAWS/NVDA announcements. Includes WSL2-to-PowerShell bridge for JAWS TTS via JFWSayString API. Hooks: ImageDetector (auto-detect architectural images), ConversionTracker (record conversion settings), FeedbackCapture (capture student ratings).

---

## RhinoScript Quick Reference (IronPython 2.7)

Use this reference FIRST before calling `get_rhinoscript_docs`. Only look up docs for functions not listed here.

### Object Creation
- `rs.AddPoint(x, y, z)` → guid
- `rs.AddLine([x1,y1,z1], [x2,y2,z2])` → guid
- `rs.AddPolyline([[x1,y1,z1], [x2,y2,z2], ...])` → guid (close by repeating first point)
- `rs.AddCircle([cx,cy,cz], radius)` → guid
- `rs.AddArc3Pt([x1,y1,z1], [x2,y2,z2], [x3,y3,z3])` → guid
- `rs.AddRectangle(rs.WorldXYPlane(), width, height)` → guid
- `rs.AddSphere([cx,cy,cz], radius)` → guid
- `rs.AddBox([corners_8_points])` → guid
- `rs.AddCylinder([base_x,base_y,base_z], height, radius)` → guid (or use center+axis form)
- `rs.AddSrfPt([[p1],[p2],[p3],[p4]])` → guid (surface from 3-4 points)
- `rs.AddPlanarSrf([curve_id])` → [guid] (planar surface from closed curve)
- `rs.AddLoftSrf([curve_id_1, curve_id_2, ...])` → [guid]
- `rs.ExtrudeCurveStraight(curve_id, [start], [end])` → guid
- `rs.AddText("text", [x,y,z], height)` → guid
- `rs.AddHatch(curve_id, "Solid")` → guid (hatch patterns: Solid, Grid, Hatch1, etc.)

### Object Queries
- `rs.ObjectName(guid)` → string (get name)
- `rs.ObjectName(guid, "new_name")` → sets name
- `rs.ObjectLayer(guid)` → string (get layer)
- `rs.ObjectLayer(guid, "layer_name")` → sets layer
- `rs.ObjectType(guid)` → int (1=point, 4=curve, 8=surface, 16=polysurface, 32=mesh, 131072=hatch, 262144=extrusion)
- `rs.ObjectsByLayer("layer_name")` → [guid, ...]
- `rs.BoundingBox(guid)` → [8 points] (corners of axis-aligned box; [0]=min, [6]=max)
- `rs.CurveLength(curve_id)` → float
- `rs.SurfaceArea(surface_id)` → (area, error_bound)
- `rs.IsObject(guid)` → bool
- `rs.IsCurve(guid)` → bool
- `rs.IsSurface(guid)` → bool

### Object Transforms
- `rs.MoveObject(guid, [dx,dy,dz])` → guid
- `rs.MoveObjects([guid,...], [dx,dy,dz])` → count
- `rs.RotateObject(guid, [cx,cy,cz], angle_degrees)` → guid (rotates in XY plane)
- `rs.RotateObject(guid, [cx,cy,cz], angle, [axis_x,axis_y,axis_z])` → guid (3D axis)
- `rs.ScaleObject(guid, [cx,cy,cz], [sx,sy,sz])` → guid
- `rs.CopyObject(guid, [dx,dy,dz])` → new_guid
- `rs.MirrorObject(guid, [start_pt], [end_pt])` → new_guid
- `rs.DeleteObject(guid)` → bool
- `rs.DeleteObjects([guid,...])` → count

### Layers
- `rs.AddLayer("name")` → string
- `rs.DeleteLayer("name")` → bool
- `rs.CurrentLayer()` → string
- `rs.CurrentLayer("name")` → sets current
- `rs.IsLayer("name")` → bool
- `rs.LayerVisible("name", True/False)` → sets visibility

### UserText (metadata on objects)
- `rs.SetUserText(guid, "key", "value")` → sets
- `rs.GetUserText(guid, "key")` → string
- `rs.GetUserText(guid)` → [key, ...] (all keys)

### Selection
- `rs.SelectedObjects()` → [guid, ...]
- `rs.SelectObject(guid)` → guid
- `rs.UnselectAllObjects()` → count

### View
- `rs.ZoomExtents()` → zooms to fit all
- `rs.ZoomBoundingBox(bbox)` → zooms to box
- `rs.Redraw()` → forces viewport refresh
- `rs.EnableRedraw(True/False)` → batch mode

### Booleans & Advanced
- `rs.BooleanUnion([guid1, guid2])` → [guid]
- `rs.BooleanDifference([guid_a], [guid_b])` → [guid]
- `rs.BooleanIntersection([guid_a], [guid_b])` → [guid]
- `rs.OffsetCurve(curve_id, [direction_pt], distance)` → [guid]
- `rs.TrimCurve(curve_id, [domain_start, domain_end])` → guid
- `rs.SplitBrep(brep_id, cutter_id)` → [guid, ...]
- `rs.ProjectCurveToSurface([curve], [surface], [direction])` → [guid]

### Important Notes
- IronPython 2.7: use `.format()` not f-strings
- All coordinates are `[x, y, z]` lists
- All angles in degrees (not radians) for rs functions
- `rs.WorldXYPlane()` returns the XY construction plane at origin
- Many functions accept either a single guid or a list
- Use `import rhinoscriptsyntax as rs` at the top of every script
