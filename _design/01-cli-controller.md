---
# 01 — CLI / Controller subsystem

## Purpose
The controller is a Python 3 REPL that mutates `state.json`, the sole source of truth for the layout model. It exists to keep Rhino out of the command path — the watcher reads the file; the controller never calls Rhino directly.

## Public API / entry points
- CLI entry: `python controller/controller_cli.py [--state path]`
- REPL loop: `apply_command(state, tokens, state_file)` dispatches all commands
- Command groups: `set` (bay/site/column/style/print), `wall`, `aperture`, `room`, `cell`, `corridor`, `block`, `hatch`, `legend`, `zone`, `grid`, `export`, `template`, `style`, `view`, `section`, `tactile3d`, `bambu`, `tts`, `history`, `snapshot`
- Built-ins: `undo`, `describe`, `list`, `status`, `print`, `help`, `quit`
- `auditor.py` and `macro_manager.py` are library modules for external callers

## Dependencies
- Stdlib: `argparse`, `copy`, `json`, `math`, `os`, `subprocess`, `sys`, `time`
- Optional intra-controller: `template_manager`, `style_manager`, `braille`, `exporter`, `macro_manager` (try-guarded)
- Optional external: `tactile_print` from `tools/rhino`, path-injected at runtime
- No pip dependencies in `controller/`; pip confined to `tools/` and `mcp/`

## What's essential
- `apply_command` as the single dispatch point — all mutations pass through for uniform undo, save, and history
- `_atomic_write` — crash-safe saves; correctness depends on no partial writes
- `copy.deepcopy` undo stack — pre-mutation snapshot; state is always recoverable
- Schema migration on `load_state` — old files must upgrade silently

## What's accidental
- `controller_cli.py` is 3135 lines; bay, wall, room, corridor, zone, and grid logic are all inlined in one file
- `_default_bay`, `_auto_rooms`, `_init_cells`, and cell-math helpers encode Layout Jig geometry, not reusable elsewhere
- `auditor.py` imports `controller_cli` — latent circular dependency
- `macro_manager.py` is disconnected from the REPL; `apply_command` has no `macro` branch — macros only reachable via MCP
- TTS and auto-export (Bambu/STL) wired into `main()`'s save loop, coupling side-effects to the mutation path
- View rendering helpers (`_view_plan`, `_view_section`, `_view_axon`) inlined rather than isolated in a renderer module
---
