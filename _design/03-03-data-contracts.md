# 03-03 — Data Contracts

Four seams in the architecture carry data across module boundaries. Each needs a defined shape. These are sketches, not full specs — field names and types are illustrative; the implementing team fixes the details.

---

## 1. State envelope (state.json root)

```json
{
  "schema": "2.0",
  "meta": {
    "project": "string",
    "created": "ISO-8601",
    "modified": "ISO-8601",
    "author": "string"
  },
  "domain": { ... }
}
```

`schema` selects the migration path on load. `meta` is stable across all domain types. `domain` is the namespaced payload — its internal shape is domain-specific and versioned separately. This envelope means the general infrastructure (migration, undo, atomic write, renderer trigger) never needs to parse domain content.

**Open question:** Should `domain` be a single object or a map of named domains (e.g. `{ "layout_jig": {...}, "site": {...} }`)? Single is simpler; multi-domain supports composite designs. See 03-09.

---

## 2. Command invocation and result

```
invocation:  { "command": "string", "args": { ... } }
result:      "OK: <one-line summary of what changed>"
           | "ERROR: <reason>"
```

The result is always a plain string with an `OK:` or `ERROR:` prefix — no JSON, no structured object. This is load-bearing for screen reader compatibility: the output must be readable by speech synthesis without parsing. The command name and args dict are logged to history regardless of success or failure.

`undo` is not a command in the domain sense — it is a dispatcher-level operation that restores the previous snapshot and returns `OK: undone <command-name>`.

---

## 3. Hook payload

```json
{
  "command": "string",
  "args": { ... },
  "result": "OK: ...",
  "elapsed_ms": 42,
  "state_path": "/path/to/state.json"
}
```

Hooks receive the command name, args, result string, timing, and the path to the now-current state file. Hooks do not receive the before-state or after-state objects in memory — they read from disk if they need the content. This keeps hook implementations independent of the dispatcher's memory model and prevents hooks from accidentally mutating state.

**Open question:** Should hooks be synchronous (blocking the REPL until they complete) or async (fire-and-forget)? TTS needs to be fast; export triggers can be slow. See 03-09.

---

## 4. Renderer trigger

```json
{
  "event": "state_changed",
  "state_path": "/path/to/state.json",
  "schema": "2.0",
  "command": "string"
}
```

The current architecture uses file mtime polling (the Rhino watcher checks every 0.5s). The trigger contract above is the shape a push-based alternative would carry — the dispatcher writes this to a sidecar file or sends it over a socket after each atomic write.

The trigger includes `command` so renderers can skip rebuilds for commands that don't affect their domain (e.g. a TTS-only command need not trigger a Rhino rebuild).

**Open question:** Push signal vs. mtime polling. Push is lower latency and more precise; mtime polling requires no IPC and works across language runtimes (critical for IronPython). The Rhino watcher's IronPython constraint likely forces mtime polling at that boundary regardless. See 03-09.

---

## Migration contract

Every schema version `N` must have a migration function `migrate_N_to_N1(doc) -> doc`. Migrations run eagerly on `load_state`. A document at the current schema version passes through unchanged. Migrations must be pure functions — no I/O, no side effects.
