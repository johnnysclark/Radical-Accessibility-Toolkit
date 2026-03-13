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
@click.option("--hatch", default=None, help="Hatch fill mode: 'auto' assigns per layer, or a pattern name (diagonal, crosshatch, dots, horizontal, dense_diagonal, sparse_diagonal).")
def plan(file: str, output: str | None, piaf: bool, height: float | None, dpi: int, hatch: str | None):
    """Extract a plan view (top-down projection).

    Use --hatch auto to fill closed regions with distinct tactile patterns
    per layer, making rooms distinguishable by touch on PIAF prints.
    """
    model = _load(file)
    if model is None:
        return

    from model_reader.core.slicer import extract_plan
    from model_reader.core.exporter import export_png, export_piaf

    try:
        img = extract_plan(model, height=height, dpi=dpi, hatch=hatch)
    except Exception as e:
        error(f"Plan extraction failed: {e}")
        ready()
        return

    base = os.path.splitext(file)[0]
    if output is None:
        suffix = "_plan_hatched" if hatch else "_plan"
        output = f"{base}{suffix}.png"

    png_path = export_png(img, output)
    ok(f"Plan saved to {png_path}.")

    if hatch:
        from model_reader.core.hatches import list_patterns
        ok(f"Hatch mode: {hatch}. Available patterns: {', '.join(list_patterns())}.")

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


# ── Export and utility commands ────────────────────────────


@main.command("export-stl")
@click.argument("file")
@click.option("-o", "--output", default=None, help="Output STL path (default: <file>.stl).")
@click.option("--scale", type=float, default=1.0, help="Uniform scale factor (e.g. 25.4 for inches to mm).")
@click.option("--layer", "-l", default=None, help="Only export geometry on this layer.")
def export_stl_cmd(file: str, output: str | None, scale: float, layer: str | None):
    """Export 3D model geometry as binary STL for 3D printing.

    Extracts mesh, brep, and extrusion geometry from the .3dm file
    and writes a binary STL file. Curves/lines are skipped (STL is
    mesh-only). Use --scale to convert units for your printer.
    """
    model = _load(file)
    if model is None:
        return

    from model_reader.core.exporter import export_stl

    base = os.path.splitext(file)[0]
    if output is None:
        output = f"{base}.stl"

    try:
        stl_path, count = export_stl(
            model.file3dm, output, scale=scale, layer=layer
        )
        ok(f"STL saved to {stl_path}.")
        ok(f"Triangles: {count}.")
        file_size = os.path.getsize(stl_path)
        ok(f"File size: {file_size:,} bytes.")
    except ValueError as e:
        error(str(e))

    ready()


@main.command()
def hatches():
    """List available hatch patterns for floor plans."""
    from model_reader.core.hatches import HATCH_PATTERNS

    ok(f"{len(HATCH_PATTERNS)} hatch patterns available.")
    for i, (name, spec) in enumerate(HATCH_PATTERNS.items(), 1):
        if spec.get("type") == "dots":
            desc = f"dot grid, spacing {spec['spacing']}px, radius {spec['radius']}px"
        else:
            angles = spec["angles"]
            angle_str = "+".join(f"{a} degrees" for a in angles)
            desc = f"{angle_str}, spacing {spec['spacing']}px, weight {spec['weight']}px"
        info(f"{i}. {name}: {desc}.")
    ready()


if __name__ == "__main__":
    main()
