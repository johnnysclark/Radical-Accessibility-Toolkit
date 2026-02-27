# -*- coding: utf-8 -*-
"""
PLAN LAYOUT JIG — Rhino Watcher  v2.3
======================================
This script runs inside Rhino or Grasshopper. It watches the JSON
state file written by the terminal controller. Every time the file
changes, the watcher clears all geometry and redraws from scratch.

The watcher never writes to the JSON file. Communication is
one-way: controller writes, watcher reads.

2D Layers:
    JIG_SITE         Site boundary rectangle
    JIG_BACKGROUND   White masks for z-order overlaps
    JIG_HATCHES      Room fill patterns for PIAF tactile output
    JIG_BAYS         Structural gridlines
    JIG_COLUMNS      Column squares at grid intersections
    JIG_PLAN         Wall outlines with aperture cutouts
    JIG_BLOCKS       Aperture symbols and room labels
    JIG_CORRIDOR     Corridor edges, centerlines, hatch fills
    JIG_VOIDS        Void outlines (rectangles or circles)
    JIG_ROOMS        Cell room boundaries, labels, areas, hatches
    JIG_LABELS       Bay labels in English and Braille
    JIG_LEGEND       Braille plus English legend key box

3D Layer:
    JIG_TACTILE3D    Extruded walls, floor slab, clipping plane

Run inside Rhino or Grasshopper Python:
    exec(open("C:/path/to/rhino_watcher.py").read())
"""
import json, math, os, time, threading

try:
    import rhinoscriptsyntax as rs
    import Rhino
    import scriptcontext as sc
    IN_RHINO = True
except ImportError:
    IN_RHINO = False
    print("[WARN] Not in Rhino. Geometry calls will be skipped.")

# ── Configuration ──────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()
STATE_FILE = os.path.join(SCRIPT_DIR, "state.json")
POLL_SEC = 0.5

LAYERS = [
    "JIG_SITE", "JIG_BACKGROUND", "JIG_HATCHES", "JIG_BAYS",
    "JIG_COLUMNS", "JIG_PLAN", "JIG_BLOCKS", "JIG_CORRIDOR",
    "JIG_VOIDS", "JIG_ROOMS", "JIG_LABELS", "JIG_LEGEND", "JIG_TACTILE3D",
]

LAYER_COLORS = {
    "JIG_SITE":       (80, 80, 80),
    "JIG_BACKGROUND": (255,255,255),
    "JIG_HATCHES":    (200,200,200),
    "JIG_BAYS":       (0, 0, 0),
    "JIG_COLUMNS":    (0, 0, 0),
    "JIG_PLAN":       (40, 40, 40),
    "JIG_BLOCKS":     (0, 0, 0),
    "JIG_CORRIDOR":   (100, 100, 100),
    "JIG_VOIDS":      (0, 0, 0),
    "JIG_LABELS":     (0, 0, 0),
    "JIG_LEGEND":     (0, 0, 0),
    "JIG_TACTILE3D":  (180, 60, 60),
}

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif"}

# Map user-facing hatch names to Rhino's built-in hatch patterns
HATCH_MAP = {"diagonal": "Hatch1", "crosshatch": "Grid", "dots": "Dots",
             "horizontal": "Dash", "solid": "Solid"}

# ══════════════════════════════════════════════════════════
# STYLE + STATE HELPERS
# ══════════════════════════════════════════════════════════

def _s(state, key, default):
    """Read a style parameter from state['style'], with fallback."""
    return state.get("style", {}).get(key, default)

def _load_state():
    if not os.path.exists(STATE_FILE): return None
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _state_mtime():
    try: return os.stat(STATE_FILE).st_mtime
    except: return 0

# ══════════════════════════════════════════════════════════
# GEOMETRY HELPERS
# ══════════════════════════════════════════════════════════

def _get_spacing_arrays(bay):
    nx, ny = bay["bays"]
    sx_a = bay.get("spacing_x"); sy_a = bay.get("spacing_y")
    if sx_a and len(sx_a) == nx:
        cx = [0.0]
        for s in sx_a: cx.append(cx[-1] + s)
    else:
        s = bay["spacing"][0]; cx = [i * s for i in range(nx + 1)]
    if sy_a and len(sy_a) == ny:
        cy = [0.0]
        for s in sy_a: cy.append(cy[-1] + s)
    else:
        s = bay["spacing"][1]; cy = [j * s for j in range(ny + 1)]
    return cx, cy

def _local_to_world(lx, ly, origin, rot_deg):
    r = math.radians(rot_deg)
    wx = origin[0] + lx * math.cos(r) - ly * math.sin(r)
    wy = origin[1] + lx * math.sin(r) + ly * math.cos(r)
    return (wx, wy, 0)

def _arc_points(cx, cy, radius, start_deg, end_deg, n=24):
    pts = []
    for i in range(n + 1):
        a = math.radians(start_deg + (end_deg - start_deg) * i / n)
        pts.append((cx + radius * math.cos(a), cy + radius * math.sin(a), 0))
    return pts

# ══════════════════════════════════════════════════════════
# LAYER MANAGEMENT
# ══════════════════════════════════════════════════════════

def _ensure_layers():
    if not IN_RHINO: return
    for name in LAYERS:
        if not rs.IsLayer(name):
            rs.AddLayer(name, LAYER_COLORS.get(name, (0,0,0)))

def _clear_layer(name):
    if not IN_RHINO: return
    if not rs.IsLayer(name): return
    objs = rs.ObjectsByLayer(name)
    if objs: rs.DeleteObjects(objs)

def _clear_all():
    for name in LAYERS: _clear_layer(name)

def _set_layer(name):
    if IN_RHINO: rs.CurrentLayer(name)

# ══════════════════════════════════════════════════════════
# DRAWING PRIMITIVES
# ══════════════════════════════════════════════════════════

def _add_line(p1, p2):
    if IN_RHINO: return rs.AddLine(p1, p2)

def _add_rect(x0, y0, x1, y1):
    if IN_RHINO:
        pts = [(x0,y0,0),(x1,y0,0),(x1,y1,0),(x0,y1,0),(x0,y0,0)]
        return rs.AddPolyline(pts)

def _add_polyline(pts):
    if IN_RHINO and len(pts) >= 2: return rs.AddPolyline(pts)

def _add_circle(cx, cy, r):
    if IN_RHINO: return rs.AddCircle((cx, cy, 0), r)

def _add_text(txt, pt, height, font="Arial"):
    if IN_RHINO: return rs.AddText(txt, pt, height, font)

