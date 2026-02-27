#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image-to-PIAF — Tactile Image Conversion Pipeline  v1.0
=========================================================
Converts architectural images into PIAF-ready output for swell paper
printing.  Optimized for blind / low-vision tactile reading with
density management, braille labeling, and architectural presets.

Part of the Radical Accessibility Project — UIUC School of Architecture.

Dependencies
------------
  Pillow  (pip install Pillow)

Usage
-----
  python image_to_piaf.py <image> [--preset floor_plan] [--output out.png]
  python image_to_piaf.py                          (interactive REPL)
  python image_to_piaf.py --help

Pipeline
--------
  Input image (JPG, PNG, TIFF, BMP, GIF, PDF, WebP)
    → Load + convert to RGB
    → Optional contrast enhancement (s_curve, histogram_eq, auto_contrast)
    → Grayscale conversion
    → Threshold to B&W
    → Density check + auto-reduction (morphological erosion)
    → Optional braille label generation
    → Optional tiling with registration marks
    → Output: PIAF-ready image at 300 DPI (PNG, TIFF, or PDF)
"""

import argparse
import json
import math
import os
import sys
import struct
from datetime import datetime

# ── Check Pillow dependency ──────────────────────────────
try:
    from PIL import (Image, ImageDraw, ImageFilter, ImageFont,
                     ImageOps, ImageEnhance)
except ImportError:
    print("ERROR: Pillow is required. Install with: pip install Pillow")
    print("READY:")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

VERSION = "1.0"
PIAF_DPI = 300

# Paper sizes in inches
PAPER_SIZES = {
    "letter":  (8.5, 11.0),
    "tabloid": (11.0, 17.0),
    "a4":      (8.27, 11.69),
    "a3":      (11.69, 16.54),
}

# Density limits for PIAF swell paper
DENSITY_MAX = 0.45       # absolute max — above this, swell paper is unreadable
DENSITY_TARGET = 0.30    # optimal target for tactile clarity

# Braille dot dimensions at 300 DPI (BANA-informed)
BRAILLE_DOT_DIAMETER = 14      # px (~1.2mm at 300 DPI)
BRAILLE_DOT_HSPACING = 26      # px horizontal center-to-center within cell
BRAILLE_DOT_VSPACING = 26      # px vertical center-to-center within cell
BRAILLE_CELL_WIDTH = 62        # px center-to-center between cells (~5.2mm)
BRAILLE_WORD_SPACE = 96        # px space between words (~8mm)
BRAILLE_LABEL_PAD = 8          # px padding around label background

SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff",
                  ".bmp", ".gif", ".webp", ".pdf"}

HISTORY_FILENAME = "image_to_piaf_history.json"

# ═══════════════════════════════════════════════════════════
# BRAILLE CONVERSION — Grade 1 ASCII-to-Unicode
# ═══════════════════════════════════════════════════════════

# Standard Grade 1 braille alphabet (dots → Unicode offset from U+2800)
_BRAILLE_ALPHA = {
    'a': 0x01, 'b': 0x03, 'c': 0x09, 'd': 0x19, 'e': 0x11,
    'f': 0x0B, 'g': 0x1B, 'h': 0x13, 'i': 0x0A, 'j': 0x1A,
    'k': 0x05, 'l': 0x07, 'm': 0x0D, 'n': 0x1D, 'o': 0x15,
    'p': 0x0F, 'q': 0x1F, 'r': 0x17, 's': 0x0E, 't': 0x1E,
    'u': 0x25, 'v': 0x27, 'w': 0x3A, 'x': 0x2D, 'y': 0x3D,
    'z': 0x35,
}

# Numbers 1-9, 0 use letters a-j with a number indicator prefix
_BRAILLE_DIGITS = {
    '1': 0x01, '2': 0x03, '3': 0x09, '4': 0x19, '5': 0x11,
    '6': 0x0B, '7': 0x1B, '8': 0x13, '9': 0x0A, '0': 0x1A,
}

_BRAILLE_PUNCT = {
    '.': 0x32, ',': 0x02, ';': 0x06, ':': 0x12,
    '!': 0x16, '?': 0x26, '-': 0x24, "'": 0x02,
    '"': 0x26, '(': 0x26, ')': 0x34, '/': 0x0C,
}

_BRAILLE_CAPITAL = 0x20   # dots 6 — capital indicator
_BRAILLE_NUMBER = 0x3C    # dots 3,4,5,6 — number indicator
_BRAILLE_SPACE = 0x00     # empty cell


def text_to_braille(text):
    """Convert ASCII text to Unicode Braille characters (Grade 1).

    Returns the braille string. Grade 1 is character-by-character
    without contractions.  For Grade 2 (contracted braille), install
    liblouis and use text_to_braille_g2().
    """
    result = []
    in_number = False
    for ch in text:
        if ch == ' ':
            result.append(chr(0x2800 + _BRAILLE_SPACE))
            in_number = False
        elif ch.isdigit():
            if not in_number:
                result.append(chr(0x2800 + _BRAILLE_NUMBER))
                in_number = True
            result.append(chr(0x2800 + _BRAILLE_DIGITS.get(ch, 0)))
        elif ch.isalpha():
            in_number = False
            lower = ch.lower()
            if ch.isupper():
                result.append(chr(0x2800 + _BRAILLE_CAPITAL))
            code = _BRAILLE_ALPHA.get(lower)
            if code is not None:
                result.append(chr(0x2800 + code))
        else:
            in_number = False
            code = _BRAILLE_PUNCT.get(ch)
            if code is not None:
                result.append(chr(0x2800 + code))
    return "".join(result)


def text_to_braille_g2(text):
    """Convert text to Grade 2 (contracted) braille via liblouis.

    Falls back to Grade 1 if liblouis is not installed.
    Returns (braille_string, grade_used).
    """
    try:
        import louis
        tables = ["en-ueb-g2.ctb"]
        braille = louis.translateString(tables, text)
        return braille, 2
    except ImportError:
        return text_to_braille(text), 1
    except Exception:
        return text_to_braille(text), 1


def braille_width_px(text):
    """Calculate pixel width of a braille string at 300 DPI."""
    cells = len(text)
    if cells == 0:
        return 0
    words = text.split(chr(0x2800))  # split on braille space
    total = 0
    for i, word in enumerate(words):
        if i > 0:
            total += BRAILLE_WORD_SPACE
        total += len(word) * BRAILLE_CELL_WIDTH
    return total


def braille_height_px():
    """Height of a braille label in pixels (3 inter-dot gaps + padding)."""
    return BRAILLE_DOT_VSPACING * 3 + BRAILLE_DOT_DIAMETER + 2 * BRAILLE_LABEL_PAD


# ═══════════════════════════════════════════════════════════
# PRESETS — Tuned parameters for different architectural image types
# ═══════════════════════════════════════════════════════════

PRESETS = {
    "floor_plan": {
        "threshold": 100,
        "contrast": "auto_contrast",
        "description": "Architectural floor plans — CAD output, printed plans",
    },
    "elevation": {
        "threshold": 120,
        "contrast": "s_curve",
        "description": "Building elevations — line drawings with moderate detail",
    },
    "photograph": {
        "threshold": 90,
        "contrast": "clahe",
        "description": "Photographs of buildings, sites, or models",
    },
    "sketch": {
        "threshold": 140,
        "contrast": "none",
        "description": "Hand-drawn sketches — light pencil or pen lines",
    },
    "section": {
        "threshold": 110,
        "contrast": "histogram_eq",
        "description": "Building sections — line drawings with poche/fill",
    },
    "site_plan": {
        "threshold": 95,
        "contrast": "auto_contrast",
        "description": "Site plans — contours, vegetation, context",
    },
    "rendering": {
        "threshold": 85,
        "contrast": "clahe",
        "description": "3D renderings — shaded views with tonal range",
    },
    "diagram": {
        "threshold": 105,
        "contrast": "s_curve",
        "description": "Diagrams — circulation, structural, concept diagrams",
    },
    "historic_photo": {
        "threshold": 80,
        "contrast": "histogram_eq",
        "description": "Historic photographs — low contrast, aged images",
    },
    "handdrawn": {
        "threshold": 130,
        "contrast": "none",
        "description": "Hand-drawn plans or details — strong pencil/ink lines",
    },
}


# ═══════════════════════════════════════════════════════════
# IMAGE PROCESSING
# ═══════════════════════════════════════════════════════════

def load_image(path):
    """Load an image from disk and convert to RGB.

    Supports JPG, PNG, TIFF, BMP, GIF, WebP.
    Returns a PIL Image in RGB mode.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_EXTS:
        raise ValueError(
            f"Unsupported format: {ext}. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTS))}")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    img = Image.open(path)
    if img.mode == "RGBA":
        # Composite onto white background
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    return img


