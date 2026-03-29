# -*- coding: utf-8 -*-
"""
Rhino Automation Harness — MCP Server
======================================
Drives Rhino through Claude Code. Connects via TCP to a watcher
process running inside Rhino, or works standalone for script generation.

Tools:
  Connection:  rhino_status, rhino_connect
  Query:       rhino_layers, rhino_objects, rhino_bounds
  Execute:     rhino_run, rhino_command
  Scripts:     script_save, script_list, script_show, script_run
  Session:     session_log, session_read, session_snapshot

Usage:
  Add to .mcp.json:
  {
    "mcpServers": {
      "rhino-harness": {
        "command": "python3",
        "args": ["harness/mcp_server.py"]
      }
    }
  }
"""

import json
import os
import socket
import sys
import time

# ── MCP framework ────────────────────────────────────────
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    sys.exit("pip install mcp   # MCP framework required")

mcp = FastMCP(
    "rhino-harness",
    instructions=(
        "Rhino automation harness. Use rhino_run to execute IronPython "
        "in Rhino. Use script_save/script_run for reusable scripts. "
        "Scripts must be IronPython 2.7 — no f-strings, no pathlib."
    ),
)

# ── Paths ────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(_HERE, "scripts")
SESSIONS_DIR = os.path.join(_HERE, "sessions")
os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)

# ── TCP connection to Rhino watcher ──────────────────────

RHINO_HOST = os.environ.get("RHINO_HOST", "127.0.0.1")
RHINO_PORT = int(os.environ.get("RHINO_PORT", "1998"))
TIMEOUT = 5.0


