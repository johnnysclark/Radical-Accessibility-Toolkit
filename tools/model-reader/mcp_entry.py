#!/usr/bin/env python3
"""
model-reader MCP Server entry point.

Usage:
    python tools/model-reader/mcp_entry.py

Or add to .mcp.json:
    {
        "mcpServers": {
            "model-reader": {
                "command": "python",
                "args": ["tools/model-reader/mcp_entry.py"]
            }
        }
    }
"""

import sys
from pathlib import Path

# Add the model-reader source to the path
lib_path = Path(__file__).parent / "src"
sys.path.insert(0, str(lib_path))

from model_reader.mcp_server.server import main

if __name__ == "__main__":
    main()
