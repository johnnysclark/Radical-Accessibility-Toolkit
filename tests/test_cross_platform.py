# -*- coding: utf-8 -*-
"""
Cross-Platform Compatibility Tests for RAP
===========================================
Runs in Python 3 (standalone) or inside Rhino's Python editor (either platform).

Usage standalone:
    python tests/test_cross_platform.py

Usage inside Rhino (paste into Python editor or ScriptEditor):
    exec(open("/path/to/tests/test_cross_platform.py").read())

Output follows the OK:/ERROR: protocol for screen reader compatibility.
"""
import os
import sys
import platform

# ── Detect environment ────────────────────────────────────

_results = []  # (name, passed, detail)


def _test(name, condition, detail=""):
    """Record a test result."""
    _results.append((name, bool(condition), detail))
    if condition:
        print("OK: {0}".format(name))
    else:
        print("ERROR: {0} -- {1}".format(name, detail))


def _section(title):
    print("")
    print("--- {0} ---".format(title))


# ══════════════════════════════════════════════════════════
# 1. Platform Detection
# ══════════════════════════════════════════════════════════

_section("Platform Detection")

plat = platform.system()
impl = platform.python_implementation()
ver = sys.version.split()[0]

print("OK: Platform = {0}, Python = {1} {2}".format(plat, impl, ver))

is_mac = plat == "Darwin"
is_windows = plat == "Windows"
is_linux = plat == "Linux"
is_ironpython = "IronPython" in sys.version or sys.platform == "cli"

_test("Platform is recognized",
      is_mac or is_windows or is_linux,
      "platform.system() = {0}".format(plat))

_test("Python implementation detected",
      impl in ("CPython", "IronPython", "PyPy"),
      "Got: {0}".format(impl))

# ══════════════════════════════════════════════════════════
# 2. compat.py Module
# ══════════════════════════════════════════════════════════

_section("compat.py Module")

# Find compat.py relative to this test file or the project root
_test_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
_project_root = os.path.dirname(_test_dir)
_compat_path = os.path.join(_project_root, "tools", "rhino", "compat.py")

_test("compat.py exists", os.path.isfile(_compat_path),
      "Expected at {0}".format(_compat_path))

# Add tools/rhino to path so we can import compat
_rhino_tools = os.path.join(_project_root, "tools", "rhino")
if _rhino_tools not in sys.path:
    sys.path.insert(0, _rhino_tools)

compat = None
try:
    import compat
    _test("compat.py imports successfully", True)
except Exception as e:
    _test("compat.py imports successfully", False, str(e))

if compat:
    _test("compat.IS_IRONPYTHON is boolean",
          isinstance(compat.IS_IRONPYTHON, bool))

    _test("compat.IS_CPYTHON is boolean",
          isinstance(compat.IS_CPYTHON, bool))

    _test("compat.IS_MAC is boolean",
          isinstance(compat.IS_MAC, bool))

    _test("compat.IS_WINDOWS is boolean",
          isinstance(compat.IS_WINDOWS, bool))

    _test("compat.IS_IRONPYTHON matches sys.version",
          compat.IS_IRONPYTHON == is_ironpython,
          "compat={0}, expected={1}".format(compat.IS_IRONPYTHON, is_ironpython))

    # Platform flags should be mutually consistent
    _test("Platform flags are consistent",
          not (compat.IS_MAC and compat.IS_WINDOWS),
          "Cannot be both Mac and Windows")

    # Test make_guid
    try:
        guid = compat.make_guid("12345678-1234-1234-1234-123456789abc")
        _test("make_guid returns an object", guid is not None)
        _test("make_guid string roundtrip",
              "12345678" in str(guid).lower(),
              "Got: {0}".format(guid))
    except Exception as e:
        _test("make_guid works", False, str(e))

    # Test chime (fire-and-forget, should not crash)
    try:
        compat.chime()
        _test("chime() does not crash", True)
    except Exception as e:
        _test("chime() does not crash", False, str(e))

    # Test speak (fire-and-forget, should not crash)
    try:
        compat.speak("test", rate=2)
        _test("speak() does not crash", True)
    except Exception as e:
        _test("speak() does not crash", False, str(e))

# ══════════════════════════════════════════════════════════
# 3. Rhino Environment (only when running inside Rhino)
# ══════════════════════════════════════════════════════════

_section("Rhino Environment")