def _tcp_send(request):
    """Send a JSON request to the Rhino watcher, return parsed response."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        sock.connect((RHINO_HOST, RHINO_PORT))
        sock.sendall(json.dumps(request).encode("utf-8") + b"\n")
        chunks = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)
        sock.close()
        return json.loads(b"".join(chunks).decode("utf-8"))
    except (socket.error, socket.timeout, json.JSONDecodeError, OSError):
        return None


def _is_connected():
    resp = _tcp_send({"type": "ping"})
    return resp is not None and resp.get("status") == "ok"


# ══════════════════════════════════════════════════════════
# CONNECTION TOOLS
# ══════════════════════════════════════════════════════════

@mcp.tool()
def rhino_status() -> str:
    """Check Rhino connection status and get basic stats."""
    resp = _tcp_send({"type": "status"})
    if resp is None:
        return ("OFFLINE: Cannot reach Rhino on {}:{}.\n"
                "Start Rhino and run the watcher script.".format(
                    RHINO_HOST, RHINO_PORT))
    r = resp.get("result", {})
    return ("ONLINE: Rhino connected.\n"
            "  Layers: {}\n"
            "  Objects: {}\n"
            "  Last rebuild: {}".format(
                r.get("layer_count", "?"),
                r.get("object_count", "?"),
                r.get("last_rebuild", "?")))


@mcp.tool()
def rhino_connect(host: str = "", port: int = 0) -> str:
    """Update connection settings and test the connection.

    Args:
        host: Rhino host IP (default 127.0.0.1)
        port: Rhino watcher port (default 1998)
    """
    global RHINO_HOST, RHINO_PORT
    if host:
        RHINO_HOST = host
    if port:
        RHINO_PORT = port
    if _is_connected():
        return "OK: Connected to Rhino at {}:{}.".format(RHINO_HOST, RHINO_PORT)
    return "ERROR: Cannot connect to {}:{}.".format(RHINO_HOST, RHINO_PORT)


# ══════════════════════════════════════════════════════════
# QUERY TOOLS
# ══════════════════════════════════════════════════════════

@mcp.tool()
def rhino_layers() -> str:
    """List all layers and their object counts."""
    resp = _tcp_send({"type": "layer_stats"})
    if resp is None:
        return "OFFLINE: Rhino not connected."
    stats = resp.get("result", {})
    if not stats:
        return "OK: No layers with objects."
    lines = ["OK: Layer statistics:"]
    total = 0
    for layer, count in sorted(stats.items()):
        if count > 0:
            lines.append("  {}: {} objects".format(layer, count))
            total += count
    lines.append("  Total: {} objects".format(total))
    return "\n".join(lines)


@mcp.tool()
def rhino_objects(layer: str = "") -> str:
    """Get object count, optionally filtered by layer.

    Args:
        layer: Layer name to filter (empty for all)
    """
    params = {}
    if layer:
        params["layer"] = layer
    resp = _tcp_send({"type": "object_count", "params": params})
    if resp is None:
        return "OFFLINE: Rhino not connected."
    r = resp.get("result", {})
    count = r.get("count", r.get("object_count", "?"))
    if layer:
        return "OK: {} objects on layer '{}'.".format(count, layer)
    return "OK: {} total objects.".format(count)


@mcp.tool()
def rhino_bounds() -> str:
    """Get the bounding box of all geometry in the document."""
    resp = _tcp_send({"type": "bounding_box"})
    if resp is None:
        return "OFFLINE: Rhino not connected."
    bb = resp.get("result", {})
    if not bb:
        return "OK: No geometry in document."
    return ("OK: Bounding box:\n"
            "  X: {:.1f} to {:.1f} ({:.1f} wide)\n"
            "  Y: {:.1f} to {:.1f} ({:.1f} deep)\n"
            "  Z: {:.1f} to {:.1f} ({:.1f} tall)".format(
                bb.get("min_x", 0), bb.get("max_x", 0),
                bb.get("max_x", 0) - bb.get("min_x", 0),
                bb.get("min_y", 0), bb.get("max_y", 0),
                bb.get("max_y", 0) - bb.get("min_y", 0),
                bb.get("min_z", 0), bb.get("max_z", 0),
                bb.get("max_z", 0) - bb.get("min_z", 0)))


# ══════════════════════════════════════════════════════════
# EXECUTE TOOLS
# ══════════════════════════════════════════════════════════

@mcp.tool()
def rhino_run(code: str) -> str:
    """Execute IronPython code inside Rhino and return printed output.

    The code runs in IronPython 2.7 with rhinoscriptsyntax available.
    Use print() to return results. Geometry-modifying calls (rs.Add*,
    rs.Delete*, rs.Move*) are blocked for safety — use rhino_command
    for those.

    Args:
        code: IronPython 2.7 code to execute
    """
    resp = _tcp_send({"type": "run_script", "code": code})
    if resp is None:
        return "OFFLINE: Rhino not connected."
    if resp.get("status") == "error":
        return "ERROR: {}".format(resp.get("message", "Unknown error"))
    output = resp.get("result", {}).get("output", "")
    return "OK:\n{}".format(output) if output else "OK: Script executed (no output)."


@mcp.tool()
def rhino_command(command: str) -> str:
    """Run a Rhino command-line string (e.g. '_Zoom _Extents').

    Uses rs.Command() inside Rhino. For complex geometry operations,
    prefer saving a script with script_save and running it.

    Args:
        command: Rhino command string
    """
    code = ('import rhinoscriptsyntax as rs\n'
            'rs.Command("{}")\n'
            'print("OK: Command executed.")'.format(
                command.replace('"', '\\"')))
    resp = _tcp_send({"type": "run_script", "code": code})
    if resp is None:
        return "OFFLINE: Rhino not connected."
    if resp.get("status") == "error":
        return "ERROR: {}".format(resp.get("message", "Unknown error"))
    output = resp.get("result", {}).get("output", "")
    return output if output else "OK: Command sent."


# ══════════════════════════════════════════════════════════
# SCRIPT TOOLS
# ══════════════════════════════════════════════════════════

def _safe_name(name):
    """Sanitize a script name to a safe filename."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)


