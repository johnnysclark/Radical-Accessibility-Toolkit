"""
Braille conversion module for generating Unicode Braille labels.

Converts text to Braille using Liblouis library and positions labels
for PDF rendering on tactile graphics.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

from tactile_core.utils.logger import AccessibleLogger

# Braille rendering constants (at 300 DPI)
BRAILLE_DPI = 300
BRAILLE_FONT_SIZE_POINTS = 24  # BANA standard: 6.2mm cell-to-cell
BRAILLE_FONT_SIZE_PX = BRAILLE_FONT_SIZE_POINTS * (BRAILLE_DPI / 72)  # ~100 px
BRAILLE_CHAR_WIDTH_PX = BRAILLE_FONT_SIZE_PX * 0.6  # ~60 pixels per character

__all__ = [
    'BrailleConversionError',
    'BrailleConfig',
    'DetectedText',
    'BrailleLabel',
    'SymbolKeyEntry',
    'KeyEntry',
    'BrailleConverter',
    'BRAILLE_DPI',
    'BRAILLE_FONT_SIZE_POINTS',
    'BRAILLE_FONT_SIZE_PX',
    'BRAILLE_CHAR_WIDTH_PX',
]


class BrailleConversionError(Exception):
    """Custom exception for Braille conversion errors."""
    pass


@dataclass
class BrailleConfig:
    """
    Configuration for Braille conversion settings.

    Attributes:
        enabled: Whether Braille conversion is enabled
        grade: Braille grade (1 = Grade 1/uncontracted, 2 = Grade 2/contracted)
        font_name: Font name for rendering Braille (must support Unicode Braille)
        font_size: Font size in points
        placement: Label placement strategy ('overlay' or 'margin')
        offset_x: Horizontal offset from original text in pixels
        offset_y: Vertical offset from original text in pixels (negative = above)
        max_label_length: Maximum characters per Braille label
        truncate_suffix: Suffix to add when truncating long labels
        font_color: Color for Braille text
        detect_overlaps: Whether to check for overlapping labels
        min_label_spacing: Minimum pixels between labels
    """
    enabled: bool = False
    grade: int = 1
    font_name: str = "DejaVu Sans"
    font_size: int = 24
    placement: str = "overlay"
    offset_x: int = 5
    offset_y: int = -24
    max_label_length: int = 30
    truncate_suffix: str = "..."
    font_color: str = "black"
    detect_overlaps: bool = True
    min_label_spacing: int = 6
    use_symbols_for_overlaps: bool = True  # Replace overlapping labels with symbols instead of skipping


@dataclass
class DetectedText:
    """
    Container for detected text with position information.

    This is a placeholder for text detection functionality that would
    come from OCR or text extraction modules.

    Attributes:
        text: The detected text string
        x: X coordinate (left position) in pixels
        y: Y coordinate (top position) in pixels
        width: Width of text bounding box in pixels
        height: Height of text bounding box in pixels
    """
    text: str
    x: int
    y: int
    width: int = 0
    height: int = 0


@dataclass
class BrailleLabel:
    """
    Container for Braille text with placement information.

    Attributes:
        braille_text: Unicode Braille string
        x: X coordinate for label placement in pixels
        y: Y coordinate for label placement in pixels
        original_text: Original text before Braille conversion
        width: Estimated width of Braille label in pixels (optional)
        rotation_degrees: Rotation angle for the label (0=horizontal, 90=clockwise, -90=counter-clockwise)
    """
    braille_text: str
    x: int
    y: int
    original_text: str
    width: Optional[int] = None
    rotation_degrees: float = 0.0  # 0=horizontal, 90=rotated clockwise, -90=counter-clockwise


@dataclass
class SymbolKeyEntry:
    """
    Entry for the symbol-to-text key page.

    When labels overlap and can't be repositioned, they are replaced
    with symbols (a, b, c, etc.) and this entry tracks the mapping.

    Attributes:
        symbol: The symbol used (e.g., "a", "b", "c")
        original_text: The full original text that was replaced
        x: Original x position (for reference)
        y: Original y position (for reference)
    """
    symbol: str
    original_text: str
    x: int
    y: int


@dataclass
class KeyEntry:
    """Entry for the abbreviation key."""
    letter: str          # "A", "B", etc.
    original_text: str   # "Kitchen"
    braille_full: str    # Full Braille translation "⠠⠅⠊⠞⠉⠓⠑⠝"


class BrailleConverter:
    """
    Convert text to Braille using Liblouis library.

    Supports Grade 1 and Grade 2 Braille with Unicode output suitable
    for rendering in PDFs with Braille-compatible fonts.

    Features:
    - Grade 1 (uncontracted) and Grade 2 (contracted) Braille
    - Unicode Braille output (U+2800 to U+28FF range)
    - Position calculation with configurable offsets
    - Label truncation for long text
    - Basic overlap detection
    """

    # Braille translation tables for Liblouis
    BRAILLE_TABLES = {
        1: "en-us-g1.ctb",  # Grade 1 Braille (uncontracted)
        2: "en-us-g2.ctb"   # Grade 2 Braille (contracted)
    }

    # Simple ASCII to Unicode Braille mapping for fallback (Grade 1 approximation)
    # Maps common characters to their Unicode Braille equivalents
    ASCII_TO_BRAILLE = {
        'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋', 'g': '⠛',
        'h': '⠓', 'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇', 'm': '⠍', 'n': '⠝',
        'o': '⠕', 'p': '⠏', 'q': '⠟', 'r': '⠗', 's': '⠎', 't': '⠞', 'u': '⠥',
        'v': '⠧', 'w': '⠺', 'x': '⠭', 'y': '⠽', 'z': '⠵',
        '0': '⠚', '1': '⠁', '2': '⠃', '3': '⠉', '4': '⠙', '5': '⠑',
        '6': '⠋', '7': '⠛', '8': '⠓', '9': '⠊',
        ' ': ' ', '.': '⠲', ',': '⠂', '?': '⠦', '!': '⠖', '-': '⠤',
        "'": '⠄', '"': '⠦', '(': '⠐⠣', ')': '⠐⠜', '/': '⠌',
        '+': '⠖', '=': '⠶', ':': '⠒', ';': '⠆', '@': '⠈⠁',
    }

    def __init__(self, config: BrailleConfig, logger: AccessibleLogger):
        """
        Initialize Braille converter.

        Args:
            config: BrailleConfig instance with conversion settings
            logger: AccessibleLogger instance for status messages

        Raises:
            BrailleConversionError: If Liblouis is not installed
        """
        self.config = config
        self.logger = logger
        self._validate_liblouis_installation()

        # Import louis after validation only if not using fallback
        if not self.use_fallback:
            import louis
            self.louis = louis
        else:
            self.louis = None

        # Validate grade setting
        if config.grade not in self.BRAILLE_TABLES:
            raise BrailleConversionError(
                f"Invalid Braille grade: {config.grade}. Must be 1 or 2."
            )

        if self.use_fallback:
            self.logger.info(f"Braille converter initialized with fallback: Grade {config.grade} (Grade 2 not supported in fallback)")
        else:
            self.logger.info(f"Braille converter initialized: Grade {config.grade}")

    def _validate_liblouis_installation(self):
        """
        Check if Liblouis is properly installed.

        Falls back to simple ASCII-to-Braille converter if not available.

        Raises:
            BrailleConversionError: If Liblouis is not available
        """
        try:
            import louis
            # Verify it's the real liblouis by checking for translateString method
            if not hasattr(louis, 'translateString'):
                self.logger.warning("Liblouis package found but appears to be incorrect version")
                self.logger.info("Using fallback ASCII-to-Braille converter")
                self.use_fallback = True
            else:
                self.use_fallback = False
        except (ImportError, AttributeError):
            self.logger.warning("Liblouis not installed. Using fallback ASCII-to-Braille converter")
            self.logger.info("For full Braille support, install liblouis: sudo apt-get install liblouis-dev python3-louis")
            self.use_fallback = True

    def _convert_text_fallback(self, text: str) -> str:
        """
        Simple fallback ASCII-to-Braille converter.

        This is a basic character-by-character mapping for when liblouis is not available.
        Does not support Grade 2 Braille contractions.

        Args:
            text: Plain text to convert

        Returns:
            Unicode Braille string
        """
        result = []
        text_lower = text.lower()

        for char in text_lower:
            if char in self.ASCII_TO_BRAILLE:
                result.append(self.ASCII_TO_BRAILLE[char])
            else:
                # For unknown characters, keep them as-is or use a placeholder
                result.append(char)

        return ''.join(result)

    def convert_text(self, text: str) -> str:
        """
        Convert text to Braille using Liblouis or fallback converter.

        Args:
            text: Plain text to convert

        Returns:
            Unicode Braille string

        Raises:
            BrailleConversionError: If conversion fails
        """
        if not text or not text.strip():
            return ""

        # Use fallback if liblouis is not available
        if self.use_fallback:
            return self._convert_text_fallback(text)

        try:
            # Get appropriate translation table
            table = self.BRAILLE_TABLES[self.config.grade]

            # Translate to Braille using Liblouis
            # Use dotsIO | ucBrl mode to get Unicode Braille output (U+2800-U+28FF range)
            # louis.translate returns (braille_string, inpos, outpos, cursor) tuple
            mode = self.louis.dotsIO | self.louis.ucBrl
            result = self.louis.translate([table], text, mode=mode)
            braille_output = result[0]  # Extract Unicode Braille string

            return braille_output

        except Exception as e:
            self.logger.warning(f"Failed to convert text to Braille: {text[:20]}...")
            # Try fallback on error
            self.logger.info("Attempting fallback conversion")
            try:
                return self._convert_text_fallback(text)
            except:
                raise BrailleConversionError(
                    f"Braille conversion failed: {str(e)}"
                ) from e

    def _truncate_text(self, text: str) -> str:
        """
        Truncate text to maximum label length.

        Args:
            text: Text to truncate

        Returns:
            Truncated text with suffix if needed
        """
        max_len = self.config.max_label_length

        if len(text) <= max_len:
            return text

        # Reserve space for suffix
        suffix_len = len(self.config.truncate_suffix)
        truncate_at = max_len - suffix_len

        return text[:truncate_at] + self.config.truncate_suffix

    def _calculate_label_position(self, detected: DetectedText) -> tuple:
        """
        Calculate label position based on detected text location and offsets.

        Args:
            detected: DetectedText object with position information

        Returns:
            Tuple of (x, y) coordinates for label
        """
        label_x = detected.x + self.config.offset_x
        label_y = detected.y + self.config.offset_y

        # Ensure coordinates are non-negative
        label_x = max(0, label_x)
        label_y = max(0, label_y)

        return label_x, label_y

    def _estimate_label_width(self, braille_text: str) -> int:
        """
        Estimate the width of a Braille label in pixels.

        This is a rough estimate based on character count and font size.
        Font size is in points, so we convert to pixels at 300 DPI.

        Args:
            braille_text: Unicode Braille string

        Returns:
            Estimated width in pixels
        """
        # Convert font size from points to pixels at 300 DPI
        font_size_px = self.config.font_size * (BRAILLE_DPI / 72)

        # Approximate: each Braille character is roughly 0.6 * font_size wide
        char_width = font_size_px * 0.6
        return int(len(braille_text) * char_width)

    def _get_next_symbol(self, index: int) -> str:
        """
        Generate a symbol for labeling overlapping text.

        Symbols are lowercase letters: a, b, c, ..., z, aa, ab, ...

        Args:
            index: Zero-based index of the symbol to generate

        Returns:
            Symbol string (e.g., "a", "b", "aa", "ab")
        """
        if index < 26:
            return chr(ord('a') + index)
        else:
            # For > 26 overlaps, use aa, ab, ac, etc.
            first = chr(ord('a') + (index // 26) - 1)
            second = chr(ord('a') + (index % 26))
            return first + second

    def _get_next_key_letter(self, index: int) -> str:
        """
        Convert index to letter(s): 0->A, 25->Z, 26->AA, 27->AB, etc.

        Args:
            index: Zero-based index of the letter to generate

        Returns:
            Letter string (e.g., "A", "B", "Z", "AA", "AB")
        """
        if index < 26:
            return chr(ord('A') + index)
        else:
            # For > 26, use AA, AB, AC, etc.
            first = chr(ord('A') + (index // 26) - 1)
            second = chr(ord('A') + (index % 26))
            return first + second

    def _would_overlap(self, box: tuple, placed_boxes: list) -> bool:
        """
        Check if a bounding box would overlap with any placed boxes.

        Args:
            box: Tuple of (x, y, width, height) for the new label
            placed_boxes: List of (x, y, width, height) tuples for placed labels

        Returns:
            True if overlap detected, False otherwise
        """
        if not placed_boxes:
            return False

        x, y, width, height = box
        spacing = self.config.min_label_spacing

        for px, py, pw, ph in placed_boxes:
            # Check for bounding box overlap with spacing
            horizontal_overlap = not (
                x + width + spacing < px or
                x > px + pw + spacing
            )
            vertical_overlap = not (
                y + height + spacing < py or
                y > py + ph + spacing
            )

            if horizontal_overlap and vertical_overlap:
                return True

        return False

    def _find_clear_position(self, label: BrailleLabel, placed_boxes: list,
                             spacing: int = 10) -> Optional[tuple]:
        """
        Find a non-overlapping position for a label.

        Tries original position first, then below, above, right, left.

        Args:
            label: BrailleLabel to position
            placed_boxes: List of (x, y, width, height) tuples for placed labels
            spacing: Pixels of space to leave between repositioned labels

        Returns:
            Tuple of (x, y) for clear position, or None if no clear position found
        """
        # Get label dimensions
        width = label.width or self._estimate_label_width(label.braille_text)

        # Convert font size from points to pixels at 300 DPI for height
        height = int(self.config.font_size * (BRAILLE_DPI / 72))

        # Try original position first
        original_box = (label.x, label.y, width, height)
        if not self._would_overlap(original_box, placed_boxes):
            return label.x, label.y

        # Try repositioning: below, above, right, left
        offsets = [
            (0, height + spacing),      # below
            (0, -(height + spacing)),   # above
            (width + spacing, 0),       # right
            (-(width + spacing), 0),    # left
        ]

        for dx, dy in offsets:
            new_x = max(0, label.x + dx)
            new_y = max(0, label.y + dy)
            new_box = (new_x, new_y, width, height)

            if not self._would_overlap(new_box, placed_boxes):
                return new_x, new_y

        # No clear position found
        return None

    def _check_overlap(self, label: BrailleLabel, existing_labels: List[BrailleLabel]) -> bool:
        """
        Check if a label overlaps with existing labels.

        This is a basic check using bounding boxes.

        Args:
            label: BrailleLabel to check
            existing_labels: List of existing BrailleLabel objects

        Returns:
            True if overlap is detected, False otherwise
        """
        if not self.config.detect_overlaps or not existing_labels:
            return False

        if label.width is None:
            return False

        # Convert font size from points to pixels at 300 DPI for height calculation
        font_size_px = self.config.font_size * (BRAILLE_DPI / 72)

        label_right = label.x + label.width
        label_bottom = label.y + font_size_px

        for existing in existing_labels:
            if existing.width is None:
                continue

            existing_right = existing.x + existing.width
            existing_bottom = existing.y + font_size_px

            # Check for bounding box overlap with spacing
            spacing = self.config.min_label_spacing

            # Check horizontal overlap
            horizontal_overlap = not (
                label_right + spacing < existing.x or
                label.x > existing_right + spacing
            )

            # Check vertical overlap
            vertical_overlap = not (
                label_bottom + spacing < existing.y or
                label.y > existing_bottom + spacing
            )

            if horizontal_overlap and vertical_overlap:
                return True

        return False

    def create_braille_labels(
        self,
        detected_texts: List[DetectedText],
        generate_key: bool = False,
        detected_text_widths: Optional[Dict[str, int]] = None,
        image_size: Optional[Tuple[int, int]] = None
    ) -> Union[Tuple[List[BrailleLabel], List[SymbolKeyEntry]], Tuple[List[BrailleLabel], List[KeyEntry]]]:
        """
        Convert detected texts to positioned Braille labels.

        Labels are automatically repositioned to avoid overlaps when possible.
        When repositioning fails and use_symbols_for_overlaps is enabled,
        overlapping labels are replaced with symbols (a, b, c, etc.) and
        tracked in a separate key list.

        When generate_key=True, labels that don't fit in their original bounding
        box are abbreviated to letters (A, B, C, ...) and a key is generated
        mapping letters to original text.

        Args:
            detected_texts: List of DetectedText objects from text detection
            generate_key: If True, generate abbreviation key for labels that don't fit
            detected_text_widths: Optional dict mapping text to original bounding box width
            image_size: Optional (width, height) in pixels. When provided with generate_key,
                        labels that would extend past the image edge are abbreviated.

        Returns:
            When generate_key=False:
                Tuple of (braille_labels, symbol_key_entries):
                    - braille_labels: List of BrailleLabel objects ready for PDF rendering
                    - symbol_key_entries: List of SymbolKeyEntry objects for the key page
            When generate_key=True:
                Tuple of (braille_labels, key_entries):
                    - braille_labels: List of BrailleLabel objects ready for PDF rendering
                    - key_entries: List of KeyEntry objects for the abbreviation key
        """
        if not detected_texts:
            self.logger.info("No text detected for Braille conversion")
            if generate_key:
                return [], []
            return [], []

        self.logger.progress(f"Converting {len(detected_texts)} text items to Braille")

        braille_labels = []
        symbol_key_entries = []  # Track symbols for overlapping labels
        key_entries = []  # Track abbreviation key entries when generate_key=True
        placed_boxes = []  # Track (x, y, width, height) of placed labels
        skipped_count = 0
        repositioned_count = 0
        symbol_count = 0
        key_letter_index = 0  # Track next letter for key generation

        # Convert font size from points to pixels for height calculation
        label_height = int(self.config.font_size * (BRAILLE_DPI / 72))

        for detected in detected_texts:
            # Truncate long text
            truncated_text = self._truncate_text(detected.text)

            # Convert to Braille
            try:
                braille_text = self.convert_text(truncated_text)

                if not braille_text:
                    skipped_count += 1
                    continue

                # Calculate initial label position
                label_x, label_y = self._calculate_label_position(detected)

                # Estimate label width
                label_width = self._estimate_label_width(braille_text)

                # Get rotation from detected text (default to 0 if not present)
                rotation = getattr(detected, 'rotation_degrees', 0.0)

                # Handle key generation if enabled
                final_braille_text = braille_text
                final_original_text = detected.text
                final_label_width = label_width

                if generate_key:
                    needs_abbreviation = False

                    # Check 1: Braille text wider than original bounding box
                    original_width = None
                    if detected_text_widths and detected.text in detected_text_widths:
                        original_width = detected_text_widths[detected.text]
                    elif detected.width > 0:
                        original_width = detected.width

                    if original_width is not None:
                        braille_width = len(braille_text) * BRAILLE_CHAR_WIDTH_PX
                        if braille_width > original_width:
                            needs_abbreviation = True

                    # Check 2: Label would bleed past image edge
                    if not needs_abbreviation and image_size is not None:
                        img_w, img_h = image_size
                        if label_x + label_width > img_w or label_y + label_height > img_h:
                            needs_abbreviation = True

                    if needs_abbreviation:
                        # Braille doesn't fit - use abbreviation letter
                        letter = self._get_next_key_letter(key_letter_index)
                        key_letter_index += 1

                        # Convert letter to Braille (with capital indicator)
                        letter_braille = self.convert_text(letter)

                        # Create key entry
                        key_entries.append(KeyEntry(
                            letter=letter,
                            original_text=detected.text,
                            braille_full=braille_text
                        ))

                        # Use abbreviated label
                        final_braille_text = letter_braille
                        final_original_text = letter
                        final_label_width = self._estimate_label_width(letter_braille)

                        self.logger.info(
                            f"Using key letter '{letter}' for: {detected.text[:20]}..."
                        )

                # Create initial label
                label = BrailleLabel(
                    braille_text=final_braille_text,
                    x=label_x,
                    y=label_y,
                    original_text=final_original_text,
                    width=final_label_width,
                    rotation_degrees=rotation
                )

                # Find clear position (may reposition if needed)
                if self.config.detect_overlaps:
                    position = self._find_clear_position(label, placed_boxes)

                    if position is None:
                        # No clear position found - use symbol if enabled
                        if self.config.use_symbols_for_overlaps:
                            symbol = self._get_next_symbol(symbol_count)
                            symbol_count += 1

                            # Convert symbol to Braille
                            symbol_braille = self.convert_text(symbol)

                            # Create symbol label at original position
                            # Symbols are small, so they should fit
                            # Note: Symbols are always rendered horizontally (rotation=0)
                            symbol_label = BrailleLabel(
                                braille_text=symbol_braille,
                                x=label_x,
                                y=label_y,
                                original_text=symbol,  # Store symbol as original for reference
                                width=self._estimate_label_width(symbol_braille),
                                rotation_degrees=0.0  # Symbols always horizontal
                            )

                            # Track the symbol mapping
                            symbol_key_entries.append(SymbolKeyEntry(
                                symbol=symbol,
                                original_text=detected.text,
                                x=detected.x,
                                y=detected.y
                            ))

                            # Add symbol label and track placement
                            braille_labels.append(symbol_label)
                            placed_boxes.append((symbol_label.x, symbol_label.y,
                                               symbol_label.width, label_height))

                            self.logger.info(
                                f"Using symbol '{symbol}' for: {detected.text[:20]}..."
                            )
                        else:
                            self.logger.info(
                                f"No clear position found, skipping: {detected.text[:20]}..."
                            )
                            skipped_count += 1
                        continue

                    # Check if label was repositioned
                    if position != (label_x, label_y):
                        repositioned_count += 1
                        label.x, label.y = position
                else:
                    position = (label_x, label_y)

                # Add to results and track placement
                braille_labels.append(label)
                placed_boxes.append((label.x, label.y, final_label_width, label_height))

            except BrailleConversionError as e:
                self.logger.warning(f"Skipping text due to conversion error: {str(e)}")
                skipped_count += 1
                continue

        self.logger.success(
            f"Created {len(braille_labels)} Braille labels "
            f"(Grade {self.config.grade})"
        )

        if repositioned_count > 0:
            self.logger.info(f"Repositioned {repositioned_count} labels to avoid overlaps")

        if symbol_count > 0:
            self.logger.info(f"Used {symbol_count} symbols for overlapping labels (see key page)")

        if len(key_entries) > 0:
            self.logger.info(f"Generated {len(key_entries)} key entries for abbreviated labels")

        if skipped_count > 0:
            self.logger.info(f"Skipped {skipped_count} items (conversion errors)")

        if generate_key:
            return braille_labels, key_entries
        return braille_labels, symbol_key_entries

    def create_braille_label_from_text(self, text: str, x: int, y: int) -> Optional[BrailleLabel]:
        """
        Create a single Braille label from text and position.

        This is a convenience method for creating individual labels
        without the full DetectedText structure.

        Args:
            text: Text to convert to Braille
            x: X coordinate for label
            y: Y coordinate for label

        Returns:
            BrailleLabel object or None if conversion fails
        """
        if not text or not text.strip():
            return None

        try:
            # Truncate and convert
            truncated_text = self._truncate_text(text)
            braille_text = self.convert_text(truncated_text)

            if not braille_text:
                return None

            # Apply offsets
            label_x = x + self.config.offset_x
            label_y = y + self.config.offset_y

            # Estimate width
            label_width = self._estimate_label_width(braille_text)

            return BrailleLabel(
                braille_text=braille_text,
                x=max(0, label_x),
                y=max(0, label_y),
                original_text=text,
                width=label_width
            )

        except BrailleConversionError:
            return None
