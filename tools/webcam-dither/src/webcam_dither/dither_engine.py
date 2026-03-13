"""Dithering algorithms for real-time and screenshot use.

Three modes:
  halftone   — variable-size dots on a grid (dithertone style)
  ordered    — Bayer matrix threshold dithering
  floyd_steinberg — error-diffusion dithering (slow, screenshots only)
"""

import cv2
import numpy as np


# 8x8 Bayer threshold matrix (normalized to 0–255 range)
_BAYER_8X8 = (
    np.array(
        [
            [0, 48, 12, 60, 3, 51, 15, 63],
            [32, 16, 44, 28, 35, 19, 47, 31],
            [8, 56, 4, 52, 11, 59, 7, 55],
            [40, 24, 36, 20, 43, 27, 39, 23],
            [2, 50, 14, 62, 1, 49, 13, 61],
            [34, 18, 46, 30, 33, 17, 45, 29],
            [10, 58, 6, 54, 9, 57, 5, 53],
            [42, 26, 38, 22, 41, 25, 37, 21],
        ],
        dtype=np.float32,
    )
    / 64.0
    * 255.0
)


def adjust_brightness_contrast(gray, brightness=0, contrast=1.0):
    """Apply brightness and contrast adjustments to a grayscale image.

    Args:
        gray: uint8 grayscale numpy array.
        brightness: integer offset (-100 to 100).
        contrast: float multiplier (0.5 to 2.0).

    Returns:
        Adjusted uint8 grayscale array.
    """
    img = gray.astype(np.float32)
    img = img * contrast + brightness
    return np.clip(img, 0, 255).astype(np.uint8)


def halftone(gray, spacing=8, dot_scale=0.8, invert=False):
    """Render halftone dithertone pattern.

    Divides the image into a grid. Each cell gets a filled circle whose
    radius is proportional to local darkness (darker = bigger dot).

    Args:
        gray: uint8 grayscale numpy array (H, W).
        spacing: grid cell size in pixels.
        dot_scale: max dot radius as fraction of half-spacing.
        invert: if True, swap black/white.

    Returns:
        uint8 single-channel image (0 or 255 values).
    """
    h, w = gray.shape
    max_radius = max(1, int(spacing * dot_scale * 0.5))

    # Start with white canvas
    output = np.full((h, w), 255, dtype=np.uint8)

    # Compute cell centers and mean brightness per cell
    half = spacing // 2
    ys = np.arange(half, h, spacing)
    xs = np.arange(half, w, spacing)

    for cy in ys:
        y0 = max(0, cy - half)
        y1 = min(h, cy + half)
        for cx in xs:
            x0 = max(0, cx - half)
            x1 = min(w, cx + half)
            cell = gray[y0:y1, x0:x1]
            mean_val = cell.mean() / 255.0  # 0=black, 1=white
            darkness = 1.0 - mean_val
            radius = int(darkness * max_radius)
            if radius > 0:
                cv2.circle(output, (int(cx), int(cy)), radius, 0, -1)

    if invert:
        output = 255 - output

    return output


def ordered_dither(gray, invert=False):
    """Ordered dithering using 8x8 Bayer matrix.

    Fast, deterministic, good for real-time preview.

    Args:
        gray: uint8 grayscale numpy array.
        invert: if True, swap black/white.

    Returns:
        uint8 single-channel image (0 or 255 values).
    """
    h, w = gray.shape
    # Tile the Bayer matrix across the image
    bayer = np.tile(_BAYER_8X8, (h // 8 + 1, w // 8 + 1))[:h, :w]
    output = np.where(gray.astype(np.float32) > bayer, 255, 0).astype(np.uint8)

    if invert:
        output = 255 - output

    return output


def floyd_steinberg(gray, invert=False):
    """Floyd-Steinberg error diffusion dithering.

    Best quality but sequential — use for screenshots, not live preview.

    Args:
        gray: uint8 grayscale numpy array.
        invert: if True, swap black/white.

    Returns:
        uint8 single-channel image (0 or 255 values).
    """
    img = gray.astype(np.float32).copy()
    h, w = img.shape

    for y in range(h):
        for x in range(w):
            old = img[y, x]
            new = 255.0 if old > 127.0 else 0.0
            img[y, x] = new
            err = old - new

            if x + 1 < w:
                img[y, x + 1] += err * 7.0 / 16.0
            if y + 1 < h:
                if x - 1 >= 0:
                    img[y + 1, x - 1] += err * 3.0 / 16.0
                img[y + 1, x] += err * 5.0 / 16.0
                if x + 1 < w:
                    img[y + 1, x + 1] += err * 1.0 / 16.0

    output = np.clip(img, 0, 255).astype(np.uint8)

    if invert:
        output = 255 - output

    return output


ALGORITHMS = {
    "halftone": halftone,
    "ordered": ordered_dither,
    "floyd_steinberg": floyd_steinberg,
}

ALGORITHM_NAMES = {
    "halftone": "Halftone (dithertone)",
    "ordered": "Ordered (Bayer 8x8)",
    "floyd_steinberg": "Floyd-Steinberg (slow)",
}


def dither(gray, algorithm="halftone", spacing=8, dot_scale=0.8,
           brightness=0, contrast=1.0, invert=False):
    """Apply dithering with pre-processing.

    Args:
        gray: uint8 grayscale numpy array.
        algorithm: one of "halftone", "ordered", "floyd_steinberg".
        spacing: grid spacing for halftone mode.
        dot_scale: dot size scale for halftone mode.
        brightness: brightness offset.
        contrast: contrast multiplier.
        invert: swap black/white.

    Returns:
        uint8 single-channel dithered image.
    """
    adjusted = adjust_brightness_contrast(gray, brightness, contrast)

    if algorithm == "halftone":
        return halftone(adjusted, spacing=spacing, dot_scale=dot_scale, invert=invert)
    elif algorithm == "ordered":
        return ordered_dither(adjusted, invert=invert)
    elif algorithm == "floyd_steinberg":
        return floyd_steinberg(adjusted, invert=invert)
    else:
        raise ValueError("Unknown algorithm: {}".format(algorithm))
