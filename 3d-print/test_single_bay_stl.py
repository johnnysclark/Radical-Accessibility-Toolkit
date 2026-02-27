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
import datetime
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
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
STL_PATH = os.path.join(OUTPUT_DIR, "single_bay_extruded_{}.stl".format(TIMESTAMP))
OBJ_PATH = os.path.join(OUTPUT_DIR, "single_bay_model_{}.obj".format(TIMESTAMP))
FLOORPLAN_PATH = os.path.join(OUTPUT_DIR, "single_bay_floor_plan_{}.png".format(TIMESTAMP))
AXON_PATH = os.path.join(OUTPUT_DIR, "single_bay_axon_pen_{}.png".format(TIMESTAMP))


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

    bay["z_order"] = 1  # Bay A takes precedence where they overlap

    # ── Bay B: same size, rotated 45°, 10' tall ──
    bay_b = copy.deepcopy(bay)
    bay_b["origin"] = [16, 40]        # offset so ~1/3 of bay A is covered
    bay_b["rotation_deg"] = 45.0
    bay_b["z_order"] = 0              # lower z_order = drawn behind bay A
    bay_b["wall_height"] = 10.0       # 10' tall (vs bay A's 30')
    bay_b["label"] = "Bay B"
    bay_b["braille"] = ""
    # Same apertures, relabeled
    for ap in bay_b["apertures"]:
        ap["id"] = "B-" + ap["id"]

    state["bays"] = {"A": bay, "B": bay_b}

    # Site big enough for both bays (rotated bay extends ~60' diagonally)
    state["site"]["origin"] = [-50, -10]
    state["site"]["width"] = 110
    state["site"]["height"] = 120

    # Bay A: 30' walls. Bay B: 10' walls (handled per-bay via wall_height).
    # tactile3d wall_height is the global max; per-bay height set below.
    state["tactile3d"]["enabled"] = True
    state["tactile3d"]["wall_height"] = 30.0
    state["tactile3d"]["cut_height"] = 30.0   # no clip
    state["tactile3d"]["floor_enabled"] = False
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


def export_obj(triangles_ft, output_path):
    """Export mesh as Wavefront OBJ file (feet units).

    OBJ files can be opened on iPhone via Quick Look, Files app,
    or free viewers like 'Reality Composer' / '3D Scanner App'.
    """
    # De-duplicate vertices
    vert_map = {}
    verts = []
    faces = []

    def get_idx(v):
        key = (round(v[0], 6), round(v[1], 6), round(v[2], 6))
        if key not in vert_map:
            vert_map[key] = len(verts) + 1  # OBJ is 1-indexed
            verts.append(key)
        return vert_map[key]

    for _, v0, v1, v2 in triangles_ft:
        i0 = get_idx(v0)
        i1 = get_idx(v1)
        i2 = get_idx(v2)
        faces.append((i0, i1, i2))

    with open(output_path, "w") as f:
        f.write("# Plan Layout Jig — Two-Bay Model\n")
        f.write(f"# {len(verts)} vertices, {len(faces)} faces\n")
        f.write(f"# Units: feet\n\n")
        for v in verts:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        f.write("\n")
        for fa in faces:
            f.write(f"f {fa[0]} {fa[1]} {fa[2]}\n")

    print(f"OBJ saved: {output_path} ({len(verts)} verts, {len(faces)} faces)")


