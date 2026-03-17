#!/usr/bin/env python3
"""Render a Cabinet 45 plan oblique of the Sonsbeek Pavilion as SVG.
Pure Python — no Rhino needed. Run from command line to generate SVG."""

import math

# ================================================================
# OBLIQUE PROJECTION SETTINGS — Cabinet 45, rotation 30
# ================================================================
ANGLE = 45.0       # receding axis angle
DEPTH = 0.5        # cabinet = half depth
ROTATION = 30.0    # degrees
CUT_ON = True
CUT_H = 2.5        # Z cut height (meters) — slices through walls below roof

# ================================================================
# GEOMETRY — Sonsbeek Pavilion (simplified boxes)
# ================================================================
# Each entry: (x, y, z, w, d, h, category, label)
# category: "arch", "ground", "foliage"

BOXES = [
    # Ground
    (-1, -1, -0.05, 16, 12, 0.05, "ground", "gravel pad"),
    (5, -4, -0.03, 2.5, 3, 0.03, "ground", "path"),

    # Walls (freestanding, De Stijl) — thickness exaggerated for rendering
    (0, 0, 0, 10, 0.3, 2.8, "arch", "Wall A south"),
    (2, 8, 0, 12, 0.3, 3.2, "arch", "Wall B north"),
    (4, 4, 0, 7, 0.3, 2.5, "arch", "Wall C interior"),
    (0, 0, 0, 0.3, 5, 3.0, "arch", "Wall D west"),
    (12, 3, 0, 0.3, 6, 2.8, "arch", "Wall E east"),
    (6, 2, 0, 0.3, 3, 2.2, "arch", "Wall F divider"),
    (8, 5, 0, 0.3, 4, 3.0, "arch", "Wall G screen"),

    # Roof planes
    (1, 0.5, 3.2, 10, 8, 0.1, "arch", "Main roof"),
    (7, 3, 3.0, 6, 6, 0.08, "arch", "Secondary roof"),

    # Columns
    (1.5, 1, 0, 0.08, 0.08, 3.2, "arch", "col"),
    (1.5, 7, 0, 0.08, 0.08, 3.2, "arch", "col"),
    (5, 1, 0, 0.08, 0.08, 3.2, "arch", "col"),
    (5, 7, 0, 0.08, 0.08, 3.2, "arch", "col"),
    (10, 1, 0, 0.08, 0.08, 3.2, "arch", "col"),
    (10, 7, 0, 0.08, 0.08, 3.2, "arch", "col"),
    (8, 4, 0, 0.08, 0.08, 3.0, "arch", "col"),
    (8, 8, 0, 0.08, 0.08, 3.0, "arch", "col"),
    (12, 4, 0, 0.08, 0.08, 3.0, "arch", "col"),
    (12, 8, 0, 0.08, 0.08, 3.0, "arch", "col"),

    # Bench
    (2, 1, 0, 3, 0.5, 0.45, "arch", "bench"),

    # Foliage — trees as tall thin boxes (simplified)
    (-2, -2, 0, 0.16, 0.16, 3.5, "foliage", "trunk"),
    (-2, -2, 3.5, 3.6, 3.6, 4.0, "foliage", "crown"),
    (-2, 10, 0, 0.16, 0.16, 4.0, "foliage", "trunk"),
    (-2, 10, 4.0, 4.4, 4.4, 5.0, "foliage", "crown"),
    (16, -1, 0, 0.16, 0.16, 3.0, "foliage", "trunk"),
    (16, -1, 3.0, 3.0, 3.0, 3.5, "foliage", "crown"),
    (16, 10, 0, 0.16, 0.16, 4.5, "foliage", "trunk"),
    (16, 10, 4.5, 5.0, 5.0, 5.5, "foliage", "crown"),
    (7, -3, 0, 0.16, 0.16, 3.5, "foliage", "trunk"),
    (7, -3, 3.5, 4.0, 4.0, 4.5, "foliage", "crown"),
    (-3, 5, 0, 0.16, 0.16, 4.0, "foliage", "trunk"),
    (-3, 5, 4.0, 3.6, 3.6, 4.0, "foliage", "crown"),

    # Hedge
    (-1, -2, 0, 8, 0.6, 0.8, "foliage", "hedge"),
]

