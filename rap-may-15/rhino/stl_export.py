# -*- coding: utf-8 -*-
# RUNTIME: pure Python, no Rhino dependency. Imported by the controller for offline STL export.
"""
RADICAL ACCESSIBILITY CONTROLLER — STL Export Pipeline  v1.0
================================================
Pure-Python companion module that reads state.json, builds
watertight triangle meshes of the section plan, writes binary STL,
and optionally slices + sends to a Bambu Lab printer.

No Rhino dependency. No numpy. Just math and struct.

Mesh generation replicates the watcher's wall extrusion logic:
rectangular bays → wall segments (gaps at apertures) → extruded
boxes clipped at cut_height, plus an optional floor slab.

Usage from controller:
    import stl_export as tp
    tp.export_stl(state, "/path/to/output.stl")
    tp.preview(state)
    tp.send_to_bambu(state, "/path/to/sliced.3mf")

Standalone:
    python stl_export.py state.json [--output model.stl]
"""

import json
import math
import os
import struct
import subprocess
import sys
import time

# ══════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════

FT_TO_MM = 304.8           # 1 foot = 304.8 mm

# Build plate sizes (mm) for fit validation
BUILD_PLATES = {
    "x1c":      (256, 256, 256),
    "x1e":      (256, 256, 256),
    "p1s":      (256, 256, 256),
    "p1p":      (256, 256, 256),
    "a1":       (256, 256, 256),
    "a1_mini":  (180, 180, 180),
}

# Default slicer profile tuned for tactile models
TACTILE_SLICER_DEFAULTS = {
    "layer_height": 0.2,        # smooth finger feel
    "wall_loops": 4,            # structural integrity
    "infill_density": 100,      # solid for thin floor
    "support_enabled": False,   # walls are vertical
    "brim_type": "outer_only",  # adhesion for small footprint
}

# ══════════════════════════════════════════════════════════
# VECTOR MATH (pure Python, no numpy)
# ══════════════════════════════════════════════════════════

def _v3(x, y, z):
    return (x, y, z)

def _vsub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def _cross(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])

def _normalize(v):
    mag = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if mag < 1e-12:
        return (0, 0, 1)
    return (v[0]/mag, v[1]/mag, v[2]/mag)

def _tri_normal(p0, p1, p2):
    """Outward normal from triangle winding order (right-hand rule)."""
    return _normalize(_cross(_vsub(p1, p0), _vsub(p2, p0)))


# ══════════════════════════════════════════════════════════
# GEOMETRY — replicated from watcher, no Rhino calls
# ══════════════════════════════════════════════════════════

def _local_to_world(lx, ly, origin, rot_deg):
    """Transform local bay coords to world coords (2D + z=0)."""
    r = math.radians(rot_deg)
    wx = origin[0] + lx * math.cos(r) - ly * math.sin(r)
    wy = origin[1] + lx * math.sin(r) + ly * math.cos(r)
    return (wx, wy)

def _get_spacing_arrays(bay):
    """Cumulative gridline positions along x and y."""
    nx, ny = bay["bays"]
    sx_a = bay.get("spacing_x")
    sy_a = bay.get("spacing_y")
    if sx_a and len(sx_a) == nx:
        cx = [0.0]
        for s in sx_a:
            cx.append(cx[-1] + s)
    else:
        s = bay["spacing"][0]
        cx = [i * s for i in range(nx + 1)]
    if sy_a and len(sy_a) == ny:
        cy = [0.0]
        for s in sy_a:
            cy.append(cy[-1] + s)
    else:
        s = bay["spacing"][1]
        cy = [j * s for j in range(ny + 1)]
    return cx, cy

def _calc_wall_segments(wall_len, apertures):
    """Solid wall segments as (start, end), skipping aperture gaps."""
    if not apertures:
        return [(0.0, wall_len)]
    segs = []
    pos = 0.0
    for ap in apertures:
        cn = ap.get("corner", 0)
        wd = ap.get("width", 3)
        if cn > pos:
            segs.append((pos, cn))
        pos = cn + wd
    if pos < wall_len:
        segs.append((pos, wall_len))
    return segs


# ══════════════════════════════════════════════════════════
# MESH GENERATION — watertight boxes
# ══════════════════════════════════════════════════════════

