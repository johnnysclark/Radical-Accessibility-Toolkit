---
name: laser-export
description: Rhino → Adobe Illustrator (.ai) export for the Siebel Center for Design 24″×40″ laser cutter. Sets up Cut Layer / Engrave Layer in the active Rhino document, stages selected or Make2D-projected geometry onto the right layer with the right color/stroke, then drives Rhino's native -_Export to write a shop-ready .ai (correct artboard, RGB mode, layer names, stroke weights — no Illustrator cleanup). Trigger when the user mentions "laser cut", "SCD laser", "24x40 laser", "Siebel Center laser", ".ai export from Rhino", or "cut layer / engrave layer setup".
---

# Laser Export Skill

This skill prepares and exports Rhino drawings for the Siebel Center for Design (SCD) laser cutter at UIUC. The SCD shop expects:

- **Artboard:** 24″ × 40″ (610 × 1016 mm), geometry inset from the edges.
- **Layer names in the .ai file:**
  - `Cut Layer` — full cut operation
  - `Engrave Layer` — general engrave *and* vector engrave (vector engrave is identified by an object-level green stroke, not a separate layer)
- **Stroke colors (literal RGB, not CMYK — the shop's action script reads RGB):**
  - Full cut: `rgb(255, 0, 0)` at 0.001″ / 0.014 mm stroke
  - General engrave: `rgb(0, 0, 0)` or grays, any stroke
  - Vector engrave: `rgb(0, 255, 0)` at 0.001″ / 0.014 mm stroke
- **Shop spec reference:** the SCD shop distributes an Illustrator template, `24x40in_laser_template--SCD.ait`, that encodes the above (artboard size, layer names, stroke colors, stroke weights). The skill's post-processor bakes the same spec into every exported `.ai`, so you do **not** need the template in the normal workflow — the exported file is submit-ready on its own. The template is handy only as a human-readable reference if you want to see the spec with your own eyes, or as a fallback if the post-processor ever lags behind a shop spec change.

## What this skill does

The underlying code lives at `tools/rhino/laser-export/` (IronPython 2.7 modules that run inside Rhino). This SKILL.md is the Claude-facing wrapper.

When triggered, Claude should:

1. **Confirm the shape of the request** — is the user staging new linework, Make2D-flattening 3D geometry, or just exporting what's already staged?
2. **Guide the user through the right step** using the operator-facing [WORKFLOW.md](WORKFLOW.md). Quick reference is in [quick-start.md](quick-start.md).
3. **If Rhino is not running** or the layers don't exist, point the user at `tools/rhino/startup.py` (which calls `laser_setup.ensure_layers()` automatically at Rhino launch) or have them run `import laser_setup; laser_setup.ensure_layers()` manually.
4. **When invoking the export**, ensure the user has specified a scale (no default). Common choices:
   - `1, 100` → 1:100 metric (good default for site plans)
   - `1, 48` → ¼″ = 1′-0″ (common US architectural plan)
   - `1, 192` → 1⁄16″ = 1′-0″ (site plan)

## Entry points (IronPython, run inside Rhino)

```python
import laser_setup
import laser_prep_selection
import laser_prep_make2d
import laser_prep_unroll
import laser_export
import laser_ai_postprocess                             # used internally by laser_export; also callable on its own to re-patch an older .ai

laser_setup.ensure_layers()                             # idempotent, OK to run anytime
laser_prep_selection.stage("cut")                       # flat linework: select first, then run
laser_prep_selection.stage("engrave")
laser_prep_selection.stage("vector_engrave")            # green-stroked on Engrave Layer
laser_prep_make2d.make2d_and_stage("cut")               # 3D -> projected drawing (site plan, elevation)
laser_prep_unroll.unroll_and_stage("cut", scale_den=48) # 3D -> unfolded panels (chipboard massing model)
laser_export.export_laser_ai(path, num, den)            # e.g. export_laser_ai("C:/x.ai", 1, 100)
```

`make2d_and_stage` and `unroll_and_stage` answer different questions about the same 3D geometry — the first gives a *drawing* of the object from one viewpoint, the second gives the *panels* that could rebuild it in chipboard. Pick by what you're handing to the laser.

## What the exporter hands the user

`laser_export.export_laser_ai(...)` produces an `.ai` that opens in Illustrator with every SCD-spec requirement already applied. The user should NOT have to change color mode, recolor strokes, resize the artboard, or touch stroke weight in Illustrator — those are the five things Rhino's own AI exporter gets wrong, and `laser_ai_postprocess.py` patches them on the way out. See `tools/rhino/laser-export/README.md` for the full defect-and-fix table.

If the user reports that the `.ai` opens on an 8.5 × 11 artboard, imports in CMYK, or shows 0.7087 pt strokes, the post-processor is being bypassed — check that `laser_ai_postprocess.py` is importable from the same folder as `laser_export.py` and that the export path is actually being written before the patch step.

## Not in scope

- Kerf compensation / offsetting curves for material thickness — user handles in Illustrator.
- Auto-nesting multiple pieces on one artboard — user arranges manually.
- Generating geometry from `state.json` (Layout Jig) for laser output — this skill is Rhino-native; it does not touch state.json.
