"""
Shared core converter for tactile toolkit.

This module provides the TactileConverter class that handles the conversion
of architectural images to PIAF-ready PDFs. It is used by both the CLI and
MCP server interfaces.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Union
import tempfile
import logging

from PIL import Image

from tactile_core.core.processor import ImageProcessor, ImageProcessorError
from tactile_core.core.pdf_generator import PIAFPDFGenerator, PDFGeneratorError
from tactile_core.config.standards_loader import StandardsLoader, StandardsLoaderError
from tactile_core.config.presets import PresetManager, PresetError
from tactile_core.core.braille_converter import BrailleConverter, BrailleConfig, KeyEntry
from tactile_core.core.text_detector import TextDetector, TextDetectionConfig, DetectedText
from tactile_core.core.label_scaler import analyze_label_fit

logger = logging.getLogger("tactile.converter")


@dataclass
class ConversionParams:
    """Parameters for tactile image conversion.

    This dataclass captures all parameters needed for converting an image
    to a PIAF-ready PDF. Both CLI and MCP interfaces build this object
    from their respective input sources.
    """
    # Required
    input_path: str

    # Output
    output_path: Optional[str] = None
    paper_size: str = "letter"

    # Preset/threshold
    preset: Optional[str] = None
    threshold: Optional[int] = None

    # Enhancement
    enhance: Optional[str] = None
    enhance_strength: float = 1.0

    # Text/Braille
    detect_text: bool = True
    braille_grade: int = 2
    braille_placement: str = "overlay"

    # Scaling (NEW for CLI via this consolidation)
    scale_percent: Optional[float] = None
    auto_scale: bool = True
    max_scale_factor: Optional[float] = None

    # Abbreviation key (NEW for CLI via this consolidation)
    use_abbreviation_key: bool = True
    force_abbreviation_key: bool = False

    # Density
    auto_reduce_density: bool = False
    target_density: Optional[float] = None
    max_reduction_iterations: Optional[int] = None

    # Tiling
    enable_tiling: bool = False
    tile_overlap: float = 0.0
    add_registration_marks: bool = True

    # Zoom
    zoom_region: Optional[Tuple[float, float, float, float]] = None
    zoom_regions: Optional[List[Dict[str, Any]]] = None

    # MCP-only (not exposed in CLI)
    zoom_to: Optional[str] = None
    claude_text_json: Optional[Union[str, List]] = None
    use_grid_overlay: bool = False
    assess_quality: bool = False

    # Color-to-tactile (RainbowTact)
    color_to_tactile: bool = False
    rainbowtact_num_colors: int = 5

    # Pre-detected texts (for hybrid OCR or CLI text injection)
    predetected_texts: Optional[List[DetectedText]] = None

    # CLI-only
    verbose: bool = False
    interactive: bool = False
    config_path: Optional[str] = None


@dataclass
class ConversionResult:
    """Result of a tactile image conversion.

    This dataclass captures all output data from a conversion operation.
    CLI formats this for terminal output, MCP formats as JSON.
    """
    success: bool
    output_file: Optional[str] = None
    density_percentage: Optional[float] = None
    braille_labels_count: int = 0
    key_entries_count: int = 0
    detected_text_count: int = 0
    scale_applied: float = 100.0
    auto_scale_used: bool = False
    needs_tiling: bool = False
    page_count: int = 1
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None
    error_type: Optional[str] = None

    # Additional metadata
    paper_size: Optional[str] = None
    threshold_used: Optional[int] = None
    preset_used: Optional[str] = None
    hybrid_ocr_used: bool = False
    color_to_tactile: bool = False
    color_regions_count: int = 0
    zoom_applied: Optional[Dict[str, Any]] = None
    is_multipage: bool = False
    is_multi_region: bool = False
    regions: Optional[List[str]] = None

    # For interactive/verbose modes
    original_size: Optional[Tuple[int, int]] = None
    processed_size: Optional[Tuple[int, int]] = None
    enhancement_applied: Optional[str] = None
    density_reduced: bool = False
    density_reduction_iterations: int = 0

    # Human-readable message
    message: Optional[str] = None


class SilentLogger:
    """A logger that doesn't output anything - for non-verbose use."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def info(self, msg, *args): pass
    def warning(self, msg, *args): pass
    def error(self, msg, *args, **kwargs): pass
    def progress(self, msg, *args): pass
    def loading(self, msg, *args): pass
    def checking(self, msg, *args): pass
    def found(self, msg, *args): pass
    def success(self, msg, *args): pass
    def solution(self, msg, *args): pass
    def generating(self, msg, *args): pass
    def complete(self, msg, *args): pass
    def blank_line(self): pass


