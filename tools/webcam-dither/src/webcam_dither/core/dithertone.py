"""Dithertone rendering engine.

Converts grayscale images to dot patterns where dot size varies with
local brightness. Darker areas produce bigger dots, lighter areas
produce smaller or no dots. This preserves tonal gradation in a
format suitable for PIAF swell paper.
"""

from dataclasses import dataclass, field
import cv2
import numpy as np


@dataclass
class DithertoneParams:
    """Tunable parameters for dithertone rendering."""

    spacing: int = 8
    min_radius: float = 0.5
    max_radius_factor: float = 0.45
    contrast: float = 0.0
    brightness: float = 0.0
    invert: bool = False
    gamma: float = 1.0

    # Clamping ranges
    SPACING_MIN: int = field(default=3, repr=False)
    SPACING_MAX: int = field(default=40, repr=False)
    GAMMA_MIN: float = field(default=0.2, repr=False)
    GAMMA_MAX: float = field(default=5.0, repr=False)
    CONTRAST_MIN: float = field(default=-100.0, repr=False)
    CONTRAST_MAX: float = field(default=100.0, repr=False)
    BRIGHTNESS_MIN: float = field(default=-100.0, repr=False)
    BRIGHTNESS_MAX: float = field(default=100.0, repr=False)

    def clamp(self):
        """Clamp all values to valid ranges."""
        self.spacing = max(self.SPACING_MIN, min(self.SPACING_MAX, self.spacing))
        self.gamma = max(self.GAMMA_MIN, min(self.GAMMA_MAX, self.gamma))
        self.contrast = max(self.CONTRAST_MIN, min(self.CONTRAST_MAX, self.contrast))
        self.brightness = max(self.BRIGHTNESS_MIN, min(self.BRIGHTNESS_MAX, self.brightness))
        self.max_radius_factor = max(0.1, min(0.5, self.max_radius_factor))


class DithertoneRenderer:
    """Renders grayscale images as dithertone dot patterns.

    Each frame is processed by placing dots on a regular grid.
    Dot radius at each grid point is proportional to the darkness
    of the underlying pixel.
    """

    def __init__(self, params=None):
        self.params = params or DithertoneParams()
        self._gamma_lut = None
        self._last_gamma = None

    def _build_gamma_lut(self, gamma):
        """Build a lookup table for gamma correction."""
        if self._last_gamma == gamma:
            return self._gamma_lut
        inv_gamma = 1.0 / gamma
        lut = np.array([
            int(((i / 255.0) ** inv_gamma) * 255)
            for i in range(256)
        ], dtype=np.uint8)
        self._gamma_lut = lut
        self._last_gamma = gamma
        return lut

    def _apply_adjustments(self, gray):
        """Apply brightness, contrast, and gamma to a grayscale image."""
        img = gray.astype(np.float32)

        # Brightness
        if self.params.brightness != 0.0:
            img = img + self.params.brightness

        # Contrast (percentage-based around midpoint)
        if self.params.contrast != 0.0:
            factor = (100.0 + self.params.contrast) / 100.0
            img = 128.0 + factor * (img - 128.0)

        img = np.clip(img, 0, 255).astype(np.uint8)

        # Gamma
        if self.params.gamma != 1.0:
            lut = self._build_gamma_lut(self.params.gamma)
            img = cv2.LUT(img, lut)

        return img

    def render(self, gray_frame):
        """Render a grayscale frame as a dithertone dot pattern.

        Args:
            gray_frame: numpy array, single-channel grayscale (0-255).

        Returns:
            numpy array, single-channel output image with dot pattern.
        """
        p = self.params
        h, w = gray_frame.shape[:2]

        # Apply brightness/contrast/gamma
        adjusted = self._apply_adjustments(gray_frame)

        # Create output canvas
        if p.invert:
            canvas = np.zeros((h, w), dtype=np.uint8)
            dot_color = 255
        else:
            canvas = np.full((h, w), 255, dtype=np.uint8)
            dot_color = 0

        max_radius = p.spacing * p.max_radius_factor

        # Generate grid coordinates
        half = p.spacing // 2
        ys = np.arange(half, h, p.spacing)
        xs = np.arange(half, w, p.spacing)

        # Sample brightness at all grid points at once
        ys_clipped = np.clip(ys, 0, h - 1)
        xs_clipped = np.clip(xs, 0, w - 1)
        grid_y, grid_x = np.meshgrid(ys_clipped, xs_clipped, indexing='ij')
        brightness_vals = adjusted[grid_y, grid_x]

        # Calculate radii: darker pixels (lower value) -> larger dots
        if p.invert:
            # In invert mode, lighter pixels get bigger dots
            radii = max_radius * (brightness_vals / 255.0)
        else:
            radii = max_radius * (1.0 - brightness_vals / 255.0)

        # Draw dots where radius exceeds minimum
        for iy in range(len(ys)):
            for ix in range(len(xs)):
                r = radii[iy, ix]
                if r > p.min_radius:
                    cv2.circle(
                        canvas,
                        (int(xs[ix]), int(ys[iy])),
                        max(1, int(round(r))),
                        int(dot_color),
                        -1,
                        lineType=cv2.LINE_AA,
                    )

        return canvas

    def adjust_spacing(self, delta):
        """Change grid spacing by delta pixels."""
        self.params.spacing += delta
        self.params.clamp()

    def adjust_contrast(self, delta):
        """Change contrast by delta."""
        self.params.contrast += delta
        self.params.clamp()

    def adjust_brightness(self, delta):
        """Change brightness by delta."""
        self.params.brightness += delta
        self.params.clamp()

    def adjust_gamma(self, delta):
        """Change gamma by delta."""
        self.params.gamma += delta
        self.params.gamma = round(self.params.gamma, 2)
        self.params.clamp()

    def toggle_invert(self):
        """Toggle invert mode."""
        self.params.invert = not self.params.invert

    def reset(self):
        """Reset all parameters to defaults."""
        self.params = DithertoneParams()
        self._gamma_lut = None
        self._last_gamma = None

    def get_status_text(self):
        """Return a single-line summary of current parameters."""
        p = self.params
        inv = "ON" if p.invert else "OFF"
        return (
            f"Spacing:{p.spacing}  "
            f"Gamma:{p.gamma:.1f}  "
            f"Contrast:{p.contrast:.0f}  "
            f"Brightness:{p.brightness:.0f}  "
            f"Invert:{inv}"
        )

    def clone_with_spacing(self, new_spacing):
        """Return a new renderer with different spacing but same other params."""
        new_params = DithertoneParams(
            spacing=new_spacing,
            min_radius=self.params.min_radius,
            max_radius_factor=self.params.max_radius_factor,
            contrast=self.params.contrast,
            brightness=self.params.brightness,
            invert=self.params.invert,
            gamma=self.params.gamma,
        )
        new_params.clamp()
        return DithertoneRenderer(new_params)
