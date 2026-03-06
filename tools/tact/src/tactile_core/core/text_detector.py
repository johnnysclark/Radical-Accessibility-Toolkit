"""
Text detection module for architectural drawings.

Uses Tesseract OCR to detect and locate text, with special focus on
architectural dimensions (e.g., 10'-6", 3.5m, 120mm).
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional
from PIL import Image
import numpy as np
import cv2

try:
    import pytesseract
    from pytesseract import Output
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    Output = None

from tactile_core.utils.logger import AccessibleLogger


class TextDetectionError(Exception):
    """Custom exception for text detection errors."""
    pass


@dataclass
class TextDetectionConfig:
    """Configuration for text detection."""
    enabled: bool = False
    language: str = 'eng'
    page_segmentation_mode: int = 3  # PSM 3 = Fully automatic
    min_confidence: int = 60
    filter_dimensions: bool = True
    dimension_patterns: List[str] = field(default_factory=list)


@dataclass
class DetectedText:
    """Container for detected text with position metadata."""
    text: str
    x: int
    y: int
    width: int
    height: int
    confidence: float
    is_dimension: bool = False
    rotation_degrees: float = 0.0  # 0=horizontal, 90=rotated clockwise, -90=counter-clockwise
    page_number: int = 1  # Page number for multi-page PDF context tracking

    def __repr__(self):
        """String representation for debugging."""
        dimension_tag = " [DIMENSION]" if self.is_dimension else ""
        rotation_tag = f" [ROT:{self.rotation_degrees}deg]" if self.rotation_degrees != 0 else ""
        page_tag = f" [page {self.page_number}]" if self.page_number > 1 else ""
        return (f"DetectedText('{self.text}'{dimension_tag}{rotation_tag}{page_tag}, "
                f"pos=({self.x},{self.y}), size=({self.width}x{self.height}), "
                f"confidence={self.confidence:.1f}%)")


class TextDetector:
    """OCR-based text and dimension detector for architectural drawings."""

    def __init__(self, config: TextDetectionConfig, logger: AccessibleLogger):
        """
        Initialize text detector.

        Args:
            config: TextDetectionConfig with detection settings
            logger: AccessibleLogger instance for status messages

        Raises:
            TextDetectionError: If Tesseract is not installed or configured
        """
        self.config = config
        self.logger = logger
        self._validate_tesseract_installation()

        # Compile dimension patterns for performance
        self._dimension_regexes = []
        if config.filter_dimensions and config.dimension_patterns:
            for pattern in config.dimension_patterns:
                try:
                    self._dimension_regexes.append(re.compile(pattern))
                except re.error as e:
                    self.logger.warning(f"Invalid dimension pattern '{pattern}': {e}")

    def _validate_tesseract_installation(self):
        """
        Check if Tesseract is properly installed and accessible.

        Raises:
            TextDetectionError: If Tesseract is not available
        """
        if not TESSERACT_AVAILABLE:
            raise TextDetectionError(
                "pytesseract module not installed. "
                "Install with: pip install pytesseract"
            )

        try:
            # Try to get Tesseract version to verify installation
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"Tesseract OCR version {version} detected")
        except Exception as e:
            raise TextDetectionError(
                "Tesseract OCR is not installed or not in PATH. "
                "Install from: https://github.com/tesseract-ocr/tesseract"
            ) from e

    def detect_text(self, image: Image.Image, page_number: int = 1) -> List[DetectedText]:
        """
        Detect all text in image with bounding boxes.

        Args:
            image: Grayscale PIL Image (BEFORE thresholding for better accuracy)
            page_number: Page number for multi-page PDF context tracking (default 1)

        Returns:
            List of DetectedText objects with positions and metadata

        Raises:
            TextDetectionError: If OCR processing fails
        """
        # Validate image mode
        if image.mode not in ('L', 'RGB'):
            self.logger.warning(
                f"Image mode {image.mode} may not work well with OCR. "
                "Converting to grayscale for better results."
            )
            image = image.convert('L')

        # Preprocess image for better OCR accuracy
        preprocessed = self._preprocess_for_ocr(image)

        # Configure Tesseract
        custom_config = f'--psm {self.config.page_segmentation_mode} -l {self.config.language}'

        try:
            # Run Tesseract OCR with bounding box data
            ocr_data = pytesseract.image_to_data(
                preprocessed,
                config=custom_config,
                output_type=Output.DICT
            )
        except Exception as e:
            raise TextDetectionError(f"OCR processing failed: {str(e)}") from e

        # Parse OCR results
        detected_texts = []
        n_boxes = len(ocr_data['text'])

        for i in range(n_boxes):
            # Get confidence and text
            confidence = float(ocr_data['conf'][i])
            text = ocr_data['text'][i].strip()

            # Filter by confidence threshold and non-empty text
            if confidence < self.config.min_confidence or not text:
                continue

            # Get bounding box coordinates
            x = int(ocr_data['left'][i])
            y = int(ocr_data['top'][i])
            width = int(ocr_data['width'][i])
            height = int(ocr_data['height'][i])

            # Check if this is a dimension
            is_dimension = self._is_dimension(text)

            # Create DetectedText object
            detected = DetectedText(
                text=text,
                x=x,
                y=y,
                width=width,
                height=height,
                confidence=confidence,
                is_dimension=is_dimension,
                page_number=page_number
            )

            detected_texts.append(detected)

        return detected_texts

    def _preprocess_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.

        Applies:
        - Median blur for noise reduction
        - Optional contrast enhancement

        Args:
            image: PIL Image (grayscale or RGB)

        Returns:
            Preprocessed PIL Image
        """
        # Convert to numpy array
        img_array = np.array(image)

        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Apply median blur to reduce noise (small kernel to preserve text)
        # Using kernel size of 3 as default - good for removing noise without blurring text
        blurred = cv2.medianBlur(img_array, 3)

        # Optional: Apply slight sharpening or contrast enhancement
        # For most architectural drawings, the original contrast is fine
        # We skip CLAHE here as it can make text detection worse on clean drawings

        return Image.fromarray(blurred, mode='L')

    def _is_dimension(self, text: str) -> bool:
        """
        Check if text matches dimension pattern.

        Uses regex patterns from config to identify architectural dimensions
        like "10'-6\"", "3.5m", "120mm", etc.

        Args:
            text: Text string to check

        Returns:
            True if text matches a dimension pattern
        """
        if not self.config.filter_dimensions or not self._dimension_regexes:
            return False

        # Check against all compiled patterns
        for regex in self._dimension_regexes:
            if regex.search(text):
                return True

        return False

    def get_dimension_texts(self, detected_texts: List[DetectedText]) -> List[DetectedText]:
        """
        Filter detected texts to only dimensions.

        Args:
            detected_texts: List of all detected texts

        Returns:
            List of only dimension texts
        """
        return [dt for dt in detected_texts if dt.is_dimension]

    def get_non_dimension_texts(self, detected_texts: List[DetectedText]) -> List[DetectedText]:
        """
        Filter detected texts to exclude dimensions.

        Args:
            detected_texts: List of all detected texts

        Returns:
            List of non-dimension texts
        """
        return [dt for dt in detected_texts if not dt.is_dimension]

    def get_text_in_region(self, detected_texts: List[DetectedText],
                          x: int, y: int, width: int, height: int) -> List[DetectedText]:
        """
        Get all detected texts within a specified region.

        Args:
            detected_texts: List of all detected texts
            x: Region x coordinate
            y: Region y coordinate
            width: Region width
            height: Region height

        Returns:
            List of texts within the region
        """
        texts_in_region = []

        for dt in detected_texts:
            # Check if text bounding box intersects with region
            # Text is in region if its center point is within the region
            text_center_x = dt.x + dt.width // 2
            text_center_y = dt.y + dt.height // 2

            if (x <= text_center_x <= x + width and
                y <= text_center_y <= y + height):
                texts_in_region.append(dt)

        return texts_in_region
