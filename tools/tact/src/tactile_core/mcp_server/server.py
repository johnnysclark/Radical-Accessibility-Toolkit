"""
FastMCP server for tactile tactile graphics conversion.

This server exposes the tactile toolkit to Claude via MCP,
allowing natural language interaction for image-to-PIAF conversion.
"""

import logging
import sys
from pathlib import Path

# Configure logging to stderr (never stdout for MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("tactile-mcp")

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    logger.error("MCP library not installed. Run: pip install mcp")
    sys.exit(1)

from tactile_core.mcp_server.tools import (
    image_to_piaf,
    image_to_dithertone,
    list_presets,
    analyze_image,
    describe_image,
    extract_text_with_vision,
    assess_tactile_quality
)

# Initialize MCP server
mcp = FastMCP(
    name="tact",
    instructions="TACT — Tactile Architectural Conversion Tool. Use image_to_piaf to convert images to PIAF-ready PDFs — text detection and Braille conversion happen automatically in a single call. Use image_to_dithertone for photographs and tonal images — it replaces binary thresholding with a dot-grid halftone where dot size maps to brightness, preserving gradients. Use list_presets to see available presets (including dithertone_photo and dithertone_drawing), analyze_image for pre-conversion checks, and describe_image for detailed accessibility descriptions. For Braille sticker workflows, use sticker_workflow=true. For color images, use color_to_tactile=true for RainbowTact pattern conversion."
)

# Register tools
mcp.tool()(image_to_piaf)
mcp.tool()(image_to_dithertone)
mcp.tool()(list_presets)
mcp.tool()(analyze_image)
mcp.tool()(describe_image)
mcp.tool()(extract_text_with_vision)
mcp.tool()(assess_tactile_quality)


# ============================================================================
# MCP Resources
# ============================================================================

@mcp.resource("arch-alt-text://prompt")
def get_arch_alt_text_prompt() -> str:
    """
    The Arch-Alt-Text system prompt for describing architectural images.

    This prompt guides Claude to create multi-sensory descriptions of
    architectural images (plans, sections, diagrams, photos) specifically
    designed for blind/low-vision architecture students.

    Usage: Read this resource, then use Claude's vision capability to
    describe an image following the Macro/Meso/Micro format.
    """
    # Try to load from the patterns directory first
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / "patterns" / "image_description_machine" / "image_description_machine.md",
    ]

    for prompt_path in possible_paths:
        if prompt_path.exists():
            return prompt_path.read_text(encoding='utf-8')

    # Fallback to embedded prompt if file not found
    logger.warning("Could not find image_description_machine.md, using embedded prompt")
    return _get_embedded_arch_alt_text_prompt()


def _get_embedded_arch_alt_text_prompt() -> str:
    """Fallback embedded prompt if file is not found."""
    return '''You are **Arch-Alt-Text**, an expert narrator and tutor for a blind architecture student. Your dual mission:

1) Translate ANY visual used in architecture education into a vivid, multi-sensory mental model.
2) Build architectural literacy—precision in vocabulary, spatial reasoning, representation conventions, and critical context—without lecturing.
3) Only describe what is in the image, do not embellish, interpret or contextualize. Do not ask questions in your answer.
4) Do not repeat yourself within the answer.

════════════════════════════════════════
MACRO • MESO • MICRO — OUTPUT FORMAT (STRICT)
════════════════════════════════════════

Title: <concise title. Say the title if known, OR "Unknown" if no source is evident>

<Macro Layer — exactly 3 sentences>
• Identify the medium (photo, drawing, plan, section, axonometric, diagram, etc).
• State the principal subject and the image's purpose/argument.
• Convey the dominant atmosphere or pedagogical intent.

<Meso Layer — at least 4 sentences>
• Decompose composition and hierarchy: main masses/forms, axes/grids, figure–ground.
• Name primary materials/assemblies or graphical conventions.
• Give orientation and viewpoint/projection.
• Describe scale cues and lighting qualities.

<Micro Layer — at least 8 sentences>
• Detail textures, assemblies, structural logic, and environmental strategies.
• Provide proportional/relative dimensions.
• Map visual traits to multi-sensory analogies (tactile, acoustic, thermal).
• State occlusions and limits.

════════════════════════════════════════
WRITING RULES
════════════════════════════════════════

• Present tense; American English; ≤25 words per sentence.
• Never refer to "this image/photo"; describe directly.
• Output only: Title + three paragraphs.'''


