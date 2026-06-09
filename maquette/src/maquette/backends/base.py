"""Backend contract.

A backend realizes journal entries somewhere: nowhere (record), in a
.3dm file (headless), or in a running Rhino (live). Backends never
touch the journal; the engine owns persistence.
"""

from __future__ import annotations


class BackendError(Exception):
    pass


class BackendAPI:
    """One method matters: apply(entry, scene) -> result dict.

    The result is stored in the journal entry for audit and drift
    detection: {"backend": name, "status": "applied"|"recorded",
    "fingerprint": {...}|None, "output": str}.
    "applied" means real geometry exists; "recorded" means the op is
    journaled intent awaiting a more capable backend.
    """

    name = "base"

    def apply(self, entry: dict, scene) -> dict:
        raise NotImplementedError

    def begin_rebuild(self) -> None:
        """Clear backend state before a journal replay."""

    def finish_rebuild(self) -> dict:
        """Return {object_id: fingerprint} for everything realized."""
        return {}

    def close(self) -> None:
        pass


def recorded(name: str, note: str = "") -> dict:
    return {"backend": name, "status": "recorded", "fingerprint": None,
            "output": note}
