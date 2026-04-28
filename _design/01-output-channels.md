---
# 01 — Output Channels subsystem (TACT / TASC / Image Describer / Web UI)

## Purpose
These channels convert model state and raw images into physical or screen-reader-accessible artifacts: PIAF swell-paper PDFs, Braille-annotated prints, structured alt-text, and a browser-based accessible chat surface. They form the accessible output layer of RAP, bridging digital geometry and AI descriptions to tactile and auditory consumers.

## Public API / entry points
- TACT CLI (`tact`): `convert`, `batch`, `render`, `presets`, `info`
- TACT MCP (7): `image_to_piaf`, `list_presets`, `analyze_image`, `describe_image`, `extract_text_with_vision`, `assess_tactile_quality`, `state_to_piaf`
- TASC CLI (`tasc`): `site`, `grid`, `zone`, `remove`, `list`, `describe`, `export` (piaf/3dm/text), `undo`, `connect`, `display`, `run`
- Image Describer CLI (`arch_alt_text.py`): `describe_image`, interactive REPL, batch mode via `main()`
- Web UI entry: `channel-server.ts` serving HTTP + SSE with `/chat`, `/edit-direct`, `/script` endpoints

## Dependencies
- TACT: Pillow, numpy, cv2, reportlab; easyocr and liblouis loaded lazily
- TASC: Pillow (rendering), rhino3dm (3dm export), tact (piaf export); RhinoMCP socket (optional)
- Image Describer: stdlib only; Anthropic REST API via `ANTHROPIC_API_KEY`
- Web UI: Node.js/bun, `@modelcontextprotocol/sdk`, zod
- TACT `state_renderer`: imports `controller/braille.py` via hardcoded relative path traversal

## What's essential
- Image-to-PIAF pipeline: threshold, contrast, RainbowTact color-to-pattern, registration marks, auto-scale to paper size
- Braille label generation and placement via liblouis (grade 1/2)
- State-to-tactile path: state.json → rasterized plan → PIAF PDF, no Rhino required
- Screen-reader-safe text output (OK:/ERROR: prefixes, no tables, no spinners)

## What's accidental
- `state_renderer.py` hard-codes Layout Jig schema keys (`bays`, `walls`, `corridors`) — not a generic state renderer
- `state_renderer.py` imports `controller/braille.py` via five levels of `os.path.join("..")` — fragile cross-package coupling
- TASC exporter duplicates TACT's PIL rasterization pipeline independently
- Image Describer calls Anthropic REST directly with hardcoded model IDs, bypassing the MCP pattern
- Web UI hardcodes paths to Layout Jig controller files, coupling the browser to one tool's layout
- `image_to_piaf` accepts `claude_text_json` as override, making Claude both caller and data provider
---
