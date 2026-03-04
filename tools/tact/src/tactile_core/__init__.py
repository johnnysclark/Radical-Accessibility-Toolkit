"""
Tactile Core - Accessible Graphics Library

A Python library for converting images to high-contrast, tactile-ready formats
for PIAF (Picture In A Flash) machines. Part of the Radical Accessibility PAI Pack.

Designed for accessibility and screen-reader compatibility in architectural education.
"""

__version__ = "1.0.0"
__author__ = "Radical Accessibility Project"

from tactile_core.core.processor import ImageProcessor
from tactile_core.core.pdf_generator import PIAFPDFGenerator

__all__ = ["ImageProcessor", "PIAFPDFGenerator"]
