"""
EasyOCR-based text detection for architectural drawings.

Provides accurate text detection with bounding boxes, replacing the
Tesseract+Claude hybrid OCR pipeline with a single-call solution.
"""

import re
import logging
from typing import List, Optional

from PIL import Image

from tactile_core.core.text_detector import DetectedText

logger = logging.getLogger("tactile-mcp")

# Singleton EasyOCR reader — heavy init (~12s), reuse across calls
_reader = None
_reader_language = None

# Dimension patterns for architectural drawings
_DIMENSION_PATTERNS = [
    r"\d+['\u2032]-?\s*\d*[\"\"'\u2033]?",  # feet-inches: 10'-6", 12' 0"
    r"\d+\.?\d*\s*(m|cm|mm|ft|in)\b",        # metric/imperial with unit
    r"\d+\s*x\s*\d+",                         # dimensions like 10x12
    r"\d+[,\.]\d+\s*m\b",                     # European decimal: 5,55 m
]
_DIMENSION_REGEXES = [re.compile(p, re.IGNORECASE) for p in _DIMENSION_PATTERNS]


def _get_reader(language: str = 'en', gpu: bool = False):
    """Get or create a singleton EasyOCR Reader."""
    global _reader, _reader_language
    if _reader is None or _reader_language != language:
        import easyocr
        logger.info(f"Initializing EasyOCR reader (language={language}, gpu={gpu})...")
        _reader = easyocr.Reader([language], gpu=gpu)
        _reader_language = language
        logger.info("EasyOCR reader initialized")
    return _reader


class EasyOCRDetector:
    """Text detector using EasyOCR for accurate bounding boxes."""

    def __init__(self, language: str = 'en', gpu: bool = False):
        self.language = language
        self.gpu = gpu

    def detect_text(self, image: Image.Image, page_number: int = 1) -> List[DetectedText]:
        """
        Detect all text in image with bounding boxes.

        Args:
            image: PIL Image (any mode — will be converted internally by EasyOCR)
            page_number: Page number for multi-page context tracking

        Returns:
            List of DetectedText objects with pixel positions and metadata
        """
        import numpy as np

        reader = _get_reader(self.language, self.gpu)

        # EasyOCR accepts numpy arrays
        img_array = np.array(image)

        results = reader.readtext(img_array)

        detected_texts = []
        for (bbox, text, confidence) in results:
            text = text.strip()
            if not text:
                continue

            # bbox is [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] (4-point polygon)
            x_min = int(min(p[0] for p in bbox))
            y_min = int(min(p[1] for p in bbox))
            x_max = int(max(p[0] for p in bbox))
            y_max = int(max(p[1] for p in bbox))

            detected = DetectedText(
                text=text,
                x=x_min,
                y=y_min,
                width=x_max - x_min,
                height=y_max - y_min,
                confidence=confidence * 100,  # EasyOCR 0-1 → match existing 0-100 scale
                is_dimension=self._is_dimension(text),
                page_number=page_number,
            )
            detected_texts.append(detected)

        return detected_texts

    @staticmethod
    def _is_dimension(text: str) -> bool:
        """Check if text matches an architectural dimension pattern."""
        for regex in _DIMENSION_REGEXES:
            if regex.search(text):
                return True
        return False
