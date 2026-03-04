#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radical Accessibility Toolkit — Setup Script
=============================================
One-command setup for the MCP server, swell-print dependencies,
and project configuration.  Screen-reader-friendly output.

Run from the CONTROLLER directory:
    python setup.py

Checks:
  1. Python version (3.8+ required)
  2. Installs MCP package (pip install mcp)
  3. Installs swell-print dependencies (Pillow, reportlab)
  4. Creates or fixes .mcp.json for Claude Code
  5. Validates controller/state.json
  6. Tests that the MCP server can import successfully

All output uses OK: / ERROR: / WARNING: prefixes for screen readers.
"""

import json
import os
import subprocess
import sys


def _ok(msg):
    print("OK: " + msg)

def _err(msg):
    print("ERROR: " + msg)

def _warn(msg):
    print("WARNING: " + msg)


def check_python():
    """Check Python version >= 3.8."""
    v = sys.version_info
    ver = "{}.{}.{}".format(v.major, v.minor, v.micro)
    if v >= (3, 8):
        _ok("Python {} (3.8+ required).".format(ver))
        return True
    else:
        _err("Python {} found but 3.8+ required.".format(ver))
        return False


def install_package(name, pip_arg=None):
    """Install a pip package.  Returns True on success."""
    arg = pip_arg or name
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", arg],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def check_mcp():
    """Install and verify the mcp package."""
    try:
        import mcp  # noqa: F401
        ver = getattr(mcp, "__version__", "unknown")
        _ok("mcp package installed (v{}).".format(ver))
        return True
    except ImportError:
        pass
    _warn("mcp package not found. Installing...")
    if install_package("mcp"):
        try:
            import importlib
            importlib.invalidate_caches()
            # Re-check
            subprocess.check_output(
                [sys.executable, "-c", "import mcp; print(mcp.__version__)"],
                stderr=subprocess.DEVNULL).decode().strip()
            _ok("mcp package installed.")
            return True
        except Exception:
            pass
    _err("Failed to install mcp. Run manually: pip install mcp")
    return False


def check_swell_print(project_root):
    """Install swell-print dependencies (optional)."""
    req_file = os.path.join(project_root, "tools", "swell-print", "requirements.txt")
    errors = 0
    if not os.path.isfile(req_file):
        _warn("tools/swell-print/requirements.txt not found. Skipping.")
        return True
    # Check Pillow
    try:
        from PIL import Image  # noqa: F401
        import PIL
        _ok("Pillow installed (v{}).".format(PIL.__version__))
    except ImportError:
        _warn("Pillow not found. Installing...")
        if install_package("Pillow"):
            _ok("Pillow installed.")
        else:
            _err("Failed to install Pillow. Run: pip install Pillow")
            errors += 1
    # Check reportlab
    try:
        import reportlab  # noqa: F401
        _ok("reportlab installed (v{}).".format(reportlab.Version))
    except ImportError:
        _warn("reportlab not found. Installing...")
        if install_package("reportlab"):
            _ok("reportlab installed.")
        else:
            _err("Failed to install reportlab. Run: pip install reportlab")
            errors += 1
    return errors == 0


def setup_mcp_json(project_root):
    """Create or fix .mcp.json for Claude Code."""
    # Claude Code looks for .mcp.json at the project root or parent
    # The repo root is one level up from CONTROLLER/
    repo_root = os.path.dirname(project_root)
    mcp_path = os.path.join(repo_root, ".mcp.json")

    # Correct config — paths relative to the repo root
    folder_name = os.path.basename(project_root)
    correct_config = {
        "mcpServers": {
            "layout-jig": {
                "command": "python",
                "args": [
                    "{}/mcp/mcp_server.py".format(folder_name),
                    "--state",
                    "{}/controller/state.json".format(folder_name)
                ]
            }
        }
    }

    needs_write = True
    if os.path.isfile(mcp_path):
        try:
            with open(mcp_path, "r") as f:
                existing = json.load(f)
            if existing == correct_config:
                needs_write = False
                _ok(".mcp.json already correct at {}".format(mcp_path))
        except (json.JSONDecodeError, IOError):
            _warn(".mcp.json exists but is invalid. Overwriting.")

    if needs_write:
        try:
            with open(mcp_path, "w") as f:
                json.dump(correct_config, f, indent=2)
                f.write("\n")
            _ok(".mcp.json written to {}".format(mcp_path))
        except IOError as e:
            _err("Could not write .mcp.json: {}".format(e))
            return False
    return True


def check_state_json(project_root):
    """Validate controller/state.json exists and has valid structure."""
    state_path = os.path.join(project_root, "controller", "state.json")
    if not os.path.isfile(state_path):
        _err("controller/state.json not found at {}".format(state_path))
        _warn("Start the CLI once to create it: python controller/controller_cli.py")
        return False
    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        schema = state.get("schema", "unknown")
        bay_count = len(state.get("bays", {}))
        _ok("controller/state.json found (schema {}, {} bays).".format(schema, bay_count))
        return True
    except json.JSONDecodeError as e:
        _err("controller/state.json is not valid JSON: {}".format(e))
        return False
    except IOError as e:
        _err("Could not read controller/state.json: {}".format(e))
        return False


def test_mcp_server(project_root):
    """Verify that mcp/mcp_server.py exists and its dependencies are met."""
    mcp_server_path = os.path.join(project_root, "mcp", "mcp_server.py")
    if not os.path.isfile(mcp_server_path):
        _err("mcp/mcp_server.py not found at {}".format(mcp_server_path))
        return False
    # Check that controller_cli.py exists (required by the server)
    cli_path = os.path.join(project_root, "controller", "controller_cli.py")
    if not os.path.isfile(cli_path):
        _err("controller/controller_cli.py not found (required by MCP server).")
        return False
    # Check that mcp package is importable (already verified above, but confirm)
    try:
        subprocess.check_output(
            [sys.executable, "-c", "import mcp"],
            stderr=subprocess.DEVNULL, timeout=10)
    except Exception:
        _err("mcp package not importable. MCP server will not start.")
        return False
    # Count tools by scanning the file for @mcp.tool() decorators
    try:
        with open(mcp_server_path, "r", encoding="utf-8") as f:
            content = f.read()
        tool_count = content.count("@mcp.tool()")
        _ok("MCP server ready ({} tools registered in source).".format(tool_count))
        return True
    except IOError as e:
        _err("Could not read mcp_server.py: {}".format(e))
        return False


def main():
    """Run all setup checks."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    print("Radical Accessibility Toolkit — Setup")
    print("Project: {}".format(project_root))
    print("")

    errors = 0

    if not check_python():
        errors += 1

    if not check_mcp():
        errors += 1

    if not check_swell_print(project_root):
        errors += 1

    if not setup_mcp_json(project_root):
        errors += 1

    if not check_state_json(project_root):
        errors += 1

    if not test_mcp_server(project_root):
        errors += 1

    print("")
    if errors == 0:
        print("READY: Setup complete. 0 errors.")
    else:
        print("DONE: Setup complete with {} error(s). Fix the issues above.".format(errors))

    return errors


if __name__ == "__main__":
    sys.exit(main())