def render_axon_pen(triangles_ft, output_path):
    """Render a black-and-white axonometric pen drawing with hidden lines dashed.

    Uses an isometric projection, extracts silhouette and crease edges,
    then classifies each edge as visible or hidden by testing against
    the projected triangles (z-buffer style depth test at edge midpoints).

    Visible edges: solid black.
    Hidden edges: dashed light gray.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    # ── Isometric camera — looking DOWN from above ──
    az = math.radians(-50)
    el = math.radians(-55)  # negative = looking downward

    # Camera basis vectors (right-hand coordinate system)
    # Forward = into screen, Right = screen X, Up = screen Y
    fwd = np.array([math.cos(el)*math.sin(az),
                     math.cos(el)*math.cos(az),
                     math.sin(el)])
    world_up = np.array([0, 0, 1.0])
    right = np.cross(fwd, world_up)
    right = right / np.linalg.norm(right)
    up = np.cross(right, fwd)
    up = up / np.linalg.norm(up)

    def project(pt):
        """Project a 3D point to 2D screen coords + depth."""
        p = np.array(pt)
        sx = float(np.dot(p, right))
        sy = float(np.dot(p, up))
        depth = float(np.dot(p, fwd))
        return sx, sy, depth

    # ── Project all triangles ──
    proj_tris = []  # list of ((sx0,sy0,d0), (sx1,sy1,d1), (sx2,sy2,d2))
    for _, v0, v1, v2 in triangles_ft:
        p0 = project(v0)
        p1 = project(v1)
        p2 = project(v2)
        proj_tris.append((p0, p1, p2))

    # ── Extract unique edges with face normals for silhouette detection ──
    # Each edge maps to list of face indices
    edge_faces = {}

    def edge_key(i, j):
        return (min(i, j), max(i, j))

    # Build vertex list and triangle index list
    vert_map = {}
    verts_3d = []
    tri_indices = []

    def get_vert_idx(v):
        key = (round(v[0], 5), round(v[1], 5), round(v[2], 5))
        if key not in vert_map:
            vert_map[key] = len(verts_3d)
            verts_3d.append(v)
        return vert_map[key]

    for fi, (_, v0, v1, v2) in enumerate(triangles_ft):
        i0 = get_vert_idx(v0)
        i1 = get_vert_idx(v1)
        i2 = get_vert_idx(v2)
        tri_indices.append((i0, i1, i2))
        for ea, eb in [(i0, i1), (i1, i2), (i2, i0)]:
            ek = edge_key(ea, eb)
            if ek not in edge_faces:
                edge_faces[ek] = []
            edge_faces[ek].append(fi)

    # ── Compute face normals in projected view ──
    face_dots = []  # dot(face_normal, view_dir) for back-face test
    for _, v0, v1, v2 in triangles_ft:
        n = tp._tri_normal(v0, v1, v2)
        dot = n[0]*fwd[0] + n[1]*fwd[1] + n[2]*fwd[2]
        face_dots.append(dot)

    # ── Select edges to draw ──
    # Silhouette: edge shared by one front-facing and one back-facing tri
    # Crease/boundary: edge shared by only one face, or angle > threshold
    draw_edges = []  # (vert_idx_a, vert_idx_b)

    for (ia, ib), faces in edge_faces.items():
        if len(faces) == 1:
            # Boundary edge — always draw
            draw_edges.append((ia, ib))
        elif len(faces) == 2:
            d0 = face_dots[faces[0]]
            d1 = face_dots[faces[1]]
            # Silhouette: one face front, one face back
            if d0 * d1 < 0:
                draw_edges.append((ia, ib))
            # Crease: both front-facing but normals differ significantly
            elif d0 < 0 and d1 < 0:
                n0 = tp._tri_normal(*[verts_3d[k] for k in tri_indices[faces[0]]])
                n1 = tp._tri_normal(*[verts_3d[k] for k in tri_indices[faces[1]]])
                cos_angle = n0[0]*n1[0] + n0[1]*n1[1] + n0[2]*n1[2]
                if cos_angle < 0.95:  # > ~18° crease
                    draw_edges.append((ia, ib))

    # ── Project edges and classify visibility ──
    # Build 2D projected triangle list for occlusion testing
    proj_2d_tris = []  # (2D verts, min_depth) for front-facing tris only
    for fi, (p0, p1, p2) in enumerate(proj_tris):
        if face_dots[fi] < 0:  # front-facing
            proj_2d_tris.append(((p0, p1, p2), min(p0[2], p1[2], p2[2])))

    def point_in_triangle_2d(px, py, t0, t1, t2):
        """Barycentric test: is (px,py) inside triangle (t0,t1,t2)?"""
        dx0 = t1[0] - t0[0]; dy0 = t1[1] - t0[1]
        dx1 = t2[0] - t0[0]; dy1 = t2[1] - t0[1]
        dx2 = px - t0[0]; dy2 = py - t0[1]
        d00 = dx0*dx0 + dy0*dy0
        d01 = dx0*dx1 + dy0*dy1
        d11 = dx1*dx1 + dy1*dy1
        d20 = dx2*dx0 + dy2*dy0
        d21 = dx2*dx1 + dy2*dy1
        denom = d00*d11 - d01*d01
        if abs(denom) < 1e-12:
            return False
        v = (d11*d20 - d01*d21) / denom
        w = (d00*d21 - d01*d20) / denom
        return v >= 0 and w >= 0 and (v + w) <= 1

    def tri_depth_at(px, py, p0, p1, p2):
        """Interpolate depth at (px,py) inside projected triangle."""
        dx0 = p1[0]-p0[0]; dy0 = p1[1]-p0[1]
        dx1 = p2[0]-p0[0]; dy1 = p2[1]-p0[1]
        dx2 = px-p0[0]; dy2 = py-p0[1]
        d00 = dx0*dx0+dy0*dy0
        d01 = dx0*dx1+dy0*dy1
        d11 = dx1*dx1+dy1*dy1
        d20 = dx2*dx0+dy2*dy0
        d21 = dx2*dx1+dy2*dy1
        denom = d00*d11-d01*d01
        if abs(denom) < 1e-12:
            return 1e9
        v = (d11*d20-d01*d21)/denom
        w = (d00*d21-d01*d20)/denom
        u = 1.0-v-w
        return u*p0[2] + v*p1[2] + w*p2[2]

    def is_occluded(px, py, edge_depth):
        """Check if a 2D point at given depth is hidden behind a triangle."""
        for (p0, p1, p2), min_d in proj_2d_tris:
            if min_d > edge_depth + 0.01:
                continue  # this tri is behind the edge
            if point_in_triangle_2d(px, py, p0, p1, p2):
                d = tri_depth_at(px, py, p0, p1, p2)
                if d < edge_depth - 0.05:  # tri is in front
                    return True
        return False

    # Classify each edge
    visible_edges = []
    hidden_edges = []
    for ia, ib in draw_edges:
        pa = project(verts_3d[ia])
        pb = project(verts_3d[ib])
        # Test 3 sample points along the edge
        samples = 3
        occluded_count = 0
        for s in range(samples):
            t = (s + 1) / (samples + 1)
            mx = pa[0] + t*(pb[0]-pa[0])
            my = pa[1] + t*(pb[1]-pa[1])
            md = pa[2] + t*(pb[2]-pa[2])
            if is_occluded(mx, my, md):
                occluded_count += 1
        if occluded_count > samples // 2:
            hidden_edges.append((pa, pb))
        else:
            visible_edges.append((pa, pb))

    # ── Draw ──
    fig, ax = plt.subplots(1, 1, figsize=(17, 11))
    ax.set_aspect("equal")
    ax.set_facecolor("white")

    # Hidden lines first (behind)
    for (pa, pb) in hidden_edges:
        ax.plot([pa[0], pb[0]], [pa[1], pb[1]],
                color=(0.7, 0.7, 0.7), linewidth=0.8,
                linestyle=(0, (4, 3)), zorder=1)

    # Visible lines on top
    for (pa, pb) in visible_edges:
        ax.plot([pa[0], pb[0]], [pa[1], pb[1]],
                color="black", linewidth=1.4, solid_capstyle="round", zorder=2)

    ax.set_title("Axonometric — Two-Bay Layout (30' + 10' @ 45\u00b0)\n"
                 'pen mode  |  solid = visible  |  dashed = hidden',
                 fontsize=12, fontweight="bold")
    ax.axis("off")

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("Axon pen drawing saved: {}".format(output_path))


def render_floor_plan(state, output_path):
    """Render a 2D floor plan PNG showing walls, doors, and windows.

    Iterates over all rectangular bays, handling rotation and origin.
    Scale: 1/8" = 1'-0". Drawn in feet, labeled in feet-inches.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import Arc
    import matplotlib.path as mpath

    fig, ax = plt.subplots(1, 1, figsize=(17, 11))
    ax.set_aspect("equal")
    ax.set_facecolor("white")

    all_world_pts = []  # for auto-fitting view limits

    # Line weights matching axon pen mode for Piaf tactile embosser
    WALL_LW = 1.4       # solid wall outlines (matches axon visible)
    DOOR_LW = 0.8       # dashed door openings (matches axon hidden)
    WINDOW_LW = 1.0     # window centerlines
    GRID_LW = 0.4       # light gridlines

    # Sort bays by z_order (draw lower z_order first = behind)
    sorted_bays = sorted(state.get("bays", {}).items(),
                         key=lambda kv: kv[1].get("z_order", 0))

    for bi, (bay_name, bay) in enumerate(sorted_bays):
        if bay.get("grid_type", "rectangular") != "rectangular":
            continue
        w = bay.get("walls", {})
        if not w.get("enabled"):
            continue

        ox, oy = bay["origin"]
        rot = bay.get("rotation_deg", 0)
        wall_t = w.get("thickness", 0.5)
        half_t = wall_t / 2.0
        aps = bay.get("apertures", [])

        cx, cy_arr = tp._get_spacing_arrays(bay)
        bay_wh = bay.get("wall_height", state.get("tactile3d", {}).get("wall_height", 30))

        def to_world(lx, ly, _ox=ox, _oy=oy, _rot=rot):
            return tp._local_to_world(lx, ly, (_ox, _oy), _rot)

        def draw_wall_rect(seg_start, seg_end, fixed, axis,
                           _half_t=half_t, _to_world=to_world):
            """Draw a rotated wall rectangle as black outline, white fill."""
            if axis == "x":
                c0 = _to_world(seg_start, fixed - _half_t)
                c1 = _to_world(seg_end,   fixed - _half_t)
                c2 = _to_world(seg_end,   fixed + _half_t)
                c3 = _to_world(seg_start, fixed + _half_t)
            else:
                c0 = _to_world(fixed - _half_t, seg_start)
                c1 = _to_world(fixed + _half_t, seg_start)
                c2 = _to_world(fixed + _half_t, seg_end)
                c3 = _to_world(fixed - _half_t, seg_end)
            poly = plt.Polygon([c0, c1, c2, c3],
                               facecolor="black", edgecolor="black",
                               linewidth=WALL_LW, zorder=2 + bi)
            ax.add_patch(poly)
            all_world_pts.extend([c0, c1, c2, c3])

        # Horizontal walls (x-axis gridlines)
        for j, y_val in enumerate(cy_arr):
            wall_aps = sorted(
                [a for a in aps if a.get("axis") == "x" and a.get("gridline") == j],
                key=lambda a: a.get("corner", 0))
            for seg_s, seg_e in tp._calc_wall_segments(cx[-1], wall_aps):
                if seg_e - seg_s > 0.001:
                    draw_wall_rect(seg_s, seg_e, y_val, "x")

        # Vertical walls (y-axis gridlines)
        for i, x_val in enumerate(cx):
            wall_aps = sorted(
                [a for a in aps if a.get("axis") == "y" and a.get("gridline") == i],
                key=lambda a: a.get("corner", 0))
            for seg_s, seg_e in tp._calc_wall_segments(cy_arr[-1], wall_aps):
                if seg_e - seg_s > 0.001:
                    draw_wall_rect(seg_s, seg_e, x_val, "y")

        # ── Aperture symbols (B&W pen mode) ──
        for ap in aps:
            ap_type = ap.get("type", "door")
            corner = ap.get("corner", 0)
            width = ap.get("width", 3)
            gridline = ap.get("gridline", 0)
            axis = ap.get("axis", "x")

            if axis == "x":
                fixed = cy_arr[gridline]
                p0 = to_world(corner, fixed)
                p1 = to_world(corner + width, fixed)
            else:
                fixed = cx[gridline]
                p0 = to_world(fixed, corner)
                p1 = to_world(fixed, corner + width)

            if ap_type == "door":
                # Dashed line across opening
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]],
                        color="black", linewidth=DOOR_LW,
                        linestyle=(0, (4, 3)),
                        solid_capstyle="round", zorder=4 + bi)
            elif ap_type == "window":
                # Thin solid line across opening (single centerline)
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]],
                        color="black", linewidth=WINDOW_LW,
                        solid_capstyle="round", zorder=4 + bi)

        # Bay label at center (light gray so it doesn't dominate on Piaf)
        center_local = (cx[-1] / 2, cy_arr[-1] / 2)
        center_w = to_world(*center_local)
        all_world_pts.append(center_w)
        ax.text(center_w[0], center_w[1],
                f"{bay_name}\n{int(bay_wh)}'",
                ha="center", va="center", fontsize=10, fontweight="bold",
                color=(0.6, 0.6, 0.6), zorder=1)

    # ── Auto-fit view limits ──
    if all_world_pts:
        xs = [p[0] for p in all_world_pts]
        ys = [p[1] for p in all_world_pts]
        pad = 8
        ax.set_xlim(min(xs) - pad, max(xs) + pad)
        ax.set_ylim(min(ys) - pad, max(ys) + pad)

    ax.set_title("Floor Plan — Two-Bay Layout\n"
                 'solid = walls  |  dashed = doors  |  thin = windows',
                 fontsize=12, fontweight="bold", pad=15)
    ax.axis("off")

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Floor plan saved: {output_path}")


