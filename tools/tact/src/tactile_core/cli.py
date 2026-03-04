"""
TACT — Tactile Architectural Conversion Tool

A continuation of Way & Barner's 1997 TACTICS system, updated for the AI era.
Provides accessible, screen-reader friendly commands for converting
images to tactile-ready formats for PIAF swell paper printing.
"""

import sys
import click
from pathlib import Path

from tactile_core import __version__
from tactile_core.core.processor import ImageProcessor, ImageProcessorError
from tactile_core.core.pdf_generator import PIAFPDFGenerator, PDFGeneratorError
from tactile_core.config.standards_loader import StandardsLoader, StandardsLoaderError
from tactile_core.config.presets import PresetManager, PresetError
from tactile_core.utils.logger import AccessibleLogger
from tactile_core.utils.validators import (
    validate_image_file,
    validate_threshold,
    validate_paper_size,
    generate_output_filename,
    resolve_wsl_path
)
from tactile_core.core.text_detector import TextDetector, TextDetectionConfig
from tactile_core.core.braille_converter import BrailleConverter, BrailleConfig
from tactile_core.core.label_scaler import analyze_label_fit


class DefaultGroup(click.Group):
    """Click group that defaults to 'convert' when first arg is a file path."""

    def parse_args(self, ctx, args):
        if args and args[0] not in self.commands and not args[0].startswith('-'):
            args.insert(0, 'convert')
        return super().parse_args(ctx, args)


@click.group(cls=DefaultGroup)
@click.version_option(version=__version__, prog_name="tact")
def main():
    """
    TACT — Tactile Architectural Conversion Tool

    Convert images to tactile-ready PDFs for PIAF swell paper printing.
    Designed for accessibility and full screen-reader compatibility.

    \b
    Quick usage:
        tact IMAGE.jpg --preset floor_plan --verbose

    \b
    Subcommands:
        tact presets    List available presets
        tact batch      Batch convert a folder
        tact info       Show tool information
    """
    pass


