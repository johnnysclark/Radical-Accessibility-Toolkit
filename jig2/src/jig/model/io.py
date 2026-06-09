"""Persistence: atomic writes, load with migration, stable ID minting."""

import json
import os
import re

from jig.model.schema import SCHEMA_VERSION, State, now_stamp
from jig.model import migrate


def atomic_write(path, text):
    """Write text to path via tmp file + fsync + os.replace. Crash-safe."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def save_state(state, path):
    state.meta.modified = now_stamp()
    atomic_write(path, json.dumps(state.to_dict(), indent=2) + "\n")


def load_state(path):
    """Load a state file, migrating older schemas in memory."""
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    schema = raw.get("schema", "")
    if schema != SCHEMA_VERSION:
        raw = migrate.migrate(raw)
    return State.from_dict(raw)


def load_or_new(path):
    if os.path.exists(path):
        return load_state(path)
    return State.new()


def mint_id(prefix, existing_ids):
    """Mint the next stable id for a prefix: z01, z02 ... never reused."""
    pattern = re.compile(r"^" + re.escape(prefix) + r"(\d+)$")
    top = 0
    for eid in existing_ids:
        m = pattern.match(eid)
        if m:
            top = max(top, int(m.group(1)))
    return "{}{:02d}".format(prefix, top + 1)
