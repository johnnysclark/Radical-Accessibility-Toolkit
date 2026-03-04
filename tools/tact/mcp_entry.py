#!/usr/bin/env python3
"""
TACT MCP Server entry point for the Radical-Accessibility-Toolkit repo.

Usage:
    python tools/tact/mcp_entry.py

Or add to .mcp.json:
    {
        "mcpServers": {
            "tactile": {
                "command": "python",
                "args": ["tools/tact/mcp_entry.py"]
            }
        }
    }
"""

import sys
from pathlib import Path

# Add the tact source to the path
lib_path = Path(__file__).parent / "src"
sys.path.insert(0, str(lib_path))

from tactile_core.mcp_server.server import main

if __name__ == "__main__":
    main()