def _add_hatch(boundary_id, pattern="Solid", scale=1.0, rotation=0.0):
    if not IN_RHINO: return None
    try: return rs.AddHatch(boundary_id, pattern, scale, rotation)
    except: return None

def _add_surface_fill(boundary_id):
    if not IN_RHINO: return None
    try:
        srf = rs.AddPlanarSrf(boundary_id)
        if srf: return srf[0]
    except: pass
    return None

def _add_dashed_line(p1, p2, dash_len, gap_len):
    """Draw a dashed line between two 3D points."""
    dx = p2[0]-p1[0]; dy = p2[1]-p1[1]
    total = math.hypot(dx, dy)
    if total < 0.001: return
    ux = dx/total; uy = dy/total
    pos = 0.0
    while pos < total:
        end = min(pos + dash_len, total)
        _add_line((p1[0]+ux*pos, p1[1]+uy*pos, 0),
                  (p1[0]+ux*end, p1[1]+uy*end, 0))
        pos = end + gap_len

# ══════════════════════════════════════════════════════════
# DRAW: SITE BOUNDARY
# ══════════════════════════════════════════════════════════

def _draw_site(state):
    _set_layer("JIG_SITE")
    site = state["site"]
    ox, oy = site["origin"]
    _add_rect(ox, oy, ox + site["width"], oy + site["height"])

# ══════════════════════════════════════════════════════════
# DRAW: Z-ORDER BACKGROUND MASKS
# ══════════════════════════════════════════════════════════

def _draw_background_masks(state):
    _set_layer("JIG_BACKGROUND")
    bays = state["bays"]
    pad = _s(state, "background_pad", 2.0)
    sorted_bays = sorted(bays.items(), key=lambda x: x[1].get("z_order", 0))
    for name, bay in sorted_bays:
        if bay.get("z_order", 0) <= 0: continue
        gt = bay.get("grid_type", "rectangular")
        ox, oy = bay["origin"]; rot = bay["rotation_deg"]
        if gt == "rectangular":
            cx, cy = _get_spacing_arrays(bay)
            w, h = cx[-1], cy[-1]
            corners = [(-pad,-pad),(w+pad,-pad),(w+pad,h+pad),(-pad,h+pad),(-pad,-pad)]
            world_pts = [_local_to_world(lx,ly,(ox,oy),rot) for lx,ly in corners]
            boundary = _add_polyline(world_pts)
            if boundary and IN_RHINO:
                srf = _add_surface_fill(boundary)
                if srf: rs.ObjectColor(srf, (255,255,255))
        else:
            outer = bay.get("rings",4) * bay.get("ring_spacing",20) + pad
            circ = _add_circle(ox, oy, outer)
            if circ and IN_RHINO:
                srf = _add_surface_fill(circ)
                if srf: rs.ObjectColor(srf, (255,255,255))

# ══════════════════════════════════════════════════════════
# DRAW: ROOM HATCH FILLS
# ══════════════════════════════════════════════════════════

def _draw_room_hatches(state):
    _set_layer("JIG_HATCHES")
    rooms = state.get("rooms", {}); bays = state.get("bays", {})
    for rid, rm in rooms.items():
        hi = rm.get("hatch_image","none")
        if hi == "none": continue
        rtype = rm.get("type","bay"); src = rm.get("source_bay")
        hs = rm.get("hatch_scale",1.0); hr = rm.get("hatch_rotation",0.0)
        boundary_id = None
        if rtype == "bay" and src and src in bays:
            bay = bays[src]; gt = bay.get("grid_type","rectangular")
            ox, oy = bay["origin"]; rot = bay["rotation_deg"]
            if gt == "rectangular":
                cx, cy = _get_spacing_arrays(bay)
                corners = [(0,0),(cx[-1],0),(cx[-1],cy[-1]),(0,cy[-1]),(0,0)]
                boundary_id = _add_polyline([_local_to_world(lx,ly,(ox,oy),rot) for lx,ly in corners])
            else:
                outer = bay.get("rings",4) * bay.get("ring_spacing",20)
                boundary_id = _add_circle(ox, oy, outer)
        elif rtype == "void" and src and src in bays:
            bay = bays[src]; vc = bay["void_center"]; vs = bay["void_size"]
            if bay.get("void_shape","rectangle") == "circle":
                boundary_id = _add_circle(vc[0], vc[1], vs[0]/2.0)
            else:
                x0 = vc[0]-vs[0]/2.0; y0 = vc[1]-vs[1]/2.0
                boundary_id = _add_rect(x0, y0, x0+vs[0], y0+vs[1])
        elif rtype == "landscape":
            site = state["site"]; ox, oy = site["origin"]
            boundary_id = _add_rect(ox, oy, ox+site["width"], oy+site["height"])
        if boundary_id is None: continue
        base = os.path.splitext(hi)[0].lower()
        pattern = HATCH_MAP.get(base, "Hatch1")
        _add_hatch(boundary_id, pattern, hs, hr)

# ══════════════════════════════════════════════════════════
# DRAW: GRID LINES
# ══════════════════════════════════════════════════════════

def _draw_bays(state):
    _set_layer("JIG_BAYS")
    sorted_bays = sorted(state["bays"].items(), key=lambda x: x[1].get("z_order",0))
    for name, bay in sorted_bays:
        gt = bay.get("grid_type","rectangular")
        ox, oy = bay["origin"]; rot = bay["rotation_deg"]
        if gt == "radial":
            nr = bay.get("rings",4); rs_val = bay.get("ring_spacing",20)
            na = bay.get("arms",8); arc = bay.get("arc_deg",360)
            arc_start = bay.get("arc_start_deg",0)
            for ring in range(1, nr+1):
                r = ring * rs_val
                if arc >= 360: _add_circle(ox, oy, r)
                else: _add_polyline(_arc_points(ox, oy, r, arc_start, arc_start+arc, 48))
            outer = nr * rs_val
            for arm in range(na):
                angle = arc_start + arc * arm / na
                a = math.radians(angle)
                _add_line((ox,oy,0), (ox+outer*math.cos(a), oy+outer*math.sin(a), 0))
            if arc < 360:
                a = math.radians(arc_start + arc)
                _add_line((ox,oy,0), (ox+outer*math.cos(a), oy+outer*math.sin(a), 0))
        else:
            cx, cy = _get_spacing_arrays(bay)
            for y_val in cy:
                _add_line(_local_to_world(cx[0],y_val,(ox,oy),rot),
                          _local_to_world(cx[-1],y_val,(ox,oy),rot))
            for x_val in cx:
                _add_line(_local_to_world(x_val,cy[0],(ox,oy),rot),
                          _local_to_world(x_val,cy[-1],(ox,oy),rot))

