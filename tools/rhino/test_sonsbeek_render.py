#!/usr/bin/env python3
"""Render a Military plan oblique of the Sonsbeek Pavilion as SVG.
Pure Python — no Rhino needed. Run from command line to generate SVG + PNG."""

import math

# ================================================================
# OBLIQUE PROJECTION SETTINGS — Military (plan rotated 45, verticals up)
# ================================================================
ANGLE = 90.0       # receding axis angle (90 = verticals go straight up)
DEPTH = 1.0        # full depth (cavalier)
ROTATION = 45.0    # plan rotated 45 degrees
CUT_ON = False     # no section cut — show full pavilion

# ================================================================
# GEOMETRY — Sonsbeek Pavilion (Rietveld 1955)
# ================================================================
# Freestanding walls with door openings on a raised platform.
# Each entry: (x, y, z, w, d, h, category, label)

WT = 0.25  # wall thickness

BOXES = [
    # ---- GROUND ----
    # Park ground (large)
    (-4, -4, -0.08, 26, 20, 0.08, "ground", "park"),

    # ---- PLATFORM ----
    # Raised concrete platform
    (-0.5, -0.5, 0, 15, 11, 0.3, "platform", "platform"),

    # ---- ARCHITECTURE — walls with door openings ----
    # Wall A south — long wall running east, split by door
    (0, 0, 0.3, 4.0, WT, 3.0, "arch", "wall"),
    (5.2, 0, 0.3, 5.8, WT, 3.0, "arch", "wall"),      # door gap 4.0-5.2

    # Wall B north — long wall, split by two doors
    (1, 9.5, 0.3, 3.5, WT, 3.5, "arch", "wall"),
    (5.8, 9.5, 0.3, 3.0, WT, 3.5, "arch", "wall"),     # door gap 4.5-5.8
    (10.0, 9.5, 0.3, 3.5, WT, 3.5, "arch", "wall"),     # door gap 8.8-10.0

    # Wall C — interior wall, offset, with door
    (3.5, 4.5, 0.3, 3.0, WT, 2.8, "arch", "wall"),
    (7.8, 4.5, 0.3, 2.5, WT, 2.8, "arch", "wall"),      # door gap 6.5-7.8

    # Wall D — west short wall, no door
    (0, 0, 0.3, WT, 5.5, 3.2, "arch", "wall"),

    # Wall E — east wall, with door
    (13, 2, 0.3, WT, 3.0, 3.0, "arch", "wall"),
    (13, 6.5, 0.3, WT, 3.5, 3.0, "arch", "wall"),       # door gap 5.0-6.5

    # Wall F — short interior screen
    (6.5, 1.5, 0.3, WT, 2.5, 2.5, "arch", "wall"),

    # Wall G — freestanding sculpture wall
    (9, 6, 0.3, WT, 3.5, 3.2, "arch", "wall"),

    # ---- ROOF PLANES ----
    # Main floating roof
    (0.5, -0.2, 3.5, 11, 10.5, 0.12, "arch", "roof"),

    # Secondary canopy
    (8, 4, 3.3, 6, 6.5, 0.10, "arch", "roof"),

    # ---- STEEL COLUMNS ----
    (1.0, 0.8, 0.3, 0.08, 0.08, 3.2, "arch", "col"),
    (1.0, 8.5, 0.3, 0.08, 0.08, 3.2, "arch", "col"),
    (5.5, 0.8, 0.3, 0.08, 0.08, 3.2, "arch", "col"),
    (5.5, 8.5, 0.3, 0.08, 0.08, 3.2, "arch", "col"),
    (10.5, 0.8, 0.3, 0.08, 0.08, 3.2, "arch", "col"),
    (10.5, 8.5, 0.3, 0.08, 0.08, 3.2, "arch", "col"),
    (9, 4.5, 0.3, 0.08, 0.08, 3.0, "arch", "col"),
    (9, 9.5, 0.3, 0.08, 0.08, 3.0, "arch", "col"),
    (13.5, 4.5, 0.3, 0.08, 0.08, 3.0, "arch", "col"),
    (13.5, 9.5, 0.3, 0.08, 0.08, 3.0, "arch", "col"),

    # ---- FOLIAGE ----
    # Trees (box trunks + box crowns centered on trunk)
    (-2.5, -2.5, 0, 0.2, 0.2, 4.0, "foliage", "trunk"),
    (-3.5, -3.5, 4.0, 2.2, 2.2, 3.0, "foliage", "crown"),

    (-2.5, 12.0, 0, 0.2, 0.2, 4.5, "foliage", "trunk"),
    (-3.5, 11.0, 4.5, 2.2, 2.2, 3.5, "foliage", "crown"),

    (18.0, -2.0, 0, 0.2, 0.2, 3.5, "foliage", "trunk"),
    (17.0, -3.0, 3.5, 2.2, 2.2, 3.0, "foliage", "crown"),

    (18.0, 12.0, 0, 0.2, 0.2, 5.0, "foliage", "trunk"),
    (17.0, 11.0, 5.0, 2.2, 2.2, 3.5, "foliage", "crown"),

    (7.0, -3.5, 0, 0.2, 0.2, 4.0, "foliage", "trunk"),
    (6.0, -4.5, 4.0, 2.2, 2.2, 3.0, "foliage", "crown"),

    # Low hedge
    (-1, -3, 0, 9, 0.8, 1.0, "foliage", "hedge"),
]

