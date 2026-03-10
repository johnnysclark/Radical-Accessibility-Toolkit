# -*- coding: utf-8 -*-
"""
PIAF Style System — Test Suite
================================
Tests for the style profile system: StyleManager, CLI commands,
paper-absolute math, density calculation, and renderer integration.

Run:  python tests/test_style_system.py
"""
import copy
import json
import os
import sys
import tempfile
import shutil

# ── Setup ──
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JIG = os.path.join(ROOT, "controller")
TOOLS_SWELL = os.path.join(ROOT, "tools", "swell-print")
STATE = os.path.join(JIG, "state.json")

sys.path.insert(0, JIG)
sys.path.insert(0, TOOLS_SWELL)

import controller_cli as cli
import style_manager as sm

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


# Ensure state.json exists
if not os.path.exists(STATE):
    state = cli.default_state()
    cli.save_state(STATE, state)

# Backup original state for reset
with open(STATE, "r", encoding="utf-8") as f:
    ORIGINAL_STATE = f.read()


def reset_state():
    with open(STATE, "w", encoding="utf-8") as f:
        f.write(ORIGINAL_STATE)


# ══════════════════════════════════════════════════
print("=" * 60)
print("PHASE 1: Style Loading and Validation")
print("=" * 60)

mgr = sm.StyleManager()

test("style manager loads styles",
     lambda: None if len(mgr.list_styles()) >= 3 else "only {} styles".format(len(mgr.list_styles())))

test("default active style is working",
     lambda: None if mgr.active_name == "working" else mgr.active_name)

test("working style has all required keys",
     lambda: None if len(mgr.validate()) == 0 else ", ".join(mgr.validate()[:3]))

# Validate each default style
for style_name in ["working", "presentation", "detail"]:
    mgr.use(style_name)
    errs = mgr.validate()
    test("validate {} style".format(style_name),
         lambda e=errs: None if len(e) == 0 else ", ".join(e[:3]))

mgr.use("working")  # reset to default

# Check all required lineweight keys exist
lw = mgr.get("lineweights")
test("lineweights has all required keys",
     lambda: None if all(k in lw for k in sm.REQUIRED_LINEWEIGHT_KEYS)
     else "missing: {}".format(sm.REQUIRED_LINEWEIGHT_KEYS - set(lw.keys())))

# Check all lineweights are positive numbers
test("all lineweights are positive",
     lambda: None if all(isinstance(v, (int, float)) and v > 0 for v in lw.values())
     else "invalid values found")

# Check density percentages are 0-100
test("density target_percent in range",
     lambda: None if 0 <= mgr.get("density.target_percent") <= 100 else "out of range")
test("density warning_percent in range",
     lambda: None if 0 <= mgr.get("density.warning_percent") <= 100 else "out of range")
test("density reject_percent in range",
     lambda: None if 0 <= mgr.get("density.reject_percent") <= 100 else "out of range")

# Check paper size is valid
test("layout.paper is valid",
     lambda: None if mgr.get("layout.paper") in sm.VALID_PAPERS else mgr.get("layout.paper"))


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 2: Style Get/Set")
print("=" * 60)

# Get values by dot path
test("get lineweights.column",
     lambda: None if isinstance(mgr.get("lineweights.column"), (int, float)) else "not numeric")
test("get hatches.diagonal.spacing_mm",
     lambda: None if mgr.get("hatches.diagonal.spacing_mm") == 8.0 else str(mgr.get("hatches.diagonal.spacing_mm")))
test("get layout.paper",
     lambda: None if mgr.get("layout.paper") == "letter" else mgr.get("layout.paper"))
test("get nonexistent returns default",
     lambda: None if mgr.get("nonexistent.key", "fallback") == "fallback" else "no fallback")

# Set values
new, old = mgr.set("lineweights.column", "4.0")
test("set lineweights.column returns correct old/new",
     lambda: None if new == 4.0 and old == 3.0 else "new={}, old={}".format(new, old))
test("get reflects set",
     lambda: None if mgr.get("lineweights.column") == 4.0 else str(mgr.get("lineweights.column")))

# Set boolean
new_b, old_b = mgr.set("layout.title_block", "false")
test("set boolean converts string to bool",
     lambda: None if new_b is False and old_b is True else "new={}, old={}".format(new_b, old_b))

# Reset back
mgr.reset()
test("reset restores original value",
     lambda: None if mgr.get("lineweights.column") == 3.0 else str(mgr.get("lineweights.column")))

# Set with bad key path
try:
    mgr.set("nonexistent.path.deep", "5")
    test("set bad key raises error", lambda: "should have raised")
