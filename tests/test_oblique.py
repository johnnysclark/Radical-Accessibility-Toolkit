# -*- coding: utf-8 -*-
"""
Oblique Projection Test — Sonsbeek Pavilion Demo
==================================================
Tests the ObliqueRenderer with a synthetic Sonsbeek Pavilion state.

Aldo van Eyck's 1966 Sonsbeek Pavilion: a field of parallel masonry
walls within a circular site, with circular columns. Walls are 14 m
(~46 ft) high; section cut at 3 m (~10 ft).

Run:  python tests/test_oblique.py
"""
import sys
import os
import math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "tact", "src", "tactile_core", "core"))
sys.path.insert(0, os.path.join(ROOT, "controller"))


# ---------------------------------------------------------------------------
# Sonsbeek Pavilion State Builder
# ---------------------------------------------------------------------------

# Conversion: 1 meter ~ 3.281 feet
M_TO_FT = 3.281

def _sonsbeek_state():
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

    # Wall rows: each is a 1-bay-wide rectangular bay with walls on
    # the y-axis gridlines (running north-south).
    # Format: (name, origin_x, origin_y, length_ft, has_portal, portal_corner, portal_width)
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

    # Three circular column elements (modeled as small rectangular bays
    # with column dots visible at gridline intersections)
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
            "name": "Sonsbeek Pavilion (test)",
            "description": "Aldo van Eyck, 1966. Synthetic test state for oblique projection.",
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
            "enabled": False,
            "wall_height": wall_height,
            "cut_height": 10.0,  # 3 m in feet
        },
    }
    return state


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

passed = 0
failed = 0
errors = []

def test(name, fn):
    global passed, failed
    try:
        result = fn()
        if result is None:
            print("PASS: {}".format(name))
            passed += 1
        elif isinstance(result, str) and result.startswith("ERROR"):
            print("FAIL: {} -> {}".format(name, result[:120]))
            failed += 1
            errors.append(name)
        else:
            print("PASS: {}".format(name))
            passed += 1
        return result
    except Exception as e:
        print("FAIL: {} -> {}".format(name, str(e)[:120]))
        failed += 1
        errors.append(name)
        return None


def main():
    global passed, failed

    print("=" * 60)
    print("Oblique Projection Tests — Sonsbeek Pavilion")
    print("=" * 60)

    # -- Test 1: State builder --
    state = _sonsbeek_state()
    test("state has schema v2.3",
         lambda: None if state["schema"] == "plan_layout_jig_v2.3" else "ERROR: wrong schema")
    test("state has 10 bays (7 walls + 3 columns)",
         lambda: None if len(state["bays"]) == 10 else
         "ERROR: expected 10, got {}".format(len(state["bays"])))
    test("wall W1 has wall_height 46",
         lambda: None if state["bays"]["W1"]["wall_height"] == 46.0 else "ERROR: wrong height")
    test("wall W1 has portals",
         lambda: None if len(state["bays"]["W1"]["apertures"]) == 2 else "ERROR: missing portals")

    # -- Test 2: Import renderer --
    try:
        from oblique_renderer import render_oblique, density
        from state_renderer import render as render_plan
        test("import oblique_renderer", lambda: None)
    except ImportError as e:
        test("import oblique_renderer", lambda: "ERROR: {}".format(e))
        print("\nERROR: Cannot import oblique_renderer. Install Pillow: pip install Pillow")
        _summary()
        return

    # -- Test 3: render_oblique exists --
    test("render_oblique function exists",
         lambda: None if callable(render_oblique) else "ERROR: missing")

    # -- Test 4: Render oblique at 3m cut (10 ft) --
    cut_height_ft = 10.0  # 3 meters
    try:
        img = render_oblique(state, cut_height=cut_height_ft, dpi=150)
        test("render_oblique returns Image",
             lambda: None if hasattr(img, 'mode') else "ERROR: not an image")
        test("render_oblique is mode '1' (B&W)",
             lambda: None if img.mode == '1' else "ERROR: mode={}".format(img.mode))

        d = density(img)
        test("density is numeric",
             lambda: None if isinstance(d, (int, float)) else
             "ERROR: type={}".format(type(d).__name__))
        test("density between 5-60%",
             lambda: None if 5 <= d <= 60 else
             "ERROR: density={:.1f}% (out of range)".format(d))

        # Save test output
        out_path = os.path.join(HERE, "oblique_sonsbeek.png")
        img.save(out_path, dpi=(150, 150))
        test("saved oblique_sonsbeek.png",
             lambda: None if os.path.isfile(out_path) else "ERROR: file not created")
        print("  -> {}".format(out_path))
    except Exception as e:
        test("render_oblique execution", lambda: "ERROR: {}".format(e))

    # -- Test 5: Different cut heights produce different images --
    try:
        img_low = render_oblique(state, cut_height=5.0, dpi=72)
        img_high = render_oblique(state, cut_height=30.0, dpi=72)
        d_low = density(img_low)
        d_high = density(img_high)
        test("different cut heights produce different densities",
             lambda: None if abs(d_low - d_high) > 0.1 else
             "ERROR: densities too similar ({:.1f} vs {:.1f})".format(d_low, d_high))
    except Exception as e:
        test("cut height variation", lambda: "ERROR: {}".format(e))

    # -- Test 6: Oblique differs from plain plan --
    try:
        img_plan = render_plan(state, dpi=72)
        img_obl = render_oblique(state, cut_height=cut_height_ft, dpi=72)
        d_plan = density(img_plan)
        d_obl = density(img_obl)
        test("oblique differs from plan (density)",
             lambda: None if abs(d_plan - d_obl) > 0.1 else
             "ERROR: too similar ({:.1f} vs {:.1f})".format(d_plan, d_obl))
    except Exception as e:
        test("oblique vs plan comparison", lambda: "ERROR: {}".format(e))

    # -- Test 7: Cabinet oblique (z_scale=0.5) --
    try:
        img_cab = render_oblique(
            state, cut_height=cut_height_ft, z_scale=0.5, dpi=72)
        test("cabinet oblique (z_scale=0.5) renders",
             lambda: None if hasattr(img_cab, 'mode') else "ERROR: not an image")
    except Exception as e:
        test("cabinet oblique", lambda: "ERROR: {}".format(e))

    # -- Test 8: High-res render for visual inspection --
    try:
        img_hires = render_oblique(
            state, cut_height=cut_height_ft, dpi=300, paper_size="tabloid")
        out_hires = os.path.join(HERE, "oblique_sonsbeek_hires.png")
        img_hires.save(out_hires, dpi=(300, 300))
        test("saved high-res tabloid oblique",
             lambda: None if os.path.isfile(out_hires) else "ERROR: file not created")
        print("  -> {}".format(out_hires))
    except Exception as e:
        test("high-res oblique", lambda: "ERROR: {}".format(e))

    _summary()


def _summary():
    print("")
    print("=" * 60)
    if failed == 0:
        print("OK: All {} tests passed.".format(passed))
    else:
        print("ERROR: {} passed, {} failed.".format(passed, failed))
        for e in errors:
            print("  FAILED: {}".format(e))
    print("READY:")


if __name__ == "__main__":
    main()
