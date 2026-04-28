---
# 01 — Rhino Watcher + JSON Contracts subsystem

## Purpose
Watches `controller/state.json` and fully rebuilds Rhino geometry on every write. Keeps Rhino as a crash-safe, read-only consumer so the user's work lives in the JSON file, not Rhino's memory.

## Public API / entry points
- `state.json` top-level keys consumed: `site`, `bays`, `zones`, `rooms`, `grid`, `corridors`, `voids`, `blocks`, `style`, `legend`, `tactile3d`
- Each bay carries: `bays` (grid dims), `spacing`/`spacing_x`/`spacing_y`, `origin`, `rotation`, `apertures`, `walls`, `z_order`
- `start_watcher()` — hooks `Rhino.RhinoApp.Idle`; polls mtime every 0.5 s
- `redraw(state)` — clears JIG layers, runs 15 ordered draw steps, caches stats, exports inventory
- `_export_inventory(state)` — writes `object_inventory.json` for the Model Navigator
- `_apply_pending_edits()` — reads `pending_edits.json` on the main thread; supports move, rotate, scale, delete, rename, layer
- `_run_pending_script()` — executes `pending_script.py` on the main thread; `RhinoBridge` (`rhino_client.py`) is the Python 3 TCP client on port 1998

## Dependencies
- IronPython 2.7 with `rhinoscriptsyntax` and `Rhino`/`scriptcontext`
- `startup.py` loads the watcher via `exec()`, starts RhinoMCP, sets LightPen display mode, sets feet units
- Reads `controller/state.json`; side-channel files `object_inventory.json`, `pending_edits.json`, `pending_script.py` sit alongside it
- Windows PowerShell subprocess for audio chime/TTS

## What's essential
- Full-clear-then-rebuild on every change; determinism requires no incremental diff
- `_local_to_world()` coordinate transform (origin + rotation) applied per bay
- `JIG_*` layer naming and `JIG_OWNER`/`JIG_ID` UserText tags on every object
- Main-thread safety: all `rs.*` calls must run on the Rhino idle event

## What's accidental
- Audio feedback is Layout Jig-specific; could be a generic accessibility hook
- 15 draw-step list is tightly coupled to the Layout Jig domain
- Braille legend rendering is duplicated between `rhino_watcher.py` and `tactile_print.py`
- `_apply_pending_edits()` uses GUIDs that become stale after any full rebuild
- `startup.py` silently resets `state.json` to blank on every Rhino launch
- TCP listener is disabled because IronPython's `rhinoscriptsyntax` is not thread-safe
---
