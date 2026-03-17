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
# WORKFLOW:
#   Use a Merge component before to combine geometry sources.
#   Each Merge input becomes a branch: {0}=arch, {1}=ground, {2}=foliage, etc.
#   Use Explode Tree after to split branches into separate Custom Previews.
#
# INPUTS:
#   geo      — Tree Access, type hint: GeometryBase  (merged geometry tree)
#   preset   — Item Access, type hint: int
#   angle    — Item Access, type hint: float
#   depth    — Item Access, type hint: float
#   rotation — Item Access, type hint: float
#   plan_ob  — Item Access, type hint: bool
#   cut      — Item Access, type hint: bool
#   cut_axis — Item Access, type hint: int
#   cut_h    — Item Access, type hint: float
#   worms_eye — Item Access, type hint: bool  (flip cut: keep above instead of below)
#   grid_on  — Item Access, type hint: bool
#   grid_sp  — Item Access, type hint: float
#
# OUTPUTS (rename via right-click):
#   a    — projected geometry (DataTree — same branches as input)
#   b    — ground grid lines (when grid_on=True)
#   info — text summary
#
# Canvas wiring:
#   [Arch] --\                                     /--> {0} --> Custom Preview (arch material)
#   [Ground] --> Merge --> geo --> [This] --> a --> Explode Tree --> {1} --> Custom Preview (ground)
#   [Foliage]-/                                    \--> {2} --> Custom Preview (foliage)
#
# After baking, run Make2D:
#   Plan oblique     — Make2D from Top view
#   Elevation oblique — Make2D from Front view

import math
import System
import Rhino
import Rhino.Geometry as rg
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def resolve_geo(item):
    """Convert Guid references to actual geometry objects.
    GhPython passes Guids when type hint is missing or set to 'No Type Hint'."""
    if isinstance(item, System.Guid):
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(item)
        if obj is not None:
            return obj.Geometry
        return None
    return item


def explode_block(item):
    """Recursively explode block instance references into individual geometry.
    Returns a flat list of non-block geometry pieces."""
    if isinstance(item, System.Guid):
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(item)
        if obj is None:
            return []
        if isinstance(obj, Rhino.DocObjects.InstanceObject):
            pieces = []
            xform = obj.InstanceXform
            idef = obj.InstanceDefinition
            for i in range(idef.ObjectCount):
                sub_obj = idef.Object(i)
                sub_geo = sub_obj.Geometry.Duplicate()
                sub_geo.Transform(xform)
                if isinstance(sub_obj, Rhino.DocObjects.InstanceObject):
                    # nested block — recurse via Guid
                    pieces.extend(explode_block(sub_obj.Id))
                else:
                    pieces.append(sub_geo)
            return pieces
        return [obj.Geometry]
    # Already resolved geometry — check if it's an InstanceReference
    if hasattr(item, 'GetType') and item.GetType().Name == 'InstanceReferenceGeometry':
        # Can't explode pure geometry-level instance refs without doc context;
        # pass through and let to_brep handle it
        return [item]
    return [item]


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
if worms_eye is None: worms_eye = False
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
    rot = p["rot"] + rotation   # slider adds to preset base rotation
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

def not_entirely_wrong_side(bbox, axis, threshold, tolerance, keep_above=False):
    """Permissive check for Brep.Trim fallback: keep geometry unless it is
    *entirely* on the discarded side of the cut plane.  If Trim failed on
    geometry that spans the plane, this keeps the whole brep as a visible
    fallback rather than dropping it."""
    mn = [bbox.Min.X, bbox.Min.Y, bbox.Min.Z]
    mx = [bbox.Max.X, bbox.Max.Y, bbox.Max.Z]
    if keep_above:
        # keep unless entirely below threshold
        return mx[axis] >= threshold - tolerance
    # keep unless entirely above threshold
    return mn[axis] <= threshold + tolerance

def center_on_kept_side(bbox, axis, threshold, tolerance, keep_above=False):
    """Strict check for mesh split parts: after a clean split each piece's
    center is clearly on one side of the cut."""
    c = bbox.Center
    vals = [c.X, c.Y, c.Z]
    if keep_above:
        return vals[axis] >= threshold - tolerance
    return vals[axis] <= threshold + tolerance

def convert_geo(g):
    """Convert a single geometry to a shear-safe type."""
    converted = to_brep(g)
    if converted is not None:
        return converted
    # meshes, curves, points all handle shear fine
    return g

