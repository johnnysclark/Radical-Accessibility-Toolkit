"""
Grid Overlay Module

Provides grid overlay functionality for architectural images to help Claude
reference specific locations using cell labels (e.g., "A1", "B3", "C4")
instead of estimating percentages.

The grid overlay enables more precise text positioning by giving Claude
visual reference points to locate text elements.
"""

from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger("tactile.grid")


def calculate_grid_density(width: int, height: int) -> Tuple[int, int]:
    """
    Calculate adaptive grid density based on image dimensions.

    Larger images get denser grids to maintain useful cell sizes.
    Base: 10x10 for small images (< 1000px)
    Scale up for larger images (max 30x30)

    Args:
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Tuple of (rows, cols) for the grid
    """
    base_size = 100  # pixels per cell minimum

    # Calculate based on dimensions
    cols = max(10, min(30, width // base_size))
    rows = max(10, min(30, height // base_size))

    return rows, cols


def create_grid_overlay(
    image: Image.Image,
    rows: Optional[int] = None,
    cols: Optional[int] = None
) -> Tuple[Image.Image, int, int]:
    """
    Create a copy of the image with grid overlay and cell labels.

    The grid divides the image into cells labeled with alphanumeric
    references (A1, A2, ... B1, B2, etc.) similar to a spreadsheet.
    Row letters go A-Z (or beyond for large grids), columns are numbered.

    Args:
        image: Source PIL Image
        rows: Number of rows (optional, auto-calculated if None)
        cols: Number of columns (optional, auto-calculated if None)

    Returns:
        Tuple of (image_with_grid, rows, cols)
    """
    # Create a copy to avoid modifying original
    img_copy = image.copy().convert("RGB")
    draw = ImageDraw.Draw(img_copy)
    width, height = img_copy.size

    # Calculate grid density if not specified
    if rows is None or cols is None:
        rows, cols = calculate_grid_density(width, height)

    cell_width = width / cols
    cell_height = height / rows

    # Grid line styling
    line_color = (255, 0, 0)  # Red for visibility
    line_width = 2 if max(width, height) > 2000 else 1

    # Draw vertical grid lines
    for i in range(1, cols):
        x = int(i * cell_width)
        draw.line([(x, 0), (x, height)], fill=line_color, width=line_width)

    # Draw horizontal grid lines
    for i in range(1, rows):
        y = int(i * cell_height)
        draw.line([(0, y), (width, y)], fill=line_color, width=line_width)

    # Draw border
    draw.rectangle([(0, 0), (width - 1, height - 1)], outline=line_color, width=line_width)

    # Try to load a font, fall back to default
    try:
        # Try to find a suitable font size based on cell dimensions
        font_size = max(8, min(16, int(min(cell_width, cell_height) / 6)))
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except (OSError, IOError):
            font = ImageFont.load_default()

    # Label each cell with its reference (A1, A2, B1, etc.)
    for row in range(rows):
        for col in range(cols):
            # Generate cell label
            label = _get_cell_label(row, col)

            # Calculate position (top-left corner of cell with small offset)
            x = int(col * cell_width + 3)
            y = int(row * cell_height + 2)

            # Draw label with a semi-transparent background for readability
            bbox = draw.textbbox((x, y), label, font=font)
            padding = 2
            draw.rectangle(
                [bbox[0] - padding, bbox[1] - padding,
                 bbox[2] + padding, bbox[3] + padding],
                fill=(255, 255, 255, 200)  # White background
            )
            draw.text((x, y), label, fill=line_color, font=font)

    logger.debug(f"Created grid overlay: {rows}x{cols} cells on {width}x{height} image")

    return img_copy, rows, cols


def _get_cell_label(row: int, col: int) -> str:
    """
    Generate cell label from row and column indices.

    Uses Excel-style notation: A1, B2, etc.
    For rows beyond 26, uses AA, AB, etc.

    Args:
        row: 0-based row index
        col: 0-based column index

    Returns:
        Cell label string (e.g., "A1", "B3", "AA15")
    """
    # Convert row index to letter(s)
    row_label = ""
    r = row
    while True:
        row_label = chr(ord("A") + (r % 26)) + row_label
        r = r // 26 - 1
        if r < 0:
            break

    # Column is 1-indexed for display
    col_label = str(col + 1)

    return f"{row_label}{col_label}"


def grid_cell_to_percent(
    cell: str,
    rows: int,
    cols: int
) -> Tuple[float, float]:
    """
    Convert a cell reference to x_percent, y_percent at cell center.

    Args:
        cell: Cell reference string (e.g., "B3", "AA15")
        rows: Total number of rows in the grid
        cols: Total number of columns in the grid

    Returns:
        Tuple of (x_percent, y_percent) at center of the cell

    Raises:
        ValueError: If cell reference format is invalid
    """
    # Parse the cell reference
    row_idx, col_idx = _parse_cell_reference(cell)

    # Validate indices
    if row_idx < 0 or row_idx >= rows:
        raise ValueError(f"Row index {row_idx} out of range for {rows} rows")
    if col_idx < 0 or col_idx >= cols:
        raise ValueError(f"Column index {col_idx} out of range for {cols} columns")

    # Calculate center of cell as percentage
    x_percent = (col_idx + 0.5) * (100.0 / cols)
    y_percent = (row_idx + 0.5) * (100.0 / rows)

    return x_percent, y_percent


def _parse_cell_reference(cell: str) -> Tuple[int, int]:
    """
    Parse a cell reference string into row and column indices.

    Args:
        cell: Cell reference string (e.g., "B3", "AA15")

    Returns:
        Tuple of (row_index, column_index), 0-based

    Raises:
        ValueError: If cell reference format is invalid
    """
    cell = cell.upper().strip()

    if not cell:
        raise ValueError("Empty cell reference")

    # Find where letters end and numbers begin
    letter_part = ""
    number_part = ""

    for char in cell:
        if char.isalpha():
            if number_part:
                # Letters after numbers - invalid format
                raise ValueError(f"Invalid cell reference format: {cell}")
            letter_part += char
        elif char.isdigit():
            number_part += char
        else:
            raise ValueError(f"Invalid character in cell reference: {char}")

    if not letter_part:
        raise ValueError(f"Cell reference must start with letters: {cell}")
    if not number_part:
        raise ValueError(f"Cell reference must end with numbers: {cell}")

    # Convert letter part to row index (A=0, B=1, ... Z=25, AA=26, etc.)
    row_idx = 0
    for char in letter_part:
        row_idx = row_idx * 26 + (ord(char) - ord("A") + 1)
    row_idx -= 1  # Convert to 0-based

    # Convert number part to column index (1=0, 2=1, etc.)
    col_idx = int(number_part) - 1

    return row_idx, col_idx


def grid_cell_to_pixels(
    cell: str,
    rows: int,
    cols: int,
    image_width: int,
    image_height: int
) -> Tuple[int, int]:
    """
    Convert a cell reference to pixel coordinates at cell center.

    Args:
        cell: Cell reference string (e.g., "B3")
        rows: Total number of rows in the grid
        cols: Total number of columns in the grid
        image_width: Image width in pixels
        image_height: Image height in pixels

    Returns:
        Tuple of (x_pixels, y_pixels) at center of the cell
    """
    x_percent, y_percent = grid_cell_to_percent(cell, rows, cols)

    x_pixels = int(x_percent / 100.0 * image_width)
    y_pixels = int(y_percent / 100.0 * image_height)

    return x_pixels, y_pixels


def get_grid_cell_bounds(
    cell: str,
    rows: int,
    cols: int,
    image_width: int,
    image_height: int
) -> Tuple[int, int, int, int]:
    """
    Get the bounding box of a grid cell in pixel coordinates.

    Args:
        cell: Cell reference string (e.g., "B3")
        rows: Total number of rows in the grid
        cols: Total number of columns in the grid
        image_width: Image width in pixels
        image_height: Image height in pixels

    Returns:
        Tuple of (x1, y1, x2, y2) representing the cell bounding box
    """
    row_idx, col_idx = _parse_cell_reference(cell)

    cell_width = image_width / cols
    cell_height = image_height / rows

    x1 = int(col_idx * cell_width)
    y1 = int(row_idx * cell_height)
    x2 = int((col_idx + 1) * cell_width)
    y2 = int((row_idx + 1) * cell_height)

    return x1, y1, x2, y2
