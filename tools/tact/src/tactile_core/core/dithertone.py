"""
Dithertone — dot-grid halftone renderer for tactile images.

Replaces simple binary thresholding with a dot grid where dot size
maps to local brightness, preserving tonal gradation in PIAF output.

Five dot shapes are available: circle, square, cross, triangle, dash.
Parameters are tunable: spacing, radius range, gamma, grid angle, invert.
"""

import math
from dataclasses import dataclass, replace
from typing import List

import numpy as np
from PIL import Image, ImageDraw


VALID_SHAPES = ("circle", "square", "cross", "triangle", "dash")


@dataclass
class DithertoneConfig:
    """Configuration for dithertone dot-grid rendering.

    Attributes:
        dot_shape: Shape of each dot. One of circle, square, cross, triangle, dash.
        dot_spacing: Center-to-center distance between dots in pixels.
        min_radius: Minimum dot radius (for brightest areas) in pixels.
        max_radius: Maximum dot radius (for darkest areas) in pixels.
        gamma: Gamma curve exponent for brightness mapping.
            >1 darkens midtones, <1 lightens midtones.
        angle: Grid rotation angle in degrees. 45 is classic halftone.
        invert: If True, bright areas get large dots and dark areas get small dots.
    """
    dot_shape: str = "circle"
    dot_spacing: int = 12
    min_radius: float = 1.0
    max_radius: float = 5.0
    gamma: float = 1.0
    angle: float = 45.0
    invert: bool = False

    def __post_init__(self):
        if self.dot_shape not in VALID_SHAPES:
            raise ValueError(
                f"Invalid dot_shape '{self.dot_shape}'. "
                f"Must be one of: {', '.join(VALID_SHAPES)}"
            )
        if self.dot_spacing < 2:
            raise ValueError("dot_spacing must be at least 2 pixels")
        if self.min_radius < 0:
            raise ValueError("min_radius must be non-negative")
        if self.max_radius <= self.min_radius:
            raise ValueError("max_radius must be greater than min_radius")
        if self.gamma <= 0:
            raise ValueError("gamma must be positive")


