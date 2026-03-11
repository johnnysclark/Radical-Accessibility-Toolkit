# -*- coding: utf-8 -*-
"""
OBLIQUE PROJECTION TOOL — Rhino Python Script
==============================================
Creates an oblique projection copy of selected 3D geometry by applying
a shear transformation. The result is a 3D object suitable for Make2D.

Oblique projection maps each point (x, y, z) to:
    x' = x + z * tan(shear_angle_x)
    y' = y + z * tan(shear_angle_y)
    z' = z

The base model can optionally be rotated around the Z axis before
shearing, which controls which face of the model is prominent.

Usage:
    1. Run this script inside Rhino (EditPythonScript or RunPythonScript).
    2. Select objects when prompted.
    3. Enter shear angle X (degrees) — lateral shear, default 30.
    4. Enter shear angle Y (degrees) — vertical shear, default 30.
    5. Enter base rotation (degrees) — Z-axis rotation, default 0.
    6. The script copies selected objects, applies rotation then shear,
       and places the result on layer "OBLIQUE_PROJECTION".
    7. Run Make2D on the result for a 2D oblique drawing.

Common presets:
    Cavalier:   shear_x=45, shear_y=0,  rotation per taste
    Cabinet:    shear_x=45, shear_y=0   (then scale Z by 0.5)
    Military:   shear_x=0,  shear_y=0,  rotation=45 (plan oblique)
    Isometric-like: shear_x=30, shear_y=30

Run inside Rhino:
    exec(open("C:/path/to/oblique_projection.py").read())
"""

import math

try:
    import rhinoscriptsyntax as rs
    import Rhino
    import scriptcontext as sc
except ImportError:
    raise RuntimeError("This script must be run inside Rhino Python.")


def get_user_inputs():
    """Prompt user for shear angles and rotation via Rhino command line."""
    shear_x = rs.GetReal(
        "Shear angle X in degrees (lateral tilt)", 30.0, -89.0, 89.0
    )
    if shear_x is None:
        return None
    shear_y = rs.GetReal(
        "Shear angle Y in degrees (depth tilt)", 30.0, -89.0, 89.0
    )
    if shear_y is None:
        return None
    rotation = rs.GetReal(
        "Base rotation around Z axis in degrees", 0.0, -360.0, 360.0
    )
    if rotation is None:
        return None
    return shear_x, shear_y, rotation


def build_shear_transform(shear_angle_x_deg, shear_angle_y_deg):
    """Build a 4x4 shear matrix for oblique projection.

    Maps (x, y, z) -> (x + z*tan(ax), y + z*tan(ay), z).
    """
    ax = math.radians(shear_angle_x_deg)
    ay = math.radians(shear_angle_y_deg)
    tx = math.tan(ax)
    ty = math.tan(ay)

    xform = Rhino.Geometry.Transform.Identity
    # Row 0, Col 2: x += z * tan(shear_x)
    xform.M02 = tx
    # Row 1, Col 2: y += z * tan(shear_y)
    xform.M12 = ty
    return xform


def build_rotation_transform(rotation_deg, center):
    """Build a Z-axis rotation transform around a given center point."""
    angle_rad = math.radians(rotation_deg)
    xform = Rhino.Geometry.Transform.Rotation(
        angle_rad,
        Rhino.Geometry.Vector3d.ZAxis,
        Rhino.Geometry.Point3d(center[0], center[1], center[2])
    )
    return xform


def ensure_layer(name):
    """Create layer if it does not exist, return name."""
    if not rs.IsLayer(name):
        rs.AddLayer(name)
    return name


def run():
    """Main entry point."""
    # Select objects
    obj_ids = rs.GetObjects(
        "Select objects for oblique projection", preselect=True
    )
    if not obj_ids:
        print("ERROR: No objects selected.")
        return

    # Get parameters
    params = get_user_inputs()
    if params is None:
        print("ERROR: Cancelled by user.")
        return
    shear_x, shear_y, rotation = params

    # Compute bounding box center for rotation pivot
    all_bb = rs.BoundingBox(obj_ids)
    if not all_bb:
        print("ERROR: Could not compute bounding box.")
        return
    # BoundingBox returns 8 corner points; center is average of [0] and [6]
    p0 = all_bb[0]
    p6 = all_bb[6]
    center = (
        (p0[0] + p6[0]) / 2.0,
        (p0[1] + p6[1]) / 2.0,
        (p0[2] + p6[2]) / 2.0,
    )

    # Build transforms
    rot_xform = build_rotation_transform(rotation, center)
    shear_xform = build_shear_transform(shear_x, shear_y)
    # Combined: first rotate, then shear
    combined = shear_xform * rot_xform

    # Prepare target layer
    layer_name = ensure_layer("OBLIQUE_PROJECTION")

    # Copy and transform
    rs.EnableRedraw(False)
    try:
        copied = rs.CopyObjects(obj_ids)
        if not copied:
            print("ERROR: Failed to copy objects.")
            return

        for obj_id in copied:
            rs.TransformObject(obj_id, combined)
            rs.ObjectLayer(obj_id, layer_name)

        rs.EnableRedraw(True)
        rs.ZoomExtents()
    except Exception as e:
        rs.EnableRedraw(True)
        print("ERROR: Transform failed — {0}".format(str(e)))
        return

    print("OK: Oblique projection created on layer OBLIQUE_PROJECTION.")
    print("  Shear X: {0} deg, Shear Y: {1} deg, Rotation: {2} deg".format(
        shear_x, shear_y, rotation
    ))
    print("  {0} objects copied and transformed.".format(len(copied)))
    print("  Use Make2D on the OBLIQUE_PROJECTION layer for a 2D drawing.")
    print("READY:")


if __name__ == "__main__":
    run()
# When run via exec(), also call run directly.
elif __name__ != "__test__":
    run()
