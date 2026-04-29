# 03-05 — MCP Surface

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
