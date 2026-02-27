# MANUAL.docx Update Notes — Image-to-PIAF Integration

These notes describe sections to add to `MANUAL.docx` for the new Image-to-PIAF tactile conversion tool (`tactile/image_to_piaf.py`). Apply these when editing on desktop.

---

## Suggested New Section: Image-to-PIAF — Tactile Image Conversion

Add this as a new top-level section after the existing sections (e.g., after Section 19 or as an appendix).

---

### Section: Overview

Image-to-PIAF converts architectural images into PIAF-ready output for swell paper printing. It handles photographs, CAD screenshots, scanned plans, textbook figures, and precedent studies — any image that needs to become a tactile graphic.

The tool lives in `tactile/image_to_piaf.py` and is separate from the Layout Jig. Layout Jig generates designs from scratch; Image-to-PIAF converts existing images.

**Dependency:** Requires Pillow. Install with `pip install Pillow`.

---

### Section: Quick Start

1. Open a terminal.
2. Run: `python tactile/image_to_piaf.py plan.jpg --preset floor_plan`
3. The tool outputs a PIAF-ready PNG at 300 DPI.
4. Print the output on PIAF microcapsule paper using a laser printer with carbon-based black toner.
5. Feed through the PIAF heater. Black areas swell into raised tactile lines.

Expected output:
```
OK: Converted plan.jpg using preset 'floor_plan'.
  Output: plan_piaf.png
  Original size: 4032 x 3024 px
  Final size: 2550 x 3300 px
  Density: 28%
READY:
```

---

### Section: Presets

Ten presets are tuned for different architectural image types. Each preset sets an optimal threshold and contrast method.

1. `floor_plan` — Architectural floor plans (CAD output, printed plans). Threshold 100, auto-contrast.
2. `elevation` — Building elevations (line drawings with moderate detail). Threshold 120, S-curve.
3. `photograph` — Photos of buildings, sites, or models. Threshold 90, CLAHE.
4. `sketch` — Hand-drawn sketches (light pencil or pen lines). Threshold 140, none.
5. `section` — Building sections (line drawings with poche/fill). Threshold 110, histogram equalization.
6. `site_plan` — Site plans (contours, vegetation, context). Threshold 95, auto-contrast.
7. `rendering` — 3D renderings (shaded views with tonal range). Threshold 85, CLAHE.
8. `diagram` — Circulation, structural, concept diagrams. Threshold 105, S-curve.
9. `historic_photo` — Historic photographs (low contrast, aged images). Threshold 80, histogram equalization.
10. `handdrawn` — Hand-drawn plans or details (strong pencil/ink lines). Threshold 130, none.

Usage: `python tactile/image_to_piaf.py photo.jpg --preset photograph`

---

### Section: Contrast Methods

Five contrast enhancement methods are available. The preset selects one automatically, but you can override with `--contrast`:

1. `none` — No enhancement. Use for images that already have good contrast.
2. `auto_contrast` — Stretches the histogram to use the full range. Good default.
3. `histogram_eq` — Equalizes the histogram for maximum contrast. Good for washed-out images.
4. `s_curve` — Applies an S-curve that steepens mid-tones while compressing shadows and highlights. Good for line drawings.
5. `clahe` — Local contrast enhancement. Good for photographs with uneven lighting.

Usage: `python tactile/image_to_piaf.py photo.jpg --contrast clahe`

---

### Section: Density Management

PIAF swell paper works best at less than 30% black pixel density. Above 45%, the paper becomes unreadable — too many black areas swell and merge together.

The tool automatically checks density after thresholding. If density exceeds 30%, it applies morphological erosion — shrinking black areas iteratively — until density drops below the target. This preserves line structure while reducing fill areas.

You can disable auto-reduction with `--no-density` or set a custom target with `--density-target 0.25`.

Density is reported in every conversion output:
```
OK: Converted photo.jpg using preset 'photograph'.
  Density: 28%
```

If density remains above 45% after reduction, a warning is printed:
```
  WARNING: Density 48% exceeds PIAF max (45%).
```

---

### Section: Braille Labels

Add braille labels to the output using `--labels`:

```
python tactile/image_to_piaf.py plan.jpg --labels "Kitchen;Living Room;Bedroom"
```

