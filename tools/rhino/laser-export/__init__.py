# Laser Export -- SCD 24x40 laser cutter workflow for Rhino.
# Entry points:
#   laser_setup.ensure_layers()           -- create Cut Layer / Engrave Layer / Artboard
#   laser_prep_selection.stage(op)        -- move selection onto a laser layer
#   laser_prep_make2d.make2d_and_stage    -- Make2D + stage (drawing-type output)
#   laser_prep_unroll.unroll_and_stage    -- unfold 3D solids + stage (physical-model output)
#   laser_export.export_laser_ai(...)     -- export selection to .ai at a given scale,
#                                            then auto-patch for SCD spec
#   laser_ai_postprocess.fix_ai_file(...) -- standalone: re-patch an older .ai
