"""
Label scaler module for analyzing Braille label fit within original text bounding boxes.

This module provides functionality to determine whether Braille conversions of detected
text will fit within the original text's bounding box dimensions, and calculates
scaling recommendations when they don't fit.
"""

import logging
from typing import Dict, List, Optional, Tuple

from tactile_core.core.braille_converter import (
    BrailleConverter, BrailleConfig,
    BRAILLE_DPI, BRAILLE_FONT_SIZE_POINTS, BRAILLE_FONT_SIZE_PX, BRAILLE_CHAR_WIDTH_PX,
)
from tactile_core.core.text_detector import DetectedText


__all__ = ["analyze_label_fit"]


# Re-export under local names used throughout this file
DPI = BRAILLE_DPI
FONT_SIZE_POINTS = BRAILLE_FONT_SIZE_POINTS
FONT_SIZE_PX = BRAILLE_FONT_SIZE_PX
CHAR_WIDTH_PX = BRAILLE_CHAR_WIDTH_PX
BRAILLE_HEIGHT_PX = BRAILLE_FONT_SIZE_PX

# Scaling constraints
MIN_TEXT_HEIGHT_THRESHOLD = 4  # Don't trust bounding boxes smaller than 4px
MAX_SCALE_CAP = 500  # Maximum scale percentage (5x)


class _SilentLogger:
    """A silent logger that suppresses all output."""
    def debug(self, *args, **kwargs): pass
    def info(self, *args, **kwargs): pass
    def warning(self, *args, **kwargs): pass
    def error(self, *args, **kwargs): pass
    def success(self, *args, **kwargs): pass
    def step(self, *args, **kwargs): pass
    def verbose(self, *args, **kwargs): pass


def _create_braille_converter(grade: int = 2) -> BrailleConverter:
    """Create a BrailleConverter with default config for label width estimation."""
    config = BrailleConfig(
        enabled=True,
        grade=grade,
        placement="overlay",
        font_name="DejaVu Sans",
        font_size=FONT_SIZE_POINTS,
        offset_x=5,
        offset_y=-24,
        max_label_length=30,
        truncate_suffix="...",
        font_color="black",
        detect_overlaps=True,
        min_label_spacing=6
    )
    return BrailleConverter(config, _SilentLogger())


