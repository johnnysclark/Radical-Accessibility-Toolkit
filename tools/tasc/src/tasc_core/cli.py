"""TASC CLI — Tactile Architecture Scripting Console.

Click-based CLI with DefaultGroup routing to 'run'.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from tasc_core import __version__
from tasc_core.core.feedback import (
    bay_placed,
    bay_updated,
    corridor_updated,
    describe_model,
    grid_applied,
    label_set,
    list_zones,
    site_created,
    void_updated,
    warning_message,
    zone_not_found,
    zone_placed,
    zone_removed,
)
from tasc_core.core.model import (
    Bay,
    BayVoid,
    Corridor,
    Grid,
    Site,
    TASCModel,
    Zone,
    clear_undo,
    pop_undo,
    push_undo,
)
from tasc_core.core.validation import validate_site

STATE_FILE = ".tasc_state.json"


class DefaultGroup(click.Group):
    """Click group that defaults to 'run' when first arg is a file path."""

    def parse_args(self, ctx, args):
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            args.insert(0, "run")
        return super().parse_args(ctx, args)


def _load_state() -> TASCModel:
    """Load model state from working directory."""
    path = Path(STATE_FILE)
    if path.exists():
        return TASCModel.load(path)
    return TASCModel()


def _save_state(model: TASCModel) -> None:
    """Save model state to working directory."""
    model.save(Path(STATE_FILE))


def _output(message: str) -> None:
    """Print screen-reader-friendly output."""
    click.echo(message)


def _get_connector():
    """Get a Rhino connector and drawer."""
    from tasc_core.rhino.commands import RhinoDrawer
    from tasc_core.rhino.connector import RhinoConnector

    connector = RhinoConnector()
    mode = connector.connect()
    drawer = RhinoDrawer(connector)
    return connector, drawer, mode


@click.group(cls=DefaultGroup)
@click.version_option(version=__version__, prog_name="tasc")
def main():
    """TASC - Tactile Architecture Scripting Console.

    Accessible programmatic Rhino design for tactile architecture.

    Run a script:  tasc my_site.py
    Quick site:    tasc site 200 150
    Place zone:    tasc zone living 50 40 --at 10,10
    Describe:      tasc describe
    Export:        tasc export piaf
    """
    pass


@main.command(name="run")
@click.argument("script", type=click.Path(exists=True))
@click.option("--no-rhino", is_flag=True, help="Run in offline mode (no Rhino connection)")
def run_script(script, no_rhino):
    """Execute a TASC Python DSL script."""
    import tasc_core.dsl.api as api

    if no_rhino:
        api._auto_connect = False

    script_path = Path(script).resolve()
    _output(f"Running {script_path.name}")

    try:
        with open(script_path) as f:
            code = f.read()
        exec(compile(code, str(script_path), "exec"), {"__name__": "__main__", "__file__": str(script_path)})
    except Exception as e:
        _output(f"Error: {e}")
        sys.exit(1)


@main.command(name="site")
@click.argument("width", type=float)
@click.argument("depth", type=float)
@click.option("--units", type=click.Choice(["feet", "meters"]), default="feet", help="Unit system")
def site_cmd(width, depth, units):
    """Define a rectangular site boundary."""
    model = _load_state()
    push_undo(model, Path(STATE_FILE))
    site = Site.rectangle(width, depth, units=units)

    warnings = validate_site(site)
    for w in warnings:
        _output(warning_message(w))

    model.site = site
    _save_state(model)
    _output(site_created(site))

    # Try to draw in Rhino
    try:
        connector, drawer, mode = _get_connector()
        if connector.is_live:
            drawer.setup_layers()
            drawer.draw_site(site)
            _output(f"Drawn in Rhino ({mode})")
    except Exception:
        pass


@main.command(name="grid")
@click.argument("spacing", type=float)
@click.option("--rotation", type=float, default=0.0, help="Grid rotation in degrees")
def grid_cmd(spacing, rotation):
    """Apply a structural grid to the current site."""
    model = _load_state()
    push_undo(model, Path(STATE_FILE))
    g = Grid(spacing=spacing, rotation=rotation)
    model.grid = g
    _save_state(model)

    if model.site:
        _output(grid_applied(g, model.site))
        try:
            connector, drawer, mode = _get_connector()
            if connector.is_live:
                drawer.setup_layers()
                drawer.draw_grid(g, model.site)
        except Exception:
            pass
    else:
        _output(f"Grid set: {spacing} spacing. Define a site first for dimensions.")


@main.command(name="zone")
@click.argument("name")
@click.argument("width", type=float, required=False)
@click.argument("depth", type=float, required=False)
@click.option("--at", "position", type=str, default=None, help="Position as X,Y (e.g. 10,20)")
@click.option("--corners", type=str, default=None, help="Corner list as X1,Y1 X2,Y2 X3,Y3 X4,Y4")
@click.option("--type", "program_type", type=str, default="", help="Program type label")
def zone_cmd(name, width, depth, position, corners, program_type):
    """Place a zone in the site."""
    model = _load_state()
    push_undo(model, Path(STATE_FILE))

    if corners:
        # Parse corner string: "0,0 20,0 20,15 0,15"
        corner_list = []
        for pair in corners.split():
            parts = pair.split(",")
            corner_list.append((float(parts[0]), float(parts[1])))
        z = Zone(name=name, corners=corner_list, program_type=program_type)
    elif width is not None and depth is not None:
        at = (0.0, 0.0)
        if position:
            parts = position.split(",")
            at = (float(parts[0]), float(parts[1]))
        z = Zone.rectangle(name, width, depth, at=at, program_type=program_type)
    else:
        _output("Error: provide width and depth, or --corners")
        sys.exit(1)

    warnings = model.add_zone(z)
    _save_state(model)
    _output(zone_placed(z, model.site))
    for w in warnings:
        _output(warning_message(w))

    try:
        connector, drawer, mode = _get_connector()
        if connector.is_live:
            drawer.setup_layers()
            drawer.draw_zone(z)
    except Exception:
        pass


@main.command(name="remove")
@click.argument("name")
def remove_cmd(name):
    """Remove a zone or bay by name."""
    model = _load_state()
    push_undo(model, Path(STATE_FILE))
    if model.remove_bay(name):
        _save_state(model)
        _output(f"Bay {name} removed.")
        try:
            connector, drawer, _ = _get_connector()
            if connector.is_live:
                drawer.redraw(model)
        except Exception:
            pass
    elif model.remove_zone(name):
        _save_state(model)
        _output(zone_removed(name))
        try:
            connector, drawer, _ = _get_connector()
            if connector.is_live:
                drawer.redraw(model)
        except Exception:
            pass
    else:
        _output(zone_not_found(name))


@main.command(name="list")
def list_cmd():
    """List current model state."""
    model = _load_state()
    _output(list_zones(model))


@main.command(name="describe")
def describe_cmd():
    """Full text description with dimensions."""
    model = _load_state()
    _output(describe_model(model))


@main.command(name="export")
@click.argument("format", type=click.Choice(["piaf", "3dm", "text"]))
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file path")
def export_cmd(format, output):
    """Export model to PIAF PDF, .3dm, or text."""
    from tasc_core.core.exporter import export_3dm, export_piaf, export_text

    model = _load_state()

    if not model.site:
        _output("Error: no site boundary defined. Use 'tasc site' first.")
        sys.exit(1)

    if output is None:
        ext = {"piaf": ".pdf", "3dm": ".3dm", "text": ".txt"}
        output = f"tasc_output{ext.get(format, '.pdf')}"

    output_path = Path(output)

    try:
        if format == "piaf":
            result = export_piaf(model, output_path)
        elif format == "3dm":
            result = export_3dm(model, output_path)
        elif format == "text":
            result = export_text(model, output_path)
        _output(f"Exported to {result}")
    except Exception as e:
        _output(f"Export error: {e}")
        sys.exit(1)


@main.command(name="undo")
def undo_cmd():
    """Undo last operation."""
    restored = pop_undo(Path(STATE_FILE))
    if restored:
        _save_state(restored)
        _output("Undo: restored previous state.")
        _output(list_zones(restored))
        try:
            connector, drawer, _ = _get_connector()
            if connector.is_live:
                drawer.redraw(restored)
        except Exception:
            pass
    else:
        _output("Nothing to undo.")


@main.command(name="connect")
@click.option("--host", default="127.0.0.1", help="RhinoMCP host")
@click.option("--port", default=1999, type=int, help="RhinoMCP port")
def connect_cmd(host, port):
    """Test Rhino connection and set LightPen display mode."""
    from tasc_core.rhino.commands import RhinoDrawer
    from tasc_core.rhino.connector import RhinoConnector

    connector = RhinoConnector(host=host, port=port)
    mode = connector.connect()

    if mode == "mcp":
        _output(f"Connected to Rhino via MCP socket at {connector.host}:{port}")
        drawer = RhinoDrawer(connector)
        drawer.set_display_mode("LightPen")
        _output("Display mode set to LightPen.")
    elif mode == "rhinocode":
        _output("Connected to Rhino via RhinoCode CLI")
    else:
        _output("Offline mode. No Rhino connection available.")
        _output("Start Rhino with RhinoMCP plugin, or install rhinocode CLI.")


@main.command(name="display")
@click.argument("mode", required=False)
def display_cmd(mode):
    """Get or set viewport display mode. Without argument, shows current mode."""
    try:
        connector, drawer, conn_mode = _get_connector()
    except Exception:
        _output("Cannot connect to Rhino.")
        return

    if not connector.is_live:
        _output("Not connected to Rhino.")
        return

    if not mode:
        # Query current mode
        from tasc_core.rhino.protocol import execute_script_cmd
        script = (
            "import rhinoscriptsyntax as rs\n"
            "print(rs.ViewDisplayMode())\n"
        )
        try:
            result = connector.send("execute_rhinoscript_python_code", {"code": script})
            current = result.get("output", "unknown").strip()
            _output(f"Current display mode: {current}")
        except Exception:
            _output("Could not query display mode.")
        return

    result = drawer.set_display_mode(mode)
    if result and "Switched" in result:
        _output(f"Display mode set to {mode}.")
    elif result and "not found" in result:
        _output(result.strip())
    else:
        _output(f"Attempted to set display mode to {mode}.")


@main.command(name="capture")
@click.argument("output", required=False, default=None)
@click.option("--viewport", default="Top", help="Viewport to capture (Top, Front, Right, Perspective)")
@click.option("--paper", default="letter", type=click.Choice(["letter", "tabloid"]), help="Paper size for output dimensions")
def capture_cmd(output, viewport, paper):
    """Capture viewport as TACT-ready image (white bg, black lines).

    Temporarily switches to Pen mode for capture, then restores LightPen.
    Output is a PNG suitable for direct TACT conversion.
    """
    if paper == "tabloid":
        w, h = 3300, 5100
    else:
        w, h = 2550, 3300

    if not output:
        output = f"capture_{viewport.lower()}.png"

    try:
        connector, drawer, mode = _get_connector()
    except Exception:
        _output("Cannot connect to Rhino.")
        return

    if not connector.is_live:
        _output("Not connected to Rhino.")
        return

    _output(f"Capturing {viewport} viewport to {output}...")
    result = drawer.capture_for_tact(output, viewport=viewport, width=w, height=h)
    if result:
        _output(f"Saved: {result}")
        _output("Image has white background, black lines. Ready for tact convert.")
    else:
        _output("Capture failed. Check Rhino viewport is visible.")


@main.command(name="reset")
def reset_cmd():
    """Clear all model state."""
    path = Path(STATE_FILE)
    if path.exists():
        path.unlink()
    clear_undo(path)
    _output("Model state cleared.")

    try:
        connector, drawer, _ = _get_connector()
        if connector.is_live:
            drawer.clear_all()
            _output("Rhino objects cleared.")
    except Exception:
        pass


@main.command(name="bay")
@click.argument("name")
@click.argument("dims", required=False, default=None)
@click.option("--spacing", nargs=2, type=float, default=None, help="Bay spacing SX SY")
@click.option("--spacing-x", type=str, default=None, help="Irregular x spacing (comma-separated)")
@click.option("--spacing-y", type=str, default=None, help="Irregular y spacing (comma-separated)")
@click.option("--at", "position", type=str, default=None, help="Position as X,Y")
@click.option("--rotation", type=float, default=None, help="Rotation in degrees")
@click.option("--column-size", type=float, default=None, help="Column size in feet")
def bay_cmd(name, dims, spacing, spacing_x, spacing_y, position, rotation, column_size):
    """Create or update a structural bay."""
    model = _load_state()
    push_undo(model, Path(STATE_FILE))

    existing = model.get_bay(name)
    if existing:
        # Update mode: merge specified fields
        if dims:
            parts = dims.lower().split("x")
            old_grid = existing.grid
            existing.grid = (int(parts[0]), int(parts[1]))
            _output(bay_updated(existing, "grid", f"{old_grid[0]}x{old_grid[1]}", dims))
        if spacing:
            old_sp = existing.spacing
            existing.spacing = (spacing[0], spacing[1])
            _output(bay_updated(existing, "spacing", f"{old_sp[0]}x{old_sp[1]}", f"{spacing[0]}x{spacing[1]}"))
        if spacing_x:
            existing.spacing_x = [float(v) for v in spacing_x.split(",")]
        if spacing_y:
            existing.spacing_y = [float(v) for v in spacing_y.split(",")]
        if position:
            parts = position.split(",")
            old_origin = existing.origin
            existing.origin = (float(parts[0]), float(parts[1]))
            _output(bay_updated(existing, "origin", f"{old_origin[0]},{old_origin[1]}", position))
        if rotation is not None:
            old_rot = existing.rotation
            existing.rotation = rotation
            _output(bay_updated(existing, "rotation", old_rot, rotation))
        if column_size is not None:
            old_cs = existing.column_size
            existing.column_size = column_size
            _output(bay_updated(existing, "column_size", old_cs, column_size))
        model.add_bay(existing)
        _save_state(model)
    else:
        # Create mode
        grid = (1, 1)
        if dims:
            parts = dims.lower().split("x")
            grid = (int(parts[0]), int(parts[1]))
        sp = (24.0, 24.0)
        if spacing:
            sp = (spacing[0], spacing[1])
        origin = (0.0, 0.0)
        if position:
            parts = position.split(",")
            origin = (float(parts[0]), float(parts[1]))
        bay = Bay(
            name=name,
            origin=origin,
            rotation=rotation or 0.0,
            grid=grid,
            spacing=sp,
            spacing_x=[float(v) for v in spacing_x.split(",")] if spacing_x else None,
            spacing_y=[float(v) for v in spacing_y.split(",")] if spacing_y else None,
            column_size=column_size or 1.5,
        )
        model.add_bay(bay)
        _save_state(model)
        _output(bay_placed(bay, model.site))

    try:
        connector, drawer, mode = _get_connector()
        if connector.is_live:
            drawer.redraw(model)
    except Exception:
        pass


@main.command(name="corridor")
@click.argument("bay_name")
@click.argument("toggle", required=False, default=None, type=click.Choice(["on", "off"]))
@click.option("--axis", type=click.Choice(["x", "y"]), default=None, help="Corridor axis")
@click.option("--width", type=float, default=None, help="Corridor width in feet")
@click.option("--loading", type=click.Choice(["single", "double"]), default=None, help="Loading type")
@click.option("--position", type=int, default=None, help="Gridline index")
def corridor_cmd(bay_name, toggle, axis, width, loading, position):
    """Add or modify a corridor on a bay."""
    model = _load_state()
    bay = model.get_bay(bay_name)
    if not bay:
        _output(f"Bay {bay_name} not found.")
        return

    push_undo(model, Path(STATE_FILE))

    if toggle == "off":
        if bay.corridor:
            bay.corridor.enabled = False
        else:
            bay.corridor = Corridor(enabled=False)
    else:
        if bay.corridor is None:
            bay.corridor = Corridor(enabled=True)
        if toggle == "on":
            bay.corridor.enabled = True
        if axis is not None:
            bay.corridor.axis = axis
        if width is not None:
            bay.corridor.width = width
        if loading is not None:
            bay.corridor.loading = loading
        if position is not None:
            bay.corridor.position = position

    model.add_bay(bay)
    _save_state(model)
    _output(corridor_updated(bay_name, bay.corridor))

    try:
        connector, drawer, _ = _get_connector()
        if connector.is_live:
            drawer.redraw(model)
    except Exception:
        pass


@main.command(name="void")
@click.argument("bay_name")
@click.argument("shape", required=False, default=None)
@click.argument("size_str", required=False, default=None)
@click.option("--at", "position", type=str, default=None, help="Center position as X,Y")
def void_cmd(bay_name, shape, size_str, position):
    """Add or modify a void in a bay."""
    model = _load_state()
    bay = model.get_bay(bay_name)
    if not bay:
        _output(f"Bay {bay_name} not found.")
        return

    push_undo(model, Path(STATE_FILE))

    if shape and shape.lower() == "off":
        bay.void = None
        model.add_bay(bay)
        _save_state(model)
        _output(void_updated(bay_name, None))
    else:
        center = (0.0, 0.0)
        if position:
            parts = position.split(",")
            center = (float(parts[0]), float(parts[1]))
        elif bay.void:
            center = bay.void.center

        if shape and shape.lower() == "circle":
            diameter = float(size_str) if size_str else 20.0
            bay.void = BayVoid(center=center, size=(diameter, diameter), shape="circle")
        else:
            size = (20.0, 20.0)
            if size_str and "x" in size_str.lower():
                parts = size_str.lower().split("x")
                size = (float(parts[0]), float(parts[1]))
            elif size_str:
                s = float(size_str)
                size = (s, s)
            bay.void = BayVoid(center=center, size=size, shape=shape or "rectangle")

        model.add_bay(bay)
        _save_state(model)
        _output(void_updated(bay_name, bay.void))

    try:
        connector, drawer, _ = _get_connector()
        if connector.is_live:
            drawer.redraw(model)
    except Exception:
        pass


@main.command(name="label")
@click.argument("name")
@click.argument("text")
@click.option("--braille", type=str, default="", help="Braille unicode text")
def label_cmd(name, text, braille):
    """Set a label on a bay or zone."""
    model = _load_state()
    push_undo(model, Path(STATE_FILE))

    bay = model.get_bay(name)
    if bay:
        bay.label = text
        bay.braille = braille
        model.add_bay(bay)
        _save_state(model)
        _output(label_set(name, text, braille))
    else:
        zone = model.get_zone(name)
        if zone:
            zone.label = text
            zone.braille = braille
            _save_state(model)
            _output(label_set(name, text, braille))
        else:
            _output(f"{name} not found in bays or zones.")

    try:
        connector, drawer, _ = _get_connector()
        if connector.is_live:
            drawer.redraw(model)
    except Exception:
        pass


@main.command(name="version")
def version_cmd():
    """Show version information."""
    _output(f"TASC - Tactile Architecture Scripting Console v{__version__}")
    _output("Part of the Radical Accessibility Project at UIUC")


if __name__ == "__main__":
    main()
