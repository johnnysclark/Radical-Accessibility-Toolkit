# Swell-Print Tool — PIAF Tactile Graphics Pipeline

Converts architectural designs and images to tactile swell-paper
graphics that can be printed on a PIAF swell-form machine for blind
users.

## Two Modes

1. **Render state.json** — Produces a PIAF-ready B&W image directly
   from the canonical model artifact. No Rhino needed. Draws columns,
   walls, corridors, apertures, room hatches, labels (English + Braille),
   legend, and section cuts.

2. **Convert any image** — Takes a photograph, sketch, CAD export, or
   any image and converts it to high-contrast B&W suitable for swell
   paper. Ten presets for different image types.

## Setup

```
pip install -r tools/swell-print/requirements.txt
```

Required: Pillow, reportlab
Optional: numpy (faster density calc), opencv-python (CLAHE), liblouis (Grade 2 braille)

## Usage

### Interactive mode

```
python tools/swell-print/swell_print.py

>> render
OK: Rendered state_tactile.pdf (Letter, 300 DPI, density 28.3%)

>> convert photo.jpg --preset floor_plan
OK: Converted photo.jpg -> photo_tactile.png (density 31.2%)

>> presets
OK: 10 presets available: ...

>> density output.png
OK: Density 31.2% (good for PIAF)
```

### Single-shot mode

```
python tools/swell-print/swell_print.py render state.json --output plan.pdf
python tools/swell-print/swell_print.py convert photo.jpg --preset sketch
python tools/swell-print/swell_print.py density output.png
python tools/swell-print/swell_print.py presets
```

### MCP tools (via Claude Code)

render_tactile, convert_to_tactile, check_tactile_density, list_tactile_presets

## Files

- swell_print.py — CLI entry point (REPL + single-shot)
- state_renderer.py — Render state.json to B&W PIL Image
- image_converter.py — Convert images to PIAF-ready B&W
- pdf_generator.py — Wrap B&W images in PIAF-ready PDF
- requirements.txt — Python dependencies

## Braille

The braille module lives at controller/braille.py (stdlib-only).
Grade 1 built-in, Grade 2 via liblouis. Used by the state renderer
for all label rendering.

## Density Management

PIAF swell paper works best with 25-40% black pixel density.
Above 45% causes excessive swelling and loss of tactile detail.
The tool warns at 40% and rejects above 45%.

Part of the Radical Accessibility Project — UIUC School of Architecture.
