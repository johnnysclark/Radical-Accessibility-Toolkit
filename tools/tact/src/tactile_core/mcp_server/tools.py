"""
MCP tool implementations for tactile.

These functions are exposed to Claude via MCP, enabling natural language
interaction for converting architectural images to tactile graphics.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Union, List, Dict, Any, Tuple

# Heavy imports are lazy-loaded for fast MCP server startup.
# Call _ensure_imports() before using any tactile_core classes.
_imports_loaded = False


def _ensure_imports():
    """Lazy-load heavy tactile_core dependencies on first tool call."""
    global _imports_loaded
    if _imports_loaded:
        return
    global ImageProcessor, ImageProcessorError
    global PIAFPDFGenerator, PDFGeneratorError
    global StandardsLoader, StandardsLoaderError
    global PresetManager, PresetError
    global BrailleConverter, BrailleConfig, KeyEntry
    global TextDetector, TextDetectionConfig, DetectedText
    global EasyOCRDetector
    global create_grid_overlay, grid_cell_to_percent
    global cache_tesseract_results, load_cached_tesseract
    global analyze_label_fit
    global RainbowTactConverter, RainbowTactConfig

    from tactile_core.core.processor import ImageProcessor as _IP, ImageProcessorError as _IPE
    from tactile_core.core.pdf_generator import PIAFPDFGenerator as _PPG, PDFGeneratorError as _PDFE
    from tactile_core.config.standards_loader import StandardsLoader as _SL, StandardsLoaderError as _SLE
    from tactile_core.config.presets import PresetManager as _PM, PresetError as _PE
    from tactile_core.core.braille_converter import BrailleConverter as _BC, BrailleConfig as _BCfg, KeyEntry as _KE
    from tactile_core.core.text_detector import TextDetector as _TD, TextDetectionConfig as _TDC, DetectedText as _DT
    from tactile_core.core.easyocr_detector import EasyOCRDetector as _EOD
    from tactile_core.core.grid_overlay import create_grid_overlay as _CGO, grid_cell_to_percent as _GCP
    from tactile_core.utils.cache import cache_tesseract_results as _CTR, load_cached_tesseract as _LCT
    from tactile_core.core.label_scaler import analyze_label_fit as _ALF
    from tactile_core.core.rainbowtact import RainbowTactConverter as _RTC, RainbowTactConfig as _RTCfg

    ImageProcessor, ImageProcessorError = _IP, _IPE
    PIAFPDFGenerator, PDFGeneratorError = _PPG, _PDFE
    StandardsLoader, StandardsLoaderError = _SL, _SLE
    PresetManager, PresetError = _PM, _PE
    BrailleConverter, BrailleConfig, KeyEntry = _BC, _BCfg, _KE
    TextDetector, TextDetectionConfig, DetectedText = _TD, _TDC, _DT
    EasyOCRDetector = _EOD
    create_grid_overlay, grid_cell_to_percent = _CGO, _GCP
    cache_tesseract_results, load_cached_tesseract = _CTR, _LCT
    analyze_label_fit = _ALF
    RainbowTactConverter, RainbowTactConfig = _RTC, _RTCfg
    _imports_loaded = True

logger = logging.getLogger("tactile-mcp")


class SilentLogger:
    """A logger that doesn't output anything - for MCP server use."""

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


def _get_density_message(density: float) -> str:
    """Generate a human-readable message about density."""
    if density < 30:
        return f"Density {density:.1f}% - optimal for PIAF printing."
    elif density < 40:
        return f"Density {density:.1f}% - acceptable for PIAF."
    elif density < 45:
        return f"Density {density:.1f}% - slightly high, may cause some paper swelling."
    else:
        return f"Density {density:.1f}% - high, consider using auto_reduce_density option."


def _get_quality_criteria(image_type: str) -> str:
    """Get quality assessment criteria based on image type."""
    criteria = {
        "floor_plan": (
            "- Wall boundaries should be clear and continuous\n"
            "- Room labels should be readable (now in Braille)\n"
            "- Doors and windows should be visible as distinct features\n"
            "- Density should be 25-40% for optimal tactile feel"
        ),
        "site_plan": (
            "- Building footprints should be distinct and filled appropriately\n"
            "- Paths and roads should be visible lines\n"
            "- Landscaping should not overwhelm the main features\n"
            "- North arrow and scale should be preserved"
        ),
        "section": (
            "- Vertical structure should be clear (floor lines, ceiling heights)\n"
            "- Levels should be distinct and separated\n"
            "- Materials should be differentiated where possible\n"
            "- Ground line and cut areas should be identifiable"
        ),
        "elevation": (
            "- Building profile should be clear and continuous\n"
            "- Openings (windows, doors) should be visible\n"
            "- Roof line should be distinct\n"
            "- Ground line should be identifiable"
        ),
        "sketch": (
            "- Main lines should be preserved\n"
            "- Light/faint lines may be lost (acceptable)\n"
            "- Overall composition should be recognizable\n"
            "- Density can be lower (15-30%) for sketches"
        )
    }
    return criteria.get(image_type, criteria["floor_plan"])




