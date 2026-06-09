"""Text export: the describe() prose, written to a file."""

from jig.describe import describe
from jig.model.io import atomic_write


def export_text(state, path):
    atomic_write(path, describe(state) + "\n")
    return path
