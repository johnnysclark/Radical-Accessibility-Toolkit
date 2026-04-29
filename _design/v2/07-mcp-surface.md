# MCP Surface

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
