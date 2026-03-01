# -*- coding: utf-8 -*-
"""
PLAN LAYOUT JIG — Auditor  v1.0
================================
Spatial analysis, validation, and rich description of layout jig models.

All functions take a state dict (the CMA) and return plain-text strings
formatted for screen readers.  No Rhino dependency — pure math on the
JSON state.

Requires: Python 3 stdlib only.
"""

import math
import os
import sys

# ── Import controller helpers ──────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

import controller_cli as cli


# ══════════════════════════════════════════════════════════
# GEOMETRY UTILITIES (wrapping controller helpers)
# ══════════════════════════════════════════════════════════

def _bay_footprint(bay):
    """Return (min_x, max_x, min_y, max_y) world-space bounding box."""
    return cli._bay_extents(bay)


def _bay_local_dims(bay):
    """Return (width, height) in local bay coordinates (feet)."""
    if bay.get("grid_type") == "radial":
        outer = bay.get("rings", 4) * bay.get("ring_spacing", 20)
        return outer * 2, outer * 2
    cx, cy = cli._get_spacing_arrays(bay)
    return cx[-1], cy[-1]


def _point_in_box(px, py, x0, x1, y0, y1):
    return x0 <= px <= x1 and y0 <= py <= y1


def _boxes_overlap(a, b):
    """Check if two (min_x, max_x, min_y, max_y) boxes overlap."""
    return not (a[1] <= b[0] or b[1] <= a[0] or a[3] <= b[2] or b[3] <= a[2])


def _distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


# ══════════════════════════════════════════════════════════
# AUDIT: FULL MODEL
# ══════════════════════════════════════════════════════════

def audit_model(state):
    """Run all validation checks on the model.

    Returns a list of issue strings.  Empty list = model is clean.
    Each issue is prefixed with WARNING: or ERROR: for severity.
    """
    issues = []
    bays = state.get("bays", {})
    rooms = state.get("rooms", {})
    site = state.get("site", {})

    # ── 1. Check bay overlaps ──
    bay_names = sorted(bays.keys())
    for i, name_a in enumerate(bay_names):
        box_a = _bay_footprint(bays[name_a])
        for name_b in bay_names[i + 1:]:
            box_b = _bay_footprint(bays[name_b])
            if _boxes_overlap(box_a, box_b):
                issues.append(
                    f"WARNING: Bay {name_a} and Bay {name_b} footprints overlap.")

    # ── 2. Check bays inside site ──
    sw = site.get("width", 180)
    sh = site.get("height", 260)
    so = site.get("origin", [0, 0])
    for name, bay in sorted(bays.items()):
        box = _bay_footprint(bay)
        if box[0] < so[0] or box[1] > so[0] + sw or box[2] < so[1] or box[3] > so[1] + sh:
            issues.append(
                f"WARNING: Bay {name} extends outside the site boundary.")

    # ── 3. Aperture validation ──
    for name, bay in sorted(bays.items()):
        walls = bay.get("walls", {})
        apertures = bay.get("apertures", [])

        if apertures and not walls.get("enabled"):
            issues.append(
                f"WARNING: Bay {name} has {len(apertures)} aperture(s) but walls are OFF.")

        if bay.get("grid_type") == "rectangular":
            nx, ny = bay["bays"]
            cx, cy = cli._get_spacing_arrays(bay)
            max_x_gridline = nx
            max_y_gridline = ny
            bay_w, bay_h = cx[-1], cy[-1]

            for ap in apertures:
                aid = ap["id"]
                gl = ap.get("gridline", 0)
                axis = ap.get("axis", "x")

                # Gridline in range?
                if axis == "x" and gl > max_y_gridline:
                    issues.append(
                        f"ERROR: Bay {name} aperture {aid}: gridline {gl} "
                        f"exceeds y-grid max ({max_y_gridline}).")
                elif axis == "y" and gl > max_x_gridline:
                    issues.append(
                        f"ERROR: Bay {name} aperture {aid}: gridline {gl} "
                        f"exceeds x-grid max ({max_x_gridline}).")

                # Aperture fits within wall?
                corner = ap.get("corner", 0)
                width = ap.get("width", 3)
                if axis == "x":
                    wall_len = bay_w
                else:
                    wall_len = bay_h

                if corner + width > wall_len:
                    issues.append(
                        f"WARNING: Bay {name} aperture {aid}: "
                        f"corner ({corner}) + width ({width}) = {corner + width} "
                        f"exceeds wall length ({wall_len:.1f}).")

    # ── 4. Corridor validation ──
    for name, bay in sorted(bays.items()):
        cor = bay.get("corridor", {})
        if not cor.get("enabled"):
            continue

        if bay.get("grid_type") == "rectangular":
            w, h = _bay_local_dims(bay)
            cor_width = cor.get("width", 8)
            axis = cor.get("axis", "x")

            if axis == "x" and cor_width > h:
                issues.append(
                    f"ERROR: Bay {name}: corridor width ({cor_width}) "
                    f"exceeds bay height ({h:.1f}).")
            elif axis == "y" and cor_width > w:
                issues.append(
                    f"ERROR: Bay {name}: corridor width ({cor_width}) "
                    f"exceeds bay width ({w:.1f}).")

    # ── 5. ADA compliance checks ──
    for name, bay in sorted(bays.items()):
        cor = bay.get("corridor", {})
        if cor.get("enabled"):
            cw = cor.get("width", 8)
            if cw < 5.0:
                issues.append(
                    f"WARNING: Bay {name}: corridor width {cw} ft "
                    f"is below ADA minimum (5 ft for wheelchair passing).")

        for ap in bay.get("apertures", []):
            if ap.get("type") == "door":
                dw = ap.get("width", 3)
                if dw < 3.0:
                    issues.append(
                        f"WARNING: Bay {name} door {ap['id']}: width {dw} ft "
                        f"is below ADA minimum (3 ft clear).")

    # ── 6. Room references ──
    for rid, room in sorted(rooms.items()):
        src = room.get("source_bay")
        if src and src not in bays:
            issues.append(
                f"ERROR: Room '{rid}' references bay '{src}' which does not exist.")

    # ── 7. Empty labels ──
    for name, bay in sorted(bays.items()):
        if not bay.get("label", "").strip():
            issues.append(
                f"WARNING: Bay {name} has no label (accessibility issue).")

    return issues


