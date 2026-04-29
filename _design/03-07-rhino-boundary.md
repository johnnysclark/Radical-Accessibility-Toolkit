# 03-07 — Rhino Boundary

## The hard constraint

Rhino's scripting runtime is IronPython 2.7. The controller is Python 3. These are separate processes with no shared memory, no import path, and no compatible IPC beyond the filesystem. The boundary between them is not an architectural choice — it is a hard runtime constraint. Any design for the Rhino integration must work within it.

---

## What crosses the boundary

**Into Rhino (controller → watcher):**
- `state.json` — the state file, read by the watcher via `os.path.getmtime()` polling. This is the only required channel.
- `pending_script.py` — a sidecar file the MCP server writes when `rhino_script()` is called. The watcher executes it on the next idle tick and deletes it. This is the escape hatch for geometry operations the state model doesn't express.

**Out of Rhino (watcher → controller/MCP):**
- `object_inventory.json` — written by the watcher after each full rebuild. Lists every Rhino object by semantic ID, layer, and bounding box. Used by the Model Navigator in the web UI. This is the only safe read-back channel because it is written after a complete rebuild, not during one.

**What must never cross:**
- Rhino GUIDs. They are assigned by Rhino at object creation and become stale after every full rebuild. Any system that holds GUIDs across rebuilds (e.g. the current `pending_edits.json` pattern) will silently operate on the wrong objects. GUIDs are Rhino-internal; they are not stable IDs.
- Writes back to `state.json` from the watcher. The watcher is read-only on the state file, always. If a Rhino operation needs to record a result, it writes to `object_inventory.json` or a dedicated sidecar — never to state.

---

## The generalized watcher pattern

The Rhino watcher is an instance of the Renderer abstraction (section 03-02). Its contract:

```
Inputs:   state.json  (reads schema version + domain content)
Trigger:  mtime poll on state.json (every 0.5s on Rhino idle)
Action:   clear all JIG-tagged objects; rebuild from state; write inventory
Output:   object_inventory.json
```

The full-clear-then-rebuild approach is intentional: it guarantees that Rhino geometry is always a pure function of `state.json`. Incremental rebuild would be faster but introduces diff-state that can diverge from truth. Correctness over speed at this boundary.

Any geometry engine that can implement this contract — read a state file, translate semantic objects to geometry, write an inventory — is a valid Renderer. Rhino is the current implementation, not the only possible one.

---

## What to cut in the rewrite

- **The 15-step draw list** (`site`, `grid`, `zones`, `bays`, `columns`, …) is Layout Jig–specific. The generalized watcher should iterate over whatever object types the domain schema defines, dispatching to per-type draw functions. Adding a new object type means adding a draw function and a schema entry, not modifying the watcher's main loop.
- **`startup.py` wiping `state.json`** on every Rhino launch. This silently destroys in-progress work. Remove it; let `state.json` persist across Rhino restarts.
- **GUID-based `pending_edits.json`** pattern. GUIDs go stale on rebuild. Replace with semantic-ID-based edits routed through the command dispatcher instead.
- **Braille legend logic** duplicated between `rhino_watcher.py` and `tactile_print.py`. One implementation, called by both.
- **Audio chimes hardcoded in the watcher.** Move to the hook system (section 03-02) so they fire on command completion, not on Rhino rebuild, and can be disabled without touching watcher code.
