# -*- coding: utf-8 -*-
"""
Community Learning Center — Demo Project
=========================================
Generates a rich state.json showcasing every Layout Jig feature:
rectangular and radial bays, walls, doors, windows, portals,
corridors, named rooms with all 5 hatch patterns, zones, global grid,
voids, Braille labels, legend, tactile 3D export, and section cuts.

Usage:
    python demos/community_center_demo.py
    python demos/community_center_demo.py --output /path/to/state.json
"""
import argparse
import json
import os
import sys

# ── Make controller importable ──
_demo_dir = os.path.dirname(os.path.abspath(__file__))
_controller_dir = os.path.dirname(_demo_dir)
if _controller_dir not in sys.path:
    sys.path.insert(0, _controller_dir)

import controller_cli as cli
import braille as _braille

# ── Helpers ──

def _br(text):
    """Shorthand for Braille translation."""
    return _braille.to_braille(text)


def _make_cell(name, label, hatch="none", hatch_scale=1.0):
    """Build a cell dict with Braille label."""
    return {
        "name": name,
        "label": label,
        "braille": _br(label),
        "hatch": hatch,
        "hatch_scale": hatch_scale,
        "hatch_rotation": 0.0,
    }


def build_state():
    """Construct the Community Learning Center state."""

    # ── Bay A: Main Hall ──
    bay_a = cli._default_bay(
        "A", (15, 15),
        grid_type="rectangular", z_order=0,
        bays=(6, 3), spacing=(24, 24),
        label="Main Hall",
    )
    bay_a["walls"] = {"enabled": True, "thickness": 0.5}
    bay_a["corridor"] = {
        "enabled": True, "axis": "x", "position": 1,
        "width": 8.0, "loading": "double",
        "hatch": "Hatch1", "hatch_scale": 4.0,
    }
    bay_a["apertures"] = [
        {"id": "d1", "type": "door", "axis": "x", "gridline": 0,
         "corner": 10.0, "width": 3.0, "height": 7.0,
         "hinge": "start", "swing": "positive"},
        {"id": "d2", "type": "door", "axis": "x", "gridline": 3,
         "corner": 10.0, "width": 3.0, "height": 7.0,
         "hinge": "end", "swing": "negative"},
        {"id": "d3", "type": "door", "axis": "y", "gridline": 0,
         "corner": 30.0, "width": 3.0, "height": 7.0,
         "hinge": "start", "swing": "positive"},
        {"id": "w1", "type": "window", "axis": "y", "gridline": 0,
         "corner": 8.0, "width": 6.0, "height": 4.0,
         "hinge": "start", "swing": "positive"},
        {"id": "w2", "type": "window", "axis": "y", "gridline": 6,
         "corner": 8.0, "width": 6.0, "height": 4.0,
         "hinge": "start", "swing": "positive"},
        {"id": "p1", "type": "portal", "axis": "x", "gridline": 1,
         "corner": 30.0, "width": 10.0, "height": 9.0,
         "hinge": "start", "swing": "positive"},
    ]
    bay_a["void_center"] = [87.0, 51.0]
    bay_a["void_size"] = [30.0, 20.0]
    bay_a["void_shape"] = "rectangle"
    bay_a["braille"] = _br("Main Hall")

    # Bay A cells: 6 columns x 3 rows
    bay_a["cells"] = {
        # Row 0 (south side of corridor)
        "0,0": _make_cell("Lobby", "Lobby", "dots"),
        "1,0": _make_cell("Lobby", "Lobby", "dots"),
        "2,0": _make_cell("Classroom 1", "Classroom 1", "diagonal"),
        "3,0": _make_cell("Classroom 1", "Classroom 1", "diagonal"),
        "4,0": _make_cell("Office", "Office", "horizontal"),
        "5,0": _make_cell("Storage", "Storage", "solid"),
        # Row 1 (corridor — hatched via corridor settings)
        "0,1": _make_cell("Corridor", "Corridor"),
        "1,1": _make_cell("Corridor", "Corridor"),
        "2,1": _make_cell("Corridor", "Corridor"),
        "3,1": _make_cell("Corridor", "Corridor"),
        "4,1": _make_cell("Corridor", "Corridor"),
        "5,1": _make_cell("Corridor", "Corridor"),
        # Row 2 (north side of corridor)
        "0,2": _make_cell("Restroom", "Restroom", "dots"),
        "1,2": _make_cell("Restroom", "Restroom", "dots"),
        "2,2": _make_cell("Classroom 2", "Classroom 2", "crosshatch"),
        "3,2": _make_cell("Classroom 2", "Classroom 2", "crosshatch"),
        "4,2": _make_cell("Classroom 2", "Classroom 2", "crosshatch"),
        "5,2": _make_cell("Office", "Office", "horizontal"),
    }

    # ── Bay B: Amphitheater ──
    bay_b = cli._default_bay(
        "B", (140, 180),
        grid_type="radial", z_order=2,
        rings=4, ring_spacing=15, arms=6,
        arc_deg=180, arc_start_deg=0,
        label="Amphitheater",
    )
    bay_b["void_center"] = [140.0, 180.0]
    bay_b["void_size"] = [15.0, 15.0]
    bay_b["void_shape"] = "circle"
    bay_b["braille"] = _br("Amphitheater")

    # ── Bay C: Workshop Wing ──
    bay_c = cli._default_bay(
        "C", (15, 180),
        grid_type="rectangular", z_order=1,
        bays=(3, 2), spacing=(20, 25),
        rotation=15.0,
        label="Workshop Wing",
    )
    bay_c["walls"] = {"enabled": True, "thickness": 0.5}
    bay_c["corridor"] = {
        "enabled": True, "axis": "y", "position": 1,
        "width": 6.0, "loading": "single",
        "hatch": "Dash", "hatch_scale": 4.0,
    }
    bay_c["apertures"] = [
        {"id": "d4", "type": "door", "axis": "x", "gridline": 0,
         "corner": 8.0, "width": 3.0, "height": 7.0,
         "hinge": "start", "swing": "positive"},
        {"id": "d5", "type": "door", "axis": "y", "gridline": 3,
         "corner": 10.0, "width": 4.0, "height": 7.0,
         "hinge": "end", "swing": "positive"},
    ]
    bay_c["braille"] = _br("Workshop Wing")

    # Bay C cells: 3 columns x 2 rows
    bay_c["cells"] = {
        "0,0": _make_cell("Wood Shop", "Wood Shop", "crosshatch"),
        "1,0": _make_cell("Metal Shop", "Metal Shop", "solid"),
        "2,0": _make_cell("Tool Room", "Tool Room", "horizontal"),
        "0,1": _make_cell("Studio A", "Studio A", "diagonal"),
        "1,1": _make_cell("Corridor", "Corridor"),
        "2,1": _make_cell("Studio B", "Studio B", "dots"),
    }

    # ── Bay D: Gallery ──
    bay_d = cli._default_bay(
        "D", (15, 105),
        grid_type="rectangular", z_order=3,
        bays=(5, 1), spacing=(28, 30),
        label="Gallery",
    )
    bay_d["spacing_x"] = [20.0, 32.0, 20.0, 32.0, 36.0]
    bay_d["walls"] = {"enabled": True, "thickness": 0.5}
    bay_d["apertures"] = [
        {"id": "w3", "type": "window", "axis": "x", "gridline": 0,
         "corner": 5.0, "width": 8.0, "height": 5.0,
         "hinge": "start", "swing": "positive"},
        {"id": "w4", "type": "window", "axis": "x", "gridline": 0,
         "corner": 30.0, "width": 8.0, "height": 5.0,
         "hinge": "start", "swing": "positive"},
        {"id": "w5", "type": "window", "axis": "x", "gridline": 0,
         "corner": 55.0, "width": 8.0, "height": 5.0,
         "hinge": "start", "swing": "positive"},
        {"id": "w6", "type": "window", "axis": "x", "gridline": 0,
         "corner": 80.0, "width": 8.0, "height": 5.0,
         "hinge": "start", "swing": "positive"},
        {"id": "d6", "type": "door", "axis": "x", "gridline": 1,
         "corner": 5.0, "width": 3.0, "height": 7.0,
         "hinge": "start", "swing": "negative"},
    ]
    bay_d["braille"] = _br("Gallery")

    # Bay D cells: 5 columns x 1 row
    bay_d["cells"] = {
        "0,0": _make_cell("Gallery 1", "Gallery 1", "diagonal"),
        "1,0": _make_cell("Gallery 2", "Gallery 2", "dots"),
        "2,0": _make_cell("Gallery 3", "Gallery 3", "horizontal"),
        "3,0": _make_cell("Gallery 4", "Gallery 4", "crosshatch"),
        "4,0": _make_cell("Gallery 5", "Gallery 5", "solid"),
    }

    # ── Assemble bays ──
    bays_dict = {"A": bay_a, "B": bay_b, "C": bay_c, "D": bay_d}

    # ── Rooms (auto-generated + hatch overrides) ──
    rooms = cli._auto_rooms(bays_dict)
    rooms["bay_A"]["hatch_image"] = "diagonal"
    rooms["bay_B"]["hatch_image"] = "dots"
    rooms["bay_C"]["hatch_image"] = "crosshatch"
    rooms["bay_D"]["hatch_image"] = "horizontal"
    # Voids: courtyard open, amphitheater center open
    rooms["void_A"]["hatch_image"] = "none"
    rooms["void_B"]["hatch_image"] = "none"

    # ── Zones ──
    zones = {
        "Public": {
            "corners": [[10, 10], [130, 10], [130, 90], [10, 90]],
            "program_type": "public",
            "label": "Public Zone",
            "braille": _br("Public Zone"),
        },
        "Education": {
            "corners": [[120, 10], [210, 10], [210, 90], [120, 90]],
            "program_type": "education",
            "label": "Education Zone",
            "braille": _br("Education Zone"),
        },
        "Creative": {
            "corners": [[10, 170], [210, 170], [210, 260], [10, 260]],
            "program_type": "creative",
            "label": "Creative Zone",
            "braille": _br("Creative Zone"),
        },
        "Admin": {
            "corners": [[10, 100], [210, 100], [210, 160], [10, 160]],
            "program_type": "administration",
            "label": "Admin Zone",
            "braille": _br("Admin Zone"),
        },
    }

    # ── Global grid ──
    grid = {"spacing": 30.0, "rotation_deg": 0.0, "origin": [0.0, 0.0]}

    # ── Style ──
    style = {
        "column_size": 1.5,
        "heavy_lineweight_mm": 1.40,
        "light_lineweight_mm": 0.08,
        "corridor_lineweight_mm": 0.35,
        "wall_lineweight_mm": 0.25,
        "label_text_height": 0.3,
        "braille_text_height": 0.5,
        "corridor_dash_len": 3.0,
        "corridor_gap_len": 2.0,
        "background_pad": 2.0,
        "label_offset": 3.0,
        "arc_segments": 16,
    }

    # ── Legend ──
    legend = cli._default_legend()
    legend["title"] = "Community Learning Center"
    legend["title_braille"] = _br("Community Learning Center")
    legend["show_braille"] = True
    legend["show_hatches"] = True
    legend["show_apertures"] = True

    # ── Tactile 3D ──
    tactile3d = cli._default_tactile3d()
    tactile3d["enabled"] = True
    tactile3d["wall_height"] = 10.0
    tactile3d["cut_height"] = 4.0
    tactile3d["floor_enabled"] = True
    tactile3d["auto_export"] = False
    tactile3d["export_path"] = "./community_center.stl"

    # ── Section ──
    section = {"axis": "x", "offset": 51.0, "last_export_path": None}

    # ── Assemble state ──
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    state = {
        "schema": cli.SCHEMA,
        "meta": {
            "created": now,
            "last_saved": now,
            "notes": "Community Learning Center demo — showcases all Layout Jig features.",
        },
        "site": {
            "origin": [0.0, 0.0],
            "width": 220.0,
            "height": 280.0,
            "corners": [[0.0, 0.0], [220.0, 0.0], [220.0, 280.0], [0.0, 280.0]],
        },
        "zones": zones,
        "grid": grid,
        "style": style,
        "bays": bays_dict,
        "blocks": cli._default_blocks(),
        "rooms": rooms,
        "legend": legend,
        "tactile3d": tactile3d,
        "section": section,
        "hatch_library_path": "./hatches/",
        "print": cli._default_print(),
        "bambu": cli._default_bambu(),
    }

    return state


