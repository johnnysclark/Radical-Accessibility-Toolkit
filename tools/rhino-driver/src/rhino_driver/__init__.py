"""rhino-driver: render a TASC model to Rhino as one deterministic RhinoPython script.

Cross-platform driver that fixes and supersedes the previous macOS path. It
unifies two transports (RhinoMCP socket on Windows/WSL2, the real ``rhinocode``
CLI on macOS) behind a single full-rebuild script, and reports its connection
state honestly so nothing fails silently.
"""

__version__ = "0.1.0"
