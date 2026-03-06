"""
Core image processing module.

Handles loading, converting, and processing images for PIAF output.
"""

from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np
from PIL import Image
import cv2

from tactile_core.utils.logger import AccessibleLogger
from tactile_core.utils.validators import validate_image_file
from tactile_core.core.contrast import ContrastEnhancer
from tactile_core.core.text_detector import TextDetector, TextDetectionConfig, DetectedText
from tactile_core.core.braille_converter import BRAILLE_DPI, BRAILLE_FONT_SIZE_POINTS
from tactile_core.core.rainbowtact import RainbowTactConverter, RainbowTactConfig, ColorRegion, TactilePattern


class ImageProcessorError(Exception):
    """Custom exception for image processing errors."""
    pass


class ImageProcessor:
    """
    Core image processor for converting images to high-contrast B&W format.

    This class handles:
    - Loading images from various formats
    - Converting to grayscale
    - Applying threshold for B&W conversion
    - Basic density checking
    """

    def __init__(self, config: Optional[dict] = None, logger: Optional[AccessibleLogger] = None):
        """
        Initialize image processor.

        Args:
            config: Optional configuration dictionary (from tactile_standards.yaml)
            logger: Optional AccessibleLogger instance
        """
        self.config = config or {}
        self.logger = logger or AccessibleLogger(verbose=False)
        self.contrast_enhancer = ContrastEnhancer(logger=self.logger)

        # Initialize text detector if enabled in config
        text_config = self.config.get('text_detection', {})
        if text_config.get('enabled', False):
            try:
                self.text_detector = TextDetector(
                    config=TextDetectionConfig(**text_config),
                    logger=self.logger
                )
            except Exception as e:
                self.logger.warning(f"Text detection initialization failed: {e}")
                self.logger.info("Text detection will be disabled")
                self.text_detector = None
        else:
            self.text_detector = None

    def load_image(self, image_path: str) -> Image.Image:
        """
        Load an image from file.

        Args:
            image_path: Path to image file

        Returns:
            PIL Image object

        Raises:
            ImageProcessorError: If image cannot be loaded
        """
        # Validate file first
        is_valid, error_msg = validate_image_file(image_path)
        if not is_valid:
            raise ImageProcessorError(error_msg)

        self.logger.loading(f"{Path(image_path).name}")

        try:
            image = Image.open(image_path)
            # Convert to RGB if necessary (handles CMYK, palette mode, etc.)
            if image.mode not in ('RGB', 'L', '1'):
                image = image.convert('RGB')

            width, height = image.size
            self.logger.info(f"Image loaded: {width}x{height} pixels, mode: {image.mode}")

            return image

        except Exception as e:
            raise ImageProcessorError(f"Failed to load image: {str(e)}") from e

    def convert_to_grayscale(self, image: Image.Image) -> Image.Image:
        """
        Convert image to grayscale.

        Args:
            image: PIL Image object

        Returns:
            Grayscale PIL Image
        """
        if image.mode == 'L':
            self.logger.info("Image already in grayscale")
            return image

        self.logger.progress("Converting to grayscale")
        return image.convert('L')

    def apply_threshold(self, image: Image.Image, threshold: int = 128) -> Image.Image:
        """
        Apply threshold to convert grayscale image to pure B&W.

        Args:
            image: Grayscale PIL Image
            threshold: Threshold value (0-255). Pixels above this become white, below become black

        Returns:
            1-bit B&W PIL Image
        """
        self.logger.progress(f"Applying threshold: {threshold}")

        # Convert to numpy array for processing
        img_array = np.array(image)

        # Apply threshold
        bw_array = (img_array > threshold).astype(np.uint8) * 255

        # Convert back to PIL Image
        bw_image = Image.fromarray(bw_array, mode='L')

        # Convert to 1-bit mode (pure B&W)
        bw_image = bw_image.convert('1')

        return bw_image

    def whiteout_braille_regions(self, image: Image.Image, braille_labels: list,
                                 font_size: int = BRAILLE_FONT_SIZE_POINTS, padding: int = 2) -> Image.Image:
        """
        White out regions where Braille labels will be placed.

        This prevents original image content from swelling during PIAF printing and
        obscuring the Braille dots. The whiteout is sized based on the Braille label
        dimensions, not the original text.

        Args:
            image: B&W PIL Image (mode '1' or 'L')
            braille_labels: List of BrailleLabel objects with positions and text
            font_size: Font size in points for Braille text
            padding: Pixels of padding around each label region (default: 2)

        Returns:
            Modified PIL Image with Braille label regions whited out
        """
        if not braille_labels:
            return image

        self.logger.progress("Clearing space for Braille labels")

        # Convert to numpy array for efficient manipulation
        # Mode '1' images need special handling
        if image.mode == '1':
            # Convert to 'L' mode for easier manipulation, then back to '1'
            img_array = np.array(image.convert('L'))
        else:
            img_array = np.array(image)

        # Get image dimensions
        height, width = img_array.shape

        # Convert font size from points to pixels at 300 DPI
        pixels_per_point = BRAILLE_DPI / 72
        font_size_px = int(font_size * pixels_per_point)

        # White out each Braille label region
        regions_whited = 0
        for label in braille_labels:
            # Calculate bounding box based on Braille text dimensions
            # The label.width should already be calculated correctly in pixels by BrailleConverter
            if hasattr(label, 'width') and label.width:
                label_width = label.width
            else:
                # Fallback: estimate if width is not available
                # Each Braille character is approximately 0.6 * font_size pixels
                label_width = int(len(label.braille_text) * font_size_px * 0.6)

            # Height is approximately the font size in pixels
            label_height = font_size_px

            # Calculate padded bounding box
            x_start = max(0, label.x - padding)
            y_start = max(0, label.y - padding)
            x_end = min(width, label.x + label_width + padding)
            y_end = min(height, label.y + label_height + padding)

            # Set region to white (255)
            img_array[y_start:y_end, x_start:x_end] = 255
            regions_whited += 1

        self.logger.info(f"Cleared {regions_whited} region(s) for Braille labels")

        # Convert back to PIL Image
        result_image = Image.fromarray(img_array, mode='L')

        # Convert back to original mode if needed
        if image.mode == '1':
            result_image = result_image.convert('1')

        return result_image

    def whiteout_text_regions(self, image: Image.Image, detected_texts: list,
                              padding: int = 5) -> Image.Image:
        """
        White out detected text regions using exact OCR bounding boxes.

        This removes original text from the image so Braille labels can be
        placed on clean white space, preventing text from obscuring Braille
        during PIAF printing.

        Args:
            image: B&W PIL Image (mode '1' or 'L')
            detected_texts: List of DetectedText objects with exact bounding boxes
            padding: Pixels of padding around each text region (default: 5)

        Returns:
            Modified PIL Image with text regions whited out
        """
        if not detected_texts:
            return image

        self.logger.progress("Removing original text regions")

        # Convert to numpy array for efficient manipulation
        if image.mode == '1':
            img_array = np.array(image.convert('L'))
        else:
            img_array = np.array(image)

        # Get image dimensions
        height, width = img_array.shape

        # White out each text region using exact OCR bounding boxes
        regions_whited = 0
        for text in detected_texts:
            # Use exact bounding box from OCR (no estimation needed)
            x_start = max(0, text.x - padding)
            y_start = max(0, text.y - padding)
            x_end = min(width, text.x + text.width + padding)
            y_end = min(height, text.y + text.height + padding)

            # Set region to white (255)
            img_array[y_start:y_end, x_start:x_end] = 255
            regions_whited += 1

        self.logger.info(f"Whited out {regions_whited} text region(s)")

        # Convert back to PIL Image
        result_image = Image.fromarray(img_array, mode='L')

        # Convert back to original mode if needed
        if image.mode == '1':
            result_image = result_image.convert('1')

        return result_image

    def calculate_density(self, image: Image.Image) -> float:
        """
        Calculate the percentage of black pixels in the image.

        Args:
            image: B&W PIL Image

        Returns:
            Percentage of black pixels (0-100)
        """
        # Convert to numpy array
        img_array = np.array(image)

        # For 1-bit images, False/0 is black, True/255 is white
        # Count black pixels
        if image.mode == '1':
            # In mode '1', False (0) is black
            black_pixels = np.sum(img_array == 0)
        else:
            # In mode 'L', 0 is black
            black_pixels = np.sum(img_array == 0)

        total_pixels = img_array.size
        density = (black_pixels / total_pixels) * 100

        return density

    def check_density(self, image: Image.Image, max_density: float = 45.0,
                     warning_threshold: float = 40.0) -> Tuple[bool, float]:
        """
        Check if image density is within acceptable range.

        Args:
            image: B&W PIL Image
            max_density: Maximum acceptable density percentage
            warning_threshold: Threshold for warning message

        Returns:
            Tuple of (is_acceptable, density_percentage)
        """
        density = self.calculate_density(image)

        self.logger.checking(f"Density analysis")
        self.logger.info(f"Black pixel density: {density:.1f}%")

        if density > max_density:
            self.logger.error(f"Density too high: {density:.1f}% (maximum: {max_density}%)")
            return False, density
        elif density > warning_threshold:
            self.logger.warning(f"Density is {density:.1f}%, target is <{warning_threshold}%")
            self.logger.info("Consider adjusting threshold or using pattern simplification")
            return True, density
        else:
            self.logger.info(f"Status: Within acceptable range (target: <{warning_threshold}%)")
            return True, density

    def apply_erosion(self, image: Image.Image, kernel_size: int = 1) -> Image.Image:
        """
        Apply morphological erosion to reduce black pixel density.

        Args:
            image: B&W PIL Image (mode '1' or 'L')
            kernel_size: Size of erosion kernel (1 or 2 pixels)

        Returns:
            Eroded PIL Image
        """
        # Convert to numpy array (as uint8)
        if image.mode == '1':
            # Convert 1-bit to 8-bit for cv2 processing
            img_array = np.array(image, dtype=np.uint8) * 255
        else:
            img_array = np.array(image, dtype=np.uint8)

        # Create erosion kernel
        # Use a larger kernel for mode effective erosion
        kernel_size = max(kernel_size, 2)  # Ensure minimum kernel size of 2
        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        # Apply erosion to reduce black pixels
        # In our images: black = 0 (background), white = 255 (foreground)
        # OpenCV's erode() reduces the foreground (bright pixels)
        # To reduce black pixels, we erode the black regions directly
        # We do this by treating black as foreground (invert), erode, then invert back

        # However, a simpler approach: use morphological opening which removes small black regions
        # and thins black structures. Opening = erosion followed by dilation, but we only want erosion

        # Direct erosion on black: invert so black becomes white, erode, invert back
        inverted = cv2.bitwise_not(img_array)
        eroded_inverted = cv2.erode(inverted, kernel, iterations=1)
        eroded = cv2.bitwise_not(eroded_inverted)

        # Convert back to PIL Image
        return Image.fromarray(eroded, mode='L')

    def reduce_density(self, image: Image.Image, target_density: float = 0.30,
                      max_iterations: int = 10, kernel_size: int = 1) -> Tuple[Image.Image, dict]:
        """
        Automatically reduce black pixel density using morphological erosion.

        Args:
            image: B&W PIL Image (mode '1' or 'L')
            target_density: Target density as percentage (0.0-1.0, where 0.30 = 30%)
            max_iterations: Maximum number of erosion iterations
            kernel_size: Size of erosion kernel (1 or 2 pixels)

        Returns:
            Tuple of (reduced PIL Image, reduction_stats dict)
        """
        # Convert target from 0-1 scale to 0-100 for consistency with calculate_density
        target_percentage = target_density * 100

        # Calculate initial density
        initial_density = self.calculate_density(image)

        self.logger.blank_line()
        self.logger.progress("Density Reduction: Starting automatic density reduction")
        self.logger.info(f"Density Reduction: Initial density {initial_density:.1f}%, target {target_percentage:.0f}%")

        # If already at or below target, no reduction needed
        if initial_density <= target_percentage:
            self.logger.info("Density Reduction: Already at target density, no reduction needed")
            return image, {
                'initial_density': initial_density,
                'final_density': initial_density,
                'iterations': 0,
                'reduced': False
            }

        # Iteratively apply erosion
        reduced_image = image
        current_density = initial_density
        iteration = 0

        for i in range(1, max_iterations + 1):
            iteration = i

            # Apply one iteration of erosion
            self.logger.progress(f"Density Reduction: Iteration {i}/{max_iterations}")
            reduced_image = self.apply_erosion(reduced_image, kernel_size)

            # Recalculate density
            current_density = self.calculate_density(reduced_image)
            self.logger.info(f"Density Reduction: Current density {current_density:.1f}%")

            # Check if we've reached target
            if current_density <= target_percentage:
                self.logger.success(f"Density Reduction: Target reached in {i} iteration(s)")
                break

        # Final report
        final_density = self.calculate_density(reduced_image)

        if final_density > target_percentage:
            self.logger.warning(
                f"Density Reduction: Maximum iterations reached. "
                f"Final density {final_density:.1f}% is above target {target_percentage:.0f}%"
            )
            self.logger.info(
                "Density Reduction: Consider adjusting threshold value for better results"
            )
        else:
            self.logger.info(
                f"Density Reduction: Complete. Final density {final_density:.1f}% "
                f"(reduced from {initial_density:.1f}%)"
            )

        # Convert back to 1-bit mode if input was 1-bit
        if image.mode == '1':
            reduced_image = reduced_image.convert('1')

        reduction_stats = {
            'initial_density': initial_density,
            'final_density': final_density,
            'iterations': iteration,
            'reduced': True,
            'target_density': target_percentage
        }

        return reduced_image, reduction_stats

    def check_image_size(self, image: Image.Image, paper_size: str = 'letter') -> Tuple[bool, str]:
        """
        Check if image fits on specified paper size at 300 DPI.

        Args:
            image: PIL Image object
            paper_size: Target paper size ('letter' or 'tabloid')

        Returns:
            Tuple of (fits, message)
        """
        # Paper sizes at 300 DPI
        paper_sizes_px = {
            'letter': (2550, 3300),    # 8.5 x 11 inches
            'tabloid': (3300, 5100)    # 11 x 17 inches
        }

        if paper_size not in paper_sizes_px:
            return True, ""

        max_width, max_height = paper_sizes_px[paper_size]
        img_width, img_height = image.size

        if img_width > max_width or img_height > max_height:
            return False, (
                f"Image size ({img_width}x{img_height} pixels) exceeds "
                f"{paper_size} paper ({max_width}x{max_height} pixels at 300 DPI)"
            )

        return True, ""

    def scale_image(self, image: Image.Image, scale_percent: float) -> Image.Image:
        """
        Enlarge image by a percentage.

        Args:
            image: PIL Image to scale
            scale_percent: Scale factor as percentage (100 = no change, 200 = 2x, 150 = 1.5x)

        Returns:
            Scaled PIL Image
        """
        factor = scale_percent / 100
        new_width = int(image.width * factor)
        new_height = int(image.height * factor)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def scale_detected_texts(self, detected_texts: List[DetectedText], scale_percent: float) -> List[DetectedText]:
        """
        Scale the coordinates of detected text objects to match a scaled image.

        Args:
            detected_texts: List of DetectedText objects
            scale_percent: Same scale factor used for the image

        Returns:
            New list of DetectedText with scaled coordinates
        """
        factor = scale_percent / 100
        scaled_texts = []
        for text in detected_texts:
            scaled_text = DetectedText(
                text=text.text,
                x=int(text.x * factor),
                y=int(text.y * factor),
                width=int(text.width * factor),
                height=int(text.height * factor),
                confidence=text.confidence,
                is_dimension=text.is_dimension
            )
            scaled_texts.append(scaled_text)
        return scaled_texts

    def crop_to_region(
        self,
        image: Image.Image,
        region: Tuple[float, float, float, float],
        margin_percent: float = 10.0
    ) -> Image.Image:
        """
        Crop image to a region specified in percentages.

        Args:
            image: PIL Image to crop
            region: (x_percent, y_percent, width_percent, height_percent)
                    where each value is 0-100 representing percentage of image dimensions
            margin_percent: Additional margin around region (default 10%)

        Returns:
            Cropped PIL Image
        """
        x_pct, y_pct, w_pct, h_pct = region

        # Add margin (split evenly on both sides)
        margin_half = margin_percent / 2
        x_pct = max(0, x_pct - margin_half)
        y_pct = max(0, y_pct - margin_half)
        w_pct = min(100 - x_pct, w_pct + margin_percent)
        h_pct = min(100 - y_pct, h_pct + margin_percent)

        # Convert percentages to pixels
        x = int(image.width * x_pct / 100)
        y = int(image.height * y_pct / 100)
        w = int(image.width * w_pct / 100)
        h = int(image.height * h_pct / 100)

        # Ensure we don't exceed image bounds
        x2 = min(x + w, image.width)
        y2 = min(y + h, image.height)

        return image.crop((x, y, x2, y2))

    def adjust_to_aspect_ratio(
        self,
        image: Image.Image,
        paper_size: str = 'letter'
    ) -> Image.Image:
        """
        Crop image to match paper aspect ratio (centered crop).

        This ensures the zoomed region fills the page without distortion
        by cropping excess width or height.

        Args:
            image: PIL Image to adjust
            paper_size: 'letter' (8.5x11) or 'tabloid' (11x17)

        Returns:
            Cropped PIL Image matching paper aspect ratio
        """
        # Paper aspect ratios (portrait orientation)
        paper_ratios = {
            'letter': 8.5 / 11.0,   # ~0.773
            'tabloid': 11.0 / 17.0  # ~0.647
        }
        target_ratio = paper_ratios.get(paper_size, paper_ratios['letter'])

        current_ratio = image.width / image.height

        if current_ratio > target_ratio:
            # Image is too wide - crop sides (centered)
            new_width = int(image.height * target_ratio)
            offset = (image.width - new_width) // 2
            return image.crop((offset, 0, offset + new_width, image.height))
        elif current_ratio < target_ratio:
            # Image is too tall - crop top/bottom (centered)
            new_height = int(image.width / target_ratio)
            offset = (image.height - new_height) // 2
            return image.crop((0, offset, image.width, offset + new_height))
        else:
            # Already correct aspect ratio
            return image

    def scale_to_fill_page(
        self,
        image: Image.Image,
        paper_size: str = 'letter',
        dpi: int = 300
    ) -> Image.Image:
        """
        Scale image up to fill the page at specified DPI.

        This is used after cropping and aspect ratio adjustment to ensure
        the zoomed region fills the entire page.

        Args:
            image: PIL Image (should already match paper aspect ratio)
            paper_size: 'letter' (8.5x11) or 'tabloid' (11x17)
            dpi: Target DPI (default 300 for PIAF)

        Returns:
            Scaled PIL Image that fills the page
        """
        # Paper sizes in inches
        paper_sizes = {
            'letter': (8.5, 11.0),
            'tabloid': (11.0, 17.0)
        }

        paper_width, paper_height = paper_sizes.get(paper_size, paper_sizes['letter'])

        # Target size in pixels
        target_width = int(paper_width * dpi)
        target_height = int(paper_height * dpi)

        # Scale to fit within page (use smaller scale factor to fit)
        width_scale = target_width / image.width
        height_scale = target_height / image.height
        scale_factor = min(width_scale, height_scale)

        new_width = int(image.width * scale_factor)
        new_height = int(image.height * scale_factor)

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def filter_texts_in_region(
        self,
        detected_texts: List[DetectedText],
        region: Tuple[float, float, float, float],
        original_image_size: Tuple[int, int],
        margin_percent: float = 10.0
    ) -> List[DetectedText]:
        """
        Filter detected texts to only include those within a zoom region,
        and adjust their coordinates relative to the cropped area.

        Args:
            detected_texts: List of DetectedText objects with pixel coordinates
            region: (x_percent, y_percent, width_percent, height_percent)
            original_image_size: (width, height) of the original image
            margin_percent: Margin that was applied to the region

        Returns:
            List of DetectedText with coordinates adjusted to cropped image
        """
        orig_width, orig_height = original_image_size
        x_pct, y_pct, w_pct, h_pct = region

        # Apply same margin calculation as crop_to_region
        margin_half = margin_percent / 2
        x_pct = max(0, x_pct - margin_half)
        y_pct = max(0, y_pct - margin_half)
        w_pct = min(100 - x_pct, w_pct + margin_percent)
        h_pct = min(100 - y_pct, h_pct + margin_percent)

        # Calculate crop boundaries in pixels
        crop_x = int(orig_width * x_pct / 100)
        crop_y = int(orig_height * y_pct / 100)
        crop_x2 = min(int(orig_width * (x_pct + w_pct) / 100), orig_width)
        crop_y2 = min(int(orig_height * (y_pct + h_pct) / 100), orig_height)

        filtered_texts = []
        for text in detected_texts:
            # Check if text center is within the crop region
            text_center_x = text.x + text.width / 2
            text_center_y = text.y + text.height / 2

            if (crop_x <= text_center_x <= crop_x2 and
                crop_y <= text_center_y <= crop_y2):
                # Adjust coordinates relative to cropped image
                adjusted_text = DetectedText(
                    text=text.text,
                    x=max(0, int(text.x - crop_x)),
                    y=max(0, int(text.y - crop_y)),
                    width=text.width,
                    height=text.height,
                    confidence=text.confidence,
                    is_dimension=text.is_dimension
                )
                filtered_texts.append(adjusted_text)

        return filtered_texts

    def process(self, input_path: str, threshold: int = 128,
                check_density_flag: bool = True,
                enhance: Optional[str] = None,
                enhance_strength: float = 1.0,
                paper_size: str = 'letter',
                auto_reduce_density: bool = False,
                target_density: Optional[float] = None,
                max_reduction_iterations: Optional[int] = None,
                detect_text: bool = False,
                save_intermediate_path: Optional[str] = None) -> Tuple[Image.Image, dict]:
        """
        Main processing pipeline: load, enhance, convert, threshold.

        Args:
            input_path: Path to input image
            threshold: B&W threshold value (0-255)
            check_density_flag: Whether to check density
            enhance: Enhancement method ('s_curve', 'auto_contrast', 'clahe', 'histogram', None)
            enhance_strength: Enhancement strength for s_curve (0.0-2.0, default 1.0)
            paper_size: Target paper size for size checking
            auto_reduce_density: Whether to automatically reduce density if too high
            target_density: Target density for reduction (0.0-1.0, default from config)
            max_reduction_iterations: Maximum erosion iterations (default from config)
            detect_text: Whether to detect text and dimensions (requires text_detector)
            save_intermediate_path: Optional path to save enhanced grayscale image before thresholding

        Returns:
            Tuple of (processed PIL Image, metadata dict)

        Raises:
            ImageProcessorError: If processing fails
        """
        try:
            # Load image
            image = self.load_image(input_path)

            # Convert to grayscale
            grayscale = self.convert_to_grayscale(image)

            # Apply contrast enhancement if requested
            enhanced = grayscale
            if enhance:
                self.logger.blank_line()
                if enhance == 's_curve':
                    enhanced = self.contrast_enhancer.apply_s_curve(grayscale, strength=enhance_strength)
                elif enhance == 'auto_contrast':
                    enhanced = self.contrast_enhancer.auto_contrast(grayscale)
                elif enhance == 'clahe':
                    enhanced = self.contrast_enhancer.clahe(grayscale)
                elif enhance == 'histogram':
                    enhanced = self.contrast_enhancer.histogram_equalization(grayscale)
                else:
                    self.logger.warning(f"Unknown enhancement method: {enhance}, skipping")
                    enhanced = grayscale

            # Save intermediate enhanced image if path provided (for debugging enhancement)
            if save_intermediate_path:
                try:
                    enhanced.save(save_intermediate_path)
                    self.logger.info(f"Saved intermediate enhanced image to: {save_intermediate_path}")
                    self.logger.info("Compare this grayscale image with the final B&W output to evaluate enhancement effect")
                except Exception as e:
                    self.logger.warning(f"Failed to save intermediate image: {e}")

            # Detect text BEFORE thresholding (on grayscale/enhanced image for better accuracy)
            detected_texts = []
            if detect_text:
                # Create text detector dynamically if needed (CLI flag overrides config)
                if not self.text_detector:
                    try:
                        text_config = self.config.get('text_detection', {})
                        # Enable text detection when CLI flag is used
                        text_config['enabled'] = True
                        self.text_detector = TextDetector(
                            config=TextDetectionConfig(**text_config),
                            logger=self.logger
                        )
                    except Exception as e:
                        self.logger.warning(f"Text detection initialization failed: {e}")
                        self.logger.info("Continuing with processing without text detection")
                        self.text_detector = None

                if self.text_detector:
                    self.logger.blank_line()
                    self.logger.progress("Detecting text and dimensions")
                    try:
                        detected_texts = self.text_detector.detect_text(enhanced)

                        dimension_count = sum(1 for dt in detected_texts if dt.is_dimension)
                        total_count = len(detected_texts)

                        if dimension_count > 0:
                            self.logger.info(f"Found {dimension_count} dimension(s)")
                        if total_count - dimension_count > 0:
                            self.logger.info(f"Found {total_count - dimension_count} other text element(s)")
                        if total_count == 0:
                            self.logger.info("No text detected")
                    except Exception as e:
                        self.logger.warning(f"Text detection failed: {e}")
                        self.logger.info("Continuing with processing")

            # Apply threshold
            bw_image = self.apply_threshold(enhanced, threshold)

            # Initialize density reduction metadata
            reduction_stats = None

            # Check density if requested
            density = None
            if check_density_flag:
                is_acceptable, density = self.check_density(bw_image)

                # Apply automatic density reduction if enabled and density is too high
                if auto_reduce_density and density > 45.0:
                    # Get settings from config or use defaults
                    config_density = self.config.get('density', {})
                    auto_reduce_config = config_density.get('auto_reduce', {})

                    # Use provided values or fall back to config, then to hardcoded defaults
                    final_target_density = target_density if target_density is not None else \
                                          auto_reduce_config.get('target_density', 0.30)
                    final_max_iterations = max_reduction_iterations if max_reduction_iterations is not None else \
                                          auto_reduce_config.get('max_iterations', 10)
                    kernel_size = auto_reduce_config.get('erosion_kernel_size', 1)

                    # Apply density reduction
                    bw_image, reduction_stats = self.reduce_density(
                        bw_image,
                        target_density=final_target_density,
                        max_iterations=final_max_iterations,
                        kernel_size=kernel_size
                    )

                    # Update density after reduction
                    density = self.calculate_density(bw_image)

                elif not is_acceptable:
                    self.logger.warning("Image density exceeds recommended maximum")
                    self.logger.info("Consider using --auto-reduce-density to automatically fix this")

            # Check image size against paper size
            fits, size_message = self.check_image_size(bw_image, paper_size)
            needs_tiling = not fits

            if needs_tiling:
                self.logger.blank_line()
                self.logger.warning(size_message)
                self.logger.info("Consider using --enable-tiling to split image into multiple pages")

            # Build metadata
            metadata = {
                'source_file': str(Path(input_path).name),
                'original_size': image.size,
                'original_mode': image.mode,
                'threshold': threshold,
                'enhancement': enhance,
                'enhance_strength': enhance_strength if enhance == 's_curve' else None,
                'density_percentage': density,
                'output_mode': bw_image.mode,
                'needs_tiling': needs_tiling,
                'paper_size': paper_size,
                'density_reduction': reduction_stats,
                'detected_texts': detected_texts
            }

            self.logger.success("Image processing complete")

            return bw_image, metadata

        except ImageProcessorError:
            raise
        except Exception as e:
            raise ImageProcessorError(f"Processing failed: {str(e)}") from e

    def process_with_rainbowtact(
        self,
        input_path: str,
        num_colors: int = 5,
        detect_text: bool = True,
        paper_size: str = 'letter',
    ) -> Tuple[Image.Image, dict, List[ColorRegion], List[TactilePattern]]:
        """
        Process image using RainbowTact color-to-tactile conversion.

        Loads the RGB image, runs text detection on a grayscale copy,
        then converts colors to tactile patterns.

        Args:
            input_path: Path to input image
            num_colors: Number of color clusters for K-means
            detect_text: Whether to detect text
            paper_size: Target paper size

        Returns:
            Tuple of (1-bit B&W image, metadata dict, color regions, tactile patterns)
        """
        try:
            # Load as RGB for color analysis
            image = self.load_image(input_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Detect text on grayscale copy (existing OCR pipeline)
            detected_texts = []
            if detect_text:
                grayscale = self.convert_to_grayscale(image)
                if not self.text_detector:
                    try:
                        text_config = self.config.get('text_detection', {})
                        text_config['enabled'] = True
                        self.text_detector = TextDetector(
                            config=TextDetectionConfig(**text_config),
                            logger=self.logger
                        )
                    except Exception as e:
                        self.logger.warning(f"Text detection init failed: {e}")

                if self.text_detector:
                    try:
                        detected_texts = self.text_detector.detect_text(grayscale)
                    except Exception as e:
                        self.logger.warning(f"Text detection failed: {e}")

            # Run RainbowTact conversion on the color image
            config = RainbowTactConfig(num_colors=num_colors)
            converter = RainbowTactConverter(config)
            bw_image, regions, patterns = converter.convert(image)

            # Check density
            density = self.calculate_density(bw_image)

            # Check image size
            fits, size_message = self.check_image_size(bw_image, paper_size)

            metadata = {
                'source_file': str(Path(input_path).name),
                'original_size': image.size,
                'original_mode': image.mode,
                'threshold': None,
                'enhancement': None,
                'density_percentage': density,
                'output_mode': bw_image.mode,
                'needs_tiling': not fits,
                'paper_size': paper_size,
                'detected_texts': detected_texts,
                'color_to_tactile': True,
                'num_color_regions': len(regions),
            }

            self.logger.success("RainbowTact processing complete")
            return bw_image, metadata, regions, patterns

        except ImageProcessorError:
            raise
        except Exception as e:
            raise ImageProcessorError(f"RainbowTact processing failed: {str(e)}") from e
