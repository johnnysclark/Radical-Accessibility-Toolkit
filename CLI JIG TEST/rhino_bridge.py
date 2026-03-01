# -*- coding: utf-8 -*-
"""
PLAN LAYOUT JIG — Rhino Bridge  v1.0
======================================
Optional TCP client that talks to the Rhino watcher's query listener.

If Rhino is running and the watcher has its TCP listener active on
port 1998, this bridge can ask read-only questions:
  - How many objects are on each layer?
  - What is the bounding box of all geometry?
  - Execute a read-only RhinoScript query

If Rhino is not running, every function returns an OFFLINE message.
No function ever fails — offline mode is a first-class result.

Port 1998 is used (not 1999) to avoid conflicting with rhinomcp.

Requires: Python 3 stdlib only (socket, json).
"""

import json
import os
import socket
import threading

# ── Configuration ──────────────────────────────────────────
DEFAULT_HOST = os.environ.get("LAYOUT_JIG_RHINO_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("LAYOUT_JIG_RHINO_PORT", "1998"))
TIMEOUT_SEC = 5.0


class RhinoBridge:
    """TCP client for querying the Rhino watcher's listener."""

    def __init__(self, host=None, port=None):
        self.host = host or DEFAULT_HOST
        self.port = port or DEFAULT_PORT
        self._lock = threading.Lock()

    # ── Low-level ──────────────────────────────────────────

    def _send(self, request):
        """Send a JSON request and return the parsed response dict.

        Returns None if the connection fails (Rhino offline).
        """
        with self._lock:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(TIMEOUT_SEC)
                sock.connect((self.host, self.port))

                payload = json.dumps(request).encode("utf-8") + b"\n"
                sock.sendall(payload)

                # Read response (accumulate until newline)
                buf = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    buf += chunk
                    if b"\n" in buf:
                        break

                sock.close()

                if not buf.strip():
                    return None
                return json.loads(buf.strip())

            except (ConnectionRefusedError, ConnectionResetError,
                    socket.timeout, OSError):
                return None
            except json.JSONDecodeError:
                return None

    # ── Public API ─────────────────────────────────────────

    def is_connected(self):
        """Check if the Rhino watcher's TCP listener is reachable.

        Returns True/False. Does not raise.
        """
        resp = self._send({"type": "ping"})
        return resp is not None and resp.get("status") == "ok"

    def status(self):
        """Get Rhino connection status as a formatted string."""
        resp = self._send({"type": "status"})
        if resp is None:
            return ("OFFLINE: Rhino watcher is not connected on "
                    f"{self.host}:{self.port}. "
                    "All model data is available in state.json.")
        result = resp.get("result", {})
        lines = [
            "OK: Rhino watcher connected.",
            f"  Host: {self.host}:{self.port}",
            f"  Layers: {result.get('layer_count', '?')}",
            f"  Objects: {result.get('object_count', '?')}",
            f"  Last rebuild: {result.get('last_rebuild', '?')}",
            "READY:"
        ]
        return "\n".join(lines)

    def query(self, query_type, params=None):
        """Send a read-only query to the Rhino watcher.

        Supported query types (implemented by watcher listener):
          - "ping"          — connectivity check
          - "status"        — layer count, object count, last rebuild time
          - "layer_stats"   — per-layer object counts
          - "bounding_box"  — world-space bounding box of all geometry
          - "object_count"  — total or per-layer (params: {"layer": "JIG_COLUMNS"})

        Returns formatted text string (never raises).
        """
        request = {"type": query_type}
        if params:
            request["params"] = params

        resp = self._send(request)
        if resp is None:
            return ("OFFLINE: Cannot query Rhino. The watcher is not "
                    f"listening on {self.host}:{self.port}. "
                    "Model data is still available in state.json.")

        if resp.get("status") == "error":
            return f"ERROR: Rhino query failed: {resp.get('message', '?')}"

        result = resp.get("result", {})

        # Format based on query type
        if query_type == "layer_stats":
            lines = ["OK: Rhino layer statistics:"]
            for layer_name, count in sorted(result.items()):
                lines.append(f"  {layer_name}: {count} object(s)")
            lines.append("READY:")
            return "\n".join(lines)

        elif query_type == "bounding_box":
            bb = result
            if not bb:
                return "OK: No geometry in Rhino.\nREADY:"
            lines = [
                "OK: Geometry bounding box:",
                f"  X: [{bb.get('min_x', '?'):.1f}, {bb.get('max_x', '?'):.1f}]",
                f"  Y: [{bb.get('min_y', '?'):.1f}, {bb.get('max_y', '?'):.1f}]",
                f"  Z: [{bb.get('min_z', '?'):.1f}, {bb.get('max_z', '?'):.1f}]",
                "READY:"
            ]
            return "\n".join(lines)

        elif query_type == "object_count":
            layer = (params or {}).get("layer", "all")
            return f"OK: {result.get('count', 0)} object(s) on {layer}.\nREADY:"

        else:
            # Generic JSON dump for unknown queries
            return f"OK: {json.dumps(result, indent=2)}\nREADY:"

    def run_script(self, code):
        """Execute a read-only Python snippet inside Rhino.

        The code runs in the watcher's IronPython context. It should use
        rhinoscriptsyntax functions and print() for output. The watcher
        captures stdout and returns it.

        IMPORTANT: This is for read-only queries only. The watcher will
        refuse scripts that call rs.AddXxx, rs.DeleteXxx, or other
        geometry-modifying functions.

        Returns formatted text string (never raises).
        """
        resp = self._send({"type": "run_script", "code": code})
        if resp is None:
            return ("OFFLINE: Cannot run script. Rhino watcher is not connected. "
                    "Use the controller CLI for model queries instead.")

        if resp.get("status") == "error":
            return f"ERROR: Script execution failed: {resp.get('message', '?')}"

        output = resp.get("result", {}).get("output", "")
        if not output:
            return "OK: Script executed. No output.\nREADY:"

        lines = ["OK: Script output:", ""]
        for line in output.strip().split("\n"):
            lines.append(f"  {line}")
        lines.append("READY:")
        return "\n".join(lines)


# ── Module-level singleton ─────────────────────────────────
_bridge = None


def get_bridge():
    """Get or create the module-level RhinoBridge singleton."""
    global _bridge
    if _bridge is None:
        _bridge = RhinoBridge()
    return _bridge