# ================================================================
# PROJECTION MATH
# ================================================================
def get_box_vertices(x, y, z, w, d, h):
    """8 vertices of an axis-aligned box."""
    return [
        (x, y, z), (x+w, y, z), (x+w, y+d, z), (x, y+d, z),         # bottom
        (x, y, z+h), (x+w, y, z+h), (x+w, y+d, z+h), (x, y+d, z+h), # top
    ]

BOX_FACES = [
    (0,1,2,3),  # bottom  (fi=0)
    (4,5,6,7),  # top     (fi=1)
    (0,1,5,4),  # front   (fi=2) — low Y side
    (2,3,7,6),  # back    (fi=3) — high Y side
    (0,3,7,4),  # left    (fi=4) — low X side
    (1,2,6,5),  # right   (fi=5) — high X side
]

def cut_box(x, y, z, w, d, h, cut_h):
    if z >= cut_h:
        return None
    if z + h <= cut_h:
        return (x, y, z, w, d, h)
    return (x, y, z, w, d, cut_h - z)

def oblique_project(verts, ang_rad, dp, rot_rad, cx, cy):
    """Rotation then plan oblique shear."""
    projected = []
    cos_r = math.cos(rot_rad)
    sin_r = math.sin(rot_rad)
    shear_x = dp * math.cos(ang_rad)
    shear_y = dp * math.sin(ang_rad)
    for (x, y, z) in verts:
        dx, dy = x - cx, y - cy
        rx = dx * cos_r - dy * sin_r + cx
        ry = dx * sin_r + dy * cos_r + cy
        px = rx + shear_x * z
        py = ry + shear_y * z
        projected.append((px, py, z))
    return projected

def face_2d(proj_verts, face_indices):
    return [(proj_verts[i][0], proj_verts[i][1]) for i in face_indices]

def face_normal_z(proj_verts, face_indices):
    pts = [(proj_verts[i][0], proj_verts[i][1]) for i in face_indices]
    ax, ay = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
    bx, by = pts[2][0] - pts[0][0], pts[2][1] - pts[0][1]
    return ax * by - ay * bx

def polygon_area(poly):
    """Signed area — positive if CCW."""
    n = len(poly)
    a = 0.0
    for i in range(n):
        j = (i + 1) % n
        a += poly[i][0] * poly[j][1]
        a -= poly[j][0] * poly[i][1]
    return a / 2.0

def sort_key(face_tuple):
    """Sort for painter's algorithm.
    Primary: average Z (low = far = draw first).
    Secondary: min Z (ensures ground drawn before walls on it).
    Tertiary: face index (bottom before sides before top)."""
    poly, avg_z, cat, lbl, fi, is_cut_top = face_tuple
    # boost ground and platform to draw first
    cat_order = {"ground": 0, "platform": 1, "foliage": 2, "arch": 3}
    return (cat_order.get(cat, 2), avg_z, fi)

# ================================================================
# RENDER
# ================================================================
ang_rad = math.radians(ANGLE)
rot_rad = math.radians(ROTATION)

# center of all geometry
all_x, all_y = [], []
for (x, y, z, w, d, h, cat, lbl) in BOXES:
    all_x.extend([x, x+w])
    all_y.extend([y, y+d])
cx = (min(all_x) + max(all_x)) / 2.0
cy = (min(all_y) + max(all_y)) / 2.0

all_faces = []

for (x, y, z, w, d, h, cat, lbl) in BOXES:
    was_cut = False
    if CUT_ON:
        clipped = cut_box(x, y, z, w, d, h, CUT_H)
        if clipped is None:
            continue
        if clipped[5] < h:
            was_cut = True
        x, y, z, w, d, h = clipped

    verts = get_box_vertices(x, y, z, w, d, h)
    proj = oblique_project(verts, ang_rad, DEPTH, rot_rad, cx, cy)

    for fi, face in enumerate(BOX_FACES):
        nz = face_normal_z(proj, face)
        if nz < 0:
            continue  # backface cull
        # skip degenerate faces (area near zero)
        poly = face_2d(proj, face)
        if abs(polygon_area(poly)) < 0.01:
            continue
        avg_z = sum(proj[i][2] for i in face) / len(face)
        is_cut_top = (fi == 1 and was_cut)
        all_faces.append((poly, avg_z, cat, lbl, fi, is_cut_top))

