#!/usr/bin/env python3
"""PostToolUse hook: log MCP tool calls to sessions/changes.jsonl."""

import json
import os
import sys
import time


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool = payload.get("tool_name", "")
    if not tool.startswith("mcp__rhino"):
        return

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(root, "sessions", "changes.jsonl")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tool": tool,
        "input": payload.get("tool_input", {}),
    }
    output = payload.get("tool_output", "")
    if output:
        first_line = output.split("\n")[0][:120]
        entry["result"] = first_line

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")
    except OSError:
        pass


if __name__ == "__main__":
    main()
