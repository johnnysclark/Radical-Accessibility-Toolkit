# -*- coding: utf-8 -*-
"""
PLAN LAYOUT JIG — Terminal Controller  v2.3
============================================
Python CLI that writes a JSON state file. A separate Rhino watcher
script reads that file and rebuilds geometry on every save.

This controller never talks to Rhino directly. The JSON file is the
sole interface between the designer and the drawing.

Features
--------
  Rectangular and radial structural grids with z-ordering.
  Walls with door, window, and portal apertures.
  PIAF-optimised block symbols for tactile drawings.
  Rooms with hatch-image fills for tactile differentiation.
  Corridors with centerline and loading zones.
  Braille plus English legend for accessible reading.
  Hatch library management: list, add, path.
  Tactile 3D: extrude walls, omit aperture openings, clip at a
  configurable cut height, and export STL for 3D printing.

Usage
-----
  python controller_cli.py
  python controller_cli.py --state "/path/to/state.json"
"""
import argparse, copy, json, math, os, subprocess, sys, time
from datetime import datetime

SCHEMA = "plan_layout_jig_v2.3"
DEFAULT_STATE_FILENAME = "state.json"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif"}

# ── Ensure tools/rhino is importable (for tactile_print) ──
_controller_dir = os.path.dirname(os.path.abspath(__file__))
_tools_rhino = os.path.join(os.path.dirname(_controller_dir), "tools", "rhino")
if os.path.isdir(_tools_rhino) and _tools_rhino not in sys.path:
    sys.path.insert(0, _tools_rhino)

# ── utilities ─────────────────────────────────────────────

def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _script_dir():
    try:    return os.path.dirname(os.path.abspath(__file__))
    except: return os.getcwd()

def _default_state_path():
    return os.path.join(_script_dir(), DEFAULT_STATE_FILENAME)

def _atomic_write(path, text):
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)

def _speak(text, rate=2):
    """Fire-and-forget TTS via PowerShell SpeechSynthesizer.

    Strips OK:/ERROR: prefixes for cleaner speech.
    Returns True on success, False if speech fails.
    """
    clean = text.strip()
    for prefix in ("OK: ", "ERROR: ", "CHANGED: "):
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break
    # Escape single quotes for PowerShell
    escaped = clean.replace("'", "''")
    ps_cmd = (
        f"Add-Type -AssemblyName System.Speech;"
        f"$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        f"$s.Rate={int(rate)};"
        f"$s.Speak('{escaped}')"
    )
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

def _history_dir(state_file):
    """Return path to the history/ folder alongside the state file."""
    return os.path.join(os.path.dirname(os.path.abspath(state_file)), "history")

def _history_save(state_file, state, seq_num):
    """Write a numbered history snapshot: history/0001.json, etc."""
    hdir = _history_dir(state_file)
    os.makedirs(hdir, exist_ok=True)
    fname = os.path.join(hdir, f"{seq_num:04d}.json")
    _atomic_write(fname, json.dumps(state, indent=2, ensure_ascii=False))

def _history_delete_last(state_file, seq_num):
    """Remove the last numbered history file on undo."""
    hdir = _history_dir(state_file)
    fname = os.path.join(hdir, f"{seq_num:04d}.json")
    if os.path.exists(fname):
        os.remove(fname)

def _history_count(state_file):
    """Count numbered history files (0001.json, 0002.json, ...)."""
    hdir = _history_dir(state_file)
    if not os.path.isdir(hdir):
        return 0
    return sum(1 for f in os.listdir(hdir)
               if f.endswith(".json") and f[:4].isdigit())

def _history_list(state_file):
    """List all files in the history folder (numbered + snapshots)."""
    hdir = _history_dir(state_file)
    if not os.path.isdir(hdir):
        return [], []
    files = sorted(f for f in os.listdir(hdir) if f.endswith(".json"))
    numbered = [f for f in files if f[:4].isdigit()]
    snapshots = [f for f in files if f.startswith("snapshot_")]
    return numbered, snapshots

