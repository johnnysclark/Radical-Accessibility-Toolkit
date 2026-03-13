"""Screenshot saving and PIAF PDF export."""

import os
from datetime import datetime

import numpy as np
from PIL import Image
from reportlab.lib.pagesizes import letter, TABLOID
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


PAPER_SIZES = {
    "letter": letter,   # 612 x 792 points (8.5 x 11 inches)
    "tabloid": TABLOID,  # 792 x 1224 points (11 x 17 inches)
}

TARGET_DPI = 300


def _timestamp():
    """Return a filename-safe timestamp."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ensure_dir(path):
    """Create output directory if needed."""
    os.makedirs(path, exist_ok=True)


def save_screenshot(dithered_frame, output_dir, suffix=""):
    """Save a dithered frame as PNG.

    Args:
        dithered_frame: uint8 numpy array (grayscale, 0/255 values).
        output_dir: directory to save into.
        suffix: optional suffix before extension (e.g. "_tight").

    Returns:
        Full path to saved PNG file.
    """
    _ensure_dir(output_dir)
    filename = "dither_{}{}.png".format(_timestamp(), suffix)
    path = os.path.join(output_dir, filename)

    img = Image.fromarray(dithered_frame, mode="L")
    img.save(path)
    return path


def save_piaf_pdf(dithered_frame, output_dir, paper_size="letter", suffix=""):
    """Save a dithered frame as a PIAF-ready PDF.

    Places the image centered on the page, scaled to fill while
    maintaining aspect ratio, at 300 DPI for swell paper printing.

    Args:
        dithered_frame: uint8 numpy array (grayscale, 0/255 values).
        output_dir: directory to save into.
        paper_size: "letter" or "tabloid".
        suffix: optional suffix before extension.

    Returns:
        Full path to saved PDF file.
    """
    _ensure_dir(output_dir)
    filename = "dither_{}{}.pdf".format(_timestamp(), suffix)
    path = os.path.join(output_dir, filename)

    page_size = PAPER_SIZES.get(paper_size, letter)
    page_w, page_h = page_size

    # Convert numpy array to PIL Image for reportlab
    img = Image.fromarray(dithered_frame, mode="L").convert("1")
    img_w, img_h = img.size

    # Scale image to fill page while maintaining aspect ratio
    scale_x = page_w / img_w
    scale_y = page_h / img_h
    scale = min(scale_x, scale_y)

    draw_w = img_w * scale
    draw_h = img_h * scale
    draw_x = (page_w - draw_w) / 2.0
    draw_y = (page_h - draw_h) / 2.0

    c = canvas.Canvas(path, pagesize=page_size)
    c.setTitle("PIAF Dithertone Capture")
    c.setAuthor("webcam-dither")

    img_reader = ImageReader(img)
    c.drawImage(img_reader, draw_x, draw_y, draw_w, draw_h)
    c.save()

    return path


def save_screenshot_with_pdf(dithered_frame, output_dir, paper_size="letter",
                             generate_pdf=True, suffix=""):
    """Save PNG screenshot and optionally a PIAF PDF.

    Args:
        dithered_frame: uint8 numpy array.
        output_dir: output directory.
        paper_size: PDF paper size.
        generate_pdf: if False, skip PDF generation.
        suffix: optional filename suffix.

    Returns:
        Tuple of (png_path, pdf_path_or_None).
    """
    png_path = save_screenshot(dithered_frame, output_dir, suffix=suffix)
    pdf_path = None
    if generate_pdf:
        pdf_path = save_piaf_pdf(dithered_frame, output_dir,
                                 paper_size=paper_size, suffix=suffix)
    return png_path, pdf_path


def save_bracket(dithered_frames, output_dir, paper_size="letter",
                 generate_pdf=True):
    """Save bracket of 3 variants (tight/medium/loose).

    Args:
        dithered_frames: dict with keys "tight", "medium", "loose",
                         each a uint8 numpy array.
        output_dir: output directory.
        paper_size: PDF paper size.
        generate_pdf: if False, skip PDF generation.

    Returns:
        List of (label, png_path, pdf_path_or_None) tuples.
    """
    results = []
    for label in ("tight", "medium", "loose"):
        frame = dithered_frames[label]
        suffix = "_{}".format(label)
        png_path, pdf_path = save_screenshot_with_pdf(
            frame, output_dir, paper_size=paper_size,
            generate_pdf=generate_pdf, suffix=suffix,
        )
        results.append((label, png_path, pdf_path))
    return results