# Sort by depth
all_faces.sort(key=sort_key)

# SVG bounds
all_px = [p[0] for f in all_faces for p in f[0]]
all_py = [p[1] for f in all_faces for p in f[0]]
pad = 2
min_x, max_x = min(all_px) - pad, max(all_px) + pad
min_y, max_y = min(all_py) - pad, max(all_py) + pad

svg_w = 900
svg_h = int(svg_w * (max_y - min_y) / (max_x - min_x))
if svg_h < 400:
    svg_h = 400
sc = svg_w / (max_x - min_x)

def to_svg(px, py):
    return (px - min_x) * sc, (max_y - py) * sc

# Colors — solid, opaque
COLORS = {
    "arch":     {"side": "#c8c0b0", "top": "#e0dbd0", "cut": "#555555",
                 "stroke": "#222222", "roof_top": "#ddd8cc", "roof_side": "#bbb5a5"},
    "platform": {"side": "#b0a898", "top": "#ccc5b8", "cut": "#888",
                 "stroke": "#665e50"},
    "ground":   {"side": "#8a9e6a", "top": "#a8be84", "cut": "#8a7e6a",
                 "stroke": "#667750"},
    "foliage":  {"side": "#4a8035", "top": "#6aaa50", "cut": "#2d5420",
                 "stroke": "#2a5518", "crown_side": "#3a7028", "crown_top": "#5a9a40"},
}

def get_fill(cat, lbl, fi, is_cut_top):
    c = COLORS[cat]
    if is_cut_top:
        return c["cut"]
    if cat == "arch" and lbl == "roof":
        return c["roof_top"] if fi == 1 else c["roof_side"]
    if cat == "foliage" and lbl == "crown":
        return c.get("crown_top", c["top"]) if fi == 1 else c.get("crown_side", c["side"])
    if fi == 1:
        return c["top"]
    return c["side"]

def get_stroke(cat, is_cut_top):
    if is_cut_top:
        return "#111111"
    return COLORS[cat]["stroke"]

# Build SVG
lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append('<svg xmlns="http://www.w3.org/2000/svg" '
             'width="{0}" height="{1}" viewBox="0 0 {0} {1}" '
             'style="background:#e8e4d8">'.format(svg_w, svg_h))

lines.append('<text x="12" y="22" font-family="Helvetica, Arial, sans-serif" '
             'font-size="13" fill="#333" font-weight="bold">'
             'Sonsbeek Pavilion (Rietveld 1955) — Military oblique</text>')

for (poly, avg_z, cat, lbl, fi, is_cut_top) in all_faces:
    pts_str = " ".join("{0:.1f},{1:.1f}".format(*to_svg(px, py)) for px, py in poly)
    fill = get_fill(cat, lbl, fi, is_cut_top)
    stroke = get_stroke(cat, is_cut_top)
    sw = "0.4" if lbl == "col" else "0.7"
    if cat == "ground":
        sw = "0.5"
    lines.append('  <polygon points="{0}" fill="{1}" stroke="{2}" '
                 'stroke-width="{3}" stroke-linejoin="round"/>'.format(
                     pts_str, fill, stroke, sw))

# Legend
ly = svg_h - 80
for cat, label in [("arch", "Architecture"), ("platform", "Platform"),
                    ("ground", "Ground"), ("foliage", "Foliage")]:
    c = COLORS[cat]
    lines.append('<rect x="12" y="{0}" width="14" height="14" fill="{1}" '
                 'stroke="{2}" stroke-width="1"/>'.format(ly, c["top"], c["stroke"]))
    lines.append('<text x="32" y="{0}" font-family="Helvetica, Arial, sans-serif" '
                 'font-size="11" fill="#333">{1}</text>'.format(ly + 11, label))
    ly += 18

lines.append('</svg>')

svg_path = "/home/user/Radical-Accessibility-Toolkit/tools/rhino/sonsbeek_oblique.svg"
with open(svg_path, "w") as f:
    f.write("\n".join(lines))
print("OK: SVG written to {0}".format(svg_path))
print("  {0} faces rendered".format(len(all_faces)))

# Also generate PNG
try:
    import cairosvg
    png_path = svg_path.replace(".svg", ".png")
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=1200)
    print("OK: PNG written to {0}".format(png_path))
except ImportError:
    print("(cairosvg not installed — SVG only)")