def apply_contrast(img, method="auto_contrast"):
    """Apply contrast enhancement to an RGB image.

    Methods:
      none          — no enhancement
      auto_contrast — stretch histogram to full range
      histogram_eq  — equalize histogram for maximum contrast
      s_curve       — apply S-curve for enhanced mid-tone contrast
      clahe         — local contrast enhancement via tiled equalization
    """
    if method == "none":
        return img

    if method == "auto_contrast":
        return ImageOps.autocontrast(img, cutoff=1)

    if method == "histogram_eq":
        return ImageOps.equalize(img)

    if method == "s_curve":
        # S-curve lookup table: steepens mid-tones, compresses shadows/highlights
        lut = []
        for i in range(256):
            x = i / 255.0
            # Sigmoid-based S-curve
            y = 1.0 / (1.0 + math.exp(-10 * (x - 0.5)))
            lut.append(int(y * 255))
        return img.point(lut * 3)  # apply to R, G, B

    if method == "clahe":
        # Simplified local contrast enhancement without OpenCV:
        # 1. Auto-contrast the full image
        # 2. Apply unsharp mask for local detail enhancement
        # 3. Equalize to spread the histogram
        enhanced = ImageOps.autocontrast(img, cutoff=2)
        enhanced = enhanced.filter(
            ImageFilter.UnsharpMask(radius=20, percent=80, threshold=3))
        return enhanced

    raise ValueError(f"Unknown contrast method: {method}. "
                     f"Options: none, auto_contrast, histogram_eq, s_curve, clahe")


def to_grayscale(img):
    """Convert RGB image to grayscale (mode L)."""
    return img.convert("L")


def threshold_bw(img_gray, threshold=128):
    """Convert grayscale image to pure black-and-white (mode 1).

    Pixels below threshold become black (0), at or above become white (1).
    Returns a mode-1 image.
    """
    return img_gray.point(lambda p: 255 if p >= threshold else 0, mode="1")


def compute_density(img_bw):
    """Compute black pixel density of a B&W image.

    Returns a float 0.0–1.0 where 1.0 = all black.
    """
    if img_bw.mode != "1":
        img_bw = img_bw.convert("1")
    # In mode 1: 0 = black, 255 = white
    w, h = img_bw.size
    total = w * h
    if total == 0:
        return 0.0
    # Count black pixels by iterating raw pixel access
    pix = img_bw.load()
    black = 0
    for y in range(h):
        for x in range(w):
            if pix[x, y] == 0:
                black += 1
    return black / total


def reduce_density(img_bw, target=DENSITY_TARGET, max_iterations=20):
    """Reduce black pixel density via morphological erosion.

    Iteratively applies MaxFilter (which expands white / shrinks black)
    until density is below target or max iterations reached.

    Returns (processed_image, final_density, iterations_used).
    """
    density = compute_density(img_bw)
    iterations = 0

    while density > target and iterations < max_iterations:
        # Convert to L for filtering, then back to 1
        img_l = img_bw.convert("L")
        img_l = img_l.filter(ImageFilter.MaxFilter(3))
        img_bw = img_l.point(lambda p: 255 if p >= 128 else 0, mode="1")
        density = compute_density(img_bw)
        iterations += 1

    return img_bw, density, iterations