# ================================================================
# MAIN — read tree, process, output tree
# ================================================================

# Read input data tree — supports both Tree Access and List/Item fallback
tagged = []  # list of (geometry, GH_Path)
input_paths = []

if geo is not None:
    if hasattr(geo, 'Paths'):
        # Tree Access — iterate branches
        for path in geo.Paths:
            branch = geo.Branch(path)
            for item in branch:
                for piece in explode_block(item):
                    resolved = resolve_geo(piece)
                    if resolved is not None:
                        tagged.append((convert_geo(resolved), path))
                        if path not in input_paths:
                            input_paths.append(path)
    else:
        # Fallback: plain list (List Access) — treat as single branch {0}
        items = geo if hasattr(geo, '__iter__') else [geo]
        fallback_path = GH_Path(0)
        input_paths.append(fallback_path)
        for item in items:
            for piece in explode_block(item):
                resolved = resolve_geo(piece)
                if resolved is not None:
                    tagged.append((convert_geo(resolved), fallback_path))

if len(tagged) == 0:
    a = DataTree[rg.GeometryBase]()
    b = None
    info = "No geometry connected."
else:
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance

    # -- bounding box center as pivot (union of all branches) --
    all_pts = []
    for g, path in tagged:
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
    cut_normal = -axis_vectors[cut_axis] if worms_eye else axis_vectors[cut_axis]
    cut_plane = rg.Plane(cut_origin, cut_normal)

    work = []  # list of (geometry, GH_Path)
    if cut:
        for g, path in tagged:
            if isinstance(g, rg.Brep):
                trimmed = g.Trim(cut_plane, tol)
                if trimmed and len(trimmed) > 0:
                    for t in trimmed:
                        work.append((t, path))
                elif not_entirely_wrong_side(g.GetBoundingBox(True), cut_axis, cut_h, tol, worms_eye):
                    work.append((g, path))
            elif isinstance(g, rg.Mesh):
                split_plane = rg.Plane(cut_origin, axis_vectors[cut_axis])
                parts = g.Split(split_plane)
                if parts and len(parts) > 0:
                    for part in parts:
                        if center_on_kept_side(part.GetBoundingBox(True), cut_axis, cut_h, tol, worms_eye):
                            work.append((part, path))
                else:
                    work.append((g, path))
            else:
                work.append((g, path))
    else:
        work = list(tagged)

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
    # TRANSFORM COPIES — build output DataTree
    # ========================================================
    out_tree = DataTree[rg.GeometryBase]()
    # Ensure all input branches exist in output even if cut removes everything.
    # Without this, Explode Tree outputs shift when a branch is fully cut away.
    for path in input_paths:
        out_tree.EnsurePath(path)
    total = 0
    branch_counts = {}  # path string -> count
    for g, path in work:
        copy = g.Duplicate()
        copy.Transform(combined)
        out_tree.Add(copy, path)
        total += 1
        key = path.ToString()
        branch_counts[key] = branch_counts.get(key, 0) + 1

    a = out_tree

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
    if is_plan:
        view = "Bottom" if worms_eye else "Top"
    else:
        view = "Back" if worms_eye else "Front"
    # type summary for diagnostics
    type_counts = {}
    for path in out_tree.Paths:
        for g in out_tree.Branch(path):
            tn = type(g).__name__
            type_counts[tn] = type_counts.get(tn, 0) + 1
    type_str = ", ".join("{0}x{1}".format(v, k) for k, v in type_counts.items())

    # per-branch counts
    branch_strs = []
    for path in input_paths:
        key = path.ToString()
        cnt = branch_counts.get(key, 0)
        branch_strs.append("{0}={1}".format(key, cnt))
    counts = " ".join(branch_strs)

    parts = [mode_name]
    parts.append("Angle={0} deg".format(ang))
    parts.append("Depth={0}".format(dp))
    parts.append("Rotation={0}".format(rot))
    if cut:
        eye = "worm's eye" if worms_eye else "bird's eye"
        parts.append("Cut {0}={1} ({2})".format(axis_names[cut_axis], cut_h, eye))
    parts.append("{0} objects ({1})".format(total, type_str))
    parts.append("{0} branches [{1}]".format(len(input_paths), counts))
    parts.append("Make2D: {0} view".format(view))
    info = " | ".join(parts)
