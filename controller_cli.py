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
import argparse, copy, json, math, os, sys, time
from datetime import datetime

SCHEMA = "plan_layout_jig_v2.3"
DEFAULT_STATE_FILENAME = "state.json"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif"}

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
    braille_map = {"A": "\u2803\u2801\u283d \u2801",
                   "B": "\u2803\u2801\u283d \u2803",
                   "C": "\u2803\u2801\u283d \u2809"}
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
        "label": label, "braille": braille_map.get(name, ""),
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
                     "arc_start_deg, void_center, void_size, void_shape, label, braille")

# ══════════════════════════════════════════════════════════
# COMMAND DISPATCH
# ══════════════════════════════════════════════════════════

def apply_command(state, tokens):
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

OUTPUT:
  set print scale|paper|margin|dpi|format <value>
  print
"""

def main():
    ap = argparse.ArgumentParser(description="Plan Layout Jig — Terminal CLI")
    ap.add_argument("--state", default=_default_state_path(),
                    help="Path to the JSON state file")
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
    undo_stack = []
    print("PLAN LAYOUT JIG v2.3 — Terminal CLI")
    print(f"State: {state_file}")
    print("Type 'help' for commands, 'describe' for full model info.\n")
    save_state(state_file, state)
    while True:
        try: raw = input(">> ").strip()
        except (EOFError, KeyboardInterrupt): print("\nExiting."); break
        if not raw: continue
        tokens = tokenize(raw); before = copy.deepcopy(state)
        try: state, msg = apply_command(state, tokens)
        except Exception as e: print(f"Error: {e}"); continue
        if msg == "__QUIT__": break
        if msg == "__HELP__": print(HELP_TEXT); continue
        if msg == "__STATUS__":
            print(f"State: {state_file}")
            try: st = os.stat(state_file); print(f"Modified: {time.ctime(st.st_mtime)}  Size: {st.st_size} bytes")
            except: pass
            continue
        if msg == "__DESCRIBE__": print(describe(state)); continue
        if msg == "__LIST_BAYS__": print(list_bays(state)); continue
        if msg == "__UNDO__":
            if undo_stack: state = undo_stack.pop(); save_state(state_file, state); print("Undo.")
            else: print("Nothing to undo.")
            continue
        if msg == "__PRINT__": undo_stack.append(before); print(do_print(state, state_file)); continue
        undo_stack.append(before)
        try:
            save_state(state_file, state); print(msg)
            # Clear one-shot export flag after save so it doesn't
            # re-trigger on subsequent commands
            t3 = state.get("tactile3d")
            if t3 and t3.get("_export_once"):
                t3["_export_once"] = False
        except Exception as e: state = before; undo_stack.pop(); print(f"[ERROR] {e}")
    try: save_state(state_file, state)
    except: pass

if __name__ == "__main__":
    main()
