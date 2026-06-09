"""Rhino lifecycle commands: install the watcher bundle, start Rhino, status.

The bundle is a self-contained copy of jig.model + jig.geometry + the
watcher script, placed in the application support folder so Rhino's
embedded CPython never touches the user's venv or repo checkout.
"""

import json
import os
import shutil
import subprocess
import sys
import time

import jig
from jig.commands.registry import CommandError, command
from jig.model.io import atomic_write

RHINOCODE = "/Applications/Rhino 8.app/Contents/Resources/bin/rhinocode"
START_TIMEOUT_SECONDS = 90


def support_dir():
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/jig")
    return os.path.expanduser("~/.jig")


def bundle_dir():
    return os.path.join(support_dir(), "watcher")


def install_bundle(session):
    """Copy the watcher bundle and write config.json. Returns the bundle dir."""
    src_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bundle = bundle_dir()
    package = os.path.join(bundle, "jig")
    if os.path.isdir(package):
        shutil.rmtree(package)
    os.makedirs(package, exist_ok=True)
    shutil.copy(os.path.join(src_root, "__init__.py"), package)
    for sub in ("model", "geometry"):
        shutil.copytree(os.path.join(src_root, sub), os.path.join(package, sub),
                        ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(os.path.join(src_root, "watcher", "jig_watcher.py"), bundle)
    atomic_write(os.path.join(support_dir(), "config.json"), json.dumps({
        "state_path": session.state_path,
        "version": jig.__version__,
        "installed": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }, indent=2) + "\n")
    return bundle


@command("rhino install", "rhino install",
         "Copy the watcher bundle for Rhino and point it at this state file.",
         mutating=False)
def rhino_install(session, args, flags):
    bundle = install_bundle(session)
    return ("watcher bundle installed at {}. In Rhino, run {} from the "
            "ScriptEditor, or say rhino start".format(
                bundle, os.path.join(bundle, "jig_watcher.py")))


@command("rhino start", "rhino start",
         "Launch Rhino 8 and inject the watcher. macOS only.", mutating=False)
def rhino_start(session, args, flags):
    if sys.platform != "darwin":
        raise CommandError("rhino start only works on macOS. On this machine, "
                           "use rhino install and run the watcher manually")
    if not os.path.exists(RHINOCODE):
        raise CommandError("rhinocode not found at {}. Is Rhino 8 installed?".format(
            RHINOCODE))
    bundle = install_bundle(session)
    subprocess.run(["open", "-a", "Rhino 8"], check=True)
    deadline = time.time() + START_TIMEOUT_SECONDS
    while time.time() < deadline:
        result = subprocess.run([RHINOCODE, "list"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            break
        time.sleep(2)
    else:
        raise CommandError("Rhino did not answer within {} seconds. Open Rhino's "
                           "ScriptEditor and run {} manually".format(
                               START_TIMEOUT_SECONDS,
                               os.path.join(bundle, "jig_watcher.py")))
    script = os.path.join(bundle, "jig_watcher.py")
    result = subprocess.run([RHINOCODE, "script", script],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise CommandError("could not inject the watcher: {}. Fallback: open "
                           "Rhino's ScriptEditor and run {}".format(
                               result.stderr.strip() or "unknown error", script))
    return "Rhino is watching {}".format(session.state_path)


@command("rhino status", "rhino status",
         "Report what the Rhino watcher last drew.", mutating=False)
def rhino_status(session, args, flags):
    path = os.path.join(os.path.dirname(session.state_path), "scene_report.json")
    if not os.path.exists(path):
        return ("no scene report yet. The watcher has not run; "
                "say rhino start, or run the watcher in Rhino's ScriptEditor")
    with open(path, "r", encoding="utf-8") as fh:
        report = json.load(fh)
    age = int(time.time() - os.path.getmtime(path))
    if report.get("error"):
        return "watcher reported an error {} seconds ago: {}".format(
            age, report["error"])
    counts = report.get("counts", {})
    drawn = report.get("drawn", counts.get("total", 0))
    return "watcher rebuilt {} objects, {} seconds ago".format(drawn, age)
