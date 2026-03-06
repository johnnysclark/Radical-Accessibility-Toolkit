"""
Image tiling module for handling oversized images.

Splits large images into overlapping tiles for multi-page printing.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import math
from PIL import Image, ImageDraw, ImageFont

from tactile_core.utils.logger import AccessibleLogger


@dataclass
class TilerConfig:
    """
    Configuration for image tiling system.

    Attributes:
        max_width_px: Maximum width in pixels (based on paper size at 300 DPI)
        max_height_px: Maximum height in pixels (based on paper size at 300 DPI)
        overlap_percentage: Overlap between tiles (0.0-1.0, default 0.0 for no overlap)
        add_registration_marks: Whether to add registration marks at tile corners
        registration_mark_size: Size of registration marks in pixels
        paper_size: Paper size name ('letter' or 'tabloid')
    """
    max_width_px: int
    max_height_px: int
    overlap_percentage: float = 0.0
    add_registration_marks: bool = True
    registration_mark_size: int = 30
    paper_size: str = 'letter'


class TilerError(Exception):
    """Custom exception for tiling errors."""
    pass


class ImageTiler:
    """
    Handles splitting large images into printable tiles.

    Features:
    - Automatic detection of oversized images
    - Overlapping tiles for alignment
    - Registration marks for assembly
    - Tile position labels
    - Maintains 300 DPI resolution
    """

    # Paper sizes in pixels at 300 DPI
    PAPER_SIZES_PX = {
        'letter': (2550, 3300),    # 8.5 x 11 inches
        'tabloid': (3300, 5100)    # 11 x 17 inches
    }

    def __init__(self, config: Optional[TilerConfig] = None, logger: Optional[AccessibleLogger] = None):
        """
        Initialize image tiler.

        Args:
            config: Optional TilerConfig instance
            logger: Optional AccessibleLogger instance
        """
        self.config = config
        self.logger = logger or AccessibleLogger(verbose=False)

    def needs_tiling(self, image: Image.Image, paper_size: str = 'letter') -> bool:
        """
        Check if an image needs to be tiled.

        Args:
            image: PIL Image object
            paper_size: Target paper size ('letter' or 'tabloid')

        Returns:
            True if image exceeds paper dimensions
        """
        if paper_size not in self.PAPER_SIZES_PX:
            raise TilerError(f"Invalid paper size: {paper_size}")

        max_width, max_height = self.PAPER_SIZES_PX[paper_size]
        img_width, img_height = image.size

        return img_width > max_width or img_height > max_height

    def calculate_tile_grid(self, image: Image.Image, config: TilerConfig) -> Tuple[int, int, int, int]:
        """
        Calculate the tile grid dimensions.

        Args:
            image: PIL Image object
            config: TilerConfig instance

        Returns:
            Tuple of (num_cols, num_rows, tile_width, tile_height)
        """
        img_width, img_height = image.size
        max_width, max_height = config.max_width_px, config.max_height_px

        # Calculate overlap in pixels
        overlap_width = int(max_width * config.overlap_percentage)
        overlap_height = int(max_height * config.overlap_percentage)

        # Effective tile size (without overlap)
        effective_width = max_width - overlap_width
        effective_height = max_height - overlap_height

        # Calculate number of tiles needed
        num_cols = math.ceil((img_width - overlap_width) / effective_width)
        num_rows = math.ceil((img_height - overlap_height) / effective_height)

        # Actual tile dimensions (with overlap)
        tile_width = max_width
        tile_height = max_height

        return num_cols, num_rows, tile_width, tile_height

    def extract_tile(self, image: Image.Image, row: int, col: int,
                    num_rows: int, num_cols: int,
                    tile_width: int, tile_height: int,
                    overlap_percentage: float) -> Image.Image:
        """
        Extract a single tile from the image.

        Args:
            image: Source PIL Image
            row: Tile row index (0-based)
            col: Tile column index (0-based)
            num_rows: Total number of rows
            num_cols: Total number of columns
            tile_width: Width of each tile
            tile_height: Height of each tile
            overlap_percentage: Overlap percentage

        Returns:
            Tile as PIL Image
        """
        img_width, img_height = image.size

        # Calculate overlap in pixels
        overlap_width = int(tile_width * overlap_percentage)
        overlap_height = int(tile_height * overlap_percentage)

        # Effective tile size (without overlap)
        effective_width = tile_width - overlap_width
        effective_height = tile_height - overlap_height

        # Calculate tile position
        x_start = col * effective_width
        y_start = row * effective_height

        # Calculate tile end position
        x_end = min(x_start + tile_width, img_width)
        y_end = min(y_start + tile_height, img_height)

        # Extract tile
        tile = image.crop((x_start, y_start, x_end, y_end))

        # If tile is smaller than expected (edge tiles), pad with white
        if tile.size[0] < tile_width or tile.size[1] < tile_height:
            # Create white background
            padded = Image.new(image.mode, (tile_width, tile_height),
                              color=1 if image.mode == '1' else 255)
            # Paste tile onto background
            padded.paste(tile, (0, 0))
            tile = padded

        return tile

    def add_registration_marks(self, tile: Image.Image, mark_size: int = 30) -> Image.Image:
        """
        Add registration marks to tile corners for alignment.

        Args:
            tile: PIL Image (1-bit B&W)
            mark_size: Size of registration marks in pixels

        Returns:
            Tile with registration marks
        """
        # Convert to RGB for drawing, then back to original mode
        if tile.mode == '1':
            tile_rgb = tile.convert('L')
        else:
            tile_rgb = tile.copy()

        draw = ImageDraw.Draw(tile_rgb)
        width, height = tile.size

        # Define registration mark positions (small corner marks)
        corners = [
            (10, 10),                          # Top-left
            (width - mark_size - 10, 10),      # Top-right
            (10, height - mark_size - 10),     # Bottom-left
            (width - mark_size - 10, height - mark_size - 10)  # Bottom-right
        ]

        # Draw crosshair marks at each corner
        for x, y in corners:
            # Horizontal line
            draw.line([(x, y + mark_size // 2),
                      (x + mark_size, y + mark_size // 2)],
                     fill=0, width=2)
            # Vertical line
            draw.line([(x + mark_size // 2, y),
                      (x + mark_size // 2, y + mark_size)],
                     fill=0, width=2)
            # Small circle in center
            center_x = x + mark_size // 2
            center_y = y + mark_size // 2
            radius = 3
            draw.ellipse([(center_x - radius, center_y - radius),
                         (center_x + radius, center_y + radius)],
                        fill=0, outline=0)

        # Convert back to original mode
        if tile.mode == '1':
            tile_rgb = tile_rgb.convert('1')

        return tile_rgb

    def generate_tile_label(self, row: int, col: int,
                          num_rows: int, num_cols: int) -> str:
        """
        Generate a descriptive label for a tile.

        Args:
            row: Tile row index (0-based)
            col: Tile column index (0-based)
            num_rows: Total number of rows
            num_cols: Total number of columns

        Returns:
            Tile label string
        """
        tile_num = row * num_cols + col + 1
        total_tiles = num_rows * num_cols

        return f"Tile {tile_num} of {total_tiles} - Row {row + 1}, Column {col + 1}"

    def tile_image(self, image: Image.Image, config: TilerConfig) -> List[Tuple[Image.Image, str]]:
        """
        Split image into tiles.

        Args:
            image: Source PIL Image (B&W)
            config: TilerConfig instance

        Returns:
            List of (tile_image, tile_label) tuples
        """
        # Calculate grid
        num_cols, num_rows, tile_width, tile_height = self.calculate_tile_grid(image, config)
        total_tiles = num_rows * num_cols

        self.logger.info(
            f"Tiling: Image requires {total_tiles} tiles "
            f"({num_rows} rows x {num_cols} columns)"
        )
        self.logger.info(f"Overlap: {int(config.overlap_percentage * 100)}%")

        tiles = []

        # Extract each tile
        for row in range(num_rows):
            for col in range(num_cols):
                # Extract tile
                tile = self.extract_tile(
                    image, row, col, num_rows, num_cols,
                    tile_width, tile_height, config.overlap_percentage
                )

                # Add registration marks if enabled
                if config.add_registration_marks:
                    tile = self.add_registration_marks(tile, config.registration_mark_size)

                # Generate label
                label = self.generate_tile_label(row, col, num_rows, num_cols)

                tiles.append((tile, label))

                self.logger.info(f"  Created: {label}")

        return tiles

    def create_assembly_instructions(self, num_rows: int, num_cols: int,
                                    overlap_percentage: float) -> str:
        """
        Generate assembly instructions for tiled output.

        Args:
            num_rows: Number of tile rows
            num_cols: Number of tile columns
            overlap_percentage: Overlap percentage

        Returns:
            Assembly instructions as string
        """
        total_tiles = num_rows * num_cols
        overlap_pct = int(overlap_percentage * 100)

        instructions = f"""Assembly Instructions for Tiled Output

Total Tiles: {total_tiles} ({num_rows} rows x {num_cols} columns)
Overlap: {overlap_pct}%

Assembly Steps:
1. Print all {total_tiles} pages on tactile paper
2. Arrange tiles in a {num_rows}x{num_cols} grid:
   - Row 1 (top): Tiles 1-{num_cols}
   - Row 2: Tiles {num_cols + 1}-{num_cols * 2}
   {'   - Row ' + str(num_rows) + ' (bottom): Tiles ' + str((num_rows - 1) * num_cols + 1) + '-' + str(total_tiles) if num_rows > 2 else ''}
3. Align tiles using the registration marks (crosshairs) at corners
4. Each tile overlaps by {overlap_pct}% with adjacent tiles
5. Tape or secure tiles together from the back
6. The overlap area helps ensure continuous tactile lines

Note: Registration marks are located approximately 10 pixels from each corner.
Align these marks carefully for best results.
"""
        return instructions