@main.command(name="convert")
@click.argument('input_path', type=click.Path(exists=True))
@click.option(
    '--output', '-o',
    type=click.Path(),
    help='Output PDF file path (auto-generated if not specified)'
)
@click.option(
    '--threshold', '-t',
    type=int,
    default=None,
    help='Black/white threshold 0-255 (default: 128). Higher values produce more black.'
)
@click.option(
    '--paper-size', '-p',
    type=click.Choice(['letter', 'tabloid'], case_sensitive=False),
    default='letter',
    help='Paper size for output (default: letter)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed progress messages'
)
@click.option(
    '--interactive', '-i',
    is_flag=True,
    help='Interactive mode with step-by-step prompts'
)
@click.option(
    '--config',
    type=click.Path(exists=True),
    help='Path to custom tactile_standards.yaml configuration'
)
@click.option(
    '--preset',
    type=str,
    default=None,
    help='Use a preset configuration (floor_plan, sketch, photograph, etc.). Use "tact presets" to see all.'
)
@click.option(
    '--enhance', '-e',
    type=click.Choice(['s_curve', 'auto_contrast', 'clahe', 'histogram'], case_sensitive=False),
    default=None,
    help='Apply contrast enhancement before thresholding (s_curve recommended, overrides preset)'
)
@click.option(
    '--enhance-strength',
    type=float,
    default=None,
    help='Enhancement strength for S-curve (0.0-2.0, default 1.0, only applies to s_curve, overrides preset)'
)
@click.option(
    '--save-intermediate',
    type=click.Path(),
    default=None,
    help='Save intermediate enhanced grayscale image before thresholding (e.g., enhanced.png). Useful for tuning enhancement parameters.'
)
@click.option(
    '--enable-tiling',
    is_flag=True,
    help='Enable automatic tiling for images larger than paper size'
)
@click.option(
    '--tile-overlap',
    type=float,
    default=0.0,
    help='Overlap percentage between tiles (0.0-1.0, default 0.0 for no overlap)'
)
@click.option(
    '--no-registration-marks',
    is_flag=True,
    help='Disable registration marks on tiles'
)
@click.option(
    '--auto-reduce-density',
    is_flag=True,
    help='Automatically reduce density if too high (default: off, preserves warning behavior)'
)
@click.option(
    '--target-density',
    type=float,
    default=None,
    help='Target density percentage (0.0-1.0, default: 0.30 for 30 percent)'
)
@click.option(
    '--max-reduction-iterations',
    type=int,
    default=None,
    help='Maximum erosion iterations for density reduction (default: 10)'
)
@click.option(
    '--detect-text',
    is_flag=True,
    help='Detect text and dimensions using OCR'
)
@click.option(
    '--braille-grade',
    type=click.Choice(['1', '2'], case_sensitive=False),
    default='1',
    help='Braille grade: 1 (uncontracted) or 2 (contracted). Default: 1'
)
@click.option(
    '--braille-placement',
    type=click.Choice(['overlay', 'margin'], case_sensitive=False),
    default='overlay',
    help='Braille label placement: overlay on image or in margins. Default: overlay'
)
@click.option(
    '--zoom-region',
    type=str,
    default=None,
    help='Zoom to a region: "x%%,y%%,w%%,h%%" (e.g., "25,30,50,40" = start at 25%%,30%% with 50%%x40%% size). Includes 10%% margin.'
)
@click.option(
    '--scale-percent',
    type=float,
    default=None,
    help='Manual zoom/scale percentage (100=no change, 150=1.5x, 200=2x). Overrides auto-scale when specified.'
)
@click.option(
    '--auto-scale/--no-auto-scale',
    default=True,
    help='Automatically scale image so Braille labels fit in original text bounding boxes (default: enabled)'
)
@click.option(
    '--max-scale-factor',
    type=float,
    default=None,
    help='Cap on auto-scale factor (e.g., 2.0 = 200%% max). Labels that do not fit after capped scaling get abbreviated.'
)
@click.option(
    '--abbreviation-key/--no-abbreviation-key',
    default=True,
    help='Auto-abbreviate labels that do not fit in their bounding box to single letters and generate a key page (default: enabled)'
)
@click.option(
    '--force-abbreviation-key',
    is_flag=True,
    help='Abbreviate ALL labels regardless of whether they fit, creating a comprehensive key page'
)
@click.option(
    '--sticker-workflow',
    is_flag=True,
    help='Generate dual PDFs for Braille sticker workflow: PIAF version (counter-highlighted, no Braille) + text-only version for second print pass'
)
def convert(input_path, output, threshold, paper_size, verbose, interactive, config, preset, enhance, enhance_strength, save_intermediate, enable_tiling, tile_overlap, no_registration_marks, auto_reduce_density, target_density, max_reduction_iterations, detect_text, braille_grade, braille_placement, zoom_region, scale_percent, auto_scale, max_scale_factor, abbreviation_key, force_abbreviation_key, sticker_workflow):
    """
    Convert an image to PIAF-ready PDF format.

    INPUT_PATH: Path to the image file to convert

    \b
    Examples:
        tact floor-plan.jpg --preset floor_plan --verbose
        tact sketch.png --threshold 140 --output result.pdf
        tact photo.jpg --preset photograph --detect-text --braille-grade 2

    Strong enhancement for faint images:
        tact faint-sketch.jpg --enhance s_curve --enhance-strength 1.5

    Interactive mode with detailed output:
        tact drawing.jpg --interactive --verbose

    Automatic density reduction (fixes high density issues):
        tact dense-image.jpg --auto-reduce-density --verbose

    Custom density reduction target:
        tact floor-plan.jpg --auto-reduce-density --target-density 0.25

    Density reduction with more iterations:
        tact complex-drawing.png --auto-reduce-density --max-reduction-iterations 15

    Enable tiling for large images:
        tact large-plan.jpg --enable-tiling --verbose

    Tiling with custom overlap:
        tact huge-drawing.png --enable-tiling --tile-overlap 0.15

    Tiling without registration marks:
        tact large-map.tif --enable-tiling --no-registration-marks

    Manual scaling (zoom in 150%):
        tact floor-plan.jpg --scale-percent 150 --detect-text

    Auto-scale with cap (max 200%):
        tact floor-plan.jpg --detect-text --max-scale-factor 2.0

    Disable auto-scaling:
        tact floor-plan.jpg --detect-text --no-auto-scale

    Force abbreviation key for all labels:
        tact dense-plan.jpg --detect-text --force-abbreviation-key

    Disable abbreviation key:
        tact floor-plan.jpg --detect-text --no-abbreviation-key

    Supported formats: JPG, PNG, TIFF, BMP, GIF, PDF

    Use 'tact presets' to see all available presets.
    """
    # Initialize logger
    logger = AccessibleLogger(verbose=verbose or interactive)

    # Sticker workflow requires text detection
    if sticker_workflow and not detect_text:
        detect_text = True
        if verbose:
            logger.info("Sticker workflow enabled: forcing text detection")

    try:
        # Display welcome message for interactive mode
        if interactive:
            logger.info("=" * 60)
            logger.info("TACT — Tactile Architectural Conversion Tool")
            logger.info("=" * 60)
            logger.blank_line()

        # Load configuration
        try:
            standards = StandardsLoader(config_path=config)
            if verbose:
                logger.info("Configuration loaded successfully")
        except StandardsLoaderError as e:
            logger.error("Failed to load configuration", e)
            logger.solution("Check that tactile_standards.yaml exists and is valid")
            sys.exit(1)

        # Load presets
        try:
            preset_manager = PresetManager()
        except PresetError as e:
            logger.error("Failed to load presets", e)
            logger.solution("Check that presets.yaml exists and is valid")
            sys.exit(1)

        # Apply preset settings if specified
        if preset:
            try:
                preset_settings = preset_manager.get_preset_settings(preset)
                preset_info = preset_manager.get_preset_info(preset)

                if verbose:
                    logger.info(f"Using preset: {preset_info['name']}")
                    logger.info(f"  {preset_info['description']}")

                # Apply preset settings (CLI options override preset)
                if threshold is None:
                    threshold = preset_settings.get('threshold', standards.get_default_threshold())
                if paper_size == 'letter':  # Only override if still default
                    paper_size = preset_settings.get('paper_size', 'letter')
                if enhance is None:
                    enhance = preset_settings.get('enhance')
                if enhance_strength is None:
                    enhance_strength = preset_settings.get('enhance_strength', 1.0)

            except PresetError as e:
                logger.error("Invalid preset", e)
                logger.solution("Use 'tact presets' to see available presets")
                sys.exit(1)

        # Get default threshold from config if still not specified
        if threshold is None:
            threshold = standards.get_default_threshold()

        # Set default enhance_strength if not set
        if enhance_strength is None:
            enhance_strength = 1.0

        # Validate threshold
        is_valid, error_msg = validate_threshold(threshold)
        if not is_valid:
            logger.error(error_msg)
            logger.solution("Use a threshold value between 0 and 255")
            sys.exit(1)

        # Validate paper size
        is_valid, error_msg = validate_paper_size(paper_size)
        if not is_valid:
            logger.error(error_msg)
            sys.exit(1)

        # Display input file
        logger.info(f"Input file: {Path(input_path).name}")

        # Validate tiling options
        if tile_overlap < 0.0 or tile_overlap > 1.0:
            logger.error("Invalid tile overlap value")
            logger.solution("Use a value between 0.0 and 1.0 (e.g., 0.1 for 10% overlap)")
            sys.exit(1)

        # Validate density reduction options
        if target_density is not None and (target_density < 0.0 or target_density > 1.0):
            logger.error("Invalid target density value")
            logger.solution("Use a value between 0.0 and 1.0 (e.g., 0.30 for 30% density)")
            sys.exit(1)

        if max_reduction_iterations is not None and max_reduction_iterations < 1:
            logger.error("Invalid max reduction iterations value")
            logger.solution("Use a positive integer (e.g., 10)")
            sys.exit(1)

        # Interactive confirmation
        if interactive:
            logger.blank_line()
            logger.info(f"Settings:")
            logger.info(f"  Threshold: {threshold}")
            logger.info(f"  Paper size: {paper_size}")
            if enhance:
                logger.info(f"  Enhancement: {enhance}")
                if enhance == 's_curve':
                    logger.info(f"  Enhancement strength: {enhance_strength}")
            if enable_tiling:
                logger.info(f"  Tiling: enabled")
                logger.info(f"  Tile overlap: {int(tile_overlap * 100)}%")
                logger.info(f"  Registration marks: {'disabled' if no_registration_marks else 'enabled'}")
            if auto_reduce_density:
                logger.info(f"  Automatic density reduction: enabled")
                if target_density is not None:
                    logger.info(f"  Target density: {int(target_density * 100)}%")
                if max_reduction_iterations is not None:
                    logger.info(f"  Max iterations: {max_reduction_iterations}")
            if zoom_region:
                logger.info(f"  Zoom region: {zoom_region}")
            if scale_percent:
                logger.info(f"  Manual scale: {scale_percent}%")
            if auto_scale:
                if max_scale_factor:
                    logger.info(f"  Auto-scale: enabled (max {max_scale_factor * 100:.0f}%)")
                else:
                    logger.info(f"  Auto-scale: enabled (no cap)")
            else:
                logger.info(f"  Auto-scale: disabled")
            if abbreviation_key:
                if force_abbreviation_key:
                    logger.info(f"  Abbreviation key: force all labels")
                else:
                    logger.info(f"  Abbreviation key: enabled")
            else:
                logger.info(f"  Abbreviation key: disabled")
            logger.blank_line()

            if not click.confirm("Continue with these settings?", default=True):
                logger.info("Operation cancelled")
                sys.exit(0)

            logger.blank_line()

        # Generate output filename if not specified
        if not output:
            output = generate_output_filename(input_path)

        # Resolve to full absolute path for clarity
        output = resolve_wsl_path(output)
        if verbose:
            logger.info(f"Output will be saved to: {output}")

        # Process image
        processor = ImageProcessor(
            config=standards.get_all_config(),
            logger=logger
        )

        # Parse and apply zoom region if specified
        zoom_region_tuple = None
        zoomed_input_path = input_path
        if zoom_region:
            try:
                parts = [float(p.strip()) for p in zoom_region.split(',')]
                if len(parts) != 4:
                    raise ValueError("Expected 4 values")
                zoom_region_tuple = tuple(parts)

                # Validate percentages
                if not all(0 <= p <= 100 for p in zoom_region_tuple):
                    logger.error("Zoom region values must be between 0 and 100")
                    sys.exit(1)

                # Load and crop the image
                from PIL import Image as PILImage
                import tempfile

                with PILImage.open(input_path) as img:
                    cropped = processor.crop_to_region(img, zoom_region_tuple, margin_percent=10.0)
                    cropped = processor.adjust_to_aspect_ratio(cropped, paper_size)
                    # Scale up to fill the page
                    cropped = processor.scale_to_fill_page(cropped, paper_size, dpi=300)

                    # Save to temp file
                    zoom_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='zoom_')
                    cropped.save(zoom_temp.name, format='PNG')
                    zoomed_input_path = zoom_temp.name

                if verbose:
                    logger.info(f"Zoomed to region: {zoom_region}")

            except ValueError as e:
                logger.error(f"Invalid zoom-region format: {e}")
                logger.solution("Use format: x%,y%,width%,height% (e.g., 25,30,50,40)")
                sys.exit(1)

        # Detect text with EasyOCR on original image (before thresholding)
        easyocr_texts = []
        if detect_text:
            try:
                from PIL import Image as PILImage
                from tactile_core.core.easyocr_detector import EasyOCRDetector
                detector = EasyOCRDetector()
                with PILImage.open(zoomed_input_path) as orig_img:
                    easyocr_texts = detector.detect_text(orig_img)
                if verbose:
                    logger.info(f"EasyOCR detected {len(easyocr_texts)} text regions")
            except Exception as e:
                logger.warning(f"EasyOCR text detection failed: {e}")
                logger.info("Continuing without text detection")

        try:
            processed_image, metadata = processor.process(
                input_path=zoomed_input_path,
                threshold=threshold,
                check_density_flag=True,
                enhance=enhance,
                enhance_strength=enhance_strength,
                paper_size=paper_size,
                auto_reduce_density=auto_reduce_density,
                target_density=target_density,
                max_reduction_iterations=max_reduction_iterations,
                detect_text=False,
                save_intermediate_path=save_intermediate
            )
        except ImageProcessorError as e:
            logger.error("Image processing failed", e)
            logger.solution("Check that the input file is a valid image")
            sys.exit(1)

        # Inject EasyOCR results into metadata
        if detect_text and easyocr_texts:
            metadata['detected_texts'] = easyocr_texts

        logger.blank_line()

        # Get image dimensions for scaling analysis
        img_width, img_height = processed_image.size
        detected_texts = metadata.get('detected_texts', [])
        effective_scale_percent = None
        key_entries = []

        # Manual scaling (works independently of text detection)
        if scale_percent is not None and scale_percent != 100:
            try:
                from PIL import Image as PILImage
                import tempfile

                # Load original and scale before processing
                with PILImage.open(zoomed_input_path) as base_image:
                    scaled_image = processor.scale_image(base_image, scale_percent)
                    img_width, img_height = scaled_image.size

                    # Save scaled image to temp file
                    scaled_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='scaled_')
                    scaled_image.save(scaled_temp.name, format='PNG')
                    scaled_path = scaled_temp.name

                effective_scale_percent = scale_percent
                logger.info(f"Manual scaling applied: {scale_percent:.0f}%")

                # Detect text on scaled image with EasyOCR
                if detect_text:
                    try:
                        from tactile_core.core.easyocr_detector import EasyOCRDetector
                        detector = EasyOCRDetector()
                        with PILImage.open(scaled_path) as scaled_img:
                            easyocr_texts = detector.detect_text(scaled_img)
                    except Exception as e:
                        if verbose:
                            logger.warning(f"EasyOCR on scaled image failed: {e}")

                # Re-process the scaled image
                processed_image, metadata = processor.process(
                    input_path=scaled_path,
                    threshold=threshold,
                    check_density_flag=True,
                    enhance=enhance,
                    enhance_strength=enhance_strength,
                    paper_size=paper_size,
                    auto_reduce_density=auto_reduce_density,
                    target_density=target_density,
                    max_reduction_iterations=max_reduction_iterations,
                    detect_text=False
                )

                # Inject EasyOCR results
                if detect_text and easyocr_texts:
                    metadata['detected_texts'] = easyocr_texts

                # Update detected texts with new detection
                detected_texts = metadata.get('detected_texts', [])
                logger.info(f"Scaled image to {scale_percent:.0f}% ({img_width}x{img_height} pixels)")

                # Warn if scaling is very high
                if scale_percent > 300:
                    logger.warning(f"High scaling ({scale_percent:.0f}%) may degrade image quality")

            except Exception as e:
                if verbose:
                    logger.warning(f"Manual scaling failed: {e}")

        # Auto-scaling analysis (requires text detection for bounding box analysis)
        elif detect_text and detected_texts and auto_scale:
            try:
                fit_analysis = analyze_label_fit(
                    detected_texts,
                    (img_width, img_height),
                    braille_grade=int(braille_grade)
                )

                recommended_scale = fit_analysis.get('recommended_scale', 100)
                labels_needing_key = len(fit_analysis.get('needs_key', []))

                if verbose:
                    logger.info(f"Label fit analysis: {len(fit_analysis.get('fits', []))} fit, {labels_needing_key} need key")
                    logger.info(f"Recommended scale: {recommended_scale:.0f}%")

                # Apply auto-scaling if recommended > 100
                if recommended_scale > 100:
                    if max_scale_factor is not None:
                        max_scale = max_scale_factor * 100
                        effective_scale_percent = min(recommended_scale, max_scale)
                        if verbose:
                            logger.info(f"Auto-scaling to {effective_scale_percent:.0f}% (capped at {max_scale:.0f}%)")
                    else:
                        effective_scale_percent = recommended_scale
                        if verbose:
                            logger.info(f"Auto-scaling to {effective_scale_percent:.0f}% (no cap)")

                    # Apply scaling
                    from PIL import Image as PILImage
                    import tempfile

                    with PILImage.open(zoomed_input_path) as base_image:
                        scaled_image = processor.scale_image(base_image, effective_scale_percent)
                        img_width, img_height = scaled_image.size

                        scaled_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='scaled_')
                        scaled_image.save(scaled_temp.name, format='PNG')
                        scaled_path = scaled_temp.name

                    # Detect text on scaled image with EasyOCR
                    if detect_text:
                        try:
                            from tactile_core.core.easyocr_detector import EasyOCRDetector
                            detector = EasyOCRDetector()
                            with PILImage.open(scaled_path) as scaled_img:
                                easyocr_texts = detector.detect_text(scaled_img)
                        except Exception as e:
                            if verbose:
                                logger.warning(f"EasyOCR on scaled image failed: {e}")

                    # Re-process the scaled image
                    processed_image, metadata = processor.process(
                        input_path=scaled_path,
                        threshold=threshold,
                        check_density_flag=True,
                        enhance=enhance,
                        enhance_strength=enhance_strength,
                        paper_size=paper_size,
                        auto_reduce_density=auto_reduce_density,
                        target_density=target_density,
                        max_reduction_iterations=max_reduction_iterations,
                        detect_text=False
                    )

                    # Inject EasyOCR results
                    if detect_text and easyocr_texts:
                        metadata['detected_texts'] = easyocr_texts

                    # Update detected texts with new detection
                    detected_texts = metadata.get('detected_texts', [])
                    logger.info(f"Scaled image to {effective_scale_percent:.0f}% ({img_width}x{img_height} pixels)")

                    # Warn if scaling is very high
                    if effective_scale_percent > 300:
                        logger.warning(f"High scaling ({effective_scale_percent:.0f}%) may degrade image quality")

            except Exception as e:
                if verbose:
                    logger.warning(f"Label fit analysis failed: {e}")

        # Convert detected text to Braille labels if text detection was enabled
        braille_labels = None
        symbol_key_entries = None
        braille_converter = None
        if detect_text and detected_texts:
            try:
                # Get braille config from standards
                braille_config_dict = standards.get_all_config().get('braille', {})

                # Create Braille config with CLI overrides
                braille_config = BrailleConfig(
                    enabled=True,
                    grade=int(braille_grade),
                    placement=braille_placement,
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

                # Convert to Braille with abbreviation key support
                braille_converter = BrailleConverter(braille_config, logger)

                if abbreviation_key or force_abbreviation_key:
                    # Use abbreviation key mode
                    detected_text_widths = {text.text: text.width for text in detected_texts}
                    braille_labels, key_entries = braille_converter.create_braille_labels(
                        detected_texts,
                        generate_key=True,
                        detected_text_widths=detected_text_widths if not force_abbreviation_key else None
                    )

                    if force_abbreviation_key and verbose:
                        logger.info(f"Force abbreviation: all {len(key_entries)} labels abbreviated")
                    elif key_entries and verbose:
                        logger.info(f"Abbreviation key: {len(key_entries)} labels abbreviated (did not fit)")
                else:
                    # Standard mode without abbreviation key
                    braille_labels, symbol_key_entries = braille_converter.create_braille_labels(
                        detected_texts
                    )

                if braille_labels:
                    logger.info(f"Generated {len(braille_labels)} Braille label(s)")
                if symbol_key_entries:
                    logger.info(f"Created {len(symbol_key_entries)} symbol key entries for key page")
                if key_entries:
                    logger.info(f"Created abbreviation key with {len(key_entries)} entries")

                # White out original text regions using exact OCR bounding boxes
                # This removes text so Braille can sit on clean white space
                whiteout_enabled = braille_config_dict.get('whiteout_original_text', True)
                whiteout_padding = braille_config_dict.get('whiteout_padding', 5)

                if whiteout_enabled and detected_texts:
                    processed_image = processor.whiteout_text_regions(
                        processed_image,
                        detected_texts,
                        padding=whiteout_padding
                    )

            except Exception as e:
                logger.warning(f"Braille conversion failed: {e}")
                logger.info("Continuing with PDF generation without Braille labels")
                braille_labels = None
                symbol_key_entries = None
                braille_converter = None
                key_entries = []

        # Check if tiling is needed and enabled
        needs_tiling = metadata.get('needs_tiling', False)

        if needs_tiling and not enable_tiling:
            logger.warning("Image is too large for specified paper size")
            logger.info("Use --enable-tiling to split image into multiple pages")
            logger.info("Or use --paper-size tabloid for larger paper")
            logger.blank_line()

            if interactive:
                if click.confirm("Enable tiling automatically?", default=True):
                    enable_tiling = True
                else:
                    logger.info("Proceeding with scaled output")
                logger.blank_line()

        # Generate PDF
        pdf_generator = PIAFPDFGenerator(logger=logger, config=standards.get_all_config())

        try:
            if sticker_workflow:
                # Sticker workflow: Generate dual PDFs for Braille sticker alignment
                logger.blank_line()
                logger.info("Sticker workflow: Generating dual PDFs")
                logger.blank_line()

                if not detected_texts:
                    logger.error("Sticker workflow requires text detection, but no text was detected")
                    logger.solution("Ensure the image contains readable text or use a different image")
                    sys.exit(1)

                # Generate output filenames
                output_base = output.rsplit('.pdf', 1)[0] if output.endswith('.pdf') else output
                piaf_output = f"{output_base}_piaf.pdf"
                text_output = f"{output_base}_text.pdf"

                # 1. Generate PIAF PDF (counter-highlighted, no Braille, with registration mark)
                logger.info("Generating PIAF PDF (for swelling)...")
                piaf_path = pdf_generator.generate(
                    image=processed_image,
                    output_path=piaf_output,
                    paper_size=paper_size,
                    metadata=metadata,
                    braille_labels=None,  # No Braille for sticker workflow
                    symbol_key_entries=None,
                    braille_converter=None,
                    key_entries=None,
                    sticker_workflow=True,
                    page_number=1
                )

                # 2. Generate text-only PDF (for second print pass)
                logger.info("Generating text-only PDF (for second print pass)...")
                text_path = pdf_generator.generate_text_only_pdf(
                    detected_texts=detected_texts,
                    output_path=text_output,
                    paper_size=paper_size,
                    page_number=1,
                    image_size=processed_image.size
                )

                # Set output_path for summary display
                output_path = piaf_output

                logger.blank_line()
                logger.success("Sticker workflow PDFs generated:")
                logger.info(f"  PIAF version (swell this): {piaf_path}")
                logger.info(f"  Text version (print second): {text_path}")
                logger.blank_line()
                logger.info("Workflow:")
                logger.info("  1. Print PIAF PDF and swell on PIAF machine")
                logger.info("  2. Reload swelled paper (align bottom-right registration mark)")
                logger.info("  3. Print text PDF on same paper")
                logger.info("  4. Apply Braille stickers over printed text")

            elif enable_tiling and needs_tiling:
                # Generate tiled PDF
                logger.blank_line()
                logger.info("Generating tiled output for oversized image")
                logger.blank_line()

                output_path = pdf_generator.generate_with_tiling(
                    image=processed_image,
                    output_path=output,
                    paper_size=paper_size,
                    tile_overlap=tile_overlap,
                    add_registration_marks=not no_registration_marks,
                    metadata=metadata,
                    braille_labels=braille_labels,
                    key_entries=key_entries if key_entries else None,
                    braille_converter=braille_converter
                )
            else:
                # Generate standard single-page PDF
                output_path = pdf_generator.generate(
                    image=processed_image,
                    output_path=output,
                    paper_size=paper_size,
                    metadata=metadata,
                    braille_labels=braille_labels,
                    symbol_key_entries=symbol_key_entries,
                    braille_converter=braille_converter,
                    key_entries=key_entries if key_entries else None
                )

            # Display final summary
            if verbose or interactive:
                logger.blank_line()
                logger.info("=" * 60)
                logger.info("Processing Summary:")
                logger.info(f"  Input: {Path(input_path).name}")
                logger.info(f"  Output: {output_path}")
                logger.info(f"  Threshold: {threshold}")
                logger.info(f"  Paper size: {paper_size}")
                if metadata.get('density_percentage'):
                    logger.info(f"  Density: {metadata['density_percentage']:.1f}%")
                if effective_scale_percent and effective_scale_percent != 100:
                    logger.info(f"  Scale applied: {effective_scale_percent:.0f}%")
                if braille_labels:
                    logger.info(f"  Braille labels: {len(braille_labels)}")
                if key_entries:
                    logger.info(f"  Abbreviation key entries: {len(key_entries)}")
                logger.info("=" * 60)

        except PDFGeneratorError as e:
            logger.error("PDF generation failed", e)
            logger.solution("Check that the output path is writable")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.blank_line()
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Unexpected error occurred", e)
        sys.exit(1)


@main.command(name="version")
def version():
    """Display version information."""
    click.echo(f"TACT — Tactile Architectural Conversion Tool v{__version__}")
    click.echo("Convert images to tactile-ready formats for PIAF swell paper printing")


@main.command(name="info")
def info():
    """Display toolkit information and supported formats."""
    logger = AccessibleLogger(verbose=True)

    logger.info("=" * 60)
    logger.info("TACT — Tactile Architectural Conversion Tool")
    logger.info(f"Version: {__version__}")
    logger.info("=" * 60)
    logger.blank_line()

    logger.info("Purpose:")
    logger.info("  Convert images to high-contrast, tactile-ready PDFs")
    logger.info("  Optimized for PIAF (Picture In A Flash) swell paper printing")
    logger.blank_line()

    logger.info("Lineage:")
    logger.info("  Continuation of Way & Barner's 1997 TACTICS system,")
    logger.info("  updated for the AI era")
    logger.blank_line()

    logger.info("Supported Input Formats:")
    logger.info("  JPG, JPEG, PNG, TIFF, TIF, BMP, GIF, PDF")
    logger.blank_line()

    logger.info("Output Format:")
    logger.info("  PDF - 300 DPI, pure black and white")
    logger.blank_line()

    logger.info("Paper Sizes:")
    logger.info("  letter  - 8.5 x 11 inches")
    logger.info("  tabloid - 11 x 17 inches")
    logger.blank_line()

    logger.info("Accessibility Features:")
    logger.info("  - Full screen reader compatibility")
    logger.info("  - Clear, descriptive status messages")
    logger.info("  - Interactive mode with step-by-step guidance")
    logger.info("  - Verbose mode for detailed progress")
    logger.blank_line()

    logger.info("For help with commands, use: tact --help")
    logger.info("=" * 60)


@main.command(name="presets")
def list_presets():
    """List all available conversion presets."""
    logger = AccessibleLogger(verbose=True)

    try:
        preset_manager = PresetManager()
        presets_info = preset_manager.get_all_presets_info()

        logger.info("=" * 60)
        logger.info("Available Conversion Presets")
        logger.info("=" * 60)
        logger.blank_line()

        for name in preset_manager.list_presets():
            info = presets_info[name]
            logger.info(f"{name}")
            logger.info(f"  {info['description']}")
            logger.blank_line()

        logger.info("=" * 60)
        logger.info("Usage:")
        logger.info("  tact IMAGE.jpg --preset PRESET_NAME")
        logger.blank_line()
        logger.info("Example:")
        logger.info("  tact floor-plan.jpg --preset floor_plan")
        logger.info("=" * 60)

    except PresetError as e:
        logger.error("Failed to load presets", e)
        sys.exit(1)


@main.command(name="batch")
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('output_dir', type=click.Path(file_okay=False, dir_okay=True))
@click.option(
    '--pattern',
    type=str,
    default='*.jpg,*.jpeg,*.png,*.tiff,*.tif',
    help='File patterns to process (comma-separated, default: *.jpg,*.jpeg,*.png,*.tiff,*.tif)'
)
@click.option(
    '--preset',
    type=str,
    default=None,
    help='Apply preset to all images'
)
@click.option(
    '--threshold', '-t',
    type=int,
    default=None,
    help='Black/white threshold for all images (overrides preset)'
)
@click.option(
    '--enhance', '-e',
    type=click.Choice(['s_curve', 'auto_contrast', 'clahe', 'histogram'], case_sensitive=False),
    default=None,
    help='Enhancement method for all images (overrides preset)'
)
@click.option(
    '--paper-size', '-p',
    type=click.Choice(['letter', 'tabloid'], case_sensitive=False),
    default='letter',
    help='Paper size for all outputs'
)
@click.option(
    '--recursive', '-r',
    is_flag=True,
    help='Process subdirectories recursively'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Show detailed progress for each file'
)
@click.option(
    '--auto-reduce-density',
    is_flag=True,
    help='Automatically reduce density for all images if too high'
)
@click.option(
    '--target-density',
    type=float,
    default=None,
    help='Target density percentage for all images (0.0-1.0, default: 0.30)'
)
@click.option(
    '--max-reduction-iterations',
    type=int,
    default=None,
    help='Maximum erosion iterations for density reduction (default: 10)'
)
@click.option(
    '--detect-text',
    is_flag=True,
    help='Detect text and dimensions using OCR for all images'
)
@click.option(
    '--braille-grade',
    type=click.Choice(['1', '2'], case_sensitive=False),
    default='1',
    help='Braille grade: 1 (uncontracted) or 2 (contracted). Default: 1'
)
@click.option(
    '--braille-placement',
    type=click.Choice(['overlay', 'margin'], case_sensitive=False),
    default='overlay',
    help='Braille label placement: overlay on image or in margins. Default: overlay'
)
@click.option(
    '--scale-percent',
    type=float,
    default=None,
    help='Manual zoom/scale percentage for all images (100=no change, 150=1.5x, 200=2x)'
)
@click.option(
    '--auto-scale/--no-auto-scale',
    default=True,
    help='Automatically scale images so Braille labels fit (default: enabled)'
)
@click.option(
    '--max-scale-factor',
    type=float,
    default=None,
    help='Cap on auto-scale factor (e.g., 2.0 = 200%% max)'
)
@click.option(
    '--abbreviation-key/--no-abbreviation-key',
    default=True,
    help='Auto-abbreviate labels that do not fit (default: enabled)'
)
@click.option(
    '--force-abbreviation-key',
    is_flag=True,
    help='Abbreviate ALL labels for all images'
)
def batch(input_dir, output_dir, pattern, preset, threshold, enhance, paper_size, recursive, verbose, auto_reduce_density, target_density, max_reduction_iterations, detect_text, braille_grade, braille_placement, scale_percent, auto_scale, max_scale_factor, abbreviation_key, force_abbreviation_key):
    """
    Batch convert multiple images to PIAF-ready PDFs.

    INPUT_DIR: Directory containing images to convert
    OUTPUT_DIR: Directory for output PDFs

    Examples:

    Convert all JPGs in a folder with floor_plan preset:
        tact batch ./drawings ./output --preset floor_plan

    Convert all images recursively:
        tact batch ./all-drawings ./output --recursive --preset floor_plan

    Custom settings for all files:
        tact batch ./sketches ./output --threshold 130 --enhance s_curve

    Process only PNG files:
        tact batch ./images ./output --pattern "*.png" --preset photograph

    Batch with automatic density reduction:
        tact batch ./drawings ./output --auto-reduce-density --verbose
    """
    import glob as glob_module
    from pathlib import Path as PathLib

    logger = AccessibleLogger(verbose=True)  # Always verbose for batch

    try:
        input_path = PathLib(input_dir)
        output_path = PathLib(output_dir)

        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 60)
        logger.info("Batch Processing")
        logger.info("=" * 60)
        logger.blank_line()

        # Load presets if needed
        preset_manager = None
        if preset:
            try:
                preset_manager = PresetManager()
                preset_info = preset_manager.get_preset_info(preset)
                logger.info(f"Using preset: {preset_info['name']}")
                logger.info(f"  {preset_info['description']}")
            except PresetError as e:
                logger.error("Invalid preset", e)
                sys.exit(1)

        # Find all matching files
        patterns = [p.strip() for p in pattern.split(',')]
        files = []

        for pat in patterns:
            if recursive:
                files.extend(input_path.rglob(pat))
            else:
                files.extend(input_path.glob(pat))

        # Filter to only image files
        image_files = [f for f in files if f.is_file()]

        if not image_files:
            logger.warning(f"No image files found matching pattern: {pattern}")
            logger.info(f"  Input directory: {input_dir}")
            if recursive:
                logger.info("  Recursive search: enabled")
            sys.exit(0)

        logger.info(f"Found {len(image_files)} image(s) to process")
        logger.info(f"Input directory: {input_dir}")
        logger.info(f"Output directory: {output_dir}")
        logger.blank_line()

        # Process each file
        successful = 0
        failed = 0
        failed_files = []

        for idx, input_file in enumerate(image_files, 1):
            logger.info(f"[{idx}/{len(image_files)}] Processing: {input_file.name}")

            try:
                # Generate output filename
                output_file = output_path / f"{input_file.stem}_piaf.pdf"

                # Determine settings (preset -> defaults)
                file_threshold = threshold
                file_enhance = enhance
                file_enhance_strength = 1.0
                file_paper_size = paper_size

                if preset and preset_manager:
                    preset_settings = preset_manager.get_preset_settings(preset)
                    if file_threshold is None:
                        file_threshold = preset_settings.get('threshold', 128)
                    if file_enhance is None:
                        file_enhance = preset_settings.get('enhance')
                    file_enhance_strength = preset_settings.get('enhance_strength', 1.0)
                    if paper_size == 'letter':
                        file_paper_size = preset_settings.get('paper_size', 'letter')

                if file_threshold is None:
                    file_threshold = 128

                # Process image
                standards = StandardsLoader()
                processor = ImageProcessor(
                    config=standards.get_all_config(),
                    logger=AccessibleLogger(verbose=verbose)
                )

                # Detect text with EasyOCR on original image
                easyocr_texts = []
                if detect_text:
                    try:
                        from PIL import Image as PILImage
                        from tactile_core.core.easyocr_detector import EasyOCRDetector
                        detector = EasyOCRDetector()
                        with PILImage.open(str(input_file)) as orig_img:
                            easyocr_texts = detector.detect_text(orig_img)
                    except Exception:
                        pass  # Silently skip EasyOCR errors in batch mode

                processed_image, metadata = processor.process(
                    input_path=str(input_file),
                    threshold=file_threshold,
                    check_density_flag=True,
                    enhance=file_enhance,
                    enhance_strength=file_enhance_strength,
                    paper_size=file_paper_size,
                    auto_reduce_density=auto_reduce_density,
                    target_density=target_density,
                    max_reduction_iterations=max_reduction_iterations,
                    detect_text=False
                )

                # Inject EasyOCR results
                if detect_text and easyocr_texts:
                    metadata['detected_texts'] = easyocr_texts

                # Get detected texts and apply scaling if needed
                detected_texts = metadata.get('detected_texts', [])
                key_entries = []
                effective_scale = None

                # Auto-scaling analysis
                if detect_text and detected_texts and (auto_scale or scale_percent is not None):
                    try:
                        img_width, img_height = processed_image.size
                        fit_analysis = analyze_label_fit(
                            detected_texts,
                            (img_width, img_height),
                            braille_grade=int(braille_grade)
                        )
                        recommended_scale = fit_analysis.get('recommended_scale', 100)

                        if scale_percent is not None:
                            effective_scale = scale_percent
                        elif auto_scale and recommended_scale > 100:
                            if max_scale_factor is not None:
                                max_scale = max_scale_factor * 100
                                effective_scale = min(recommended_scale, max_scale)
                            else:
                                effective_scale = recommended_scale

                        # Apply scaling if needed
                        if effective_scale and effective_scale != 100:
                            from PIL import Image as PILImage
                            import tempfile

                            with PILImage.open(str(input_file)) as base_image:
                                scaled_image = processor.scale_image(base_image, effective_scale)
                                scaled_temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix='scaled_')
                                scaled_image.save(scaled_temp.name, format='PNG')

                            # Detect text on scaled image with EasyOCR
                            if detect_text:
                                try:
                                    from tactile_core.core.easyocr_detector import EasyOCRDetector
                                    detector = EasyOCRDetector()
                                    with PILImage.open(scaled_temp.name) as scaled_img:
                                        easyocr_texts = detector.detect_text(scaled_img)
                                except Exception:
                                    pass  # Silently skip in batch mode

                            # Re-process the scaled image
                            processed_image, metadata = processor.process(
                                input_path=scaled_temp.name,
                                threshold=file_threshold,
                                check_density_flag=True,
                                enhance=file_enhance,
                                enhance_strength=file_enhance_strength,
                                paper_size=file_paper_size,
                                auto_reduce_density=auto_reduce_density,
                                target_density=target_density,
                                max_reduction_iterations=max_reduction_iterations,
                                detect_text=False
                            )

                            # Inject EasyOCR results
                            if detect_text and easyocr_texts:
                                metadata['detected_texts'] = easyocr_texts

                            detected_texts = metadata.get('detected_texts', [])
                    except Exception:
                        pass  # Silently skip scaling errors in batch mode

                # Convert detected text to Braille labels if text detection was enabled
                braille_labels = None
                symbol_key_entries = None
                braille_converter = None
                if detect_text and detected_texts:
                    try:
                        # Get braille config from standards
                        braille_config_dict = standards.get_all_config().get('braille', {})

                        # Create Braille config with CLI overrides
                        braille_config = BrailleConfig(
                            enabled=True,
                            grade=int(braille_grade),
                            placement=braille_placement,
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

                        # Convert to Braille with abbreviation key support
                        braille_converter = BrailleConverter(braille_config, AccessibleLogger(verbose=verbose))

                        if abbreviation_key or force_abbreviation_key:
                            detected_text_widths = {text.text: text.width for text in detected_texts}
                            braille_labels, key_entries = braille_converter.create_braille_labels(
                                detected_texts,
                                generate_key=True,
                                detected_text_widths=detected_text_widths if not force_abbreviation_key else None
                            )
                        else:
                            braille_labels, symbol_key_entries = braille_converter.create_braille_labels(
                                detected_texts
                            )

                        # White out text regions
                        if detected_texts:
                            processed_image = processor.whiteout_text_regions(
                                processed_image,
                                detected_texts,
                                padding=braille_config_dict.get('whiteout_padding', 5)
                            )
                    except Exception:
                        # Silently skip braille conversion errors in batch mode
                        braille_labels = None
                        symbol_key_entries = None
                        braille_converter = None
                        key_entries = []

                # Generate PDF
                pdf_generator = PIAFPDFGenerator(logger=AccessibleLogger(verbose=verbose), config=standards.get_all_config())
                pdf_generator.generate(
                    image=processed_image,
                    output_path=str(output_file),
                    paper_size=file_paper_size,
                    metadata=metadata,
                    braille_labels=braille_labels,
                    symbol_key_entries=symbol_key_entries,
                    braille_converter=braille_converter,
                    key_entries=key_entries if key_entries else None
                )

                successful += 1
                logger.info(f"  Success: {output_file.name}")

            except Exception as e:
                failed += 1
                failed_files.append((input_file.name, str(e)))
                logger.error(f"  Failed: {input_file.name}", e)

            logger.blank_line()

        # Summary
        logger.info("=" * 60)
        logger.info("Batch Processing Complete")
        logger.info("=" * 60)
        logger.info(f"Total files: {len(image_files)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")

        if failed_files:
            logger.blank_line()
            logger.info("Failed files:")
            for filename, error in failed_files:
                logger.info(f"  {filename}: {error}")

        logger.info("=" * 60)

        if failed > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.blank_line()
        logger.info("Batch processing cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Batch processing failed", e)
        sys.exit(1)


if __name__ == '__main__':
    main()