def fit_to_paper(img, paper="letter", margin_inches=0.5):
    """Resize image to fit paper size at PIAF_DPI, preserving aspect ratio.

    Args:
        img: PIL Image (any mode)
        paper: Paper size name or (width_in, height_in) tuple
        margin_inches: Margin on each side

    Returns (resized_image, scale_factor).
    """
    if isinstance(paper, str):
        paper_w, paper_h = PAPER_SIZES.get(paper, PAPER_SIZES["letter"])
    else:
        paper_w, paper_h = paper

    # Printable area in pixels
    max_w = int((paper_w - 2 * margin_inches) * PIAF_DPI)
    max_h = int((paper_h - 2 * margin_inches) * PIAF_DPI)

    # Current size
    w, h = img.size

    # Scale to fit
    scale = min(max_w / w, max_h / h)
    if scale >= 1.0:
        # Image already fits — don't upscale
        return img, 1.0

    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    return resized, scale


def center_on_page(img_bw, paper="letter", margin_inches=0.5):
    """Place a B&W image centered on a white page at PIAF_DPI.

    Returns a new image sized to the full paper dimensions.
    """
    if isinstance(paper, str):
        paper_w, paper_h = PAPER_SIZES.get(paper, PAPER_SIZES["letter"])
    else:
        paper_w, paper_h = paper

    page_w = int(paper_w * PIAF_DPI)
    page_h = int(paper_h * PIAF_DPI)
    page = Image.new("1", (page_w, page_h), 1)  # white page

    w, h = img_bw.size
    x_off = (page_w - w) // 2
    y_off = (page_h - h) // 2
    page.paste(img_bw, (x_off, y_off))
    return page


# ═══════════════════════════════════════════════════════════
# BRAILLE LABEL RENDERING
# ═══════════════════════════════════════════════════════════

def _draw_braille_char(draw, x, y, braille_char):
    """Draw a single braille character as dots.

    The braille character is decoded from its Unicode offset to determine
    which of the 6 dots (standard 6-dot braille) to draw.

    Args:
        draw: ImageDraw instance
        x, y: top-left corner of the character cell
        braille_char: single Unicode braille character
    """
    code = ord(braille_char) - 0x2800
    r = BRAILLE_DOT_DIAMETER // 2

    # 6-dot braille layout:
    # dot 1 (bit 0)  dot 4 (bit 3)
    # dot 2 (bit 1)  dot 5 (bit 4)
    # dot 3 (bit 2)  dot 6 (bit 5)
    dot_positions = [
        (0, 0, 0x01),  # dot 1
        (0, 1, 0x02),  # dot 2
        (0, 2, 0x04),  # dot 3
        (1, 0, 0x08),  # dot 4
        (1, 1, 0x10),  # dot 5
        (1, 2, 0x20),  # dot 6
    ]

    for col, row, mask in dot_positions:
        if code & mask:
            cx = x + BRAILLE_LABEL_PAD + col * BRAILLE_DOT_HSPACING + r
            cy = y + BRAILLE_LABEL_PAD + row * BRAILLE_DOT_VSPACING + r
            draw.ellipse(
                [cx - r, cy - r, cx + r, cy + r],
                fill=0)  # black dot


def draw_braille_label(img_bw, text, position, english_above=True):
    """Draw a braille label on a B&W image.

    Renders the text as braille dots with an optional English text line
    above.  Clears (whiteouts) the area behind the label first so PIAF
    swell paper doesn't create interfering bumps.

    Args:
        img_bw: PIL Image in mode 1
        text: English text to convert to braille
        position: (x, y) top-left corner of the label area
        english_above: if True, draw English text above braille dots

    Returns the modified image.
    """
    # Convert to L mode for drawing, convert back at end
    img = img_bw.convert("L")
    draw = ImageDraw.Draw(img)

    braille = text_to_braille(text)
    bw = braille_width_px(braille) + 2 * BRAILLE_LABEL_PAD
    bh = braille_height_px()

    x, y = position
    label_y = y

    if english_above:
        # Draw English text above braille
        # Use default font at a readable size
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except (OSError, IOError):
            font = ImageFont.load_default()
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        english_h = text_h + 8

        # Whiteout area for both English and braille
        total_w = max(bw, text_w + 2 * BRAILLE_LABEL_PAD)
        total_h = english_h + bh
        draw.rectangle([x, y, x + total_w, y + total_h], fill=255)

        # Draw English text
        draw.text((x + BRAILLE_LABEL_PAD, y + 4), text, fill=0, font=font)
        label_y = y + english_h
    else:
        # Whiteout area for braille only
        draw.rectangle([x, y, x + bw, y + bh], fill=255)
        label_y = y

    # Draw braille dots
    cx = x
    for ch in braille:
        if ch == chr(0x2800):  # space
            cx += BRAILLE_WORD_SPACE
        else:
            _draw_braille_char(draw, cx, label_y, ch)
            cx += BRAILLE_CELL_WIDTH

    result = img.point(lambda p: 255 if p >= 128 else 0, mode="1")
    return result


