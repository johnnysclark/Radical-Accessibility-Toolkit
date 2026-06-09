"""jig watcher: runs inside Rhino 8 (CPython 3). Crash-only by design.

Polls the state file's mtime on Rhino's Idle event; on change, clears all
JIG layers, recompiles the scene from disk, redraws, and writes
scene_report.json next to the state file. Rhino is a consumer: this script
never writes to state.json.

It runs from the watcher bundle that ``jig rhino install`` copies to the
application support folder; the bundle carries its own copy of jig.model
and jig.geometry, so Rhino never imports from the user's venv.

Manual start (fallback when rhinocode injection is unavailable): open
Rhino's ScriptEditor, open this file from the bundle folder, and run it.
"""

import json
import os
import subprocess
import sys
import time

BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
if BUNDLE_DIR not in sys.path:
    sys.path.insert(0, BUNDLE_DIR)

from jig.geometry.compile import ALL_LAYERS, compile_scene  # noqa: E402
from jig.geometry.primitives import (Arc, Circle, Polyline, TextLabel,  # noqa: E402
                                     arc_three_points, plan_bbox, plan_counts)
from jig.model.io import load_state  # noqa: E402

POLL_SECONDS = 0.5

try:
    import rhinoscriptsyntax as rs
    import Rhino
    import scriptcontext
    IN_RHINO = True
except ImportError:
    rs = None
    Rhino = None
    scriptcontext = None
    IN_RHINO = False


def config_path():
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/jig/config.json")
    return os.path.expanduser("~/.jig/config.json")


def load_config():
    path = os.environ.get("JIG_CONFIG", config_path())
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def report_path(state_path):
    return os.path.join(os.path.dirname(state_path), "scene_report.json")


# -- drawing ----------------------------------------------------------------

def draw_primitive(rs_module, primitive, layer):
    """Draw one primitive with an rs-like module; returns the new object id."""
    if isinstance(primitive, Polyline):
        points = [[x, y, 0.0] for x, y in primitive.points]
        if primitive.closed:
            points.append(points[0])
        if len(points) == 2:
            guid = rs_module.AddLine(points[0], points[1])
        else:
            guid = rs_module.AddPolyline(points)
    elif isinstance(primitive, Circle):
        guid = rs_module.AddCircle([primitive.center[0], primitive.center[1], 0.0],
                                   primitive.radius)
    elif isinstance(primitive, Arc):
        start, mid, end = arc_three_points(primitive)
        guid = rs_module.AddArc3Pt([start[0], start[1], 0.0],
                                   [end[0], end[1], 0.0],
                                   [mid[0], mid[1], 0.0])
    elif isinstance(primitive, TextLabel):
        guid = rs_module.AddText(primitive.text,
                                 [primitive.at[0], primitive.at[1], 0.0],
                                 primitive.height)
    else:
        raise TypeError("unknown primitive {!r}".format(primitive))
    if guid:
        rs_module.ObjectLayer(guid, layer)
    return guid


def clear_layers(rs_module):
    for layer in ALL_LAYERS:
        if rs_module.IsLayer(layer):
            objects = rs_module.ObjectsByLayer(layer)
            if objects:
                rs_module.DeleteObjects(objects)


def render_plan(rs_module, plan):
    """Clear JIG layers and draw a full ScenePlan. Returns drawn count."""
    clear_layers(rs_module)
    drawn = 0
    for layer in sorted(plan):
        primitives = plan[layer]
        if not primitives:
            continue
        if not rs_module.IsLayer(layer):
            rs_module.AddLayer(layer)
        for primitive in primitives:
            if draw_primitive(rs_module, primitive, layer):
                drawn += 1
    return drawn


# -- rebuild cycle ----------------------------------------------------------

def rebuild(state_path):
    """One full rebuild from disk. Returns the report dict it wrote."""
    report = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "state_path": state_path, "error": ""}
    try:
        state = load_state(state_path)
        plan = compile_scene(state)
        report["counts"] = plan_counts(plan)
        report["bbox"] = plan_bbox(plan)
        if IN_RHINO:
            rs.EnableRedraw(False)
            try:
                report["drawn"] = render_plan(rs, plan)
            finally:
                rs.EnableRedraw(True)
            print("[jig] Rebuilt: {} objects.".format(report["drawn"]))
            _audio(report)
    except Exception as exc:  # crash-only: report, never die
        report["error"] = str(exc)
        if IN_RHINO:
            print("[jig] ERROR: {}".format(exc))
    _write_report(state_path, report)
    return report


def _write_report(state_path, report):
    path = report_path(state_path)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    os.replace(tmp, path)


def _audio(report):
    mode = os.environ.get("JIG_AUDIO", "none")
    if mode in ("chime", "both") and sys.platform == "darwin":
        subprocess.Popen(["afplay", "/System/Library/Sounds/Pop.aiff"])
    if mode in ("speak", "both") and sys.platform == "darwin":
        subprocess.Popen(["say", "rebuilt {} objects".format(report.get("drawn", 0))])


# -- idle-event watcher -------------------------------------------------------

class Watcher:
    def __init__(self, state_path):
        self.state_path = state_path
        self.last_mtime = 0.0
        self.last_poll = 0.0

    def on_idle(self, sender, args):
        now = time.time()
        if now - self.last_poll < POLL_SECONDS:
            return
        self.last_poll = now
        try:
            mtime = os.path.getmtime(self.state_path)
        except OSError:
            return
        if mtime != self.last_mtime:
            self.last_mtime = mtime
            rebuild(self.state_path)


def install():
    config = load_config()
    state_path = os.environ.get("JIG_STATE", config["state_path"])
    if not IN_RHINO:
        print("[jig] not inside Rhino; doing a single dry-run compile")
        rebuild(state_path)
        return
    # replace any previously installed handler so re-running is safe
    old = scriptcontext.sticky.pop("jig_watcher", None)
    if old is not None:
        try:
            Rhino.RhinoApp.Idle -= old.on_idle
        except Exception:
            pass
    watcher = Watcher(state_path)
    scriptcontext.sticky["jig_watcher"] = watcher
    Rhino.RhinoApp.Idle += watcher.on_idle
    print("[jig] Watching {}".format(state_path))
    rebuild(state_path)


if __name__ == "__main__":
    install()
