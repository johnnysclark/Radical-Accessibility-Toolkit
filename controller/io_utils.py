# -*- coding: utf-8 -*-
"""Shared IO helpers for the controller package.

Anything in controller/ that writes to disk should go through atomic_write.
Per CLAUDE.md: "All file writes through _atomic_write(path, text) — write
.tmp, fsync, then os.replace." This module is the single home for that
pattern so callers cannot drift.
"""

import os


def atomic_write(path, text):
    """Write text to path via tmp + fsync + replace for crash safety."""
    folder = os.path.dirname(os.path.abspath(path))
    if folder:
        os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
