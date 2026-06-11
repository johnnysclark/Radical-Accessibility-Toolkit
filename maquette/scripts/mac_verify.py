"""Run this ON THE MAC to verify the full Maquette stack against Rhino 8.

    python3 maquette/scripts/mac_verify.py

Prints PASS: or FAIL: per check, then the short manual checklist that
needs human ears (VoiceOver) and a deliberate Rhino crash. Safe to run
repeatedly; it models into a throwaway project under /tmp.
"""

import os
import shutil
import struct
import sys
import tempfile

PASSED, FAILED = 0, 0


def report(ok, label, detail=""):
    global PASSED, FAILED
    prefix = "PASS: " if ok else "FAIL: "
    print(prefix + label + ((" " + detail) if detail else ""))
    if ok:
        PASSED += 1
    else:
        FAILED += 1
    return ok


def main():
    report(sys.version_info >= (3, 10), "Python 3.10 or newer",
           "{0}.{1}.{2}".format(*sys.version_info[:3]))

    try:
        import maquette  # noqa: F401
        report(True, "maquette importable", "version " + maquette.VERSION)
    except ImportError as exc:
        report(False, "maquette importable",
               "pip install -e 'maquette[headless,mcp,chat]' ({0})".format(exc))
        return finish()

    try:
        import rhino3dm  # noqa: F401
        report(True, "rhino3dm importable")
    except ImportError:
        report(False, "rhino3dm importable", "pip install 'maquette[headless]'")

    from maquette import DEFAULT_HOST, DEFAULT_PORT
    from maquette.netclient import ListenerClient
    from maquette.backends.base import BackendError

    client = ListenerClient(DEFAULT_HOST, DEFAULT_PORT)
    try:
        info = client.connect()
        report(True, "Rhino listener answers",
               "Rhino {0}, document {1}".format(info.get("rhino"),
                                                info.get("doc")))
        listener_up = True
    except BackendError as exc:
        report(False, "Rhino listener answers", str(exc))
        listener_up = False

    from maquette.rhinocode import find_rhinocode
    binary = find_rhinocode()
    report(binary is not None, "rhinocode CLI present", binary or
           "install Rhino 8.11+ for no-GUI recovery")

    if listener_up:
        _live_round_trip(client)
    client.close()
    return finish()


def _live_round_trip(client):
    from maquette.engine import Engine
    from maquette.project import init_project

    root = tempfile.mkdtemp(prefix="maquette-verify-")
    project_dir = os.path.join(root, "verify")
    try:
        project = init_project(project_dir, name="verify")
        engine = Engine(project, backend="live", actor="test")
        result = engine.run_text('box 2 2 2 at 0,0,0 name "verify box"')
        report(any("created m1" in line for line in result["lines"]),
               "live create reaches Rhino", result["lines"][0])
        entry = engine.entries()[-1]
        fingerprint = entry["result"]["fingerprint"]
        ok = (fingerprint and fingerprint.get("quality") == "measured"
              and fingerprint["bbox"][1][2] == 2)
        report(bool(ok), "Rhino measured the box", str(fingerprint))
        engine.run_text("move m1 by 5,0,0")
        response = client.request("query", {"what": "tagged", "ids": ["m1"]})
        objects = response["result"]["objects"]
        moved = objects and objects[0]["bbox"][0][0] == 5
        report(bool(moved), "live move verified by query",
               str(objects[0]["bbox"] if objects else "missing"))
        _fabrication_outputs(engine, project_dir)
        engine.undo_steps(2)
        response = client.request("query", {"what": "tagged", "ids": ["m1"]})
        report(not response["result"]["objects"],
               "undo removed the box from Rhino")
    except Exception as exc:  # noqa: BLE001 - report anything to the user
        report(False, "live round trip", "{0}: {1}".format(
            type(exc).__name__, exc))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def _fabrication_outputs(engine, project_dir):
    """STL, plan, and section against the live box (it sits at x 5..7)."""
    exports = os.path.join(project_dir, "exports")

    stl_path = os.path.join(exports, "verify.stl")
    result = engine.export(stl_path)
    spoken = " ".join(result["lines"])
    with open(stl_path, "rb") as handle:
        blob = handle.read()
    count = struct.unpack_from("<I", blob, 80)[0] if len(blob) >= 84 else 0
    report(count >= 12 and len(blob) == 84 + 50 * count,
           "STL export written and complete",
           "{0} triangles".format(count))
    report("watertight: yes" in spoken, "STL is watertight", spoken)

    plan_path = os.path.join(exports, "verify-plan.svg")
    result = engine.export_plan(1.0, plan_path)
    with open(plan_path, "r", encoding="utf-8") as handle:
        svg = handle.read()
    report("<path" in svg, "plan SVG has cut outlines",
           result["lines"][1] if len(result["lines"]) > 1 else "")

    section_path = os.path.join(exports, "verify-section.dxf")
    result = engine.export_section("x", 6.0, section_path)
    with open(section_path, "r", encoding="utf-8") as handle:
        dxf = handle.read()
    report("POLYLINE" in dxf, "section DXF has cut outlines",
           result["lines"][1] if len(result["lines"]) > 1 else "")


def finish():
    print("RESULT: {0} passed, {1} failed.".format(PASSED, FAILED))
    print("Manual checks that need a human:")
    print("1. VoiceOver reads every line of: maquette describe")
    print("2. Force-quit Rhino, reopen it, then: maquette rebuild")
    print("   The model comes back; WARNING lines only where expected.")
    print("3. maquette listener-stop, then: maquette connect --inject")
    print("   The listener returns with no Rhino clicking.")
    print("4. maquette chat: one direct command (box 1 1 1), one ask.")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
