# -*- coding: utf-8 -*-
"""
Test: 24'x60' three-bay extruded plan → watertight STL + 3D screenshot.

Builds a 24' x 60' rectangular plan with walls every 20' along the
60' length (3 structural bays), 30' tall walls, 8'x8' windows on
the short sides (4' above ground), and double doors on both long
sides. No clipping plane, no roof — full-height open-top walls.

Output scale: 1/8" = 1'-0"  (1:96)
Units: feet → mm at print scale

Usage:
    python 3d-print/test_single_bay_stl.py
"""

import copy
import json
import math
import os
import struct
import sys

# Add sibling folder so we can import tactile_print
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "rhino-python-driver"))
import tactile_print as tp

# ── Paths ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_PATH = os.path.join(REPO_ROOT, "rhino-python-driver", "state.json")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "test-output")
STL_PATH = os.path.join(OUTPUT_DIR, "single_bay_extruded.stl")
SCREENSHOT_PATH = os.path.join(OUTPUT_DIR, "single_bay_3d_screenshot.png")
FLOORPLAN_PATH = os.path.join(OUTPUT_DIR, "single_bay_floor_plan.png")


def make_three_bay_state(full_state):
    """Build a 24'x60' plan, 3 bays @ 20', 30' walls, windows + doors.

    Layout (plan view, Y is the 60' long axis, X is 24' short axis):

        Y=0  ── south short wall (8'x8' window, 4' AFF) ──
             |                                              |
             |  Bay 1  (24' x 20')                          |
             |                                              |
        Y=20 ── interior wall (double doors on both sides) ─
             |                                              |
             |  Bay 2  (24' x 20')                          |
             |                                              |
        Y=40 ── interior wall (double doors on both sides) ─
             |                                              |
             |  Bay 3  (24' x 20')                          |
             |                                              |
        Y=60 ── north short wall (8'x8' window, 4' AFF) ──

    X-axis walls = horizontal (gridlines along Y at x=0, x=24)
    Y-axis walls = vertical   (gridlines along X at y=0, y=20, y=40, y=60)

    In the state format:
      bays=[1, 3]  → 1 bay in X (24'), 3 bays in Y (3×20'=60')
      spacing=[24, 20]
      x-axis gridlines: j=0..3 → y=0, 20, 40, 60  (4 horizontal walls)
      y-axis gridlines: i=0..1 → x=0, 24           (2 vertical walls)
    """
    state = copy.deepcopy(full_state)

    bay = state["bays"]["A"]
    bay["origin"] = [0, 0]
    bay["rotation_deg"] = 0.0
    bay["grid_type"] = "rectangular"

    # 1 bay across (24'), 3 bays deep (3 × 20' = 60')
    bay["bays"] = [1, 3]
    bay["spacing"] = [24, 20]
    bay["spacing_x"] = None
    bay["spacing_y"] = None

    bay["walls"]["enabled"] = True
    bay["walls"]["thickness"] = 0.667  # 8" walls in feet

    # ── Apertures ──
    # x-axis gridlines (horizontal walls running along X, at y = 0,20,40,60)
    #   gridline 0 → y=0  (south short wall)    → 8' window centered
    #   gridline 1 → y=20 (first interior wall)  → double doors on each long side
    #   gridline 2 → y=40 (second interior wall) → double doors on each long side
    #   gridline 3 → y=60 (north short wall)     → 8' window centered
    #
    # y-axis gridlines (vertical walls running along Y, at x = 0, 24)
    #   gridline 0 → x=0  (west long wall)  → double doors in each bay
    #   gridline 1 → x=24 (east long wall)  → double doors in each bay

    bay["apertures"] = [
        # ── South short wall (x-axis, gridline 0, wall length = 24') ──
        # 8' wide × 8' tall window, 4' AFF sill, centered (corner at 8')
        {
            "id": "w-south",
            "type": "window",
            "axis": "x",
            "gridline": 0,
            "corner": 8.0,
            "width": 8.0,
            "height": 8.0,
            "sill": 4.0,
            "hinge": "start",
            "swing": "positive"
        },

        # ── North short wall (x-axis, gridline 3, wall length = 24') ──
        # 8' wide × 8' tall window, 4' AFF sill, centered (corner at 8')
        {
            "id": "w-north",
            "type": "window",
            "axis": "x",
            "gridline": 3,
            "corner": 8.0,
            "width": 8.0,
            "height": 8.0,
            "sill": 4.0,
            "hinge": "start",
            "swing": "positive"
        },

        # ── First interior wall (x-axis, gridline 1, wall length = 24') ──
        # Double door pair, centered (two 3' leaves = 6' opening)
        {
            "id": "dd-int1",
            "type": "door",
            "axis": "x",
            "gridline": 1,
            "corner": 9.0,
            "width": 6.0,
            "height": 7.0,
            "hinge": "start",
            "swing": "positive"
        },

        # ── Second interior wall (x-axis, gridline 2, wall length = 24') ──
        # Double door pair, centered
        {
            "id": "dd-int2",
            "type": "door",
            "axis": "x",
            "gridline": 2,
            "corner": 9.0,
            "width": 6.0,
            "height": 7.0,
            "hinge": "start",
            "swing": "positive"
        },

        # ── West long wall (y-axis, gridline 0, wall length = 60') ──
        # Double doors in each of the 3 bays (centered in each 20' bay)
        {
            "id": "dd-west-1",
            "type": "door",
            "axis": "y",
            "gridline": 0,
            "corner": 7.0,       # centered in bay 1 (0-20')
            "width": 6.0,
            "height": 7.0,
            "hinge": "start",
            "swing": "positive"
        },
        {
            "id": "dd-west-2",
            "type": "door",
            "axis": "y",
            "gridline": 0,
            "corner": 27.0,      # centered in bay 2 (20-40')
            "width": 6.0,
            "height": 7.0,
            "hinge": "start",
            "swing": "positive"
        },
        {
            "id": "dd-west-3",
            "type": "door",
            "axis": "y",
            "gridline": 0,
            "corner": 47.0,      # centered in bay 3 (40-60')
            "width": 6.0,
            "height": 7.0,
            "hinge": "start",
            "swing": "positive"
        },

        # ── East long wall (y-axis, gridline 1, wall length = 60') ──
        # Double doors in each of the 3 bays
        {
            "id": "dd-east-1",
            "type": "door",
            "axis": "y",
            "gridline": 1,
            "corner": 7.0,
            "width": 6.0,
            "height": 7.0,
            "hinge": "end",
            "swing": "negative"
        },
        {
            "id": "dd-east-2",
            "type": "door",
            "axis": "y",
            "gridline": 1,
            "corner": 27.0,
            "width": 6.0,
            "height": 7.0,
            "hinge": "end",
            "swing": "negative"
        },
        {
            "id": "dd-east-3",
            "type": "door",
            "axis": "y",
            "gridline": 1,
            "corner": 47.0,
            "width": 6.0,
            "height": 7.0,
            "hinge": "end",
            "swing": "negative"
        },
    ]

    # Only this bay
    state["bays"] = {"A": bay}

    # Site matches the footprint
    state["site"]["origin"] = [-2, -2]
    state["site"]["width"] = 28     # 24' + 4' pad
    state["site"]["height"] = 64    # 60' + 4' pad

    # 30' walls, NO clipping plane (cut_height >= wall_height), no roof
    state["tactile3d"]["enabled"] = True
    state["tactile3d"]["wall_height"] = 30.0
    state["tactile3d"]["cut_height"] = 30.0   # no clip
    state["tactile3d"]["floor_enabled"] = True
    state["tactile3d"]["floor_thickness"] = 0.5

    # Scale: 1/8" = 1'-0"  →  1 ft = 3.175 mm  →  print_scale = 96
    if "bambu" not in state:
        state["bambu"] = {}
    state["bambu"]["print_scale"] = 96

    return state


