"""Entry point for the output MCP server."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from output.mcp_server.server import main
if __name__ == "__main__":
    main()
