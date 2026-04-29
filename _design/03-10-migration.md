# 03-10 — Migration Sketch

A rough sequence for getting from the current codebase to the target architecture. Not a full plan — a phased sketch with risks called out. Each phase should leave the system working at the end; no phase should require a big-bang cutover.

---

## Phase A — Extract the dispatcher core (low risk)

Pull `apply_command`, `_atomic_write`, `load_state`, and the undo stack out of `controller_cli.py` into a standalone `dispatcher.py` module. The REPL and the MCP server both import from it. No behavior changes — this is a pure extraction.

**Risk:** `auditor.py` imports `controller_cli` directly. Fix the circular dependency at this step by making `auditor.py` import from `dispatcher.py` instead.

**Exit state:** `controller_cli.py` is a thin REPL shell. The dispatcher is independently importable and testable.

---

## Phase B — Introduce the hook registry (low risk)

Add a hook registry to the dispatcher. Move TTS announcement and Bambu/STL auto-export out of `main()`'s save loop and into registered hooks. The observable behavior is identical; the coupling is gone.

**Risk:** low. These are side effects with no return values; the move is mechanical.

**Exit state:** the mutation path has no side effects. All post-command behavior is in hooks.

---

## Phase C — Formalize the state schema (medium risk)

Define `"schema"` and `"domain_type"` as required root fields. Write a migration function for existing `state.json` files that lack them. Add `supports_schema()` checks to the Rhino watcher and TACT renderer.

**Risk:** existing `state.json` files may have unexpected shapes from historical drift. The migration function must handle all known historical versions. Test against the three historical schemas identified in the controller.

**Exit state:** every `state.json` is version-tagged. Schema migration runs on every load. Renderers refuse gracefully on unknown schema versions.

---

## Phase D — Decouple output channels (medium risk)

Refactor `state_renderer.py` to read only the domain envelope rather than hardcoded Layout Jig keys. Remove the `os.path.join("..")` controller import; route Braille through a shared module. Remove TASC's duplicate rasterization pipeline; have it call TACT's render function. Route the image describer through the provider layer.

**Risk:** TACT's state renderer is 1633 lines with Layout Jig assumptions throughout. Key-by-key replacement, not a rewrite. Tests before and after are essential.

**Exit state:** output channels depend on the schema contract, not on controller internals.

---

## Phase E — Slim the MCP surface (medium risk)

Remove the ~20 domain-specific wrapper functions from the MCP server. Verify that every removed function's behavior is reachable via `run_command`. Update any agent prompts or SKILL.md files that reference removed function names.

**Risk:** existing sessions or saved scripts may call removed function names. Provide a deprecation period where removed functions delegate to `run_command` with a logged warning.

**Exit state:** MCP surface is ~15 functions. The server is under 500 lines.

---

## Phase F — Generalize the Rhino watcher (higher risk)

Replace the 15-step draw list with a dispatch table keyed on domain object type. Remove the `startup.py` state wipe. Replace GUID-based `pending_edits.json` with semantic-ID edits routed through the command dispatcher.

**Risk:** the watcher is IronPython 2.7 with no test harness. Any regression requires running Rhino to observe. Build a minimal fixture-based test before touching the draw loop.

**Exit state:** the watcher iterates over domain object types defined in the schema; adding a new type requires no watcher changes.

---

## Risks not tied to a specific phase

- The co-designer uses the system daily. No phase should break the CLI REPL for more than one session.
- `controller_cli.py` has no unit tests. Phases A–C need tests written before refactoring begins.
- IronPython 2.7 and Python 3 must stay compatible at the file boundary throughout. Never introduce a Python 3–only JSON feature into the state format.
