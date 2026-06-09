"""Connect to Rhino and push a model as one script over whichever transport works.

Two live transports, one payload:

- **RhinoMCP socket** (Windows/WSL2, and macOS if the plugin is installed): the
  whole-model script is sent as a single ``execute_rhinoscript_python_code``
  command — one round trip instead of hundreds of per-object commands.
- **rhinocode CLI** (the macOS path): the same script is written to a temp file
  and run once via ``rhinocode script``.

If neither is available the driver is *offline* and says so — loudly. Reporting
"success" while nothing was drawn (the old behavior) is the bug we are fixing, so
every result carries a real status.

The socket client and wire framing are reused from ``tasc.rhino.connector`` /
``tasc.rhino.protocol``; this module adds the unified one-script behavior, the
real macOS path, and honest diagnostics.
"""

from __future__ import annotations

import json
import subprocess

from tasc.rhino.connector import MCPClient

from rhino_driver.render import commands_to_script, render_model
from rhino_driver.rhinocode import RhinoCodeCLI


def _is_wsl2() -> bool:
    """True when running inside WSL2 (Rhino is then on the Windows host)."""
    try:
        with open("/proc/version") as handle:
            return "microsoft" in handle.read().lower()
    except OSError:
        return False


def _wsl2_gateway() -> str | None:
    """Windows host IP as seen from WSL2 (the default-route gateway)."""
    try:
        result = subprocess.run(
            ["ip", "route", "show", "default"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        parts = result.stdout.strip().split()
        if "via" in parts:
            return parts[parts.index("via") + 1]
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return None


class RhinoDriver:
    """Drive Rhino from the model via a single deterministic script per redraw."""

    def __init__(self, host: str = "127.0.0.1", port: int = 1999, timeout: float = 15.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.mode: str | None = None
        self._mcp: MCPClient | None = None
        self._rhinocode: RhinoCodeCLI | None = None

    # -- connection -----------------------------------------------------------

    def connect(self) -> str:
        """Pick a transport. Order: MCP socket, WSL2 gateway socket, rhinocode, offline.

        rhinocode is only chosen when a *live* script-server instance exists, so
        we never select a transport that would quietly do nothing.
        """
        client = MCPClient(self.host, self.port, self.timeout)
        if client.connect():
            self._mcp = client
            self.mode = "mcp"
            return self.mode

        if self.host in ("127.0.0.1", "localhost") and _is_wsl2():
            gateway = _wsl2_gateway()
            if gateway:
                gw_client = MCPClient(gateway, self.port, self.timeout)
                if gw_client.connect():
                    self._mcp = gw_client
                    self.host = gateway
                    self.mode = "mcp"
                    return self.mode

        cli = RhinoCodeCLI()
        if cli.found and cli.has_live_instance():
            self._rhinocode = cli
            self.mode = "rhinocode"
            return self.mode

        self.mode = "offline"
        return self.mode

    def disconnect(self) -> None:
        if self._mcp:
            self._mcp.close()
            self._mcp = None
        self._rhinocode = None
        self.mode = None

    @property
    def is_live(self) -> bool:
        return self.mode in ("mcp", "rhinocode")

    # -- sending --------------------------------------------------------------

    def run_script(self, code: str) -> dict:
        """Run a RhinoPython script once over the active transport.

        Returns ``{"status": "ok"|"error"|"offline", "mode": ..., "output": ...}``.
        """
        if self.mode == "mcp" and self._mcp:
            try:
                response = self._mcp.send_command("execute_rhinoscript_python_code", {"code": code})
            except (ConnectionError, OSError) as exc:
                return {"status": "error", "mode": "mcp", "output": str(exc)}
            return self._normalize_mcp(response)

        if self.mode == "rhinocode" and self._rhinocode:
            result = self._rhinocode.run_script(code)
            result["mode"] = "rhinocode"
            return result

        return {
            "status": "offline",
            "mode": self.mode or "offline",
            "output": "No Rhino connection; nothing was drawn.",
        }

    def apply(self, commands: list[dict]) -> dict:
        """Translate a protocol command list to one script and run it once."""
        return self.run_script(commands_to_script(commands))

    def run_model(self, model) -> dict:
        """Render a TASC model to one script and run it once (full rebuild)."""
        return self.run_script(render_model(model))

    @staticmethod
    def _normalize_mcp(response: dict) -> dict:
        status = str(response.get("status", "")).lower()
        ok = status in ("success", "ok")
        payload = response.get("result")
        if payload is None:
            payload = response.get("message", "")
        output = payload if isinstance(payload, str) else json.dumps(payload)
        return {"status": "ok" if ok else "error", "mode": "mcp", "output": output}

    # -- diagnostics ----------------------------------------------------------

    def status(self) -> dict:
        """Probe every transport and recommend the next action. Never raises.

        This is the accessibility backbone: it turns silent failure into a
        labeled, actionable report (which transport is live, where rhinocode is,
        whether the script server is running, and exactly what to do next).
        """
        probe_timeout = min(self.timeout, 5.0)
        info: dict = {"socket_host": self.host, "socket_port": self.port, "wsl2": _is_wsl2()}

        client = MCPClient(self.host, self.port, probe_timeout)
        socket_ok = client.connect()
        client.close()

        if not socket_ok and self.host in ("127.0.0.1", "localhost") and info["wsl2"]:
            gateway = _wsl2_gateway()
            if gateway:
                gw_client = MCPClient(gateway, self.port, probe_timeout)
                if gw_client.connect():
                    socket_ok = True
                    info["socket_host"] = gateway
                gw_client.close()
        info["socket_reachable"] = socket_ok

        cli = RhinoCodeCLI()
        info["rhinocode_found"] = cli.found
        info["rhinocode_path"] = cli.exe
        instances = cli.list_instances() if cli.found else []
        info["rhinocode_instances"] = instances

        if socket_ok:
            info["mode"] = "mcp"
            info["recommendation"] = "Connected via RhinoMCP socket at {0}:{1}.".format(
                info["socket_host"], self.port
            )
        elif cli.found and instances:
            info["mode"] = "rhinocode"
            info["recommendation"] = "Connected via rhinocode (instance {0}).".format(instances[0])
        elif cli.found and not instances:
            info["mode"] = "offline"
            info["recommendation"] = (
                "rhinocode found but no live script server. In Rhino, run: StartScriptServer"
            )
        else:
            info["mode"] = "offline"
            info["recommendation"] = (
                "No Rhino connection. Install Rhino 8 and ensure 'rhinocode' is on PATH "
                "(macOS: /Applications/Rhino 8.app/Contents/Resources/bin), then run "
                "StartScriptServer in Rhino. Or start the RhinoMCP plugin for the socket."
            )
        return info