async def _process_multipage_pdf(
    pdf_pages: list,
    image_file,
    output_path: str,
    preset: str,
    effective_threshold: int,
    enhance: str,
    enhance_strength: float,
    effective_paper_size: str,
    detect_text: bool,
    braille_grade: int,
    auto_reduce_density: bool,
    claude_text_json,
    standards,
    silent_logger
) -> str:
    """
    Process a multi-page PDF and combine all pages into a single tactile output.
    
    This handles the special case where the input is a PDF with multiple pages.
    Each page is processed independently, and the results are combined into
    a single output PDF with a shared symbol key.
    
    Args:
        pdf_pages: List of PIL Images from pdf2image conversion
        image_file: Path object for the input file
        output_path: Optional output path
        preset: Preset name
        effective_threshold: Threshold value to use
        enhance: Enhancement mode
        enhance_strength: Enhancement strength
        effective_paper_size: Paper size
        detect_text: Whether to detect text
        braille_grade: Braille grade (1 or 2)
        auto_reduce_density: Whether to auto-reduce density
        claude_text_json: Claude's text extraction (optional)
        standards: StandardsLoader instance
        silent_logger: SilentLogger instance
    
    Returns:
        JSON string with conversion results
    """
    from PIL import Image
    
    # Generate output path if not specified
    if not output_path:
        output_path = str(image_file.parent / f"{image_file.stem}_piaf.pdf")
    
    # Initialize processor
    processor = ImageProcessor(
        config=standards.get_all_config(),
        logger=silent_logger
    )
    
    # Collect results for all pages
    pages_data = []  # List of (processed_image, braille_labels) tuples
    all_symbol_key_entries = []  # Shared symbol key across all pages
    all_detected_texts = []
    total_braille_labels = 0
    densities = []
    
    # Process each page
    for page_idx, page_image in enumerate(pdf_pages, 1):
        logger.info(f"Processing page {page_idx} of {len(pdf_pages)}")
        
        # Get page dimensions
        img_width, img_height = page_image.size
        
        # Detect text on this page if requested
        page_detected_texts = []
        if detect_text:
            try:
                text_config = TextDetectionConfig(
                    enabled=True,
                    language='eng',
                    page_segmentation_mode=3,
                    min_confidence=50,
                    filter_dimensions=True
                )
                text_detector = TextDetector(config=text_config, logger=silent_logger)
                gray_image = page_image.convert('L')
                page_detected_texts = text_detector.detect_text(gray_image, page_number=page_idx)
                
                # Add page number to each detected text
                for dt in page_detected_texts:
                    dt.page_number = page_idx
                    all_detected_texts.append(dt)
                    
            except Exception as e:
                logger.warning(f"Text detection failed for page {page_idx}: {e}")
        
        # Process the page image
        try:
            # Save page temporarily for processing
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                page_image.save(tmp.name, format='PNG')
                tmp_path = tmp.name
            
            processed_image, metadata = processor.process(
                input_path=tmp_path,
                threshold=effective_threshold,
                check_density_flag=True,
                enhance=enhance,
                enhance_strength=enhance_strength,
                paper_size=effective_paper_size,
                auto_reduce_density=auto_reduce_density,
                detect_text=False  # We already did text detection
            )
            
            # Clean up temp file
            import os as os_module
            os_module.unlink(tmp_path)
            
            densities.append(metadata.get('density_percentage', 0))
            
        except ImageProcessorError as e:
            return json.dumps({
                "success": False,
                "error": f"Image processing failed for page {page_idx}: {e}",
                "error_type": "processing_error"
            })
        
        # Convert detected text to Braille labels for this page
        braille_labels = None
        symbol_key_entries = None
        
        if detect_text and page_detected_texts:
            try:
                braille_config_dict = standards.get_all_config().get('braille', {})
                braille_config = BrailleConfig(
                    enabled=True,
                    grade=int(braille_grade),
                    placement="overlay",
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
                
                braille_converter = BrailleConverter(braille_config, silent_logger)
                braille_labels, symbol_key_entries = braille_converter.create_braille_labels(
                    page_detected_texts
                )
                
                if braille_labels:
                    total_braille_labels += len(braille_labels)
                
                # Add symbol key entries to shared key (with page reference)
                if symbol_key_entries:
                    for entry in symbol_key_entries:
                        # Prefix symbol with page number to avoid conflicts
                        entry.original_text = f"[Page {page_idx}] {entry.original_text}"
                        all_symbol_key_entries.append(entry)
                
                # White out original text regions
                whiteout_enabled = braille_config_dict.get('whiteout_original_text', True)
                whiteout_padding = braille_config_dict.get('whiteout_padding', 5)
                
                if whiteout_enabled and page_detected_texts:
                    processed_image = processor.whiteout_text_regions(
                        processed_image,
                        page_detected_texts,
                        padding=whiteout_padding
                    )
                    
            except Exception as e:
                logger.warning(f"Braille conversion failed for page {page_idx}: {e}")
        
        # Add to pages data
        pages_data.append((processed_image, braille_labels or []))
    
    # Generate multi-page PDF
    pdf_generator = PIAFPDFGenerator(
        logger=silent_logger,
        config=standards.get_all_config()
    )
    
    try:
        # Create braille converter for symbol key page
        braille_converter_for_key = None
        if all_symbol_key_entries:
            try:
                braille_config_dict = standards.get_all_config().get('braille', {})
                braille_config = BrailleConfig(
                    enabled=True,
                    grade=int(braille_grade),
                    font_name=braille_config_dict.get('font_name', 'DejaVu Sans'),
                    font_size=braille_config_dict.get('font_size', 24)
                )
                braille_converter_for_key = BrailleConverter(braille_config, silent_logger)
            except:
                pass
        
        final_output = pdf_generator.generate_multipage(
            pages_data=pages_data,
            output_path=output_path,
            paper_size=effective_paper_size,
            shared_symbol_key=all_symbol_key_entries if all_symbol_key_entries else None,
            braille_converter=braille_converter_for_key
        )
    except PDFGeneratorError as e:
        return json.dumps({
            "success": False,
            "error": f"PDF generation failed: {e}",
            "error_type": "pdf_error"
        })
    
    # Calculate average density
    avg_density = sum(densities) / len(densities) if densities else 0
    density_message = _get_density_message(avg_density)
    
    # Build success message
    message_parts = [f"Converted {len(pdf_pages)} pages successfully."]
    if total_braille_labels > 0:
        message_parts.append(f"{total_braille_labels} Braille label(s) added across all pages.")
    message_parts.append(density_message)
    if all_symbol_key_entries:
        message_parts.append(f"Shared symbol key with {len(all_symbol_key_entries)} entries on final page.")
    message_parts.append("Ready for PIAF printing.")
    
    return json.dumps({
        "success": True,
        "output_file": str(final_output),
        "page_count": len(pdf_pages),
        "density_percentage": round(avg_density, 1),
        "braille_labels_count": total_braille_labels,
        "paper_size": effective_paper_size,
        "threshold_used": effective_threshold,
        "preset_used": preset,
        "detected_text_count": len(all_detected_texts),
        "symbol_key_entries": len(all_symbol_key_entries),
        "is_multipage": True,
        "message": " ".join(message_parts)
    })


async def _process_rainbowtact(
    processor,
    image_path_for_processing: str,
    image_file,
    output_path: str,
    effective_paper_size: str,
    effective_threshold: int,
    preset,
    detect_text: bool,
    braille_grade: int,
    rainbowtact_num_colors: int,
    merged_detected_texts,
    use_abbreviation_key: bool,
    force_abbreviation_key: bool,
    effective_scale_percent,
    zoom_applied,
    standards,
    silent_logger,
) -> str:
    """Process image using RainbowTact color-to-tactile conversion."""
    from PIL import Image
    import io

    try:
        # Run RainbowTact processing
        from tactile_core.core.rainbowtact import RainbowTactConverter, RainbowTactConfig

        processed_image, metadata, color_regions, tactile_patterns = \
            processor.process_with_rainbowtact(
                input_path=image_path_for_processing,
                num_colors=rainbowtact_num_colors,
                detect_text=detect_text and not merged_detected_texts,
                paper_size=effective_paper_size,
            )

        # Use pre-detected texts or processor's detected texts
        detected_texts = merged_detected_texts or metadata.get('detected_texts', [])

        # Convert to Braille labels
        braille_labels = None
        key_entries = []
        braille_converter = None
        braille_labels_count = 0

        if detect_text and detected_texts:
            try:
                braille_config_dict = standards.get_all_config().get('braille', {})
                braille_config = BrailleConfig(
                    enabled=True,
                    grade=int(braille_grade),
                    placement="overlay",
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
                braille_converter = BrailleConverter(braille_config, silent_logger)

                if use_abbreviation_key or force_abbreviation_key:
                    detected_text_widths = {t.text: t.width for t in detected_texts}
                    braille_labels, key_entries = braille_converter.create_braille_labels(
                        detected_texts,
                        generate_key=True,
                        detected_text_widths=detected_text_widths if not force_abbreviation_key else None
                    )
                else:
                    braille_labels, _ = braille_converter.create_braille_labels(detected_texts)

                if braille_labels:
                    braille_labels_count = len(braille_labels)

                # White out original text regions
                whiteout_enabled = braille_config_dict.get('whiteout_original_text', True)
                whiteout_padding = braille_config_dict.get('whiteout_padding', 5)
                if whiteout_enabled and detected_texts:
                    processed_image = processor.whiteout_text_regions(
                        processed_image, detected_texts, padding=whiteout_padding
                    )
            except Exception as e:
                logger.warning(f"Braille conversion failed: {e}")

        # Generate PDF with legend page
        pdf_generator = PIAFPDFGenerator(
            logger=silent_logger,
            config=standards.get_all_config()
        )

        from reportlab.pdfgen import canvas as reportlab_canvas
        from reportlab.lib.units import inch
        from reportlab.lib.utils import ImageReader
        from tactile_core.utils.validators import resolve_wsl_path, verify_file_exists

        page_width, page_height = pdf_generator.SIZES[effective_paper_size]
        page_width_pts = page_width * inch
        page_height_pts = page_height * inch

        c = reportlab_canvas.Canvas(output_path, pagesize=(page_width_pts, page_height_pts))
        c.setTitle(metadata.get('source_file', 'PIAF Color-Tactile'))
        c.setAuthor("TACT — Tactile Architectural Conversion Tool")
        c.setSubject("Color-to-tactile graphics for PIAF printing")
        c.setCreator("tact")

        pdf_generator.image_height = processed_image.size[1]

        fits, (iw, ih) = pdf_generator.fits_on_page(processed_image, effective_paper_size, pdf_generator.TARGET_DPI)
        if not fits:
            scale_w = page_width / iw
            scale_h = page_height / ih
            scale = min(scale_w, scale_h) * 0.95
            iw *= scale
            ih *= scale

        x_offset = (page_width - iw) / 2 * inch
        y_offset = (page_height - ih) / 2 * inch

        img_buffer = io.BytesIO()
        processed_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)

        c.drawImage(img_reader, x_offset, y_offset,
                   width=iw * inch, height=ih * inch, preserveAspectRatio=True)

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
            c, color_regions, tactile_patterns, page_width_pts, page_height_pts
        )

        full_output_path = resolve_wsl_path(output_path)
        c.save()

        density = metadata.get('density_percentage', 0)
        density_message = _get_density_message(density)

        message_parts = ["Color-to-tactile conversion complete."]
        message_parts.append(f"{len(color_regions)} color regions mapped to tactile patterns.")
        if braille_labels_count > 0:
            message_parts.append(f"{braille_labels_count} Braille label(s) added.")
        if key_entries:
            message_parts.append(f"{len(key_entries)} label(s) abbreviated with key page.")
        message_parts.append("Color pattern legend page included.")
        message_parts.append(density_message)
        message_parts.append("Ready for PIAF printing.")

        return json.dumps({
            "success": True,
            "output_file": str(full_output_path),
            "density_percentage": round(density, 1),
            "braille_labels_count": braille_labels_count,
            "key_entries_count": len(key_entries) if key_entries else 0,
            "color_to_tactile": True,
            "color_regions_count": len(color_regions),
            "color_regions": [
                {"name": r.color_name, "type": "chromatic" if r.is_chromatic else "achromatic"}
                for r in color_regions
            ],
            "scale_applied": effective_scale_percent if effective_scale_percent else 100,
            "paper_size": effective_paper_size,
            "threshold_used": effective_threshold,
            "preset_used": preset,
            "detected_text_count": len(detected_texts),
            "zoom_applied": zoom_applied,
            "message": " ".join(message_parts)
        })

    except Exception as e:
        logger.error(f"RainbowTact conversion error: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "rainbowtact_error"
        })