class TactileConverter:
    """Core converter for creating PIAF-ready tactile PDFs.

    This class encapsulates all the conversion logic shared between
    the CLI and MCP interfaces. It handles:
    - Configuration loading (standards, presets)
    - Image processing (thresholding, enhancement, density)
    - Text detection and Braille conversion
    - Scaling and abbreviation key generation
    - PDF generation (single-page, tiled, multi-page)
    """

    def __init__(self, config_path: Optional[str] = None, logger=None):
        """Initialize the converter.

        Args:
            config_path: Optional path to custom tactile_standards.yaml
            logger: Optional logger instance. If None, uses SilentLogger.
        """
        self.logger = logger or SilentLogger()
        self._config_path = config_path
        self._standards = None
        self._preset_manager = None

    def _load_configuration(self) -> StandardsLoader:
        """Load tactile standards configuration."""
        if self._standards is None:
            try:
                self._standards = StandardsLoader(config_path=self._config_path)
            except StandardsLoaderError as e:
                raise ConversionError(f"Failed to load configuration: {e}", "configuration_error")
        return self._standards

    def _load_presets(self) -> PresetManager:
        """Load conversion presets."""
        if self._preset_manager is None:
            try:
                self._preset_manager = PresetManager()
            except PresetError as e:
                raise ConversionError(f"Failed to load presets: {e}", "preset_error")
        return self._preset_manager

    def _apply_preset(self, params: ConversionParams) -> Tuple[int, Optional[str], float, str]:
        """Apply preset settings, with explicit params taking precedence.

        Returns:
            Tuple of (threshold, enhance, enhance_strength, paper_size)
        """
        standards = self._load_configuration()

        threshold = params.threshold
        enhance = params.enhance
        enhance_strength = params.enhance_strength
        paper_size = params.paper_size

        if params.preset:
            preset_manager = self._load_presets()
            try:
                preset_settings = preset_manager.get_preset_settings(params.preset)

                # Apply preset settings (explicit params override preset)
                if threshold is None:
                    threshold = preset_settings.get('threshold', standards.get_default_threshold())
                if paper_size == 'letter':  # Only override if using default
                    paper_size = preset_settings.get('paper_size', 'letter')
                if enhance is None:
                    enhance = preset_settings.get('enhance')
                if params.enhance_strength == 1.0:  # Default value
                    enhance_strength = preset_settings.get('enhance_strength', 1.0)

            except PresetError as e:
                raise ConversionError(f"Invalid preset '{params.preset}': {e}", "preset_error")

        # Get default threshold from config if still not specified
        if threshold is None:
            threshold = standards.get_default_threshold()

        return threshold, enhance, enhance_strength, paper_size

    def _create_braille_config(self, params: ConversionParams) -> BrailleConfig:
        """Create Braille configuration from standards and params."""
        standards = self._load_configuration()
        braille_config_dict = standards.get_all_config().get('braille', {})

        return BrailleConfig(
            enabled=True,
            grade=int(params.braille_grade),
            placement=params.braille_placement,
            font_name=braille_config_dict.get('font_name', 'DejaVu Sans'),
            font_size=braille_config_dict.get('font_size', 24),
            offset_x=braille_config_dict.get('offset_x', 5),
            offset_y=braille_config_dict.get('offset_y', -24),
            max_label_length=braille_config_dict.get('max_label_length', 30),
            truncate_suffix=braille_config_dict.get('truncate_suffix', '...'),
            font_color=braille_config_dict.get('font_color', 'black'),
            detect_overlaps=braille_config_dict.get('detect_overlaps', True),
            min_label_spacing=braille_config_dict.get('min_label_spacing', 6)
        )

    def _generate_output_path(self, input_path: str, zoom_label: Optional[str] = None) -> str:
        """Generate output path from input path."""
        import re
        input_file = Path(input_path)

        if zoom_label:
            safe_label = re.sub(r'[^\w\s-]', '', zoom_label).strip().replace(' ', '_').lower()
            return str(input_file.parent / f"{input_file.stem}_{safe_label}_piaf.pdf")
        else:
            return str(input_file.parent / f"{input_file.stem}_piaf.pdf")

    def _get_density_message(self, density: float) -> str:
        """Generate a human-readable message about density."""
        if density < 30:
            return f"Density {density:.1f}% - optimal for PIAF printing."
        elif density < 40:
            return f"Density {density:.1f}% - acceptable for PIAF."
        elif density < 45:
            return f"Density {density:.1f}% - slightly high, may cause some paper swelling."
        else:
            return f"Density {density:.1f}% - high, consider using auto_reduce_density option."

    def convert(self, params: ConversionParams) -> ConversionResult:
        """Convert an image to PIAF-ready PDF.

        This is the main conversion method that handles the full pipeline:
        1. Load configuration and apply preset
        2. Apply zoom region if specified
        3. Process image (threshold, enhance, density)
        4. Detect text and create Braille labels
        5. Apply scaling if needed
        6. Generate PDF output

        Args:
            params: ConversionParams with all conversion settings

        Returns:
            ConversionResult with output file path and metadata
        """
        try:
            # Load configuration
            standards = self._load_configuration()

            # Apply preset and get effective settings
            threshold, enhance, enhance_strength, paper_size = self._apply_preset(params)

            # Validate input file
            input_file = Path(params.input_path)
            if not input_file.exists():
                return ConversionResult(
                    success=False,
                    error=f"Image file not found: {params.input_path}",
                    error_type="file_not_found"
                )

            # Initialize processor
            processor = ImageProcessor(
                config=standards.get_all_config(),
                logger=self.logger
            )

            # Track image state
            image_path_for_processing = str(params.input_path)
            zoom_applied = None
            img_width, img_height = None, None
            original_img_width, original_img_height = None, None

            # Get original image dimensions
            with Image.open(input_file) as img:
                original_img_width, original_img_height = img.size
                img_width, img_height = original_img_width, original_img_height

            # Apply zoom region if specified
            if params.zoom_region:
                with Image.open(input_file) as base_image:
                    cropped = processor.crop_to_region(base_image, params.zoom_region, margin_percent=10.0)
                    cropped = processor.adjust_to_aspect_ratio(cropped, paper_size)
                    cropped = processor.scale_to_fill_page(cropped, paper_size, dpi=300)

                    # Save to temp file
                    zoom_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='zoom_')
                    cropped.save(zoom_temp.name, format='PNG')
                    image_path_for_processing = zoom_temp.name
                    img_width, img_height = cropped.size

                    zoom_applied = {
                        "region": params.zoom_region,
                        "original_size": {"width": original_img_width, "height": original_img_height},
                        "cropped_size": {"width": img_width, "height": img_height}
                    }

            # ============================================================
            # RAINBOWTACT: Color-to-Tactile Pattern Conversion
            # ============================================================
            if params.color_to_tactile:
                return self._convert_with_rainbowtact(
                    params, processor, standards, image_path_for_processing,
                    paper_size, threshold, zoom_applied,
                    original_img_width, original_img_height, img_width, img_height
                )

            # Handle pre-detected texts (from hybrid OCR or CLI)
            detected_texts = params.predetected_texts or []
            effective_scale_percent = None

            # Manual scaling (works independently of text detection)
            if params.scale_percent is not None and params.scale_percent != 100:
                with Image.open(image_path_for_processing) as base_image:
                    scaled_image = processor.scale_image(base_image, params.scale_percent)
                    img_width, img_height = scaled_image.size

                    scaled_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='scaled_')
                    scaled_image.save(scaled_temp.name, format='PNG')
                    image_path_for_processing = scaled_temp.name

                effective_scale_percent = params.scale_percent

                # Scale detected text coordinates if we have any
                if detected_texts:
                    detected_texts = processor.scale_detected_texts(detected_texts, params.scale_percent)

            # Auto-scaling analysis (requires detected texts for bounding box analysis)
            # Uses HEIGHT-BASED scaling: scale when Braille height > original bounding box height
            elif detected_texts and params.auto_scale:
                fit_analysis = analyze_label_fit(
                    detected_texts,
                    (img_width, img_height),
                    braille_grade=params.braille_grade,
                    max_scale_factor=params.max_scale_factor
                )

                recommended_scale = fit_analysis.get('recommended_scale', 100)
                was_capped = fit_analysis.get('capped', False)
                needs_abbreviation = fit_analysis.get('needs_abbreviation', [])

                # Log scaling analysis results
                if recommended_scale > 100:
                    cap_note = " (capped)" if was_capped else ""
                    logger.info(f"Height-based scaling: {recommended_scale:.0f}%{cap_note}")
                    if needs_abbreviation:
                        logger.info(f"{len(needs_abbreviation)} label(s) will need abbreviation after scaling")

                # Apply auto-scaling if recommended > 100
                if recommended_scale > 100:
                    effective_scale_percent = recommended_scale

                    # Apply scaling
                    with Image.open(image_path_for_processing) as base_image:
                        scaled_image = processor.scale_image(base_image, effective_scale_percent)
                        img_width, img_height = scaled_image.size

                        scaled_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='scaled_')
                        scaled_image.save(scaled_temp.name, format='PNG')
                        image_path_for_processing = scaled_temp.name

                        # Scale detected text coordinates
                        detected_texts = processor.scale_detected_texts(detected_texts, effective_scale_percent)

            # Process image
            try:
                processed_image, metadata = processor.process(
                    input_path=image_path_for_processing,
                    threshold=threshold,
                    check_density_flag=True,
                    enhance=enhance,
                    enhance_strength=enhance_strength,
                    paper_size=paper_size,
                    auto_reduce_density=params.auto_reduce_density,
                    target_density=params.target_density,
                    max_reduction_iterations=params.max_reduction_iterations,
                    detect_text=params.detect_text and not detected_texts  # Skip if we have pre-detected
                )
            except ImageProcessorError as e:
                return ConversionResult(
                    success=False,
                    error=f"Image processing failed: {e}",
                    error_type="processing_error"
                )

            # Use pre-detected texts or processor's detected texts
            texts_to_use = detected_texts or metadata.get('detected_texts', [])

            # Convert to Braille labels
            braille_labels = None
            symbol_key_entries = None
            key_entries = []
            braille_converter = None
            braille_labels_count = 0

            if params.detect_text and texts_to_use:
                try:
                    braille_config = self._create_braille_config(params)
                    braille_converter = BrailleConverter(braille_config, self.logger)

                    # Handle abbreviation key generation
                    if params.use_abbreviation_key or params.force_abbreviation_key:
                        detected_text_widths = {text.text: text.width for text in texts_to_use}

                        braille_labels, key_entries = braille_converter.create_braille_labels(
                            texts_to_use,
                            generate_key=True,
                            detected_text_widths=detected_text_widths if not params.force_abbreviation_key else None,
                            image_size=processed_image.size
                        )
                    else:
                        braille_labels, symbol_key_entries = braille_converter.create_braille_labels(texts_to_use)

                    if braille_labels:
                        braille_labels_count = len(braille_labels)

                    # White out original text regions
                    braille_config_dict = standards.get_all_config().get('braille', {})
                    whiteout_enabled = braille_config_dict.get('whiteout_original_text', True)
                    whiteout_padding = braille_config_dict.get('whiteout_padding', 5)

                    if whiteout_enabled and texts_to_use:
                        processed_image = processor.whiteout_text_regions(
                            processed_image,
                            texts_to_use,
                            padding=whiteout_padding
                        )

                except Exception as e:
                    self.logger.warning(f"Braille conversion failed: {e}")

            # Generate output path
            output_path = params.output_path or self._generate_output_path(params.input_path)

            # Generate PDF
            pdf_generator = PIAFPDFGenerator(
                logger=self.logger,
                config=standards.get_all_config()
            )

            needs_tiling = metadata.get('needs_tiling', False)

            try:
                if params.enable_tiling and needs_tiling:
                    final_output = pdf_generator.generate_with_tiling(
                        image=processed_image,
                        output_path=output_path,
                        paper_size=paper_size,
                        tile_overlap=params.tile_overlap,
                        add_registration_marks=params.add_registration_marks,
                        metadata=metadata,
                        braille_labels=braille_labels,
                        key_entries=key_entries if key_entries else None,
                        braille_converter=braille_converter
                    )
                else:
                    final_output = pdf_generator.generate(
                        image=processed_image,
                        output_path=output_path,
                        paper_size=paper_size,
                        metadata=metadata,
                        braille_labels=braille_labels,
                        symbol_key_entries=symbol_key_entries,
                        braille_converter=braille_converter,
                        key_entries=key_entries if key_entries else None
                    )
            except PDFGeneratorError as e:
                return ConversionResult(
                    success=False,
                    error=f"PDF generation failed: {e}",
                    error_type="pdf_error"
                )

            # Build result
            density = metadata.get('density_percentage', 0)
            density_message = self._get_density_message(density)

            # Build warnings
            warnings = []
            if effective_scale_percent is not None and effective_scale_percent > 300:
                warnings.append(f"High scaling ({effective_scale_percent:.0f}%) may degrade image quality.")

            # Build message
            message_parts = ["Converted successfully."]
            if braille_labels_count > 0:
                message_parts.append(f"{braille_labels_count} Braille label(s) added.")
            if key_entries:
                message_parts.append(f"{len(key_entries)} label(s) abbreviated with key page.")
            if zoom_applied:
                message_parts.append("Zoomed to specified region.")
            if effective_scale_percent and effective_scale_percent != 100:
                message_parts.append(f"Image scaled to {effective_scale_percent:.0f}%.")
            message_parts.append(density_message)
            if needs_tiling and params.enable_tiling:
                message_parts.append("Image was tiled across multiple pages.")
            message_parts.append("Ready for PIAF printing.")

            return ConversionResult(
                success=True,
                output_file=str(final_output),
                density_percentage=round(density, 1),
                braille_labels_count=braille_labels_count,
                key_entries_count=len(key_entries) if key_entries else 0,
                detected_text_count=len(texts_to_use),
                scale_applied=effective_scale_percent if effective_scale_percent else 100,
                auto_scale_used=params.auto_scale and effective_scale_percent is not None and effective_scale_percent != 100,
                needs_tiling=needs_tiling,
                page_count=1,  # Single page for basic convert
                warnings=warnings,
                paper_size=paper_size,
                threshold_used=threshold,
                preset_used=params.preset,
                hybrid_ocr_used=params.predetected_texts is not None,
                zoom_applied=zoom_applied,
                original_size=(original_img_width, original_img_height),
                processed_size=(img_width, img_height),
                enhancement_applied=enhance,
                density_reduced=metadata.get('density_reduced', False),
                density_reduction_iterations=metadata.get('density_reduction_iterations', 0),
                message=" ".join(message_parts)
            )

        except ConversionError as e:
            return ConversionResult(
                success=False,
                error=str(e),
                error_type=e.error_type
            )
        except Exception as e:
            logger.error(f"Unexpected error in convert: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                error_type="unexpected_error"
            )

    def _convert_with_rainbowtact(
        self,
        params: ConversionParams,
        processor: 'ImageProcessor',
        standards: 'StandardsLoader',
        image_path_for_processing: str,
        paper_size: str,
        threshold: int,
        zoom_applied,
        original_img_width, original_img_height,
        img_width, img_height
    ) -> ConversionResult:
        """Handle conversion using RainbowTact color-to-tactile patterns."""
        try:
            # Run RainbowTact processing
            processed_image, metadata, color_regions, tactile_patterns = \
                processor.process_with_rainbowtact(
                    input_path=image_path_for_processing,
                    num_colors=params.rainbowtact_num_colors,
                    detect_text=params.detect_text,
                    paper_size=paper_size,
                )

            # Text detection results from RainbowTact processing
            detected_texts = metadata.get('detected_texts', [])

            # EasyOCR override: if no pre-detected, try EasyOCR on original
            if params.detect_text and not detected_texts and not params.predetected_texts:
                try:
                    from tactile_core.core.easyocr_detector import EasyOCRDetector
                    from PIL import Image
                    detector = EasyOCRDetector(language='en', gpu=False)
                    source_image = Image.open(image_path_for_processing)
                    detected_texts = detector.detect_text(source_image)
                except Exception as e:
                    self.logger.warning(f"EasyOCR text detection failed: {e}")

            if params.predetected_texts:
                detected_texts = params.predetected_texts

            # Convert to Braille labels
            braille_labels = None
            key_entries = []
            braille_converter = None
            braille_labels_count = 0

            if params.detect_text and detected_texts:
                try:
                    braille_config = self._create_braille_config(params)
                    braille_converter = BrailleConverter(braille_config, self.logger)

                    if params.use_abbreviation_key or params.force_abbreviation_key:
                        detected_text_widths = {t.text: t.width for t in detected_texts}
                        braille_labels, key_entries = braille_converter.create_braille_labels(
                            detected_texts,
                            generate_key=True,
                            detected_text_widths=detected_text_widths if not params.force_abbreviation_key else None,
                            image_size=processed_image.size
                        )
                    else:
                        braille_labels, _ = braille_converter.create_braille_labels(detected_texts)

                    if braille_labels:
                        braille_labels_count = len(braille_labels)

                    # White out text regions on the pattern image
                    braille_config_dict = standards.get_all_config().get('braille', {})
                    if braille_config_dict.get('whiteout_original_text', True) and detected_texts:
                        processed_image = processor.whiteout_text_regions(
                            processed_image, detected_texts,
                            padding=braille_config_dict.get('whiteout_padding', 5)
                        )
                except Exception as e:
                    self.logger.warning(f"Braille conversion failed: {e}")

            # Generate output path
            output_path = params.output_path or self._generate_output_path(params.input_path)

            # Generate PDF with color pattern legend
            pdf_generator = PIAFPDFGenerator(
                logger=self.logger,
                config=standards.get_all_config()
            )

            try:
                final_output = pdf_generator.generate(
                    image=processed_image,
                    output_path=output_path,
                    paper_size=paper_size,
                    metadata=metadata,
                    braille_labels=braille_labels,
                    braille_converter=braille_converter,
                    key_entries=key_entries if key_entries else None
                )

                # Add color pattern legend page
                # We need to reopen the PDF and add the legend
                # Actually, we'll generate it as part of a multipage approach
            except PDFGeneratorError as e:
                return ConversionResult(
                    success=False,
                    error=f"PDF generation failed: {e}",
                    error_type="pdf_error"
                )

            # Re-generate with legend page included
            # The cleanest approach: generate using the multipage pipeline
            try:
                from reportlab.pdfgen import canvas as reportlab_canvas
                from reportlab.lib.units import inch
                from reportlab.lib.utils import ImageReader
                import io

                page_width, page_height = pdf_generator.SIZES[paper_size]
                page_width_pts = page_width * inch
                page_height_pts = page_height * inch

                c = reportlab_canvas.Canvas(output_path, pagesize=(page_width_pts, page_height_pts))
                c.setTitle(metadata.get('source_file', 'PIAF Color-Tactile') if metadata else 'PIAF Color-Tactile')
                c.setAuthor("TACT — Tactile Architectural Conversion Tool")
                c.setSubject("Color-to-tactile graphics for PIAF printing")
                c.setCreator("tact")

                # Store image height for Braille label coordinate conversion
                pdf_generator.image_height = processed_image.size[1]

                # Check if image fits
                fits, (iw, ih) = pdf_generator.fits_on_page(processed_image, paper_size, pdf_generator.TARGET_DPI)
                if not fits:
                    scale_w = page_width / iw
                    scale_h = page_height / ih
                    scale = min(scale_w, scale_h) * 0.95
                    iw *= scale
                    ih *= scale

                x_offset = (page_width - iw) / 2 * inch
                y_offset = (page_height - ih) / 2 * inch

                # Draw main image
                img_buffer = io.BytesIO()
                processed_image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                img_reader = ImageReader(img_buffer)

                c.drawImage(img_reader, x_offset, y_offset,
                           width=iw * inch, height=ih * inch,
                           preserveAspectRatio=True)

                # Add Braille labels
                if braille_labels:
                    scale_factor = iw / processed_image.size[0]
                    pdf_generator._add_braille_labels(c, braille_labels, scale_factor, x_offset, y_offset)

                # Add abbreviation key page
                if key_entries:
                    c.showPage()
                    pdf_generator.add_abbreviation_key_page(c, key_entries, page_width_pts, page_height_pts)

                # Add color pattern legend page
                c.showPage()
                pdf_generator.add_color_pattern_legend(
                    c, color_regions, tactile_patterns,
                    page_width_pts, page_height_pts
                )

                from tactile_core.utils.validators import resolve_wsl_path, verify_file_exists
                full_output_path = resolve_wsl_path(output_path)
                c.save()

                verify_file_exists(full_output_path)

            except Exception as e:
                return ConversionResult(
                    success=False,
                    error=f"PDF generation with legend failed: {e}",
                    error_type="pdf_error"
                )

            # Build result
            density = metadata.get('density_percentage', 0)
            density_message = self._get_density_message(density)

            message_parts = ["Color-to-tactile conversion complete."]
            message_parts.append(f"{len(color_regions)} color regions mapped to tactile patterns.")
            if braille_labels_count > 0:
                message_parts.append(f"{braille_labels_count} Braille label(s) added.")
            if key_entries:
                message_parts.append(f"{len(key_entries)} label(s) abbreviated with key page.")
            message_parts.append("Color pattern legend page included.")
            message_parts.append(density_message)
            message_parts.append("Ready for PIAF printing.")

            return ConversionResult(
                success=True,
                output_file=str(full_output_path),
                density_percentage=round(density, 1),
                braille_labels_count=braille_labels_count,
                key_entries_count=len(key_entries) if key_entries else 0,
                detected_text_count=len(detected_texts),
                color_to_tactile=True,
                color_regions_count=len(color_regions),
                paper_size=paper_size,
                threshold_used=threshold,
                preset_used=params.preset,
                zoom_applied=zoom_applied,
                original_size=(original_img_width, original_img_height),
                processed_size=(img_width, img_height),
                message=" ".join(message_parts)
            )

        except Exception as e:
            logger.error(f"RainbowTact conversion error: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                error_type="rainbowtact_error"
            )

    def convert_multipage(
        self,
        params: ConversionParams,
        pages: List[Image.Image]
    ) -> ConversionResult:
        """Convert multiple pages to a single PIAF-ready PDF.

        This handles multi-page PDFs where each page is processed independently
        and combined into a single output with a shared symbol key.

        Args:
            params: ConversionParams with all conversion settings
            pages: List of PIL Images representing each page

        Returns:
            ConversionResult with output file path and metadata
        """
        try:
            standards = self._load_configuration()
            threshold, enhance, enhance_strength, paper_size = self._apply_preset(params)

            processor = ImageProcessor(
                config=standards.get_all_config(),
                logger=self.logger
            )

            # Collect results for all pages
            pages_data = []  # List of (processed_image, braille_labels) tuples
            all_key_entries = []
            all_detected_texts = []
            total_braille_labels = 0
            densities = []

            for page_idx, page_image in enumerate(pages, 1):
                # Detect text on this page if requested
                page_detected_texts = []
                if params.detect_text:
                    try:
                        text_config = TextDetectionConfig(
                            enabled=True,
                            language='eng',
                            page_segmentation_mode=3,
                            min_confidence=50,
                            filter_dimensions=True
                        )
                        text_detector = TextDetector(config=text_config, logger=self.logger)
                        gray_image = page_image.convert('L')
                        page_detected_texts = text_detector.detect_text(gray_image, page_number=page_idx)

                        for dt in page_detected_texts:
                            dt.page_number = page_idx
                            all_detected_texts.append(dt)
                    except Exception as e:
                        self.logger.warning(f"Text detection failed for page {page_idx}: {e}")

                # Save page to temp file for processing
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    page_image.save(tmp.name, format='PNG')
                    tmp_path = tmp.name

                try:
                    processed_image, metadata = processor.process(
                        input_path=tmp_path,
                        threshold=threshold,
                        check_density_flag=True,
                        enhance=enhance,
                        enhance_strength=enhance_strength,
                        paper_size=paper_size,
                        auto_reduce_density=params.auto_reduce_density,
                        detect_text=False  # Already did text detection
                    )
                    densities.append(metadata.get('density_percentage', 0))
                except ImageProcessorError as e:
                    return ConversionResult(
                        success=False,
                        error=f"Image processing failed for page {page_idx}: {e}",
                        error_type="processing_error"
                    )

                # Convert to Braille labels
                braille_labels = []
                if params.detect_text and page_detected_texts:
                    try:
                        braille_config = self._create_braille_config(params)
                        braille_converter = BrailleConverter(braille_config, self.logger)

                        braille_labels, page_keys = braille_converter.create_braille_labels(
                            page_detected_texts,
                            generate_key=params.use_abbreviation_key,
                            image_size=processed_image.size
                        )

                        if braille_labels:
                            total_braille_labels += len(braille_labels)

                        if page_keys:
                            for key in page_keys:
                                key.original_text = f"[Page {page_idx}] {key.original_text}"
                            all_key_entries.extend(page_keys)

                        # White out text regions
                        braille_config_dict = standards.get_all_config().get('braille', {})
                        if braille_config_dict.get('whiteout_original_text', True):
                            processed_image = processor.whiteout_text_regions(
                                processed_image,
                                page_detected_texts,
                                padding=braille_config_dict.get('whiteout_padding', 5)
                            )
                    except Exception as e:
                        self.logger.warning(f"Braille conversion failed for page {page_idx}: {e}")

                pages_data.append((processed_image, braille_labels or []))

            # Generate output path
            output_path = params.output_path or self._generate_output_path(params.input_path)

            # Generate multi-page PDF
            pdf_generator = PIAFPDFGenerator(
                logger=self.logger,
                config=standards.get_all_config()
            )

            try:
                braille_converter_for_key = None
                if all_key_entries:
                    braille_config = self._create_braille_config(params)
                    braille_converter_for_key = BrailleConverter(braille_config, self.logger)

                final_output = pdf_generator.generate_multipage(
                    pages_data=pages_data,
                    output_path=output_path,
                    paper_size=paper_size,
                    shared_symbol_key=all_key_entries if all_key_entries else None,
                    braille_converter=braille_converter_for_key
                )
            except PDFGeneratorError as e:
                return ConversionResult(
                    success=False,
                    error=f"PDF generation failed: {e}",
                    error_type="pdf_error"
                )

            avg_density = sum(densities) / len(densities) if densities else 0
            density_message = self._get_density_message(avg_density)

            message_parts = [f"Converted {len(pages)} pages successfully."]
            if total_braille_labels > 0:
                message_parts.append(f"{total_braille_labels} Braille label(s) added across all pages.")
            message_parts.append(density_message)
            if all_key_entries:
                message_parts.append(f"Shared symbol key with {len(all_key_entries)} entries on final page.")
            message_parts.append("Ready for PIAF printing.")

            return ConversionResult(
                success=True,
                output_file=str(final_output),
                density_percentage=round(avg_density, 1),
                braille_labels_count=total_braille_labels,
                key_entries_count=len(all_key_entries),
                detected_text_count=len(all_detected_texts),
                page_count=len(pages),
                paper_size=paper_size,
                threshold_used=threshold,
                preset_used=params.preset,
                is_multipage=True,
                message=" ".join(message_parts)
            )

        except ConversionError as e:
            return ConversionResult(
                success=False,
                error=str(e),
                error_type=e.error_type
            )
        except Exception as e:
            logger.error(f"Unexpected error in convert_multipage: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                error_type="unexpected_error"
            )

    def convert_multi_region(
        self,
        params: ConversionParams,
        regions: List[Dict[str, Any]]
    ) -> ConversionResult:
        """Convert multiple zoom regions to a multi-page PIAF PDF.

        Each region becomes a separate page in the output PDF.

        Args:
            params: ConversionParams with all conversion settings
            regions: List of dicts with label, x_percent, y_percent, width_percent, height_percent

        Returns:
            ConversionResult with output file path and metadata
        """
        try:
            standards = self._load_configuration()
            threshold, enhance, enhance_strength, paper_size = self._apply_preset(params)

            processor = ImageProcessor(
                config=standards.get_all_config(),
                logger=self.logger
            )

            input_file = Path(params.input_path)
            if not input_file.exists():
                return ConversionResult(
                    success=False,
                    error=f"Image file not found: {params.input_path}",
                    error_type="file_not_found"
                )

            base_image = Image.open(input_file)

            pages_data = []
            all_key_entries = []
            region_labels = []
            total_braille_labels = 0

            braille_config = self._create_braille_config(params)
            braille_converter = BrailleConverter(braille_config, self.logger)

            for region_info in regions:
                region_label = region_info.get('label', f'Region {len(pages_data)+1}')
                region_labels.append(region_label)
                region = (
                    region_info['x_percent'],
                    region_info['y_percent'],
                    region_info['width_percent'],
                    region_info['height_percent']
                )

                # Crop and process region
                region_image = processor.crop_to_region(base_image.copy(), region, margin_percent=10.0)
                region_image = processor.adjust_to_aspect_ratio(region_image, paper_size)
                region_image = processor.scale_to_fill_page(region_image, paper_size, dpi=300)

                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    region_image.save(tmp.name, format='PNG')
                    tmp_path = tmp.name

                region_processed, region_metadata = processor.process(
                    input_path=tmp_path,
                    threshold=threshold,
                    check_density_flag=True,
                    enhance=enhance,
                    enhance_strength=enhance_strength,
                    paper_size=paper_size,
                    auto_reduce_density=params.auto_reduce_density,
                    detect_text=params.detect_text
                )

                # Create Braille labels
                region_braille_labels = []
                if params.detect_text and region_metadata.get('detected_texts'):
                    try:
                        region_labels_result, region_keys = braille_converter.create_braille_labels(
                            region_metadata['detected_texts'],
                            generate_key=params.use_abbreviation_key,
                            image_size=region_processed.size
                        )
                        region_braille_labels = region_labels_result or []
                        total_braille_labels += len(region_braille_labels)

                        if region_keys:
                            for key in region_keys:
                                key.original_text = f"[{region_label}] {key.original_text}"
                            all_key_entries.extend(region_keys)

                        # White out text
                        if region_metadata.get('detected_texts'):
                            region_processed = processor.whiteout_text_regions(
                                region_processed,
                                region_metadata['detected_texts'],
                                padding=5
                            )
                    except Exception as e:
                        self.logger.warning(f"Braille failed for '{region_label}': {e}")

                pages_data.append((region_processed, region_braille_labels))

            base_image.close()

            # Generate output path
            import re
            if params.zoom_to:
                safe_target = re.sub(r'[^\w\s-]', '', params.zoom_to).strip().replace(' ', '_').lower()
                output_path = str(input_file.parent / f"{input_file.stem}_{safe_target}_piaf.pdf")
            else:
                output_path = params.output_path or str(input_file.parent / f"{input_file.stem}_zoomed_piaf.pdf")

            # Generate PDF
            pdf_generator = PIAFPDFGenerator(
                logger=self.logger,
                config=standards.get_all_config()
            )

            try:
                final_output = pdf_generator.generate_multipage(
                    pages_data=pages_data,
                    output_path=output_path,
                    paper_size=paper_size,
                    shared_symbol_key=all_key_entries if all_key_entries else None,
                    braille_converter=braille_converter
                )
            except PDFGeneratorError as e:
                return ConversionResult(
                    success=False,
                    error=f"Multi-region PDF generation failed: {e}",
                    error_type="pdf_error"
                )

            return ConversionResult(
                success=True,
                output_file=str(final_output),
                page_count=len(pages_data),
                regions=region_labels,
                braille_labels_count=total_braille_labels,
                key_entries_count=len(all_key_entries),
                paper_size=paper_size,
                threshold_used=threshold,
                preset_used=params.preset,
                is_multi_region=True,
                message=f"Generated {len(pages_data)}-page PDF with zoomed regions. {total_braille_labels} Braille labels added. Ready for PIAF printing."
            )

        except ConversionError as e:
            return ConversionResult(
                success=False,
                error=str(e),
                error_type=e.error_type
            )
        except Exception as e:
            logger.error(f"Unexpected error in convert_multi_region: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                error_type="unexpected_error"
            )


class ConversionError(Exception):
    """Exception raised for conversion errors."""

    def __init__(self, message: str, error_type: str = "conversion_error"):
        super().__init__(message)
        self.error_type = error_type
