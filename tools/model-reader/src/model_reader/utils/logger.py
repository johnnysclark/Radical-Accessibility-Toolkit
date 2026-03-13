"""Screen-reader-friendly output helpers.

All output follows CLAUDE.md rules:
- OK: prefix for success
- ERROR: prefix for errors
- READY: suffix after command completes
- Short labeled lines, no tables, no ASCII art
"""


def ok(message):
    """Print a success message."""
    print(f"OK: {message}")


def error(message):
    """Print an error message."""
    print(f"ERROR: {message}")


def ready():
    """Print the ready signal for screen reader detection."""
    print("READY:")


def info(message):
    """Print an informational line (no prefix)."""
    print(message)


def numbered_list(items, label_fn=str):
    """Print a numbered list of items, screen-reader friendly.

    Args:
        items: Iterable of items to list.
        label_fn: Function that converts each item to a display string.
    """
    for i, item in enumerate(items, 1):
        print(f"{i}. {label_fn(item)}")
