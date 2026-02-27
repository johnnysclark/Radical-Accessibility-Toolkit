# -*- coding: utf-8 -*-
"""
Image-to-PIAF — MCP Server  v1.0
==================================
Model Context Protocol wrapper around the Image-to-PIAF pipeline.

Exposes tactile image conversion as semantic MCP tools so that Claude Code,
Claude Desktop, Cursor, or any MCP-compatible client can convert images
to PIAF-ready output conversationally.

Requires: pip install mcp Pillow

Usage:
    python mcp_server.py

Claude Code config (.mcp.json at project root):
{
  "mcpServers": {
    "image-to-piaf": {
      "command": "python",
      "args": ["tactile/mcp_server.py"]
    }
  }
}
"""

import builtins
import json
import os
import sys

# ── Redirect print to stderr (stdout is JSON-RPC) ──────
_real_print = builtins.print

def _stderr_print(*args, **kwargs):
    kwargs.setdefault("file", sys.stderr)
    _real_print(*args, **kwargs)

builtins.print = _stderr_print

# ── Import image_to_piaf from same directory ──────────
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)

import image_to_piaf as piaf

# ── MCP dependency ─────────────────────────────────────
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    _real_print(
        "ERROR: mcp package not found. Install with: pip install mcp",
        file=sys.stderr)
    sys.exit(1)


# ══════════════════════════════════════════════════════════
# MCP SERVER
# ══════════════════════════════════════════════════════════

mcp = FastMCP("image-to-piaf")


# ──────────────────────────────────────────────────────────
# TOOLS
# ──────────────────────────────────────────────────────────

@mcp.tool()
def image_to_piaf(
    image_path: str,
    preset: str = "floor_plan",
    output_path: str = None,
    labels: str = None,
    paper: str = "letter",
    invert: bool = False,
    tile: bool = False,
) -> str:
    """Convert an image to PIAF-ready output for tactile swell paper printing.

    Runs the full conversion pipeline: contrast enhancement, grayscale,
    threshold, density management, optional braille labels, and paper fitting.

    Args:
        image_path: Path to the source image (JPG, PNG, TIFF, etc.)
        preset: Conversion preset. One of:
            - "floor_plan" — CAD output, printed plans
            - "elevation" — line drawings with moderate detail
            - "photograph" — photos of buildings, sites, models
            - "sketch" — hand-drawn sketches (light pencil/pen)
            - "section" — sections with poche/fill
            - "site_plan" — contours, vegetation, context
            - "rendering" — 3D shaded views
            - "diagram" — circulation, structural, concept diagrams
            - "historic_photo" — low contrast aged images
            - "handdrawn" — strong pencil/ink line drawings
        output_path: Output file path (auto-generated if None)
        labels: Semicolon-separated labels to add as braille (e.g. "Kitchen;Bath")
        paper: Paper size: "letter", "tabloid", "a4", "a3"
        invert: True to invert (white-on-black → black-on-white)
        tile: True to split into page-sized tiles with registration marks
    """
    label_list = None
    if labels:
        label_list = [
            {"text": t.strip(), "x": 10, "y": 10 + i * 80}
            for i, t in enumerate(labels.split(";")) if t.strip()
        ]

    try:
        result = piaf.convert(
            image_path=image_path,
            preset=preset,
            labels=label_list,
            paper=paper,
            invert=invert,
            tile=tile,
            output_path=output_path,
        )
        piaf._history_add(result)
        return piaf._format_result(result)
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def analyze_image(image_path: str) -> str:
    """Pre-flight analysis of an image before PIAF conversion.

    Returns dimensions, density at multiple thresholds, suggested preset,
    and warnings about potential issues.

    Args:
        image_path: Path to the image to analyze
    """
    try:
        result = piaf.analyze_image(image_path)
        return piaf._format_analysis(result)
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def assess_tactile_quality(image_path: str) -> str:
    """Post-conversion quality check of a PIAF-ready image.

    Checks density, blank margins, and provides a PASS/REVIEW verdict.

    Args:
        image_path: Path to the converted PIAF image to assess
    """
    try:
        result = piaf.assess_quality(image_path)
        return piaf._format_quality(result)
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def list_presets() -> str:
    """List all available conversion presets with descriptions.

    Each preset is tuned for a specific type of architectural image
    with optimized threshold and contrast settings.
    """
    lines = ["OK: Available presets:"]
    for name in sorted(piaf.PRESETS):
        info = piaf.PRESETS[name]
        lines.append(f"  {name}: {info['description']} "
                     f"(threshold={info['threshold']}, "
                     f"contrast={info['contrast']})")
    return "\n".join(lines)


@mcp.tool()
def convert_text_to_braille(text: str) -> str:
    """Convert English text to Grade 1 Unicode Braille.

    Useful for generating braille labels for architectural drawings.
    Returns the braille string and character count.

    Args:
        text: English text to convert
    """
    braille = piaf.text_to_braille(text)
    braille_g2, grade = piaf.text_to_braille_g2(text)
    lines = [f"OK: Braille conversion of '{text}'"]
    lines.append(f"  Grade 1: {braille} ({len(braille)} cells)")
    if grade == 2:
        lines.append(f"  Grade 2: {braille_g2} ({len(braille_g2)} cells)")
    else:
        lines.append("  Grade 2: liblouis not installed (using Grade 1 fallback)")
    return "\n".join(lines)