# ══════════════════════════════════════════════════════════
# DRAW: COLUMNS
# ══════════════════════════════════════════════════════════

def _draw_columns(state):
    _set_layer("JIG_COLUMNS")
    cs = _s(state, "column_size", 1.5)
    half = cs / 2.0
    for name, bay in state["bays"].items():
        gt = bay.get("grid_type","rectangular")
        ox, oy = bay["origin"]; rot = bay["rotation_deg"]
        if gt == "rectangular":
            cx, cy = _get_spacing_arrays(bay)
            for x_val in cx:
                for y_val in cy:
                    wx, wy, _ = _local_to_world(x_val, y_val, (ox,oy), rot)
                    _add_rect(wx-half, wy-half, wx+half, wy+half)
        else:
            _add_rect(ox-half, oy-half, ox+half, oy+half)
            nr = bay.get("rings",4); rs_val = bay.get("ring_spacing",20)
            na = bay.get("arms",8); arc = bay.get("arc_deg",360)
            arc_start = bay.get("arc_start_deg",0)
            for ring in range(1, nr+1):
                r = ring * rs_val
                for arm in range(na):
                    angle = arc_start + arc * arm / na
                    a = math.radians(angle)
                    cx_pt = ox + r*math.cos(a); cy_pt = oy + r*math.sin(a)
                    _add_rect(cx_pt-half, cy_pt-half, cx_pt+half, cy_pt+half)

# ══════════════════════════════════════════════════════════
# DRAW: WALLS + APERTURE CUTOUTS
# ══════════════════════════════════════════════════════════

def _calc_wall_segments(wall_len, apertures):
    """Return solid wall segments as (start, end) pairs, skipping apertures."""
    if not apertures: return [(0.0, wall_len)]
    segments = []; pos = 0.0
    for ap in apertures:
        cn = ap.get("corner",0); wd = ap.get("width",3)
        if cn > pos: segments.append((pos, cn))
        pos = cn + wd
    if pos < wall_len: segments.append((pos, wall_len))
    return segments

def _draw_wall_line(state, seg_start, seg_end, fixed_val, axis, half_t, ox, oy, rot):
    """Draw a pair of offset wall lines for one solid segment."""
    if axis == "x":
        _add_line(_local_to_world(seg_start, fixed_val-half_t, (ox,oy), rot),
                  _local_to_world(seg_end,   fixed_val-half_t, (ox,oy), rot))
        _add_line(_local_to_world(seg_start, fixed_val+half_t, (ox,oy), rot),
                  _local_to_world(seg_end,   fixed_val+half_t, (ox,oy), rot))
    else:
        _add_line(_local_to_world(fixed_val-half_t, seg_start, (ox,oy), rot),
                  _local_to_world(fixed_val-half_t, seg_end,   (ox,oy), rot))
        _add_line(_local_to_world(fixed_val+half_t, seg_start, (ox,oy), rot),
                  _local_to_world(fixed_val+half_t, seg_end,   (ox,oy), rot))

def _draw_plan_layout(state):
    _set_layer("JIG_PLAN")
    for name, bay in state["bays"].items():
        if bay.get("grid_type","rectangular") != "rectangular": continue
        w = bay.get("walls",{})
        if not w.get("enabled"): continue
        t = w.get("thickness",0.5); half_t = t/2.0
        ox, oy = bay["origin"]; rot = bay["rotation_deg"]
        cx, cy = _get_spacing_arrays(bay)
        aps = bay.get("apertures",[])
        # Horizontal walls (x-axis gridlines)
        for j, y_val in enumerate(cy):
            wall_aps = sorted([a for a in aps if a.get("axis")=="x" and a.get("gridline")==j],
                              key=lambda a: a.get("corner",0))
            for s, e in _calc_wall_segments(cx[-1], wall_aps):
                _draw_wall_line(state, s, e, y_val, "x", half_t, ox, oy, rot)
            # End caps at each aperture edge
            for ap in wall_aps:
                cn = ap.get("corner",0); wd = ap.get("width",3)
                for x_pos in [cn, cn+wd]:
                    _add_line(_local_to_world(x_pos, y_val-half_t, (ox,oy), rot),
                              _local_to_world(x_pos, y_val+half_t, (ox,oy), rot))
        # Vertical walls (y-axis gridlines)
        for i, x_val in enumerate(cx):
            wall_aps = sorted([a for a in aps if a.get("axis")=="y" and a.get("gridline")==i],
                              key=lambda a: a.get("corner",0))
            for s, e in _calc_wall_segments(cy[-1], wall_aps):
                _draw_wall_line(state, s, e, x_val, "y", half_t, ox, oy, rot)
            for ap in wall_aps:
                cn = ap.get("corner",0); wd = ap.get("width",3)
                for y_pos in [cn, cn+wd]:
                    _add_line(_local_to_world(x_val-half_t, y_pos, (ox,oy), rot),
                              _local_to_world(x_val+half_t, y_pos, (ox,oy), rot))

# ══════════════════════════════════════════════════════════
# APERTURE SYMBOL DRAWING
# ══════════════════════════════════════════════════════════

def _draw_door_symbol(ap, bay, ox, oy, rot, cx, cy, wd, arc_n):
    axis = ap.get("axis","x"); gl = ap.get("gridline",0)
    cn = ap.get("corner",0); hinge_pos = ap.get("hinge","start")
    swing_dir = ap.get("swing","positive")
    swing_sign = 1 if swing_dir == "positive" else -1
    if axis == "x":
        y_val = cy[gl] if gl < len(cy) else cy[-1]
        hx = cn if hinge_pos == "start" else cn + wd
        hy = y_val
        if hinge_pos == "start": start_ang, end_ang = 0, 90*swing_sign
        else: start_ang, end_ang = 180, 180+90*swing_sign
    else:
        x_val = cx[gl] if gl < len(cx) else cx[-1]
        hx = x_val; hy = cn if hinge_pos == "start" else cn + wd
        if hinge_pos == "start": start_ang, end_ang = 90, 90+90*swing_sign
        else: start_ang, end_ang = 270, 270+90*swing_sign
    a0 = min(start_ang, end_ang); a1 = max(start_ang, end_ang)
    arc_pts = []
    for k in range(arc_n + 1):
        ang = math.radians(a0 + (a1-a0)*k/arc_n)
        arc_pts.append(_local_to_world(hx+wd*math.cos(ang), hy+wd*math.sin(ang), (ox,oy), rot))
    _add_polyline(arc_pts)
    leaf_ang = math.radians(end_ang)
    _add_line(_local_to_world(hx, hy, (ox,oy), rot),
              _local_to_world(hx+wd*math.cos(leaf_ang), hy+wd*math.sin(leaf_ang), (ox,oy), rot))

