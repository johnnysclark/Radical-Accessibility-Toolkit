# -*- coding: utf-8 -*-
"""
PLAN LAYOUT JIG — Tactile Print Pipeline  v1.0
================================================
Pure-Python companion module that reads state.json, builds
watertight triangle meshes of the section plan, writes binary STL,
and optionally slices + sends to a Bambu Lab printer.

No Rhino dependency. No numpy. Just math and struct.

Mesh generation replicates the watcher's wall extrusion logic:
rectangular bays → wall segments (gaps at apertures) → extruded
boxes clipped at cut_height, plus an optional floor slab.

Usage from controller:
    import tactile_print as tp
    tp.export_stl(state, "/path/to/output.stl")
    tp.preview(state)
    tp.send_to_bambu(state, "/path/to/sliced.3mf")

Standalone:
    python tactile_print.py state.json [--output model.stl]
"""

import ftplib
import json
import math
import os
import ssl
import struct
import subprocess
import sys
import time

# ══════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════

FT_TO_MM = 304.8           # 1 foot = 304.8 mm
BAMBU_FTP_PORT = 990       # FTPS implicit TLS
BAMBU_MQTT_PORT = 8883     # MQTT over TLS
BAMBU_USER = "bblp"        # fixed Bambu username

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

def _world_to_local(wx, wy, origin, rot_deg):
    """Inverse of _local_to_world: world coords → local bay coords."""
    r = math.radians(rot_deg)
    dx = wx - origin[0]
    dy = wy - origin[1]
    lx = dx * math.cos(r) + dy * math.sin(r)
    ly = -dx * math.sin(r) + dy * math.cos(r)
    return (lx, ly)

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


def _aperture_infill(ap, extrude_h, fixed_val, axis, half_t,
                     ox, oy, rot):
    """Generate header and sill boxes for a partial-height aperture.

    Doors:   opening from z=0 to z=height → header from height to extrude_h.
    Windows: opening from z=sill to z=sill+height →
             sill box from 0 to sill, header from sill+height to extrude_h.

    The infill boxes are inset by EPS along the wall length so they
    don't share exact edges with adjacent full-height wall segments.
    This keeps the combined mesh manifold and watertight.

    Returns a list of (normal, v0, v1, v2) triangles.
    """
    EPS = 0.001  # tiny inset to avoid shared edges (< 0.3 mm)
    triangles = []
    ap_corner = ap.get("corner", 0)
    ap_width = ap.get("width", 3)
    ap_height = ap.get("height", 7)
    ap_type = ap.get("type", "door")
    sill_h = ap.get("sill", 0.0)

    # For doors, opening runs from z=0 to z=ap_height
    # For windows, opening runs from z=sill_h to z=sill_h+ap_height
    if ap_type == "door":
        opening_top = ap_height
        opening_bot = 0.0
    else:
        opening_bot = sill_h
        opening_top = sill_h + ap_height

    # Inset the box slightly so it doesn't share edges with adjacent walls
    corners = _wall_box_corners(
        ap_corner + EPS, ap_corner + ap_width - EPS,
        fixed_val, axis, half_t, ox, oy, rot)

    # Header: wall above the opening
    if opening_top < extrude_h - 0.001:
        triangles.extend(_box_triangles(
            *corners, z_bot=opening_top, z_top=extrude_h))

    # Sill: wall below the opening (windows with sill > 0)
    if opening_bot > 0.001:
        triangles.extend(_box_triangles(
            *corners, z_bot=0.0, z_top=opening_bot))

    return triangles


