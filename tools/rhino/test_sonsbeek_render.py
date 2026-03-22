#!/usr/bin/env python3
"""Render a Military plan oblique of the Sonsbeek Pavilion as SVG.
Based on the actual Rietveld plan: curved + straight walls, columns, platforms.
Pure Python — no Rhino needed."""

import math

# ================================================================
# OBLIQUE PROJECTION SETTINGS — Military
# ================================================================
ANGLE = 90.0       # verticals go straight up
DEPTH = 1.0        # full depth
ROTATION = 45.0    # plan rotated 45
CUT_ON = False

# ================================================================
# WALL GEOMETRY BUILDERS
# ================================================================
def make_wall(x1, y1, x2, y2, thickness, z0, h, cat, lbl):
    """Oriented wall from (x1,y1) to (x2,y2) with thickness and height.
    Returns list of 3D quads (8 vertices each) as dicts."""
    dx, dy = x2 - x1, y2 - y1
    length = math.sqrt(dx*dx + dy*dy)
    if length < 0.001:
        return []
    # normal perpendicular to wall direction
    nx, ny = -dy / length, dx / length
    t2 = thickness / 2.0
    # 4 base corners
    corners = [
        (x1 + nx*t2, y1 + ny*t2),
        (x2 + nx*t2, y2 + ny*t2),
        (x2 - nx*t2, y2 - ny*t2),
        (x1 - nx*t2, y1 - ny*t2),
    ]
    verts = []
    for cx, cy in corners:
        verts.append((cx, cy, z0))
    for cx, cy in corners:
        verts.append((cx, cy, z0 + h))
    return [{"verts": verts, "cat": cat, "lbl": lbl}]

def make_arc_wall(cx, cy, radius, start_deg, end_deg, thickness, z0, h, cat, lbl, n_seg=20):
    """Curved wall along an arc. Returns list of wall segment dicts."""
    walls = []
    for i in range(n_seg):
        a1 = math.radians(start_deg + (end_deg - start_deg) * i / n_seg)
        a2 = math.radians(start_deg + (end_deg - start_deg) * (i + 1) / n_seg)
        x1 = cx + radius * math.cos(a1)
        y1 = cy + radius * math.sin(a1)
        x2 = cx + radius * math.cos(a2)
        y2 = cy + radius * math.sin(a2)
        walls.extend(make_wall(x1, y1, x2, y2, thickness, z0, h, cat, lbl))
    return walls

def make_box(x, y, z, w, d, h, cat, lbl):
    """Axis-aligned box."""
    verts = [
        (x, y, z), (x+w, y, z), (x+w, y+d, z), (x, y+d, z),
        (x, y, z+h), (x+w, y, z+h), (x+w, y+d, z+h), (x, y+d, z+h),
    ]
    return [{"verts": verts, "cat": cat, "lbl": lbl}]

def make_column(cx, cy, z0, h, radius, cat, n=8):
    """Polygonal column."""
    bottom, top = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        px = cx + radius * math.cos(a)
        py = cy + radius * math.sin(a)
        bottom.append((px, py, z0))
        top.append((px, py, z0 + h))
    return [{"verts": bottom + top, "cat": cat, "lbl": "col", "nsides": n}]

# ================================================================
# SONSBEEK PAVILION — based on actual Rietveld plan
# ================================================================
# Coordinate system: plan is ~12m x 10m, centered roughly at (6, 5)
# Black walls = 3.5m high (user said 14m but that's ~4 stories;
#   using proportional height for good oblique reading)
# Gray platform walls = 1m high

WALL_H = 3.5       # full-height walls
PLAT_H = 1.0       # platform walls
WT = 0.25           # wall thickness
PWT = 0.20          # platform wall thickness
FLOOR_Z = 0.0

all_solids = []

# ---- GROUND ----
all_solids.extend(make_box(-2, -2, -0.05, 18, 14, 0.05, "ground", "ground"))

# ---- PLATFORM (raised floor) ----
all_solids.extend(make_box(0.5, 0.5, 0, 13, 9, 0.15, "platform", "slab"))

# ---- PLATFORM WALLS (gray, 1m high) — perimeter ----
# Left platform wall (tall rectangle in plan)
all_solids.extend(make_wall(0.5, 1.5, 0.5, 8.5, PWT, 0.15, PLAT_H, "platform", "plat_wall"))

# Right platform wall
all_solids.extend(make_wall(13.0, 1.5, 13.0, 8.5, PWT, 0.15, PLAT_H, "platform", "plat_wall"))

# Small platform rectangles near center-top
all_solids.extend(make_box(5.5, 7.5, 0.15, 1.2, 0.6, PLAT_H, "platform", "plat_wall"))
all_solids.extend(make_box(8.5, 7.5, 0.15, 0.8, 0.5, PLAT_H, "platform", "plat_wall"))

# Small platform rectangle lower center
all_solids.extend(make_box(7.5, 1.5, 0.15, 1.5, 0.8, PLAT_H, "platform", "plat_wall"))

