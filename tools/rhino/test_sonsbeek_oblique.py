# Test: Sonsbeek Pavilion oblique projection
# Run in Rhino EditPythonScript to generate geometry, then test in Grasshopper.
#
# Creates a simplified Rietveld Sonsbeek Pavilion (1955) with:
#   - Freestanding walls at varying heights (De Stijl composition)
#   - Floating roof planes supported by thin steel columns
#   - Ground plane / gravel pad
#   - Surrounding trees (simplified cones)
#
# Geometry is placed on three layers for Grasshopper testing:
#   SONSBEEK::Architecture  — walls, columns, roof planes
#   SONSBEEK::Ground        — ground slab, pathways
#   SONSBEEK::Foliage       — trees, hedges
#
# In Grasshopper:
#   1. Use three Pipeline components, one per layer
#   2. Wire into a Merge component
#   3. Connect Merge output to the oblique projection script (geo input, Tree Access)
#   4. Use Explode Tree after to split back into 3 branches
#   5. Connect each branch to Custom Preview with different materials
#
# Recommended test: preset 1 (Cabinet 45), rotation 30, cut on, cut_axis 2, cut_h 2.5
# All dimensions in meters.

import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import math


def ensure_layer(name, color):
    """Create layer if it doesn't exist, set color."""
    if not rs.IsLayer(name):
        rs.AddLayer(name, color)
    else:
        rs.LayerColor(name, color)


def add_box(x, y, z, w, d, h, layer):
    """Add a box (wall, slab, column) at position with size, on layer."""
    corner = rg.Point3d(x, y, z)
    plane = rg.Plane(corner, rg.Vector3d.ZAxis)
    box = rg.Box(plane, rg.Interval(0, w), rg.Interval(0, d), rg.Interval(0, h))
    brep = box.ToBrep()
    obj_id = rs.coerceguid(Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(brep))
    if obj_id:
        rs.ObjectLayer(obj_id, layer)
    return obj_id


def add_cone_tree(cx, cy, trunk_h, crown_h, crown_r, layer):
    """Add a simplified tree: cylinder trunk + cone crown."""
    import Rhino
    trunk_r = 0.08
    # trunk
    trunk_base = rg.Circle(rg.Plane(rg.Point3d(cx, cy, 0), rg.Vector3d.ZAxis), trunk_r)
    trunk = rg.Cylinder(trunk_base, trunk_h)
    trunk_brep = trunk.ToBrep(True, True)
    tid = rs.coerceguid(Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(trunk_brep))
    if tid:
        rs.ObjectLayer(tid, layer)

    # crown (cone)
    cone_base = rg.Circle(
        rg.Plane(rg.Point3d(cx, cy, trunk_h), rg.Vector3d.ZAxis), crown_r)
    cone = rg.Cone(
        rg.Plane(rg.Point3d(cx, cy, trunk_h + crown_h), -rg.Vector3d.ZAxis),
        crown_h, crown_r)
    cone_brep = cone.ToBrep(True)
    cid = rs.coerceguid(Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(cone_brep))
    if cid:
        rs.ObjectLayer(cid, layer)


# ================================================================
# SETUP LAYERS
# ================================================================
import Rhino

ARCH_LAYER = "SONSBEEK::Architecture"
GROUND_LAYER = "SONSBEEK::Ground"
FOLIAGE_LAYER = "SONSBEEK::Foliage"

# parent layer
if not rs.IsLayer("SONSBEEK"):
    rs.AddLayer("SONSBEEK")

ensure_layer(ARCH_LAYER, [200, 200, 200])   # light gray
ensure_layer(GROUND_LAYER, [180, 160, 120])  # warm beige
ensure_layer(FOLIAGE_LAYER, [80, 140, 70])   # green

rs.EnableRedraw(False)

