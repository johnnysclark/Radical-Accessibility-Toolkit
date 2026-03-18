#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radical Accessibility Toolkit — Runtime Launcher
==================================================
Single-command operational launcher for daily use.

Commands:
    python runtime/launcher.py start    — validate and start the controller CLI
    python runtime/launcher.py status   — show subsystem health
    python runtime/launcher.py doctor   — run all health checks with detail
    python runtime/launcher.py stop     — release locks and write shutdown status

All output uses OK:/ERROR:/WARNING: prefixes for screen readers.
Prints READY: when done so screen readers detect completion.

Python 3 stdlib only.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime

# Ensure runtime package is importable
_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(_here)
if _root not in sys.path:
    sys.path.insert(0, _root)

from runtime.config import (
    PROJECT_ROOT, CONTROLLER_DIR, CONTROLLER_CLI_PATH,
    MCP_SERVER_PATH, STATUS_FILE, resolve_state_path,
    load_runtime_config,
)
from runtime.health import run_all_checks


def _ok(msg):
    print("OK: " + msg)


def _err(msg):
    print("ERROR: " + msg)


def _warn(msg):
    print("WARNING: " + msg)


def _write_status(status_data):
    """Write machine-readable status to runtime/status.json."""
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    tmp = STATUS_FILE + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, STATUS_FILE)
    except IOError:
        pass


def cmd_doctor(state_path=None):
    """Run all health checks and report results."""
    print("Radical Accessibility Toolkit — Doctor")
    print("Project: {}".format(PROJECT_ROOT))
    print("")

    checks = run_all_checks(state_path)
    errors = 0
    warnings = 0

    for check in checks:
        status = check["status"]
        name = check["name"]
        msg = check["message"]
        if status == "ok":
            _ok("{}: {}".format(name, msg))
        elif status == "warning":
            _warn("{}: {}".format(name, msg))
            warnings += 1
        else:
            _err("{}: {}".format(name, msg))
            errors += 1

    print("")
    if errors == 0 and warnings == 0:
        _ok("All checks passed.")
    elif errors == 0:
        _ok("{} checks passed, {} warnings.".format(
            len(checks) - warnings, warnings))
    else:
        _err("{} errors, {} warnings out of {} checks.".format(
            errors, warnings, len(checks)))

    status_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": "doctor",
        "errors": errors,
        "warnings": warnings,
        "total_checks": len(checks),
        "checks": checks,
    }
    _write_status(status_data)

    print("READY:")
    return errors


def cmd_status(state_path=None):
    """Show a brief subsystem health summary."""
    print("Radical Accessibility Toolkit — Status")
    print("")

    checks = run_all_checks(state_path)
    for check in checks:
        status_char = {"ok": "OK", "warning": "WARN", "error": "ERR"}[check["status"]]
        print("{}: {} — {}".format(status_char, check["name"], check["message"]))

    errors = sum(1 for c in checks if c["status"] == "error")

    status_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": "status",
        "errors": errors,
        "checks": checks,
    }
    _write_status(status_data)

    print("")
    print("READY:")
    return errors


def cmd_start(state_path=None):
    """Validate environment and start the controller CLI."""
    print("Radical Accessibility Toolkit — Start")
    print("Project: {}".format(PROJECT_ROOT))
    print("")

    state_path = state_path or resolve_state_path()

    # Run essential checks first
    checks = run_all_checks(state_path)
    critical_failed = False
    for check in checks:
        if check["status"] == "error" and check["name"] in (
                "python_version", "project_structure", "controller_cli"):
            _err("{}: {}".format(check["name"], check["message"]))
            critical_failed = True
        elif check["status"] == "warning":
            _warn("{}: {}".format(check["name"], check["message"]))
        else:
            _ok("{}: {}".format(check["name"], check["message"]))

    if critical_failed:
        _err("Cannot start — fix the errors above.")
        print("READY:")
        return 1

    print("")
    _ok("Environment validated. Starting controller CLI.")
    print("")

    status_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": "start",
        "state_path": state_path,
        "status": "starting",
    }
    _write_status(status_data)

    # Launch the controller CLI in the current process
    cli_args = [sys.executable, CONTROLLER_CLI_PATH, "--state", state_path]
    try:
        result = subprocess.run(cli_args)
        return result.returncode
    except KeyboardInterrupt:
        print("")
        _ok("Controller stopped.")
        print("READY:")
        return 0
    except FileNotFoundError:
        _err("Could not find Python or controller_cli.py.")
        print("READY:")
        return 1


def cmd_stop(state_path=None):
    """Release any stale locks and write shutdown status."""
    print("Radical Accessibility Toolkit — Stop")
    print("")

    state_path = state_path or resolve_state_path()
    lock_path = state_path + ".lock"

    if os.path.isfile(lock_path):
        try:
            with open(lock_path, "r", encoding="utf-8") as f:
                lock_info = json.load(f)
            _warn("Removing lock held by '{}' since {}.".format(
                lock_info.get("writer", "unknown"),
                lock_info.get("acquired_at", "unknown")))
        except (json.JSONDecodeError, IOError):
            _warn("Removing unreadable lock file.")
        os.remove(lock_path)
        _ok("Lock released.")
    else:
        _ok("No active lock to release.")

    status_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "command": "stop",
        "status": "stopped",
    }
    _write_status(status_data)

    print("READY:")
    return 0


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Radical Accessibility Toolkit — Runtime Launcher")
    parser.add_argument("command", nargs="?", default="status",
                        choices=["start", "status", "doctor", "stop"],
                        help="Command to run (default: status)")
    parser.add_argument("--state", default=None,
                        help="Path to state.json (default: controller/state.json)")
    args = parser.parse_args()

    commands = {
        "start": cmd_start,
        "status": cmd_status,
        "doctor": cmd_doctor,
        "stop": cmd_stop,
    }
    return commands[args.command](args.state)


if __name__ == "__main__":
    sys.exit(main())
