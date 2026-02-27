# -*- coding: utf-8 -*-
"""
Test: Single-bay extruded plan layout → watertight STL + 3D screenshot.

Isolates Bay A (single 1×1 bay subset) from state.json, builds the
watertight mesh via tactile_print.build_mesh(), exports binary STL,
validates watertightness, and saves a matplotlib 3D screenshot.

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


def make_single_bay_state(full_state):
    """Extract Bay A as a single 1×1 bay with walls and one door aperture."""
    state = copy.deepcopy(full_state)

    # Keep only Bay A, set it to a single 1×1 bay
    bay_a = state["bays"]["A"]
    bay_a["bays"] = [1, 1]
    bay_a["spacing"] = [24, 24]
    bay_a["spacing_x"] = None
    bay_a["spacing_y"] = None
    bay_a["walls"]["enabled"] = True
    bay_a["walls"]["thickness"] = 0.5

    # Explicit apertures: door on south wall, window on east wall,
    # door on north wall, window on west wall — all cut into the walls.
    bay_a["apertures"] = [
        {
            "id": "d1",
            "type": "door",
            "axis": "x",        # horizontal wall (south, gridline 0)
            "gridline": 0,
            "corner": 8.0,      # 8 ft from left corner
            "width": 3.0,       # 3 ft wide door opening
            "height": 7.0,
            "hinge": "start",
            "swing": "positive"
        },
        {
            "id": "w1",
            "type": "window",
            "axis": "y",        # vertical wall (west, gridline 0)
            "gridline": 0,
            "corner": 6.0,      # 6 ft from bottom corner
            "width": 6.0,       # 6 ft wide window opening
            "height": 4.0,
            "hinge": "start",
            "swing": "positive"
        },
        {
            "id": "d2",
            "type": "door",
            "axis": "x",        # horizontal wall (north, gridline 1)
            "gridline": 1,
            "corner": 10.0,     # 10 ft from left corner
            "width": 4.0,       # 4 ft wide door opening
            "height": 7.0,
            "hinge": "end",
            "swing": "negative"
        },
        {
            "id": "w2",
            "type": "window",
            "axis": "y",        # vertical wall (east, gridline 1)
            "gridline": 1,
            "corner": 8.0,      # 8 ft from bottom corner
            "width": 5.0,       # 5 ft wide window opening
            "height": 4.0,
            "hinge": "start",
            "swing": "positive"
        },
    ]

    # Remove other bays
    state["bays"] = {"A": bay_a}

    # Shrink site to match single bay
    state["site"]["origin"] = [bay_a["origin"][0] - 2, bay_a["origin"][1] - 2]
    state["site"]["width"] = 28
    state["site"]["height"] = 28

    # Enable tactile3d
    state["tactile3d"]["enabled"] = True
    state["tactile3d"]["wall_height"] = 9.0
    state["tactile3d"]["cut_height"] = 4.0
    state["tactile3d"]["floor_enabled"] = True
    state["tactile3d"]["floor_thickness"] = 0.5

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


def render_screenshot(stl_path, output_path):
    """Render a 3D screenshot of the STL using matplotlib."""
    import matplotlib
    matplotlib.use("Agg")  # headless backend
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    triangles = read_binary_stl(stl_path)

    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection="3d")

    # Collect polygon vertices for Poly3DCollection
    polys = []
    for _, v0, v1, v2 in triangles:
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
    pad = 2.0
    ax.set_xlim(min(all_x) - pad, max(all_x) + pad)
    ax.set_ylim(min(all_y) - pad, max(all_y) + pad)
    ax.set_zlim(min(all_z) - pad, max(all_z) + pad)

    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")
    ax.set_zlabel("Z (mm)")

    ax.set_title("Single Bay — Extruded Plan Layout (Watertight STL)\n"
                 f"{len(triangles)} triangles, scale 1:200",
                 fontsize=13, fontweight="bold")

    # Isometric-ish view
    ax.view_init(elev=30, azim=-55)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Screenshot saved: {output_path}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load full state
    print(f"Loading state from {STATE_PATH}")
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        full_state = json.load(f)

    # 2. Build single-bay state
    state = make_single_bay_state(full_state)
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

    # 5. Render 3D screenshot
    print(f"\nRendering 3D screenshot to {SCREENSHOT_PATH}")
    render_screenshot(STL_PATH, SCREENSHOT_PATH)

    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"  STL file:       {STL_PATH}")
    print(f"  Screenshot:     {SCREENSHOT_PATH}")
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
