#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Radical Accessibility Toolkit — Setup Script
=============================================
One-command setup: installs all dependencies, creates config files,
initializes state.json. Screen-reader-friendly output.

Run from the repo root:
    python setup.py

Optional:
    python setup.py --minimal    Skip TACT install (CI or lightweight setups)

Steps:
  1. Check Python version (3.10+ required for TACT)
  2. Install MCP package (pip install mcp)
  3. Install TACT with extras (pip install -e tools/tact[ocr,mcp])
  4. Create controller/state.json if missing
  5. Write .mcp.json for Claude Code
  6. Validate state.json
  7. Test MCP server import
  8. Check acclaude dependencies (optional, Node.js)
  9. Print summary

All output uses OK: / ERROR: / WARNING: prefixes for screen readers.
No API keys needed — MCP servers run through the Claude Code subscription.
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
    """Check Python version >= 3.10."""
    v = sys.version_info
    ver = "{}.{}.{}".format(v.major, v.minor, v.micro)
    if v >= (3, 10):
        _ok("Python {} (3.10+ required).".format(ver))
        return True
    else:
        _err("Python {} found but 3.10+ required.".format(ver))
        return False


def _pip_install(arg):
    """Try pip install; retry with --break-system-packages on PEP 668 failure."""
    cmd = [sys.executable, "-m", "pip", "install", "-q", arg]
    try:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        stderr_text = e.stderr.decode() if e.stderr else ""
        if "externally-managed-environment" in stderr_text:
            _warn("PEP 668 detected. Retrying with --break-system-packages.")
            try:
                subprocess.check_call(
                    cmd + ["--break-system-packages"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except subprocess.CalledProcessError:
                return False
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
    if _pip_install("mcp"):
        try:
            import importlib
            importlib.invalidate_caches()
            subprocess.check_output(
                [sys.executable, "-c", "import mcp; print(mcp.__version__)"],
                stderr=subprocess.DEVNULL).decode().strip()
            _ok("mcp package installed.")
            return True
        except Exception:
            pass
    _err("Failed to install mcp. Run manually: pip install mcp")
    return False


def install_tact(project_root):
    """Install TACT with ocr and mcp extras."""
    tact_dir = os.path.join(project_root, "tools", "tact")
    if not os.path.isdir(tact_dir):
        _err("tools/tact/ not found. Cannot install TACT.")
        return False

    # Check if already installed
    try:
        subprocess.check_output(
            [sys.executable, "-c", "import tactile_core"],
            stderr=subprocess.DEVNULL, timeout=10)
        _ok("TACT (tactile-core) already installed.")
        return True
    except Exception:
        pass

    _warn("TACT not installed. Installing with OCR and MCP extras...")
    tact_spec = os.path.join(project_root, "tools", "tact") + "[ocr,mcp]"
    install_arg = "-e " + tact_spec

    # pip install -e requires the -e and path as separate args
    cmd = [sys.executable, "-m", "pip", "install", "-q", "-e", tact_spec]
    try:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        _ok("TACT installed with OCR and MCP extras.")
        return True
    except subprocess.CalledProcessError as e:
        stderr_text = e.stderr.decode() if e.stderr else ""
        if "externally-managed-environment" in stderr_text:
            _warn("PEP 668 detected. Retrying with --break-system-packages.")
            try:
                subprocess.check_call(
                    cmd + ["--break-system-packages"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                _ok("TACT installed with OCR and MCP extras.")
                return True
            except subprocess.CalledProcessError:
                pass
        _err("Failed to install TACT. Run manually: pip install -e tools/tact[ocr,mcp]")
        return False


def create_state_json(project_root):
    """Create controller/state.json if missing, using controller_cli defaults."""
    state_path = os.path.join(project_root, "controller", "state.json")
    if os.path.isfile(state_path):
        return True  # Already exists, will be validated later

    _warn("controller/state.json not found. Creating default state...")
    try:
        # Import controller_cli to get default state
        cli_path = os.path.join(project_root, "controller")
        if cli_path not in sys.path:
            sys.path.insert(0, cli_path)
        import controller_cli as cli
        state = cli.load_state(state_path)  # Returns default_state() when file missing
        cli.save_state(state_path, state)
        _ok("controller/state.json created with default state.")
        return True
    except Exception as e:
        _err("Could not create state.json: {}".format(e))
        _warn("Start the CLI once to create it: python controller/controller_cli.py")
        return False


def check_acclaude(project_root):
    """Check if acclaude dependencies are available (optional)."""
    acclaude_dir = os.path.join(project_root, "tools", "accessible-client")
    if not os.path.isdir(acclaude_dir):
        _warn("tools/accessible-client/ not found. Skipping acclaude check.")
        return False
    try:
        result = subprocess.check_output(
            ["node", "--version"],
            stderr=subprocess.DEVNULL, timeout=5).decode().strip()
        _ok("Node.js {} found (acclaude ready).".format(result))
        return True
    except Exception:
        _warn("Node.js not found. acclaude requires Node.js 18+.")
        _warn("acclaude is optional. It provides a screen-reader-friendly Claude Code wrapper.")
        return False


def setup_mcp_json(project_root):
    """Create or fix .mcp.json for Claude Code. Always includes tactile server."""
    mcp_path = os.path.join(project_root, ".mcp.json")

    correct_config = {
        "mcpServers": {
            "layout-jig": {
                "command": "python",
                "args": [
                    "mcp/mcp_server.py",
                    "--state",
                    "controller/state.json"
                ]
            },
            "tactile": {
                "command": "python",
                "args": ["tools/tact/mcp_entry.py"]
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
        return False
    try:
        with open(state_path, "r") as f:
            state = json.load(f)
        schema = state.get("schema", "unknown")
        bay_count = len(state.get("bays", {}))
        _ok("controller/state.json valid (schema {}, {} bays).".format(schema, bay_count))
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
    cli_path = os.path.join(project_root, "controller", "controller_cli.py")
    if not os.path.isfile(cli_path):
        _err("controller/controller_cli.py not found (required by MCP server).")
        return False
    try:
        subprocess.check_output(
            [sys.executable, "-c", "import mcp"],
            stderr=subprocess.DEVNULL, timeout=10)
    except Exception:
        _err("mcp package not importable. MCP server will not start.")
        return False
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
    """Run all setup steps."""
    project_root = os.path.dirname(os.path.abspath(__file__))

    minimal = "--minimal" in sys.argv

    print("Radical Accessibility Toolkit — Setup")
    print("Project: {}".format(project_root))
    if minimal:
        print("Mode: minimal (skipping TACT install)")
    print("")

    errors = 0

    # 1. Python version
    if not check_python():
        errors += 1

    # 2. Install mcp
    if not check_mcp():
        errors += 1

    # 3. Install TACT (unless --minimal)
    if not minimal:
        if not install_tact(project_root):
            errors += 1
    else:
        _warn("Skipping TACT install (--minimal mode).")

    # 4. Create state.json if missing
    if not create_state_json(project_root):
        errors += 1

    # 5. Write .mcp.json
    if not setup_mcp_json(project_root):
        errors += 1

    # 6. Validate state.json
    if not check_state_json(project_root):
        errors += 1

    # 7. Test MCP server
    if not test_mcp_server(project_root):
        errors += 1

    # 8. Check acclaude (optional, never an error)
    check_acclaude(project_root)

    # 9. Summary
    print("")
    if errors == 0:
        print("READY: Setup complete. 0 errors.")
        print("")
        print("Next steps:")
        print("  1. Start designing: python controller/controller_cli.py")
        print("  2. MCP servers start automatically via .mcp.json in Claude Code.")
        print("  3. No API keys needed — runs through the Claude Code subscription.")
    else:
        print("DONE: Setup complete with {} error(s). Fix the issues above.".format(errors))

    return errors


if __name__ == "__main__":
    sys.exit(main())