def read_binary_stl(filepath):
    """Read a binary STL and return list of (normal, v0, v1, v2) tuples."""
    triangles = []
    with open(filepath, "rb") as f:
        f.read(80)  # header
        count = struct.unpack("<I", f.read(4))[0]
        for _ in range(count):
            data = struct.unpack("<12f", f.read(48))
            normal = data[0:3]
            v0 = data[3:6]
            v1 = data[6:9]
            v2 = data[9:12]
            f.read(2)  # attribute byte count
            triangles.append((normal, v0, v1, v2))
    return triangles


def validate_watertight(triangles):
    """Check that the mesh is watertight (every edge shared by exactly 2 triangles).

    Returns (is_watertight, edge_count, boundary_edges, report_str).
    """
    edge_count = {}

    def edge_key(a, b):
        # Round to avoid floating-point mismatch
        a_r = (round(a[0], 6), round(a[1], 6), round(a[2], 6))
        b_r = (round(b[0], 6), round(b[1], 6), round(b[2], 6))
        return (min(a_r, b_r), max(a_r, b_r))

    for _, v0, v1, v2 in triangles:
        for a, b in [(v0, v1), (v1, v2), (v2, v0)]:
            key = edge_key(a, b)
            edge_count[key] = edge_count.get(key, 0) + 1

    total_edges = len(edge_count)
    boundary = [k for k, v in edge_count.items() if v != 2]
    non_manifold = [k for k, v in edge_count.items() if v > 2]

    lines = [
        f"Triangles: {len(triangles)}",
        f"Unique edges: {total_edges}",
        f"Boundary edges (shared by !=2 tris): {len(boundary)}",
        f"Non-manifold edges (shared by >2 tris): {len(non_manifold)}",
    ]

    is_watertight = len(boundary) == 0
    if is_watertight:
        lines.append("PASS: Mesh is watertight.")
    else:
        lines.append(f"FAIL: {len(boundary)} boundary edge(s) found.")

    return is_watertight, total_edges, len(boundary), "\n".join(lines)