def _box_triangles(p0, p1, p2, p3, z_bot, z_top):
    """Generate 12 triangles for a watertight extruded quad.

    p0..p3 are the four 2D corners (x,y) of the bottom face,
    wound counterclockwise when viewed from above.
    z_bot and z_top are the bottom and top z values.

    Returns list of (normal, v0, v1, v2) tuples.
    """
    # 8 vertices: 4 bottom + 4 top
    b = [_v3(p[0], p[1], z_bot) for p in [p0, p1, p2, p3]]
    t = [_v3(p[0], p[1], z_top) for p in [p0, p1, p2, p3]]

    tris = []

    # Bottom face (normal pointing down) — clockwise from above
    tris.append((_v3(0, 0, -1), b[0], b[3], b[2]))
    tris.append((_v3(0, 0, -1), b[0], b[2], b[1]))

    # Top face (normal pointing up) — counterclockwise from above
    tris.append((_v3(0, 0, 1), t[0], t[1], t[2]))
    tris.append((_v3(0, 0, 1), t[0], t[2], t[3]))

    # Four side faces — each side connects edge[i]→edge[i+1]
    for i in range(4):
        j = (i + 1) % 4
        # Two triangles for this side, normal pointing outward
        n = _tri_normal(b[i], b[j], t[j])
        tris.append((n, b[i], b[j], t[j]))
        tris.append((n, b[i], t[j], t[i]))

    return tris


def _wall_box_corners(seg_start, seg_end, fixed_val, axis, half_t,
                      ox, oy, rot):
    """Compute 4 bottom corners for one wall segment box.

    Returns (p0, p1, p2, p3) counterclockwise from above.
    Mirrors the watcher's _extrude_wall_box corner logic exactly.
    """
    if axis == "x":
        p0 = _local_to_world(seg_start, fixed_val - half_t, (ox, oy), rot)
        p1 = _local_to_world(seg_end,   fixed_val - half_t, (ox, oy), rot)
        p2 = _local_to_world(seg_end,   fixed_val + half_t, (ox, oy), rot)
        p3 = _local_to_world(seg_start, fixed_val + half_t, (ox, oy), rot)
    else:
        p0 = _local_to_world(fixed_val - half_t, seg_start, (ox, oy), rot)
        p1 = _local_to_world(fixed_val + half_t, seg_start, (ox, oy), rot)
        p2 = _local_to_world(fixed_val + half_t, seg_end,   (ox, oy), rot)
        p3 = _local_to_world(fixed_val - half_t, seg_end,   (ox, oy), rot)
    return p0, p1, p2, p3


def build_mesh(state):
    """Build the full triangle mesh from state.

    Returns a list of (normal, v0, v1, v2) tuples, where each
    vertex is (x, y, z) in FEET. Caller handles unit conversion.

    Generates the same geometry as the watcher's _draw_tactile3d:
    extruded wall segments clipped at cut_height, plus floor slab.
    """
    t3 = state.get("tactile3d", {})
    wall_height = t3.get("wall_height", 9.0)
    cut_height = t3.get("cut_height", 4.0)
    floor_thick = t3.get("floor_thickness", 0.5)
    floor_on = t3.get("floor_enabled", True)

    extrude_h = min(wall_height, cut_height)
    triangles = []

    # ── Wall segment boxes ──
    for name, bay in state.get("bays", {}).items():
        if bay.get("grid_type", "rectangular") != "rectangular":
            continue
        w = bay.get("walls", {})
        if not w.get("enabled"):
            continue
        t = w.get("thickness", 0.5)
        half_t = t / 2.0
        ox, oy = bay["origin"]
        rot = bay.get("rotation_deg", 0)
        cx, cy = _get_spacing_arrays(bay)
        aps = bay.get("apertures", [])

        # Horizontal gridlines (x-axis walls)
        for j, y_val in enumerate(cy):
            wall_aps = sorted(
                [a for a in aps if a.get("axis") == "x" and a.get("gridline") == j],
                key=lambda a: a.get("corner", 0))
            for seg_s, seg_e in _calc_wall_segments(cx[-1], wall_aps):
                if seg_e - seg_s < 0.001:
                    continue
                corners = _wall_box_corners(
                    seg_s, seg_e, y_val, "x", half_t, ox, oy, rot)
                triangles.extend(_box_triangles(
                    *corners, z_bot=0.0, z_top=extrude_h))

        # Vertical gridlines (y-axis walls)
        for i, x_val in enumerate(cx):
            wall_aps = sorted(
                [a for a in aps if a.get("axis") == "y" and a.get("gridline") == i],
                key=lambda a: a.get("corner", 0))
            for seg_s, seg_e in _calc_wall_segments(cy[-1], wall_aps):
                if seg_e - seg_s < 0.001:
                    continue
                corners = _wall_box_corners(
                    seg_s, seg_e, x_val, "y", half_t, ox, oy, rot)
                triangles.extend(_box_triangles(
                    *corners, z_bot=0.0, z_top=extrude_h))

    # ── Floor slab ──
    if floor_on:
        site = state.get("site", {})
        sox = site.get("origin", [0, 0])[0]
        soy = site.get("origin", [0, 0])[1]
        sw = site.get("width", 200)
        sh = site.get("height", 300)
        p0 = (sox,      soy)
        p1 = (sox + sw,  soy)
        p2 = (sox + sw,  soy + sh)
        p3 = (sox,       soy + sh)
        triangles.extend(_box_triangles(
            p0, p1, p2, p3, z_bot=-floor_thick, z_top=0.0))

    return triangles


