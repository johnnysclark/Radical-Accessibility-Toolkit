"""Export rendered views to PNG and PIAF PDF."""

from __future__ import annotations

import os

from PIL import Image


def export_png(image: Image.Image, output_path: str) -> str:
    """Save a PIL image as PNG.

    Args:
        image: PIL Image to save.
        output_path: Destination file path.

    Returns:
        Absolute path to the saved file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    image.save(output_path, "PNG")
    return os.path.abspath(output_path)


def export_piaf(image: Image.Image, output_path: str, paper_size: str = "letter") -> str:
    """Save a PIL image as a PIAF-ready tactile PDF.

    Requires tactile-core to be installed (pip install tactile-core).

    Args:
        image: PIL Image (ideally mode '1' or 'L').
        output_path: Destination PDF file path.
        paper_size: 'letter' or 'tabloid'.

    Returns:
        Absolute path to the saved file.

    Raises:
        ImportError: If tactile-core is not installed.
    """
    try:
        from tactile_core.core.pdf_generator import PIAFPDFGenerator
    except ImportError:
        raise ImportError(
            "PIAF export requires tactile-core. Install with: "
            "pip install -e tools/tact"
        )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Ensure 1-bit image for PIAF
    if image.mode != "1":
        image = image.convert("1")

    generator = PIAFPDFGenerator()
    generator.generate(image, output_path, paper_size=paper_size)
    return os.path.abspath(output_path)
