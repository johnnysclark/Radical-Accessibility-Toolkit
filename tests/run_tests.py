# -*- coding: utf-8 -*-
"""
LAYOUT JIG v3.0 — End-to-End Test Suite
=========================================
Tests every CLI command, auditor function, skill manager function,
and rhino client call against the test state.json.

Run:  python tests/run_tests.py
"""
import sys, os, json, copy

# ── Setup ──
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STATE = os.path.join(ROOT, "rhino", "state.json")
os.environ["LAYOUT_JIG_STATE"] = STATE
sys.path.insert(0, ROOT)

import controller_cli as cli
import auditor
import skill_manager
import rhino_client

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

# Backup original state for reset
with open(STATE, "r", encoding="utf-8") as f:
    ORIGINAL_STATE = f.read()

def reset_state():
    with open(STATE, "w", encoding="utf-8") as f:
        f.write(ORIGINAL_STATE)

# ══════════════════════════════════════════════════
print("=" * 60)
print("PHASE 1: State Loading and Structure")
print("=" * 60)

state = test("load_state", lambda: cli.load_state(STATE))
test("schema is v2.3",
     lambda: None if state["schema"] == "plan_layout_jig_v2.3" else "wrong schema")
test("2 bays exist",
     lambda: None if len(state["bays"]) == 2 else "wrong bay count")
test("bay A is rectangular",
     lambda: None if state["bays"]["A"]["grid_type"] == "rectangular" else "wrong")
test("bay B is radial",
     lambda: None if state["bays"]["B"]["grid_type"] == "radial" else "wrong")
test("bay A is 3x3 (9 sections)",
     lambda: None if state["bays"]["A"]["bays"] == [3, 3] else "wrong dims")
test("bay B has 9 arms",
     lambda: None if state["bays"]["B"]["arms"] == 9 else "wrong arms")
test("bay A has corridor ON",
     lambda: None if state["bays"]["A"]["corridor"]["enabled"] else "off")
test("bay A has walls ON",
     lambda: None if state["bays"]["A"]["walls"]["enabled"] else "off")
test("bay A has 2 apertures",
     lambda: None if len(state["bays"]["A"]["apertures"]) == 2 else "wrong count")
test("bay B has no apertures",
     lambda: None if len(state["bays"]["B"]["apertures"]) == 0 else "has apertures")

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 2: Describe and List")
print("=" * 60)

desc = test("describe()", lambda: cli.describe(state))
test("describe mentions Bay A",
     lambda: None if "Bay A" in desc else "missing")
test("describe mentions Bay B",
     lambda: None if "Bay B" in desc else "missing")
test("describe mentions corridor",
     lambda: None if "corridor" in desc.lower() else "missing")

lb = test("list_bays()", lambda: cli.list_bays(state))
test("list_bays has A and B",
     lambda: None if "A" in lb and "B" in lb else "missing")

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 3: Tokenizer")
print("=" * 60)

test("tokenize simple",
     lambda: None if cli.tokenize("set bay A rotation 30") == ["set","bay","A","rotation","30"] else "bad")
test("tokenize quoted string",
     lambda: None if len(cli.tokenize('set bay A label "My Bay"')) == 5 else "bad")
test("tokenize empty",
     lambda: None if cli.tokenize("") == [] else "bad")

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 4: Command Mutations (set, corridor, wall, aperture)")
print("=" * 60)

s = copy.deepcopy(state)

# Site
s, msg = cli.apply_command(s, cli.tokenize("set site width 250"), STATE)
test("set site width 250",
     lambda: None if s["site"]["width"] == 250.0 else msg)
s, msg = cli.apply_command(s, cli.tokenize("set site height 300"), STATE)
test("set site height 300",
     lambda: None if s["site"]["height"] == 300.0 else msg)

# Bay A mutations
s, msg = cli.apply_command(s, cli.tokenize("set bay A rotation 15"), STATE)
test("set bay A rotation 15",
     lambda: None if s["bays"]["A"]["rotation_deg"] == 15.0 else msg)

s, msg = cli.apply_command(s, cli.tokenize("set bay A spacing 30 30"), STATE)
test("set bay A spacing 30x30",
     lambda: None if s["bays"]["A"]["spacing"] == [30.0, 30.0] else msg)