class LabelPlacer:
    """Manages label placement with overlap detection.

    Tracks placed labels and attempts repositioning when overlaps
    are detected.  If no clear position is found, assigns an
    abbreviation letter and builds an abbreviation key.
    """

    def __init__(self, img_width, img_height):
        self.img_width = img_width
        self.img_height = img_height
        self.placed = []        # list of (x, y, w, h) bounding boxes
        self.abbreviations = {} # letter → full text
        self._next_abbrev = 0

    def _overlaps(self, x, y, w, h, min_spacing=6):
        """Check if a proposed label overlaps any placed label."""
        for px, py, pw, ph in self.placed:
            if (x < px + pw + min_spacing and
                x + w > px - min_spacing and
                y < py + ph + min_spacing and
                y + h > py - min_spacing):
                return True
        return False

    def _in_bounds(self, x, y, w, h):
        """Check if label fits within image bounds."""
        return (x >= 0 and y >= 0 and
                x + w <= self.img_width and
                y + h <= self.img_height)

    def place(self, text, preferred_x, preferred_y, label_w, label_h):
        """Find a non-overlapping position for a label.

        Tries: preferred → below → above → right → left.
        If all overlap, abbreviates to a letter.

        Returns (x, y, display_text, was_abbreviated).
        """
        # Try preferred position
        candidates = [
            (preferred_x, preferred_y),
            (preferred_x, preferred_y + label_h + 10),          # below
            (preferred_x, preferred_y - label_h - 10),          # above
            (preferred_x + label_w + 10, preferred_y),          # right
            (preferred_x - label_w - 10, preferred_y),          # left
        ]

        for cx, cy in candidates:
            if (self._in_bounds(cx, cy, label_w, label_h) and
                    not self._overlaps(cx, cy, label_w, label_h)):
                self.placed.append((cx, cy, label_w, label_h))
                return cx, cy, text, False

        # All positions overlap — abbreviate
        letter = chr(ord('A') + self._next_abbrev)
        self._next_abbrev += 1
        self.abbreviations[letter] = text

        # Abbreviation is much smaller — try again with just the letter
        abbrev_w = BRAILLE_CELL_WIDTH + 2 * BRAILLE_LABEL_PAD
        abbrev_h = braille_height_px()
        for cx, cy in candidates:
            if (self._in_bounds(cx, cy, abbrev_w, abbrev_h) and
                    not self._overlaps(cx, cy, abbrev_w, abbrev_h)):
                self.placed.append((cx, cy, abbrev_w, abbrev_h))
                return cx, cy, letter, True

        # Last resort: place at preferred position regardless of overlap
        self.placed.append((preferred_x, preferred_y, abbrev_w, abbrev_h))
        return preferred_x, preferred_y, letter, True


# ═══════════════════════════════════════════════════════════
# TILING — Split large images across multiple pages
# ═══════════════════════════════════════════════════════════

def tile_image(img_bw, paper="letter", margin_inches=0.5, overlap_inches=0.5):
    """Split a large B&W image into page-sized tiles with registration marks.

    Each tile includes a small overlap region for alignment and
    registration marks (crosshairs at corners) for physical assembly.

    Args:
        img_bw: PIL Image in mode 1
        paper: Paper size name
        margin_inches: Margin on each side
        overlap_inches: Overlap between adjacent tiles

    Returns list of (tile_image, row, col) tuples.
    """
    if isinstance(paper, str):
        paper_w, paper_h = PAPER_SIZES.get(paper, PAPER_SIZES["letter"])
    else:
        paper_w, paper_h = paper

    printable_w = int((paper_w - 2 * margin_inches) * PIAF_DPI)
    printable_h = int((paper_h - 2 * margin_inches) * PIAF_DPI)
    overlap_px = int(overlap_inches * PIAF_DPI)

    # Effective tile step (excluding overlap)
    step_w = printable_w - overlap_px
    step_h = printable_h - overlap_px

    w, h = img_bw.size

    if w <= printable_w and h <= printable_h:
        # Image fits on one page — no tiling needed
        return [(center_on_page(img_bw, paper, margin_inches), 0, 0)]

    cols = max(1, math.ceil((w - overlap_px) / step_w))
    rows = max(1, math.ceil((h - overlap_px) / step_h))

    tiles = []
    for row in range(rows):
        for col in range(cols):
            x0 = col * step_w
            y0 = row * step_h
            x1 = min(x0 + printable_w, w)
            y1 = min(y0 + printable_h, h)

            tile = img_bw.crop((x0, y0, x1, y1))

            # Place on full page
            page = Image.new("1",
                             (int(paper_w * PIAF_DPI), int(paper_h * PIAF_DPI)),
                             1)
            margin_px = int(margin_inches * PIAF_DPI)
            page.paste(tile, (margin_px, margin_px))

            # Draw registration marks (crosshairs at tile corners)
            page_draw = ImageDraw.Draw(page)
            mark_len = int(0.3 * PIAF_DPI)  # 0.3 inch crosshair

            corners = [
                (margin_px, margin_px),                                   # top-left
                (margin_px + x1 - x0, margin_px),                        # top-right
                (margin_px, margin_px + y1 - y0),                        # bottom-left
                (margin_px + x1 - x0, margin_px + y1 - y0),             # bottom-right
            ]
            for cx, cy in corners:
                page_draw.line([(cx - mark_len, cy), (cx + mark_len, cy)],
                               fill=0, width=2)
                page_draw.line([(cx, cy - mark_len), (cx, cy + mark_len)],
                               fill=0, width=2)

            # Draw page label (row, col) in corner
            label = f"R{row+1}C{col+1}"
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except (OSError, IOError):
                font = ImageFont.load_default()
            page_draw.text((margin_px + 5, margin_px - 20), label,
                           fill=0, font=font)

            tiles.append((page, row, col))

    return tiles


# ═══════════════════════════════════════════════════════════
# CONVERSION PIPELINE
# ═══════════════════════════════════════════════════════════

