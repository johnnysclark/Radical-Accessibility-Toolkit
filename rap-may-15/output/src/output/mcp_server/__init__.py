"""
MCP Server for TACT — Tactile Architectural Conversion Tool.

Exposes tactile conversion tools to Claude, enabling natural language
interaction for converting architectural images to tactile graphics.
"""

from output.mcp_server.server import main

__all__ = ['main']