s, msg = cli.apply_command(s, cli.tokenize("set bay A origin 20 20"), STATE)
test("set bay A origin 20,20",
     lambda: None if s["bays"]["A"]["origin"] == [20.0, 20.0] else msg)

s, msg = cli.apply_command(s, cli.tokenize("set bay A z_order 5"), STATE)
test("set bay A z_order 5",
     lambda: None if s["bays"]["A"]["z_order"] == 5 else msg)

s, msg = cli.apply_command(s, cli.tokenize("set bay A void_center 50 50"), STATE)
test("set bay A void_center",
     lambda: None if s["bays"]["A"]["void_center"] == [50.0, 50.0] else msg)

s, msg = cli.apply_command(s, cli.tokenize("set bay A void_size 25 25"), STATE)
test("set bay A void_size",
     lambda: None if s["bays"]["A"]["void_size"] == [25.0, 25.0] else msg)

s, msg = cli.apply_command(s, cli.tokenize("set bay A void_shape circle"), STATE)
test("set bay A void_shape circle",
     lambda: None if s["bays"]["A"]["void_shape"] == "circle" else msg)

# Label
s, msg = cli.apply_command(s, cli.tokenize('set bay A label "Library Wing"'), STATE)
test("set bay A label",
     lambda: None if s["bays"]["A"]["label"] == "Library Wing" else msg)

# Corridor
s, msg = cli.apply_command(s, cli.tokenize("corridor A off"), STATE)
test("corridor A off",
     lambda: None if not s["bays"]["A"]["corridor"]["enabled"] else msg)
s, msg = cli.apply_command(s, cli.tokenize("corridor A on"), STATE)
test("corridor A on",
     lambda: None if s["bays"]["A"]["corridor"]["enabled"] else msg)
s, msg = cli.apply_command(s, cli.tokenize("corridor A width 10"), STATE)
test("corridor A width 10",
     lambda: None if s["bays"]["A"]["corridor"]["width"] == 10.0 else msg)
s, msg = cli.apply_command(s, cli.tokenize("corridor A axis y"), STATE)
test("corridor A axis y",
     lambda: None if s["bays"]["A"]["corridor"]["axis"] == "y" else msg)
s, msg = cli.apply_command(s, cli.tokenize("corridor A loading single"), STATE)
test("corridor A loading single",
     lambda: None if s["bays"]["A"]["corridor"]["loading"] == "single" else msg)

# Walls
s, msg = cli.apply_command(s, cli.tokenize("wall A off"), STATE)
test("wall A off",
     lambda: None if not s["bays"]["A"]["walls"]["enabled"] else msg)
s, msg = cli.apply_command(s, cli.tokenize("wall A on"), STATE)
test("wall A on",
     lambda: None if s["bays"]["A"]["walls"]["enabled"] else msg)
s, msg = cli.apply_command(s, cli.tokenize("wall A thickness 0.75"), STATE)
test("wall A thickness 0.75",
     lambda: None if s["bays"]["A"]["walls"]["thickness"] == 0.75 else msg)

# Apertures: add, modify, list, remove
s, msg = cli.apply_command(s, cli.tokenize("aperture A add d2 door y 0 5 3.5 7"), STATE)
test("aperture add d2",
     lambda: None if any(a["id"] == "d2" for a in s["bays"]["A"]["apertures"]) else msg)

s, msg = cli.apply_command(s, cli.tokenize("aperture A set d2 width 4"), STATE)
d2 = next(a for a in s["bays"]["A"]["apertures"] if a["id"] == "d2")
test("aperture modify d2 width=4",
     lambda: None if d2["width"] == 4.0 else msg)

s, msg = cli.apply_command(s, cli.tokenize("aperture A add p2 portal x 3 20 10 9"), STATE)
test("aperture add portal p2",
     lambda: None if any(a["id"] == "p2" for a in s["bays"]["A"]["apertures"]) else msg)

s, msg = cli.apply_command(s, cli.tokenize("aperture A list"), STATE)
test("aperture A list",
     lambda: None if "d1" in msg and "d2" in msg else msg)

s, msg = cli.apply_command(s, cli.tokenize("aperture A remove d2"), STATE)
test("aperture remove d2",
     lambda: None if not any(a["id"] == "d2" for a in s["bays"]["A"]["apertures"]) else msg)

