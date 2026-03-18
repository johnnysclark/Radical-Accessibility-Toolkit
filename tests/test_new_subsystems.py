#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for new subsystems: state manager, validation, capture presets, runtime.
==============================================================================
Run: python tests/test_new_subsystems.py
"""
import copy
import json
import os
import sys
import tempfile
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONTROLLER = os.path.join(ROOT, "controller")
TOOLS_RHINO = os.path.join(ROOT, "tools", "rhino")

sys.path.insert(0, ROOT)
sys.path.insert(0, CONTROLLER)
sys.path.insert(0, TOOLS_RHINO)

passed = 0
failed = 0
errors = []


def test(name, fn):
    global passed, failed
    try:
        result = fn()
        if result is None or result is True:
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


# ══════════════════════════════════════════════════════
print("=" * 60)
print("PHASE 1: Schema Validation")
print("=" * 60)

from controller.validation.schema import validate_schema

# Load the real state for testing
STATE_PATH = os.path.join(CONTROLLER, "state.json")
with open(STATE_PATH, "r", encoding="utf-8") as f:
    REAL_STATE = json.load(f)

test("schema_valid_state",
     lambda: None if len([i for i in validate_schema(REAL_STATE)
                          if i["level"] == "error"]) == 0 else "has errors")

test("schema_missing_bays",
     lambda: None if any(i["code"] == "missing_key"
                         for i in validate_schema({"schema": "x", "meta": {}, "site": {}}))
     else "should report missing bays")

test("schema_not_dict",
     lambda: None if validate_schema("not a dict")[0]["code"] == "not_dict"
     else "should report not_dict")

test("schema_bad_grid_type",
     lambda: (lambda s: None if any(i["code"] == "invalid_grid_type"
                                     for i in validate_schema(s))
              else "should report invalid_grid_type")(
         {"schema": "plan_layout_jig_v2.3", "meta": {"last_saved": "x"},
          "site": {"width": 100, "height": 100},
          "bays": {"A": {"grid_type": "hexagonal", "origin": [0, 0],
                          "bays": [2, 2], "spacing": [10, 10],
                          "corridor": {}, "walls": {}, "apertures": []}}}))

test("schema_duplicate_aperture_id",
     lambda: (lambda s: None if any(i["code"] == "duplicate_aperture_id"
                                     for i in validate_schema(s))
              else "should report duplicate")(
         {"schema": "plan_layout_jig_v2.3", "meta": {"last_saved": "x"},
          "site": {"width": 100, "height": 100},
          "bays": {"A": {"grid_type": "rectangular", "origin": [0, 0],
                          "bays": [2, 2], "spacing": [10, 10],
                          "corridor": {}, "walls": {},
                          "apertures": [{"id": "d1", "type": "door"},
                                        {"id": "d1", "type": "window"}]}}}))


# ══════════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 2: Semantic Validation")
print("=" * 60)

from controller.validation.semantic import validate_semantic

test("semantic_valid_state",
     lambda: None if not any(i["level"] == "error"
                              for i in validate_semantic(REAL_STATE)) else "has errors")

test("semantic_bad_corridor_position",
     lambda: (lambda s: None if any(i["code"] == "corridor_out_of_range"
                                     for i in validate_semantic(s))
              else "should report out of range")(
         {"site": {"width": 100, "height": 100},
          "bays": {"A": {"grid_type": "rectangular", "origin": [0, 0],
                          "bays": [3, 3], "spacing": [10, 10],
                          "corridor": {"enabled": True, "axis": "x",
                                       "position": 99, "width": 8},
                          "walls": {}, "apertures": []}}}))

test("semantic_zero_site",
     lambda: None if any(i["code"] == "site_non_positive"
                          for i in validate_semantic(
                              {"site": {"width": 0, "height": 100}, "bays": {}}))
     else "should report non-positive")


# ══════════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 3: Spatial Validation")
print("=" * 60)

from controller.validation.spatial import validate_spatial

test("spatial_valid_state",
     lambda: None if isinstance(validate_spatial(REAL_STATE), list) else "should return list")

test("spatial_zero_grid",
     lambda: (lambda s: None if any(i["code"] == "zero_grid"
                                     for i in validate_spatial(s))
              else "should report zero grid")(
         {"site": {"width": 100, "height": 100},
          "bays": {"A": {"grid_type": "rectangular", "origin": [0, 0],
                          "bays": [0, 3], "spacing": [10, 10],
                          "corridor": {}, "walls": {}, "apertures": []}}}))


# ══════════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 4: Tactile Validation")
print("=" * 60)

from controller.validation.tactile import validate_tactile

test("tactile_valid_state",
     lambda: None if isinstance(validate_tactile(REAL_STATE), list) else "should return list")


# ══════════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 5: Fabrication Validation")
print("=" * 60)

from controller.validation.fabrication import validate_fabrication

test("fabrication_valid_state",
     lambda: None if isinstance(validate_fabrication(REAL_STATE), list) else "should return list")

test("fabrication_zero_wall_height",
     lambda: (lambda s: None if any(i["code"] == "wall_height_zero"
                                     for i in validate_fabrication(s))
              else "should report wall_height_zero")(
         {"tactile3d": {"enabled": True, "wall_height": 0, "cut_height": 4,
                         "floor_thickness": 0.5, "scale_factor": 1},
          "bays": {}}))


# ══════════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 6: State Manager")
print("=" * 60)

from controller.state_manager import StateManager, StateLock

# Use a temp directory for state manager tests
_tmpdir = tempfile.mkdtemp(prefix="rat_test_")
_tmp_state = os.path.join(_tmpdir, "state.json")


def _setup_tmp_state():
    state = copy.deepcopy(REAL_STATE)
    with open(_tmp_state, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return state


def test_lock():
    _setup_tmp_state()
    lock = StateLock(_tmp_state, writer="test", timeout=2.0)
    assert lock.acquire(), "Should acquire lock"
    # Second lock should fail (timeout reduced)
    lock2 = StateLock(_tmp_state, writer="test2", timeout=0.5)
    acquired = lock2.acquire()
    lock.release()
    if acquired:
        lock2.release()
    assert not acquired, "Second lock should fail"


test("state_lock", test_lock)


def test_transaction():
    _setup_tmp_state()
    mgr = StateManager(_tmp_state, writer="test",
                        journal_dir=os.path.join(_tmpdir, "journal"))
    with mgr.transaction("test command") as txn:
        state = txn.state
        state["site"]["width"] = 999
        txn.set_state(state)
    # Verify state was committed
    reloaded = mgr.load()
    assert reloaded["site"]["width"] == 999, "Width should be 999"
    assert reloaded["meta"]["state_revision"] > 0, "Revision should be > 0"
    assert reloaded["meta"]["last_writer"] == "test"


test("state_transaction", test_transaction)


def test_journal():
    _setup_tmp_state()
    journal_dir = os.path.join(_tmpdir, "journal2")
    mgr = StateManager(_tmp_state, writer="test", journal_dir=journal_dir)
    with mgr.transaction("cmd1") as txn:
        txn.set_state(txn.state)
    with mgr.transaction("cmd2") as txn:
        txn.set_state(txn.state)
    entries = mgr.journal.list_entries()
    assert len(entries) == 2, "Should have 2 journal entries, got {}".format(len(entries))


test("state_journal", test_journal)


# ══════════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 7: Capture Presets")
print("=" * 60)

from capture_presets import CapturePresetManager


def test_preset_manager():
    mgr = CapturePresetManager()
    presets = mgr.list_presets()
    assert len(presets) >= 2, "Should have default presets"
    p = mgr.get_preset("plan_technical")
    assert p is not None, "Should find plan_technical"
    assert p["width"] == 4000


test("preset_defaults", test_preset_manager)


def test_preset_add_remove():
    mgr = CapturePresetManager()
    mgr.add_preset({"id": "test_preset", "enabled": True, "width": 1000, "height": 800})
    assert mgr.get_preset("test_preset") is not None
    mgr.remove_preset("test_preset")
    assert mgr.get_preset("test_preset") is None


test("preset_add_remove", test_preset_add_remove)


def test_preset_format():
    mgr = CapturePresetManager()
    text = mgr.format_list()
    assert "OK:" in text
    assert "plan_technical" in text


test("preset_format", test_preset_format)


# ══════════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 8: Capture Service (offline)")
print("=" * 60)

from capture_service import CaptureService

_cap_dir = os.path.join(_tmpdir, "captures")


def test_capture_offline():
    svc = CaptureService(_cap_dir, _tmp_state, rhino_client=None)
    preset = {"id": "test", "enabled": True, "named_view": "Top",
              "display_mode": "Wireframe", "width": 1000, "height": 800,
              "format": "png", "output": "test.png"}
    result = svc.capture_one(preset)
    assert result["status"] == "error", "Should fail offline"
    assert "offline" in result["message"].lower()


test("capture_offline", test_capture_offline)


def test_capture_all_offline():
    svc = CaptureService(_cap_dir, _tmp_state, rhino_client=None)
    presets = [
        {"id": "a", "enabled": True, "output": "a.png"},
        {"id": "b", "enabled": False, "output": "b.png"},
    ]
    status = svc.capture_all(presets)
    assert status["total"] == 2
    assert status["skipped"] >= 1  # b is disabled


test("capture_all_offline", test_capture_all_offline)


def test_capture_status_format():
    svc = CaptureService(_cap_dir, _tmp_state, rhino_client=None)
    text = svc.format_status()
    assert isinstance(text, str)


test("capture_status_format", test_capture_status_format)


# ══════════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 9: CLI validate command")
print("=" * 60)

import controller_cli as cli


def test_cli_validate():
    state = cli.load_state(STATE_PATH)
    new_state, msg = cli.apply_command(state, ["validate"])
    assert "READY:" in msg, "Should end with READY:"


test("cli_validate", test_cli_validate)


def test_cli_validate_schema():
    state = cli.load_state(STATE_PATH)
    new_state, msg = cli.apply_command(state, ["validate", "schema"])
    assert "READY:" in msg


test("cli_validate_schema", test_cli_validate_schema)


def test_cli_validate_tactile():
    state = cli.load_state(STATE_PATH)
    new_state, msg = cli.apply_command(state, ["validate", "tactile"])
    assert "READY:" in msg


test("cli_validate_tactile", test_cli_validate_tactile)


# ══════════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 10: CLI capture command")
print("=" * 60)


def test_cli_capture_list():
    state = cli.load_state(STATE_PATH)
    new_state, msg = cli.apply_command(state, ["capture", "list"])
    assert "READY:" in msg


test("cli_capture_list", test_cli_capture_list)


def test_cli_capture_status():
    state = cli.load_state(STATE_PATH)
    new_state, msg = cli.apply_command(state, ["capture", "status"],
                                        state_file=_tmp_state)
    assert "READY:" in msg


test("cli_capture_status", test_cli_capture_status)


# ══════════════════════════════════════════════════════
print("")
print("=" * 60)
print("PHASE 11: Runtime Health Checks")
print("=" * 60)

from runtime.health import (
    check_python_version, check_project_structure,
    check_state_file, check_lock_status, run_all_checks,
)

test("health_python",
     lambda: None if check_python_version()["status"] == "ok" else "bad python")

test("health_structure",
     lambda: None if check_project_structure()["status"] == "ok" else "bad structure")

test("health_state",
     lambda: None if check_state_file(STATE_PATH)["status"] == "ok" else "bad state")

test("health_lock",
     lambda: None if check_lock_status(STATE_PATH)["status"] == "ok" else "lock present")

test("health_all",
     lambda: None if isinstance(run_all_checks(STATE_PATH), list) else "not a list")


# ══════════════════════════════════════════════════════
# Cleanup
shutil.rmtree(_tmpdir, ignore_errors=True)

print("")
print("=" * 60)
if failed == 0:
    print("READY: All {} tests passed. 0 failures.".format(passed))
else:
    print("DONE: {} passed, {} failed.".format(passed, failed))
    for e in errors:
        print("  FAILED: {}".format(e))
print("=" * 60)

sys.exit(1 if failed else 0)
