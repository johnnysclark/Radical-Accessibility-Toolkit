# tools/rhino/laser-export/

Rhino-side IronPython code that prepares and exports geometry for the Siebel Center for Design (SCD) 24″ × 40″ laser cutter.

This is the **code layer**. The **Claude-invocable skill** that wraps it lives at `skills/laser-export/SKILL.md`. See the skill's `WORKFLOW.md` for the step-by-step operator guide.

## Files

| File | Role |
| --- | --- |
| `laser_setup.py` | Creates `Cut Layer`, `Engrave Layer`, `Artboard` in the active document. Idempotent. Invoked at Rhino startup via `tools/rhino/startup.py`. |
| `laser_prep_selection.py` | Moves the current selection onto `Cut Layer` / `Engrave Layer`, with the right color-source and (for vector engrave) explicit green stroke. |
| `laser_prep_make2d.py` | Runs Rhino `_-Make2D` on the current selection, discards hidden lines, then stages the visible output curves. Use when the deliverable is a *drawing* of the 3D geometry. |
| `laser_prep_unroll.py` | Runs `rs.UnrollSurface(explode=True)` on each selected 3D solid, extracts exterior borders, row-packs the pieces into the scaled bed, stages the curves. Use when the deliverable is a *physical model* built from the unfolded panels. |
| `laser_export.py` | Drives Rhino `-_Export` to write an `.ai` file at a caller-specified scale, then patches the file to match the SCD shop spec. |
| `laser_ai_postprocess.py` | Text-substitution pass that fixes the five defects in Rhino's AI output (artboard, color mode, CMYK→RGB, stroke weight, bounding box). Called automatically by `laser_export.py`. |

## SCD color/operation spec (for reference)

| Operation | RGB | Stroke | Where |
| --- | --- | --- | --- |
| Full cut | (255, 0, 0) | 0.001″ / 0.014 mm | `Cut Layer` (ByLayer) |
| General engrave | (0, 0, 0) + grays | any | `Engrave Layer` (ByLayer) |
| Vector engrave | (0, 255, 0) | 0.001″ / 0.014 mm | `Engrave Layer`, object-color override |

Bed: 24″ × 40″ (610 × 1016 mm). Geometry must not touch the bed edges.

## Quick use inside Rhino

```python
import laser_setup, laser_prep_selection, laser_prep_make2d, laser_prep_unroll, laser_export

# one time (also happens at startup)
laser_setup.ensure_layers()

# flat linework you already have:
# (select first, then)
laser_prep_selection.stage("cut")
laser_prep_selection.stage("engrave")
laser_prep_selection.stage("vector_engrave")

# 3D -> drawing (site plan, elevation, section):
# (select 3D, pick the projection viewport, then)
laser_prep_make2d.make2d_and_stage("cut")

# 3D -> unfolded panels (chipboard massing model):
# (select closed polysurfaces/extrusions, then)
laser_prep_unroll.unroll_and_stage("cut", scale_den=48)

# export
laser_export.export_laser_ai("C:/tmp/out.ai", 1, 48)   # 1/4" = 1'-0"
```

## What Rhino's AI exporter gets wrong (and how we fix it)

Rhino's legacy `-_Export` to `.ai` writes a valid AI3 PostScript file but with five defects that break the SCD shop workflow. `laser_ai_postprocess.fix_ai_file` patches all five in one text pass.

| Defect | Symptom in Illustrator | Fix |
| --- | --- | --- |
| No `%AI7_ArtboardBox` header | Artboard opens at 8.5 × 11 Letter instead of 40 × 24. | Inject `%AI7_ArtboardBox`, `%AI5_ArtSize`, `%AI5_RulerUnits` headers. Also correct `%AI3_TileBox` and `%AI3_TemplateBox`. |
| `%%BoundingBox` wraps geometry, not artboard | Bounding box shrinks to the drawn content. | Rewrite both `%%BoundingBox` and `%%HiResBoundingBox` to the artboard. |
| No `%AI9_ColorModel` header; CMYK `K`/`k` color operators | Illustrator opens in CMYK mode; red shows as muddy `(237, 28, 36)` instead of `(255, 0, 0)`. SCD action script fails. | Add `%AI9_ColorModel: 1`, substitute CMYK `K`/`k` operators with RGB `XA`/`Xa` operators for pure red, green, and black. |
| Writes `1.0000 w` for every stroke, ignoring PlotWeight | Strokes import at 0.7087 pt (≈ 0.25 mm); laser rejects as too thick. | Replace `1.0000 w` with `0.0720 w` (= 0.001 inch at 72 pt/in). |
| Writes 36 pt per doc unit instead of 72 pt per inch | Everything is half size on paper. | `laser_export.py` pre-scales the selection by `2 × inches-per-doc-unit × num/den` before `-_Export`, then undoes the scale. |

All five fixes run automatically from `laser_export.export_laser_ai(...)`. You don't invoke the post-processor directly unless you're reprocessing an older `.ai`.

## Units

Rhino model units are feet (set in `startup.py`). The artboard rectangle is drawn at model scale (40″ along X, 24″ along Y = 3.333 ft × 2 ft). Print scale is passed to `export_laser_ai(path, num, den)` and handled via the pre-scale step described above; the source `.3dm` geometry is restored before the function returns.