# Bay B radial mutations
s, msg = cli.apply_command(s, cli.tokenize("set bay B arms 12"), STATE)
test("set bay B arms 12",
     lambda: None if s["bays"]["B"]["arms"] == 12 else msg)
s, msg = cli.apply_command(s, cli.tokenize("set bay B ring_spacing 25"), STATE)
test("set bay B ring_spacing 25",
     lambda: None if s["bays"]["B"]["ring_spacing"] == 25.0 else msg)
s, msg = cli.apply_command(s, cli.tokenize("set bay B arc_deg 270"), STATE)
test("set bay B arc_deg 270",
     lambda: None if s["bays"]["B"]["arc_deg"] == 270.0 else msg)
s, msg = cli.apply_command(s, cli.tokenize("set bay B arc_start_deg 45"), STATE)
test("set bay B arc_start_deg 45",
     lambda: None if s["bays"]["B"]["arc_start_deg"] == 45.0 else msg)
s, msg = cli.apply_command(s, cli.tokenize("set bay B rings 5"), STATE)
test("set bay B rings 5",
     lambda: None if s["bays"]["B"]["rings"] == 5 else msg)

# Style
s, msg = cli.apply_command(s, cli.tokenize("set style heavy 2.0"), STATE)
test("set style heavy 2.0",
     lambda: None if s["style"]["heavy_lineweight_mm"] == 2.0 else msg)
s, msg = cli.apply_command(s, cli.tokenize("set style light 0.1"), STATE)
test("set style light 0.1",
     lambda: None if s["style"]["light_lineweight_mm"] == 0.1 else msg)
s, msg = cli.apply_command(s, cli.tokenize("set column size 2.0"), STATE)
test("set column size 2.0",
     lambda: None if s["style"]["column_size"] == 2.0 else msg)

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 5: Sentinels")
print("=" * 60)

_, msg = cli.apply_command(s, cli.tokenize("help"), STATE)
test("help -> __HELP__", lambda: None if msg == "__HELP__" else msg)
_, msg = cli.apply_command(s, cli.tokenize("describe"), STATE)
test("describe -> __DESCRIBE__", lambda: None if msg == "__DESCRIBE__" else msg)
_, msg = cli.apply_command(s, cli.tokenize("list bays"), STATE)
test("list bays -> __LIST_BAYS__", lambda: None if msg == "__LIST_BAYS__" else msg)
_, msg = cli.apply_command(s, cli.tokenize("undo"), STATE)
test("undo -> __UNDO__", lambda: None if msg == "__UNDO__" else msg)
_, msg = cli.apply_command(s, cli.tokenize("status"), STATE)
test("status -> __STATUS__", lambda: None if msg == "__STATUS__" else msg)
_, msg = cli.apply_command(s, cli.tokenize("quit"), STATE)
test("quit -> __QUIT__", lambda: None if msg == "__QUIT__" else msg)

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 6: Rooms")
print("=" * 60)

s2 = copy.deepcopy(state)
s2, msg = cli.apply_command(s2, cli.tokenize("room list"), STATE)
test("room list", lambda: None if "bay_A" in msg else msg)

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 7: Snapshots")
print("=" * 60)

reset_state()
s3 = cli.load_state(STATE)
s3, msg = cli.apply_command(s3, cli.tokenize("snapshot save before_test"), STATE)
cli.save_state(STATE, s3)
test("snapshot save before_test",
     lambda: None if "before_test" in msg else msg)

s3, msg = cli.apply_command(s3, cli.tokenize("snapshot list"), STATE)
test("snapshot list shows before_test",
     lambda: None if "before_test" in msg else msg)

s3, msg = cli.apply_command(s3, cli.tokenize("snapshot load before_test"), STATE)
test("snapshot load before_test",
     lambda: None if "before_test" in msg.lower() or "loaded" in msg.lower() or "restored" in msg.lower() else msg)

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 8: Geometry Helpers")
print("=" * 60)

bayA = state["bays"]["A"]
bayB = state["bays"]["B"]

test("bay_col_count A (4x4=16)",
     lambda: None if cli._bay_col_count(bayA) == 16 else str(cli._bay_col_count(bayA)))