def format_audit(issues):
    """Format audit issues as a numbered screen-reader-friendly report."""
    if not issues:
        return "OK: Model passes all validation checks. 0 issues found.\nREADY:"

    lines = [f"AUDIT: {len(issues)} issue(s) found.", ""]
    for i, issue in enumerate(issues, 1):
        lines.append(f"  {i}. {issue}")
    lines.append("")
    lines.append(f"Total: {len(issues)} issue(s).")
    lines.append("READY:")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
# AUDIT: SINGLE BAY
# ══════════════════════════════════════════════════════════

def audit_bay(state, bay_name):
    """Deep audit of a single bay. Returns a text report."""
    bays = state.get("bays", {})
    if bay_name not in bays:
        return f"ERROR: Bay '{bay_name}' not found. Available: {', '.join(sorted(bays.keys()))}"

    bay = bays[bay_name]
    lines = [f"AUDIT: Bay {bay_name}", ""]

    # Grid info
    gt = bay.get("grid_type", "rectangular")
    lines.append(f"  Grid type: {gt}")
    lines.append(f"  Origin: ({bay['origin'][0]:.1f}, {bay['origin'][1]:.1f})")
    lines.append(f"  Rotation: {bay.get('rotation_deg', 0)} deg")
    lines.append(f"  Z-order: {bay.get('z_order', 0)}")

    if gt == "rectangular":
        nx, ny = bay["bays"]
        cx, cy = cli._get_spacing_arrays(bay)
        w, h = cx[-1], cy[-1]
        lines.append(f"  Grid: {nx} x {ny} bays")
        lines.append(f"  Dimensions: {w:.1f} x {h:.1f} ft")
        lines.append(f"  Area: {cli._bay_area(bay):,.0f} sq ft")
        lines.append(f"  Columns: {cli._bay_col_count(bay)}")

        if bay.get("spacing_x"):
            lines.append(f"  Irregular X spacing: {bay['spacing_x']}")
        if bay.get("spacing_y"):
            lines.append(f"  Irregular Y spacing: {bay['spacing_y']}")
    else:
        rings = bay.get("rings", 4)
        arms = bay.get("arms", 8)
        rs = bay.get("ring_spacing", 20)
        lines.append(f"  Rings: {rings}  Arms: {arms}  Ring spacing: {rs} ft")
        lines.append(f"  Arc: {bay.get('arc_deg', 360)} deg from {bay.get('arc_start_deg', 0)} deg")
        lines.append(f"  Outer radius: {rings * rs:.1f} ft")
        lines.append(f"  Area: {cli._bay_area(bay):,.0f} sq ft")
        lines.append(f"  Columns: {cli._bay_col_count(bay)}")

    # Extents
    box = _bay_footprint(bay)
    lines.append(f"  World extents: X [{box[0]:.1f}, {box[1]:.1f}]  "
                 f"Y [{box[2]:.1f}, {box[3]:.1f}]")

    # Walls
    walls = bay.get("walls", {})
    if walls.get("enabled"):
        lines.append(f"  Walls: ON  thickness={walls.get('thickness', 0.5)} ft")
    else:
        lines.append("  Walls: OFF")

    # Corridor
    cor = bay.get("corridor", {})
    if cor.get("enabled"):
        lines.append(f"  Corridor: ON  axis={cor.get('axis','x')}  "
                     f"position={cor.get('position',1)}  "
                     f"width={cor.get('width',8)} ft  "
                     f"loading={cor.get('loading','double')}")
        if cor.get("hatch", "none") != "none":
            lines.append(f"    Corridor hatch: {cor['hatch']}  "
                         f"scale={cor.get('hatch_scale', 4.0)}")
    else:
        lines.append("  Corridor: OFF")

    # Apertures
    apertures = bay.get("apertures", [])
    if apertures:
        lines.append(f"  Apertures: {len(apertures)}")
        for ap in apertures:
            lines.append(f"    {ap['id']}: {ap['type']}  "
                         f"axis={ap.get('axis','x')}  "
                         f"gridline={ap.get('gridline',0)}  "
                         f"corner={ap.get('corner',0)}  "
                         f"width={ap.get('width',3)} x height={ap.get('height',7)}")
    else:
        lines.append("  Apertures: none")

    # Void
    vc = bay.get("void_center", [0, 0])
    vs = bay.get("void_size", [20, 20])
    vsh = bay.get("void_shape", "rectangle")
    lines.append(f"  Void: {vsh}  center=({vc[0]:.1f}, {vc[1]:.1f})  "
                 f"size={vs[0]:.1f} x {vs[1]:.1f}")

    # Labels
    lines.append(f"  Label: {bay.get('label', '(none)')}")
    lines.append(f"  Braille: {bay.get('braille', '(none)')}")

    # Per-bay issues
    issues = []
    for issue in audit_model(state):
        if f"Bay {bay_name}" in issue:
            issues.append(issue)

    if issues:
        lines.append("")
        lines.append(f"  Issues ({len(issues)}):")
        for issue in issues:
            lines.append(f"    - {issue}")
    else:
        lines.append("  Issues: none")

    lines.append("READY:")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
