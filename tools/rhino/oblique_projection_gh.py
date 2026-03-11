# Oblique Projection — GhPython component
# Paste into a GhPython Script component in Grasshopper.
#
# INPUTS (right-click component > set these on the input side):
#   geo       — Geometry (list access, type hint: Geometry / GeometryBase)
#   shear_x   — float, slider 0 to 89  (shear angle X degrees)
#   shear_y   — float, slider 0 to 89  (shear angle Y degrees)
#   rotation  — float, slider 0 to 360 (Z-axis rotation degrees)
#   plan_ob   — bool, toggle True/False (True = plan oblique, False = elevation oblique)
#
# OUTPUTS:
#   a — projected geometry (plug into a preview or bake)
#   info — text summary of current settings

import math
import Rhino.Geometry as rg

# -- defaults if sliders are missing --
if shear_x is None: shear_x = 30.0
if shear_y is None: shear_y = 30.0
if rotation is None: rotation = 0.0
if plan_ob is None: plan_ob = False

# -- handle single object or list --
if geo is None:
    a = None
    info = "No geometry connected."
else:
    if not hasattr(geo, '__iter__'):
        geo = [geo]

    # -- bounding box center as pivot --
    # Collect all corner points; BoundingBox is a .NET struct so
    # calling .Union() in a loop may not mutate in place in IronPython.
    all_pts = []
    for g in geo:
        bb = g.GetBoundingBox(True)
        all_pts.append(bb.Min)
        all_pts.append(bb.Max)
    union_bb = rg.BoundingBox(all_pts)
    center = union_bb.Center

    # -- rotation transform --
    rot = rg.Transform.Rotation(
        math.radians(rotation),
        rg.Vector3d.ZAxis,
        center
    )

    # -- shear transform --
    # Plan oblique:      true plan on top, walls shear sideways
    #   shears X and Y based on Z height  (z drives x,y)
    # Elevation oblique: true elevation, plan shears behind
    #   shears Z based on X/Y depth       (y drives x,z)
    shear = rg.Transform.Identity

    if plan_ob:
        # plan oblique: z pushes x and y
        shear.M02 = math.tan(math.radians(shear_x))
        shear.M12 = math.tan(math.radians(shear_y))
        mode_name = "Plan oblique"
    else:
        # elevation oblique: y pushes x and z
        # gives a true front elevation with depth receding up and to the side
        shear.M01 = math.tan(math.radians(shear_x))
        shear.M21 = math.tan(math.radians(shear_y))
        mode_name = "Elevation oblique"

    # -- combine: rotate first, then shear --
    combined = shear * rot

    # -- transform copies --
    result = []
    for g in geo:
        copy = g.Duplicate()
        copy.Transform(combined)
        result.append(copy)

    a = result
    info = "{0} | Shear X={1}, Shear Y={2}, Rotation={3}, {4} objects".format(
        mode_name, shear_x, shear_y, rotation, len(result)
    )
