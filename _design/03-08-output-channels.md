# 03-08 — Output Channels

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