# ══════════════════════════════════════════════════════════
# SECTION CUT — slice mesh with constant-axis plane
# ══════════════════════════════════════════════════════════

def _lerp_edge(v_in, v_out, d_in, d_out):
    """Linearly interpolate between two 3D points at the plane crossing.

    d_in and d_out are signed distances from the cutting plane.
    Returns the intersection point as (x, y, z).
    """
    t = d_in / (d_in - d_out)
    return (v_in[0] + t * (v_out[0] - v_in[0]),
            v_in[1] + t * (v_out[1] - v_in[1]),
            v_in[2] + t * (v_out[2] - v_in[2]))


def section_cut(triangles, axis, offset):
    """Slice a triangle mesh with a constant-X or constant-Y plane.

    Args:
        triangles: list of (normal, v0, v1, v2) from build_mesh()
        axis: "x" or "y" — the axis the plane is perpendicular to
        offset: the position along that axis where the plane sits

    Returns a list of 2D line segments [((u1,v1),(u2,v2)), ...]
    where u is the in-plane horizontal axis and v is the Z axis.
    For axis="x": u=Y, v=Z.  For axis="y": u=X, v=Z.
    """
    ax = 0 if axis.lower() == "x" else 1
    segments = []

    for _, v0, v1, v2 in triangles:
        verts = [v0, v1, v2]
        dists = [v[ax] - offset for v in verts]

        # Classify vertices as inside (>=0) or outside (<0)
        pos = [i for i in range(3) if dists[i] >= 0]
        neg = [i for i in range(3) if dists[i] < 0]

        # No intersection if all on one side
        if len(pos) == 0 or len(neg) == 0:
            # Check for exact plane-coincident edge (dist == 0)
            on_plane = [i for i in range(3) if abs(dists[i]) < 1e-9]
            if len(on_plane) == 2:
                i, j = on_plane
                vi, vj = verts[i], verts[j]
                # Project to 2D: (other_axis, z)
                other = 1 if ax == 0 else 0
                p1 = (vi[other], vi[2])
                p2 = (vj[other], vj[2])
                if abs(p1[0] - p2[0]) > 1e-9 or abs(p1[1] - p2[1]) > 1e-9:
                    segments.append((p1, p2))
            continue

        # Find the two intersection points
        cross_pts = []
        for p_idx in pos:
            for n_idx in neg:
                pt = _lerp_edge(verts[p_idx], verts[n_idx],
                                dists[p_idx], dists[n_idx])
                cross_pts.append(pt)

        if len(cross_pts) >= 2:
            other = 1 if ax == 0 else 0
            p1 = (cross_pts[0][other], cross_pts[0][2])
            p2 = (cross_pts[1][other], cross_pts[1][2])
            if abs(p1[0] - p2[0]) > 1e-9 or abs(p1[1] - p2[1]) > 1e-9:
                segments.append((p1, p2))

    return segments


def section_to_svg(segments, title="Section Cut", stroke_width=0.5):
    """Generate an SVG string from 2D section line segments.

    Uses scale(1,-1) to flip Y for architectural Z-up convention.
    """
    if not segments:
        return '<svg xmlns="http://www.w3.org/2000/svg"></svg>'

    # Compute bounds
    all_u = [p[0] for seg in segments for p in seg]
    all_v = [p[1] for seg in segments for p in seg]
    u_min, u_max = min(all_u), max(all_u)
    v_min, v_max = min(all_v), max(all_v)

    pad = max((u_max - u_min), (v_max - v_min)) * 0.05 + 1.0
    vb_x = u_min - pad
    vb_y = -(v_max + pad)  # flipped
    vb_w = (u_max - u_min) + 2 * pad
    vb_h = (v_max - v_min) + 2 * pad

    lines_svg = []
    for (u1, v1), (u2, v2) in segments:
        lines_svg.append(
            f'  <line x1="{u1:.4f}" y1="{-v1:.4f}" '
            f'x2="{u2:.4f}" y2="{-v2:.4f}" '
            f'stroke="black" stroke-width="{stroke_width}" '
            f'stroke-linecap="round"/>')

    title_esc = title.replace("&", "&amp;").replace("<", "&lt;")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{vb_x:.4f} {vb_y:.4f} {vb_w:.4f} {vb_h:.4f}" '
        f'width="{vb_w:.1f}" height="{vb_h:.1f}">\n'
        f'  <title>{title_esc}</title>\n'
        f'  <rect x="{vb_x:.4f}" y="{vb_y:.4f}" '
        f'width="{vb_w:.4f}" height="{vb_h:.4f}" fill="white"/>\n'
        + "\n".join(lines_svg) + "\n"
        f'</svg>')
    return svg


