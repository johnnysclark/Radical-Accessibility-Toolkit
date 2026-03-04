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
import io, json, math, os, subprocess, time, threading

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
# Allow STATE_FILE to be pre-set before exec(), e.g.:
#   STATE_FILE = r"C:\path\to\controller\state.json"
#   exec(open(r"C:\path\to\rhino_watcher.py").read())
if 'STATE_FILE' not in dir() or not globals().get('STATE_FILE'):
    # Try next to the script first (flat layout)
    _candidate = os.path.join(SCRIPT_DIR, "state.json")
    # Then try the CONTROLLER project structure (tools/rhino/ -> ../../controller/)
    _project = os.path.join(SCRIPT_DIR, "..", "..", "controller", "state.json")
    if os.path.exists(_candidate):
        STATE_FILE = _candidate
    elif os.path.exists(_project):
        STATE_FILE = os.path.abspath(_project)
    else:
        # Default: next to script (will show helpful error later)
        STATE_FILE = _candidate
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

# ── Audio feedback ────────────────────────────────────────
# Short audio signals so a blind user knows the rebuild happened
# without needing to read the Rhino command line.
#
# AUDIO_MODE controls what plays after each rebuild:
#   "chime"  — short system beep only (fast, non-blocking)
#   "speak"  — spoken summary via Windows TTS (e.g. "2 bays, 1 door")
#   "both"   — chime then speak
#   "none"   — silent (screen reader users who read Rhino output)
AUDIO_MODE = os.environ.get("LAYOUT_JIG_AUDIO", "both")
SPEAK_RATE = int(os.environ.get("LAYOUT_JIG_SPEAK_RATE", "3"))


