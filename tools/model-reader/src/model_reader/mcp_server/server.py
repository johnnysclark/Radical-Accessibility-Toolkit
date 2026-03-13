"""FastMCP server for model-reader.

Exposes 3dm file reading capabilities to Claude via MCP.
"""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("model-reader-mcp")

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    logger.error("MCP library not installed. Run: pip install mcp")
    sys.exit(1)

from model_reader.mcp_server.tools import (
    open_3dm,
    list_layers,
    list_objects,
    extract_plan_view,
    extract_section_view,
    extract_elevation_view,
)

mcp = FastMCP(
    name="model-reader",
    instructions=(
        "model-reader — Read .3dm Rhino files accessibly. "
        "Use open_3dm to load a file and get a summary. "
        "Use list_layers and list_objects to explore contents. "
        "Use extract_plan_view, extract_section_view, and extract_elevation_view "
        "to generate 2D drawings as PNG images or PIAF tactile PDFs."
    ),
)

mcp.tool()(open_3dm)
mcp.tool()(list_layers)
mcp.tool()(list_objects)
mcp.tool()(extract_plan_view)
mcp.tool()(extract_section_view)
mcp.tool()(extract_elevation_view)


def main():
    """Run the MCP server."""
    logger.info("Starting model-reader MCP server")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