# ══════════════════════════════════════════════════════════
# STL EXPORT — binary format, no dependencies
# ══════════════════════════════════════════════════════════

def _scale_triangles(triangles, scale):
    """Scale all vertex coordinates by a uniform factor."""
    out = []
    for normal, v0, v1, v2 in triangles:
        out.append((
            normal,
            (v0[0]*scale, v0[1]*scale, v0[2]*scale),
            (v1[0]*scale, v1[1]*scale, v1[2]*scale),
            (v2[0]*scale, v2[1]*scale, v2[2]*scale),
        ))
    return out


def write_binary_stl(triangles, filepath):
    """Write a binary STL file.

    Binary STL format:
      80 bytes  header
       4 bytes  uint32 triangle count
      per triangle:
        12 bytes  normal  (3 × float32)
        12 bytes  vertex0 (3 × float32)
        12 bytes  vertex1 (3 × float32)
        12 bytes  vertex2 (3 × float32)
         2 bytes  attribute count (0)
    """
    folder = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(folder, exist_ok=True)

    with open(filepath, "wb") as f:
        # Header
        header = b"Radical Accessibility Controller tactile model" + b"\0" * 34
        f.write(header[:80])
        # Triangle count
        f.write(struct.pack("<I", len(triangles)))
        # Triangles
        for normal, v0, v1, v2 in triangles:
            f.write(struct.pack("<fff", *normal))
            f.write(struct.pack("<fff", *v0))
            f.write(struct.pack("<fff", *v1))
            f.write(struct.pack("<fff", *v2))
            f.write(struct.pack("<H", 0))  # attribute byte count

    return len(triangles)


# ══════════════════════════════════════════════════════════
# PREVIEW — dimensions, fit check, triangle count
# ══════════════════════════════════════════════════════════

def _mesh_bounds(triangles):
    """Axis-aligned bounding box of a triangle list."""
    xs, ys, zs = [], [], []
    for _, v0, v1, v2 in triangles:
        for v in (v0, v1, v2):
            xs.append(v[0]); ys.append(v[1]); zs.append(v[2])
    if not xs:
        return (0, 0, 0), (0, 0, 0)
    return ((min(xs), min(ys), min(zs)),
            (max(xs), max(ys), max(zs)))


def preview(state):
    """Return a multiline preview string with model dimensions and fit check.

    Does a full mesh build to get exact bounds and triangle count.
    """
    triangles_ft = build_mesh(state)
    if not triangles_ft:
        return "No mesh geometry. Enable walls on at least one rectangular bay."

    t3 = state.get("tactile3d", {})
    rep_scale = t3.get("print_scale", 200)
    plate = BUILD_PLATES["p1s"]

    # Convert feet → mm at representation scale
    ft_to_print_mm = FT_TO_MM / rep_scale
    triangles_mm = _scale_triangles(triangles_ft, ft_to_print_mm)
    bmin, bmax = _mesh_bounds(triangles_mm)

    size_x = bmax[0] - bmin[0]
    size_y = bmax[1] - bmin[1]
    size_z = bmax[2] - bmin[2]

    # Fit check
    fits_x = size_x <= plate[0]
    fits_y = size_y <= plate[1]
    fits_z = size_z <= plate[2]
    fits = fits_x and fits_y and fits_z

    lines = [
        f"Triangles: {len(triangles_ft)}",
        f"Scale: 1:{rep_scale}",
        f"Print size: {size_x:.1f} x {size_y:.1f} x {size_z:.1f} mm",
        f"Printer: {printer.upper()} (plate {plate[0]}x{plate[1]}x{plate[2]} mm)",
    ]
    if fits:
        lines.append("OK: Model fits on build plate.")
    else:
        over = []
        if not fits_x: over.append(f"X by {size_x - plate[0]:.1f} mm")
        if not fits_y: over.append(f"Y by {size_y - plate[1]:.1f} mm")
        if not fits_z: over.append(f"Z by {size_z - plate[2]:.1f} mm")
        lines.append(f"WARNING: Exceeds plate — {', '.join(over)}.")
        auto = _auto_scale(triangles_ft, plate)
        lines.append(f"  Suggested scale: 1:{auto} to fit.")

    # Model feet dimensions
    bmin_ft, bmax_ft = _mesh_bounds(triangles_ft)
    lines.append(f"Model extents (ft): "
                 f"{bmax_ft[0]-bmin_ft[0]:.1f} x "
                 f"{bmax_ft[1]-bmin_ft[1]:.1f} x "
                 f"{bmax_ft[2]-bmin_ft[2]:.1f}")
    lines.append(f"Wall height: {t3.get('wall_height',9.0)} ft, "
                 f"cut: {t3.get('cut_height',4.0)} ft, "
                 f"floor: {'ON' if t3.get('floor_enabled') else 'OFF'} "
                 f"({t3.get('floor_thickness',0.5)} ft)")
    return "\n".join(lines)


