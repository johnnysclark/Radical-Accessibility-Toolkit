# Oblique Projection — paste into Rhino EditPythonScript and hit Run
# Copies selected 3D objects, applies rotation + shear, ready for Make2D
#
# Variables:
#   shear_x  — shear angle in degrees along X (lateral tilt)
#   shear_y  — shear angle in degrees along Y (depth tilt)
#   rotation — rotate the base model around Z before shearing
#
# Common combos:
#   Cavalier:       shear_x=45, shear_y=0
#   Plan oblique:   shear_x=0,  shear_y=0,  rotation=45
#   Isometric-ish:  shear_x=30, shear_y=30

import math
import rhinoscriptsyntax as rs
import Rhino

# --- select objects ---
obj_ids = rs.GetObjects("Select objects for oblique projection", preselect=True)
if not obj_ids:
    print("Nothing selected.")

else:
    # --- get parameters ---
    shear_x = rs.GetReal("Shear angle X degrees (lateral)", 30.0, -89.0, 89.0)
    shear_y = rs.GetReal("Shear angle Y degrees (depth)", 30.0, -89.0, 89.0)
    rotation = rs.GetReal("Rotation around Z degrees", 0.0, -360.0, 360.0)

    if shear_x is not None and shear_y is not None and rotation is not None:

        # --- find bounding box center as pivot ---
        bb = rs.BoundingBox(obj_ids)
        p0 = bb[0]
        p6 = bb[6]
        cx = (p0[0] + p6[0]) / 2.0
        cy = (p0[1] + p6[1]) / 2.0
        cz = (p0[2] + p6[2]) / 2.0
        center = Rhino.Geometry.Point3d(cx, cy, cz)

        # --- build rotation transform ---
        rot = Rhino.Geometry.Transform.Rotation(
            math.radians(rotation),
            Rhino.Geometry.Vector3d.ZAxis,
            center
        )

        # --- build shear transform ---
        # Maps (x,y,z) to (x + z*tan(ax), y + z*tan(ay), z)
        shear = Rhino.Geometry.Transform.Identity
        shear.M02 = math.tan(math.radians(shear_x))
        shear.M12 = math.tan(math.radians(shear_y))

        # --- combine: rotate first, then shear ---
        combined = shear * rot

        # --- make layer ---
        if not rs.IsLayer("OBLIQUE_PROJECTION"):
            rs.AddLayer("OBLIQUE_PROJECTION")

        # --- copy, transform, assign layer ---
        rs.EnableRedraw(False)
        copied = rs.CopyObjects(obj_ids)
        for obj in copied:
            rs.TransformObject(obj, combined)
            rs.ObjectLayer(obj, "OBLIQUE_PROJECTION")
        rs.EnableRedraw(True)

        rs.ZoomExtents()

        print("{0} objects projected.".format(len(copied)))
        print("Shear X={0}, Shear Y={1}, Rotation={2}".format(shear_x, shear_y, rotation))
        print("Result on layer OBLIQUE_PROJECTION — run Make2D on it.")