try:
    # ================================================================
    # GROUND — gravel pad and pathway
    # ================================================================

    # main gravel pad under pavilion
    add_box(-1, -1, -0.05, 16, 12, 0.05, GROUND_LAYER)

    # approach path
    add_box(5, -4, -0.03, 2.5, 3, 0.03, GROUND_LAYER)

    # ================================================================
    # ARCHITECTURE — Rietveld-inspired freestanding walls + roof + columns
    # ================================================================
    # The Sonsbeek pavilion has walls that slide past each other,
    # never forming enclosed rooms. De Stijl: orthogonal, asymmetric.

    wall_t = 0.12  # wall thickness (brick)

    # --- Long walls (running in X direction) ---

    # Wall A — south long wall, low
    add_box(0, 0, 0, 10, wall_t, 2.8, ARCH_LAYER)

    # Wall B — north long wall, extends past roof, taller
    add_box(2, 8, 0, 12, wall_t, 3.2, ARCH_LAYER)

    # Wall C — interior long wall, mid-height, offset
    add_box(4, 4, 0, 7, wall_t, 2.5, ARCH_LAYER)

    # --- Short walls (running in Y direction) ---

    # Wall D — west short wall
    add_box(0, 0, 0, wall_t, 5, 3.0, ARCH_LAYER)

    # Wall E — east closing wall, partial height
    add_box(12, 3, 0, wall_t, 6, 2.8, ARCH_LAYER)

    # Wall F — interior divider, short
    add_box(6, 2, 0, wall_t, 3, 2.2, ARCH_LAYER)

    # Wall G — freestanding screen wall, sculpture backdrop
    add_box(8, 5, 0, wall_t, 4, 3.0, ARCH_LAYER)

    # --- Roof planes (floating, supported by columns) ---

    # Main roof — large floating plane
    add_box(1, 0.5, 3.2, 10, 8, 0.1, ARCH_LAYER)

    # Secondary roof — cantilevered overhang
    add_box(7, 3, 3.0, 6, 6, 0.08, ARCH_LAYER)

    # --- Steel columns (thin square section) ---
    col_size = 0.08  # 80mm steel column

    # Columns supporting main roof
    col_positions = [
        (1.5, 1),
        (1.5, 7),
        (5, 1),
        (5, 7),
        (10, 1),
        (10, 7),
    ]
    for cx, cy in col_positions:
        add_box(cx, cy, 0, col_size, col_size, 3.2, ARCH_LAYER)

    # Columns supporting secondary roof
    sec_col_positions = [
        (8, 4),
        (8, 8),
        (12, 4),
        (12, 8),
    ]
    for cx, cy in sec_col_positions:
        add_box(cx, cy, 0, col_size, col_size, 3.0, ARCH_LAYER)

    # --- Low plinth / bench (Rietveld often included built-in seating) ---
    add_box(2, 1, 0, 3, 0.5, 0.45, ARCH_LAYER)

    # ================================================================
    # FOLIAGE — surrounding trees
    # ================================================================

    # Trees around the pavilion (park setting, Sonsbeek is in a park)
    tree_positions = [
        (-2, -2, 3.5, 4.0, 1.8),   # (cx, cy, trunk_h, crown_h, crown_r)
        (-2, 10, 4.0, 5.0, 2.2),
        (16, -1, 3.0, 3.5, 1.5),
        (16, 10, 4.5, 5.5, 2.5),
        (7, -3, 3.5, 4.5, 2.0),
        (-3, 5, 4.0, 4.0, 1.8),
        (17, 5, 3.5, 4.0, 2.0),
    ]
    for cx, cy, th, ch, cr in tree_positions:
        add_cone_tree(cx, cy, th, ch, cr, FOLIAGE_LAYER)

    # Low hedge along south edge
    add_box(-1, -2, 0, 8, 0.6, 0.8, FOLIAGE_LAYER)

finally:
    rs.EnableRedraw(True)

rs.ZoomExtents()

# ================================================================
# REPORT
# ================================================================
arch_count = len(rs.ObjectsByLayer(ARCH_LAYER))
ground_count = len(rs.ObjectsByLayer(GROUND_LAYER))
foliage_count = len(rs.ObjectsByLayer(FOLIAGE_LAYER))

print("OK: Sonsbeek Pavilion test geometry created.")
print("  {0} architecture objects on {1}".format(arch_count, ARCH_LAYER))
print("  {0} ground objects on {1}".format(ground_count, GROUND_LAYER))
print("  {0} foliage objects on {1}".format(foliage_count, FOLIAGE_LAYER))
print("")
print("Grasshopper test setup:")
print("  1. Add 3 Pipeline components, one per SONSBEEK sub-layer")
print("  2. Wire all 3 into a Merge component")
print("  3. Connect Merge result to oblique projection geo input (Tree Access)")
print("  4. Connect output a to Explode Tree")
print("  5. Wire each Explode Tree branch to a Custom Preview")
print("")
print("Recommended settings:")
print("  preset=1 (Cabinet 45), rotation=30")
print("  cut=on, cut_axis=2 (Z), cut_h=2.5 (cuts through walls, below roof)")
print("  grid_on=on, grid_sp=1.0")
print("READY:")
