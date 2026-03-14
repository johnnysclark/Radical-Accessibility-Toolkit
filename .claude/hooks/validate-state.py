#!/usr/bin/env python3
"""Hook: Validate state.json schema after writes.

Called by PostToolUse hook when state.json is written.
Exit 0 = OK, Exit 2 = block with warning on stderr.
"""
import json
import sys


def validate_state(state):
    """Validate state.json structure. Returns list of issues."""
    issues = []

    # Top-level required keys
    if "schema" not in state:
        issues.append("Missing top-level 'schema' key")
    if "meta" not in state:
        issues.append("Missing top-level 'meta' key")

    # Required collections
    required_collections = [
        "bays", "corridors", "rooms", "walls",
        "apertures", "hatches", "legend", "section_cuts", "snapshots"
    ]
    for coll in required_collections:
        if coll not in state:
            issues.append("Missing collection: '{}'".format(coll))

    # Check for duplicate IDs within collections
    for coll_name in required_collections:
        coll = state.get(coll_name)
        if coll is None:
            continue
        # Handle both list and dict collections
        items = []
        if isinstance(coll, list):
            items = coll
        elif isinstance(coll, dict):
            items = list(coll.values()) if coll else []
        else:
            continue

        seen_ids = set()
        for item in items:
            if not isinstance(item, dict):
                continue
            item_id = item.get("id")
            if item_id is not None:
                if item_id in seen_ids:
                    issues.append("Duplicate ID '{}' in collection '{}'".format(
                        item_id, coll_name))
                seen_ids.add(item_id)

    # Check for camelCase keys (should be snake_case)
    def check_keys(obj, path=""):
        if isinstance(obj, dict):
            for key in obj:
                # Simple camelCase detection: lowercase start + uppercase letter
                if any(c.isupper() for c in key[1:]) and key[0].islower() and "_" not in key:
                    issues.append("camelCase key '{}' at {} (use snake_case)".format(
                        key, path or "root"))
                check_keys(obj[key], "{}.{}".format(path, key) if path else key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_keys(item, "{}[{}]".format(path, i))

    check_keys(state)

    return issues


def main():
    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = hook_input.get("tool_input", {}).get("file_path", "")

    # Only validate state.json files
    if not file_path.endswith("state.json"):
        sys.exit(0)

    try:
        with open(file_path, "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        sys.exit(0)
    except json.JSONDecodeError as e:
        print("state.json is not valid JSON: {}".format(e), file=sys.stderr)
        sys.exit(2)

    issues = validate_state(state)

    if issues:
        msg = "state.json validation failed ({} issues):\n".format(len(issues))
        for i, issue in enumerate(issues, 1):
            msg += "{}. {}\n".format(i, issue)
        print(msg, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