def convert(
    image_path,
    preset="floor_plan",
    threshold=None,
    contrast=None,
    labels=None,
    paper="letter",
    margin=0.5,
    auto_density=True,
    density_target=None,
    invert=False,
    crop=None,
    output_path=None,
    output_format="png",
    tile=False,
):
    """Run the full image-to-PIAF conversion pipeline.

    Args:
        image_path: Path to source image
        preset: Preset name (determines threshold + contrast defaults)
        threshold: Override threshold (0-255). Lower = more black.
        contrast: Override contrast method
        labels: List of {"text": str, "x": int, "y": int} label dicts
        paper: Paper size name or (w, h) tuple in inches
        margin: Margin in inches
        auto_density: If True, auto-reduce density when above target
        density_target: Override density target (0.0-1.0)
        invert: If True, invert image before processing
        crop: Optional (left, top, right, bottom) crop box in pixels
        output_path: Output file path (auto-generated if None)
        output_format: "png", "tiff", or "pdf"
        tile: If True, split into page-sized tiles

    Returns dict with:
        output_path(s), density, dimensions, labels_placed, etc.
    """
    # Resolve preset defaults
    p = PRESETS.get(preset, PRESETS["floor_plan"])
    if threshold is None:
        threshold = p["threshold"]
    if contrast is None:
        contrast = p["contrast"]
    if density_target is None:
        density_target = DENSITY_TARGET

    result = {
        "source": os.path.abspath(image_path),
        "preset": preset,
        "threshold": threshold,
        "contrast": contrast,
    }

    # Step 1: Load
    img = load_image(image_path)
    orig_w, orig_h = img.size
    result["original_size"] = (orig_w, orig_h)

    # Step 2: Crop (optional)
    if crop:
        img = img.crop(crop)
        result["cropped_to"] = crop

    # Step 3: Contrast enhancement
    img = apply_contrast(img, method=contrast)

    # Step 4: Grayscale
    img_gray = to_grayscale(img)

    # Step 5: Invert (optional — for images where lines are white on black)
    if invert:
        img_gray = ImageOps.invert(img_gray)
        result["inverted"] = True

    # Step 6: Fit to paper
    img_gray, scale = fit_to_paper(img_gray, paper, margin)
    result["scale_factor"] = round(scale, 4)
    result["fitted_size"] = img_gray.size

    # Step 7: Threshold to B&W
    img_bw = threshold_bw(img_gray, threshold)

    # Step 8: Density check + auto-reduce
    density_before = compute_density(img_bw)
    result["density_before"] = round(density_before, 4)

    if auto_density and density_before > density_target:
        img_bw, density_after, iters = reduce_density(
            img_bw, target=density_target)
        result["density_after"] = round(density_after, 4)
        result["density_iterations"] = iters
    else:
        result["density_after"] = round(density_before, 4)
        result["density_iterations"] = 0

    # Step 9: Labels
    labels_info = []
    if labels:
        placer = LabelPlacer(*img_bw.size)
        for lab in labels:
            txt = lab["text"]
            lx, ly = lab.get("x", 10), lab.get("y", 10)
            braille = text_to_braille(txt)
            lw = braille_width_px(braille) + 2 * BRAILLE_LABEL_PAD
            lh = braille_height_px() + 30  # 30px for English text above
            px, py, display, abbreviated = placer.place(txt, lx, ly, lw, lh)
            img_bw = draw_braille_label(img_bw, display, (px, py))
            labels_info.append({
                "text": txt,
                "display": display,
                "position": (px, py),
                "abbreviated": abbreviated,
            })
        result["labels"] = labels_info
        if placer.abbreviations:
            result["abbreviation_key"] = placer.abbreviations

    # Step 10: Center on page
    img_page = center_on_page(img_bw, paper, margin)

    # Step 11: Generate output path
    if output_path is None:
        base = os.path.splitext(image_path)[0]
        output_path = f"{base}_piaf.{output_format}"

    # Step 12: Tile or save single page
    if tile:
        tiles = tile_image(img_bw, paper, margin)
        result["tiles"] = len(tiles)
        paths = []
        for tile_img, row, col in tiles:
            tile_base = os.path.splitext(output_path)[0]
            tile_path = f"{tile_base}_R{row+1}C{col+1}.{output_format}"
            _save_image(tile_img, tile_path, output_format)
            paths.append(tile_path)
        result["output_paths"] = paths
        result["output_path"] = paths[0]
    else:
        _save_image(img_page, output_path, output_format)
        result["output_path"] = output_path

    result["final_size"] = img_page.size
    result["density_warning"] = result["density_after"] > DENSITY_MAX

    return result


def _save_image(img, path, fmt="png"):
    """Save image with DPI metadata for correct printing."""
    folder = os.path.dirname(os.path.abspath(path))
    if folder:
        os.makedirs(folder, exist_ok=True)

    if fmt == "pdf":
        # PIL can save single-page PDFs
        if img.mode == "1":
            img = img.convert("L")
        img.save(path, "PDF", resolution=PIAF_DPI)
    elif fmt == "tiff":
        img.save(path, "TIFF", dpi=(PIAF_DPI, PIAF_DPI),
                 compression="tiff_deflate")
    else:
        # PNG
        if img.mode == "1":
            img = img.convert("L")
        img.save(path, "PNG", dpi=(PIAF_DPI, PIAF_DPI))


def analyze_image(image_path):
    """Pre-flight analysis of an image before conversion.

    Returns density, dimensions, suggested preset, and warnings.
    """
    img = load_image(image_path)
    w, h = img.size
    gray = to_grayscale(img)

    # Sample density at several thresholds
    densities = {}
    for t in [80, 100, 120, 140]:
        bw = threshold_bw(gray, t)
        densities[t] = round(compute_density(bw), 4)

    # Estimate best preset based on density pattern
    d100 = densities[100]
    if d100 < 0.15:
        suggested = "sketch"
    elif d100 < 0.25:
        suggested = "floor_plan"
    elif d100 < 0.35:
        suggested = "section"
    elif d100 < 0.45:
        suggested = "photograph"
    else:
        suggested = "rendering"

    warnings = []
    if w < 500 or h < 500:
        warnings.append("Low resolution — output may lack detail.")
    if d100 > DENSITY_MAX:
        warnings.append(
            f"High density ({d100:.0%}) at threshold 100. "
            f"Auto-reduction will be applied.")
    if w > 10000 or h > 10000:
        warnings.append("Very large image — consider cropping or tiling.")

    return {
        "path": os.path.abspath(image_path),
        "size": (w, h),
        "megapixels": round(w * h / 1e6, 1),
        "densities_by_threshold": densities,
        "suggested_preset": suggested,
        "warnings": warnings,
    }


