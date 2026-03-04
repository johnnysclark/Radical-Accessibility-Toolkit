"""Rhino connection management: MCP socket, RhinoCode CLI, and offline fallback.

Automatically detects WSL2 and routes to the Windows host IP when Rhino
is running on Windows but TASC is running inside WSL2.
"""

from __future__ import annotations

import json
import shutil
import socket
import subprocess

from tasc_core.rhino.protocol import make_command, parse_response


def _is_wsl2() -> bool:
    """Check if running inside WSL2."""
    try:
        with open("/proc/version") as f:
            return "microsoft" in f.read().lower()
    except OSError:
        return False


def _get_wsl2_gateway() -> str | None:
    """Get the Windows host IP from WSL2's default gateway."""
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Output like: "default via 172.28.208.1 dev eth0"
        parts = result.stdout.strip().split()
        if "via" in parts:
            return parts[parts.index("via") + 1]
    except (FileNotFoundError, subprocess.TimeoutExpired, IndexError, ValueError):
        pass
    return None


class MCPClient:
    """Direct TCP socket connection to RhinoMCP plugin."""

    def __init__(self, host: str = "127.0.0.1", port: int = 1999, timeout: float = 15.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._socket: socket.socket | None = None
        self._buffer = ""

    def connect(self) -> bool:
        """Attempt TCP connection. Returns True on success."""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.host, self.port))
            return True
        except (ConnectionRefusedError, OSError, TimeoutError):
            self._socket = None
            return False

    def send_command(self, cmd_type: str, params: dict) -> dict:
        """Send a command and wait for response."""
        if not self._socket:
            raise ConnectionError("Not connected to RhinoMCP")
        data = make_command(cmd_type, params)
        self._socket.sendall(data)
        # Read response
        while True:
            chunk = self._socket.recv(4096).decode("utf-8")
            if not chunk:
                raise ConnectionError("Connection closed by RhinoMCP")
            self._buffer += chunk
            response, self._buffer = parse_response(self._buffer)
            if response is not None:
                return response

    def close(self) -> None:
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None


class RhinoCodeClient:
    """Fallback: generates Python scripts and executes via rhinocode CLI."""

    def is_available(self) -> bool:
        """Check if rhinocode binary exists."""
        return shutil.which("rhinocode") is not None

    def execute_script(self, code: str) -> str:
        """Execute a RhinoPython script via rhinocode CLI."""
        try:
            result = subprocess.run(
                ["rhinocode", "exec", "--code", code],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.stdout + result.stderr
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return f"RhinoCode error: {e}"


class RhinoConnector:
    """Manages connection to Rhino. Tries MCP socket first, falls back to RhinoCode, then offline."""

    def __init__(self, host: str = "127.0.0.1", port: int = 1999, timeout: float = 15.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.mode: str | None = None
        self._mcp: MCPClient | None = None
        self._rhinocode: RhinoCodeClient | None = None

    def connect(self) -> str:
        """Try MCP socket, then RhinoCode, then offline. Returns mode string.

        When running in WSL2 with the default localhost host, automatically
        detects the Windows gateway IP and retries the MCP connection there.
        This handles the common case where Rhino runs on Windows while TASC
        runs inside WSL2.
        """
        # Try MCP socket at specified host
        mcp = MCPClient(self.host, self.port, self.timeout)
        if mcp.connect():
            self._mcp = mcp
            self.mode = "mcp"
            return "mcp"

        # If localhost failed and we're in WSL2, try the Windows gateway IP.
        # RhinoMCP binds to 127.0.0.1 on Windows, which requires a netsh
        # portproxy to be reachable from WSL2. The gateway IP is the bridge.
        if self.host in ("127.0.0.1", "localhost") and _is_wsl2():
            gateway = _get_wsl2_gateway()
            if gateway:
                mcp_wsl = MCPClient(gateway, self.port, self.timeout)
                if mcp_wsl.connect():
                    self._mcp = mcp_wsl
                    self.host = gateway
                    self.mode = "mcp"
                    return "mcp"

        # Try RhinoCode CLI
        rc = RhinoCodeClient()
        if rc.is_available():
            self._rhinocode = rc
            self.mode = "rhinocode"
            return "rhinocode"

        # Offline mode
        self.mode = "offline"
        return "offline"

    def send(self, command_type: str, params: dict) -> dict:
        """Send command via active connection mode."""
        if self.mode == "mcp" and self._mcp:
            return self._mcp.send_command(command_type, params)
        elif self.mode == "rhinocode" and self._rhinocode:
            # Convert command to RhinoPython script
            script = self._command_to_script(command_type, params)
            output = self._rhinocode.execute_script(script)
            return {"status": "ok", "output": output}
        elif self.mode == "offline":
            return {"status": "offline", "message": "No Rhino connection. Command queued locally."}
        else:
            raise ConnectionError("Not connected. Call connect() first.")

    def send_batch(self, commands: list[dict]) -> list[dict]:
        """Send multiple commands."""
        results = []
        for cmd in commands:
            result = self.send(cmd.get("type", ""), cmd.get("params", {}))
            results.append(result)
        return results

    def disconnect(self) -> None:
        if self._mcp:
            self._mcp.close()
            self._mcp = None
        self._rhinocode = None
        self.mode = None

    @property
    def is_connected(self) -> bool:
        return self.mode is not None

    @property
    def is_live(self) -> bool:
        """True if connected to a live Rhino instance (not offline)."""
        return self.mode in ("mcp", "rhinocode")

    def _command_to_script(self, cmd_type: str, params: dict) -> str:
        """Convert a TASC protocol command to a RhinoPython script."""
        if cmd_type == "create_object":
            obj_type = params.get("object_type", "")
            if obj_type == "polyline":
                points = params.get("points", [])
                pts_str = ", ".join(f"({p[0]},{p[1]},{p[2]})" for p in points)
                return (
                    f"import rhinoscriptsyntax as rs\n"
                    f"pts = [{pts_str}]\n"
                    f"rs.AddPolyline(pts)\n"
                )
            elif obj_type == "line":
                start = params.get("start", [0, 0, 0])
                end = params.get("end", [0, 0, 0])
                return (
                    f"import rhinoscriptsyntax as rs\n"
                    f"rs.AddLine(({start[0]},{start[1]},{start[2]}), ({end[0]},{end[1]},{end[2]}))\n"
                )
        elif cmd_type == "create_layer":
            name = params.get("name", "")
            color = params.get("color", [0, 0, 0])
            return (
                f"import rhinoscriptsyntax as rs\n"
                f"if not rs.IsLayer('{name}'):\n"
                f"    rs.AddLayer('{name}', ({color[0]},{color[1]},{color[2]}))\n"
            )
        # Generic fallback
        return f"# Unsupported command: {cmd_type}\nprint('{json.dumps(params)}')\n"
