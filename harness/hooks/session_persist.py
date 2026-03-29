#!/usr/bin/env python3
"""Stop hook: write session summary to sessions/last-session.json."""

import json
import os
import time


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    session_path = os.path.join(root, "sessions", "session.jsonl")
    out_path = os.path.join(root, "sessions", "last-session.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Count session log entries
    entry_count = 0
    last_entry = None
    try:
        with open(session_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entry_count += 1
                    try:
                        last_entry = json.loads(line)
                    except json.JSONDecodeError:
                        pass
    except OSError:
        pass

    summary = {
        "ended": time.strftime("%Y-%m-%d %H:%M:%S"),
        "log_entries": entry_count,
        "last_entry": last_entry.get("entry", "") if last_entry else "",
    }

    try:
        tmp = out_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, out_path)
    except OSError:
        pass


if __name__ == "__main__":
    main()