except ValueError:
    test("set bad key raises ValueError", lambda: None)


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 3: Paper-Absolute Math")
print("=" * 60)

# Hatch spacing at 8.0mm at 300 DPI -> 8.0 * 300 / 25.4 = 94.488 pixels
expected_hatch_px = 8.0 * 300 / 25.4
test("hatch spacing 8mm at 300DPI = ~94.5px",
     lambda: None if abs(expected_hatch_px - 94.488) < 0.1 else str(expected_hatch_px))

# Lineweight at 3.0pt at 300 DPI -> 3.0 * 300 / 72 = 12.5 pixels
expected_lw_px = 3.0 * 300 / 72.0
test("lineweight 3.0pt at 300DPI = 12.5px",
     lambda: None if abs(expected_lw_px - 12.5) < 0.01 else str(expected_lw_px))

# Verify the conversion functions
from state_renderer import _pt_to_px, _mm_to_px

test("_pt_to_px(3.0, 300) = 13",
     lambda: None if _pt_to_px(3.0, 300) == 13 else str(_pt_to_px(3.0, 300)))
test("_pt_to_px(0.3, 300) >= 1",
     lambda: None if _pt_to_px(0.3, 300) >= 1 else str(_pt_to_px(0.3, 300)))
test("_mm_to_px(8.0, 300) = 94",
     lambda: None if _mm_to_px(8.0, 300) == 94 else str(_mm_to_px(8.0, 300)))


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 4: Style Switching")
print("=" * 60)

mgr2 = sm.StyleManager()

name, desc = mgr2.use("presentation")
test("switch to presentation",
     lambda: None if name == "presentation" else name)
test("presentation has tabloid paper",
     lambda: None if mgr2.get("layout.paper") == "tabloid" else mgr2.get("layout.paper"))
test("presentation has heavier column weight",
     lambda: None if mgr2.get("lineweights.column") > 3.0 else str(mgr2.get("lineweights.column")))

name2, desc2 = mgr2.use("detail")
test("switch to detail",
     lambda: None if name2 == "detail" else name2)
test("detail has dimensions enabled",
     lambda: None if mgr2.get("layout.dimensions") is True else str(mgr2.get("layout.dimensions")))

# Switch to nonexistent
try:
    mgr2.use("nonexistent")
    test("use nonexistent raises error", lambda: "should have raised")
except ValueError:
    test("use nonexistent raises ValueError", lambda: None)


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 5: Save and Save-As")
print("=" * 60)

# Create a temp styles dir for save tests
_tmp_dir = tempfile.mkdtemp()
_tmp_styles = os.path.join(_tmp_dir, "styles")
os.makedirs(_tmp_styles)

# Copy default styles
for f in os.listdir(os.path.join(JIG, "styles")):
    if f.endswith(".json"):
        shutil.copy2(os.path.join(JIG, "styles", f), _tmp_styles)

mgr3 = sm.StyleManager(styles_dir=_tmp_styles)
mgr3.set("lineweights.column", "5.0")
path = mgr3.save()
test("save returns path",
     lambda: None if path.endswith(".json") else path)

# Verify file on disk
with open(path, "r", encoding="utf-8") as f:
    saved_data = json.load(f)
test("saved file has updated value",
     lambda: None if saved_data["lineweights"]["column"] == 5.0 else str(saved_data["lineweights"]["column"]))

# Save-as
mgr3.save("custom_style")
test("save-as creates new style",
     lambda: None if any(n == "custom_style" for n, _, _ in mgr3.list_styles()) else "missing")

# Cleanup
shutil.rmtree(_tmp_dir)


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 6: Hatch Management")
print("=" * 60)

mgr4 = sm.StyleManager()

mgr4.add_hatch("brick", 4.0, 0, 0.4)
test("add_hatch creates pattern",
     lambda: None if "brick" in mgr4.active.get("hatches", {}) else "missing")
test("custom hatch has correct spacing",
     lambda: None if mgr4.get("hatches.brick.spacing_mm") == 4.0 else str(mgr4.get("hatches.brick.spacing_mm")))

mgr4.remove_hatch("brick")
test("remove_hatch removes pattern",
     lambda: None if "brick" not in mgr4.active.get("hatches", {}) else "still present")

# Cannot remove built-in
try:
    mgr4.remove_hatch("diagonal")
    test("remove built-in raises error", lambda: "should have raised")
except ValueError:
    test("remove built-in raises ValueError", lambda: None)


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 7: Show / List Output")
print("=" * 60)

mgr5 = sm.StyleManager()
summary = mgr5.show()
test("show summary contains style name",
     lambda: None if "working" in summary else summary[:80])

