# -*- coding: utf-8 -*-
"""
Runtime configuration for the Radical Accessibility Toolkit.
Resolves paths, detects environments, and provides runtime defaults.

Python 3 stdlib only.
"""
import json
import os
import sys


def _find_project_root():
    """Walk up from this file to find the project root (contains controller/)."""
    d = os.path.dirname(os.path.abspath(__file__))
    # runtime/ is directly under project root
    candidate = os.path.dirname(d)
    if os.path.isdir(os.path.join(candidate, "controller")):
        return candidate
    return candidate


PROJECT_ROOT = _find_project_root()
CONTROLLER_DIR = os.path.join(PROJECT_ROOT, "controller")
MCP_DIR = os.path.join(PROJECT_ROOT, "mcp")
TOOLS_DIR = os.path.join(PROJECT_ROOT, "tools")
RUNTIME_DIR = os.path.join(PROJECT_ROOT, "runtime")

DEFAULT_STATE_PATH = os.path.join(CONTROLLER_DIR, "state.json")
MCP_SERVER_PATH = os.path.join(MCP_DIR, "mcp_server.py")
WATCHER_PATH = os.path.join(TOOLS_DIR, "rhino", "rhino_watcher.py")
CONTROLLER_CLI_PATH = os.path.join(CONTROLLER_DIR, "controller_cli.py")

STATUS_FILE = os.path.join(RUNTIME_DIR, "status.json")
LOCK_DIR = os.path.join(CONTROLLER_DIR, "locks")
JOURNAL_DIR = os.path.join(CONTROLLER_DIR, "journal")


def resolve_state_path(override=None):
    """Return the state file path from override, env, or default."""
    if override:
        return os.path.abspath(override)
    env = os.environ.get("LAYOUT_JIG_STATE")
    if env:
        return os.path.abspath(env)
    return DEFAULT_STATE_PATH


def load_runtime_config(path=None):
    """Load optional runtime config from runtime/runtime_config.json."""
    if path is None:
        path = os.path.join(RUNTIME_DIR, "runtime_config.json")
    if not os.path.isfile(path):
        return _default_runtime_config()
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        merged = _default_runtime_config()
        merged.update(cfg)
        return merged
    except (json.JSONDecodeError, IOError):
        return _default_runtime_config()


def _default_runtime_config():
    return {
        "auto_start_mcp": False,
        "auto_start_rhino": False,
        "state_path": DEFAULT_STATE_PATH,
        "mcp_port": None,
        "log_level": "info",
        "capability_tier": "user",
    }