def summarize(state):
    """Print a screen-reader-friendly summary."""
    bays = state["bays"]
    zones = state["zones"]
    total_apertures = sum(len(b.get("apertures", [])) for b in bays.values())
    total_cells = sum(len(b.get("cells", {})) for b in bays.values())
    corridors = sum(1 for b in bays.values()
                    if b.get("corridor", {}).get("enabled"))
    walled = sum(1 for b in bays.values()
                 if b.get("walls", {}).get("enabled"))

    lines = [
        "OK: Community Learning Center demo generated.",
        "  Site: {w:.0f} x {h:.0f} ft.".format(
            w=state["site"]["width"], h=state["site"]["height"]),
        "  Bays: {n} ({names}).".format(
            n=len(bays), names=", ".join(sorted(bays.keys()))),
    ]
    for name in sorted(bays):
        b = bays[name]
        gt = b.get("grid_type", "rectangular")
        lbl = b.get("label", "Bay " + name)
        if gt == "rectangular":
            nx, ny = b["bays"]
            lines.append("    {n}: {lbl}, {gt} {nx}x{ny}.".format(
                n=name, lbl=lbl, gt=gt, nx=nx, ny=ny))
        else:
            lines.append("    {n}: {lbl}, {gt} {r} rings {a} arms.".format(
                n=name, lbl=lbl, gt=gt,
                r=b.get("rings", 4), a=b.get("arms", 8)))
    lines.extend([
        "  Walls: {n} bays walled.".format(n=walled),
        "  Apertures: {n} total (doors, windows, portals).".format(
            n=total_apertures),
        "  Corridors: {n} bays with corridors.".format(n=corridors),
        "  Cells: {n} named cells across all bays.".format(n=total_cells),
        "  Zones: {n} ({names}).".format(
            n=len(zones), names=", ".join(sorted(zones.keys()))),
        "  Grid: {s:.0f} ft spacing.".format(
            s=state["grid"]["spacing"]),
        "  Legend: enabled, {pos}.".format(
            pos=state["legend"]["position"]),
        "  Tactile3D: {e}, {h:.0f} ft walls.".format(
            e="enabled" if state["tactile3d"]["enabled"] else "disabled",
            h=state["tactile3d"]["wall_height"]),
        "  Section: {a}={o:.0f} ft.".format(
            a=state["section"]["axis"].upper(),
            o=state["section"]["offset"]),
        "READY:",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Community Learning Center demo state.")
    parser.add_argument(
        "--output", "-o",
        default=os.path.join(_controller_dir, "state.json"),
        help="Output path for state.json (default: controller/state.json)")
    args = parser.parse_args()

    state = build_state()
    text = json.dumps(state, indent=2, ensure_ascii=False)
    cli._atomic_write(args.output, text)

    summary = summarize(state)
    print(summary)
    print("  Written to: {p}".format(p=os.path.abspath(args.output)))


if __name__ == "__main__":
    main()