async def image_to_piaf(
    image_path: str,
    output_path: Optional[str] = None,
    preset: Optional[str] = None,
    threshold: Optional[int] = None,
    paper_size: str = "letter",
    detect_text: bool = True,
    braille_grade: int = 2,
    auto_reduce_density: bool = False,
    tile_overlap: float = 0.0,
    claude_text_json: Optional[Union[str, List[Dict[str, Any]]]] = None,
    use_grid_overlay: bool = False,
    assess_quality: bool = False,
    scale_percent: Optional[float] = None,
    auto_scale: bool = True,
    max_scale_factor: Optional[float] = None,
    use_abbreviation_key: bool = True,
    force_abbreviation_key: bool = False,
    zoom_region: Optional[Tuple[float, float, float, float]] = None,
    zoom_to: Optional[str] = None,
    zoom_regions: Optional[List[Dict[str, Any]]] = None,
    sticker_workflow: bool = False,
    color_to_tactile: bool = False,
    rainbowtact_num_colors: int = 5
) -> str:
    """
    Convert an architectural image to a PIAF-ready tactile PDF.

    This tool processes images (floor plans, sections, diagrams, etc.) and
    creates high-contrast PDFs suitable for printing on PIAF tactile machines.

    When detect_text=True, text is automatically detected using EasyOCR and
    converted to Braille labels in a single call. No multi-step workflow needed.
    If EasyOCR is unavailable, falls back to Tesseract OCR.

    You can optionally pass claude_text_json to manually specify text positions,
    which overrides automatic detection.

    When color_to_tactile=True, uses the RainbowTact algorithm to convert colors
    into distinguishable tactile patterns (waves for chromatic, dots for achromatic)
    instead of simple B&W thresholding. Includes a color pattern legend page.

    Args:
        image_path: Path to the input image file (JPG, PNG, TIFF, BMP, GIF, or PDF)
        output_path: Path for output PDF. If not specified, creates {input_name}_piaf.pdf
        preset: Preset configuration to use (floor_plan, section, sketch, etc.)
        threshold: Black/white threshold 0-255. Higher = more black. Default varies by preset.
        paper_size: Output paper size - "letter" (8.5x11") or "tabloid" (11x17")
        detect_text: Enable OCR to detect text/dimensions and convert to Braille (default: True)
        braille_grade: Braille grade - 1 (uncontracted) or 2 (contracted, recommended)
        auto_reduce_density: Automatically reduce density if too high for PIAF
        tile_overlap: Overlap between tiles for large images (0.0-1.0, default 0.0 for no overlap)
        claude_text_json: Optional manual text override as JSON string or list of dicts.
                         When provided, skips automatic OCR and uses these positions directly.
        use_grid_overlay: Enable grid overlay for more precise text positioning using cell references (e.g., "C4")
        assess_quality: Enable quality assessment - returns instructions for visual comparison (default: False)
        scale_percent: Manual zoom/scale percentage. None=auto (uses auto_scale), 150=1.5x, 200=2x.
                      Overrides auto_scale when specified.
        auto_scale: Automatically scale the image so Braille labels fit in original text bounding boxes.
                   Default: True. Scales as much as needed unless max_scale_factor is set.
        max_scale_factor: Optional cap on auto-scale factor (e.g., 2.0 = 200%). Default: None (no cap).
                         When set, labels that don't fit after capped scaling get abbreviated to key.
                         Warning issued when scaling exceeds 300%.
        use_abbreviation_key: Auto-abbreviate labels that don't fit in their bounding box to single
                             letters (A, B, C...) and generate a key page mapping letters to full text.
                             Default: True.
        force_abbreviation_key: Abbreviate ALL labels regardless of whether they fit, creating a
                               comprehensive key page. Useful for dense drawings. Default: False.
        zoom_region: Zoom to a specific region. Format: (x_percent, y_percent, width_percent, height_percent)
                    where each value is 0-100. Example: (25, 30, 50, 40) starts at 25% from left,
                    30% from top, cropping 50% of width and 40% of height. Includes 10% margin.
        zoom_to: Natural language description of region to zoom to (e.g., "Bedroom", "Kitchen",
                "staircase", "upper-left area"). Returns instructions for Claude to identify the region
                using vision, then call again with zoom_region or zoom_regions.
        zoom_regions: Multiple regions for multi-page output. List of dicts with keys:
                     label, x_percent, y_percent, width_percent, height_percent.
                     Each region becomes a page in the output PDF.
        sticker_workflow: Generate dual PDFs for Braille sticker workflow. Creates:
                         1. PIAF PDF with counter-highlighted text (no Braille) for swelling
                         2. Text-only PDF for second print pass alignment
                         Both include registration marks for paper alignment. Default: False.
        color_to_tactile: Enable RainbowTact color-to-tactile conversion. Instead of simple
                         B&W thresholding, maps colors to distinguishable tactile patterns
                         (waves for chromatic colors, dots for achromatic). Includes a color
                         pattern legend page. Default: False.
        rainbowtact_num_colors: Number of color clusters for RainbowTact segmentation (2-10).
                               More colors = more patterns but harder to distinguish. Default: 5.

    Returns:
        JSON string with conversion results including output file path and metadata
    """
    _ensure_imports()
    try:
        silent_logger = SilentLogger()

        # Load configuration
        try:
            standards = StandardsLoader()
        except StandardsLoaderError as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to load configuration: {e}",
                "error_type": "configuration_error"
            })

        # Apply preset if specified
        effective_threshold = threshold
        enhance = None
        enhance_strength = 1.0
        effective_paper_size = paper_size

        if preset:
            try:
                preset_manager = PresetManager()
                preset_settings = preset_manager.get_preset_settings(preset)
                preset_info = preset_manager.get_preset_info(preset)

                # Apply preset settings (explicit parameters override preset)
                if effective_threshold is None:
                    effective_threshold = preset_settings.get('threshold', 128)
                if paper_size == "letter":  # Only override if using default
                    effective_paper_size = preset_settings.get('paper_size', 'letter')
                enhance = preset_settings.get('enhance')
                enhance_strength = preset_settings.get('enhance_strength', 1.0)

                logger.info(f"Using preset: {preset_info['name']}")
            except PresetError as e:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid preset '{preset}': {e}",
                    "error_type": "preset_error"
                })

        # Set default threshold if still not set
        if effective_threshold is None:
            effective_threshold = standards.get_default_threshold()

        # Initialize processor early (needed for zoom operations)
        processor = ImageProcessor(
            config=standards.get_all_config(),
            logger=silent_logger
        )

        # Validate image path
        image_file = Path(image_path)
        if not image_file.exists():
            return json.dumps({
                "success": False,
                "error": f"Image file not found: {image_path}",
                "error_type": "file_not_found"
            })

        # ============================================================
        # MULTI-PAGE PDF DETECTION AND HANDLING
        # ============================================================
        from PIL import Image
        
        # Check if this is a multi-page PDF
        is_multipage_pdf = False
        pdf_pages = []
        
        if image_file.suffix.lower() == '.pdf':
            try:
                from pdf2image import convert_from_path
                # Convert PDF pages to images at 300 DPI for quality
                pdf_pages = convert_from_path(str(image_file), dpi=300)
                if len(pdf_pages) > 1:
                    is_multipage_pdf = True
                    logger.info(f"Multi-page PDF detected: {len(pdf_pages)} pages")
            except ImportError:
                # pdf2image not installed, fall back to single-page handling
                logger.warning("pdf2image not installed. Multi-page PDF support unavailable.")
                logger.warning("Install with: pip install pdf2image")
            except Exception as e:
                logger.warning(f"Failed to read PDF pages: {e}")
        
        # If multi-page PDF, process all pages together
        if is_multipage_pdf and len(pdf_pages) > 1:
            return await _process_multipage_pdf(
                pdf_pages=pdf_pages,
                image_file=image_file,
                output_path=output_path,
                preset=preset,
                effective_threshold=effective_threshold,
                enhance=enhance,
                enhance_strength=enhance_strength,
                effective_paper_size=effective_paper_size,
                detect_text=detect_text,
                braille_grade=braille_grade,
                auto_reduce_density=auto_reduce_density,
                claude_text_json=claude_text_json,
                standards=standards,
                silent_logger=silent_logger
            )

        # Get image dimensions for hybrid OCR (single image or single-page PDF)
        if pdf_pages:
            # Single-page PDF - use first page
            img = pdf_pages[0]
            img_width, img_height = img.size
        else:
            with Image.open(image_file) as img:
                img_width, img_height = img.size

        # Track original dimensions for scaling
        original_img_width, original_img_height = img_width, img_height

        # Track if we applied scaling (for later coordinate adjustment)
        effective_scale_percent = None
        scaled_image_path = None  # Temp path if we scale the image

        # Track zoom information
        zoom_applied = None
        zoom_label = None

        # ============================================================
        # ZOOM PHASE 0: LLM-Assisted Zoom Region Identification
        # ============================================================
        if zoom_to and not zoom_region and not zoom_regions:
            # Return instructions for Claude to identify the region using vision
            return json.dumps({
                "success": True,
                "phase": "zoom_region_identification",
                "image_path": str(image_file.absolute()),
                "image_size": {"width": img_width, "height": img_height},
                "zoom_target": zoom_to,
                "instructions": (
                    f"ZOOM REGION IDENTIFICATION for: '{zoom_to}'\n\n"
                    f"Please view the image at: {image_file.absolute()}\n"
                    f"Image dimensions: {img_width}x{img_height} pixels\n\n"
                    "Identify the region(s) matching the target. Return a JSON array:\n"
                    "[\n"
                    "  {\n"
                    '    "label": "Bedroom 1",\n'
                    '    "x_percent": 25,\n'
                    '    "y_percent": 30,\n'
                    '    "width_percent": 30,\n'
                    '    "height_percent": 25,\n'
                    '    "confidence": "high"\n'
                    "  }\n"
                    "]\n\n"
                    "SEARCH STRATEGIES:\n"
                    "1. Look for text labels (e.g., 'BEDROOM', 'Kitchen')\n"
                    "2. Identify room shapes and boundaries\n"
                    "3. For features (staircase, door), identify the element\n"
                    "4. For spatial (upper-left), calculate quadrant coordinates\n\n"
                    "After identification, call image_to_piaf again with:\n"
                    "- Same image_path\n"
                    "- For single region: zoom_region=(x_percent, y_percent, width_percent, height_percent)\n"
                    "- For multiple matches: zoom_regions=[{label, x_percent, y_percent, ...}, ...]"
                ),
                "message": f"Please view the image and identify region(s) matching '{zoom_to}'."
            })

        # ============================================================
        # ZOOM PHASE 1: Apply Zoom Region (Single or Multi)
        # ============================================================
        if zoom_regions and len(zoom_regions) > 1:
            # Multi-region zoom: generate multi-page PDF
            # This is handled later after all processing setup
            pass  # Will be handled in PDF generation section

        elif zoom_region or (zoom_regions and len(zoom_regions) == 1):
            # Single region zoom
            if zoom_regions:
                region_info = zoom_regions[0]
                zoom_label = region_info.get('label')
                zoom_region = (
                    region_info['x_percent'],
                    region_info['y_percent'],
                    region_info['width_percent'],
                    region_info['height_percent']
                )

            # Load the base image for cropping
            if pdf_pages:
                base_image = pdf_pages[0].copy()
            else:
                base_image = Image.open(image_file)

            # Crop to region with 10% margin
            cropped_image = processor.crop_to_region(base_image, zoom_region, margin_percent=10.0)

            # Adjust to paper aspect ratio
            cropped_image = processor.adjust_to_aspect_ratio(cropped_image, effective_paper_size)

            # Scale up to fill the page
            cropped_image = processor.scale_to_fill_page(cropped_image, effective_paper_size, dpi=300)

            # Save cropped image to temp file for further processing
            import tempfile
            zoom_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='zoom_')
            cropped_image.save(zoom_temp.name, format='PNG')

            # Update tracking variables
            img_width, img_height = cropped_image.size
            image_path_for_processing = zoom_temp.name
            zoom_applied = {
                "region": zoom_region,
                "label": zoom_label,
                "original_size": {"width": original_img_width, "height": original_img_height},
                "cropped_size": {"width": img_width, "height": img_height}
            }

            logger.info(f"Zoomed to region {zoom_region}, cropped to {img_width}x{img_height}")

        # ============================================================
        # TEXT DETECTION: EasyOCR (primary) or Tesseract (fallback)
        # ============================================================
        merged_detected_texts = None

        if detect_text and claude_text_json:
            # Manual override: user provided text positions directly
            try:
                if isinstance(claude_text_json, str):
                    manual_results = json.loads(claude_text_json)
                else:
                    manual_results = claude_text_json

                # Convert manual results to DetectedText objects
                merged_detected_texts = []
                for item in manual_results:
                    # Support both pixel and percent-based coordinates
                    if 'x' in item and 'y' in item:
                        x, y = int(item['x']), int(item['y'])
                        w, h = int(item.get('width', 50)), int(item.get('height', 20))
                    elif 'x_percent' in item and 'y_percent' in item:
                        x = int(float(item['x_percent']) / 100 * img_width)
                        y = int(float(item['y_percent']) / 100 * img_height)
                        w = int(float(item.get('width_percent', 5)) / 100 * img_width)
                        h = int(float(item.get('height_percent', 2)) / 100 * img_height)
                    else:
                        continue

                    merged_detected_texts.append(DetectedText(
                        text=item.get('text', ''),
                        x=x, y=y, width=w, height=h,
                        confidence=80.0,
                        is_dimension=item.get('type') == 'dimension',
                        rotation_degrees=float(item.get('rotation_degrees', 0)),
                    ))
                logger.info(f"Manual text override: {len(merged_detected_texts)} items")

            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Invalid claude_text_json, falling back to auto-detect: {e}")
                merged_detected_texts = None

        if detect_text and not merged_detected_texts:
            # Auto-detect text using EasyOCR (preferred) or Tesseract (fallback)
            try:
                detector = EasyOCRDetector(language='en', gpu=False)
                source_image = Image.open(image_file)
                merged_detected_texts = detector.detect_text(source_image)
                logger.info(f"EasyOCR detected {len(merged_detected_texts)} text items")
            except Exception as e:
                logger.warning(f"EasyOCR failed, falling back to Tesseract: {e}")
                try:
                    text_config = TextDetectionConfig(
                        enabled=True,
                        language='eng',
                        page_segmentation_mode=3,
                        min_confidence=50,
                        filter_dimensions=True
                    )
                    text_detector = TextDetector(config=text_config, logger=silent_logger)
                    gray_image = Image.open(image_file).convert('L')
                    merged_detected_texts = text_detector.detect_text(gray_image)
                    logger.info(f"Tesseract fallback detected {len(merged_detected_texts)} text items")
                except Exception as e2:
                    logger.warning(f"Tesseract also failed: {e2}")
                    # Continue without text detection

        # Generate output path if not specified
        if not output_path:
            # Include zoom target in filename if zooming
            if zoom_applied and zoom_applied.get('label'):
                import re
                safe_label = re.sub(r'[^\w\s-]', '', zoom_applied['label']).strip().replace(' ', '_').lower()
                output_path = str(image_file.parent / f"{image_file.stem}_{safe_label}_piaf.pdf")
            elif zoom_to:
                import re
                safe_target = re.sub(r'[^\w\s-]', '', zoom_to).strip().replace(' ', '_').lower()
                output_path = str(image_file.parent / f"{image_file.stem}_{safe_target}_piaf.pdf")
            else:
                output_path = str(image_file.parent / f"{image_file.stem}_piaf.pdf")

        # ============================================================
        # AUTO-SCALING: Analyze label fit and scale image if needed
        # ============================================================
        # Use zoomed image path if zoom was applied, otherwise original
        if not zoom_applied:
            image_path_for_processing = str(image_path)

        # Handle manual scale_percent even without text detection
        if scale_percent is not None and not merged_detected_texts:
            effective_scale_percent = scale_percent
            # Apply manual scaling
            if effective_scale_percent != 100:
                import tempfile

                if pdf_pages:
                    base_image = pdf_pages[0]
                else:
                    base_image = Image.open(image_file)

                scaled_image = processor.scale_image(base_image, effective_scale_percent)
                img_width, img_height = scaled_image.size

                scaled_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='scaled_')
                scaled_image.save(scaled_temp.name, format='PNG')
                scaled_image_path = scaled_temp.name
                image_path_for_processing = scaled_image_path

                logger.info(f"Manual scaling applied: {effective_scale_percent:.0f}%")

        if merged_detected_texts and (auto_scale or scale_percent is not None):
            # Analyze how much scaling is needed for labels to fit
            fit_analysis = analyze_label_fit(
                merged_detected_texts,
                (img_width, img_height),
                braille_grade=braille_grade
            )

            recommended_scale = fit_analysis.get('recommended_scale', 100)
            labels_needing_key = len(fit_analysis.get('needs_key', []))

            logger.info(f"Label fit analysis: {len(fit_analysis.get('fits', []))} fit, {labels_needing_key} need key, recommended scale: {recommended_scale:.0f}%")

            # Determine effective scale
            if scale_percent is not None:
                # Manual scale overrides auto
                effective_scale_percent = scale_percent
            elif auto_scale and recommended_scale > 100:
                # Auto-scale, optionally capped at max_scale_factor
                if max_scale_factor is not None:
                    max_scale = max_scale_factor * 100
                    effective_scale_percent = min(recommended_scale, max_scale)
                    logger.info(f"Auto-scaling to {effective_scale_percent:.0f}% (recommended: {recommended_scale:.0f}%, max: {max_scale:.0f}%)")
                else:
                    # No cap - scale as much as needed
                    effective_scale_percent = recommended_scale
                    logger.info(f"Auto-scaling to {effective_scale_percent:.0f}% (no cap)")

            # Apply scaling if needed
            if effective_scale_percent and effective_scale_percent != 100:
                import tempfile

                # Load the original image
                if pdf_pages:
                    base_image = pdf_pages[0]
                else:
                    base_image = Image.open(image_file)

                # Scale the image
                scaled_image = processor.scale_image(base_image, effective_scale_percent)
                img_width, img_height = scaled_image.size

                # Save to temp file for processor.process()
                scaled_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='scaled_')
                scaled_image.save(scaled_temp.name, format='PNG')
                scaled_image_path = scaled_temp.name
                image_path_for_processing = scaled_image_path

                logger.info(f"Scaled image from {original_img_width}x{original_img_height} to {img_width}x{img_height}")

                # Scale detected text coordinates to match
                merged_detected_texts = processor.scale_detected_texts(merged_detected_texts, effective_scale_percent)
                logger.info(f"Scaled {len(merged_detected_texts)} detected text coordinates")

        # ============================================================
        # RAINBOWTACT: Color-to-Tactile Pattern Conversion
        # ============================================================
        if color_to_tactile:
            return await _process_rainbowtact(
                processor=processor,
                image_path_for_processing=image_path_for_processing,
                image_file=image_file,
                output_path=output_path,
                effective_paper_size=effective_paper_size,
                effective_threshold=effective_threshold,
                preset=preset,
                detect_text=detect_text,
                braille_grade=braille_grade,
                rainbowtact_num_colors=rainbowtact_num_colors,
                merged_detected_texts=merged_detected_texts,
                use_abbreviation_key=use_abbreviation_key,
                force_abbreviation_key=force_abbreviation_key,
                effective_scale_percent=effective_scale_percent,
                zoom_applied=zoom_applied,
                standards=standards,
                silent_logger=silent_logger
            )

        # If we have merged results from hybrid OCR, skip text detection in processor
        # (we already have the text, just need image processing)
        should_run_tesseract = detect_text and not merged_detected_texts

        try:
            processed_image, metadata = processor.process(
                input_path=image_path_for_processing,
                threshold=effective_threshold,
                check_density_flag=True,
                enhance=enhance,
                enhance_strength=enhance_strength,
                paper_size=effective_paper_size,
                auto_reduce_density=auto_reduce_density,
                detect_text=should_run_tesseract  # Skip if we have hybrid results
            )
        except ImageProcessorError as e:
            return json.dumps({
                "success": False,
                "error": f"Image processing failed: {e}",
                "error_type": "processing_error"
            })

        # Use merged results from hybrid OCR if available, otherwise use Tesseract results
        detected_texts_to_use = merged_detected_texts or metadata.get('detected_texts', [])

        # Convert detected text to Braille labels
        braille_labels = None
        symbol_key_entries = None
        key_entries = []  # Abbreviation key entries
        braille_converter = None
        braille_labels_count = 0

        if detect_text and detected_texts_to_use:
            try:
                braille_config_dict = standards.get_all_config().get('braille', {})

                braille_config = BrailleConfig(
                    enabled=True,
                    grade=int(braille_grade),
                    placement="overlay",
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

                braille_converter = BrailleConverter(braille_config, silent_logger)

                # ============================================================
                # ABBREVIATION KEY: Generate key for labels that don't fit
                # ============================================================
                if use_abbreviation_key or force_abbreviation_key:
                    # Build detected_text_widths dict for fit analysis
                    detected_text_widths = {text.text: text.width for text in detected_texts_to_use}

                    # Call create_braille_labels with generate_key=True
                    braille_labels, key_entries = braille_converter.create_braille_labels(
                        detected_texts_to_use,
                        generate_key=True,
                        detected_text_widths=detected_text_widths if not force_abbreviation_key else None
                    )

                    if force_abbreviation_key:
                        # When forcing, all labels get abbreviated
                        logger.info(f"Force abbreviation: {len(key_entries)} key entries generated for all labels")
                    elif key_entries:
                        logger.info(f"Abbreviation key: {len(key_entries)} labels abbreviated (didn't fit in bounding box)")
                else:
                    # Standard Braille label creation without abbreviation key
                    braille_labels, symbol_key_entries = braille_converter.create_braille_labels(
                        detected_texts_to_use
                    )

                if braille_labels:
                    braille_labels_count = len(braille_labels)

                # White out original text regions
                whiteout_enabled = braille_config_dict.get('whiteout_original_text', True)
                whiteout_padding = braille_config_dict.get('whiteout_padding', 5)

                if whiteout_enabled and detected_texts_to_use:
                    processed_image = processor.whiteout_text_regions(
                        processed_image,
                        detected_texts_to_use,  # Use merged or Tesseract results
                        padding=whiteout_padding
                    )

            except Exception as e:
                logger.warning(f"Braille conversion failed: {e}")
                # Continue without Braille - don't fail the whole conversion

        # Generate PDF
        pdf_generator = PIAFPDFGenerator(
            logger=silent_logger,
            config=standards.get_all_config()
        )

        needs_tiling = metadata.get('needs_tiling', False)

        # ============================================================
        # MULTI-REGION ZOOM: Generate multi-page PDF with each region
        # ============================================================
        if zoom_regions and len(zoom_regions) > 1:
            import re
            import tempfile

            pages_data = []
            all_key_entries = []

            # Load the original base image once
            if pdf_pages:
                base_image_for_zoom = pdf_pages[0]
            else:
                base_image_for_zoom = Image.open(image_file)

            for region_info in zoom_regions:
                region_label = region_info.get('label', f'Region {len(pages_data)+1}')
                region = (
                    region_info['x_percent'],
                    region_info['y_percent'],
                    region_info['width_percent'],
                    region_info['height_percent']
                )

                # Crop to this region with 10% margin
                region_image = processor.crop_to_region(base_image_for_zoom.copy(), region, margin_percent=10.0)
                region_image = processor.adjust_to_aspect_ratio(region_image, effective_paper_size)
                # Scale up to fill the page
                region_image = processor.scale_to_fill_page(region_image, effective_paper_size, dpi=300)

                # Save to temp file for processing
                region_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='region_')
                region_image.save(region_temp.name, format='PNG')

                # Process the region
                region_processed, region_metadata = processor.process(
                    input_path=region_temp.name,
                    threshold=effective_threshold,
                    check_density_flag=True,
                    enhance=enhance,
                    enhance_strength=enhance_strength,
                    paper_size=effective_paper_size,
                    auto_reduce_density=auto_reduce_density,
                    detect_text=detect_text
                )

                # Create Braille labels for this region
                region_braille_labels = []
                if detect_text and region_metadata.get('detected_texts'):
                    try:
                        region_labels, region_keys = braille_converter.create_braille_labels(
                            region_metadata['detected_texts'],
                            generate_key=use_abbreviation_key
                        )
                        region_braille_labels = region_labels or []
                        if region_keys:
                            # Add region label prefix to key entries
                            for key in region_keys:
                                key.original_text = f"[{region_label}] {key.original_text}"
                            all_key_entries.extend(region_keys)

                        # White out text regions
                        if region_metadata.get('detected_texts'):
                            region_processed = processor.whiteout_text_regions(
                                region_processed,
                                region_metadata['detected_texts'],
                                padding=5
                            )
                    except Exception as e:
                        logger.warning(f"Braille conversion failed for region '{region_label}': {e}")

                pages_data.append((region_processed, region_braille_labels))
                logger.info(f"Processed zoom region: {region_label}")

            # Generate multi-page PDF
            # Create output filename with zoom target
            if zoom_to:
                safe_target = re.sub(r'[^\w\s-]', '', zoom_to).strip().replace(' ', '_').lower()
                multi_output_path = str(image_file.parent / f"{image_file.stem}_{safe_target}_piaf.pdf")
            else:
                multi_output_path = str(image_file.parent / f"{image_file.stem}_zoomed_piaf.pdf")

            try:
                final_output = pdf_generator.generate_multipage(
                    pages_data=pages_data,
                    output_path=multi_output_path,
                    paper_size=effective_paper_size,
                    shared_symbol_key=all_key_entries if all_key_entries else None,
                    braille_converter=braille_converter
                )
            except PDFGeneratorError as e:
                return json.dumps({
                    "success": False,
                    "error": f"Multi-region PDF generation failed: {e}",
                    "error_type": "pdf_error"
                })

            # Build response for multi-region output
            total_braille = sum(len(labels) for _, labels in pages_data)
            return json.dumps({
                "success": True,
                "output_file": str(final_output),
                "page_count": len(pages_data),
                "regions": [r.get('label', f'Region {i+1}') for i, r in enumerate(zoom_regions)],
                "braille_labels_count": total_braille,
                "key_entries_count": len(all_key_entries),
                "paper_size": effective_paper_size,
                "threshold_used": effective_threshold,
                "zoom_target": zoom_to,
                "is_multi_region": True,
                "message": f"Generated {len(pages_data)}-page PDF with zoomed regions. {total_braille} Braille labels added. Ready for PIAF printing."
            })

        try:
            if sticker_workflow:
                # Sticker workflow: Generate dual PDFs for Braille sticker alignment
                if not detected_texts_to_use:
                    return json.dumps({
                        "success": False,
                        "error": "Sticker workflow requires text detection, but no text was detected",
                        "error_type": "sticker_workflow_error"
                    })

                # Generate output filenames
                output_base = output_path.rsplit('.pdf', 1)[0] if output_path.endswith('.pdf') else output_path
                piaf_output = f"{output_base}_piaf.pdf"
                text_output = f"{output_base}_text.pdf"

                # 1. Generate PIAF PDF (counter-highlighted, no Braille, with registration mark)
                piaf_path = pdf_generator.generate(
                    image=processed_image,
                    output_path=piaf_output,
                    paper_size=effective_paper_size,
                    metadata=metadata,
                    braille_labels=None,  # No Braille for sticker workflow
                    symbol_key_entries=None,
                    braille_converter=None,
                    key_entries=None,
                    sticker_workflow=True,
                    page_number=1
                )

                # 2. Generate text-only PDF (for second print pass)
                text_path = pdf_generator.generate_text_only_pdf(
                    detected_texts=detected_texts_to_use,
                    output_path=text_output,
                    paper_size=effective_paper_size,
                    page_number=1,
                    image_size=processed_image.size
                )

                density = metadata.get('density_percentage', 0)
                return json.dumps({
                    "success": True,
                    "sticker_workflow": True,
                    "piaf_output": str(piaf_path),
                    "text_output": str(text_path),
                    "density_percentage": round(density, 1),
                    "detected_text_count": len(detected_texts_to_use),
                    "paper_size": effective_paper_size,
                    "threshold_used": effective_threshold,
                    "message": (
                        f"Sticker workflow PDFs generated. "
                        f"PIAF version: {piaf_path}, Text version: {text_path}. "
                        f"{len(detected_texts_to_use)} text regions detected. "
                        "Workflow: 1) Print and swell PIAF PDF, 2) Reload paper aligned to bottom-right mark, "
                        "3) Print text PDF, 4) Apply Braille stickers over text."
                    )
                })

            elif needs_tiling:
                # Generate tiled PDF for oversized images
                final_output = pdf_generator.generate_with_tiling(
                    image=processed_image,
                    output_path=output_path,
                    paper_size=effective_paper_size,
                    tile_overlap=tile_overlap,
                    add_registration_marks=True,
                    metadata=metadata,
                    braille_labels=braille_labels,
                    key_entries=key_entries if key_entries else None,
                    braille_converter=braille_converter
                )
            else:
                # Generate standard single-page PDF
                # If we have abbreviation key entries, pass them for key page generation
                final_output = pdf_generator.generate(
                    image=processed_image,
                    output_path=output_path,
                    paper_size=effective_paper_size,
                    metadata=metadata,
                    braille_labels=braille_labels,
                    symbol_key_entries=symbol_key_entries,
                    braille_converter=braille_converter,
                    key_entries=key_entries if key_entries else None
                )
        except PDFGeneratorError as e:
            return json.dumps({
                "success": False,
                "error": f"PDF generation failed: {e}",
                "error_type": "pdf_error"
            })

        # ============================================================
        # QUALITY ASSESSMENT (if requested)
        # ============================================================
        if assess_quality:
            import tempfile
            # Save processed image to temp file for comparison
            processed_temp = tempfile.NamedTemporaryFile(
                suffix='.png', delete=False, prefix='processed_'
            )
            processed_image.save(processed_temp.name, format='PNG')
            processed_image_path = processed_temp.name

            density = metadata.get('density_percentage', 0)

            # Determine image type from preset for context-aware assessment
            image_type = preset if preset else "floor_plan"

            return json.dumps({
                "success": True,
                "phase": "quality_assessment_needed",
                "output_file": str(final_output),
                "original_image": str(image_file.absolute()),
                "processed_image": processed_image_path,
                "current_params": {
                    "threshold": effective_threshold,
                    "density": round(density, 1),
                    "enhance": enhance,
                    "preset": preset,
                    "paper_size": effective_paper_size,
                    "braille_labels_count": braille_labels_count,
                    "auto_reduce_density": auto_reduce_density
                },
                "image_type": image_type,
                "instructions": (
                    "QUALITY ASSESSMENT REQUESTED\n\n"
                    "Please compare the original and processed images:\n"
                    f"1. Original: {image_file.absolute()}\n"
                    f"2. Processed: {processed_image_path}\n\n"
                    f"Current density: {density:.1f}%\n"
                    f"Image type: {image_type}\n\n"
                    f"EVALUATION CRITERIA for {image_type}:\n"
                    + _get_quality_criteria(image_type) +
                    "\n\nIf adjustments are needed, call image_to_piaf again with:\n"
                    "- threshold: increase (more white) or decrease (more black)\n"
                    "- auto_reduce_density: True if too dense\n"
                    "- preset: try different preset for different image types\n\n"
                    "Or call assess_tactile_quality() for a detailed quality report."
                ),
                "message": "PDF generated. Please review quality by comparing original and processed images."
            })

        # Build success response
        density = metadata.get('density_percentage', 0)
        density_message = _get_density_message(density)

        # Build warnings list
        warnings = []
        if effective_scale_percent is not None and effective_scale_percent > 300:
            warnings.append(f"High scaling ({effective_scale_percent:.0f}%) may degrade image quality. Recommended range: 100-300%.")

        # Build human-readable message
        message_parts = ["Converted successfully."]
        if braille_labels_count > 0:
            message_parts.append(f"{braille_labels_count} Braille label(s) added.")
        if key_entries:
            message_parts.append(f"{len(key_entries)} label(s) abbreviated with key page.")
        if zoom_applied:
            if zoom_applied.get('label'):
                message_parts.append(f"Zoomed to '{zoom_applied['label']}'.")
            else:
                message_parts.append("Zoomed to specified region.")
        if effective_scale_percent is not None and effective_scale_percent != 100:
            message_parts.append(f"Image scaled to {effective_scale_percent:.0f}%.")
        if warnings:
            message_parts.append(f"Warning: {warnings[0]}")
        message_parts.append(density_message)
        if needs_tiling:
            message_parts.append("Image was tiled across multiple pages.")
        message_parts.append("Ready for PIAF printing.")

        response = {
            "success": True,
            "output_file": str(final_output),
            "density_percentage": round(density, 1),
            "braille_labels_count": braille_labels_count,
            "key_entries_count": len(key_entries) if key_entries else 0,
            "scale_applied": effective_scale_percent if effective_scale_percent else 100,
            "auto_scale_used": auto_scale and effective_scale_percent is not None and effective_scale_percent != 100,
            "paper_size": effective_paper_size,
            "threshold_used": effective_threshold,
            "preset_used": preset,
            "needs_tiling": needs_tiling,
            "detected_text_count": len(detected_texts_to_use),
            "message": " ".join(message_parts)
        }

        # Add warnings if any
        if warnings:
            response["warnings"] = warnings
            response["recommended_scale_range"] = "100-300%"

        # Add zoom information if zoom was applied
        if zoom_applied:
            response["zoom_applied"] = zoom_applied

        return json.dumps(response)

    except Exception as e:
        logger.error(f"Unexpected error in image_to_piaf: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "unexpected_error"
        })


