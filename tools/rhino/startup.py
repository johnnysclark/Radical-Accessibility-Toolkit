# -*- coding: utf-8 -*-
"""
Radical Accessibility — Rhino Startup Script
=============================================
Auto-loads everything needed for accessible Rhino modeling:
  1. Layout Jig watcher (file watching, inventory export, pending edits)
  2. RhinoMCP server (mcpstart command)
  3. LightPen display mode on ALL viewports
  4. Model units set to Feet

Run via:  exec(open("C:/path/to/startup.py").read())
Or via:   Rhino.exe /runscript="_-RunPythonScript C:/path/to/startup.py"
"""
import os
import rhinoscriptsyntax as rs
import Rhino

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else os.getcwd()

# ── Step 1: Reset state.json to blank ─────────────────────

state_path = os.path.join(SCRIPT_DIR, "..", "..", "controller", "state.json")
state_path = os.path.abspath(state_path)
if os.path.exists(state_path):
    import json as _json
    try:
        with open(state_path, "r") as _f:
            _state = _json.load(_f)
        # Clear all geometry-producing content but keep schema
        _state["bays"] = {}
        _state["zones"] = {}
        _state.get("rooms", {}).clear()
        _state.get("legend", {})["enabled"] = False
        _state.get("tactile3d", {})["enabled"] = False
        with open(state_path, "w") as _f:
            _json.dump(_state, _f, indent=2, ensure_ascii=False)
        print("[STARTUP] State reset to blank.")
    except Exception as e:
        print("[STARTUP] WARNING: Could not reset state: {0}".format(e))

# ── Step 2: Load the watcher ──────────────────────────────

watcher_path = os.path.join(SCRIPT_DIR, "rhino_watcher.py")
if os.path.exists(watcher_path):
    print("[STARTUP] Loading watcher from {0}".format(watcher_path))
    exec(open(watcher_path).read())
else:
    print("[STARTUP] WARNING: Watcher not found at {0}".format(watcher_path))

# ── Step 3: Start RhinoMCP ────────────────────────────────

print("[STARTUP] Starting RhinoMCP...")
try:
    rs.Command("_mcpstart", False)
except Exception as e:
    print("[STARTUP] WARNING: mcpstart failed: {0}".format(e))

# ── Step 4: Set ALL viewports to LightPen ─────────────────

print("[STARTUP] Setting all viewports to LightPen display mode...")
try:
    # List all available display modes for debugging
    modes = Rhino.Display.DisplayModeDescription.GetDisplayModes()
    mode_names = []
    lightpen = None
    for mode in modes:
        eng = mode.EnglishName if hasattr(mode, "EnglishName") else ""
        loc = str(mode.LocalName) if hasattr(mode, "LocalName") else ""
        mode_names.append(eng or loc)
        # Case-insensitive match on either name
        if eng.lower() == "lightpen" or loc.lower() == "lightpen":
            lightpen = mode
    print("[STARTUP] Available display modes: {0}".format(", ".join(mode_names)))
    if lightpen:
        views = Rhino.RhinoDoc.ActiveDoc.Views.GetViewList(True, False)
        for view in views:
            view.ActiveViewport.DisplayMode = lightpen
            view.Redraw()
        print("[STARTUP] LightPen mode set on {0} viewports.".format(len(views)))
    else:
        # Fallback: try via Rhino command which may find custom display modes
        print("[STARTUP] LightPen not found in API. Trying command...")
        rs.Command("_-SetDisplayMode _Viewport=_All LightPen _Enter", False)
        print("[STARTUP] SetDisplayMode command sent.")
except Exception as e:
    print("[STARTUP] WARNING: Display mode switch failed: {0}".format(e))

# ── Step 5: Set units to Feet ─────────────────────────────

print("[STARTUP] Setting units to Feet...")
try:
    # UnitSystem 4 = Feet. Avoids DocumentProperties dialog.
    rs.UnitSystem(4, False)
    print("[STARTUP] Units set to Feet.")
except Exception as e:
    print("[STARTUP] WARNING: Unit setting failed: {0}".format(e))

# ── Step 6: Ensure SCD laser-cutter layers exist ──────────
# See tools/rhino/laser-export/ and skills/laser-export/SKILL.md

print("[STARTUP] Ensuring SCD laser layers (Cut Layer, Engrave Layer, Artboard)...")
try:
    import sys as _sys
    _laser_dir = os.path.join(SCRIPT_DIR, "laser-export")
    if _laser_dir not in _sys.path:
        _sys.path.insert(0, _laser_dir)
    import laser_setup as _laser_setup
    _laser_setup.ensure_layers(draw_artboard=True)
except Exception as e:
    print("[STARTUP] WARNING: laser layer setup failed: {0}".format(e))

print("[STARTUP] Ready. Watcher active. RhinoMCP started. LightPen on all viewports.")
