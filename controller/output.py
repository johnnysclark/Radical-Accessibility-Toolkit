# -*- coding: utf-8 -*-
"""
Screen-reader output formatting for the Layout Jig.

CLAUDE.md fixes the output contract for every CLI response:

  OK: ...         prefix for successful commands
  ERROR: ...      prefix for errors
  READY:          trailing marker so the screen reader detects the
                  end of the response and can re-focus the cursor

Before this module, each handler hand-prefixed its own messages (or
didn't), and the REPL printed raw "Error: ..." text that violated the
contract. The helpers here own the normalization so every interface --
REPL, MCP server, script runner -- produces the same shape.

stdlib only.
"""

__all__ = ["format_ok", "format_error", "STATUS_PREFIXES", "READY"]

STATUS_PREFIXES = ("OK:", "ERROR:", "CHANGED:", "WARNING:")
READY = "READY:"


def format_ok(message):
    """Normalize a successful command's output.

    - Adds an `OK: ` prefix if no status prefix is already present.
    - Appends a `READY:` line if the message doesn't already end with
      one (multi-line outputs like `describe` add their own).
    - Empty or whitespace-only messages come back empty so the REPL
      can skip them silently.
    """
    s = (message or "").rstrip()
    if not s:
        return ""
    if not any(s.startswith(p) for p in STATUS_PREFIXES):
        s = "OK: " + s
    if not s.rstrip().endswith(READY):
        s = s + "\n" + READY
    return s


def format_error(message):
    """Normalize an error message: `ERROR: ...` plus trailing `READY:`."""
    s = str(message).strip()
    return "ERROR: " + s + "\n" + READY