def _draw_window_symbol(ap, bay, ox, oy, rot, cx, cy, wd):
    axis = ap.get("axis","x"); gl = ap.get("gridline",0); cn = ap.get("corner",0)
    if axis == "x":
        y_val = cy[gl] if gl < len(cy) else cy[-1]
        _add_line(_local_to_world(cn, y_val, (ox,oy), rot),
                  _local_to_world(cn+wd, y_val, (ox,oy), rot))
    else:
        x_val = cx[gl] if gl < len(cx) else cx[-1]
        _add_line(_local_to_world(x_val, cn, (ox,oy), rot),
                  _local_to_world(x_val, cn+wd, (ox,oy), rot))

def _draw_portal_symbol(ap, bay, ox, oy, rot, cx, cy, wd):
    axis = ap.get("axis","x"); gl = ap.get("gridline",0)
    cn = ap.get("corner",0); t = bay.get("walls",{}).get("thickness",0.5)
    mark = t * 1.5
    if axis == "x":
        y_val = cy[gl] if gl < len(cy) else cy[-1]
        _add_line(_local_to_world(cn,    y_val-mark,(ox,oy),rot),
                  _local_to_world(cn,    y_val+mark,(ox,oy),rot))
        _add_line(_local_to_world(cn+wd, y_val-mark,(ox,oy),rot),
                  _local_to_world(cn+wd, y_val+mark,(ox,oy),rot))
    else:
        x_val = cx[gl] if gl < len(cx) else cx[-1]
        _add_line(_local_to_world(x_val-mark, cn,   (ox,oy),rot),
                  _local_to_world(x_val+mark, cn,   (ox,oy),rot))
        _add_line(_local_to_world(x_val-mark, cn+wd,(ox,oy),rot),
                  _local_to_world(x_val+mark, cn+wd,(ox,oy),rot))

# ══════════════════════════════════════════════════════════
# DRAW: BLOCK INSERTIONS (aperture symbols + room labels)
# ══════════════════════════════════════════════════════════

def _draw_block_insertions(state):
    _set_layer("JIG_BLOCKS")
    blocks = state.get("blocks",{})
    arc_n = int(_s(state, "arc_segments", 16))
    for name, bay in state["bays"].items():
        if bay.get("grid_type","rectangular") != "rectangular": continue
        ox, oy = bay["origin"]; rot = bay["rotation_deg"]
        cx, cy = _get_spacing_arrays(bay)
        for ap in bay.get("apertures",[]):
            atype = ap.get("type","door"); wd = ap.get("width",3)
            bk = blocks.get(atype,{})
            if atype == "door":     _draw_door_symbol(ap,bay,ox,oy,rot,cx,cy,wd,arc_n)
            elif atype == "window": _draw_window_symbol(ap,bay,ox,oy,rot,cx,cy,wd)
            elif atype == "portal": _draw_portal_symbol(ap,bay,ox,oy,rot,cx,cy,wd)
            if bk.get("show_label",True):
                axis = ap.get("axis","x"); gl = ap.get("gridline",0)
                cn = ap.get("corner",0)
                prefix = bk.get("label_prefix",atype[0].upper())
                aid = ap.get("id",""); num = "".join(c for c in aid if c.isdigit()) or aid
                lh = bk.get("label_height",1.5); t = bay.get("walls",{}).get("thickness",0.5)
                label_offset = t + lh * 0.5
                if axis == "x":
                    y_val = cy[gl] if gl < len(cy) else cy[-1]
                    _add_text(f"{prefix}{num}",
                              _local_to_world(cn+wd/2, y_val+label_offset, (ox,oy), rot), lh)
                else:
                    x_val = cx[gl] if gl < len(cx) else cx[-1]
                    _add_text(f"{prefix}{num}",
                              _local_to_world(x_val+label_offset, cn+wd/2, (ox,oy), rot), lh)
    # Room labels
    rooms = state.get("rooms",{}); room_bk = blocks.get("room",{})
    for rid, rm in rooms.items():
        if not room_bk.get("show_label",True): continue
        label = rm.get("label","")
        if not label: continue
        lh = room_bk.get("label_height",3.0); bays = state.get("bays",{})
        rtype = rm.get("type","bay"); src = rm.get("source_bay")
        if rtype == "bay" and src and src in bays:
            bay = bays[src]; ox, oy = bay["origin"]; rot = bay["rotation_deg"]
            if bay.get("grid_type","rectangular") == "rectangular":
                cxs, cys = _get_spacing_arrays(bay)
                pt = _local_to_world(cxs[-1]/2, cys[-1]/2, (ox,oy), rot)
            else: pt = (ox, oy, 0)
            _add_text(label, pt, lh)
        elif rtype == "void" and src and src in bays:
            vc = bays[src]["void_center"]
            _add_text(label, (vc[0], vc[1], 0), lh*0.8)
        elif rtype == "landscape":
            site = state["site"]
            _add_text(label, (site["origin"][0]+5, site["origin"][1]+5, 0), lh*0.6)

# ══════════════════════════════════════════════════════════
# DRAW: CORRIDORS
# ══════════════════════════════════════════════════════════