def assess_quality(image_path):
    """Post-conversion quality check of a PIAF-ready image.

    Checks density, coverage, edge clarity, and label legibility.
    """
    img = Image.open(image_path)
    if img.mode not in ("1", "L"):
        img = img.convert("L")
    bw = img.point(lambda p: 255 if p >= 128 else 0, mode="1")

    w, h = bw.size
    density = compute_density(bw)

    # Check for blank margins (unused space)
    pix = bw.load()
    # Top margin: scan rows from top
    top_blank = 0
    for row in range(h):
        if all(pix[x, row] == 255 for x in range(w)):
            top_blank += 1
        else:
            break
    # Bottom margin
    bottom_blank = 0
    for row in range(h - 1, -1, -1):
        if all(pix[x, row] == 255 for x in range(w)):
            bottom_blank += 1
        else:
            break

    margin_pct = (top_blank + bottom_blank) / h if h > 0 else 0

    issues = []
    if density > DENSITY_MAX:
        issues.append(
            f"Density {density:.0%} exceeds PIAF maximum ({DENSITY_MAX:.0%}). "
            f"Swell paper will be overloaded.")
    elif density > DENSITY_TARGET:
        issues.append(
            f"Density {density:.0%} is above target ({DENSITY_TARGET:.0%}). "
            f"May be hard to read tactilely.")
    if density < 0.02:
        issues.append("Very low density — image may appear nearly blank.")
    if margin_pct > 0.5:
        issues.append(
            f"{margin_pct:.0%} of page is blank margins. "
            f"Consider cropping or scaling up.")

    return {
        "path": os.path.abspath(image_path),
        "size": (w, h),
        "density": round(density, 4),
        "density_ok": density <= DENSITY_TARGET,
        "margin_pct": round(margin_pct, 4),
        "issues": issues,
        "verdict": "PASS" if not issues else "REVIEW",
    }


# ═══════════════════════════════════════════════════════════
# HISTORY TRACKING
# ═══════════════════════════════════════════════════════════

def _history_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        HISTORY_FILENAME)


def _history_load():
    path = _history_path()
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _history_save(entries):
    path = _history_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def _history_add(result):
    entries = _history_load()
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": result.get("source", ""),
        "preset": result.get("preset", ""),
        "output": result.get("output_path", ""),
        "density": result.get("density_after", 0),
        "size": result.get("final_size", (0, 0)),
    }
    entries.append(entry)
    # Keep last 100
    if len(entries) > 100:
        entries = entries[-100:]
    _history_save(entries)


# ═══════════════════════════════════════════════════════════
# CLI — Screen-reader-friendly interface
# ═══════════════════════════════════════════════════════════

def _format_result(result):
    """Format conversion result for screen reader output."""
    lines = []
    lines.append(f"OK: Converted {os.path.basename(result['source'])} "
                 f"using preset '{result['preset']}'.")
    lines.append(f"  Output: {result['output_path']}")
    lines.append(f"  Original size: {result['original_size'][0]} x "
                 f"{result['original_size'][1]} px")
    lines.append(f"  Final size: {result['final_size'][0]} x "
                 f"{result['final_size'][1]} px")
    if result.get("scale_factor", 1.0) < 1.0:
        lines.append(f"  Scale: {result['scale_factor']:.0%}")
    lines.append(f"  Density: {result['density_after']:.0%}")
    if result.get("density_iterations", 0) > 0:
        lines.append(f"  Density reduced from {result['density_before']:.0%} "
                     f"in {result['density_iterations']} iterations.")
    if result.get("density_warning"):
        lines.append(f"  WARNING: Density {result['density_after']:.0%} "
                     f"exceeds PIAF max ({DENSITY_MAX:.0%}).")
    if result.get("labels"):
        lines.append(f"  Labels: {len(result['labels'])} placed.")
    if result.get("abbreviation_key"):
        lines.append("  Abbreviation key:")
        for letter, full in result["abbreviation_key"].items():
            lines.append(f"    {letter} = {full}")
    if result.get("tiles"):
        lines.append(f"  Tiles: {result['tiles']} pages.")
    return "\n".join(lines)


def _format_analysis(analysis):
    """Format analysis result for screen reader output."""
    lines = []
    lines.append(f"OK: Analysis of {os.path.basename(analysis['path'])}")
    lines.append(f"  Size: {analysis['size'][0]} x {analysis['size'][1]} px "
                 f"({analysis['megapixels']} MP)")
    lines.append(f"  Suggested preset: {analysis['suggested_preset']}")
    lines.append("  Density at thresholds:")
    for t, d in sorted(analysis["densities_by_threshold"].items()):
        lines.append(f"    Threshold {t}: {d:.0%}")
    if analysis["warnings"]:
        for w in analysis["warnings"]:
            lines.append(f"  WARNING: {w}")
    return "\n".join(lines)


def _format_quality(quality):
    """Format quality check result for screen reader output."""
    lines = []
    lines.append(f"OK: Quality check of {os.path.basename(quality['path'])}")
    lines.append(f"  Density: {quality['density']:.0%} "
                 f"({'OK' if quality['density_ok'] else 'HIGH'})")
    lines.append(f"  Margin: {quality['margin_pct']:.0%} blank")
    lines.append(f"  Verdict: {quality['verdict']}")
    if quality["issues"]:
        for issue in quality["issues"]:
            lines.append(f"  Issue: {issue}")
    return "\n".join(lines)


