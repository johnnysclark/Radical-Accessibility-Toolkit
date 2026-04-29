# Implementation Sequence

Build in this order. Each phase produces a working system at the end; no phase requires everything else to be done first.

---

## Phase A — Core dispatcher (no dependencies)

Build `rap/core/dispatcher.py`, `rap/core/schema.py`, and `rap/core/hooks.py`. Implement `apply_command`, `load_state`, `_atomic_write`, the undo stack, and the hook registry. Write tests that run purely against JSON files with no Rhino, no MCP, no renderer. This is the foundation everything else builds on.

Define the state envelope schema (`schema`, `domain_type`, `meta`, `domain`). Write the first migration function (v1.0 → v2.0).

**Done when:** `apply_command` dispatches to a stub handler, writes state atomically, fires hooks, and returns `OK: ... READY:`. Tests pass.

---

## Phase B — CLI REPL

Build `rap/cli/repl.py` — the readline input loop that calls `apply_command`. Add `help`, `undo`, `quit`, and `describe` as built-ins. This makes the system usable by a human before any other component exists.

**Done when:** a developer can run `python -m rap.cli.repl` and issue commands in a terminal, with confirmations printed to stdout.

---

## Phase C — First domain module

Build `rap/domain/layout_jig/`. Implement the schema (bays, walls, rooms, corridors, zones, grid) and the command handlers. Register them with the dispatcher. Write domain-level tests.

This is the first time domain logic exists separately from infrastructure. Validate that the dispatcher is genuinely unmodified by adding domain commands.

**Done when:** all Layout Jig commands work in the CLI REPL. Domain tests pass without importing any renderer or MCP code.

---

## Phase D — MCP server

Build `rap/mcp/server.py`. Implement the 14 core functions. Wire `run_command` to `apply_command`. Implement `get_state`, `describe`, `undo`, `save_snapshot`, `load_snapshot`, `run_macro`, `load_template`.

Leave Group 3 (Rhino bridge) and Group 4 (AI output) as stubs returning `ERROR: not implemented` until the corresponding components exist.

**Done when:** an MCP host can connect and issue `run_command("add bay A")`, receiving a proper `OK:` response.

---

## Phase E — Provider layer and AI output

Build `rap/provider/`. Implement `AnthropicProvider`, `OpenAIProvider`, `NullProvider`. Wire the provider into the Group 4 MCP functions (`describe_image`, `convert_to_tactile`, `render_tactile`, `audit`).

Build `renderer/tact/pdf.py` and `renderer/tact/image.py`. Build `renderer/text/describe.py` and `renderer/text/audit.py`.

**Done when:** `render_tactile` produces a valid PDF from a `state.json`. All provider tests pass with `NullProvider`.

---

## Phase F — Rhino watcher

Build `renderer/rhino/watcher.py` (IronPython 2.7). Implement the mtime poll loop, the draw registry, per-object draw functions for the Layout Jig domain, and `object_inventory.json` export.

Test by running Rhino with a real `state.json` and verifying geometry rebuilds correctly on each write.

**Done when:** Rhino geometry rebuilds deterministically from `state.json`. `object_inventory.json` is written after each rebuild with correct semantic IDs.

---

## What to validate at the end

Run this sequence manually or as an integration test:

1. Start the CLI REPL. Issue several Layout Jig commands. Verify each returns `OK: ... READY:`.
2. Issue `undo`. Verify the previous state is restored.
3. Connect an MCP host. Issue `run_command("add bay B")` via MCP. Verify `get_state()` reflects the change.
4. Call `render_tactile(output_path="out.pdf")`. Open the PDF. Verify it shows the current design.
5. Start Rhino with the watcher. Issue a command via the CLI. Verify Rhino geometry updates within one second.
6. Kill Rhino. Issue a command. Verify `state.json` is updated and the CLI is unaffected.