async def list_presets() -> str:
    """
    List all available conversion presets with their descriptions.

    Presets provide optimized settings for different types of architectural
    images. Using the right preset improves conversion quality.

    Returns:
        JSON string with list of presets and their settings
    """
    _ensure_imports()
    try:
        preset_manager = PresetManager()
        presets_list = []

        for name in preset_manager.list_presets():
            info = preset_manager.get_preset_info(name)
            settings = preset_manager.get_preset_settings(name)

            presets_list.append({
                "name": name,
                "description": info.get('description', ''),
                "threshold": settings.get('threshold', 128),
                "paper_size": settings.get('paper_size', 'letter'),
                "enhance": settings.get('enhance'),
                "notes": info.get('notes', '')
            })

        return json.dumps({
            "success": True,
            "presets": presets_list,
            "count": len(presets_list),
            "message": f"{len(presets_list)} presets available. Use preset name with image_to_piaf."
        })

    except PresetError as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to load presets: {e}",
            "error_type": "preset_error"
        })
    except Exception as e:
        logger.error(f"Unexpected error in list_presets: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "unexpected_error"
        })


async def analyze_image(image_path: str) -> str:
    """
    Analyze an image before conversion to provide recommendations.

    This tool performs a pre-flight check on an image, detecting its
    characteristics and recommending optimal conversion settings.

    Args:
        image_path: Path to the image file to analyze

    Returns:
        JSON string with image analysis and recommendations
    """
    _ensure_imports()
    try:
        silent_logger = SilentLogger()

        # Validate image path
        image_file = Path(image_path)
        if not image_file.exists():
            return json.dumps({
                "success": False,
                "error": f"Image file not found: {image_path}",
                "error_type": "file_not_found"
            })

        # Load configuration
        try:
            standards = StandardsLoader()
        except StandardsLoaderError as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to load configuration: {e}",
                "error_type": "configuration_error"
            })

        # Process image with default settings to get metadata
        processor = ImageProcessor(
            config=standards.get_all_config(),
            logger=silent_logger
        )

        try:
            # Process with default threshold to analyze
            processed_image, metadata = processor.process(
                input_path=str(image_path),
                threshold=128,
                check_density_flag=True,
                detect_text=True
            )
        except ImageProcessorError as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to analyze image: {e}",
                "error_type": "processing_error"
            })

        # Get image info
        original_size = metadata.get('original_size', (0, 0))
        density = metadata.get('density_percentage', 0)
        detected_texts = metadata.get('detected_texts', [])
        needs_tiling = metadata.get('needs_tiling', False)

        # Determine recommended preset based on characteristics
        recommendations = []
        recommended_preset = "floor_plan"  # Default

        # Analyze text content for hints
        text_content = " ".join([t.text.lower() for t in detected_texts if hasattr(t, 'text')])

        if any(word in text_content for word in ['section', 'elevation', 'height']):
            recommended_preset = "section"
            recommendations.append("Detected section/elevation indicators - using 'section' preset")
        elif any(word in text_content for word in ['site', 'north', 'scale']):
            recommended_preset = "site_plan"
            recommendations.append("Detected site plan indicators - using 'site_plan' preset")
        elif len(detected_texts) > 30:
            recommended_preset = "floor_plan"
            recommendations.append("High text density suggests floor plan - using 'floor_plan' preset")
        elif len(detected_texts) < 5:
            recommended_preset = "sketch"
            recommendations.append("Low text density suggests sketch or diagram - using 'sketch' preset")
        else:
            recommendations.append("Using default 'floor_plan' preset")

        # Density recommendations
        if density > 45:
            recommendations.append(f"Density is high ({density:.1f}%). Recommend using --auto-reduce-density")
        elif density > 40:
            recommendations.append(f"Density is moderately high ({density:.1f}%). May cause some paper swelling")
        elif density < 20:
            recommendations.append(f"Density is low ({density:.1f}%). Consider lowering threshold for more detail")
        else:
            recommendations.append(f"Density is good ({density:.1f}%) - optimal for PIAF")

        # Size recommendations
        if needs_tiling:
            recommendations.append("Image is larger than paper size. Will require tiling or use tabloid paper")

        # Paper size recommendation
        if original_size[0] > 2550 or original_size[1] > 3300:
            recommendations.append("Consider using tabloid paper (11x17\") for better detail")

        return json.dumps({
            "success": True,
            "image_path": str(image_path),
            "format": image_file.suffix.upper().replace('.', ''),
            "dimensions": {
                "width": original_size[0],
                "height": original_size[1]
            },
            "estimated_density": round(density, 1),
            "detected_text_count": len(detected_texts),
            "needs_tiling": needs_tiling,
            "recommended_preset": recommended_preset,
            "recommendations": recommendations,
            "message": f"Analysis complete. Recommended preset: {recommended_preset}. {len(recommendations)} suggestion(s)."
        })

    except Exception as e:
        logger.error(f"Unexpected error in analyze_image: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "unexpected_error"
        })