# ================================================================
# PROJECTION MATH
# ================================================================
def get_box_vertices(x, y, z, w, d, h):
    """8 vertices of an axis-aligned box."""
    return [
        (x, y, z), (x+w, y, z), (x+w, y+d, z), (x, y+d, z),
        (x, y, z+h), (x+w, y, z+h), (x+w, y+d, z+h), (x, y+d, z+h),
    ]

# Box faces as vertex index quads (for visible-face rendering)
BOX_FACES = [
    (0,1,2,3),  # bottom
    (4,5,6,7),  # top
    (0,1,5,4),  # front
    (2,3,7,6),  # back
    (0,3,7,4),  # left
    (1,2,6,5),  # right
]

def cut_box(x, y, z, w, d, h, cut_h):
    """Clip a box to Z <= cut_h. Returns clipped (x,y,z,w,d,h) or None."""
    if z >= cut_h:
        return None  # entirely above cut
    if z + h <= cut_h:
        return (x, y, z, w, d, h)  # entirely below
    return (x, y, z, w, d, cut_h - z)  # clip top

def oblique_project(verts, ang_rad, dp, rot_rad, cx, cy):
    """Apply rotation then plan oblique shear, project to 2D (drop Z)."""
    projected = []
    cos_r = math.cos(rot_rad)
    sin_r = math.sin(rot_rad)
    shear_x = dp * math.cos(ang_rad)
    shear_y = dp * math.sin(ang_rad)

    for (x, y, z) in verts:
        # rotate around center
        dx, dy = x - cx, y - cy
        rx = dx * cos_r - dy * sin_r + cx
        ry = dx * sin_r + dy * cos_r + cy
        # plan oblique shear
        px = rx + shear_x * z
        py = ry + shear_y * z
        projected.append((px, py, z))
    return projected

def face_2d(proj_verts, face_indices):
    """Get 2D polygon for a face."""
    return [(proj_verts[i][0], proj_verts[i][1]) for i in face_indices]

def face_normal_z(proj_verts, face_indices):
    """Compute Z component of face normal in projected space (for backface culling)."""
    pts = [(proj_verts[i][0], proj_verts[i][1]) for i in face_indices]
    # cross product of two edges
    ax, ay = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
    bx, by = pts[2][0] - pts[0][0], pts[2][1] - pts[0][1]
    return ax * by - ay * bx

def avg_depth(proj_verts, face_indices):
    """Average Z for painter's algorithm sorting."""
    return sum(proj_verts[i][2] for i in face_indices) / len(face_indices)

# ================================================================
# RENDER
# ================================================================
ang_rad = math.radians(ANGLE)
rot_rad = math.radians(ROTATION)

# compute center of all geometry
all_x = []
all_y = []
for (x, y, z, w, d, h, cat, lbl) in BOXES:
    all_x.extend([x, x+w])
    all_y.extend([y, y+d])
cx = (min(all_x) + max(all_x)) / 2.0
cy = (min(all_y) + max(all_y)) / 2.0

# Process all boxes into projected faces
all_faces = []  # (polygon_2d, avg_z, category, label)

for (x, y, z, w, d, h, cat, lbl) in BOXES:
    was_cut = False
    # section cut
    if CUT_ON:
        clipped = cut_box(x, y, z, w, d, h, CUT_H)
        if clipped is None:
            continue
        if clipped[5] < h:  # height was reduced = this object was cut
            was_cut = True
        x, y, z, w, d, h = clipped

    verts = get_box_vertices(x, y, z, w, d, h)
    proj = oblique_project(verts, ang_rad, DEPTH, rot_rad, cx, cy)

    for fi, face in enumerate(BOX_FACES):
        nz = face_normal_z(proj, face)
        if nz < 0:
            continue  # backface cull
        poly = face_2d(proj, face)
        az = avg_depth(proj, face)
        is_cut_top = (fi == 1 and was_cut)
        all_faces.append((poly, az, cat, lbl, fi, is_cut_top))