def build_mesh(state):
    """Build the full triangle mesh from state.

    Returns a list of (normal, v0, v1, v2) tuples, where each
    vertex is (x, y, z) in FEET. Caller handles unit conversion.

    Generates the same geometry as the watcher's _draw_tactile3d:
    extruded wall segments clipped at cut_height, plus floor slab.

    Apertures produce partial-height openings:
      - Doors: full-height gap from 0 to door height, header above.
      - Windows: sill below, opening, header above.
    """
    t3 = state.get("tactile3d", {})
    wall_height = t3.get("wall_height", 9.0)
    cut_height = t3.get("cut_height", 4.0)
    floor_thick = t3.get("floor_thickness", 0.5)
    floor_on = t3.get("floor_enabled", True)

    extrude_h = min(wall_height, cut_height)
    triangles = []

    # ── Collect bay footprints for z_order clipping ──
    # Higher z_order bays take precedence: lower-z_order bay walls
    # that fall inside a higher-z_order bay's footprint are skipped.
    bay_footprints = []  # (z_order, origin, rot, total_x, total_y)
    for name, bay in state.get("bays", {}).items():
        if bay.get("grid_type", "rectangular") != "rectangular":
            continue
        w = bay.get("walls", {})
        if not w.get("enabled"):
            continue
        cx_fp, cy_fp = _get_spacing_arrays(bay)
        bay_footprints.append((
            bay.get("z_order", 0),
            bay["origin"],
            bay.get("rotation_deg", 0),
            cx_fp[-1],
            cy_fp[-1],
        ))

    def _is_clipped_by_higher(wx, wy, my_z_order):
        """Check if a world point is inside any higher-z_order bay."""
        for z_ord, fp_origin, fp_rot, fp_total_x, fp_total_y in bay_footprints:
            if z_ord <= my_z_order:
                continue  # same or lower priority — no clipping
            lx, ly = _world_to_local(wx, wy, fp_origin, fp_rot)
            if 0 < lx < fp_total_x and 0 < ly < fp_total_y:
                return True
        return False

    # ── Wall segment boxes ──
    for name, bay in state.get("bays", {}).items():
        if bay.get("grid_type", "rectangular") != "rectangular":
            continue
        w = bay.get("walls", {})
        if not w.get("enabled"):
            continue
        # Per-bay wall_height override (falls back to global)
        bay_wh = bay.get("wall_height", wall_height)
        bay_extrude_h = min(bay_wh, cut_height)
        t = w.get("thickness", 0.5)
        half_t = t / 2.0
        ox, oy = bay["origin"]
        rot = bay.get("rotation_deg", 0)
        my_z_order = bay.get("z_order", 0)
        cx, cy = _get_spacing_arrays(bay)
        aps = bay.get("apertures", [])

        # Horizontal gridlines (x-axis walls)
        for j, y_val in enumerate(cy):
            wall_aps = sorted(
                [a for a in aps if a.get("axis") == "x" and a.get("gridline") == j],
                key=lambda a: a.get("corner", 0))
            # Solid wall segments (full height)
            for seg_s, seg_e in _calc_wall_segments(cx[-1], wall_aps):
                if seg_e - seg_s < 0.001:
                    continue
                # Test 3 points along segment for robust boundary clipping
                clipped = False
                for frac in (0.25, 0.5, 0.75):
                    tw = _local_to_world(
                        seg_s + frac * (seg_e - seg_s), y_val,
                        (ox, oy), rot)
                    if _is_clipped_by_higher(tw[0], tw[1], my_z_order):
                        clipped = True
                        break
                if clipped:
                    continue
                corners = _wall_box_corners(
                    seg_s, seg_e, y_val, "x", half_t, ox, oy, rot)
                triangles.extend(_box_triangles(
                    *corners, z_bot=0.0, z_top=bay_extrude_h))
            # Aperture infill (headers + sills)
            for ap in wall_aps:
                ap_mid = ap.get("corner", 0) + ap.get("width", 3) / 2
                mid_w = _local_to_world(ap_mid, y_val, (ox, oy), rot)
                if _is_clipped_by_higher(mid_w[0], mid_w[1], my_z_order):
                    continue
                triangles.extend(_aperture_infill(
                    ap, bay_extrude_h, y_val, "x", half_t, ox, oy, rot))

        # Vertical gridlines (y-axis walls)
        for i, x_val in enumerate(cx):
            wall_aps = sorted(
                [a for a in aps if a.get("axis") == "y" and a.get("gridline") == i],
                key=lambda a: a.get("corner", 0))
            # Solid wall segments (full height)
            for seg_s, seg_e in _calc_wall_segments(cy[-1], wall_aps):
                if seg_e - seg_s < 0.001:
                    continue
                # Test 3 points along segment for robust boundary clipping
                clipped = False
                for frac in (0.25, 0.5, 0.75):
                    tw = _local_to_world(
                        x_val, seg_s + frac * (seg_e - seg_s),
                        (ox, oy), rot)
                    if _is_clipped_by_higher(tw[0], tw[1], my_z_order):
                        clipped = True
                        break
                if clipped:
                    continue
                corners = _wall_box_corners(
                    seg_s, seg_e, x_val, "y", half_t, ox, oy, rot)
                triangles.extend(_box_triangles(
                    *corners, z_bot=0.0, z_top=bay_extrude_h))
            # Aperture infill (headers + sills)
            for ap in wall_aps:
                ap_mid = ap.get("corner", 0) + ap.get("width", 3) / 2
                mid_w = _local_to_world(x_val, ap_mid, (ox, oy), rot)
                if _is_clipped_by_higher(mid_w[0], mid_w[1], my_z_order):
                    continue
                triangles.extend(_aperture_infill(
                    ap, bay_extrude_h, x_val, "y", half_t, ox, oy, rot))

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
        header = b"Plan Layout Jig tactile model" + b"\0" * 51
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


