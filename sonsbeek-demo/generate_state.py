# -*- coding: utf-8 -*-
"""
Sonsbeek Pavilion — State Generator
=====================================
Generates a state.json for Aldo van Eyck's 1966 Sonsbeek Pavilion.

A field of parallel masonry walls within a circular site, with
circular columns. Walls are 14 m (~46 ft) high.

Usage:
    python generate_state.py              # writes sonsbeek_state.json
    python generate_state.py --pretty     # writes with 2-space indent
    python generate_state.py --out FILE   # writes to custom path

No external dependencies — stdlib only.
"""
import json
import os
import sys

M_TO_FT = 3.281


def build_sonsbeek_state():
    """Build a state dict approximating the Sonsbeek Pavilion.

    Based on Aldo van Eyck's 1966 design:
    - Circular site ~28 m diameter
    - 7 parallel north-south masonry wall rows of varying lengths
    - Walls ~0.6 m (2 ft) thick, 14 m (46 ft) tall
    - Openings (portals) in some walls
    - 3 circular column elements
    """
    site_w = 100.0  # feet (~30 m)
    site_h = 100.0
    wall_thickness = 2.0  # ft (~0.6 m)
    wall_height = 46.0    # ft (~14 m)

    # Wall rows: (name, origin_x, origin_y, length_ft,
    #             has_portal, portal_corner, portal_width)
    wall_rows = [
        # Left cluster
        ("W1", 12.0, 15.0, 70.0, True, 25.0, 8.0),
        ("W2", 22.0, 20.0, 60.0, False, 0, 0),
        ("W3", 32.0, 10.0, 75.0, True, 35.0, 10.0),
        # Center cluster
        ("W4", 44.0, 18.0, 65.0, True, 20.0, 6.0),
        ("W5", 54.0, 12.0, 72.0, True, 40.0, 8.0),
        # Right cluster
        ("W6", 66.0, 22.0, 55.0, True, 15.0, 7.0),
        ("W7", 76.0, 8.0,  80.0, False, 0, 0),
    ]

    bays = {}
    for name, ox, oy, length, has_portal, p_corner, p_width in wall_rows:
        bay = {
            "grid_type": "rectangular",
            "origin": [ox, oy],
            "rotation_deg": 0,
            "bays": [1, 1],
            "spacing": [wall_thickness, length],
            "wall_height": wall_height,
            "walls": {
                "enabled": True,
                "thickness": wall_thickness,
                "A": "on", "B": "on", "C": "on", "D": "on",
            },
            "corridor": {"enabled": False},
            "apertures": [],
        }
        if has_portal:
            bay["apertures"].append({
                "type": "portal",
                "axis": "y",
                "gridline": 0,
                "corner": p_corner,
                "width": p_width,
            })
            bay["apertures"].append({
                "type": "portal",
                "axis": "y",
                "gridline": 1,
                "corner": p_corner,
                "width": p_width,
            })
        bays[name] = bay

    # Three circular column elements
    columns = [
        ("C1", 38.0, 45.0),
        ("C2", 55.0, 55.0),
        ("C3", 72.0, 40.0),
    ]
    for cname, cx, cy in columns:
        bays[cname] = {
            "grid_type": "rectangular",
            "origin": [cx, cy],
            "rotation_deg": 0,
            "bays": [1, 1],
            "spacing": [3.0, 3.0],
            "wall_height": wall_height,
            "walls": {"enabled": False},
            "corridor": {"enabled": False},
            "apertures": [],
        }

    state = {
        "schema": "plan_layout_jig_v2.3",
        "meta": {
            "name": "Sonsbeek Pavilion",
            "description": "Aldo van Eyck, 1966. Parallel masonry walls "
                           "with portals and column clusters.",
        },
        "site": {
            "width": site_w,
            "height": site_h,
        },
        "style": {
            "column_size": 1.5,
        },
        "bays": bays,
        "tactile3d": {
            "enabled": True,
            "wall_height": wall_height,
            "cut_height": 10.0,
        },
    }
    return state


def main():
    indent = None
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "sonsbeek_state.json")

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--pretty":
            indent = 2
        elif args[i] == "--out" and i + 1 < len(args):
            out_path = args[i + 1]
            i += 1
        i += 1

    state = build_sonsbeek_state()
    text = json.dumps(state, indent=indent)

    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, out_path)

    print("OK: Wrote {} ({} bytes)".format(out_path, len(text)))
    print("READY:")


if __name__ == "__main__":
    main()