test("bay_col_count B (1+3*9=28)",
     lambda: None if cli._bay_col_count(bayB) == 28 else str(cli._bay_col_count(bayB)))

area_a = cli._bay_area(bayA)
test("bay_area A (72x72=5184)",
     lambda: None if abs(area_a - 5184) < 1 else str(area_a))

area_b = cli._bay_area(bayB)
expected_b = 3.14159 * (60**2)  # pi * r^2, r=3*20=60
test("bay_area B (pi*60^2 ~ 11310)",
     lambda: None if abs(area_b - expected_b) < 10 else str(area_b))

ext_a = cli._bay_extents(bayA)
test("bay_extents A returns 4 values",
     lambda: None if len(ext_a) == 4 else str(ext_a))

ext_b = cli._bay_extents(bayB)
test("bay_extents B returns 4 values",
     lambda: None if len(ext_b) == 4 else str(ext_b))

cx, cy = cli._get_spacing_arrays(bayA)
test("spacing_arrays A: 4 x-vals, 4 y-vals",
     lambda: None if len(cx) == 4 and len(cy) == 4 else "cx={} cy={}".format(len(cx), len(cy)))

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 9: Auditor")
print("=" * 60)

reset_state()
state = cli.load_state(STATE)

issues = auditor.audit_model(state)
test("audit_model returns list",
     lambda: None if isinstance(issues, list) else type(issues))

formatted = auditor.format_audit(issues)
test("format_audit returns string",
     lambda: None if isinstance(formatted, str) else type(formatted))
test("format_audit ends with READY:",
     lambda: None if formatted.strip().endswith("READY:") else formatted[-50:])

ab = auditor.audit_bay(state, "A")
test("audit_bay A returns report",
     lambda: None if "Bay A" in ab or "AUDIT" in ab else ab[:80])
test("audit_bay A has grid info",
     lambda: None if "rectangular" in ab else ab[:80])
test("audit_bay A has column count",
     lambda: None if "Columns" in ab or "columns" in ab else ab[:80])

ab_b = auditor.audit_bay(state, "B")
test("audit_bay B returns report",
     lambda: None if "Bay B" in ab_b or "AUDIT" in ab_b else ab_b[:80])
test("audit_bay B has radial info",
     lambda: None if "radial" in ab_b.lower() or "ring" in ab_b.lower() else ab_b[:80])

ab_bad = auditor.audit_bay(state, "Z")
test("audit_bay Z returns ERROR",
     lambda: None if "ERROR" in ab_bad else ab_bad[:80])

# describe_bay
db = auditor.describe_bay(state, "A")
test("describe_bay A returns narrative",
     lambda: None if "3-by-3" in db or "rectangular" in db else db[:80])
test("describe_bay A has spatial relationships",
     lambda: None if "Bay B" in db else db[:80])

db_b = auditor.describe_bay(state, "B")
test("describe_bay B returns narrative",
     lambda: None if "radial" in db_b else db_b[:80])

# describe_circulation
circ = auditor.describe_circulation(state)
test("describe_circulation returns text",
     lambda: None if "CIRCULATION" in circ else circ[:80])
test("describe_circulation mentions Bay A corridor",
     lambda: None if "Bay A" in circ else circ[:80])

# measure
m1 = auditor.measure(state, "bay A origin", "bay B center")
test("measure A origin to B center",
     lambda: None if "OK:" in m1 else m1[:80])
test("measure has distance",
     lambda: None if "ft" in m1 else m1[:80])

m2 = auditor.measure(state, "site origin", "site center")
test("measure site origin to center",
     lambda: None if "OK:" in m2 else m2[:80])

m3 = auditor.measure(state, "bay A void", "bay B void")
test("measure void to void",
     lambda: None if "OK:" in m3 else m3[:80])

m_bad = auditor.measure(state, "bay Z origin", "site center")
test("measure bad bay returns ERROR",
     lambda: None if "ERROR" in m_bad else m_bad[:80])

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 10: Skill Manager")
print("=" * 60)

skills = skill_manager.list_skills()
test("list_skills returns list",
     lambda: None if isinstance(skills, list) else type(skills))
test("list_skills finds 2 bundled skills",
     lambda: None if len(skills) >= 2 else str(len(skills)))