Labels are semicolon-separated. Each label is:
1. Converted to Grade 1 braille (or Grade 2 if liblouis is installed).
2. Rendered as raised dot patterns on the image.
3. Placed with overlap detection — if labels overlap, the tool tries repositioning (below, above, right, left).
4. If no clear position is found, the label is abbreviated to a letter (A, B, C) and an abbreviation key is printed.

Expected output:
```
OK: Converted plan.jpg using preset 'floor_plan'.
  Labels: 3 placed.
  Abbreviation key:
    A = Living Room
```

---

### Section: Pre-flight Analysis

Before converting, you can analyze an image to check its suitability:

```
python tactile/image_to_piaf.py photo.jpg --analyze
```

Expected output:
```
OK: Analysis of photo.jpg
  Size: 4032 x 3024 px (12.2 MP)
  Suggested preset: photograph
  Density at thresholds:
    Threshold 80: 32%
    Threshold 100: 25%
    Threshold 120: 18%
    Threshold 140: 12%
```

This shows how dense the image will be at different thresholds, helping you choose the right preset or override.

---

### Section: Quality Check

After converting, verify the output quality:

```
python tactile/image_to_piaf.py plan_piaf.png --quality
```

Expected output:
```
OK: Quality check of plan_piaf.png
  Density: 28% (OK)
  Margin: 15% blank
  Verdict: PASS
```

The tool checks density, blank margins, and reports issues if found.

---

### Section: Output Formats

Three output formats are supported:

1. `png` (default) — Best for viewing and most printers. `--format png`
2. `tiff` — Lossless with embedded DPI. `--format tiff`
3. `pdf` — Embeds page size for direct printing. `--format pdf`

All formats output at 300 DPI.

---

### Section: Paper Sizes

Four paper sizes are supported:

1. `letter` (default) — 8.5 x 11 inches
2. `tabloid` — 11 x 17 inches
3. `a4` — 8.27 x 11.69 inches
4. `a3` — 11.69 x 16.54 inches

Usage: `python tactile/image_to_piaf.py plan.jpg --paper tabloid`

---

### Section: Tiling

For images that are too large for one page, use `--tile` to split across multiple pages with registration marks:

```
python tactile/image_to_piaf.py large_plan.jpg --tile
```

Each tile gets crosshair registration marks at the corners and a page label (R1C1, R1C2, etc.) for assembly.

---

### Section: Invert

For images with white lines on a black background (common in CAD dark mode), use `--invert`:

```
python tactile/image_to_piaf.py dark_cad.jpg --invert
```

---

### Section: Interactive REPL

Run without arguments to enter interactive mode:

```
python tactile/image_to_piaf.py
```

Prompt: `piaf>>`

Commands:
- `convert <path> [preset]` — Convert an image
- `analyze <path>` — Pre-flight analysis
- `quality <path>` — Quality check
- `presets` — List all presets
- `preset <name>` — Show preset details
- `braille <text>` — Convert text to braille
- `history` — Show conversion history
- `set threshold|contrast|paper|labels|invert|tile|output <value>` — Override settings
- `clear` — Reset all overrides
- `help` — Full command reference
- `quit` — Exit

---

### Section: MCP Server

The Image-to-PIAF MCP server enables AI-driven conversion. Run alongside the Layout Jig MCP server:

```json
{
  "mcpServers": {
    "image-to-piaf": {
      "command": "python",
      "args": ["tactile/mcp_server.py"]
    }
  }
}
```

Tools: `image_to_piaf`, `analyze_image`, `assess_tactile_quality`, `list_presets`, `convert_text_to_braille`, `conversion_history`.

---

### Section: Full Command Reference

```
python tactile/image_to_piaf.py <image> [options]

Options:
  --preset, -p     Preset name (default: floor_plan)
  --threshold, -t  Override threshold 0-255
  --contrast, -c   Override contrast method
  --output, -o     Output file path
  --format, -f     Output format: png, tiff, pdf
  --paper          Paper size: letter, tabloid, a4, a3
  --margin         Margin in inches (default: 0.5)
  --invert         Invert image colors
  --tile           Split into tiled pages
  --no-density     Skip density reduction
  --density-target Custom density target (0.0-1.0)
  --labels         Semicolon-separated braille labels
  --analyze        Analyze without converting
  --quality        Quality-check output image
  --json           Machine-readable JSON output
  --no-history     Skip history tracking
```