def _draw_corridors(state):
    _set_layer("JIG_CORRIDOR")
    dash_len = _s(state, "corridor_dash_len", 3.0)
    gap_len  = _s(state, "corridor_gap_len", 2.0)
    for name, bay in state["bays"].items():
        cor = bay.get("corridor",{})
        if not cor.get("enabled") or bay.get("grid_type","rectangular") != "rectangular":
            continue
        ox, oy = bay["origin"]; rot = bay["rotation_deg"]
        cx, cy = _get_spacing_arrays(bay)
        axis = cor.get("axis","x"); pos = cor.get("position",1)
        half_w = cor.get("width",8.0) / 2.0
        if axis == "x":
            if pos < 0 or pos >= len(cy): continue
            y_center = cy[pos]; x_s = cx[0]; x_e = cx[-1]
            y_top = y_center+half_w; y_bot = y_center-half_w
            _add_line(_local_to_world(x_s,y_top,(ox,oy),rot), _local_to_world(x_e,y_top,(ox,oy),rot))
            _add_line(_local_to_world(x_s,y_bot,(ox,oy),rot), _local_to_world(x_e,y_bot,(ox,oy),rot))
            _add_dashed_line(_local_to_world(x_s,y_center,(ox,oy),rot),
                             _local_to_world(x_e,y_center,(ox,oy),rot), dash_len, gap_len)
            ht = cor.get("hatch","none")
            if ht not in ("none",""):
                boundary = _add_polyline([
                    _local_to_world(x_s,y_bot,(ox,oy),rot), _local_to_world(x_e,y_bot,(ox,oy),rot),
                    _local_to_world(x_e,y_top,(ox,oy),rot), _local_to_world(x_s,y_top,(ox,oy),rot),
                    _local_to_world(x_s,y_bot,(ox,oy),rot)])
                if boundary: _add_hatch(boundary, ht, cor.get("hatch_scale",4.0))
        else:
            if pos < 0 or pos >= len(cx): continue
            x_center = cx[pos]; y_s = cy[0]; y_e = cy[-1]
            x_l = x_center-half_w; x_r = x_center+half_w
            _add_line(_local_to_world(x_l,y_s,(ox,oy),rot), _local_to_world(x_l,y_e,(ox,oy),rot))
            _add_line(_local_to_world(x_r,y_s,(ox,oy),rot), _local_to_world(x_r,y_e,(ox,oy),rot))
            _add_dashed_line(_local_to_world(x_center,y_s,(ox,oy),rot),
                             _local_to_world(x_center,y_e,(ox,oy),rot), dash_len, gap_len)
            ht = cor.get("hatch","none")
            if ht not in ("none",""):
                boundary = _add_polyline([
                    _local_to_world(x_l,y_s,(ox,oy),rot), _local_to_world(x_r,y_s,(ox,oy),rot),
                    _local_to_world(x_r,y_e,(ox,oy),rot), _local_to_world(x_l,y_e,(ox,oy),rot),
                    _local_to_world(x_l,y_s,(ox,oy),rot)])
                if boundary: _add_hatch(boundary, ht, cor.get("hatch_scale",4.0))

# ══════════════════════════════════════════════════════════
# DRAW: VOIDS
# ══════════════════════════════════════════════════════════

def _draw_voids(state):
    _set_layer("JIG_VOIDS")
    for name, bay in state["bays"].items():
        vc = bay["void_center"]; vs = bay["void_size"]
        if bay.get("void_shape","rectangle") == "circle":
            _add_circle(vc[0], vc[1], vs[0]/2.0)
        else:
            x0 = vc[0]-vs[0]/2.0; y0 = vc[1]-vs[1]/2.0
            _add_rect(x0, y0, x0+vs[0], y0+vs[1])

# ══════════════════════════════════════════════════════════
# DRAW: LABELS
# ══════════════════════════════════════════════════════════

def _draw_labels(state):
    _set_layer("JIG_LABELS")
    txt_h = _s(state, "label_text_height", 0.3)
    brl_h = _s(state, "braille_text_height", 0.5)
    label_off = _s(state, "label_offset", 3.0)
    for name, bay in state["bays"].items():
        gt = bay.get("grid_type","rectangular"); ox, oy = bay["origin"]
        if gt == "rectangular":
            cx_arr, cy_arr = _get_spacing_arrays(bay); rot = bay["rotation_deg"]
            label_pt = _local_to_world(cx_arr[-1]/2, cy_arr[-1]+label_off, (ox,oy), rot)
            braille_pt = _local_to_world(cx_arr[-1]/2, cy_arr[-1]+label_off+brl_h*1.5, (ox,oy), rot)
        else:
            outer = bay.get("rings",4)*bay.get("ring_spacing",20)
            label_pt = (ox, oy+outer+label_off, 0)
            braille_pt = (ox, oy+outer+label_off+brl_h*1.5, 0)
        label = bay.get("label", f"Bay {name}"); braille = bay.get("braille","")
        if label:  _add_text(label, label_pt, txt_h)
        if braille: _add_text(braille, braille_pt, brl_h)

# ══════════════════════════════════════════════════════════
# DRAW: CELL ROOMS
# ══════════════════════════════════════════════════════════

