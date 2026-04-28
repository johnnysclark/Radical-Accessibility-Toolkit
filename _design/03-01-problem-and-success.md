# 03-01 — Problem and Success Criteria

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
