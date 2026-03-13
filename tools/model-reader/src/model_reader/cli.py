"""Click CLI for model-reader.

All commands print OK:/ERROR: prefixed output and end with READY:.
"""

from __future__ import annotations

import os

import click

from model_reader.utils.logger import ok, error, ready, info


@click.group()
def main():
    """model-reader: Read .3dm Rhino files accessibly.

    Explore layers, list objects, and extract plans, sections,
    and elevations from .3dm files created in Rhino.
    """
    pass


def _load(file: str):
    """Load a .3dm file with error handling. Returns ModelInfo or None."""
    from model_reader.core.reader import load_3dm

    try:
        return load_3dm(file)
    except FileNotFoundError:
        error(f"File not found: {file}")
        ready()
        return None
    except ValueError as e:
        error(str(e))
        ready()
        return None


# ── Read commands ──────────────────────────────────────────────


@main.command()
@click.argument("file")
def open(file: str):
    """Load a .3dm file and print a summary."""
    model = _load(file)
    if model is None:
        return

    from model_reader.core.describer import describe_model

    info(describe_model(model))
    ready()


@main.command()
@click.argument("file")
def layers(file: str):
    """List all layers with object counts."""
    model = _load(file)
    if model is None:
        return

    from model_reader.core.describer import describe_layers

    info(describe_layers(model))
    ready()


@main.command()
@click.argument("file")
@click.option("--layer", "-l", default=None, help="Filter by layer name.")
@click.option("--type", "-t", "geo_type", default=None, help="Filter by geometry type (curve, mesh, brep).")
def objects(file: str, layer: str | None, geo_type: str | None):
    """List objects in the model."""
    model = _load(file)
    if model is None:
        return

    from model_reader.core.describer import describe_objects

    info(describe_objects(model, layer=layer, geo_type=geo_type))
    ready()


@main.command()
@click.argument("file")
@click.argument("name")
def inspect(file: str, name: str):
    """Show detailed info for a single object by name or ID."""
    model = _load(file)
    if model is None:
        return

    from model_reader.core.describer import describe_object_detail

    info(describe_object_detail(model, name))
    ready()


# ── View extraction commands ──────────────────────────────────


@main.command()
@click.argument("file")
@click.option("-o", "--output", default=None, help="Output file path (default: <file>_plan.png).")
@click.option("--piaf", is_flag=True, help="Also export PIAF tactile PDF.")
@click.option("--height", type=float, default=None, help="Only include geometry at this Z height.")
@click.option("--dpi", type=int, default=150, help="Output resolution (default: 150).")
def plan(file: str, output: str | None, piaf: bool, height: float | None, dpi: int):
    """Extract a plan view (top-down projection)."""
    model = _load(file)
    if model is None:
        return

    from model_reader.core.slicer import extract_plan
    from model_reader.core.exporter import export_png, export_piaf

    try:
        img = extract_plan(model, height=height, dpi=dpi)
    except Exception as e:
        error(f"Plan extraction failed: {e}")
        ready()
        return

    base = os.path.splitext(file)[0]
    if output is None:
        output = f"{base}_plan.png"

    png_path = export_png(img, output)
    ok(f"Plan saved to {png_path}.")

    if piaf:
        pdf_path = output.rsplit(".", 1)[0] + ".pdf"
        try:
            pdf_out = export_piaf(img, pdf_path)
            ok(f"PIAF PDF saved to {pdf_out}.")
        except ImportError as e:
            error(str(e))

    ready()


@main.command()
@click.argument("file")
@click.option("--axis", type=click.Choice(["x", "y", "z"], case_sensitive=False), default="z", help="Cut axis (default: z).")
@click.option("--at", "position", type=float, required=True, help="Coordinate on the axis to cut at.")
@click.option("-o", "--output", default=None, help="Output file path.")
@click.option("--piaf", is_flag=True, help="Also export PIAF tactile PDF.")
@click.option("--dpi", type=int, default=150, help="Output resolution (default: 150).")
def section(file: str, axis: str, position: float, output: str | None, piaf: bool, dpi: int):
    """Extract a section cut through the model."""
    model = _load(file)
    if model is None:
        return

    from model_reader.core.slicer import extract_section
    from model_reader.core.exporter import export_png, export_piaf

    try:
        img = extract_section(model, axis=axis, position=position, dpi=dpi)
    except Exception as e:
        error(f"Section extraction failed: {e}")
        ready()
        return

    base = os.path.splitext(file)[0]
    if output is None:
        output = f"{base}_section_{axis}{position}.png"

    png_path = export_png(img, output)
    ok(f"Section saved to {png_path}.")

    if piaf:
        pdf_path = output.rsplit(".", 1)[0] + ".pdf"
        try:
            pdf_out = export_piaf(img, pdf_path)
            ok(f"PIAF PDF saved to {pdf_out}.")
        except ImportError as e:
            error(str(e))

    ready()


@main.command()
@click.argument("file")
@click.option("--direction", "-d", type=click.Choice(["north", "south", "east", "west"], case_sensitive=False), default="north", help="View direction (default: north).")
@click.option("-o", "--output", default=None, help="Output file path.")
@click.option("--piaf", is_flag=True, help="Also export PIAF tactile PDF.")
@click.option("--dpi", type=int, default=150, help="Output resolution (default: 150).")
def elevation(file: str, direction: str, output: str | None, piaf: bool, dpi: int):
    """Extract an elevation view."""
    model = _load(file)
    if model is None:
        return

    from model_reader.core.slicer import extract_elevation
    from model_reader.core.exporter import export_png, export_piaf

    try:
        img = extract_elevation(model, direction=direction, dpi=dpi)
    except Exception as e:
        error(f"Elevation extraction failed: {e}")
        ready()
        return

    base = os.path.splitext(file)[0]
    if output is None:
        output = f"{base}_elevation_{direction}.png"

    png_path = export_png(img, output)
    ok(f"Elevation saved to {png_path}.")

    if piaf:
        pdf_path = output.rsplit(".", 1)[0] + ".pdf"
        try:
            pdf_out = export_piaf(img, pdf_path)
            ok(f"PIAF PDF saved to {pdf_out}.")
        except ImportError as e:
            error(str(e))

    ready()


if __name__ == "__main__":
    main()