def _draw_cell_rooms(state):
    """Draw room boundaries, labels, hatches, and areas for cell subdivisions."""
    _set_layer("JIG_ROOMS")
    txt_h = _s(state, "label_text_height", 0.3)
    for bay_name, bay in state["bays"].items():
        cells = bay.get("cells")
        if not cells or bay.get("grid_type","rectangular") != "rectangular":
            continue
        ox, oy = bay["origin"]; rot = bay["rotation_deg"]
        cx, cy = _get_spacing_arrays(bay)
        nx, ny = bay["bays"]
        # Build lookup: (c,r) -> room name
        cell_names = {}
        for key, cl in cells.items():
            parts = key.split(",")
            if len(parts) == 2:
                c, r = int(parts[0]), int(parts[1])
                cell_names[(c, r)] = cl.get("name", "")
        # Group by room name
        rooms = {}
        for (c, r), name in cell_names.items():
            if not name: continue
            if name not in rooms:
                rooms[name] = {"cells": [], "label": "", "braille": "",
                               "hatch": "none", "hatch_scale": 1.0,
                               "hatch_rotation": 0.0, "area": 0.0}
            rooms[name]["cells"].append((c, r))
            cl = cells[f"{c},{r}"]
            cell_area = (cx[c+1] - cx[c]) * (cy[r+1] - cy[r])
            rooms[name]["area"] += cell_area
            if cl.get("label") and not rooms[name]["label"]:
                rooms[name]["label"] = cl["label"]
            if cl.get("braille") and not rooms[name]["braille"]:
                rooms[name]["braille"] = cl["braille"]
            if cl.get("hatch","none") != "none" and rooms[name]["hatch"] == "none":
                rooms[name]["hatch"] = cl["hatch"]
                rooms[name]["hatch_scale"] = cl.get("hatch_scale", 1.0)
                rooms[name]["hatch_rotation"] = cl.get("hatch_rotation", 0.0)
        if not rooms: continue
        for rname, rd in rooms.items():
            room_set = set(rd["cells"])
            # Draw boundary edges where adjacent cell differs
            for c, r in rd["cells"]:
                x0, x1 = cx[c], cx[c+1]
                y0, y1 = cy[r], cy[r+1]
                # Left
                if c == 0 or (c-1, r) not in room_set:
                    _add_line(_local_to_world(x0,y0,(ox,oy),rot),
                              _local_to_world(x0,y1,(ox,oy),rot))
                # Right
                if c == nx-1 or (c+1, r) not in room_set:
                    _add_line(_local_to_world(x1,y0,(ox,oy),rot),
                              _local_to_world(x1,y1,(ox,oy),rot))
                # Bottom
                if r == 0 or (c, r-1) not in room_set:
                    _add_line(_local_to_world(x0,y0,(ox,oy),rot),
                              _local_to_world(x1,y0,(ox,oy),rot))
                # Top
                if r == ny-1 or (c, r+1) not in room_set:
                    _add_line(_local_to_world(x0,y1,(ox,oy),rot),
                              _local_to_world(x1,y1,(ox,oy),rot))
                # Hatch each cell (they tile seamlessly)
                cl = cells.get(f"{c},{r}", {})
                ht = cl.get("hatch", rd["hatch"])
                hs = cl.get("hatch_scale", rd["hatch_scale"])
                hr = cl.get("hatch_rotation", rd["hatch_rotation"])
                if ht not in ("none", ""):
                    base = os.path.splitext(ht)[0].lower()
                    pattern = HATCH_MAP.get(base, "Hatch1")
                    boundary = _add_polyline([
                        _local_to_world(x0,y0,(ox,oy),rot),
                        _local_to_world(x1,y0,(ox,oy),rot),
                        _local_to_world(x1,y1,(ox,oy),rot),
                        _local_to_world(x0,y1,(ox,oy),rot),
                        _local_to_world(x0,y0,(ox,oy),rot)])
                    if boundary:
                        _add_hatch(boundary, pattern, hs, hr)
            # Label at centroid of all cells in the room
            label = rd["label"] or rname
            n = len(rd["cells"])
            sum_x = sum((cx[c] + cx[c+1]) / 2.0 for c, r in rd["cells"])
            sum_y = sum((cy[r] + cy[r+1]) / 2.0 for c, r in rd["cells"])
            ctr = _local_to_world(sum_x/n, sum_y/n, (ox,oy), rot)
            _add_text(label, ctr, txt_h * 6)
            # Area text below label
            area = rd["area"]
            area_txt = f"{area:,.0f} sf"
            ctr_below = _local_to_world(sum_x/n, sum_y/n - txt_h*8, (ox,oy), rot)
            _add_text(area_txt, ctr_below, txt_h * 4)
            # Braille below area
            brl = rd.get("braille","")
            if brl:
                brl_pt = _local_to_world(sum_x/n, sum_y/n - txt_h*14, (ox,oy), rot)
                _add_text(brl, brl_pt, _s(state, "braille_text_height", 0.5))

# ══════════════════════════════════════════════════════════
# DRAW: LEGEND (Braille + English key)
# ══════════════════════════════════════════════════════════

def _draw_legend(state):
    leg = state.get("legend", {})
    if not leg.get("enabled", False): return
    _set_layer("JIG_LEGEND")

    site = state["site"]; sox, soy = site["origin"]
    sw, sh = site["width"], site["height"]
    lw = leg.get("width", 40.0)
    pad = leg.get("padding", 3.0)
    row_h = leg.get("row_height", 7.0)
    swatch = leg.get("swatch_size", 5.0)
    txt_h = leg.get("text_height", 2.0)
    brl_h = leg.get("braille_height", 2.5)
    show_braille = leg.get("show_braille", True)
    show_hatches = leg.get("show_hatches", True)
    show_apertures = leg.get("show_apertures", True)

    rooms = state.get("rooms", {}); blocks = state.get("blocks", {})
    hatched_rooms = {rid: rm for rid, rm in rooms.items()
                     if rm.get("hatch_image","none") != "none"} if show_hatches else {}
    ap_types = []
    if show_apertures:
        for bt in ("door","window","portal"):
            if bt in blocks: ap_types.append(bt)
    n_rows = len(hatched_rooms) + len(ap_types)
    if n_rows == 0: return

    total_h = pad * 2 + (1 + n_rows) * row_h

    pos = leg.get("position", "bottom-right")
    if pos == "bottom-right":   lox = sox + sw + pad * 2;  loy = soy
    elif pos == "bottom-left":  lox = sox - lw - pad * 2;  loy = soy
    elif pos == "top-right":    lox = sox + sw + pad * 2;  loy = soy + sh - total_h
    elif pos == "top-left":     lox = sox - lw - pad * 2;  loy = soy + sh - total_h
    elif pos == "custom":       lox, loy = leg.get("custom_origin", [0, 0])
    else:                       lox = sox + sw + pad * 2;  loy = soy

    _add_rect(lox, loy, lox + lw, loy + total_h)

    cursor_y = loy + total_h - pad
    title = leg.get("title", "Legend")
    _add_text(title, (lox + pad, cursor_y - txt_h, 0), txt_h * 1.3)
    if show_braille and leg.get("title_braille"):
        _add_text(leg["title_braille"],
                  (lox + pad + len(title) * txt_h * 0.7, cursor_y - brl_h, 0), brl_h)
    cursor_y -= row_h

    for rid in sorted(hatched_rooms):
        rm = hatched_rooms[rid]
        sx0 = lox + pad; sy0 = cursor_y - swatch
        swatch_id = _add_rect(sx0, sy0, sx0 + swatch, cursor_y)
        if swatch_id:
            hi = rm.get("hatch_image","none")
            base = os.path.splitext(hi)[0].lower()
            pattern = HATCH_MAP.get(base, "Hatch1")
            _add_hatch(swatch_id, pattern,
                       rm.get("hatch_scale",1.0), rm.get("hatch_rotation",0.0))
        label = rm.get("label", rid)
        _add_text(label, (sx0 + swatch + pad, cursor_y - txt_h * 1.2, 0), txt_h)
        if show_braille:
            braille = rm.get("braille", "")
            if braille:
                _add_text(braille,
                          (sx0 + swatch + pad, cursor_y - txt_h * 1.2 - brl_h * 1.2, 0), brl_h)
        cursor_y -= row_h

    for bt in ap_types:
        bk = blocks[bt]
        prefix = bk.get("label_prefix", bt[0].upper())
        sx0 = lox + pad; sy0 = cursor_y - swatch
        mid_y = sy0 + swatch / 2.0
        if bt == "door":
            arc_pts = _arc_points(sx0, sy0, swatch, 0, 90, 8)
            _add_polyline(arc_pts)
            _add_line((sx0, sy0, 0), (sx0 + swatch, sy0, 0))
        elif bt == "window":
            _add_line((sx0, mid_y, 0), (sx0 + swatch, mid_y, 0))
            _add_line((sx0, mid_y - swatch*0.15, 0), (sx0, mid_y + swatch*0.15, 0))
            _add_line((sx0+swatch, mid_y-swatch*0.15, 0), (sx0+swatch, mid_y+swatch*0.15, 0))
        elif bt == "portal":
            _add_line((sx0, sy0, 0), (sx0, sy0 + swatch*0.4, 0))
            _add_line((sx0+swatch, sy0, 0), (sx0+swatch, sy0+swatch*0.4, 0))
        _add_text(f"{prefix} = {bt.title()}",
                  (sx0 + swatch + pad, cursor_y - txt_h * 1.2, 0), txt_h)
        cursor_y -= row_h