@mcp.resource("ocr-extraction://prompt")
def get_ocr_extraction_prompt() -> str:
    """
    OCR extraction prompt for Claude's vision to detect text in architectural images.

    This prompt guides text extraction for Braille conversion, with special
    attention to handwritten annotations, dimensions, and rotated text.

    Usage: Read this resource, then use Claude's vision to extract text
    and return a JSON array of detected text with positions.
    """
    return '''You are extracting text from an architectural drawing for Braille conversion.

Your task: Identify ALL visible text in the image, including text that traditional OCR often misses.

For EACH text element found, provide:
- text: The exact text content (preserve case)
- x: Left edge position in pixels (estimate from image dimensions)
- y: Top edge position in pixels (estimate from image dimensions)
- width: Approximate width in pixels
- height: Approximate height in pixels
- type: One of "printed", "handwritten", or "dimension"
- confidence: Your confidence level ("high", "medium", or "low")

SPECIAL ATTENTION TO:

1. DIMENSIONS: Architectural measurements in various formats:
   - Feet-inches: 10'-6", 12' 0", 8'-4 1/2"
   - Metric: 3.5m, 2500mm, 45cm
   - Plain numbers with context: 120, 2400

2. HANDWRITTEN TEXT: Annotations, notes, corrections, sketched labels
   - Often in margins or near specific features
   - May be harder to read than printed text

3. ROTATED TEXT: Labels that are not horizontal
   - Vertical text along walls
   - Angled dimension strings
   - Text following curved paths

4. SMALL TEXT: Fine print, scale indicators, stamps
   - Often in title blocks
   - May be low contrast

5. ROOM LABELS: Names of spaces
   - LIVING ROOM, KITCHEN, BEDROOM
   - Often centered in rooms

OUTPUT FORMAT:
Return ONLY a valid JSON array. Example:

[
  {"text": "LIVING ROOM", "x": 450, "y": 320, "width": 120, "height": 18, "type": "printed", "confidence": "high"},
  {"text": "12'-6\\"", "x": 200, "y": 500, "width": 45, "height": 12, "type": "dimension", "confidence": "high"},
  {"text": "add outlet here", "x": 180, "y": 620, "width": 100, "height": 15, "type": "handwritten", "confidence": "medium"},
  {"text": "N", "x": 50, "y": 50, "width": 20, "height": 20, "type": "printed", "confidence": "high"}
]

IMPORTANT:
- Coordinates are pixel positions from TOP-LEFT corner (not bottom-left)
- Estimate positions based on image dimensions provided
- Include ALL readable text, even if partially obscured
- For rotated text, use the bounding box that would contain it
- Do not include decorative elements or hatching patterns
- Return empty array [] if no text is found'''


@mcp.resource("zoom-region-finder://prompt")
def get_zoom_region_finder_prompt() -> str:
    """
    Prompt for Claude to identify zoom regions in architectural drawings.

    This prompt guides Claude's vision capability to find specific regions
    (rooms, features, areas) that the user wants to zoom into.

    Usage: Read this resource when image_to_piaf returns phase="zoom_region_identification",
    then use vision to identify the requested region and return coordinates.
    """
    return '''You are identifying a specific region in an architectural drawing for zooming.

Your task: Find the region(s) matching the user's description and return their coordinates.

SEARCH STRATEGIES:

1. TEXT LABELS: Look for printed labels matching or similar to the target
   - Room names: "BEDROOM", "Kitchen", "LIVING ROOM", "Bath"
   - May be centered in rooms or along walls
   - Check for numbered variants: "Bedroom 1", "Bath 2"

2. ROOM SHAPES: If no label, identify rooms by:
   - Shape and size (bedrooms typically rectangular, bathrooms smaller)
   - Fixtures visible (kitchen has counters/appliances, bathroom has fixtures)
   - Position (master bedroom often largest, near master bath)

3. FEATURES: For non-room targets:
   - "staircase" - look for stair symbols, hatched areas, or stair labels
   - "entrance" / "entry" - look for main door, foyer area
   - "garage" - typically large rectangular space with car door symbol
   - "closet" - small spaces adjacent to bedrooms

4. SPATIAL REFERENCES: For directional targets:
   - "upper-left" = x: 0-50%, y: 0-50%
   - "upper-right" = x: 50-100%, y: 0-50%
   - "lower-left" = x: 0-50%, y: 50-100%
   - "lower-right" = x: 50-100%, y: 50-100%
   - "center" = x: 25-75%, y: 25-75%
   - "north side" - check for north arrow orientation

OUTPUT FORMAT:
Return a JSON array with ALL matching regions. For each region:

[
  {
    "label": "Bedroom 1",
    "x_percent": 25,
    "y_percent": 30,
    "width_percent": 30,
    "height_percent": 25,
    "confidence": "high"
  }
]

COORDINATE RULES:
- All values are percentages (0-100) of image dimensions
- x_percent: distance from LEFT edge to region's left edge
- y_percent: distance from TOP edge to region's top edge
- width_percent: region width as percentage of image width
- height_percent: region height as percentage of image height
- Include the ENTIRE room/feature, not just the label

MULTIPLE MATCHES:
- If multiple regions match (e.g., "bedroom" matches Bedroom 1, 2, 3), include ALL
- Add descriptive labels to distinguish them
- User will select which one(s) to zoom to

NO MATCH FOUND:
If no matching region found, return:
{
  "error": "no_match",
  "suggestions": ["list", "of", "detected", "regions"],
  "message": "Could not find 'target'. Available regions: ..."
}

IMPORTANT:
- Be generous with region boundaries - better to include too much than cut off content
- A 10% margin will be added automatically, so don't add extra padding
- For irregularly shaped rooms, use a bounding rectangle
- Coordinates from TOP-LEFT corner (not bottom-left)'''


def main():
    """Run the MCP server."""
    logger.info("Starting tactile MCP server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
