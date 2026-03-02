# -*- coding: utf-8 -*-
"""
Image Converter — Convert images to PIAF-ready B&W  v1.0
=========================================================
Takes any image (photo, sketch, CAD export) and converts it to
high-contrast black-and-white output suitable for PIAF swell-paper
printing at 300 DPI.

Pipeline:
  Load → Grayscale → Enhancement → Threshold → Density check → Output

Part of the Radical Accessibility Project — UIUC School of Architecture.

Dependencies:  Pillow (PIL)
Optional:      opencv-python (CLAHE), numpy (faster density calc)
"""

import os

from PIL import Image, ImageEnhance, ImageOps

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_DPI = 300

PAPER_SIZES_PX = {
    "letter":  (int(8.5 * 300), int(11.0 * 300)),    # 2550 x 3300
    "tabloid": (int(11.0 * 300), int(17.0 * 300)),    # 3300 x 5100
}

SUPPORTED_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".tiff", ".tif",
    ".bmp", ".gif", ".webp",
)

# Presets adapted from Ethan's fabric-accessible-graphics presets.yaml
PRESETS = {
    "floor_plan": {
        "name": "Floor Plan",
        "description": "Architectural floor plans with walls and dimensions",
        "threshold": 140,
        "enhance": "s_curve",
        "enhance_strength": 1.0,
        "max_density": 40,
    },
    "elevation": {
        "name": "Building Elevation",
        "description": "Building elevations and section drawings",
        "threshold": 135,
        "enhance": "s_curve",
        "enhance_strength": 1.0,
        "max_density": 35,
    },
    "section": {
        "name": "Section Drawing",
        "description": "Building sections with material hatching",
        "threshold": 145,
        "enhance": "s_curve",
        "enhance_strength": 1.2,
        "max_density": 35,
    },
    "photograph": {
        "name": "Photograph",
        "description": "Photos of buildings, models, or sites",
        "threshold": 120,
        "enhance": "clahe",
        "enhance_strength": 1.0,
        "max_density": 30,
    },
    "sketch": {
        "name": "Hand Sketch",
        "description": "Hand-drawn sketches with pencil or pen",
        "threshold": 130,
        "enhance": "s_curve",
        "enhance_strength": 1.3,
        "max_density": 35,
    },
    "technical_drawing": {
        "name": "Technical Drawing",
        "description": "CAD-generated technical drawings with crisp lines",
        "threshold": 150,
        "enhance": None,
        "enhance_strength": 1.0,
        "max_density": 45,
    },
    "diagram": {
        "name": "Diagram",
        "description": "Conceptual and bubble diagrams",
        "threshold": 135,
        "enhance": "auto_contrast",
        "enhance_strength": 1.0,
        "max_density": 35,
    },
    "site_plan": {
        "name": "Site Plan",
        "description": "Site plans with landscape and topography",
        "threshold": 140,
        "enhance": "s_curve",
        "enhance_strength": 1.0,
        "max_density": 38,
    },
    "detail_drawing": {
        "name": "Detail Drawing",
        "description": "Construction details and enlarged views",
        "threshold": 145,
        "enhance": "s_curve",
        "enhance_strength": 1.1,
        "max_density": 40,
    },
    "presentation": {
        "name": "Presentation Board",
        "description": "Presentation boards with mixed content",
        "threshold": 125,
        "enhance": "clahe",
        "enhance_strength": 1.0,
        "max_density": 32,
    },
}

DEFAULT_PRESET = "floor_plan"


# ---------------------------------------------------------------------------
# Enhancement functions
# ---------------------------------------------------------------------------

def _enhance_s_curve(image, strength=1.0):
    """Apply S-curve contrast enhancement using PIL."""
    # Boost contrast via ImageEnhance
    enhancer = ImageEnhance.Contrast(image)
    enhanced = enhancer.enhance(1.0 + strength * 0.5)
    # Apply S-curve via point transform
    # S-curve: darker darks, lighter lights
    lut = []
    for i in range(256):
        normalized = i / 255.0
        # Sigmoid-like S-curve
        curved = 1.0 / (1.0 + ((1.0 - normalized) / max(normalized, 0.001)) ** (1.0 + strength))
        lut.append(int(curved * 255))
    return enhanced.point(lut)


def _enhance_auto_contrast(image):
    """Apply auto-contrast using PIL ImageOps."""
    return ImageOps.autocontrast(image, cutoff=1)


