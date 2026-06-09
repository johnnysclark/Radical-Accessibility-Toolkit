"""Command registry population: importing this package registers every command."""

from jig.commands import (  # noqa: F401
    aperture,
    bay,
    cell,
    corridor,
    export,
    grid,
    history,
    meta,
    rhino,
    site,
    wall,
    zone,
)
from jig.commands.registry import CommandError, dispatch  # noqa: F401
from jig.commands.session import Session  # noqa: F401