def _chime():
    """Play a short system beep. Non-blocking, fire-and-forget."""
    try:
        # Windows: [System.Console]::Beep(frequency_hz, duration_ms)
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command",
             "[System.Console]::Beep(880, 120)"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def _speak(text):
    """Speak text via Windows PowerShell SpeechSynthesizer.

    Non-blocking (fire-and-forget). Uses SPEAK_RATE for speed.
    """
    escaped = text.replace("'", "''")
    ps_cmd = (
        "Add-Type -AssemblyName System.Speech;"
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        "$s.Rate={0};"
        "$s.Speak('{1}')").format(SPEAK_RATE, escaped)
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def _audio_feedback(state):
    """Play audio after a successful rebuild."""
    if AUDIO_MODE == "none":
        return

    if AUDIO_MODE in ("chime", "both"):
        _chime()

    if AUDIO_MODE in ("speak", "both"):
        nbays = len(state.get("bays", {}))
        total_aps = sum(len(b.get("apertures", []))
                        for b in state.get("bays", {}).values())
        nrooms = len(state.get("rooms", {}))
        parts = []
        parts.append("{0} bay{1}".format(nbays, "" if nbays == 1 else "s"))
        if total_aps:
            parts.append("{0} aperture{1}".format(
                total_aps, "" if total_aps == 1 else "s"))
        parts.append("{0} room{1}".format(nrooms, "" if nrooms == 1 else "s"))
        _speak("Rebuilt. " + ", ".join(parts) + ".")

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
    with open(STATE_FILE, "rb") as f:
        return json.loads(f.read().decode("utf-8"))

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

    # ── Radial bay walls ──
    for name, bay in state["bays"].items():
        if bay.get("grid_type","rectangular") != "radial": continue
        w = bay.get("walls",{})
        if not w.get("enabled"): continue
        t = w.get("thickness",0.5); half_t = t/2.0
        ox, oy = bay["origin"]
        nr = bay.get("rings",4); ring_sp = bay.get("ring_spacing",20)
        na = bay.get("arms",8); arc = bay.get("arc_deg",360)
        arc_start = bay.get("arc_start_deg",0)
        arc_n = int(_s(state, "arc_segments", 16))
        outer = nr * ring_sp
        # Ring walls
        for ring_idx in range(1, nr+1):
            r = ring_idx * ring_sp
            if arc >= 360:
                _add_circle(ox, oy, r - half_t)
                _add_circle(ox, oy, r + half_t)
            else:
                _add_polyline(_arc_points(ox, oy, r - half_t, arc_start, arc_start+arc, arc_n*2))
                _add_polyline(_arc_points(ox, oy, r + half_t, arc_start, arc_start+arc, arc_n*2))
                # End caps at arc endpoints
                for ang in [arc_start, arc_start+arc]:
                    a_rad = math.radians(ang)
                    _add_line((ox+(r-half_t)*math.cos(a_rad), oy+(r-half_t)*math.sin(a_rad), 0),
                              (ox+(r+half_t)*math.cos(a_rad), oy+(r+half_t)*math.sin(a_rad), 0))
        # Arm walls
        for arm in range(na):
            angle = arc_start + arc * arm / na
            a_rad = math.radians(angle)
            perp_rad = math.radians(angle + 90)
            dx = half_t * math.cos(perp_rad)
            dy = half_t * math.sin(perp_rad)
            # Inner end at first ring (or center if no inner ring offset)
            r_inner = ring_sp  # start from first ring
            for sign in [-1, 1]:
                sx = ox + r_inner * math.cos(a_rad) + sign * dx
                sy = oy + r_inner * math.sin(a_rad) + sign * dy
                ex = ox + outer * math.cos(a_rad) + sign * dx
                ey = oy + outer * math.sin(a_rad) + sign * dy
                _add_line((sx, sy, 0), (ex, ey, 0))
        # Closing arm for partial arcs
        if arc < 360:
            angle = arc_start + arc
            a_rad = math.radians(angle)
            perp_rad = math.radians(angle + 90)
            dx = half_t * math.cos(perp_rad)
            dy = half_t * math.sin(perp_rad)
            r_inner = ring_sp
            for sign in [-1, 1]:
                sx = ox + r_inner * math.cos(a_rad) + sign * dx
                sy = oy + r_inner * math.sin(a_rad) + sign * dy
                ex = ox + outer * math.cos(a_rad) + sign * dx
                ey = oy + outer * math.sin(a_rad) + sign * dy
                _add_line((sx, sy, 0), (ex, ey, 0))

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
                    _add_text("{0}{1}".format(prefix, num),
                              _local_to_world(cn+wd/2, y_val+label_offset, (ox,oy), rot), lh)
                else:
                    x_val = cx[gl] if gl < len(cx) else cx[-1]
                    _add_text("{0}{1}".format(prefix, num),
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
        label = bay.get("label", "Bay {0}".format(name)); braille = bay.get("braille","")
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
            cl = cells["{0},{1}".format(c, r)]
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
                cl = cells.get("{0},{1}".format(c, r), {})
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
            area_txt = "{0:,.0f} sf".format(area)
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
        _add_text("{0} = {1}".format(prefix, bt.title()),
                  (sx0 + swatch + pad, cursor_y - txt_h * 1.2, 0), txt_h)
        cursor_y -= row_h

# ══════════════════════════════════════════════════════════
# DRAW: TACTILE 3D (extruded walls for 3D printing)
# ══════════════════════════════════════════════════════════

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

        for i, x_val in enumerate(cx):
            wall_aps = sorted(
                [a for a in aps if a.get("axis")=="y" and a.get("gridline")==i],
                key=lambda a: a.get("corner", 0))
            for seg_s, seg_e in _calc_wall_segments(cy[-1], wall_aps):
                obj = _extrude_wall_box(seg_s, seg_e, x_val, "y",
                                        half_t, ox, oy, rot, extrude_h)
                if obj: created_ids.append(obj)

    # ── Radial bay 3D walls ──
    for name, bay in state["bays"].items():
        if bay.get("grid_type","rectangular") != "radial": continue
        w = bay.get("walls",{})
        if not w.get("enabled"): continue
        t = w.get("thickness",0.5); half_t = t / 2.0
        ox, oy = bay["origin"]
        nr = bay.get("rings",4); ring_sp = bay.get("ring_spacing",20)
        na = bay.get("arms",8); arc = bay.get("arc_deg",360)
        arc_start = bay.get("arc_start_deg",0)
        outer = nr * ring_sp
        n_seg = 48  # segments per full circle for smooth curves
        # Ring walls as extruded arc profiles
        for ring_idx in range(1, nr+1):
            r = ring_idx * ring_sp
            # Create closed profile: inner arc, outer arc (reversed), close
            inner_pts = _arc_points(ox, oy, r - half_t, arc_start, arc_start + arc, n_seg)
            outer_pts = _arc_points(ox, oy, r + half_t, arc_start, arc_start + arc, n_seg)
            outer_pts.reverse()
            profile_pts = inner_pts + outer_pts
            profile_pts.append(profile_pts[0])  # close
            if IN_RHINO:
                profile = rs.AddPolyline(profile_pts)
                if profile:
                    brep = rs.ExtrudeCurveStraight(profile, (0,0,0), (0,0,extrude_h))
                    rs.DeleteObject(profile)
                    if brep:
                        rs.CapPlanarHoles(brep)
                        created_ids.append(brep)
        # Arm walls as extruded boxes
        for arm in range(na):
            angle = arc_start + arc * arm / na
            a_rad = math.radians(angle)
            perp_rad = math.radians(angle + 90)
            dx = half_t * math.cos(perp_rad)
            dy = half_t * math.sin(perp_rad)
            r_inner = ring_sp
            corners = [
                (ox + r_inner*math.cos(a_rad) - dx, oy + r_inner*math.sin(a_rad) - dy, 0),
                (ox + outer*math.cos(a_rad) - dx, oy + outer*math.sin(a_rad) - dy, 0),
                (ox + outer*math.cos(a_rad) + dx, oy + outer*math.sin(a_rad) + dy, 0),
                (ox + r_inner*math.cos(a_rad) + dx, oy + r_inner*math.sin(a_rad) + dy, 0),
            ]
            corners.append(corners[0])
            if IN_RHINO:
                profile = rs.AddPolyline(corners)
                if profile:
                    brep = rs.ExtrudeCurveStraight(profile, (0,0,0), (0,0,extrude_h))
                    rs.DeleteObject(profile)
                    if brep:
                        rs.CapPlanarHoles(brep)
                        created_ids.append(brep)
        # Closing arm for partial arcs
        if arc < 360:
            angle = arc_start + arc
            a_rad = math.radians(angle)
            perp_rad = math.radians(angle + 90)
            dx = half_t * math.cos(perp_rad)
            dy = half_t * math.sin(perp_rad)
            r_inner = ring_sp
            corners = [
                (ox + r_inner*math.cos(a_rad) - dx, oy + r_inner*math.sin(a_rad) - dy, 0),
                (ox + outer*math.cos(a_rad) - dx, oy + outer*math.sin(a_rad) - dy, 0),
                (ox + outer*math.cos(a_rad) + dx, oy + outer*math.sin(a_rad) + dy, 0),
                (ox + r_inner*math.cos(a_rad) + dx, oy + r_inner*math.sin(a_rad) + dy, 0),
            ]
            corners.append(corners[0])
            if IN_RHINO:
                profile = rs.AddPolyline(corners)
                if profile:
                    brep = rs.ExtrudeCurveStraight(profile, (0,0,0), (0,0,extrude_h))
                    rs.DeleteObject(profile)
                    if brep:
                        rs.CapPlanarHoles(brep)
                        created_ids.append(brep)

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

    print("[PLJ TACTILE3D] Created {0} objects.".format(len(created_ids)))
    # ── Export only when explicitly requested ──
    should_export = (auto_export or export_once) and export_path and created_ids
    if should_export:
        _export_stl(created_ids, export_path)
    # Clear the one-shot flag in memory AND in the JSON file.
    # This is the ONE exception to the "watcher never writes" rule —
    # without clearing it, the flag stays True and re-triggers on
    # every watcher restart.
    if export_once:
        t3["_export_once"] = False
        try:
            with open(STATE_FILE, "rb") as _f:
                _disk = json.loads(_f.read().decode("utf-8"))
            if "_export_once" in _disk.get("tactile3d", {}):
                _disk["tactile3d"]["_export_once"] = False
                _tmp = STATE_FILE + ".tmp"
                with open(_tmp, "wb") as _fw:
                    _fw.write(json.dumps(_disk, indent=2).encode("utf-8"))
                os.replace(_tmp, STATE_FILE)
                # Update mtime so we don't re-trigger a redraw
                _watcher_state["last_mtime"] = os.stat(STATE_FILE).st_mtime
        except Exception as _e:
            print("[PLJ] Could not clear _export_once: {0}".format(_e))


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
    if not profile:
        print("[PLJ TACTILE3D] AddPolyline failed for segment {0}..{1}".format(seg_start, seg_end))
        return None
    brep = rs.ExtrudeCurveStraight(profile, (0, 0, 0), (0, 0, height))
    rs.DeleteObject(profile)
    if not brep:
        print("[PLJ TACTILE3D] ExtrudeCurveStraight failed for segment {0}..{1}".format(seg_start, seg_end))
        return None
    rs.CapPlanarHoles(brep)
    return brep


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
        print("[PLJ TACTILE3D] Clipping plane: {0}".format(e))
        return None


def _export_stl(obj_ids, filepath):
    """Convert 3D objects to meshes and write binary STL directly.

    Writes the binary STL format from mesh vertex/face data using
    struct.pack.  No dependency on Rhino.FileIO.FileStl (which may
    not exist in all versions) and no interactive Export dialog.
    Works even when EnableRedraw is off.
    """
    if not IN_RHINO:
        return
    try:
        import System
        import struct

        # --- collect meshes from all geometry types ---
        meshes = []
        mp = Rhino.Geometry.MeshingParameters.Default
        for oid in obj_ids:
            robj = sc.doc.Objects.FindId(System.Guid(str(oid)))
            if robj is None:
                continue
            geom = robj.Geometry
            if isinstance(geom, Rhino.Geometry.Mesh):
                meshes.append(geom)
            elif isinstance(geom, Rhino.Geometry.Brep):
                ms = Rhino.Geometry.Mesh.CreateFromBrep(geom, mp)
                if ms:
                    for m in ms:
                        meshes.append(m)
            elif isinstance(geom, Rhino.Geometry.Extrusion):
                brep = geom.ToBrep()
                if brep:
                    ms = Rhino.Geometry.Mesh.CreateFromBrep(brep, mp)
                    if ms:
                        for m in ms:
                            meshes.append(m)

        if not meshes:
            print("[PLJ TACTILE3D] No meshable geometry found.")
            return

        # --- join into one mesh, triangulate ---
        joined = Rhino.Geometry.Mesh()
        for m in meshes:
            joined.Append(m)
        joined.Faces.ConvertQuadsToTriangles()
        joined.FaceNormals.ComputeFaceNormals()

        # --- ensure output directory ---
        out_dir = os.path.dirname(filepath)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # --- write binary STL ---
        tri_count = joined.Faces.Count
        verts = joined.Vertices
        fnormals = joined.FaceNormals

        f = open(filepath, "wb")
        try:
            # 80-byte header
            hdr = "Binary STL - Layout Jig"
            hdr = hdr + "\0" * (80 - len(hdr))
            f.write(hdr.encode("ascii") if hasattr(hdr, "encode") else hdr)
            # triangle count (uint32 LE)
            f.write(struct.pack("<I", tri_count))
            # each triangle: normal(3f) + v0(3f) + v1(3f) + v2(3f) + attr(H)
            for i in range(tri_count):
                face = joined.Faces[i]
                fn = fnormals[i]
                f.write(struct.pack("<fff",
                    float(fn.X), float(fn.Y), float(fn.Z)))
                for vi in [face.A, face.B, face.C]:
                    v = verts[vi]
                    f.write(struct.pack("<fff",
                        float(v.X), float(v.Y), float(v.Z)))
                f.write(struct.pack("<H", 0))
        finally:
            f.close()

        sz = os.path.getsize(filepath)
        print("[PLJ TACTILE3D] Exported {0} triangles ({1} KB) to {2}".format(
            tri_count, sz // 1024, filepath))
    except Exception as e:
        print("[PLJ TACTILE3D] Export error: {0}".format(e))

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
        steps = [
            ("site", _draw_site),
            ("backgrounds", _draw_background_masks),
            ("hatches", _draw_room_hatches),
            ("bays", _draw_bays),
            ("columns", _draw_columns),
            ("walls", _draw_plan_layout),
            ("blocks", _draw_block_insertions),
            ("corridors", _draw_corridors),
            ("voids", _draw_voids),
            ("labels", _draw_labels),
            ("rooms", _draw_cell_rooms),
            ("legend", _draw_legend),
            ("tactile3d", _draw_tactile3d),
        ]
        for step_name, step_fn in steps:
            try:
                step_fn(state)
            except Exception as e:
                print("[PLJ] WARNING: {0} failed: {1}".format(step_name, e))
        rs.ZoomExtents()
    finally:
        rs.EnableRedraw(True)
    # Cache stats on the main thread so the TCP listener never calls rs.*
    try:
        obj_total = 0
        layer_stats = {}
        for lname in LAYERS:
            if rs.IsLayer(lname):
                objs = rs.ObjectsByLayer(lname)
                n = len(objs) if objs else 0
            else:
                n = 0
            layer_stats[lname] = n
            obj_total += n
        all_objs = []
        for lname in LAYERS:
            if rs.IsLayer(lname):
                objs = rs.ObjectsByLayer(lname)
                if objs:
                    all_objs.extend(objs)
        bb = {}
        if all_objs:
            bx = rs.BoundingBox(all_objs)
            if bx and len(bx) >= 8:
                bb = {"min_x": bx[0][0], "min_y": bx[0][1], "min_z": bx[0][2],
                      "max_x": bx[6][0], "max_y": bx[6][1], "max_z": bx[6][2]}
        _cached_stats["layer_count"] = len([l for l in LAYERS if rs.IsLayer(l)])
        _cached_stats["object_count"] = obj_total
        _cached_stats["layer_stats"] = layer_stats
        _cached_stats["bounding_box"] = bb
        _cached_stats["last_rebuild"] = time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass
    t3 = state.get("tactile3d", {})
    t3_s = "  tactile3D ON (cut {0}ft)".format(t3.get("cut_height", 4.0)) if t3.get("enabled") else ""
    leg_s = "  legend ON" if state.get("legend",{}).get("enabled") else ""
    total_aps = sum(len(b.get("apertures",[])) for b in state["bays"].values())
    print("[PLJ] Redrawn: {0} bays, {1} apertures, {2} rooms{3}{4}".format(
        len(state["bays"]), total_aps, len(state.get("rooms", {})), leg_s, t3_s))
    _audio_feedback(state)

# ══════════════════════════════════════════════════════════
# TCP QUERY LISTENER (v3.0)
# ══════════════════════════════════════════════════════════
# Optional TCP server on port 1998 that answers read-only queries
# from the MCP server's rhino_client.  Port 1998 avoids conflict
# with rhinomcp (port 1999).
#
# Supported queries:
#   {"type": "ping"}                   -> {"status": "ok"}
#   {"type": "status"}                 -> layer/object counts
#   {"type": "layer_stats"}            -> per-layer object counts
#   {"type": "bounding_box"}           -> world bounding box
#   {"type": "object_count", "params": {"layer": "JIG_COLUMNS"}}
#   {"type": "run_script", "code": "import rhinoscriptsyntax as rs\n..."}
#
# All queries are READ-ONLY.  run_script blocks calls to geometry-
# modifying functions (AddLine, DeleteObject, etc.).

import socket as _socket

QUERY_PORT = 1998
QUERY_HOST = "127.0.0.1"

# Functions that modify geometry -- blocked in run_script
_BLOCKED_PREFIXES = (
    "rs.Add", "rs.Delete", "rs.Move", "rs.Rotate", "rs.Scale",
    "rs.Copy", "rs.Mirror", "rs.Transform", "rs.Offset",
    "rs.Trim", "rs.Split", "rs.Explode", "rs.Join",
    "rs.Command", "rs.Undo", "rs.Redo",
)


def _handle_query(request):
    """Process a single query dict and return a response dict.

    Runs in the listener thread.  NEVER calls rhinoscriptsyntax --
    all Rhino data is served from _cached_stats, which is populated
    on the main thread during redraw().
    """
    qtype = request.get("type", "")
    params = request.get("params", {})

    if qtype == "ping":
        return {"status": "ok"}

    if qtype == "status":
        return {"status": "ok", "result": {
            "layer_count": _cached_stats.get("layer_count", 0),
            "object_count": _cached_stats.get("object_count", 0),
            "last_rebuild": _cached_stats.get("last_rebuild", ""),
        }}

    if qtype == "layer_stats":
        return {"status": "ok", "result": _cached_stats.get("layer_stats", {})}

    if qtype == "bounding_box":
        return {"status": "ok", "result": _cached_stats.get("bounding_box", {})}

    if qtype == "object_count":
        layer = params.get("layer", "")
        if layer:
            count = _cached_stats.get("layer_stats", {}).get(layer, 0)
        else:
            count = _cached_stats.get("object_count", 0)
        return {"status": "ok", "result": {"count": count, "layer": layer or "all"}}

    if qtype == "run_script":
        code = request.get("code", "")
        if not code:
            return {"status": "error", "message": "No code provided."}
        # Block modifying calls
        for prefix in _BLOCKED_PREFIXES:
            if prefix in code:
                return {"status": "error",
                        "message": "Blocked: '{0}' is a geometry-modifying call. "
                                   "Only read-only queries are allowed.".format(prefix)}
        if not IN_RHINO:
            return {"status": "error",
                    "message": "Not running inside Rhino. Script execution unavailable."}
        try:
            # Capture stdout
            old_stdout = sys.stdout if 'sys' in dir() else None
            capture = io.StringIO()
            import sys as _sys
            _sys.stdout = capture
            try:
                exec(code)
            finally:
                _sys.stdout = old_stdout
            output = capture.getvalue()
            return {"status": "ok", "result": {"output": output}}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    return {"status": "error", "message": "Unknown query type: '{0}'".format(qtype)}


def _listener_loop():
    """TCP listener thread.  Accepts one connection at a time."""
    try:
        srv = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        srv.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
        srv.bind((QUERY_HOST, QUERY_PORT))
        srv.listen(1)
        srv.settimeout(2.0)
        print("[PLJ] TCP listener on {0}:{1}".format(QUERY_HOST, QUERY_PORT))
    except Exception as e:
        print("[PLJ] TCP listener failed to start: {0}".format(e))
        print("[PLJ] (MCP bridge will report OFFLINE -- this is fine)")
        return

    while True:
        try:
            conn, addr = srv.accept()
        except _socket.timeout:
            continue
        except Exception:
            break

        try:
            conn.settimeout(5.0)
            buf = b""
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    break
                buf += chunk
                if b"\n" in buf:
                    break

            if buf.strip():
                request = json.loads(buf.strip())
                response = _handle_query(request)
                conn.sendall(json.dumps(response).encode("utf-8") + b"\n")
        except Exception as e:
            try:
                err = json.dumps({"status": "error", "message": str(e)})
                conn.sendall(err.encode("utf-8") + b"\n")
            except Exception:
                pass
        finally:
            try:
                conn.close()
            except Exception:
                pass


def start_listener():
    """Start the TCP query listener in a background thread."""
    t = threading.Thread(target=_listener_loop)
    t.daemon = True
    t.start()
    return t


# ══════════════════════════════════════════════════════════
# FILE WATCHER (Idle-event based, safe for Rhino)
# ══════════════════════════════════════════════════════════
# The watcher hooks Rhino.RhinoApp.Idle so that file checks
# and geometry rebuilds happen on the MAIN thread.  Never call
# rhinoscriptsyntax from a background thread — it will crash.
#
# The TCP listener is the only background thread; it only reads
# Rhino state and never modifies geometry.

_watcher_state = {
    "last_mtime": 0,
    "last_check": 0,
    "running": False,
}

# Cached stats from the last redraw (main thread).
# The TCP listener reads these instead of calling rhinoscriptsyntax.
_cached_stats = {
    "layer_count": 0,
    "object_count": 0,
    "layer_stats": {},
    "bounding_box": {},
    "last_rebuild": "",
}


def _on_idle(sender, args):
    """Called on Rhino's main thread during idle moments.

    Checks file mtime at most every POLL_SEC seconds.  If the
    file changed, reloads and redraws on the main thread.
    """
    now = time.time()
    if now - _watcher_state["last_check"] < POLL_SEC:
        return
    _watcher_state["last_check"] = now
    try:
        mt = _state_mtime()
        if mt > _watcher_state["last_mtime"]:
            _watcher_state["last_mtime"] = mt
            state = _load_state()
            if state:
                redraw(state)
    except Exception as e:
        print("[PLJ] Watcher error: {0}".format(e))


def start_watcher():
    """Hook the Rhino Idle event to watch for file changes.

    Safe to call multiple times (from repeated exec() calls).
    Unhooks any previous handler first to prevent accumulation.
    """
    if not IN_RHINO:
        print("[PLJ] Not in Rhino. Using fallback thread watcher.")
        _start_thread_watcher()
        return
    # Remove previous handler if exec() was called again
    if _watcher_state["running"]:
        try:
            Rhino.RhinoApp.Idle -= _on_idle
        except Exception:
            pass
        print("[PLJ] Stopped previous watcher.")
    Rhino.RhinoApp.Idle += _on_idle
    _watcher_state["running"] = True
    print("[PLJ] Watching: {0}".format(STATE_FILE))
    print("[PLJ] Watcher attached to Rhino Idle event.")


def stop_watcher():
    """Unhook the Rhino Idle event."""
    if IN_RHINO and _watcher_state["running"]:
        try:
            Rhino.RhinoApp.Idle -= _on_idle
        except Exception:
            pass
        _watcher_state["running"] = False
        print("[PLJ] Watcher stopped.")


def _start_thread_watcher():
    """Fallback for non-Rhino (dry-run) testing only."""
    def _loop():
        while True:
            try:
                mt = _state_mtime()
                if mt > _watcher_state["last_mtime"]:
                    _watcher_state["last_mtime"] = mt
                    state = _load_state()
                    if state:
                        print("[DRY RUN] Would redraw: {0}".format(
                            list(state["bays"].keys())))
                time.sleep(POLL_SEC)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print("[PLJ] Error: {0}".format(e))
                time.sleep(2)
    t = threading.Thread(target=_loop)
    t.daemon = True
    t.start()


# ── Startup ───────────────────────────────────────────────

state = _load_state()
if state:
    try:
        redraw(state)
    except Exception as e:
        print("[PLJ] Initial redraw failed: {0}".format(e))
        if IN_RHINO:
            try:
                rs.EnableRedraw(True)
            except Exception:
                pass
    start_watcher()
    # TCP listener disabled — it runs on a background thread and
    # IronPython's rhinoscriptsyntax is not thread-safe.  The MCP
    # rhino_query tool will report OFFLINE, but the watcher itself
    # is unaffected.  Uncomment to re-enable if needed:
    # start_listener()
    print("[PLJ] Ready. Edit state.json and the viewport updates automatically.")
else:
    print("[PLJ] No state file at {0}".format(STATE_FILE))
    print("  Run controller_cli.py to generate one.")
