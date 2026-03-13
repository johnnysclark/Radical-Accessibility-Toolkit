"""Screenshot and PIAF PDF export.

Saves dithered frames as PNG images and optionally generates
PIAF-ready PDFs via the tactile_core package.
"""

import os
from datetime import datetime

import cv2
import numpy as np
from PIL import Image


def _timestamp():
    """Return a filesystem-safe timestamp string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_screenshot(image, output_dir, prefix="dither"):
    """Save a dithered frame as a PNG image.

    Args:
        image: numpy array, single-channel dithered image.
        output_dir: Directory to save into.
        prefix: Filename prefix.

    Returns:
        Absolute path to the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{prefix}_{_timestamp()}.png"
    path = os.path.join(output_dir, filename)
    cv2.imwrite(path, image)
    return os.path.abspath(path)


def save_piaf_pdf(image, output_dir, paper_size="letter", prefix="dither"):
    """Save a dithered frame as a PIAF-ready PDF.

    Requires tactile-core to be installed. Returns None if not available.

    Args:
        image: numpy array, single-channel dithered image.
        output_dir: Directory to save into.
        paper_size: 'letter' or 'tabloid'.
        prefix: Filename prefix.

    Returns:
        Absolute path to the saved PDF, or None if tactile-core is missing.
    """
    try:
        from tactile_core.core.pdf_generator import PIAFPDFGenerator
    except ImportError:
        return None

    os.makedirs(output_dir, exist_ok=True)

    # Convert to 1-bit PIL Image
    bw = (image > 128).astype(np.uint8) * 255
    pil_img = Image.fromarray(bw, mode="L").convert("1")

    filename = f"{prefix}_{_timestamp()}.pdf"
    path = os.path.join(output_dir, filename)

    generator = PIAFPDFGenerator()
    generator.generate(pil_img, path, paper_size=paper_size)
    return os.path.abspath(path)


def save_bracket(gray_frame, renderer, output_dir, paper_size="letter", piaf=False):
    """Save three spacing variants: tight, medium, loose.

    Args:
        gray_frame: numpy array, grayscale source frame.
        renderer: DithertoneRenderer with current settings.
        output_dir: Directory to save into.
        paper_size: Paper size for PIAF PDFs.
        piaf: Whether to also generate PIAF PDFs.

    Returns:
        List of (label, png_path, pdf_path_or_none) tuples.
    """
    base_spacing = renderer.params.spacing
    variants = [
        ("tight", max(3, int(base_spacing * 0.6))),
        ("medium", base_spacing),
        ("loose", min(40, int(base_spacing * 1.6))),
    ]

    results = []
    ts = _timestamp()
    for label, spacing in variants:
        variant_renderer = renderer.clone_with_spacing(spacing)
        dithered = variant_renderer.render(gray_frame)

        name = f"bracket_{label}_{ts}"
        os.makedirs(output_dir, exist_ok=True)

        png_path = os.path.join(output_dir, f"{name}.png")
        cv2.imwrite(png_path, dithered)
        png_path = os.path.abspath(png_path)

        pdf_path = None
        if piaf:
            pdf_path = save_piaf_pdf(dithered, output_dir, paper_size, prefix=name)

        results.append((label, png_path, pdf_path))

    return results