# DESCRIBE: CIRCULATION
# ══════════════════════════════════════════════════════════

def describe_circulation(state):
    """Describe corridor connectivity across all bays.

    Reports which bays have corridors, their alignment, whether portals
    connect them, and identifies dead ends.
    """
    bays = state.get("bays", {})
    lines = ["CIRCULATION ANALYSIS", ""]

    corridor_bays = {}
    for name, bay in sorted(bays.items()):
        cor = bay.get("corridor", {})
        if cor.get("enabled"):
            corridor_bays[name] = cor

    if not corridor_bays:
        lines.append("  No corridors enabled in any bay.")
        lines.append("READY:")
        return "\n".join(lines)

    lines.append(f"  Bays with corridors: {', '.join(sorted(corridor_bays.keys()))}")
    lines.append(f"  Bays without corridors: "
                 f"{', '.join(sorted(set(bays.keys()) - set(corridor_bays.keys()))) or '(none)'}")
    lines.append("")

    # Describe each corridor
    for name, cor in sorted(corridor_bays.items()):
        bay = bays[name]
        axis = cor.get("axis", "x")
        width = cor.get("width", 8)
        loading = cor.get("loading", "double")
        pos = cor.get("position", 1)
        lines.append(f"  Bay {name} corridor:")
        lines.append(f"    Axis: {axis}  Position: gridline {pos}  "
                     f"Width: {width} ft  Loading: {loading}")

        # Count doors/portals on this corridor
        doors_on_corridor = []
        portals_on_corridor = []
        for ap in bay.get("apertures", []):
            # Apertures on the corridor axis walls connect to the corridor
            if ap.get("axis") == axis:
                gl = ap.get("gridline", 0)
                if gl == pos or gl == pos - 1 or gl == pos + 1:
                    if ap.get("type") == "door":
                        doors_on_corridor.append(ap["id"])
                    elif ap.get("type") == "portal":
                        portals_on_corridor.append(ap["id"])

        if doors_on_corridor:
            lines.append(f"    Doors near corridor: {', '.join(doors_on_corridor)}")
        if portals_on_corridor:
            lines.append(f"    Portals near corridor: {', '.join(portals_on_corridor)}")
        if not doors_on_corridor and not portals_on_corridor:
            lines.append("    WARNING: No doors or portals near corridor (dead end?)")
        lines.append("")

    # Check for potential inter-bay connections via proximity
    corridor_names = sorted(corridor_bays.keys())
    connections = []
    for i, name_a in enumerate(corridor_names):
        box_a = _bay_footprint(bays[name_a])
        for name_b in corridor_names[i + 1:]:
            box_b = _bay_footprint(bays[name_b])
            # Check if bays are adjacent (within 10 ft)
            gap_x = max(0, max(box_a[0], box_b[0]) - min(box_a[1], box_b[1]))
            gap_y = max(0, max(box_a[2], box_b[2]) - min(box_a[3], box_b[3]))
            gap = math.sqrt(gap_x ** 2 + gap_y ** 2)
            if gap < 10:
                connections.append((name_a, name_b, gap))

    if connections:
        lines.append("  Potential inter-bay connections:")
        for a, b, gap in connections:
            lines.append(f"    Bay {a} <-> Bay {b}  (gap: {gap:.1f} ft)")
    else:
        lines.append("  No adjacent corridor bays found (bays may be isolated).")

    lines.append("READY:")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