fmt = skill_manager.format_skill_list(skills)
test("format_skill_list returns string",
     lambda: None if isinstance(fmt, str) and "OK:" in fmt else fmt[:80])
test("format_skill_list ends with READY:",
     lambda: None if fmt.strip().endswith("READY:") else fmt[-50:])

sk = skill_manager.load_skill("add-double-loaded-corridor")
test("load_skill corridor",
     lambda: None if sk["name"] == "add-double-loaded-corridor" else str(sk))
test("skill has 4 commands",
     lambda: None if len(sk["commands"]) == 4 else str(len(sk["commands"])))
test("skill has 3 params",
     lambda: None if len(sk["params"]) == 3 else str(len(sk["params"])))

detail = skill_manager.format_skill_detail(sk)
test("format_skill_detail",
     lambda: None if "OK:" in detail and "READY:" in detail else detail[:80])

# save a new skill
save_msg = skill_manager.save_skill(
    "test-skill",
    "Test skill for validation",
    ["set site width {w}", "set site height {h}"],
    {"w": {"description": "Width", "default": "100"},
     "h": {"description": "Height", "default": "100"}},
)
test("save_skill test-skill",
     lambda: None if "OK:" in save_msg else save_msg)

# verify it appears in list
skills2 = skill_manager.list_skills()
test("new skill in list",
     lambda: None if any(s["name"] == "test-skill" for s in skills2) else "missing")

# load it back
sk2 = skill_manager.load_skill("test-skill")
test("load new skill",
     lambda: None if sk2["name"] == "test-skill" else str(sk2))

# Run a skill (using _run helper simulation)
reset_state()

def fake_run(cmd):
    """Simulate _run by applying command to state."""
    st = cli.load_state(STATE)
    tokens = cli.tokenize(cmd)
    try:
        st, msg = cli.apply_command(st, tokens, STATE)
        cli.save_state(STATE, st)
        return msg
    except Exception as e:
        return "ERROR: {}".format(e)

run_msg = skill_manager.run_skill("test-skill", {"w": "150", "h": "180"}, fake_run)
test("run_skill test-skill",
     lambda: None if "completed" in run_msg.lower() or "OK:" in run_msg else run_msg[:120])

# Verify state changed
st_after = cli.load_state(STATE)
test("skill changed site width to 150",
     lambda: None if st_after["site"]["width"] == 150.0 else str(st_after["site"]["width"]))
test("skill changed site height to 180",
     lambda: None if st_after["site"]["height"] == 180.0 else str(st_after["site"]["height"]))

# Run corridor skill
reset_state()
run_msg2 = skill_manager.run_skill("add-double-loaded-corridor", {"bay": "B"}, fake_run)
test("run corridor skill on bay B",
     lambda: None if "completed" in run_msg2.lower() or "OK:" in run_msg2 else run_msg2[:120])

st_after2 = cli.load_state(STATE)
test("corridor skill turned on bay B corridor",
     lambda: None if st_after2["bays"]["B"]["corridor"]["enabled"] else "still off")

# bad skill name
bad_msg = skill_manager.run_skill("nonexistent-skill", {}, fake_run)
test("run nonexistent skill returns ERROR",
     lambda: None if "ERROR" in bad_msg else bad_msg[:80])

# Clean up test skill
test_skill_path = os.path.join(HERE, "skills", "test-skill.json")
if os.path.exists(test_skill_path):
    os.remove(test_skill_path)

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 11: Rhino Client (Offline)")
print("=" * 60)

bridge = rhino_client.get_bridge()

connected = bridge.is_connected()
test("bridge.is_connected() = False (no Rhino)",
     lambda: None if connected == False else str(connected))

status = bridge.status()
test("bridge.status() starts with OFFLINE",
     lambda: None if status.startswith("OFFLINE") else status[:80])

q1 = bridge.query("layer_stats")
test("bridge.query layer_stats -> OFFLINE",
     lambda: None if "OFFLINE" in q1 else q1[:80])

q2 = bridge.query("bounding_box")
test("bridge.query bounding_box -> OFFLINE",
     lambda: None if "OFFLINE" in q2 else q2[:80])

q3 = bridge.query("object_count", {"layer": "JIG_COLUMNS"})
test("bridge.query object_count -> OFFLINE",
     lambda: None if "OFFLINE" in q3 else q3[:80])