def preview(state, bambu_cfg=None):
    """Return a multiline preview string with model dimensions and fit check.

    Does a full mesh build to get exact bounds and triangle count.
    """
    triangles_ft = build_mesh(state)
    if not triangles_ft:
        return "No mesh geometry. Enable walls on at least one rectangular bay."

    t3 = state.get("tactile3d", {})
    cfg = bambu_cfg or state.get("bambu", {})
    rep_scale = cfg.get("print_scale", 200)  # 1:N
    printer = cfg.get("printer_model", "p1s").lower()
    plate = BUILD_PLATES.get(printer, BUILD_PLATES["p1s"])

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

def export_stl(state, filepath, bambu_cfg=None):
    """Build mesh, scale to mm, center on origin, write binary STL.

    Returns (filepath, triangle_count, size_mm_tuple) on success.
    """
    triangles_ft = build_mesh(state)
    if not triangles_ft:
        raise RuntimeError("No mesh geometry. Enable walls on at least "
                           "one rectangular bay and ensure tactile3d "
                           "settings are configured.")

    cfg = bambu_cfg or state.get("bambu", {})
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
    size_mm = (bmax[0]-bmin[0], bmax[1]-bmin[1], bmax[2]-bmin[2])
    return filepath, count, size_mm


# ══════════════════════════════════════════════════════════
# ORCASLICER — slice STL → 3MF
# ══════════════════════════════════════════════════════════