# ══════════════════════════════════════════════════════════
# DRAW: TACTILE 3D (extruded walls for 3D printing)
# ══════════════════════════════════════════════════════════

def _aperture_infill_boxes(ap, extrude_h, fixed_val, axis, half_t,
                           ox, oy, rot):
    """Create Rhino surface geometry for header and sill at an aperture.

    Doors:   header box from door height to extrude_h.
    Windows: sill box from 0 to sill height, header from sill+height to extrude_h.

    Returns list of Rhino object IDs (may be empty if not in Rhino).
    """
    ids = []
    ap_corner = ap.get("corner", 0)
    ap_width = ap.get("width", 3)
    ap_height = ap.get("height", 7)
    ap_type = ap.get("type", "door")
    sill_h = ap.get("sill", 0.0)

    if ap_type == "door":
        opening_top = ap_height
        opening_bot = 0.0
    else:
        opening_bot = sill_h
        opening_top = sill_h + ap_height

    # Header: wall above the opening
    if opening_top < extrude_h - 0.001:
        obj = _extrude_wall_box(ap_corner, ap_corner + ap_width,
                                fixed_val, axis, half_t, ox, oy, rot,
                                extrude_h - opening_top)
        if obj:
            # Move the box up to the opening_top z level
            if IN_RHINO:
                rs.MoveObject(obj, (0, 0, opening_top))
            ids.append(obj)

    # Sill: wall below the opening (windows with sill > 0)
    if opening_bot > 0.001:
        obj = _extrude_wall_box(ap_corner, ap_corner + ap_width,
                                fixed_val, axis, half_t, ox, oy, rot,
                                opening_bot)
        if obj:
            ids.append(obj)

    return ids


def _draw_tactile3d(state):
    """Build 3D geometry for tactile plan models.

    Extrudes each solid wall segment as a capped box. Aperture
    locations are left open — no extrusion where a door, window,
    or portal sits. A clipping plane at cut_height trims the tops.
    STL export only runs when auto_export is on or when the
    controller sets the _export_once flag via 'tactile3d export'.
    """
    t3 = state.get("tactile3d", {})
    if not t3.get("enabled", False): return
    if not IN_RHINO: return
    _set_layer("JIG_TACTILE3D")

    wall_height = t3.get("wall_height", 9.0)
    cut_height = t3.get("cut_height", 4.0)
    floor_thick = t3.get("floor_thickness", 0.5)
    floor_on = t3.get("floor_enabled", True)
    scale_f = t3.get("scale_factor", 1.0)
    auto_export = t3.get("auto_export", False)
    export_once = t3.get("_export_once", False)
    export_path = t3.get("export_path", "")

    # Extrude only up to the cut height
    extrude_h = min(wall_height, cut_height)
    created_ids = []

    # ── Extrude wall segments ──
    for name, bay in state["bays"].items():
        if bay.get("grid_type", "rectangular") != "rectangular": continue
        w = bay.get("walls", {})
        if not w.get("enabled"): continue
        t = w.get("thickness", 0.5); half_t = t / 2.0
        ox, oy = bay["origin"]; rot = bay["rotation_deg"]
        cx, cy = _get_spacing_arrays(bay)
        aps = bay.get("apertures", [])

        for j, y_val in enumerate(cy):
            wall_aps = sorted(
                [a for a in aps if a.get("axis")=="x" and a.get("gridline")==j],
                key=lambda a: a.get("corner", 0))
            for seg_s, seg_e in _calc_wall_segments(cx[-1], wall_aps):
                obj = _extrude_wall_box(seg_s, seg_e, y_val, "x",
                                        half_t, ox, oy, rot, extrude_h)
                if obj: created_ids.append(obj)
            # Aperture infill: headers above doors, sills + headers for windows
            for ap in wall_aps:
                for obj in _aperture_infill_boxes(ap, extrude_h, y_val, "x",
                                                   half_t, ox, oy, rot):
                    created_ids.append(obj)

        for i, x_val in enumerate(cx):
            wall_aps = sorted(
                [a for a in aps if a.get("axis")=="y" and a.get("gridline")==i],
                key=lambda a: a.get("corner", 0))
            for seg_s, seg_e in _calc_wall_segments(cy[-1], wall_aps):
                obj = _extrude_wall_box(seg_s, seg_e, x_val, "y",
                                        half_t, ox, oy, rot, extrude_h)
                if obj: created_ids.append(obj)
            # Aperture infill: headers above doors, sills + headers for windows
            for ap in wall_aps:
                for obj in _aperture_infill_boxes(ap, extrude_h, x_val, "y",
                                                   half_t, ox, oy, rot):
                    created_ids.append(obj)

    # ── Floor slab ──
    if floor_on:
        slab = _create_floor_slab(state, floor_thick)
        if slab: created_ids.append(slab)

    # ── Clipping plane ──
    _add_clipping_plane(state, cut_height)

    # ── Scale ──
    if scale_f != 1.0 and created_ids:
        origin_pt = state["site"]["origin"]
        rs.ScaleObjects(created_ids, (origin_pt[0], origin_pt[1], 0),
                        (scale_f, scale_f, scale_f))

    # ── Export only when explicitly requested ──
    should_export = (auto_export or export_once) and export_path and created_ids
    if should_export:
        _export_stl(created_ids, export_path)
    # Clear the one-shot flag (watcher doesn't write JSON, but
    # we clear it from the in-memory state so it doesn't re-fire
    # on the next poll cycle if the file hasn't changed)
    if export_once:
        t3["_export_once"] = False