# DESCRIBE: SINGLE BAY (RICH NARRATIVE)
# ══════════════════════════════════════════════════════════

def describe_bay(state, bay_name):
    """Rich narrative description of a single bay for screen reader users.

    More detailed than the main describe() output, with spatial
    relationships and accessibility-relevant observations.
    """
    bays = state.get("bays", {})
    if bay_name not in bays:
        return f"ERROR: Bay '{bay_name}' not found. Available: {', '.join(sorted(bays.keys()))}"

    bay = bays[bay_name]
    gt = bay.get("grid_type", "rectangular")
    lines = [f"BAY {bay_name}: {bay.get('label', '(unlabeled)')}", ""]

    # Opening sentence
    area = cli._bay_area(bay)
    cols = cli._bay_col_count(bay)
    ox, oy = bay["origin"]

    if gt == "rectangular":
        w, h = _bay_local_dims(bay)
        nx, ny = bay["bays"]
        lines.append(
            f"  A {nx}-by-{ny} rectangular grid anchored at ({ox:.0f}, {oy:.0f}). "
            f"{w:.0f} feet wide by {h:.0f} feet deep, "
            f"totaling {area:,.0f} square feet with {cols} columns.")
    else:
        rings = bay.get("rings", 4)
        arms = bay.get("arms", 8)
        arc = bay.get("arc_deg", 360)
        lines.append(
            f"  A radial grid centered at ({ox:.0f}, {oy:.0f}) "
            f"with {rings} rings and {arms} arms spanning {arc} degrees. "
            f"Area: {area:,.0f} square feet with {cols} columns.")

    rot = bay.get("rotation_deg", 0)
    if rot != 0:
        lines.append(f"  Rotated {rot} degrees from baseline.")

    # Walls and corridor
    walls = bay.get("walls", {})
    cor = bay.get("corridor", {})

    if walls.get("enabled") and cor.get("enabled"):
        lines.append(
            f"  Enclosed with {walls.get('thickness', 0.5)}-ft walls. "
            f"A {cor.get('width', 8)}-ft {cor.get('loading', 'double')}-loaded corridor "
            f"runs along the {cor.get('axis', 'x')}-axis at gridline {cor.get('position', 1)}.")
    elif walls.get("enabled"):
        lines.append(f"  Enclosed with {walls.get('thickness', 0.5)}-ft walls. No corridor.")
    elif cor.get("enabled"):
        lines.append(
            f"  No walls. A {cor.get('width', 8)}-ft corridor "
            f"runs along the {cor.get('axis', 'x')}-axis.")
    else:
        lines.append("  Open grid: no walls, no corridor.")

    # Apertures
    apertures = bay.get("apertures", [])
    if apertures:
        doors = [a for a in apertures if a.get("type") == "door"]
        windows = [a for a in apertures if a.get("type") == "window"]
        portals = [a for a in apertures if a.get("type") == "portal"]
        parts = []
        if doors:
            parts.append(f"{len(doors)} door(s)")
        if windows:
            parts.append(f"{len(windows)} window(s)")
        if portals:
            parts.append(f"{len(portals)} portal(s)")
        lines.append(f"  Apertures: {', '.join(parts)}.")

        for ap in apertures:
            lines.append(
                f"    {ap['id']}: {ap['type']}  "
                f"{ap.get('width', 3)}w x {ap.get('height', 7)}h ft  "
                f"on {ap.get('axis', 'x')}-wall gridline {ap.get('gridline', 0)}  "
                f"at corner offset {ap.get('corner', 0)} ft")
    else:
        lines.append("  No apertures.")

    # Void
    vc = bay.get("void_center", [0, 0])
    vs = bay.get("void_size", [20, 20])
    vsh = bay.get("void_shape", "rectangle")
    void_area = vs[0] * vs[1] if vsh == "rectangle" else math.pi * (vs[0]/2) * (vs[1]/2)
    lines.append(
        f"  Void: {vsh} at center ({vc[0]:.0f}, {vc[1]:.0f}), "
        f"size {vs[0]:.0f} x {vs[1]:.0f} ft ({void_area:,.0f} sq ft).")

    # Cell rooms (if rectangular and cells exist)
    cells = bay.get("cells", {})
    if cells:
        named_cells = {k: v for k, v in cells.items() if v.get("name")}
        if named_cells:
            room_groups = cli._room_summary(bay)
            lines.append(f"  Named cell rooms: {len(room_groups)}")
            for rname, rdata in sorted(room_groups.items()):
                lines.append(
                    f"    {rname}: {len(rdata['cells'])} cell(s), "
                    f"{rdata['area']:,.0f} sq ft")

    # Spatial relationships to other bays
    other_bays = {n: b for n, b in bays.items() if n != bay_name}
    if other_bays:
        my_box = _bay_footprint(bay)
        my_center = ((my_box[0] + my_box[1]) / 2, (my_box[2] + my_box[3]) / 2)
        lines.append("")
        lines.append("  Relative to other bays:")
        for other_name, other_bay in sorted(other_bays.items()):
            other_box = _bay_footprint(other_bay)
            other_center = ((other_box[0] + other_box[1]) / 2,
                            (other_box[2] + other_box[3]) / 2)
            dist = _distance(my_center, other_center)
            dx = other_center[0] - my_center[0]
            dy = other_center[1] - my_center[1]

            # Cardinal direction
            if abs(dx) > abs(dy):
                direction = "east" if dx > 0 else "west"
            else:
                direction = "north" if dy > 0 else "south"

            lines.append(f"    Bay {other_name}: {dist:.0f} ft to the {direction}")

    lines.append("READY:")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════
