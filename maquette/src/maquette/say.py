"""Output contract for screen readers.

Every status line is prefixed OK:, ERROR:, or WARNING: so a screen
reader user can parse outcomes instantly. Detail lines are short,
labeled, one fact per line. No tables, no box drawing, no spinners,
no streaming. Commands end with READY: so the state change is audible.
"""

from __future__ import annotations

PAGE_LIMIT = 20


def ok(message: str) -> str:
    line = "OK: " + message
    print(line)
    return line


def err(message: str) -> str:
    # Errors go to stdout: screen readers follow one stream, and the
    # ERROR: prefix plus the exit code carry the failure signal.
    line = "ERROR: " + message
    print(line)
    return line


def warn(message: str) -> str:
    line = "WARNING: " + message
    print(line)
    return line


def info(message: str) -> str:
    """A plain detail line under an OK:/ERROR: heading."""
    print(message)
    return message


def ready() -> str:
    print("READY:")
    return "READY:"


def page(lines: list[str], show_all: bool = False, ask=None) -> list[str]:
    """Print lines with a screen-reader-friendly cap.

    Beyond PAGE_LIMIT lines, stop and either announce how to get the
    rest (CLI) or call ask() -> bool to continue (interactive REPL).
    Returns the lines actually printed.
    """
    if show_all or len(lines) <= PAGE_LIMIT:
        for line in lines:
            print(line)
        return lines
    head = lines[: PAGE_LIMIT - 2]
    for line in head:
        print(line)
    remaining = len(lines) - len(head)
    if ask is None:
        print("MORE: {0} more lines. Add --all to hear everything.".format(remaining))
        return head
    print("MORE: {0} more lines.".format(remaining))
    if ask("more? answer yes or no."):
        for line in lines[len(head):]:
            print(line)
        return lines
    return head