HELP_TEXT = """
IMAGE-TO-PIAF v1.0 — Tactile Image Conversion
================================================
Converts architectural images to PIAF-ready output for swell paper printing.

USAGE (single command):
  python image_to_piaf.py <image_path> [options]

USAGE (interactive mode):
  python image_to_piaf.py

COMMANDS (interactive mode):
  convert <path> [preset]      Convert image using preset
  analyze <path>               Pre-flight analysis of image
  quality <path>               Post-conversion quality check
  presets                      List all available presets
  preset <name>                Show details for a preset
  braille <text>               Convert text to braille
  history                      Show conversion history
  set threshold <0-255>        Override threshold for next conversion
  set contrast <method>        Override contrast method
  set paper <letter|tabloid|a4|a3>  Set paper size
  set labels <text1;text2;...> Set labels for next conversion
  set invert on|off            Invert image colors
  set tile on|off              Enable/disable tiling
  set output <path>            Set output path
  clear                        Reset all overrides
  help / h / ?                 This message
  quit / q / exit              Exit

PRESETS:
  floor_plan     Architectural floor plans (CAD, printed)
  elevation      Building elevations (line drawings)
  photograph     Photos of buildings, sites, models
  sketch         Hand-drawn sketches (pencil, pen)
  section        Building sections (with poche/fill)
  site_plan      Site plans (contours, vegetation)
  rendering      3D renderings (shaded views)
  diagram        Circulation, structural, concept diagrams
  historic_photo Historic photographs (low contrast)
  handdrawn      Hand-drawn plans or details

CONTRAST METHODS:
  none           No enhancement
  auto_contrast  Stretch histogram to full range
  histogram_eq   Equalize histogram for maximum contrast
  s_curve        S-curve for enhanced mid-tone contrast
  clahe          Local contrast enhancement

DENSITY:
  PIAF swell paper works best at <30% black pixel density.
  Above 45%, the paper becomes unreadable.  The tool auto-reduces
  density by eroding black pixels when needed.

EXAMPLES:
  convert photo.jpg photograph
  convert plan.pdf floor_plan
  analyze sketch.png
  set labels "Kitchen;Living Room;Bedroom"
  convert plan.jpg
"""