# MEASURE
# ══════════════════════════════════════════════════════════

def measure(state, from_desc, to_desc):
    """Measure distance between two semantic locations.

    Supported location formats:
        "bay A origin"    — origin point of bay A
        "bay A center"    — center of bay A footprint
        "bay A void"      — center of bay A's void
        "site origin"     — site origin
        "site center"     — center of site

    Returns a text description of the distance.
    """
    def _resolve(desc):
        parts = desc.strip().lower().split()
        if len(parts) >= 3 and parts[0] == "bay":
            bay_name = parts[1].upper()
            bays = state.get("bays", {})
            if bay_name not in bays:
                raise ValueError(f"Bay '{bay_name}' not found.")
            bay = bays[bay_name]
            keyword = parts[2]
            if keyword == "origin":
                return bay["origin"]
            elif keyword == "center":
                box = _bay_footprint(bay)
                return [(box[0] + box[1]) / 2, (box[2] + box[3]) / 2]
            elif keyword == "void":
                return bay.get("void_center", bay["origin"])
            else:
                raise ValueError(
                    f"Unknown bay location '{keyword}'. Use: origin, center, void.")
        elif len(parts) >= 2 and parts[0] == "site":
            site = state.get("site", {})
            keyword = parts[1]
            if keyword == "origin":
                return site.get("origin", [0, 0])
            elif keyword == "center":
                o = site.get("origin", [0, 0])
                w = site.get("width", 180)
                h = site.get("height", 260)
                return [o[0] + w / 2, o[1] + h / 2]
            else:
                raise ValueError(
                    f"Unknown site location '{keyword}'. Use: origin, center.")
        else:
            raise ValueError(
                f"Cannot parse location: '{desc}'. "
                f"Use format like 'bay A origin' or 'site center'.")

    try:
        p1 = _resolve(from_desc)
        p2 = _resolve(to_desc)
    except ValueError as e:
        return f"ERROR: {e}"

    dist = _distance(p1, p2)
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])

    lines = [
        f"OK: Distance from '{from_desc}' to '{to_desc}':",
        f"  Straight line: {dist:.1f} ft",
        f"  Horizontal (X): {dx:.1f} ft",
        f"  Vertical (Y): {dy:.1f} ft",
        f"  From: ({p1[0]:.1f}, {p1[1]:.1f})",
        f"  To: ({p2[0]:.1f}, {p2[1]:.1f})",
        "READY:"
    ]
    return "\n".join(lines)