def _extrude_wall_box(seg_start, seg_end, fixed_val, axis, half_t,
                      ox, oy, rot, height):
    """Extrude one wall segment as a capped 3D box."""
    if not IN_RHINO: return None
    if seg_end - seg_start < 0.001: return None  # skip degenerate segments
    if axis == "x":
        corners = [
            _local_to_world(seg_start, fixed_val - half_t, (ox, oy), rot),
            _local_to_world(seg_end,   fixed_val - half_t, (ox, oy), rot),
            _local_to_world(seg_end,   fixed_val + half_t, (ox, oy), rot),
            _local_to_world(seg_start, fixed_val + half_t, (ox, oy), rot),
        ]
    else:
        corners = [
            _local_to_world(fixed_val - half_t, seg_start, (ox, oy), rot),
            _local_to_world(fixed_val + half_t, seg_start, (ox, oy), rot),
            _local_to_world(fixed_val + half_t, seg_end,   (ox, oy), rot),
            _local_to_world(fixed_val - half_t, seg_end,   (ox, oy), rot),
        ]
    corners.append(corners[0])
    profile = rs.AddPolyline(corners)
    if not profile: return None
    srf = rs.AddPlanarSrf(profile)
    if not srf:
        rs.DeleteObject(profile)
        return None
    srf_id = srf[0]
    path = rs.AddLine((0, 0, 0), (0, 0, height))
    brep = rs.ExtrudeSurface(srf_id, path, True)
    rs.DeleteObject(profile)
    rs.DeleteObject(srf_id)
    rs.DeleteObject(path)
    if brep:
        rs.CapPlanarHoles(brep)
        return brep
    return None


def _create_floor_slab(state, thickness):
    """Create a floor slab from z=-thickness to z=0 spanning the site."""
    if not IN_RHINO: return None
    site = state["site"]
    sox, soy = site["origin"]; sw, sh = site["width"], site["height"]
    corners = [
        (sox, soy, -thickness), (sox+sw, soy, -thickness),
        (sox+sw, soy+sh, -thickness), (sox, soy+sh, -thickness),
        (sox, soy, -thickness),
    ]
    profile = rs.AddPolyline(corners)
    if not profile: return None
    srf = rs.AddPlanarSrf(profile)
    if not srf:
        rs.DeleteObject(profile)
        return None
    srf_id = srf[0]
    path = rs.AddLine((0, 0, 0), (0, 0, thickness))
    brep = rs.ExtrudeSurface(srf_id, path, True)
    rs.DeleteObject(profile)
    rs.DeleteObject(srf_id)
    rs.DeleteObject(path)
    if brep:
        rs.CapPlanarHoles(brep)
        return brep
    return None


def _add_clipping_plane(state, cut_height):
    """Place a horizontal clipping plane at the given height."""
    if not IN_RHINO: return None
    site = state["site"]
    sox, soy = site["origin"]; sw, sh = site["width"], site["height"]
    center = Rhino.Geometry.Point3d(sox + sw/2.0, soy + sh/2.0, cut_height)
    plane = Rhino.Geometry.Plane(center, Rhino.Geometry.Vector3d.ZAxis)
    extent = max(sw, sh) * 2.0
    try:
        return sc.doc.Objects.AddClippingPlane(
            plane, extent, extent, sc.doc.Views.ActiveView.ActiveViewportID)
    except Exception as e:
        print(f"[PLJ TACTILE3D] Clipping plane: {e}")
        return None


def _export_stl(obj_ids, filepath):
    """Select the 3D objects and export as STL."""
    if not IN_RHINO: return
    try:
        rs.UnselectAllObjects()
        rs.SelectObjects(obj_ids)
        rs.Command(f'-Export "{filepath}" Enter', False)
        rs.UnselectAllObjects()
        print(f"[PLJ TACTILE3D] Exported {len(obj_ids)} objects to {filepath}")
    except Exception as e:
        print(f"[PLJ TACTILE3D] Export: {e}")

# ══════════════════════════════════════════════════════════
# MASTER REDRAW
# ══════════════════════════════════════════════════════════

def redraw(state):
    if not IN_RHINO:
        print("[DRY RUN] Would redraw:", list(state["bays"].keys()))
        return
    rs.EnableRedraw(False)
    try:
        _ensure_layers()
        _clear_all()
        _draw_site(state)
        _draw_background_masks(state)
        _draw_room_hatches(state)
        _draw_bays(state)
        _draw_columns(state)
        _draw_plan_layout(state)
        _draw_block_insertions(state)
        _draw_corridors(state)
        _draw_voids(state)
        _draw_labels(state)
        _draw_cell_rooms(state)
        _draw_legend(state)
        _draw_tactile3d(state)
        rs.ZoomExtents()
    finally:
        rs.EnableRedraw(True)
    t3 = state.get("tactile3d", {})
    t3_s = f"  tactile3D ON (cut {t3.get('cut_height',4.0)}ft)" if t3.get("enabled") else ""
    leg_s = "  legend ON" if state.get("legend",{}).get("enabled") else ""
    total_aps = sum(len(b.get("apertures",[])) for b in state["bays"].values())
    print(f"[PLJ] Redrawn: {len(state['bays'])} bays, {total_aps} apertures, "
          f"{len(state.get('rooms',{}))} rooms{leg_s}{t3_s}")

# ══════════════════════════════════════════════════════════
# FILE WATCHER
# ══════════════════════════════════════════════════════════

def watch_loop():
    print(f"[PLJ] Watching: {STATE_FILE}")
    print(f"[PLJ] Poll interval: {POLL_SEC}s")
    last_mtime = 0
    while True:
        try:
            mt = _state_mtime()
            if mt > last_mtime:
                last_mtime = mt
                state = _load_state()
                if state: redraw(state)
            time.sleep(POLL_SEC)
        except KeyboardInterrupt:
            print("[PLJ] Watcher stopped."); break
        except Exception as e:
            print(f"[PLJ] Error: {e}"); time.sleep(2)

def start_watcher():
    t = threading.Thread(target=watch_loop, daemon=True)
    t.start()
    print("[PLJ] Background watcher started.")
    return t

if __name__ == "__main__":
    state = _load_state()
    if state: redraw(state)
    else:
        print(f"[PLJ] No state file at {STATE_FILE}")
        print("  Run controller_cli.py to generate one.")