@mcp.tool()
def script_save(name: str, code: str, description: str = "") -> str:
    """Save a reusable IronPython script.

    Scripts are stored in harness/scripts/ as .py files with a JSON
    sidecar for metadata.

    Args:
        name: Script name (alphanumeric, hyphens, underscores)
        code: IronPython 2.7 code
        description: What the script does
    """
    safe = _safe_name(name)
    if not safe:
        return "ERROR: Invalid script name."

    script_path = os.path.join(SCRIPTS_DIR, safe + ".py")
    meta_path = os.path.join(SCRIPTS_DIR, safe + ".json")

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)

    meta = {
        "name": name,
        "description": description,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "file": safe + ".py",
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return "OK: Saved script '{}' ({} bytes).".format(name, len(code))


@mcp.tool()
def script_list() -> str:
    """List all saved scripts."""
    scripts = []
    for f in sorted(os.listdir(SCRIPTS_DIR)):
        if f.endswith(".json"):
            try:
                with open(os.path.join(SCRIPTS_DIR, f), "r") as fh:
                    meta = json.load(fh)
                scripts.append("  {}: {}".format(
                    meta.get("name", f), meta.get("description", "")))
            except (json.JSONDecodeError, OSError):
                pass
    if not scripts:
        return "OK: No saved scripts."
    return "OK: Saved scripts:\n" + "\n".join(scripts)


@mcp.tool()
def script_show(name: str) -> str:
    """Show the contents of a saved script.

    Args:
        name: Script name
    """
    safe = _safe_name(name)
    script_path = os.path.join(SCRIPTS_DIR, safe + ".py")
    if not os.path.exists(script_path):
        return "ERROR: Script '{}' not found.".format(name)
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    return "OK: Script '{}':\n{}".format(name, code)


@mcp.tool()
def script_run(name: str) -> str:
    """Run a saved script in Rhino.

    Args:
        name: Script name
    """
    safe = _safe_name(name)
    script_path = os.path.join(SCRIPTS_DIR, safe + ".py")
    if not os.path.exists(script_path):
        return "ERROR: Script '{}' not found.".format(name)
    with open(script_path, "r", encoding="utf-8") as f:
        code = f.read()
    return rhino_run(code)


@mcp.tool()
def script_delete(name: str) -> str:
    """Delete a saved script.

    Args:
        name: Script name
    """
    safe = _safe_name(name)
    script_path = os.path.join(SCRIPTS_DIR, safe + ".py")
    meta_path = os.path.join(SCRIPTS_DIR, safe + ".json")
    if not os.path.exists(script_path):
        return "ERROR: Script '{}' not found.".format(name)
    os.remove(script_path)
    if os.path.exists(meta_path):
        os.remove(meta_path)
    return "OK: Deleted script '{}'.".format(name)


# ══════════════════════════════════════════════════════════
# SESSION TOOLS
# ══════════════════════════════════════════════════════════

def _session_path():
    return os.path.join(SESSIONS_DIR, "session.jsonl")


@mcp.tool()
def session_log(entry: str, tag: str = "") -> str:
    """Log a session entry (milestone, note, or progress marker).

    Args:
        entry: What happened or was accomplished
        tag: Optional category tag (e.g. milestone, note, issue)
    """
    record = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "entry": entry,
    }
    if tag:
        record["tag"] = tag

    with open(_session_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, separators=(",", ":")) + "\n")

    return "OK: Logged{}.".format(" [{}]".format(tag) if tag else "")


@mcp.tool()
def session_read(last: int = 10) -> str:
    """Read recent session log entries.

    Args:
        last: Number of recent entries to show (default 10)
    """
    path = _session_path()
    if not os.path.exists(path):
        return "OK: No session log yet."
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
    recent = lines[-last:]
    if not recent:
        return "OK: Session log is empty."
    entries = []
    for line in recent:
        try:
            r = json.loads(line)
            tag = " [{}]".format(r["tag"]) if r.get("tag") else ""
            entries.append("  {}{}: {}".format(r.get("time", "?"), tag, r.get("entry", "")))
        except json.JSONDecodeError:
            pass
    return "OK: Recent session log:\n" + "\n".join(entries)


