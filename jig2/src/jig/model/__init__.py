"""Semantic model: dataclasses, validation, migration, persistence.

Zero external dependencies. This subpackage is copied into the Rhino
watcher bundle and must run on Rhino 8's embedded CPython unchanged.
"""

from jig.model.schema import (  # noqa: F401
    Aperture,
    Bay,
    Cell,
    Corridor,
    Grid,
    Meta,
    Site,
    State,
    Void,
    Walls,
    Zone,
)
from jig.model.io import load_state, save_state, atomic_write, mint_id  # noqa: F401