def slice_model(stl_path, slicer_path, output_3mf=None, profile_overrides=None):
    """Slice an STL file to 3MF using OrcaSlicer CLI.

    Args:
        stl_path: Path to the input STL file.
        slicer_path: Path to the OrcaSlicer executable.
        output_3mf: Output path. Defaults to same name with .3mf extension.
        profile_overrides: Dict of slicer settings to override.

    Returns the output 3MF path on success.
    Raises RuntimeError on failure.
    """
    if not os.path.isfile(stl_path):
        raise RuntimeError(f"STL not found: {stl_path}")
    if not os.path.isfile(slicer_path):
        raise RuntimeError(
            f"OrcaSlicer not found: {slicer_path}\n"
            "  Download from: https://github.com/SoftFever/OrcaSlicer/releases\n"
            "  Then: bambu config slicer_path <path_to_orca_slicer>")

    if output_3mf is None:
        output_3mf = os.path.splitext(stl_path)[0] + ".3mf"

    # Build slicer CLI arguments
    settings = dict(TACTILE_SLICER_DEFAULTS)
    if profile_overrides:
        settings.update(profile_overrides)

    cmd = [slicer_path, "--slice", "0"]
    for key, val in settings.items():
        if isinstance(val, bool):
            cmd.extend([f"--{key}", "1" if val else "0"])
        else:
            cmd.extend([f"--{key}", str(val)])
    cmd.extend(["--output", output_3mf, stl_path])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(
                f"OrcaSlicer failed (exit {result.returncode}):\n"
                f"  {result.stderr.strip()}")
        if not os.path.isfile(output_3mf):
            raise RuntimeError(
                f"OrcaSlicer ran but output not found: {output_3mf}\n"
                f"  stdout: {result.stdout.strip()}")
    except FileNotFoundError:
        raise RuntimeError(f"OrcaSlicer executable not found: {slicer_path}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("OrcaSlicer timed out after 120 seconds.")

    return output_3mf


# ══════════════════════════════════════════════════════════
# BAMBU PRINTER — FTP upload + MQTT print trigger
# ══════════════════════════════════════════════════════════

def _bambu_ftp_upload(filepath, printer_ip, access_code, remote_name=None):
    """Upload a file to the Bambu printer's SD card via FTPS (port 990).

    Bambu printers run an implicit-TLS FTP server:
      Port: 990
      User: bblp
      Pass: access code from printer LCD → Network → Access Code
      Path: / (root of SD card)
    """
    if remote_name is None:
        remote_name = os.path.basename(filepath)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # printer uses self-signed cert

    try:
        ftp = ftplib.FTP_TLS(context=context)
        ftp.connect(printer_ip, BAMBU_FTP_PORT, timeout=15)
        ftp.login(BAMBU_USER, access_code)
        ftp.prot_p()  # switch data connection to TLS

        with open(filepath, "rb") as f:
            ftp.storbinary(f"STOR {remote_name}", f)

        ftp.quit()
        return remote_name
    except ftplib.all_errors as e:
        raise RuntimeError(
            f"FTP upload failed: {e}\n"
            f"  Verify: printer IP ({printer_ip}), access code, "
            f"printer powered on and on same network.")


def _bambu_mqtt_print(printer_ip, access_code, serial_number,
                      remote_filename, subtask_name="tactile_model"):
    """Send a print command to the Bambu printer via MQTT.

    Requires paho-mqtt. If not installed, provides clear instructions.

    MQTT protocol:
      Broker: printer IP, port 8883 (TLS)
      User: bblp / access_code
      Topic: device/{serial}/request
      Payload: JSON print command
    """
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        raise RuntimeError(
            "paho-mqtt not installed. Install with:\n"
            "  pip install paho-mqtt\n"
            "Or upload the 3MF file to the printer manually via SD card.")

    publish_topic = f"device/{serial_number}/request"
    payload = json.dumps({
        "print": {
            "command": "project_file",
            "param": "Metadata/plate_1.gcode",
            "subtask_name": subtask_name,
            "file": f"/sdcard/{remote_filename}",
            "bed_type": "auto",
            "timelapse": False,
            "use_ams": False,
        }
    })

    connected = [False]
    published = [False]
    error_msg = [None]

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            connected[0] = True
        else:
            error_msg[0] = f"MQTT connect failed with code {rc}"

    def on_publish(client, userdata, mid, reason_code=None, properties=None):
        published[0] = True

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        # Support both paho-mqtt v1 and v2
        try:
            client = mqtt.Client(
                client_id="plj_tactile",
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        except (AttributeError, TypeError):
            client = mqtt.Client(client_id="plj_tactile")

        client.on_connect = on_connect
        client.on_publish = on_publish
        client.tls_set_context(context)
        client.username_pw_set(BAMBU_USER, access_code)
        client.connect(printer_ip, BAMBU_MQTT_PORT, keepalive=10)
        client.loop_start()

        # Wait for connection
        deadline = time.time() + 10
        while not connected[0] and not error_msg[0] and time.time() < deadline:
            time.sleep(0.1)
        if error_msg[0]:
            raise RuntimeError(error_msg[0])
        if not connected[0]:
            raise RuntimeError("MQTT connection timed out.")

        # Publish print command
        result = client.publish(publish_topic, payload)
        deadline = time.time() + 5
        while not published[0] and time.time() < deadline:
            time.sleep(0.1)

        client.loop_stop()
        client.disconnect()

        if not published[0]:
            raise RuntimeError("MQTT publish timed out.")

    except (ConnectionRefusedError, OSError) as e:
        raise RuntimeError(
            f"MQTT connection failed: {e}\n"
            f"  Verify: printer IP ({printer_ip}), access code, "
            f"serial ({serial_number}), printer on same network.")


def _bambu_mqtt_status(printer_ip, access_code, serial_number, timeout=8):
    """Poll the Bambu printer for current status via MQTT.

    Returns a dict with status fields, or raises RuntimeError.
    """
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        raise RuntimeError("paho-mqtt not installed. pip install paho-mqtt")

    report_topic = f"device/{serial_number}/report"
    status = {"raw": None}

    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            client.subscribe(report_topic)

    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            status["raw"] = data
        except Exception:
            pass

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        try:
            client = mqtt.Client(
                client_id="plj_status",
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        except (AttributeError, TypeError):
            client = mqtt.Client(client_id="plj_status")

        client.on_connect = on_connect
        client.on_message = on_message
        client.tls_set_context(context)
        client.username_pw_set(BAMBU_USER, access_code)
        client.connect(printer_ip, BAMBU_MQTT_PORT, keepalive=10)
        client.loop_start()

        deadline = time.time() + timeout
        while status["raw"] is None and time.time() < deadline:
            time.sleep(0.2)

        client.loop_stop()
        client.disconnect()

    except (ConnectionRefusedError, OSError) as e:
        raise RuntimeError(f"MQTT status failed: {e}")

    raw = status["raw"]
    if raw is None:
        raise RuntimeError("No status received within timeout.")

    # Parse Bambu status report
    p = raw.get("print", {})
    result = {
        "state": p.get("gcode_state", "UNKNOWN"),
        "progress": p.get("mc_percent", 0),
        "layer": p.get("layer_num", 0),
        "total_layers": p.get("total_layer_num", 0),
        "remaining_min": p.get("mc_remaining_time", 0),
        "subtask_name": p.get("subtask_name", ""),
        "bed_temp": p.get("bed_temper", 0),
        "nozzle_temp": p.get("nozzle_temper", 0),
        "fan_speed": p.get("big_fan1_speed", "0"),
    }
    return result


def format_status(status_dict):
    """Format a printer status dict as a readable string."""
    s = status_dict
    state_map = {
        "IDLE": "Idle",
        "RUNNING": "Printing",
        "PAUSE": "Paused",
        "FINISH": "Finished",
        "FAILED": "Failed",
        "PREPARE": "Preparing",
    }
    state = state_map.get(s["state"], s["state"])
    lines = [f"Printer: {state}"]

    if s["state"] == "RUNNING":
        pct = s["progress"]
        layer = s["layer"]
        total = s["total_layers"]
        remain = s["remaining_min"]
        h = remain // 60
        m = remain % 60
        lines.append(f"Progress: {pct}%  (layer {layer}/{total})")
        if h > 0:
            lines.append(f"Remaining: {h}h {m}m")
        else:
            lines.append(f"Remaining: {m}m")

    if s.get("subtask_name"):
        lines.append(f"Job: {s['subtask_name']}")

    lines.append(f"Bed: {s['bed_temp']}\u00b0C  Nozzle: {s['nozzle_temp']}\u00b0C")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
# HIGH-LEVEL OPERATIONS (called by controller)
# ══════════════════════════════════════════════════════════

def do_export(state, filepath=None):
    """Export the tactile model as a scaled, centered binary STL.

    Returns a status message string.
    """
    cfg = state.get("bambu", {})
    if filepath is None:
        filepath = cfg.get("stl_path", "./tactile_model.stl")

    path, count, size = export_stl(state, filepath)
    fsize = os.path.getsize(path)
    return (f"OK: Exported {count} triangles to {path}\n"
            f"  Size: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm  "
            f"({fsize:,} bytes)")


def do_slice(state):
    """Export STL and slice to 3MF. Returns status message."""
    cfg = state.get("bambu", {})
    stl = cfg.get("stl_path", "./tactile_model.stl")
    slicer = cfg.get("slicer_path", "")
    if not slicer:
        raise RuntimeError(
            "Slicer path not set. Configure with:\n"
            "  bambu config slicer_path <path_to_orca_slicer>")

    # Export STL first
    path, count, size = export_stl(state, stl)

    # Slice
    output_3mf = os.path.splitext(stl)[0] + ".3mf"
    result = slice_model(stl, slicer, output_3mf)
    fsize = os.path.getsize(result)
    return (f"OK: Sliced {count} triangles.\n"
            f"  STL: {stl}\n"
            f"  3MF: {result} ({fsize:,} bytes)")


def do_send(state, filepath=None):
    """Upload a 3MF file to the Bambu printer and start printing.

    Returns status message.
    """
    cfg = state.get("bambu", {})
    ip = cfg.get("printer_ip", "")
    code = cfg.get("access_code", "")
    serial = cfg.get("serial_number", "")

    if not ip:
        raise RuntimeError("Printer IP not set. bambu config ip <address>")
    if not code:
        raise RuntimeError("Access code not set. bambu config access_code <code>")
    if not serial:
        raise RuntimeError("Serial number not set. bambu config serial <number>")

    if filepath is None:
        stl = cfg.get("stl_path", "./tactile_model.stl")
        filepath = os.path.splitext(stl)[0] + ".3mf"

    if not os.path.isfile(filepath):
        raise RuntimeError(
            f"File not found: {filepath}\n"
            "  Run 'bambu slice' first to generate the 3MF file.")

    remote = os.path.basename(filepath)
    lines = [f"Uploading {remote} to {ip}..."]
    _bambu_ftp_upload(filepath, ip, code, remote)
    lines.append(f"OK: Uploaded to printer SD card.")

    lines.append("Sending print command...")
    _bambu_mqtt_print(ip, code, serial, remote)
    lines.append("OK: Print started.")

    return "\n".join(lines)


def do_print(state):
    """Full pipeline: export → slice → upload → print.

    Returns combined status message.
    """
    msgs = []

    # 1. Export STL
    cfg = state.get("bambu", {})
    stl = cfg.get("stl_path", "./tactile_model.stl")
    path, count, size = export_stl(state, stl)
    msgs.append(f"Exported {count} triangles "
                f"({size[0]:.1f}x{size[1]:.1f}x{size[2]:.1f} mm)")

    # 2. Slice
    slicer = cfg.get("slicer_path", "")
    if not slicer:
        raise RuntimeError(
            "Slicer path not set. Configure with:\n"
            "  bambu config slicer_path <path_to_orca_slicer>")
    output_3mf = os.path.splitext(stl)[0] + ".3mf"
    slice_model(stl, slicer, output_3mf)
    msgs.append(f"Sliced to {output_3mf}")

    # 3. Upload + print
    ip = cfg.get("printer_ip", "")
    code = cfg.get("access_code", "")
    serial = cfg.get("serial_number", "")
    if not all([ip, code, serial]):
        msgs.append(f"3MF ready at {output_3mf}.")
        msgs.append("Printer not fully configured — upload manually or set:")
        if not ip: msgs.append("  bambu config ip <address>")
        if not code: msgs.append("  bambu config access_code <code>")
        if not serial: msgs.append("  bambu config serial <number>")
        return "\n".join(msgs)

    remote = os.path.basename(output_3mf)
    _bambu_ftp_upload(output_3mf, ip, code, remote)
    msgs.append(f"Uploaded {remote} to printer.")
    _bambu_mqtt_print(ip, code, serial, remote)
    msgs.append("OK: Print started on " + ip)

    return "\n".join(msgs)


def do_status(state):
    """Poll the printer for current status. Returns formatted string."""
    cfg = state.get("bambu", {})
    ip = cfg.get("printer_ip", "")
    code = cfg.get("access_code", "")
    serial = cfg.get("serial_number", "")
    if not all([ip, code, serial]):
        raise RuntimeError(
            "Printer not configured. Set ip, access_code, and serial first.")
    status = _bambu_mqtt_status(ip, code, serial)
    return format_status(status)


# ══════════════════════════════════════════════════════════
# STANDALONE ENTRY POINT
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        description="Plan Layout Jig — Tactile Print Pipeline")
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
