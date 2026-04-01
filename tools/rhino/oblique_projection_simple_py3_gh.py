# Oblique Projection (Simple) — Python 3 Script component (Rhino 8 SR8+)
#
# Stripped-down version of oblique_projection_gh.py.
# No section cut, no worm's eye, no ground grid.
#
# USE WITH: Python 3 Script component (search "Script" or "cpython" on canvas)
# Requires Rhino 8 SR8 or later for correct DataTree output.
#
# Migration notes (IronPython 2.7 -> CPython 3):
#   - Imports unchanged; pythonnet provides System/Grasshopper/Rhino namespaces
#   - DataTree output works correctly in Rhino 8 SR8+
#   - .format() calls replaced with f-strings
#   - No clr.AddReference() needed; Script component pre-loads assemblies
#   - from __future__ import annotations required so X | None type hints
#     don't crash at runtime (pythonnet CLRMetatype has no __or__)
#   - Python 3 Script component does NOT auto-unwrap IGH_Goo wrappers
#     (GH_Brep, GH_Guid, etc.) — must call .Value manually
#   - Tree input read via ghenv.Component.Params.Input[0].VolatileData
#     so the script works regardless of the access level setting
#
# INPUTS:
#   geo      — any Access, type hint: goo or GeometryBase  (merged geometry tree)
#   preset   — Item Access, type hint: int
#   angle    — Item Access, type hint: float
#   depth    — Item Access, type hint: float
#   rotation — Item Access, type hint: float
#   plan_ob  — Item Access, type hint: bool
#
# OUTPUTS:
#   out  — projected geometry (list — connect to Explode Tree for branches)
#          The Python 3 Script component names its first output "out" internally.
#          The NickName shown on the component can be renamed to "a" via right-click,
#          but the script variable must always be "out".
#   info — text summary

from __future__ import annotations

import math
import System
import Rhino
import Rhino.Geometry as rg
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper.Kernel.Types import IGH_Goo


def unwrap_goo(item: object) -> object:
    """Unwrap IGH_Goo wrappers (GH_Brep, GH_Guid, etc.) to raw values.
    The Python 3 Script component does not auto-unwrap like GhPython did.
    For geometry goo types, try ScriptVariable() first — this resolves
    referenced geometry to actual GeometryBase without needing Objects.Find."""
    if isinstance(item, IGH_Goo):
        # ScriptVariable() is what GhPython's type-hint unwrapping called
        # internally — it resolves Guid references to geometry objects.
        if hasattr(item, 'ScriptVariable'):
            sv = item.ScriptVariable()
            if sv is not None:
                return sv
        return item.Value
    return item


def resolve_geo(item: object) -> rg.GeometryBase | None:
    """Convert Guid references to actual geometry objects."""
    if isinstance(item, System.Guid):
        obj = Rhino.RhinoDoc.ActiveDoc.Objects.Find(item)
        if obj is not None:
            return obj.Geometry
        return None
    return item


def explode_block(item: object) -> list:
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
def to_brep(g: rg.GeometryBase) -> rg.Brep | None:
    """Convert any geometry to Brep for reliable shear transforms.
    Extrusions CANNOT handle arbitrary transforms — they silently fail."""
    if isinstance(g, rg.Brep):
        return g
    if isinstance(g, rg.Extrusion):
        return g.ToBrep()
    if isinstance(g, rg.Surface):
        return g.ToBrep()
    return None

def convert_geo(g: rg.GeometryBase) -> rg.GeometryBase:
    """Convert a single geometry to a shear-safe type."""
    converted = to_brep(g)
    if converted is not None:
        return converted
    return g

# ================================================================
# MAIN — read tree, process, output tree
# ================================================================

tagged = []
input_paths = []

# Read the geo tree directly from the component parameter.
# This bypasses the access-level setting (Item/List/Tree) and gives
# us the raw GH_Structure with all branches and IGH_Goo items.
geo_tree = ghenv.Component.Params.Input[0].VolatileData

if geo_tree is not None and not geo_tree.IsEmpty:
    for path in geo_tree.Paths:
        branch = geo_tree.get_Branch(path)
        for goo_item in branch:
            raw = unwrap_goo(goo_item)
            if raw is None:
                continue
            for piece in explode_block(raw):
                resolved = resolve_geo(piece)
                if resolved is not None:
                    tagged.append((convert_geo(resolved), path))
                    if path not in input_paths:
                        input_paths.append(path)

def _set_output_geo(items, paths=None):
    """Write geometry directly to the first output parameter.
    Bypasses variable assignment which doesn't work reliably
    in the Python 3 Script component."""
    param = ghenv.Component.Params.Output[0]
    param.ClearData()
    if paths is not None:
        for item, path in zip(items, paths):
            idx = param.VolatileData.get_Branch(path).Count if param.VolatileData.PathExists(path) else 0
            param.AddVolatileData(path, idx, item)
    else:
        for i, item in enumerate(items):
            param.AddVolatileData(GH_Path(0), i, item)

if len(tagged) == 0:
    _set_output_geo([])
    info = "No geometry connected."
else:
    # -- bounding box center as pivot --
    all_pts = []
    for g, path in tagged:
        gbb = g.GetBoundingBox(True)
        all_pts.append(gbb.Min)
        all_pts.append(gbb.Max)
    union_bb = rg.BoundingBox(all_pts)
    center = union_bb.Center

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
    # TRANSFORM COPIES
    # ========================================================
    out_list = []
    total = 0
    branch_counts = {}
    for g, path in tagged:
        copy = g.Duplicate()
        copy.Transform(combined)
        out_list.append(copy)
        total += 1
        key = path.ToString()
        branch_counts[key] = branch_counts.get(key, 0) + 1

    _set_output_geo(out_list)

    # ========================================================
    # INFO
    # ========================================================
    view = "Top" if is_plan else "Front"
    type_counts = {}
    for g in out_list:
        tn = type(g).__name__
        type_counts[tn] = type_counts.get(tn, 0) + 1
    type_str = ", ".join(f"{v}x{k}" for k, v in type_counts.items())

    branch_strs = []
    for path in input_paths:
        key = path.ToString()
        cnt = branch_counts.get(key, 0)
        branch_strs.append(f"{key}={cnt}")
    counts = " ".join(branch_strs)

    parts = [mode_name]
    parts.append(f"Angle={ang} deg")
    parts.append(f"Depth={dp}")
    parts.append(f"Rotation={rot}")
    parts.append(f"{total} objects ({type_str})")
    parts.append(f"{len(input_paths)} branches [{counts}]")
    parts.append(f"Make2D: {view} view")
    info = " | ".join(parts)
