# Oblique Projection — GhPython component
# Paste into a GhPython Script component in Grasshopper.
#
# INPUTS (right-click component, rename inputs, set type hints):
#   geo      — list access, type hint: GeometryBase
#   preset   — int, slider -1 to 3   (-1=custom, 0=cavalier, 1=cabinet, 2=military, 3=isometric)
#   shear_x  — float, slider 0 to 89  (used when preset=-1)
#   shear_y  — float, slider 0 to 89  (used when preset=-1)
#   rotation — float, slider 0 to 360 (used when preset=-1)
#   plan_ob  — bool toggle             (used when preset=-1)
#   depth    — float, slider 0 to 1    (1=cavalier full depth, 0.5=cabinet half depth)
#   cut      — bool toggle             (section cut on/off)
#   cut_h    — float, slider           (cut height — Z for plan, Y for elevation)
#   grid_on  — bool toggle             (ground plane grid on/off)
#   grid_sp  — float, slider 1 to 100  (grid spacing)
#
# OUTPUTS (right-click component, rename outputs):
#   a    — projected geometry
#   b    — ground grid lines (when grid_on=True)
#   info — text summary

import math
import Rhino.Geometry as rg

# ================================================================
# PRESETS
# ================================================================
PRESETS = {
    0: {"name": "Cavalier 45",  "plan_ob": True,  "sx": 45, "sy": 0,  "rot": 0,  "depth": 1.0},
    1: {"name": "Cabinet 45",   "plan_ob": True,  "sx": 45, "sy": 0,  "rot": 0,  "depth": 0.5},
    2: {"name": "Military",     "plan_ob": True,  "sx": 45, "sy": 45, "rot": 45, "depth": 1.0},
    3: {"name": "Isometric 30", "plan_ob": True,  "sx": 30, "sy": 30, "rot": 0,  "depth": 1.0},
}

# ================================================================
# DEFAULTS
# ================================================================
if preset is None:  preset = -1
if shear_x is None: shear_x = 30.0
if shear_y is None: shear_y = 30.0
if rotation is None: rotation = 0.0
if plan_ob is None: plan_ob = False
if depth is None:   depth = 1.0
if cut is None:     cut = False
if cut_h is None:   cut_h = 0.0
if grid_on is None: grid_on = False
if grid_sp is None: grid_sp = 10.0

# ================================================================
# RESOLVE PRESET vs CUSTOM
# ================================================================
if preset in PRESETS:
    p = PRESETS[preset]
    sx = p["sx"]
    sy = p["sy"]
    rot = p["rot"]
    is_plan = p["plan_ob"]
    dp = p["depth"]
    mode_name = p["name"]
else:
    sx = shear_x
    sy = shear_y
    rot = rotation
    is_plan = plan_ob
    dp = depth
    mode_name = "Plan oblique (custom)" if is_plan else "Elevation oblique (custom)"

# ================================================================
# MAIN
# ================================================================
if geo is None:
    a = None
    b = None
    info = "No geometry connected."