def _archive_old_outputs():
    """Move any existing timestamped outputs into Tests/ subfolder."""
    archive_dir = os.path.join(OUTPUT_DIR, "Tests")
    os.makedirs(archive_dir, exist_ok=True)
    for fname in os.listdir(OUTPUT_DIR):
        if fname == "Tests" or fname == "single_bay_state.json":
            continue
        src = os.path.join(OUTPUT_DIR, fname)
        if os.path.isfile(src):
            dst = os.path.join(archive_dir, fname)
            os.rename(src, dst)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Archive previous outputs into Tests/
    _archive_old_outputs()

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

    # 5. Export OBJ for iPhone 3D inspection
    print(f"\nExporting OBJ to {OBJ_PATH}")
    export_obj(triangles_ft, OBJ_PATH)

    # 6. Render floor plan
    print(f"\nRendering floor plan to {FLOORPLAN_PATH}")
    render_floor_plan(state, FLOORPLAN_PATH)

    # 7. Render axonometric pen drawing
    print(f"\nRendering axon pen drawing to {AXON_PATH}")
    render_axon_pen(triangles_ft, AXON_PATH)

    # Summary
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"  STL file:       {STL_PATH}")
    print(f"  OBJ file:       {OBJ_PATH}")
    print(f"  Floor plan:     {FLOORPLAN_PATH}")
    print(f"  Axon pen:       {AXON_PATH}")
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