@mcp.tool()
def conversion_history() -> str:
    """Show recent conversion history.

    Lists the last 10 conversions with source, preset, and density.
    """
    entries = piaf._history_load()
    if not entries:
        return "OK: No conversion history yet."

    lines = [f"OK: Last {min(10, len(entries))} conversions:"]
    for e in entries[-10:]:
        src = os.path.basename(e.get("source", "?"))
        lines.append(f"  {e.get('timestamp','?')}  {src}  "
                     f"preset={e.get('preset','?')}  "
                     f"density={e.get('density',0):.0%}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────
# RESOURCES
# ──────────────────────────────────────────────────────────

@mcp.resource("piaf://presets")
def resource_presets() -> str:
    """All available conversion presets as JSON."""
    return json.dumps(piaf.PRESETS, indent=2)


@mcp.resource("piaf://help")
def resource_help() -> str:
    """Full CLI command reference for image-to-piaf."""
    return piaf.HELP_TEXT


@mcp.resource("piaf://density-guide")
def resource_density_guide() -> str:
    """Guide to PIAF density management."""
    return (
        "PIAF DENSITY GUIDE\n"
        "==================\n"
        "PIAF swell paper uses microcapsules that expand when heated.\n"
        "Black areas (printed with carbon-based toner) swell to create\n"
        "raised tactile surfaces.  Only carbon-based black toner works;\n"
        "other toners and inks do not swell.\n\n"
        "DENSITY LIMITS:\n"
        f"  Target: {piaf.DENSITY_TARGET:.0%} black pixels (optimal tactile clarity)\n"
        f"  Maximum: {piaf.DENSITY_MAX:.0%} black pixels (above this, paper overloads)\n"
        f"  Below 2%: image may appear nearly blank\n\n"
        "AUTO-REDUCTION:\n"
        "  When density exceeds the target, the tool applies iterative\n"
        "  morphological erosion (shrinking black areas) until density\n"
        "  falls below the target.  This preserves line structure while\n"
        "  reducing fill areas.\n\n"
        "TIPS:\n"
        "  - Use higher thresholds (130-150) for sketches to keep only strong lines\n"
        "  - Use lower thresholds (80-100) for photographs to capture tonal range\n"
        "  - If auto-reduction removes too much detail, try --no-density and\n"
        "    manually adjust the threshold instead\n"
        "  - For floor plans with heavy hatching, consider using the 'diagram'\n"
        "    preset which uses S-curve contrast to separate line work from fill"
    )


# ──────────────────────────────────────────────────────────
# PROMPTS
# ──────────────────────────────────────────────────────────

@mcp.prompt()
def tactile_conversion_workflow() -> str:
    """Guide for converting an architectural image to PIAF swell paper.

    Walks through the recommended workflow: analyze, choose preset,
    convert, assess quality.
    """
    return (
        "You are helping a blind architecture student convert an image\n"
        "to PIAF tactile swell paper output.  Follow this workflow:\n\n"
        "1. ANALYZE: Use analyze_image to check dimensions, density,\n"
        "   and get a suggested preset.\n\n"
        "2. CHOOSE PRESET: Based on the image type, select the best\n"
        "   preset.  Use list_presets to see all options.\n\n"
        "3. LABELS: Ask the user what areas should be labeled in braille.\n"
        "   Collect labels as semicolon-separated text.\n\n"
        "4. CONVERT: Use image_to_piaf with the chosen preset and labels.\n\n"
        "5. QUALITY CHECK: Use assess_tactile_quality on the output to\n"
        "   verify density and coverage.\n\n"
        "6. ITERATE: If quality issues are found, adjust the preset or\n"
        "   threshold and re-convert.\n\n"
        "Always communicate results using screen-reader-friendly text:\n"
        "short labeled lines, no tables, OK:/ERROR: prefixes."
    )


@mcp.prompt()
def describe_image_for_tactile() -> str:
    """System prompt for describing what should be labeled in a tactile conversion.

    Helps the AI identify key architectural features that need braille labels.
    """
    return (
        "You are examining an architectural image that will be converted\n"
        "to PIAF tactile swell paper for a blind student.\n\n"
        "Identify the key areas that should receive braille labels:\n"
        "- Room names and program types (Kitchen, Bedroom, etc.)\n"
        "- Structural elements (columns, walls, beams)\n"
        "- Circulation (corridors, stairs, elevators)\n"
        "- Outdoor spaces (courtyard, terrace, garden)\n"
        "- Scale references (dimensions, scale bar text)\n"
        "- North arrow or orientation markers\n\n"
        "Return labels as a semicolon-separated list.\n"
        "Prioritize the most important labels first — too many labels\n"
        "will crowd the tactile output.\n"
        "Maximum 8-10 labels per image for readability."
    )


# ── Entry point ────────────────────────────────────────

if __name__ == "__main__":
    _real_print("Image-to-PIAF MCP Server v1.0 starting...", file=sys.stderr)
    _real_print(f"Tools: {len(mcp._tool_manager._tools)} registered",
                file=sys.stderr)
    mcp.run()
