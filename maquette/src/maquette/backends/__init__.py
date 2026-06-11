"""Backend selection.

"auto" prefers live Rhino, then headless rhino3dm, then record —
and always says out loud which one it picked when it is not live,
because silent downgrades are inaccessible.
"""

from __future__ import annotations

import socket

from maquette.backends.base import BackendAPI, BackendError
from maquette.backends.record import RecordBackend

BACKEND_NAMES = ("record", "headless", "live", "auto")


def headless_available() -> bool:
    try:
        import rhino3dm  # noqa: F401
        return True
    except ImportError:
        return False


def listener_reachable(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def make_backend(name: str, project) -> BackendAPI:
    if name == "record":
        return RecordBackend()
    if name == "headless":
        from maquette.backends.headless import HeadlessBackend
        return HeadlessBackend(project)
    if name == "live":
        from maquette.backends.live import LiveBackend
        return LiveBackend(project)
    raise BackendError("unknown backend {0!r}".format(name))


def choose_backend(project, requested: str = "auto") -> tuple[BackendAPI, str]:
    """Return (backend, note). The note explains any downgrade; empty
    when the user got exactly what they asked for."""
    if requested != "auto":
        return make_backend(requested, project), ""
    host, port = project.listener_address
    if listener_reachable(host, port):
        return make_backend("live", project), ""
    if headless_available():
        return (make_backend("headless", project),
                "Rhino is not connected. Building the 3dm file directly "
                "(backend headless).")
    return (make_backend("record", project),
            "Rhino is not connected and rhino3dm is not installed. "
            "Recording intent only (backend record).")
