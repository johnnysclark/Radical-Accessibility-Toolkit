# Oblique Projection — paste into Rhino EditPythonScript and hit Run
# Copies selected 3D objects, applies oblique projection, ready for Make2D
#
# Features:
#   - Presets: cavalier 45, cabinet 45, cabinet 30, military
#   - Plan oblique (true plan) or elevation oblique (true elevation)
#   - Receding angle + depth scale (cleaner than raw shear values)
#   - Section cut on any axis at any location
#   - Ground plane reference grid (24" on center default)

import math
import rhinoscriptsyntax as rs
import Rhino

# ================================================================
# PRESETS
# ================================================================
PRESETS = {
    0: {"name": "Cavalier 45",  "plan": True,  "angle": 45, "dp": 1.0, "rot": 0},
    1: {"name": "Cabinet 45",   "plan": True,  "angle": 45, "dp": 0.5, "rot": 0},
    2: {"name": "Cabinet 30",   "plan": True,  "angle": 30, "dp": 0.5, "rot": 0},
    3: {"name": "Military",     "plan": True,  "angle": 90, "dp": 1.0, "rot": 45},
}

# ================================================================
# SELECT OBJECTS
# ================================================================
obj_ids = rs.GetObjects("Select objects for oblique projection", preselect=True)
if not obj_ids:
    print("Nothing selected.")

