# -*- coding: utf-8 -*-
"""
PDF Generator — Create PIAF-ready PDF output  v1.0
====================================================
Wraps B&W images into PDF files optimized for PIAF swell-paper
printing.  300 DPI, pure black & white, letter or tabloid paper.

Supports braille labels rendered with DejaVu Sans font and
metadata embedding.

Part of the Radical Accessibility Project — UIUC School of Architecture.

Dependencies:  Pillow (PIL), reportlab
"""

import io
import os
from datetime import datetime

from PIL import Image

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    _REPORTLAB = True
except ImportError:
    _REPORTLAB = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TARGET_DPI = 300

PAPER_SIZES_IN = {
    "letter":  (8.5, 11.0),
    "tabloid": (11.0, 17.0),
}

# Points per inch (PDF standard)
PTS_PER_INCH = 72


# ---------------------------------------------------------------------------
# Font registration
# ---------------------------------------------------------------------------

_FONT_REGISTERED = False


def _register_braille_font():
    """Register a Unicode-Braille-capable font with reportlab."""
    global _FONT_REGISTERED
    if _FONT_REGISTERED or not _REPORTLAB:
        return
    # Try DejaVu Sans (has full Unicode Braille block)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "C:/Windows/Fonts/DejaVuSans.ttf",
        os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf"),
    ]
    for fp in font_paths:
        if os.path.isfile(fp):
            try:
                pdfmetrics.registerFont(TTFont("DejaVuSans", fp))
                _FONT_REGISTERED = True
                return
            except Exception:
                continue
    # Fallback: use Helvetica (no Braille support, but won't crash)
    _FONT_REGISTERED = True


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

def generate_pdf(image, output_path, paper_size="letter", metadata=None):
    """Generate a PIAF-ready PDF from a B&W PIL Image.

    Args:
        image:       PIL.Image (mode '1' or 'L').
        output_path: Path for output PDF file.
        paper_size:  "letter" or "tabloid".
        metadata:    Optional dict with source info for embedding.

    Returns:
        Absolute path of the generated PDF.

    Raises:
        ImportError: If reportlab is not installed.
    """
    if not _REPORTLAB:
        raise ImportError(
            "reportlab is required for PDF generation. "
            "Install it: pip install reportlab")

    _register_braille_font()

    pw, ph = PAPER_SIZES_IN.get(paper_size, PAPER_SIZES_IN["letter"])
    page_w_pts = pw * PTS_PER_INCH
    page_h_pts = ph * PTS_PER_INCH

    # Convert image to bytes for embedding
    if image.mode == '1':
        # Convert to 'L' for better PDF embedding
        image = image.convert('L')

    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG', dpi=(TARGET_DPI, TARGET_DPI))
    img_buffer.seek(0)
    img_reader = ImageReader(img_buffer)

    # Calculate image placement (centered with margins)
    margin = 0.5 * PTS_PER_INCH
    draw_w = page_w_pts - 2 * margin
    draw_h = page_h_pts - 2 * margin

    img_w, img_h = image.size
    # Scale image to fit drawing area
    img_w_in = img_w / TARGET_DPI
    img_h_in = img_h / TARGET_DPI
    img_w_pts = img_w_in * PTS_PER_INCH
    img_h_pts = img_h_in * PTS_PER_INCH

    scale = min(draw_w / img_w_pts, draw_h / img_h_pts, 1.0)
    final_w = img_w_pts * scale
    final_h = img_h_pts * scale

    # Center on page
    x_offset = margin + (draw_w - final_w) / 2
    y_offset = margin + (draw_h - final_h) / 2

    # Create PDF
    c = canvas.Canvas(output_path, pagesize=(page_w_pts, page_h_pts))

    # Metadata
    c.setTitle("PIAF Tactile Graphic")
    c.setAuthor("Radical Accessibility Project")
    c.setSubject("Tactile graphic for PIAF swell-paper printing")
    if metadata:
        source = metadata.get("source", "unknown")
        c.setKeywords("PIAF, tactile, swell-paper, {}".format(source))

    # Draw the image
    c.drawImage(img_reader, x_offset, y_offset, final_w, final_h)

    # Footer with generation info
    c.setFont("Helvetica", 6)
    footer = "Generated {} | {} paper | {} DPI | Radical Accessibility Project".format(
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        paper_size.title(),
        TARGET_DPI)
    c.drawString(margin, margin / 2, footer)

    c.save()
    return os.path.abspath(output_path)


def generate_pdf_from_file(image_path, output_path=None, paper_size="letter"):
    """Generate PDF from an image file.

    Args:
        image_path:  Path to B&W image (PNG recommended).
        output_path: Path for output PDF (default: input.pdf).
        paper_size:  "letter" or "tabloid".

    Returns:
        Absolute path of the generated PDF.
    """
    if output_path is None:
        output_path = os.path.splitext(image_path)[0] + ".pdf"

    img = Image.open(image_path)
    return generate_pdf(img, output_path, paper_size,
                        metadata={"source": os.path.basename(image_path)})