else:
    if not hasattr(geo, '__iter__'):
        geo = [geo]

    tol = 0.001

    # -- bounding box center as pivot --
    all_pts = []
    for g in geo:
        gbb = g.GetBoundingBox(True)
        all_pts.append(gbb.Min)
        all_pts.append(gbb.Max)
    union_bb = rg.BoundingBox(all_pts)
    center = union_bb.Center

    # ============================================================
    # SECTION CUT (before transform — cut the real 3D model)
    # ============================================================
    work = []
    if cut:
        if is_plan:
            cut_plane = rg.Plane(rg.Point3d(0, 0, cut_h), -rg.Vector3d.ZAxis)
        else:
            cut_plane = rg.Plane(rg.Point3d(0, cut_h, 0), -rg.Vector3d.YAxis)

        for g in geo:
            if isinstance(g, rg.Brep):
                trimmed = g.Trim(cut_plane, tol)
                if trimmed and len(trimmed) > 0:
                    work.extend(trimmed)
                else:
                    # trim returned nothing — object may be entirely on kept side
                    gbb = g.GetBoundingBox(True)
                    if is_plan:
                        if gbb.Max.Z <= cut_h + tol:
                            work.append(g)
                    else:
                        if gbb.Max.Y <= cut_h + tol:
                            work.append(g)
            elif isinstance(g, rg.Mesh):
                parts = g.Split(cut_plane)
                if parts and len(parts) > 0:
                    for part in parts:
                        pc = part.GetBoundingBox(True).Center
                        if is_plan:
                            if pc.Z <= cut_h + tol:
                                work.append(part)
                        else:
                            if pc.Y <= cut_h + tol:
                                work.append(part)
                else:
                    work.append(g)
            else:
                work.append(g)
    else:
        work = list(geo)

    # ============================================================
    # BUILD TRANSFORMS
    # ============================================================
    # rotation
    rot_xform = rg.Transform.Rotation(
        math.radians(rot),
        rg.Vector3d.ZAxis,
        center
    )

    # shear with depth scale
    shear_xform = rg.Transform.Identity
    if is_plan:
        shear_xform.M02 = math.tan(math.radians(sx)) * dp
        shear_xform.M12 = math.tan(math.radians(sy)) * dp
    else:
        shear_xform.M01 = math.tan(math.radians(sx)) * dp
        shear_xform.M21 = math.tan(math.radians(sy)) * dp

    combined = shear_xform * rot_xform

    # ============================================================
    # TRANSFORM COPIES
    # ============================================================
    result = []
    for g in work:
        copy = g.Duplicate()
        copy.Transform(combined)
        result.append(copy)

    a = result

    # ============================================================
    # GROUND PLANE GRID
    # ============================================================
    if grid_on and grid_sp > 0:
        # grid covers the model footprint, extended one bay each side
        bb_min = union_bb.Min
        bb_max = union_bb.Max

        if is_plan:
            # grid on Z=0 plane, lines in X and Y
            x0 = math.floor(bb_min.X / grid_sp) * grid_sp - grid_sp
            x1 = math.ceil(bb_max.X / grid_sp) * grid_sp + grid_sp
            y0 = math.floor(bb_min.Y / grid_sp) * grid_sp - grid_sp
            y1 = math.ceil(bb_max.Y / grid_sp) * grid_sp + grid_sp
            grid_lines = []
            # lines parallel to Y
            x = x0
            while x <= x1:
                ln = rg.Line(rg.Point3d(x, y0, 0), rg.Point3d(x, y1, 0))
                grid_lines.append(ln.ToNurbsCurve())
                x += grid_sp
            # lines parallel to X
            y = y0
            while y <= y1:
                ln = rg.Line(rg.Point3d(x0, y, 0), rg.Point3d(x1, y, 0))
                grid_lines.append(ln.ToNurbsCurve())
                y += grid_sp
        else:
            # grid on Y=0 plane, lines in X and Z
            x0 = math.floor(bb_min.X / grid_sp) * grid_sp - grid_sp
            x1 = math.ceil(bb_max.X / grid_sp) * grid_sp + grid_sp
            z0 = math.floor(bb_min.Z / grid_sp) * grid_sp - grid_sp
            z1 = math.ceil(bb_max.Z / grid_sp) * grid_sp + grid_sp
            grid_lines = []
            # lines parallel to Z
            x = x0
            while x <= x1:
                ln = rg.Line(rg.Point3d(x, 0, z0), rg.Point3d(x, 0, z1))
                grid_lines.append(ln.ToNurbsCurve())
                x += grid_sp
            # lines parallel to X
            z = z0
            while z <= z1:
                ln = rg.Line(rg.Point3d(x0, 0, z), rg.Point3d(x1, 0, z))
                grid_lines.append(ln.ToNurbsCurve())
                z += grid_sp

        # apply same oblique transform to grid
        for ln in grid_lines:
            ln.Transform(combined)

        b = grid_lines
    else:
        b = None

    # ============================================================
    # INFO
    # ============================================================
    parts = [mode_name]
    parts.append("Shear X={0}, Y={1}".format(sx, sy))
    parts.append("Rotation={0}".format(rot))
    parts.append("Depth={0}".format(dp))
    if cut:
        parts.append("Section cut at {0}".format(cut_h))
    parts.append("{0} objects".format(len(result)))
    info = " | ".join(parts)
