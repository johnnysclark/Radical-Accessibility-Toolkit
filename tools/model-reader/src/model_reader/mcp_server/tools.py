"""MCP tool implementations for model-reader.

Heavy imports are lazy-loaded for fast MCP server startup.
"""

from __future__ import annotations

import os
from typing import Optional

_imports_loaded = False


def _ensure_imports():
    """Lazy-load heavy dependencies on first tool call."""
    global _imports_loaded
    if _imports_loaded:
        return
    global load_3dm, describe_model, describe_layers_fn, describe_objects_fn
    global extract_plan_fn, extract_section_fn, extract_elevation_fn
    global export_png, export_piaf

    from model_reader.core.reader import load_3dm as _lr
    from model_reader.core.describer import (
        describe_model as _dm,
        describe_layers as _dl,
        describe_objects as _do,
    )
    from model_reader.core.slicer import (
        extract_plan as _ep,
        extract_section as _es,
        extract_elevation as _ee,
    )
    from model_reader.core.exporter import export_png as _xp, export_piaf as _xf

    load_3dm = _lr
    describe_model, describe_layers_fn, describe_objects_fn = _dm, _dl, _do
    extract_plan_fn, extract_section_fn, extract_elevation_fn = _ep, _es, _ee
    export_png, export_piaf = _xp, _xf

    _imports_loaded = True


async def open_3dm(file_path: str) -> str:
    """Load a .3dm file and return an accessible summary.

    Args:
        file_path: Path to the .3dm file.

    Returns:
        Text summary of the model (units, dimensions, layers, objects).
    """
    _ensure_imports()
    try:
        info = load_3dm(file_path)
        return describe_model(info) + "\nREADY:"
    except (FileNotFoundError, ValueError) as e:
        return f"ERROR: {e}"


async def list_layers(file_path: str) -> str:
    """List all layers in a .3dm file with object counts.

    Args:
        file_path: Path to the .3dm file.

    Returns:
        Numbered list of layers.
    """
    _ensure_imports()
    try:
        info = load_3dm(file_path)
        return describe_layers_fn(info) + "\nREADY:"
    except (FileNotFoundError, ValueError) as e:
        return f"ERROR: {e}"


async def list_objects(
    file_path: str,
    layer: Optional[str] = None,
    geo_type: Optional[str] = None,
) -> str:
    """List objects in a .3dm file, optionally filtered by layer or type.

    Args:
        file_path: Path to the .3dm file.
        layer: Filter to this layer name (optional).
        geo_type: Filter to this geometry type: curve, mesh, brep (optional).

    Returns:
        Numbered list of objects with dimensions.
    """
    _ensure_imports()
    try:
        info = load_3dm(file_path)
        return describe_objects_fn(info, layer=layer, geo_type=geo_type) + "\nREADY:"
    except (FileNotFoundError, ValueError) as e:
        return f"ERROR: {e}"


async def extract_plan_view(
    file_path: str,
    output_path: Optional[str] = None,
    height: Optional[float] = None,
    piaf: bool = False,
) -> str:
    """Extract a plan view (top-down projection) from a .3dm file.

    Args:
        file_path: Path to the .3dm file.
        output_path: Where to save the PNG (default: <file>_plan.png).
        height: Only include geometry at this Z height (optional).
        piaf: Also generate a PIAF tactile PDF.

    Returns:
        Confirmation with output file path(s).
    """
    _ensure_imports()
    try:
        info = load_3dm(file_path)
        img = extract_plan_fn(info, height=height)

        base = os.path.splitext(file_path)[0]
        if output_path is None:
            output_path = f"{base}_plan.png"

        png_path = export_png(img, output_path)
        result = f"OK: Plan saved to {png_path}."

        if piaf:
            pdf_path = output_path.rsplit(".", 1)[0] + ".pdf"
            try:
                pdf_out = export_piaf(img, pdf_path)
                result += f"\nOK: PIAF PDF saved to {pdf_out}."
            except ImportError as e:
                result += f"\nERROR: {e}"

        return result + "\nREADY:"
    except Exception as e:
        return f"ERROR: {e}"


async def extract_section_view(
    file_path: str,
    axis: str = "z",
    position: float = 0.0,
    output_path: Optional[str] = None,
    piaf: bool = False,
) -> str:
    """Extract a section cut through a .3dm model.

    Args:
        file_path: Path to the .3dm file.
        axis: Cut axis — 'x', 'y', or 'z'.
        position: Coordinate on the axis to cut at.
        output_path: Where to save the PNG.
        piaf: Also generate a PIAF tactile PDF.

    Returns:
        Confirmation with output file path(s).
    """
    _ensure_imports()
    try:
        info = load_3dm(file_path)
        img = extract_section_fn(info, axis=axis, position=position)

        base = os.path.splitext(file_path)[0]
        if output_path is None:
            output_path = f"{base}_section_{axis}{position}.png"

        png_path = export_png(img, output_path)
        result = f"OK: Section saved to {png_path}."

        if piaf:
            pdf_path = output_path.rsplit(".", 1)[0] + ".pdf"
            try:
                pdf_out = export_piaf(img, pdf_path)
                result += f"\nOK: PIAF PDF saved to {pdf_out}."
            except ImportError as e:
                result += f"\nERROR: {e}"

        return result + "\nREADY:"
    except Exception as e:
        return f"ERROR: {e}"


async def extract_elevation_view(
    file_path: str,
    direction: str = "north",
    output_path: Optional[str] = None,
    piaf: bool = False,
) -> str:
    """Extract an elevation view from a .3dm model.

    Args:
        file_path: Path to the .3dm file.
        direction: View direction — 'north', 'south', 'east', or 'west'.
        output_path: Where to save the PNG.
        piaf: Also generate a PIAF tactile PDF.

    Returns:
        Confirmation with output file path(s).
    """
    _ensure_imports()
    try:
        info = load_3dm(file_path)
        img = extract_elevation_fn(info, direction=direction)

        base = os.path.splitext(file_path)[0]
        if output_path is None:
            output_path = f"{base}_elevation_{direction}.png"

        png_path = export_png(img, output_path)
        result = f"OK: Elevation saved to {png_path}."

        if piaf:
            pdf_path = output_path.rsplit(".", 1)[0] + ".pdf"
            try:
                pdf_out = export_piaf(img, pdf_path)
                result += f"\nOK: PIAF PDF saved to {pdf_out}."
            except ImportError as e:
                result += f"\nERROR: {e}"

        return result + "\nREADY:"
    except Exception as e:
        return f"ERROR: {e}"