# ---- STRAIGHT BLACK WALLS (14m / 3.5m high) ----
# Reading from the plan left to right:

# Wall 1 — far left, long N-S wall
all_solids.extend(make_wall(2.0, 0.5, 2.0, 9.5, WT, 0.15, WALL_H, "arch", "wall"))

# Wall 2 — second from left, two segments with door gap
all_solids.extend(make_wall(4.0, 0.5, 4.0, 3.5, WT, 0.15, WALL_H, "arch", "wall"))
all_solids.extend(make_wall(4.0, 5.5, 4.0, 9.5, WT, 0.15, WALL_H, "arch", "wall"))

# Wall 3 — center-left, segments
all_solids.extend(make_wall(5.5, 0.5, 5.5, 2.5, WT, 0.15, WALL_H, "arch", "wall"))
all_solids.extend(make_wall(5.5, 7.0, 5.5, 9.5, WT, 0.15, WALL_H, "arch", "wall"))

# Wall 4 — center
all_solids.extend(make_wall(7.0, 0.5, 7.0, 2.0, WT, 0.15, WALL_H, "arch", "wall"))
all_solids.extend(make_wall(7.0, 8.0, 7.0, 9.5, WT, 0.15, WALL_H, "arch", "wall"))

# Wall 5 — center-right
all_solids.extend(make_wall(8.5, 0.5, 8.5, 2.0, WT, 0.15, WALL_H, "arch", "wall"))
all_solids.extend(make_wall(8.5, 7.5, 8.5, 9.5, WT, 0.15, WALL_H, "arch", "wall"))

# Wall 6 — second from right, segments
all_solids.extend(make_wall(10.0, 0.5, 10.0, 4.0, WT, 0.15, WALL_H, "arch", "wall"))
all_solids.extend(make_wall(10.0, 6.0, 10.0, 9.5, WT, 0.15, WALL_H, "arch", "wall"))

# Wall 7 — far right, long wall
all_solids.extend(make_wall(11.5, 0.5, 11.5, 9.5, WT, 0.15, WALL_H, "arch", "wall"))

# ---- CURVED WALLS (black, same height) ----
# Left biomorphic curve — large C/S shape opening right
# Approximating the two connected arcs visible in the plan:

# Left curve — upper arc (opens right, concave right)
all_solids.extend(make_arc_wall(
    4.0, 6.0, 2.5, 90, 270, WT, 0.15, WALL_H, "arch", "curve", n_seg=24))

# Left curve — lower arc connecting (opens right, smaller)
all_solids.extend(make_arc_wall(
    4.0, 3.5, 1.8, 90, 250, WT, 0.15, WALL_H, "arch", "curve", n_seg=20))

# Right biomorphic curve — mirror, opening left
# Upper arc
all_solids.extend(make_arc_wall(
    9.5, 6.0, 2.2, -90, 90, WT, 0.15, WALL_H, "arch", "curve", n_seg=24))

# Lower arc
all_solids.extend(make_arc_wall(
    9.5, 3.5, 1.5, -70, 90, WT, 0.15, WALL_H, "arch", "curve", n_seg=20))

# ---- COLUMNS (circles in plan) ----
# Small column top center
all_solids.extend(make_column(6.5, 8.5, 0.15, WALL_H, 0.15, "arch"))

# Column center-left
all_solids.extend(make_column(5.0, 5.0, 0.15, WALL_H, 0.25, "arch"))

# Column center
all_solids.extend(make_column(7.5, 5.5, 0.15, WALL_H, 0.20, "arch"))

# Column right
all_solids.extend(make_column(11.0, 4.5, 0.15, WALL_H, 0.25, "arch"))

# Small column bottom center
all_solids.extend(make_column(6.5, 1.0, 0.15, WALL_H, 0.12, "arch"))

# ================================================================
# PROJECTION + RENDERING
# ================================================================
FACES_QUAD = [
    (0,1,2,3),  # bottom
    (4,5,6,7),  # top
    (0,1,5,4),  # front
    (2,3,7,6),  # back
    (0,3,7,4),  # left
    (1,2,6,5),  # right
]

def get_ngon_faces(n):
    """Face indices for an n-sided prism."""
    faces = []
    # bottom
    faces.append(tuple(range(n)))
    # top
    faces.append(tuple(range(n, 2*n)))
    # sides
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j+n, i+n))
    return faces

def oblique_project(verts, ang_rad, dp, rot_rad, cx, cy):
    projected = []
    cos_r, sin_r = math.cos(rot_rad), math.sin(rot_rad)
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

def face_2d(proj, fi):
    return [(proj[i][0], proj[i][1]) for i in fi]

def face_normal_z(proj, fi):
    pts = [(proj[i][0], proj[i][1]) for i in fi]
    if len(pts) < 3:
        return 0
    ax, ay = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
    bx, by = pts[2][0] - pts[0][0], pts[2][1] - pts[0][1]
    return ax * by - ay * bx

def polygon_area(poly):
    n = len(poly)
    a = 0.0
    for i in range(n):
        j = (i + 1) % n
        a += poly[i][0] * poly[j][1] - poly[j][0] * poly[i][1]
    return a / 2.0