@mcp.tool()
def session_clear() -> str:
    """Clear the session log (start fresh)."""
    path = _session_path()
    if os.path.exists(path):
        os.remove(path)
    return "OK: Session log cleared."


@mcp.tool()
def session_export() -> str:
    """Export the full session log as text."""
    path = _session_path()
    if not os.path.exists(path):
        return "OK: No session log to export."
    with open(path, "r", encoding="utf-8") as f:
        return "OK: Full session log:\n" + f.read()


# ══════════════════════════════════════════════════════════
# PROMPTS
# ══════════════════════════════════════════════════════════

@mcp.prompt()
def plan_session() -> str:
    """Start a Rhino automation session. Checks connection,
    lists saved scripts, and reviews the session log."""
    parts = []

    # Connection
    if _is_connected():
        resp = _tcp_send({"type": "status"})
        r = resp.get("result", {}) if resp else {}
        parts.append("Rhino: ONLINE ({} objects, {} layers)".format(
            r.get("object_count", "?"), r.get("layer_count", "?")))
    else:
        parts.append("Rhino: OFFLINE — start Rhino and run the watcher.")

    # Scripts
    scripts = []
    for f in sorted(os.listdir(SCRIPTS_DIR)):
        if f.endswith(".json"):
            try:
                with open(os.path.join(SCRIPTS_DIR, f), "r") as fh:
                    meta = json.load(fh)
                scripts.append(meta.get("name", f))
            except (json.JSONDecodeError, OSError):
                pass
    if scripts:
        parts.append("Saved scripts: " + ", ".join(scripts))
    else:
        parts.append("No saved scripts yet.")

    # Session log
    path = _session_path()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        if lines:
            last = json.loads(lines[-1])
            parts.append("Last session entry: {} — {}".format(
                last.get("time", "?"), last.get("entry", "?")))

    parts.append("\nWhat would you like to do in Rhino?")
    return "\n".join(parts)


@mcp.prompt()
def review_model() -> str:
    """Get a full description of the current Rhino model state."""
    if not _is_connected():
        return "Rhino is offline. Start Rhino and run the watcher to review."

    parts = ["Current Rhino model state:\n"]

    # Status
    resp = _tcp_send({"type": "status"})
    if resp:
        r = resp.get("result", {})
        parts.append("Objects: {}".format(r.get("object_count", "?")))
        parts.append("Layers: {}".format(r.get("layer_count", "?")))
        parts.append("Last rebuild: {}".format(r.get("last_rebuild", "?")))

    # Layers
    resp = _tcp_send({"type": "layer_stats"})
    if resp:
        stats = resp.get("result", {})
        parts.append("\nLayer breakdown:")
        for layer, count in sorted(stats.items()):
            if count > 0:
                parts.append("  {}: {}".format(layer, count))

    # Bounding box
    resp = _tcp_send({"type": "bounding_box"})
    if resp:
        bb = resp.get("result", {})
        if bb:
            parts.append("\nBounding box:")
            parts.append("  X: {:.1f} to {:.1f}".format(
                bb.get("min_x", 0), bb.get("max_x", 0)))
            parts.append("  Y: {:.1f} to {:.1f}".format(
                bb.get("min_y", 0), bb.get("max_y", 0)))
            parts.append("  Z: {:.1f} to {:.1f}".format(
                bb.get("min_z", 0), bb.get("max_z", 0)))

    parts.append("\nDescribe what you see and suggest improvements or next steps.")
    return "\n".join(parts)


# ── Entry point ──────────────────────────────────────────

if __name__ == "__main__":
    print("Rhino Automation Harness starting...", file=sys.stderr)
    print("  Scripts: {}".format(SCRIPTS_DIR), file=sys.stderr)
    print("  Sessions: {}".format(SESSIONS_DIR), file=sys.stderr)
    print("  Rhino: {}:{}".format(RHINO_HOST, RHINO_PORT), file=sys.stderr)
    mcp.run()