def _get_image_media_type(file_path: Path) -> str:
    """Get the media type for an image file."""
    suffix = file_path.suffix.lower()
    media_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.tif': 'image/tiff',
    }
    return media_types.get(suffix, 'image/jpeg')


async def describe_image(
    image_path: str,
    detail_level: str = "full"
) -> str:
    """
    Generate a detailed architectural description of an image for accessibility.

    Uses the Arch-Alt-Text system to create multi-sensory descriptions of
    architectural images (plans, sections, diagrams, photos, etc.) specifically
    designed for blind/low-vision architecture students.

    The description follows a structured format:
    - Title: Identifies the piece
    - Macro Layer: Medium, subject, purpose (3 sentences)
    - Meso Layer: Composition, materials, orientation, scale (4+ sentences)
    - Micro Layer: Details, textures, dimensions, analogies (8+ sentences)

    Args:
        image_path: Path to the image file to describe
        detail_level: "full" for complete description, "brief" for summary only

    Returns:
        JSON string with the structured description
    """
    _ensure_imports()
    try:
        # Validate image path
        image_file = Path(image_path)
        if not image_file.exists():
            return json.dumps({
                "success": False,
                "error": f"Image file not found: {image_path}",
                "error_type": "file_not_found"
            })

        # Check supported formats
        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif'}
        if image_file.suffix.lower() not in supported_formats:
            return json.dumps({
                "success": False,
                "error": f"Unsupported image format: {image_file.suffix}. Supported: {', '.join(supported_formats)}",
                "error_type": "format_error"
            })

        # Get image metadata
        try:
            from PIL import Image
            with Image.open(image_file) as img:
                width, height = img.size
                mode = img.mode
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to read image metadata: {e}",
                "error_type": "file_error"
            })

        # Get media type
        media_type = _get_image_media_type(image_file)

        # Return success with instructions for Claude to use its native vision
        return json.dumps({
            "success": True,
            "image_path": str(image_file.absolute()),
            "image_info": {
                "format": image_file.suffix.upper().replace('.', ''),
                "media_type": media_type,
                "width": width,
                "height": height,
                "mode": mode
            },
            "detail_level": detail_level,
            "instructions": (
                "To describe this image using the Arch-Alt-Text system:\n"
                "1. Read the prompt from resource: arch-alt-text://prompt\n"
                "2. Use your vision capability to view the image at the path above\n"
                "3. Apply the Arch-Alt-Text format (Macro/Meso/Micro) to describe it\n\n"
                f"Detail level requested: {detail_level}"
            ),
            "message": f"Image validated. Use the arch-alt-text://prompt resource and view the image to generate description."
        })

    except Exception as e:
        logger.error(f"Unexpected error in describe_image: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "unexpected_error"
        })


