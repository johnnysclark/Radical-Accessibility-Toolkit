# Oblique Projection (Section Cut) — GhPython Script component (IronPython 2.7)
#
# Based on oblique_projection_simple_gh.py with section cut added back.
# No worm's eye, no ground grid.
#
# USE WITH: GhPython Script component (search "GhPy" on canvas)
# DO NOT USE the Rhino 8 "Python 3 Script" component — its output is broken.
#
# INPUTS:
#   geo      — Tree Access, type hint: GeometryBase  (merged geometry tree)
#   preset   — Item Access, type hint: int
#   angle    — Item Access, type hint: float
#   depth    — Item Access, type hint: float
#   rotation — Item Access, type hint: float
#   plan_ob  — Item Access, type hint: bool
#   cut      — Item Access, type hint: bool   (enable section cut)
#   cut_axis — Item Access, type hint: int     (0=X, 1=Y, 2=Z)
#   cut_h    — Item Access, type hint: float   (cut plane position)
#
# OUTPUTS (rename via right-click):
#   a    — projected geometry (DataTree — same branches as input)
#   info — text summary

import math
import System
import Rhino
import Rhino.Geometry as rg
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path


def resolve_geo(item):
    """Convert Guid references to actual geometry objects."""
    if isinstance(item, System.Guid):
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(item)
        if obj is not None:
            return obj.Geometry
        return None
    return item


def explode_block(item):
    """Recursively explode block instance references into individual geometry."""
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
                    pieces.extend(explode_block(sub_obj.Id))
                else:
                    pieces.append(sub_geo)
            return pieces
        return [obj.Geometry]
    if hasattr(item, 'GetType') and item.GetType().Name == 'InstanceReferenceGeometry':
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
if cut_h is None:    cut_h = 0.0

cut_axis = int(max(0, min(2, cut_axis)))

# ================================================================
# RESOLVE PRESET vs CUSTOM
# ================================================================
is_plan = plan_ob

if preset in PRESETS:
    p = PRESETS[preset]
    ang = p["angle"]
    dp = p["depth"]
    rot = p["rot"] + rotation
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

def convert_geo(g):
    """Convert a single geometry to a shear-safe type."""
    converted = to_brep(g)
    if converted is not None:
        return converted
    return g

def bbox_entirely_above(bbox, axis, threshold, tol):
    """True if the geometry's bounding box is entirely above the cut plane."""
    mn = [bbox.Min.X, bbox.Min.Y, bbox.Min.Z]
    return mn[axis] >= threshold - tol

# ================================================================
# MAIN — read tree, process, output tree
# ================================================================

tagged = []
input_paths = []

if geo is not None:
    if hasattr(geo, 'Paths'):
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
    info = "No geometry connected."
else:
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance

    # -- bounding box center as pivot --
    all_pts = []
    for g, path in tagged:
        gbb = g.GetBoundingBox(True)
        all_pts.append(gbb.Min)
        all_pts.append(gbb.Max)
    union_bb = rg.BoundingBox(all_pts)
    center = union_bb.Center

    # ========================================================
    # SECTION CUT (before transform, keeps geometry below cut)
    # ========================================================
    axis_names = ["X", "Y", "Z"]
    axis_vectors = [rg.Vector3d.XAxis, rg.Vector3d.YAxis, rg.Vector3d.ZAxis]
    cut_origins = [
        rg.Point3d(cut_h, 0, 0),
        rg.Point3d(0, cut_h, 0),
        rg.Point3d(0, 0, cut_h)]
    cut_origin = cut_origins[cut_axis]
    cut_normal = axis_vectors[cut_axis]
    cut_plane = rg.Plane(cut_origin, cut_normal)

    work = []
    if cut:
        for g, path in tagged:
            if isinstance(g, rg.Brep):
                trimmed = g.Trim(cut_plane, tol)
                if trimmed and len(trimmed) > 0:
                    for t in trimmed:
                        work.append((t, path))
                elif not bbox_entirely_above(g.GetBoundingBox(True), cut_axis, cut_h, tol):
                    # Trim failed but geometry is at least partially below — keep it
                    work.append((g, path))
            elif isinstance(g, rg.Mesh):
                split_plane = rg.Plane(cut_origin, axis_vectors[cut_axis])
                parts = g.Split(split_plane)
                if parts and len(parts) > 0:
                    for part in parts:
                        c = part.GetBoundingBox(True).Center
                        vals = [c.X, c.Y, c.Z]
                        if vals[cut_axis] <= cut_h + tol:
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
    shear_xform = rg.Transform(1)
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
    for path in input_paths:
        out_tree.EnsurePath(path)
    total = 0
    branch_counts = {}
    for g, path in work:
        copy = g.Duplicate()
        copy.Transform(combined)
        out_tree.Add(copy, path)
        total += 1
        key = path.ToString()
        branch_counts[key] = branch_counts.get(key, 0) + 1

    a = out_tree

    # ========================================================
    # INFO
    # ========================================================
    view = "Top" if is_plan else "Front"
    type_counts = {}
    for path in out_tree.Paths:
        for g in out_tree.Branch(path):
            tn = type(g).__name__
            type_counts[tn] = type_counts.get(tn, 0) + 1
    type_str = ", ".join("{0}x{1}".format(v, k) for k, v in type_counts.items())

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
        parts.append("Cut {0}={1}".format(axis_names[cut_axis], cut_h))
    parts.append("{0} objects ({1})".format(total, type_str))
    parts.append("{0} branches [{1}]".format(len(input_paths), counts))
    parts.append("Make2D: {0} view".format(view))
    info = " | ".join(parts)
