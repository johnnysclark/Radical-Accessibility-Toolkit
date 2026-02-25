# -*- coding: utf-8 -*-
"""
PLAN LAYOUT JIG — MCP Server  v1.0
====================================
Model Context Protocol wrapper around the Layout Jig CLI.

Exposes the CLI's command vocabulary as MCP tools so that Claude Desktop,
Cursor, or any MCP-compatible client can drive the jig conversationally.

Requires: pip install mcp

Usage:
    python mcp_server.py --state path/to/state.json

Or set the environment variable:
    LAYOUT_JIG_STATE=path/to/state.json python mcp_server.py

Claude Desktop config snippet (claude_desktop_config.json):
{
  "mcpServers": {
    "layout-jig": {
      "command": "python",
      "args": ["path/to/mcp_server.py", "--state", "path/to/state.json"]
    }
  }
}
"""

import builtins
import json
import os
import sys

# ── Redirect print to stderr (stdout is JSON-RPC) ──────
_real_print = builtins.print

def _stderr_print(*args, **kwargs):
    kwargs.setdefault("file", sys.stderr)
    _real_print(*args, **kwargs)

builtins.print = _stderr_print

# ── Import controller_cli from same directory ──────────
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

import controller_cli as cli

# ── MCP dependency ─────────────────────────────────────
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    _real_print(
        "ERROR: mcp package not found. Install with: pip install mcp",
        file=sys.stderr)
    sys.exit(1)

# ── Resolve state file path ───────────────────────────
def _resolve_state_path():
    """Resolve state file from CLI args or environment variable."""
    # Check CLI args
    for i, arg in enumerate(sys.argv):
        if arg == "--state" and i + 1 < len(sys.argv):
            return os.path.abspath(sys.argv[i + 1])
    # Check environment variable
    env = os.environ.get("LAYOUT_JIG_STATE")
    if env:
        return os.path.abspath(env)
    # Default: state.json in same folder as this script
    return os.path.join(_here, "state.json")


STATE_PATH = _resolve_state_path()

# ── Helper: load, run command, save ───────────────────

def _load_state():
    """Load state from disk with migration."""
    state = cli.load_state(STATE_PATH)
    # Apply same migrations as main()
    if state.get("schema") not in (cli.SCHEMA, "school_jig_2d_v2.2"):
        state = cli.default_state()
    if state.get("schema") == "school_jig_2d_v2.2":
        state["schema"] = cli.SCHEMA
    if "legend" not in state:
        state["legend"] = cli._default_legend()
    if "tactile3d" not in state:
        state["tactile3d"] = cli._default_tactile3d()
    if "auto_export" not in state.get("tactile3d", {}):
        state["tactile3d"]["auto_export"] = False
    if "bambu" not in state:
        state["bambu"] = cli._default_bambu()
    if "tts" not in state:
        state["tts"] = cli._default_tts()
    if "section" not in state:
        state["section"] = cli._default_section()
    return state


def _run(command_str):
    """Load state, tokenize+run one command, save, return message.

    Handles all special sentinels (__DESCRIBE__, __HELP__, etc.)
    except __QUIT__ (not meaningful over MCP) and __UNDO__ (returns
    an error suggesting snapshots instead).
    """
    state = _load_state()
    tokens = cli.tokenize(command_str)
    if not tokens:
        return "No command provided."

    try:
        state, msg = cli.apply_command(state, tokens, state_file=STATE_PATH)
    except Exception as e:
        return f"ERROR: {e}"

    # Handle sentinels
    if msg == "__QUIT__":
        return "Use 'snapshot save <name>' to checkpoint. Quit is not available in MCP mode."
    if msg == "__HELP__":
        return cli.HELP_TEXT
    if msg == "__DESCRIBE__":
        return cli.describe(state)
    if msg == "__LIST_BAYS__":
        return cli.list_bays(state)
    if msg == "__STATUS__":
        try:
            st = os.stat(STATE_PATH)
            import time
            return (f"State: {STATE_PATH}\n"
                    f"Modified: {time.ctime(st.st_mtime)}  "
                    f"Size: {st.st_size} bytes")
        except Exception:
            return f"State: {STATE_PATH}"
    if msg == "__UNDO__":
        return ("ERROR: Undo is not available in MCP mode. "
                "Use 'snapshot save <name>' before changes and "
                "'snapshot load <name>' to restore.")
    if msg == "__PRINT__":
        result = cli.do_print(state, STATE_PATH)
        return result

    # Normal command — save state
    try:
        cli.save_state(STATE_PATH, state)
        # Clear one-shot export flag
        t3 = state.get("tactile3d")
        if t3 and t3.get("_export_once"):
            t3["_export_once"] = False
    except Exception as e:
        return f"ERROR saving state: {e}"

    return msg


# ── MCP Server ─────────────────────────────────────────

mcp = FastMCP("layout-jig")


@mcp.tool()
def run_command(command: str) -> str:
    """Execute any Layout Jig CLI command.

    Examples:
        run_command("set bay A rotation 30")
        run_command("wall A on")
        run_command("corridor A width 12")
        run_command("aperture A add d2 door x 1 5 3 7")
        run_command("describe")
        run_command("list bays")
        run_command("snapshot save before_changes")
    """
    return _run(command)


@mcp.tool()
def describe() -> str:
    """Get a full text description of the current model state.

    Returns all settings: site, style, bays, corridors, walls,
    apertures, rooms, legend, tactile3d, TTS, section cut, and totals.
    """
    state = _load_state()
    return cli.describe(state)


@mcp.tool()
def list_bays() -> str:
    """Get a compact table of all bays with key properties.

    Shows: name, grid type, z-order, anchor, rotation, columns,
    walls, apertures, and corridor status.
    """
    state = _load_state()
    return cli.list_bays(state)


@mcp.tool()
def get_state() -> str:
    """Get the raw JSON contents of the state file.

    Returns the complete Canonical Model Artifact (CMA) as a
    formatted JSON string.
    """
    state = _load_state()
    return json.dumps(state, indent=2, ensure_ascii=False)


@mcp.tool()
def get_help() -> str:
    """Get the full command reference for the Layout Jig CLI.

    Lists all available commands with syntax and examples.
    """
    return cli.HELP_TEXT


# ── Entry point ────────────────────────────────────────

if __name__ == "__main__":
    _real_print(f"Layout Jig MCP Server starting...", file=sys.stderr)
    _real_print(f"State file: {STATE_PATH}", file=sys.stderr)
    mcp.run()