async def extract_text_with_vision(
    image_path: str,
    include_handwritten: bool = True,
    include_dimensions: bool = True
) -> str:
    """
    Extract text from an architectural image using Claude's vision capability.

    This tool validates the image and returns instructions for Claude to use
    its native vision capability to detect all text, including handwritten
    annotations, dimensions, and rotated text that Tesseract may miss.

    The extracted text can then be passed to image_to_piaf() via the
    extracted_text_json parameter for Braille conversion.

    Args:
        image_path: Path to the image file to extract text from
        include_handwritten: Whether to include handwritten text/annotations
        include_dimensions: Whether to identify dimension annotations (e.g., 10'-6")

    Returns:
        JSON with image info and extraction instructions for Claude's vision
    """
    _ensure_imports()
    try:
        image_file = Path(image_path)
        if not image_file.exists():
            return json.dumps({
                "success": False,
                "error": f"Image file not found: {image_path}",
                "error_type": "file_not_found"
            })

        # Validate format
        supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.tif'}
        if image_file.suffix.lower() not in supported_formats:
            return json.dumps({
                "success": False,
                "error": f"Unsupported format: {image_file.suffix}",
                "error_type": "format_error"
            })

        # Get image metadata
        try:
            from PIL import Image
            with Image.open(image_file) as img:
                width, height = img.size
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to read image: {e}",
                "error_type": "file_error"
            })

        media_type = _get_image_media_type(image_file)

        return json.dumps({
            "success": True,
            "image_path": str(image_file.absolute()),
            "image_info": {
                "format": image_file.suffix.upper().replace('.', ''),
                "media_type": media_type,
                "width": width,
                "height": height
            },
            "extraction_settings": {
                "include_handwritten": include_handwritten,
                "include_dimensions": include_dimensions
            },
            "instructions": (
                "To extract text from this image for Braille conversion:\n\n"
                "1. Use your vision capability to view the image at the path above\n"
                f"2. Image dimensions: {width}x{height} pixels\n"
                "3. Identify ALL text including:\n"
                "   - Printed text and labels (room names, titles)\n"
                f"   - {'Handwritten annotations' if include_handwritten else '(skip handwritten)'}\n"
                f"   - {'Dimensions (e.g., 10 feet-6 inches, 3.5m, 5,55 m)' if include_dimensions else '(skip dimensions)'}\n"
                "   - Rotated or angled text\n\n"
                "4. Return a JSON array with NORMALIZED COORDINATES (percentages 0-100):\n"
                "[\n"
                "  {\n"
                '    "text": "Kitchen",\n'
                '    "x_percent": 35,      // horizontal position as % from left edge\n'
                '    "y_percent": 25,      // vertical position as % from top edge\n'
                '    "width_percent": 8,   // approximate width as % of image width\n'
                '    "height_percent": 3,  // approximate height as % of image height\n'
                '    "rotation_degrees": 0,  // 0=horizontal, 90=rotated clockwise, -90=counter-clockwise\n'
                '    "type": "printed",    // "printed", "handwritten", or "dimension"\n'
                '    "confidence": "high"  // "high", "medium", or "low"\n'
                "  }\n"
                "]\n\n"
                "TIPS:\n"
                "- Use percentages NOT pixels (easier to estimate visually)\n"
                "- Center of image is approximately x_percent=50, y_percent=50\n"
                "- Top-left corner is x_percent=0, y_percent=0\n"
                "- For dimensions like '5,55 m' use type='dimension'\n"
                "- For rotated text: 90=vertical reading bottom-to-top, -90=vertical reading top-to-bottom\n\n"
                "5. Pass this JSON to image_to_piaf() via claude_text_json parameter"
            ),
            "message": "Image validated. View the image and extract text with normalized coordinates (percentages)."
        })

    except Exception as e:
        logger.error(f"Unexpected error in extract_text_with_vision: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "unexpected_error"
        })