def render_screenshot(triangles_ft, output_path):
    """Render a 3D screenshot of the mesh in feet using matplotlib."""
    import matplotlib
    matplotlib.use("Agg")  # headless backend
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(16, 10))
    ax = fig.add_subplot(111, projection="3d")

    # Collect polygon vertices (already in feet)
    polys = []
    for _, v0, v1, v2 in triangles_ft:
        polys.append([list(v0), list(v1), list(v2)])

    # Determine bounds for coloring
    all_z = [v[2] for tri in polys for v in tri]
    z_min, z_max = min(all_z), max(all_z)
    z_range = z_max - z_min if z_max > z_min else 1.0

    # Color faces by average Z height
    face_colors = []
    for tri in polys:
        avg_z = sum(v[2] for v in tri) / 3.0
        t = (avg_z - z_min) / z_range
        # Warm color ramp: floor=blue, walls=orange/red
        r = min(1.0, 0.3 + 0.7 * t)
        g = min(1.0, 0.3 + 0.4 * t)
        b = max(0.0, 0.8 - 0.6 * t)
        face_colors.append((r, g, b, 0.85))

    mesh_collection = Poly3DCollection(polys, facecolors=face_colors,
                                       edgecolors=(0.2, 0.2, 0.2, 0.3),
                                       linewidths=0.15)
    ax.add_collection3d(mesh_collection)

    # Set axis limits from mesh bounds
    all_x = [v[0] for tri in polys for v in tri]
    all_y = [v[1] for tri in polys for v in tri]
    pad = 5.0
    ax.set_xlim(min(all_x) - pad, max(all_x) + pad)
    ax.set_ylim(min(all_y) - pad, max(all_y) + pad)
    ax.set_zlim(min(all_z) - pad, max(all_z) + pad)

    ax.set_xlabel("X (ft)")
    ax.set_ylabel("Y (ft)")
    ax.set_zlabel("Z (ft)")

    ax.set_title("24' x 60' Three-Bay Plan — 30' Walls, Watertight STL\n"
                 f'{len(triangles_ft)} triangles | scale 1/8" = 1\'-0" (1:96)',
                 fontsize=13, fontweight="bold")

    # Isometric-ish view
    ax.view_init(elev=25, azim=-50)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Screenshot saved: {output_path}")


