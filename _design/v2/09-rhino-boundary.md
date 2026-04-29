# Rhino Boundary

## The hard runtime constraint

Rhino's scripting runtime is IronPython 2.7. The controller is Python 3. These are separate processes with no shared memory, no import path, and no IPC beyond the filesystem. This is not an architectural choice — it is a hard runtime constraint imposed by Rhino. Any design for the Rhino integration must work within it.

The watcher script (`renderer/rhino/watcher.py`) runs inside Rhino under IronPython 2.7. It must use `.format()` instead of f-strings. It must use `os.path` instead of `pathlib`. It must not import anything from the `rap/` Python 3 package.

---

## What crosses the boundary

**Into Rhino:**
- `state.json` — read by the watcher via `os.path.getmtime()` polling every 0.5 seconds on `Rhino.RhinoApp.Idle`. This is the only required inbound channel.
- `pending_script.py` — a sidecar file written by the MCP `rhino_script()` function. The watcher executes it on the next idle tick and deletes it. This is the escape hatch for geometry operations the state model does not express.

**Out of Rhino:**
- `object_inventory.json` — written by the watcher after each full rebuild. Lists every geometry object by its semantic ID (see Data Contracts). This is the only safe outbound channel. It is written only after a complete rebuild, never during one.

**Never cross the boundary:**
- Rhino GUIDs. They are assigned by Rhino at object creation and become stale after every full rebuild. Nothing outside the watcher should hold a GUID.
- Writes back to `state.json` from the watcher. The watcher is read-only on the state file, always.

---

## Watcher implementation

The watcher is a Renderer (section: Core Abstractions). Its contract:

```
Inputs:   state.json  (reads schema version + domain content)
Trigger:  mtime poll on state.json, every 0.5s on Rhino.RhinoApp.Idle
Action:   delete all JIG-tagged objects; rebuild from state; write inventory
Output:   object_inventory.json
```

Full-clear-then-rebuild on every detected change. This guarantees Rhino geometry is always a pure function of `state.json`. Incremental rebuild would be faster but introduces diff-state that can diverge.

All `rhinoscriptsyntax` calls must happen on the Rhino idle event thread. Do not call `rs.*` functions from any other thread — `rhinoscriptsyntax` is not thread-safe.

---

## How the watcher handles domain objects

The watcher does not hardcode a list of object types. It dispatches by object type using a registry:

```python
# renderer/rhino/draw.py (IronPython 2.7)
DRAW_REGISTRY = {}  # object_type -> draw function

def register_draw(object_type, fn):
    DRAW_REGISTRY[object_type] = fn

def draw_all(state):
    domain = state.get("domain", {})
    for object_type, items in domain.items():
        fn = DRAW_REGISTRY.get(object_type)
        if fn:
            for item in items:
                fn(item, state)
```

Adding a new geometry type means registering a draw function — not modifying the watcher loop.

---

## Implementation requirements

- Tag every created Rhino object with `JIG_OWNER`, `JIG_ID`, and `JIG_SCHEMA` UserText keys. The watcher deletes objects by `JIG_OWNER` tag on rebuild.
- Apply per-object `_local_to_world(origin, rotation)` coordinate transforms, not global transforms. Each domain object carries its own origin and rotation.
- `state.json` must not be wiped or modified by the Rhino startup script. The state file persists across Rhino restarts.
- Do not implement GUID-based edit queuing. Edits from external sources go through the command dispatcher and produce a new `state.json` write; the watcher picks up the change on the next poll.
