"""Wrapper around Rhino 8's rhinocode CLI (Rhino >= 8.11).

Bootstrap and recovery transport only: it can start the Maquette
listener inside a running Rhino with zero GUI interaction. The
persistent socket stays the primary transport. rhinocode needs the
in-Rhino script server, enabled once with the StartScriptServer
command (or the _StartScriptServer startup command).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess

MAC_RHINOCODE = "/Applications/Rhino 8.app/Contents/Resources/bin/rhinocode"


def find_rhinocode() -> str | None:
    found = shutil.which("rhinocode")
    if found:
        return found
    if os.path.exists(MAC_RHINOCODE):
        return MAC_RHINOCODE
    return None


def list_instances() -> list[dict]:
    """Running Rhino instances, [] when rhinocode is missing or silent."""
    binary = find_rhinocode()
    if binary is None:
        return []
    try:
        result = subprocess.run([binary, "list", "--json"],
                                capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout or "[]")
        return data if isinstance(data, list) else []
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        return []


def run_script(script_path: str, rhino_id: str | None = None) -> tuple[bool, str]:
    """Ask a running Rhino to execute a script file."""
    binary = find_rhinocode()
    if binary is None:
        return False, "rhinocode CLI not found"
    command = [binary]
    if rhino_id:
        command += ["--rhino", rhino_id]
    command += ["script", script_path]
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=30)
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except (subprocess.SubprocessError, OSError) as exc:
        return False, str(exc)