def _enhance_clahe(image):
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).

    Requires opencv-python.  Falls back to auto_contrast if unavailable.
    """
    try:
        import cv2
        import numpy as np
        img_array = np.array(image)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        result = clahe.apply(img_array)
        return Image.fromarray(result, mode='L')
    except ImportError:
        # Graceful fallback
        return _enhance_auto_contrast(image)


# ---------------------------------------------------------------------------
# Core conversion
# ---------------------------------------------------------------------------

def load_image(path):
    """Load an image file.

    Args:
        path: Path to image file.

    Returns:
        PIL.Image object.

    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If file format is unsupported.
    """
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise FileNotFoundError("Image not found: {}".format(path))
    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported format '{}'. Supported: {}".format(
                ext, ", ".join(SUPPORTED_EXTENSIONS)))
    img = Image.open(path)
    if img.mode not in ('RGB', 'L', '1'):
        img = img.convert('RGB')
    return img


def to_grayscale(image):
    """Convert image to grayscale."""
    if image.mode == 'L':
        return image
    return image.convert('L')


def apply_threshold(image, threshold=128):
    """Convert grayscale image to pure B&W.

    Args:
        image:     Grayscale PIL.Image.
        threshold: 0-255. Pixels above → white, below → black.

    Returns:
        PIL.Image in mode '1'.
    """
    return image.point(lambda px: 255 if px > threshold else 0, mode='1')


def calculate_density(image):
    """Calculate black pixel density percentage.

    Args:
        image: PIL.Image (any mode, converted to '1' internally).

    Returns:
        Float percentage (0-100).
    """
    if image.mode != '1':
        image = image.convert('1')
    total = image.size[0] * image.size[1]
    if total == 0:
        return 0.0
    # In mode '1', 0 is black
    black = sum(1 for px in image.getdata() if px == 0)
    return (black / total) * 100.0


def check_density(image, max_density=45.0, warn_threshold=40.0):
    """Check if density is within acceptable range.

    Returns:
        Tuple of (is_ok, density_pct, message).
    """
    d = calculate_density(image)
    if d > max_density:
        return (False, d,
                "Density {:.1f}% exceeds maximum {:.0f}%. "
                "Lower the threshold or simplify the image.".format(d, max_density))
    if d > warn_threshold:
        return (True, d,
                "Density {:.1f}% is high (target <{:.0f}%). "
                "Consider lowering threshold.".format(d, warn_threshold))
    return (True, d, "Density {:.1f}% — within range.".format(d))


def scale_to_paper(image, paper_size="letter", dpi=DEFAULT_DPI):
    """Scale image to fit paper at specified DPI.

    Maintains aspect ratio.  Fits within margins.

    Returns:
        Scaled PIL.Image.
    """
    margin_px = int(0.5 * dpi)  # 0.5 inch margin
    target_w, target_h = PAPER_SIZES_PX.get(paper_size, PAPER_SIZES_PX["letter"])
    draw_w = target_w - 2 * margin_px
    draw_h = target_h - 2 * margin_px

    img_w, img_h = image.size
    scale = min(draw_w / img_w, draw_h / img_h)

    if scale >= 1.0:
        # Image fits without scaling
        return image

    new_w = int(img_w * scale)
    new_h = int(img_h * scale)
    return image.resize((new_w, new_h), Image.Resampling.LANCZOS)


def get_preset(name):
    """Get a preset by name.

    Returns:
        Preset dict, or None if not found.
    """
    return PRESETS.get(name)


def list_presets():
    """List all available presets.

    Returns:
        List of (name, description) tuples.
    """
    result = []
    for name, preset in sorted(PRESETS.items()):
        result.append((name, preset["description"]))
    return result


# ---------------------------------------------------------------------------
# Main conversion pipeline
# ---------------------------------------------------------------------------

def convert(input_path, output_path=None, preset=DEFAULT_PRESET,
            threshold=None, enhance=None, enhance_strength=None,
            paper_size="letter", dpi=DEFAULT_DPI):
    """Convert an image to PIAF-ready B&W output.

    Args:
        input_path:       Path to input image.
        output_path:      Path for output file (default: input_tactile.png).
        preset:           Preset name (overridden by explicit threshold/enhance).
        threshold:        B&W threshold 0-255 (overrides preset).
        enhance:          Enhancement method (overrides preset).
        enhance_strength: Enhancement strength (overrides preset).
        paper_size:       "letter" or "tabloid".
        dpi:              Output DPI (default 300).

    Returns:
        Dict with keys: output_path, density, width, height, preset_used, message.

    Raises:
        FileNotFoundError: If input file not found.
        ValueError: If format unsupported.
    """
    # Load preset
    p = PRESETS.get(preset, PRESETS[DEFAULT_PRESET])
    if threshold is None:
        threshold = p["threshold"]
    if enhance is None:
        enhance = p["enhance"]
    if enhance_strength is None:
        enhance_strength = p.get("enhance_strength", 1.0)
    max_density = p.get("max_density", 45)

    # Default output path
    if output_path is None:
        base = os.path.splitext(input_path)[0]
        output_path = base + "_tactile.png"

    # Pipeline
    img = load_image(input_path)
    gray = to_grayscale(img)

    # Enhancement
    if enhance == "s_curve":
        gray = _enhance_s_curve(gray, enhance_strength)
    elif enhance == "auto_contrast":
        gray = _enhance_auto_contrast(gray)
    elif enhance == "clahe":
        gray = _enhance_clahe(gray)

    # Threshold
    bw = apply_threshold(gray, threshold)

    # Scale to paper
    bw = scale_to_paper(bw, paper_size, dpi)

    # Density check
    ok, d, msg = check_density(bw, max_density=max_density)

    # Save
    bw.save(output_path, dpi=(dpi, dpi))

    return {
        "output_path": os.path.abspath(output_path),
        "density": d,
        "width": bw.size[0],
        "height": bw.size[1],
        "threshold": threshold,
        "preset_used": preset,
        "density_ok": ok,
        "message": msg,
    }
