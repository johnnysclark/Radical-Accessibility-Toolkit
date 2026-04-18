# Laser Export — Quick Start

Five-line cheatsheet. See [WORKFLOW.md](WORKFLOW.md) for the full walkthrough.

```python
import laser_setup, laser_prep_selection, laser_prep_make2d, laser_prep_unroll, laser_export

laser_setup.ensure_layers()                              # one time per doc
# select objects in Rhino, then pick exactly one of:
laser_prep_selection.stage("cut")                        # flat linework already drawn
laser_prep_make2d.make2d_and_stage("cut")                # 3D -> drawing (site plan, elevation, section)
laser_prep_unroll.unroll_and_stage("cut", scale_den=100) # 3D -> panels to rebuild in chipboard
# then:
laser_export.export_laser_ai("C:/tmp/out.ai", 1, 100)    # scale 1:100
```

Open the result in Illustrator. The exporter already applies the SCD spec: artboard 40 × 24 in, RGB color mode, RGB `(255, 0, 0)` cut strokes at 0.001", green `(0, 255, 0)` for vector engrave, `Cut Layer` / `Engrave Layer` names preserved. No manual cleanup, no need to touch the shop's `.ait` template — hand the `.ai` to the shop as-is.

If any of those are off when you open the `.ai`, the post-processor was skipped — see the SKILL troubleshooting section.
