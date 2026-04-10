"""
RainbowTact: Color-to-Tactile Pattern Conversion.

Implements the RainbowTact algorithm (Ka & Kim, ICCHP 2024) which translates
color into distinguishable tactile patterns — waves for chromatic colors,
dots for achromatic — enabling blind users to perceive color through touch.

All pattern parameters are tuned for PIAF's ~20 DPI tactile resolution
at 300 DPI output.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import numpy as np
import cv2
from PIL import Image
import logging

logger = logging.getLogger("tactile.rainbowtact")


@dataclass
class RainbowTactConfig:
    """PIAF-tuned defaults for RainbowTact conversion."""
    # Number of color clusters for K-means segmentation
    num_colors: int = 5

    # Minimum region size as percentage of total image area
    min_region_percent: float = 0.5

    # Chromatic vs achromatic threshold (HSV saturation 0-255)
    saturation_threshold: int = 30

    # Wave pattern constraints (chromatic colors)
    min_wavelength: int = 90     # px (~8mm at 300 DPI) — minimum distinguishable period
    max_wavelength: int = 300    # px (~25mm)
    min_amplitude: int = 6       # px (~0.5mm) — minimum raised height
    max_amplitude: int = 30      # px (~2.5mm)
    min_line_width: int = 6      # px (~0.5mm) — reliably raised on PIAF
    max_line_width: int = 18     # px (~1.5mm)

    # Dot pattern constraints (achromatic colors)
    min_dot_spacing: int = 45    # px (~4mm) — individually tactile
    max_dot_spacing: int = 120   # px (~10mm)
    min_dot_radius: int = 4      # px (~0.3mm)
    max_dot_radius: int = 12     # px (~1mm)

    # Boundary rendering
    boundary_width: int = 4      # px — contour line width

    # Hue merge threshold (degrees, wraps at 360)
    hue_merge_threshold: int = 15

    # K-means parameters
    kmeans_attempts: int = 10
    kmeans_max_iter: int = 100
    kmeans_epsilon: float = 0.2


@dataclass
class ColorRegion:
    """A segmented color region with classification."""
    cluster_id: int
    hsv_center: Tuple[int, int, int]  # (H 0-179, S 0-255, V 0-255)
    mask: np.ndarray                   # Boolean mask (H x W)
    is_chromatic: bool
    color_name: str
    pixel_count: int


@dataclass
class TactilePattern:
    """Tactile pattern assigned to a color region."""
    region_id: int
    color_name: str
    is_chromatic: bool

    # Wave params (chromatic only)
    wavelength: Optional[int] = None
    amplitude: Optional[int] = None
    line_width: Optional[int] = None

    # Dot params (achromatic only)
    dot_spacing: Optional[int] = None
    dot_radius: Optional[int] = None

    # Whether this region is left empty (white/very light)
    is_empty: bool = False


class RainbowTactConverter:
    """Converts color images to tactile patterns using the RainbowTact method."""

    def __init__(self, config: Optional[RainbowTactConfig] = None):
        self.config = config or RainbowTactConfig()

    def convert(self, image: Image.Image) -> Tuple[Image.Image, List[ColorRegion], List[TactilePattern]]:
        """
        Main entry point. Convert a color image to a tactile pattern image.

        Args:
            image: RGB PIL Image

        Returns:
            Tuple of:
                - 1-bit B&W PIL Image with tactile patterns
                - List of ColorRegion metadata
                - List of TactilePattern metadata (for legend)
        """
        # Ensure RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')

        img_array = np.array(image)
        height, width = img_array.shape[:2]

        # Step 1: Segment colors
        regions = self.segment_colors(img_array)
        logger.info(f"Segmented into {len(regions)} color regions")

        # Step 2: Assign tactile patterns
        patterns = self.assign_patterns(regions)
        logger.info(f"Assigned {len(patterns)} tactile patterns")

        # Step 3: Render patterns to B&W image
        output = self.render_patterns(regions, patterns, width, height)
        logger.info(f"Rendered tactile output {width}x{height}")

        # Convert to PIL 1-bit image
        pil_output = Image.fromarray(output, mode='L').convert('1')

        return pil_output, regions, patterns

    def segment_colors(self, img_array: np.ndarray) -> List[ColorRegion]:
        """
        Segment image into color regions using K-means clustering on HSV.

        Args:
            img_array: RGB image as numpy array (H x W x 3)

        Returns:
            List of ColorRegion objects
        """
        height, width = img_array.shape[:2]
        total_pixels = height * width
        min_pixels = int(total_pixels * self.config.min_region_percent / 100)

        # Convert to HSV
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)

        # Reshape for K-means: (N, 3) float32
        pixels = hsv.reshape(-1, 3).astype(np.float32)

        # K-means clustering
        criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            self.config.kmeans_max_iter,
            self.config.kmeans_epsilon
        )
        _, labels, centers = cv2.kmeans(
            pixels,
            self.config.num_colors,
            None,
            criteria,
            self.config.kmeans_attempts,
            cv2.KMEANS_PP_CENTERS
        )

        labels = labels.flatten().reshape(height, width)
        centers = centers.astype(int)

        # Merge similar hues (with circular wrapping)
        centers, labels = self._merge_similar_hues(centers, labels)

        # Build regions, filtering small ones
        regions = []
        for cluster_id in range(len(centers)):
            mask = labels == cluster_id
            pixel_count = int(np.sum(mask))

            if pixel_count < min_pixels:
                continue

            h, s, v = int(centers[cluster_id][0]), int(centers[cluster_id][1]), int(centers[cluster_id][2])
            is_chromatic = s > self.config.saturation_threshold
            color_name = self._name_color(h, s, v)

            regions.append(ColorRegion(
                cluster_id=cluster_id,
                hsv_center=(h, s, v),
                mask=mask,
                is_chromatic=is_chromatic,
                color_name=color_name,
                pixel_count=pixel_count
            ))

        # Sort by pixel count descending (largest regions first)
        regions.sort(key=lambda r: r.pixel_count, reverse=True)

        return regions

    def _merge_similar_hues(
        self, centers: np.ndarray, labels: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Merge clusters with similar hues, respecting circular hue wrapping."""
        threshold = self.config.hue_merge_threshold
        n = len(centers)
        merged_to = list(range(n))  # Maps each cluster to its merge target

        for i in range(n):
            for j in range(i + 1, n):
                if merged_to[j] != j:
                    continue  # Already merged

                # Both must be chromatic to merge by hue
                si, sj = centers[i][1], centers[j][1]
                if si <= self.config.saturation_threshold or sj <= self.config.saturation_threshold:
                    continue

                # Circular hue distance (OpenCV hue is 0-179)
                hi, hj = centers[i][0], centers[j][0]
                hue_diff = min(abs(hi - hj), 180 - abs(hi - hj))

                if hue_diff < threshold:
                    merged_to[j] = i

        # Remap labels
        for j in range(n):
            if merged_to[j] != j:
                labels[labels == j] = merged_to[j]

        # Rebuild centers for merged clusters (weighted average)
        new_centers = []
        new_id_map = {}
        new_id = 0
        for i in range(n):
            if merged_to[i] == i:
                mask = labels == i
                count = np.sum(mask)
                if count > 0:
                    new_id_map[i] = new_id
                    new_centers.append(centers[i])
                    new_id += 1

        # Remap labels to contiguous IDs
        new_labels = np.full_like(labels, -1)
        for old_id, nid in new_id_map.items():
            new_labels[labels == old_id] = nid

        # Assign any unmapped pixels to nearest cluster
        unmapped = new_labels == -1
        if np.any(unmapped):
            new_labels[unmapped] = 0

        return np.array(new_centers, dtype=np.float32), new_labels

    def assign_patterns(self, regions: List[ColorRegion]) -> List[TactilePattern]:
        """
        Assign tactile patterns to color regions based on HSV values.

        Chromatic: Hue -> wavelength, Saturation -> amplitude, Value -> line_width
        Achromatic: Value -> dot_spacing + dot_radius; white = empty

        Args:
            regions: List of ColorRegion objects

        Returns:
            List of TactilePattern objects
        """
        cfg = self.config
        patterns = []

        for idx, region in enumerate(regions):
            h, s, v = region.hsv_center

            if region.is_chromatic:
                # Hue (0-179 in OpenCV) -> wavelength
                # Map full hue range to wavelength range
                hue_norm = h / 179.0
                wavelength = int(cfg.min_wavelength + hue_norm * (cfg.max_wavelength - cfg.min_wavelength))

                # Saturation (0-255) -> amplitude
                sat_norm = s / 255.0
                amplitude = int(cfg.min_amplitude + sat_norm * (cfg.max_amplitude - cfg.min_amplitude))

                # Value (0-255) -> line_width (inverted: darker = thicker)
                val_norm = 1.0 - (v / 255.0)
                line_width = int(cfg.min_line_width + val_norm * (cfg.max_line_width - cfg.min_line_width))

                patterns.append(TactilePattern(
                    region_id=idx,
                    color_name=region.color_name,
                    is_chromatic=True,
                    wavelength=wavelength,
                    amplitude=amplitude,
                    line_width=line_width,
                ))
            else:
                # Achromatic region
                # Very light (white-ish): leave empty
                if v > 230:
                    patterns.append(TactilePattern(
                        region_id=idx,
                        color_name=region.color_name,
                        is_chromatic=False,
                        is_empty=True,
                    ))
                    continue

                # Value -> dot spacing and radius (darker = denser, larger dots)
                val_norm = 1.0 - (v / 255.0)  # 0 = white, 1 = black
                dot_spacing = int(cfg.max_dot_spacing - val_norm * (cfg.max_dot_spacing - cfg.min_dot_spacing))
                dot_radius = int(cfg.min_dot_radius + val_norm * (cfg.max_dot_radius - cfg.min_dot_radius))

                patterns.append(TactilePattern(
                    region_id=idx,
                    color_name=region.color_name,
                    is_chromatic=False,
                    dot_spacing=dot_spacing,
                    dot_radius=dot_radius,
                ))

        return patterns

    def render_patterns(
        self,
        regions: List[ColorRegion],
        patterns: List[TactilePattern],
        width: int,
        height: int
    ) -> np.ndarray:
        """
        Render tactile patterns to a B&W image.

        Args:
            regions: List of ColorRegion objects
            patterns: List of TactilePattern objects
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            uint8 numpy array (H x W), 0=black, 255=white
        """
        # Start with white canvas
        output = np.full((height, width), 255, dtype=np.uint8)

        for region, pattern in zip(regions, patterns):
            if pattern.is_empty:
                continue

            mask = region.mask

            if pattern.is_chromatic and pattern.wavelength:
                self._render_waves(output, mask, pattern)
            elif not pattern.is_chromatic and pattern.dot_spacing:
                self._render_dots(output, mask, pattern)

        # Draw region boundaries
        self._render_boundaries(output, regions)

        return output

    def _render_waves(self, output: np.ndarray, mask: np.ndarray, pattern: TactilePattern):
        """
        Render wave pattern within a masked region using vectorized math.

        The wave centerline follows y = A * sin(2*pi/lambda * x).
        Pixels within line_width/2 of the centerline are black.
        """
        height, width = output.shape
        wl = pattern.wavelength
        amp = pattern.amplitude
        lw = pattern.line_width

        # Get bounding box of mask for efficiency
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        if not np.any(rows) or not np.any(cols):
            return

        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]

        # Create coordinate grids for the bounding box
        y_coords = np.arange(rmin, rmax + 1)
        x_coords = np.arange(cmin, cmax + 1)
        xx, yy = np.meshgrid(x_coords, y_coords)

        # Wave centerline: y_center = amp * sin(2*pi/wl * x) + offset
        # We tile waves vertically with spacing = 2*amplitude + line_width
        wave_period_y = 2 * amp + lw + 10  # Vertical spacing between wave rows

        # Distance of each pixel from nearest wave centerline
        # Modular arithmetic for tiling
        y_mod = (yy - rmin) % wave_period_y
        # Centerline of the nearest wave at this y_mod position
        wave_y = amp * np.sin(2 * np.pi / wl * xx)
        # Shift wave center to middle of the period
        centerline_y = wave_period_y / 2.0

        # Distance from pixel to nearest point on the sinusoidal centerline
        dist = np.abs(y_mod - centerline_y - wave_y)

        # Pixels within half line_width are black
        wave_mask = dist <= (lw / 2.0)

        # Apply only within the region mask (crop to bounding box)
        region_crop = mask[rmin:rmax + 1, cmin:cmax + 1]
        combined = wave_mask & region_crop

        # Write to output
        output[rmin:rmax + 1, cmin:cmax + 1][combined] = 0

    def _render_dots(self, output: np.ndarray, mask: np.ndarray, pattern: TactilePattern):
        """
        Render dot grid pattern within a masked region.
        """
        height, width = output.shape
        spacing = pattern.dot_spacing
        radius = pattern.dot_radius

        # Get bounding box of mask
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        if not np.any(rows) or not np.any(cols):
            return

        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]

        # Create temporary layer for dots
        dot_layer = np.full((height, width), 255, dtype=np.uint8)

        # Generate dot grid positions
        for y in range(rmin + spacing // 2, rmax + 1, spacing):
            for x in range(cmin + spacing // 2, cmax + 1, spacing):
                if mask[y, x]:
                    cv2.circle(dot_layer, (x, y), radius, 0, -1)

        # Composite: only apply dots within the mask
        masked_dots = (dot_layer == 0) & mask
        output[masked_dots] = 0

    def _render_boundaries(self, output: np.ndarray, regions: List[ColorRegion]):
        """Draw region boundaries using contours."""
        bw = self.config.boundary_width

        for region in regions:
            mask_uint8 = region.mask.astype(np.uint8) * 255
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(output, contours, -1, 0, bw)

    def _name_color(self, h: int, s: int, v: int) -> str:
        """
        Convert HSV values to a human-readable color name.

        Args:
            h: Hue (0-179, OpenCV scale)
            s: Saturation (0-255)
            v: Value (0-255)

        Returns:
            Human-readable color name like "Dark Blue", "Light Gray"
        """
        # Achromatic colors
        if s <= self.config.saturation_threshold:
            if v > 230:
                return "White"
            elif v > 180:
                return "Light Gray"
            elif v > 100:
                return "Gray"
            elif v > 50:
                return "Dark Gray"
            else:
                return "Black"

        # Chromatic: determine base hue name
        # OpenCV hue: 0-179 (0-360 degrees / 2)
        if h < 8 or h >= 170:
            base = "Red"
        elif h < 22:
            base = "Orange"
        elif h < 33:
            base = "Yellow"
        elif h < 45:
            base = "Yellow-Green"
        elif h < 75:
            base = "Green"
        elif h < 95:
            base = "Cyan"
        elif h < 125:
            base = "Blue"
        elif h < 145:
            base = "Purple"
        elif h < 170:
            base = "Magenta"
        else:
            base = "Red"

        # Add lightness/darkness modifier
        if v < 80:
            return f"Dark {base}"
        elif v > 200 and s < 100:
            return f"Light {base}"
        elif s < 80:
            return f"Muted {base}"
        else:
            return base
