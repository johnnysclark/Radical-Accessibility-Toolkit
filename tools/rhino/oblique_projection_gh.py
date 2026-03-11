# Oblique Projection — GhPython Script component (IronPython 2.7)
#
# USE WITH: GhPython Script component (search "GhPy" on canvas)
# DO NOT USE the Rhino 8 "Python 3 Script" component — its output is broken.
#
# SETUP:
#   1. Place a GhPython Script component on the canvas
#   2. Zoom in and use +/- on component edges to add inputs/outputs
#   3. Right-click each input to rename and set type hints:
#
# INPUTS:
#   geo      — List Access, type hint: GeometryBase
#   preset   — Item Access, type hint: int
#   angle    — Item Access, type hint: float
#   depth    — Item Access, type hint: float
#   rotation — Item Access, type hint: float
#   plan_ob  — Item Access, type hint: bool
#   cut      — Item Access, type hint: bool
#   cut_axis — Item Access, type hint: int
#   cut_h    — Item Access, type hint: float
#   grid_on  — Item Access, type hint: bool
#   grid_sp  — Item Access, type hint: float
#
# OUTPUTS (rename via right-click):
#   a    — projected geometry
#   b    — ground grid lines (when grid_on=True)
#   info — text summary
#
# After baking, run Make2D:
#   Plan oblique     — Make2D from Top view
#   Elevation oblique — Make2D from Front view

import math
import System
import Rhino
import Rhino.Geometry as rg


def resolve_geo(item):
    """Convert Guid references to actual geometry objects.
    GhPython passes Guids when type hint is missing or set to 'No Type Hint'."""
    if isinstance(item, System.Guid):
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(item)
        if obj is not None:
            return obj.Geometry
        return None
    return item

# ================================================================
# PRESETS
# ================================================================
PRESETS = {
    0: {"name": "Cavalier 45",  "angle": 45, "depth": 1.0, "rot": 0},
    1: {"name": "Cabinet 45",   "angle": 45, "depth": 0.5, "rot": 0},
    2: {"name": "Cabinet 30",   "angle": 30, "depth": 0.5, "rot": 0},
    3: {"name": "Military",     "angle": 90, "depth": 1.0, "rot": 45},
}

# ================================================================
# DEFAULTS
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

cut_axis = int(max(0, min(2, cut_axis)))

# ================================================================
# RESOLVE PRESET vs CUSTOM
# ================================================================
is_plan = plan_ob

if preset in PRESETS:
    p = PRESETS[preset]
    ang = p["angle"]
    dp = p["depth"]
    rot = p["rot"]
    mode_name = p["name"]
else:
    ang = angle
    dp = depth
    rot = rotation
    mode_name = "Custom"

if is_plan:
    mode_name += " (plan oblique)"
else:
    mode_name += " (elevation oblique)"

# ================================================================
# HELPERS
# ================================================================
def to_brep(g):
    """Convert any geometry to Brep for reliable shear transforms.
    Extrusions CANNOT handle arbitrary transforms — they silently fail."""
    if isinstance(g, rg.Brep):
        return g
    if isinstance(g, rg.Extrusion):
        return g.ToBrep()
    if isinstance(g, rg.Surface):
        return g.ToBrep()
    return None

def kept_side(bbox, axis, threshold, tolerance):
    c = bbox.Center
    vals = [c.X, c.Y, c.Z]
    return vals[axis] <= threshold + tolerance

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
    geo = [resolve_geo(g) for g in geo]
    geo = [g for g in geo if g is not None]

    if len(geo) == 0:
        a = None
        b = None
        info = "No valid geometry."
    else:
        tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance

        # -- bounding box center as pivot --
        all_pts = []
        for g in geo:
            gbb = g.GetBoundingBox(True)
            all_pts.append(gbb.Min)
            all_pts.append(gbb.Max)
        union_bb = rg.BoundingBox(all_pts)
        center = union_bb.Center

        # ========================================================
        # SECTION CUT (before transform)
        # ========================================================
        axis_names = ["X", "Y", "Z"]
        axis_vectors = [rg.Vector3d.XAxis, rg.Vector3d.YAxis, rg.Vector3d.ZAxis]
        cut_pts = [
            rg.Point3d(cut_h, 0, 0),
            rg.Point3d(0, cut_h, 0),
            rg.Point3d(0, 0, cut_h)]
        cut_origin = cut_pts[cut_axis]
        cut_plane = rg.Plane(cut_origin, -axis_vectors[cut_axis])

        # Convert ALL geometry to Brep first — Extrusions cannot be sheared
        brep_geo = []
        for g in geo:
            converted = to_brep(g)
            if converted is not None:
                brep_geo.append(converted)
            elif isinstance(g, rg.Mesh):
                brep_geo.append(g)  # meshes handle shear fine
            elif isinstance(g, rg.Curve):
                brep_geo.append(g)  # curves handle shear fine
            elif isinstance(g, rg.Point):
                brep_geo.append(g)
            else:
                brep_geo.append(g)  # try anyway

        work = []
        if cut:
            for g in brep_geo:
                if isinstance(g, rg.Brep):
                    trimmed = g.Trim(cut_plane, tol)
                    if trimmed and len(trimmed) > 0:
                        work.extend(trimmed)
                    elif kept_side(g.GetBoundingBox(True), cut_axis, cut_h, tol):
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
            work = list(brep_geo)

        # ========================================================
        # BUILD TRANSFORMS
        # ========================================================
        rot_xform = rg.Transform.Rotation(
            math.radians(rot),
            rg.Vector3d.ZAxis,
            center
        )

        ang_rad = math.radians(ang)
        # Build shear via indexer — .M02 property setters silently fail
        # on .NET structs even in IronPython in some Rhino builds
        shear_xform = rg.Transform(1)  # identity via constructor
        if is_plan:
            shear_xform[0, 2] = dp * math.cos(ang_rad)
            shear_xform[1, 2] = dp * math.sin(ang_rad)
        else:
            shear_xform[0, 1] = dp * math.cos(ang_rad)
            shear_xform[2, 1] = dp * math.sin(ang_rad)

        combined = shear_xform * rot_xform

        # ========================================================
        # TRANSFORM COPIES
        # ========================================================
        result = []
        for g in work:
            copy = g.Duplicate()
            copy.Transform(combined)
            result.append(copy)

        a = result

        # ========================================================
        # GROUND PLANE GRID
        # ========================================================
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

        # ========================================================
        # INFO
        # ========================================================
        view = "Top" if is_plan else "Front"
        # type summary for diagnostics
        type_counts = {}
        for g in result:
            tn = type(g).__name__
            type_counts[tn] = type_counts.get(tn, 0) + 1
        type_str = ", ".join("{0}x{1}".format(v, k) for k, v in type_counts.items())

        parts = [mode_name]
        parts.append("Angle={0} deg".format(ang))
        parts.append("Depth={0}".format(dp))
        parts.append("Rotation={0}".format(rot))
        if cut:
            parts.append("Cut {0}={1}".format(axis_names[cut_axis], cut_h))
        parts.append("{0} objects ({1})".format(len(result), type_str))
        parts.append("Make2D: {0} view".format(view))
        info = " | ".join(parts)