# Sort by depth (painter's algorithm — draw far things first)
all_faces.sort(key=lambda f: f[1])

# Compute SVG bounds
all_px = [p[0] for (poly, _, _, _, _, _) in all_faces for p in poly]
all_py = [p[1] for (poly, _, _, _, _, _) in all_faces for p in poly]
min_x, max_x = min(all_px) - 1, max(all_px) + 1
min_y, max_y = min(all_py) - 1, max(all_py) + 1

# SVG coordinate system: flip Y
svg_w = 800
svg_h = int(svg_w * (max_y - min_y) / (max_x - min_x))
scale = svg_w / (max_x - min_x)

def to_svg(px, py):
    sx = (px - min_x) * scale
    sy = (max_y - py) * scale  # flip Y
    return sx, sy

# Category colors
COLORS = {
    "arch": {"fill": "#d4cfc4", "stroke": "#333333", "top": "#e8e4da", "cut": "#555555"},
    "ground": {"fill": "#c8b898", "stroke": "#8a7e6a", "top": "#d8ccb0", "cut": "#8a7e6a"},
    "foliage": {"fill": "#6a9e55", "stroke": "#3d6b2e", "top": "#7db866", "cut": "#2d5420"},
}

def face_color(cat, face_idx, is_cut_face=False):
    c = COLORS[cat]
    if face_idx == 1:  # top face
        if is_cut_face:
            return c["cut"]  # section poché — darker
        return c["top"]
    if face_idx == 0:
        return c["fill"]
    return c["fill"]

# Build SVG
lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append('<svg xmlns="http://www.w3.org/2000/svg" '
             'width="{0}" height="{1}" '
             'viewBox="0 0 {0} {1}" '
             'style="background:#f5f0e8">'.format(svg_w, svg_h))

# Title
lines.append('<text x="10" y="25" font-family="Arial, sans-serif" '
             'font-size="14" fill="#333">Sonsbeek Pavilion (Rietveld 1955) '
             '— Cabinet 45, rotation 30, section cut Z=2.5m</text>')

for (poly, az, cat, lbl, fi, is_cut_top) in all_faces:
    pts_str = " ".join("{0:.1f},{1:.1f}".format(*to_svg(px, py)) for px, py in poly)
    fill = face_color(cat, fi, is_cut_top)
    stroke = COLORS[cat]["stroke"]
    if is_cut_top:
        stroke = "#1a1a1a"  # darker outline for cut faces
    sw = "0.3" if lbl == "col" else "0.8"
    lines.append('  <polygon points="{0}" fill="{1}" stroke="{2}" '
                 'stroke-width="{3}" stroke-linejoin="round"/>'.format(
                     pts_str, fill, stroke, sw))

# Legend
ly = svg_h - 60
for cat, label in [("arch", "Architecture"), ("ground", "Ground"), ("foliage", "Foliage")]:
    lines.append('<rect x="10" y="{0}" width="16" height="16" fill="{1}" '
                 'stroke="{2}" stroke-width="1"/>'.format(
                     ly, COLORS[cat]["fill"], COLORS[cat]["stroke"]))
    lines.append('<text x="32" y="{0}" font-family="Arial, sans-serif" '
                 'font-size="12" fill="#333">{1}</text>'.format(ly + 13, label))
    ly += 22

lines.append('</svg>')

svg_path = "/home/user/Radical-Accessibility-Toolkit/tools/rhino/sonsbeek_oblique.svg"
with open(svg_path, "w") as f:
    f.write("\n".join(lines))
print("OK: SVG written to {0}".format(svg_path))
print("  {0} faces rendered".format(len(all_faces)))