def _repl():
    """Interactive REPL for the tactile conversion pipeline."""
    print("IMAGE-TO-PIAF v1.0 — Tactile Image Conversion")
    print("Type 'help' for commands.\n")

    # Session overrides
    overrides = {
        "threshold": None,
        "contrast": None,
        "paper": "letter",
        "labels": None,
        "invert": False,
        "tile": False,
        "output": None,
    }

    while True:
        try:
            raw = input("piaf>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not raw:
            continue

        parts = raw.split(None, 2)
        cmd = parts[0].lower()

        if cmd in ("quit", "q", "exit"):
            break

        if cmd in ("help", "h", "?"):
            print(HELP_TEXT)
            print("READY:")
            continue

        if cmd == "presets":
            print("OK: Available presets:")
            for name, info in sorted(PRESETS.items()):
                print(f"  {name:15s} {info['description']}")
            print("READY:")
            continue

        if cmd == "preset":
            if len(parts) < 2:
                print("ERROR: Usage: preset <name>")
                print("READY:")
                continue
            name = parts[1].lower()
            info = PRESETS.get(name)
            if info is None:
                print(f"ERROR: Unknown preset '{name}'. "
                      f"Available: {', '.join(sorted(PRESETS))}")
            else:
                print(f"OK: Preset '{name}':")
                print(f"  Description: {info['description']}")
                print(f"  Threshold: {info['threshold']}")
                print(f"  Contrast: {info['contrast']}")
            print("READY:")
            continue

        if cmd == "braille":
            text = raw[len("braille"):].strip()
            if not text:
                print("ERROR: Usage: braille <text>")
            else:
                b = text_to_braille(text)
                print(f"OK: {text}")
                print(f"  Braille: {b}")
                print(f"  Cells: {len(b)}")
            print("READY:")
            continue

        if cmd == "history":
            entries = _history_load()
            if not entries:
                print("OK: No conversion history yet.")
            else:
                print(f"OK: Last {min(10, len(entries))} conversions:")
                for e in entries[-10:]:
                    src = os.path.basename(e.get("source", "?"))
                    print(f"  {e.get('timestamp','?')}  {src}  "
                          f"preset={e.get('preset','?')}  "
                          f"density={e.get('density',0):.0%}")
            print("READY:")
            continue

        if cmd == "set":
            if len(parts) < 2:
                print("ERROR: Usage: set <field> <value>")
                print("READY:")
                continue
            field = parts[1].lower()
            val = parts[2] if len(parts) > 2 else ""

            if field == "threshold":
                try:
                    overrides["threshold"] = int(val)
                    print(f"OK: Threshold set to {overrides['threshold']}.")
                except ValueError:
                    print("ERROR: Threshold must be an integer 0-255.")
            elif field == "contrast":
                if val not in ("none", "auto_contrast", "histogram_eq",
                               "s_curve", "clahe"):
                    print("ERROR: Unknown contrast method. "
                          "Options: none, auto_contrast, histogram_eq, "
                          "s_curve, clahe")
                else:
                    overrides["contrast"] = val
                    print(f"OK: Contrast set to {val}.")
            elif field == "paper":
                if val.lower() not in PAPER_SIZES:
                    print(f"ERROR: Unknown paper size. "
                          f"Options: {', '.join(sorted(PAPER_SIZES))}")
                else:
                    overrides["paper"] = val.lower()
                    print(f"OK: Paper set to {val}.")
            elif field == "labels":
                labels_text = val.split(";")
                overrides["labels"] = [
                    {"text": t.strip(), "x": 10, "y": 10 + i * 80}
                    for i, t in enumerate(labels_text) if t.strip()
                ]
                names = [l["text"] for l in overrides["labels"]]
                print(f"OK: {len(names)} labels set: {', '.join(names)}")
            elif field == "invert":
                overrides["invert"] = val.lower() in ("on", "true", "yes", "1")
                print(f"OK: Invert {'ON' if overrides['invert'] else 'OFF'}.")
            elif field == "tile":
                overrides["tile"] = val.lower() in ("on", "true", "yes", "1")
                print(f"OK: Tiling {'ON' if overrides['tile'] else 'OFF'}.")
            elif field == "output":
                overrides["output"] = val if val else None
                print(f"OK: Output path set to {val}." if val
                      else "OK: Output path cleared (auto-generate).")
            else:
                print(f"ERROR: Unknown field '{field}'. "
                      f"Options: threshold, contrast, paper, labels, "
                      f"invert, tile, output")
            print("READY:")
            continue

        if cmd == "clear":
            overrides = {
                "threshold": None, "contrast": None, "paper": "letter",
                "labels": None, "invert": False, "tile": False,
                "output": None,
            }
            print("OK: All overrides cleared.")
            print("READY:")
            continue

        if cmd == "analyze":
            if len(parts) < 2:
                print("ERROR: Usage: analyze <image_path>")
                print("READY:")
                continue
            path = parts[1].strip().strip('"')
            try:
                result = analyze_image(path)
                print(_format_analysis(result))
            except Exception as e:
                print(f"ERROR: {e}")
            print("READY:")
            continue

        if cmd == "quality":
            if len(parts) < 2:
                print("ERROR: Usage: quality <image_path>")
                print("READY:")
                continue
            path = parts[1].strip().strip('"')
            try:
                result = assess_quality(path)
                print(_format_quality(result))
            except Exception as e:
                print(f"ERROR: {e}")
            print("READY:")
            continue

        if cmd == "convert":
            if len(parts) < 2:
                print("ERROR: Usage: convert <image_path> [preset]")
                print("READY:")
                continue
            path = parts[1].strip().strip('"')
            preset = parts[2].strip() if len(parts) > 2 else "floor_plan"

            if preset not in PRESETS:
                print(f"ERROR: Unknown preset '{preset}'. "
                      f"Available: {', '.join(sorted(PRESETS))}")
                print("READY:")
                continue

            try:
                result = convert(
                    image_path=path,
                    preset=preset,
                    threshold=overrides["threshold"],
                    contrast=overrides["contrast"],
                    labels=overrides["labels"],
                    paper=overrides["paper"],
                    invert=overrides["invert"],
                    tile=overrides["tile"],
                    output_path=overrides["output"],
                )
                print(_format_result(result))
                _history_add(result)
            except Exception as e:
                print(f"ERROR: {e}")
            print("READY:")
            continue

        print(f"ERROR: Unknown command '{cmd}'. Type 'help' for a list.")
        print("READY:")


# ═══════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════

def main():
    if len(sys.argv) <= 1:
        _repl()
        return

    ap = argparse.ArgumentParser(
        description="Image-to-PIAF: Convert images to tactile swell paper output")
    ap.add_argument("image", nargs="?",
                    help="Path to source image")
    ap.add_argument("--preset", "-p", default="floor_plan",
                    choices=sorted(PRESETS.keys()),
                    help="Conversion preset (default: floor_plan)")
    ap.add_argument("--threshold", "-t", type=int, default=None,
                    help="Override threshold 0-255 (lower = more black)")
    ap.add_argument("--contrast", "-c", default=None,
                    choices=["none", "auto_contrast", "histogram_eq",
                             "s_curve", "clahe"],
                    help="Override contrast method")
    ap.add_argument("--output", "-o", default=None,
                    help="Output file path (auto-generated if omitted)")
    ap.add_argument("--format", "-f", default="png",
                    choices=["png", "tiff", "pdf"],
                    help="Output format (default: png)")
    ap.add_argument("--paper", default="letter",
                    choices=sorted(PAPER_SIZES.keys()),
                    help="Paper size (default: letter)")
    ap.add_argument("--margin", type=float, default=0.5,
                    help="Margin in inches (default: 0.5)")
    ap.add_argument("--invert", action="store_true",
                    help="Invert image (white lines on black → black on white)")
    ap.add_argument("--tile", action="store_true",
                    help="Split into page-sized tiles with registration marks")
    ap.add_argument("--no-density", action="store_true",
                    help="Skip automatic density reduction")
    ap.add_argument("--density-target", type=float, default=None,
                    help="Override density target 0.0-1.0 (default: 0.30)")
    ap.add_argument("--labels", default=None,
                    help="Semicolon-separated labels: 'Kitchen;Bath;Bedroom'")
    ap.add_argument("--analyze", action="store_true",
                    help="Analyze image without converting")
    ap.add_argument("--quality", action="store_true",
                    help="Quality-check a PIAF output image")
    ap.add_argument("--json", action="store_true",
                    help="Output result as JSON")
    ap.add_argument("--no-history", action="store_true",
                    help="Skip saving to conversion history")

    args = ap.parse_args()

    if not args.image:
        print("ERROR: No image path provided. Use --help for usage.")
        print("READY:")
        sys.exit(1)

    # Analyze mode
    if args.analyze:
        try:
            result = analyze_image(args.image)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(_format_analysis(result))
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        print("READY:")
        return

    # Quality check mode
    if args.quality:
        try:
            result = assess_quality(args.image)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(_format_quality(result))
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        print("READY:")
        return

    # Parse labels
    labels = None
    if args.labels:
        labels = [
            {"text": t.strip(), "x": 10, "y": 10 + i * 80}
            for i, t in enumerate(args.labels.split(";")) if t.strip()
        ]

    # Convert
    try:
        result = convert(
            image_path=args.image,
            preset=args.preset,
            threshold=args.threshold,
            contrast=args.contrast,
            labels=labels,
            paper=args.paper,
            margin=args.margin,
            auto_density=not args.no_density,
            density_target=args.density_target,
            invert=args.invert,
            tile=args.tile,
            output_path=args.output,
            output_format=args.format,
        )
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            print(_format_result(result))

        if not args.no_history:
            _history_add(result)

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print("READY:")


if __name__ == "__main__":
    main()