def render_floor_plan(state, output_path):
    """Render a 2D floor plan PNG showing walls, doors, and windows.

    Scale: 1/8" = 1'-0". Drawn in feet, labeled in feet-inches.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyArrowPatch, Arc

    bay = state["bays"]["A"]
    ox, oy = bay["origin"]
    nx, ny = bay["bays"]
    sx, sy = bay["spacing"]
    wall_t = bay["walls"]["thickness"]
    half_t = wall_t / 2.0
    total_x = nx * sx  # 24'
    total_y = ny * sy  # 60'
    aps = bay.get("apertures", [])

    fig, ax = plt.subplots(1, 1, figsize=(8, 16))
    ax.set_aspect("equal")
    ax.set_facecolor("white")

    # ── Draw wall segments ──
    # Cumulative gridline positions
    cx = [i * sx for i in range(nx + 1)]  # [0, 24]
    cy = [j * sy for j in range(ny + 1)]  # [0, 20, 40, 60]

    wall_color = (0.15, 0.15, 0.15)

    def draw_wall_segments(seg_start, seg_end, fixed, axis):
        """Draw a filled wall rectangle."""
        if axis == "x":
            rect = mpatches.Rectangle(
                (ox + seg_start, oy + fixed - half_t),
                seg_end - seg_start, wall_t,
                facecolor=wall_color, edgecolor="black", linewidth=0.5)
        else:
            rect = mpatches.Rectangle(
                (ox + fixed - half_t, oy + seg_start),
                wall_t, seg_end - seg_start,
                facecolor=wall_color, edgecolor="black", linewidth=0.5)
        ax.add_patch(rect)

    # Horizontal walls (x-axis gridlines)
    for j, y_val in enumerate(cy):
        wall_aps = sorted(
            [a for a in aps if a.get("axis") == "x" and a.get("gridline") == j],
            key=lambda a: a.get("corner", 0))
        for seg_s, seg_e in tp._calc_wall_segments(cx[-1], wall_aps):
            if seg_e - seg_s > 0.001:
                draw_wall_segments(seg_s, seg_e, y_val, "x")

    # Vertical walls (y-axis gridlines)
    for i, x_val in enumerate(cx):
        wall_aps = sorted(
            [a for a in aps if a.get("axis") == "y" and a.get("gridline") == i],
            key=lambda a: a.get("corner", 0))
        for seg_s, seg_e in tp._calc_wall_segments(cy[-1], wall_aps):
            if seg_e - seg_s > 0.001:
                draw_wall_segments(seg_s, seg_e, x_val, "y")

    # ── Draw aperture symbols ──
    for ap in aps:
        ap_type = ap.get("type", "door")
        corner = ap.get("corner", 0)
        width = ap.get("width", 3)
        gridline = ap.get("gridline", 0)
        axis = ap.get("axis", "x")

        if axis == "x":
            fixed = cy[gridline]
            x_start = ox + corner
            y_center = oy + fixed
        else:
            fixed = cx[gridline]
            x_center = ox + fixed
            y_start = oy + corner

        if ap_type == "door":
            # Draw door swing arc
            if axis == "x":
                # Horizontal wall — door swings vertically
                mid = x_start + width / 2
                ax.plot([x_start, x_start + width],
                        [y_center, y_center],
                        color="white", linewidth=3, zorder=3)
                # Swing arc
                arc = Arc((x_start, y_center), width * 2, width * 2,
                          angle=0, theta1=0, theta2=90,
                          color=(0.4, 0.4, 0.8), linewidth=1.0, linestyle="--")
                ax.add_patch(arc)
                # Leaf line
                ax.plot([x_start, x_start],
                        [y_center, y_center + width],
                        color=(0.4, 0.4, 0.8), linewidth=0.8)
            else:
                # Vertical wall — door swings horizontally
                mid = y_start + width / 2
                ax.plot([x_center, x_center],
                        [y_start, y_start + width],
                        color="white", linewidth=3, zorder=3)
                arc = Arc((x_center, y_start), width * 2, width * 2,
                          angle=0, theta1=0, theta2=90,
                          color=(0.4, 0.4, 0.8), linewidth=1.0, linestyle="--")
                ax.add_patch(arc)
                ax.plot([x_center, x_center + width],
                        [y_start, y_start],
                        color=(0.4, 0.4, 0.8), linewidth=0.8)

            # Label
            if axis == "x":
                ax.text(x_start + width / 2, y_center + 1.5,
                        ap["id"].upper(), ha="center", va="bottom",
                        fontsize=7, color=(0.3, 0.3, 0.7))
            else:
                ax.text(x_center + 1.5, y_start + width / 2,
                        ap["id"].upper(), ha="left", va="center",
                        fontsize=7, color=(0.3, 0.3, 0.7))

        elif ap_type == "window":
            # Draw window as parallel lines across the opening
            if axis == "x":
                ax.plot([x_start, x_start + width],
                        [y_center, y_center],
                        color="white", linewidth=3, zorder=3)
                # Glass lines
                for offset in [-half_t * 0.5, half_t * 0.5]:
                    ax.plot([x_start, x_start + width],
                            [y_center + offset, y_center + offset],
                            color=(0.2, 0.5, 0.8), linewidth=1.2, zorder=4)
                ax.text(x_start + width / 2, y_center - 1.5,
                        ap["id"].upper(), ha="center", va="top",
                        fontsize=7, color=(0.2, 0.5, 0.8))
            else:
                ax.plot([x_center, x_center],
                        [y_start, y_start + width],
                        color="white", linewidth=3, zorder=3)
                for offset in [-half_t * 0.5, half_t * 0.5]:
                    ax.plot([x_center + offset, x_center + offset],
                            [y_start, y_start + width],
                            color=(0.2, 0.5, 0.8), linewidth=1.2, zorder=4)
                ax.text(x_center - 1.5, y_start + width / 2,
                        ap["id"].upper(), ha="right", va="center",
                        fontsize=7, color=(0.2, 0.5, 0.8))

    # ── Gridline dashes ──
    for y_val in cy:
        ax.axhline(oy + y_val, color=(0.7, 0.7, 0.7), linewidth=0.3,
                    linestyle=":", zorder=0)
    for x_val in cx:
        ax.axvline(ox + x_val, color=(0.7, 0.7, 0.7), linewidth=0.3,
                    linestyle=":", zorder=0)

    # ── Dimension labels ──
    # Overall X dimension
    ax.annotate("", xy=(ox + total_x, oy - 4), xytext=(ox, oy - 4),
                arrowprops=dict(arrowstyle="<->", color="black", lw=0.8))
    ax.text(ox + total_x / 2, oy - 5, f"{int(total_x)}'-0\"",
            ha="center", va="top", fontsize=9, fontweight="bold")

    # Overall Y dimension
    ax.annotate("", xy=(ox - 4, oy + total_y), xytext=(ox - 4, oy),
                arrowprops=dict(arrowstyle="<->", color="black", lw=0.8))
    ax.text(ox - 5, oy + total_y / 2, f"{int(total_y)}'-0\"",
            ha="right", va="center", fontsize=9, fontweight="bold", rotation=90)

    # Bay spacing labels along Y
    for j in range(ny):
        mid_y = oy + cy[j] + sy / 2
        ax.text(ox + total_x + 2, mid_y,
                f"Bay {j+1}\n{int(sy)}'-0\"",
                ha="left", va="center", fontsize=8, color=(0.3, 0.3, 0.3))

    # ── Title ──
    ax.set_title("Floor Plan — 24' x 60' Three-Bay Layout\n"
                 'scale 1/8" = 1\'-0"  |  8" walls  |  30\' wall height',
                 fontsize=12, fontweight="bold", pad=15)

    ax.set_xlabel("X (ft)")
    ax.set_ylabel("Y (ft)")
    ax.set_xlim(ox - 8, ox + total_x + 10)
    ax.set_ylim(oy - 8, oy + total_y + 4)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Floor plan saved: {output_path}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load full state
    print(f"Loading state from {STATE_PATH}")
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        full_state = json.load(f)

    # 2. Build three-bay state (24'x60', 30' walls, windows + doors)
    state = make_three_bay_state(full_state)
    single_bay_state_path = os.path.join(OUTPUT_DIR, "single_bay_state.json")
    with open(single_bay_state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    print(f"Single-bay state written: {single_bay_state_path}")

    # 3. Build mesh and export STL
    print("\nBuilding mesh...")
    triangles_ft = tp.build_mesh(state)
    print(f"  Triangles (feet): {len(triangles_ft)}")

    # Preview
    print("\n" + tp.preview(state))

    # Export STL (scaled to mm, centered)
    print(f"\nExporting STL to {STL_PATH}")
    path, count, size_mm = tp.export_stl(state, STL_PATH)
    file_size = os.path.getsize(path)
    print(f"  Wrote {count} triangles, {file_size:,} bytes")
    print(f"  Print dimensions: {size_mm[0]:.1f} x {size_mm[1]:.1f} x {size_mm[2]:.1f} mm")

    # 4. Validate watertightness
    print("\nValidating watertightness...")
    stl_tris = read_binary_stl(STL_PATH)
    is_wt, edge_ct, boundary_ct, report = validate_watertight(stl_tris)
    print(report)

    # 5. Render 3D screenshot (in feet, not mm)
    print(f"\nRendering 3D screenshot to {SCREENSHOT_PATH}")
    render_screenshot(triangles_ft, SCREENSHOT_PATH)

    # 6. Render floor plan
    print(f"\nRendering floor plan to {FLOORPLAN_PATH}")
    render_floor_plan(state, FLOORPLAN_PATH)

    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"  STL file:       {STL_PATH}")
    print(f"  Screenshot:     {SCREENSHOT_PATH}")
    print(f"  Floor plan:     {FLOORPLAN_PATH}")
    print(f"  Triangles:      {count}")
    print(f"  Watertight:     {'YES' if is_wt else 'NO'}")
    print(f"  Boundary edges: {boundary_ct}")
    print(f"  File size:      {file_size:,} bytes")

    if not is_wt:
        print("\n  WARNING: Mesh is NOT watertight!")
        sys.exit(1)
    else:
        print("\n  All checks passed.")

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
