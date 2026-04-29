# RAP Design Document

A build specification for a non-visual, agentic CAD design pipeline.
This document is self-contained: no prior codebase context is required.

---

## Table of Contents

1. [Conceptual Brief](#conceptual-brief)
2. [Goals and Requirements](#goals-and-requirements)
3. [Core Abstractions](#core-abstractions)
4. [Module Structure](#module-structure)
5. [Data Contracts](#data-contracts)
6. [Provider Layer](#provider-layer)
7. [MCP Surface](#mcp-surface)
8. [Agent Loop](#agent-loop)
9. [Rhino Boundary](#rhino-boundary)
10. [Output Channels](#output-channels)
11. [Open Design Questions](#open-design-questions)
12. [Implementation Sequence](#implementation-sequence)

---

## Conceptual Brief

## What RAP is

RAP is a non-visual, agentic CAD design pipeline. A designer — human or AI agent — issues semantic design intentions through a text interface. Those intentions are recorded in a plain-text JSON file that is the sole source of truth for the design. Downstream renderers — geometry engines, tactile print pipelines, alt-text generators — are read-only consumers of that file. Vision is never required at any stage.

Non-visual interaction is the primary design case; sighted interaction is a bonus layer on top.

## Why it exists

The co-designer is a blind architecture student. His daily workflow — designing a building, reviewing it, fabricating tactile models, presenting to critics — is the test suite for every tool. A feature that can't be heard, felt, or read by a screen reader doesn't ship.

That constraint is generative rather than limiting. To make design accessible without vision, you must make design legible through language; you must separate what a thing *is* from where it appears on screen; you must make every mutation auditable and every state recoverable. These are not accommodations — they are engineering virtues the discipline should have had regardless.

## What "non-visual, agentic CAD pipeline" means in practice

Three properties define the system:

**Non-visual.** Every command has a text form. Every response has a text form. No step requires a viewport, a click, or a look. Physical output — swell-paper tactile graphics, 3D-printed models — closes the loop for users whose primary sense is touch.

**Agentic.** A language model can drive the entire pipeline: issue commands, read state, evaluate geometry, trigger output. The JSON state file is the handoff between the agent's reasoning and the geometry engine's execution. The agent does not need to know Rhino exists.

**CAD pipeline.** The system is grounded in real geometry — meter-accurate plans, structural grids, fabrication-ready exports. The design artifacts it produces go to a laser cutter, a braille embosser, or an architecture critic.

## Why this generalizes across design tasks

The architecture — command dispatcher → JSON state → read-only renderers — has no inherent dependency on any specific building type or geometric vocabulary. It applies to any design task where the designer works through language rather than a viewport. A clean implementation separates the general infrastructure (dispatch, undo, atomic write, renderer boundary) from the domain-specific content (what objects exist, what commands operate on them). Swapping in a new design domain means writing new commands and a new schema — the infrastructure is unchanged.

## The success bar

The system succeeds if a blind architecture student can design, review, and fabricate a building without touching a mouse or screen, and if a language model can do the same with no special affordances beyond the documented API. Everything else is negotiable.

---


## Goals and Requirements

## Design requirements

These are the properties the implementation must have. They are constraints on the architecture, not implementation suggestions.

**1. The dispatcher is independently testable.** The command dispatch mechanism — receiving a command string, loading state, applying a handler, writing state — must work with no geometry engine running. Tests for individual commands run against JSON files only.

**2. Domain logic is isolated in one layer.** All geometry-specific logic (what objects a domain has, what commands operate on them, what schema keys they use) lives in a domain module. The dispatcher, the MCP server, the hook registry, and all renderers are domain-agnostic. Adding a new design domain means writing a new domain module, not modifying infrastructure.

**3. All side effects go through the hook registry.** Nothing in the mutation path produces side effects. TTS announcement, audio signals, export triggers, and logging all run as post-mutation hooks. The dispatcher emits a hook payload after each successful write; hooks consume it. The dispatcher has no knowledge of what hooks are registered.

**4. Renderers depend only on the state schema.** No renderer imports from any other part of the system. A renderer receives a path to `state.json` and a path for its output. It reads the schema, produces an artifact, returns an `OK:` or `ERROR:` string. Renderers are independently deployable.

**5. The MCP surface is small and stable.** The MCP server exposes ~15 named functions. All domain mutations go through `run_command`. Named functions exist only where they provide something `run_command` cannot (structured data reads, file I/O, AI inference). The surface does not grow when new domain commands are added.

**6. LLM calls are behind a provider interface.** Any place the system calls a language model for inference uses the provider interface, not a vendor SDK directly. The provider is selected at startup. Tests run against `NullProvider`.

**7. The Rhino boundary is filesystem-only.** The only channel between the Python 3 controller and the IronPython 2.7 Rhino runtime is the filesystem. `state.json` flows into Rhino; `object_inventory.json` flows out. No sockets, no shared memory, no GUIDs crossing the boundary.

---

## Success criteria

The implementation is complete when:

- A new developer can read this document and build a working system without reading any other source.
- The dispatcher, schema layer, and each renderer each have passing tests with no Rhino running.
- An AI agent can design a complete architectural artifact using fewer than 15 distinct MCP function names.
- The same `state.json` file drives Rhino geometry, a tactile PDF, and a text description with no code changes between them.
- A post-mutation hook handles TTS and export triggers; neither is wired into the dispatcher.

## Non-goals

- A graphical user interface. The CLI and MCP surface are the interfaces.
- Replacing Rhino as the geometry engine. The goal is a clean boundary at the Rhino edge.
- Supporting multiple simultaneous design domains in one state file. One domain per deployment; multi-domain is a future extension.
- Streaming or async command responses. All commands are synchronous; `READY:` marks completion.

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

Schema changes are migrations, not breaking changes. A migration function upgrades an older document to the current version on load. The schema version field in `state.json` selects the right migration path. Domain-specific schemas are namespaced under the root schema so the general envelope stays stable.

---

## 4. Renderer

Any read-only consumer of state that produces an artifact. A renderer watches for state changes (by file mtime, by explicit signal, or by explicit invocation) and translates the current state into an output: Rhino geometry, a tactile PDF, a text description, a 3D print file, a braille document. A renderer never writes back to state. If a renderer crashes or is absent, the design is unaffected.

Renderers are pluggable: adding a new output format means writing a new renderer, not modifying the command layer or the schema. The only contract a renderer must honor is the schema it reads.

---

## 5. Hook

A post-mutation callback registered against the dispatch loop. After a command completes and state is saved, the dispatcher fires all registered hooks in order. A hook receives the command name, the arguments, the result string, and the path to the now-current state file. Hooks handle every side effect that is not a renderer: TTS announcement, screen reader signals, export triggers, logging, telemetry. Nothing in the mutation path itself produces side effects.

Hooks are registered at startup, not hardcoded into commands. A deployment without a screen reader registers no TTS hook. A deployment with auto-export registers an export hook. The command code is identical in both cases.

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


## Module Structure

## Directory layout

```
rap/
  core/
    dispatcher.py     # apply_command(), load_state(), _atomic_write(), undo stack
    schema.py         # CURRENT_VERSION, load_with_migration(), migration functions
    hooks.py          # HookRegistry, HookPayload, register(), fire()
  cli/
    repl.py           # readline REPL — thin shell over dispatcher
  mcp/
    server.py         # FastMCP server, ~15 @mcp.tool() functions
  provider/
    base.py           # Provider protocol
    anthropic.py      # AnthropicProvider
    openai.py         # OpenAIProvider
    null.py           # NullProvider (offline / test)
  renderer/
    base.py           # Renderer protocol
    rhino/
      watcher.py      # IronPython 2.7 file-watch loop (runs inside Rhino)
      draw.py         # per-object-type draw functions, dispatched by watcher
    tact/
      pdf.py          # state.json → PIAF tactile PDF
      image.py        # raster image → PIAF tactile PDF (RainbowTact pipeline)
    text/
      describe.py     # state → structured verbal description
      audit.py        # state → labeled accessibility / structural check report
  domain/
    layout_jig/       # Layout Jig domain (replace or extend for other domains)
      commands.py     # all Layout Jig command handlers
      schema.py       # Layout Jig domain schema definition
```

`rap/core/` has zero pip dependencies — Python stdlib only. `mcp/`, `provider/`, and `renderer/tact/` may use pip packages.

---

## Key interfaces

```python
# core/dispatcher.py
def apply_command(state: dict, tokens: list[str], state_file: str) -> str:
    """Dispatch one command. Returns 'OK: ...' or 'ERROR: ...'."""

def load_state(path: str) -> dict:
    """Read state.json. Runs schema migration on every load."""

def _atomic_write(path: str, content: str) -> None:
    """Write to .tmp, fsync, os.replace. Never leaves a partial file."""
```

```python
# renderer/base.py
from typing import Protocol

class Renderer(Protocol):
    def render(self, state_path: str, output_path: str, options: dict) -> str:
        """Produce an artifact. Returns 'OK: <path>' or 'ERROR: <reason>'."""

    def supports_schema(self, version: str) -> bool:
        """Return True if this renderer can consume this schema version."""
```

```python
# provider/base.py
from typing import Protocol

class Provider(Protocol):
    def complete(self, prompt: str, images: list[bytes] | None = None) -> str:
        """Send a prompt; return plain-text response."""

    def describe_image(self, image: bytes, context: str) -> str:
        """Return a screen-reader-ready description of an image."""

    def available(self) -> bool:
        """Return True if credentials are present and the endpoint is reachable."""
```

```python
# core/hooks.py
from typing import TypedDict, Callable

class HookPayload(TypedDict):
    command: str
    args: dict
    result: str        # the OK:/ERROR: string
    elapsed_ms: int
    state_path: str

HookFn = Callable[[HookPayload], None]

class HookRegistry:
    def register(self, fn: HookFn) -> None: ...
    def fire(self, payload: HookPayload) -> None: ...
```

---

## Dependency rules

- `core/` imports nothing outside stdlib.
- `cli/` imports `core/` only.
- `mcp/` imports `core/` and optionally `provider/` and `renderer/`.
- `renderer/` imports `core/schema` and nothing else from `rap/`.
- `provider/` imports nothing from `rap/`.
- `domain/` imports `core/dispatcher` to register its commands; nothing else.
- No module imports from `domain/` directly — domain registration happens at startup via config.

---


## Data Contracts

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

---


## Provider Layer

RAP has two directions of LLM interaction that must stay model-agnostic: **inbound** (an agent driving RAP via MCP) and **outbound** (RAP calling an LLM for AI-powered analysis).

---

## Inbound: agents driving RAP

The MCP surface is the inbound interface. MCP is a protocol, not a vendor-specific API, so any MCP-capable agent — Claude, Gemini, GPT-4o, a local model — can call RAP's tools. Write MCP tool docstrings in neutral terms. Do not reference any specific LLM by name in tool descriptions or error messages. Treat any MCP host as a valid caller.

---

## Outbound: RAP calling an LLM

Several output channels require AI inference: image description, alt-text generation, and tactile quality assessment. All of these must route through the provider interface defined in `provider/base.py`. No module outside `provider/` imports a vendor AI SDK directly.

**Implement these three provider classes:**

`AnthropicProvider` — wraps the Anthropic Python SDK. Default for deployments with an `ANTHROPIC_API_KEY` environment variable. Uses `claude-sonnet-4-6` as the default model; the model ID is set in config, not hardcoded in call sites.

`OpenAIProvider` — wraps the OpenAI Python SDK. Works for any OpenAI-compatible endpoint including local models. Default model configurable.

`NullProvider` — returns `"[description unavailable]"` for `describe_image` and `complete`. Does not require network access or credentials. Used in tests and offline deployments.

Provider selection at startup:
```python
provider = get_provider()  # reads RAP_PROVIDER env var, defaults to auto-detect
```

Auto-detect: if `ANTHROPIC_API_KEY` is set, use `AnthropicProvider`; elif `OPENAI_API_KEY` is set, use `OpenAIProvider`; else `NullProvider`.

---

## The provider interface

Defined in `provider/base.py` as a `Protocol`:

```python
class Provider(Protocol):
    def complete(self, prompt: str, images: list[bytes] | None = None) -> str:
        """Send prompt with optional images; return plain-text response."""

    def describe_image(self, image: bytes, context: str) -> str:
        """Return a screen-reader-ready description of an architectural image."""

    def available(self) -> bool:
        """True if credentials are present and the endpoint is reachable."""
```

**What the interface hides:**
- API endpoint URLs and authentication headers
- Model IDs and version strings
- Request/response envelope format (Anthropic vs. OpenAI vs. Vertex)
- Retry logic, rate limiting, and timeout handling
- Streaming vs. batch response handling

**What the interface exposes:**
- Whether the provider is usable right now (`available()`)
- A synchronous call contract — all calls block until the response is ready

The interface does not manage conversation history, tool-call loops, or multi-step reasoning. Those responsibilities belong to the MCP caller or the CLI user.

---

## Calling the provider

Renderer modules and MCP tool handlers that need AI inference receive a `Provider` instance injected at construction or call time — they do not call `get_provider()` themselves. This makes them testable with `NullProvider` without environment setup.

Example in a renderer:

```python
class AltTextRenderer:
    def __init__(self, provider: Provider):
        self.provider = provider

    def render(self, state_path: str, output_path: str, options: dict) -> str:
        image = load_image(options["image_path"])
        description = self.provider.describe_image(image, context="architectural plan")
        write(output_path, description)
        return "OK: " + output_path
```

---


## MCP Surface

The MCP server exposes exactly these functions, organized in four groups. All domain mutations go through `run_command`. Named functions in other groups exist only where they provide something `run_command` cannot.

---

## Group 1 — Command core (5 functions)

```
run_command(command: str) -> str
```
The primary mutation path. Accepts any command string the CLI accepts. Runs it through the dispatcher. Returns the `OK:`/`ERROR:` confirmation string ending with `READY:`. This is the function agents use for all domain operations.

```
get_state() -> str
```
Returns the full current `state.json` as a JSON text string. Agents read this before issuing commands to understand the current design.

```
describe() -> str
```
Returns a human-readable plain-text summary of the current design. Suitable for reading aloud or printing to a braille display.

```
undo() -> str
```
Reverses the last command. Returns `OK: undone <command-name> READY:` or `ERROR: nothing to undo`.

```
load_template(name: str, args: dict) -> str
```
Loads a named template, replacing the entire state with a freshly generated one. This is destructive — it overwrites the current design. Kept separate from `run_macro` to prevent accidents.

---

## Group 2 — Persistence (2 functions)

```
save_snapshot(name: str) -> str
load_snapshot(name: str) -> str
```
Save and restore named snapshots of `state.json`. Snapshots are stored as timestamped copies alongside the state file. `load_snapshot` is also destructive — it replaces current state.

```
run_macro(name: str, args: dict) -> str
```
Replay a saved command sequence. Macros are JSON files listing commands with optional parameter substitution. Unlike `load_template`, macros apply commands on top of existing state rather than replacing it.

---

## Group 3 — Rhino bridge (3 functions)

```
rhino_status() -> str
```
Returns whether Rhino is running, whether it has loaded the watcher, and whether its last-rendered schema matches the current `state.json` schema version.

```
rhino_query(query: str) -> str
```
Reads from `object_inventory.json` — returns object counts, bounding boxes, layer contents. Does not require Rhino to be running; reads the last-written inventory.

```
rhino_script(script: str) -> str
```
Writes `script` to `pending_script.py`. The Rhino watcher picks it up on the next idle tick, executes it, and deletes it. Returns `OK: script queued` immediately; script execution is asynchronous. Use for geometry operations not expressible in the state model.

---

## Group 4 — AI output (4 functions)

```
describe_image(image_path: str, context: str) -> str
```
Returns a screen-reader-ready alt-text description of an architectural image. Uses the configured provider.

```
convert_to_tactile(image_path: str, preset: str, output_path: str) -> str
```
Converts an image to a PIAF-ready tactile PDF using the specified preset. Returns `OK: <output_path>`.

```
render_tactile(output_path: str) -> str
```
Renders the current `state.json` directly to a tactile PDF. No image input — reads geometry from state. Returns `OK: <output_path>`.

```
audit() -> str
```
Runs structural and accessibility checks on the current state. Returns a labeled plain-text report.

---

## MCP resources

Expose `state://current` as an MCP resource returning the full `state.json` content. Agents may read this resource directly rather than calling `get_state()`. Keep the two in sync.

---

## Extension functions (optional, deployment-specific)

A deployment may register additional domain-specific functions (e.g. `add_bay`, `set_wall`) in a config file. Cap at 20 extension functions. Extensions must delegate to `run_command` internally — they are shortcuts, not new mutation paths. The core 14 functions above are fixed and apply to all deployments.

---


## Agent Loop

## Two callers, one dispatcher

The system has two kinds of driver: a human at a terminal (CLI REPL) and an LLM agent over MCP. Both route through the same command dispatcher. The dispatcher does not know or care which caller it is serving — it receives a command string, runs it, and returns a confirmation string.

```
Human:  stdin → tokenize → dispatcher → stdout
Agent:  MCP call → run_command() → dispatcher → return value
```

---

## Turn lifecycle

A single turn is:

1. **Receive** — a command string arrives (typed line or MCP argument).
2. **Load** — read `state.json` from disk. Run schema migration if needed.
3. **Snapshot** — `copy.deepcopy(state)` onto the undo stack.
4. **Dispatch** — look up the command handler by name; call it with state and parsed args.
5. **Validate** — the handler returns the mutated state. Check required schema fields are present.
6. **Write** — `_atomic_write`: serialize to `.tmp`, fsync, `os.replace`. State is now durable.
7. **Hook** — fire all registered hooks in order with the `HookPayload`.
8. **Confirm** — print or return the `OK:` / `ERROR:` string, then `READY:` on a new line.

Steps 2–8 happen inside a single call. No turn is left half-done — the atomic write either completes or the previous file remains intact.

---

## State is on disk, not in memory

The dispatcher reloads state from disk at the start of every turn. It does not hold state in a long-lived object between turns. This is what makes the system safe across crashes, process restarts, and simultaneous access from the CLI and MCP server against the same file.

The undo stack is the one in-memory exception: it lives in the REPL process and is lost on restart. `state.json` is the durable record; the undo stack is a session convenience.

---

## How a turn completes for an agent

`READY:` on its own line at the end of every response is the agent's signal that the turn is finished and state is durable. An agent must not issue the next command until it receives a line containing only `READY:`. This convention:
- Replaces streaming indicators (forbidden — screen reader hostile)
- Eliminates the need to poll for completion
- Survives across both synchronous and async transport

For multi-command sequences, the agent issues one command at a time and waits for `READY:` between each. Use `run_macro` to compress a deterministic sequence into one call.

---

## What the agent loop does not do

- **Render geometry.** The Rhino watcher reacts to file changes asynchronously. The dispatcher does not wait for it.
- **Call an LLM.** The provider layer is invoked by specific MCP functions in Group 4, not by the dispatcher.
- **Manage conversation history.** The calling agent owns its context window. The dispatcher is stateless between turns.
- **Watch for external changes to `state.json`.** If an external process modifies state, the next CLI turn picks up the change on load.

---

## The REPL vs. single-call distinction

`cli/repl.py` adds a readline input loop, `help`, and a graceful quit above the dispatcher. It is a thin shell. The MCP `run_command` function is identical to one iteration of that loop minus readline and help. Both call `apply_command` with the same arguments.

---

## Screen reader output rules

All output from the dispatcher must follow these rules — they are not optional:

- Every response begins with `OK:` or `ERROR:`.
- Every response ends with `READY:` on its own line.
- No tables, no multi-column layout, no box-drawing characters.
- No progress spinners or streaming partial output.
- No lines longer than 120 characters.
- When listing items, one item per line with a label prefix.

---


## Rhino Boundary

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

---


## Output Channels

## All channels are Renderers

Every output channel implements the Renderer interface from `renderer/base.py`:

```python
class Renderer(Protocol):
    def render(self, state_path: str, output_path: str, options: dict) -> str:
        ...  # returns "OK: <artifact path>" or "ERROR: <reason>"

    def supports_schema(self, version: str) -> bool:
        ...  # return False to refuse gracefully on unknown schema versions
```

Channels read `state.json` and produce artifacts. They never write back to state. They have no knowledge of the dispatcher, the MCP server, or other channels. The only import a channel needs from the `rap/` package is `core/schema.py` for version checking.

Channels are triggered by: file mtime watch (continuous renderers), explicit MCP call (on-demand renderers), or a registered hook (event-driven renderers).

---

## Required channels

### Tactile PDF (`renderer/tact/pdf.py`)
Reads `state.json`, rasterizes the plan view, applies RainbowTact color-to-tactile-pattern conversion, places Braille labels via liblouis, adds registration marks, and writes a PIAF-ready PDF at the target paper size. The Braille label generator lives in a shared module (`renderer/tact/braille.py`) used by both this channel and the 3D print channel.

Options: `paper_size` (A4/letter/custom), `preset` (name from the preset registry), `braille_grade` (1 or 2).

### Image-to-tactile PDF (`renderer/tact/image.py`)
Converts an input raster image (not a state-derived view) to PIAF-ready PDF. Pipeline: load image → threshold → RainbowTact pattern fill → optional EasyOCR text detection → Braille label placement → PDF output. Exposes preset configs (high-contrast, line-drawing, photo, etc.) as named options.

### 3D print (`renderer/tact/print3d.py`)
Reads 3D tactile objects from `state.domain` and generates an STL or 3MF file for Bambu Lab or compatible printers. Output format determined by `options["format"]`.

### Text description (`renderer/text/describe.py`)
Reads `state.json` and produces a structured plain-text description of the design: object counts, named elements, spatial relationships in semantic terms. No AI inference — fully deterministic. Used by the CLI `describe` built-in and the MCP `describe()` function.

### Audit report (`renderer/text/audit.py`)
Runs structural and accessibility checks: clearance widths, door swing conflicts, missing labels, elements with no semantic ID. Returns a labeled list with `PASS:`, `WARN:`, and `FAIL:` prefixes per check. No AI inference.

### Alt-text generator (via provider layer)
Not a standalone renderer — invoked by the MCP `describe_image()` function. Uses the configured `Provider` to generate a screen-reader-ready description of an input image. The description format follows architectural alt-text conventions: space type, primary elements, relationships, notable features.

### Rhino watcher (`renderer/rhino/watcher.py`)
Covered in the Rhino Boundary section. Runs continuously; file-watch triggered.

### Web viewer
Serves `object_inventory.json` over HTTP to a browser-based viewer. Updates on file change. Not part of the `rap/` Python package — a separate Node.js/TypeScript server. Reads inventory; never writes state.

---

## Extension model

To add a new output channel:
1. Implement `render()` and `supports_schema()` in a new file under `renderer/`.
2. Register the channel in `deployment.json` with its trigger type (`watch`, `on_demand`, or `hook`) and default options.
3. Optionally add it as a Group 4 MCP function if agents need to invoke it by name.

No changes to the dispatcher, the MCP server core, or any existing channel.

---

## What channels must not do

- Import from `domain/` or hardcode domain schema keys. Read only what the schema envelope guarantees (`schema`, `domain_type`, `meta`) plus the contents of `domain` accessed by the keys the schema defines.
- Import from other channels. If two channels share logic (e.g. Braille rendering), extract that logic to a shared module.
- Write to `state.json` or any file the dispatcher owns.

---


## Open Design Questions

Each question is stated cleanly, the tradeoff sketched briefly, and a tentative lean given. The implementing team decides; these leans are recommendations, not requirements.

---

## Q1: Single domain vs. multi-domain state envelope

Should `state.json` hold one domain object (`"domain": {...}`) or a named map (`"domain": { "layout_jig": {...}, "site": {...} }`)?

**Single:** simpler schema, simpler migration, simpler renderer contracts. One domain per deployment covers all known use cases.

**Multi:** future-proofs composite designs (e.g. a site model and a building model coexisting in one file). Adds schema complexity and forces all renderers to declare which domain they consume.

**Lean:** single domain with a `"domain_type"` string at the root. Multi-domain is a future extension.

---

## Q2: Hook execution: synchronous vs. asynchronous

Should post-mutation hooks block the dispatcher until they complete, or fire asynchronously?

**Synchronous:** `READY:` is only emitted after all hooks finish. TTS completes before the next command is accepted. Simpler to reason about.

**Async:** hooks that are slow (e.g. STL export) don't delay the user. But `READY:` must be emitted before hooks complete, which weakens its guarantee for export-dependent workflows.

**Lean:** synchronous for TTS and screen reader hooks; async opt-in for export hooks where latency matters. The hook registration API should accept a `sync: bool` flag.

---

## Q3: Undo stack persistence

Should the undo stack serialize to disk alongside `state.json` so undo works across process restarts?

**Persist:** undo survives CLI restarts and CLI/MCP interleaving.

**In-memory only:** simpler; undo is a session convenience. The state file and git history provide coarser-grained recovery.

**Lean:** in-memory only for the initial implementation. Add persistence if users report it as a real problem.

---

## Q4: Renderer trigger: mtime poll vs. push signal

Should renderers be triggered by mtime polling or by an explicit sidecar signal written by the dispatcher?

**Mtime poll:** works across Python 3 and IronPython 2.7. No IPC required. Latency bounded by poll interval.

**Push signal:** lower latency; `command` field lets renderers skip irrelevant rebuilds. Requires a sidecar write per command.

**Lean:** mtime poll for the Rhino watcher (IronPython forces it). Optional sidecar signal for Python 3 renderers.

---

## Q5: Optional domain-specific MCP functions

Should deployments be allowed to register extra named MCP functions (e.g. `add_bay`, `set_wall`) alongside the core 14?

**Fixed surface only:** enforces small-API discipline.

**Optional extensions:** shortcuts reduce agent turn count for frequent workflows. Risk: the surface grows back over time.

**Lean:** allow extensions declared in a config file, capped at 20. Core surface is fixed; extensions are deployment-specific and must delegate to `run_command` internally.

---

## Q6: Template vs. macro naming

Should `load_template` and `run_macro` be merged into a single `run_macro` function with a `--template` flag?

**Unified:** smaller surface; the distinction is an implementation detail.

**Separate:** the distinction matters — templates are destructive (they replace state); macros are additive (they replay commands on existing state). Keeping them separate prevents an agent from accidentally overwriting a design.

**Lean:** keep separate. Use `load_template` and `run_macro` as the two names. The destructive/additive distinction is worth a separate function name.

---

## Q7: Domain registration mechanism

How does a domain module register its commands with the dispatcher at startup?

**Config file:** `deployment.json` lists the domain module path; the dispatcher imports it.

**Entry points:** domain modules declare a `rap.domain` entry point in `pyproject.toml`; the dispatcher discovers them via `importlib.metadata`.

**Lean:** config file for simplicity. Entry points are better for third-party domains but add packaging complexity that isn't needed for the initial implementation.

---


## Implementation Sequence

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

---