def analyze_label_fit(
    detected_texts: List[DetectedText],
    image_size: Tuple[int, int],
    braille_grade: int = 2,
    max_scale_factor: Optional[float] = None,
) -> Dict:
    """
    Analyze whether Braille labels will fit within their original text bounding boxes.

    Uses HEIGHT-BASED scaling: Scale the image when Braille height exceeds the
    original bounding box height. After scaling, width is checked for abbreviation.

    Algorithm:
    1. For each detected text, calculate required scale so Braille height fits
    2. Required scale = BRAILLE_HEIGHT_PX / original_bounding_box_height
    3. Take the maximum scale across all labels (so ALL labels fit)
    4. Cap at MAX_SCALE_CAP (400%) or max_scale_factor if provided
    5. Track which labels will need width-based abbreviation after scaling

    Args:
        detected_texts: List of DetectedText objects containing text and bounding box info.
        image_size: Tuple of (width, height) of the source image in pixels.
        braille_grade: Braille grade to use for conversion (1 or 2). Default is 2.
        max_scale_factor: Optional cap on scale factor (e.g., 4.0 = 400%).
                          If None, uses MAX_SCALE_CAP.

    Returns:
        A dictionary containing:
            - fits_height: List of DetectedText where Braille height fits without scaling
            - needs_scaling: List of DetectedText that require image scaling
            - needs_abbreviation: List of DetectedText that need abbreviation after scaling
            - height_ratios: Dict mapping text to (braille_height / original_height)
            - width_ratios: Dict mapping text to (braille_width / scaled_original_width)
            - recommended_scale: The scale percentage to make all Braille heights fit
            - capped: True if recommended_scale was capped at max
            - fits: (Legacy) alias for fits_height
            - needs_key: (Legacy) alias for needs_abbreviation
            - fit_ratios: (Legacy) alias for height_ratios

    Example:
        >>> from tactile_core.core.text_detector import DetectedText
        >>> texts = [
        ...     DetectedText(text="Room", x=100, y=100, width=80, height=20, confidence=0.95),
        ...     DetectedText(text="Kitchen", x=200, y=200, width=50, height=20, confidence=0.90),
        ... ]
        >>> result = analyze_label_fit(texts, image_size=(1000, 800))
        >>> print(f"Labels that fit height: {len(result['fits_height'])}")
        >>> print(f"Labels needing abbreviation: {len(result['needs_abbreviation'])}")
        >>> print(f"Recommended scale: {result['recommended_scale']}%")
    """
    converter = _create_braille_converter(braille_grade)

    fits_height: List[DetectedText] = []
    needs_scaling: List[DetectedText] = []
    needs_abbreviation: List[DetectedText] = []
    height_ratios: Dict[str, float] = {}
    width_ratios: Dict[str, float] = {}
    max_height_ratio: float = 1.0

    # Determine effective max scale
    effective_max_scale = (max_scale_factor * 100) if max_scale_factor else MAX_SCALE_CAP

    # First pass: analyze height-based scaling needs
    for detected in detected_texts:
        # Skip texts with unreliable bounding boxes (too small)
        if detected.height < MIN_TEXT_HEIGHT_THRESHOLD:
            continue

        # Get original text bounding box height
        original_height = detected.height

        # Calculate HEIGHT ratio (braille_height / original_height)
        # This tells us: "How much taller is Braille than original text?"
        # If ratio > 1.0, we need to scale the image UP by this ratio
        if original_height > 0:
            height_ratio = BRAILLE_HEIGHT_PX / original_height
        else:
            height_ratio = float("inf") if BRAILLE_HEIGHT_PX > 0 else 1.0

        height_ratios[detected.text] = height_ratio

        # Track maximum height ratio for recommended scale
        if height_ratio != float("inf"):
            max_height_ratio = max(max_height_ratio, height_ratio)

        # Categorize based on height fit
        if height_ratio <= 1.0:
            fits_height.append(detected)
        else:
            needs_scaling.append(detected)

    # Calculate recommended scale (as percentage)
    raw_scale = max_height_ratio * 100
    capped = raw_scale > effective_max_scale
    recommended_scale = min(raw_scale, effective_max_scale)

    # Second pass: check width-based abbreviation needs after scaling
    scale_factor = recommended_scale / 100
    for detected in detected_texts:
        if detected.height < MIN_TEXT_HEIGHT_THRESHOLD:
            continue

        # Convert original text to Braille
        braille_text = converter.convert_text(detected.text)
        braille_width = len(braille_text) * CHAR_WIDTH_PX

        # After scaling, original width becomes: original_width * scale_factor
        scaled_original_width = detected.width * scale_factor

        # Calculate width ratio after scaling
        if scaled_original_width > 0:
            width_ratio = braille_width / scaled_original_width
        else:
            width_ratio = float("inf") if braille_width > 0 else 1.0

        width_ratios[detected.text] = width_ratio

        # If Braille is still wider than scaled bounding box, needs abbreviation
        if width_ratio > 1.0:
            needs_abbreviation.append(detected)

    return {
        # New fields
        "fits_height": fits_height,
        "needs_scaling": needs_scaling,
        "needs_abbreviation": needs_abbreviation,
        "height_ratios": height_ratios,
        "width_ratios": width_ratios,
        "recommended_scale": recommended_scale,
        "capped": capped,
        # Legacy aliases for backward compatibility
        "fits": fits_height,
        "needs_key": needs_abbreviation,
        "fit_ratios": height_ratios,
    }