def _auto_scale(triangles_ft, plate):
    """Compute the smallest integer 1:N scale that fits the plate."""
    bmin, bmax = _mesh_bounds(triangles_ft)
    dx = bmax[0] - bmin[0]
    dy = bmax[1] - bmin[1]
    dz = bmax[2] - bmin[2]
    if dx < 1e-6 and dy < 1e-6:
        return 200
    # Required scale = model_ft * FT_TO_MM / plate_mm
    scales = []
    if dx > 0: scales.append(dx * FT_TO_MM / plate[0])
    if dy > 0: scales.append(dy * FT_TO_MM / plate[1])
    if dz > 0: scales.append(dz * FT_TO_MM / plate[2])
    raw = max(scales) if scales else 200
    # Round up to nearest 10
    return int(math.ceil(raw / 10.0)) * 10


# ══════════════════════════════════════════════════════════
# EXPORT — full pipeline: mesh → STL → optional re-center
# ══════════════════════════════════════════════════════════

def export_stl(state, filepath):
    """Build mesh, scale to mm, center on origin, write binary STL.

    Returns the triangle count on success.
    """
    triangles_ft = build_mesh(state)
    if not triangles_ft:
        raise RuntimeError("No mesh geometry. Enable walls on at least "
                           "one rectangular bay and ensure tactile3d "
                           "settings are configured.")

    cfg = state.get("bambu", {})
    rep_scale = cfg.get("print_scale", 200)
    ft_to_mm = FT_TO_MM / rep_scale

    triangles_mm = _scale_triangles(triangles_ft, ft_to_mm)

    # Re-center on XY origin (move bounding box center to 0,0)
    bmin, bmax = _mesh_bounds(triangles_mm)
    cx = (bmin[0] + bmax[0]) / 2.0
    cy = (bmin[1] + bmax[1]) / 2.0
    # Keep Z as-is (floor at bottom)
    centered = []
    for normal, v0, v1, v2 in triangles_mm:
        centered.append((
            normal,
            (v0[0]-cx, v0[1]-cy, v0[2]),
            (v1[0]-cx, v1[1]-cy, v1[2]),
            (v2[0]-cx, v2[1]-cy, v2[2]),
        ))

    count = write_binary_stl(centered, filepath)
    return count


# ══════════════════════════════════════════════════════════
# HIGH-LEVEL OPERATION (called by controller)
# ══════════════════════════════════════════════════════════

def do_export(state, filepath=None):
    """CLI wrapper: export STL to filepath (defaults to ./tactile_model.stl)."""
    out = filepath or "./tactile_model.stl"
    tri_count = export_stl(state, out)
    return "OK: STL written to {0} ({1} triangles)".format(out, tri_count)


# ══════════════════════════════════════════════════════════
# STANDALONE ENTRY POINT
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        description="Radical Accessibility Controller — STL Export Pipeline")
    ap.add_argument("state_file", help="Path to state_v2.json")
    ap.add_argument("--output", "-o", default="./tactile_model.stl",
                    help="Output STL path")
    ap.add_argument("--scale", "-s", type=int, default=200,
                    help="Representation scale (1:N, default 200)")
    ap.add_argument("--preview", action="store_true",
                    help="Show dimensions without exporting")
    args = ap.parse_args()

    with open(args.state_file, "r", encoding="utf-8") as f:
        state = json.load(f)

    # Inject scale into bambu config for this run
    if "bambu" not in state:
        state["bambu"] = {}
    state["bambu"]["print_scale"] = args.scale

    if args.preview:
        print(preview(state))
    else:
        msg = do_export(state, args.output)
        print(msg)
