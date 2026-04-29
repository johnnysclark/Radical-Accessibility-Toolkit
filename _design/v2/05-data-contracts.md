# Data Contracts

Four seams in the architecture carry data across module boundaries. Each has a defined shape.

---

## 1. State envelope (state.json root)

```json
{
  "schema": "2.0",
  "domain_type": "layout_jig",
  "meta": {
    "project": "string",
    "created": "ISO-8601",
    "modified": "ISO-8601",
    "author": "string"
  },
  "domain": { }
}
```

`schema` selects the migration path on load. `domain_type` identifies the domain so renderers can confirm compatibility before parsing. `meta` is stable across all domain types. `domain` is the namespaced payload — its internal shape is domain-specific and versioned separately from the envelope.

The general infrastructure (migration, undo, atomic write, renderer trigger) operates only on the envelope fields. It never parses `domain` content.

**Migration contract.** Every schema version `N` has a function `migrate_N_to_next(doc) -> doc`. Migrations run eagerly in `load_state`. They are pure functions — no I/O, no side effects. A document already at the current version passes through unchanged.

---

## 2. Command invocation and result

```
invocation:  tokens: list[str]  (e.g. ["add", "bay", "A", "--spacing", "6"])
result:      "OK: <one-line summary of what changed>"
           | "ERROR: <reason>"
```

The result is always a plain string with an `OK:` or `ERROR:` prefix — no JSON, no structured object. This is load-bearing for screen reader compatibility: the output is read by speech synthesis without parsing. The dispatcher appends `READY:` on a new line after every result so agents and screen readers detect turn completion.

The command name and tokens are logged to a history list in state regardless of success or failure.

`undo` is a dispatcher-level operation, not a domain command. It pops the undo stack, overwrites state on disk, and returns `OK: undone <command-name> READY:`.

---

## 3. Hook payload

```json
{
  "command": "string",
  "args": { },
  "result": "OK: ...",
  "elapsed_ms": 42,
  "state_path": "/abs/path/to/state.json"
}
```

Hooks receive the command name, parsed args dict, result string, timing, and the absolute path to the now-current state file. Hooks do not receive in-memory state objects — they read from disk if they need content. This keeps hook implementations independent of the dispatcher's memory model and prevents hooks from accidentally mutating state.

Hook execution order: hooks registered first fire first. If a hook raises an exception, subsequent hooks still fire; the exception is logged but does not affect the dispatcher's response.

---

## 4. Renderer trigger

The primary trigger mechanism is filesystem mtime polling: the renderer checks `os.path.getmtime(state_path)` on a timer and rebuilds when the mtime advances. This is the only mechanism that works reliably across Python 3 and IronPython 2.7 (the Rhino scripting runtime) without IPC.

For Python 3 renderers that want richer signal, the dispatcher optionally writes a sidecar trigger file after each atomic write:

```json
{
  "event": "state_changed",
  "state_path": "/abs/path/to/state.json",
  "schema": "2.0",
  "domain_type": "layout_jig",
  "command": "add bay A"
}
```

The `command` field lets renderers skip rebuilds for mutations that don't affect their domain. The sidecar is written atomically alongside `state.json` and deleted after the renderer consumes it.

---

## 5. Object inventory (Rhino → controller)

After each full Rhino rebuild, the watcher writes:

```json
{
  "generated_at": "ISO-8601",
  "objects": [
    {
      "semantic_id": "bay_A_column_0_0",
      "domain_type": "layout_jig",
      "object_type": "column",
      "layer": "JIG::Columns",
      "bbox": [[x1,y1,z1],[x2,y2,z2]]
    }
  ]
}
```

This is the only read-back channel from Rhino. Semantic IDs are stable across rebuilds; Rhino GUIDs are not included.
