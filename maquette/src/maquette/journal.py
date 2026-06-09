"""Append-only JSONL journal: the source of truth for a project.

Each line is one self-contained op entry. Appends are flushed and
fsynced so a crash loses at most the line being written; the reader
tolerates a truncated final line (reports it, skips it). Nothing
ever rewrites earlier lines.
"""

from __future__ import annotations

import json
import os

from maquette import JOURNAL_VERSION
from maquette.project import utc_now


class JournalError(Exception):
    pass


def make_entry(seq: int, op: str, params: dict, actor: str,
               obj_id: str | None = None, name: str | None = None,
               layer: str | None = None, undo_of: int | None = None,
               result: dict | None = None) -> dict:
    return {
        "v": JOURNAL_VERSION,
        "seq": seq,
        "ts": utc_now(),
        "actor": actor,
        "op": op,
        "id": obj_id,
        "name": name,
        "layer": layer,
        "params": params,
        "undo_of": undo_of,
        "result": result or {},
    }


def append(journal_path: str, entry: dict) -> None:
    line = json.dumps(entry, separators=(",", ":"))
    with open(journal_path, "a", encoding="utf-8") as handle:
        handle.write(line + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def read_entries(journal_path: str, after_seq: int = 0):
    """Yield entries with seq greater than after_seq.

    A truncated or corrupt final line is skipped (crash tolerance);
    corruption anywhere else raises, because that means real damage.
    """
    try:
        with open(journal_path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except FileNotFoundError:
        return
    for index, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            if index == len(lines) - 1:
                # Interrupted final append; the op never finished.
                return
            raise JournalError(
                "journal line {0} is corrupt. The journal is the source of "
                "truth; restore it from backup or git.".format(index + 1))
        if entry.get("seq", 0) > after_seq:
            yield entry


def last_seq(journal_path: str) -> int:
    seq = 0
    for entry in read_entries(journal_path):
        seq = entry["seq"]
    return seq


def entry_summary(entry: dict) -> str:
    """One speakable line for journal listings."""
    parts = [str(entry["seq"]) + ":", entry["op"]]
    if entry.get("id"):
        parts.append(entry["id"])
    if entry.get("name"):
        parts.append(entry["name"])
    if entry.get("undo_of"):
        parts.append("(undo of {0})".format(entry["undo_of"]))
    intent = entry.get("params", {}).get("intent")
    if intent:
        parts.append("- " + intent)
    return " ".join(parts)