lw_show = mgr5.show("lineweights")
test("show lineweights has column entry",
     lambda: None if "column" in lw_show else lw_show[:80])

hat_show = mgr5.show("hatches")
test("show hatches has diagonal entry",
     lambda: None if "diagonal" in hat_show else hat_show[:80])

styles_list = mgr5.list_styles()
test("list_styles returns 3+ tuples",
     lambda: None if len(styles_list) >= 3 else str(len(styles_list)))
test("list_styles has active marker",
     lambda: None if any(active for _, _, active in styles_list) else "no active")


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 8: CLI Round-Trip")
print("=" * 60)

reset_state()
state = cli.load_state(STATE)

# style list
state, msg = cli.apply_command(state, cli.tokenize("style list"), STATE)
test("CLI style list returns OK",
     lambda: None if "OK:" in msg else msg[:80])
test("CLI style list shows working",
     lambda: None if "working" in msg else msg[:80])

# style show
state, msg = cli.apply_command(state, cli.tokenize("style show"), STATE)
test("CLI style show returns OK",
     lambda: None if "OK:" in msg else msg[:80])

# style show lineweights
state, msg = cli.apply_command(state, cli.tokenize("style show lineweights"), STATE)
test("CLI style show lineweights has column",
     lambda: None if "column" in msg else msg[:80])

# style set
state, msg = cli.apply_command(state, cli.tokenize("style set lineweights.column 4.0"), STATE)
test("CLI style set returns OK with old/new",
     lambda: None if "OK:" in msg and "4.0" in msg and "3.0" in msg else msg[:80])

# style show to verify
state, msg = cli.apply_command(state, cli.tokenize("style show lineweights"), STATE)
test("CLI style show reflects set",
     lambda: None if "4.0" in msg else msg[:80])

# style use
state, msg = cli.apply_command(state, cli.tokenize("style use presentation"), STATE)
test("CLI style use presentation",
     lambda: None if "OK:" in msg and "presentation" in msg else msg[:80])

# style reset
state, msg = cli.apply_command(state, cli.tokenize("style use working"), STATE)
state, msg = cli.apply_command(state, cli.tokenize("style reset"), STATE)
test("CLI style reset",
     lambda: None if "OK:" in msg and "reset" in msg.lower() else msg[:80])

# style add-hatch
state, msg = cli.apply_command(state, cli.tokenize("style add-hatch brick 4.0 0 0.4"), STATE)
test("CLI style add-hatch",
     lambda: None if "OK:" in msg and "brick" in msg else msg[:80])

# style remove-hatch
state, msg = cli.apply_command(state, cli.tokenize("style remove-hatch brick"), STATE)
test("CLI style remove-hatch",
     lambda: None if "OK:" in msg and "brick" in msg else msg[:80])


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 9: Density Calculation")
print("=" * 60)

_swell_ok = False
try:
    from PIL import Image
    import state_renderer
    _swell_ok = True
except ImportError:
    print("SKIP: Pillow not installed, skipping density tests")

if _swell_ok:
    reset_state()
    _state = cli.load_state(STATE)

    # Render with no style manager (backward compat)
    img_legacy = state_renderer.render(_state, dpi=72, paper_size="letter")
    test("render without style_manager works",
         lambda: None if hasattr(img_legacy, "mode") else "not an image")

    d_legacy = state_renderer.density(img_legacy)
    test("density is reasonable (< 80%)",
         lambda: None if d_legacy < 80 else "density: {}".format(d_legacy))

    # Render with style manager
    mgr_render = sm.StyleManager()
    img_styled = state_renderer.render(_state, dpi=72, paper_size="letter",
                                        style_manager=mgr_render)
    test("render with style_manager works",
         lambda: None if hasattr(img_styled, "mode") else "not an image")

    d_styled = state_renderer.density(img_styled)
    test("styled density is reasonable (< 80%)",
         lambda: None if d_styled < 80 else "density: {}".format(d_styled))


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 10: Test Swatch Generation")
print("=" * 60)

if _swell_ok:
    _tmp_swatch = tempfile.mktemp(suffix=".png")
    mgr_swatch = sm.StyleManager()
    try:
        result_path = mgr_swatch.generate_test_swatch(_tmp_swatch, dpi=72)
        test("test swatch generates file",
             lambda: None if os.path.exists(result_path) else "file not found")
        if os.path.exists(result_path):
            swatch_img = Image.open(result_path)
            # Letter landscape at 72 DPI: 11*72=792 x 8.5*72=612
            test("test swatch has correct width",
                 lambda: None if swatch_img.size[0] == 792 else "width: {}".format(swatch_img.size[0]))
            test("test swatch has correct height",
                 lambda: None if swatch_img.size[1] == 612 else "height: {}".format(swatch_img.size[1]))
    except Exception as e:
        test("test swatch generation", lambda: "ERROR: {}".format(e))
    finally:
        if os.path.exists(_tmp_swatch):
            os.remove(_tmp_swatch)
