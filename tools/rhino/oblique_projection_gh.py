# Oblique Projection — GhPython component
# Paste into a GhPython Script component in Grasshopper.
#
# INPUTS (right-click component, rename inputs, set type hints):
#   geo      — list access, type hint: GeometryBase  (your 3D model)
#   preset   — int, slider -1 to 3   (-1=custom, 0=cavalier45, 1=cabinet45, 2=cabinet30, 3=military)
#   angle    — float, slider 0 to 90  (receding axis angle in drawing, degrees from horizontal)
#   depth    — float, slider 0.1 to 1 (depth scale: 1=full/cavalier, 0.5=half/cabinet)
#   rotation — float, slider 0 to 360 (Z-axis rotation of base model before projection)
#   plan_ob  — bool toggle             (True=plan oblique, False=elevation oblique)
#   cut      — bool toggle             (section cut on/off)
#   cut_axis — int, slider 0 to 2      (cut plane axis: 0=X, 1=Y, 2=Z)
#   cut_h    — float, slider 0 to 50   (cut location along axis, feet)
#   grid_on  — bool toggle             (ground plane grid on/off)
#   grid_sp  — float, slider 0.5 to 10 (grid spacing, default 2 = 24 inches on center)
#
# OUTPUTS (right-click component, rename outputs):
#   a    — projected geometry
#   b    — ground grid lines (when grid_on=True)
#   info — text summary
#
# After baking, run Make2D:
#   Plan oblique     — Make2D from Top view
#   Elevation oblique — Make2D from Front view

import math
import Rhino
import Rhino.Geometry as rg

# ================================================================
# PRESETS
# ================================================================
# angle  = direction of receding axis in the 2D drawing (degrees from horizontal)
# depth  = foreshortening of receding axis (1.0 = true length, 0.5 = half)
# rot    = Z rotation of base model before projection
PRESETS = {
    0: {"name": "Cavalier 45",  "plan_ob": True,  "angle": 45, "depth": 1.0, "rot": 0},
    1: {"name": "Cabinet 45",   "plan_ob": True,  "angle": 45, "depth": 0.5, "rot": 0},
    2: {"name": "Cabinet 30",   "plan_ob": True,  "angle": 30, "depth": 0.5, "rot": 0},
    3: {"name": "Military",     "plan_ob": True,  "angle": 90, "depth": 1.0, "rot": 45},
}

# ================================================================
# DEFAULTS  (50'x50'x50' bounding box, 24" grid)
# ================================================================
if preset is None:   preset = -1
if angle is None:    angle = 45.0
if depth is None:    depth = 1.0
if rotation is None: rotation = 0.0
if plan_ob is None:  plan_ob = True
if cut is None:      cut = False
if cut_axis is None: cut_axis = 2
if cut_h is None:    cut_h = 25.0
if grid_on is None:  grid_on = False
if grid_sp is None:  grid_sp = 2.0

# clamp cut_axis to valid range
cut_axis = int(max(0, min(2, cut_axis)))

# ================================================================
# RESOLVE PRESET vs CUSTOM
# ================================================================
if preset in PRESETS:
    p = PRESETS[preset]
    ang = p["angle"]
    dp = p["depth"]
    rot = p["rot"]
    is_plan = p["plan_ob"]
    mode_name = p["name"]
