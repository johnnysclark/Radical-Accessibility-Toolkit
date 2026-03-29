#!/usr/bin/env python3
"""PreToolUse hook: auto-save snapshot before destructive MCP operations."""

import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.dirname(os.path.dirname(_here))
_controller = os.path.join(_root, "controller")
_state_path = os.path.join(_controller, "state.json")

if _controller not in sys.path:
    sys.path.insert(0, _controller)


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = payload.get("tool_name", "")
    destructive = ("remove_bay", "remove_zone", "remove_aperture",
                   "template_load", "load_snapshot")
    short_name = tool_name.split("__")[-1] if "__" in tool_name else tool_name
    if short_name not in destructive:
        return

    try:
        import datetime
        import controller_cli as cli
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        snap_name = f"auto-before-{short_name}-{ts}"
        state = cli.load_state(_state_path)
        cli._snapshot_save(_state_path, state, snap_name)
    except Exception:
        pass


if __name__ == "__main__":
    main()