async def assess_tactile_quality(
    original_image_path: str,
    processed_image_path: str,
    image_type: str = "floor_plan",
    current_params: Optional[Dict[str, Any]] = None
) -> str:
    """
    Assess tactile output quality by comparing original and processed images.

    This tool helps evaluate whether a tactile conversion is suitable for PIAF
    printing. It provides context-aware criteria based on the image type and
    suggests parameter adjustments if needed.

    Args:
        original_image_path: Path to the original source image
        processed_image_path: Path to the processed B&W image
        image_type: Type of architectural image (floor_plan, site_plan, section, elevation, sketch)
        current_params: Optional dict with current conversion parameters for context

    Returns:
        JSON string with quality assessment criteria and suggestions
    """
    _ensure_imports()
    try:
        from PIL import Image

        # Validate original image path
        original_file = Path(original_image_path)
        if not original_file.exists():
            return json.dumps({
                "success": False,
                "error": f"Original image not found: {original_image_path}",
                "error_type": "file_not_found"
            })

        # Validate processed image path
        processed_file = Path(processed_image_path)
        if not processed_file.exists():
            return json.dumps({
                "success": False,
                "error": f"Processed image not found: {processed_image_path}",
                "error_type": "file_not_found"
            })

        # Get image metadata
        try:
            with Image.open(original_file) as orig_img:
                orig_width, orig_height = orig_img.size
            with Image.open(processed_file) as proc_img:
                proc_width, proc_height = proc_img.size
                # Calculate density of processed image
                if proc_img.mode == '1':
                    # Binary image
                    pixels = list(proc_img.getdata())
                    black_pixels = sum(1 for p in pixels if p == 0)
                    density = (black_pixels / len(pixels)) * 100
                else:
                    # Grayscale - threshold at 128
                    pixels = list(proc_img.convert('L').getdata())
                    black_pixels = sum(1 for p in pixels if p < 128)
                    density = (black_pixels / len(pixels)) * 100
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Failed to read images: {e}",
                "error_type": "file_error"
            })

        # Get quality criteria for this image type
        criteria = _get_quality_criteria(image_type)

        # Build detailed assessment instructions
        assessment_prompt = (
            f"TACTILE QUALITY ASSESSMENT for {image_type.upper()}\n\n"
            "Please compare these two images:\n"
            f"1. ORIGINAL: {original_file.absolute()}\n"
            f"   Size: {orig_width}x{orig_height} pixels\n\n"
            f"2. PROCESSED: {processed_file.absolute()}\n"
            f"   Size: {proc_width}x{proc_height} pixels\n"
            f"   Current density: {density:.1f}%\n\n"
            "EVALUATION CRITERIA:\n"
            f"{criteria}\n\n"
            "DENSITY GUIDELINES:\n"
            "- < 25%: May be too sparse, important details could be lost\n"
            "- 25-35%: Optimal range for most images\n"
            "- 35-45%: Acceptable but may cause some paper swelling\n"
            "- > 45%: Too dense, risk of paper damage and poor tactile discrimination\n\n"
            "Please provide:\n"
            "1. Quality score (1-10)\n"
            "2. List of any issues found\n"
            "3. Specific parameter adjustments to try\n"
            "4. Brief explanation of your assessment"
        )

        return json.dumps({
            "success": True,
            "original_image": str(original_file.absolute()),
            "processed_image": str(processed_file.absolute()),
            "image_type": image_type,
            "current_density": round(density, 1),
            "current_params": current_params or {},
            "density_status": (
                "too_low" if density < 25 else
                "optimal" if density < 35 else
                "acceptable" if density < 45 else
                "too_high"
            ),
            "criteria": criteria,
            "instructions": assessment_prompt,
            "suggested_adjustments": _get_adjustment_suggestions(density, image_type),
            "message": "View both images and provide a quality assessment based on the criteria above."
        })

    except Exception as e:
        logger.error(f"Unexpected error in assess_tactile_quality: {e}")
        return json.dumps({
            "success": False,
            "error": str(e),
            "error_type": "unexpected_error"
        })