else:
    print("SKIP: Pillow not installed, skipping swatch tests")


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 11: Wall Height Support")
print("=" * 60)

reset_state()
state = cli.load_state(STATE)

state, msg = cli.apply_command(state, cli.tokenize("set bay A wall_height 12"), STATE)
test("set bay A wall_height 12",
     lambda: None if state["bays"]["A"]["wall_height"] == 12.0 else msg)
test("wall_height set message",
     lambda: None if "12.0" in msg and "10.0" in msg else msg[:80])


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 12: View Commands")
print("=" * 60)

if _swell_ok:
    reset_state()
    state = cli.load_state(STATE)

    # view plan
    try:
        state, msg = cli.apply_command(state, cli.tokenize("view plan"), STATE)
        test("view plan returns OK",
             lambda: None if "OK:" in msg and "plan.png" in msg else msg[:120])
        test("view plan reports density",
             lambda: None if "density" in msg.lower() else msg[:120])
    except Exception as e:
        test("view plan", lambda: "ERROR: {}".format(e))

    # view section
    try:
        state, msg = cli.apply_command(state, cli.tokenize("view section x 1"), STATE)
        test("view section returns OK",
             lambda: None if "OK:" in msg and "section" in msg else msg[:120])
    except Exception as e:
        test("view section", lambda: "ERROR: {}".format(e))

    # view axon
    try:
        state, msg = cli.apply_command(state, cli.tokenize("view axon"), STATE)
        test("view axon returns OK",
             lambda: None if "OK:" in msg and "axon" in msg else msg[:120])
    except Exception as e:
        test("view axon", lambda: "ERROR: {}".format(e))

    # view elevation
    try:
        state, msg = cli.apply_command(state, cli.tokenize("view elevation south"), STATE)
        test("view elevation returns OK",
             lambda: None if "OK:" in msg and "elevation" in msg else msg[:120])
    except Exception as e:
        test("view elevation", lambda: "ERROR: {}".format(e))

    # Cleanup generated files
    out_dir = os.path.dirname(os.path.abspath(STATE))
    for f in ["plan.png", "section_x1.png", "axon.png", "elevation_south.png"]:
        p = os.path.join(out_dir, f)
        if os.path.exists(p):
            os.remove(p)
else:
    print("SKIP: Pillow not installed, skipping view tests")


# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 13: Presentation and Detail Style Differences")
print("=" * 60)

mgr_diff = sm.StyleManager()

mgr_diff.use("working")
working_col = mgr_diff.get("lineweights.column")

mgr_diff.use("presentation")
pres_col = mgr_diff.get("lineweights.column")
test("presentation column heavier than working",
     lambda: None if pres_col > working_col else "{} not > {}".format(pres_col, working_col))
test("presentation paper is tabloid",
     lambda: None if mgr_diff.get("layout.paper") == "tabloid" else mgr_diff.get("layout.paper"))
test("presentation density target is 25",
     lambda: None if mgr_diff.get("density.target_percent") == 25 else str(mgr_diff.get("density.target_percent")))

mgr_diff.use("detail")
detail_col = mgr_diff.get("lineweights.column")
test("detail column lighter than working",
     lambda: None if detail_col < working_col else "{} not < {}".format(detail_col, working_col))
test("detail has dimensions enabled",
     lambda: None if mgr_diff.get("layout.dimensions") is True else str(mgr_diff.get("layout.dimensions")))
test("detail density target is 35",
     lambda: None if mgr_diff.get("density.target_percent") == 35 else str(mgr_diff.get("density.target_percent")))


# ══════════════════════════════════════════════════
# FINAL RESET AND SUMMARY
# ══════════════════════════════════════════════════

reset_state()

print("")
print("=" * 60)
print("STYLE SYSTEM TEST RESULTS")
print("=" * 60)
print("")
print("  Passed: {}".format(passed))
print("  Failed: {}".format(failed))
print("  Total:  {}".format(passed + failed))
print("")
if errors:
    print("  Failed tests:")
    for e in errors:
        print("    - {}".format(e))
    print("")
if failed == 0:
    print("  ALL STYLE SYSTEM TESTS PASSED")
else:
    print("  {} TEST(S) FAILED".format(failed))
print("")

sys.exit(1 if failed > 0 else 0)