ang_rad = math.radians(ANGLE)
rot_rad = math.radians(ROTATION)

# Center
all_x, all_y = [], []
for s in all_solids:
    for v in s["verts"]:
        all_x.append(v[0])
        all_y.append(v[1])
cx = (min(all_x) + max(all_x)) / 2.0
cy = (min(all_y) + max(all_y)) / 2.0

# Generate faces
all_faces = []
cat_order = {"ground": 0, "platform": 1, "foliage": 2, "arch": 3}

for solid in all_solids:
    verts = solid["verts"]
    cat = solid["cat"]
    lbl = solid["lbl"]
    nsides = solid.get("nsides", 4)

    proj = oblique_project(verts, ang_rad, DEPTH, rot_rad, cx, cy)

    if nsides == 4:
        faces = FACES_QUAD
    else:
        faces = get_ngon_faces(nsides)

    for fi_idx, face in enumerate(faces):
        nz = face_normal_z(proj, face)
        if nz < 0:
            continue
        poly = face_2d(proj, face)
        if abs(polygon_area(poly)) < 0.005:
            continue
        avg_z = sum(proj[i][2] for i in face) / len(face)
        is_top = (fi_idx == 1)  # second face is always top
        all_faces.append((poly, avg_z, cat, lbl, is_top))

all_faces.sort(key=lambda f: (cat_order.get(f[2], 2), f[1]))

# SVG bounds
all_px = [p[0] for f in all_faces for p in f[0]]
all_py = [p[1] for f in all_faces for p in f[0]]
pad = 1.5
min_x, max_x = min(all_px) - pad, max(all_px) + pad
min_y, max_y = min(all_py) - pad, max(all_py) + pad

svg_w = 1000
svg_h = int(svg_w * (max_y - min_y) / (max_x - min_x))
if svg_h < 500:
    svg_h = 500
sc = svg_w / (max_x - min_x)

def to_svg(px, py):
    return (px - min_x) * sc, (max_y - py) * sc

COLORS = {
    "arch":     {"side": "#2a2a2a", "top": "#1a1a1a",
                 "stroke": "#000000"},
    "platform": {"side": "#b0a898", "top": "#ccc5b8",
                 "stroke": "#8a8070"},
    "ground":   {"side": "#c8c0a8", "top": "#ddd8c8",
                 "stroke": "#a09880"},
}

def get_fill(cat, lbl, is_top):
    c = COLORS[cat]
    if cat == "arch":
        # black walls — dark gray sides, very dark tops
        return c["top"] if is_top else c["side"]
    return c["top"] if is_top else c["side"]

lines = []
lines.append('<?xml version="1.0" encoding="UTF-8"?>')
lines.append('<svg xmlns="http://www.w3.org/2000/svg" '
             'width="{0}" height="{1}" viewBox="0 0 {0} {1}" '
             'style="background:#f0ece0">'.format(svg_w, svg_h))

lines.append('<text x="14" y="24" font-family="Helvetica, Arial, sans-serif" '
             'font-size="14" fill="#333" font-weight="bold">'
             'Sonsbeek Pavilion (Rietveld 1955) — Military oblique</text>')

for (poly, avg_z, cat, lbl, is_top) in all_faces:
    pts_str = " ".join("{0:.1f},{1:.1f}".format(*to_svg(px, py)) for px, py in poly)
    fill = get_fill(cat, lbl, is_top)
    stroke = COLORS[cat]["stroke"]
    sw = "0.3" if lbl == "col" else "0.6"
    if cat == "ground":
        sw = "0.3"
    lines.append('  <polygon points="{0}" fill="{1}" stroke="{2}" '
                 'stroke-width="{3}" stroke-linejoin="round"/>'.format(
                     pts_str, fill, stroke, sw))

# Legend
ly = svg_h - 60
for cat, label in [("arch", "Walls (3.5m)"), ("platform", "Platform (1m)"), ("ground", "Ground")]:
    c = COLORS[cat]
    lines.append('<rect x="14" y="{0}" width="14" height="14" fill="{1}" '
                 'stroke="{2}" stroke-width="1"/>'.format(ly, c["side"], c["stroke"]))
    lines.append('<text x="34" y="{0}" font-family="Helvetica, Arial, sans-serif" '
                 'font-size="11" fill="#333">{1}</text>'.format(ly + 11, label))
    ly += 18

lines.append('</svg>')

svg_path = "/home/user/Radical-Accessibility-Toolkit/tools/rhino/sonsbeek_oblique.svg"
with open(svg_path, "w") as f:
    f.write("\n".join(lines))
print("OK: SVG written to {0}".format(svg_path))
print("  {0} faces rendered from {1} solids".format(len(all_faces), len(all_solids)))

try:
    import cairosvg
    png_path = svg_path.replace(".svg", ".png")
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=1400)
    print("OK: PNG written to {0}".format(png_path))
except ImportError:
    print("(cairosvg not installed — SVG only)")
