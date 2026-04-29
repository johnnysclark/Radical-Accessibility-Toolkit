# Output Channels

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