else:
    # ============================================================
    # CHOOSE PRESET OR CUSTOM
    # ============================================================
    preset_names = [
        "Cavalier 45 (plan oblique, full depth, receding at 45 deg)",
        "Cabinet 45 (plan oblique, half depth, receding at 45 deg)",
        "Cabinet 30 (plan oblique, half depth, receding at 30 deg)",
        "Military (plan oblique, full depth, verticals straight up, plan rotated 45)",
        "Custom (set all values manually)"]
    pick = rs.ListBox(preset_names, "Pick a projection preset", "Oblique Projection")

    if pick is None:
        print("Cancelled.")
    else:
        preset_idx = preset_names.index(pick)
        cancelled = False

        if preset_idx <= 3:
            p = PRESETS[preset_idx]
            ang = p["angle"]
            dp = p["dp"]
            rot = p["rot"]
            is_plan = p["plan"]
            mode_name = p["name"]
        else:
            mode_pick = rs.ListBox(
                ["Plan oblique (true plan on top, Make2D from Top)",
                 "Elevation oblique (true front elevation, Make2D from Front)"],
                "Projection mode", "Mode")
            if mode_pick is None:
                cancelled = True
            else:
                is_plan = mode_pick.startswith("Plan")
                ang = rs.GetReal("Receding axis angle in drawing (degrees from horizontal)", 45.0, 0.0, 90.0)
                dp = rs.GetReal("Depth scale (1.0=full cavalier, 0.5=half cabinet)", 1.0, 0.01, 2.0)
                rot = rs.GetReal("Rotation around Z degrees", 0.0, -360.0, 360.0)
                if ang is None or dp is None or rot is None:
                    cancelled = True
                else:
                    mode_name = "Plan oblique (custom)" if is_plan else "Elevation oblique (custom)"

        if not cancelled:
            # ========================================================
            # SECTION CUT
            # ========================================================
            do_cut = rs.MessageBox("Apply a section cut?", 4, "Section Cut") == 6
            cut_axis = 2
            cut_h = 25.0
            if do_cut:
                axis_pick = rs.ListBox(["X axis", "Y axis", "Z axis"],
                                       "Cut plane axis", "Cut Axis")
                if axis_pick is None:
                    do_cut = False
                else:
                    cut_axis = ["X axis", "Y axis", "Z axis"].index(axis_pick)
                    axis_label = ["X", "Y", "Z"][cut_axis]
                    cut_h = rs.GetReal(
                        "Cut location along {0} axis (model is ~50ft)".format(axis_label),
                        25.0)
                    if cut_h is None:
                        do_cut = False

            # ========================================================
            # GROUND GRID
            # ========================================================
            do_grid = rs.MessageBox("Add ground plane grid? (24 in on center)", 4, "Grid") == 6
            grid_sp = 2.0
            if do_grid:
                grid_sp = rs.GetReal("Grid spacing (2.0 = 24 inches on center)", 2.0, 0.1, 100.0)
                if grid_sp is None:
                    do_grid = False

            # ========================================================
            # BOUNDING BOX CENTER
            # ========================================================
            bb = rs.BoundingBox(obj_ids)
            p0 = bb[0]
            p6 = bb[6]
            cx = (p0[0] + p6[0]) / 2.0
            cy = (p0[1] + p6[1]) / 2.0
            cz = (p0[2] + p6[2]) / 2.0
            center = Rhino.Geometry.Point3d(cx, cy, cz)

            bb_min = Rhino.Geometry.Point3d(p0[0], p0[1], p0[2])
            bb_max = Rhino.Geometry.Point3d(p6[0], p6[1], p6[2])

            # ========================================================
            # BUILD TRANSFORMS
            # ========================================================
            rot_xform = Rhino.Geometry.Transform.Rotation(
                math.radians(rot),
                Rhino.Geometry.Vector3d.ZAxis,
                center
            )

            # oblique shear using receding angle + depth scale
            ang_rad = math.radians(ang)
            shear_xform = Rhino.Geometry.Transform.Identity
            if is_plan:
                shear_xform.M02 = dp * math.cos(ang_rad)
                shear_xform.M12 = dp * math.sin(ang_rad)
            else:
                shear_xform.M01 = dp * math.cos(ang_rad)
                shear_xform.M21 = dp * math.sin(ang_rad)

            combined = shear_xform * rot_xform

            # ========================================================
            # LAYERS
            # ========================================================
            if not rs.IsLayer("OBLIQUE_PROJECTION"):
                rs.AddLayer("OBLIQUE_PROJECTION")
            if do_grid and not rs.IsLayer("OBLIQUE_GRID"):
                rs.AddLayer("OBLIQUE_GRID")

            rs.EnableRedraw(False)
            try:
                tol = rs.UnitAbsoluteTolerance()

                # ====================================================
                # SECTION CUT
                # ====================================================
                axis_vectors = [
                    Rhino.Geometry.Vector3d.XAxis,
                    Rhino.Geometry.Vector3d.YAxis,
                    Rhino.Geometry.Vector3d.ZAxis]
                cut_origins = [
                    Rhino.Geometry.Point3d(cut_h, 0, 0),
                    Rhino.Geometry.Point3d(0, cut_h, 0),
                    Rhino.Geometry.Point3d(0, 0, cut_h)]

                copied = rs.CopyObjects(obj_ids)
                work_ids = []

                if do_cut:
                    cut_pt = cut_origins[cut_axis]
                    cut_normal = axis_vectors[cut_axis]
                    # flip so Trim keeps the negative side (below/in front of cut)
                    flip_plane = Rhino.Geometry.Plane(cut_pt, -cut_normal)
                    split_plane = Rhino.Geometry.Plane(cut_pt, cut_normal)

                    for obj_id in copied:
                        brep = rs.coercebrep(obj_id)
                        # try extrusion conversion if coercebrep fails
                        if brep is None:
                            geo = rs.coercegeometry(obj_id)
                            if isinstance(geo, Rhino.Geometry.Extrusion):
                                brep = geo.ToBrep()

                        if brep is not None:
                            trimmed = brep.Trim(flip_plane, tol)
                            if trimmed and len(trimmed) > 0:
                                rs.DeleteObject(obj_id)
                                for t in trimmed:
                                    new_id = Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(t)
                                    if new_id:
                                        work_ids.append(new_id)
                            else:
                                # check if entirely on kept side
                                obj_bb = rs.BoundingBox([obj_id])
                                if obj_bb:
                                    max_val = [obj_bb[6][0], obj_bb[6][1], obj_bb[6][2]][cut_axis]
                                    if max_val <= cut_h + tol:
                                        work_ids.append(obj_id)
                                    else:
                                        rs.DeleteObject(obj_id)
                                else:
                                    work_ids.append(obj_id)
                        else:
                            mesh = rs.coercemesh(obj_id)
                            if mesh:
                                parts = mesh.Split(split_plane)
                                if parts and len(parts) > 0:
                                    rs.DeleteObject(obj_id)
                                    for part in parts:
                                        pbb = part.GetBoundingBox(True)
                                        ctr = pbb.Center
                                        ctr_val = [ctr.X, ctr.Y, ctr.Z][cut_axis]
                                        if ctr_val <= cut_h + tol:
                                            new_id = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(part)
                                            if new_id:
                                                work_ids.append(new_id)
                                else:
                                    work_ids.append(obj_id)
                            else:
                                work_ids.append(obj_id)
                else:
                    work_ids = list(copied)

                # ====================================================
                # TRANSFORM
                # ====================================================
                for obj_id in work_ids:
                    rs.TransformObject(obj_id, combined)
                    rs.ObjectLayer(obj_id, "OBLIQUE_PROJECTION")

                # ====================================================
                # GROUND GRID (24" on center = 2' spacing default)
                # ====================================================
                grid_count = 0
                if do_grid:
                    if is_plan:
                        x0 = math.floor(bb_min.X / grid_sp) * grid_sp - grid_sp
                        x1 = math.ceil(bb_max.X / grid_sp) * grid_sp + grid_sp
                        y0 = math.floor(bb_min.Y / grid_sp) * grid_sp - grid_sp
                        y1 = math.ceil(bb_max.Y / grid_sp) * grid_sp + grid_sp
                        x = x0
                        while x <= x1:
                            gid = rs.AddLine([x, y0, 0], [x, y1, 0])
                            rs.TransformObject(gid, combined)
                            rs.ObjectLayer(gid, "OBLIQUE_GRID")
                            grid_count += 1
                            x += grid_sp
                        y = y0
                        while y <= y1:
                            gid = rs.AddLine([x0, y, 0], [x1, y, 0])
                            rs.TransformObject(gid, combined)
                            rs.ObjectLayer(gid, "OBLIQUE_GRID")
                            grid_count += 1
                            y += grid_sp
                    else:
                        x0 = math.floor(bb_min.X / grid_sp) * grid_sp - grid_sp
                        x1 = math.ceil(bb_max.X / grid_sp) * grid_sp + grid_sp
                        z0 = math.floor(bb_min.Z / grid_sp) * grid_sp - grid_sp
                        z1 = math.ceil(bb_max.Z / grid_sp) * grid_sp + grid_sp
                        x = x0
                        while x <= x1:
                            gid = rs.AddLine([x, 0, z0], [x, 0, z1])
                            rs.TransformObject(gid, combined)
                            rs.ObjectLayer(gid, "OBLIQUE_GRID")
                            grid_count += 1
                            x += grid_sp
                        z = z0
                        while z <= z1:
                            gid = rs.AddLine([x0, 0, z], [x1, 0, z])
                            rs.TransformObject(gid, combined)
                            rs.ObjectLayer(gid, "OBLIQUE_GRID")
                            grid_count += 1
                            z += grid_sp

            finally:
                rs.EnableRedraw(True)

            rs.ZoomExtents()

            # ========================================================
            # REPORT
            # ========================================================
            view = "Top" if is_plan else "Front"
            print("OK: {0}".format(mode_name))
            print("  Receding angle={0} deg, Depth scale={1}, Rotation={2}".format(ang, dp, rot))
            print("  {0} objects on layer OBLIQUE_PROJECTION.".format(len(work_ids)))
            if do_cut:
                axis_label = ["X", "Y", "Z"][cut_axis]
                print("  Section cut: {0}={1}.".format(axis_label, cut_h))
            if do_grid:
                print("  {0} grid lines on layer OBLIQUE_GRID.".format(grid_count))
            print("  Run Make2D from {0} view.".format(view))
            print("READY:")
