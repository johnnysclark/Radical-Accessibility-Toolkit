"""
PDF generation module for PIAF-compatible output.

Generates high-contrast PDFs optimized for tactile printing on PIAF machines.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image
import io
import numpy as np
import cv2

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from tactile_core.utils.logger import AccessibleLogger
from tactile_core.utils.validators import validate_output_path, resolve_wsl_path, verify_file_exists
from tactile_core.core.braille_converter import BrailleConverter, BrailleConfig, BrailleLabel, KeyEntry, BRAILLE_DPI, BRAILLE_FONT_SIZE_POINTS


class PDFGeneratorError(Exception):
    """Custom exception for PDF generation errors."""
    pass


class PIAFPDFGenerator:
    """
    PDF generator optimized for PIAF (Picture In A Flash) machines.

    Features:
    - 300 DPI output
    - Pure black & white (no grayscale)
    - Precise dimensions
    - Embedded metadata
    """

    # Paper sizes in inches
    SIZES = {
        'letter': (8.5, 11.0),
        'tabloid': (11.0, 17.0)
    }

    # Target DPI for PIAF printing
    TARGET_DPI = 300

    def __init__(self, logger: Optional[AccessibleLogger] = None, config: Optional[dict] = None):
        """
        Initialize PDF generator.

        Args:
            logger: Optional AccessibleLogger instance
            config: Optional configuration dictionary
        """
        self.logger = logger or AccessibleLogger(verbose=False)
        self.config = config or {}
        self.image_height = 0  # Track image height for coordinate conversion
        self._braille_font_available = False  # Track if Braille font is registered

        # Register Unicode Braille-compatible font
        self._register_braille_font()

        # Create internal Braille converter for dual-text rendering
        self._internal_braille_converter = self._create_internal_braille_converter()

    def _register_braille_font(self):
        """
        Register TrueType font with Unicode Braille support.

        Attempts to register DejaVu Sans which has full Unicode Braille
        character support (U+2800-U+28FF). Sets _braille_font_available flag.
        """
        # Check if font is already registered (prevent duplicate registration errors)
        if 'DejaVu Sans' in pdfmetrics.getRegisteredFontNames():
            # Font already registered, mark as available
            self._braille_font_available = True
            return

        # Font paths in priority order - bundled font first for reliability
        font_paths = [
            # 1. Bundled font (most reliable)
            Path(__file__).parent.parent / 'data' / 'fonts' / 'DejaVuSans.ttf',
            # 2. Linux/WSL system paths
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
            Path('/usr/share/fonts/truetype/dejavu-sans/DejaVuSans.ttf'),
            # 3. macOS
            Path('/System/Library/Fonts/Supplemental/DejaVuSans.ttf'),
            Path('/Library/Fonts/DejaVuSans.ttf'),
            # 4. Windows
            Path('C:/Windows/Fonts/DejaVuSans.ttf'),
        ]

        for font_path in font_paths:
            try:
                if font_path.exists():
                    # Register with space to match config: "DejaVu Sans"
                    dejavu_font = TTFont('DejaVu Sans', str(font_path))
                    try:
                        pdfmetrics.registerFont(dejavu_font)
                        self._braille_font_available = True
                        self.logger.info(f"Registered DejaVu Sans font from: {font_path}")
                    except KeyError as e:
                        # Font already registered in this session, which is fine
                        if "already registered" in str(e) or "redefining" in str(e):
                            self._braille_font_available = True
                            self.logger.debug(f"DejaVu Sans already registered: {e}")
                        else:
                            raise
                    return
            except Exception as e:
                self.logger.debug(f"Failed to register font from {font_path}: {e}")
                continue

        # If we get here, no font was registered - this is critical
        self._braille_font_available = False
        self.logger.error(
            "CRITICAL: DejaVu Sans font not found. Braille characters will NOT render. "
            "Install with: sudo apt-get install fonts-dejavu"
        )

    def _create_internal_braille_converter(self) -> Optional[BrailleConverter]:
        """
        Create a BrailleConverter for tool-generated text (labels, instructions).

        Returns:
            BrailleConverter instance or None if creation fails
        """
        if not self._braille_font_available:
            return None

        try:
            braille_config = BrailleConfig(
                enabled=True,
                grade=2,  # Use Grade 2 (contracted) for shorter output
                font_name=self.config.get('braille', {}).get('font_name', 'DejaVu Sans'),
                font_size=BRAILLE_FONT_SIZE_POINTS
            )
            return BrailleConverter(braille_config, self.logger)
        except Exception as e:
            self.logger.debug(f"Failed to create internal BrailleConverter: {e}")
            return None

    def calculate_dimensions(self, image: Image.Image, dpi: int = 300) -> Tuple[float, float]:
        """
        Calculate physical dimensions of image in inches.

        Args:
            image: PIL Image
            dpi: Dots per inch

        Returns:
            Tuple of (width_inches, height_inches)
        """
        width_px, height_px = image.size
        width_inches = width_px / dpi
        height_inches = height_px / dpi

        return width_inches, height_inches

    def fits_on_page(self, image: Image.Image, paper_size: str = 'letter',
                     dpi: int = 300) -> Tuple[bool, Tuple[float, float]]:
        """
        Check if image fits on specified paper size.

        Args:
            image: PIL Image
            paper_size: Paper size name ('letter' or 'tabloid')
            dpi: Dots per inch

        Returns:
            Tuple of (fits, (image_width, image_height))
        """
        if paper_size not in self.SIZES:
            raise PDFGeneratorError(f"Invalid paper size: {paper_size}")

        page_width, page_height = self.SIZES[paper_size]

        # Auto-detect landscape: if image is wider than tall, use landscape page
        img_w, img_h = image.size
        if img_w > img_h:
            page_width, page_height = page_height, page_width

        img_width, img_height = self.calculate_dimensions(image, dpi)

        fits = img_width <= page_width and img_height <= page_height

        return fits, (img_width, img_height)

    def generate(self, image: Image.Image, output_path: str,
                 paper_size: str = 'letter',
                 metadata: Optional[dict] = None,
                 braille_labels: Optional[list] = None,
                 symbol_key_entries: Optional[list] = None,
                 braille_converter=None,
                 key_entries: Optional[List[KeyEntry]] = None,
                 sticker_workflow: bool = False,
                 page_number: int = 1) -> str:
        """
        Generate PDF optimized for PIAF printing.

        Args:
            image: Processed B&W PIL Image
            output_path: Path for output PDF
            paper_size: Paper size ('letter' or 'tabloid')
            metadata: Optional metadata dictionary to embed
            braille_labels: Optional list of BrailleLabel objects to render
            symbol_key_entries: Optional list of SymbolKeyEntry objects for key page
            braille_converter: Optional BrailleConverter for rendering Braille on key page
            key_entries: Optional list of KeyEntry objects for abbreviation key page
            sticker_workflow: If True, adds registration mark for alignment
            page_number: Page number for registration mark (sticker workflow)

        Returns:
            Path to generated PDF file

        Raises:
            PDFGeneratorError: If PDF generation fails
        """
        # Validate output path
        is_valid, error_msg = validate_output_path(output_path)
        if not is_valid:
            raise PDFGeneratorError(error_msg)

        self.logger.generating("Creating PDF output")

        try:
            # Get paper dimensions
            if paper_size not in self.SIZES:
                raise PDFGeneratorError(f"Invalid paper size: {paper_size}")

            page_width, page_height = self.SIZES[paper_size]

            # Auto-detect landscape: if image is wider than tall, use landscape page
            img_w, img_h = image.size
            if img_w > img_h:
                page_width, page_height = page_height, page_width
                self.logger.info(f"Auto-rotated to landscape ({page_width}\" x {page_height}\")")

            page_width_pts = page_width * inch
            page_height_pts = page_height * inch

            # Store image height for coordinate conversion
            self.image_height = image.size[1]

            # Check if image fits
            fits, (img_width, img_height) = self.fits_on_page(image, paper_size, self.TARGET_DPI)

            if not fits:
                self.logger.warning(
                    f"Image size ({img_width:.1f}\" x {img_height:.1f}\") "
                    f"exceeds {paper_size} paper ({page_width}\" x {page_height}\")"
                )
                self.logger.info("Image will be scaled to fit")
                # Calculate scaling factor
                scale_w = page_width / img_width
                scale_h = page_height / img_height
                scale = min(scale_w, scale_h) * 0.95  # 5% margin

                img_width *= scale
                img_height *= scale
            else:
                self.logger.info(
                    f"Image size: {img_width:.1f} inches x {img_height:.1f} inches"
                )
                self.logger.info(f"Fits on: {paper_size} size paper ({page_width}\" x {page_height}\")")

            # Create PDF canvas
            c = canvas.Canvas(output_path, pagesize=(page_width_pts, page_height_pts))

            # Set metadata
            c.setTitle(metadata.get('source_file', 'PIAF Image') if metadata else 'PIAF Image')
            c.setAuthor("TACT — Tactile Architectural Conversion Tool")
            c.setSubject("Tactile graphics for PIAF printing")
            c.setCreator("tact")

            # Center image on page
            x_offset = (page_width - img_width) / 2 * inch
            y_offset = (page_height - img_height) / 2 * inch

            # Convert PIL Image to format reportlab can use
            img_buffer = io.BytesIO()
            # Save as PNG to preserve 1-bit format
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            img_reader = ImageReader(img_buffer)

            # Draw image
            c.drawImage(
                img_reader,
                x_offset,
                y_offset,
                width=img_width * inch,
                height=img_height * inch,
                preserveAspectRatio=True
            )

            # Add Braille labels if provided
            if braille_labels:
                # Calculate scale factor from image pixels to PDF inches
                scale_factor = img_width / image.size[0]

                # Filter labels that would bleed off page edge → abbreviate to key
                if key_entries is not None and braille_converter:
                    braille_labels, key_entries = self._filter_overflow_labels(
                        braille_labels, key_entries, braille_converter,
                        scale_factor, x_offset, page_width_pts
                    )

                self._add_braille_labels(c, braille_labels, scale_factor, x_offset, y_offset,
                                        page_width_pts, page_height_pts)

            # Add registration mark for sticker workflow alignment
            if sticker_workflow:
                self.add_registration_mark(c, page_width_pts, page_height_pts, page_number)

            # Add processing metadata as PDF info
            if metadata:
                timestamp = datetime.now().isoformat()

                # Add custom metadata
                density = metadata.get('density_percentage', 'N/A')
                density_str = f"{density:.1f}%" if isinstance(density, (int, float)) else str(density)

                c.setKeywords(
                    f"threshold:{metadata.get('threshold', 'N/A')}, "
                    f"density:{density_str}, "
                    f"timestamp:{timestamp}"
                )

            # Add key page if there are symbol entries
            if symbol_key_entries:
                c.showPage()
                self.add_key_page(c, symbol_key_entries, page_width_pts, page_height_pts,
                                 braille_converter)

            # Add abbreviation key page if there are key entries
            if key_entries:
                c.showPage()
                self.add_abbreviation_key_page(c, key_entries, page_width_pts, page_height_pts)

            # Resolve to full absolute path
            full_output_path = resolve_wsl_path(output_path)

            # Save PDF
            c.save()

            # Verify the file was actually created
            file_exists, verified_path = verify_file_exists(full_output_path)
            if file_exists:
                self.logger.success(f"PDF saved successfully")
                self.logger.info(f"Output path: {verified_path}")
            else:
                self.logger.warning("PDF save() completed but file verification failed")
                self.logger.warning(f"Expected at: {full_output_path}")

            self.logger.blank_line()
            self.logger.complete("Processing finished successfully")
            self.logger.info("Ready to print on PIAF machine")

            return full_output_path

        except PDFGeneratorError:
            raise
        except Exception as e:
            raise PDFGeneratorError(f"Failed to generate PDF: {str(e)}") from e

    def _filter_overflow_labels(
        self,
        labels: list,
        key_entries: List[KeyEntry],
        braille_converter,
        scale_factor: float,
        x_offset: float,
        page_width_pts: float
    ) -> tuple:
        """
        Check each label's rendered PDF position. Labels that would extend
        past the right page edge are replaced with single-letter abbreviations
        and added to the abbreviation key.

        Returns:
            Tuple of (filtered_labels, updated_key_entries)
        """
        # Braille font metrics for width estimation
        braille_config = self.config.get('braille', {})
        font_name = braille_config.get('font_name', 'DejaVu Sans')
        font_size = BRAILLE_FONT_SIZE_POINTS

        # We need a temporary canvas to measure string widths
        # Use stringWidth from reportlab directly
        from reportlab.pdfbase.pdfmetrics import stringWidth

        # Track next key letter index (continue from existing entries)
        next_letter_idx = len(key_entries)
        filtered = []
        overflow_count = 0

        for label in labels:
            # Compute PDF x position (same math as _add_braille_labels)
            pdf_x = label.x * scale_factor * inch + x_offset
            label_width_pts = stringWidth(label.braille_text, font_name, font_size)

            if pdf_x + label_width_pts > page_width_pts and len(label.braille_text) > 3:
                # This label overflows and isn't already a short abbreviation
                if next_letter_idx < 26:
                    letter = chr(ord('A') + next_letter_idx)
                else:
                    first = chr(ord('A') + (next_letter_idx // 26) - 1)
                    second = chr(ord('A') + (next_letter_idx % 26))
                    letter = first + second
                next_letter_idx += 1

                letter_braille = braille_converter.convert_text(letter)

                # Add to key
                key_entries.append(KeyEntry(
                    letter=letter,
                    original_text=label.original_text,
                    braille_full=label.braille_text
                ))

                # Replace label text with abbreviated version
                filtered.append(BrailleLabel(
                    braille_text=letter_braille,
                    x=label.x,
                    y=label.y,
                    original_text=letter,
                    width=braille_converter._estimate_label_width(letter_braille),
                    rotation_degrees=label.rotation_degrees
                ))
                overflow_count += 1
            else:
                filtered.append(label)

        if overflow_count > 0:
            self.logger.info(
                f"Abbreviated {overflow_count} label(s) that would overflow page edge"
            )

        return filtered, key_entries

    def _add_braille_labels(self, canvas_obj: canvas.Canvas, labels: list,
                          scale_factor: float, x_offset: float, y_offset: float,
                          page_width_pts: float = 0, page_height_pts: float = 0):
        """
        Render Braille labels on PDF.

        Args:
            canvas_obj: ReportLab canvas object
            labels: List of BrailleLabel objects
            scale_factor: Scale factor for coordinates (image pixels to PDF inches)
            x_offset: X offset for centering image on page (in points)
            y_offset: Y offset for centering image on page (in points)
            page_width_pts: Page width in points for edge clamping
            page_height_pts: Page height in points for edge clamping
        """
        if not labels:
            return

        # Check if Braille font is available - critical for rendering
        if not self._braille_font_available:
            self.logger.error(
                "Cannot render Braille labels: No Braille-compatible font available. "
                "Braille characters require DejaVu Sans or similar Unicode font. "
                "Install with: sudo apt-get install fonts-dejavu"
            )
            return

        self.logger.progress(f"Adding {len(labels)} Braille labels to PDF")

        # Get Braille font settings from config
        braille_config = self.config.get('braille', {})
        font_name = braille_config.get('font_name', 'DejaVu Sans')
        font_size = braille_config.get('font_size', BRAILLE_FONT_SIZE_POINTS)

        # Set font for Braille text - must use Braille-compatible font
        try:
            canvas_obj.setFont(font_name, font_size)
        except Exception as e:
            self.logger.error(
                f"Failed to set Braille font '{font_name}': {e}. "
                "Braille labels will not render correctly."
            )
            return

        # Convert font size from points to pixels for baseline calculation
        font_size_px = font_size * (BRAILLE_DPI / 72)

        # Set fill color to black for Braille text
        # This is critical - without explicit color, text may not render visibly
        canvas_obj.setFillColorRGB(0, 0, 0)

        # Counter-highlighting margin in points (provides visual separation)
        bg_margin = 2.0

        # Render each label with white background (counter-highlighting)
        for label in labels:
            # Scale coordinates from image pixels to PDF inches
            x = label.x * scale_factor

            # Convert Y coordinate: PDF origin is bottom-left, image origin is top-left
            # label.y is the TOP of where text should appear (in image space, in pixels)
            # drawString expects the BASELINE position
            # Baseline is approximately at (top + ascent), where ascent ≈ 0.8 * font_size_px
            # So: baseline_image_y = label.y + (0.8 * font_size_px)
            # Then convert to PDF space: PDF_y = (image_height - baseline_image_y) * scale_factor
            baseline_offset = 0.8 * font_size_px
            y = (self.image_height - label.y - baseline_offset) * scale_factor

            # Add offsets for image centering
            x = x * inch + x_offset
            y = y * inch + y_offset

            # Get rotation (default to 0 if not present)
            rotation = getattr(label, 'rotation_degrees', 0.0)

            # Calculate label width in points for background rectangle
            label_width_pts = canvas_obj.stringWidth(label.braille_text, font_name, font_size)

            # Clamp to page boundaries so labels never bleed off the edge
            if page_width_pts > 0:
                right_edge = x + label_width_pts
                if right_edge > page_width_pts:
                    x = max(0, page_width_pts - label_width_pts)
            if page_height_pts > 0:
                if y + font_size > page_height_pts:
                    y = page_height_pts - font_size
                if y < 0:
                    y = 0

            # Draw white background (counter-highlighting) behind label
            # This ensures Braille is readable against any underlying image content
            descent = font_size * 0.2  # Approximate descent below baseline
            rect_x = x - bg_margin
            rect_y = y - descent - bg_margin
            rect_width = label_width_pts + (2 * bg_margin)
            rect_height = font_size + (2 * bg_margin)

            if rotation != 0:
                # For rotated text, draw rotated background
                canvas_obj.saveState()
                canvas_obj.translate(x, y)
                canvas_obj.rotate(rotation)
                # Draw background at origin (we've translated to x, y)
                canvas_obj.setFillColorRGB(1, 1, 1)  # White
                canvas_obj.rect(-bg_margin, -descent - bg_margin,
                               rect_width, rect_height, stroke=0, fill=1)
                # Draw text
                canvas_obj.setFillColorRGB(0, 0, 0)  # Black
                canvas_obj.drawString(0, 0, label.braille_text)
                canvas_obj.restoreState()
            else:
                # Draw background then text
                canvas_obj.setFillColorRGB(1, 1, 1)  # White
                canvas_obj.rect(rect_x, rect_y, rect_width, rect_height, stroke=0, fill=1)
                canvas_obj.setFillColorRGB(0, 0, 0)  # Black
                canvas_obj.drawString(x, y, label.braille_text)

        self.logger.success(f"Added {len(labels)} Braille labels")

    def add_text_page(self, canvas_obj: canvas.Canvas, text: str,
                     page_width: float, page_height: float):
        """
        Add a text page to the PDF (for assembly instructions).

        Renders each line in dual format: Braille above, print below.
        This ensures both blind and sighted users can read the content.

        Args:
            canvas_obj: ReportLab canvas object
            text: Text content to add
            page_width: Page width in points
            page_height: Page height in points
        """
        braille_config = self.config.get('braille', {})
        braille_font = braille_config.get('font_name', 'DejaVu Sans')
        margin = 0.5 * inch
        y_position = page_height - margin
        braille_to_print_gap = BRAILLE_FONT_SIZE_POINTS + 6  # Braille baseline to print baseline
        print_to_next_gap = 20  # Print baseline to next entry

        for line in text.split('\n'):
            if y_position < margin:
                # New page needed
                canvas_obj.showPage()
                y_position = page_height - margin

            # Draw Braille version first (if converter available and line not empty)
            if line.strip() and self._internal_braille_converter and self._braille_font_available:
                try:
                    braille_line = self._internal_braille_converter.convert_text(line)
                    canvas_obj.setFont(braille_font, BRAILLE_FONT_SIZE_POINTS)
                    canvas_obj.drawString(margin, y_position, braille_line)
                    y_position -= braille_to_print_gap  # Move down for print line
                except Exception:
                    pass  # If Braille fails, just show print

            # Draw print version
            canvas_obj.setFont("Courier", 12)
            canvas_obj.drawString(margin, y_position, line)
            y_position -= print_to_next_gap

    def add_tile_label(self, canvas_obj: canvas.Canvas, label: str,
                      page_width: float, page_height: float):
        """
        Add tile label to bottom of page in dual format (Braille + print).

        Args:
            canvas_obj: ReportLab canvas object
            label: Tile label text
            page_width: Page width in points
            page_height: Page height in points
        """
        braille_config = self.config.get('braille', {})
        braille_font = braille_config.get('font_name', 'DejaVu Sans')
        y_base = 0.25 * inch

        # Draw Braille version first (above print)
        if self._internal_braille_converter and self._braille_font_available:
            try:
                braille_label = self._internal_braille_converter.convert_text(label)
                canvas_obj.setFont(braille_font, BRAILLE_FONT_SIZE_POINTS)
                braille_width = canvas_obj.stringWidth(braille_label, braille_font, BRAILLE_FONT_SIZE_POINTS)
                x_braille = (page_width - braille_width) / 2
                canvas_obj.drawString(x_braille, y_base + 16, braille_label)
            except Exception:
                pass  # If Braille fails, just show print

        # Draw print version below Braille
        canvas_obj.setFont("Helvetica-Bold", 12)
        text_width = canvas_obj.stringWidth(label, "Helvetica-Bold", 12)
        x = (page_width - text_width) / 2
        canvas_obj.drawString(x, y_base, label)

    def add_registration_mark(self, canvas_obj: canvas.Canvas,
                              page_width: float, page_height: float,
                              page_number: int = 1) -> None:
        """
        Add registration mark in bottom-right corner with Braille page number.

        Used for sticker workflow alignment - ensures PIAF and text PDFs
        can be aligned when reloading paper for second print pass.

        Design:
        - Position: 0.5 inch from right edge, 0.5 inch from bottom
        - Visual: Corner bracket shape (inverted L)
        - Braille page number to the left of the bracket

        Args:
            canvas_obj: ReportLab canvas object
            page_width: Page width in points
            page_height: Page height in points
            page_number: Page number to display in Braille
        """
        margin = 0.5 * inch
        mark_size = 0.3 * inch

        # Position in bottom-right corner
        x = page_width - margin - mark_size
        y = margin

        # Draw corner bracket (inverted L shape)
        canvas_obj.setStrokeColorRGB(0, 0, 0)
        canvas_obj.setLineWidth(2)
        canvas_obj.line(x, y + mark_size, x, y)  # Vertical line
        canvas_obj.line(x, y, x + mark_size, y)  # Horizontal line

        # Add small corner dot for precise alignment
        canvas_obj.setFillColorRGB(0, 0, 0)
        canvas_obj.circle(x, y, 3, stroke=0, fill=1)

        # Add Braille page number to the left of the mark
        braille_config = self.config.get('braille', {})
        braille_font = braille_config.get('font_name', 'DejaVu Sans')

        if self._internal_braille_converter and self._braille_font_available:
            try:
                braille_num = self._internal_braille_converter.convert_text(str(page_number))
                canvas_obj.setFont(braille_font, BRAILLE_FONT_SIZE_POINTS)
                # Position Braille number to the left of the bracket
                braille_width = canvas_obj.stringWidth(braille_num, braille_font, BRAILLE_FONT_SIZE_POINTS)
                canvas_obj.drawString(x - braille_width - 8, y + 4, braille_num)
            except Exception:
                pass  # If Braille fails, mark is still useful

    def add_abbreviation_key_page(self, canvas_obj: canvas.Canvas,
                                   key_entries: List[KeyEntry],
                                   page_width: float, page_height: float) -> None:
        """
        Add an abbreviation key page at the current position in the PDF.

        Renders each key entry in dual format:
          ⠠⠁ = ⠠⠅⠊⠞⠉⠓⠑⠝
          A = Kitchen

        This should be called BEFORE adding drawing pages so the key appears first.

        Args:
            canvas_obj: ReportLab canvas object
            key_entries: List of KeyEntry objects to include in the key
            page_width: Page width in points
            page_height: Page height in points
        """
        if not key_entries:
            return

        # Layout constants — sized for BANA-standard 24pt Braille
        margin = 0.75 * inch
        braille_line_height = BRAILLE_FONT_SIZE_POINTS + 6  # Braille line + clearance
        print_line_height = 16   # Points for print line
        entry_spacing = 12       # Breathing room between entries
        total_entry_height = braille_line_height + print_line_height + entry_spacing

        # Two-column layout constants
        column_gap = 0.4 * inch  # Gap between columns
        column_width = (page_width - 2 * margin - column_gap) / 2
        left_column_x = margin
        right_column_x = margin + column_width + column_gap

        # Get font settings
        braille_config = self.config.get('braille', {})
        braille_font = braille_config.get('font_name', 'DejaVu Sans')
        braille_font_size = BRAILLE_FONT_SIZE_POINTS  # BANA standard Braille size
        print_font_size = 12  # Readable alongside 24pt Braille
        title_print_font_size = 16  # Title for visual hierarchy

        # Start position
        y_position = page_height - margin
        content_start_y = None  # Will be set after title

        # Add title in dual format: Braille and print (spans both columns)
        title_text = "ABBREVIATION KEY"

        # Title in Braille
        if self._internal_braille_converter and self._braille_font_available:
            try:
                braille_title = self._internal_braille_converter.convert_text(title_text)
                canvas_obj.setFont(braille_font, braille_font_size)
                canvas_obj.setFillColorRGB(0, 0, 0)
                # Truncate if wider than available space
                title_max_width = page_width - 2 * margin
                title_width = canvas_obj.stringWidth(braille_title, braille_font, braille_font_size)
                if title_width > title_max_width:
                    ellipsis = "\u2804\u2804\u2804"
                    while len(braille_title) > 3 and canvas_obj.stringWidth(braille_title + ellipsis, braille_font, braille_font_size) > title_max_width:
                        braille_title = braille_title[:-1]
                    braille_title = braille_title.rstrip() + ellipsis

                canvas_obj.drawString(margin, y_position, braille_title)
                y_position -= braille_line_height
            except Exception as e:
                self.logger.debug(f"Failed to render Braille title: {e}")

        # Title in print
        canvas_obj.setFont("Helvetica-Bold", title_print_font_size)
        canvas_obj.setFillColorRGB(0, 0, 0)
        canvas_obj.drawString(margin, y_position, title_text)
        y_position -= title_print_font_size + 8

        # Draw horizontal line under title (spans both columns)
        canvas_obj.setStrokeColorRGB(0, 0, 0)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(margin, y_position, page_width - margin, y_position)
        y_position -= braille_line_height

        # Store the content start position for column resets
        content_start_y = y_position

        # Two-column rendering state
        current_column = 0  # 0 = left, 1 = right
        left_y = content_start_y
        right_y = content_start_y

        def get_current_x():
            return left_column_x if current_column == 0 else right_column_x

        def get_current_y():
            return left_y if current_column == 0 else right_y

        def set_current_y(new_y):
            nonlocal left_y, right_y
            if current_column == 0:
                left_y = new_y
            else:
                right_y = new_y

        # Maximum characters for truncation in two-column layout
        max_chars = 28

        # Render each key entry
        for idx, entry in enumerate(key_entries):
            y_pos = get_current_y()

            # Check if current column has room
            if y_pos < margin + total_entry_height + braille_line_height:
                if current_column == 0:
                    # Switch to right column
                    current_column = 1
                    y_pos = right_y
                else:
                    # Both columns full - start new page
                    canvas_obj.showPage()
                    current_column = 0
                    left_y = page_height - margin
                    right_y = page_height - margin

                    # Add continuation header in dual format (spans both columns)
                    if self._internal_braille_converter and self._braille_font_available:
                        try:
                            cont_braille = self._internal_braille_converter.convert_text("KEY (continued)")
                            canvas_obj.setFont(braille_font, braille_font_size)
                            canvas_obj.setFillColorRGB(0, 0, 0)
                            canvas_obj.drawString(margin, left_y, cont_braille)
                            left_y -= braille_line_height
                        except Exception:
                            pass

                    canvas_obj.setFont("Helvetica-Bold", title_print_font_size)
                    canvas_obj.setFillColorRGB(0, 0, 0)
                    canvas_obj.drawString(margin, left_y, "KEY (continued)")
                    left_y -= title_print_font_size + 8

                    # Draw horizontal line under continuation header
                    canvas_obj.setStrokeColorRGB(0, 0, 0)
                    canvas_obj.setLineWidth(1)
                    canvas_obj.line(margin, left_y, page_width - margin, left_y)
                    left_y -= braille_line_height

                    # Sync both column starting positions
                    right_y = left_y
                    y_pos = left_y

            x_pos = get_current_x()
            y_pos = get_current_y()

            # Line 1 (Braille): letter_braille = braille_full
            if self._internal_braille_converter and self._braille_font_available:
                try:
                    # Convert the letter to Braille
                    letter_braille = self._internal_braille_converter.convert_text(entry.letter)
                    equals_braille = self._internal_braille_converter.convert_text("=")

                    # Construct Braille line: letter_braille = braille_full
                    braille_line = f"{letter_braille} {equals_braille} {entry.braille_full}"

                    # Truncate Braille line if it exceeds column width
                    braille_width = canvas_obj.stringWidth(braille_line, braille_font, braille_font_size)
                    if braille_width > column_width:
                        ellipsis = "\u2804\u2804\u2804"
                        while len(braille_line) > 5 and canvas_obj.stringWidth(braille_line + ellipsis, braille_font, braille_font_size) > column_width:
                            braille_line = braille_line[:-1]
                        braille_line = braille_line.rstrip() + ellipsis

                    canvas_obj.setFont(braille_font, braille_font_size)
                    canvas_obj.setFillColorRGB(0, 0, 0)
                    canvas_obj.drawString(x_pos, y_pos, braille_line)
                except Exception as e:
                    self.logger.debug(f"Failed to render Braille entry for {entry.letter}: {e}")

            y_pos -= braille_line_height

            # Line 2 (Print): letter = original_text
            print_line = f"{entry.letter} = {entry.original_text}"

            # Truncate if too long for column width
            if len(print_line) > max_chars:
                print_line = print_line[:max_chars - 3] + "..."

            canvas_obj.setFont("Helvetica", print_font_size)
            canvas_obj.setFillColorRGB(0, 0, 0)
            canvas_obj.drawString(x_pos, y_pos, print_line)

            y_pos -= print_line_height + entry_spacing
            set_current_y(y_pos)

        self.logger.info(f"Added abbreviation key page with {len(key_entries)} entries (two-column layout)")

    def add_color_pattern_legend(
        self,
        canvas_obj: canvas.Canvas,
        regions,
        patterns,
        page_width: float,
        page_height: float,
    ) -> None:
        """
        Add a COLOR PATTERN KEY page showing which tactile pattern maps to which color.

        Each entry shows a rendered pattern swatch alongside the color name
        in both Braille and print.

        Args:
            canvas_obj: ReportLab canvas object
            regions: List of ColorRegion objects
            patterns: List of TactilePattern objects
            page_width: Page width in points
            page_height: Page height in points
        """
        if not regions or not patterns:
            return

        from tactile_core.core.rainbowtact import RainbowTactConverter, RainbowTactConfig

        # Layout constants
        margin = 0.75 * inch
        swatch_width_in = 1.0   # inches
        swatch_height_in = 0.5  # inches
        swatch_width_pts = swatch_width_in * inch
        swatch_height_pts = swatch_height_in * inch
        swatch_px_w = int(swatch_width_in * 300)  # 300 DPI
        swatch_px_h = int(swatch_height_in * 300)

        braille_line_height = BRAILLE_FONT_SIZE_POINTS + 6
        print_line_height = 16
        entry_spacing = 12
        entry_height = swatch_height_pts + braille_line_height + print_line_height + entry_spacing

        # Two-column layout
        column_gap = 0.4 * inch
        column_width = (page_width - 2 * margin - column_gap) / 2
        left_column_x = margin
        right_column_x = margin + column_width + column_gap

        # Font settings
        braille_config = self.config.get('braille', {})
        braille_font = braille_config.get('font_name', 'DejaVu Sans')
        braille_font_size = BRAILLE_FONT_SIZE_POINTS
        print_font_size = 10
        title_print_font_size = 14

        # Start position
        y_position = page_height - margin

        # Title: "COLOR PATTERN KEY" in dual format
        title_text = "COLOR PATTERN KEY"

        if self._internal_braille_converter and self._braille_font_available:
            try:
                braille_title = self._internal_braille_converter.convert_text(title_text)
                canvas_obj.setFont(braille_font, braille_font_size)
                canvas_obj.setFillColorRGB(0, 0, 0)
                canvas_obj.drawString(margin, y_position, braille_title)
                y_position -= braille_font_size + 4
            except Exception:
                pass

        canvas_obj.setFont("Helvetica-Bold", title_print_font_size)
        canvas_obj.setFillColorRGB(0, 0, 0)
        canvas_obj.drawString(margin, y_position, title_text)
        y_position -= title_print_font_size + 8

        # Horizontal line under title
        canvas_obj.setStrokeColorRGB(0, 0, 0)
        canvas_obj.setLineWidth(1)
        canvas_obj.line(margin, y_position, page_width - margin, y_position)
        y_position -= 16

        content_start_y = y_position

        # Column tracking
        current_column = 0
        left_y = content_start_y
        right_y = content_start_y

        # Create a dummy converter for rendering swatches
        converter = RainbowTactConverter()

        for region, pattern in zip(regions, patterns):
            # Get column position
            y_pos = left_y if current_column == 0 else right_y
            x_pos = left_column_x if current_column == 0 else right_column_x

            # Check if entry fits in current column
            if y_pos < margin + entry_height:
                if current_column == 0:
                    current_column = 1
                    y_pos = right_y
                    x_pos = right_column_x
                else:
                    # New page
                    canvas_obj.showPage()
                    current_column = 0
                    left_y = page_height - margin
                    right_y = page_height - margin

                    # Continuation header
                    if self._internal_braille_converter and self._braille_font_available:
                        try:
                            cont_braille = self._internal_braille_converter.convert_text("KEY (continued)")
                            canvas_obj.setFont(braille_font, braille_font_size)
                            canvas_obj.setFillColorRGB(0, 0, 0)
                            canvas_obj.drawString(margin, left_y, cont_braille)
                            left_y -= braille_font_size + 4
                        except Exception:
                            pass

                    canvas_obj.setFont("Helvetica-Bold", title_print_font_size)
                    canvas_obj.setFillColorRGB(0, 0, 0)
                    canvas_obj.drawString(margin, left_y, "KEY (continued)")
                    left_y -= title_print_font_size + 8

                    canvas_obj.setStrokeColorRGB(0, 0, 0)
                    canvas_obj.setLineWidth(1)
                    canvas_obj.line(margin, left_y, page_width - margin, left_y)
                    left_y -= 16

                    right_y = left_y
                    y_pos = left_y
                    x_pos = left_column_x

            # Render pattern swatch as bitmap
            swatch_array = np.full((swatch_px_h, swatch_px_w), 255, dtype=np.uint8)
            full_mask = np.ones((swatch_px_h, swatch_px_w), dtype=bool)

            if not pattern.is_empty:
                if pattern.is_chromatic and pattern.wavelength:
                    converter._render_waves(swatch_array, full_mask, pattern)
                elif not pattern.is_chromatic and pattern.dot_spacing:
                    converter._render_dots(swatch_array, full_mask, pattern)

            # Draw border around swatch
            cv2.rectangle(swatch_array, (0, 0), (swatch_px_w - 1, swatch_px_h - 1), 0, 2)

            # Convert swatch to PIL, then to reportlab image
            swatch_pil = Image.fromarray(swatch_array, mode='L')
            img_buffer = io.BytesIO()
            swatch_pil.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            img_reader = ImageReader(img_buffer)

            # Draw swatch on PDF (y_pos is top of entry, draw swatch at top)
            swatch_y = y_pos - swatch_height_pts
            canvas_obj.drawImage(
                img_reader, x_pos, swatch_y,
                width=swatch_width_pts, height=swatch_height_pts
            )

            # Color name in Braille (to the right of swatch)
            text_x = x_pos + swatch_width_pts + 8
            text_y = swatch_y + swatch_height_pts - braille_line_height

            if self._internal_braille_converter and self._braille_font_available:
                try:
                    braille_name = self._internal_braille_converter.convert_text(region.color_name)
                    canvas_obj.setFont(braille_font, braille_font_size)
                    canvas_obj.setFillColorRGB(0, 0, 0)
                    canvas_obj.drawString(text_x, text_y, braille_name)
                except Exception:
                    pass

            text_y -= print_line_height

            # Color name in print
            canvas_obj.setFont("Helvetica", print_font_size)
            canvas_obj.setFillColorRGB(0, 0, 0)

            # Add pattern type indicator
            if pattern.is_empty:
                descriptor = f"{region.color_name} (empty)"
            elif pattern.is_chromatic:
                descriptor = f"{region.color_name} (wave)"
            else:
                descriptor = f"{region.color_name} (dots)"

            canvas_obj.drawString(text_x, text_y, descriptor)

            # Update column y position
            new_y = swatch_y - entry_spacing
            if current_column == 0:
                left_y = new_y
            else:
                right_y = new_y

            # Alternate columns
            if current_column == 0:
                current_column = 1
            else:
                current_column = 0

        self.logger.info(f"Added color pattern legend with {len(regions)} entries")

    def add_key_page(self, canvas_obj: canvas.Canvas, symbol_key_entries: list,
                    page_width: float, page_height: float,
                    braille_converter=None):
        """
        Add a key page listing symbol-to-text mappings.

        Each entry shows the Braille symbol, print symbol, and original text.
        Format: ⠁ a = Original Text Here

        Args:
            canvas_obj: ReportLab canvas object
            symbol_key_entries: List of SymbolKeyEntry objects
            page_width: Page width in points
            page_height: Page height in points
            braille_converter: Optional BrailleConverter for converting symbols to Braille
        """
        if not symbol_key_entries:
            return

        margin = 0.5 * inch
        line_height = BRAILLE_FONT_SIZE_POINTS + 4  # Points between lines
        max_text_width = page_width - (2 * margin) - 100  # Leave room for symbol

        # Title
        y_position = page_height - margin

        # Draw title "KEY" in print
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.drawString(margin, y_position, "KEY")

        # Draw Braille title next to it if converter available
        if braille_converter:
            try:
                braille_title = braille_converter.convert_text("KEY")
                # Get Braille font settings
                braille_config = self.config.get('braille', {})
                font_name = braille_config.get('font_name', 'DejaVu Sans')
                try:
                    canvas_obj.setFont(font_name, BRAILLE_FONT_SIZE_POINTS)
                except:
                    canvas_obj.setFont('Helvetica', BRAILLE_FONT_SIZE_POINTS)
                canvas_obj.drawString(margin + 80, y_position, braille_title)
            except:
                pass  # Skip Braille title if conversion fails

        y_position -= line_height * 2  # Space after title

        # Horizontal line under title
        canvas_obj.setStrokeColorRGB(0, 0, 0)
        canvas_obj.line(margin, y_position + 10, page_width - margin, y_position + 10)

        y_position -= line_height

        # Get fonts ready
        braille_config = self.config.get('braille', {})
        braille_font = braille_config.get('font_name', 'DejaVu Sans')
        braille_font_size = BRAILLE_FONT_SIZE_POINTS

        entries_per_page = int((y_position - margin) / line_height)
        current_entry = 0

        for entry in symbol_key_entries:
            # Each entry takes 2 lines: Braille on top, print below
            lines_needed = 2

            # Check if we need a new page
            if y_position < margin + (line_height * lines_needed):
                canvas_obj.showPage()
                y_position = page_height - margin

                # Add continuation header
                canvas_obj.setFont("Helvetica-Bold", 12)
                canvas_obj.drawString(margin, y_position, "KEY (continued)")
                y_position -= line_height * 2

            # Line 1: Full Braille line (symbol = original_text)
            if braille_converter:
                try:
                    braille_symbol = braille_converter.convert_text(entry.symbol)
                    braille_equals = braille_converter.convert_text("=")
                    braille_text = braille_converter.convert_text(entry.original_text)

                    # Truncate if too long
                    if len(braille_text) > 35:
                        braille_text = braille_text[:32] + "..."

                    braille_line = f"{braille_symbol} {braille_equals} {braille_text}"

                    try:
                        canvas_obj.setFont(braille_font, braille_font_size)
                    except:
                        canvas_obj.setFont('Helvetica', braille_font_size)
                    canvas_obj.drawString(margin, y_position, braille_line)
                except:
                    pass

            y_position -= line_height

            # Line 2: Print line (symbol = original_text)
            text = entry.original_text
            # Truncate very long text
            max_chars = 50
            if len(text) > max_chars:
                text = text[:max_chars-3] + "..."

            canvas_obj.setFont("Helvetica", 12)
            canvas_obj.drawString(margin, y_position, f"{entry.symbol} = {text}")

            y_position -= line_height * 1.5  # Extra space between entries
            current_entry += 1

        self.logger.info(f"Added key page with {len(symbol_key_entries)} entries")

    def generate_with_tiling(self, image: Image.Image, output_path: str,
                            paper_size: str = 'letter',
                            tile_overlap: float = 0.1,
                            add_registration_marks: bool = True,
                            metadata: Optional[dict] = None,
                            braille_labels: Optional[list] = None,
                            key_entries: Optional[List[KeyEntry]] = None,
                            braille_converter=None) -> str:
        """
        Generate multi-page tiled PDF for large images.

        Args:
            image: Large B&W PIL Image
            output_path: Path for output PDF
            paper_size: Paper size to use for tiles
            tile_overlap: Overlap percentage between tiles (0.0-1.0)
            add_registration_marks: Whether to add registration marks
            metadata: Optional metadata dictionary
            braille_labels: Optional list of BrailleLabel objects to render
            key_entries: Optional list of KeyEntry objects for abbreviation key page
            braille_converter: Optional BrailleConverter for key page rendering

        Returns:
            Path to generated PDF file

        Raises:
            PDFGeneratorError: If PDF generation fails
        """
        from tactile_core.core.tiler import ImageTiler, TilerConfig

        # Validate output path
        is_valid, error_msg = validate_output_path(output_path)
        if not is_valid:
            raise PDFGeneratorError(error_msg)

        self.logger.generating("Creating multi-page tiled PDF")

        try:
            # Get paper dimensions
            if paper_size not in self.SIZES:
                raise PDFGeneratorError(f"Invalid paper size: {paper_size}")

            page_width, page_height = self.SIZES[paper_size]

            # Auto-detect landscape: if image is wider than tall, use landscape page
            img_w, img_h = image.size
            if img_w > img_h:
                page_width, page_height = page_height, page_width
                self.logger.info(f"Auto-rotated to landscape ({page_width}\" x {page_height}\")")

            page_width_pts = page_width * inch
            page_height_pts = page_height * inch

            # Calculate max dimensions in pixels at 300 DPI
            max_width_px = int(page_width * self.TARGET_DPI)
            max_height_px = int(page_height * self.TARGET_DPI)

            # Create tiler config
            tiler_config = TilerConfig(
                max_width_px=max_width_px,
                max_height_px=max_height_px,
                overlap_percentage=tile_overlap,
                add_registration_marks=add_registration_marks,
                paper_size=paper_size
            )

            # Create tiler and generate tiles
            tiler = ImageTiler(config=tiler_config, logger=self.logger)
            tiles = tiler.tile_image(image, tiler_config)

            # Calculate grid dimensions for assembly instructions
            num_cols, num_rows, _, _ = tiler.calculate_tile_grid(image, tiler_config)

            # Create PDF canvas
            c = canvas.Canvas(output_path, pagesize=(page_width_pts, page_height_pts))

            # Set metadata
            c.setTitle(metadata.get('source_file', 'PIAF Tiled Image') if metadata else 'PIAF Tiled Image')
            c.setAuthor("TACT — Tactile Architectural Conversion Tool")
            c.setSubject("Tiled tactile graphics for PIAF printing")
            c.setCreator("tact")

            # Add abbreviation key page if there are key entries (at the beginning)
            if key_entries:
                self.logger.info(f"Adding abbreviation key page with {len(key_entries)} entries")
                self.add_abbreviation_key_page(c, key_entries, page_width_pts, page_height_pts)
                c.showPage()

            # Add assembly instructions as first page
            self.logger.info("Adding assembly instructions page")
            assembly_text = tiler.create_assembly_instructions(num_rows, num_cols, tile_overlap)
            self.add_text_page(c, assembly_text, page_width_pts, page_height_pts)
            c.showPage()

            # Store original image height for Braille coordinate conversion
            self.image_height = image.size[1]

            # Add each tile as a page
            for idx, (tile, label) in enumerate(tiles, 1):
                self.logger.progress(f"Adding page {idx + 1} of {len(tiles) + 1}: {label}")

                # Convert PIL Image to format reportlab can use
                img_buffer = io.BytesIO()
                tile.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                img_reader = ImageReader(img_buffer)

                # Calculate dimensions
                tile_width_in, tile_height_in = self.calculate_dimensions(tile, self.TARGET_DPI)

                # Center tile on page (leave room for label at bottom)
                label_space = 0.5 * inch
                available_height = page_height - (label_space / inch)

                # Check if tile needs scaling
                scale = 1.0
                if tile_width_in > page_width or tile_height_in > available_height:
                    scale_w = page_width / tile_width_in
                    scale_h = available_height / tile_height_in
                    scale = min(scale_w, scale_h) * 0.95

                tile_width_in *= scale
                tile_height_in *= scale

                # Center horizontally, top-align vertically (with margin)
                x_offset = (page_width - tile_width_in) / 2 * inch
                y_offset = (page_height - tile_height_in - 0.5) * inch

                # Draw tile
                c.drawImage(
                    img_reader,
                    x_offset,
                    y_offset,
                    width=tile_width_in * inch,
                    height=tile_height_in * inch,
                    preserveAspectRatio=True
                )

                # Add tile label at bottom
                self.add_tile_label(c, label, page_width_pts, page_height_pts)

                # New page for next tile
                if idx < len(tiles):
                    c.showPage()

            # Resolve to full absolute path
            full_output_path = resolve_wsl_path(output_path)

            # Save PDF
            c.save()

            # Verify the file was actually created
            file_exists, verified_path = verify_file_exists(full_output_path)
            if file_exists:
                self.logger.success(f"Multi-page PDF saved successfully")
                self.logger.info(f"Output path: {verified_path}")
            else:
                self.logger.warning("PDF save() completed but file verification failed")
                self.logger.warning(f"Expected at: {full_output_path}")

            self.logger.info(f"Total pages: {len(tiles) + 1} (1 instruction page + {len(tiles)} tile pages)")
            self.logger.blank_line()
            self.logger.complete("Tiled output generation finished successfully")
            self.logger.info("Ready to print on PIAF machine")

            return full_output_path

        except PDFGeneratorError:
            raise
        except Exception as e:
            raise PDFGeneratorError(f"Failed to generate tiled PDF: {str(e)}") from e
    def generate_multipage(self, pages_data: List[Tuple[Image.Image, list]], 
                          output_path: str, paper_size: str = "letter",
                          shared_symbol_key: list = None,
                          braille_converter=None) -> str:
        """
        Generate multi-page PDF from list of (processed_image, braille_labels) tuples.
        
        This method is used for combining multiple pages from a multi-page PDF input
        into a single tactile output with shared context (symbol key) across all pages.

        Args:
            pages_data: List of (processed_image, braille_labels) tuples, one per page
            output_path: Path for output PDF
            paper_size: Paper size ('letter' or 'tabloid')
            shared_symbol_key: Optional list of SymbolKeyEntry objects shared across all pages
            braille_converter: Optional BrailleConverter for rendering Braille on key page

        Returns:
            Path to generated PDF file

        Raises:
            PDFGeneratorError: If PDF generation fails
        """
        from tactile_core.utils.validators import validate_output_path, resolve_wsl_path, verify_file_exists
        
        # Validate output path
        is_valid, error_msg = validate_output_path(output_path)
        if not is_valid:
            raise PDFGeneratorError(error_msg)

        self.logger.generating(f"Creating multi-page PDF with {len(pages_data)} pages")

        try:
            # Get paper dimensions
            if paper_size not in self.SIZES:
                raise PDFGeneratorError(f"Invalid paper size: {paper_size}")

            page_width, page_height = self.SIZES[paper_size]

            # Auto-detect landscape from first page: if image is wider than tall, use landscape page
            if pages_data:
                first_img = pages_data[0][0]
                img_w, img_h = first_img.size
                if img_w > img_h:
                    page_width, page_height = page_height, page_width
                    self.logger.info(f"Auto-rotated to landscape ({page_width}\" x {page_height}\")")

            page_width_pts = page_width * inch
            page_height_pts = page_height * inch

            # Create PDF canvas
            c = canvas.Canvas(output_path, pagesize=(page_width_pts, page_height_pts))

            # Set metadata
            c.setTitle("Multi-page PIAF Document")
            c.setAuthor("TACT — Tactile Architectural Conversion Tool")
            c.setSubject("Multi-page tactile graphics for PIAF printing")
            c.setCreator("tact")

            # Process each page
            for page_idx, (processed_image, braille_labels) in enumerate(pages_data, 1):
                self.logger.progress(f"Adding page {page_idx} of {len(pages_data)}")

                # Store image height for coordinate conversion
                self.image_height = processed_image.size[1]

                # Check if image fits
                fits, (img_width, img_height) = self.fits_on_page(
                    processed_image, paper_size, self.TARGET_DPI
                )

                if not fits:
                    # Calculate scaling factor
                    scale_w = page_width / img_width
                    scale_h = page_height / img_height
                    scale = min(scale_w, scale_h) * 0.95  # 5% margin
                    img_width *= scale
                    img_height *= scale

                # Center image on page
                x_offset = (page_width - img_width) / 2 * inch
                y_offset = (page_height - img_height) / 2 * inch

                # Convert PIL Image to format reportlab can use
                img_buffer = io.BytesIO()
                processed_image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                img_reader = ImageReader(img_buffer)

                # Draw image
                c.drawImage(
                    img_reader,
                    x_offset,
                    y_offset,
                    width=img_width * inch,
                    height=img_height * inch,
                    preserveAspectRatio=True
                )

                # Add Braille labels if provided
                if braille_labels:
                    scale_factor = img_width / processed_image.size[0]

                    # Filter labels that would bleed off page edge → abbreviate to key
                    if key_entries is not None and braille_converter:
                        braille_labels, key_entries = self._filter_overflow_labels(
                            braille_labels, key_entries, braille_converter,
                            scale_factor, x_offset, page_width_pts
                        )

                    self._add_braille_labels(c, braille_labels, scale_factor, x_offset, y_offset,
                                            page_width_pts, page_height_pts)

                # Add page number label at bottom
                page_label = f"Page {page_idx} of {len(pages_data)}"
                self.add_tile_label(c, page_label, page_width_pts, page_height_pts)

                # New page for next image (but not after the last one)
                if page_idx < len(pages_data):
                    c.showPage()

            # Add shared symbol key page at the end if provided
            if shared_symbol_key:
                c.showPage()
                self.add_key_page(c, shared_symbol_key, page_width_pts, page_height_pts,
                                 braille_converter)

            # Resolve to full absolute path
            full_output_path = resolve_wsl_path(output_path)

            # Save PDF
            c.save()

            # Verify the file was actually created
            file_exists, verified_path = verify_file_exists(full_output_path)
            if file_exists:
                self.logger.success(f"Multi-page PDF saved successfully")
                self.logger.info(f"Output path: {verified_path}")
            else:
                self.logger.warning("PDF save() completed but file verification failed")
                self.logger.warning(f"Expected at: {full_output_path}")

            total_pages = len(pages_data) + (1 if shared_symbol_key else 0)
            self.logger.info(f"Total pages: {total_pages}")
            self.logger.blank_line()
            self.logger.complete("Multi-page output generation finished successfully")
            self.logger.info("Ready to print on PIAF machine")

            return full_output_path

        except PDFGeneratorError:
            raise
        except Exception as e:
            raise PDFGeneratorError(f"Failed to generate multi-page PDF: {str(e)}") from e

    def generate_text_only_pdf(self, detected_texts: list, output_path: str,
                                paper_size: str = 'letter',
                                page_number: int = 1,
                                image_size: Optional[Tuple[int, int]] = None) -> str:
        """
        Generate PDF with only positioned text (no image background).

        Used for second print pass in sticker workflow - text aligns with
        counter-highlighted areas from the PIAF PDF when paper is reloaded.

        Args:
            detected_texts: List of DetectedText objects with position data
            output_path: Path for output PDF
            paper_size: Paper size ('letter' or 'tabloid')
            page_number: Page number for registration mark
            image_size: Original image size (width, height) in pixels for scaling

        Returns:
            Path to generated PDF file

        Raises:
            PDFGeneratorError: If PDF generation fails
        """
        # Validate output path
        is_valid, error_msg = validate_output_path(output_path)
        if not is_valid:
            raise PDFGeneratorError(error_msg)

        self.logger.generating("Creating text-only PDF for sticker workflow")

        try:
            # Get paper dimensions
            if paper_size not in self.SIZES:
                raise PDFGeneratorError(f"Invalid paper size: {paper_size}")

            page_width, page_height = self.SIZES[paper_size]

            # Auto-detect landscape: if image is wider than tall, use landscape page
            if image_size and image_size[0] > image_size[1]:
                page_width, page_height = page_height, page_width
                self.logger.info(f"Auto-rotated to landscape ({page_width}\" x {page_height}\")")

            page_width_pts = page_width * inch
            page_height_pts = page_height * inch

            # Create PDF canvas
            c = canvas.Canvas(output_path, pagesize=(page_width_pts, page_height_pts))

            # Set metadata
            c.setTitle("Text Layer for Sticker Workflow")
            c.setAuthor("TACT — Tactile Architectural Conversion Tool")
            c.setSubject("Text-only output for second print pass")
            c.setCreator("tact")

            # Calculate scale factor if image size provided
            if image_size:
                img_width_in = image_size[0] / self.TARGET_DPI
                img_height_in = image_size[1] / self.TARGET_DPI

                # Check if scaling needed
                scale = 1.0
                if img_width_in > page_width or img_height_in > page_height:
                    scale_w = page_width / img_width_in
                    scale_h = page_height / img_height_in
                    scale = min(scale_w, scale_h) * 0.95

                img_width_in *= scale
                img_height_in *= scale

                # Calculate offsets for centering (same as image placement)
                x_offset = (page_width - img_width_in) / 2 * inch
                y_offset = (page_height - img_height_in) / 2 * inch
                scale_factor = img_width_in / image_size[0]
            else:
                # Default: assume image fills page at 300 DPI
                x_offset = 0
                y_offset = 0
                scale_factor = 1.0 / self.TARGET_DPI

            # Render each detected text at its original position
            text_count = 0
            for text in detected_texts:
                if not text.text.strip():
                    continue

                # Convert pixel coordinates to PDF points
                # X position: scale from pixels to inches, add offset
                x_pts = text.x * scale_factor * inch + x_offset

                # Y position: PDF origin is bottom-left, image origin is top-left
                # text.y is top of text box, we need baseline position
                if image_size:
                    y_pts = y_offset + (image_size[1] - text.y - text.height) * scale_factor * inch
                else:
                    y_pts = page_height_pts - (text.y + text.height) / self.TARGET_DPI * inch

                # Estimate font size from text height (approximate)
                # At 300 DPI, font height in points = pixel height * 72 / 300
                font_size = max(6, min(24, text.height * 72 / self.TARGET_DPI * scale_factor * self.TARGET_DPI))

                # Set font and draw text
                c.setFont("Helvetica", font_size)
                c.setFillColorRGB(0, 0, 0)

                # Handle rotated text
                rotation = getattr(text, 'rotation_degrees', 0.0)
                if rotation != 0:
                    c.saveState()
                    c.translate(x_pts, y_pts)
                    c.rotate(rotation)
                    c.drawString(0, 0, text.text)
                    c.restoreState()
                else:
                    c.drawString(x_pts, y_pts, text.text)

                text_count += 1

            # Add registration mark in bottom-right corner
            self.add_registration_mark(c, page_width_pts, page_height_pts, page_number)

            # Resolve to full absolute path
            full_output_path = resolve_wsl_path(output_path)

            # Save PDF
            c.save()

            # Verify the file was actually created
            file_exists, verified_path = verify_file_exists(full_output_path)
            if file_exists:
                self.logger.success(f"Text-only PDF saved successfully")
                self.logger.info(f"Output path: {verified_path}")
                self.logger.info(f"Text elements rendered: {text_count}")
            else:
                self.logger.warning("PDF save() completed but file verification failed")
                self.logger.warning(f"Expected at: {full_output_path}")

            return full_output_path

        except PDFGeneratorError:
            raise
        except Exception as e:
            raise PDFGeneratorError(f"Failed to generate text-only PDF: {str(e)}") from e

