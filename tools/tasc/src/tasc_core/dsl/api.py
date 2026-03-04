"""Python DSL for TASC: module-level functions for scripting site layouts.

Usage in a script::

    from tasc_core.dsl.api import *

    boundary(200, 150, units="feet")
    grid(10)
    zone("living", 50, 40, at=(10, 10))
    describe()
    export("piaf")
"""

from __future__ import annotations

from pathlib import Path

from tasc_core.core.feedback import (
    describe_model,
    grid_applied,
    list_zones,
    site_created,
    warning_message,
    zone_not_found,
    zone_placed,
    zone_removed,
)
from tasc_core.core.model import Grid, Site, TASCModel, Zone
from tasc_core.rhino.commands import RhinoDrawer
from tasc_core.rhino.connector import RhinoConnector

# Global state
_model = TASCModel()
_connector: RhinoConnector | None = None
_drawer: RhinoDrawer | None = None
_auto_connect: bool = True


def _get_connector() -> RhinoConnector:
    """Get or create the Rhino connector (auto-connect on first use)."""
    global _connector, _drawer
    if _connector is None and _auto_connect:
        _connector = RhinoConnector()
        mode = _connector.connect()
        _drawer = RhinoDrawer(_connector)
        _drawer.setup_layers()
        print(f"Rhino connection: {mode}")
    if _connector is None:
        _connector = RhinoConnector()
        _connector.mode = "offline"
        _drawer = RhinoDrawer(_connector)
    return _connector


def _get_drawer() -> RhinoDrawer:
    """Get the drawer, ensuring connector exists."""
    global _drawer
    _get_connector()
    assert _drawer is not None
    return _drawer


def _print(msg: str) -> None:
    """Print feedback to stdout."""
    print(msg, flush=True)


def boundary(width=None, depth=None, *, corners=None, units="feet") -> Site:
    """Define site boundary.

    Args:
        width: Site width (for rectangle).
        depth: Site depth (for rectangle).
        corners: List of (x, y) tuples for polygon boundary.
        units: "feet" or "meters".

    Returns:
        The created Site object.
    """
    global _model

    if corners is not None:
        site = Site(corners=[tuple(c) for c in corners], units=units)
    elif width is not None and depth is not None:
        site = Site.rectangle(float(width), float(depth), units=units)
    else:
        raise ValueError("Provide either width+depth or corners")

    from tasc_core.core.validation import validate_site

    warnings = validate_site(site)
    for w in warnings:
        _print(warning_message(w))

    _model.site = site
    _print(site_created(site))

    drawer = _get_drawer()
    drawer.draw_site(site)

    return site


def grid(spacing, rotation=0, origin=(0, 0)) -> Grid:
    """Set up site grid."""
    global _model

    g = Grid(spacing=float(spacing), rotation=float(rotation), origin=tuple(origin))
    _model.grid = g

    if _model.site:
        _print(grid_applied(g, _model.site))
        drawer = _get_drawer()
        drawer.draw_grid(g, _model.site)
    else:
        _print(f"Grid set: {spacing} spacing. Define a site boundary to see grid dimensions.")

    return g


def zone(name, width=None, depth=None, *, at=None, corners=None, program_type="") -> Zone:
    """Place a zone.

    Args:
        name: Zone name.
        width: Zone width (for rectangle).
        depth: Zone depth (for rectangle).
        at: (x, y) position for rectangle placement.
        corners: List of (x, y) tuples for polygon zone.
        program_type: Optional program type label.

    Returns:
        The created Zone object.
    """
    global _model

    if corners is not None:
        z = Zone(name=name, corners=[tuple(c) for c in corners], program_type=program_type)
    elif width is not None and depth is not None:
        pos = at if at is not None else (0, 0)
        z = Zone.rectangle(name, float(width), float(depth), at=tuple(pos), program_type=program_type)
    else:
        raise ValueError("Provide either width+depth+at or corners")

    warnings = _model.add_zone(z)
    _print(zone_placed(z, _model.site))
    for w in warnings:
        _print(warning_message(w))

    drawer = _get_drawer()
    drawer.draw_zone(z)

    return z


def remove(name: str) -> str:
    """Remove a zone by name."""
    global _model

    if _model.remove_zone(name):
        msg = zone_removed(name)
        _print(msg)
        # Redraw to remove from Rhino
        drawer = _get_drawer()
        drawer.redraw(_model)
        return msg
    else:
        msg = zone_not_found(name)
        _print(msg)
        return msg


def describe() -> str:
    """Print full model description with dimensions."""
    text = describe_model(_model)
    _print(text)
    return text


def list_model() -> str:
    """Print short model listing."""
    text = list_zones(_model)
    _print(text)
    return text


def export(format="piaf", output=None) -> str:
    """Export model.

    Args:
        format: 'piaf', '3dm', or 'text'.
        output: Output file path. Auto-generated if not provided.

    Returns:
        Output file path.
    """
    from tasc_core.core.exporter import export_3dm, export_piaf, export_text

    if output is None:
        ext = {"piaf": ".pdf", "3dm": ".3dm", "text": ".txt"}
        output = f"tasc_output{ext.get(format, '.pdf')}"

    output_path = Path(output)

    if format == "piaf":
        result = export_piaf(_model, output_path)
    elif format == "3dm":
        result = export_3dm(_model, output_path)
    elif format == "text":
        result = export_text(_model, output_path)
    else:
        raise ValueError(f"Unknown export format: {format}. Use 'piaf', '3dm', or 'text'.")

    _print(f"Exported to {result}")
    return result


def undo(steps=1):
    """Undo last N operations. Currently redraws the model."""
    _print(f"Undo not yet implemented for DSL scripts.")


def connect(host="127.0.0.1", port=1999) -> str:
    """Explicitly connect to Rhino."""
    global _connector, _drawer, _auto_connect
    _auto_connect = False  # Disable auto-connect since user is explicit
    _connector = RhinoConnector(host=host, port=int(port))
    mode = _connector.connect()
    _drawer = RhinoDrawer(_connector)
    _drawer.setup_layers()
    _print(f"Connected to Rhino: {mode}")
    return mode


def get_model() -> TASCModel:
    """Get the current model (for advanced use)."""
    return _model


def reset():
    """Reset the global model state."""
    global _model
    _model = TASCModel()
    drawer = _get_drawer()
    drawer.clear_all()
    _print("Model reset.")


__all__ = [
    "boundary",
    "grid",
    "zone",
    "remove",
    "describe",
    "list_model",
    "export",
    "undo",
    "connect",
    "get_model",
    "reset",
]
