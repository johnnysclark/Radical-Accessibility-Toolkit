# Goals and Requirements

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