def _get_adjustment_suggestions(density: float, image_type: str) -> Dict[str, Any]:
    """Generate parameter adjustment suggestions based on density and image type."""
    suggestions = {"adjustments": []}

    if density < 25:
        suggestions["adjustments"].append({
            "parameter": "threshold",
            "action": "decrease",
            "reason": "Increase black pixels to capture more detail"
        })
    elif density > 45:
        suggestions["adjustments"].append({
            "parameter": "auto_reduce_density",
            "action": "set to True",
            "reason": "Automatically reduce density for better PIAF printing"
        })
        suggestions["adjustments"].append({
            "parameter": "threshold",
            "action": "increase",
            "reason": "Reduce black pixels to prevent paper swelling"
        })

    # Image-type specific suggestions
    if image_type == "sketch" and density > 30:
        suggestions["adjustments"].append({
            "parameter": "threshold",
            "action": "increase by 20-30",
            "reason": "Sketches typically work better with lower density"
        })
    elif image_type in ["floor_plan", "site_plan"] and density < 20:
        suggestions["adjustments"].append({
            "parameter": "threshold",
            "action": "decrease by 10-20",
            "reason": "Plans need enough density to show walls and boundaries clearly"
        })

    if not suggestions["adjustments"]:
        suggestions["adjustments"].append({
            "parameter": "none",
            "action": "current settings look good",
            "reason": "Density is in acceptable range for this image type"
        })

    return suggestions
