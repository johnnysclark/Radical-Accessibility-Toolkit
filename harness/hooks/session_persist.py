#!/usr/bin/env python3
"""Stop hook: persist session context for clean handoffs."""

import datetime
import json
import os
import sys


def main():
    _root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    state_path = os.path.join(_root, "controller", "state.json")
    context_path = os.path.join(_root, "controller", "session-context.json")
    progress_path = os.path.join(_root, "controller", "progress.jsonl")

    try:
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, json.JSONDecodeError):
        return

    bays = state.get("bays", {})
    context = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "bay_count": len(bays),
        "bay_names": sorted(bays.keys()),
        "door_count": sum(
            len([a for a in b.get("apertures", []) if a.get("type") == "door"])
            for b in bays.values()),
        "room_count": len(state.get("rooms", {})),
        "zone_count": len(state.get("zones", {})),
        "corridors_on": sum(
            1 for b in bays.values()
            if b.get("corridor", {}).get("enabled")),
    }

    try:
        with open(progress_path, "r", encoding="utf-8") as f:
            lines = [l for l in f.read().strip().split("\n") if l.strip()]
            if lines:
                last = json.loads(lines[-1])
                context["last_milestone"] = last.get("milestone")
    except (OSError, json.JSONDecodeError):
        pass

    try:
        tmp = context_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(context, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, context_path)
    except Exception:
        pass


if __name__ == "__main__":
    main()