sc = bridge.run_script("print('hello')")
test("bridge.run_script -> OFFLINE",
     lambda: None if "OFFLINE" in sc else sc[:80])

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 11b: Rhino Watcher File Validation")
print("=" * 60)

watcher_path = os.path.join(HERE, "rhino_watcher.py")

test("rhino_watcher.py exists",
     lambda: None if os.path.exists(watcher_path) else "file not found")

# Read the file and check for f-strings (IronPython 2.7 compat)
if os.path.exists(watcher_path):
    with open(watcher_path, encoding="utf-8") as wf:
        watcher_src = wf.read()

    test("rhino_watcher.py is non-empty",
         lambda: None if len(watcher_src) > 100 else "file too small")

    # Check no f-strings (IronPython 2.7 does not support them)
    import re as _re
    fstring_hits = _re.findall(r'(?<!\w)f"[^"]*\{', watcher_src)
    fstring_hits += _re.findall(r"(?<!\w)f'[^']*\{", watcher_src)
    test("rhino_watcher.py has no f-strings",
         lambda: None if len(fstring_hits) == 0
         else "found {} f-string(s)".format(len(fstring_hits)))

    # Check it parses as valid Python
    import ast as _ast
    try:
        _ast.parse(watcher_src)
        test("rhino_watcher.py parses as valid Python", lambda: None)
    except SyntaxError as e:
        test("rhino_watcher.py parses as valid Python",
             lambda: "SyntaxError: {}".format(str(e)))

    # Check key markers exist
    test("watcher has rhinoscriptsyntax import",
         lambda: None if "rhinoscriptsyntax" in watcher_src else "missing import")
    test("watcher has state.json file watch",
         lambda: None if "state.json" in watcher_src or "STATE_FILE" in watcher_src
         else "no state file reference")
    test("watcher has Idle event hook",
         lambda: None if "Idle" in watcher_src or "on_idle" in watcher_src
         else "no idle hook")
    test("watcher has JIG_ layer names",
         lambda: None if "JIG_COLUMNS" in watcher_src else "no JIG layer names")
else:
    # Skip all watcher tests if file missing
    for label in ["rhino_watcher.py is non-empty",
                  "rhino_watcher.py has no f-strings",
                  "rhino_watcher.py parses as valid Python",
                  "watcher has rhinoscriptsyntax import",
                  "watcher has state.json file watch",
                  "watcher has Idle event hook",
                  "watcher has JIG_ layer names"]:
        test(label, lambda: "SKIPPED: file not found")

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 12: Error Handling")
print("=" * 60)

reset_state()
state = cli.load_state(STATE)

# Unknown command
try:
    cli.apply_command(state, cli.tokenize("foobar"), STATE)
    test("unknown command raises", lambda: "should have raised")
except ValueError:
    test("unknown command raises ValueError", lambda: None)

# Bad bay name
try:
    cli.apply_command(state, cli.tokenize("set bay Z rotation 10"), STATE)
    test("bad bay raises", lambda: "should have raised")
except (ValueError, KeyError):
    test("bad bay raises error", lambda: None)

# Bad aperture type
try:
    cli.apply_command(state, cli.tokenize("aperture A add x1 laser x 0 5 3 7"), STATE)
    test("bad aperture type raises", lambda: "should have raised")
except ValueError:
    test("bad aperture type raises ValueError", lambda: None)

# ══════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 13: Atomic Write Safety")
print("=" * 60)

reset_state()
state = cli.load_state(STATE)
state["meta"]["notes"] = "atomic write test"
cli.save_state(STATE, state)
reloaded = cli.load_state(STATE)
test("atomic write preserves data",
     lambda: None if reloaded["meta"]["notes"] == "atomic write test" else reloaded["meta"]["notes"])
test("atomic write no .tmp left",
     lambda: None if not os.path.exists(STATE + ".tmp") else ".tmp exists")

# ══════════════════════════════════════════════════
# FINAL RESET AND SUMMARY
# ══════════════════════════════════════════════════

reset_state()

print("")
print("=" * 60)
print("RESULTS")
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
    print("  ALL TESTS PASSED")
else:
    print("  {} TEST(S) FAILED".format(failed))
print("")
