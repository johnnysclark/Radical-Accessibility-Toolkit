# -*- coding: utf-8 -*-
"""
Health checks for the Radical Accessibility Toolkit runtime.
Each check returns a dict: {"name": str, "status": "ok"|"warning"|"error", "message": str}

Python 3 stdlib only.
"""
import json
import os
import subprocess
import sys

from runtime.config import (
    PROJECT_ROOT, CONTROLLER_DIR, MCP_DIR, TOOLS_DIR,
    CONTROLLER_CLI_PATH, MCP_SERVER_PATH, WATCHER_PATH,
    resolve_state_path,
)


def _result(name, status, message):
    return {"name": name, "status": status, "message": message}


def check_python_version():
    """Python 3.8+ required."""
    v = sys.version_info
    ver = "{}.{}.{}".format(v.major, v.minor, v.micro)
    if v >= (3, 8):
        return _result("python_version", "ok", "Python {} (3.8+ required).".format(ver))
    return _result("python_version", "error", "Python {} found but 3.8+ required.".format(ver))


def check_project_structure():
    """Verify critical directories exist."""
    missing = []
    for name, path in [("controller", CONTROLLER_DIR), ("mcp", MCP_DIR),
                       ("tools", TOOLS_DIR)]:
        if not os.path.isdir(path):
            missing.append(name)
    if missing:
        return _result("project_structure", "error",
                       "Missing directories: {}.".format(", ".join(missing)))
    return _result("project_structure", "ok", "Project structure intact.")


def check_controller_cli():
    """Verify controller_cli.py exists and is importable."""
    if not os.path.isfile(CONTROLLER_CLI_PATH):
        return _result("controller_cli", "error",
                       "controller_cli.py not found at {}.".format(CONTROLLER_CLI_PATH))
    try:
        if CONTROLLER_DIR not in sys.path:
            sys.path.insert(0, CONTROLLER_DIR)
        import controller_cli
        schema = getattr(controller_cli, "SCHEMA", "unknown")
        return _result("controller_cli", "ok",
                       "Controller CLI importable (schema {}).".format(schema))
    except Exception as e:
        return _result("controller_cli", "error",
                       "Controller CLI import failed: {}.".format(e))


def check_state_file(state_path=None):
    """Validate state.json exists and parses."""
    state_path = state_path or resolve_state_path()
    if not os.path.isfile(state_path):
        return _result("state_file", "warning",
                       "state.json not found at {}. Will be created on first CLI run.".format(
                           state_path))
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        schema = state.get("schema", "unknown")
        bay_count = len(state.get("bays", {}))
        rev = state.get("meta", {}).get("state_revision", "none")
        return _result("state_file", "ok",
                       "state.json loaded (schema {}, {} bays, revision {}).".format(
                           schema, bay_count, rev))
    except json.JSONDecodeError as e:
        return _result("state_file", "error",
                       "state.json is not valid JSON: {}.".format(e))
    except IOError as e:
        return _result("state_file", "error",
                       "Could not read state.json: {}.".format(e))


def check_mcp_package():
    """Check if the mcp Python package is installed."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import mcp; print(getattr(mcp, '__version__', 'unknown'))"],
            capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            ver = result.stdout.strip()
            return _result("mcp_package", "ok", "mcp package installed (v{}).".format(ver))
        return _result("mcp_package", "warning",
                       "mcp package not importable. MCP server will not start.")
    except Exception as e:
        return _result("mcp_package", "warning",
                       "Could not check mcp package: {}.".format(e))


def check_mcp_server():
    """Verify MCP server file exists."""
    if not os.path.isfile(MCP_SERVER_PATH):
        return _result("mcp_server", "error",
                       "mcp_server.py not found at {}.".format(MCP_SERVER_PATH))
    return _result("mcp_server", "ok", "MCP server file present.")


def check_rhino_watcher():
    """Verify watcher script exists."""
    if not os.path.isfile(WATCHER_PATH):
        return _result("rhino_watcher", "error",
                       "rhino_watcher.py not found at {}.".format(WATCHER_PATH))
    return _result("rhino_watcher", "ok", "Rhino watcher script present.")


def check_swell_print():
    """Check swell-print dependencies."""
    swell_dir = os.path.join(TOOLS_DIR, "swell-print")
    if not os.path.isdir(swell_dir):
        return _result("swell_print", "warning", "tools/swell-print/ not found.")
    try:
        result = subprocess.run(
            [sys.executable, "-c", "from PIL import Image; import reportlab"],
            capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return _result("swell_print", "ok", "Swell-print dependencies available.")
        return _result("swell_print", "warning",
                       "Swell-print dependencies missing (Pillow/reportlab).")
    except Exception:
        return _result("swell_print", "warning", "Could not check swell-print dependencies.")


def check_lock_status(state_path=None):
    """Check if a write lock exists on state.json."""
    state_path = state_path or resolve_state_path()
    lock_path = state_path + ".lock"
    if os.path.isfile(lock_path):
        try:
            with open(lock_path, "r", encoding="utf-8") as f:
                lock_info = json.load(f)
            writer = lock_info.get("writer", "unknown")
            ts = lock_info.get("acquired_at", "unknown")
            return _result("lock_status", "warning",
                           "Write lock held by '{}' since {}.".format(writer, ts))
        except (json.JSONDecodeError, IOError):
            return _result("lock_status", "warning",
                           "Lock file exists but could not be read.")
    return _result("lock_status", "ok", "No active write lock.")


def check_journal(state_path=None):
    """Check journal directory status."""
    from runtime.config import JOURNAL_DIR
    if not os.path.isdir(JOURNAL_DIR):
        return _result("journal", "ok", "Journal directory not yet created (will be created on first write).")
    entries = [f for f in os.listdir(JOURNAL_DIR) if f.endswith(".json")]
    return _result("journal", "ok",
                   "Journal has {} entries.".format(len(entries)))


def run_all_checks(state_path=None):
    """Run all health checks and return list of results."""
    checks = [
        check_python_version(),
        check_project_structure(),
        check_controller_cli(),
        check_state_file(state_path),
        check_mcp_package(),
        check_mcp_server(),
        check_rhino_watcher(),
        check_swell_print(),
        check_lock_status(state_path),
        check_journal(state_path),
    ]
    return checks
