#!/usr/bin/env python3
"""PostToolUse hook: log state-modifying MCP calls to changes.jsonl."""

import datetime
import json
import os
import sys


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    tool_output = payload.get("tool_output", "")

    summary = ""
    if isinstance(tool_output, str):
        for line in tool_output.split("\n"):
            if line.startswith("OK:") or line.startswith("ERROR:"):
                summary = line.strip()
                break
        if not summary:
            summary = tool_output[:200].strip()

    entry = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "tool": tool_name,
        "input": tool_input,
        "summary": summary,
    }

    _root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    changes_path = os.path.join(_root, "controller", "changes.jsonl")

    try:
        line = json.dumps(entry, separators=(",", ":"))
        with open(changes_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


if __name__ == "__main__":
    main()
