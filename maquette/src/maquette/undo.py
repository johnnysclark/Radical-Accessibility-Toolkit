"""Undo target selection.

Undo appends compensating ops; it never rewrites history. The walker
finds the most recent entry that is not itself a compensator, has not
already been compensated, and is undoable at all.
"""

from __future__ import annotations

from maquette import ops


def pick_undo_target(entries: list[dict]) -> dict | None:
    compensated = {e["undo_of"] for e in entries if e.get("undo_of")}
    for entry in reversed(entries):
        if entry["op"] in ops.NO_UNDO_OPS:
            continue
        if entry.get("undo_of"):
            continue
        if entry["seq"] in compensated:
            continue
        return entry
    return None