else:
    ang = angle
    dp = depth
    rot = rotation
    is_plan = plan_ob
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

    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance

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
    # Build cut plane from axis slider (0=X, 1=Y, 2=Z)
    axis_names = ["X", "Y", "Z"]
    axis_vectors = [rg.Vector3d.XAxis, rg.Vector3d.YAxis, rg.Vector3d.ZAxis]
    cut_origin = rg.Point3d(0, 0, 0)
    if cut_axis == 0:
        cut_origin = rg.Point3d(cut_h, 0, 0)
    elif cut_axis == 1:
        cut_origin = rg.Point3d(0, cut_h, 0)
    else:
        cut_origin = rg.Point3d(0, 0, cut_h)
    # plane normal points in +axis direction; flip so Trim keeps the negative side
    cut_plane = rg.Plane(cut_origin, -axis_vectors[cut_axis])

    def as_brep(g):
        """Convert Extrusion or Surface to Brep for trimming."""
        if isinstance(g, rg.Extrusion):
            return g.ToBrep()
        if isinstance(g, rg.Surface):
            return g.ToBrep()
        return None

    def kept_side(bbox, axis, threshold, tolerance):
        """Check if bounding box center is on the kept side of the cut."""
        c = bbox.Center
        if axis == 0:
            return c.X <= threshold + tolerance
        elif axis == 1:
            return c.Y <= threshold + tolerance
        else:
            return c.Z <= threshold + tolerance

    work = []
    if cut:
        for g in geo:
            brep = None
            if isinstance(g, rg.Brep):
                brep = g
            else:
                brep = as_brep(g)

            if brep is not None:
                trimmed = brep.Trim(cut_plane, tol)
                if trimmed and len(trimmed) > 0:
                    work.extend(trimmed)
                else:
                    if kept_side(g.GetBoundingBox(True), cut_axis, cut_h, tol):
                        work.append(g)
            elif isinstance(g, rg.Mesh):
                split_plane = rg.Plane(cut_origin, axis_vectors[cut_axis])
                parts = g.Split(split_plane)
                if parts and len(parts) > 0:
                    for part in parts:
                        if kept_side(part.GetBoundingBox(True), cut_axis, cut_h, tol):
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
    # rotation around Z
    rot_xform = rg.Transform.Rotation(
        math.radians(rot),
        rg.Vector3d.ZAxis,
        center
    )

    # oblique shear
    # receding axis appears at angle `ang` in the 2D drawing, scaled by `dp`
    #
    # Plan oblique (Make2D from Top):
    #   x' = x + z * dp * cos(ang)
    #   y' = y + z * dp * sin(ang)
    #
    # Elevation oblique (Make2D from Front):
    #   x' = x + y * dp * cos(ang)
    #   z' = z + y * dp * sin(ang)
    ang_rad = math.radians(ang)
    shear_xform = rg.Transform.Identity
    if is_plan:
        shear_xform.M02 = dp * math.cos(ang_rad)
        shear_xform.M12 = dp * math.sin(ang_rad)
    else:
        shear_xform.M01 = dp * math.cos(ang_rad)
        shear_xform.M21 = dp * math.sin(ang_rad)

    # combined: rotate first, then shear
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
    # GROUND PLANE GRID (24" on center default = 2' spacing)
    # ============================================================
    if grid_on and grid_sp > 0:
        bb_min = union_bb.Min
        bb_max = union_bb.Max
        grid_lines = []

        if is_plan:
            x0 = math.floor(bb_min.X / grid_sp) * grid_sp - grid_sp
            x1 = math.ceil(bb_max.X / grid_sp) * grid_sp + grid_sp
            y0 = math.floor(bb_min.Y / grid_sp) * grid_sp - grid_sp
            y1 = math.ceil(bb_max.Y / grid_sp) * grid_sp + grid_sp
            x = x0
            while x <= x1:
                ln = rg.LineCurve(rg.Point3d(x, y0, 0), rg.Point3d(x, y1, 0))
                ln.Transform(combined)
                grid_lines.append(ln)
                x += grid_sp
            y = y0
            while y <= y1:
                ln = rg.LineCurve(rg.Point3d(x0, y, 0), rg.Point3d(x1, y, 0))
                ln.Transform(combined)
                grid_lines.append(ln)
                y += grid_sp
        else:
            x0 = math.floor(bb_min.X / grid_sp) * grid_sp - grid_sp
            x1 = math.ceil(bb_max.X / grid_sp) * grid_sp + grid_sp
            z0 = math.floor(bb_min.Z / grid_sp) * grid_sp - grid_sp
            z1 = math.ceil(bb_max.Z / grid_sp) * grid_sp + grid_sp
            x = x0
            while x <= x1:
                ln = rg.LineCurve(rg.Point3d(x, 0, z0), rg.Point3d(x, 0, z1))
                ln.Transform(combined)
                grid_lines.append(ln)
                x += grid_sp
            z = z0
            while z <= z1:
                ln = rg.LineCurve(rg.Point3d(x0, 0, z), rg.Point3d(x1, 0, z))
                ln.Transform(combined)
                grid_lines.append(ln)
                z += grid_sp

        b = grid_lines
    else:
        b = None

    # ============================================================
    # INFO
    # ============================================================
    view = "Top" if is_plan else "Front"
    parts = [mode_name]
    parts.append("Receding angle={0} deg".format(ang))
    parts.append("Depth scale={0}".format(dp))
    parts.append("Rotation={0}".format(rot))
    if cut:
        parts.append("Cut {0}={1}".format(axis_names[cut_axis], cut_h))
    parts.append("{0} objects".format(len(result)))
    parts.append("Make2D: {0} view".format(view))
    info = " | ".join(parts)
