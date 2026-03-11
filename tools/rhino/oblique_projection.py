# Oblique Projection — paste into Rhino EditPythonScript and hit Run
# Copies selected 3D objects, applies oblique projection, ready for Make2D
#
# Features:
#   - Presets: cavalier, cabinet, military, isometric, or custom
#   - Plan oblique (true plan) or elevation oblique (true elevation)
#   - Depth scale (1.0 = cavalier full depth, 0.5 = cabinet half depth)
#   - Section cut at a given height
#   - Ground plane reference grid

import math
import rhinoscriptsyntax as rs
import Rhino

# ================================================================
# PRESETS
# ================================================================
PRESETS = {
    0: {"name": "Cavalier 45",  "plan": True,  "sx": 45, "sy": 0,  "rot": 0,  "dp": 1.0},
    1: {"name": "Cabinet 45",   "plan": True,  "sx": 45, "sy": 0,  "rot": 0,  "dp": 0.5},
    2: {"name": "Military",     "plan": True,  "sx": 45, "sy": 45, "rot": 45, "dp": 1.0},
    3: {"name": "Isometric 30", "plan": True,  "sx": 30, "sy": 30, "rot": 0,  "dp": 1.0},
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
    preset_names = ["Cavalier 45 (plan oblique, full depth)",
                    "Cabinet 45 (plan oblique, half depth)",
                    "Military (plan oblique, 45/45, rotated 45)",
                    "Isometric-ish (plan oblique, 30/30)",
                    "Custom (set all values manually)"]
    pick = rs.ListBox(preset_names, "Pick a projection preset", "Oblique Projection")

    if pick is not None:
        preset_idx = preset_names.index(pick)

        if preset_idx <= 3:
            p = PRESETS[preset_idx]
            sx = p["sx"]
            sy = p["sy"]
            rot = p["rot"]
            is_plan = p["plan"]
            dp = p["dp"]
            mode_name = p["name"]
        else:
            # custom mode
            mode_pick = rs.ListBox(["Plan oblique (true plan on top)",
                                     "Elevation oblique (true front elevation)"],
                                    "Projection mode", "Mode")
            if mode_pick is None:
                print("Cancelled.")
                is_plan = None
            else:
                is_plan = mode_pick.startswith("Plan")
                sx = rs.GetReal("Shear angle X degrees", 30.0, 0.0, 89.0)
                sy = rs.GetReal("Shear angle Y degrees", 30.0, 0.0, 89.0)
                rot = rs.GetReal("Rotation around Z degrees", 0.0, -360.0, 360.0)
                dp = rs.GetReal("Depth scale (1.0=full, 0.5=half)", 1.0, 0.01, 1.0)
                if is_plan:
                    mode_name = "Plan oblique (custom)"
                else:
                    mode_name = "Elevation oblique (custom)"

        if is_plan is not None and sx is not None and sy is not None and rot is not None and dp is not None:

            # ========================================================
            # SECTION CUT
            # ========================================================
            do_cut = rs.MessageBox("Apply a section cut?", 4, "Section Cut") == 6
            cut_h = 0.0
            if do_cut:
                if is_plan:
                    cut_h = rs.GetReal("Cut height (Z)", 0.0)
                else:
                    cut_h = rs.GetReal("Cut depth (Y)", 0.0)
                if cut_h is None:
                    do_cut = False

            # ========================================================
            # GROUND GRID
            # ========================================================
            do_grid = rs.MessageBox("Add ground plane grid?", 4, "Grid") == 6
            grid_sp = 10.0
            if do_grid:
                grid_sp = rs.GetReal("Grid spacing", 10.0, 0.1, 10000.0)
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

            shear_xform = Rhino.Geometry.Transform.Identity
            if is_plan:
                shear_xform.M02 = math.tan(math.radians(sx)) * dp
                shear_xform.M12 = math.tan(math.radians(sy)) * dp
            else:
                shear_xform.M01 = math.tan(math.radians(sx)) * dp
                shear_xform.M21 = math.tan(math.radians(sy)) * dp

            combined = shear_xform * rot_xform

            # ========================================================
            # LAYERS
            # ========================================================
            if not rs.IsLayer("OBLIQUE_PROJECTION"):
                rs.AddLayer("OBLIQUE_PROJECTION")
            if do_grid and not rs.IsLayer("OBLIQUE_GRID"):
                rs.AddLayer("OBLIQUE_GRID")

            rs.EnableRedraw(False)
            tol = rs.UnitAbsoluteTolerance()

            # ========================================================
            # SECTION CUT — trim copies before transforming
            # ========================================================
            copied = rs.CopyObjects(obj_ids)
            work_ids = []

            if do_cut:
                if is_plan:
                    cut_pt = Rhino.Geometry.Point3d(0, 0, cut_h)
                    cut_normal = Rhino.Geometry.Vector3d.ZAxis
                else:
                    cut_pt = Rhino.Geometry.Point3d(0, cut_h, 0)
                    cut_normal = Rhino.Geometry.Vector3d.YAxis
                cut_plane = Rhino.Geometry.Plane(cut_pt, cut_normal)

                for obj_id in copied:
                    brep = rs.coercebrep(obj_id)
                    if brep:
                        # Trim keeps positive side (where normal points)
                        # We want below cut, so flip normal
                        flip_plane = Rhino.Geometry.Plane(cut_pt, -cut_normal)
                        trimmed = brep.Trim(flip_plane, tol)
                        if trimmed and len(trimmed) > 0:
                            rs.DeleteObject(obj_id)
                            for t in trimmed:
                                new_id = rs.coerceguid(
                                    Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(t)
                                )
                                if new_id:
                                    work_ids.append(new_id)
                        else:
                            # entirely on one side — check if on kept side
                            obj_bb = rs.BoundingBox([obj_id])
                            if obj_bb:
                                if is_plan:
                                    keep = obj_bb[6][2] <= cut_h + tol
                                else:
                                    keep = obj_bb[6][1] <= cut_h + tol
                                if keep:
                                    work_ids.append(obj_id)
                                else:
                                    rs.DeleteObject(obj_id)
                            else:
                                work_ids.append(obj_id)
                    else:
                        mesh = rs.coercemesh(obj_id)
                        if mesh:
                            if is_plan:
                                split_plane = Rhino.Geometry.Plane(
                                    cut_pt, Rhino.Geometry.Vector3d.ZAxis)
                            else:
                                split_plane = Rhino.Geometry.Plane(
                                    cut_pt, Rhino.Geometry.Vector3d.YAxis)
                            parts = mesh.Split(split_plane)
                            if parts and len(parts) > 0:
                                rs.DeleteObject(obj_id)
                                for part in parts:
                                    pbb = part.GetBoundingBox(True)
                                    if is_plan:
                                        keep = pbb.Center.Z <= cut_h + tol
                                    else:
                                        keep = pbb.Center.Y <= cut_h + tol
                                    if keep:
                                        new_id = rs.coerceguid(
                                            Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(part)
                                        )
                                        if new_id:
                                            work_ids.append(new_id)
                            else:
                                work_ids.append(obj_id)
                        else:
                            # curves, points, etc — keep as-is
                            work_ids.append(obj_id)
            else:
                work_ids = list(copied)

            # ========================================================
            # TRANSFORM
            # ========================================================
            for obj_id in work_ids:
                rs.TransformObject(obj_id, combined)
                rs.ObjectLayer(obj_id, "OBLIQUE_PROJECTION")

            # ========================================================
            # GROUND GRID
            # ========================================================
            grid_count = 0
            if do_grid:
                if is_plan:
                    x0 = math.floor(bb_min.X / grid_sp) * grid_sp - grid_sp
                    x1 = math.ceil(bb_max.X / grid_sp) * grid_sp + grid_sp
                    y0 = math.floor(bb_min.Y / grid_sp) * grid_sp - grid_sp
                    y1 = math.ceil(bb_max.Y / grid_sp) * grid_sp + grid_sp
                    x = x0
                    while x <= x1:
                        pt_a = Rhino.Geometry.Point3d(x, y0, 0)
                        pt_b = Rhino.Geometry.Point3d(x, y1, 0)
                        pt_a.Transform(combined)
                        pt_b.Transform(combined)
                        gid = rs.AddLine(pt_a, pt_b)
                        rs.ObjectLayer(gid, "OBLIQUE_GRID")
                        grid_count += 1
                        x += grid_sp
                    y = y0
                    while y <= y1:
                        pt_a = Rhino.Geometry.Point3d(x0, y, 0)
                        pt_b = Rhino.Geometry.Point3d(x1, y, 0)
                        pt_a.Transform(combined)
                        pt_b.Transform(combined)
                        gid = rs.AddLine(pt_a, pt_b)
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
                        pt_a = Rhino.Geometry.Point3d(x, 0, z0)
                        pt_b = Rhino.Geometry.Point3d(x, 0, z1)
                        pt_a.Transform(combined)
                        pt_b.Transform(combined)
                        gid = rs.AddLine(pt_a, pt_b)
                        rs.ObjectLayer(gid, "OBLIQUE_GRID")
                        grid_count += 1
                        x += grid_sp
                    z = z0
                    while z <= z1:
                        pt_a = Rhino.Geometry.Point3d(x0, 0, z)
                        pt_b = Rhino.Geometry.Point3d(x1, 0, z)
                        pt_a.Transform(combined)
                        pt_b.Transform(combined)
                        gid = rs.AddLine(pt_a, pt_b)
                        rs.ObjectLayer(gid, "OBLIQUE_GRID")
                        grid_count += 1
                        z += grid_sp

            rs.EnableRedraw(True)
            rs.ZoomExtents()

            # ========================================================
            # REPORT
            # ========================================================
            print("OK: {0}".format(mode_name))
            print("  Shear X={0}, Shear Y={1}, Rotation={2}, Depth={3}".format(sx, sy, rot, dp))
            print("  {0} objects on layer OBLIQUE_PROJECTION.".format(len(work_ids)))
            if do_cut:
                print("  Section cut at {0}.".format(cut_h))
            if do_grid:
                print("  {0} grid lines on layer OBLIQUE_GRID.".format(grid_count))
            print("  Run Make2D on the result for a 2D oblique drawing.")
            print("READY:")
