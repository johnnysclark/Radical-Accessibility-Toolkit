# RAP Rewrite Design Document

A portable design document for a non-visual, agentic CAD design pipeline.
Any LLM can pick this up cold and implement from it.

---

## Table of Contents

1. [Conceptual Brief](#conceptual-brief)
2. [Problem and Success Criteria](#problem-and-success-criteria)
3. [Core Abstractions](#core-abstractions)
4. [Data Contracts](#data-contracts)
5. [Provider Layer](#provider-layer)
6. [MCP Surface](#mcp-surface)
7. [Agent Loop](#agent-loop)
8. [Rhino Boundary](#rhino-boundary)
9. [Output Channels](#output-channels)
10. [Open Design Questions](#open-design-questions)
11. [Migration Sketch](#migration-sketch)

---

## Conceptual Brief

## What RAP is

RAP is a non-visual, agentic CAD design pipeline. A designer — human or AI agent — issues semantic design intentions through a text interface. Those intentions are recorded in a plain-text JSON file that is the sole source of truth for the design. Downstream renderers — geometry engines, tactile print pipelines, alt-text generators — are read-only consumers of that file. Vision is never required at any stage.

RAP exists because every mainstream design tool treats sight as a prerequisite. Non-visual interaction is the primary design case here; sighted interaction is a bonus layer on top.

## Why it exists

The co-designer is a blind architecture student. His daily workflow — designing a building, reviewing it, fabricating tactile models, presenting to critics — is the test suite for every tool. A feature that can't be heard, felt, or read by a screen reader doesn't ship.

That constraint is generative rather than limiting. To make design accessible without vision, you must make design legible through language; you must separate what a thing *is* from where it appears on screen; you must make every mutation auditable and every state recoverable. These are not accommodations — they are engineering virtues the discipline should have had regardless.

## What "non-visual, agentic CAD pipeline" means in practice

Three properties define the system:

**Non-visual.** Every command has a text form. Every response has a text form. No step requires a viewport, a click, or a look. Physical output — swell-paper tactile graphics, 3D-printed models — closes the loop for users whose primary sense is touch.

**Agentic.** A language model can drive the entire pipeline: issue commands, read state, evaluate geometry, trigger output. The JSON state file is the handoff between the agent's reasoning and the geometry engine's execution. The agent does not need to know Rhino exists.

**CAD pipeline.** The system is grounded in real geometry — meter-accurate plans, structural grids, fabrication-ready exports. The design artifacts it produces go to a laser cutter, a braille embosser, or an architecture critic.

## Why this generalizes beyond one building type

The current codebase carries a large amount of accidental specificity: the Layout Jig's bay-and-wall geometry, hard-coded schema keys, inlined column math. But the underlying architecture — command dispatcher → JSON state → read-only renderers — has no inherent dependency on any of those specifics. It applies to any Rhino design task where the designer works through language rather than a viewport.

The rewrite should distill this general architecture from the specific application. A clean implementation looks like: a small command core that reads and writes a well-defined state schema; a renderer boundary that consumes the schema without knowing where it came from; and an agent-facing API surface that exposes the schema clearly enough that any LLM can drive it.

## The elegance bar

The rewrite succeeds if a new implementer — given only this document — can build a system where a blind architecture student designs, reviews, and fabricates a building without touching a mouse or screen, and where a language model can do the same with no special affordances beyond the documented API. Everything else is negotiable.

---


## Problem and Success Criteria

## What the rewrite is solving

The current codebase has a sound conceptual core — command dispatcher → JSON state → read-only renderer — buried under years of Layout Jig-specific accretion. Six specific problems motivate a rewrite rather than continued patching:

**1. Domain logic inlined into infrastructure.** `controller_cli.py` is 3135 lines. Bay geometry (`_default_bay`, `_init_cells`, `_auto_rooms`), wall logic, corridor math, and view rendering are all inlined alongside the command dispatcher and undo stack. The general mechanism (dispatch, undo, atomic write) cannot be extracted without also extracting the domain logic it is tangled with.

**2. MCP surface has grown without a shape.** The MCP server exposes 71 tool functions. Many are thin wrappers around single controller commands that could be reached via a generic `run_command` escape hatch. The 71-function surface forces any agent working with RAP to choose from a large undifferentiated menu rather than a small, principled API.

**3. Accidental coupling across modules.** `auditor.py` imports `controller_cli` (latent circular dependency). `state_renderer.py` in TACT reaches into the controller directory via five levels of `os.path.join("..")`. TASC duplicates TACT's rasterization pipeline independently. `extend_controller` writes Python source into `controller_cli.py` at runtime. These couplings make the subsystems impossible to test or replace in isolation.

**4. Schema keys are Layout Jig vocabulary.** `bays`, `walls`, `apertures`, `corridors`, `voids`, `tactile3d` are hard-coded in the watcher, the state renderer, the MCP server, and the TACT pipeline. Generalizing to any Rhino design task requires the schema to be either generic or explicitly namespaced.

**5. Side-effects are coupled to the mutation path.** TTS announcement and STL auto-export are wired into `main()`'s save loop. The Rhino watcher plays audio chimes on rebuild. These are accessibility features, but their implementation ties them to specific code paths rather than a general post-mutation hook system.

**6. No clean seam for alternative LLMs or renderers.** The MCP server assumes Claude Code as the caller. The image describer calls the Anthropic REST API directly with hardcoded model IDs. There is no abstraction boundary that lets a different LLM, a different geometry engine, or a different output channel plug in without modifying core files.

---

## Success criteria

The rewrite succeeds when:

- A new implementer can read this document and build a working system without reading the current source.
- The command dispatcher, the state schema, and the renderer boundary are each independently testable with no Rhino running.
- An AI agent using the MCP surface can design a complete architectural artifact using fewer than 15 distinct function names.
- The geometry-specific domain logic (whatever building type is being designed) lives entirely in one layer and can be replaced without touching the command dispatch or output pipeline.
- A post-mutation hook system handles TTS, export triggers, and other side effects — none are wired into the mutation path itself.
- The same JSON state file drives Rhino geometry, a tactile PDF, and a text description with no code changes between them.

## Non-goals

- Feature parity on day one. The rewrite should implement the general architecture; Layout Jig commands can be ported incrementally after the core is clean.
- Replacing Rhino. Rhino stays. The goal is a cleaner boundary at the Rhino edge, not a different geometry engine.
- A new user interface. The CLI and MCP surface are the interfaces; no GUI work is in scope.
- Backwards compatibility with existing `state.json` files. Schema migration is in scope; preserving the old schema is not.

---


## Core Abstractions

Five nouns. Everything else in the architecture is either one of these or a relationship between them.

---

## 1. State

A single JSON document on disk. It is the sole source of truth for the design at every moment. Every command reads from it and writes back to it; every renderer reads from it and never writes back. If Rhino crashes, if the agent disconnects, if the process dies mid-command, the design survives as whatever `state.json` last contained. Recoverability is not a feature — it is the defining property of this abstraction.

The state document has a `schema` version field at its root. All code that reads state must handle older versions via migration, not rejection.

---

## 2. Command

An atomic, named, text-addressable mutation of state. A command takes the current state and a set of typed arguments, applies a transformation, and returns a plain-text confirmation string. Commands are the only legal mutation path — nothing writes to state except through the command dispatcher.

Two properties follow from this: commands are trivially undoable (snapshot state before dispatch, restore on undo), and every mutation is auditable (the command name and arguments are the audit record). The command set is domain-specific — what commands exist depends on the design task — but the dispatch mechanism is domain-agnostic.

---

## 3. Schema

The versioned, documented contract that defines the shape of state. The schema is the seam between command handlers and renderers: command handlers write objects that conform to the schema; renderers read only what the schema defines. Neither side depends on implementation details of the other.

Schema changes are migrations, not breaking changes. A migration function upgrades an older document to the current version on load. The schema version field in state.json selects the right migration path. Domain-specific schemas (Layout Jig, future building types) are namespaced under the root schema so the general envelope stays stable.

---

## 4. Renderer

Any read-only consumer of state that produces an artifact. A renderer watches for state changes (by file mtime, by explicit signal, or by explicit invocation) and translates the current state into an output: Rhino geometry, a tactile PDF, a text description, a 3D print file, a braille document. A renderer never writes back to state. If a renderer crashes or is absent, the design is unaffected.

Renderers are pluggable: adding a new output format means writing a new renderer, not modifying the command layer or the schema. The only contract a renderer must honor is the schema it reads.

---

## 5. Hook

A post-mutation callback registered against the dispatch loop. After a command completes and state is saved, the dispatcher fires all registered hooks in order. A hook receives the command name, the arguments, the before-state, and the after-state. Hooks handle every side effect that is not a renderer: TTS announcement, screen reader signals, export triggers, logging, telemetry. Nothing in the mutation path itself produces side effects.

Hooks are registered at startup, not hardcoded into commands. A deployment without a screen reader simply registers no TTS hook. A deployment with Bambu auto-export registers an export hook. The command code is identical in both cases.

---

## Relationships

```
Agent
  → issues Command
    → Command mutates State (atomic write)
      → Hook fires (post-mutation, side effects only)
      → Renderer reads State (produces artifact)
Schema
  → constrains State shape
  → is honored by both Command and Renderer
```

---


## Data Contracts

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

---


## Provider Layer

RAP has two directions of LLM interaction that need to stay model-agnostic: **inbound** (an agent driving RAP via MCP) and **outbound** (RAP calling an LLM for AI-powered analysis). Both currently assume Claude. Neither should.

---

## Inbound: agents driving RAP

The MCP surface (section 03-05) is the inbound interface. MCP is a protocol, not a Claude-specific API, so any MCP-capable agent — Claude, Gemini, GPT-4o, a local model — can call RAP's tools. The inbound direction is already structurally model-agnostic.

What currently breaks that guarantee:
- The MCP server's setup documentation and `.mcp.json` reference Claude Code by name.
- Some MCP tool docstrings contain Claude-specific phrasing ("ask Claude to…").
- `extend_controller` writes Python source into the controller at runtime — a feature that assumes a Claude Code session with file-write access.

The fix is editorial and architectural: write tool docstrings in neutral terms, remove the `extend_controller` escape hatch, and treat Claude Code as one possible MCP host rather than the only one.

---

## Outbound: RAP calling an LLM

Three places in the current codebase call an LLM directly:

1. `tools/image-describer/arch_alt_text.py` — calls Anthropic REST with a hardcoded `claude-3-5-sonnet` model ID.
2. `tools/tact/src/tact/mcp_server/tools.py` — `describe_image` and `extract_text_with_vision` call the Anthropic SDK directly.
3. `image_to_piaf` accepts a `claude_text_json` parameter, making Claude both the caller and a data provider in the same request.

All three should route through a provider abstraction.

---

## The provider interface

The abstraction is minimal — RAP only needs two operations from an LLM:

```
complete(prompt: str, images: list[bytes] | None) -> str
```

A text prompt with optional image attachments; returns a plain text response. No streaming, no tool calls, no conversation history. If the use case grows, the interface grows — but start with this.

```
describe_image(image: bytes, context: str) -> str
```

A specialized form of `complete` for image description, included separately because it is called in hot paths and may benefit from a different model or caching strategy than general completions.

**What the abstraction must hide:**
- API endpoint URLs and authentication
- Model IDs and version strings
- Request/response envelope format (Anthropic vs. OpenAI vs. Vertex)
- Retry logic, rate limiting, timeout handling
- Streaming vs. batch response handling

**What the abstraction must expose:**
- Whether the provider is available (so callers can degrade gracefully)
- The model identifier being used (for logging and audit, not for routing)
- A synchronous call interface — RAP's output pipeline is not async

---

## Provider implementations

Three implementations cover the realistic deployment cases:

- `AnthropicProvider` — wraps the Anthropic SDK; default for Claude Code deployments.
- `OpenAIProvider` — wraps the OpenAI SDK; covers GPT-4o and compatible endpoints.
- `NullProvider` — returns a fixed "description unavailable" string; used in tests and offline deployments where no LLM key is present.

The provider is selected at startup via an environment variable or config entry. The rest of the codebase imports the provider interface, not any vendor SDK.

---

## What this does not cover

The provider layer is not a general agent framework. It does not manage conversation history, tool-call loops, or multi-step reasoning. Those are the agent loop's responsibility (section 03-06). The provider layer is a thin, synchronous call boundary — the smallest seam needed to make vendor SDKs swappable.

---


## MCP Surface

## The problem with 71 functions

The current MCP server exposes 71 tool functions. Most are thin wrappers around individual controller commands (`set_bay`, `add_aperture`, `set_zone_label`, `clear_grid`, …). An agent working with this surface must scan a large undifferentiated menu to find the right function for each step. Many of these functions do nothing `run_command` cannot do — they exist as named shortcuts, not as structurally distinct capabilities.

A large surface also creates maintenance drag: every new domain command needs a corresponding MCP wrapper, test, and docstring. The wrappers diverge from the CLI as each is patched independently.

---

## Proposed shape: ~15 functions in 4 groups

### Group 1 — Command core (4)

```
run_command(command: str) -> str
```
The general mutation path. Takes any CLI command string, runs it through the dispatcher, returns the `OK:`/`ERROR:` confirmation. This is the primary tool for all domain mutations — bay operations, wall operations, zone operations, everything the CLI can do.

```
get_state() -> str
undo() -> str
describe() -> str
```

`get_state` returns current state as JSON text. `undo` reverses the last command. `describe` returns the human-readable model summary (equivalent to the CLI `describe` built-in). These three cannot be composed from `run_command` because they either read structured data or need special dispatcher access.

### Group 2 — Persistence (3)

```
save_snapshot(name: str) -> str
load_snapshot(name: str) -> str
run_macro(name: str, args: dict) -> str
```

Snapshots and macros require file I/O that `run_command` cannot do in a single invocation. Templates collapse into `run_macro` with a `--template` flag or a separate `load_template` if the implementer prefers explicit naming (open question — see 03-09).

### Group 3 — Rhino bridge (3)

```
rhino_status() -> str
rhino_query(query: str) -> str
rhino_script(script: str) -> str
```

`rhino_status` checks whether Rhino is running and current. `rhino_query` reads geometry properties (bounding box, layer contents, object count). `rhino_script` executes arbitrary RhinoScript — the escape hatch for geometry operations the state model doesn't cover. These are Rhino-specific and cannot route through the controller.

### Group 4 — AI output (4)

```
describe_image(image_path: str, context: str) -> str
convert_to_tactile(image_path: str, preset: str, output_path: str) -> str
render_tactile(state_path: str, output_path: str) -> str
audit() -> str
```

These require AI inference, file input, or multi-step pipelines that don't fit the command dispatcher model. `audit` is here rather than in Group 1 because it calls the auditor module, not the controller.

---

## What gets cut

- All 20+ domain-specific wrapper functions (`set_bay`, `add_aperture`, `set_wall`, `add_zone`, etc.) — replaced by `run_command`.
- `extend_controller` — unsafe, couples the MCP server to controller source layout, no replacement needed.
- `view_plan`, `view_section`, `view_axon`, `view_elevation` — these call Rhino renders; replace with `rhino_script` for the rare cases that need them.
- `get_field` / `set_field` / `list_fields` — low-level state surgery that belongs in `run_command`.
- `list_commands`, `show_command_source` — introspection tools that belong in help text, not MCP functions.

---

## Resources and prompts

The current 6 resources (`state://current`, etc.) are underused. The rewrite should promote `state://current` to a first-class resource that agents read before issuing commands. The 4 prompt generators can stay if they demonstrably reduce agent turn count; otherwise cut.

**Open question:** Should domain-specific helper functions be allowed as optional extensions that a deployment can register, keeping the core surface small while enabling shortcuts for frequent workflows? See 03-09.

---


## Agent Loop

## Two callers, one dispatcher

The system has two kinds of driver: a human at a terminal (CLI REPL) and an LLM agent over MCP. Both route through the same command dispatcher. The dispatcher does not know or care which caller it is serving — it receives a command string, runs it, and returns a confirmation string. This is the invariant that must survive the rewrite.

```
Human:  stdin → tokenize → dispatcher → stdout
Agent:  MCP call → run_command() → dispatcher → return value
```

---

## Turn lifecycle

A single turn is:

1. **Receive** — a command string arrives (typed line or MCP argument).
2. **Load** — read `state.json` from disk. Apply any pending schema migration.
3. **Snapshot** — `copy.deepcopy(state)` onto the undo stack.
4. **Dispatch** — find the command handler by name; call it with state and parsed args.
5. **Validate** — the handler returns the mutated state. Basic schema invariants are checked.
6. **Write** — `_atomic_write`: serialize to `.tmp`, fsync, `os.replace`. State is now durable.
7. **Hook** — fire all registered post-mutation hooks in order (TTS, export triggers, etc.).
8. **Confirm** — print or return the `OK:` / `ERROR:` string, then `READY:`.

Steps 2–8 happen inside a single Python call. No turn is left half-done — the write either completes atomically or the old file remains intact.

---

## State is on disk, not in memory

The dispatcher reloads state from disk at the start of every turn. It does not hold state in a long-lived object between turns. This is not inefficiency — it is the property that makes the system safe across crashes, process restarts, and multi-process access (CLI and MCP server can run simultaneously against the same file).

The undo stack is the one in-memory exception: it lives in the REPL process and is lost on restart. This is acceptable because `state.json` is the durable record; the undo stack is a convenience within a session. An open question (see 03-09) is whether the undo stack should be serialized alongside state for persistence across restarts.

---

## How a turn completes for an agent

The `READY:` suffix on every confirmation is the agent's signal that the turn is finished and state is durable. An agent must not issue the next command until it has received a string ending with `READY:`. This convention replaces streaming indicators (forbidden — screen reader hostile) and eliminates the need for the agent to poll for completion.

For multi-command sequences, the agent issues commands one at a time, waiting for `READY:` between each. Macros exist precisely to compress known sequences into a single MCP call — an agent should prefer `run_macro` over issuing a sequence of `run_command` calls when the sequence is deterministic.

---

## What the agent loop does not do

- It does not render geometry. That is the Rhino watcher's job (section 03-07).
- It does not call an LLM. That is the provider layer's job (section 03-04) invoked by specific MCP functions.
- It does not manage conversation history or multi-step reasoning. That is the calling agent's job — the dispatcher is stateless between turns.
- It does not watch for external changes to `state.json`. If another process modifies state, the next CLI turn will pick up the change on load; the MCP server will too.

---

## The REPL vs. single-call distinction

The CLI REPL adds one layer above the dispatcher: a `readline`-backed input loop, a help command, and a graceful quit. This layer is thin and has no access to state beyond what it passes into the dispatcher. The MCP `run_command` function is identical to one iteration of that loop minus the readline and help.

---


## Rhino Boundary

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

---


## Output Channels

## The current coupling problem

Output channels are currently wired into the core architecture rather than sitting on top of it. `state_renderer.py` (TACT) hardcodes Layout Jig schema keys and reaches into the controller directory via five levels of `..` path traversal. TASC duplicates TACT's rasterization pipeline independently. The image describer bypasses the MCP pattern and calls Anthropic REST directly. The web UI hardcodes paths to Layout Jig sidecar files. Each channel is a bespoke integration, not an instance of a common pattern.

---

## Output channels are Renderers

All output channels are instances of the Renderer abstraction (section 03-02). They read `state.json` and produce an artifact. They never write back to state. They can be triggered by file watch, by an explicit MCP call, or by a hook registered with the dispatcher.

**The minimal interface each channel implements:**

```
render(state_path: str, output_path: str, options: dict) -> str
  # returns OK: <artifact path> or ERROR: <reason>

supports_schema(version: str) -> bool
  # returns True if this channel can render this schema version
```

That is the entire contract. A channel that implements these two methods can plug into the system.

---

## Channel taxonomy

**File-output channels** consume state and write a file:
- *Tactile PDF* (TACT) — rasterizes the plan, applies RainbowTact patterns, adds Braille labels, writes a PIAF-ready PDF.
- *3D print* (`tactile_print.py`) — generates an STL or 3MF for Bambu Lab printers from 3D tactile objects in state.
- *3DM export* — writes a Rhino-format file from the current Rhino geometry (delegated to `rhino_script`).
- *GHX-gen* — generates a Grasshopper definition from state; a future channel, not yet implemented.

**Text-output channels** consume state and return a string:
- *Text description* — translates state into a structured verbal description of the design. Currently implemented as `describe` in the controller; the output channel form is the same logic decoupled from the REPL.
- *Alt-text generator* — produces screen-reader-ready image descriptions from architectural images, using the provider layer (section 03-04).
- *Audit report* — structural and accessibility checks on the model, returned as a labeled text list.

**Interactive channels** maintain a live view:
- *Rhino watcher* — covered in section 03-07; a file-watching Renderer that runs continuously.
- *Web viewer* — serves `object_inventory.json` to a browser; updates when inventory changes.

---

## What each existing channel must shed

- **TACT `state_renderer.py`** — remove hardcoded Layout Jig schema keys; read only the domain envelope defined by the schema. Remove the `os.path.join("..")` controller import; use the provider interface for Braille instead.
- **TASC** — remove the duplicated PIL rasterization pipeline; call TACT's render function instead. TASC's unique value is its site-planning CLI, not its own PDF renderer.
- **Image describer** — route LLM calls through the provider layer; remove the hardcoded model ID and Anthropic SDK import from the channel code.
- **Web UI** — remove hardcoded paths to `pending_edits.json` and `object_inventory.json`; consume these via the MCP surface rather than direct file access.

---

## Extension model

Adding a new output channel means:
1. Implement `render()` and `supports_schema()`.
2. Register the channel in the deployment config (name, trigger type, default options).
3. Optionally expose it as an MCP function in Group 4 (section 03-05) if agents need to invoke it directly.

No changes to the controller, the dispatcher, or any existing channel. This is the test of whether output channels are genuinely pluggable.

---


## Open Design Questions

Each question is stated cleanly, the tradeoff sketched briefly, and a tentative lean given. The implementing team decides; these leans are recommendations, not requirements.

---

## Q1: Single domain vs. multi-domain state envelope

Should `state.json` hold one domain object at the root (`"domain": {...}`) or a named map (`"domain": { "layout_jig": {...}, "site": {...} }`)?

**Single:** simpler schema, simpler migration, simpler renderer contracts. Every deployment has one domain type; there is no current use case for composing two.

**Multi:** future-proofs composite designs (e.g. a site model and a building model coexisting). Adds schema complexity and forces all renderers to declare which domain they read.

**Lean:** single domain with a `"domain_type"` string at the root so renderers can check compatibility. Multi-domain is an extension if the use case arises.

---

## Q2: Hook execution: synchronous vs. asynchronous

Should post-mutation hooks block the REPL until they complete, or fire asynchronously?

**Synchronous:** simpler; `READY:` is only printed after all hooks finish; TTS completes before the next command is accepted.

**Async:** faster perceived response for the user when hooks are slow (e.g. STL export); but `READY:` must be emitted before hooks complete, which weakens its guarantee.

**Lean:** synchronous for TTS and screen reader hooks (they must complete before the next command); async opt-in for slow export hooks (export can lag behind; READY: is still safe to emit).

---

## Q3: Undo stack persistence

Should the undo stack be serialized to disk alongside `state.json` so undo survives process restarts?

**Persist:** undo works across CLI restarts and across CLI/MCP interleaving. Adds a sidecar file and serialization cost per command.

**In-memory only:** simpler; undo is a session convenience, not a durability guarantee. Git history of `state.json` provides coarser-grained recovery.

**Lean:** in-memory for now. If restart-induced undo loss proves a real problem in practice, add persistence then.

---

## Q4: Renderer trigger: mtime poll vs. push signal

Should renderers be triggered by filesystem mtime polling or by an explicit signal written by the dispatcher after each atomic write?

**Mtime poll:** works across all runtimes including IronPython 2.7. No IPC required. Latency is bounded by poll interval (currently 0.5s).

**Push signal:** lower latency, more precise (includes command name so renderers can skip irrelevant rebuilds). Requires IPC that works across Python 3 and IronPython 2.7 — the options are limited (named pipe, sidecar file, UDP). A sidecar-file push signal is essentially mtime polling with a richer payload.

**Lean:** mtime poll for the Rhino watcher (IronPython forces it). Optional sidecar-file signal for Python 3 renderers that want the command name.

---

## Q5: Optional domain-specific MCP functions

Should the MCP surface allow optional domain-specific function sets to be registered alongside the core ~15 functions?

**Fixed surface only:** enforces the small-API discipline; agents learn one surface and it works everywhere.

**Optional extensions:** a Layout Jig deployment can register `add_bay`, `set_wall`, etc. as shortcuts. Reduces agent turn count for frequent workflows. Risks the surface growing back to 71.

**Lean:** allow extensions declared in a config file with a cap (e.g. 20 max). Core surface is fixed; extensions are deployment-specific.

---

## Q6: Template vs. macro unification

Should templates (startup state generators) and macros (command sequences) be unified under one `run_macro` function with a `--template` flag, or kept as separate MCP functions?

**Unified:** smaller surface; the distinction between "replace state" and "replay commands" is an implementation detail the agent should not need to track.

**Separate:** the distinction is semantically meaningful and prevents accidents (an agent running a template mid-session overwrites the current design).

**Lean:** keep separate. The overwrite risk justifies the extra function name. Use `load_template` and `run_macro` as the two names.

---


## Migration Sketch

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

---