class DithertoneRenderer:
    """Renders a grayscale image as a dot-grid halftone.

    Each grid point samples the local brightness and draws a dot
    whose size is proportional to that brightness value.
    """

    def __init__(self, config: DithertoneConfig = None):
        self.config = config or DithertoneConfig()

    def render(self, image: Image.Image) -> Image.Image:
        """Convert a grayscale image to a dithertone dot-grid image.

        Args:
            image: Grayscale PIL Image (mode 'L').

        Returns:
            1-bit B&W PIL Image (mode '1') with dot-grid halftone.
        """
        if image.mode != 'L':
            image = image.convert('L')

        width, height = image.size
        img_array = np.array(image, dtype=np.float64)

        # Create white canvas in grayscale, then convert to 1-bit at the end
        output = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(output)

        # Build rotated grid of dot centers
        centers = self._build_grid(width, height)

        # Shape dispatch
        draw_fn = self._get_draw_fn()

        for cx, cy in centers:
            # Sample brightness at grid point (clamp to image bounds)
            ix = max(0, min(int(round(cx)), width - 1))
            iy = max(0, min(int(round(cy)), height - 1))
            brightness = img_array[iy, ix]

            radius = self._brightness_to_radius(brightness)

            # Skip dots that are too small to render
            if radius < 0.3:
                continue

            draw_fn(draw, cx, cy, radius)

        # Convert to 1-bit
        return output.convert('1')

    def _build_grid(self, width: int, height: int) -> List:
        """Build a rotated grid of dot center positions.

        Returns a list of (x, y) tuples covering the image area.
        """
        spacing = self.config.dot_spacing
        angle_rad = math.radians(self.config.angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        # Expand grid bounds to cover the image after rotation
        diagonal = math.sqrt(width * width + height * height)
        half_diag = diagonal / 2.0
        cx_img = width / 2.0
        cy_img = height / 2.0

        n_cols = int(math.ceil(diagonal / spacing)) + 2
        n_rows = int(math.ceil(diagonal / spacing)) + 2

        centers = []
        for row in range(-n_rows // 2, n_rows // 2 + 1):
            for col in range(-n_cols // 2, n_cols // 2 + 1):
                # Grid position before rotation
                gx = col * spacing
                gy = row * spacing

                # Rotate around origin
                rx = gx * cos_a - gy * sin_a
                ry = gx * sin_a + gy * cos_a

                # Translate to image center
                px = rx + cx_img
                py = ry + cy_img

                # Keep only points within image bounds (with margin for dot size)
                margin = self.config.max_radius
                if -margin <= px < width + margin and -margin <= py < height + margin:
                    centers.append((px, py))

        return centers

    def _brightness_to_radius(self, brightness: float) -> float:
        """Map a brightness value (0-255) to a dot radius.

        Dark pixels (0) get large dots, bright pixels (255) get small dots.
        Gamma controls the curve shape.

        Args:
            brightness: Pixel value 0 (black) to 255 (white).

        Returns:
            Dot radius in pixels.
        """
        # Normalize to 0-1
        t = brightness / 255.0

        if self.config.invert:
            # Invert: bright = large dots
            darkness = t
        else:
            # Normal: dark = large dots
            darkness = 1.0 - t

        # Apply gamma curve
        darkness = math.pow(darkness, self.config.gamma)

        # Map to radius range
        return self.config.min_radius + darkness * (self.config.max_radius - self.config.min_radius)

    def _get_draw_fn(self):
        """Return the drawing function for the configured dot shape."""
        dispatch = {
            "circle": self._draw_circle,
            "square": self._draw_square,
            "cross": self._draw_cross,
            "triangle": self._draw_triangle,
            "dash": self._draw_dash,
        }
        return dispatch[self.config.dot_shape]

    def _draw_circle(self, draw: ImageDraw.Draw, cx: float, cy: float, radius: float):
        """Draw a filled circle dot."""
        x0 = cx - radius
        y0 = cy - radius
        x1 = cx + radius
        y1 = cy + radius
        draw.ellipse([x0, y0, x1, y1], fill=0)

    def _draw_square(self, draw: ImageDraw.Draw, cx: float, cy: float, radius: float):
        """Draw a filled square dot."""
        x0 = cx - radius
        y0 = cy - radius
        x1 = cx + radius
        y1 = cy + radius
        draw.rectangle([x0, y0, x1, y1], fill=0)

    def _draw_cross(self, draw: ImageDraw.Draw, cx: float, cy: float, radius: float):
        """Draw a cross/plus shape."""
        arm_width = max(1.0, radius * 0.4)
        # Horizontal arm
        draw.rectangle([cx - radius, cy - arm_width, cx + radius, cy + arm_width], fill=0)
        # Vertical arm
        draw.rectangle([cx - arm_width, cy - radius, cx + arm_width, cy + radius], fill=0)

    def _draw_triangle(self, draw: ImageDraw.Draw, cx: float, cy: float, radius: float):
        """Draw an equilateral triangle pointing up."""
        # Triangle vertices
        top = (cx, cy - radius)
        bottom_left = (cx - radius * 0.866, cy + radius * 0.5)
        bottom_right = (cx + radius * 0.866, cy + radius * 0.5)
        draw.polygon([top, bottom_left, bottom_right], fill=0)

    def _draw_dash(self, draw: ImageDraw.Draw, cx: float, cy: float, radius: float):
        """Draw a horizontal dash."""
        dash_height = max(1.0, radius * 0.35)
        draw.rectangle([cx - radius, cy - dash_height, cx + radius, cy + dash_height], fill=0)


def bracket_configs(base_config: DithertoneConfig) -> List[DithertoneConfig]:
    """Generate three spacing variants for quick PIAF testing.

    Returns:
        List of [tight, medium, loose] DithertoneConfig instances.
        Tight uses 70% spacing, medium is unchanged, loose uses 140% spacing.
    """
    tight_spacing = max(2, int(round(base_config.dot_spacing * 0.7)))
    loose_spacing = int(round(base_config.dot_spacing * 1.4))

    tight = replace(base_config, dot_spacing=tight_spacing)
    medium = replace(base_config)  # unchanged copy
    loose = replace(base_config, dot_spacing=loose_spacing)

    return [tight, medium, loose]
