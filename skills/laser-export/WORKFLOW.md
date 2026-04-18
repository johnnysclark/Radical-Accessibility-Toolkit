# Laser Export Workflow (operator-facing)

Step-by-step for preparing a Rhino model for the Siebel Center for Design 24″ × 40″ laser cutter. Read the color/layer spec in [SKILL.md](SKILL.md) first if you haven't.

## 1 · Open Rhino on the correct file

Use the `.3dm` you've been modeling in.

Confirm that `Cut Layer`, `Engrave Layer`, and `Artboard` exist in the Layers panel. They're created automatically at Rhino startup by `tools/rhino/startup.py`. If they're missing, run this in the Rhino Python editor:

    import laser_setup
    laser_setup.ensure_layers()

The `Artboard` layer will contain a 24″ × 40″ reference rectangle at world origin (landscape, 40″ along X). It's non-plotting — it will not export.

## 2 · Decide: flat linework, projected drawing, or unfolded 3D?

The laser output is always 2D curves, but the question is where those curves come from. Pick by intent:

- **Flat linework** — you already have 2D curves drawn in plan. Skip to **3a**.
- **Make2D** — you have 3D geometry and want a *drawing* of it (site plan, elevation, section, any single-viewpoint projection). Skip to **3b**.
- **Unroll** — you have 3D solids and want a *physical model* of them (chipboard massing, folded paper, assembly pieces that glue edge-to-edge to rebuild the 3D form). Skip to **3c**.

Make2D and Unroll look similar on the surface — both consume 3D and produce cuttable 2D curves — but they answer different questions. Make2D says "what does this *look like* from over there?" Unroll says "what are all the *panels* that make up this object?" A site plan is Make2D. A chipboard model of a building is Unroll. A site plan *with* a chipboard building on it is both, run in sequence.

## 3a · Stage flat linework

1. In Rhino, **select** the curves you want to cut.
2. Run in the Python editor (or a script alias):

       import laser_prep_selection
       laser_prep_selection.stage("cut")

   Options for the argument: `"cut"`, `"engrave"`, `"vector_engrave"`.

3. Repeat for each operation type. Selection is preserved across stages so you can iterate.

## 3b · Flatten 3D geometry with Make2D

Use when the deliverable is a 2D drawing of a 3D scene.

1. Set the viewport you want to project FROM (usually Top, Front, or a custom named view).
2. **Select** the 3D objects you want to flatten.
3. Run:

       import laser_prep_make2d
       laser_prep_make2d.make2d_and_stage("cut")

4. Rhino runs `_-Make2D`, keeps the visible lines (hidden / dashed / clipping are discarded for laser use), and moves them onto `Cut Layer`.

## 3c · Unfold 3D geometry with Unroll

Use when the deliverable is a physical model whose panels you will cut and glue to reconstruct the 3D form.

1. **Select** the 3D solids (closed polysurfaces or extrusions) you want to unfold.
2. Run, passing the scale you plan to export at:

       import laser_prep_unroll
       laser_prep_unroll.unroll_and_stage("cut", scale_den=48)

   The `scale_den` argument matters here in a way it doesn't for Make2D: Unroll back-computes the gap between unfolded faces (default 0.25" in the final AI) into doc-units at the given print scale, so the laid-out faces land at the requested spacing in the exported file. Pass the same `scale_den` you will use in step 5.

3. Each selected solid is unrolled with faces exploded. The module prints `OK:` or `SKIPPED:` per piece — non-developable surfaces (doubly-curved BREPs, complex sweeps) will be skipped with a reason. All faces, *including bottom faces*, are kept; prune in Rhino before export if your chipboard workflow doesn't want them.

4. Pieces are row-packed (first-fit decreasing, tallest first) into the bed's footprint at the target scale. Expect a `WARN:` if the packed extent exceeds the bed — that means the scale is too large for the selection and you need a larger denominator.

## 4 · Arrange on the artboard

Move / rotate / scale your staged geometry so it fits inside the 24″ × 40″ `Artboard` rectangle. **Don't touch the edges** — the shop specifies a margin.

Because Rhino model units are feet, the bed rectangle is 2 ft × 3.333 ft (= 24 in × 40 in) at 1:1 scale. At 1:100, you'd expect to fit a 200 ft × 333 ft design inside it.