def _snapshot_save(state_file, state, name):
    """Write a named snapshot: history/snapshot_<name>.json."""
    hdir = _history_dir(state_file)
    os.makedirs(hdir, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    fname = os.path.join(hdir, f"snapshot_{safe}.json")
    _atomic_write(fname, json.dumps(state, indent=2, ensure_ascii=False))
    return fname

def _snapshot_load(state_file, name):
    """Load a named snapshot. Returns the state dict or raises ValueError."""
    hdir = _history_dir(state_file)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    fname = os.path.join(hdir, f"snapshot_{safe}.json")
    if not os.path.isfile(fname):
        # Try exact match
        available = [f[9:-5] for f in os.listdir(hdir)
                     if f.startswith("snapshot_") and f.endswith(".json")] if os.path.isdir(hdir) else []
        avail_s = ", ".join(available) if available else "(none)"
        raise ValueError(f"Snapshot '{name}' not found. Available: {avail_s}")
    with open(fname, "r", encoding="utf-8") as f:
        return json.load(f)

def _fmt(p):
    return f"({p[0]:.1f}, {p[1]:.1f})"

def _float(x, name):
    try:    return float(x)
    except: raise ValueError(f"{name} must be a number. Got: {x}")

def _int_pos(x, name):
    try:    v = int(x)
    except: raise ValueError(f"{name} must be a whole number. Got: {x}")
    if v < 1: raise ValueError(f"{name} must be >= 1. Got: {v}")
    return v

def _int_nn(x, name):
    try:    v = int(x)
    except: raise ValueError(f"{name} must be a whole number. Got: {x}")
    if v < 0: raise ValueError(f"{name} must be >= 0. Got: {v}")
    return v

def _scale_label(ft_per_in):
    n = int(ft_per_in) if ft_per_in == int(ft_per_in) else ft_per_in
    return f'1/{n}"=1\'-0"'

def tokenize(raw):
    """Split input into tokens, respecting double-quoted strings."""
    tokens, buf, in_q = [], "", False
    for ch in raw:
        if ch == '"':
            in_q = not in_q; buf += ch
        elif ch.isspace() and not in_q:
            if buf: tokens.append(buf); buf = ""
        else:
            buf += ch
    if buf: tokens.append(buf)
    return tokens

def _scan_hatch_folder(path):
    if not os.path.isdir(path): return []
    return sorted(f for f in os.listdir(path)
                  if os.path.splitext(f)[1].lower() in IMAGE_EXTS)

# ══════════════════════════════════════════════════════════
# DEFAULT STATE
# ══════════════════════════════════════════════════════════

def _default_corridor():
    return {"enabled": False, "axis": "x", "position": 1,
            "width": 8.0, "loading": "double",
            "hatch": "none", "hatch_scale": 4.0}

def _default_walls():
    return {"enabled": False, "thickness": 0.5}

def _default_blocks():
    return {
        "door":   {"symbol": "arc_swing",     "label_prefix": "D",
                   "show_label": True, "label_height": 1.5,
                   "tactile_weight_mm": 0.35},
        "window": {"symbol": "glass_line",    "label_prefix": "W",
                   "show_label": True, "label_height": 1.5,
                   "tactile_weight_mm": 0.25},
        "portal": {"symbol": "bracket_arrow", "label_prefix": "P",
                   "show_label": True, "label_height": 1.5,
                   "tactile_weight_mm": 0.35},
        "room":   {"symbol": "boundary_label","show_label": True,
                   "label_height": 3.0, "tactile_weight_mm": 0.50},
    }

def _default_legend():
    return {
        "enabled": True,
        "position": "bottom-right",
        "custom_origin": [0, 0],
        "width": 40.0,
        "title": "Legend",
        "title_braille": "",
        "show_braille": True,
        "show_hatches": True,
        "show_apertures": True,
        "swatch_size": 5.0,
        "row_height": 7.0,
        "text_height": 2.0,
        "braille_height": 2.5,
        "border_weight_mm": 0.50,
        "padding": 3.0,
    }

def _default_tactile3d():
    return {
        "enabled": False,
        "wall_height": 9.0,
        "cut_height": 4.0,
        "floor_thickness": 0.5,
        "floor_enabled": True,
        "auto_export": False,
        "export_path": "./tactile3d_export.stl",
        "scale_factor": 1.0,
    }

def _default_bambu():
    return {
        "printer_ip": "",
        "access_code": "",
        "serial_number": "",
        "printer_model": "p1s",
        "print_scale": 200,         # 1:N representation scale
        "stl_path": "./tactile_model.stl",
        "slicer_path": "",          # path to OrcaSlicer executable
    }

def _default_tts():
    return {"enabled": False, "rate": 2}

def _default_section():
    return {"axis": None, "offset": None, "last_export_path": None}

def _default_bay(name, origin,
                 grid_type="rectangular", z_order=0,
                 bays=(3,3), spacing=(24,24), rotation=0.0,
                 rings=4, ring_spacing=20.0, arms=8,
                 arc_deg=360.0, arc_start_deg=0.0,
                 corridor=None, walls=None, apertures=None,
                 void_center=None, void_size=(20,20),
                 void_shape="rectangle", label=None):
    if corridor is None:   corridor = _default_corridor()
    if walls is None:      walls = _default_walls()
    if apertures is None:  apertures = []
    if void_center is None: void_center = list(origin)
    if label is None:       label = "Bay " + name
    try:
        import braille as _braille_mod
        braille_text = _braille_mod.to_braille(label)
    except ImportError:
        # Fallback: hard-coded for A/B/C if braille module unavailable
        _braille_fallback = {"A": "\u2803\u2801\u283d \u2801",
                             "B": "\u2803\u2801\u283d \u2803",
                             "C": "\u2803\u2801\u283d \u2809"}
        braille_text = _braille_fallback.get(name, "")
    return {
        "grid_type": grid_type, "z_order": z_order,
        "origin": list(origin), "rotation_deg": rotation,
        "bays": list(bays), "spacing": list(spacing),
        "spacing_x": None, "spacing_y": None,
        "rings": rings, "ring_spacing": ring_spacing,
        "arms": arms, "arc_deg": arc_deg, "arc_start_deg": arc_start_deg,
        "corridor": corridor, "walls": walls, "apertures": apertures,
        "void_center": list(void_center), "void_size": list(void_size),
        "void_shape": void_shape,
        "label": label, "braille": braille_text,
    }

def _auto_rooms(bays_dict):
    rooms = {}
    for name, bay in sorted(bays_dict.items()):
        rooms[f"bay_{name}"] = {
            "type": "bay", "source_bay": name,
            "label": bay.get("label", f"Bay {name}"),
            "braille": bay.get("braille", ""),
            "hatch_image": "none", "hatch_scale": 1.0, "hatch_rotation": 0.0}
        rooms[f"void_{name}"] = {
            "type": "void", "source_bay": name,
            "label": f"{bay.get('label','Bay '+name)} Void",
            "braille": "",
            "hatch_image": "none", "hatch_scale": 1.0, "hatch_rotation": 0.0}
    rooms["landscape"] = {
        "type": "landscape", "source_bay": None,
        "label": "Landscape", "braille": "",
        "hatch_image": "none", "hatch_scale": 1.0, "hatch_rotation": 0.0}
    return rooms

# ── Cell-room helpers ──

def _init_cells(bay):
    """Auto-generate a cells dict for a rectangular bay (nx * ny cells)."""
    if bay.get("grid_type","rectangular") != "rectangular":
        return {}
    nx, ny = bay["bays"]
    cells = {}
    for c in range(nx):
        for r in range(ny):
            cells[f"{c},{r}"] = {
                "name": "", "label": "", "braille": "",
                "hatch": "none", "hatch_scale": 1.0, "hatch_rotation": 0.0}
    return cells

def _cell_area(bay, c, r):
    """Area of cell (c, r) in square feet."""
    cx, cy = _get_spacing_arrays(bay)
    return (cx[c+1] - cx[c]) * (cy[r+1] - cy[r])

def _parse_cell_ref(s):
    """Parse '2,1' or '2.1' into (col, row) ints."""
    sep = "," if "," in s else "."
    parts = s.split(sep)
    if len(parts) != 2:
        raise ValueError(f"Bad cell ref '{s}'. Use col,row (e.g. 2,1).")
    return int(parts[0]), int(parts[1])

def _expand_cell_range(s, nx, ny):
    """Parse '0,0-2,1' into list of (c,r) tuples.  Also accepts a single ref."""
    if "-" in s and s.count("-") == 1:
        a, b = s.split("-")
        c0, r0 = _parse_cell_ref(a)
        c1, r1 = _parse_cell_ref(b)
        if c0 > c1: c0, c1 = c1, c0
        if r0 > r1: r0, r1 = r1, r0
        out = []
        for c in range(c0, c1 + 1):
            for r in range(r0, r1 + 1):
                if 0 <= c < nx and 0 <= r < ny:
                    out.append((c, r))
        if not out:
            raise ValueError(f"Range {s} is outside the grid (0..{nx-1}, 0..{ny-1}).")
        return out
    c, r = _parse_cell_ref(s)
    if not (0 <= c < nx and 0 <= r < ny):
        raise ValueError(f"Cell {c},{r} is outside the grid (0..{nx-1}, 0..{ny-1}).")
    return [(c, r)]

def _room_summary(bay):
    """Group cells by room name; return dict of name -> {cells, area, label, hatch}."""
    cells = bay.get("cells", {})
    if not cells: return {}
    rooms = {}
    for key, cell in sorted(cells.items()):
        c, r = _parse_cell_ref(key)
        name = cell.get("name","") or "(unnamed)"
        if name not in rooms:
            rooms[name] = {"cells": [], "area": 0.0, "label": "",
                           "hatch": "none", "hatch_scale": 1.0}
        rooms[name]["cells"].append((c, r))
        rooms[name]["area"] += _cell_area(bay, c, r)
        if cell.get("label") and not rooms[name]["label"]:
            rooms[name]["label"] = cell["label"]
        if cell.get("hatch","none") != "none" and rooms[name]["hatch"] == "none":
            rooms[name]["hatch"] = cell["hatch"]
            rooms[name]["hatch_scale"] = cell.get("hatch_scale", 1.0)
    return rooms

def _default_print():
    return {"scale_ft_per_inch": 8, "paper_width_in": 24.0,
            "paper_height_in": 36.0, "margin_in": 0.5,
            "dpi": 300, "format": "png", "request_id": 0}

def default_state():
    """Full default state with demo bays, apertures, and corridors."""
    cor_a = {"enabled": True, "axis": "x", "position": 1,
             "width": 8.0, "loading": "double",
             "hatch": "Hatch1", "hatch_scale": 4.0}
    cor_c = {"enabled": True, "axis": "y", "position": 2,
             "width": 8.0, "loading": "single",
             "hatch": "Hatch1", "hatch_scale": 4.0}
    walls_a = {"enabled": True, "thickness": 0.5}
    ap_a = [
        {"id": "d1", "type": "door",   "axis": "x", "gridline": 0,
         "corner": 10.0, "width": 3.0, "height": 7.0,
         "hinge": "start", "swing": "positive"},
        {"id": "w1", "type": "window", "axis": "y", "gridline": 0,
         "corner": 8.0,  "width": 6.0, "height": 4.0,
         "hinge": "start", "swing": "positive"},
        {"id": "p1", "type": "portal", "axis": "x", "gridline": 2,
         "corner": 30.0, "width": 10.0, "height": 9.0,
         "hinge": "start", "swing": "positive"},
    ]
    bays_dict = {
        "A": _default_bay("A", (18,8), grid_type="rectangular", z_order=0,
                bays=(6,3), spacing=(24,24),
                corridor=cor_a, walls=walls_a, apertures=ap_a,
                void_center=(90,44), void_size=(30,18)),
        "B": _default_bay("B", (90,145), grid_type="radial", z_order=2,
                rings=3, ring_spacing=20, arms=8,
                void_center=(90,145), void_size=(20,20), void_shape="circle"),
        "C": _default_bay("C", (30,210), grid_type="rectangular", z_order=1,
                bays=(4,1), spacing=(24,30),
                corridor=cor_c,
                void_center=(78,225), void_size=(20,14)),
    }
    return {
        "schema": SCHEMA,
        "meta": {"created": _now(), "last_saved": _now(),
                 "notes": "Plan Layout Jig v2.3"},
        "site": {"origin": [0.0, 0.0], "width": 180.0, "height": 260.0},
        "style": {
            "column_size": 1.5,
            "heavy_lineweight_mm": 1.40, "light_lineweight_mm": 0.08,
            "corridor_lineweight_mm": 0.35, "wall_lineweight_mm": 0.25,
            "label_text_height": 0.3, "braille_text_height": 0.5,
            "corridor_dash_len": 3.0, "corridor_gap_len": 2.0,
            "background_pad": 2.0, "label_offset": 3.0,
            "arc_segments": 16,
        },
        "bays": bays_dict,
        "blocks": _default_blocks(),
        "rooms": _auto_rooms(bays_dict),
        "legend": _default_legend(),
        "tactile3d": _default_tactile3d(),
        "hatch_library_path": "./hatches/",
        "print": _default_print(),
        "bambu": _default_bambu(),
    }

# ══════════════════════════════════════════════════════════
# LOAD / SAVE
# ══════════════════════════════════════════════════════════

def load_state(path):
    if not os.path.exists(path): return default_state()
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

def save_state(path, state):
    state["meta"]["last_saved"] = _now()
    _atomic_write(path, json.dumps(state, indent=2, ensure_ascii=False))

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

def _bay_extents_rect(bay):
    ox, oy = bay["origin"]; rot = bay["rotation_deg"]
    cx, cy = _get_spacing_arrays(bay)
    w, h = cx[-1], cy[-1]
    corners = [(0,0),(w,0),(w,h),(0,h)]
    r = math.radians(rot)
    wxs = [ox + lx*math.cos(r) - ly*math.sin(r) for lx,ly in corners]
    wys = [oy + lx*math.sin(r) + ly*math.cos(r) for lx,ly in corners]
    return min(wxs), max(wxs), min(wys), max(wys)

def _bay_extents_radial(bay):
    ox, oy = bay["origin"]
    outer = bay.get("rings",4) * bay.get("ring_spacing",20)
    arc_deg = bay.get("arc_deg", 360)
    if arc_deg >= 360:
        return ox - outer, ox + outer, oy - outer, oy + outer
    # Sample the arc boundary plus critical points for a tight bbox
    start = bay.get("arc_start_deg", 0)
    pts_x = [0.0]; pts_y = [0.0]  # include the center
    n = max(36, int(arc_deg / 5))
    for i in range(n + 1):
        a = math.radians(start + arc_deg * i / n)
        pts_x.append(outer * math.cos(a))
        pts_y.append(outer * math.sin(a))
    return (ox + min(pts_x), ox + max(pts_x),
            oy + min(pts_y), oy + max(pts_y))

def _bay_extents(bay):
    if bay.get("grid_type") == "radial": return _bay_extents_radial(bay)
    return _bay_extents_rect(bay)

def _bay_col_count(bay):
    if bay.get("grid_type") == "radial":
        return 1 + bay.get("rings",4) * bay.get("arms",8)
    return (bay["bays"][0] + 1) * (bay["bays"][1] + 1)

def _bay_area(bay):
    """Gross footprint area in square feet."""
    if bay.get("grid_type") == "radial":
        outer = bay.get("rings",4) * bay.get("ring_spacing",20)
        arc = bay.get("arc_deg",360)
        return math.pi * outer**2 * (arc / 360.0)
    cx, cy = _get_spacing_arrays(bay)
    return cx[-1] * cy[-1]

# ══════════════════════════════════════════════════════════
# DESCRIBE / LIST
# ══════════════════════════════════════════════════════════

def describe(state):
    """Build a comprehensive text description of the entire model.

    The output is organized into sections:
      META       — schema version, creation date, last save time
      SITE       — site dimensions and total area
      STYLE      — all lineweights, text heights, and drawing params
      BAY (each) — grid type, origin, rotation, spacing, extents,
                   column count, corridor, walls, each aperture with
                   all its properties, void, and labels
      ROOMS      — every room with type, label, braille, and hatch
      BLOCKS     — aperture symbol config and tactile weights
      LEGEND     — on/off, position, braille, sizing
      TACTILE 3D — on/off, wall height, cut height, floor, export
      HATCH LIB  — folder path and image count
      PRINT      — scale, paper size, margins, DPI, format
      TOTALS     — column count, bay count, total area
    """
    s = state["site"]; st = state["style"]
    meta = state.get("meta", {})
    lines = ["=" * 60,
             "PLAN LAYOUT JIG — Full Model Description",
             "=" * 60, ""]

    # ── Meta ──
    lines.append(f"Schema: {state.get('schema','?')}")
    lines.append(f"Created: {meta.get('created','?')}   "
                 f"Last saved: {meta.get('last_saved','?')}")
    if meta.get("notes"): lines.append(f"Notes: {meta['notes']}")
    lines.append("")

    # ── Site ──
    site_area = s["width"] * s["height"]
    lines.append(f"SITE: {s['width']:.0f} x {s['height']:.0f} ft  "
                 f"({site_area:,.0f} sq ft)")
    lines.append(f"  Origin: {_fmt(s['origin'])}")
    lines.append("")

    # ── Style ──
    lines.append("STYLE VARIABLES:")
    lines.append(f"  column_size: {st.get('column_size',1.5)} ft")
    lines.append(f"  heavy_lineweight: {st.get('heavy_lineweight_mm',1.4)} mm")
    lines.append(f"  light_lineweight: {st.get('light_lineweight_mm',0.08)} mm")
    lines.append(f"  corridor_lineweight: {st.get('corridor_lineweight_mm',0.35)} mm")
    lines.append(f"  wall_lineweight: {st.get('wall_lineweight_mm',0.25)} mm")
    lines.append(f"  label_text_height: {st.get('label_text_height',0.3)} ft")
    lines.append(f"  braille_text_height: {st.get('braille_text_height',0.5)} ft")
    lines.append(f"  corridor_dash_len: {st.get('corridor_dash_len',3.0)} ft")
    lines.append(f"  corridor_gap_len: {st.get('corridor_gap_len',2.0)} ft")
    lines.append(f"  background_pad: {st.get('background_pad',2.0)} ft")
    lines.append(f"  label_offset: {st.get('label_offset',3.0)} ft")
    lines.append(f"  arc_segments: {st.get('arc_segments',16)}")
    lines.append("")

    # ── Bays ──
    total_cols = 0
    total_area = 0.0
    for name in sorted(state["bays"]):
        b = state["bays"][name]
        gt = b.get("grid_type","rectangular"); zo = b.get("z_order",0)
        rot = b["rotation_deg"]; cols = _bay_col_count(b); total_cols += cols
        area = _bay_area(b); total_area += area
        rot_s = "no rotation" if rot == 0 else f"rotated {rot:.1f} deg"
        lines.append(f"BAY {name}  ({gt}, z_order={zo})  "
                     f"anchor {_fmt(b['origin'])}, {rot_s}")
        if gt == "radial":
            nr = b.get("rings",4); rsv = b.get("ring_spacing",20)
            na = b.get("arms",8); ad = b.get("arc_deg",360)
            asd = b.get("arc_start_deg",0)
            lines.append(f"  {nr} rings x {na} arms, ring spacing {rsv:.0f} ft, "
                         f"arc {ad:.0f} deg from {asd:.0f} deg")
            lines.append(f"  Outer radius: {nr*rsv:.0f} ft   "
                         f"{cols} columns   area: {area:,.0f} sq ft")
        else:
            nx, ny = b["bays"]
            sx_a = b.get("spacing_x"); sy_a = b.get("spacing_y")
            if sx_a and len(sx_a)==nx:
                lines.append(f"  {nx} bays across (irregular): {sx_a}")
            else:
                lines.append(f"  {nx} bays across @ {b['spacing'][0]:.0f} ft")
            if sy_a and len(sy_a)==ny:
                lines.append(f"  {ny} bays deep (irregular): {sy_a}")
            else:
                lines.append(f"  {ny} bays deep @ {b['spacing'][1]:.0f} ft")
            cx, cy = _get_spacing_arrays(b)
            lines.append(f"  Footprint: {cx[-1]:.0f} x {cy[-1]:.0f} ft   "
                         f"{cols} columns   area: {area:,.0f} sq ft")
            lines.append(f"  Gridlines: {len(cx)} vertical (x), {len(cy)} horizontal (y)")
        xlo, xhi, ylo, yhi = _bay_extents(b)
        lines.append(f"  World bounds: x [{xlo:.0f}, {xhi:.0f}]  "
                     f"y [{ylo:.0f}, {yhi:.0f}]")
        cor = b.get("corridor", {})
        if cor.get("enabled"):
            ax_n = "east-west (x-axis)" if cor["axis"]=="x" else "north-south (y-axis)"
            lines.append(f"  Corridor: {cor.get('loading','double')}-loaded, {ax_n}, "
                         f"gridline {cor['position']}, {cor['width']:.0f} ft wide")
            lines.append(f"    hatch={cor.get('hatch','none')}  "
                         f"hatch_scale={cor.get('hatch_scale',4.0)}")
        else: lines.append("  Corridor: none")
        w = b.get("walls", {})
        if w.get("enabled") and gt == "rectangular":
            t_in = w.get("thickness",0.5) * 12
            lines.append(f"  Walls: ON, thickness {w.get('thickness',0.5):.3f} ft "
                         f"({t_in:.1f} inches)")
        else: lines.append("  Walls: off")
        aps = b.get("apertures", [])
        if aps:
            lines.append(f"  Apertures: {len(aps)}")
            for a in aps:
                tp = a.get("type","door")
                lines.append(f"    {a.get('id','?')}: {tp}  axis={a['axis']}  "
                             f"gridline={a['gridline']}  "
                             f"corner={a['corner']:.1f} ft  "
                             f"width={a['width']:.1f} ft  "
                             f"height={a['height']:.1f} ft")
                if tp == "door":
                    lines.append(f"      hinge={a.get('hinge','start')}  "
                                 f"swing={a.get('swing','positive')}")
        else: lines.append("  Apertures: none")
        vs = b["void_size"]; shape = b.get("void_shape","rectangle")
        lines.append(f"  Void: {shape} {vs[0]:.0f} x {vs[1]:.0f} ft  "
                     f"center {_fmt(b['void_center'])}")
        lbl = b.get("label",""); brl = b.get("braille","")
        lines.append(f"  Label: \"{lbl}\"" + (f"  Braille: \"{brl}\"" if brl else ""))
        # Cell rooms
        bay_cells = b.get("cells", {})
        if bay_cells:
            named = {k: v for k, v in bay_cells.items() if v.get("name","")}
            rooms = _room_summary(b)
            named_rooms = {n: d for n, d in rooms.items() if n != "(unnamed)"}
            if named_rooms:
                lines.append(f"  Cell rooms: {len(named_rooms)} rooms "
                             f"({len(named)} of {len(bay_cells)} cells named)")
                for rn in sorted(named_rooms):
                    rd = named_rooms[rn]
                    coords = ", ".join(f"{c},{r}" for c, r in rd["cells"])
                    ht = rd["hatch"]
                    ht_s = f"  hatch={ht}" if ht != "none" else ""
                    lines.append(f"    {rn}: {len(rd['cells'])} cells, "
                                 f"{rd['area']:,.0f} sq ft  [{coords}]{ht_s}")
            else:
                lines.append(f"  Cell rooms: {len(bay_cells)} cells, none named")
        lines.append("")

    # ── Rooms ──
    rooms = state.get("rooms", {})
    if rooms:
        lines.append(f"ROOMS: {len(rooms)} total")
        for rid in sorted(rooms):
            rm = rooms[rid]
            hi = rm.get("hatch_image","none")
            hs_s = f"  scale={rm.get('hatch_scale',1.0)}  rot={rm.get('hatch_rotation',0.0)}" if hi != "none" else ""
            brl = rm.get("braille","")
            brl_s = f'  braille="{brl}"' if brl else ""
            lines.append(f"  {rid}: type={rm.get('type','bay')}  "
                         f'label="{rm.get("label","")}"  '
                         f"hatch={hi}{hs_s}{brl_s}")
        lines.append("")

    # ── Blocks ──
    blocks = state.get("blocks", {})
    if blocks:
        lines.append("BLOCK SYMBOLS:")
        for bt in sorted(blocks):
            bk = blocks[bt]
            lbl = "on" if bk.get("show_label",True) else "off"
            lines.append(f"  {bt}: symbol={bk.get('symbol','')}  "
                         f"label={lbl}  prefix={bk.get('label_prefix','')}  "
                         f"label_height={bk.get('label_height',1.5)}  "
                         f"tactile={bk.get('tactile_weight_mm',0.35)} mm")
        lines.append("")

    # ── Legend ──
    leg = state.get("legend", {})
    lines.append(f"LEGEND: {'ON' if leg.get('enabled') else 'OFF'}  "
                 f"position={leg.get('position','bottom-right')}  "
                 f"width={leg.get('width',40)} ft")
    if leg.get("enabled"):
        lines.append(f"  title=\"{leg.get('title','Legend')}\"  "
                     f"title_braille=\"{leg.get('title_braille','')}\"")
        lines.append(f"  show_braille={leg.get('show_braille',True)}  "
                     f"show_hatches={leg.get('show_hatches',True)}  "
                     f"show_apertures={leg.get('show_apertures',True)}")
        lines.append(f"  swatch_size={leg.get('swatch_size',5.0)}  "
                     f"row_height={leg.get('row_height',7.0)}  "
                     f"text_height={leg.get('text_height',2.0)}  "
                     f"braille_height={leg.get('braille_height',2.5)}")
        lines.append(f"  padding={leg.get('padding',3.0)}  "
                     f"border_weight={leg.get('border_weight_mm',0.5)} mm")
    lines.append("")

    # ── Tactile 3D ──
    t3 = state.get("tactile3d", {})
    lines.append(f"TACTILE 3D: {'ON' if t3.get('enabled') else 'OFF'}")
    lines.append(f"  wall_height={t3.get('wall_height',9.0)} ft  "
                 f"cut_height={t3.get('cut_height',4.0)} ft  "
                 f"floor={'ON' if t3.get('floor_enabled') else 'OFF'}  "
                 f"floor_thickness={t3.get('floor_thickness',0.5)} ft")
    lines.append(f"  auto_export={t3.get('auto_export',False)}  "
                 f"export_path={t3.get('export_path','')}  "
                 f"scale_factor={t3.get('scale_factor',1.0)}")
    lines.append("")

    # ── Bambu printer ──
    bam = state.get("bambu", {})
    ip = bam.get("printer_ip", "")
    lines.append(f"BAMBU PRINTER: {'configured' if ip else 'not configured'}")
    if ip:
        lines.append(f"  ip={ip}  model={bam.get('printer_model','p1s')}  "
                     f"serial={bam.get('serial_number','(not set)')}")
    lines.append(f"  print_scale=1:{bam.get('print_scale',200)}  "
                 f"stl_path={bam.get('stl_path','./tactile_model.stl')}")
    if bam.get("slicer_path"):
        lines.append(f"  slicer={bam['slicer_path']}")
    lines.append("")

    # ── TTS ──
    tts = state.get("tts", {})
    lines.append(f"TTS: {'ON' if tts.get('enabled') else 'OFF'}  "
                 f"rate={tts.get('rate', 2)}")
    lines.append("")

    # ── Section Cut ──
    sec = state.get("section", {})
    if sec.get("axis"):
        lines.append(f"SECTION CUT: {sec['axis'].upper()}={sec['offset']:.1f} ft")
        if sec.get("last_export_path"):
            lines.append(f"  Last export: {sec['last_export_path']}")
    else:
        lines.append("SECTION CUT: not defined")
    lines.append("")

    # ── Hatch library ──
    hlp = state.get("hatch_library_path","./hatches/")
    lines.append(f"HATCH LIBRARY: {hlp}")
    if os.path.isdir(hlp):
        imgs = _scan_hatch_folder(hlp)
        lines.append(f"  {len(imgs)} images: {', '.join(imgs[:10])}"
                     + ("..." if len(imgs)>10 else ""))
    else: lines.append("  (folder not found)")
    lines.append("")

    # ── Print ──
    pr = state.get("print",{}); scv = pr.get("scale_ft_per_inch",8)
    pw = pr.get("paper_width_in",24); ph = pr.get("paper_height_in",36)
    lines.append(f"PRINT: {_scale_label(scv)} on {pw}x{ph}\" paper  "
                 f"margin={pr.get('margin_in',0.5)}\"  "
                 f"{pr.get('dpi',300)} DPI  format={pr.get('format','png')}")
    lines.append("")

    # ── Totals ──
    lines.append("-" * 40)
    lines.append(f"TOTALS: {total_cols} columns across {len(state['bays'])} bays")
    lines.append(f"  Combined bay area: {total_area:,.0f} sq ft")
    lines.append(f"  Site area: {site_area:,.0f} sq ft")
    hatched = sum(1 for rm in rooms.values() if rm.get("hatch_image","none") != "none")
    lines.append(f"  Rooms: {len(rooms)} defined, {hatched} hatched")
    total_aps = sum(len(b.get("apertures",[])) for b in state["bays"].values())
    lines.append(f"  Apertures: {total_aps} total")
    return "\n".join(lines)

def list_bays(state):
    lines = ["Name  Type   Z  Anchor           Rot    Cols  Walls  Apertures  Corridor"]
    lines.append("-" * 75)
    for name in sorted(state["bays"]):
        b = state["bays"][name]
        gt = b.get("grid_type","rect")[:4]; zo = b.get("z_order",0)
        cols = _bay_col_count(b)
        w = b.get("walls",{}); w_s = f"{w.get('thickness',0.5)*12:.0f}in" if w.get("enabled") else "off"
        aps = len(b.get("apertures",[])); cor = b.get("corridor",{})
        cor_s = f"{cor.get('loading','dbl')[:3]} {cor['axis']}" if cor.get("enabled") else "off"
        lines.append(f"  {name}   {gt:<6} {zo}  {_fmt(b['origin']):<16} "
                     f"{b['rotation_deg']:<6.0f} {cols:<5} {w_s:<6} {aps:<10} {cor_s}")
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════
# WALL / APERTURE / CORRIDOR
# ══════════════════════════════════════════════════════════

def _resolve_bay(state, tokens, idx=1):
    name = tokens[idx].upper()
    if name not in state["bays"]:
        raise ValueError(f"No bay '{name}'. Have: {', '.join(sorted(state['bays']))}")
    return name, state["bays"][name]

def cmd_wall(state, tokens):
    if len(tokens) < 3: raise ValueError("Usage: wall <bay> on|off|thickness [value]")
    name, bay = _resolve_bay(state, tokens)
    if "walls" not in bay: bay["walls"] = _default_walls()
    w = bay["walls"]; sub = tokens[2].lower()
    if sub == "on":
        w["enabled"] = True
        return state, f"Bay {name} walls ON, {w['thickness']*12:.0f}-inch thick."
    if sub == "off":
        w["enabled"] = False; return state, f"Bay {name} walls OFF."
    if sub == "thickness":
        if len(tokens) != 4: raise ValueError("wall <bay> thickness <feet>")
        val = _float(tokens[3],"thickness")
        if val <= 0: raise ValueError("Thickness must be > 0.")
        old = w.get("thickness",0.5); w["thickness"] = val
        return state, f"Bay {name} wall thickness = {val:.3f} ft ({val*12:.1f} in). Was {old:.3f} ft."
    raise ValueError("Wall subcommands: on, off, thickness")

def cmd_aperture(state, tokens):
    if len(tokens) < 3: raise ValueError("Usage: aperture <bay> add|remove|set|list ...")
    name, bay = _resolve_bay(state, tokens)
    if "apertures" not in bay: bay["apertures"] = []
    aps = bay["apertures"]; sub = tokens[2].lower()
    if sub == "list":
        if not aps: return state, f"Bay {name}: no apertures."
        lines = [f"Bay {name} apertures ({len(aps)}):"]
        lines.append("  ID     Type     Axis  GL   Corner   Width   Height  Hinge   Swing")
        lines.append("  " + "-" * 70)
        for a in aps:
            tp = a.get("type","door")
            h = a.get("hinge","start") if tp == "door" else "-"
            sw = a.get("swing","positive") if tp == "door" else "-"
            lines.append(f"  {a['id']:<6} {tp:<8} {a['axis']}     "
                         f"{a['gridline']:<4} {a['corner']:<8.1f} "
                         f"{a['width']:<7.1f} {a['height']:<7.1f} "
                         f"{h:<7} {sw}")
        return state, "\n".join(lines)
    if sub == "add":
        if len(tokens) < 10:
            raise ValueError("aperture <bay> add <id> <door|window|portal> "
                             "<x|y> <gridline> <corner> <width> <height>")
        aid = tokens[3]
        if any(a["id"]==aid for a in aps):
            raise ValueError(f"Aperture '{aid}' already exists in bay {name}.")
        atype = tokens[4].lower()
        if atype not in ("door","window","portal"): raise ValueError("Type must be door, window, or portal.")
        axis = tokens[5].lower()
        if axis not in ("x","y"): raise ValueError("Axis must be x or y.")
        gl = _int_nn(tokens[6],"gridline"); cn = _float(tokens[7],"corner")
        wd = _float(tokens[8],"width"); ht = _float(tokens[9],"height")
        if wd <= 0 or ht <= 0: raise ValueError("Width and height must be > 0.")
        aps.append({"id": aid, "type": atype, "axis": axis, "gridline": gl,
                    "corner": cn, "width": wd, "height": ht,
                    "hinge": "start", "swing": "positive"})
        return state, f"Bay {name} aperture '{aid}' added: {atype}, {axis}-gridline {gl}, {wd:.1f} x {ht:.1f} ft."
    if sub == "remove":
        if len(tokens) != 4: raise ValueError("aperture <bay> remove <id>")
        aid = tokens[3]
        idx = next((i for i,a in enumerate(aps) if a["id"]==aid), None)
        if idx is None: raise ValueError(f"No aperture '{aid}' in bay {name}.")
        removed = aps.pop(idx)
        return state, f"Bay {name} aperture '{aid}' ({removed['type']}) removed."
    if sub == "set":
        if len(tokens) < 6: raise ValueError("aperture <bay> set <id> <field> <value>")
        aid = tokens[3]
        ap = next((a for a in aps if a["id"]==aid), None)
        if ap is None: raise ValueError(f"No aperture '{aid}' in bay {name}.")
        field = tokens[4].lower(); val = tokens[5]
        if field == "type":
            v = val.lower()
            if v not in ("door","window","portal"): raise ValueError("door, window, or portal.")
            old = ap["type"]; ap["type"] = v; return state, f"Aperture {aid} type = {v}. Was {old}."
        if field == "axis":
            v = val.lower()
            if v not in ("x","y"): raise ValueError("x or y.")
            old = ap["axis"]; ap["axis"] = v; return state, f"Aperture {aid} axis = {v}. Was {old}."
        if field == "gridline":
            v = _int_nn(val,"gridline"); old = ap["gridline"]; ap["gridline"] = v
            return state, f"Aperture {aid} gridline = {v}. Was {old}."
        if field == "corner":
            v = _float(val,"corner"); old = ap["corner"]; ap["corner"] = v
            return state, f"Aperture {aid} corner = {v:.1f} ft. Was {old:.1f} ft."
        if field == "width":
            v = _float(val,"width")
            if v <= 0: raise ValueError("Width must be > 0.")
            old = ap["width"]; ap["width"] = v
            return state, f"Aperture {aid} width = {v:.1f} ft. Was {old:.1f} ft."
        if field == "height":
            v = _float(val,"height")
            if v <= 0: raise ValueError("Height must be > 0.")
            old = ap["height"]; ap["height"] = v
            return state, f"Aperture {aid} height = {v:.1f} ft. Was {old:.1f} ft."
        if field == "hinge":
            v = val.lower()
            if v not in ("start","end"): raise ValueError("start or end.")
            old = ap.get("hinge","start"); ap["hinge"] = v
            return state, f"Aperture {aid} hinge = {v}. Was {old}."
        if field == "swing":
            v = val.lower()
            if v in ("positive","pos"): v = "positive"
            elif v in ("negative","neg"): v = "negative"
            else: raise ValueError("positive (pos) or negative (neg).")
            old = ap.get("swing","positive"); ap["swing"] = v
            return state, f"Aperture {aid} swing = {v}. Was {old}."
        raise ValueError("Aperture fields: type, axis, gridline, corner, width, height, hinge, swing")
    raise ValueError("Aperture subcommands: add, remove, set, list")

def cmd_corridor(state, tokens):
    if len(tokens) < 3: raise ValueError("Usage: corridor <bay> on|off|axis|position|width|loading|hatch|hatch_scale")
    name, bay = _resolve_bay(state, tokens)
    if "corridor" not in bay: bay["corridor"] = _default_corridor()
    cor = bay["corridor"]; sub = tokens[2].lower()
    if sub == "on":  cor["enabled"] = True;  return state, f"Bay {name} corridor ON."
    if sub == "off": cor["enabled"] = False; return state, f"Bay {name} corridor OFF."
    if len(tokens) < 4: raise ValueError(f"corridor {name} {sub} needs a value.")
    if sub == "axis":
        v = tokens[3].lower()
        if v not in ("x","y"): raise ValueError("x or y.")
        old = cor["axis"]; cor["axis"] = v; return state, f"Bay {name} corridor axis = {v}. Was {old}."
    if sub == "position":
        v = int(tokens[3]); old = cor["position"]; cor["position"] = v
        return state, f"Bay {name} corridor position = gridline {v}. Was {old}."
    if sub == "width":
        v = _float(tokens[3],"width")
        if v <= 0: raise ValueError("Width must be > 0.")
        old = cor["width"]; cor["width"] = v
        return state, f"Bay {name} corridor width = {v} ft. Was {old} ft."
    if sub == "loading":
        v = tokens[3].lower()
        if v not in ("single","double"): raise ValueError("single or double.")
        old = cor.get("loading","double"); cor["loading"] = v
        return state, f"Bay {name} corridor loading = {v}. Was {old}."
    if sub == "hatch":
        v = tokens[3]; v = "none" if v.lower() in ("none","off") else v
        old = cor.get("hatch","none"); cor["hatch"] = v
        return state, f"Bay {name} corridor hatch = {v}. Was {old}."
    if sub in ("hatch_scale","hatchscale"):
        v = _float(tokens[3],"hatch_scale"); old = cor.get("hatch_scale",4.0); cor["hatch_scale"] = v
        return state, f"Bay {name} corridor hatch_scale = {v}. Was {old}."
    raise ValueError("Corridor subcommands: on, off, axis, position, width, loading, hatch, hatch_scale")

# ══════════════════════════════════════════════════════════
# ROOM / BLOCK / HATCH / LEGEND / TACTILE3D
# ══════════════════════════════════════════════════════════

def cmd_room(state, tokens):
    if "rooms" not in state: state["rooms"] = _auto_rooms(state.get("bays",{}))
    rooms = state["rooms"]
    if len(tokens) < 2: raise ValueError("Usage: room list|refresh|add|remove|<id> [field] [value]")
    sub = tokens[1].lower()
    if sub == "list":
        if not rooms: return state, "No rooms. Try 'room refresh'."
        lines = [f"ROOMS: {len(rooms)} total",
                 "  ID                Type       Label                    Hatch",
                 "  " + "-" * 65]
        for rid in sorted(rooms):
            rm = rooms[rid]
            lines.append(f"  {rid:<18} {rm.get('type','bay'):<10} "
                         f"{rm.get('label','')[:24]:<24} "
                         f"{rm.get('hatch_image','none')} "
                         f"(x{rm.get('hatch_scale',1.0)})")
        return state, "\n".join(lines)
    if sub == "refresh":
        state["rooms"] = _auto_rooms(state.get("bays",{}))
        return state, f"Rooms refreshed: {len(state['rooms'])} rooms."
    if sub == "add":
        if len(tokens) < 4: raise ValueError("room add <id> bay|void|landscape [source_bay]")
        rid = tokens[2]
        if rid in rooms: raise ValueError(f"Room '{rid}' already exists.")
        rt = tokens[3].lower()
        if rt not in ("bay","void","landscape"): raise ValueError("Type must be bay, void, or landscape.")
        src = tokens[4].upper() if len(tokens) > 4 else None
        rooms[rid] = {"type": rt, "source_bay": src, "label": rid, "braille": "",
                      "hatch_image": "none", "hatch_scale": 1.0, "hatch_rotation": 0.0}
        return state, f"Room '{rid}' added (type={rt})."
    if sub == "remove":
        if len(tokens) != 3: raise ValueError("room remove <id>")
        rid = tokens[2]
        if rid not in rooms: raise ValueError(f"No room '{rid}'.")
        del rooms[rid]; return state, f"Room '{rid}' removed."
    # Direct room access by ID
    rid = tokens[1]
    if rid not in rooms: raise ValueError(f"No room '{rid}'. Try 'room list'.")
    rm = rooms[rid]
    if len(tokens) < 3:
        lines = [f"Room '{rid}':"]
        for k,v in rm.items(): lines.append(f"  {k}: {v}")
        return state, "\n".join(lines)
    field = tokens[2].lower()
    if field in ("label","braille"):
        raw = " ".join(tokens[3:])
        if raw.startswith('"') and raw.endswith('"'): raw = raw[1:-1]
        old = rm.get(field,""); rm[field] = raw
        return state, f"Room {rid} {field} = '{raw}'. Was '{old}'."
    if field == "hatch":
        v = tokens[3]; v = "none" if v.lower() in ("none","off") else v
        old = rm.get("hatch_image","none"); rm["hatch_image"] = v
        return state, f"Room {rid} hatch = {v}. Was {old}."
    if field == "hatch_scale":
        v = _float(tokens[3],"s"); old = rm.get("hatch_scale",1.0); rm["hatch_scale"] = v
        return state, f"Room {rid} hatch_scale = {v}. Was {old}."
    if field in ("hatch_rotation","hatch_rot"):
        v = _float(tokens[3],"deg"); old = rm.get("hatch_rotation",0.0); rm["hatch_rotation"] = v
        return state, f"Room {rid} hatch_rotation = {v} deg. Was {old} deg."
    raise ValueError("Room fields: label, braille, hatch, hatch_scale, hatch_rotation")

def cmd_cell(state, tokens):
    """Cell-room commands: cell <bay> list|rooms|clear_all|auto_corridor|<ref> ..."""
    if len(tokens) < 3:
        raise ValueError("Usage: cell <bay> list|rooms|clear_all|<col,row> [field] [value]")
    bay_name = tokens[1].upper()
    bays = state.get("bays", {})
    if bay_name not in bays:
        raise ValueError(f"No bay '{bay_name}'. Bays: {', '.join(sorted(bays))}.")
    bay = bays[bay_name]
    if bay.get("grid_type","rectangular") != "rectangular":
        raise ValueError("Cells are only available for rectangular bays.")
    nx, ny = bay["bays"]
    # Lazy-init cells
    if "cells" not in bay or not bay["cells"]:
        bay["cells"] = _init_cells(bay)
    cells = bay["cells"]
    sub = tokens[2].lower()

    # ── cell <bay> list ──
    if sub == "list":
        total = nx * ny
        lines = [f"Bay {bay_name} cells ({nx} across x {ny} deep = {total} cells):"]
        lines.append(f"  {'Cell':<8} {'Name':<24} {'Label':<20} {'Area':>10}  Hatch")
        lines.append("  " + "-" * 76)
        for r in range(ny):
            for c in range(nx):
                key = f"{c},{r}"
                cl = cells.get(key, {})
                nm = cl.get("name","") or "(unnamed)"
                lb = cl.get("label","") or ""
                area = _cell_area(bay, c, r)
                ht = cl.get("hatch","none")
                ht_s = ht if ht != "none" else ""
                lines.append(f"  {key:<8} {nm:<24} {lb:<20} {area:>8,.0f} sf  {ht_s}")
        return state, "\n".join(lines)

    # ── cell <bay> rooms ──
    if sub == "rooms":
        rooms = _room_summary(bay)
        if not rooms:
            return state, f"Bay {bay_name}: no cells defined."
        lines = [f"Bay {bay_name} rooms:"]
        lines.append(f"  {'Name':<24} {'Cells':>5}  {'Area':>10}")
        lines.append("  " + "-" * 44)
        grand_area = 0.0; grand_cells = 0
        for rname in sorted(rooms, key=lambda n: (n == "(unnamed)", n)):
            rd = rooms[rname]
            lines.append(f"  {rname:<24} {len(rd['cells']):>5}  "
                         f"{rd['area']:>8,.0f} sf")
            grand_area += rd["area"]; grand_cells += len(rd["cells"])
        lines.append("  " + "-" * 44)
        lines.append(f"  {'Total':<24} {grand_cells:>5}  {grand_area:>8,.0f} sf")
        return state, "\n".join(lines)

    # ── cell <bay> clear_all ──
    if sub == "clear_all":
        bay["cells"] = _init_cells(bay)
        return state, f"Bay {bay_name}: all {nx*ny} cells reset."

    # ── cell <bay> auto_corridor ──
    if sub == "auto_corridor":
        cor = bay.get("corridor", {})
        if not cor.get("enabled"):
            return state, f"Bay {bay_name} has no corridor enabled."
        cx_arr, cy_arr = _get_spacing_arrays(bay)
        axis = cor.get("axis","x"); pos = cor.get("position",1)
        half_w = cor.get("width",8.0) / 2.0
        count = 0
        if axis == "x":
            if pos >= len(cy_arr): raise ValueError(f"Corridor gridline {pos} out of range.")
            cor_lo = cy_arr[pos] - half_w
            cor_hi = cy_arr[pos] + half_w
            for c in range(nx):
                for r in range(ny):
                    cell_lo, cell_hi = cy_arr[r], cy_arr[r+1]
                    # Check if corridor zone overlaps this cell
                    if cell_hi > cor_lo and cell_lo < cor_hi:
                        key = f"{c},{r}"
                        cells[key]["name"] = "Corridor"
                        cells[key]["label"] = ""
                        count += 1
        else:
            if pos >= len(cx_arr): raise ValueError(f"Corridor gridline {pos} out of range.")
            cor_lo = cx_arr[pos] - half_w
            cor_hi = cx_arr[pos] + half_w
            for c in range(nx):
                for r in range(ny):
                    cell_lo, cell_hi = cx_arr[c], cx_arr[c+1]
                    if cell_hi > cor_lo and cell_lo < cor_hi:
                        key = f"{c},{r}"
                        cells[key]["name"] = "Corridor"
                        cells[key]["label"] = ""
                        count += 1
        # Set label on just one middle cell
        cor_cells = [(c,r) for c in range(nx) for r in range(ny)
                     if cells[f"{c},{r}"].get("name") == "Corridor"]
        if cor_cells:
            mid = cor_cells[len(cor_cells)//2]
            cells[f"{mid[0]},{mid[1]}"]["label"] = "Corridor"
        return state, f"Bay {bay_name}: {count} cells marked as Corridor."

    # ── cell <bay> <ref> clear ──
    # ── cell <bay> <ref> <field> <value> ──
    # ref can be single "2,1" or range "0,0-2,1"
    ref = tokens[2]
    try:
        targets = _expand_cell_range(ref, nx, ny)
    except ValueError as e:
        raise ValueError(str(e))
    if len(tokens) < 4:
        # Show info for single cell
        if len(targets) != 1:
            raise ValueError("Provide a field to set, e.g.: cell A 0,0 name \"Office\"")
        c, r = targets[0]
        key = f"{c},{r}"; cl = cells.get(key, {})
        area = _cell_area(bay, c, r)
        lines = [f"Cell {bay_name} {key} ({area:,.0f} sq ft):"]
        for k, v in cl.items():
            lines.append(f"  {k}: {v}")
        return state, "\n".join(lines)
    field = tokens[3].lower()
    if field == "clear":
        for c, r in targets:
            cells[f"{c},{r}"] = {
                "name": "", "label": "", "braille": "",
                "hatch": "none", "hatch_scale": 1.0, "hatch_rotation": 0.0}
        n = len(targets)
        return state, f"{n} cell{'s' if n > 1 else ''} cleared in bay {bay_name}."
    if len(tokens) < 5:
        raise ValueError(f"cell {bay_name} {ref} {field} <value>")
    if field in ("name","label","braille"):
        val = " ".join(tokens[4:])
        if val.startswith('"') and val.endswith('"'): val = val[1:-1]
        for c, r in targets:
            cells[f"{c},{r}"][field] = val
        n = len(targets)
        if n == 1:
            c, r = targets[0]
            return state, f"Cell {bay_name} {c},{r} {field} = \"{val}\"."
        total_area = sum(_cell_area(bay, c, r) for c, r in targets)
        return state, (f"{n} cells in bay {bay_name} {field} = \"{val}\". "
                       f"Combined area: {total_area:,.0f} sq ft.")
    if field == "hatch":
        val = tokens[4]; val = "none" if val.lower() in ("none","off") else val
        for c, r in targets:
            cells[f"{c},{r}"]["hatch"] = val
        n = len(targets)
        return state, f"{n} cell{'s' if n > 1 else ''} in bay {bay_name} hatch = {val}."
    if field == "hatch_scale":
        val = _float(tokens[4], "scale")
        for c, r in targets:
            cells[f"{c},{r}"]["hatch_scale"] = val
        return state, f"Cell{'s' if len(targets)>1 else ''} hatch_scale = {val}."
    if field in ("hatch_rotation","hatch_rot"):
        val = _float(tokens[4], "deg")
        for c, r in targets:
            cells[f"{c},{r}"]["hatch_rotation"] = val
        return state, f"Cell{'s' if len(targets)>1 else ''} hatch_rotation = {val} deg."
    raise ValueError("Cell fields: name, label, braille, hatch, hatch_scale, "
                     "hatch_rotation, clear")

def cmd_block(state, tokens):
    if "blocks" not in state: state["blocks"] = _default_blocks()
    blocks = state["blocks"]
    if len(tokens) < 2: raise ValueError("Usage: block list|door|window|portal|room [field] [value]")
    sub = tokens[1].lower()
    if sub == "list":
        lines = ["BLOCK SYMBOLS:"]
        for bt in sorted(blocks):
            bk = blocks[bt]
            lines.append(f"  {bt}:")
            for k,v in bk.items(): lines.append(f"    {k}: {v}")
        return state, "\n".join(lines)
    if sub not in blocks: raise ValueError(f"Block types: {', '.join(sorted(blocks))}")
    bk = blocks[sub]
    if len(tokens) < 3:
        lines = [f"Block '{sub}':"]
        for k,v in bk.items(): lines.append(f"  {k}: {v}")
        return state, "\n".join(lines)
    field = tokens[2].lower(); val = tokens[3] if len(tokens) > 3 else ""
    if field == "symbol":
        old = bk.get("symbol",""); bk["symbol"] = val
        return state, f"Block {sub} symbol = {val}. Was {old}."
    if field == "label":
        bk["show_label"] = val.lower() in ("on","true","yes","1")
        return state, f"Block {sub} show_label = {bk['show_label']}."
    if field == "label_height":
        v = _float(val,"h"); old = bk.get("label_height",1.5); bk["label_height"] = v
        return state, f"Block {sub} label_height = {v}. Was {old}."
    if field in ("tactile_weight","weight"):
        v = _float(val,"w"); old = bk.get("tactile_weight_mm",0.35); bk["tactile_weight_mm"] = v
        return state, f"Block {sub} tactile_weight = {v} mm. Was {old} mm."
    if field == "label_prefix":
        old = bk.get("label_prefix",""); bk["label_prefix"] = val
        return state, f"Block {sub} label_prefix = '{val}'. Was '{old}'."
    raise ValueError("Block fields: symbol, label, label_height, tactile_weight, label_prefix")

def cmd_hatch(state, tokens):
    if len(tokens) < 2: raise ValueError("Usage: hatch list|path|add")
    sub = tokens[1].lower()
    if sub == "list":
        hlp = state.get("hatch_library_path","./hatches/")
        if not os.path.isdir(hlp): return state, f"Folder not found: {hlp}\nUse 'hatch path <folder>'."
        imgs = _scan_hatch_folder(hlp)
        if not imgs: return state, f"No images in {hlp}."
        lines = [f"Hatch library: {hlp}  ({len(imgs)} images)"]
        for img in imgs:
            sz = os.path.getsize(os.path.join(hlp,img))
            lines.append(f"  {img:<30} {sz:>8} bytes")
        return state, "\n".join(lines)
    if sub == "path":
        if len(tokens) != 3: raise ValueError("hatch path <folder>")
        raw = tokens[2]
        if raw.startswith('"') and raw.endswith('"'): raw = raw[1:-1]
        old = state.get("hatch_library_path","./hatches/"); state["hatch_library_path"] = raw
        exists = os.path.isdir(raw); n = len(_scan_hatch_folder(raw)) if exists else 0
        return state, f"Hatch path = {raw}. Was {old}. {'Found' if exists else 'NOT FOUND'}: {n} images."
    if sub == "add":
        if len(tokens) < 4: raise ValueError("hatch add <name> <source_image_path>")
        hatch_name = tokens[2]; src_path = tokens[3]
        if src_path.startswith('"') and src_path.endswith('"'): src_path = src_path[1:-1]
        if not os.path.isfile(src_path): raise ValueError(f"Source file not found: {src_path}")
        ext = os.path.splitext(src_path)[1].lower()
        if ext not in IMAGE_EXTS: raise ValueError(f"Unsupported image format: {ext}. "
                                                    f"Supported: {', '.join(sorted(IMAGE_EXTS))}")
        hlp = state.get("hatch_library_path","./hatches/")
        os.makedirs(hlp, exist_ok=True)
        dest = os.path.join(hlp, hatch_name + ext)
        import shutil; shutil.copy2(src_path, dest)
        return state, f"Hatch '{hatch_name}' added: {dest}"
    raise ValueError("Hatch subcommands: list, path, add")

def cmd_legend(state, tokens):
    if "legend" not in state: state["legend"] = _default_legend()
    leg = state["legend"]
    if len(tokens) < 2: raise ValueError(
        "Usage: legend on|off|position|width|title|title_braille|"
        "show_braille|show_hatches|show_apertures|swatch_size|"
        "row_height|text_height|braille_height|padding|border_weight_mm")
    sub = tokens[1].lower()
    if sub == "on":  leg["enabled"] = True;  return state, "Legend ON."
    if sub == "off": leg["enabled"] = False; return state, "Legend OFF."
    if sub == "position":
        v = tokens[2].lower() if len(tokens) > 2 else ""
        valid = ("bottom-right","bottom-left","top-right","top-left","custom")
        if v not in valid: raise ValueError(f"Position options: {', '.join(valid)}")
        leg["position"] = v
        if v == "custom" and len(tokens) >= 5:
            leg["custom_origin"] = [_float(tokens[3],"x"), _float(tokens[4],"y")]
        return state, f"Legend position = {v}."
    if sub in ("title","title_braille"):
        raw = " ".join(tokens[2:])
        if raw.startswith('"') and raw.endswith('"'): raw = raw[1:-1]
        old = leg.get(sub,""); leg[sub] = raw
        return state, f"Legend {sub} = '{raw}'. Was '{old}'."
    if sub == "width":
        v = _float(tokens[2],"w"); old = leg.get("width",40); leg["width"] = v
        return state, f"Legend width = {v} ft. Was {old} ft."
    bool_fields = {"show_braille","show_hatches","show_apertures"}
    if sub in bool_fields:
        v = tokens[2].lower() if len(tokens) > 2 else "on"
        leg[sub] = v in ("on","true","yes","1")
        return state, f"Legend {sub} = {leg[sub]}."
    num_fields = {"swatch_size","row_height","text_height","braille_height",
                  "padding","border_weight_mm"}
    if sub in num_fields:
        v = _float(tokens[2], sub); old = leg.get(sub, 0); leg[sub] = v
        return state, f"Legend {sub} = {v}. Was {old}."
    raise ValueError("Legend subcommands: on, off, position, width, title, title_braille, "
                     "show_braille, show_hatches, show_apertures, swatch_size, "
                     "row_height, text_height, braille_height, padding, border_weight_mm")

def cmd_tactile3d(state, tokens):
    """Configure the tactile 3D print mode."""
    if "tactile3d" not in state: state["tactile3d"] = _default_tactile3d()
    t3 = state["tactile3d"]
    if len(tokens) < 2: raise ValueError(
        "Usage: tactile3d on|off|wall_height|cut_height|floor_thickness|"
        "floor|auto_export|export_path|scale_factor|export")
    sub = tokens[1].lower()
    if sub == "on":
        t3["enabled"] = True
        return state, (f"Tactile 3D ON. Walls extruded to {t3['wall_height']} ft, "
                       f"clipped at {t3['cut_height']} ft.")
    if sub == "off":
        t3["enabled"] = False; return state, "Tactile 3D OFF."
    if sub == "wall_height":
        v = _float(tokens[2],"h")
        if v <= 0: raise ValueError("Must be > 0.")
        old = t3.get("wall_height",9.0); t3["wall_height"] = v
        return state, f"Tactile3D wall_height = {v} ft. Was {old} ft."
    if sub == "cut_height":
        v = _float(tokens[2],"h")
        if v <= 0: raise ValueError("Must be > 0.")
        old = t3.get("cut_height",4.0); t3["cut_height"] = v
        return state, f"Tactile3D cut_height = {v} ft. Was {old} ft."
    if sub == "floor_thickness":
        v = _float(tokens[2],"t")
        if v <= 0: raise ValueError("Must be > 0.")
        old = t3.get("floor_thickness",0.5); t3["floor_thickness"] = v
        return state, f"Tactile3D floor_thickness = {v} ft. Was {old} ft."
    if sub == "floor":
        v = tokens[2].lower() if len(tokens) > 2 else "on"
        t3["floor_enabled"] = v in ("on","true","yes","1")
        return state, f"Tactile3D floor = {'ON' if t3['floor_enabled'] else 'OFF'}."
    if sub == "auto_export":
        v = tokens[2].lower() if len(tokens) > 2 else "off"
        t3["auto_export"] = v in ("on","true","yes","1")
        return state, f"Tactile3D auto_export = {'ON' if t3['auto_export'] else 'OFF'}."
    if sub == "export_path":
        raw = tokens[2]
        if raw.startswith('"') and raw.endswith('"'): raw = raw[1:-1]
        old = t3.get("export_path",""); t3["export_path"] = raw
        return state, f"Tactile3D export_path = {raw}. Was {old}."
    if sub == "scale_factor":
        v = _float(tokens[2],"s")
        if v <= 0: raise ValueError("Must be > 0.")
        old = t3.get("scale_factor",1.0); t3["scale_factor"] = v
        return state, f"Tactile3D scale_factor = {v}. Was {old}."
    if sub == "export":
        # Trigger a one-time export on next redraw
        t3["_export_once"] = True
        return state, f"Tactile3D export queued to: {t3.get('export_path','./tactile3d_export.stl')}"
    raise ValueError("Tactile3D subcommands: on, off, wall_height, cut_height, "
                     "floor_thickness, floor, auto_export, export_path, scale_factor, export")


def cmd_bambu(state, tokens):
    """Configure and operate the Bambu 3D printer pipeline.

    Subcommands:
        config <field> <value>   Set printer configuration
        preview                  Show model dimensions and fit check
        export [path]            Build mesh and write binary STL
        slice                    Export STL then slice to 3MF
        send [path]              Upload 3MF to printer and start print
        print                    Full pipeline: export → slice → send
        status                   Poll printer for current status
    """
    if "bambu" not in state:
        state["bambu"] = _default_bambu()
    bam = state["bambu"]
    if len(tokens) < 2:
        raise ValueError(
            "Usage: bambu config|preview|export|slice|send|print|status")

    sub = tokens[1].lower()

    # ── config ──
    if sub in ("config", "cfg", "set"):
        if len(tokens) < 4:
            raise ValueError(
                "bambu config <field> <value>\n"
                "  Fields: ip, access_code, serial, printer_model,\n"
                "          print_scale, stl_path, slicer_path")
        field = tokens[2].lower()
        val = tokens[3]
        alias = {"printer_ip": "ip", "access": "access_code",
                 "code": "access_code", "model": "printer_model",
                 "scale": "print_scale", "stl": "stl_path",
                 "slicer": "slicer_path"}
        field = alias.get(field, field)
        if field == "ip":
            old = bam.get("printer_ip", ""); bam["printer_ip"] = val
            return state, f"Bambu printer_ip = {val}. Was '{old}'."
        if field == "access_code":
            bam["access_code"] = val
            return state, "Bambu access_code set."
        if field == "serial":
            old = bam.get("serial_number", ""); bam["serial_number"] = val
            return state, f"Bambu serial = {val}. Was '{old}'."
        if field == "printer_model":
            val_l = val.lower().replace("-", "_").replace(" ", "_")
            bam["printer_model"] = val_l
            return state, f"Bambu printer_model = {val_l}."
        if field == "print_scale":
            v = _int_pos(val, "print_scale")
            old = bam.get("print_scale", 200); bam["print_scale"] = v
            return state, f"Bambu print_scale = 1:{v}. Was 1:{old}."
        if field == "stl_path":
            old = bam.get("stl_path", ""); bam["stl_path"] = val
            return state, f"Bambu stl_path = {val}. Was '{old}'."
        if field == "slicer_path":
            old = bam.get("slicer_path", ""); bam["slicer_path"] = val
            return state, f"Bambu slicer_path = {val}. Was '{old}'."
        raise ValueError(
            "Unknown bambu config field. Options: ip, access_code, serial, "
            "printer_model, print_scale, stl_path, slicer_path")

    # ── All other subcommands need tactile_print module ──
    try:
        import tactile_print as tp
    except ImportError:
        raise RuntimeError(
            "tactile_print.py not found. Place it in the same folder as "
            "this controller to enable mesh generation and printing.")

    if sub == "preview":
        return state, tp.preview(state, bam)

    if sub == "export":
        path = tokens[2] if len(tokens) > 2 else None
        msg = tp.do_export(state, path)
        return state, msg

    if sub == "slice":
        msg = tp.do_slice(state)
        return state, msg

    if sub == "send":
        path = tokens[2] if len(tokens) > 2 else None
        msg = tp.do_send(state, path)
        return state, msg

    if sub in ("print", "go"):
        msg = tp.do_print(state)
        return state, msg

    if sub == "status":
        msg = tp.do_status(state)
        return state, msg

    raise ValueError(
        "Bambu subcommands: config, preview, export, slice, send, print, status")

# ══════════════════════════════════════════════════════════
# SET COMMANDS
# ══════════════════════════════════════════════════════════

def _cmd_set_site(state, tokens):
    if len(tokens) != 4: raise ValueError("set site width|height <value>")
    f = tokens[2].lower()
    if f not in ("width","height"): raise ValueError("width or height.")
    v = _float(tokens[3],f)
    if v <= 0: raise ValueError("Must be > 0.")
    old = state["site"][f]; state["site"][f] = v
    return state, f"Site {f} = {v} ft. Was {old} ft."

def _cmd_set_column(state, tokens):
    if len(tokens) != 4 or tokens[2].lower() != "size": raise ValueError("set column size <value>")
    v = _float(tokens[3],"size")
    if v <= 0: raise ValueError("Must be > 0.")
    old = state["style"]["column_size"]; state["style"]["column_size"] = v
    return state, f"Column size = {v} ft. Was {old} ft."

def _cmd_set_style(state, tokens):
    if len(tokens) != 4: raise ValueError("set style <field> <value>")
    f = tokens[2].lower()
    m = {"heavy":"heavy_lineweight_mm","light":"light_lineweight_mm",
         "corridor":"corridor_lineweight_mm","wall":"wall_lineweight_mm",
         "text_height":"label_text_height","braille_height":"braille_text_height",
         "dash_len":"corridor_dash_len","gap_len":"corridor_gap_len",
         "bg_pad":"background_pad","label_offset":"label_offset",
         "arc_segments":"arc_segments"}
    if f not in m: raise ValueError(f"Style fields: {', '.join(sorted(m))}")
    v = _float(tokens[3],f); old = state["style"].get(m[f],0); state["style"][m[f]] = v
    return state, f"Style {f} = {v}. Was {old}."

def _cmd_set_print(state, tokens):
    if len(tokens) != 4: raise ValueError("set print scale|paper|margin|dpi|format <value>")
    f = tokens[2].lower(); pr = state.setdefault("print", _default_print())
    if f == "scale":
        v = _float(tokens[3],"scale")
        if v <= 0: raise ValueError("Must be > 0.")
        old = pr.get("scale_ft_per_inch",8); pr["scale_ft_per_inch"] = v
        return state, f"Print scale = {_scale_label(v)}. Was {_scale_label(old)}."
    if f == "paper":
        raw = tokens[3]
        if "x" not in raw.lower(): raise ValueError('Format: WxH (e.g. 24x36)')
        parts = raw.lower().split("x"); w = _float(parts[0],"w"); h = _float(parts[1],"h")
        pr["paper_width_in"] = w; pr["paper_height_in"] = h
        return state, f'Paper = {w} x {h} inches.'
    if f == "margin":
        v = _float(tokens[3],"margin"); pr["margin_in"] = v
        return state, f'Margin = {v} inches.'
    if f == "dpi":
        v = _int_pos(tokens[3],"dpi"); pr["dpi"] = v; return state, f"DPI = {v}."
    if f == "format":
        v = tokens[3].lower()
        if v not in ("png","jpg"): raise ValueError("png or jpg.")
        pr["format"] = v; return state, f"Format = {v}."
    raise ValueError("Print fields: scale, paper, margin, dpi, format")

def _cmd_set_bay(state, tokens):
    if len(tokens) < 5: raise ValueError("set bay <name> <field> <value(s)>")
    name = tokens[2].upper()
    if name not in state["bays"]:
        raise ValueError(f"No bay '{name}'. Have: {', '.join(sorted(state['bays']))}")
    bay = state["bays"][name]; f = tokens[3].lower()
    if f == "grid_type":
        v = tokens[4].lower()
        v = "rectangular" if v in ("rect","rectangular") else ("radial" if v in ("rad","radial") else None)
        if not v: raise ValueError("rectangular or radial.")
        old = bay.get("grid_type","rectangular"); bay["grid_type"] = v
        return state, f"Bay {name} grid_type = {v}. Was {old}."
    if f == "z_order":
        v = _int_nn(tokens[4],"z"); old = bay.get("z_order",0); bay["z_order"] = v
        return state, f"Bay {name} z_order = {v}. Was {old}."
    if f == "origin":
        if len(tokens) < 6: raise ValueError("set bay <n> origin <x> <y>")
        old = list(bay["origin"]); bay["origin"] = [_float(tokens[4],"x"), _float(tokens[5],"y")]
        return state, f"Bay {name} origin = {_fmt(bay['origin'])}. Was {_fmt(old)}."
    if f == "rotation":
        old = bay["rotation_deg"]; bay["rotation_deg"] = _float(tokens[4],"r")
        return state, f"Bay {name} rotation = {bay['rotation_deg']} deg. Was {old} deg."
    if f == "bays":
        if len(tokens) < 6: raise ValueError("set bay <n> bays <nx> <ny>")
        old = list(bay["bays"]); bay["bays"] = [_int_pos(tokens[4],"nx"), _int_pos(tokens[5],"ny")]
        bay["spacing_x"] = None; bay["spacing_y"] = None
        return state, f"Bay {name} bays = {bay['bays']}. Was {old}."
    if f == "spacing":
        if len(tokens) < 6: raise ValueError("set bay <n> spacing <sx> <sy>")
        sx = _float(tokens[4],"sx"); sy = _float(tokens[5],"sy")
        if sx <= 0 or sy <= 0: raise ValueError("Spacing must be > 0.")
        old = list(bay["spacing"]); bay["spacing"] = [sx,sy]
        bay["spacing_x"] = None; bay["spacing_y"] = None
        return state, f"Bay {name} spacing = {sx} x {sy} ft. Was {old[0]} x {old[1]} ft."
    if f == "spacing_x":
        nx = bay["bays"][0]; vals = tokens[4:]
        if len(vals) != nx: raise ValueError(f"Need {nx} values (one per bay span), got {len(vals)}.")
        arr = [_float(v,f"sx[{i}]") for i,v in enumerate(vals)]
        bay["spacing_x"] = arr
        return state, f"Bay {name} spacing_x = {arr}."
    if f == "spacing_y":
        ny = bay["bays"][1]; vals = tokens[4:]
        if len(vals) != ny: raise ValueError(f"Need {ny} values (one per bay span), got {len(vals)}.")
        arr = [_float(v,f"sy[{i}]") for i,v in enumerate(vals)]
        bay["spacing_y"] = arr
        return state, f"Bay {name} spacing_y = {arr}."
    if f == "rings":
        v = _int_pos(tokens[4],"r"); old = bay.get("rings",4); bay["rings"] = v
        return state, f"Bay {name} rings = {v}. Was {old}."
    if f == "ring_spacing":
        v = _float(tokens[4],"rs")
        if v <= 0: raise ValueError("Must be > 0.")
        old = bay.get("ring_spacing",20); bay["ring_spacing"] = v
        return state, f"Bay {name} ring_spacing = {v} ft. Was {old} ft."
    if f == "arms":
        v = _int_pos(tokens[4],"a"); old = bay.get("arms",8); bay["arms"] = v
        return state, f"Bay {name} arms = {v}. Was {old}."
    if f == "arc_deg":
        v = _float(tokens[4],"d"); old = bay.get("arc_deg",360); bay["arc_deg"] = v
        return state, f"Bay {name} arc_deg = {v}. Was {old}."
    if f == "arc_start_deg":
        v = _float(tokens[4],"d"); old = bay.get("arc_start_deg",0); bay["arc_start_deg"] = v
        return state, f"Bay {name} arc_start_deg = {v}. Was {old}."
    if f == "wall_height":
        v = _float(tokens[4],"h")
        if v <= 0: raise ValueError("wall_height must be > 0.")
        old = bay.get("wall_height",10.0); bay["wall_height"] = v
        return state, f"Bay {name} wall_height = {v} ft. Was {old} ft."
    if f == "void_center":
        if len(tokens) < 6: raise ValueError("set bay <n> void_center <x> <y>")
        old = list(bay["void_center"]); bay["void_center"] = [_float(tokens[4],"x"), _float(tokens[5],"y")]
        return state, f"Bay {name} void_center = {_fmt(bay['void_center'])}. Was {_fmt(old)}."
    if f == "void_size":
        if len(tokens) < 6: raise ValueError("set bay <n> void_size <w> <h>")
        w = _float(tokens[4],"w"); h = _float(tokens[5],"h")
        if w <= 0 or h <= 0: raise ValueError("Size must be > 0.")
        old = list(bay["void_size"]); bay["void_size"] = [w,h]
        return state, f"Bay {name} void_size = {w} x {h} ft. Was {old[0]} x {old[1]} ft."
    if f == "void_shape":
        v = tokens[4].lower()
        v = "rectangle" if v in ("rect","rectangle") else ("circle" if v in ("circ","circle") else None)
        if not v: raise ValueError("rectangle or circle.")
        old = bay.get("void_shape","rectangle"); bay["void_shape"] = v
        return state, f"Bay {name} void_shape = {v}. Was {old}."
    if f in ("label","braille"):
        raw = " ".join(tokens[4:])
        if raw.startswith('"') and raw.endswith('"'): raw = raw[1:-1]
        old = bay.get(f,""); bay[f] = raw
        return state, f"Bay {name} {f} = '{raw}'. Was '{old}'."
    raise ValueError("Bay fields: grid_type, z_order, origin, rotation, bays, spacing, "
                     "spacing_x, spacing_y, rings, ring_spacing, arms, arc_deg, "
                     "arc_start_deg, wall_height, void_center, void_size, void_shape, label, braille")

# ══════════════════════════════════════════════════════════
# SECTION CUT
# ══════════════════════════════════════════════════════════

def cmd_section(state, tokens):
    """Section cut commands: section x|y <offset>, preview, export, list, clear."""
    if "section" not in state:
        state["section"] = _default_section()
    sec = state["section"]
    if len(tokens) < 2:
        raise ValueError("Usage: section x|y <offset> | preview | export [path] | list | clear")
    sub = tokens[1].lower()

    if sub in ("x", "y"):
        if len(tokens) < 3:
            raise ValueError(f"section {sub} <offset>")
        offset = _float(tokens[2], "offset")
        sec["axis"] = sub
        sec["offset"] = offset
        return state, f"OK: Section cut set to {sub.upper()}={offset:.1f} ft."

    if sub == "list":
        if sec["axis"] is None:
            return state, "Section cut: not defined. Use 'section x|y <offset>'."
        msg = (f"Section cut: {sec['axis'].upper()}={sec['offset']:.1f} ft")
        if sec.get("last_export_path"):
            msg += f"\n  Last export: {sec['last_export_path']}"
        return state, msg

    if sub == "clear":
        sec["axis"] = None
        sec["offset"] = None
        sec["last_export_path"] = None
        return state, "OK: Section cut cleared."

    if sub in ("preview", "export"):
        if sec["axis"] is None:
            raise ValueError("No section cut defined. Use 'section x|y <offset>' first.")
        try:
            import tactile_print as tp
        except ImportError:
            raise RuntimeError(
                "tactile_print.py not found. Place it in the same folder.")
        triangles = tp.build_mesh(state)
        if not triangles:
            raise RuntimeError("No mesh geometry. Enable walls on at least one bay.")
        segments = tp.section_cut(triangles, sec["axis"], sec["offset"])

        if sub == "preview":
            if not segments:
                return state, (f"Section {sec['axis'].upper()}={sec['offset']:.1f}: "
                               f"0 segments. Plane misses all geometry.")
            all_u = [p[0] for s in segments for p in s]
            all_v = [p[1] for s in segments for p in s]
            u_ext = max(all_u) - min(all_u)
            v_ext = max(all_v) - min(all_v)
            return state, (f"Section {sec['axis'].upper()}={sec['offset']:.1f}: "
                           f"{len(segments)} segments, "
                           f"extent {u_ext:.1f} x {v_ext:.1f} ft.")

        # export
        path = tokens[2] if len(tokens) > 2 else None
        if path is None:
            path = f"./section_{sec['axis']}_{sec['offset']:.0f}.svg"

        title = f"Section {sec['axis'].upper()}={sec['offset']:.1f} ft"
        svg = tp.section_to_svg(segments, title=title)
        _atomic_write(path, svg)
        sec["last_export_path"] = path
        return state, (f"OK: Section exported — {len(segments)} segments to {path}")

    raise ValueError("Section subcommands: x|y <offset>, preview, export [path], list, clear")

# ══════════════════════════════════════════════════════════
# HISTORY & SNAPSHOTS
# ══════════════════════════════════════════════════════════

def cmd_history(state, tokens, state_file=None):
    """History commands: history list|count."""
    if len(tokens) < 2:
        raise ValueError("Usage: history list|count")
    sub = tokens[1].lower()
    if sub == "count":
        n = _history_count(state_file) if state_file else 0
        return state, f"History: {n} entries."
    if sub == "list":
        if not state_file:
            return state, "History not available (no state file)."
        numbered, snapshots = _history_list(state_file)
        lines = [f"History: {len(numbered)} entries, {len(snapshots)} snapshots."]
        if numbered:
            show = numbered[-20:]  # last 20
            if len(numbered) > 20:
                lines.append(f"  (showing last 20 of {len(numbered)})")
            for f in show:
                seq = f[:4]
                lines.append(f"  {seq}: {f}")
        if snapshots:
            lines.append("Named snapshots:")
            for f in snapshots:
                name = f[9:-5]  # strip snapshot_ and .json
                lines.append(f"  {name}")
        return state, "\n".join(lines)
    raise ValueError("History subcommands: list, count")

def cmd_snapshot(state, tokens, state_file=None):
    """Snapshot commands: snapshot save|load|list <name>."""
    if len(tokens) < 2:
        raise ValueError("Usage: snapshot save|load|list <name>")
    sub = tokens[1].lower()
    if sub == "list":
        if not state_file:
            return state, "Snapshots not available (no state file)."
        _, snapshots = _history_list(state_file)
        if not snapshots:
            return state, "No named snapshots. Use 'snapshot save <name>' to create one."
        lines = [f"Named snapshots ({len(snapshots)}):"]
        for f in snapshots:
            name = f[9:-5]
            fpath = os.path.join(_history_dir(state_file), f)
            sz = os.path.getsize(fpath)
            mt = time.ctime(os.path.getmtime(fpath))
            lines.append(f"  {name}  ({sz:,} bytes, {mt})")
        return state, "\n".join(lines)
    if sub == "save":
        if len(tokens) < 3:
            raise ValueError("snapshot save <name>")
        name = tokens[2]
        if not state_file:
            raise ValueError("Cannot save snapshot (no state file).")
        fpath = _snapshot_save(state_file, state, name)
        return state, f"OK: Snapshot '{name}' saved to {fpath}."
    if sub == "load":
        if len(tokens) < 3:
            raise ValueError("snapshot load <name>")
        name = tokens[2]
        if not state_file:
            raise ValueError("Cannot load snapshot (no state file).")
        loaded = _snapshot_load(state_file, name)
        return loaded, f"OK: Snapshot '{name}' loaded."
    raise ValueError("Snapshot subcommands: save, load, list")

# ══════════════════════════════════════════════════════════
# TTS
# ══════════════════════════════════════════════════════════

def cmd_tts(state, tokens):
    """Text-to-speech control: tts [on|off|rate <-10..10>]."""
    if "tts" not in state:
        state["tts"] = _default_tts()
    tts = state["tts"]
    if len(tokens) < 2:
        status = "ON" if tts["enabled"] else "OFF"
        return state, f"TTS: {status}, rate={tts['rate']}."
    sub = tokens[1].lower()
    if sub == "on":
        tts["enabled"] = True
        return state, "OK: TTS enabled."
    if sub == "off":
        tts["enabled"] = False
        return state, "OK: TTS disabled."
    if sub == "rate":
        if len(tokens) < 3:
            raise ValueError("tts rate <-10..10>")
        v = int(tokens[2])
        if v < -10 or v > 10:
            raise ValueError("Rate must be between -10 and 10.")
        old = tts["rate"]
        tts["rate"] = v
        return state, f"OK: TTS rate = {v}. Was {old}."
    raise ValueError("TTS subcommands: on, off, rate <-10..10>")

# ══════════════════════════════════════════════════════════
# SETUP (Rhino auto-launch)
# ══════════════════════════════════════════════════════════

# Default Rhino install locations (Windows)
_RHINO_SEARCH_PATHS = [
    r"C:\Program Files\Rhino 8\System\Rhino.exe",
    r"C:\Program Files\Rhino 7\System\Rhino.exe",
    r"C:\Program Files (x86)\Rhino 8\System\Rhino.exe",
]

def _find_rhino():
    """Return the Rhino executable path if found, else None."""
    for p in _RHINO_SEARCH_PATHS:
        if os.path.isfile(p):
            return p
    return None

def _rhino_is_connected():
    """Quick TCP check: is the watcher listening on port 1998?"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(("127.0.0.1", 1998))
        s.sendall(b'{"type":"ping"}\n')
        buf = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b"\n" in buf:
                break
        s.close()
        import json as _json
        resp = _json.loads(buf.strip())
        return resp.get("status") == "ok"
    except Exception:
        return False

def cmd_setup(state, tokens, state_file):
    """Handle the 'setup' command family.

    setup rhino            — launch Rhino with the watcher auto-loaded
    setup rhino --path <p> — specify Rhino executable path and launch
    setup status           — check if the watcher is reachable
    """
    if len(tokens) < 2:
        raise ValueError(
            "Usage: setup rhino [--path <exe>]  |  setup status")
    sub = tokens[1].lower()

    if sub == "status":
        if _rhino_is_connected():
            return state, "OK: Rhino watcher is connected on 127.0.0.1:1998."
        return state, "OFFLINE: Rhino watcher is not responding on 127.0.0.1:1998."

    if sub != "rhino":
        raise ValueError(
            "Unknown setup target: '{}'. Options: rhino, status".format(sub))

    # Determine Rhino path
    rhino_path = None
    for i, t in enumerate(tokens):
        if t == "--path" and i + 1 < len(tokens):
            rhino_path = tokens[i + 1]
            break
    if rhino_path is None:
        rhino_path = _find_rhino()
    if rhino_path is None or not os.path.isfile(rhino_path):
        return state, (
            "ERROR: Rhino not found. Use: setup rhino --path "
            "\"C:\\Program Files\\Rhino 8\\System\\Rhino.exe\"")

    # Build watcher path
    watcher_path = os.path.join(_script_dir(), "rhino", "rhino_watcher.py")
    if not os.path.isfile(watcher_path):
        return state, (
            "ERROR: Watcher not found at {}.".format(watcher_path))

    # Build command: launch Rhino, auto-run the watcher script,
    # and set units to Feet.
    run_cmds = (
        '_-RunPythonScript "{}"'
        " _-DocumentProperties _Units _ModelUnits _Feet _Enter _Enter"
    ).format(watcher_path.replace("\\", "/"))

    try:
        subprocess.Popen(
            [rhino_path, "/nosplash",
             "/runscript={}".format(run_cmds)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
    except Exception as e:
        return state, "ERROR: Failed to launch Rhino: {}".format(e)

    # Poll for connection (up to 30 seconds)
    lines = [
        "OK: Launching Rhino with watcher...",
        "  Rhino: {}".format(rhino_path),
        "  Watcher: {}".format(watcher_path),
        "  Waiting for connection on 127.0.0.1:1998...",
    ]
    import time as _time
    connected = False
    for _ in range(15):
        _time.sleep(2)
        if _rhino_is_connected():
            connected = True
            break
    if connected:
        lines.append("OK: Connected. Rhino is ready. Units: Feet.")
    else:
        lines.append(
            "WAITING: Rhino launched but watcher not yet responding. "
            "Check Rhino is open and try 'setup status' in a moment.")
    return state, "\n".join(lines)

# ══════════════════════════════════════════════════════════
# STYLE COMMANDS
# ══════════════════════════════════════════════════════════

# Module-level style manager, initialized lazily
_style_mgr = None

def _get_style_manager():
    """Get or create the singleton StyleManager instance."""
    global _style_mgr
    if _style_mgr is None:
        import style_manager as _sm
        _style_mgr = _sm.StyleManager()
    return _style_mgr


def cmd_style(state, tokens, state_file=None):
    """Handle all style subcommands."""
    if len(tokens) < 2:
        raise ValueError("Usage: style use|list|show|set|save|reset|test|add-hatch|remove-hatch")
    sub = tokens[1].lower()
    mgr = _get_style_manager()

    if sub == "use":
        if len(tokens) < 3:
            raise ValueError("Usage: style use <name>")
        name, desc = mgr.use(tokens[2])
        return state, f'OK: Style "{name}" active. {desc}'

    if sub == "list":
        styles = mgr.list_styles()
        lines = [f"OK: {len(styles)} styles available:"]
        for i, (name, desc, active) in enumerate(styles, 1):
            marker = " (active)" if active else ""
            lines.append(f"  {i}. {name}{marker}")
        return state, "\n".join(lines)

    if sub == "show":
        cat = tokens[2].lower() if len(tokens) >= 3 else None
        result = mgr.show(cat)
        return state, f"OK: {result}"

    if sub == "set":
        if len(tokens) < 4:
            raise ValueError("Usage: style set <key.path> <value>")
        key = tokens[2]
        value = " ".join(tokens[3:])
        new_val, old_val = mgr.set(key, value)
        # Determine unit suffix
        parts = key.split(".")
        unit = ""
        if "lineweights" in parts or key.endswith("_pt"):
            unit = " pt"
        elif key.endswith("_mm") or key.endswith("spacing_mm"):
            unit = " mm"
        elif key.endswith("_inches"):
            unit = " in"
        elif key.endswith("_percent"):
            unit = "%"
        short_key = parts[-1]
        return state, f"OK: {short_key} = {new_val}{unit}. Was {old_val}{unit}."

    if sub == "save":
        name = tokens[2] if len(tokens) >= 3 else None
        path = mgr.save(name)
        save_name = name or mgr.active_name
        return state, f'OK: Saved style "{save_name}" to {os.path.basename(path)}.'

    if sub == "reset":
        name = mgr.reset()
        return state, f'OK: Style "{name}" reset to saved state.'

    if sub == "test":
        out_dir = os.path.dirname(os.path.abspath(state_file)) if state_file else "."
        out_path = os.path.join(out_dir, "style_test.png")
        # Try PDF first
        try:
            from reportlab.pdfgen import canvas as _c  # noqa: F401
            out_path = os.path.join(out_dir, "style_test.pdf")
        except ImportError:
            pass
        result_path = mgr.generate_test_swatch(out_path)
        paper = mgr.get("layout.paper", "letter")
        return state, f"OK: Rendered {os.path.basename(result_path)} ({paper.title()}, all lineweights and hatches at current settings)."

    if sub == "add-hatch":
        if len(tokens) < 5:
            raise ValueError("Usage: style add-hatch <name> <spacing_mm> <angle_deg> [weight_pt]")
        hname = tokens[2]
        spacing = float(tokens[3])
        angle = float(tokens[4])
        weight = float(tokens[5]) if len(tokens) >= 6 else 0.4
        mgr.add_hatch(hname, spacing, angle, weight)
        return state, f'OK: Added hatch "{hname}" (spacing {spacing:.1f} mm, angle {angle:.0f} deg, weight {weight:.1f} pt).'

    if sub == "remove-hatch":
        if len(tokens) < 3:
            raise ValueError("Usage: style remove-hatch <name>")
        hname = tokens[2]
        mgr.remove_hatch(hname)
        return state, f'OK: Removed hatch "{hname}".'

    raise ValueError(f"Unknown style subcommand: '{sub}'. Options: use, list, show, set, save, reset, test, add-hatch, remove-hatch")


# ══════════════════════════════════════════════════════════
# VIEW COMMANDS
# ══════════════════════════════════════════════════════════

def _get_view_renderer():
    """Import and return the state renderer and pdf generator."""
    _swell_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "..", "tools", "swell-print")
    if os.path.isdir(_swell_dir) and _swell_dir not in sys.path:
        sys.path.insert(0, _swell_dir)
    import state_renderer as _sr
    return _sr


def _parse_view_opts(tokens, start=2):
    """Parse --style, --paper, --scale flags from tokens."""
    opts = {}
    i = start
    while i < len(tokens):
        if tokens[i] == "--style" and i + 1 < len(tokens):
            opts["style"] = tokens[i + 1]; i += 2
        elif tokens[i] == "--paper" and i + 1 < len(tokens):
            opts["paper"] = tokens[i + 1]; i += 2
        elif tokens[i] == "--scale" and i + 1 < len(tokens):
            opts["scale"] = tokens[i + 1]; i += 2
        elif tokens[i] == "--hidden":
            opts["hidden"] = True; i += 1
        else:
            i += 1
    return opts


def cmd_view(state, tokens, state_file=None):
    """Handle view subcommands: plan, section, axon, elevation."""
    if len(tokens) < 2:
        raise ValueError("Usage: view plan|section|axon|elevation")
    sub = tokens[1].lower()
    mgr = _get_style_manager()
    sr = _get_view_renderer()
    out_dir = os.path.dirname(os.path.abspath(state_file)) if state_file else "."

    if sub == "plan":
        opts = _parse_view_opts(tokens, 2)
        if opts.get("style"):
            mgr.use(opts["style"])
        paper = opts.get("paper", mgr.get("layout.paper", "letter"))
        dpi = 300
        margin = mgr.get("layout.margin_inches", 0.5)
        img = sr.render(state, dpi=dpi, paper_size=paper, margin_in=margin,
                        style_manager=mgr)
        out_path = os.path.join(out_dir, "plan.png")
        img.save(out_path, dpi=(dpi, dpi))
        dens = sr.density(img)
        return state, f"OK: Rendered plan.png ({paper.title()}, {dpi} DPI, density {dens:.1f}%)"

    if sub == "section":
        if len(tokens) < 4:
            raise ValueError("Usage: view section <x|y> <gridline> [--style name]")
        axis = tokens[2].lower()
        gridline = int(tokens[3])
        opts = _parse_view_opts(tokens, 4)
        if opts.get("style"):
            mgr.use(opts["style"])
        paper = opts.get("paper", mgr.get("layout.paper", "letter"))
        dpi = 300

        img = _render_section(state, axis, gridline, mgr, dpi, paper)
        out_name = f"section_{axis}{gridline}.png"
        out_path = os.path.join(out_dir, out_name)
        img.save(out_path, dpi=(dpi, dpi))
        dens = sr.density(img)
        return state, f"OK: Rendered {out_name} (section cut at {axis}-gridline {gridline}, density {dens:.1f}%)"

    if sub == "axon":
        # Parse optional angles
        opts = _parse_view_opts(tokens, 2)
        angle1 = 30.0
        angle2 = 60.0
        # Look for numeric args before flags
        non_flag_args = []
        i = 2
        while i < len(tokens):
            if tokens[i].startswith("--"):
                break
            try:
                non_flag_args.append(float(tokens[i]))
            except ValueError:
                pass
            i += 1
        if len(non_flag_args) >= 2:
            angle1, angle2 = non_flag_args[0], non_flag_args[1]
        elif len(non_flag_args) == 1:
            angle1 = non_flag_args[0]

        if opts.get("style"):
            mgr.use(opts["style"])
        paper = opts.get("paper", mgr.get("layout.paper", "letter"))
        hidden = opts.get("hidden", False)
        dpi = 300

        img = _render_axon(state, angle1, angle2, hidden, mgr, dpi, paper)
        suffix = "_hidden" if hidden else ""
        out_name = f"axon{suffix}.png"
        out_path = os.path.join(out_dir, out_name)
        img.save(out_path, dpi=(dpi, dpi))
        dens = sr.density(img)
        proj_type = "isometric" if angle1 == 45 and angle2 == 45 else f"{angle1:.0f}/{angle2:.0f} projection"
        line_type = "hidden-line" if hidden else "wireframe"
        return state, f"OK: Rendered {out_name} ({proj_type}, {line_type}, density {dens:.1f}%)"

    if sub == "elevation":
        if len(tokens) < 3:
            raise ValueError("Usage: view elevation <north|south|east|west> [--style name]")
        direction = tokens[2].lower()
        if direction not in ("north", "south", "east", "west"):
            raise ValueError(f"Invalid direction: {direction}. Options: north, south, east, west")
        opts = _parse_view_opts(tokens, 3)
        if opts.get("style"):
            mgr.use(opts["style"])
        paper = opts.get("paper", mgr.get("layout.paper", "letter"))
        dpi = 300

        img = _render_elevation(state, direction, mgr, dpi, paper)
        out_name = f"elevation_{direction}.png"
        out_path = os.path.join(out_dir, out_name)
        img.save(out_path, dpi=(dpi, dpi))
        dens = sr.density(img)
        return state, f"OK: Rendered {out_name} (density {dens:.1f}%)"

    raise ValueError(f"Unknown view type: '{sub}'. Options: plan, section, axon, elevation")


# ---------------------------------------------------------------------------
# Section renderer
# ---------------------------------------------------------------------------

def _render_section(state, axis, gridline, style_mgr, dpi=300, paper="letter"):
    """Render a building section cut at the given axis and gridline."""
    from PIL import Image, ImageDraw, ImageFont

    paper_sizes = {"letter": (11.0, 8.5), "tabloid": (17.0, 11.0)}
    pw, ph = paper_sizes.get(paper, (11.0, 8.5))
    w_px = int(pw * dpi)
    h_px = int(ph * dpi)
    margin_px = int(style_mgr.get("layout.margin_inches", 0.5) * dpi)

    img = Image.new('1', (w_px, h_px), 1)
    draw = ImageDraw.Draw(img)

    def pt_to_px(pt):
        return max(1, int(round(pt * dpi / 72.0)))

    # Gather geometry: find what the section cuts through
    site = state.get("site", {})
    bays = state.get("bays", {})
    overrides = style_mgr.get("drawing_overrides.section", {})
    poche_fill = overrides.get("poche_fill", True)
    beyond_factor = overrides.get("beyond_weight_factor", 0.5)

    cut_weight = pt_to_px(style_mgr.get("lineweights.section_cut", 3.5))
    wall_ext_weight = pt_to_px(style_mgr.get("lineweights.wall_exterior", 2.5))
    beyond_weight = max(1, int(wall_ext_weight * beyond_factor))

    # Determine cut position from gridline
    # We use the first bay that has the relevant gridline
    cut_pos = None
    for bname, bay in sorted(bays.items()):
        if bay.get("grid_type") != "rectangular":
            continue
        cx_arr, cy_arr = _get_spacing_arrays(bay)
        ox, oy = bay["origin"]
        if axis == "x" and gridline < len(cy_arr):
            cut_pos = oy + cy_arr[gridline]
            break
        elif axis == "y" and gridline < len(cx_arr):
            cut_pos = ox + cx_arr[gridline]
            break

    if cut_pos is None:
        # Fallback: use gridline as direct offset
        cut_pos = float(gridline) * 24.0

    # For section rendering: project onto the plane perpendicular to cut
    # axis=x: cut is horizontal; show section looking in +y direction
    #   horizontal axis = x (model), vertical axis = z (height)
    # axis=y: cut is vertical; show section looking in +x direction
    #   horizontal axis = y (model), vertical axis = z (height)
    default_wall_height = 10.0

    # Collect wall segments that cross the cut plane
    draw_area_w = w_px - 2 * margin_px
    draw_area_h = h_px - 2 * margin_px

    # Determine model extents for the section view
    sw = site.get("width", 200)
    sh = site.get("height", 200)
    max_height = default_wall_height

    for bname, bay in bays.items():
        wh = bay.get("wall_height", default_wall_height)
        if wh > max_height:
            max_height = wh

    if axis == "x":
        model_w = sw
    else:
        model_w = sh
    model_h = max_height * 1.2  # Add some headroom

    scale = min(draw_area_w / max(model_w, 1), draw_area_h / max(model_h, 1))

    def model_to_px(mx, mz):
        """Convert model (horizontal, height) to pixel coords."""
        px = margin_px + mx * scale
        py = margin_px + draw_area_h - mz * scale  # flip Y
        return (int(round(px)), int(round(py)))

    # Draw ground line
    p1 = model_to_px(0, 0)
    p2 = model_to_px(model_w, 0)
    draw.line([p1, p2], fill=0, width=pt_to_px(style_mgr.get("lineweights.site_boundary", 2.0)))

    # Draw walls in section
    for bname, bay in sorted(bays.items()):
        if bay.get("grid_type") != "rectangular":
            continue
        walls = bay.get("walls", {})
        if not walls.get("enabled"):
            continue

        ox, oy = bay["origin"]
        rot = bay.get("rotation_deg", 0)
        cx_arr, cy_arr = _get_spacing_arrays(bay)
        wh = bay.get("wall_height", default_wall_height)
        t = walls.get("thickness", 0.5)

        if axis == "x":
            # Cut is horizontal at y = cut_pos
            # Check which y-gridlines this bay has near the cut
            for j, y_val in enumerate(cy_arr):
                wall_y = oy + y_val
                if abs(wall_y - cut_pos) < t:
                    # This wall is cut through
                    # Draw vertical wall elements at each x span
                    for i in range(len(cx_arr) - 1):
                        x_start = ox + cx_arr[i]
                        x_end = ox + cx_arr[i + 1]
                        # Section cut: draw heavy rectangle (poche)
                        p_bl = model_to_px(x_start, 0)
                        p_tl = model_to_px(x_start, wh)
                        p_tr = model_to_px(x_end, wh)
                        p_br = model_to_px(x_end, 0)
                        # Wall thickness in section (exaggerated for visibility)
                        half_t_px = max(2, int(t * scale / 2))

                        # Draw wall at each column position
                        for k in [i, i + 1]:
                            wall_x = ox + cx_arr[k]
                            bl = model_to_px(wall_x - t/2, 0)
                            tl = model_to_px(wall_x - t/2, wh)
                            tr = model_to_px(wall_x + t/2, wh)
                            br = model_to_px(wall_x + t/2, 0)
                            if poche_fill:
                                draw.polygon([tl, tr, br, bl], fill=0)
                            else:
                                draw.polygon([tl, tr, br, bl], fill=None, outline=0, width=cut_weight)
                elif wall_y > cut_pos:
                    # Beyond the cut — draw lighter
                    for k in range(len(cx_arr)):
                        wall_x = ox + cx_arr[k]
                        bl = model_to_px(wall_x, 0)
                        tl = model_to_px(wall_x, wh)
                        draw.line([bl, tl], fill=0, width=beyond_weight)
        else:
            # Cut is vertical at x = cut_pos
            for i, x_val in enumerate(cx_arr):
                wall_x = ox + x_val
                if abs(wall_x - cut_pos) < t:
                    for k in [j for j in range(len(cy_arr))]:
                        wall_y_pos = oy + cy_arr[k]
                        bl = model_to_px(wall_y_pos - t/2, 0)
                        tl = model_to_px(wall_y_pos - t/2, wh)
                        tr = model_to_px(wall_y_pos + t/2, wh)
                        br = model_to_px(wall_y_pos + t/2, 0)
                        if poche_fill:
                            draw.polygon([tl, tr, br, bl], fill=0)
                        else:
                            draw.polygon([tl, tr, br, bl], fill=None, outline=0, width=cut_weight)
                elif wall_x > cut_pos:
                    for k in range(len(cy_arr)):
                        wall_y_pos = oy + cy_arr[k]
                        bl = model_to_px(wall_y_pos, 0)
                        tl = model_to_px(wall_y_pos, wh)
                        draw.line([bl, tl], fill=0, width=beyond_weight)

    # Draw columns in section
    col_weight = pt_to_px(style_mgr.get("lineweights.column", 3.0))
    col_size = state.get("style", {}).get("column_size", 1.5)
    for bname, bay in sorted(bays.items()):
        if bay.get("grid_type") != "rectangular":
            continue
        ox, oy = bay["origin"]
        cx_arr, cy_arr = _get_spacing_arrays(bay)
        wh = bay.get("wall_height", default_wall_height)

        if axis == "x":
            # Check which columns are at or near the cut
            for j, y_val in enumerate(cy_arr):
                if abs(oy + y_val - cut_pos) < col_size:
                    for i, x_val in enumerate(cx_arr):
                        col_x = ox + x_val
                        bl = model_to_px(col_x - col_size/2, 0)
                        tl = model_to_px(col_x - col_size/2, wh)
                        tr = model_to_px(col_x + col_size/2, wh)
                        br = model_to_px(col_x + col_size/2, 0)
                        draw.polygon([tl, tr, br, bl], fill=0)
        else:
            for i, x_val in enumerate(cx_arr):
                if abs(ox + x_val - cut_pos) < col_size:
                    for j, y_val in enumerate(cy_arr):
                        col_y = oy + y_val
                        bl = model_to_px(col_y - col_size/2, 0)
                        tl = model_to_px(col_y - col_size/2, wh)
                        tr = model_to_px(col_y + col_size/2, wh)
                        br = model_to_px(col_y + col_size/2, 0)
                        draw.polygon([tl, tr, br, bl], fill=0)

    return img


# ---------------------------------------------------------------------------
# Axonometric renderer
# ---------------------------------------------------------------------------

def _render_axon(state, angle1, angle2, hidden, style_mgr, dpi=300, paper="letter"):
    """Render a parallel axonometric projection."""
    from PIL import Image, ImageDraw

    paper_sizes = {"letter": (11.0, 8.5), "tabloid": (17.0, 11.0)}
    pw, ph = paper_sizes.get(paper, (11.0, 8.5))
    w_px = int(pw * dpi)
    h_px = int(ph * dpi)
    margin_px = int(style_mgr.get("layout.margin_inches", 0.5) * dpi)

    img = Image.new('1', (w_px, h_px), 1)
    draw = ImageDraw.Draw(img)

    def pt_to_px(pt):
        return max(1, int(round(pt * dpi / 72.0)))

    site = state.get("site", {})
    bays = state.get("bays", {})
    default_wall_height = 10.0

    # Axon projection angles (in degrees)
    a_rad = math.radians(angle1)
    b_rad = math.radians(angle2)

    cos_a = math.cos(a_rad)
    sin_a = math.sin(a_rad)
    sin_b = math.sin(b_rad)
    cos_b = math.cos(b_rad)

    def project(x, y, z):
        """Project 3D point to 2D axon."""
        px = x * cos_a + y * sin_a
        py = -x * sin_a * sin_b + y * cos_a * sin_b + z * cos_b
        return (px, py)

    # Collect all 3D edges
    edges = []  # list of ((x1,y1,z1), (x2,y2,z2), depth, element_type)

    sw = site.get("width", 200)
    sh = site.get("height", 200)

    # Floor plane
    floor_corners_3d = [(0, 0, 0), (sw, 0, 0), (sw, sh, 0), (0, sh, 0)]
    for i in range(4):
        p1 = floor_corners_3d[i]
        p2 = floor_corners_3d[(i + 1) % 4]
        depth = (p1[1] + p2[1]) / 2.0
        edges.append((p1, p2, depth, "site_boundary"))

    # Build 3D wireframe from bays
    for bname, bay in sorted(bays.items()):
        if bay.get("grid_type") != "rectangular":
            continue
        ox, oy = bay["origin"]
        rot = bay.get("rotation_deg", 0)
        cx_arr, cy_arr = _get_spacing_arrays(bay)
        wh = bay.get("wall_height", default_wall_height)
        col_size = state.get("style", {}).get("column_size", 1.5)

        # Column verticals
        for xi in cx_arr:
            for yi in cy_arr:
                r = math.radians(rot)
                wx = ox + xi * math.cos(r) - yi * math.sin(r)
                wy = oy + xi * math.sin(r) + yi * math.cos(r)
                p1 = (wx, wy, 0)
                p2 = (wx, wy, wh)
                depth = wy
                edges.append((p1, p2, depth, "column"))

        # Wall edges
        walls = bay.get("walls", {})
        if walls.get("enabled"):
            # Bottom and top horizontal wall lines
            for j, y_val in enumerate(cy_arr):
                for segment_start, segment_end in [(0, len(cx_arr) - 1)]:
                    r = math.radians(rot)
                    for z in [0, wh]:
                        sx = ox + cx_arr[0] * math.cos(r) - y_val * math.sin(r)
                        sy = oy + cx_arr[0] * math.sin(r) + y_val * math.cos(r)
                        ex = ox + cx_arr[-1] * math.cos(r) - y_val * math.sin(r)
                        ey = oy + cx_arr[-1] * math.sin(r) + y_val * math.cos(r)
                        depth = (sy + ey) / 2.0
                        etype = "wall_exterior" if j == 0 or j == len(cy_arr) - 1 else "wall_interior"
                        edges.append(((sx, sy, z), (ex, ey, z), depth, etype))

            for i, x_val in enumerate(cx_arr):
                r = math.radians(rot)
                for z in [0, wh]:
                    sx = ox + x_val * math.cos(r) - cy_arr[0] * math.sin(r)
                    sy = oy + x_val * math.sin(r) + cy_arr[0] * math.cos(r)
                    ex = ox + x_val * math.cos(r) - cy_arr[-1] * math.sin(r)
                    ey = oy + x_val * math.sin(r) + cy_arr[-1] * math.cos(r)
                    depth = (sy + ey) / 2.0
                    etype = "wall_exterior" if i == 0 or i == len(cx_arr) - 1 else "wall_interior"
                    edges.append(((sx, sy, z), (ex, ey, z), depth, etype))

            # Vertical wall edges at corners
            corners_xy = []
            r = math.radians(rot)
            for xi in [cx_arr[0], cx_arr[-1]]:
                for yi in [cy_arr[0], cy_arr[-1]]:
                    wx = ox + xi * math.cos(r) - yi * math.sin(r)
                    wy = oy + xi * math.sin(r) + yi * math.cos(r)
                    corners_xy.append((wx, wy))
                    edges.append(((wx, wy, 0), (wx, wy, wh), wy, "wall_exterior"))

    # Project all edges to 2D
    projected = []
    all_px = []
    all_py = []
    for (p1_3d, p2_3d, depth, etype) in edges:
        px1, py1 = project(*p1_3d)
        px2, py2 = project(*p2_3d)
        projected.append(((px1, py1), (px2, py2), depth, etype))
        all_px.extend([px1, px2])
        all_py.extend([py1, py2])

    if not all_px:
        return img

    # Fit projected coords to drawing area
    min_px, max_px = min(all_px), max(all_px)
    min_py, max_py = min(all_py), max(all_py)
    proj_w = max_px - min_px if max_px > min_px else 1
    proj_h = max_py - min_py if max_py > min_py else 1
    draw_w = w_px - 2 * margin_px
    draw_h = h_px - 2 * margin_px
    scale = min(draw_w / proj_w, draw_h / proj_h) * 0.9

    cx_off = margin_px + draw_w / 2
    cy_off = margin_px + draw_h / 2
    mid_px_proj = (min_px + max_px) / 2
    mid_py_proj = (min_py + max_py) / 2

    def to_screen(px_proj, py_proj):
        sx = cx_off + (px_proj - mid_px_proj) * scale
        sy = cy_off - (py_proj - mid_py_proj) * scale  # flip Y
        return (int(round(sx)), int(round(sy)))

    # Depth fade settings
    overrides = style_mgr.get("drawing_overrides.axon", {})
    depth_fade = overrides.get("depth_fade", True)
    min_factor = overrides.get("depth_fade_min_factor", 0.3)

    all_depths = [d for _, _, d, _ in projected]
    min_depth = min(all_depths) if all_depths else 0
    max_depth = max(all_depths) if all_depths else 1
    depth_range = max_depth - min_depth if max_depth > min_depth else 1

    # Sort by depth (painter's algorithm: far to near)
    projected.sort(key=lambda e: e[2])

    for (p1_2d, p2_2d, depth, etype) in projected:
        base_weight = style_mgr.get(f"lineweights.{etype}",
                                     style_mgr.get("lineweights.wall_interior", 1.5))
        if depth_fade:
            # Closer (larger y in world) = heavier
            norm_depth = (depth - min_depth) / depth_range
            factor = min_factor + (1.0 - min_factor) * norm_depth
            weight = base_weight * factor
        else:
            weight = base_weight

        weight_px = pt_to_px(weight)
        s1 = to_screen(*p1_2d)
        s2 = to_screen(*p2_2d)
        draw.line([s1, s2], fill=0, width=weight_px)

    return img


# ---------------------------------------------------------------------------
# Elevation renderer
# ---------------------------------------------------------------------------

def _render_elevation(state, direction, style_mgr, dpi=300, paper="letter"):
    """Render a building elevation (orthographic projection of one face)."""
    from PIL import Image, ImageDraw

    paper_sizes = {"letter": (11.0, 8.5), "tabloid": (17.0, 11.0)}
    pw, ph = paper_sizes.get(paper, (11.0, 8.5))
    w_px = int(pw * dpi)
    h_px = int(ph * dpi)
    margin_px = int(style_mgr.get("layout.margin_inches", 0.5) * dpi)

    img = Image.new('1', (w_px, h_px), 1)
    draw = ImageDraw.Draw(img)

    def pt_to_px(pt):
        return max(1, int(round(pt * dpi / 72.0)))

    site = state.get("site", {})
    bays = state.get("bays", {})
    default_wall_height = 10.0

    sw = site.get("width", 200)
    sh = site.get("height", 200)

    # Direction determines which face we see
    # north: looking from +y toward -y, horizontal=x, vertical=z
    # south: looking from -y toward +y, horizontal=x (reversed), vertical=z
    # east: looking from +x toward -x, horizontal=y, vertical=z
    # west: looking from -x toward +x, horizontal=y (reversed), vertical=z

    max_height = default_wall_height
    for bname, bay in bays.items():
        wh = bay.get("wall_height", default_wall_height)
        if wh > max_height:
            max_height = wh

    if direction in ("north", "south"):
        model_w = sw
    else:
        model_w = sh
    model_h = max_height * 1.2

    draw_w = w_px - 2 * margin_px
    draw_h = h_px - 2 * margin_px
    elev_scale = min(draw_w / max(model_w, 1), draw_h / max(model_h, 1)) * 0.9

    def model_to_px(mh, mz):
        px = margin_px + (draw_w - model_w * elev_scale) / 2 + mh * elev_scale
        py = margin_px + draw_h - mz * elev_scale
        return (int(round(px)), int(round(py)))

    # Ground line
    gl1 = model_to_px(0, 0)
    gl2 = model_to_px(model_w, 0)
    draw.line([gl1, gl2], fill=0, width=pt_to_px(style_mgr.get("lineweights.site_boundary", 2.0)))

    # Draw walls as rectangles on the elevation
    for bname, bay in sorted(bays.items()):
        if bay.get("grid_type") != "rectangular":
            continue
        walls = bay.get("walls", {})
        if not walls.get("enabled"):
            continue

        ox, oy = bay["origin"]
        cx_arr, cy_arr = _get_spacing_arrays(bay)
        wh = bay.get("wall_height", default_wall_height)
        wall_weight = pt_to_px(style_mgr.get("lineweights.wall_exterior", 2.5))

        if direction == "north":
            # Front face at max y of this bay
            face_y = oy + cy_arr[-1]
            for i in range(len(cx_arr)):
                wall_h = ox + cx_arr[i]
                bl = model_to_px(wall_h, 0)
                tl = model_to_px(wall_h, wh)
                draw.line([bl, tl], fill=0, width=wall_weight)
            # Top and bottom horizontals
            left = ox + cx_arr[0]
            right = ox + cx_arr[-1]
            draw.line([model_to_px(left, 0), model_to_px(right, 0)], fill=0, width=wall_weight)
            draw.line([model_to_px(left, wh), model_to_px(right, wh)], fill=0, width=wall_weight)

        elif direction == "south":
            face_y = oy + cy_arr[0]
            for i in range(len(cx_arr)):
                wall_h = ox + cx_arr[i]
                bl = model_to_px(wall_h, 0)
                tl = model_to_px(wall_h, wh)
                draw.line([bl, tl], fill=0, width=wall_weight)
            left = ox + cx_arr[0]
            right = ox + cx_arr[-1]
            draw.line([model_to_px(left, 0), model_to_px(right, 0)], fill=0, width=wall_weight)
            draw.line([model_to_px(left, wh), model_to_px(right, wh)], fill=0, width=wall_weight)

        elif direction == "east":
            for j in range(len(cy_arr)):
                wall_h = oy + cy_arr[j]
                bl = model_to_px(wall_h, 0)
                tl = model_to_px(wall_h, wh)
                draw.line([bl, tl], fill=0, width=wall_weight)
            bottom_l = oy + cy_arr[0]
            bottom_r = oy + cy_arr[-1]
            draw.line([model_to_px(bottom_l, 0), model_to_px(bottom_r, 0)], fill=0, width=wall_weight)
            draw.line([model_to_px(bottom_l, wh), model_to_px(bottom_r, wh)], fill=0, width=wall_weight)

        elif direction == "west":
            for j in range(len(cy_arr)):
                wall_h = oy + cy_arr[j]
                bl = model_to_px(wall_h, 0)
                tl = model_to_px(wall_h, wh)
                draw.line([bl, tl], fill=0, width=wall_weight)
            bottom_l = oy + cy_arr[0]
            bottom_r = oy + cy_arr[-1]
            draw.line([model_to_px(bottom_l, 0), model_to_px(bottom_r, 0)], fill=0, width=wall_weight)
            draw.line([model_to_px(bottom_l, wh), model_to_px(bottom_r, wh)], fill=0, width=wall_weight)

    return img


# ══════════════════════════════════════════════════════════
# COMMAND DISPATCH
# ══════════════════════════════════════════════════════════

def apply_command(state, tokens, state_file=None):
    if not tokens: return state, ""
    cmd = tokens[0].lower()
    if cmd in ("quit","q","exit"):   return state, "__QUIT__"
    if cmd in ("help","h","?"):      return state, "__HELP__"
    if cmd == "status":              return state, "__STATUS__"
    if cmd in ("describe","d"):      return state, "__DESCRIBE__"
    if cmd in ("list","l"):
        if len(tokens) >= 2 and tokens[1].lower() in ("bays","bay"):
            return state, "__LIST_BAYS__"
        raise ValueError("Usage: list bays")
    if cmd == "undo":    return state, "__UNDO__"
    if cmd in ("print","p"): return state, "__PRINT__"
    if cmd == "corridor": return cmd_corridor(state, tokens)
    if cmd == "wall":     return cmd_wall(state, tokens)
    if cmd == "aperture": return cmd_aperture(state, tokens)
    if cmd == "room":     return cmd_room(state, tokens)
    if cmd == "cell":     return cmd_cell(state, tokens)
    if cmd == "block":    return cmd_block(state, tokens)
    if cmd == "hatch":    return cmd_hatch(state, tokens)
    if cmd == "legend":   return cmd_legend(state, tokens)
    if cmd == "tactile3d": return cmd_tactile3d(state, tokens)
    if cmd == "bambu":    return cmd_bambu(state, tokens)
    if cmd == "tts":      return cmd_tts(state, tokens)
    if cmd == "section":  return cmd_section(state, tokens)
    if cmd == "history":  return cmd_history(state, tokens, state_file)
    if cmd == "snapshot": return cmd_snapshot(state, tokens, state_file)
    if cmd == "setup":    return cmd_setup(state, tokens, state_file)
    if cmd == "style":    return cmd_style(state, tokens, state_file)
    if cmd == "view":     return cmd_view(state, tokens, state_file)
    if cmd != "set":
        raise ValueError(f"Unknown command: '{cmd}'. Type 'help' for a list.")
    if len(tokens) < 3: raise ValueError("set <site|column|style|bay|print> ...")
    target = tokens[1].lower()
    dispatch = {"site": _cmd_set_site, "column": _cmd_set_column,
                "style": _cmd_set_style, "print": _cmd_set_print, "bay": _cmd_set_bay}
    fn = dispatch.get(target)
    if fn is None: raise ValueError(f"Unknown set target: '{target}'. "
                                    f"Options: {', '.join(sorted(dispatch))}")
    return fn(state, tokens)

def do_print(state, state_file):
    pr = state.get("print",{}); site = state["site"]
    scv = pr.get("scale_ft_per_inch",8)
    pw = pr.get("paper_width_in",24.0); ph = pr.get("paper_height_in",36.0)
    dpi = pr.get("dpi",300); px_w = int(pw*dpi); px_h = int(ph*dpi)
    mw = pw*scv; mh = ph*scv
    pr["request_id"] = pr.get("request_id",0) + 1
    state["print"] = pr; save_state(state_file, state)
    lines = [f"Print requested (id={pr['request_id']}).",
             f'  Scale: {_scale_label(scv)} on {pw} x {ph} inch paper.',
             f"  {px_w} x {px_h} px at {dpi} DPI.",
             f"  Model area: {mw:.0f} x {mh:.0f} ft."]
    if site["width"] > mw or site["height"] > mh:
        lines.append("  WARNING: Site exceeds paper at this scale.")
    # --- Render tactile output via swell-print if available ---
    try:
        _swell_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "tools", "swell-print")
        if os.path.isdir(_swell_dir) and _swell_dir not in sys.path:
            sys.path.insert(0, _swell_dir)
        import state_renderer as _sr
        import pdf_generator as _pg
        paper = "tabloid" if pw > 12 else "letter"
        img = _sr.render(state, dpi=dpi, paper_size=paper)
        out_dir = os.path.dirname(os.path.abspath(state_file))
        fmt = pr.get("format", "pdf").lower()
        if fmt == "pdf":
            out_path = os.path.join(out_dir, "state_tactile.pdf")
            _pg.generate_pdf(img, out_path, paper_size=paper)
        else:
            out_path = os.path.join(out_dir, "state_tactile.png")
            img.save(out_path, dpi=(dpi, dpi))
        dens = _sr.density(img)
        lines.append(f"  Output: {out_path}")
        lines.append(f"  Density: {dens:.1f}%")
        if dens > 40:
            lines.append("  WARNING: Density above 40% may reduce PIAF clarity.")
    except ImportError:
        lines.append("  (swell-print not installed; no image generated)")
        lines.append("  Run: pip install -r tools/swell-print/requirements.txt")
    except Exception as e:
        lines.append(f"  (render failed: {e})")
    return "\n".join(lines)

HELP_TEXT = """
PLAN LAYOUT JIG v2.3 — Commands
====================================
describe / d ............. Full model description (all settings and geometry)
list bays / l bays ....... Compact bay table
undo ..................... Revert last change
status ................... Show state file path and timestamp
help / h / ? ............. This message
quit / q / exit .......... Save and exit

SITE & STYLE:
  set site width|height <ft>
  set column size <ft>
  set style heavy|light|corridor|wall|text_height|braille_height|
           dash_len|gap_len|bg_pad|label_offset|arc_segments <value>

BAY CONFIGURATION:
  set bay <name> grid_type rectangular|radial
  set bay <name> z_order|origin|rotation|bays|spacing <value(s)>
  set bay <name> spacing_x <s1 s2 ...>  /  spacing_y <s1 s2 ...>
  set bay <name> rings|ring_spacing|arms|arc_deg|arc_start_deg <value>
  set bay <name> void_center <x y>  /  void_size <w h>  /  void_shape rect|circle
  set bay <name> label|braille <text>

CORRIDOR:
  corridor <bay> on|off
  corridor <bay> axis|position|width|loading|hatch|hatch_scale <value>

WALLS:
  wall <bay> on|off
  wall <bay> thickness <feet>

APERTURES:
  aperture <bay> add <id> <door|window|portal> <x|y> <gridline> <corner> <width> <height>
  aperture <bay> remove <id>
  aperture <bay> set <id> <field> <value>
     fields: type, axis, gridline, corner, width, height, hinge, swing
  aperture <bay> list

BLOCKS (symbol configuration):
  block list
  block <door|window|portal|room> [field] [value]
     fields: symbol, label, label_height, tactile_weight, label_prefix

ROOMS (hatch-filled regions):
  room list  /  room refresh
  room <id> label|braille|hatch|hatch_scale|hatch_rotation <value>
  room add <id> bay|void|landscape [bay_name]
  room remove <id>

CELLS (subdivide bays into named rooms with areas):
  cell <bay> list .............. all cells with names and areas
  cell <bay> rooms ............. rooms grouped by name with totals
  cell <bay> <col,row> ......... show one cell's properties
  cell <bay> <col,row> name <n>  assign room name
  cell <bay> <col,row> label <l> display label (defaults to name)
  cell <bay> <col,row> braille <b> braille label
  cell <bay> <col,row> hatch <h>  hatch pattern (diagonal, crosshatch, dots, etc.)
  cell <bay> <col,row> hatch_scale|hatch_rotation <v>
  cell <bay> <c0,r0-c1,r1> name|label|hatch <v>  apply to a range of cells
  cell <bay> <col,row> clear ... reset one cell
  cell <bay> clear_all ......... reset all cells
  cell <bay> auto_corridor ..... auto-name corridor cells

LEGEND (Braille + English key):
  legend on|off
  legend position bottom-right|bottom-left|top-right|top-left|custom [x y]
  legend width|title|title_braille <value>
  legend swatch_size|row_height|text_height|braille_height|padding|border_weight_mm <value>
  legend show_braille|show_hatches|show_apertures on|off

TACTILE 3D (printable plan model):
  tactile3d on|off
  tactile3d wall_height|cut_height|floor_thickness <feet>
  tactile3d floor on|off
  tactile3d auto_export on|off
  tactile3d export_path <filepath>
  tactile3d scale_factor <value>
  tactile3d export ................ trigger one-time STL export

BAMBU PRINTER (3D print pipeline):
  bambu config ip <address> ...... printer IP address
  bambu config access_code <code>  access code from printer LCD
  bambu config serial <number> ... printer serial number
  bambu config printer_model <m> . p1s, x1c, a1, a1_mini, etc.
  bambu config print_scale <N> ... 1:N representation scale (default 200)
  bambu config stl_path <path> ... STL output path
  bambu config slicer_path <path>  OrcaSlicer executable path
  bambu preview .................. show dimensions and plate fit
  bambu export [path] ............ build mesh, write binary STL
  bambu slice .................... export + slice to 3MF
  bambu send [path] .............. upload 3MF and start print
  bambu print .................... full pipeline: export+slice+send
  bambu status ................... poll printer progress

HATCH LIBRARY:
  hatch list
  hatch path <folder>
  hatch add <name> <source_image_path>

SECTION CUT (SVG export of vertical slice):
  section x|y <offset> ....... define cut plane
  section preview ............. show segment count and extent
  section export [path] ....... export SVG (default: ./section_<axis>_<offset>.svg)
  section list ................ current section settings
  section clear ............... remove section definition

HISTORY & SNAPSHOTS:
  history list ............... show last 20 history entries + snapshots
  history count .............. number of history entries
  snapshot save <name> ....... save current state as named snapshot
  snapshot load <name> ....... restore a named snapshot
  snapshot list .............. list all named snapshots

TEXT-TO-SPEECH:
  tts ........................ show TTS status
  tts on|off ................. enable/disable speech
  tts rate <-10..10> ......... speech rate (-10=slowest, 10=fastest)

STYLE PROFILES (PIAF rendering):
  style list .............. list available styles
  style use <name> ........ switch active style
  style show [category] ... show settings (lineweights, hatches, labels, layout, density)
  style set <key> <value> . set a value (dot notation: lineweights.column 4.0)
  style save [name] ....... save current style (or save-as with name)
  style reset ............. discard unsaved changes
  style test .............. render calibration test swatch
  style add-hatch <name> <spacing_mm> <angle_deg> [weight_pt]
  style remove-hatch <name>

VIEW (drawing types with style support):
  view plan [--style <name>] [--paper <size>]
  view section <x|y> <gridline> [--style <name>]
  view axon [angle1] [angle2] [--hidden] [--style <name>]
  view elevation <north|south|east|west> [--style <name>]

OUTPUT:
  set print scale|paper|margin|dpi|format <value>
  print

SETUP (Rhino auto-launch):
  setup rhino ............. launch Rhino with watcher + set units to Feet
  setup rhino --path <exe>  specify Rhino executable path
  setup status ............ check if Rhino watcher is connected
"""

def main():
    ap = argparse.ArgumentParser(description="Plan Layout Jig — Terminal CLI")
    ap.add_argument("--state", default=_default_state_path(),
                    help="Path to the JSON state file")
    ap.add_argument("--tts", action="store_true",
                    help="Enable text-to-speech on startup")
    args = ap.parse_args(); state_file = os.path.abspath(args.state)
    try: state = load_state(state_file)
    except Exception as e: print(f"[ERROR] {e}"); sys.exit(1)
    # Schema migration: accept old or new schema
    if state.get("schema") not in (SCHEMA, "school_jig_2d_v2.2"):
        state = default_state()
    if state.get("schema") == "school_jig_2d_v2.2":
        state["schema"] = SCHEMA
    if "legend" not in state: state["legend"] = _default_legend()
    if "tactile3d" not in state: state["tactile3d"] = _default_tactile3d()
    if "auto_export" not in state.get("tactile3d",{}):
        state["tactile3d"]["auto_export"] = False
    if "bambu" not in state: state["bambu"] = _default_bambu()
    if "tts" not in state: state["tts"] = _default_tts()
    if "section" not in state: state["section"] = _default_section()
    if args.tts:
        state["tts"]["enabled"] = True

    # TTS availability check
    tts_available = True

    def _out(text):
        """Print text and optionally speak it via TTS."""
        nonlocal tts_available
        print(text)
        if tts_available and state.get("tts", {}).get("enabled"):
            rate = state.get("tts", {}).get("rate", 2)
            ok = _speak(text, rate=rate)
            if not ok:
                tts_available = False

    undo_stack = []
    history_seq = _history_count(state_file)
    _out("PLAN LAYOUT JIG v2.3 — Terminal CLI")
    print(f"State: {state_file}")
    if state.get("tts", {}).get("enabled"):
        print("TTS: ON")
    print("Type 'help' for commands, 'describe' for full model info.\n")
    save_state(state_file, state)
    while True:
        try: raw = input(">> ").strip()
        except (EOFError, KeyboardInterrupt): print("\nExiting."); break
        if not raw: continue
        tokens = tokenize(raw); before = copy.deepcopy(state)
        try: state, msg = apply_command(state, tokens, state_file=state_file)
        except Exception as e: _out(f"Error: {e}"); continue
        if msg == "__QUIT__": break
        if msg == "__HELP__": print(HELP_TEXT); continue
        if msg == "__STATUS__":
            print(f"State: {state_file}")
            try: st = os.stat(state_file); print(f"Modified: {time.ctime(st.st_mtime)}  Size: {st.st_size} bytes")
            except: pass
            print(f"History: {history_seq} entries")
            continue
        if msg == "__DESCRIBE__": _out(describe(state)); continue
        if msg == "__LIST_BAYS__": _out(list_bays(state)); continue
        if msg == "__UNDO__":
            if undo_stack:
                state = undo_stack.pop()
                save_state(state_file, state)
                _history_delete_last(state_file, history_seq)
                history_seq = max(0, history_seq - 1)
                _out("Undo.")
            else: _out("Nothing to undo.")
            continue
        if msg == "__PRINT__": undo_stack.append(before); _out(do_print(state, state_file)); continue
        undo_stack.append(before)
        try:
            save_state(state_file, state); _out(msg)
            history_seq += 1
            _history_save(state_file, state, history_seq)
            # Clear one-shot export flag after save so it doesn't
            # re-trigger on subsequent commands
            t3 = state.get("tactile3d")
            if t3 and t3.get("_export_once"):
                t3["_export_once"] = False
            # Auto-export STL if tactile3d is enabled and auto_export is on
            if t3 and t3.get("auto_export") and t3.get("enabled"):
                _export_path = t3.get("export_path", "./tactile3d_export.stl")
                try:
                    import tactile_print as _tp
                    _export_msg = _tp.do_export(state, _export_path)
                    _out("AUTO-EXPORT: " + _export_msg)
                except ImportError:
                    pass  # tactile_print not available; silent skip
                except Exception as _e:
                    _out(f"[WARNING] Auto-export failed: {_e}")
        except Exception as e: state = before; undo_stack.pop(); _out(f"[ERROR] {e}")
    try: save_state(state_file, state)
    except: pass

if __name__ == "__main__":
    main()
