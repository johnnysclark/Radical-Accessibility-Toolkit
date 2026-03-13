"""Screen-reader friendly logging.

All output uses OK:/ERROR:/READY: prefixes for quick parsing.
No spinners, no progress bars, no animations.
"""


def info(message):
    """Print an informational message."""
    print(f"OK: {message}")


def error(message):
    """Print an error message."""
    print(f"ERROR: {message}")


def ready(message=""):
    """Print a ready indicator."""
    if message:
        print(f"READY: {message}")
    else:
        print("READY:")