## 5 · Export to .ai

1. Optionally select just what you want to export (to export a subset). Otherwise pass `selection_only=False` to grab everything on `Cut Layer` and `Engrave Layer`.
2. Run, picking the scale:

       import laser_export
       laser_export.export_laser_ai("C:/tmp/plaza_cut_A.ai", 1, 100)

3. The exporter runs Rhino's `-_Export` and then immediately patches the `.ai` in place. What you get back is a file with the correct 40 × 24 inch artboard, RGB color mode, RGB `(255, 0, 0)` cut strokes at 0.001" stroke weight, and the `Cut Layer` / `Engrave Layer` layer names preserved. The Rhino source `.3dm` is unchanged — the pre-scale used for the AI math is undone before the function returns.

## 6 · Verify in Illustrator and hand to the shop

The exported `.ai` is already shop-ready — the post-processor encoded every SCD requirement into the file. You do **not** need to open the shop's `.ait` template as part of this workflow.

1. Open the exported `.ai` in Adobe Illustrator.
2. Sanity check:
   - Artboard reads 40 × 24 in.
   - Document color mode is RGB (Window → Document Info, or File → Document Color Mode).
   - Layers panel shows `Cut Layer` and `Engrave Layer` at the top level.
   - Red strokes are exactly RGB `(255, 0, 0)`, green strokes `(0, 255, 0)`, at 0.001 in stroke weight.
   - Geometry sits inside the artboard with a margin from every edge.
3. Hand the file to the shop during open hours.

If any of those checks fail, something in the export pipeline is off — see the Troubleshooting section below and, as a fallback, the shop's distributed `24x40in_laser_template--SCD.ait` template is the authoritative spec you can compare against.

## Troubleshooting

**Layers don't exist after startup.** Run `laser_setup.ensure_layers()` manually. If still failing, check that `tools/rhino/laser-export/` is on Rhino's Python path (the startup.py hook adds `tools/rhino/` — laser-export should be importable from there).

**Artboard opens at 8.5 × 11 in Illustrator.** The post-processor wasn't applied. Make sure `laser_ai_postprocess.py` is next to `laser_export.py` on disk; the export function imports it as `import laser_ai_postprocess as _ai` and calls `_ai.fix_ai_file(path, W, H)` after Rhino's `-_Export` returns. If you only have the old `laser_export.py`, re-pull this folder.

**Red strokes look pink or dull, or colors are CMYK.** Same cause: post-processor skipped. Verify by reading the exported `.ai`'s header — it should contain `%AI9_ColorModel: 1` and `%AI7_ArtboardBox: 0 0 2880 1728`. If those headers are missing, rerun through `laser_export.export_laser_ai(...)` or call `laser_ai_postprocess.fix_ai_file(path)` directly on the file.

**Strokes come in at 0.7087 pt instead of 0.001".** Same cause — post-processor swaps Rhino's default `1.0000 w` for `0.0720 w` (= 0.001" at 72 pt/in). If you see 0.7087 pt, the patch didn't run.

**Vector-engrave (green) object still looks black.** The color override didn't stick at the Rhino end. Re-run `laser_prep_selection.stage("vector_engrave")` on that selection — it sets the object color to RGB (0, 255, 0) so the post-processor's pure-green substitution applies.

**Geometry bigger than the bed.** The exporter warns but doesn't block. Either scale your selection down in Rhino (one-time, before export) or pick a higher scale denominator (e.g. 1:200 instead of 1:100).

**Unroll skipped a piece.** The module printed a `SKIPPED:` line because `rs.UnrollSurface` refused to unfold that solid — almost always a doubly-curved surface (blob, NURBS with mixed curvature) that isn't developable. Options: rebuild the surface as a developable form (single-direction curvature) in Rhino; split it at the problem seam; or fall back to Make2D for that one piece and unfold the rest.

**Unrolled pieces don't fit the bed at the chosen scale.** The module printed a `WARN:` with the actual packed extent. Use a larger denominator (1:96 instead of 1:48, etc.) or reshape the widest unrolled strip by hand before running export — typically the longest strip belongs to a single solid whose faces would pack much tighter in a grid than a row.