in_rhino = False
try:
    import rhinoscriptsyntax as rs
    import Rhino
    import scriptcontext as sc
    in_rhino = True
    _test("rhinoscriptsyntax imports", True)
    _test("Rhino module imports", True)
    _test("scriptcontext imports", True)
except ImportError as e:
    print("OK: Not running inside Rhino (expected for standalone test).")
    print("  Detail: {0}".format(e))

if in_rhino:
    _test("Rhino.RhinoApp.Version accessible",
          hasattr(Rhino.RhinoApp, "Version"),
          "Rhino.RhinoApp has no Version attribute")

    try:
        v = str(Rhino.RhinoApp.Version)
        _test("Rhino version readable", len(v) > 0,
              "Version: {0}".format(v))
    except Exception as e:
        _test("Rhino version readable", False, str(e))

    _test("scriptcontext.doc accessible",
          hasattr(sc, "doc") and sc.doc is not None)

    # Test Idle event hook (just check it exists, don't attach)
    _test("Rhino.RhinoApp.Idle event exists",
          hasattr(Rhino.RhinoApp, "Idle"))

    # Test key rhinoscriptsyntax functions
    for fn_name in ["AddLine", "AddPolyline", "AddCircle", "AddText",
                    "AddLayer", "IsLayer", "ObjectsByLayer", "CurrentLayer",
                    "EnableRedraw"]:
        _test("rs.{0} exists".format(fn_name),
              hasattr(rs, fn_name),
              "rhinoscriptsyntax missing {0}".format(fn_name))

# ══════════════════════════════════════════════════════════
# 4. Controller CLI (Python 3 only)
# ══════════════════════════════════════════════════════════

_section("Controller CLI")

_controller_dir = os.path.join(_project_root, "controller")
if _controller_dir not in sys.path:
    sys.path.insert(0, _controller_dir)

if not is_ironpython:
    try:
        import controller_cli
        _test("controller_cli imports", True)

        _test("controller_cli.IS_MAC is boolean",
              isinstance(controller_cli.IS_MAC, bool))

        _test("controller_cli.IS_WINDOWS is boolean",
              isinstance(controller_cli.IS_WINDOWS, bool))

        # Test that _find_rhino doesn't crash (may return None)
        try:
            result = controller_cli._find_rhino()
            _test("_find_rhino() does not crash", True,
                  "Found: {0}".format(result))
        except Exception as e:
            _test("_find_rhino() does not crash", False, str(e))

        # Test that default_state() produces valid state with required keys
        try:
            state = controller_cli.default_state()
            has_schema = "schema" in state
            has_bays = "bays" in state
            _test("default_state() has required keys",
                  has_schema and has_bays,
                  "Keys: {0}".format(list(state.keys())[:6]))
        except Exception as e:
            _test("default_state() works", False, str(e))

    except ImportError as e:
        _test("controller_cli imports", False, str(e))
else:
    print("OK: Skipping controller_cli tests (IronPython environment).")

# ══════════════════════════════════════════════════════════
# 5. File Structure
# ══════════════════════════════════════════════════════════

_section("File Structure")

expected_files = [
    ("tools/rhino/compat.py", "Compatibility layer"),
    ("tools/rhino/rhino_watcher.py", "Rhino watcher"),
    ("controller/controller_cli.py", "Controller CLI"),
    ("controller/auditor.py", "Auditor"),
    ("mcp/mcp_server.py", "MCP server"),
    ("docs/cross-platform-audit.md", "Cross-platform audit"),
    ("services/com.rap.mcp-server.plist", "macOS launchd config"),
    ("services/install-windows-service.ps1", "Windows NSSM config"),
    ("services/README.md", "Services documentation"),
]

for rel_path, desc in expected_files:
    full = os.path.join(_project_root, rel_path)
    _test("{0} exists".format(desc), os.path.isfile(full),
          "Missing: {0}".format(rel_path))

# ══════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════

_section("Summary")

passed = sum(1 for _, p, _ in _results if p)
failed = sum(1 for _, p, _ in _results if not p)
total = len(_results)

if failed == 0:
    print("OK: All {0} tests passed.".format(total))
else:
    print("ERROR: {0} of {1} tests failed.".format(failed, total))
    for name, p, detail in _results:
        if not p:
            print("  FAILED: {0} -- {1}".format(name, detail))

print("READY:")
