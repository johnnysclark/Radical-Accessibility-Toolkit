"""
Contrast enhancement module.

Provides curves adjustments and histogram manipulation for improving
image contrast before threshold conversion.
"""

import numpy as np
from PIL import Image
import cv2
from typing import Optional, Tuple

from tactile_core.utils.logger import AccessibleLogger


class ContrastEnhancer:
    """
    Contrast enhancement for grayscale images.

    Provides:
    - S-curve tone adjustment (like Photoshop curves)
    - Histogram equalization
    - CLAHE (Contrast Limited Adaptive Histogram Equalization)
    - Auto-contrast
    """

    def __init__(self, logger: Optional[AccessibleLogger] = None):
        """
        Initialize contrast enhancer.

        Args:
            logger: Optional AccessibleLogger instance
        """
        self.logger = logger or AccessibleLogger(verbose=False)

    def apply_s_curve(self, image: Image.Image, strength: float = 1.0) -> Image.Image:
        """
        Apply an S-curve to enhance midtone contrast.

        This increases contrast in midtones while preserving detail in
        shadows and highlights, similar to a classic Photoshop S-curve.

        Args:
            image: Grayscale PIL Image (mode 'L')
            strength: Curve strength 0.0-2.0 (default 1.0)
                     0.0 = no adjustment
                     1.0 = standard S-curve
                     2.0 = aggressive S-curve

        Returns:
            Enhanced PIL Image
        """
        self.logger.progress(f"Applying S-curve enhancement (strength: {strength:.1f})")

        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32)

        # Normalize to 0-1 range
        normalized = img_array / 255.0

        # Apply S-curve using a sigmoid-based transformation
        # The S-curve formula: f(x) = 1 / (1 + exp(-k * (x - 0.5)))
        # Adjusted to maintain 0-1 range

        if strength == 0.0:
            # No adjustment
            adjusted = normalized
        else:
            # Adjust steepness based on strength
            k = 4.0 * strength  # Steepness factor

            # Apply sigmoid S-curve
            # Shift input to center at 0, apply sigmoid, rescale to 0-1
            adjusted = 1.0 / (1.0 + np.exp(-k * (normalized - 0.5)))

            # Normalize to maintain 0-1 range
            # The sigmoid doesn't naturally hit 0 and 1, so we rescale
            min_val = 1.0 / (1.0 + np.exp(k * 0.5))
            max_val = 1.0 / (1.0 + np.exp(-k * 0.5))
            adjusted = (adjusted - min_val) / (max_val - min_val)

        # Convert back to 0-255 range
        result = (adjusted * 255).astype(np.uint8)

        self.logger.info("S-curve applied - enhanced midtone contrast")

        return Image.fromarray(result, mode='L')

    def apply_custom_curve(self, image: Image.Image,
                          shadows: int = 0, midtones: int = 128,
                          highlights: int = 255) -> Image.Image:
        """
        Apply a custom curve with adjustable shadow, midtone, and highlight points.

        Args:
            image: Grayscale PIL Image (mode 'L')
            shadows: Output value for darkest pixels (0-255, default 0)
            midtones: Output value for middle gray (0-255, default 128)
            highlights: Output value for brightest pixels (0-255, default 255)

        Returns:
            Enhanced PIL Image
        """
        self.logger.progress("Applying custom curve adjustment")

        # Create a lookup table for the curve
        # We'll use quadratic interpolation for smooth curves
        lut = np.zeros(256, dtype=np.uint8)

        # Three control points: (0, shadows), (128, midtones), (255, highlights)
        # Use quadratic Bezier curve for smooth interpolation

        for i in range(256):
            t = i / 255.0

            # Quadratic Bezier: B(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂
            # where P₀=(0, shadows), P₁=(128, midtones), P₂=(255, highlights)

            if i <= 128:
                # First half: from shadows to midtones
                t_local = i / 128.0
                output = ((1 - t_local)**2 * shadows +
                         2 * (1 - t_local) * t_local * midtones +
                         t_local**2 * midtones)
            else:
                # Second half: from midtones to highlights
                t_local = (i - 128) / 127.0
                output = ((1 - t_local)**2 * midtones +
                         2 * (1 - t_local) * t_local * highlights +
                         t_local**2 * highlights)

            lut[i] = int(np.clip(output, 0, 255))

        # Apply lookup table
        img_array = np.array(image)
        result = lut[img_array]

        self.logger.info(f"Custom curve applied (shadows:{shadows}, mid:{midtones}, high:{highlights})")

        return Image.fromarray(result, mode='L')

    def auto_contrast(self, image: Image.Image, cutoff: float = 2.0) -> Image.Image:
        """
        Automatically adjust contrast by stretching histogram.

        Args:
            image: Grayscale PIL Image (mode 'L')
            cutoff: Percentage of darkest/lightest pixels to ignore (default 2.0)

        Returns:
            Enhanced PIL Image
        """
        self.logger.progress("Applying auto-contrast")

        img_array = np.array(image)

        # Calculate histogram
        hist, bins = np.histogram(img_array.flatten(), bins=256, range=(0, 256))

        # Calculate cumulative distribution
        cdf = hist.cumsum()
        total_pixels = cdf[-1]

        # Find the cutoff points (ignore outliers)
        cutoff_pixels = int(total_pixels * cutoff / 100.0)

        # Find min and max values (excluding cutoff percentiles)
        vmin = np.searchsorted(cdf, cutoff_pixels)
        vmax = np.searchsorted(cdf, total_pixels - cutoff_pixels)

        # Ensure valid range
        if vmax <= vmin:
            self.logger.info("Auto-contrast: Image already has good contrast")
            return image

        # Stretch histogram to full 0-255 range
        img_float = img_array.astype(np.float32)
        stretched = (img_float - vmin) * (255.0 / (vmax - vmin))
        result = np.clip(stretched, 0, 255).astype(np.uint8)

        self.logger.info(f"Auto-contrast applied (stretched {vmin}-{vmax} to 0-255)")

        return Image.fromarray(result, mode='L')

    def histogram_equalization(self, image: Image.Image) -> Image.Image:
        """
        Apply histogram equalization for global contrast enhancement.

        Args:
            image: Grayscale PIL Image (mode 'L')

        Returns:
            Enhanced PIL Image
        """
        self.logger.progress("Applying histogram equalization")

        img_array = np.array(image)

        # Apply OpenCV histogram equalization
        equalized = cv2.equalizeHist(img_array)

        self.logger.info("Histogram equalization applied")

        return Image.fromarray(equalized, mode='L')

    def clahe(self, image: Image.Image, clip_limit: float = 2.0,
             tile_size: int = 8) -> Image.Image:
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).

        Better than regular histogram equalization for images with varying
        lighting conditions. Good for photographs.

        Args:
            image: Grayscale PIL Image (mode 'L')
            clip_limit: Contrast limiting threshold (default 2.0)
            tile_size: Size of grid for local equalization (default 8)

        Returns:
            Enhanced PIL Image
        """
        self.logger.progress(f"Applying CLAHE (adaptive contrast enhancement)")

        img_array = np.array(image)

        # Create CLAHE object
        clahe = cv2.createCLAHE(clipLimit=clip_limit,
                                tileGridSize=(tile_size, tile_size))

        # Apply CLAHE
        enhanced = clahe.apply(img_array)

        self.logger.info("CLAHE applied - local contrast enhanced")

        return Image.fromarray(enhanced, mode='L')

    def analyze_histogram(self, image: Image.Image) -> dict:
        """
        Analyze image histogram to suggest optimal enhancements.

        Args:
            image: Grayscale PIL Image (mode 'L')

        Returns:
            Dictionary with histogram statistics and recommendations
        """
        img_array = np.array(image)

        # Calculate histogram
        hist, bins = np.histogram(img_array.flatten(), bins=256, range=(0, 256))

        # Calculate statistics
        mean = np.mean(img_array)
        std = np.std(img_array)
        min_val = np.min(img_array)
        max_val = np.max(img_array)

        # Check for contrast issues
        dynamic_range = max_val - min_val
        low_contrast = dynamic_range < 128

        # Check for brightness issues
        too_dark = mean < 85
        too_bright = mean > 170

        # Generate recommendations
        recommendations = []

        if low_contrast:
            recommendations.append("Low contrast detected - recommend S-curve or auto-contrast")

        if too_dark:
            recommendations.append("Image is dark - recommend increasing midtones")
        elif too_bright:
            recommendations.append("Image is bright - recommend decreasing midtones")

        if std < 40:
            recommendations.append("Low variation - recommend CLAHE for local enhancement")

        return {
            'mean': float(mean),
            'std': float(std),
            'min': int(min_val),
            'max': int(max_val),
            'dynamic_range': int(dynamic_range),
            'low_contrast': low_contrast,
            'recommendations': recommendations
        }

    def auto_enhance(self, image: Image.Image, method: str = 's_curve') -> Image.Image:
        """
        Automatically enhance image using specified method.

        Args:
            image: Grayscale PIL Image (mode 'L')
            method: Enhancement method ('s_curve', 'auto_contrast', 'clahe', 'histogram')

        Returns:
            Enhanced PIL Image
        """
        if method == 's_curve':
            return self.apply_s_curve(image, strength=1.0)
        elif method == 'auto_contrast':
            return self.auto_contrast(image)
        elif method == 'clahe':
            return self.clahe(image)
        elif method == 'histogram':
            return self.histogram_equalization(image)
        else:
            self.logger.warning(f"Unknown enhancement method: {method}")
            return image
