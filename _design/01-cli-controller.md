---
# 01 — CLI / Controller subsystem

## Purpose
The controller is a Python 3 REPL that mutates a single `state.json` file, the sole source of truth for the layout model. It exists to keep Rhino out of the command path — the watcher reads the file; the controller never calls Rhino directly.

## Public API / entry points
- CLI entry: `python controller/controller_cli.py [--state path]`
- REPL loop: `apply_command(state, tokens, state_file)` dispatches all commands
- Command groups: `set bay|site|column|style|print`, `wall`, `aperture`, `room`, `cell`, `corridor`, `block`, `hatch`, `legend`, `zone`, `grid`, `export`, `template`, `style`, `view`, `section`, `tactile3d`, `bambu`, `tts`, `history`, `snapshot`, `setup`
- Built-ins: `undo`, `describe`, `list`, `status`, `print`, `help`, `quit`
- `auditor.py` and `macro_manager.py` are library modules callable by external agents

## Dependencies
- Stdlib: `argparse`, `copy`, `json`, `math`, `os`, `subprocess`, `sys`, `time`, `datetime`, `socket`
- Optional intra-controller: `template_manager`, `style_manager`, `braille`, `exporter`, `macro_manager`, `auditor` (try/import guarded)
- Optional external: `tactile_print` from `tools/rhino`, path-loaded at runtime
- No pip dependencies in `controller/`; pip is confined to `tools/` and `mcp/`

## What's essential
- `apply_command` as the single dispatch point — all mutations pass through here, allowing uniform undo, save, and history
- `_atomic_write` for crash-safe file saves — controller correctness depends on no partial writes
- `copy.deepcopy` undo stack — in-memory undo before every mutation; state is always recoverable
- Schema migration on load — old `state.json` files must upgrade silently without breaking the REPL

## What's accidental
- `controller_cli.py` is 3135 lines; bay, wall, room, corridor, zone, and grid logic are all inlined rather than split into modules
- `_default_bay`, `_auto_rooms`, `_init_cells`, and cell-math helpers encode Layout Jig geometry not reusable by other tools
- Braille fallback (A/B/C hardcoded in `_default_bay`) should be delegated entirely to `braille.py`
- `auditor.py` imports `controller_cli as cli`; the dependency becomes circular if `controller_cli` ever imports `auditor`
- `macro_manager.py` exists but `apply_command` has no `macro` branch — the module is disconnected from the REPL
- TTS and Bambu/STL auto-export are wired into `main()`'s save loop, coupling side-effects to the mutation path
---
